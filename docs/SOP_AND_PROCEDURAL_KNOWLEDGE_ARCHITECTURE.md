# SOP 与程序性知识架构 V1

## 1. 定位

本文件定义 MyAttention 中“方法、SOP、Playbook、Skill、Policy”这一类程序性知识对象的架构。

它解决的问题不是“怎么多写几篇文档”，而是：

- 如何让方法本身成为系统中的正式知识对象
- 如何让自然语言描述成为可调用、可版本化、可评估的能力载体
- 如何让进化大脑不只优化代码，也优化方法、流程、规则与协作方式

结论先明确：

- 程序性知识是系统主知识体系的一部分
- 但它不能只有自由文本，必须带结构化元数据、版本与评估
- 它不替代结构化数据库，而是与结构化层形成双层知识系统

## 2. 为什么它是主线

MyAttention 的长期目标不是“做一个固定的软件”，而是构建一个：

- 能持续感知
- 能持续研究
- 能持续调整方法
- 能持续重构自己的智能系统

因此，系统真正需要管理和进化的对象，不只是：

- 代码
- 数据
- 模型配置

还包括：

- 方法
- 流程
- SOP
- Skill
- Policy
- Prompt 模板
- 评估规则
- 协作协议

这些对象如果不进入正式架构，就会退化成：

- 零散文档
- 口头约定
- 隐性经验
- 无法追溯的 prompt 片段

这与“自我进化系统”的目标冲突。

## 3. 基本判断

### 3.1 自然语言是重要知识形态

在大模型时代，很多知识的高价值形态已经不只是结构化表记录，而是：

- 自然语言描述的方法
- 结构化步骤
- 操作策略
- 判断原则
- 协作协议

例如：

- 深度研究方法
- source intelligence 建源流程
- 问题建模与方法选择框架
- UI 巡检方法
- 任务外包协议
- Claude/OpenClaw/Codex skill

这些都属于程序性知识。

### 3.2 但不能只有自然语言

如果只有自由文本，会失去：

- 可比较性
- 可约束性
- 可验证性
- 可回滚性
- 可调度性

所以程序性知识必须采用：

**自然语言主体 + 结构化元数据 + 版本管理 + 效果评估**

## 4. 程序性知识对象分类

V1 先定义五类对象：

### 4.1 Method

含义：

- 解决某类问题的方法论

示例：

- 深度研究方法
- source intelligence 方法
- comparative analysis
- boundary review

特点：

- 更偏抽象原则
- 不直接规定每一步执行细节

### 4.2 SOP

含义：

- 标准操作流程

示例：

- 如何围绕一个 topic 建 source plan
- 如何执行 source plan refresh 复核
- 如何对进化问题做人工复核

特点：

- 步骤明确
- 适合重复执行

### 4.3 Playbook

含义：

- 面向特定场景的操作手册

示例：

- 前端裸 HTML 退化排查 playbook
- source plan 质量退化处置 playbook
- 新 topic 冷启动建源 playbook

特点：

- 面向具体情景
- 允许多路径和条件判断

### 4.4 Skill

含义：

- 可被某类 agent/工具直接调用的能力包

示例：

- Claude/Codex/OpenClaw skill
- 项目自定义 skill

特点：

- 有明确触发条件、输入输出和操作步骤
- 接近“程序性知识的执行封装”

### 4.5 Policy

含义：

- 用于约束或裁决的方法配置/规则

示例：

- attention policy
- delegation gate policy
- quality gate policy

特点：

- 不一定包含完整执行步骤
- 更偏约束、筛选和门禁

## 5. 与现有架构的关系

程序性知识层与现有层的关系：

- 问题建模层
  - 决定这是哪类问题
- 程序性知识层
  - 决定该用什么方法、SOP、Playbook、Policy
- 任务系统
  - 把这些对象落实为任务和子任务
- 大脑控制层
  - 路由到合适的 brain/agent 去执行
- 记忆层
  - 记录方法使用效果、失败模式、修订历史

也就是说：

**程序性知识层是认知控制层和任务执行层之间的桥。**

## 6. 核心对象模型

V1 建议统一成 `procedural_knowledge_object` 抽象。

通用字段：

- `object_id`
- `object_type`
- `title`
- `summary`
- `body`
- `problem_types`
- `thinking_frameworks`
- `applicable_contexts`
- `inputs`
- `outputs`
- `constraints`
- `acceptance_criteria`
- `status`
- `version`
- `parent_version`
- `change_reason`
- `evidence_of_effectiveness`
- `owner`
- `tags`
- `created_at`
- `updated_at`

说明：

- `body` 是自然语言主体
- 其他字段用于让系统理解、调度、比较和评估

## 7. 生命周期

程序性知识对象的生命周期不应是静态文档式，而应是：

1. `draft`
2. `trial`
3. `active`
4. `degraded`
5. `superseded`
6. `retired`

解释：

- `draft`
  - 初稿，未验证
- `trial`
  - 正在试用，需观察
- `active`
  - 已证明有效，可正式使用
- `degraded`
  - 曾经有效，但近期效果下降
- `superseded`
  - 被新版本替代
- `retired`
  - 明确淘汰

## 8. 版本管理要求

程序性知识对象必须被版本化。

至少要回答：

- 当前版本是什么
- 从哪个版本演化而来
- 为什么改
- 改后效果如何
- 是否应回滚

版本字段建议：

- `version_id`
- `parent_version`
- `baseline_version`
- `change_reason`
- `effective_from`
- `evaluation_result`
- `rollback_target`

## 9. 效果评估

程序性知识不能因为“写得很合理”就默认为有效。

每个对象至少应记录：

- 使用次数
- 成功率
- 失败模式
- 适用范围
- 误用场景
- 典型案例

评估维度建议：

- `correctness`
- `repeatability`
- `cost_efficiency`
- `coverage`
- `stability`
- `evolvability`

## 10. 与进化大脑的关系

进化大脑不只负责：

- 发现 bug
- 监控服务

它还必须负责：

- 评估当前方法是否仍有效
- 比较方法版本
- 发现程序性知识对象退化
- 生成修订建议
- 触发 playbook/skill/policy 的更新任务

所以进化大脑后面评估的对象，至少包括：

- 代码
- source plan
- attention policy
- 方法
- SOP
- Playbook
- Skill

## 11. 与 Skill 的关系

Skill 是程序性知识的一种特殊执行封装。

因此，项目中的 skill 不应被当作“外挂附件”，而应被纳入：

- 适用场景定义
- 版本管理
- 试用评估
- 失效淘汰

这意味着后面：

- 有效方法可以沉淀成 skill
- 失效 skill 需要被降级或淘汰
- 不是安装了 skill 就算有效

## 12. 与文档的关系

现有项目中的大量文档，本质上已经是程序性知识雏形。

例如：

- `PROBLEM_FRAMING_AND_METHOD_SELECTION.md`
- `SOURCE_INTELLIGENCE_ARCHITECTURE.md`
- `CONTROLLED_DELEGATION_STRATEGY.md`
- `TASK_AND_WORKFLOW_MODEL.md`

后续不应把“文档”和“知识对象”完全割裂，而应逐步把高价值文档升级成：

- 有结构化元数据
- 有版本记录
- 有评估状态
- 可被大脑调用的程序性知识对象

## 13. 存储建议

V1 不建议把程序性知识只塞进数据库字段，也不建议只留在 Markdown。

更合理的是：

- 主体文本：Markdown / text body
- 元数据：PostgreSQL
- 索引与语义检索：Qdrant
- 版本与关系：PostgreSQL + object storage

这样能同时满足：

- 人类可读
- LLM 可读
- 系统可查
- 可版本化

## 14. 短期实施优先级

### P0

- 把高价值方法对象显式化
- 明确哪些文档已经属于程序性知识对象

### P1

- 为方法/SOP/Playbook/Skill 增加统一元数据模型
- 让任务系统和大脑控制层能引用这些对象

### P2

- 让进化大脑评估程序性知识有效性
- 让有效对象自动进入 skill/playbook 沉淀

## 15. 当前结论

当前阶段应明确：

- 方法、SOP、Skill、Policy、Playbook 都属于正式知识对象
- 它们不是附属文档，而是系统可进化能力的一部分
- 未来自我进化的核心之一，不是只改代码，而是持续改进这些程序性知识对象

因此，MyAttention 的知识体系至少应包含两大层：

- 事实/概念/关系知识层
- 方法/SOP/技能/策略知识层

后者就是系统真正“会怎么做事”的知识基础。
