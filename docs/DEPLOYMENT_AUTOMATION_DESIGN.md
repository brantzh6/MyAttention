# 部署自动化与开发启动器设计

> 目标：为 MyAttention 设计一套跨平台、配置化、可扩展的启动与健康检查系统，支持当前本机进程开发模式，并为容器和分布式模式保留统一控制面。

服务化部署专项设计见：

- `docs/SERVICE_DEPLOYMENT_ARCHITECTURE.md`

---

## 1. 设计目标

- Windows / Linux / macOS 都能使用
- 当前机器优先支持本机进程开发模式
- 容器模式和分布式模式共用同一套控制思路
- 所有路径、端口、启动命令都可配置
- 启动、停止、状态、健康检查统一入口

---

## 2. 总体方案

采用：

- Python 主启动器
- TOML 配置文件
- OS 薄包装脚本

结构建议：

```text
manage.py
config/runtime/
  local-process.toml
  container.toml
  distributed.toml
scripts/
  dev/
    start-dev.ps1
    start-dev.sh
    start-dev.command
```

其中：

- `manage.py`：真正的控制面
- `config/runtime/*.toml`：运行模式定义
- `scripts/dev/*`：只负责调用 `manage.py`

---

## 3. `manage.py` 目标能力

建议支持命令：

- `setup local-process`
- `start infra`
- `start api`
- `start web`
- `start dev`
- `stop api`
- `stop web`
- `status`
- `health`

后续可扩展：

- `start worker`
- `health --json`
- `logs api`

---

## 4. 配置文件设计

推荐使用 `toml`，因为：

- 可读性好
- 注释友好
- Python 3.11 可直接读取

示例结构：

```toml
[runtime]
mode = "local-process"
api_port = 8000
web_port = 3000

[api]
workdir = "services/api"
python = ".venv/Scripts/python.exe"
entry = "run_with_loop.py"

[web]
workdir = "services/web"
command = "npm run dev"

[postgres]
host = "localhost"
port = 5432
start_command = ""

[redis]
host = "localhost"
port = 6379
start_command = ""

[qdrant]
mode = "embedded"
host = "localhost"
port = 6333
start_command = ""
```

---

## 5. 健康检查设计

`manage.py health` 应检查：

- PostgreSQL TCP
- Redis TCP
- Qdrant embedded / service
- API `/health`
- Web 端口或首页

输出既要支持：

- 终端人读
- 后续 `--json` 机器读

---

## 6. 与现有 API 健康检查的关系

保留现有：

- `/api/settings/system`
- `/api/system/health`

但要明确分工：

- `manage.py health`：开发者侧、本机环境级健康检查
- API health endpoints：系统运行时、前端和外部依赖可见性

两者应共享同一个“运行模式认知”，避免一个说 embedded 正常，另一个误报异常。

---

## 7. 当前阶段的最优先实现

当前先不做大而全自动化。

第一阶段只做：

1. `manage.py` 读取运行模式配置
2. 支持 `start api / start web / status / health`
3. 支持本机进程模式
4. Qdrant embedded 识别
5. 可选 infra 启动命令

第二阶段再做：

- `start dev`
- `start infra`
- stop / logs / json 输出
- 跨平台薄包装脚本

---

## 8. 风险控制

### 风险 1：过早写三套脚本

控制：

- 主逻辑只写 Python 一套

### 风险 2：启动命令写死

控制：

- 所有路径和命令都进配置文件

### 风险 3：把当前机器特例做成全局默认

控制：

- 当前机器只是 `local-process` 的一个实例
- 不是长期架构前提

---

## 9. 当前建议结论

结论非常明确：

- 当前不应该继续扩展 `start.bat`
- 也不应该单独写一套 Windows-only 启动方案
- 正确做法是把 `manage.py` 升级成跨平台、配置化启动器

这才符合项目长期方向。

---

## 10. 当前已落地能力

当前仓库已经落地：

- `manage.py setup`
- `manage.py start api|web|infra|dev`
- `manage.py stop api|web|dev`
- `manage.py status [--json]`
- `manage.py health [--json]`

当前还同时提供了跨平台薄包装脚本：

- Windows PowerShell:
  - `scripts/dev/setup.ps1`
  - `scripts/dev/start-dev.ps1`
  - `scripts/dev/status.ps1`
  - `scripts/dev/check-health.ps1`
  - `scripts/dev/stop-dev.ps1`
- Linux:
  - `scripts/dev/setup.sh`
  - `scripts/dev/start-dev.sh`
  - `scripts/dev/status.sh`
  - `scripts/dev/check-health.sh`
  - `scripts/dev/stop-dev.sh`
- macOS:
  - `scripts/dev/start-dev.command`
  - `scripts/dev/status.command`
  - `scripts/dev/check-health.command`
  - `scripts/dev/stop-dev.command`

这些脚本都只做一件事：

- 自动定位仓库根目录
- 调用 `manage.py`

---

## 11. 当前配置落点

当前运行配置已经落到：

- `config/runtime/local-process.toml`
- `config/runtime/container.toml`
- `config/runtime/distributed.toml`
- `config/runtime/local-process.local.example.toml`

当前开发机推荐方式：

1. 复制 `config/runtime/local-process.local.example.toml`
2. 命名为 `config/runtime/local-process.local.toml`
3. 按机器实际情况配置：
   - Python 路径
   - npm/pnpm/yarn 路径
   - PostgreSQL 启动命令
   - Redis 启动命令
   - 迁移命令

---

## 12. 当前开发机最小工作流

本机进程开发模式下，建议工作流已经明确为：

1. `python manage.py setup`
2. 根据需要补本机 override 配置
3. `python manage.py start infra`
4. `python manage.py start dev`
5. `python manage.py status`
6. `python manage.py health --json`

这套工作流的目标是：

- Windows / Linux / macOS 共用同一套控制逻辑
- 当前机器可以不用 Docker
- 未来切容器或分布式时，只切运行模式和配置，不重写控制面

---

## 13. 后台运行与日志原则

当前开发机运行控制面已经收敛为：

- 服务不依赖黑色控制台窗口维持
- API / Web / Infra 启动命令统一走后台进程
- 启动器负责把托管进程 stdout / stderr 落到固定日志文件

当前日志目录：

- `.runtime/logs/api.log`
- `.runtime/logs/web.log`
- `.runtime/logs/postgres.log`
- `.runtime/logs/redis.log`
- `.runtime/logs/watchdog.log`

当前建议的日常操作：

- `python manage.py status`
- `python manage.py health --json`
- `python manage.py logs api`
- `python manage.py logs web`
- `python manage.py logs watchdog`

不再依赖“看黑窗有没有报错”。

---

## 14. 自我监控组件托管原则

自我监控 / 自我修复能力当前不单独起一个额外的外部黑窗进程，而是：

- 跟随 API 生命周期自动启动
- 由 `Auto Evolution System` 托管
- 通过 `/api/evolution/status` 暴露状态
- 由 `manage.py health` 聚合为 `auto_evolution`

这样做的目标是：

- 减少额外窗口和人工盯盘
- 让启动器和系统状态页都能看到它是否正常运行
- 保持后续可扩展到独立 supervisor 的空间

同时，本机运行控制面已经增加独立 `watchdog` 托管：

- `python manage.py start watchdog`
- `python manage.py stop watchdog`
- `python manage.py start infra|postgres|redis`
- `python manage.py stop infra|postgres|redis`

也就是说，当前自我监控能力分成两层：

- API 内部的 `auto_evolution`
- API 外部的 `runtime_watchdog`

前者负责日志分析、自测和问题归并，后者负责进程与基础设施巡检、重启和运行态守护。

对于 `local-process` 模式，当前建议的默认策略是：

- `start dev` 只负责 `api + web + watchdog`
- `postgres/redis` 由 `start infra` 显式启动
- `watchdog` 默认只守护 `api/web/auto_evolution`
- `watchdog` 不默认自动重启 `postgres/redis`

这样做是为了避免 Windows 本机环境下基础设施进程被重复拉起、控制台包装进程残留和进程归属不清的问题。

对于 Windows 本机开发机，当前进一步建议：

- PostgreSQL / Redis 尽量使用 Windows Service 模式
- `manage.py` 通过配置里的 `use_service/service_name/log_path` 感知并控制这些服务
- 应用层仍由 `manage.py` 托管
- 基础设施日志分别直接读取：
  - PostgreSQL: `server.log`
  - Redis: `redis.log`

应用层后续可平滑升级为 service 模式：

- `api.use_service = true`
- `web.use_service = true`
- `watchdog.use_service = true`

当前仓库已提供 Windows NSSM 模板脚本，但默认仍保持关闭，避免在开发机上过早切换。

这样可以进一步减少黑色控制台窗口，并让本机开发环境更接近长期可维护的运维方式。
