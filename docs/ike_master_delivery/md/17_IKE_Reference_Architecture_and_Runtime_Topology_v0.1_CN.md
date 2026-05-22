# IKE 参考架构与运行时拓扑 v0.1

## 1. 目的

本文档定义了一个适合从 MyAttention 演进到 IKE 的参考架构与运行时拓扑。它的目标不是做概念包装，而是给 Codex 一个明确的工程运行图，说明系统在保留当前 FastAPI + Next.js + PostgreSQL + Redis + Qdrant 前提下，应该如何逐步落地。

## 2. 当前运行时基线

当前仓库已经清楚地围绕这些前提组织：
- `services/api` 中的 FastAPI 后端；
- `services/web` 中的 Next.js 前端；
- PostgreSQL 作为主要结构化存储；
- Redis 作为缓存与队列/状态基座；
- Qdrant 作为向量索引；
- 正在引入对象存储抽象以承载原始对象和大体积 artifact。

IKE 的参考架构不应推翻这些选择，而应在这些选择之上叠加能力。

## 3. 推荐的 v0 运行时拓扑

```text
Browser / Admin UI
        |
        v
 Next.js console (services/web)
        |
        v
 FastAPI app (services/api)
   |        |         |         |
   |        |         |         +--> Notification adapters
   |        |         +------------> LLM / embedding providers
   |        +----------------------> Redis (queue, cache, locks)
   +-------------------------------> PostgreSQL (objects, tasks, decisions)
                 |
                 +---------------> Qdrant (semantic retrieval)
                 |
                 +---------------> Object store (raw artifacts, reports)

 Background worker(s)
   - ingestion jobs
   - enrichment jobs
   - harness runs
   - experiment runs
   - governance review jobs
```

第一阶段应该保持 modular monolith + 多进程角色，而不是直接进入分布式微服务。

## 4. 逻辑架构分层

### 4.1 产品与控制层

面向用户与运营者的表面包括：
- research workspace；
- entity / paradigm 视图；
- governance review console；
- harness report；
- system / health 视图。

初期运行时映射建议：
- `services/web` 负责人类界面；
- FastAPI routers 负责机器控制接口。

### 4.2 应用接口层

第一阶段仍应保持 router-based 控制面，按下面几组组织：
- system / settings；
- information flows；
- knowledge / retrieval；
- conversations / memories；
- evolution / governance；
- testing / harness。

### 4.3 Domain services 层

这里应该成为后续新增工作的重心。核心业务逻辑应该逐步从 routers 下沉到 domain services。

推荐的服务组：
- Information services
- Knowledge services
- Thinking model services
- Governance services
- Workflow services
- Harness services
- Memory projection services

### 4.4 Artifact 与 memory 层

所有持久化输出都应表达为一等对象，而不是散落文件。该层包括：
- PostgreSQL 中的关系对象与状态；
- Qdrant 中的 embedding 与向量检索；
- 对象存储中的原始输入与生成文件；
- Redis 中的短期状态与队列。

### 4.5 执行层

后台执行应与 HTTP 请求生命周期分离。v0 阶段可以仍在同一仓库甚至同一代码库中，但要有独立入口：
- job worker；
- scheduler / tick runner；
- harness runner；
- offline rebuild command。

## 5. 三脑到运行时的映射

### 5.1 Information Brain

运行时职责：
- source registration；
- watchlist；
- crawler / feed collector；
- raw ingest；
- normalization；
- source quality scoring；
- signal extraction。

推荐的初始映射：
- 当前 `feeds/` 模块；
- 当前 `routers/feeds.py`；
- Redis 队列；
- PostgreSQL 归一化条目存储；
- 对象存储中的 raw capture。

### 5.2 Knowledge Brain

运行时职责：
- entity extraction；
- relation creation；
- claim management；
- field model update；
- retrieval / grounding；
- memory promotion。

推荐的初始映射：
- 当前 `knowledge/` 与 `rag/`；
- `routers/rag.py`、chat 相关 routers 和后续 knowledge routers；
- PostgreSQL 结构化对象存储；
- Qdrant 检索；
- 可选 offline rebuild worker。

### 5.3 Evolution Brain

运行时职责：
- concept emergence tracking；
- self-relevance analysis；
- direction finding；
- task generation；
- experiment planning；
- adoption decision；
- governance review。

推荐的初始映射：
- 当前 `routers/evolution.py` 与 `routers/testing.py` 作为控制面种子；
- 后续新增 `workflow/`、`governance/`、`thinking_models/` 服务；
- experiment 和 review jobs 通过 worker 执行。

## 6. 共享底座拓扑

### PostgreSQL

作为 canonical state store，用于：
- entities；
- relations；
- claims；
- tasks；
- experiments；
- decisions；
- governance reviews；
- source / observation metadata。

### Redis

用于：
- job queueing；
- 临时 workflow 状态；
- dedupe lock；
- rate limit state；
- cache projection。

不允许 Redis 成为 durable workflow truth 的唯一来源。

### Qdrant

用于：
- document chunk embedding；
- retrieval index；
- 选配的 claim / observation / paradigm note 语义检索。

### Object storage

用于：
- raw capture；
- HTML snapshot；
- imported document；
- harness report；
- experiment artifact；
- generated export。

## 7. 进程拓扑建议

### v0 进程集合

第一阶段推荐的进程角色：
- `api`：FastAPI server
- `web`：Next.js dev/prod server
- `worker`：background worker loop
- `scheduler`：periodic tick runner

这仍然可以在 docker compose 和本地脚本下运行。

### v1 可选扩展

只有在需要时再加：
- `harness-worker`
- `offline-rebuild-worker`
- `governance-review-worker`
- `console-admin`（当 UI 复杂到需要拆分时）

## 8. 最关键的运行流

### Flow 1 - Information ingest
1. register / update source；
2. enqueue fetch；
3. persist raw artifact；
4. normalize to observation / item；
5. optional enrich；
6. emit downstream workflow event。

### Flow 2 - Knowledge update
1. 选择新增或变更 artifact；
2. 抽取 entity / relation / claim；
3. 写入 structured object；
4. 更新 retrieval index；
5. 发布 knowledge update record。

### Flow 3 - Evolution trigger
1. 发现 concept 或 anomaly signal；
2. 进行 self-relevance evaluation；
3. 生成或更新 task；
4. 必要时设计 experiment；
5. 记录 decision 或 governance review 要求。

### Flow 4 - Harness and governance
1. 执行目标 harness suite；
2. 生成 evaluation artifact；
3. 将结果挂接到 experiment / review；
4. 更新 model / decision policy。

## 9. 必须避免的架构反模式

不要让运行时演化成下面这些形态：
- HTTP routers 直接承载大量核心业务逻辑；
- 用 Qdrant 代替 durable structured state；
- 用 Redis 存长期 workflow 真相；
- 所有 job 混成一个 giant worker 且没有 artifact discipline；
- prompts 成为唯一的领域逻辑表达；
- 在 modular contracts 未稳定前就过早微服务化。

## 10. 给 Codex 的实施优先级

Codex 应按下面顺序落地运行时：
1. 先稳定 1 个 API 进程和 1 个 worker 进程；
2. 统一 DB、Redis、Qdrant、对象存储适配器；
3. 引入类事件化的内部 workflow contract；
4. 将 harness execution 与 request handling 隔离；
5. 只有在 task / experiment 状态稳定后，再补 governance review jobs。

## 11. 成功标准

当系统可以做到下面这些事时，这份参考架构就算成功：
- durably ingest information；
- 将其提升为 structured knowledge；
- 由新信号触发 task 与 experiment；
- 通过 harness run 对自身进行评测；
- 在不推倒当前技术栈的情况下完成以上流程。

这才是从 MyAttention 向 IKE 过渡的正确架构桥梁。
