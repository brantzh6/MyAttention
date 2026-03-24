# 问题建模与方法选择框架 V1

> 本文档定义 MyAttention 的 `Problem Framing and Method Selection` 框架 `V1`。
>
> 它不是终局认知体系。
> 它是一个可运行、可演化、可被替换的第一版上位框架。
>
> 目标不是一次定义正确所有问题，而是建立一个：
>
> - 可判断问题类型
> - 可选择思维模型
> - 可匹配方法
> - 可路由执行
> - 可在后续迭代中被评估和升级
>
> 的基础认知控制层。

---

## 1. 为什么需要这层

当前项目已经明确暴露出一个问题：

- 不能遇到问题就直接搜
- 不能遇到任务就直接上深度研究
- 不能遇到判断就直接上投票
- 不能遇到执行就直接写代码

如果没有更上层的判断框架，就会发生：

- 方法滥用
- 研究漂移
- 信息入口失衡
- 任务拆解混乱
- 进化大脑无法解释“为什么这次用了这个方法”

所以后面正确顺序应该是：

1. 先判断问题类型
2. 再选思维模型 / 思考框架
3. 再选方法
4. 最后才进入执行

---

## 2. 文档定位

这份文档解决的是：

- `这是什么问题`
- `该用什么视角看`
- `该优先用什么方法`
- `哪些方法不适合`
- `后面应该路由给哪些能力`

它不直接解决：

- 具体任务状态机
- 多脑协作协议
- 长期记忆具体表结构
- 版本化时间模型

这些属于后续文档：

- `TASK_AND_WORKFLOW_MODEL.md`
- `BRAIN_CONTROL_ARCHITECTURE.md`
- `MEMORY_ARCHITECTURE.md`
- `VERSIONED_INTELLIGENCE_ARCHITECTURE.md`

---

## 3. 核心原则

### 3.1 问题优先于方法

不能先想到一个方法，再把问题塞进去。

要先判断：

- 问题目标是什么
- 结果要服务谁
- 时间敏感度如何
- 风险级别如何
- 是否需要连续跟踪

### 3.2 思维模型优先于执行工具

工具只负责执行。

真正决定质量的是：

- 你用什么框架理解问题
- 你关注哪些维度
- 你忽略哪些维度

### 3.3 `V1` 不是终局 taxonomy

本框架明确是：

- provisional
- evolvable
- replaceable

后续允许：

- 新增问题类型
- 拆分已有类型
- 合并错误分类
- 调整方法优先级
- 新增思维模型

### 3.4 同一个问题可包含多层子问题

例如：

- “搭建某领域信息流”

可能同时包含：

- source discovery 问题
- authority evaluation 问题
- monitoring design 问题
- decision framing 问题

所以框架必须允许：

- 主问题类型
- 次问题类型
- 分阶段方法切换

---

## 4. 问题类型 V1

当前建议把问题先分成 8 类。

### 4.1 `source_intelligence_problem`

目标：

- 确定该关注什么来源、对象、社区、人物、仓库、站点、机构

典型问题：

- 某领域的信息流应如何搭建
- 哪些来源值得长期订阅
- 哪些来源只是信号，不应直接当事实依据

输出更像：

- source plan
- source hierarchy
- subscription strategy

### 4.2 `monitoring_problem`

目标：

- 持续跟踪一个主题、来源、对象或领域变化

典型问题：

- 某个前沿方向需要持续关注什么
- 某个来源是否还值得持续监控
- 某个风险点最近是否有变化

输出更像：

- monitoring plan
- refresh cadence
- watch list

### 4.3 `deep_research_problem`

目标：

- 对明确主题做结构化深度研究

典型问题：

- 学科综述
- 主题综述
- 机制分析
- 决策研究

输出更像：

- research brief
- evidence log
- fact base
- interpretation / boundary / tension maps

### 4.4 `decision_support_problem`

目标：

- 面向行动或选择，给出可解释的判断

典型问题：

- 该优先做哪个方向
- 该选择哪条路线
- 哪些方案应早期排除

输出更像：

- decision frame
- option comparison
- recommendation
- no-go conditions

### 4.5 `knowledge_structuring_problem`

目标：

- 把已有信息和研究转成结构化知识

典型问题：

- 某学科如何分层
- 某主题的权威理解如何组织
- 某知识对象应放在哪个结构位置

输出更像：

- concept map
- taxonomy
- entity / relation structure

### 4.6 `system_diagnosis_problem`

目标：

- 诊断系统、流程、数据或质量问题

典型问题：

- 为什么页面异常
- 为什么投票质量差
- 为什么信息流偏

输出更像：

- diagnosis
- root cause candidates
- recovery options

### 4.7 `method_evolution_problem`

目标：

- 评估当前方法、skill、流程是否有效，是否应替换

典型问题：

- 现在的研究方法是否合适
- 当前投票策略是否有效
- 某个 skill 是否值得继续用

输出更像：

- method comparison
- evaluation report
- promote / demote / retire decision

### 4.8 `implementation_problem`

目标：

- 把明确方案落地到代码、任务流或配置

典型问题：

- 实现一个新接口
- 接入一个新数据层
- 修复一个已确认的问题

输出更像：

- implementation plan
- patch set
- validation result

---

## 5. 思维模型 / 思考框架 V1

方法不是直接挂在问题下面，而是先经过思维模型。

当前建议的思维模型有：

### 5.1 `source_intelligence`

关注：

- 应关注哪些对象
- 为什么关注
- 来源层级是什么
- 来源执行策略是什么

适合：

- source intelligence problem
- monitoring problem

### 5.2 `lifecycle_analysis`

关注：

- 一个对象如何产生、变化、稳定、退化、失效

适合：

- knowledge structuring
- memory design
- source review
- task evolution

### 5.3 `mechanism_analysis`

关注：

- 为什么发生
- 真正驱动因素是什么
- 失效条件是什么

适合：

- deep research
- system diagnosis
- method evolution

### 5.4 `comparative_analysis`

关注：

- 真正差异在哪里
- 各方案在什么条件下更优/更差

适合：

- decision support
- method evaluation
- architecture choice

### 5.5 `decision_framing`

关注：

- 选择是什么
- 变量是什么
- 哪些应尽早排除
- 哪些条件下应切换路线

适合：

- decision support
- roadmap planning

### 5.6 `boundary_review`

关注：

- 结论在哪些情况下不成立
- 有哪些 counterarguments
- 哪些风险被忽略

适合：

- deep research
- decision support
- evolution review

### 5.7 `systems_diagnosis`

关注：

- 症状
- 证据
- 候选根因
- 可验证修复路径

适合：

- system diagnosis
- evolution brain

### 5.8 `temporal_analysis`

关注：

- 时间序列
- 演化轨迹
- 版本变化
- 先后关系

适合：

- financial / market monitoring
- scientific evolution
- versioned knowledge
- long-term method evaluation

---

## 6. 方法集合 V1

当前建议的核心方法不是一个，而是一组。

### 6.1 `search_discovery`

用途：

- 发现来源
- 发现人、事、社区、仓库、关键词

适合：

- source intelligence
- landscape scan

### 6.2 `authority_mapping`

用途：

- 识别权威源、可信二级源、社区信号源

适合：

- source planning
- knowledge quality control

### 6.3 `continuous_collection`

用途：

- 对已决定关注的对象进行持续采集

适合：

- monitoring
- hot/warm data handling

### 6.4 `deep_research`

用途：

- 针对明确主题做 research-assets-first 的深度研究

适合：

- deep research problem
- decision support 中的高价值专题

### 6.5 `multi_model_voting`

用途：

- 比较观点
- 暴露分歧
- 做复核
- 做决策裁决

适合：

- comparative analysis
- decision framing
- boundary review
- evolution review

限制：

- 不适合作为 source discovery 的第一步
- 不适合作为事实建立的唯一方法
- 不适合替代深度研究骨架

### 6.6 `counterexample_review`

用途：

- 强制寻找反例、非适用场景、边界

适合：

- decision support
- deep research
- evolution diagnosis

### 6.7 `timeline_reconstruction`

用途：

- 做时间线、版本变化、事件先后关系整理

适合：

- scientific evolution
- market events
- incident analysis

### 6.8 `cross_validation`

用途：

- 在不同来源、不同方法、不同模型之间做交叉校验

适合：

- knowledge verification
- high-stakes decisions
- method evaluation

---

## 7. 问题类型 -> 思维模型 -> 方法映射 V1

### 7.1 source intelligence

优先思维模型：

- `source_intelligence`
- `comparative_analysis`

优先方法：

- `search_discovery`
- `authority_mapping`
- `cross_validation`

不应直接默认：

- `deep_research`
- `multi_model_voting`

### 7.2 monitoring

优先思维模型：

- `source_intelligence`
- `temporal_analysis`
- `lifecycle_analysis`

优先方法：

- `continuous_collection`
- `search_discovery`
- `cross_validation`

### 7.3 deep research

优先思维模型：

- `mechanism_analysis`
- `boundary_review`
- `comparative_analysis`
- `decision_framing`

优先方法：

- `deep_research`
- `counterexample_review`
- `multi_model_voting` 作为分析/复核工具

### 7.4 decision support

优先思维模型：

- `decision_framing`
- `comparative_analysis`
- `boundary_review`

优先方法：

- `multi_model_voting`
- `cross_validation`
- 高价值时叠加 `deep_research`

### 7.5 knowledge structuring

优先思维模型：

- `lifecycle_analysis`
- `temporal_analysis`
- `mechanism_analysis`

优先方法：

- `timeline_reconstruction`
- `cross_validation`
- 必要时叠加 `deep_research`

### 7.6 system diagnosis

优先思维模型：

- `systems_diagnosis`
- `boundary_review`

优先方法：

- evidence collection
- UI / log / data probing
- `multi_model_voting` 作为 root-cause review

### 7.7 method evolution

优先思维模型：

- `comparative_analysis`
- `systems_diagnosis`
- `temporal_analysis`

优先方法：

- `cross_validation`
- `multi_model_voting`
- `counterexample_review`

### 7.8 implementation

优先思维模型：

- `decision_framing`
- `systems_diagnosis`

优先方法：

- plan review
- implementation
- validation

---

## 8. 方法选择规则 V1

### 8.1 先判断时间敏感度

- 高时间敏感：
  - 优先 search + monitoring + recency verification
- 低时间敏感：
  - 可优先 authority + deep research

### 8.2 先判断事实需求强度

- 事实要求高：
  - 优先 primary sources + cross validation
- 解释要求高：
  - 再引入 mechanism / comparative / voting

### 8.3 先判断是否连续任务

- 连续任务：
  - 优先 source intelligence + collection loop
- 一次性任务：
  - 可走深度研究或专题分析

### 8.4 先判断风险等级

- 高风险 / 高代价问题：
  - 不能只靠单模型
  - 不能只靠社区信号
  - 需要 boundary review

---

## 9. 执行路由原则 V1

后续主控大脑/控制层应按这个顺序路由：

1. `classify problem`
2. `select thinking framework`
3. `select methods`
4. `plan evidence / source requirements`
5. `assign execution`
6. `collect outputs`
7. `review boundaries`
8. `commit artifacts to memory / knowledge / task history`

也就是说，执行前必须至少生成一个最小 plan，而不是直接进工具。

---

## 10. 当前已知局限

这份 `V1` 框架有明确局限：

- 问题类型分类还不完备
- 思维模型还偏人工整理
- 方法映射规则仍然主要靠启发式
- 还没有正式和任务系统、版本系统、记忆系统接通
- 还不能自动学习“哪种问题该用哪种方法最好”

所以它只是：

- `V1`
- `provisional`
- `evolvable`

---

## 11. 对后续设计的直接影响

本框架后续应直接约束：

- `SOURCE_INTELLIGENCE_ARCHITECTURE.md`
- `MEMORY_ARCHITECTURE.md`
- `TASK_AND_WORKFLOW_MODEL.md`
- `BRAIN_CONTROL_ARCHITECTURE.md`

因为后续多任务、多脑协作、深度研究、方法演化，都应该建立在“先判断问题，再选方法”的上层框架上。

---

## 12. 当前结论

现在我们已经明确：

- 深度研究不是唯一方法
- 投票不是唯一方法
- 搜索不是补充，而是很多问题的前置能力
- feed 不是固定 RSS，而是持续发现和校准循环

所以后面 MyAttention 的正确方向不是“固定一种方法”，而是：

**建立一个可进化的问题建模与方法选择系统。**
