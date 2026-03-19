# MyAttention 项目工作进度

## 当前阶段任务：信息流数据架构规划

### 本阶段新增项目级约束

- 已新增项目总计划：`docs/PROJECT_MASTER_PLAN.md`
- 已明确后续研发运作方式：
  - 先确认方案
  - 先落设计文档
  - 再开始编码
  - 编码后必须测试与验证
  - 结果必须更新文档和进度记录
- 该约束适用于后续信息流、知识大脑、自我进化等所有中大型改造

### 背景

- 当前信息流主链路仍以运行时缓存为主
- 后续目标已经升级为：
  - 信息大脑：趋势分析、深度总结、来源质量评估、推荐
  - 知识大脑：长期知识沉淀、知识抽取重跑、跨学科组织
  - 自我进化：基于真实事实层进行监控、评测和优化
- 因此必须先完成信息流数据分层与可扩展架构设计，再开始实施改造

### 已完成

#### 1. 信息流数据专项架构设计

- 新增文档：`docs/FEED_DATA_ARCHITECTURE.md`
- 明确了四层数据模型：
  - 原始层 `raw_ingest`
  - 标准条目层 `feed_items`
  - 富化分析层 `feed_enrichments`
  - 聚合分析层 `feed_aggregates`

#### 1.1 存储层专项架构设计

- 新增文档：`docs/STORAGE_ARCHITECTURE.md`
- 明确了长期存储层的正式组成：
  - PostgreSQL：结构化事实与分析结果
  - Redis：缓存、队列缓冲、调度状态
  - Qdrant：语义检索与向量索引
  - Object Storage：原始对象、大文件、中间产物
- 明确了对象存储抽象：
  - 开发阶段：`LocalObjectStore`
  - 生产阶段：`MinIO / S3 / OSS`
- 明确了迁移路径：
  - 先对象存储抽象
  - 再原始层元数据
  - 再主链路持久化
  - 再聚合与分布式扩展

#### 1.2 研发方法与质量体系

- 新增文档：`docs/ENGINEERING_METHOD.md`
- 明确了项目级开发方法：
  - 主线优先
  - 方案先行
  - 设计先行
  - 编码后必须验证
  - 结果必须归档
- 明确了测试方法：
  - 不同改动级别对应不同最低测试要求
  - 测试结果必须可记录、可追踪、可被进化系统消费
- 明确了进化路径：
  - 可见性
  - 自动发现
  - 问题闭环
  - 质量驱动优化
  - 策略级自适应
- 明确了非功能设计要求：
  - 可维护性
  - 可测试性
  - 可观测性
  - 可扩展性
  - 性能、稳定性、安全性、可部署性

#### 1.3 变更与版本管理

- 新增文档：`docs/CHANGE_MANAGEMENT.md`
- 新增项目级变更日志：`CHANGELOG.md`
- 明确了后续必须记录的内容：
  - 项目版本变更
  - 架构与数据模型变更
  - API 兼容性变更
  - 测试基线变更
  - 自我进化策略变更
- 明确了自我进化能力本身也必须版本化和留痕：
  - 日志规则
  - 去重规则
  - 测试计划
  - 告警阈值
  - 自动任务策略
  - 提示词与策略模板

#### 1.4 gstack skill 受控试用

- 已研究并安装以下 gstack skill：
  - `plan-eng-review`
  - `plan-design-review`
  - `design-consultation`
  - `review`
  - `qa`
  - `document-release`
- 新增试用方案文档：`docs/GSTACK_TRIAL_PLAN.md`
- 新增评估记录文档：`docs/SKILL_EVALUATION_LOG.md`
- 已明确：
  - 哪些 skill 适合当前项目
  - 哪些环节使用
  - 如何评估效果
  - 何时应缩减或停止使用

#### 1.5 项目推进路线图

- 新增文档：`docs/PROJECT_EXECUTION_ROADMAP.md`
- 将后续推进拆成明确阶段：
  - Phase 1：对象存储与原始层
  - Phase 2：信息流事实层落库
  - Phase 3：富化、聚类、embedding
  - Phase 4：趋势分析与深度总结
  - Phase 5：知识大脑结构化升级
  - Phase 6：进化大脑强化
  - Phase 7：分布式部署准备
- 明确了每个阶段如何与现有代码对接，而不是推倒重来

#### 1.6 部署运行模式与启动器设计

- 新增文档：`docs/DEPLOYMENT_RUN_MODES.md`
- 新增文档：`docs/DEPLOYMENT_AUTOMATION_DESIGN.md`
- 明确了三种运行模式：
  - 本机进程开发模式
  - 容器化单机模式
  - 分布式部署模式
- 当前机器明确采用本机进程开发模式
- 已明确后续实现原则：
  - 启动器以 Python 为主
  - PowerShell / bash / macOS `.command` 仅做薄包装
  - 所有路径、端口、命令都通过配置文件管理
  - 健康检查需区分 local-process / container / distributed 与 embedded / service 模式


#### 2. 确认长期架构方向

- 原始层按对象存储抽象设计
- 开发阶段可用本地文件系统实现
- 后续生产/多机阶段切换到 MinIO / S3 / OSS
- PostgreSQL 作为信息流事实库
- Redis 负责缓存与任务缓冲
- Qdrant 负责语义检索和相似性能力

#### 3. 确认实施顺序

- Phase 1：对象存储抽象 + 原始层落地
- Phase 2：信息流主链路落库
- Phase 3：富化、聚类、embedding
- Phase 4：趋势分析与深度总结
- Phase 5：分布式部署与多机扩展

### 下一步

- 已新增 Phase 1 实施计划：`docs/PHASE1_OBJECT_STORE_IMPLEMENTATION_PLAN.md`
- 已完成首批 Phase 1 代码落地：
  - 新增 `services/api/storage/` 下的对象存储抽象
  - 新增 `LocalObjectStore`
  - 新增 `raw_ingest` ORM 模型
  - 新增 `migrations/006_raw_ingest.sql`
  - 新增 `services/api/feeds/raw_ingest.py`
  - 将 `/api/feeds/import` 接成“原始层持久化 + 现有缓存注入”双落点
- 已完成基础验证：
  - Python 语法编译通过
  - `LocalObjectStore` 读写删验证通过
- 已继续补强 Phase 1 基础层能力：
  - `LocalObjectStore` 现已为对象保存 `.meta.json` 侧车元数据，`head()` 可返回 `content_type / content_encoding`
  - `raw_ingest` 对象 key 已改为“安全前缀 + 稳定哈希”格式，避免把 URL 直接写进 Windows 文件名
  - `storage.__init__` 与 `feeds.__init__` 已改为惰性导出，减少包入口对运行期依赖的硬耦合
  - 已新增最小自动化测试：
    - `services/api/tests/test_local_object_store.py`
    - `services/api/tests/test_raw_ingest_keys.py`
  - 已完成真实链路烟测：
    - `POST /api/feeds/import` 返回 `200`
    - `raw_ingest.object_key` 已写入新格式
    - 本地对象层已同时生成数据文件和 `.meta.json`
- 当前阻塞：
  - API 被 watchdog 重新拉起后，`manage.py` 当前会丢失 `api` 的 PID/metadata 记录
  - 这会影响“停止/重启/状态追踪”的一致性，但不影响当前业务可用性
- 紧接着要做：
  - 收敛 API 被 watchdog 拉起后丢失 `manage.py` PID/metadata 的问题
  - 已新增 Phase 2 实施设计：`docs/PHASE2_FEED_FACT_STORE_IMPLEMENTATION_PLAN.md`
  - 已完成 Phase 2 第一批落地：
    - 新增 `services/api/feeds/persistence.py`
    - `/api/feeds/import` 已升级为 `raw_ingest + feed_items + cache` 双写
    - 导入响应新增 `persisted`
    - 导入时会自动解析或创建 `sources` 记录
    - 已对齐 `FeedItem.metadata` 和 `sources` 相关 PostgreSQL enum 的 ORM 映射
  - 已完成真实烟测：
    - `POST /api/feeds/import` 返回 `status=ok, imported=1, persisted=1`
    - `feed_items` 可查到新写入记录
    - `sources` 可查到对应导入来源记录
    - `feed_items.metadata.raw_ingest_id` 可追溯回原始层
  - 已完成 Phase 2 第二批：
    - `/api/feeds` 已支持 `cache / db / hybrid` 三种读取模式
    - 默认读取已切到兼容性的 `hybrid`
    - `source_id` 过滤已兼容抓取器 source key 和数据库 source 记录
    - 导入链路已改为逐条 nested transaction，避免单条失败污染整个 session
  - 已完成真实读取烟测：
    - `GET /api/feeds?backend=db` 返回数据库事实层内容
    - `GET /api/feeds?backend=hybrid&source_id=phase2/smoke` 返回导入样本
    - `GET /api/feeds?source_id=phase2/smoke` 默认请求也已正常工作
  - 下一步进入可运行版收口：优先强化“自我进化 + 信息收集”闭环

## 当前任务：排查知识库检索问题

### 问题描述
- 用户创建了 openclaw 知识库，添加了网页索引
- 大模型对话无法查找到知识库内容

### 已完成的修复

#### 1. 系统健康检查 API
- 文件: `services/api/routers/settings.py`
- 添加了 `/api/settings/system` 端点
- 测试所有配置的 LLM 模型（通义千问、GLM、Kimi、Claude、OpenAI）

#### 2. 前端通知设置页面 - 系统状态监控
- 文件: `services/web/components/settings/notifications-config.tsx`
- 添加了系统状态面板，显示：
  - 数据库服务 (PostgreSQL, Redis, Qdrant)
  - 核心服务 (MyAttention API)
  - 外部依赖 (各 LLM 模型)
- 每30秒自动刷新

#### 3. 知识库检索问题排查

**问题原因**：知识库搜索的 `score_threshold=0.5` 太高
- 实际检索到的文档相似度分数在 0.5-0.6 之间
- 阈值 0.5 导致所有结果被过滤掉

**修复**：
- 文件: `services/api/routers/chat.py`
- 修改了第 264-271 行，将 `score_threshold` 从默认 0.5 降低到 0.3
- 添加了调试日志 `log(f"KB {kb_id} 找到 {len(results)} 个结果")`

### 日志文件位置
- `services/api/chat_debug.log` - 聊天日志

### 常用命令
```bash
# 查看 KB 相关日志
tail -30 "C:\Users\Jiu You\code\MyAttention - 副本\services\api\chat_debug.log" | grep -E "KB|知识库"

# 查看服务健康状态
curl -s http://localhost:8000/api/settings/system | python -m json.tool

# 测试知识库搜索
curl -s "http://localhost:8000/api/rag/knowledge-bases/070f7b1e/search?query=openclaw" | python -m json.tool
```

### 待验证
- 知识库检索修复是否生效（需要用户再次测试）
- 确认对话时能看到知识库内容

## 1.7 跨平台部署启动器首批落地

### 已完成

- 将根目录 `manage.py` 升级为跨平台运行控制面
- 新增运行模式配置：
  - `config/runtime/local-process.toml`
  - `config/runtime/container.toml`
  - `config/runtime/distributed.toml`
- 新增本机 override 示例：
  - `config/runtime/local-process.local.example.toml`
- 新增前端环境模板：
  - `services/web/.env.local.example`
- 新增跨平台脚本：
  - PowerShell: `setup/start-dev/status/check-health/stop-dev`
  - shell: `setup/start-dev/status/check-health/stop-dev`
  - macOS `.command`: `start-dev/status/check-health/stop-dev`
- 将旧 `start.bat` 收敛为薄包装入口，不再硬编码 Docker 检查和端口

### 当前能力

- `python manage.py setup`
- `python manage.py start api|web|infra|dev`
- `python manage.py stop api|web|dev`
- `python manage.py status [--json]`
- `python manage.py health [--json]`

### 已验证

- `python -m py_compile manage.py`
- `python manage.py setup`
- `python manage.py status --json`
- `python manage.py health --json`

### 当前限制

- 当前 Redis 使用的是 Windows 本地开发兜底实现 `tporadowski/redis 5.0.14.1`，适合开发，不是长期生产方案
- `local-process.local.toml` 当前已经包含这台机器的本机命令，但换机器后仍需重新配置
- `run_with_loop.py` 仍是非 UTF-8 历史文件，当前本机启动已绕过它，后续应单独清理
- `auto_evolution` 当前仍挂在 API 进程内部，不是独立 supervisor；如果未来要做跨进程自愈，再单独设计
- Windows 本机运行的 API 已恢复为由 `manage.py` 准确记录 `pid/meta/log_path`

### 本机执行结果更新

- 已为当前机器补充 `config/runtime/local-process.local.toml`
- 已接入本机 PostgreSQL 启动命令：
  - `D:/tools/postgresql17/pgsql/bin/pg_ctl.exe`
  - 数据目录：`D:/tools/postgres-data`
- 已下载并接入本机 Redis 开发进程：
  - `D:/tools/redis/Redis-x64-5.0.14.1/redis-server.exe`
  - 配置文件：`D:/tools/redis/redis.local.conf`
- 已执行 `migrations/006_raw_ingest.sql`
- 已启动本机 API 与 Web
- 已验证：
  - `GET /health` = 200
  - `GET /api/settings/system` = 200
  - `GET /settings/sources` = 200
  - `GET /settings/knowledge` = 200
- 已收敛后台运行方式：
  - API / Web 不再依赖黑色控制台窗口维持
  - 启动器日志落盘到 `.runtime/logs/`
  - `manage.py logs <component>` 可直接查看启动日志
  - `manage.py health --json` 已聚合 `auto_evolution`
- 已补强 watchdog 与基础设施托管：
  - 新增 `runtime_watchdog.py` 独立守护进程
  - `manage.py` 已支持 `start/stop watchdog`
  - `manage.py` 已支持 `start/stop infra`、`start/stop postgres`、`start/stop redis`
  - Windows 停止进程已改为优先使用 `taskkill /T /F`
  - 本机 API 默认命令已切到非 `--reload` 后台模式
- 已调整本机启动方案：
  - `python manage.py start dev` 默认只拉起 `api + web + watchdog`
  - PostgreSQL / Redis 作为显式基础设施，需单独 `python manage.py start infra`
  - `watchdog` 默认只守护 `api/web/auto_evolution`，不自动重启 `postgres/redis`
  - API 现已恢复为由 `manage.py` 准确记录 `pid/meta/log_path`
  - Windows 当前机型已进一步把 PostgreSQL / Redis 注册为 Windows Service，用于减少黑色控制台窗口
- 已补服务化部署设计与模板：
  - `docs/SERVICE_DEPLOYMENT_ARCHITECTURE.md`
  - `scripts/services/windows/`
  - `scripts/services/linux/`
  - `scripts/services/macos/`
- `manage.py status` 现已显式展示 `postgres/redis/qdrant` 的运行模式：
  - `service`
  - `embedded`
  - 后续可扩展 `process`
- `manage.py` 现已支持 `api/web/watchdog` 的可选 service 模式识别与控制：
  - 默认仍使用 `process`
  - 若配置 `use_service = true`，则 `start/stop/status/health/logs` 会切换到 service 认知
- 已新增 Windows 应用层服务模板脚本：
  - `scripts/services/windows/install-app-services.ps1`
  - `scripts/services/windows/uninstall-app-services.ps1`
- 已确认黑色窗口与 API `process` 模式直接相关
- 已确认 `MyAttentionApi` 在当前机器上属于失败后残留的实验 service，而不是稳定方案：
  - 当前稳定运行模式为：`postgres/redis/web/watchdog = service`
  - `api = manage.py` 后台进程
  - `manage.py status` / `health` 已补充“残留 service”识别，避免后续误判
- 已额外修复前端构建阻塞：
  - `services/web/lib/api-client.ts`
  - `services/web/components/settings/knowledge-base-manager.tsx`
  - `npm run build` 已通过

## 2026-03-19 Mainline Update

### Collection Health And Self-Evolution

- Added `services/api/feeds/collection_health.py` to compute durable feed collection snapshots from `raw_ingest` and `feed_items`.
- Wired collection health into `auto_evolution`, so the system now records collection metrics alongside log health and self tests.
- Added `GET /api/evolution/collection-health` and `GET /api/feeds/health`.
- Added `Feed Collection` service details into `GET /api/settings/system`.

### Import Durability And Traceability

- `/api/feeds/import` now updates `raw_ingest.parse_status` to `persisted`, `duplicate`, or `error`.
- `raw_ingest.response_meta` now records `source_id`, `feed_item_id`, and whether the feed item was newly created.
- Performed a one-time compatibility backfill for legacy `raw_saved` rows that could be matched to existing `feed_items`.

### Verified

- `python -m unittest services/api/tests/test_collection_health.py`
- `POST /api/feeds/import` = 200
- `GET /api/evolution/collection-health` = 200
- `GET /api/feeds/health` = 200
- `GET /api/settings/system` = 200
- `python manage.py health --json` = `healthy`

## 2026-03-19 Mainline Update 2

### Collection Health To Task Center

- Added `build_collection_health_issue(...)` in `services/api/feeds/collection_health.py`.
- `auto_evolution` now converts non-healthy collection snapshots into deduplicated `system_health` tasks via the existing task processor.
- Healthy snapshots do not create tasks, so the problem center only records actionable collection degradations.

### Verified

- `python -m unittest services/api/tests/test_collection_health.py`
- `python manage.py health --json` = `healthy`
- Querying `tasks` with `source_type=system_health` and `source_id=feed_collection` returned `0` while collection health stayed healthy.

## 2026-03-19 Mainline Update 3

### Source-Level Collection Diagnostics

- Collection health snapshots now include `pending_sources_1h` and `error_sources_24h` so degraded states can be traced to concrete sources.
- Collection-health-generated tasks now carry those source lists in both description and `source_data`, making the issue center actionable without extra digging.

### Verified

- `python -m unittest services/api/tests/test_collection_health.py`
- `GET /api/evolution/collection-health` now returns source-level diagnostics such as `pending_sources_1h`.
- `python manage.py health --json` = `healthy`

## 2026-03-19 Frontend Runtime Fix

### Root Cause

- The local Windows machine was still serving `services/web/.next/standalone/server.js` through the residual `MyAttentionWeb` Windows service.
- Port `3000` was therefore returning an old standalone build instead of the current source-driven frontend, which caused the visible style and layout drift.
- `manage.py` also had two Windows-specific launcher issues:
  - stale `web.pid` values could be misread as alive because PID probing relied on `os.kill(pid, 0)`
  - npm script commands resolved incorrectly in detached process mode on Windows

### Fixes

- Removed the residual `MyAttentionWeb` service from the local development machine.
- Updated `manage.py` so process-mode web startup stops any residual `web` service before launching the current frontend.
- Replaced Windows PID liveness checks with `tasklist`-based validation and clear stale pid/meta state before starting a component.
- Fixed npm command generation on Windows so process-mode web startup resolves to `npm.cmd run dev`.
- Cleared the local web override back to process-mode source startup instead of a hard-coded standalone command.

### Verified

- `python -m py_compile manage.py`
- `python manage.py start web`
- listener on port `3000` now runs `node_modules/next/dist/server/lib/start-server.js`
- `GET /settings/sources` now returns dev-mode HTML instead of the stale standalone service output
- `python manage.py health --json` = `healthy`

## 2026-03-19 MVP Loop Closure

### Self-Evolution MVP

- `system_health` tasks are no longer passive records for feed collection degradation.
- `services/api/feeds/task_processor.py` now:
  - auto-processes `auto_processible` `system_health` tasks
  - derives a recovery plan for `feed_collection_health`
  - triggers `/api/pipeline/trigger`
  - re-checks `/api/evolution/collection-health`
  - records before/after state and remediation details into task history
- `services/api/feeds/collection_health.py` now marks feed collection degradation issues as `auto_processible=True`.
- Added an operational MVP status endpoint at `/api/evolution/mvp-status` to summarize:
  - auto evolution state
  - self-test result
  - collection health
  - pipeline scheduler status
  - recent task actions
  - active blockers for trial runs

### Verified

- `D:\\code\\MyAttention\\.venv\\Scripts\\python.exe -m unittest services/api/tests/test_collection_health.py services/api/tests/test_task_processor_system_health.py`
- `GET /api/evolution/mvp-status` = `200`
- `GET /api/evolution/status` = `200`
- `GET /api/evolution/collection-health?fresh=true` = `200`
- `python manage.py health --json` = `healthy`
- Current MVP status reports:
  - `trial_ready = true`
  - `pipeline_status = running`
  - `collection_health.summary.status = healthy`
  - `self_test.healthy = true`
