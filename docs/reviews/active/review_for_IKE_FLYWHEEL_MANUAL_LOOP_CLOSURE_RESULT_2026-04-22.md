# Review For IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_RESULT_2026-04-22

Canonical review target:

- [D:\code\MyAttention\docs\IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_RESULT_2026-04-22.md](/D:/code/MyAttention/docs/IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_RESULT_2026-04-22.md)

Review pack:

- [D:\code\MyAttention\.runtime\review-packs\IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_RESULT_2026-04-22.zip](/D:/code/MyAttention/.runtime/review-packs/IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_RESULT_2026-04-22.zip)
- [D:\code\MyAttention\.runtime\review-packs\IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_RESULT_2026-04-22_FILE_LIST.md](/D:/code/MyAttention/.runtime/review-packs/IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_RESULT_2026-04-22_FILE_LIST.md)

GitHub version:

- [commit bc2e303 baseline branch](https://github.com/brantzh6/MyAttention/tree/codex/pre-ike-restructure-2026-04-09)

## Review Request

Please review the manual AI-assisted flywheel loop closure result.

Focus:

1. Whether this is enough to count as a manual information -> knowledge -> evolution -> worker -> feedback loop milestone.
2. Whether the result avoids overclaiming runtime automation, verified provenance, persistence, or canonical absorption.
3. Whether the next implementation step should be decomposition rather than more bridge fields.
4. Whether any blocker exists before accepting this as the short-term flywheel closure point.

Non-goals:

1. Do not require automatic scheduling.
2. Do not require verified provenance yet.
3. Do not require persistence.
4. Do not require more UI fields.

Expected format:

```text
recommendation: accept | accept_with_changes | reject

findings:
- ...

validation_gaps:
- ...

next_suggestions:
- ...
```

## Internal Run Notes

- Qwen `qwen3.6-plus` performed flywheel inspect.
- `claude-worker / qwen-bailian-coding / glm-5` performed read-only delegated worker execution.
- Qwen `qwen3.6-plus` performed execution-feedback inspect.
- Worker run: `20260421T164215-398e1412`.
- Runtime artifacts are in `.runtime\flywheel-loop-demo-2026-04-22\` and are summarized in the result doc.

## External Review Results

Write reviewer results below this line.

# claude
Reading the review request document first.
Now reading the result document and the file list.
Reading the scenario doc and the new extracted provenance component, plus the updated core files.
Now checking the tests and the panel for the provenance reset and integration with the extracted component.
Let me check the provenance reset context and how the extracted components are used in the panel.
Now let me check where the extracted component is used in the panel's render (replacing inline provenance UI).
Let me also quickly check the runtime artifacts referenced in the result doc to confirm they exist.
Let me sample one runtime artifact to verify it's a real AI result, not a placeholder.
I now have complete context. Here is my structured review.

---

## Review: IKE Flywheel Manual Loop Closure (2026-04-22)

### Nature of This Slice

This is **not a code-change slice**. It is a **milestone result document** with one supporting decomposition step and one real end-to-end scenario run. Specifically:

1. **Result doc** — documents a 4-step manual loop execution with real AI calls and a real delegated worker run
2. **Scenario doc** — fixes the accepted loop shape and non-claims
3. **One decomposition step** — provenance input/display extracted from `flywheel-inspect-panel.tsx` into `execution-feedback-provenance.tsx` (124 lines)
4. **Provenance reset fix** — panel clears provenance fields on new flywheel inspect run
5. **Runtime artifacts** — 3 real JSON snapshots in `.runtime/flywheel-loop-demo-2026-04-22/`

Backend contracts, flywheel logic, router, and tests are **unchanged from the provenance slice**.

---

### Focus 1: Does this count as a manual information → knowledge → evolution → worker → feedback loop milestone?

**Yes.**

The loop executed was:

| Step | Tool | Real AI? | Output |
|------|------|----------|--------|
| 1. Flywheel Inspect | `POST /flywheel/inspect` | Qwen `qwen3.6-plus` | `flywheel_signal`, 2 knowledge + 2 evolution labels |
| 2. Task Packet Preview | `POST /flywheel/task-packet/preview` | No (deterministic) | `mixed` intent, `prioritize_and_sequence` |
| 3. Delegated Worker | `claude-worker / glm-5` | Yes | Read-only analysis, 3 validation gaps noted |
| 4. Execution Feedback | `POST /execution-feedback/inspect` | Qwen `qwen3.6-plus` | `execution_feedback` intent, 2 knowledge + 2 evolution candidates echoed back |

The runtime artifact `03_execution_feedback_inspect.json` confirms:
- `feedback_intent: "execution_feedback"` (real extraction, not no-action fallback)
- 2 knowledge candidates + 2 evolution candidates with correct lifecycle metadata (`proposal_state: "proposed"`, `review_gate: "controller_review_required"`, `absorption_state: "not_absorbed"`)
- Provenance echo with `provenance_source: "caller_provided"`, `verified: false`
- `promotion_state: "inspect_only"` throughout
- 12 truth boundary statements enforced

This is a **genuine loop closure** — information entered at step 1 flowed through all 4 steps and returned as structured knowledge/evolution candidates with provenance context.

---

### Focus 2: Does the result avoid overclaiming?

**Yes. The doc is disciplined about non-claims.**

| What is claimed | What is explicitly not claimed |
|----------------|-------------------------------|
| Manual loop runs end-to-end | Runtime scheduler or persistence |
| AI calls produce structured candidates | Verified provenance |
| Provenance is annotation | Automatic absorption |
| Worker executed one bounded task | Automatic task scheduling |
| Labels echo through the loop | Canonical promotion |

The scenario doc (L68–77) has an explicit **Non-Claims** section listing 6 items the scenario does NOT prove. The result doc (L20) states: *"It does not prove verified provenance, automatic absorption, or runtimeized execution."*

The self-recommendation is `accept_with_changes` rather than `accept` — the doc correctly recognizes this is proof, not completion.

---

### Focus 3: Should the next step be decomposition rather than more bridge fields?

**Yes. The evidence supports this.**

1. **Panel went from 1601 → 1537 lines** — net -64 lines from extracting `execution-feedback-provenance.tsx` (124 lines). This is the **first decomposition** in the flywheel panel's history.

2. **`flywheel.py` is still 779 lines** — unchanged, still contains 3 functional groups (flywheel inspect, task-packet preview, execution feedback). Ripe for split into 3 files.

3. **The scenario doc explicitly states** (L81–86): the next meaningful review point should be either an end-to-end scenario OR a bounded decomposition. "Do not open review for every small cleanup."

4. **The result doc's known risks** (L153) explicitly lists: *"`flywheel.py` and `flywheel-inspect-panel.tsx` still need larger decomposition."*

The evidence chain is clear: the loop works manually, more bridge fields would increase monolith pressure, decomposition is the correct next priority.

---

### Focus 4: Any acceptance blocker?

**No blocker found.**

| Potential concern | Verdict |
|-------------------|---------|
| Backend changed? | No — contracts.py, flywheel.py, router, tests are identical to post-provenance state |
| Tests pass? | 36 tests OK (21 flywheel + 15 conversation runtime) |
| Frontend build? | success |
| Decomposition safe? | Yes — `ExecutionFeedbackProvenanceInputs` and `ExecutionFeedbackProvenanceDisplay` are pure presentational. No state, no side effects. |
| Provenance reset correct? | Yes — L401–404 clear all 4 provenance state vars when a new flywheel inspect starts. Prevents stale run identity leaking. |
| Runtime artifacts exist? | Yes — 3 JSON files verified: `01_flywheel_inspect.json` (4.6KB), `02_task_packet_preview.json` (1.9KB), `03_execution_feedback_inspect.json` (4.8KB) |
| Artifacts are real? | Yes — `03_execution_feedback_inspect.json` contains real AI output with structured candidates, not stub data |

---

### Decomposition Quality Check

The extracted component `execution-feedback-provenance.tsx` (124 lines) is well-structured:

- **`ExecutionFeedbackProvenanceInputs`** — controlled form with 4 fields, callbacks for each, no internal state
- **`ExecutionFeedbackProvenanceDisplay`** — conditional render gated by `hasProvenanceValue()` type guard, amber badge with `inspect-only / caller-provided / unverified`
- **`hasProvenanceValue()`** — type narrowing guard, returns `false` if all fields are empty
- Import from `@/lib/api-client` type `FlywheelWorkerProvenance` — correct dependency direction
- Labels now in English (`Worker provenance`, `caller-provided, not verified`) — consistent with the component being a reusable building block, whereas the parent panel retains Chinese UI text for the controller-facing surface

One minor observation: the parent panel still owns the 4 `useState` calls for provenance fields (L375–378). This is fine for now — keeping state in the parent follows standard React lift-up pattern. A future extraction could bundle this into a `useWorkerProvenance()` hook, but it's not necessary at this stage.

---

### Structured Result

```
recommendation: accept

findings:
- Manual flywheel loop ran end-to-end with real AI calls (Qwen qwen3.6-plus) and a real delegated worker (claude-worker / glm-5)
- All 4 steps produced correct structured output; runtime artifacts verify non-stub data
- Result doc and scenario doc are disciplined about non-claims — no overclaiming of automation, persistence, verification, or canonical promotion
- First panel decomposition completed: provenance input/display extracted into execution-feedback-provenance.tsx (124 lines)
- Panel shrank from 1601 to 1537 lines (net -64)
- Provenance reset on new inspect run prevents stale identity leaking
- Backend/tests/router unchanged from provenance slice — zero semantic drift
- 36 tests pass; frontend builds cleanly
- Self-recommendation is honest: accept_with_changes, not accept

validation_gaps:
- Worker task was read-only — does not validate a production code change through the loop
- No test for the provenance reset behavior (UI state management, not backend)
- flywheel.py still 779 lines — decomposition urgency acknowledged but not started

next_suggestions:
- Split flywheel.py into 3 modules: flywheel_inspect.py, task_packet_preview.py, execution_feedback.py — same pattern as the panel decomposition, semantics-preserving
- Continue panel decomposition: worker-packet-bridge section and clipboard handlers are next extraction targets
- When decomposition is complete, consider a code-change loop (not read-only) through the manual flywheel to validate the path with real file edits
```

# chatgpt
本轮 review 对象是压缩包 **`IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_RESULT_2026-04-22.zip`**。
我按“不能只看第一层”的要求完整解包并审阅了这些文件：

* `MANIFEST.md`
* `docs/IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_RESULT_2026-04-22.md`
* `docs/IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_SCENARIO_2026-04-22.md`
* `docs/reviews/active/review_for_IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_RESULT_2026-04-22.md`
* `services/api/conversation_runtime/contracts.py`
* `services/api/conversation_runtime/flywheel.py`
* `services/api/tests/test_flywheel_inspect_route.py`
* `services/web/lib/api-client.ts`
* `services/web/components/evolution/flywheel-inspect-panel.tsx`
* `services/web/components/evolution/execution-feedback-provenance.tsx`

我没有在这里亲自重跑测试，也没有直接打开 `.runtime\flywheel-loop-demo-2026-04-22\` 和外部 worker run artifact，所以文档里写的“36 tests OK”“真实 AI/worker 调用”我视为**包内声明**，不当成我本地复验过的事实。

# 总体结论

**recommendation: `accept_with_changes`**

这是一次**方向正确、切片克制、而且确实完成了当前短期目标**的结果包。
如果这轮要证明的是：

```text
manual information input
-> AI-assisted flywheel inspect
-> human/controller selection
-> worker task packet
-> delegated worker execution
-> execution feedback inspect
-> controller absorption decision
```

那么从设计与实现层面看，这个目标**已经基本成立**。

它成立的前提是：

* 这是 **manual AI-assisted loop**
* 不是 runtimeized execution loop
* 不是 verified provenance loop
* 不是 automatic absorption loop
* 不是 canonical state update loop

这一点文档写得很克制，我认可。

---

# 我认为方向上最对的地方

## 1. 你们终于把“当前真实飞轮”定义清楚了

这轮最重要的进步，不是多了哪个字段，而是把短期 flywheel 目标钉死了：

* 先证明一个**人工驱动但 AI 辅助**的闭环能跑通
* 不要求自动调度
* 不要求 verified provenance
* 不要求 persistence
* 不要求 canonical absorption

这个定义很对。
它避免了两个常见错误：

* 过早把 flywheel 讲成自动闭环
* 因为不够自动，就否定当前切片的价值

## 2. 方向仍然符合长期主线

这轮没有偏离我们前面一直守的几条主线：

* 不 fake durability
* 不 fake automation
* 不把 chat / pasted feedback 当 truth
* 不 clean-slate
* 不把 UI 当主证明
* 不把 worker output 直接当 accepted knowledge

它依然是在证明一个**窄而真的飞轮闭环**。

## 3. “下一步先分解，不再加桥”这个判断是对的

结果文档最后一句我认同：

> The next implementation step should be bounded decomposition before any new bridge capability.

这是很成熟的判断。
因为现在这条线已经够证明自己了，再继续加 bridge，只会把 `flywheel.py` 和 panel 顶成伪 workflow shell。

---

# 主要 findings

## finding 1：这次已经足够算一个“短期 manual loop closure milestone”

我认为可以算。
理由不是它已经是完整 runtime，而是它完成了当前定义的最小闭环：

* 前面几轮补出来的 inspect / task packet / execution feedback bridge
* 这次被串成了一次真实的 manual scenario
* 形成了 information -> knowledge/evolution labels -> worker packet -> feedback reflection 的闭环叙述

对当前阶段来说，这已经是一个合理 milestone。

## finding 2：它没有明显 overclaim

这一点做得不错。
文档明确写了：

* 不证明 verified provenance
* 不证明 automatic absorption
* 不证明 runtimeized execution
* 不证明 canonical closure

这很重要。
因为现在最危险的不是“做得不够多”，而是“做完一个手动闭环后开始讲成自动系统已经成立”。

这轮没有犯这个错。

## finding 3：真实缺口已经从“有没有桥”变成“桥是不是该停了”

前几轮是在补：

* review bridge
* decision bridge
* task packet preview
* execution feedback bridge
* provenance annotation

现在这轮 manual loop closure 跑通后，重点已经不是再补下一座桥，而是：

* 这些桥的语义是不是已经够
* backend / frontend 是否该拆层
* 后续哪些桥要升级成真正 runtime object
* 哪些桥应该永久保持 manual

这说明项目在这一线上的成熟度确实往前走了一步。

---

# 主要 validation gaps

## gap 1：外部 runtime artifacts 不在包里

结果文档引用了：

* `.runtime\flywheel-loop-demo-2026-04-22\01_flywheel_inspect.json`
* `.runtime\flywheel-loop-demo-2026-04-22\02_task_packet_preview.json`
* `.runtime\flywheel-loop-demo-2026-04-22\03_execution_feedback_inspect.json`
* `claude-worker` 的 `final.json`

这些不在当前 review 包里，所以这轮更像是：

**基于实现 + 结果总结文档的架构/方向 review**，
而不是我直接核验了整条链的外部 artifact 真实性。

这不阻止我给方向上的 `accept_with_changes`，但要说清楚：
**它是有外部 evidence 依赖的 milestone**。

## gap 2：worker 仍然是 read-only scenario

结果文档自己也写了，这次 worker 是 read-only analysis，不是代码变更验证。
所以它证明的是：

* worker lane can participate in the manual loop

不是：

* end-to-end engineering execution loop is production-grade

这点要继续守住。

## gap 3：`flywheel.py` 和前端 panel 的结构债仍然真实存在

这轮没有解决这个问题，也不需要在这轮解决。
但它已经足够成为**下一步的主问题**。

---

# 当前最重要的 5 个风险

## 风险 1：把“manual loop closure”讲成“runtime closure”

这是当前最大的叙述风险。
这轮成立的是：

> manual AI-assisted flywheel can close once end-to-end

它不等于：

> runtime can now durably close the loop

这个边界必须继续守住。

## 风险 2：external evidence 仍然需要 controller 汇总

因为关键 runtime artifacts 不在包里，当前 closure 还是明显依赖 controller synthesis。
这在当前阶段不是致命问题，但说明它还不是 fully self-evidencing milestone。

## 风险 3：继续加 bridge 会把系统推成 pseudo-workflow

这轮之后再继续加：

* absorption write-back
* automatic rerun
* packet history
* feedback promotion
* more bridge fields

基本就会开始把 flywheel shell 做成伪 workflow 平台。
这是最该避免的事。

## 风险 4：panel 和 `flywheel.py` 再不拆就会越来越重

这不是本轮 blocker，但已经是明确下阶段问题。
现在 manual loop 成立后，再继续往这两个文件里堆语义，会比继续加新功能更危险。

## 风险 5：worker provenance annotation 仍然容易被社会语义过度相信

虽然前几轮已经把 `caller_provided` / `verified=false` 写得很明确，但用户视角里“有 run_id、有 provider、有 artifact_ref”天然就会让人更信它。
所以这个边界以后必须继续显眼，不然会被默默当成可信 provenance。

---

# 是否足够算当前短期 flywheel closure 点

**是，可以算。**

但我会加限定词：

> **它足够算当前短期 manual flywheel closure point。**

不是：

* durable closure point
* autonomous closure point
* runtimeized closure point
* verified execution closure point

这个限定词非常重要。

---

# 下一步建议

## 建议 1：接受这个 milestone，但不要再加 bridge

这轮之后，最合理的动作不是继续加桥，而是把这条线暂时收口。

## 建议 2：下一 implementation step 应该是 decomposition

我同意结果文档的结论：
下一步最值得做的不是功能，而是：

* `flywheel.py` 分层
* `flywheel-inspect-panel.tsx` 分层
* packet builders / review surfaces / execution feedback surfaces 拆开
* 保持语义不变

## 建议 3：如果后面要继续往前走，重点应转向“哪些桥该升格为真正对象”

也就是：

* 哪些仍然 manual
* 哪些该变成 reviewed object
* 哪些需要 runtime persistence
* 哪些不能继续留在 clipboard packet 层

这比继续补桥更有价值。

---

# 最后一句判断

**这轮 milestone 值得接受，而且它已经足够作为当前 flywheel 线的一个短期 closure point。**
但它证明的是：

> **人工驱动、AI 辅助、非 canonical 的飞轮闭环可以真实跑通一次。**

不是：

> **IKE 已经拥有了可信 runtime 化的自动飞轮。**

这条边界继续守住，方向就是对的。


# gemini
recommendation: accept_with_changes

findings:
- **End-to-End Loop Closure Verified:** The provided code and scenario trace successfully prove that a manual, AI-assisted flywheel loop (Information -> Knowledge -> Evolution -> Worker -> Feedback) can be executed without breaking the `inspect-only` boundary. The architectural pipeline is contiguous.
- **Strict Boundary Enforcement:** The system brilliantly avoids overclaiming trust. By hardcoding `provenance_source="caller_provided"` and `verified=False` in `flywheel.py` and reflecting this with explicit UI badges ("caller-provided, not verified") in `execution-feedback-provenance.tsx`, the design successfully absorbs worker output without granting it unearned canonical authority.
- **Successful Initial UI Decomposition:** Extracting the provenance inputs and display into `execution-feedback-provenance.tsx` is a highly effective proof-of-concept for the necessary frontend refactoring. It keeps the main panel cleaner while isolating the provenance state logic.
- **Defensive Test Coverage:** The tests in `test_flywheel_inspect_route.py` successfully assert that even when a user or controller provides empty provenance fields, the system defaults safely to unverified, caller-provided states.

validation_gaps:
- **Complex UI State Management:** While the extraction of the provenance component helps, `flywheel-inspect-panel.tsx` still manages a massive amount of local state (extraction, knowledge, triggers, sources, advice, controller packets). Relying on top-level component resets to clear stale worker identity or review decisions across different inspect runs is fragile and prone to state-leakage bugs during extended manual sessions.
- **Backend Module Bloat:** `flywheel.py` now handles intent derivation, summary building, task packet previews, and execution feedback reflection. It is bearing too much cognitive load for a single file, increasing the risk of boundary violations in future edits.

next_suggestions:
- **Immediate Mandate:** Halt all new feature development or bridge field additions. The immediate next phase must be purely structural decomposition.
- **Backend Decomposition:** Split `flywheel.py` into distinct bounded contexts (e.g., `flywheel_inspect.py`, `flywheel_preview.py`, `flywheel_feedback.py`) while preserving the exact current route semantics and tests.
- **Frontend Decomposition:** Continue the pattern established by `execution-feedback-provenance.tsx`. Break `flywheel-inspect-panel.tsx` into smaller, stateless presentational components managed by a central reducer or strict state machine to prevent cross-run data leakage.