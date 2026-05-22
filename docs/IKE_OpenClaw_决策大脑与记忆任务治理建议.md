# IKE 项目提示文件

**主题**：决策大脑定位、与 IKE 的关系、以及 OpenClaw 记忆与任务治理子项目建议  
**用途**：输入给 IKE 中控，作为后续工作范围、架构边界与优化优先级的参考。

> **核心结论**：逻辑上统一到 IKE，工程上拆出一个可独立交付的子项目；近期只聚焦两件事——修复 OpenClaw 的记忆失效与任务管理混乱，不把问题一开始扩大成“完整 IKE 落地”。

## 1. 这份文件要回答什么

- 用户当前的核心疑问：Claude Code、OpenClaw 与“真正的决策大脑”应该如何分工；该决策大脑与正在推进的 IKE 项目究竟应该拆开做，还是作为 IKE 的一个能力出口来落地。
- 用户当前最紧急的问题不是继续抽象讨论，而是尽快解决 OpenClaw 在真实使用中的两个失效点：第一，记忆系统失效；第二，任务管理混乱。
- 因此，文件一方面沉淀前述讨论中的判断，另一方面给出边界、优先级与扩展 backlog。

## 2. 用户当前问题、疑虑与约束

| 主题 | 用户的真实判断 / 约束 |
|---|---|
| 关于 OpenClaw 的现实评价 | OpenClaw 在多渠道网关、hook、connector 与消息入口层面有价值，但它并不具备稳定可靠的“中控大脑”能力；表现为无法持续进化、经常遗忘、记忆系统无效、无法有效管理多个任务，难以承担决策大脑角色。 |
| 关于 Claude Code 的现实评价 | Claude Code 更擅长在单个项目或单个 repo 内进行深度执行，例如编码、修改、调试、测试与推进明确任务；但它并不天然适合承担多项目协同、日常任务统筹、长期记忆与跨渠道交互。 |
| 关于 IKE 的偏好 | 从长期方向看，更倾向于把“决策大脑”作为 IKE 的一个能力出口，而不是完全独立于 IKE 之外再造一套体系。 |
| 关于收敛风险的担心 | 如果把“修复 OpenClaw”直接上升为“完整 IKE 落地”，项目目标会过大，范围会迅速扩张到信息摄取、知识建模、进化判断、研究任务、harness/evaluation 等，短期内不易收敛。 |
| 关于当前落地诉求 | 近期最急的是修复 OpenClaw：先让它不再明显遗忘、不再在多项目/多任务上混乱；这两个问题需要一个可以独立启动、独立交付的小项目。 |

## 3. 对前述问题的判断与建议

建议采用“逻辑统一，工程拆分”的方式处理：

- 逻辑上：不要把决策大脑做成一个与 IKE 完全平行、彼此割裂的系统；它应当被定义为 IKE 的一个能力出口或一条现实落地路径。
- 工程上：不要一开始就把它做成“全量 IKE”。应先拆成一个独立可交付的子项目，专门解决 OpenClaw 的记忆与任务治理问题。
- 架构上：OpenClaw 只保留为渠道网关 / 触发层；Claude Code 只保留为深度开发执行器；真正的项目状态、任务状态、决策记录、工作记忆与反思机制，应放在一个独立中控内核中。
- 节奏上：先做状态持续化，再谈进化。也就是说，先把 Project、Task、Memory、Decision 等对象变成第一类对象，后续再往 IKE 的知识建模、进化回路、研究触发、评估框架扩展。

## 4. 对 IKE 项目的直接提示：后续工作需要注意什么

### 4.1 不要把“修复 OpenClaw”直接升级成“完整 IKE 落地”
IKE 是长期主线，但当前阶段只应取其最小必要内核。近期范围必须收敛到“工作状态持续化”问题，而不是同时推进信息大脑、知识大脑、进化大脑的全量实现。

### 4.2 近期目标应当是 IKE Runtime v0，而不是 IKE Full Stack
建议将近期工作命名为 **IKE Runtime v0: Memory & Task Control for OpenClaw**。这样既不脱离 IKE 主线，又能保持一个工程上可控、可验证、可独立交付的范围。

### 4.3 近期优先做“状态”，不要优先做“智能幻觉”
如果底层没有可靠的项目状态、任务状态与决策日志，那么所谓进化、反思、研究建议都容易变成脆弱的表面智能。应先保证系统能够知道：当前在做什么、上次做到哪里、为什么这么做、接下来做什么。

### 4.4 记忆与任务管理不是两个孤立问题，本质上都属于工作状态治理
任务之所以混乱，常常因为系统并不真正知道任务当前状态；记忆之所以失效，往往因为系统只保存聊天，不保存结构化工作状态。因此二者应在一个统一内核中设计，而不是各做一套。

### 4.5 IKE 后续扩展应建立在稳定内核之上
等到 v0 解决了记忆与任务治理，再逐步扩展到知识关系、进化判断、research trigger、harness evaluation 等。这些能力应建立在稳定的状态层之上。

## 5. 建议立即启动的独立开发子项目

建议以单独项目形式启动，但明确标注其属于 IKE 的第一阶段落地。推荐项目名之一：

- IKE Runtime v0: Memory & Task Control for OpenClaw
- OpenClaw Cognitive Control v0
- IKE Memory & Task Kernel v0

### 项目目标（只做近期必须项）

- 让 OpenClaw 在多轮交互中不再出现明显的“刚说完就忘”。
- 让 OpenClaw 可以在多个项目与多个任务之间切换，而不是把上下文混在一起。
- 让任务状态成为结构化对象，而不是停留在聊天文本中。
- 为后续 IKE 扩展留下对象模型与状态流转基础。

### 建议的最小对象模型

| 对象 | 核心字段（建议） | 作用 |
|---|---|---|
| Project | project_id, goal, status, current_phase, blockers, next_milestone | 承载项目级目标、阶段与当前状态；是多项目切换与上下文恢复的主锚点。 |
| Task | task_id, project_id, title, status, priority, dependency, next_action | 承载真正可执行的工作单元；避免“所有事情都只存在于聊天里”。 |
| Decision | decision_id, summary, rationale, alternatives, impact_scope, timestamp | 沉淀关键判断与理由，便于后续恢复上下文与避免重复决策。 |
| Memory Packet | project_summary, recent_changes, blockers, active_tasks, next_steps | 提供轻量、可恢复的工作记忆载荷，用于会前加载、会后压缩。 |
| Session / Work Context | current_project, active_task, working_set, open_questions | 承载当前工作集，减少跨项目串线。 |

## 6. v0 范围建议：先修哪两件事

### Workstream A - 记忆修复

- 项目识别：系统要能识别当前这句话属于哪个项目；不确定时进入 triage/inbox，而不是直接混入已有项目。
- 上下文恢复：每次进入项目会话前，自动加载项目摘要、活跃任务、关键决策、blocker、next step。
- 会后压缩：每次交互后不保存整段聊天，而是只沉淀新决策、新任务、状态变化、新 blocker、新 next step。
- 跨渠道隔离与合并规则：同一用户跨不同 channel 时，允许共享用户级记忆，但必须对项目级与任务级记忆做严格边界控制。

### Workstream B - 任务治理

- 建立最小状态机：inbox / active / waiting / blocked / done / dropped。
- 定义最小操作集：create task、update status、set next action、link to project / decision。
- 把任务从聊天文本中抽出来，变成可查询、可排序、可恢复的对象。
- 允许每个项目存在独立 active queue，并保留一个全局 personal inbox，避免任务既不属于项目也不被收敛。

## 7. 这个子项目明确不做什么

- 不在 v0 阶段追求完整的知识图谱或复杂实体关系建模。
- 不在 v0 阶段追求自动研究代理、全自动规划器或完全自治的多智能体编排。
- 不在 v0 阶段把所有 OpenClaw 生态问题一次性解决。
- 不把“记忆修复”误解成单纯换个向量库；重点是结构化工作状态与上下文治理。

## 8. 除记忆与任务管理外，OpenClaw 还应关注的其他硬伤

以下条目不是对整个用户群做统计学调查后的结论，而是基于 2026 年 1-3 月公开 GitHub issue/PR 中出现的高频痛点整理而成，适合作为下一阶段优化 backlog。

| 类别 | 表现 | 建议方向 | 优先级 |
|---|---|---|---|
| 上下文压缩/compaction | 压缩后“刚说完就忘”，最近讨论的核心内容丢失，甚至会重复验证已完成工作。 | 增加 compaction 前/后强制状态刷新机制；把 recent sticky context 与结构化状态分离保存；支持 postCompaction hook 与强制 re-read。 | P0 |
| 上下文装载策略 | 当前倾向于把大量 personality/memory 内容静态塞入上下文，导致 token 成本高、复杂项目容量不足。 | 引入语义索引、按需加载、上下文预算监控、最小启动上下文。 | P0 |
| 多项目/多渠道隔离 | 单 workspace、单 session 容易造成项目串线；跨不同渠道时又会造成记忆碎片化。 | 建立 project scope 与 user scope 两层隔离；支持项目切换协议、统一 user identity、channel-aware memory。 | P0 |
| 可观测性不足 | 外部系统很难稳定查看 cron、session 生命周期、工具调用、最近活动与失败原因。 | 补充稳定的 gateway observability API / activity API，便于 Mission Control 或外部 dashboard 接管。 | P1 |
| 计划任务/cron 稳定性 | 定时任务存在投递目标、路由、非默认 agent 调度等问题，影响长期运行可靠性。 | 统一 cron 状态模型、增加投递前校验与可见的执行记录。 | P1 |
| 插件/runtime 可靠性 | 不同安装形态、插件依赖解析、provider 解析、runtime backend 配置容易导致插件“看似加载、实际不可用”。 | 改进插件加载前检查、版本解析、错误提示与安装形态兼容性；优先解决 provider/runtime 推断错误。 | P1 |
| 索引与 embedding 机制 | 大文件未预分块就进入 embedding，可能导致整个 memory index 失败。 | 预分块、限长、失败文件隔离、增量索引与重试策略。 | P1 |
| 升级/兼容性 | 更新过程中因配置或插件槽位变动而回滚，影响生产稳定性。 | 升级前 config preflight、迁移提示、兼容层与回滚原因可读化。 | P2 |

## 9. 建议的优先级排序

- **P0**：项目级记忆、任务状态机、上下文压缩保护、跨项目/跨渠道边界。
- **P1**：上下文按需装载、可观测性 API、cron 稳定性、embedding/indexing 稳定性、插件/runtime 可靠性。
- **P2**：升级体验、移动端离线队列、更多自动化与体验优化。

## 10. 建议给 IKE 中控的执行口径

- 把“OpenClaw 记忆与任务治理”定义为 IKE 的第一阶段现实落地，不单独开辟一套与 IKE 冲突的对象模型。
- 但在工程排期上，将其视为一个独立子项目，允许单独设计、开发、验证与迭代。
- 近期 success criteria 不是“更聪明”，而是“更稳定”：不忘、不串项目、不丢任务、可恢复。
- 一旦 v0 稳定，再逐步扩展为 IKE 的更高阶能力，如知识关系、进化判断、research trigger 与 harness evaluation。

## 附录 A. 公开反馈与证据线索（供 backlog 参考）

- Issue #48782 - Project-level memory for multi-project workflows：指出同一 session 多项目混用技术栈与特性。
- Issue #9142 - Built-in Context & Memory Management：指出长期运行时 context 膨胀、token 成本高、需要自动归档与预算监控。
- Issue #12333 - Project/Context Switching within Workspace：指出单 workspace 致多项目切换需要人工管理。
- Issue #3922 - Context compaction causes 'dementia effect'：指出压缩会让 agent 几分钟内忘记刚讨论的内容。
- Issue #7776 - Channel-aware memory context：指出多渠道/多项目下 memory search 会返回无关噪音。
- Issue #3827 - User-based workspace and memory system with multi-channel binding support：指出绑定是 channel-centric 而非 user-centric，造成跨渠道记忆碎片化。
- Issue #14384 - Intelligent Context Management System：指出静态加载全部 personality/memory 文件会消耗 60-80% context。
- Issue #28919 - Memory index fails with input length exceeds context length：指出大文件未预分块就进入 embedding，导致整个索引失败。
- Issue #11338 - Gateway observability API：指出缺少对 cron、activity、session lifecycle 的稳定外部可见面。
- Issue #13053 - Post-compaction hook：指出 compaction 后仅靠 AGENTS.md 提示并不能可靠触发强制恢复。
- Issue #17905 - Cron jobs multiple delivery and scheduling bugs：指出计划任务在投递、agent 路由、channel 解析上存在系统性问题。
- Issue #40832 / #51494 / #30807 / #40278 等：反映插件加载、版本解析、runtime backend 与 provider 推断方面存在稳定性问题。

## 附录 B. 一句话总纲

> 不要让 OpenClaw 负责思考；让它负责接消息。不要让 Claude Code 负责全局管理；让它负责深度执行。把真正的项目状态、任务状态、决策记录与工作记忆做成 IKE 的最小中控内核，并先用一个小项目把它在 OpenClaw 上跑通。
