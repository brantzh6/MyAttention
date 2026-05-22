# 任务与工作流模型设计 V1

> 本文档定义 MyAttention 的 `Task and Workflow Model` `V1`。
>
> 目标不是立即实现完整分布式 workflow engine，而是先建立一个：
>
> - 能表达持续任务与一次性任务
> - 能表达父子任务、依赖、refinement
> - 能保存执行历史和中间产物
> - 能支持恢复、重试、降级和复核
> - 能为多大脑协作提供统一任务语义
>
> 的任务基础模型。

---

## 1. 文档定位

本设计解决的问题是：

- 持续运行任务和一次性任务如何统一建模
- 子任务、嵌套任务、后续 refinement 如何管理
- 任务状态机如何定义
- 任务输出与日志如何从“文本记录”升级成结构化对象
- 后续多脑协作如何基于统一任务语义运行

本设计不直接解决：

- 完整多脑协作拓扑
- 模型配置和脑控制层策略
- 全量版本化智能架构
- 完整深度研究工作流

这些属于后续文档：

- `docs/BRAIN_CONTROL_ARCHITECTURE.md`
- `docs/VERSIONED_INTELLIGENCE_ARCHITECTURE.md`
- `docs/DEEP_RESEARCH_ARCHITECTURE.md`

---

## 2. 设计目标

### 2.1 核心目标

- 把 MyAttention 的复杂工作从“零散函数调用”升级成“可追踪任务系统”
- 让长期运行能力和一次性任务共享同一套基础语义
- 让任务结果、任务历史、任务产物成为一等对象
- 让恢复、复核、重试、降级成为模型内能力，而不是临时补丁

### 2.2 架构目标

- 至少支持四类任务：`daemon / workflow / unit / refinement`
- 明确 `Context / Task / Artifact / Event / Relation` 五类核心对象
- 状态机显式建模，不能再依赖隐式布尔字段
- 父子任务和依赖边必须单独表示
- 长任务必须支持 checkpoint / resume 语义

### 2.3 非目标

- 本阶段不实现完整 DAG 调度器
- 本阶段不引入新的重量级工作流基础设施
- 本阶段不追求无限层级并发

---

## 3. 核心纠偏

### 3.1 不能把所有事情都当成一种任务

后续 MyAttention 同时会存在：

- 常驻监控循环
- 一次性分析
- 多步骤研究
- 自动恢复
- 复核与反驳
- 子任务拆解

如果这些都叫“task”但没有进一步分类，系统很快会失控。

### 3.2 长期运行不等于无限增长单任务

“进化大脑持续运行”不应实现成一个永不结束、不断堆日志的单任务。

更合理的做法是：

- 一个长期 `context`
- 下面周期性产生很多具体 `task`
- 每个任务都有自己的状态、产物和终态

### 3.3 输出不能只落日志

诊断、截图、研究摘要、修复建议、比较结果都不应只存在日志文本里。

它们必须成为：

- 可引用
- 可版本化
- 可比较
- 可回溯

的 `artifact`。

---

## 4. 核心对象模型 V1

V1 先固定五类核心对象。

### 4.1 Context

定义：

- 一个长期目标、连续会话或持续工作域

作用：

- 把多次任务执行逻辑地归到同一背景之下

典型例子：

- 某个长期研究主题
- 某个持续监控主题
- 某个系统运行监护上下文
- 某个用户会话

建议字段：

- `context_id`
- `context_type`
- `title`
- `goal`
- `owner_type`
- `owner_id`
- `status`
- `priority`
- `created_at`
- `updated_at`
- `closed_at`
- `metadata`

### 4.2 Task

定义：

- 一次明确的工作执行单元

作用：

- 作为任务调度、状态管理、恢复、复核的核心对象

建议字段：

- `task_id`
- `context_id`
- `task_type`
- `title`
- `goal`
- `status`
- `priority`
- `parent_task_id`
- `initiator_type`
- `initiator_id`
- `assigned_brain`
- `assigned_agent`
- `budget_policy`
- `timeout_policy`
- `retry_policy`
- `created_at`
- `started_at`
- `ended_at`
- `checkpoint_ref`
- `result_summary`
- `metadata`

### 4.3 Artifact

定义：

- 任务产出的结构化结果对象

作用：

- 让结果脱离日志，成为可引用和可比较的对象

建议字段：

- `artifact_id`
- `context_id`
- `task_id`
- `artifact_type`
- `version`
- `parent_version`
- `title`
- `summary`
- `storage_ref`
- `content_ref`
- `created_at`
- `created_by`
- `metadata`

### 4.4 Event

定义：

- 记录任务或上下文生命周期中的状态变化和关键动作

作用：

- 作为 durable execution 的最小事件历史基础

建议字段：

- `event_id`
- `context_id`
- `task_id`
- `event_type`
- `from_status`
- `to_status`
- `triggered_by`
- `reason`
- `payload`
- `created_at`

### 4.5 Relation

定义：

- 显式表示对象间关系

作用：

- 避免父子、依赖、handoff、refinement 全塞进杂项字段

建议字段：

- `relation_id`
- `source_type`
- `source_id`
- `relation_type`
- `target_type`
- `target_id`
- `created_at`
- `metadata`

---

## 5. 任务类型 V1

V1 明确四类任务。

### 5.1 `daemon_task`

定义：

- 常驻型、周期性或持续观察型任务

例子：

- 进化大脑巡检
- 来源质量监控
- 长期监测某主题变化

特点：

- 本身不应无限增长成单一执行记录
- 应依赖 `context` 派生多个具体执行子任务

### 5.2 `workflow_task`

定义：

- 面向一个清晰目标的多步骤任务

例子：

- 诊断前端异常
- 搭建某领域 source plan
- 做一轮深度研究

特点：

- 可以产生子任务
- 可以等待依赖
- 可以经历暂停、降级、复核

### 5.3 `unit_task`

定义：

- 最小执行单元

例子：

- 访问页面并截图
- 调一个接口
- 执行一次搜索
- 跑一次评分

特点：

- 粒度小
- 可重试
- 易观测

### 5.4 `refinement_task`

定义：

- 对已有任务结论进行继续追问、重做、修正或收敛

例子：

- 基于上次诊断再查数据层
- 对某次研究结果增加反例复核
- 重跑某轮投票并切换策略

特点：

- 不是覆盖原任务
- 应作为新任务记录，并通过关系关联到原任务

---

## 6. 状态机 V1

V1 先统一任务状态集。

建议状态：

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

### 6.1 状态含义

- `created`
  - 已创建但尚未进入调度
- `queued`
  - 已进入调度等待执行
- `running`
  - 正在执行
- `waiting_input`
  - 等待外部输入、批准或新信息
- `waiting_dependency`
  - 等待其他任务完成
- `paused`
  - 主动暂停，后续可恢复
- `degraded`
  - 以降级模式运行或部分结果可用
- `succeeded`
  - 成功完成
- `failed`
  - 失败结束
- `canceled`
  - 主动取消
- `expired`
  - 超过有效期或调度窗口

### 6.2 状态转换要求

每次状态转换至少记录：

- `from_status`
- `to_status`
- `triggered_by`
- `reason`
- `timestamp`

不允许：

- 只覆盖当前状态，不保留历史

---

## 7. 关系类型 V1

建议至少支持这些关系类型：

- `parent_of`
- `child_of`
- `depends_on`
- `blocked_by`
- `refines`
- `handoff_to`
- `produced`
- `reviews`
- `retries`
- `supersedes`

作用分别是：

- 父子层级
- 执行依赖
- 后续 refinement
- 大脑/agent 交接
- 任务与产物关联
- 复核关系
- 重试关系
- 版本替换关系

---

## 8. Artifact 模型 V1

V1 不求一次列全所有类型，但先固定几类高价值 artifact。

建议类型：

- `report`
- `screenshot`
- `structured_diagnosis`
- `repair_plan`
- `research_brief`
- `evidence_log`
- `knowledge_extraction`
- `timeline`
- `comparison`
- `decision_summary`

### 8.1 Artifact 原则

- artifact 是人和系统都要消费的正式对象
- artifact 可版本化
- artifact 可以被后续任务引用
- artifact 可以被记忆层召回

### 8.2 Artifact 与对象存储关系

- 大内容进对象存储
- 结构化元数据进 PostgreSQL
- 需要语义召回的摘要和片段可入 Qdrant

---

## 9. Event History 模型 V1

任务系统必须明确区分：

### 9.1 事件历史 `event_history`

用于记录：

- 状态变化
- 子任务创建
- handoff
- 重试
- 超时
- 取消

### 9.2 结果历史 `result_history`

用于记录：

- 诊断结果版本
- 研究结论版本
- 修复建议版本
- 比较结果版本

这样做的原因是：

- 事件历史回答“发生了什么”
- 结果历史回答“得出了什么”

---

## 10. 持续任务建模 V1

这部分是 MyAttention 最特殊的地方。

### 10.1 持续任务不直接等于单任务

例如：

- 进化大脑
- 来源监控
- 某主题持续跟踪

后续应建模成：

- 一个长期 `context`
- 一个 `daemon_task` 作为常驻逻辑入口
- 周期性派生多个 `workflow_task / unit_task`

### 10.2 建议结构

```text
Evolution Context
  -> Evolution Daemon Task
     -> Self-test Workflow Task
     -> UI Probe Workflow Task
     -> Diagnosis Workflow Task
     -> Recovery Workflow Task
     -> Review Workflow Task
```

这样：

- 常驻逻辑可长期存在
- 单次执行不会无限膨胀
- 每轮产物和错误都可追溯

---

## 11. 并发、预算与降级 V1

V1 明确一个原则：

- 并发不是越多越好
- 嵌套不是越深越强

任务模型至少要支持这些控制字段：

- `max_parallel_children`
- `soft_timeout`
- `hard_timeout`
- `retry_limit`
- `cost_budget`
- `token_budget`
- `degrade_policy`
- `fallback_policy`

### 11.1 降级语义

当任务无法按理想方式完成时，允许进入：

- `degraded`

例如：

- 页面巡检失败，但接口自测仍可运行
- 搜索失败，但已存在知识和历史信息可作为保底
- 高能力脑不可用，退回保底脑或规则层

---

## 12. 与记忆和多脑协作的衔接

### 12.1 与记忆架构的关系

- `task memory` 直接绑定任务系统
- `episodic memory` 从任务历史中沉淀
- `procedural memory` 从方法有效性和任务产物中沉淀

### 12.2 与多脑协作的关系

后续多脑协作不应直接围绕自由文本通信展开，而应围绕：

- task assignment
- task handoff
- artifact delivery
- review relation
- dependency relation

也就是说：

- 脑与脑的协作要落在任务模型之上
- 而不是让每个大脑随意互发消息

---

## 13. V1 实施建议

V1 不应直接上复杂工作流引擎，先把内部语义定对。

### 第一优先级

- `context`
- `task`
- `event_history`
- `artifact`
- `relation`

### 第二优先级

- checkpoint / resume 语义
- daemon task 周期派生模型

### 第三优先级

- 预算与并发治理
- refinement / review / handoff 的正式流程化

---

## 14. 演化约束

本设计是 `V1`，必须允许后续调整：

- 任务类型拆分或合并
- 状态机扩展
- relation 类型扩展
- artifact 类型扩展
- 从内建任务系统迁移到更强 workflow engine

不应写死为：

- 固定四类任务永不变化
- 固定状态集永不变化
- 固定单机实现

---

## 15. 设计结论

1. MyAttention 需要的不是普通待办列表，而是可恢复、可追溯的任务系统。
2. `Context / Task / Artifact / Event / Relation` 应成为任务层的一等对象。
3. V1 至少区分 `daemon / workflow / unit / refinement` 四类任务。
4. 持续任务应建模成长期 context + 周期派生任务，而不是无限增长的单任务。
5. 状态机、事件历史、结果产物必须显式建模，不能继续隐含在日志和散字段里。
6. 任务系统是后续多脑协作和进化大脑升级的基础，而不是附属功能。
