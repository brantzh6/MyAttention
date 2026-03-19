# 服务化部署架构设计

> 目标：为 MyAttention 提供统一的跨平台服务化运行方案，覆盖 Windows、Linux、macOS 三类宿主环境，并和当前 `manage.py` 启动控制面保持一致。

---

## 1. 设计目标

- 本机开发环境不依赖黑色控制台窗口维持服务存活
- 基础设施和应用层区分托管方式
- Windows / Linux / macOS 都有明确的一等方案
- 本机开发、单机部署、分布式部署共用同一套组件认知
- 日志、健康检查、启动顺序、失败恢复都有明确落点

---

## 2. 组件分层

推荐按两层托管：

### 基础设施层

- PostgreSQL
- Redis
- 后续如外置 Qdrant / MinIO / Nginx 也属于这一层

特点：

- 生命周期独立于应用代码
- 更适合由 OS service / 容器编排系统托管
- 日志、权限、自动重启策略应由宿主环境管理

### 应用层

- API
- Web
- Watchdog
- 后续 worker / scheduler / enrichment pipeline

特点：

- 与项目代码版本强关联
- 更适合由项目启动器或应用服务模板托管
- 与 `.env`、运行模式、代码目录绑定更紧

---

## 3. 当前推荐策略

### 本机开发

- PostgreSQL / Redis：优先 OS service
- API / Web / Watchdog：由 `manage.py` 托管
- Qdrant：当前仍为 embedded

### 单机长期运行

- PostgreSQL / Redis / Qdrant / Object Storage：OS service 或容器
- API / Web / Watchdog / Worker：OS service

### 分布式部署

- PostgreSQL / Redis / Qdrant / Object Storage：独立基础设施节点或托管服务
- API / Web / Worker / Watchdog：独立服务组，交给 systemd / k8s / 进程编排器

---

## 4. 平台方案

### Windows

推荐：

- PostgreSQL：Windows Service
- Redis：Windows Service
- API / Web / Watchdog：短期可由 `manage.py` 后台托管；长期建议使用 NSSM 或 Windows Service 包装

当前本机已采用：

- `MyAttentionPostgres`
- `MyAttentionRedis`

适用场景：

- 当前开发机
- 本机长期挂跑
- 需要尽量减少控制台窗口

注意：

- PostgreSQL 在当前权限模型下不适合直接用 `postgres.exe -D ...` 普通进程后台拉起
- 使用 `pg_ctl register` 注册为 Windows Service 更稳定
- Redis 当前二进制支持 `--service-install`
- API / Web / Watchdog 更适合借助 NSSM 这类服务包装器

当前仓库已经提供：

- `scripts/services/windows/install-app-services.ps1`
- `scripts/services/windows/uninstall-app-services.ps1`
- `scripts/services/windows/winsw/MyAttentionApi.xml`

这些脚本是模板，不默认执行。

当前开发机已实际落地：

- `MyAttentionPostgres`
- `MyAttentionRedis`
- `MyAttentionWeb`
- `MyAttentionWatchdog`

当前稳定结论：

- `PostgreSQL / Redis / Web / Watchdog` 适合以 Windows Service 运行
- `API` 在当前机器上仍以 `manage.py` 后台进程模式为稳定方案
- 之前试装过 `MyAttentionApi`，但已验证该 service 方案不稳定，应视为实验路径而不是当前基线

### Linux

推荐：

- PostgreSQL / Redis：systemd service
- API / Web / Watchdog / Worker：systemd service

适用场景：

- 单机服务器
- 云主机
- 未来分布式节点

优点：

- 启动顺序明确
- 日志可接 journald
- 自动重启、依赖、资源限制都成熟

### macOS

推荐：

- 开发机场景：`launchd`
- 应用层服务：`launchd` agent / daemon
- PostgreSQL / Redis：优先 Homebrew service 或 launchd

适用场景：

- 本机开发
- 演示机
- 小型单机常驻环境

---

## 5. 启动控制面与 OS Service 的关系

`manage.py` 不替代 OS service，而是作为统一入口：

- 读取运行模式配置
- 感知某个基础设施是否使用 service 模式
- 提供 `status / health / logs`
- 在本机开发阶段托管应用层进程

同时，当前 `manage.py` 已支持：

- 感知 `api/web/watchdog` 是否被配置成 service 模式
- 在 `status` 中显示 `mode=service|process`
- 在 `health` 中附带 service 名称与状态

也就是说：

- OS service 负责“服务如何存活”
- `manage.py` 负责“项目如何理解这些服务”

---

## 6. 日志设计

### 基础设施层

- PostgreSQL：宿主日志文件或 journald
- Redis：宿主日志文件或 journald

### 应用层

- API：`.runtime/logs/api.log`
- Web：`.runtime/logs/web.log`
- Watchdog：`.runtime/logs/watchdog.log`

要求：

- `manage.py logs <component>` 应优先读取配置中声明的真实日志路径
- service 模式和进程模式都要能被统一查看

---

## 7. 健康检查设计

`manage.py health` 应覆盖：

- PostgreSQL TCP + service state
- Redis TCP + service state
- Qdrant embedded / service
- API `/health`
- `auto_evolution`
- Web 健康页
- Watchdog 存活状态

设计原则：

- 运行存活和服务注册状态要区分
- 不能只看 PID
- 不能只看端口

---

## 8. 启动顺序

推荐顺序：

1. 基础设施层
2. API
3. Watchdog
4. Web
5. 后续 worker / scheduler

说明：

- API 应先于 Watchdog，避免 watchdog 误判首启失败
- Web 依赖 API，但不是强同步依赖

---

## 9. 推荐命令约定

本机开发：

```bash
python manage.py start infra
python manage.py start dev
python manage.py status
python manage.py health --json
```

停止：

```bash
python manage.py stop watchdog
python manage.py stop api
python manage.py stop web
python manage.py stop infra
```

---

## 10. 模板文件约定

仓库内建议保留服务模板：

- Windows: `scripts/services/windows/`
- Linux: `scripts/services/linux/`
- macOS: `scripts/services/macos/`

这些模板的作用：

- 明确正式部署结构
- 减少换机器时的手工猜测
- 方便后续自动化安装

---

## 11. 后续实施建议

下一阶段建议按这个顺序推进：

1. 固化多平台 service 模板
2. 给 `manage.py` 增加 `infra` 的 service / process 模式显示
3. 给部署文档补“安装 service”步骤
4. 后续再考虑把 API / Web / Watchdog 也服务化

---

## 12. 当前结论

当前最合理的架构不是：

- 所有组件都靠黑色控制台窗口跑
- 所有组件都由 `manage.py` 当普通子进程托管

而是：

- 基础设施：OS service / 容器
- 应用层：项目启动器或应用服务模板
- `manage.py`：统一控制面和环境抽象层
