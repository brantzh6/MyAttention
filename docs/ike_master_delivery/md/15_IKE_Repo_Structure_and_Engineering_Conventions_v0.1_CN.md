# IKE 仓库结构与工程约定 v0.1

## 1. 目的

本文档定义 IKE 第一阶段可实施版本的工程约定。目标是给 Codex 和人类开发者一套稳定的仓库形态、命名规则、质量门和日常协作方式，使系统在开发时不发生结构性漂移。

这份文档强调可执行性。它不重复顶层理念，而是把前面已经定义的系统边界、数据契约、API 接口面和治理规则，落实为仓库级规范。

## 2. 设计原则

仓库应该优先优化以下目标：
- 在 modular monolith 形态下快速迭代；
- 在服务拆分前先建立强模块契约；
- 以 schema-first 方式开发共享对象和工件；
- 以英文 Markdown 作为长期 LLM 协作主源；
- 通过 harness、测试和审查工件建立确定性的质量门。

仓库需要明确避免：
- 过早微服务化；
- 业务逻辑散落在 router、脚本和 notebook 中；
- 同一对象在多个模块重复定义 schema；
- 工作流状态隐藏在临时文件里；
- 仅靠 prompt 承载领域规则。

## 3. 推荐仓库形态

建议起步采用 monorepo：一个主运行时，加一组可复用内部 package。

```text
ike/
  apps/
    api/
    worker/
    console/
  packages/
    core/
    schemas/
    objects/
    memory/
    information/
    knowledge/
    evolution/
    thinking_models/
    governance/
    workflow/
    harness/
    observability/
    common/
  docs/
    architecture/
    specs/
    product/
    decisions/
  data/
    seeds/
    fixtures/
    eval/
    paradigm_packs/
  scripts/
  infra/
  tests/
  .github/
```

这个形态适合 A/B 阶段，同时为未来走向 C/D 保留清晰路径。

## 4. 顶层目录约定

### 4.1 `apps/`
运行时入口，保持轻量。

- `apps/api/`：HTTP 与内部控制 API。
- `apps/worker/`：后台任务、调度、编排入口。
- `apps/console/`：管理与治理界面；如果前端延后，也至少保留占位 package。

### 4.2 `packages/`
承载可持续业务逻辑的内部包。

建议包括：
- `core/`：共享抽象、ID、结果包络、错误类型。
- `schemas/`：规范化 Pydantic / JSON schema。
- `objects/`：对象构造、生命周期辅助、验证封装。
- `memory/`：共享记忆读写服务与投影逻辑。
- `information/`：采集、来源管理、信号提取、watchlist。
- `knowledge/`：实体抽取、关系构建、claim 管理、领域模型。
- `evolution/`：新概念跟踪、方向发现、采纳规划。
- `thinking_models/`：思考模型、范式包、模型注册表。
- `governance/`：元推理策略、评审、升级/冻结/退休规则。
- `workflow/`：任务、实验、决策、编排策略。
- `harness/`：suite、评分器、报告、fixture、评测运行时。
- `observability/`：日志、指标、trace、审查仪表盘。
- `common/`：只有真正跨域的通用工具才允许进入。

### 4.3 `docs/`
文档是一级资产。

建议结构：
- `docs/architecture/`：系统级架构文档。
- `docs/specs/`：模块规范、schema、接口说明。
- `docs/product/`：产品界面与用户流程。
- `docs/decisions/`：架构决策记录 ADR。

### 4.4 `data/`
用于启动、测试和评测的小规模受控数据。

建议内容：
- `seeds/`：默认来源、starter paradigms、starter thinking models。
- `fixtures/`：确定性开发 fixture。
- `eval/`：benchmark 与 harness 数据集。
- `paradigm_packs/`：按领域组织的范式启动包。

### 4.5 `infra/`
基础设施定义：
- docker compose；
- queue / worker 配置；
- secrets 模板；
- 环境模板；
- 部署说明。

### 4.6 `tests/`
跨 package 的契约与集成测试。各 package 也可保留本地 unit tests。

## 5. 语言与文档策略

主源策略如下：

- 可持续编辑主源：英文 Markdown；
- 翻译层：中文 Markdown；
- 评审/导出层：中文 DOCX；
- 文件名：ASCII only。

后续架构、产品和治理文档都应遵守该规则。目标是同时兼顾 LLM 迭代效率与当前团队的评审可读性。

## 6. 命名规则

### 6.1 文件与目录
- Python 文件和目录使用 lowercase snake_case；
- 文件名只用 ASCII；
- 尽量使用语义清晰的完整名称，少用缩写。

示例：
- `task_engine.py`
- `model_registry.py`
- `research_task_service.py`

### 6.2 类与类型
- 类和 DTO 使用 PascalCase；
- 领域对象命名应明确，如 `ResearchTask`、`ThinkingModel`、`DecisionRecord`。

### 6.3 ID
所有主要对象使用带类型前缀的 ID，避免面向应用层时只暴露匿名 UUID。

示例：
- `src_...`
- `obs_...`
- `ent_...`
- `rel_...`
- `tsk_...`
- `exp_...`
- `dec_...`
- `mdl_...`
- `prg_...`

## 7. 模块所有权与依赖方向

依赖方向必须保持稳定并尽量向内收敛。

建议规则：
- `apps/*` 可以依赖所有 package，但不应承载核心业务逻辑；
- `workflow/` 可以编排 `information/`、`knowledge/`、`evolution/`、`thinking_models/`、`governance/`、`harness/`；
- `governance/` 可以读取各域状态，但应主要通过显式 policy 和 decision interface 写入；
- `schemas/` 与 `core/` 不依赖领域包；
- `common/` 不能演化成杂物仓。

禁止模式：
- `information/` 直接依赖 `console/`；
- `schemas/` 导入运行时 service；
- router 内联治理决策；
- 只靠 prompt 表达 policy。

## 8. package 内部布局

每个 package 尽量采用可预测结构。

建议布局：
```text
package_name/
  __init__.py
  models.py
  service.py
  repository.py
  policies.py
  selectors.py
  adapters.py
  errors.py
  tests/
```

如果 package 较大，也可采用更显式的子域结构：

```text
knowledge/
  entities/
  relations/
  claims/
  field_models/
  services/
  repositories/
  policies/
  tests/
```

关键不在唯一形式，而在边界清晰。

## 9. Schema-first 开发规则

任何跨越以下边界的对象，都必须有规范 schema：
- package 边界；
- API 边界；
- workflow artifact 边界；
- 持久化对象边界；
- harness artifact 边界。

规范 schema 统一放在 `packages/schemas/` 下。

建议结构：
```text
packages/schemas/
  envelope/
  sources/
  observations/
  entities/
  relations/
  claims/
  tasks/
  experiments/
  decisions/
  thinking_models/
  paradigms/
  governance/
  harness/
```

各 package 不得各自重复定义。

## 10. 持久化约定

建议的存储分工：
- relational database：规范对象和 workflow 状态；
- object storage：大体积 artifact、报告、快照、原始抓取；
- vector store：embedding 与 retrieval surface；
- cache / queue：短期执行状态。

规则：
- 持久化领域状态不能只存在于队列里；
- object storage key 必须可追溯回规范 ID；
- durable artifact 必须携带 schema version；
- 关键写操作应在合适时机发出结构化事件。

## 11. API 与 router 约定

HTTP router 只做轻量翻译层。

规则：
- request validation -> service call -> structured response；
- router 不承载隐藏副作用；
- router 不直接拼 repository 逻辑；
- 长任务返回 task ID 和 progress handle。

建议 API 分组：
- `/sources`
- `/observations`
- `/entities`
- `/relations`
- `/claims`
- `/tasks`
- `/experiments`
- `/decisions`
- `/thinking-models`
- `/paradigms`
- `/governance`
- `/harness`
- `/health`

## 12. Workflow 与 job 约定

Job 必须是显式对象，而不是隐式代码路径。

必要特性：
- idempotent handler；
- 尽可能支持 resumable steps；
- typed payload；
- 结构化状态流转；
- 持续输出 review artifact。

长流程建议采用：
- task record；
- substep state；
- artifact emission；
- event trail。

## 13. Prompt 与模型集成约定

Prompt 是配置，不是业务规则唯一载体。

规则：
- prompt 放在可版本化文件中，不埋在字符串里；
- prompt 必须引用显式对象字段和 policy 输入；
- 模型选择要记录理由与执行元数据；
- 尽量强制 structured output schema。

建议路径：
```text
packages/thinking_models/prompts/
packages/evolution/prompts/
packages/harness/prompts/
```

## 14. 测试与 harness 约定

测试应分四层：
- package 级 unit tests；
- schema / interface contract tests；
- workflow integration tests；
- system-level harness suites。

建议目录：
```text
tests/
  contract/
  integration/
  workflow/
  harness/
```

各 package 仍可保留局部 unit tests。

## 15. 配置约定

采用显式 typed config。

建议形态：
- `env.example`
- `settings/base.py`
- `settings/local.py`
- `settings/test.py`
- `settings/prod.py`

规则：
- 不允许静默回退到近似生产配置；
- secrets 不提交；
- feature flag 必须命名并文档化；
- 实验性 flag 尽量映射到 task 或 decision。

## 16. 日志与可观测性约定

主要动作都要输出结构化日志。

最小公共字段：
- timestamp
- request_id
- task_id
- object_id
- module
- action
- outcome
- model_id（如适用）
- policy_id（如适用）

重点事件：
- source ingestion
- entity merge
- claim update
- task creation
- experiment start/end
- decision promotion/freeze/retire
- harness run summary
- model selection record

## 17. 工程评审节奏

建议节奏：
- 每日：活跃任务与 blocker review；
- 每周：harness 变化、schema 变化、模块漂移检查；
- 双周：paradigm pack 与 thinking-model 变更评审；
- 每月：架构简化与 service boundary 回顾。

重大边界变更必须配一份简短 ADR，存放在 `docs/decisions/`。

## 18. 分支与版本控制约定

建议方式：
- 短生命周期功能分支；
- PR 聚焦单一关注点；
- schema 变化必须附 migration 说明；
- 行为变化要在同一 PR 同步更新文档。

Commit 风格示例：
- `feat(tasks): add experiment acceptance policy`
- `docs(governance): define freeze and retire states`
- `refactor(knowledge): split relation merge service`

## 19. 需要避免的反模式

Codex 和人类开发者都应避免：
- 模块边界还不稳定就先拆很多服务；
- 不演化规范 schema，而是新增平行 schema；
- 把生命周期流转埋在 UI 代码中；
- 把评测 artifact 与规范业务状态混在一起；
- 让 notebook 变成生产逻辑；
- 使用巨大 `utils.py` / `helpers.py`；
- 把英文 Markdown 主规范当可有可无。

## 20. Codex 应先建设什么

第一波：
1. 仓库骨架；
2. 规范 schema package；
3. API app shell；
4. worker app shell；
5. task / experiment / decision 核心对象；
6. source / observation 对象；
7. harness runner 骨架；
8. config / logging 基础；
9. docs 与 ADR 模板。

第二波：
1. knowledge 对象服务；
2. thinking model registry；
3. governance policies；
4. bootstrap data loader；
5. 第一批故事模板。

## 21. 演化路径

该仓库形态针对 A 和 B 阶段优化，不应误解为最终形态。

预期演化：
- Stage A：单体部署下的 modular monolith；
- Stage B：更强 package 边界与 async 执行；
- Stage C：对 worker-heavy 或 evaluation-heavy 路径做选择性运行时分离；
- Stage D：当 portfolio-style governance 足够成熟时，再演化出更独立的运行面。

仓库结构应支持该路径，而不是过早强推。

## 22. 最终建议

把仓库结构当作治理工具，而不只是目录树。如果仓库形态有纪律，Codex 才能安全生成代码；如果仓库形态模糊，前面所有文档都会打折。

因此第一版实现应该优先保证：
- 稳定 package seam；
- 规范 schema；
- 轻量 app entry point；
- 显式 workflow 对象；
- harness 驱动开发；
- 英文 Markdown 作为长期主规范层。
