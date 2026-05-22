# claude

Now let me read the actual code changes.
Now let me read the rest of the target extraction helper and the prompt builder, plus both test files.
Now let me read the route-level test.
All files fully read. Here's the review:

---

## Review: IKE_SOURCE_INTELLIGENCE_V1_M11_VERSION_JUDGMENT_RESULT_2026-04-15

---

### Findings

**1. [正面] 这是 `ai_judgment` substrate 的第二个真实消费者——证明了 M10 提取的价值**

M10 把 judgment kernel 提取到 `feeds/ai_judgment.py`。M11 用它在一个完全不同的表面上（source-plan version changes vs discovery candidates）做 inspect。关键复用点：

- `default_model_for_provider` → L1334 ✅
- `parse_ai_judgment_payload` → L1341 ✅
- `normalize_ai_judgments_from_candidates` → L1342 ✅
- `_ai_judgment_truth_boundary` → L1351 ✅

这不是重复代码，是真正的 substrate 复用。**M10 + M11 合在一起才完整证明了 substrate 的价值。**

**2. [正面] Target extraction 的优先级排序有业务意义**

`_build_source_plan_version_judgment_targets` 的 priority 排序：

| Priority | Change Type | Rationale |
|---|---|---|
| 0 | removed | 对象消失 = 最高风险 |
| 1 | stale | 对象过期 = 需要关注 |
| 2 | authority_regressed | 权威性下降 = 质量退化 |
| 3 | subscribed | 新订阅 = controller 决定，中等关注 |
| 4 | added | 新增 = 通常是好的，低风险 |
| 5 | score_shift | 分数变化 = 最低优先级 |

这个优先级反映了"什么最可能需要 controller 关注"的实际判断。removed > stale > regressed 的排序是正确的——消失 > 过期 > 退化。

在同一优先级内，按 `abs(score_delta)` 降序排列，大变化排在前面。

**3. [正面] Fallback 到 snapshot_only targets 是防御性设计**

L996-1018: 当 `change_summary` 中没有显式 diff keys 时（例如初始版本），fallback 到 snapshot items 的前 N 个，标记为 `change_type="snapshot_only"`。

这保证了即使对没有 diff 的版本调用 inspect，也不会返回空 targets（空 targets 会导致空 prompt → model 返回无用结果）。

**4. [正面] `SourcePlanVersionJudgmentTarget` 有 `object_key` 属性——兼容 `normalize_ai_judgments_from_candidates`**

`normalize_ai_judgments_from_candidates` 要求传入的 candidates 有 `object_key` 和 `item_type` 属性。`SourcePlanVersionJudgmentTarget` 作为 Pydantic model 自然满足这个接口（L329-339）。这证明 M10 的泛化设计是对的——只要对象有 `object_key` + `item_type`，就可以被 judgment substrate 消费。

**5. [中] Prompt 包含了丰富的版本上下文——比 M7 discovery prompt 信息密度更高**

`_build_source_plan_version_judgment_prompt` (L1036-1076) 除了候选列表外，还传入了：
- `trigger_type` (manual_refresh / auto_refresh / etc.)
- `current_decision_status` (accepted / needs_review)
- `change_reason` (自由文本)
- `change_summary.summary` (结构化 diff 统计)
- `evaluation.gate_signals` (gate 信号)

这些额外上下文让 model 能做出更 informed 的判断。但 prompt 越长，model 越有可能偏离 JSON-only 输出。M10 已经有 `parse_ai_judgment_payload` 的 fence stripping + fallback 兜底。

**6. [低] Route-level test mock 了 `_load_source_plan_version_judgment_context` 和 `_build_source_plan_version_judgment_targets`**

Route test (L2815-2822) 同时 mock 了 DB 加载和 target extraction。这意味着 route test 只验证了：
- 路由分发正确
- LLM 调用 → normalize → response 组装

Target extraction 的真实行为只在 helper test 中验证。这是合理的分层（route test 不需要真实 DB），但缺少一个 integration 层的 mock（只 mock DB，不 mock extraction）。不阻碍。

**7. [正面] Helper test 验证了优先级排序的核心声明**

`test_build_source_plan_version_judgment_targets_prioritizes_risky_changes`:
- removed object (`github.com/openclaw/openclaw`) 排在第一位 ✅
- stale object (`reddit.com/r/machinelearning/comments/abc123`) 排在第二位 ✅
- change_type 正确赋值 ✅

**8. [正面] Route test 验证了 provider-aware default model 的实际使用**

L2826: `{"provider": "anthropic", "model": "", "max_candidates": 2}` — model 留空。
L2834: `self.assertEqual(data["model"], "claude-3-5-sonnet-20241022")` — 验证了 `default_model_for_provider("anthropic")` 被正确调用。

这证明了 M10 提取的 `default_model_for_provider` 在第二个消费者上也工作正常。

---

### Validation Gaps

**1. [低] 缺少 fallback (snapshot_only) 路径的测试**

当 `change_summary` 没有 removed/stale/added 等 keys 时，target extraction fallback 到 snapshot items。这个路径没有被测试。

**2. [低] 缺少版本不存在时 404 的 route test**

`_load_source_plan_version_judgment_context` 在找不到版本时抛 `HTTPException(404)`。当前 route test mock 了这个函数，没有测试 404 路径。

---

### Recommendation

**`accept`**

**理由：**

- 这是 `ai_judgment` substrate 的第二个真实消费者，materially 证明了 M10 提取的复用价值
- Target extraction 的优先级排序有清晰的业务语义（removed > stale > regressed > subscribed > added > score_shift）
- 严格保持 inspect-only：无 DB 写入，无 plan/version mutation，无 decision_status override
- 完整复用了 substrate 的 4 个核心函数
- Prompt 设计增加了版本上下文（trigger_type, change_reason, gate_signals），比 M7 的 discovery prompt 更 informed
- 92 个测试全部通过，无回归
- Truth boundary 精准："plan-version inspect judges refresh-change targets, not the canonical plan decision"

**注意项（非 blocker）：**

- 补 fallback (snapshot_only) 和 404 edge case 的测试会更完整
- 这是一个好的停止点——M7 (single inspect) + M8 (panel inspect) + M10 (substrate extraction) + M11 (second consumer) 已经证明了 AI judgment 作为 inspect-only advisory lane 的完整形状。下一步应该是 review/absorption 或真实使用反馈，而非继续扩展 inspect surface

# gemini
**IKE Sentinel (治理代理) 审查模式已激活。**

> **当前审查目标声明 (Review Target Statement)**
> **正在审查的文档/包：** `IKE_SOURCE_INTELLIGENCE_V1_M10_JUDGMENT_SUBSTRATE_RESULT_2026-04-15`
> **涉及核心代码：** `routers/feeds.py`, `feeds/ai_judgment.py`, `tests/test_feeds_source_discovery_route.py`
> **审查范围：** M10 阶段（Judgment Substrate Extraction）边界断言、重构安全性与代码物理验证。

基于你提供的 M10 代码实现与测试证据，以下是针对本次内部提取重构的深度审查报告：

### 1. 核心发现 (Findings)

* **成功的基建下沉 (Successful Substrate Extraction):** 你新建了 `services/api/feeds/ai_judgment.py`，并将以下核心的、非路由特有的逻辑从 `feeds.py` 成功剥离：
    * 模型默认值解析 (`default_model_for_provider`)
    * JSON 安全解析与 fallback (`parse_ai_judgment_payload`)
    * Payload 归一化 (`normalize_ai_judgments`, `normalize_ai_judgments_from_candidates`)
    * 面板重叠度计算 (`compare_judgment_verdict_overlap`)
    * 面板共识与分歧洞察派生 (`derive_panel_insights`)
* **路由合约的稳定性 (Route Contract Stability):** 尽管底层实现被抽离，`feeds.py` 中的 public API models（如 `SourceDiscoveryJudgeInspectResponse`）和路由函数本身完全没有被修改。这确保了外部调用的后向兼容性。
* **克制的补丁 (Restrained Repair):** 你在文档中诚实地记录了 Claude Code 第一次尝试时的失败（遗漏了某些路由内的局部调用，导致 `NameError`）。你进行的修复非常克制——你没有重写大段代码，而是通过在 `feeds.py` 底部保留 `_compare_ai_candidate_judgments` 等极薄的 wrapper，将旧的私有名称安全地桥接到新的 substrate 上，从而保护了已有的测试用例。
* **清晰的边界防御 (Clear Boundary Defense):** 你没有在这个“重构”切片中夹带私货。系统依然是 inspect-only 的，没有引入数据库表，没有增加持久化逻辑。

### 2. 验证缺口与遗留问题 (Validation Gaps / Open Questions)

这是一次出色的内部整理，但仍有一些结构上的观察可以作为未来改进的参考：

* **类型定义的重复 (Type Duplication):** 目前 `feeds.py` 和 `ai_judgment.py` 都定义了 `SourceCandidateJudgment`、`SourceDiscoveryJudgePanelConsensusItem` 等 Pydantic models。在 `feeds.py` 中，你依然在使用自己本地定义的 model 列表构建响应。虽然 Python 的鸭子类型和 Pydantic 的灵活性允许这样做（且测试通过了），但在更严格的类型检查下，这可能被视为两种不同的类型。未来的重构可以考虑将这些核心 Domain Models 提取到一个单独的 schemas 文件中。
* **`LLMAdapter` 的耦合:** `ai_judgment.py` 里的方法依然比较底层（例如接收 raw string），而实际调用大模型和构建 Prompt 的逻辑（如 `_build_ai_candidate_judgment_prompt`, `_run_ai_candidate_judgment_once`）仍然留在了 `feeds.py` 里面。这是一种务实的折中（符合 "do not widen semantics"），但这意味着 `ai_judgment.py` 目前只是个“数据处理器”，而不是一个完整的“判断引擎”。

### 3. 最终判定 (Recommendation)

M10 证明了 IKE 团队和 Claude Code 能够以受控的、增量的方式进行架构的“深呼吸”（清理内部，不改变外部）。你及时介入修复了 AI 代理在处理大文件时的局部失忆，这正是“治理代理”存在的原因。这为后续将 AI judgment 能力应用到自动过滤或持续评估（如 M11+）打下了干净的基础。

**Recommendation: `accept_with_changes` (通过，同意当前状态)**

*(注：此处的 `with_changes` 呼应了你在文档中的自我评估——即认可了你在 Claude 生成后所做的必要修正。代码目前已达标，可以直接合并。)*

**哨兵结语:** 干得漂亮。内部脂肪被成功切除了一部分。批准合并 M10，进入下一个实质性功能阶段。

# chatgpt
**Review 对象**

这次我实际 review 的是这个 zip 里的**全部文件**，不是只看第一层名字：

* **Zip 包**：`IKE_SOURCE_INTELLIGENCE_V1_M11_VERSION_JUDGMENT_RESULT_2026-04-15.zip`
* **实际 reviewed 文件列表**：

  1. `docs/ IKE_SOURCE_INTELLIGENCE_V1_M11_PHASE_JUDGMENT_2026-04-15.md`
  2. `docs/ IKE_SOURCE_INTELLIGENCE_V1_M11_PLAN_2026-04-15.md`
  3. `docs/ IKE_SOURCE_INTELLIGENCE_V1_M11_VERSION_JUDGMENT_RESULT_2026-04-15.md`
  4. `docs/ review-for IKE_SOURCE_INTELLIGENCE_V1_M11_VERSION_JUDGMENT_RESULT_2026-04-15.md`
  5. `services/api/routers/feeds.py`
  6. `services/api/tests/test_feeds_source_discovery_route.py`
  7. `services/api/tests/test_source_plan_versioning_helpers.py`

---

## verdict

**accept_with_changes**

---

## findings

### 1. 这一步的主 claim 是诚实的，且基本成立

M11 的主张是：

* 在 discovery-candidate inspect 之外，
* 再证明一个**第二个 distinct use case**
* 复用同一套内部 AI judgment substrate
* 但仍然保持 inspect-only、non-mutating、non-workflow

从实际实现看，这个主张是成立的。

新增的 route 是：

* `POST /api/sources/plans/{plan_id}/versions/{version_number}/judge/inspect`

它做的事情也和文档一致：

* 读取一个**已持久化的 version**
* 从 version snapshot / diff 中抽一个 **bounded target set**
* 跑 advisory AI judgment
* 返回规范化的 `follow/review/ignore`
* 不改 source plan
* 不改 source-plan version
* 不覆盖 `evaluation.decision_status`
* 不持久化 AI judgment

从边界诚实性来说，这一轮是过线的。

---

### 2. 这确实证明了第二个 substrate use case，而不是换皮重复 M7

这轮和 M7 的差异是实质性的，不只是换个 route 名字。

M7 的对象是：

* discovery candidates

M11 的对象是：

* persisted source-plan version changes

这里的差别很重要，因为 M11 证明的是：

> judgment substrate 不只适用于“当前发现候选”，也能适用于“已有版本事实上的变化对象”。

这个跨度是有价值的。
它说明 `feeds.ai_judgment` 现在至少不是完全绑死在 discovery route 上。

所以从“是不是第二个 distinct surface”这个问题看，我的答案是：**是。**

---

### 3. request/response 语义仍然是 inspect-only，而且比 M7 更稳一些

M11 的 response shape 比 M7 更克制：

* `version`
* `judged_targets`
* `judgments`
* `summary`
* `notes`
* `truth_boundary`

这里最好的地方有两个：

第一，`version` 本身带着 persisted `decision_status` 和 change summary。
这意味着 AI judgment 没有机会伪装成 canonical plan decision；真正的 persisted version 状态仍然原样可见。

第二，`truth_boundary` 额外补了一句：

> `plan-version inspect judges refresh-change targets, not the canonical plan decision`

这句很重要，而且是对的。
它把 AI judgment 明确压回到了“version refresh 变化对象的 advisory inspect”，而不是“plan decision 审批”。

---

### 4. target extraction 是有界的，而且总体 coherent，但它仍然是 heuristic，不是语义完备

`_build_source_plan_version_judgment_targets(...)` 现在的做法是：

优先级从高到低 roughly 是：

1. `removed`
2. `stale`
3. `authority_regressed`
4. `subscribed`
5. `added`
6. `score_shift`

然后按：

* 变化优先级
* score delta 绝对值
* object_key

排序，再截断到 `max_candidates`。

这个逻辑是 coherent 的，我认为对当前 slice 足够合理。
它表达的其实是：

> 先把最可能需要人/模型再看一眼的 version-change objects 抽出来

这比随机挑、或按 snapshot 全量喂模型健康得多。

但这里也必须说清楚：

* 这是 **bounded heuristic extraction**
* 不是“系统已经懂 version change significance”

尤其是 fallback：

* 如果 version 没有显式 diff keys，就从 snapshot 里取前几个 object，标成 `snapshot_only`

这个 fallback 是实用的，但它也意味着：

* 这条 inspect lane 倾向于**保持非空**
* 而不是严格要求“只有明确 change keys 才能 judgment”

这不一定错，但它是一个需要明确知道的设计选择。

---

### 5. 这轮 route proof 是成立的，但 helper proof 还不算厚

当前测试结构是这样：

**helper test**

* 证明 `_build_source_plan_version_judgment_targets(...)` 会优先取更 risky 的变化：

  * removed
  * stale
  * authority regression

**route test**

* patch 掉 context loader
* patch 掉 target builder
* patch 掉 LLMAdapter
* 验证：

  * route contract 正常
  * provider-aware default model 生效
  * advisory summary/judgment 正常返回
  * truth boundary 有 inspect-only 语义

这套验证对“这个 bounded packet 是否成立”来说，我认为**基本够了**。
但它的弱点也很明显：

* route test 没有真正把 extraction helper 串进 route 一起验证
* helper test 只覆盖了一个高风险排序 case
* 没覆盖 fallback `snapshot_only`
* 没覆盖 `max_candidates` 截断
* 没覆盖 `added/subscribed/score_shift` 这些次级 change family

所以从 review question 5 “focused tests sufficient?” 来说，我的判断是：

> **对当前 slice 可以算 sufficient，但只是刚好够，不算厚实。**

---

### 6. 这一步比 persistence/workflow 扩张健康得多，是一个好停点

M11 的 phase judgment 和 result judgment 都抓住了同一个关键点：

> 这一步的意义是证明 substrate 复用，不是继续扩 workflow

我认同这个判断。
因为现在最容易犯的错是：

* 既然已经能 judge version change，
* 那下一步就 persistence 吧，
* 或者 auto-promote / auto-rollback 吧，
* 或者 generic approval framework 吧。

这几步都**不应该**是 M11 的自然延伸。

M11 的健康价值恰恰在于：

* 它把 AI judgment 从 discovery candidate 扩到 version surface
* 但仍然停在 inspect-only

所以这一步是一个**好的 stop point**。

---

## risks

### 1. 最大风险：`version judgment` 被误读成 `version decision`

这轮实现其实已经很克制了，但语义上最危险的地方仍然是：

* route 返回了 version
* route 返回了 judgments
* route 返回了 summary

外部很容易自然地把它读成：

> “模型在判断这个 version 应不应该接受/回滚/跟进”

但当前代码并**没有**做这个。
它只是在 judge **refresh-change targets**，不是 judge **the version as a whole**。

所以后续文档和命名都要继续压住这个误读。

---

### 2. 第二个风险：fallback `snapshot_only` 会被误读成“version judgment 总应该有对象可看”

现在 helper 的 fallback 逻辑会让 inspect lane 在无显式 diff keys 时仍尽量非空。
这在产品体验上很自然，但语义上也有风险：

* 它会让人觉得“每个 version 都应该拿去让 AI judge”
* 而不是“只有有变化意义的 version 才值得 judge”

所以这块至少要继续明确：
`snapshot_only` 只是 bounded fallback，不代表 version truly needs AI review。

---

### 3. 第三个风险：当前还只是 single-model advisory lane，不能过度上纲成“version intelligence”

result 文档自己已经写了 known risks：

* single-model inspect
* heuristic extraction
* 不证明 workflow usefulness

这个判断是对的。
我建议保持原样，不要再包装成更强能力。

---

## whether this slice should stop here or immediately continue

**应该先停，不应该立刻继续。**

更准确地说：

* **这条 slice 本身应当 stop here**
* 下一步可以做的是 **review / absorption**
* 而不是顺着它直接扩成：

  * persistence
  * panel
  * auto-promotion
  * auto-rollback
  * generic approval framework

如果后续真要继续，也应该是一个**新 packet**，而不是把 M11 顺延成 workflow line。

---

## final judgment

**M11 是成立的。**

它已经足够证明：

* `feeds.ai_judgment` 不只锁在 discovery candidate inspect
* 它已经能被复用到第二个 truth-adjacent surface：

  * source-plan version changes

同时，它还没有明显越界成 workflow。

所以我给：

**`accept_with_changes`**

### 我建议补的 changes 很简单：

1. **补一个 focused helper test**
   覆盖 `snapshot_only` fallback 或 `max_candidates` 截断，二选一都行。

2. **在结果文档里再强调一句**
   `version judgment` judges change targets, **not the version decision itself**。

3. **把这一步明确标成 stop point**
   后续如果要 persistence/workflow，必须单独立 packet，不得作为 M11 的自然延伸。

---

一句话总结：

**这一步是一个健康、克制、真实的第二 substrate use case 证明；它的价值在于证明“AI judgment substrate 已经能跨到 version surface”，而不是证明“AI 已经能替代 version-level decisioning”。**
