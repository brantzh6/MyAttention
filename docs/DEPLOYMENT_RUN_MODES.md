# 部署运行模式设计

> 目标：统一 MyAttention 在不同环境下的运行方式，覆盖当前本机进程开发模式、容器模式和未来分布式部署模式，并明确 setup、自动启动、健康检查和配置化要求。

---

## 1. 设计原则

1. 逻辑架构保持一致，运行模式按环境切换。
2. 当前开发机器以本机进程模式为主，不再假设 Docker 可用。
3. 未来仍保留容器和分布式扩展能力，不为当前便利牺牲长期可扩展性。
4. 启动与健康检查必须跨平台，不绑定单一 OS。
5. 所有启动方式必须配置化，而不是把路径、端口、命令写死在脚本里。

---

## 2. 统一逻辑架构

不论运行模式如何，系统逻辑结构保持：

```text
Frontend / Web
  -> API / FastAPI
     -> PostgreSQL
     -> Redis
     -> Qdrant
     -> Object Storage
```

职责边界：

- PostgreSQL：结构化事实层
- Redis：缓存、短队列、调度状态
- Qdrant：向量与语义检索
- Object Storage：原始对象和大文件

---

## 3. 运行模式

## Mode A：本机进程开发模式

适用：

- 当前开发机器
- 无法稳定运行容器的环境
- 日常联调与调试

运行方式：

- Web：本机 Node.js 进程
- API：本机 Python 进程
- PostgreSQL：本机进程或本机服务
- Redis：本机进程或本机服务
- Qdrant：embedded 或本机服务
- Object Storage：`LocalObjectStore`

当前推荐组合：

- API：本机 Python 进程
- Web：本机 Node.js 进程
- PostgreSQL：本机进程
- Redis：本机进程
- Qdrant：embedded
- Object Storage：本地目录

## Mode B：容器化单机模式

适用：

- 支持 Docker 的开发或测试环境
- 需要环境一致性的机器

运行方式：

- 前端容器
- API 容器
- PostgreSQL 容器
- Redis 容器
- Qdrant 容器
- 可选 MinIO 容器

## Mode C：分布式部署模式

适用：

- 未来生产环境
- 多机部署
- 数据量和后台任务持续增长后

运行方式：

- Web 独立服务
- API 独立服务
- Worker 独立服务
- PostgreSQL 独立实例
- Redis 独立实例
- Qdrant 独立实例
- Object Storage 独立服务（MinIO / S3 / OSS）

---

## 4. 当前选择

当前机器明确采用：

**Mode A：本机进程开发模式**

原因：

- 当前机器无法稳定跑容器
- 项目处于高频开发和联调阶段
- Qdrant 已支持 embedded
- Object Storage 已规划为 `LocalObjectStore`

---

## 5. 启动系统的设计要求

启动系统必须支持：

- 单独 setup
- 单独启动基础设施
- 单独启动 API
- 单独启动 Web
- 一键启动全部开发环境
- 状态查询
- 健康检查

并且要求：

- 同一套逻辑能在 Windows / Linux / macOS 上使用
- 允许每台机器自定义命令、路径、端口和模式

---

## 6. 跨平台实现原则

这里不建议把 PowerShell 或 bash 当主实现。

正确方式应是：

- **主启动器使用 Python**
- PowerShell / bash / `.command` 只作为薄包装入口

原因：

- Python 已经是项目运行前提
- 便于统一进程管理、配置解析、健康检查逻辑
- 避免 Windows / Linux / macOS 维护三套不一致脚本

因此推荐方向：

- 将当前 `manage.py` 从“Windows 专用 API 启动器”升级为“跨平台 devctl”

---

## 7. 配置化要求

启动系统必须支持配置文件，而不是写死：

- Python 路径
- Node/npm/pnpm 路径
- API 端口
- Web 端口
- PostgreSQL 启动命令
- Redis 启动命令
- Qdrant 模式和启动命令
- Object Storage 模式
- 日志目录

推荐使用：

- `config/runtime/local-process.toml`
- `config/runtime/container.toml`
- `config/runtime/distributed.toml`

每台机器可以再加本机覆盖文件，例如：

- `config/runtime/local-process.local.toml`

---

## 8. 健康检查要求

健康检查必须覆盖：

- PostgreSQL
- Redis
- Qdrant
- API
- Web

并能区分：

- 未配置
- 未启动
- 启动但异常
- embedded 模式
- 外部服务模式

健康检查输出应包含：

- 当前运行模式
- 每个组件状态
- 总体状态
- 失败原因

---

## 9. setup 要求

不同环境都应有明确 setup：

### 本机进程模式

- Python 虚拟环境安装
- Node 依赖安装
- 本机 PostgreSQL / Redis / Qdrant 的准备方式
- `.env` 和前端 `.env.local` 模板

### 容器模式

- docker compose / container 启动方式

### 分布式模式

- 各服务拆分部署要求
- 配置项和依赖关系

---

## 10. 当前代码的结论

当前已有的：

- [manage.py](/D:/code/MyAttention/manage.py)
- [start.bat](/D:/code/MyAttention/start.bat)
- [system.py](/D:/code/MyAttention/services/api/routers/system.py)
- [settings.py](/D:/code/MyAttention/services/api/routers/settings.py)

存在的问题：

- `manage.py` 偏 Windows 且只关注 API
- `start.bat` 仍带强 Docker 假设
- 健康检查已有基础，但还没有和“运行模式配置”真正打通

所以后续方向应该是：

- 保留现有能力
- 但把启动器和健康检查收敛到“跨平台 + 配置化 + 多运行模式”

---

## 11. 下一步实施建议

建议按这个顺序推进：

1. 先补部署自动化专项设计
2. 再把 `manage.py` 重构成跨平台启动器
3. 再补各 OS 的薄包装脚本
4. 再把 API 健康检查与运行模式配置接通

---

## 12. 当前实现对齐

上述路线的第一批实现已经完成：

- `manage.py` 已经从单一脚本升级为跨平台控制面
- 运行模式配置已经落到 `config/runtime/*.toml`
- 薄包装脚本已经覆盖 Windows / Linux / macOS
- 健康检查已经支持：
  - PostgreSQL TCP
  - Redis TCP
  - Qdrant embedded/service 区分
  - API `/health`
  - Web 首页/端口
- 健康输出同时支持：
  - 终端可读文本
  - `--json` 机器可读结果

当前还未完全打通的部分是：

- 本机 PostgreSQL 和 Redis 自动拉起命令仍需按机器实际配置
- API 内部健康接口与 `manage.py` 共享同一份运行模式配置还可继续收敛
- distributed mode 还只是控制面预留，不是完整生产编排
