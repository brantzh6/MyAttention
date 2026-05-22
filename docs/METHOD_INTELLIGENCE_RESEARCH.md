# 方法情报与信息流前置索引研究

> 目标：明确 MyAttention 不应把信息流理解为“固定抓几个 RSS”，而应把“主题识别 -> 权威源发现 -> 持续关注 -> 方法更新”作为正式能力，服务于世界知识目标与进化目标。

---

## 1. 当前问题

当前信息流最容易退化成一种低水平形态：

- 预先配几个站点
- 固定抓 RSS
- 默认偏向最新内容
- 再把抓到的内容做摘要

这对“世界知识系统”是不够的，原因很明确：

1. 固定源会过时
- 新社区、新作者、新论文入口、新工具仓库会不断出现
- 如果方法不更新，系统会长期错过关键变化

2. RSS 只覆盖一部分公开信息入口
- 很多高价值来源没有标准 RSS
- 很多权威来源以论文库、机构站点、GitHub、论坛、标准组织、邮件列表、发布说明等形式存在

3. “最新”不等于“最重要”
- 金融、政策、市场、开源动态，对时效性要求很高
- 但科学理解、学科结构、理论共识、权威综述，并不一定是最新

4. 系统如果不知道“要找什么”，就无法判断“该跟踪谁”
- 信息流不是盲抓
- 它应该由目标和研究意图驱动

---

## 2. 研究结论

### 2.1 搜索不是补充，而是信息流的重要前置索引

对于复杂主题，更合理的链路应是：

```text
用户目标 / 系统研究目标
  -> 主题理解
  -> 权威来源发现
  -> 权威人物 / 机构 / 社区发现
  -> 持续关注配置
  -> 信息流采集
  -> 事实/知识/洞察处理
```

也就是说：

- 搜索不是只在“没数据时临时查一下”
- 搜索是信息流建源、扩源、纠偏、更新的重要前置步骤

---

### 2.2 信息流至少要服务 4 类目标

后续不应把所有信息都放进一个“新内容流”里，而应区分：

#### A. `latest intelligence`

目标：

- 追踪最新变化
- 适合金融、政策、科技动态、开源更新、市场信号

重点：

- 快
- 新
- 高更新频率

#### B. `authoritative understanding`

目标：

- 找当前最权威、最稳定、最主流的理解

重点：

- 权威机构
- 教科书级资料
- 标准组织
- 高质量综述

#### C. `frontier research`

目标：

- 找最前沿的研究进展和新方法

重点：

- 论文
- 研究社区
- 专业会议
- 顶级实验室 / 核心作者

#### D. `method intelligence`

目标：

- 持续发现更好的技能、工作流、agent 框架、记忆架构、评测方法

重点：

- GitHub
- 开源社区
- 框架文档
- RFC / 设计说明
- 实践案例

---

### 2.3 信息流应该先知道“要什么”，再决定“去哪找”

后续的正确思路不是：

- 先抓一堆内容
- 再试图从里面找价值

而是：

- 先明确任务或研究目标
- 再确定：
  - 需要最新信息？
  - 需要权威理解？
  - 需要前沿研究？
  - 需要方法更新？
- 然后再决定：
  - 该搜索哪些机构、人物、仓库、论文库、社区、标准组织
  - 哪些适合持续跟踪
  - 哪些只做一次性研究

#### 并且这个判断必须持续复查

因为：

- 新权威来源会出现
- 老来源会衰退
- 社区会迁移
- 新方法会出现
- 当前研究目标也会变化

因此后续必须支持：

- source promotion
- source demotion
- source replacement
- source retirement
- source rediscovery

否则信息流会越来越僵化。

---

## 3. 对 MyAttention 的直接启发

### 3.1 信息流需要新增“建源 intelligence”

后续应新增一类能力：

- `source_discovery_agent`
  - 针对主题发现候选来源
- `authority_mapping_agent`
  - 识别权威机构、权威作者、权威社区
- `source_strategy_agent`
  - 决定哪些进入长期订阅，哪些保留为按需搜索
- `source_refresh_agent`
  - 定期检查当前源是否过时，是否需要新增/替换

这意味着信息流不再只是“采集器”，还必须有“建源与扩源 intelligence”。

---

### 3.2 搜索、大模型、信息流要联合使用

后续更合理的关系是：

- `LLM`
  - 理解主题
  - 生成搜索方向
  - 归纳来源类型
  - 压缩信息
- `Search`
  - 找当前可用来源
  - 找权威机构/人物/社区
  - 找最新入口
- `Feed / collector`
  - 对已确认来源做持续跟踪

也就是说：

- LLM 负责“理解和压缩”
- Search 负责“发现和校准”
- Feed 负责“持续感知”

三者缺一不可。

#### 它们不是静态分工，而是闭环迭代关系

更准确地说，后续应该形成：

```text
目标 / 问题
  -> LLM 理解主题与信息需求
  -> Search 发现来源、机构、人物、社区、关键词
  -> LLM 判断哪些值得长期关注
  -> Feed 更新关注集合
  -> 持续采集
  -> 新信息进入知识与方法层
  -> 暴露新的空白、变化、异常、机会
  -> 再触发下一轮 Search / 评估 / 更新
```

也就是说：

- Search 不只是初始化时用一次
- Feed 不应该一旦配置完就长期不变
- LLM 也不只是做摘要，而要参与判断“以后应关注什么”

这个闭环更适合拆成：

- `discover`
- `judge`
- `subscribe`
- `collect`
- `refresh`
- `retire`

---

### 3.3 信息流不应只追“新”，还要追“权威”和“当前理解”

后续应显式区分信息对象的目标属性，例如：

- `freshness`
- `authority`
- `consensus_relevance`
- `frontier_novelty`
- `decision_criticality`

对不同任务，这些属性的权重不同：

- 金融决策：
  - freshness 高
  - authority 中高
- 科学知识整理：
  - authority 高
  - consensus_relevance 高
  - freshness 不是唯一重点
- 方法研究：
  - frontier_novelty 高
  - practical_reproducibility 高

---

## 4. 与知识生命周期的关系

信息流不是独立模块，而是知识生命周期前端。

更完整的链路应是：

```text
研究目标 / 决策目标
  -> source discovery / search
  -> source monitoring / collection
  -> event / fact extraction
  -> claim / evidence alignment
  -> structured knowledge
  -> authoritative understanding / frontier research / insight
  -> decision support / method update / skill distillation
```

因此，“信息流”后续需要和这些文档一起设计：

- `KNOWLEDGE_LIFECYCLE_RESEARCH.md`
- `BRAIN_CONTROL_RESEARCH.md`
- `TASK_AND_WORKFLOW_MODEL_RESEARCH.md`
- `METHOD_EFFECTIVENESS_AND_SKILL_RESEARCH.md`

---

## 4.1 来源发现与来源执行必须分开

这是后续设计中的一个核心原则：

- `来源发现`
  - 决定应该关注什么对象
  - 可能是机构、作者、社区、仓库、账号、论文库、标准组织、站点
- `来源执行`
  - 决定用什么手段拿数据
  - 可能是 RSS、API、普通抓取、浏览器抓取、agent-assisted retrieval、按需搜索

这两者不能混在一个 `FeedSource(url)` 抽象里。

如果混在一起，会导致：

- 系统把“关注对象”和“抓取手段”混为一谈
- 难以表达 X、Reddit、论坛、作者主页、论文库、标准组织这类异质来源
- 难以根据来源性质选择正确的执行策略

---

## 4.2 不是所有信息都应该持续抓取

后续必须区分至少三类对象：

### A. `stable knowledge source`

特征：

- 相对稳定
- 更新很慢
- 一次性采集或低频复查即可

例子：

- 经典论文
- 历史事件资料
- 基础定义
- 长期稳定的教科书级知识
- 标准文档的固定版本

策略：

- 以一次性导入或低频 review 为主
- 不应作为高频信息流抓取对象

### B. `reviewable source`

特征：

- 不需要高频跟踪
- 但可能会被新版本、修订版、共识变化影响

例子：

- 综述论文
- 机构白皮书
- 学会指南
- 标准文档
- 方法学总结

策略：

- 低频 review
- 版本化跟踪
- 关注“是否发生重要更新”

### C. `live intelligence source`

特征：

- 动态变化快
- 有持续信号价值
- 对决策、前沿研究、方法更新重要

例子：

- 社交平台讨论
- GitHub 项目动态
- 开源社区
- 新闻媒体
- 研究社区
- 新论文流

策略：

- 持续采集
- 强调时效性和去噪

---

## 4.3 应从“source type”升级到“source nature”

后续 source intelligence 不应只关心：

- RSS
- WEB
- API

而更应该先判断来源的性质：

- `authority source`
- `signal source`
- `frontier source`
- `community source`
- `stable knowledge source`
- `reviewable source`
- `live intelligence source`

再由执行层决定：

- 是否持续抓取
- 抓取频率
- 是否只做一次性导入
- 是否低频 review
- 是否需要 agent-assisted retrieval

---

## 5. 当前结论

1. 固定 RSS 采集不是长期可接受的主模式。
2. 搜索不是信息流的补充，而是建源、扩源、纠偏的重要前置索引能力。
3. 信息流至少要支持：
   - 最新信息
   - 权威理解
   - 前沿研究
   - 方法情报
4. 信息流必须由目标驱动，而不是默认盲抓。
5. LLM、搜索、持续采集应该形成持续发现与持续校准的闭环，而不是一次性串联。

---

## 6. 下一步建议

后续在正式设计阶段，应新增至少两份设计文档：

1. `SOURCE_INTELLIGENCE_ARCHITECTURE.md`
   - 建源、扩源、权威映射、持续关注策略

2. `METHOD_INTELLIGENCE_ARCHITECTURE.md`
   - 如何让进化大脑持续跟踪 skill、agent framework、workflow、memory、eval 等方法进展

在这两份设计完成前，不建议继续把信息流只按 RSS 管理来扩展。
