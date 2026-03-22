# 大脑控制层与多智能体体系研究

> 目的：在正式设计 `Brain Control Plane` 之前，先研究多智能体分工、A2A 通信、长任务管理、嵌套子任务、长期记忆与回忆效率等关键问题，避免过早下方案。

---

## 1. 研究背景

当前 MyAttention 已经有：

- 信息大脑的部分采集和存储能力
- 知识大脑的部分知识库、RAG、记忆能力
- 进化大脑的监控、自测、UI 巡检与问题中心能力

但系统仍缺一个正式的“大脑控制层”：

- 现在模型配置仍偏向“智能对话”
- 还没有把不同任务映射到不同大脑角色
- 还没有定义持续任务、一次性任务、嵌套子任务的统一管理模型
- 还没有定义长期记忆如何分层、如何高效召回、如何避免遗忘

因此，这次研究的目标不是立即定实现，而是回答：

1. 多大脑协作应该参考什么模式？
2. Agent 之间如何通信更稳？
3. 长期运行任务和嵌套子任务如何建模？
4. 长期记忆应该如何分层和保存？
5. 在复杂大脑失效时，系统靠什么兜底？

---

## 2. 外部参考研究

### 2.1 Claude Code / Claude Agent SDK

参考：

- [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents)
- [Building agents with the Claude Agent SDK](https://claude.com/blog/building-agents-with-the-claude-agent-sdk)

关键结论：

- `subagent` 的核心价值有两个：
  - 隔离上下文
  - 并行处理子任务
- 每个 subagent 可以有：
  - 独立系统提示
  - 独立工具权限
  - 独立模型选择
  - 独立上下文窗口
- Anthropic 明确区分了两种东西：
  - `subagents`：同一会话内的专长代理
  - `agent teams`：跨独立会话协作的多代理系统

对 MyAttention 的启发：

- “智能对话”不应该等于唯一大脑，而应该只是入口。
- 适合引入“主管大脑 + 专业大脑”的分工：
  - 主管大脑负责拆解、调度、仲裁
  - 研究大脑、对话大脑、编码大脑、进化大脑分别执行专长任务
- 独立上下文非常关键，否则复杂任务会迅速污染主上下文。

限制：

- Claude 的 subagent 机制本身更偏单产品内部编排，不是通用的系统级任务控制模型。
- 它对“长期运行任务”和“跨大量任务持久状态”不是完整答案。

#### 关于 agent teams / 协作

这里需要特别区分：

- `subagent`：偏“隔离上下文 + 分工执行”
- `agent team`：偏“独立上下文 + 明确协作协议 + 编排与仲裁”

从 Claude Code / Claude Agent SDK 的资料看，真正有价值的不是“多开几个 subagent”，而是这些协作特征：

1. 并行研究
   - 多个 subagent 可并行工作
   - 主代理只接收摘要而不是原始上下文
   - 适合信息搜集、模块分析、证据汇总
2. 串行链式协作
   - 一个 subagent 先分析
   - 主代理抽取关键信息
   - 再交给下一个 subagent继续
3. 可恢复协作
   - subagent 可以 resume
   - 适合长任务分阶段推进
4. 协作生命周期事件
   - `SubagentStart`
   - `SubagentStop`
   - 适合做审计、记录、状态同步

但 Claude Code 也有一个非常重要的限制：

- subagent **不能再生成 subagent**

这意味着：

- Claude 风格的 subagent 适合“主管编排 -> 专家执行”
- 但不适合无限层级嵌套协作
- 如果要真正做 agent teams，需要一个上层 orchestrator / supervisor 负责：
  - 任务拆解
  - 上下文分发
  - 状态汇总
  - 冲突仲裁
  - 结果合成

这对 MyAttention 很重要，因为进化大脑不可能只是一个单体 agent，它更像：

- `chief_evolution_brain`
  - 负责任务拆解、派工、回收结果、判断是否升级问题
- `ui_probe_agent`
  - 负责真实界面检查
- `log_analysis_agent`
  - 负责日志模式识别
- `recovery_agent`
  - 负责恢复建议与自动恢复
- `review_agent`
  - 负责对归因与恢复方案做二次校验

也就是说，进化大脑应该是一个 team，而不是一个 agent。

但是，从 Anthropic 这一组资料里也能看到一个边界：

- Claude 给了“专长代理 + 委派”的能力
- 但没有给出一整套成熟的、可直接照搬的多 agent 协作控制平面

因此，Claude 资料更适合作为：

- 角色隔离
- 上下文隔离
- 主管委派

的参考，而不是完整的 team 协作总答案。

---

### 2.1.1 AutoGen 的协作模式

参考：

- [AutoGen Core](https://microsoft.github.io/autogen/dev/user-guide/core-user-guide/index.html)
- [Group Chat](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/group-chat.html)
- [Selector Group Chat](https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/selector-group-chat.html)
- [Swarm](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html)
- [AutoGen paper / COLM 2024](https://openreview.net/pdf?id=BAakY1hNKS)

关键结论：

- AutoGen 把协作模式明确做成了“可复用模式”，这点非常重要。
- 其中最值得参考的不是具体代码，而是 3 类 team 结构：

#### A. Group Chat

特征：

- 所有代理共享同一条消息线程
- 每次只有一个代理发言
- 由 `Group Chat Manager` 负责下一位说话者选择

优点：

- 结构直观
- 易观察
- 适合逐轮协作

缺点：

- 所有代理共享上下文，容易污染
- 对复杂任务容易变成“多人轮流说话”，但不一定高效

适用：

- 讨论类
- 评审类
- 轻量协作类任务

#### B. Selector / Supervisor

特征：

- 有一个显式主管代理
- 主管决定把任务给谁
- 各 specialist 不必共享全部上下文

优点：

- 更符合真实 team
- 更适合复杂任务
- 可以控制上下文泄漏

缺点：

- 主管质量会成为瓶颈
- 容易出现“主管过度集中”

适用：

- 任务拆解
- 路由
- 复核
- 仲裁

#### C. Swarm

特征：

- 多代理共享上下文
- 可以在代理之间进行 handoff
- 更偏自治协作

优点：

- 灵活
- 对开放型任务适应性强

缺点：

- 上下文很容易膨胀
- 长期任务中更容易漂移

适用：

- 创造型任务
- 探索型任务
- 人类持续参与的协作场景

对 MyAttention 的启发：

- 进化大脑不适合纯 `group chat`
- 更适合 `supervisor + specialists`
- 某些需要争论和交叉验证的场景，可以在局部引入 `debate/group chat`
- 对外统一入口，对内按模式组织 team，不能只用一种模式套所有任务

---

### 2.1.2 LangGraph 的协作模式

参考：

- [LangGraph Supervisor](https://langchain-ai.github.io/langgraphjs/reference/modules/langgraph-supervisor.html)
- [How to build a multi-agent network](https://langchain-ai.github.io/langgraph/how-tos/multi-agent-network-functional/)
- [LangGraph Checkpoint](https://langchain-ai.github.io/langgraphjs/reference/modules/langgraph-checkpoint.html)

关键结论：

- LangGraph 这组资料最大的价值是：
  - 不只讲“有几个 agent”
  - 而是讲“图结构如何组织协作”

它至少给了两种非常重要的 team 形态：

#### A. Hierarchical Supervisor

特征：

- 一个 supervisor 编排多个 specialist
- 甚至支持 supervisor 管 supervisor 的多层级结构

价值：

- 这是目前最接近你要的“主管大脑 + 专业大脑 team”的主流模式
- 非常适合复杂任务拆解

#### B. Multi-agent Network

特征：

- 多代理 many-to-many 通信
- 谁调用谁由当前上下文和 handoff 决定

价值：

- 更灵活
- 适合开放网络型协作

风险：

- 如果没有很强的约束，复杂度会迅速上升
- 状态管理和审计难度更高

对 MyAttention 的启发：

- 顶层更适合用 `hierarchical supervisor`
- 底层某些局部协作才考虑 `network`
- 也就是说：
  - 顶层控制收敛
  - 局部协作开放

这比一开始就让所有 agent 自由互相对话稳得多。

---

### 2.2 A2A 协议

参考：

- [A2A: Life of a Task](https://a2a-protocol.org/latest/topics/life-of-a-task/)

关键结论：

- A2A 把交互分成两种：
  - `Message`：即时、无状态
  - `Task`：有状态、长时间运行、可中断
- `Task` 不是普通消息，它有生命周期。
- `contextId` 用来把同一目标下的一组任务和消息串起来。
- `taskId` 标识具体的一次工作单元。
- A2A 强调：
  - 任务不可重启，终态后如要继续必须新建任务
  - refinement / follow-up 应该是同一 `contextId` 下的新任务
  - 并行后续任务应是多个独立任务，而不是把所有状态揉进一个任务里

对 MyAttention 的启发：

- 进化大脑这种持续任务，不能简单等于“一条无限循环任务”。
- 更合理的是：
  - 持续运行的“监督上下文”
  - 不断派生出一个个具体 `Task`
  - 每个任务有清晰状态、输入、输出、子任务关系、终态
- “嵌套子任务”应该建成：
  - 父任务负责目标
  - 子任务负责单元工作
  - refinement 是新任务，不是复写旧任务

限制：

- A2A 是通信协议和任务模型，不是存储、记忆和执行引擎。
- 直接照搬协议实现会过重，更适合作为内部任务建模的参考语义。

#### 对协作的进一步启发

A2A 真正有价值的地方，不是“又一个接口格式”，而是它把协作里的几个关键点说清楚了：

- 谁在发起任务
- 谁在执行任务
- 任务当前处于什么状态
- 任务产生了哪些 artifact
- 一个任务结束后，后续 refinement 应该如何继续

这对 agent team 尤其关键，因为协作如果没有任务语义，很快会退化成：

- 互相丢 prompt
- 没有统一状态
- 没有结果归档
- 没有恢复点

因此，MyAttention 后续即使不直接实现标准 A2A，也应吸收这种思想：

- team 内协作不能只靠自由文本
- 至少需要结构化的：
  - task
  - message
  - artifact
  - status
  - context

---

### 2.3 OpenClaw

参考：

- [OpenClaw Architecture](https://openclaw.cc/en/concepts/architecture)
- [OpenClaw Session](https://openclaw.cc/en/concepts/session)
- [OpenClaw Memory](https://openclaw.cc/en/concepts/memory)
- [OpenClaw Model Failover](https://openclaw.cc/en/concepts/model-failover)
- [OpenClaw Security](https://openclaw.cc/en/gateway/security/)

关键结论：

- OpenClaw 非常强调 `Gateway` 作为中心控制面：
  - 路由消息
  - 管理 session
  - 管理 memory
  - 管理 model router
  - 管理 tools / skills / cron
- 它明确区分：
  - `Session`：单会话上下文
  - `Memory`：跨会话长期记忆
- 它内建：
  - 模型 failover
  - 多 agent 路由
  - 工具与权限控制
  - 网关与节点分离

对 MyAttention 的启发：

- 这个项目也需要一个类似 `Gateway / Control Plane` 的中心层。
- “大脑控制层”不应只是模型配置页，而应负责：
  - 大脑定义
  - 路由
  - 任务分发
  - 权限/工具边界
  - 失败切换
  - 会话与长期记忆管理
- OpenClaw 的 `session vs memory` 区分非常适合我们。

限制：

- OpenClaw更偏个人助理 / 通道网关，不是为“世界知识系统 + 长期研究 + 自我进化”专门设计。
- 它的安全文档明确强调“一个 trust boundary 一个 gateway”，这对我们未来多用户/多团队场景是重要提醒。

---

### 2.4 LangGraph / LangMem

参考：

- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangMem Core Concepts](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/)

关键结论：

- LangGraph 把短期执行状态分成：
  - `thread`
  - `checkpoint`
- 每个 graph step 都能形成 checkpoint，可恢复、可 time-travel、可回放。
- LangMem 把长期记忆分成三类：
  - `Semantic`：事实、知识、偏好
  - `Episodic`：过去经历、成功案例、交互样本
  - `Procedural`：规则、行为方式、提示词/流程经验
- 它还区分记忆形成方式：
  - `hot path`
  - `background`

对 MyAttention 的启发：

- 长期记忆不能只做“用户事实记忆”。
- 对这个项目，更适合至少四层：
  - 会话状态记忆
  - 任务过程记忆
  - 长期事实/知识记忆
  - 策略/程序性记忆
- “进化大脑”的经验不应该只写日志，它需要形成：
  - 错误模式
  - 成功修复经验
  - 可复用恢复策略

限制：

- LangGraph/LangMem 给的是很好的建模方式，但不是直接可落到当前项目架构的全部答案。
- 需要结合 PostgreSQL / Redis / Qdrant / 对象存储来做本地化设计。

---

### 2.5 Temporal / Prefect

参考：

- [Temporal durable execution](https://temporal.io/)
- [Prefect states](https://docs.prefect.io/latest/concepts/states)
- [Prefect flows](https://docs.prefect.io/concepts/flows)

关键结论：

- 这类工作流系统擅长：
  - 长任务
  - 子任务
  - 状态机
  - 重试
  - 观察性
  - 崩溃恢复
- Prefect 强调：
  - flow / task / nested flow 都是 first-class observable
- Temporal 强调：
  - durable execution
  - retry
  - signals / timers / child workflows

对 MyAttention 的启发：

- “持续运行的进化大脑 + 大量子任务”本质上更像 workflow orchestration 问题，而不只是聊天问题。
- 当前项目至少需要吸收这些设计原则：
  - 明确状态机
  - 子任务 first-class
  - 幂等
  - 可恢复
  - 失败补偿

限制：

- 现在直接引入完整 Temporal/Prefect 会显著扩大复杂度。
- 更现实的路径是：
  - 先在项目内部落稳定的任务模型
  - 后续再判断是否升级到独立工作流引擎

---

## 3. 对 MyAttention 的关键判断

### 3.1 当前缺口不是“再加一个模型选择器”

真正缺的是：

- 大脑角色定义
- 大脑路由
- 大脑之间的协作关系
- 任务生命周期模型
- 长期记忆模型
- 失败降级与兜底机制

所以，后续不能继续把“智能对话模型配置”当作整个智能系统配置。

---

### 3.2 应把系统分成三层，而不是一个大脑

更合适的抽象是：

#### A. 脑干层

职责：

- 基础运行保障
- 健康检查
- 守护与重启
- 基础规则路由
- 最低功能保持

特点：

- 不依赖高级推理
- 就算高级大脑失效，系统仍能活着

#### B. 小脑层

职责：

- 任务队列
- 调度
- 重试
- 限流
- 工作流协调
- 子任务追踪

特点：

- 负责“动作协调”
- 更接近 workflow engine / orchestrator

#### C. 皮层层

职责：

- 分析
- 判断
- 规划
- 仲裁
- 归因
- 优化路径建议

这里不应只有一个大脑，而是脑群：

- `chief_brain`
- `dialog_brain`
- `research_brain`
- `knowledge_brain`
- `coding_brain`
- `evolution_brain`

#### 协作比单纯分工更重要

这里要特别强调：

- 分工只解决“谁负责什么”
- 协作解决的是：
  - 谁先做
  - 谁把结果传给谁
  - 谁做复核
  - 谁做仲裁
  - 谁保留长期记忆
  - 谁在失败时接管

后续设计里至少要支持 5 种协作模式：

1. `parallel gather`
   - 多代理并行收集信息
   - 适合研究、检索、证据搜集
2. `sequential handoff`
   - 上一个代理完成后交给下一个
   - 适合“搜索 -> 总结 -> 仲裁”
3. `supervisor mediated`
   - 所有代理通过主管协调
   - 适合高风险和高治理要求场景
4. `direct agent-to-agent`
   - 在受控协议下直接通信
   - 适合需要高频交换的协作
5. `debate / review`
   - 一个代理提出判断
   - 另一个代理审查和挑战
   - 最后由主管代理合成

对进化大脑来说，最重要的不是“多几个子代理名字”，而是至少要有：

- 观察
- 归因
- 恢复
- 复核
- 仲裁

这 5 个协作角色。

---

### 3.3 任务模型必须支持“持续任务 + 一次性任务 + 嵌套任务”

建议后续设计中把任务分成：

- `daemon_task`
  - 持续运行
  - 例如进化大脑监督循环
- `workflow_task`
  - 面向目标的一组步骤
  - 例如“诊断前端异常”
- `unit_task`
  - 最小工作单元
  - 例如“访问 /chat 并截图”
- `refinement_task`
  - 对已有结果的修正/继续
  - 不是覆盖旧任务，而是新任务

任务状态至少要支持：

- `created`
- `queued`
- `running`
- `waiting_input`
- `waiting_dependency`
- `succeeded`
- `failed`
- `canceled`
- `degraded`
- `expired`

并明确：

- 父任务与子任务关系
- 上下文 ID
- 输入、输出、artifact、事件历史
- 幂等键
- 重试策略
- 是否允许自动执行

---

### 3.4 长期记忆不能只有一层

建议研究后续设计时至少区分：

#### A. Session Memory

- 单会话
- 临时上下文
- 可压缩

#### B. Task Memory

- 单任务/单工作流状态
- checkpoint
- 中间结果
- 工具调用与执行轨迹

#### C. Semantic Memory

- 事实
- 偏好
- 长期知识

#### D. Episodic Memory

- 成功案例
- 失败案例
- 经验总结

#### E. Procedural Memory

- 提示词策略
- 恢复策略
- 决策规则
- 大脑协作策略

这部分对进化大脑尤其重要，因为“进化”本质上是把经验沉淀成程序性能力。

---

### 3.5 必须有模型失效时的保底层

这一点非常重要。

如果高级模型失效，系统仍需要：

- 保持健康检查
- 保持守护
- 保持任务记录
- 保持问题中心
- 执行预定义恢复策略

这意味着系统不能把全部控制权交给高阶大脑。

因此后续设计中必须把：

- rule-based survival layer
- model failover
- provider failover
- safe-mode

作为正式能力，而不是临时补丁。

---

## 4. 当前阶段不宜直接下定论的部分

当前还不应该立刻拍板：

- 是否直接引入 A2A 协议作为内部协议
- 是否立即引入完整 Temporal / Prefect
- 是否直接实现全量 agent team
- 是否马上把所有功能拆成多大脑

原因：

- 当前项目还处于信息事实层和进化大脑 MVP 收口阶段
- 现在过早上重量级编排层，会显著增加复杂度
- 需要先明确最小可落地的控制平面数据模型

---

## 5. 研究结论

在正式设计前，当前最重要的共识是：

1. MyAttention 后续必须从“聊天模型配置”升级到“Brain Control Plane”。
2. 任务模型应吸收 A2A 的 `Message / Task / contextId / taskId / refinement` 思路。
3. 多大脑协作应借鉴 Claude 的 `subagent / team` 分工，但不能只停留在 prompt 层。
   - 更具体地说，应吸收：
     - 并行研究
     - 串行 handoff
     - 可恢复会话
     - 生命周期事件
     - 主管仲裁
4. 控制面结构应借鉴 OpenClaw 的 `gateway + session + memory + model failover` 思路。
5. 记忆体系应借鉴 LangGraph / LangMem 的 `checkpoint + store + semantic/episodic/procedural` 分层。
6. 长任务与嵌套任务应吸收 Temporal / Prefect 的 durable execution 与状态机思想。
7. 必须保留“脑干层”兜底，让系统在高阶大脑不可用时仍能基本运行。

---

## 6. 建议的下一步研究输出

在开始设计之前，下一阶段建议形成 3 份正式设计文档：

1. `BRAIN_CONTROL_ARCHITECTURE.md`
   - 多大脑分层
   - 大脑角色
   - 协作拓扑
   - 脑干/小脑/皮层关系

2. `TASK_AND_WORKFLOW_MODEL.md`
   - 持续任务
   - 一次性任务
   - 嵌套子任务
   - 状态机
   - artifact / event / checkpoint

3. `MEMORY_ARCHITECTURE.md`
   - session / task / semantic / episodic / procedural
   - 存储落点
   - 回忆策略
   - 归档与压缩

在这三份文档完成之前，不建议直接实现完整的大脑控制层。
