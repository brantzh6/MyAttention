# claude

Now let me read the actual code — the panel route, request/response models, agreement logic, and test.
Now let me read the agreement comparison function and the refactored `_run_ai_candidate_judgment_once`.
Let me also check how M7 was refactored — the `_parse_ai_candidate_judgment_payload` that was introduced (addressing the M7 review's `json.loads` error handling concern).
Excellent. Now let me check the updated `_normalize_ai_candidate_judgments` signature (it now returns 3 values including discarded count).
All code fully read. Here's the review:

---

## Review: IKE_SOURCE_INTELLIGENCE_V1_M8_PANEL_INSPECT_RESULT_2026-04-15

---

### Findings

**1. [正面] M7 review 中提出的两个 changes 都已被吸收**

M7 review 的核心 `accept_with_changes` 要求是：
- **`json.loads` error handling** → 已解决：`_parse_ai_candidate_judgment_payload` (L989-1003) 包含 markdown fence stripping + try/except + fallback to empty payload with `"invalid_json_fallback"` status ✅
- **parse status 可审计** → `parse_status` 现在出现在 notes 中（`primary_parse_status=valid_json`） ✅
- **discarded judgments 可审计** → `_normalize_ai_candidate_judgments` 现在返回 discarded count ✅

这些改进同时受益于 M7 和 M8 两条路径。说明 M8 不是简单堆积，而是在吸收 M7 review 反馈的基础上增量构建。

**2. [正面] M7 → M8 的重构路径干净**

M7 的 `_run_ai_candidate_judgment_inspect` 中的内联逻辑被抽取为 `_run_ai_candidate_judgment_once` (L1006-1028)，现在被 M7 route 和 M8 route 共同复用。这是正确的重构——M8 不是 copy-paste M7，而是提取了 shared kernel。

**3. [正面] Agreement comparison 逻辑简洁且不越界**

`_compare_ai_candidate_judgments` (L1031-1051)：
- 只比较 verdict 是否相同，不做加权、投票或偏好
- 清晰地分离了 `agreed` / `disagreed` / `primary_only` / `secondary_only`
- `panel_signal` 只有两个值：`"stable"` (全部同意) 或 `"mixed"` (有分歧)
- 没有产出合并后的 "panel verdict"——完全遵守了 "non-merging" 承诺 ✅

**4. [中] 两个 model lane 是串行执行的**

L1120-1132：primary 和 secondary judgment 是顺序 `await` 的。这意味着 panel inspect 的延迟 ≈ 2× 单次 judgment。

对于 inspect-only 的 advisory lane 来说这不是 blocker（不在关键路径上），但如果未来有实际使用压力，可以用 `asyncio.gather` 并行执行两个 model 调用。

**5. [低] `secondary_model` fallback 到 `primary_model`**

L1119: `secondary_model = body.secondary_model.strip() or primary_model`

如果 controller 只填了 primary_model 不填 secondary_model，两个 lane 会用同一个 model。这时 panel 的意义会退化为"同一 model 两次调用的一致性检查"（温度随机性导致的差异）。

这不是 bug——response 中的 `secondary_model` 字段会诚实地显示实际使用的 model name，controller 可以自行判断。但 docs 中没有说明这个 fallback 行为。

**6. [正面] 测试设计精准验证了核心声明**

测试中 primary 和 secondary 对 repo 一致 (`follow`)，对 issue 不一致 (`review` vs `ignore`)。验证了：
- `agreement_count == 1` ✅
- `disagreement_count == 1` ✅
- `panel_signal == "mixed"` ✅
- `disagreed_object_keys` 包含 issue ✅
- truth_boundary 包含 "panel inspect exposes agreement shape" ✅
- 两个 lane 的 parse_status 都被记录 ✅

**7. [正面] Truth boundary 精准扩展**

在 M7 的 3 条 truth boundary 基础上添加了第 4 条："panel inspect exposes agreement shape, not a merged canonical verdict"。这直接回应了最容易产生的误解：panel 不等于投票。

---

### Validation Gaps

**1. [低] 缺少一个 "全部一致" 的 test case**

当前只测试了 mixed 场景。没有测试 primary/secondary 完全一致时 `panel_signal == "stable"` 的情况。逻辑非常直白（`"stable" if not disagreed else "mixed"`），但一个显式的 stable case 测试会使证据更完整。

**2. [低] 缺少一个 "一方 parse 失败" 的 test case**

如果 secondary model 返回非法 JSON，`_parse_ai_candidate_judgment_payload` 会 fallback 到空 judgments。此时 `_compare_ai_candidate_judgments` 会计算出 `shared_candidates == 0, primary_only_count == N`。这个降级行为是安全的，但没有显式测试。

---

### Recommendation

**`accept`**

**理由：**

- M7 review 中提出的两个核心 changes 都已吸收（JSON parse safety + auditability）
- M7 → M8 的重构路径干净，提取了共享 kernel 而非 copy-paste
- Agreement comparison 严格遵守 non-merging 边界，只暴露 shape
- 完整审计链：两个 lane 的 provider/model/parse_status/discarded_count 全部记录
- Truth boundary 精准扩展
- 71 个测试全部通过，无回归
- 没有 DB 写入，没有 truth mutation

**注意项（非 blocker）：**

- 两个 model lane 是串行的，未来有延迟压力时可改为并行
- secondary_model fallback 到 primary_model 的行为应在使用文档中说明
- 补 stable + parse-failure edge case 测试会使证据链更完整
- 这是 AI judgment 系列的一个好的停止点——M7 (single) + M8 (panel) 已覆盖了 inspect-only AI 参与的基础形状，下一步应该是 review/absorption 而非继续扩展 inspect surface

# gemini
**IKE Sentinel (治理代理) 审查模式已激活。**

> **当前审查目标声明 (Review Target Statement)**
> **正在审查的文档/包：** `IKE_SOURCE_INTELLIGENCE_V1_M8_PANEL_INSPECT_RESULT_2026-04-15`
> **涉及核心代码：** `routers/feeds.py`, `tests/test_feeds_source_discovery_route.py`
> **审查范围：** M8 阶段（AI Judgment Panel Inspect）边界断言与代码物理验证。

基于你提供的 M8 代码实现与测试证据，以下是针对本次结案请求的深度审查报告：

### 1. 核心发现 (Findings)

* **双轨隔离的物理实现 (Isolation Realism):** 你在 `feeds.py` 中新增了 `inspect_source_candidate_judgment_panel` 路由 (`POST /sources/discover/judge/panel/inspect`)。代码物理证明了这是一个真正的“并行面板”：你提取出了公共的 `_run_ai_candidate_judgment_once` 函数，并在主路由中分别使用 `primary_provider`/`primary_model` 和 `secondary_provider`/`secondary_model` 独立调用了两次。两个模型之间没有上下文污染（它们各自收到一份独立的、相同的候选列表 JSON）。
* **诚实的协议形状 (Honest Contract Shape):** 返回的数据结构极其克制。你没有试图通过某种硬编码权重将两者的意见合并为一个伪造的“最终真理（merged canonical verdict）”。相反，你通过 `_compare_ai_candidate_judgments` 诚实地暴露了分歧点：`agreed_object_keys` vs `disagreed_object_keys`，并将其抽象为 `panel_signal: "stable" | "mixed"`。
* **非侵入性与边界遵守 (Non-Invasiveness):** 像 M7 一样，这个路由依然没有任何对数据库的 `db.add()` 或 `db.commit()` 操作。它完美遵守了“inspect-only”和“non-persistent”的红线。

### 2. 验证缺口与遗留问题 (Validation Gaps / Open Questions)

这个切片非常干净，但有一些工程细节可以在后续阶段（或如果代码被外部频繁调用时）优化：

* **并发调用的缺失 (Lack of Concurrency):** 在 `_run_ai_candidate_judgment_panel_inspect` 中，你使用了串行等待：
    ```python
    primary_judgments, ... = await _run_ai_candidate_judgment_once(...)
    secondary_judgments, ... = await _run_ai_candidate_judgment_once(...)
    ```
    既然两者的输入互不依赖，这应该通过 `asyncio.gather` 并行执行，以避免路由响应时间翻倍（大模型的延迟很高）。考虑到这是 `inspect` 接口（通常面向操作员），目前的串行是可以接受的，但在自动化流中这会是个瓶颈。
* **JSON 容错逻辑的分离 (Refactoring Artifact):** 我看到你提取了 `_parse_ai_candidate_judgment_payload`。这是一个很好的改进（解决了 M7 中指出的脆弱性）。现在它能够处理带有 markdown 包装的、或者完全失效的 JSON，并返回 `valid_json` 或 `invalid_json_fallback`。

### 3. 最终判定 (Recommendation)

本次 M8 切片是一个极其克制的 AI 治理实验。它没有陷入“用一个 AI 管理另一个 AI”的复杂黑盒陷阱，而是建立了一个透明的法庭，仅仅告诉你：“这两位专家在这个问题上是否有分歧”。

**Recommendation: `accept`**

**哨兵结语:** 你成功地将不确定性（Uncertainty）转化为了可度量的信号（`panel_signal`），且没有污染底层的数据库真相。同意合并 M8。下一步可以考虑基于这个 `panel_signal` 决定是否将某些 `agreed` 的候选吸收进真实的 Source Plan。

# chatgpt
你说得对，上一轮不该在没把 zip 读完前就下结论。
这次我是**先把 zip 里的全部文件都读了**，再给 review。

## Review 对象

本轮实际 review 的材料是：

* **Zip 包**：`IKE_SOURCE_INTELLIGENCE_V1_M8_PANEL_INSPECT_RESULT_2026-04-15.zip`
* **主结果文档**：`IKE_SOURCE_INTELLIGENCE_V1_M8_PANEL_INSPECT_RESULT_2026-04-15.md`
* **阶段判断文档**：`IKE_SOURCE_INTELLIGENCE_V1_M8_PHASE_JUDGMENT_2026-04-15.md`
* **计划文档**：`IKE_SOURCE_INTELLIGENCE_V1_M8_PLAN_2026-04-15.md`
* **review 请求文档**：`review-for IKE_SOURCE_INTELLIGENCE_V1_M8_PANEL_INSPECT_RESULT_2026-04-15.md`
* **实现文件**：`services/api/routers/feeds.py`
* **测试文件**：`services/api/tests/test_feeds_source_discovery_route.py`

---

## findings

### 1. 这一步整体成立，方向也对，我给 `accept_with_changes`

M8 做成的是一条很窄的 panel inspect lane：

* 复用现有 discovery path
* 复用同一个 bounded candidate subset
* 跑两条 model lane
* 暴露 agreement/disagreement shape
* 不 merge
* 不 persist
* 不改 source-plan truth

这个边界在文档、实现、route docstring、response shape 上基本是一致的。
所以从主线上看，这一步是成立的，而且比直接跳 persistence、voting、workflow 健康得多。

### 2. inspect-only / non-canonical 边界守住了

这个 packet 最重要的事，是没有偷偷长成 merged decision surface。现在代码里是：

* `primary_judgments`
* `secondary_judgments`
* `primary_summary`
* `secondary_summary`
* `panel_summary`
* `truth_boundary`

没有 `merged_judgment`、没有 `winning_model`、没有 canonical verdict。
`truth_boundary` 还额外补了一句：

> panel inspect exposes agreement shape, not a merged canonical verdict

这句是对的，而且是这轮能通过的核心前提。

### 3. “two independent model lanes” 这个说法要收紧一点

文档里多次写 “two independent model lanes”。
从实现看，实际成立的是：

* 同一个 `LLMAdapter()` 实例
* 调两次 `_run_ai_candidate_judgment_once(...)`
* 用不同 provider/model 参数

所以它证明的是：

> **two separate judgment calls on the same candidate subset**

这没问题。
但“independent”这个词如果说重了，会让人以为已经证明了更强的 epistemic independence，实际上没有。因为：

* secondary model 默认可以回退成 primary model
* 也没有 provider-level isolation / failure isolation / calibration proof
* 更没有 panel diversity proof

所以这一步最准确的表述，不是“independent panel intelligence”，而是：

> **one bounded dual-lane inspect surface**

### 4. agreement/disagreement shape 是诚实的，但它现在只比较 verdict，不比较 confidence / rationale / priority

`_compare_ai_candidate_judgments(...)` 现在只做了：

* shared candidates
* agreement_count
* disagreement_count
* primary_only_count
* secondary_only_count
* agreed_object_keys
* disagreed_object_keys
* panel_signal = stable/mixed

它比较的是 **verdict**，不是：

* confidence 一致性
* rationale 差异
* review_priority 差异

所以当前 `panel_summary` 的语义应该被理解为：

> **verdict overlap shape**

不是更广义的 panel agreement。
这一点不算 bug，但我认为文档和命名最好更明确一点，否则很容易被人读成“两个模型整体上意见一致/不一致”。

### 5. M7 的透明度改进延续到了 M8，这点是加分项

这轮比我之前担心的好一点，因为 M7 里最该补的透明度信息，这里其实已经带进来了：

* `primary_parse_status`
* `secondary_parse_status`
* `primary_discarded_judgments`
* `secondary_discarded_judgments`
* `judged_candidates`
* `panel_agreement_count`
* `panel_disagreement_count`

这说明 M8 没有只暴露“看起来漂亮的 panel 结果”，而是把 normalization / parse honesty 也继续带着。这个是好的。

### 6. 这一步最大的剩余风险不在 truth mutation，而在“panel usefulness 被过早高估”

当前实现确实没有 merge truth，也没有写回 plan。
真正的风险是解释层：

* 有两个模型
* 有 agreement/disagreement
* 有 panel_signal

很容易让人自然地往下一步联想：

* disagreement 就该触发 review queue
* agreement 就更可信
* stable 就可以更放心 follow

但当前 packet **没有证明这些**。
它只证明：

> 现在可以看见 panel shape

没有证明：

* panel shape 足以指导 controller action
* agreement 比单模型更可靠
* disagreement 真能标示 uncertainty

这一点必须继续压住。

### 7. 这一步是一个好停点，但不该顺着它继续长成 voting / workflow

阶段文档和结果文档这点判断是对的：
下一步不应该默认扩成 workflow 或 automation。

我会把这个 stop rule 说得更硬一点：

> **M8 的价值在于打开 panel inspect，不在于给 panel governance 找自然延伸。**

如果下一步顺势做：

* vote
* majority
* tie-break
* disagreement escalation
* auto-route
* persistence

那这条线就会从 inspect slice 变成 controller workflow seed。

---

## validation gaps

### 1. 缺 panel invalid-json / malformed-response 的 focused test

M7 单模型 route 已经有 invalid JSON fallback test。
但这轮 panel route 我只看到正向 mixed-case proof，没有看到：

* primary invalid / secondary valid
* primary valid / secondary invalid
* two lanes both invalid

这类测试很重要，因为 M8 的核心不是单次 judgment，而是**双 lane 并列的 honesty**。

### 2. 缺 “primary_only / secondary_only” 的 focused proof

实现里有：

* `primary_only_count`
* `secondary_only_count`

但当前 route test 用的是两个 lane 都判断了同样两个 candidates。
所以实际并没有证明：

* primary judgment subset 更窄时 response shape 是否正常
* secondary judgment subset 更窄时 response shape 是否正常

这条缺口不大，但从 panel semantics 来说是自然该补的。

### 3. panel_summary 命名略宽，建议强调它是 verdict-level comparison

现在 `panel_summary` 这个名字容易让人读成整体 panel assessment。
更诚实一点的表达，应该接近：

* `panel_verdict_overlap`
* 或至少在文档里明确：只基于 verdict 比较，不代表整体 model agreement

### 4. secondary model fallback 语义需要更清楚

当前代码里：

* `secondary_model = body.secondary_model.strip() or primary_model`

这意味着如果 secondary_model 不填，两个 lane 可能使用同一个 model name。
文档如果还写成“dual-model panel”，就有一点偏大。
更准确的说法应该是：

> dual-lane panel inspect

而不是无条件 dual-model。

---

## recommendation

**accept_with_changes**

### 为什么可以 accept

因为这轮最核心的 claim 已经成立：

* 新 route 确实存在
* 两条 lane 确实都跑了
* agreement/disagreement shape 确实被显式暴露
* 没有 merged truth
* 没有 persistence
* 没有 auto-routing

这已经足够构成一个有效的 bounded slice。

### 为什么必须 with_changes

因为还有三类边界要补强：

1. **收紧文案**
   把 “independent model lanes / dual-model panel” 收紧成更贴实现的：

   * dual-lane
   * bounded panel inspect
   * verdict-overlap shape

2. **补 panel failure-path tests**
   最优先是：

   * one lane invalid JSON
   * both lanes invalid JSON
   * one lane empty judgments

3. **防止 usefulness 被过早上纲**
   在结果文档里继续明确：

   * panel agreement ≠ stronger truth
   * panel disagreement ≠ automatic escalation rule
   * panel inspect ≠ controller workflow

---

一句话结论：

**这一步是成立的，而且是一个健康的 M7 上探；但它证明的是“现在可以并列看两个 AI judgment lane 的 verdict shape”，不是“panel judgment 已经足够可靠或足以驱动后续治理动作”。**
