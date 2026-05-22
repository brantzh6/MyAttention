# 来源智能架构设计 V1

> 本文档定义 MyAttention 的 `Source Intelligence Architecture` `V1`。
>
> 目标不是简单“加更多 RSS”，而是建立一个：
>
> - 目标驱动
> - 可持续发现
> - 可持续校准
> - 可区分冷热对象
> - 可与搜索、LLM、持续采集联动
>
> 的来源智能体系。

---

## 1. 文档定位

本设计解决的问题是：

- 面对一个主题，系统应知道去哪里找
- 系统应知道为什么关注某个来源
- 系统应知道某个来源适合持续监控还是低频 review
- 系统应知道该用什么执行方式获取数据
- 系统应能持续升级、降级、替换和淘汰来源

本设计不直接解决：

- 任务状态机
- 多脑协作协议
- 全量记忆分层
- 全量知识结构化

这些属于后续设计：

- `TASK_AND_WORKFLOW_MODEL.md`
- `BRAIN_CONTROL_ARCHITECTURE.md`
- `MEMORY_ARCHITECTURE.md`

---

## 2. 设计目标

### 2.1 核心目标

- 从“固定 RSS 列表”升级为“目标驱动的 source intelligence”
- 让信息流能够持续发现新入口，而不是只重复旧入口
- 让来源管理具备 promotion / demotion / replacement / retirement 能力
- 为后续深度研究、知识构建和进化大脑提供更可靠的输入基础

### 2.2 架构目标

- 来源发现与来源执行彻底分层
- 来源对象不再只等于 `url`
- 支持冷 / 温 / 热对象的不同策略
- 支持 authority / signal / frontier / community 的不同权重
- 允许 agent-assisted retrieval，但不让 agent 直接替代持续采集主链路

### 2.3 非目标

- 本阶段不追求覆盖所有网站和平台
- 本阶段不追求一步到位的“全自动最佳建源”
- 本阶段不让 source intelligence 直接接管整个采集执行层

---

## 3. 核心纠偏

### 3.1 不是先想抓什么协议，而是先想关注什么对象

当前常见错误是：

- RSS 是来源
- API 是来源
- Web 是来源

这不对。

这些只是执行协议。

真正的来源对象可以是：

- 机构
- 作者
- 研究团队
- 社区
- 账号
- 仓库
- 站点
- 论文库
- 标准组织
- 话题 / 标签

### 3.2 不是所有来源都应该进入持续高频抓取

必须区分：

- 冷对象：一次性导入 + 低频 review
- 温对象：定期 review
- 热对象：持续监控

### 3.3 搜索不是补充，而是前置索引能力

source intelligence 的正确循环不是：

- 先固定源
- 再抓

而是：

- 先明确目标
- 再搜索发现候选来源和关注对象
- 再由 LLM / 规则判断是否值得长期关注
- 再进入 feed / review / agent-assisted retrieval
- 再持续校准和替换

---

## 4. Source Intelligence 主循环

```text
目标 / 主题 / 研究任务
  -> discover
  -> evaluate
  -> subscribe / review / ignore
  -> collect / review / special retrieval
  -> observe quality and yield
  -> promote / demote / replace / retire
  -> rediscover
```

进一步展开：

```text
Problem framing
  -> Search discovery
  -> Candidate source/object set
  -> Authority + relevance + freshness judgment
  -> Source plan update
  -> Execution strategy assignment
  -> Collection / review / agent-assisted retrieval
  -> Signal / evidence / facts enter storage
  -> Quality evaluation and source evolution
```

这意味着信息流不再只是抓取器，而是：

- `discover`
- `judge`
- `subscribe`
- `collect`
- `review`
- `refresh`
- `retire`

---

## 5. 逻辑分层

### 5.1 Discovery Layer

职责：

- 搜索新来源
- 搜索新对象
- 搜索新入口
- 搜索新的权威节点、社区节点、前沿节点

输入：

- 主题
- 任务目标
- 关注类型

输出：

- candidate source list
- candidate object list
- candidate keywords / tags

### 5.2 Evaluation Layer

职责：

- 判断是否值得长期关注
- 判断属于哪类来源
- 判断冷热属性
- 判断执行策略

输出：

- source classification
- monitoring mode
- execution strategy
- review cadence

### 5.3 Subscription Layer

职责：

- 把评估后的对象纳入长期关注集合
- 或纳入低频 review
- 或仅保留为按需发现来源

输出：

- active source plan
- review plan
- retirement plan

### 5.4 Execution Strategy Layer

职责：

- 决定该用哪种方式获取

方式可能包括：

- RSS
- API
- direct fetch
- browser fetch
- proxy fetch
- agent-assisted retrieval
- search-on-demand

### 5.5 Collection / Review Layer

职责：

- 真正执行抓取或 review
- 持久化 raw / fact / enrichment
- 产出数据供知识层和进化层使用

### 5.6 Evolution Layer

职责：

- 评估来源是否仍有效
- 评估来源是否值得提升/降级/淘汰
- 评估是否需要补新来源

---

## 6. 来源对象模型 V1

后续至少要区分两层对象。

### 6.1 SourceObject

表示“关注对象”，不是协议。

建议字段：

- `object_id`
- `object_type`
  - `organization`
  - `author`
  - `community`
  - `account`
  - `repository`
  - `website`
  - `paper_hub`
  - `standards_body`
  - `topic`
- `name`
- `canonical_ref`
- `topic_scope`
- `authority_type`
- `signal_value`
- `frontier_value`
- `community_value`
- `source_nature`
  - `authority`
  - `signal`
  - `frontier`
  - `community`
- `temperature`
  - `cold`
  - `warm`
  - `hot`
- `status`
  - `candidate`
  - `active`
  - `review`
  - `retired`
- `version`

### 6.2 SourceEndpoint

表示“执行入口”。

建议字段：

- `endpoint_id`
- `object_id`
- `endpoint_type`
  - `rss`
  - `api`
  - `web`
  - `browser`
  - `agent`
  - `search`
- `url_or_locator`
- `auth_required`
- `proxy_required`
- `anti_crawl_risk`
- `cadence`
- `execution_strategy`
- `enabled`
- `health_score`
- `last_success_at`
- `last_failure_at`
- `version`

结论：

- 一个关注对象可以有多个执行入口
- 一个执行入口只是手段，不是来源本体

---

## 7. 来源分类维度 V1

### 7.1 按价值分类

- `authority source`
- `signal source`
- `frontier source`
- `community source`

### 7.2 按时效性分类

- `cold object`
- `warm object`
- `hot object`

### 7.3 按使用场景分类

- `stable knowledge source`
- `reviewable source`
- `live intelligence source`

### 7.4 按执行难度分类

- `easy structured`
- `semi-structured`
- `anti-crawl sensitive`
- `agent-assisted only`

---

## 8. 执行策略矩阵 V1

### 8.1 冷对象

典型策略：

- 一次性导入
- 低频 review
- 版本比较

适合：

- 历史资料
- 经典论文
- 基础理论
- 老标准

### 8.2 温对象

典型策略：

- 定期 review
- 变化检测
- 必要时重新抽取和更新知识

适合：

- 指南
- 白皮书
- 综述
- 学会文件

### 8.3 热对象

典型策略：

- 高频持续监控
- 事件化处理
- 快速去噪
- 快速入事实层

适合：

- 社区动态
- 仓库动态
- 媒体动态
- 前沿研究动态

---

## 9. Search / LLM / Feed / Agent 的关系

### 9.1 Search

职责：

- 发现来源
- 发现新对象
- 发现新入口
- 做校准

它是 source intelligence 的前置索引能力。

### 9.2 LLM

职责：

- 理解目标
- 判断来源价值
- 帮助分类与策略选择
- 生成 source plan 候选

### 9.3 Feed / Collection

职责：

- 对已决策关注的对象做持续执行
- 提供稳定、低成本、可回放的数据入口

### 9.4 Agent-assisted retrieval

职责：

- 建源探索
- 复杂站点
- 社交平台和强反爬场景
- 一次性研究任务中的特殊获取

限制：

- 不应替代全量持续采集主链路
- 不应成为事实层唯一入口

---

## 10. OpenClaw / agent-assisted retrieval 的位置

OpenClaw 这类 agent 更适合放在：

- `discovery`
- `special retrieval`
- `strategy exploration`

而不是放在：

- 高频批量抓取
- 长期低成本事实层采集

这点必须明确，否则系统会：

- 成本失控
- 稳定性下降
- 可回放性变差

---

## 11. 与现有代码的对接方式 V1

不推倒现有信息流执行层，先做旁路接入。

### 11.1 保留

- 现有 fetcher
- 现有 import pipeline
- 现有 raw / feed_items 持久化

### 11.2 新增

- source intelligence service
- candidate source discovery
- source object model
- execution strategy assignment
- source promotion/demotion/replacement flow

### 11.3 逐步切换

- 当前 `feed_sources.json` / 运行时 sources 先继续工作
- source intelligence 先作为“建源和校准层”
- 稳定后再逐步接管来源计划更新

---

## 12. 对数据层的要求

来源智能后续至少需要这些数据对象：

- `source_objects`
- `source_endpoints`
- `source_discovery_runs`
- `source_evaluations`
- `source_plan_versions`
- `source_events`

这部分暂时不在这里直接定表结构，但设计上必须预留。

---

## 13. 关键里程碑 V1

### M1

系统可以根据主题生成候选来源和关注对象，而不是只依赖固定 RSS。

### M2

系统可以给每个候选对象明确：

- 来源性质
- 热度层级
- 执行策略
- review 频率

### M3

系统可以持续：

- promote
- demote
- replace
- retire
- rediscover

### M4

source intelligence 正式成为信息流上游控制层，而不是附属功能。

---

## 14. 当前已知局限

这份设计是 `V1`，当前仍有局限：

- 来源对象 taxonomy 还不完备
- authority 评分规则还偏启发式
- agent-assisted retrieval 的策略还未细化到平台级
- 还未与任务系统和版本系统接通
- 还未正式定义 source plan 的版本化机制

所以它必须被后续迭代。

---

## 15. 当前结论

对 MyAttention 来说，source intelligence 不是“信息流设置页增强”。

它是后续这些能力的上游基础：

- 信息抓取
- 深度研究
- 知识构建
- 进化大脑
- 方法情报

因此，后续信息流的正确形态不是：

- 固定几个 RSS 一直抓

而是：

- 目标驱动发现
- 结构化评估
- 策略化执行
- 持续校准与替换
