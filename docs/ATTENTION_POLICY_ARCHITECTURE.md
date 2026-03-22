# Attention Policy Architecture V1

> 本文档定义 MyAttention 的 `Attention Policy Architecture V1`。
>
> 目标不是发明一个固定 attention 分数公式，而是建立一个：
>
> - 动态加载
> - 可版本化
> - 可门禁
> - 可回滚
> - 可被 LLM 驱动但不被 LLM 随意支配
>
> 的关注策略系统。

---

## 1. 文档定位

本设计解决的问题是：

- 如何把“什么值得关注”从硬编码逻辑升级成可配置策略
- 如何让搜索 + LLM 动态发现关注对象，但又不失控
- 如何记录这次 attention 决策为什么成立
- 如何比较不同 attention policy 版本的效果
- 如何对候选关注对象进行质量门禁

本设计不直接解决：

- 具体搜索 provider 接口实现
- 具体 agent-assisted retrieval 执行细节
- 全量知识图谱对象模式

这些属于后续实现层或相邻模块设计。

---

## 2. 核心原则

### 2.1 不把方法写死在代码分支里

后续不能继续依赖这种结构：

- `if topic == ...`
- `if focus == ...`
- `if method topic then github boost`

原因：

- 不可追踪
- 不可比较
- 不可回滚
- 不可版本化
- 容易随需求堆规则

### 2.2 不把 LLM 当成真理生成器

LLM 可以：

- 发现候选对象
- 给出理由
- 提炼结构
- 初步分类

LLM 不应直接决定：

- 最终注意力策略定义
- 最终质量判断标准
- 最终是否接受一个新 policy

### 2.3 动态，不等于无约束

Attention 应该是动态系统，但动态来自：

- 可配置 policy
- 可替换维度
- 可调整权重
- 可比较版本
- 可门禁接受

而不是来自 LLM 自由发挥。

### 2.4 所有 policy 都只是 V1 / V2 / Vn

attention policy 必须显式版本化。

后续任何 attention policy 都应被视为：

- 当前最优猜测
- 可观察
- 可校正
- 可废弃

---

## 3. Attention Policy 的职责

一个 attention policy 至少要回答 5 个问题：

1. 针对什么问题类型生效
2. 关注哪些对象类型
3. 按哪些维度评价候选对象
4. 如何做组合平衡和质量门禁
5. 最终产出什么动作

所以 policy 的职责不是简单打分，而是：

- `candidate evaluation`
- `portfolio balancing`
- `quality gating`
- `attention action selection`

---

## 4. 核心对象模型 V1

### 4.1 AttentionCandidate

表示一次发现流程产出的候选关注对象。

建议字段：

- `candidate_id`
- `object_type`
  - `source`
  - `person`
  - `community`
  - `repository`
  - `organization`
  - `event`
- `canonical_key`
- `display_name`
- `primary_url`
- `discovery_context`
- `raw_evidence`
- `structured_attributes`
- `discovered_at`

### 4.2 AttentionPolicy

表示一个可执行的 attention 策略。

建议字段：

- `policy_id`
- `policy_name`
- `policy_type`
  - `topic_source_discovery`
  - `frontier_monitoring`
  - `method_intelligence`
  - `decision_support_attention`
- `status`
  - `draft`
  - `active`
  - `deprecated`
  - `retired`
- `version`
- `parent_version`
- `scope`
  - 问题类型、主题类型、适用上下文
- `object_type_targets`
- `dimension_config`
- `portfolio_rules`
- `gate_rules`
- `action_rules`
- `created_by`
- `created_at`

### 4.3 AttentionEvaluation

表示一个候选对象在某一策略版本下的结构化评价。

建议字段：

- `evaluation_id`
- `candidate_id`
- `policy_id`
- `policy_version`
- `dimension_scores`
- `evidence_summary`
- `reasoning_summary`
- `portfolio_bucket`
- `recommended_action`
- `confidence`
- `created_at`

### 4.4 AttentionDecision

表示最终被接受或拒绝的关注动作。

建议字段：

- `decision_id`
- `candidate_id`
- `policy_id`
- `policy_version`
- `decision_status`
  - `accepted`
  - `needs_review`
  - `rejected`
- `accepted_action`
  - `watch`
  - `promote`
  - `review`
  - `sample`
  - `retire`
  - `escalate`
- `change_reason`
- `review_notes`
- `created_at`

### 4.5 AttentionReview

表示对现有注意力配置的周期复核。

建议字段：

- `review_id`
- `subject_type`
  - `policy`
  - `candidate`
  - `portfolio`
  - `attention_plan`
- `subject_id`
- `trigger_type`
  - `scheduled`
  - `manual`
  - `evolution`
- `summary`
- `decision`
- `created_at`

---

## 5. 配置层结构

### 5.1 Dimension Config

定义：

- 本策略看哪些维度
- 各维度怎么计算
- 权重如何分配

建议结构：

```json
{
  "goal_relevance": { "enabled": true, "weight": 0.20 },
  "authority_score": { "enabled": true, "weight": 0.18 },
  "frontier_score": { "enabled": false, "weight": 0.00 },
  "community_signal_score": { "enabled": true, "weight": 0.12 },
  "bridge_score": { "enabled": true, "weight": 0.08 }
}
```

注意：

- 这里的权重也不应被视为终局值
- 后续可以演化为分段规则、非线性门槛或 learned calibration

### 5.2 Portfolio Rules

定义：

- 最终结果的结构平衡

例如：

- 至少 2 个 authority objects
- 至少 1 个 community object
- 至少 1 个 implementation object
- 单一 object_type 不超过 40%
- 单一 domain 不超过 25%

这一步非常关键，因为它直接解决：

- 阿里云过靠前
- 官网过多
- 缺少 repo/person/community

### 5.3 Gate Rules

定义：

- 候选对象何时自动接受
- 何时需要人工复核
- 何时应拒绝

例如：

- authority 太低且 evidence 过少 -> reject
- 单次搜索噪音命中 -> needs_review
- portfolio bucket 缺失但对象高价值 -> accept with watch

### 5.4 Action Rules

定义：

- 在不同评分和 gate 结果下，产出什么动作

例如：

- `accepted + high authority + stable` -> `promote`
- `accepted + frontier + noisy` -> `watch`
- `needs_review + high novelty` -> `review`
- `rejected + low evidence` -> `sample` or `retire`

---

## 6. Attention Runtime Pipeline

V1 运行流程建议：

```text
Problem framing
  -> policy selection
  -> search prompt generation
  -> candidate discovery
  -> LLM structured evaluation
  -> portfolio balancing
  -> quality gate
  -> decision
  -> action
  -> review
  -> version/evaluation logging
```

### 6.1 Policy selection

根据：

- 问题类型
- 思维模型
- attention 场景

选择当前应使用的 policy version。

### 6.2 Search-driven discovery

通过：

- 搜索引擎
- 已有信息流
- 已有知识库
- 已有 attention objects

发现候选对象。

### 6.3 LLM structured evaluation

LLM 的职责：

- 从候选对象和证据中提取结构化信息
- 解释为什么值得关注
- 给出维度级判断草稿

LLM 输出必须是结构化的，不应直接产出最终接受结论。

### 6.4 Policy-based balancing and gating

系统根据当前 policy：

- 做组合平衡
- 做质量门禁
- 得到建议动作

### 6.5 Review loop

后续通过：

- source plan 成效
- 实际任务产出
- 知识沉淀
- 用户采纳/忽略
- 进化大脑观察

回头评估 policy 是否有效。

---

## 7. 为什么这层必须版本化

如果 attention policy 不版本化，后面无法回答：

- 为什么这次推荐了这些对象
- 为什么之前没有推荐
- policy 变更后，结果是更好还是更差
- 某类 topic 为何突然从 repo 导向变成官网导向

所以 attention policy 至少要进入：

- `policy_version`
- `evaluation_result`
- `effective_from`
- `effective_to`
- `rollback_target`

也就是说，attention policy 是 versioned intelligence object，不是普通配置。

---

## 8. 质量管理与门禁

你前面提的要求是关键：即使是动态系统，也必须有门禁。

后续至少要有三层质量控制。

### 8.1 Structural validity

检查：

- 候选对象结构是否完整
- object_type 是否可识别
- 证据是否存在
- 关键字段是否缺失

### 8.2 Portfolio validity

检查：

- 是否过度偏向单一类型
- 是否只覆盖官网/官方博客
- 是否缺少 community / repo / person / implementation

### 8.3 Outcome validity

检查：

- 被关注对象后续是否真的产生价值
- 是否触发高质量任务/知识沉淀/决策支持
- 是否长期只是噪音

这层决定 policy 该保留、调参还是淘汰。

---

## 9. 和现有模块的关系

### 9.1 和 source intelligence

当前 source plan 是第一个落点，但未来不应只服务 source。

先期关系应是：

- attention policy
  -> candidate discovery
  -> source plan generation

后续应扩展到：

- person plan
- repository plan
- community plan

### 9.2 和 evolution brain

进化大脑后续应评估：

- 哪个 attention policy 更有效
- 哪类对象带来更高 downstream value
- 当前 attention portfolio 是否失衡

### 9.3 和 memory

需要记录：

- 哪些 policy 曾经有效
- 哪些候选对象长期高价值
- 哪些关注动作经常无效

所以 attention 结果也应沉淀进：

- task memory
- procedural memory
- episodic memory

---

## 10. V1 实施顺序

当前最合理的实现顺序：

1. 定义 `attention candidate` 数据对象
2. 定义 `attention policy` 配置对象
3. 把现有 source discovery 接到 policy-driven evaluation
4. 加入 portfolio balancing
5. 加入 gate rules
6. 记录 evaluation / decision / review
7. 再扩到 person / repo / community

不建议的顺序：

- 先做一个固定总分公式
- 先把所有对象类型一次性打通
- 先做复杂自学习策略

---

## 11. 当前结论

后续正确方向不是：

- 再给 `source plan` 加更多临时排序规则

而是：

- 把 source intelligence 提升到 attention policy 驱动
- 用搜索 + LLM 动态发现对象
- 用 policy + gate + versioning 管理变化

所以：

- 动态发现是必须的
- 结构化门禁是必须的
- policy 版本化也是必须的
