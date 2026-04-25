# Review For IKE Flywheel Frontend Section Decomposition Result

Canonical review write-back file for:

- [D:\code\MyAttention\docs\IKE_FLYWHEEL_FRONTEND_SECTION_DECOMPOSITION_RESULT_2026-04-23.md](/D:/code/MyAttention/docs/IKE_FLYWHEEL_FRONTEND_SECTION_DECOMPOSITION_RESULT_2026-04-23.md)

## Review Scope

Please review whether the flywheel runtime UI has reached a meaningful checkpoint after section-level decomposition.

Focus:

1. Whether the runtime surface is now clearly organized around the manual flywheel chain.
2. Whether `flywheel-inspect-panel.tsx` now behaves as an orchestrator rather than a monolithic mixed-responsibility panel.
3. Whether `task-preview`, `worker-packet bridge`, and `execution-feedback` are now sufficiently bounded UI sections.
4. Whether current inspect-only / non-canonical / caller-provided provenance semantics remain intact.
5. Whether this is enough for a phase-level checkpoint review, even if not yet a final runtime milestone.

Out of scope:

- new bridge semantics
- persistence
- automatic workflow scheduling
- canonical absorption
- backend semantic debt cleanup

## Controller-Provided Validation

```text
python -m unittest services.api.tests.test_conversation_runtime_route services.api.tests.test_flywheel_inspect_route
36 tests OK

npm run build
success
```

## Expected Review Output

```text
recommendation: accept | accept_with_changes | reject

findings:
- ...

validation_gaps:
- ...

next_suggestions:
- ...
```

---

Write reviewer results below this line.

# claude
<thinking>
Let me read the file list first.
</thinking>

先读取文件列表。
并行读取 result doc、review request doc，以及主面板文件。
最后读取 panel 剩余部分，了解 orchestrator 层如何组装 section 组件。
<thinking>
Now I have a comprehensive picture of the decomposition. Let me look at a few more things in the panel:

1. How the panel renders the three section components (TaskPreviewSection, WorkerPacketBridgeSection, ExecutionFeedbackSection)
2. The overall size reduction

Let me check the middle portion of the panel to see how the sections are assembled.
</thinking>

还需要看 panel 中间部分如何 render 三个 section 组件。
<thinking>
Now I have the full picture. Let me write the review.

**Key observations:**

1. **Panel size reduction**: From 1537 lines (after previous decomposition) to 865 lines. That's -672 lines. Significant.

2. **New files**:
   - `task-preview-section.tsx`: 142 lines — pure display + 2 callbacks
   - `worker-packet-bridge-section.tsx`: 93 lines — tab selector + copy + pre + slot for executionFeedbackSection
   - `execution-feedback-section.tsx`: 202 lines — form fields + provenance inputs + results display
   - `collapsible-section.tsx`: 49 lines — extracted from inline panel code
   - `flywheel-packet-builders.ts`: 325 lines — all 6 packet builder functions extracted
   - `clipboard.ts`: 16 lines — shared clipboard utility

3. **What's still in the panel (orchestrator role)**:
   - All state declarations (lines 28-66)
   - All event handlers: `handleSubmit`, `toggleSection`, `copyReviewPacket`, `copyAbsorptionPacket`, `copyDecisionPacket`, `requestTaskPreview`, `copyTaskPreviewPacket`, `copyWorkerPacket`, `requestExecutionFeedbackInspect`, `copyExecutionFeedbackPacket`, `toggleSelect`, `isSectionOpen`
   - Input form
   - Error/truth boundary banner
   - Manual review bridge (inline, not extracted)
   - Manual absorption surface (inline, not extracted)
   - Manual decision bridge (inline, not extracted)
   - Results area (CollapsibleSection blocks)
   - TaskPreviewSection, WorkerPacketBridgeSection (with ExecutionFeedbackSection as prop)

4. **Inspect-only semantics**:
   - Trust boundary banner still shown on every result
   - Non-canonical footers preserved in all packet builders
   - provenance semantics: `ExecutionFeedbackProvenanceInputs` and `ExecutionFeedbackProvenanceDisplay` are still used via `execution-feedback-section.tsx`

5. **Interesting design choice**: `ExecutionFeedbackSection` is passed as a prop (`executionFeedbackSection: ReactNode`) to `WorkerPacketBridgeSection`. This is the "slot" pattern — keeps the nesting hierarchy while allowing the bridge section to own its layout without knowing about execution feedback state. This is reasonable but adds complexity: the orchestrator constructs `ExecutionFeedbackSection` as JSX and passes it as a prop, which means all the state wiring for `ExecutionFeedbackSection` lives in the panel but the display logic lives in the section component.

6. **What was NOT extracted (still inline in panel)**:
   - Manual review bridge (L413-505): ~90 lines of inline display
   - Manual absorption surface (L507-620): ~110 lines with checkboxes
   - Manual decision bridge (L622-702): ~80 lines of display
   - Results CollapsibleSections (L756-860): ~100 lines

   These are the "earlier flywheel chain" elements. They weren't extracted in this round. The result doc says the panel is still the owner of state and request orchestration.

7. **`CollapsibleSection` extracted**: This was previously inline in the panel. Now it's its own file (49 lines). Good.

8. **Focus questions from review request**:
   - Is the runtime surface clearly organized around the manual flywheel chain? YES — the order in the panel is: input → inspect result → selection/absorption → decision → task preview → worker packet (with execution feedback inside)
   - Does panel now behave as orchestrator rather than monolithic? MOSTLY YES — but the manual review bridge, absorption surface, and decision bridge are still inline. The three chain sections are extracted.
   - Are task-preview, worker-packet-bridge, execution-feedback sufficiently bounded? YES — each is a pure controlled component with well-defined props.
   - Inspect-only/non-canonical/provenance semantics intact? YES — verified via packet builders footers + truth boundary banner + provenance component usage
   - Sufficient for phase-level checkpoint? YES with notes

9. **`CollapsibleSection` design observation**: It has both external `open` control and internal `expanded` state. The logic is: if `isForced (open)` then show expanded, if not forced check internal `expanded`. But clicking the button when `isForced` does nothing (sets `expanded` but it doesn't matter since `isForced` governs). This is a bit odd — when the parent forces `open=true`, clicking the header does nothing. When `open=false`, clicking toggles internal `expanded`. There's no way to collapse a forced-open section. This is a behavioral quirk but not a blocking issue.

10. **Indentation inconsistency in panel**: Looking at L705-753, the three section renders are not indented consistently with the rest of the JSX. This is likely leftover from the extraction process. Not a blocking issue.

Now let me write the review in Chinese (交流 convention).
</thinking>

已读完全部 10 个文件，信息充分。以下是结构化 review。

---

## Review: IKE Flywheel Frontend Section Decomposition (2026-04-23)

### 拆分全貌

| 文件 | 行数 | 角色 |
|------|------|------|
| `flywheel-inspect-panel.tsx` | 865 → 原 1537 | 缩减 **-672 行**，保留 state + handlers + orchestration |
| `task-preview-section.tsx` | 142 | 受控组件：task-packet preview 显示 + 2 个 callback |
| `worker-packet-bridge-section.tsx` | 93 | 受控组件：lane 选择 + copy + pre 预览 + slot |
| `execution-feedback-section.tsx` | 202 | 受控组件：反馈输入 + provenance + 结果展示 |
| `collapsible-section.tsx` | 49 | 通用 collapsible，已从 panel inline 提取 |
| `flywheel-packet-builders.ts` | 325 | 纯函数：6 个 packet builder，零副作用 |
| `clipboard.ts` | 16 | 共享剪贴板工具，navigator + execCommand 双 fallback |

---

### Focus 1: 运行时表面是否清晰对应 manual flywheel 链？

**是。** Panel 中 render 顺序现在与 flywheel 链完全对应：

```
输入表单 (L327-396)
→ inspect-only truth boundary banner (L407-411)
→ 手动审查包 (L413-505) — 仍 inline
→ 手动吸收面板 (L507-620) — 仍 inline
→ 手动决策桥接 (L622-702) — 仍 inline
→ TaskPreviewSection (L705-716) ← 提取 ✅
→ WorkerPacketBridgeSection (L720-753) ← 提取 ✅
  └── ExecutionFeedbackSection (prop slot) ← 提取 ✅
→ CollapsibleSection 结果组 (L756-860)
```

"早期链"（review/absorption/decision bridge）尚未提取，但顺序正确、与后段分离。

---

### Focus 2: Panel 是否现在充当 orchestrator？

**基本是，有一个重要观察。**

**orchestrator 层保留的职责（正确）：**
- 全部 state（L28-66）
- 全部 API handler：`handleSubmit`、`requestTaskPreview`、`requestExecutionFeedbackInspect`
- 全部 copy handler：6 个，均改为调用 `copyTextToClipboard`（不再内联重复 clipboard 逻辑）
- 事件下推：所有 `onChange` / `onClick` 以 callback prop 形式传给子组件

**仍 inline 的部分（不是阻塞，但值得记录）：**
- 手动审查包（~90 行）
- 手动吸收面板（~110 行，含 checkbox）
- 手动决策桥接（~80 行）

这三块是"飞轮链上游"的 UI，本次 scope 没有包含，合理。Panel 仍是 865 行，但职责边界更清楚了。

**`ExecutionFeedbackSection` 的 slot 设计值得注意：**

```tsx
<WorkerPacketBridgeSection
  executionFeedbackSection={
    <ExecutionFeedbackSection ... />
  }
/>
```

`WorkerPacketBridgeSection` 接受 `executionFeedbackSection: ReactNode`（L18），在 L89 直接渲染。这是 composition slot 模式——`WorkerPacketBridgeSection` 不感知 execution feedback 的状态，只管布局容器。这个设计合理，但有一个轻微耦合点：`ExecutionFeedbackSection` 需要 `taskPreviewResult` 作为 prop（L32、L192-196），而这个 prop 在 orchestrator 层传入，不是来自 `WorkerPacketBridgeSection`。整体没有问题。

---

### Focus 3: 三个 section 是否足够 bounded？

**是。** 逐个检查：

| 组件 | 内部状态 | 外部依赖 | 副作用 |
|------|---------|---------|--------|
| `TaskPreviewSection` | 无 | 7 个 props + 2 callback | 无（纯受控） |
| `WorkerPacketBridgeSection` | 无 | 8 个 props，在内部调用 `buildWorkerPacket()`（来自 builders）| 无，packet 内联渲染到 `<pre>` |
| `ExecutionFeedbackSection` | 无 | 16 个 props + 5 callback | 无，所有 API 调用通过 `onRequestInspect` callback 触发 |
| `CollapsibleSection` | `expanded: boolean`（内部） | `open: boolean`（external force）| 无 |

**`CollapsibleSection` 一个设计细节：** 当 `open=true` 时，点击 header 不能折叠（L39：`onClick={() => !isForced && setExpanded(false)}`）。这是有意设计——`open` 由父组件控制，非 forced 时才可手动 toggle。但 `expanded` 内部状态在 forced open 时无意义。这不是 bug，不影响功能，但后续如果需要双向控制需要明确处理。

---

### Focus 4: Inspect-only / non-canonical / provenance 语义是否完整？

**完整，且提取后更清晰。**

| 约束 | 位置 | 状态 |
|------|------|------|
| Truth boundary banner | `flywheel-inspect-panel.tsx` L407-411 | ✅ 仍在 |
| Packet 非规范 footer | `flywheel-packet-builders.ts` 所有 6 个 builder 末行 | ✅ 集中在一处，更易审计 |
| Provenance 展示 badge | `execution-feedback-section.tsx` L149，使用 `ExecutionFeedbackProvenanceDisplay` | ✅ |
| Provenance 输入 | `execution-feedback-section.tsx` L113-122，使用 `ExecutionFeedbackProvenanceInputs` | ✅ |
| Provenance 字段传 API | `flywheel-inspect-panel.tsx` L276-279，`trim() \|\| undefined` | ✅ |

**`flywheel-packet-builders.ts` 是本次最有价值的提取：** 6 个 builder 过去分散在 panel 内，现在集中在 325 行的纯函数模块。每个 builder 的最后一行都有明确的非规范声明，可以一次性 audit，不需要在 panel 里寻找。

---

### Focus 5: 是否足够进入 phase-level checkpoint review？

**是。**

**现状：**
- Panel 1537 → 865 行（-44%）
- Backend: flywheel.py 779 → 38 行 facade + 3 个 ~200-340 行模块
- 新增独立模块/组件：8 个（`execution-feedback-provenance.tsx` + 本次 6 个 + `clipboard.ts`）
- 手动 flywheel loop 已运行验证（2026-04-22 runtime artifacts）
- 36 tests 全绿，frontend build success

**这是一个合理的 phase checkpoint 节点。** 但 phase 级 review 时需要明确区分已完成和未完成的：

已完成：
- Backend 拆分（flywheel.py 拆成 3 模块）
- Frontend section 拆分（3 个 section 组件 + builders + clipboard）
- 手动 loop 端对端验证
- 信任边界 / non-canonical 语义全程完整

未完成（应在 phase review 中记录为已知 debt）：
- 手动审查包 / 吸收面板 / 决策桥接仍 inline（~280 行）
- Panel 仍持有全部 state（合理但未来可考虑 reducer / hooks）
- `ConversationControllerPacket` 字段对齐债务（多个 advisory_scope 语义待统一）

---

### 结构化结果

```
recommendation: accept

findings:
- 面板从 1537 行缩减至 865 行（-672 行，-44%），是迄今最大的单次 frontend 减量
- 三个 section 均为纯受控组件：零内部状态、零副作用、所有 API 调用通过 callback 触发
- flywheel-packet-builders.ts 将 6 个 packet builder 集中为可独立 audit 的纯函数模块
- clipboard.ts 消除了原先散布在 panel 中的重复剪贴板逻辑
- collapsible-section.tsx 完成通用组件提取
- inspect-only 语义：truth boundary banner 保留，所有 builder 末行非规范声明集中可审
- provenance 组件链完整：inputs → api call → display，均经由 section 组件传递
- 36 tests 全绿，build success，行为无回归

validation_gaps:
- 手动审查包、吸收面板、决策桥接 (~280 行) 尚未提取，panel 仍有 inline layout 块
- CollapsibleSection 双状态设计（forced open + internal expanded）轻微耦合，可在下次清理时明确
- 无针对 section 组件的独立测试（UI 行为层，非强制阻塞）

next_suggestions:
- Phase checkpoint review 时明确区分已完成项和已知 debt 项（见上方列表）
- 下一轮提取目标：手动吸收面板（含 checkbox）+ 手动决策桥接
- 中期：将 state 迁移到 useFlywheelState() hook 或 reducer，减少 orchestrator 层膨胀
- 长期：ConversationControllerPacket advisory_scope 语义统一（backend semantic debt）
```
# chatgpt
本轮 review 对象是压缩包 **`IKE_FLYWHEEL_BACKEND_DECOMPOSITION_RESULT_2026-04-22.zip`**。

我实际审阅的文件是：

* `MANIFEST.md`
* `docs/IKE_FLYWHEEL_BACKEND_DECOMPOSITION_RESULT_2026-04-22.md`
* `docs/reviews/active/review_for_IKE_FLYWHEEL_BACKEND_DECOMPOSITION_RESULT_2026-04-22.md`
* `services/api/conversation_runtime/flywheel.py`
* `services/api/conversation_runtime/flywheel_inspect.py`
* `services/api/conversation_runtime/task_packet_preview.py`
* `services/api/conversation_runtime/execution_feedback.py`
* `services/api/conversation_runtime/contracts.py`
* `services/api/routers/conversation_runtime.py`
* `services/api/tests/test_flywheel_inspect_route.py`

我没有在这里亲自重跑测试，所以文档里写的 `21 tests OK / 36 tests OK / py_compile passed` 视为包内声明，不算我本地复验过的事实。

## 总体结论

**recommendation: `accept_with_changes`**

这轮是一次**方向正确、范围守住、而且确实在解决上一轮主问题**的 backend decomposition。
它做的是我们上一轮明确建议的事：

* 不再继续给 `flywheel.py` 加语义
* 先把 backend 拆成更清楚的 bounded modules
* 保持现有 route shape、truth boundary、inspect-only 语义不变

从代码看，这个目标基本达成了：

* `flywheel.py` 现在已经退成了兼容 facade
* `flywheel_inspect.py`、`task_packet_preview.py`、`execution_feedback.py` 分别承接三条主要后端能力
* `router` 仍然只依赖公共入口函数
* 没有顺手扩 persistence、workflow、自动吸收、自动执行

这说明这不是“重构之名、扩面之实”的包。方向是对的。

---

## 做对了什么

### 1. `flywheel.py` 退成 facade，这一步是对的

这是这轮最重要的正向结果。
现在它只做：

* re-export route functions
* 保留 `LLMAdapter` 兼容 patch 路径
* 暴露 `flywheel_truth_boundary`

这比之前把所有逻辑堆在一个文件里健康得多。

### 2. 三个模块的职责划分基本合理

当前切分大致是：

* `flywheel_inspect.py`

  * flywheel inspect
  * 知识/进化候选提取
  * advice / controller packet
* `task_packet_preview.py`

  * 已选 labels 的归一化
  * preview intent / lane / next step
* `execution_feedback.py`

  * execution feedback prompt
  * reflection candidate
  * provenance echo
  * feedback advice / controller packet

这个切法不是终局，但对当前阶段已经够用，而且比单文件堆叠清楚很多。

### 3. truth boundary 看起来保持住了

从新模块里的注释、返回对象和 route 语义看，原有边界没有明显被破坏：

* inspect-only
* non-canonical
* no persistence
* no automatic delegation
* no automatic promotion
* caller-provided provenance 仍然只是 unverified context

这是这轮最需要守住的东西，你们守住了。

### 4. decomposition 没有改变 public route 形状

当前 public routes 还是：

* `/conversation-runtime/flywheel/inspect`
* `/conversation-runtime/flywheel/task-packet/preview`
* `/conversation-runtime/flywheel/execution-feedback/inspect`

这很好，因为当前这轮目标是 backend 分层，不是 API 再设计。

---

## 最主要的 5 个问题

### 问题 1：这只是 decomposition phase 1，不是 backend architecture clean-up complete

这一点文档自己也写得还算诚实，我同意。
虽然 `flywheel.py` 被拆开了，但**共享逻辑并没有真正抽成中性层**，只是被重新分布到了几个模块里。

最明显的是：

* `execution_feedback.py` 仍然直接复用 `flywheel_inspect.py` 里的 `_normalize_knowledge_delta_candidates` 和 `_normalize_evolution_trigger_candidates`

这现在可以接受，但说明：

> 共享候选归一化逻辑还只是“模块内复用”，不是“明确 shared helper/substrate”。

所以这轮不应被讲成“后端 flywheel 模块已经整理干净了”。
更准确的说法应该是：

> `backend decomposition phase 1 complete`

### 问题 2：`LLMAdapter` 兼容 facade patch 是现实做法，但仍然是过渡债

为了让旧测试还能 patch `conversation_runtime.flywheel.LLMAdapter`，现在 facade 里保留了这个导入。
这在当前阶段是合理的 pragmatic 选择，我不反对。
但它本质上还是一个**测试兼容债**，不是优雅设计。

如果后面测试逐步转向 patch 具体模块，这个 compatibility shim 就应该考虑收掉。
否则 facade 会一直带着历史兼容包袱。

### 问题 3：`task_packet_preview.py` 里的 `ConversationControllerPacket` 语义错位债仍在

这一轮没有解决这个问题，只是把它搬到了更清楚的模块里。
具体还是这句：

* `actionable_correction_targets=actionable_targets`

但这里装进去的是：

* `knowledge:...`
* `evolution:...`
* `source:...`

不是 correction target。
这在当前 slice 还没造成严重问题，因为它还是 inspect-only preview。
但这是明确的语义错位债，不能因为现在分模块了就当它不存在。

### 问题 4：`flywheel_inspect.py` 仍然偏厚

虽然总体比以前好很多，但 `flywheel_inspect.py` 现在仍然比较厚，承担了：

* prompt
* extraction parsing
* normalization
* advice
* controller packet
* truth boundary
* route function

这在当前阶段不是 blocker，但说明分解还只是第一步。
如果后面继续扩：

* more candidate kinds
* richer advice
* more inspect traces

这个文件会再次变成新的“中心模块”。

### 问题 5：worker lifecycle 问题不该阻塞代码接受，但也不能被弱化

结果文档里提到 delegated run：

* 有 useful patch
* 但因 no-final / no-stdout 被 controller abort
* 最终是 controller 本地验证后接受

我认同文档里的判断：
这更像 **worker lifecycle reliability issue**，不是代码语义问题，所以不应该阻塞这轮 patch 接受。
但这也意味着你们的“support-track reliability concern”是真实存在的，不能因为代码包本身正确就忽略。

---

## materially complete 的部分

我认为这轮已经 materially complete 的有：

1. `flywheel.py` 的第一阶段后端拆分
2. facade + bounded submodule 的基本结构
3. public route 兼容保持
4. inspect/task-preview/execution-feedback 三条线的后端逻辑分离
5. 现有 truth boundaries 的保持
6. 作为 “manual loop closure 之后的下一步结构收敛” 这一点，已经成立

---

## 仍然 mixed / 需要继续记账的部分

1. shared candidate helper 还没有真正独立出来
2. `ConversationControllerPacket` 的字段语义债还在
3. `flywheel_inspect.py` 本身以后仍可能再次变厚
4. facade 中的 `LLMAdapter` 兼容 patch 是过渡设计
5. frontend decomposition 还没开始，而前端现在同样是明显厚点

---

## 是否建议接受

**建议：`accept_with_changes`。**

### 接受理由

* 方向对
* 范围守住
* 解决的是上一轮明确建议的问题
* 没有借分解偷偷扩 scope
* 保持了 inspect-only / non-canonical / no automation 的主线边界

### `with_changes` 的含义

不是要求回去重做，而是建议明确把以下几项记账成下一阶段债务：

1. shared flywheel candidate helper 提取
2. `ConversationControllerPacket` 字段语义修正
3. facade `LLMAdapter` 兼容 shim 的后续收敛
4. frontend decomposition 作为下一明显结构目标

---

## 推荐的下一步

### 最推荐

**前端 decomposition，而不是继续补 backend 语义。**

因为当前这轮之后，backend 至少已经不再是明显的单文件堆叠问题。
接下来更突出的结构债，其实已经转到了前端：

* `flywheel-inspect-panel.tsx`
* worker packet / feedback / review / decision 这些桥的组合

### 次推荐

如果还想继续 backend 收敛，就只做：

* shared candidate helper 抽取
* 不加任何新能力

我不建议现在继续做：

* 新 bridge
* 新对象族
* richer execution semantics
* persistent workflow handoff

---

## 一句话总结

**这轮 backend decomposition 是对的，而且足够作为“phase 1 结构收敛”接受；它没有扩 scope，保持了原有 truth boundary，也确实缓解了 `flywheel.py` 的单文件问题。下一步最该动的不是 backend 再加语义，而是前端 decomposition，外加把 shared helper 和 controller packet 的语义债明确记账。**


# gemini
recommendation: accept_with_changes

findings:
- **完美的领域与视图物理隔离 (Domain vs. View Isolation):** 你提取的 `clipboard.ts` 处理得非常干净，通过创建 `left: '-9999px'` 的隐藏 `textarea` 实现了向 `document.execCommand('copy')` 的优雅降级。同时，`flywheel-packet-builders.ts` 彻底接管了数据契约转换，硬编码了 `--- 此包为执行结果的 inspect-only 反思压缩，非规范事实，未自动吸收，未自动重新派发 ---` 这一免责声明。这意味着即使未来其他开发者乱改 UI 组件，底层的 Truth Boundary 契约也不会被破坏。
- **渲染职责的精确下放 (Render Delegation):** 拆分后的 `execution-feedback-section.tsx` 独立承担了复杂的反馈结果渲染。我看到代码中它直接消费 `executionFeedbackResult`，并为 `knowledge_delta_candidates` (使用 `bg-blue-50 text-blue-700` 样式) 和 `evolution_trigger_candidates` (使用 `bg-purple-50 text-purple-700` 样式) 进行了精准的映射渲染。这极大降低了顶层组件的 DOM 树深度和认知负载。
- **类型安全的通道遍历 (Type-Safe Lane Iteration):** 在 `worker-packet-bridge-section.tsx` 中，你使用了精确的类型断言 `(['coding', 'review', 'test'] as WorkerLane[])` 来遍历渲染按钮，配合 `workerCopiedMap` 记录拷贝状态。这在人工决策 UI 中保证了绝对的枚举安全。

validation_gaps:
- **灾难性的状态透传 (Catastrophic Prop Drilling):** 虽然你在 DOM 结构上成功解耦了 Section，但**状态管理完全没有解耦**。在 `execution-feedback-section.tsx` 的类型签名 `ExecutionFeedbackSectionProps` 中，我看到了多达 **19 个** 扁平透传的 Props（例如 `executionStatusHint`, `onExecutionStatusHintChange`, `workerRunId`, `onWorkerRunIdChange`, `executionFeedbackLoading`, `taskPreviewResult` 等）。`flywheel-inspect-panel.tsx` 仍然是一个持有海量 `useState` 的上帝组件（God Component），这在 React 架构中是典型的反模式，极度脆弱。
- **并发与状态重置漏洞 (State Reset Vulnerability):** 现在的状态是由散落的 `useState` 管理的。在连续的“手动飞轮循环”中，如果用户修改了顶层的 `topic` 并发起新的 `onRequestInspect`，系统缺乏一个原子化操作来同步清空下游的 `taskPreviewResult` 和 `executionFeedbackResult`。这极易导致上一个任务的 Worker ID 幽灵般地残留、污染到下一个任务中。

next_suggestions:
- **接受当前切片为里程碑 (Phase Checkpoint Approval):** 就“前端区块分解 (Section-level Decomposition)”这一阶段目标而言，你已经完美实现了前后端拓扑的镜像对齐（UI 拆分与之前的后端路由拆分相呼应）。同意将此切片作为闭环点合并。
- **立刻执行状态收敛 (Immediate State Reducer Refactoring):** 下一步**严禁**在前端引入任何新的桥接字段或业务功能。必须立刻启动状态机重构：在 `flywheel-inspect-panel.tsx` 中引入 `useReducer`（例如定义一个 `FlywheelReducer`，响应 `START_NEW_INSPECT`, `UPDATE_PROVENANCE`, `SET_PREVIEW_RESULT` 等 Action），用一个统一的 `state` 对象和 `dispatch` 函数替换掉所有冗长丑陋的回调 Props 透传。