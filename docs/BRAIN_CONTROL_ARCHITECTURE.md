# 大脑控制架构设计 V1

> 本文档定义 MyAttention 的 `Brain Control Architecture` `V1`。
>
> 目标不是一次性做出终局智能体团队，而是先建立一个：
>
> - 分层明确
> - 角色清晰
> - 协作可控
> - 可降级保底
> - 可被后续进化和替换
>
> 的多大脑控制平面。

---

## 1. 文档定位

本设计解决的问题是：

- MyAttention 需要哪些大脑层级
- 不同大脑负责什么
- 不同大脑之间通过什么方式协作
- 多大脑如何围绕任务系统协同，而不是自由混聊
- 当高阶大脑失效时，系统如何维持基本运行

本设计不直接解决：

- 全量任务表结构与状态落库实现
- 全量模型与供应商配置细节
- 全量知识结构和深度研究工作流
- 全量版本化智能体系

这些属于后续或并行文档：

- `docs/TASK_AND_WORKFLOW_MODEL.md`
- `docs/MEMORY_ARCHITECTURE.md`
- `docs/DEEP_RESEARCH_ARCHITECTURE.md`
- `docs/VERSIONED_INTELLIGENCE_ARCHITECTURE.md`

---

## 2. 设计目标

### 2.1 核心目标

- 把“智能对话模型配置”升级为“多大脑控制平面”
- 让用户面对单一入口，但系统内部可以多脑分工和协作
- 保证系统在高阶智能失效时仍有保底运行能力
- 为信息大脑、知识大脑、进化大脑提供统一的角色和协作框架

### 2.2 架构目标

- 采用分层结构，而不是平面 agent 列表
- 顶层使用 `hierarchical supervisor`
- 局部任务允许受控 `parallel gather / review / debate / handoff`
- 协作必须建立在 `task / artifact / event / relation` 之上
- 所有角色和路由必须可版本化、可替换、可扩展

### 2.3 非目标

- 本阶段不追求所有脑都自动自治
- 本阶段不追求无限制 many-to-many agent 通信
- 本阶段不直接绑定某个具体 framework 实现

---

## 3. 核心纠偏

### 3.1 智能对话不是大脑本体

对话只是用户入口之一。

它不能继续承担：

- 主控调度
- 研究编排
- 方法选择
- 恢复仲裁
- 长期演化判断

### 3.2 不是“多几个 agent”就叫 team

真正重要的不是数量，而是：

- 谁判断任务类型
- 谁拆解任务
- 谁负责执行
- 谁负责复核
- 谁负责仲裁
- 谁负责降级和保底

### 3.3 不能把协作建立在自由文本上

后续协作必须围绕：

- task
- artifact
- event
- relation

如果只靠大脑之间互发自然语言，后面无法审计、回放和演化。

---

## 4. 分层架构 V1

V1 采用三层控制结构。

### 4.1 脑干层 `Brainstem`

职责：

- 保底运行
- 基础健康检查
- 最低限度恢复
- 配置加载
- 简单规则路由
- 基础任务触发

特点：

- 不依赖高阶推理
- 可以规则化
- 可以在高阶大脑失效时继续工作

典型能力：

- watchdog
- health checks
- service restart
- basic fallback routing
- minimal alerting

### 4.2 小脑层 `Cerebellum`

职责：

- 任务调度
- 状态协调
- 重试
- 并发控制
- budget / timeout / degrade 控制
- artifact 和 event 的流转管理

特点：

- 偏执行和协调
- 不负责高阶判断
- 是多脑协作的稳定执行层

典型能力：

- task scheduler
- retry policy
- dependency resolution
- handoff control
- degrade / fallback orchestration

### 4.3 皮层层 `Cortex`

职责：

- 问题建模
- 方法选择
- 任务拆解
- 多脑协作
- 归因与仲裁
- 研究与决策

特点：

- 高阶智能层
- 可被多模型和多角色驱动
- 允许局部并行、辩论和复核

---

## 5. 大脑角色 V1

V1 先定义一个 `chief` 和若干 `specialist brains`。

### 5.1 `chief_brain`

职责：

- 判断问题类型
- 选择思维模型和方法
- 创建任务与子任务
- 选择参与脑
- 汇总结果
- 仲裁分歧

它是顶层 supervisor，不直接承担全部执行。

### 5.2 `dialog_brain`

职责：

- 面向用户表达
- 把内部研究和协作结果转成可理解输出
- 管理会话节奏和上下文

### 5.3 `source_intelligence_brain`

职责：

- 理解主题需要关注什么
- 发现候选来源和候选对象
- 评估 authority / signal / frontier / community
- 更新 source plan

### 5.4 `research_brain`

职责：

- 面向主题、综述、机制、决策问题执行结构化研究
- 构建 source plan / evidence log / fact base

### 5.5 `knowledge_brain`

职责：

- 抽取实体、关系、概念
- 组织学科、主题、时间和事实结构
- 管理长期知识结构

### 5.6 `evolution_brain`

职责：

- 观察系统运行
- 做自测、归因、恢复建议、方法评估
- 生成问题和优化路径

注意：

- `evolution_brain` 本身也更像一个 team，而不是单一脑

### 5.7 `coding_brain`

职责：

- 代码定位
- 修改
- 测试
- 修复
- 变更验证

---

## 6. 进化大脑内部团队 V1

`evolution_brain` 在 V1 中应先拆成以下角色：

- `chief_evolution_brain`
  - 拆解问题、分配任务、回收结果、决定是否升级问题
- `ui_probe_agent`
  - 真实界面检查
- `log_analysis_agent`
  - 日志模式分析
- `data_health_agent`
  - 数据链路和事实层健康分析
- `recovery_agent`
  - 恢复建议与自动恢复
- `review_agent`
  - 对归因和恢复方案做二次校验
- `method_evaluator_agent`
  - 判断当前方法、测试和策略是否有效

这说明：

- 进化大脑不是监控面板
- 它是一个内部协作 team

---

## 7. 协作拓扑 V1

V1 不采用完全自由网络，而采用“顶层收敛、局部开放”的结构。

### 7.1 顶层：`hierarchical supervisor`

规则：

- 所有用户面任务先进入 `chief_brain`
- 所有持续系统性任务先进入对应长期 `context`
- 由 `chief_brain` 或 `chief_evolution_brain` 决定派工

优点：

- 可控
- 易审计
- 易回放
- 易降级

### 7.2 局部：受控并行 `parallel gather`

适用场景：

- 多源收集
- 多模型比较
- 多页面巡检
- 多案例对比

规则：

- 并行任务数要有预算和上限
- fan-out / fan-in 由小脑层控制

### 7.3 局部：`review / challenge`

适用场景：

- 关键决策
- 故障归因
- 研究结论
- 方法评估

规则：

- 一个脑提出判断
- 另一个脑负责反驳或复核
- 最终由主管脑裁决

### 7.4 局部：`sequential handoff`

适用场景：

- 研究交给表达
- 诊断交给恢复
- 搜索建源交给订阅规划

规则：

- handoff 必须基于 artifact，而不是只靠口头文本

### 7.5 禁止默认自由群聊

V1 不建议用完全 `group chat / swarm` 作为主协作方式。

原因：

- 易失控
- 易污染上下文
- 难审计
- 不利于长期任务

---

## 8. 协作协议 V1

V1 不必实现标准 A2A，但内部语义应吸收其核心思想。

后续脑之间协作至少要显式携带：

- `context_id`
- `task_id`
- `problem_type`
- `thinking_framework`
- `method`
- `artifact_refs`
- `requested_output`
- `budget_policy`
- `timeout_policy`

也就是说：

- 协作以任务为中心
- artifact 是正式交接对象
- 自由消息只是辅助，不是事实载体

---

## 9. 配置层 V1

后续不能再只有聊天页的模型配置。

需要一个正式的 `Brain Control Plane` 配置模型。

### 9.1 `brain_profile`

定义：

- 一个大脑是谁、负责什么、默认使用什么能力

建议字段：

- `brain_id`
- `role`
- `description`
- `capabilities`
- `default_models`
- `fallback_models`
- `tool_policy`
- `cost_policy`
- `latency_policy`
- `risk_policy`
- `status`
- `version`

### 9.2 `brain_route`

定义：

- 什么问题交给哪个脑

建议字段：

- `route_id`
- `problem_type`
- `thinking_framework`
- `primary_brain`
- `supporting_brains`
- `review_brain`
- `fallback_brain`
- `version`

### 9.3 `brain_policy`

定义：

- 预算、联网、执行权限、超时、降级等策略

### 9.4 `brain_fallback`

定义：

- 主脑失效时如何退回保底路径

---

## 10. 降级与保底 V1

这部分是多脑系统必须有的“脑干”能力。

### 10.1 保底原则

当高阶脑不可用时，系统应至少保持：

- 基础运行
- 基础监控
- 基础恢复
- 基础采集
- 基础响应

### 10.2 典型降级路径

- `chief_brain` 不可用
  - 退回规则化问题分类与默认路由
- `evolution_brain` 不可用
  - 退回脑干层健康检查和 watchdog
- `source_intelligence_brain` 不可用
  - 退回已存在 source plan + 低频 review
- `research_brain` 不可用
  - 退回已有知识 / 历史信息 / 基础搜索
- 高级模型不可用
  - 退回低成本保底模型或规则流程

### 10.3 保底层不能依赖高阶层

这是硬约束：

- 脑干层必须独立于高阶脑而存在
- 否则“大脑失灵时维持运转”只是空话

---

## 11. 与主线模块的关系

### 11.1 信息大脑

后续应主要由：

- `source_intelligence_brain`
- `research_brain`
- `knowledge_brain`

协同驱动。

### 11.2 知识大脑

后续应主要由：

- `knowledge_brain`
- `research_brain`
- `chief_brain`

协同驱动。

### 11.3 进化大脑

后续应主要由：

- `chief_evolution_brain`
- `ui_probe_agent`
- `log_analysis_agent`
- `data_health_agent`
- `recovery_agent`
- `review_agent`

协同驱动。

---

## 12. V1 实施建议

V1 不应一次实现全部团队自治，而应分步落地。

### 第一优先级

- 明确脑干 / 小脑 / 皮层分层
- 明确 `chief_brain` 和 `evolution_brain team`
- 明确 `brain_profile / brain_route / brain_policy / brain_fallback`

### 第二优先级

- 把任务系统和脑路由接通
- 把对话入口从“直接调用模型”升级为“调用脑控制层”

### 第三优先级

- 局部引入 review / challenge / debate 模式
- 局部引入 agent-assisted retrieval

---

## 13. 演化约束

本设计是 `V1`，不是终局 brain taxonomy。

后续必须允许：

- 新增脑角色
- 合并或拆分已有脑
- 调整协作拓扑
- 替换 supervisor 策略
- 调整降级路径

不应写死为：

- 固定几个脑永不变化
- 固定一个 framework 永不替换
- 固定某个模型提供商永不改变

---

## 14. 设计结论

1. MyAttention 需要的是大脑控制平面，而不是聊天模型配置页升级版。
2. V1 采用 `Brainstem / Cerebellum / Cortex` 三层结构。
3. 顶层协作应采用 `hierarchical supervisor`，而不是默认自由群聊。
4. 多脑协作必须围绕 `task / artifact / event / relation` 展开，而不是围绕自由文本展开。
5. `evolution_brain` 本身应视为一个内部 team，而不是单一 agent。
6. 脑干层保底运行能力是硬约束，不能依赖高阶脑。
