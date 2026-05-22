# Attention Model Research

> 目标：研究 MyAttention 应如何回答“什么值得关注、为什么值得关注、应该以什么方式持续关注”，并把 source / person / community / repo / event / method 等对象放进同一套可进化的关注模型，而不是继续停留在固定 RSS 与静态排序规则上。

---

## 1. 先纠偏

“Attention 算法”这个说法有启发性，但如果直接落成一个固定打分公式，风险很大：

- 会把策略问题伪装成算法问题
- 会过早写死分类和权重
- 会让系统看起来像“在计算”，实际仍然是在硬编码
- 会忽略不同问题类型下，值得关注的对象和标准完全不同

因此，当前阶段更合理的目标不是直接发明一个最终 Attention Algorithm，而是先定义：

- `Attention Object`
- `Attention Dimensions`
- `Attention Policy`
- `Attention Review Loop`

也就是先做一个 **可运行、可观察、可迭代的 Attention Model V1**。

---

## 2. Attention 不只针对“信息源”

当前最需要纠正的地方是：关注对象不应只等于一个 URL 或 RSS feed。

后续至少应支持这些对象类型：

- `source`
  - 网站、媒体、期刊、博客、数据库、标准组织
- `person`
  - 研究者、工程师、意见领袖、创始人、学者、分析师
- `community`
  - Reddit 社区、论坛、邮件列表、HN、Slack/Discord/微信群等可公开社区
- `repository`
  - GitHub/GitLab 项目、组织、awesome list、benchmark repo
- `organization`
  - 公司、实验室、大学、协会、基金会、监管机构
- `event`
  - 会议、发布会、听证会、公开演讲、论坛、比赛、政策节点
- `topic`
  - 主题、标签、关键词簇
- `method`
  - 某类框架、工作流、skill、工程方法

这意味着后续 source intelligence 上层其实应该进一步升级为：

- `attention intelligence`

source 只是 attention object 的一种。

---

## 3. 值得关注，不等于“更新快”

Attention 不能只盯时效性。

后续至少要区分这些价值来源：

- `authority`
  - 是否代表权威理解、正式发布、稳定事实
- `novelty`
  - 是否带来新信号、新方法、新入口、新变化
- `timeliness`
  - 是否对当前决策窗口敏感
- `impact`
  - 是否会影响系统目标、用户决策、研究方向
- `signal_quality`
  - 是否高密度、低噪音、少营销包装
- `bridge_value`
  - 是否能连接不同学科、社区或方法
- `execution_value`
  - 是否能直接转化为任务、建源、验证、实施

所以：

- 官网不一定值得高频关注，但适合做 authority anchor
- 社交媒体不一定更权威，但适合做 signal detection
- 高星 repo 不等于高价值，但通常比随机博客更值得进入方法关注池
- 公开演讲、议程、与会关系、合作网络，很多时候比单篇文章更值得关注

---

## 4. Attention Dimensions V1

当前建议把 V1 关注模型分成 12 个维度。

### 4.1 Core Relevance

- `goal_relevance`
  - 与当前目标、主题、任务的相关性
- `problem_fit`
  - 是否适合当前问题类型与思维模型

### 4.2 Knowledge Value

- `authority_score`
  - 对正式理解、稳定知识、权威结论的价值
- `frontier_score`
  - 对前沿研究、方法演进、早期信号的价值
- `evidence_density`
  - 是否能提供高密度证据与可交叉验证材料

### 4.3 Time Value

- `freshness_score`
  - 最近是否有更新、变化是否频繁
- `timeliness_score`
  - 对当前窗口是否有强时间敏感性

### 4.4 Network / Ecosystem Value

- `centrality_score`
  - 在相关网络里是否处于核心位置
- `bridge_score`
  - 是否连接不同圈层、学科、社区、组织
- `community_signal_score`
  - 是否能反映社区真实关注度和长期讨论强度

### 4.5 Operational Value

- `accessibility_score`
  - 是否能稳定拿到，成本和反爬复杂度如何
- `actionability_score`
  - 是否能直接转成 source plan、研究任务、验证任务、产品优化

这些维度不应该全部等权，也不应固定写死。

---

## 5. 不同问题，权重不同

这也是为什么 Attention 不能是单一静态算法。

### 5.1 主题建源

更看重：

- goal_relevance
- authority_score
- centrality_score
- accessibility_score
- bridge_score

### 5.2 前沿研究监控

更看重：

- frontier_score
- freshness_score
- community_signal_score
- bridge_score
- evidence_density

### 5.3 决策支持

更看重：

- authority_score
- timeliness_score
- actionability_score
- evidence_density

### 5.4 方法与 skill 研究

更看重：

- novelty
- execution_value
- github/repo 信号
- community_signal_score
- reproducibility

结论：

- 同一个对象，在不同问题下 attention value 不同
- 关注策略必须经过 `problem framing -> thinking framework -> method selection`

---

## 6. 关注策略不只决定“排前面”，还决定“怎么关注”

Attention 输出不该只是一个 rank。

后续至少应输出：

- `watch`
  - 值得继续跟踪
- `promote`
  - 升为长期核心对象
- `review`
  - 先人工或模型复核
- `sample`
  - 偶尔抽样检查
- `retire`
  - 暂时移出注意力核心
- `escalate`
  - 升级成专题研究或任务

并进一步决定执行方式：

- `feed_or_fetch`
- `api_poll`
- `search_review`
- `review_capture`
- `agent_assisted`
- `one_time_ingest`
- `low_frequency_review`

也就是说 attention model 的输出是：

- `what to watch`
- `why`
- `how`
- `how often`
- `what to do next`

---

## 7. 一个 V1 注意力策略框架

当前最适合实现的不是 learned ranking，而是 policy-driven ranking。

### Step 1. Object identification

从搜索、信息流、手工输入、知识库中识别对象：

- source
- person
- organization
- repository
- community
- event

### Step 2. Object typing

判定对象性质：

- authority / signal / frontier / community / stable / reviewable / live

### Step 3. Dimension scoring

按当前任务上下文给出多个维度分值。

### Step 4. Portfolio balancing

注意力不应只给最高分对象，还要做组合平衡：

- authority bucket
- frontier bucket
- community bucket
- implementation bucket
- person bucket

否则会出现：

- 官网过多
- 单一国家/语言来源过多
- 缺少社区
- 缺少代码实现入口

### Step 5. Attention action

决定：

- subscribe
- watch
- review
- retire
- escalate

### Step 6. Review and recalibration

经过 refresh、任务结果、使用反馈后重新校准。

---

## 8. 为什么现在质量不够好

当前 source plan 机制已经跑起来，但质量仍然偏弱，根因大致有这些：

- query 模板太通用
- 当前候选仍偏站点思维
- authority 压过了 diversity
- 没有 repository / person / community 的正式对象模型
- 没有 portfolio balancing
- 没有“当前问题类型 -> attention 权重”的正式路由

所以像“多智能体研究”这类 topic，容易变成：

- 若干官网
- 若干官方博客
- 若干可抓取搜索结果

而缺少：

- GitHub 高活跃项目
- 行业主导公司研究/工程博客
- 高价值社区
- 代表性人物与其输出轨迹

这不是 UI 问题，而是 attention model 还没正式建起来。

---

## 9. 和进化大脑的关系

进化大脑后续不只是监控系统故障，也应该监控 attention quality。

至少应持续观察：

- 不同 topic 的 object diversity 是否过低
- 是否长期偏向单一来源类型
- 哪些 source plan 长期没有高价值订阅对象
- 哪些 object 被持续关注但从未产生实际价值
- 哪些 object 经常触发高价值任务/知识沉淀/决策支持

也就是说：

- Attention Model 本身也应进入方法评估与进化闭环

---

## 10. V1 实施建议

当前不建议直接做“学习型算法”。

更现实的 V1 顺序：

1. 补 attention object 类型
   - source / person / repository / community / organization / event
2. 补 attention dimensions
3. 补 topic-type-aware ranking policy
4. 补 portfolio balancing
5. 补 attention action 输出
6. 再把它接进 source plan / source intelligence UI / evolution

---

## 11. 对当前 4 类 focus 的判断

当前的：

- `authoritative`
- `latest`
- `frontier`
- `method`

只能算 V1 入口分类。

它们的价值在于：

- 足够简单
- 能先把系统跑起来

它们的问题在于：

- 不够科学
- 不够细
- 不能覆盖 person/community/repo/event
- 不足以支撑后续 attention policy

所以后续不应围绕这 4 类继续无限叠规则，而应让它们逐步退化成：

- 一个浅层 UI 入口
- 而不是底层 attention ontology

---

## 12. 当前结论

后续更正确的方向不是继续问：

- “该加哪些 RSS？”

而是问：

- “在这个问题下，哪些对象值得进入注意力系统？”
- “这些对象为什么值得关注？”
- “它们分别适合高频跟踪、低频 review，还是一次性摄取？”
- “当前 attention portfolio 是否结构失衡？”

所以 source intelligence 的下一层，应该是：

- `Attention Intelligence`

source plan 只是它的第一个具体落点。
