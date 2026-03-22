# 任务与工作流模型研究

> 目标：为 MyAttention 的多大脑协作、持续运行任务、一次性任务、嵌套子任务与恢复机制提供前置研究，而不是先拍实现方案。

---

## 1. 研究问题

MyAttention 后续会同时存在几类工作：

- 持续运行的监督任务
  - 例如进化大脑、信息源监控、质量巡检
- 一次性任务
  - 例如分析一个问题、做一轮研究、完成一次修复
- 嵌套任务
  - 例如“诊断问题”下面再拆“看页面”“看日志”“看数据”“做复核”
- refinement / follow-up
  - 例如基于已有结果继续追问、修正、重做

因此，我们需要的不是普通待办列表，而是：

- 长期运行任务模型
- 子任务模型
- 任务状态机
- artifact 模型
- 可恢复执行模型
- 事件历史模型

---

## 2. 主要外部参考

### 2.1 A2A 协议

参考：

- [A2A Life of a Task](https://a2a-protocol.org/latest/topics/life-of-a-task/)

关键点：

- A2A 区分 `Message` 和 `Task`
- `contextId` 用于把一系列交互 logically group 起来
- `taskId` 标识具体工作单元
- 终态任务不可重启；refinement 应该在同一 `contextId` 下创建新任务
- 支持并行 follow-up task
- artifact 是一等结果对象

最值得吸收的地方：

- 不把“后续请求”硬塞进同一任务，而是让 refinement 成为新任务
- 用 `contextId` 管“同一目标/同一会话”
- 用 `taskId` 管“具体一次执行”
- artifact 独立持久化与版本演进

对 MyAttention 的启发：

- “进化大脑持续运行”不应等于一个无限增长的单任务
- 应该是：
  - 长期监督上下文
  - 周期性派生具体任务
  - 每个子任务都有自己的输入、状态、artifact、终态

---

### 2.2 Temporal

参考：

- [Temporal Workflow](https://docs.temporal.io/workflows)
- [Child Workflows](https://docs.temporal.io/child-workflows)
- [Event History](https://docs.temporal.io/encyclopedia/event-history)

关键点：

- Workflow 是 durable execution，可以持续运行很多年
- 完整执行历史会落在 `Event History`
- 崩溃恢复依赖事件重放
- Child Workflow 适合：
  - 分块大任务
  - 周期逻辑
  - 独立资源建模
- 官方建议：
  - 不要为了代码组织滥用 child workflow
  - 能先用单 workflow + activities 就先这样做

最值得吸收的地方：

- `event history` 必须是一等对象
- 长任务不靠内存活着，而靠持久化历史与可重放状态活着
- 周期逻辑可以通过 child workflow / continue-as-new 控制体量

对 MyAttention 的启发：

- 后续任务系统应至少保留：
  - task event history
  - child task linkage
  - periodic runner / continue-as-new 等价语义
- 当前还不一定要直接引 Temporal
- 但必须吸收它的 durable execution 思想

---

### 2.3 Prefect

参考：

- [Prefect Tasks](https://docs.prefect.io/v3/concepts/tasks)
- [Prefect Flows](https://docs.prefect.io/v3/concepts/flows)
- [Prefect States](https://docs.prefect.io/latest/concepts/states)
- [Prefect Artifacts](https://docs.prefect.io/v3/concepts/artifacts)
- [Prefect Assets](https://docs.prefect.io/v3/concepts/assets)

关键点：

- `task` 是 atomic unit of work
- 每个 task run 都有完整 state lifecycle
- 任务可重试、可缓存、可并发、可超时
- background task 可以异步排队给 worker
- artifact 是面向人类消费的持久结果
- asset 更强调结果对象与依赖关系

最值得吸收的地方：

- 小任务粒度 + 清晰状态 + first-class observability
- artifact 和 asset 分离
- 后台任务与主流程解耦

对 MyAttention 的启发：

- “修复动作”“截图结果”“诊断报告”“研究摘要”都不该只是日志
- 应该是 artifact
- 信息流数据、知识抽取结果、洞察结果，则更接近 asset / fact object

---

## 3. 研究结论

### 3.1 任务至少要分 4 类

后续设计里建议明确区分：

- `daemon_task`
  - 持续监督
  - 例如进化大脑主循环、信息源监控
- `workflow_task`
  - 面向目标的一次工作流
  - 例如“诊断前端异常”
- `unit_task`
  - 最小执行单元
  - 例如“访问 /chat 并截图”
- `refinement_task`
  - 对已完成任务的新一轮修正/追问/重做

这 4 类任务的生命周期和保留策略应该不同。

---

### 3.2 状态机必须显式建模

建议后续任务模型至少具备：

- `created`
- `queued`
- `running`
- `waiting_input`
- `waiting_dependency`
- `paused`
- `degraded`
- `succeeded`
- `failed`
- `canceled`
- `expired`

并记录：

- 状态进入时间
- 状态退出时间
- 状态转换原因
- 谁触发了转换

如果没有显式状态机，复杂 team 协作很快会失控。

---

### 3.3 artifact 必须是一等对象

后续任务输出不应只落日志。

至少要支持这些 artifact 类型：

- `report`
- `screenshot`
- `structured_diagnosis`
- `repair_plan`
- `research_brief`
- `knowledge_extraction`
- `timeline`
- `comparison`

artifact 至少要有：

- `artifact_id`
- `task_id`
- `context_id`
- `type`
- `version`
- `storage_ref`
- `summary`
- `created_at`

---

### 3.4 任务历史应该区分“事件历史”和“结果历史”

参考 Temporal 的 event history 和 Prefect 的 artifact 思路，后续应分成：

- `event_history`
  - 状态变更
  - 子任务生成
  - 重试
  - 失败
  - handoff
- `result_history`
  - 诊断结果
  - 研究结果
  - 产物版本

否则日志会混成一锅。

---

### 3.5 并行和嵌套必须是受控的

研究结论不是“越多并行越好”，而是：

- 并行应有上限
- 嵌套应有层级控制
- 子任务要有预算和超时
- 父任务要知道何时等待、何时放弃、何时降级

也就是说，任务系统后续必须具备：

- fan-out / fan-in
- retry policy
- timeout policy
- cancellation policy
- dependency edges

---

## 4. 对 MyAttention 的直接启发

后续设计时，不应再把：

- 进化大脑
- 信息采集
- 知识加工
- 研究任务

都当成一类任务。

而应按下面方式建模：

- `Context`
  - 一个长期目标或连续会话
- `Task`
  - 一个明确工作单元
- `Artifact`
  - 任务产物
- `Event`
  - 状态变化和执行历史
- `Relation`
  - 父子任务、依赖、refinement、handoff

这会成为后续多大脑协作、长期记忆、知识生命周期管理的基础。

---

## 5. 当前不建议直接做的事

- 现在还不建议直接引入完整 Temporal / Prefect / Argo
- 也不建议先实现一整套复杂分布式 workflow engine

更现实的路径是：

1. 先把内部任务语义设计正确
2. 先把 artifact / event / context / child task 设计正确
3. 再决定是否需要升级为独立工作流引擎

---

## 6. 下一步应产出的正式设计

- `docs/TASK_AND_WORKFLOW_MODEL.md`

重点应包括：

- 任务类别
- 状态机
- parent / child / dependency / refinement
- artifact schema
- event history schema
- daemon task 建模
- 并发与预算控制
