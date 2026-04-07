# IKE 现有代码评估与增量开发计划 v0.1

## 1. 目的

本文档的目标，是把 IKE 的设计体系和当前 MyAttention 仓库真实对齐，让 Codex 基于现有代码继续演进，而不是按从零开始的方式重写系统。重点是明确：哪些部分已经存在、哪些可以直接复用、哪些需要重构、哪些能力应该分阶段补齐。

## 2. 当前仓库的真实情况

当前仓库已经是一个 monorepo，包含 `services/api` 与 `services/web`，同时还有根目录下的运行脚本、设计文档、迁移、基础设施和 PNPM workspace。后端是 FastAPI，前端是 Next.js；文档中的运行时栈已经明确依赖 PostgreSQL、Redis 和 Qdrant。进度记录也已经明确了：先落设计文档，再开始编码，并且正在推进 feed 持久化分层、对象存储抽象、测试先行的改造路线。

因此，IKE 的实现方式应该是“基于 MyAttention 的受控演进”，而不是 greenfield rewrite。

## 3. 已存在且应保留的部分

### 3.1 运行时与打包骨架

建议保留并直接复用：
- 根级 monorepo 结构；
- `services/api` 作为第一阶段主应用运行时；
- `services/web` 作为第一阶段主 UI 运行时；
- 根目录 `package.json` 与 PNPM workspace 约定；
- `manage.py` 与 watchdog 类运行辅助脚本。

### 3.2 后端领域骨架

后端已经具备较好的顶层模块命名空间：
- `feeds/`
- `knowledge/`
- `rag/`
- `llm/`
- `memory/`
- `pipeline/`
- `storage/`
- `notifications/`
- `routers/`
- `tests/`

这些模块本身就可以作为 Information Brain、Knowledge Brain 以及 Evolution Brain 早期实现的种子模块。

### 3.3 现有 router 面已经形成

当前已经存在的 routers 包括：
- chat
- conversations
- evolution
- feeds
- feishu
- memories
- models
- rag
- settings
- system
- testing

这意味着未来 IKE 的 API surface 不需要从空白 OpenAPI 重新设计，而应该在现有 router 面基础上逐步升级。

### 3.4 持久化与测试方向已经启动

根据进度记录和现有测试文件，项目已经开始推进：
- raw ingest key；
- feed persistence helper；
- local object store abstraction；
- collection health；
- task processor system health。

这恰好是挂接 IKE harness 和治理闭环的最佳起点。

## 4. 当前代码到 IKE 的映射

| 现有模块 | 近阶段 IKE 角色 | 说明 |
|---|---|---|
| `feeds/` | Information Brain 核心 | 保持为来源采集与信号抽取中心。 |
| `knowledge/` | Knowledge Brain 种子 | 从 graph 与 web_search 扩展到字段模型、claim 与领域结构。 |
| `rag/` | 知识访问运行时 | 保留为 retrieval engine，不应等同于整个 Knowledge Brain。 |
| `memory/` | Shared Memory 种子 | 从对话记忆扩展到共享记忆对象。 |
| `pipeline/` | Workflow 编排种子 | 在拆独立 worker 之前，适合作为任务与实验流的落点。 |
| `routers/evolution.py` | Evolution Brain 控制入口种子 | 不应推倒重来，而应沿用为第一版进化控制 API。 |
| `routers/testing.py` | Harness 网关种子 | 逐步升级为正式 harness 执行入口。 |
| `storage/` + 对象存储工作 | 共享 artifact 基座 | 应直接保留并加固。 |
| `tests/` | 第一批回归 harness 种子 | 从模块测试扩展为分层 harness 套件。 |

## 5. 不应重写的部分

Codex 不应轻易重写以下区域，除非有明确阻塞：
- FastAPI 应用引导与 router 注册；
- `services/web` 的基础壳；
- 当前 PostgreSQL / Redis / Qdrant 依赖前提；
- 根级 workspace 与 docker 入口；
- 已经在测试和进度记录中体现出的 feed storage / health 相关工作。

原则很简单：保留可运行骨架，向内重构，而不是先拆掉。

## 6. 当前代码与目标 IKE 之间的缺口

### 6.1 概念层缺口

当前仓库已经在文档层表达了三脑模型，但还没有完全落成系统级契约。缺口主要包括：
- Thinking Model 一等对象；
- Paradigm 一等对象；
- Meta-Reasoning Governance 状态；
- Task / Experiment / Decision 引擎契约；
- Shared Object envelope 与记忆晋升规则。

### 6.2 架构层缺口

当前尚未完全成形的架构点包括：
- 后端内部稳定 package 边界；
- 在 routers 与 workers 之间共享的 schemas 层；
- API model 与 domain model 的明确分离；
- 后台 workflow 的事件契约；
- harness worker 与 governance review job 的运行时拓扑。

### 6.3 产品层缺口

当前系统已经有 chat、feeds、memory、knowledge base 类功能，但 IKE 还缺：
- paradigm library 检视面；
- research card 生命周期；
- experiment review；
- decision promotion / adoption history；
- governance review dashboard。

## 7. 推荐的增量演进路线

### 阶段 A - 稳定并包裹现有实现

优先做：
- 冻结已经足够合理的外部目录名；
- 在现有后端内新增 shared schema 包；
- 先定义 canonical object envelope，而不是一次性重写所有实现；
- 加入薄兼容层，让 routers 可以逐步返回新 envelope。

### 阶段 B - 原地重构核心模块

下一步做：
- 将 feed persistence 与 raw ingest 工作收口到稳定 service interface 后面；
- 将 `knowledge/graph.py` 与 `rag/engine.py` 提升为明确的 domain service；
- 在现有模块旁新增 `workflow/` 与 `governance/`；
- 将 `routers/testing.py` 接到正式 harness run 与 artifact 模型上。

### 阶段 C - 补齐 IKE-first 能力

再往后补：
- Thinking Model registry；
- Domain Paradigm registry；
- Task / Experiment / Decision engine；
- Governance review jobs；
- research card 相关 UI 与 admin console。

### 阶段 D - 只在压力真实时再拆分

仅在 modular monolith 已稳定之后，再考虑：
- 当异步负载足够大时拆 worker runtime；
- 当评测成本足够高时拆 harness runner；
- 当治理 UI 足够复杂时拆 console app。

## 8. 给 Codex 的实施指引

Codex 在实现时应遵循：
- 第一轮优先“新增 package”，而不是大规模 destructive move；
- 保持现有 router 继续可用，在其背后引入新 service；
- 深度重构前先写 migration shim；
- 保留并扩展现有测试；
- 大 workflow 变化前先落 schema-first 契约。

推荐的第一波顺序是：
1. 在 `services/api` 或新的 `packages/` 下创建 `schemas/`、`objects/`、`workflow/`、`governance/`；
2. 用 service interface 包裹现有 feed 与 knowledge 模块；
3. 让 routers 依赖 service interface，而不是直接落本地实现逻辑；
4. 增加第一批 harness artifact 与 governance review record；
5. 合同稳定后，再补 UI 视图。

## 9. 成功标准

本文档的成功标准，是让 Codex 开始 coding 时能同时满足三件事：
- 不按 greenfield rewrite 处理；
- 不退回到 router-centric 逻辑堆积；
- 不破坏当前已经可运行的骨架。

最终目标不是另起一个新项目，而是让 MyAttention 通过显式契约、共享对象、治理闭环与 harness 驱动，逐步演进为 IKE。
