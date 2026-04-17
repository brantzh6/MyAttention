# claude

Now let me read the actual code — the new route and normalization logic, plus the tests.
Now let me read the prompt builder and normalization function.
Let me also check the request/response models.
I now have the full picture. Let me also quickly check `_candidate_to_judgment_payload`.
All code reviewed. Here's the review:

---

## Review: IKE_SOURCE_INTELLIGENCE_V1_M7_AI_JUDGMENT_INSPECT_RESULT_2026-04-14

---

### Findings

**1. [正面] Inspect-only 边界严格遵守，无 truth mutation**

整个流程链：
1. `_run_source_discovery` → 复用已有 discovery 路径 ✅
2. `candidates[:max_candidates]` → 有界截断 ✅
3. `LLMAdapter.chat` → 发送 prompt，获取 JSON ✅
4. `_normalize_ai_candidate_judgments` → 只接受已知 candidate 的 judgment ✅
5. 返回 `SourceDiscoveryJudgeInspectResponse` → 无 DB 写入、无 source plan 变更 ✅

路由函数签名中虽然注入了 `db: AsyncSession`，但它只用于传递给 `_run_source_discovery`（discovery 本身需要读 attention policy），judge inspect 路径本身无任何 DB 写入操作。

**2. [正面] Normalization 是这个 packet 的核心价值，且实现正确**

`_normalize_ai_candidate_judgments` (L914-950) 做了三层过滤：
- **object_key 白名单**：只接受 `allowed_keys` 中的 candidate，out-of-scope key 直接丢弃 ✅
- **verdict 白名单**：只接受 `follow/review/ignore`，非法 verdict 丢弃 ✅
- **priority 归一化**：非法 priority 降级为 `normal` 而非丢弃 ✅
- **confidence 钳位**：`max(0.0, min(1.0, confidence))` ✅

测试中显式验证了这一点：model 返回了 3 个 judgment（其中第 3 个 `github.com/out-of-scope/repo` 不在候选列表中），normalization 后只剩 2 个。这是正确的防御性设计。

**3. [中] `json.loads(raw)` 没有 error handling**

L982: `payload = json.loads(raw)` — 如果 model 返回非法 JSON（这在实际使用中很常见，特别是 model 可能在 JSON 前后添加 markdown fence 或解释文本），这行会抛出 `json.JSONDecodeError`，导致 500 错误。

当前 system_prompt 是 `"Return valid JSON only."`，这在大部分情况下有效，但不保证 100%。

**建议**：至少加一个 try/except 包裹 `json.loads`，在 parse 失败时返回空 judgments + error note，而非 500。这是一个 `accept_with_changes` 级别的项，但不阻碍 packet 的核心声明。

**4. [中] Prompt 语言是中文——可能影响非中文 model 的表现**

Prompt (L886-910) 使用中文指令。对 qwen 系列 model 没有问题。但如果 controller 切换 provider 到非中文 model（request body 支持任意 provider/model），prompt 效果可能下降。

当前 scope 是 bounded inspect，provider 默认是 qwen，model 默认是 `get_settings().qwen_model`——对当前 packet 来说是合理的。但值得注意。

**5. [低] `max_candidates` 的截断在 discovery 之后而非之前**

L967: `judged_candidates = discovery.candidates[: body.max_candidates]`

这意味着即使只判断 6 个候选，系统仍然会对完整的 `body.limit`（最多 30）个候选执行完整的 discovery 流程（搜索 + 分类 + scoring + compression）。这是性能上的浪费，但对正确性没有影响，且确保了 judgment 看到的候选是经过完整 scoring 后的 top-N。

**6. [正面] Response 包含完整审计链**

`SourceDiscoveryJudgeInspectResponse` 返回：
- 原始 discovery 结果
- 被判断的候选子集
- normalized judgments
- provider + model 信息
- notes（provider、model、judged count、normalized count）
- truth_boundary

controller 可以完整审计：discovery 返回了什么 → 哪些被送去判断 → model 说了什么 → normalization 保留了什么。

**7. [正面] Truth boundary 声明精准**

三条 boundary 直接覆盖了最容易产生误解的边界：
- "advisory, not canonical source truth"
- "does not auto-subscribe, auto-promote, or write source plans"
- "model verdicts must remain reviewable and may be wrong or incomplete"

---

### Validation Gaps

**1. [中] 缺少 model 返回非法 JSON 的 test case**

当前只有一个 happy-path 测试。没有测试：
- model 返回空字符串
- model 返回 ````json\n{...}\n```` 带 markdown fence
- model 返回不包含 `judgments` key 的 JSON

这些是 LLM 实际使用中的常见 failure mode。结合 finding #3（无 error handling），这是当前 packet 的主要薄弱点。

**2. [低] 缺少 verdict 全为 `ignore` 的 edge case 测试**

如果 model 判断所有候选都是 ignore，response 仍然是 valid 的（judgments 列表全是 ignore verdict）。这个行为是正确的，但没有显式测试。

---

### Recommendation

**`accept_with_changes`**

**理由：**

这是 Source Intelligence V1 的一个**重要转折点**——从纯启发式规则（M1-M6）到 AI 参与判断。核心设计选择正确：
- inspect-only，无 truth mutation ✅
- normalization 防御性强，only accept known candidates ✅
- 完整审计链 ✅
- truth boundary 精准 ✅

**需要的 changes：**

1. **`json.loads` error handling**：wrap in try/except，parse 失败时返回空 judgments + error note，不 500。这是唯一的 production-readiness 要求。

**可选但建议的 changes（非 blocker）：**

2. 补一个 model 返回非法 JSON 的测试 case
3. 考虑在 `json.loads` 之前做简单的 markdown fence stripping（`raw.strip("` \n")`）

# gemini
**IKE Sentinel (治理代理) 审查模式已激活。**

> **当前审查目标声明 (Review Target Statement)**
> **正在审查的文档/包：** `IKE_SOURCE_INTELLIGENCE_V1_M7_AI_JUDGMENT_INSPECT_RESULT_2026-04-14`
> **涉及核心代码：** `routers/feeds.py`, `tests/test_feeds_source_discovery_route.py`
> **审查范围：** M7 阶段（AI-Assisted Candidate Judgment Inspect）边界断言与代码物理验证。

基于你提供的 M7 代码实现与测试证据，以下是针对本次结案请求的深度审查报告：

### 1. 核心发现 (Findings)

* **物理实现与计划高度一致 (Truthfulness):** 你在 `feeds.py` 中新增了 `inspect_source_candidate_judgment` 路由（`POST /sources/discover/judge/inspect`）以及相关的内部处理函数（如 `_build_ai_candidate_judgment_prompt` 和 `_normalize_ai_candidate_judgments`）。这个路由确实是构建在现有的 `_run_source_discovery` 之上，成功提取了前 `max_candidates` 个候选，然后将其传递给 `LLMAdapter`。
* **出色的输入/输出沙箱 (Boundary Enforcement):**
    * **输入隔离:** 传递给大模型的 Prompt 经过了 `_candidate_to_judgment_payload` 的清洗，去除了多余的内部状态（如 `gate_status` 等），只保留了对判断有价值的元数据、角色推断、以及少量的标题/摘要样本。这防止了模型被内部字段迷惑。
    * **输出正规化 (Normalization):** 你的 `_normalize_ai_candidate_judgments` 函数是一个坚固的防线。它使用已知候选的 `object_key` 作为白名单：`allowed_keys = {candidate.object_key: candidate for candidate in candidates}`。如果模型产生了幻觉，输出了不在列表中的 `object_key`（或者编造了新的源），这个函数会直接将其丢弃。同时，它也严格校验了 `verdict` 和 `review_priority` 的枚举值。
* **非破坏性 (Non-mutating):** 这个新路由完全没有触碰数据库写入路径 (`db.commit()`)，也没有修改任何 `SourcePlan` 或 `Source`。它就是一个纯粹的、无副作用的“建议引擎（advisory engine）”。

### 2. 验证缺口与遗留问题 (Validation Gaps / Open Questions)

这些点不影响 M7 阶段的合并，但需要在后续阶段引起注意：

* **JSON 健壮性盲点 (JSON Fragility):** 在 `_run_ai_candidate_judgment_inspect` 中，你直接使用了 `payload = json.loads(raw)`。虽然你在系统提示中要求了 `"Return valid JSON only."`，但大模型（尤其是较小的模型）经常会在 JSON 外面包裹 Markdown 代码块（如 ````json ... ````），或者输出带 trailing commas 的非标准 JSON。如果 `LLMAdapter` 内部没有处理这种清理，那么这个路由极容易因为 `json.decoder.JSONDecodeError` 而崩溃抛出 500 错误。
* **Prompt 上下文窗口限制:** 你将多个 candidate 的 `sample_titles` 和 `sample_snippets` 直接压入 JSON 并放入 Prompt。如果 `max_candidates` 设置得较大（如 12），这个 JSON 字符串可能会非常长，可能超出某些快速模型的最佳注意力窗口。

### 3. 最终判定 (Recommendation)

本次 M7 阶段非常成功。这是 Source Intelligence 第一次在“收集数据”之上引入了“机器思考”，但你克制地将这只“野兽”关在了一个 inspect-only 的只读笼子里。归一化（Normalization）逻辑写得尤其漂亮。

**Recommendation: `accept_with_changes` (通过，建议微调)**

**建议修改 (The "Changes" in "Accept with Changes"):**
虽然核心逻辑完美，但我强烈建议在合并前，或者在 M8 的第一个提交中，为 `json.loads(raw)` 加上一层容错处理。例如：
```python
# 简单的清洗示例
clean_raw = raw.strip()
if clean_raw.startswith("```json"):
    clean_raw = clean_raw[7:]
if clean_raw.endswith("```"):
    clean_raw = clean_raw[:-3]
try:
    payload = json.loads(clean_raw)
except json.JSONDecodeError:
    # 至少记录错误或返回一个安全的降级响应，而不是让 API 崩溃
    payload = {"summary": "Model failed to return valid JSON", "judgments": []}
```

**哨兵结语:** M7 为 AI 参与决策铺平了道路。同意在解决 JSON 解析健壮性后，将此功能闭环。你可以准备着手下一步（如你计划中的将 inspect 结果有条件地吸收为 source-plan 更新）。

# chatgpt
**Review 对象**

这次我实际 review 的材料是这一个包里的以下文件，不是相邻的别的 M 文档：

* **Zip 包**：`IKE_SOURCE_INTELLIGENCE_V1_M7_AI_JUDGMENT_INSPECT_RESULT_2026-04-14.zip`
* **主结果文档**：`IKE_SOURCE_INTELLIGENCE_V1_M7_AI_JUDGMENT_INSPECT_RESULT_2026-04-14.md`
* **阶段判断文档**：`IKE_SOURCE_INTELLIGENCE_V1_M7_PHASE_JUDGMENT_2026-04-14.md`
* **计划文档**：`IKE_SOURCE_INTELLIGENCE_V1_M7_PLAN_2026-04-14.md`
* **review 请求文档**：`review-for IKE_SOURCE_INTELLIGENCE_V1_M7_AI_JUDGMENT_INSPECT_RESULT_2026-04-14.md`
* **实现文件**：`services/api/routers/feeds.py`
* **测试文件**：`services/api/tests/test_feeds_source_discovery_route.py`

---

## findings

### 1. 这一步方向是对的，而且是 Source Intelligence 从“纯 heuristic cleanup”重新回到 AI participation 的第一个合理切点

这轮不是 persistence，也不是 auto-promotion，而是在现有 discovery surface 之上加了一条很窄的 AI inspect lane：

* 复用 `/sources/discover`
* 只看 bounded candidate subset
* 只返回 advisory verdict
* 不写 truth

这个切点选得是对的。
它比继续补 M3/M4/M5/M6 那种 heuristic patch 更接近长期目标，但又没有一下跳到 orchestration、paneling、methodology program generation 这些更宽的东西。

### 2. inspect-only / advisory 边界目前基本守住了

从实现和 route 文档看，这条 `/api/sources/discover/judge/inspect` 现在是干净的：

* route docstring 明确写了不 persist judgments、不 auto-promote
* response 里单独返回 `truth_boundary`
* judgment 结果没有写回 discovery candidates
* 也没有 source plan mutation

这一点我认可。
至少从当前 packet 来看，它没有偷偷长成“AI 代替 controller 做选择”的 lane。

### 3. normalization 总体是诚实的，但还差一层“对模型越界行为的显式可见性”

当前 `_normalize_ai_candidate_judgments(...)` 做得对的地方有：

* 只接受已知 `object_key`
* 只接受 `follow/review/ignore`
* review_priority 只接受 `high/normal/low`
* confidence 被 clamp 到 `0.0 ~ 1.0`
* out-of-scope object_key 会被丢掉

这是健康的。
而且测试里也专门构造了一个越界 object_key，最后没有进入结果，说明这条 normalization 不是纸面声明。

但这里有一个小缺口：
**系统现在会丢弃越界 judgment，却不会把“丢弃了几个”“为什么丢弃”显式反馈出来。**
目前 notes 只有：

* provider
* model
* judged_candidates
* normalized_judgments

所以这条 lane 虽然已经是“honest enough”，但还不是“fully inspect-honest”。因为 controller 只能看见最终保留了什么，看不见模型实际还尝试判断了什么。

### 4. 当前最容易被高估的，不是 route，而是 `summary`

`judgments` 是被严格 normalize 过的，但 `summary` 只是简单地从 model payload 里取字符串。
这意味着一个潜在问题：

* judgments 已经被限制在 known candidates
* 但 summary 仍可能带出超出 judged subset 的结论、倾向或措辞

也就是说，**结构化 judgment 是有边界的，summary 其实没有同样强的边界。**
这不至于让这轮 reject，但它是当前 packet 里最值得提醒的一点。
如果后续有人开始把 `summary` 当成更强的 judgment condensation，这条 lane 就会变得不那么诚实。

### 5. 这一步引入了真实 AI participation，但还不是“可靠 AI judgment”

我同意主结果文档里的总体判断：这是 first inspect-only AI participation lane。
但我会把它再收紧一点：

它现在证明的是：

* **AI 已经参与了 candidate judgment**
* 而不是
* **AI judgment 已经具备可依赖的 sufficiency**

这是两个完全不同的层级。
当前 prompt 仍然是单模型、单轮、固定 JSON schema、无 uncertainty shaping、无 paneling、无 calibration。
所以这一步的价值在于“AI 参与面已打开”，不在于“AI judgment 已经成熟”。

### 6. validation 对这个 bounded slice 来说基本够用，但还缺两类最关键的失败路径

当前 route test 已经证明了：

* route 能通
* judged subset 是 bounded 的
* known candidates 能回写
* out-of-scope object_key 被丢弃
* truth boundary 带 advisory

这对当前 slice 是够的。
但如果只看“是否已足够稳”，还缺两类最关键的失败路径：

**第一类：模型返回 malformed JSON**
现在代码里是直接 `json.loads(raw)`。如果模型返回非 JSON，这条 route 很可能直接抛异常。
这不一定现在就要做 graceful fallback，但至少这是一个真实缺口。

**第二类：模型返回合法 JSON，但字段类型错乱**
现在部分错乱会被 normalize 吞掉，但没有 focused test 去证明：

* judgment list 里混入非 dict
* confidence 是字符串垃圾值
* review_priority 非法
  这些虽然代码已经做了处理，但测试没把这些保护钉死。

### 7. 这一步是个好停点，但不能顺着它直接走向 persistence 或 workflow

主结果文档最后这个判断我基本同意：
下一步不该直接扩成 persistence 或 orchestration。
我甚至会说得更硬一点：

**M7 的正确价值是“打开 inspect-only AI judgment lane”，不是“给 AI decision lane 找下一步自然扩张路径”。**

如果下一步马上变成：

* 写入 source plan
* auto-follow
* controller suggestion queue
* generic source triage workflow

那这条 lane 会迅速越界。

---

## validation gaps

### 1. 缺 malformed JSON 路径测试

当前 `json.loads(raw)` 没有显式保护。
最少应知道：现在这是“允许 500”的受限 inspect lane，还是你们想让它变成“bad model output 也能稳定返回 bounded error”。

### 2. 缺 summary honesty 的边界说明

现在 `summary` 没被 normalization 到和 judgments 同样强的边界。
建议至少在 truth boundary 或 notes 里明确：

* `summary` 是 advisory model summary
* 不应被当成 canonical candidate decision set

### 3. 缺“discarded judgments count”或同类透明度信息

既然这轮 review scope 里专门强调 normalization honesty，那 notes 里没有 `discarded_judgments` / `unknown_object_keys_ignored` 一类信息，会让 inspect 透明度差半步。

### 4. 缺 provider/model failure path 的最小 contract

现在 route 接了 provider 和 model，但没有这轮 packet 内的 focused proof 来说明：

* provider/model 不可用时会怎样
* response 是否仍保持 inspect-only semantics
  这不一定是当前必须补的，但从“AI lane”角度，这是很自然的下一层缺口。

---

## recommendation

**accept_with_changes**

### 为什么不是 reject

因为这轮的核心主张是成立的：

* 新 route 确实存在
* AI 确实参与了 judgment
* normalization 确实把结果压回 known candidates
* truth mutation 确实没发生

这已经足够让它成为一个有效的 bounded slice。

### 为什么也不是纯 accept

因为现在还有三个边界需要补强：

1. **把 `summary` 的语义再收紧**
   明确它是 advisory summary，不是 canonical compressed decision。

2. **补最关键的失败路径 proof**
   最优先是 malformed JSON。

3. **提高 normalization 透明度**
   至少让 controller 能看见：模型有多少 judgment 被丢弃。

---

一句话结论：

**这一步是成立的，而且是 Source Intelligence 重新引入 AI participation 的一个正确切点；但它当前证明的是“AI 已经参与 inspect judgment”，不是“AI judgment 已经可依赖”，所以建议通过，但要补失败路径与透明度边界。**
