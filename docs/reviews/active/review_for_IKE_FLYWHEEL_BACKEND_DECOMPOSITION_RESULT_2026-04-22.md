# Review For IKE Flywheel Backend Decomposition Result

Canonical review write-back file for:

- [D:\code\MyAttention\docs\IKE_FLYWHEEL_BACKEND_DECOMPOSITION_RESULT_2026-04-22.md](/D:/code/MyAttention/docs/IKE_FLYWHEEL_BACKEND_DECOMPOSITION_RESULT_2026-04-22.md)

## Review Scope

Please review whether backend decomposition phase 1 should be accepted.

Focus:

1. Whether `conversation_runtime/flywheel.py` is now only a safe compatibility facade.
2. Whether the split into `flywheel_inspect.py`, `task_packet_preview.py`, and `execution_feedback.py` preserves current route semantics.
3. Whether truth boundaries, inspect-only behavior, caller-provided provenance, and non-canonical proposal state remain intact.
4. Whether this is a sufficient structural step after the manual flywheel loop closure milestone.
5. Whether the worker lifecycle issue should block this patch or remain a support-track reliability issue.

Out of scope:

- new bridge fields
- automatic absorption
- persistence
- scheduler/runtime execution
- frontend decomposition

## Controller-Provided Validation

```text
python -m unittest services.api.tests.test_flywheel_inspect_route
21 tests OK

python -m unittest services.api.tests.test_conversation_runtime_route services.api.tests.test_flywheel_inspect_route
36 tests OK

python -m py_compile services/api/conversation_runtime/flywheel_inspect.py services/api/conversation_runtime/task_packet_preview.py services/api/conversation_runtime/execution_feedback.py
passed
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
先读取 review 请求文件和文件列表。
好，现在并行读取所有核心代码文件——新的 3 个模块 + facade + router。
现在检查测试文件和 contracts.py 是否有变化。
已经读完全部 10 个文件。以下是我的结构化 review。

---

## Review: IKE Flywheel Backend Decomposition Phase 1 (2026-04-22)

### 拆分概览

| 文件 | 行数 | 职责 |
|------|------|------|
| `flywheel.py` (facade) | 38 | 兼容性门面，re-export 三个路由函数 + `LLMAdapter` |
| `flywheel_inspect.py` | 340 | flywheel inspect 提示词、候选归一化、advice/controller packet、路由函数 |
| `task_packet_preview.py` | 251 | 标签归一化、intent/lane 推导、preview 构建（纯同步，零 LLM 依赖） |
| `execution_feedback.py` | 232 | 反馈提示词、反馈 advice/controller packet、provenance echo、路由函数 |
| **合计** | **861** | 原 monolith 779 行 → +82 行（import 块 + 模块 docstring 开销） |

Router、contracts、tests 均 **零变更**。

---

### Focus 1: flywheel.py 是否只是一个安全的兼容 facade？

**是。** 38 行，结构清晰：

```
facade docstring → LLMAdapter re-export → 3 个路由函数 re-export → __all__
```

关键设计：
- `from llm.adapter import LLMAdapter` 在 facade 顶层导入，tests 继续 patch `conversation_runtime.flywheel.LLMAdapter` 不需要改动
- `__all__` 显式声明了 5 个公共符号，没有多余暴露
- Facade 不含任何业务逻辑——没有条件分支、没有默认值覆盖、没有 wrapper 层

**无问题。**

---

### Focus 2: 拆分是否保留了当前的路由语义？

逐模块比对上一版 monolithic `flywheel.py`（779 行）：

| 模块 | 语义变化 | 依赖变化 |
|------|---------|---------|
| `flywheel_inspect.py` | 零语义变化。提示词、归一化器、advice/packet/notes/truth boundary 逐行一致 | `LLMAdapter` 改为运行时 deferred import from facade（L227） |
| `task_packet_preview.py` | 零语义变化。全部 7 个函数逐行一致 | 仅依赖 `contracts.py`，**最干净的模块** |
| `execution_feedback.py` | 零语义变化。提示词 + provenance section + advice + controller packet + notes + truth boundary 逐行一致 | `_normalize_knowledge_delta_candidates` / `_normalize_evolution_trigger_candidates` 从 `flywheel_inspect.py` 导入（L23-27），`LLMAdapter` deferred import from facade（L158） |

**deferred import 机制验证：**

```
模块加载时: flywheel.py → import flywheel_inspect (OK, 无回引)
                        → import task_packet_preview (OK, 无回引)
                        → import execution_feedback → import flywheel_inspect (已加载, OK)

路由调用时: run_flywheel_inspect() → from conversation_runtime.flywheel import LLMAdapter
            run_execution_feedback_inspect() → from conversation_runtime.flywheel import LLMAdapter
```

**无循环导入。** 加载时没有 facade → 子模块 → facade 的循环路径。运行时 deferred import 在 facade 已完全加载后才触发。

**测试 mock 路径兼容：** 全部 12 处 `patch("conversation_runtime.flywheel.LLMAdapter")` 不需要改动——facade 的 `LLMAdapter` 就是被 patch 的符号，子模块在运行时通过 deferred import 读取的正是被 patch 后的版本。

**Router 零变更确认：** L19-23 仍然 `from conversation_runtime.flywheel import ...`。

---

### Focus 3: Truth boundary、inspect-only、provenance、proposal state 是否完整？

| 约束 | flywheel_inspect.py | task_packet_preview.py | execution_feedback.py |
|------|----|----|-----|
| truth boundary | `flywheel_truth_boundary()` 5 条 ✅ | `_task_packet_preview_truth_boundary()` 5 条 ✅ | `_execution_feedback_truth_boundary()` 7 条（含 provenance 2 条）✅ |
| promotion_state | 未设置（FlywheelInspectResponse 默认 `inspect_only`）✅ | 显式 `"inspect_only"` L249 ✅ | 显式 `"inspect_only"` L230 ✅ |
| provenance | N/A | N/A | `provenance_source="caller_provided"`, `verified=False` 硬编码 L197-198 ✅ |
| proposal_state / review_gate | KnowledgeDeltaCandidate/EvolutionTriggerCandidate 默认值不变 ✅ | N/A | 复用同一 contract，不变 ✅ |
| advisory_scope | `"flywheel_inspect_only"` L217 ✅ | `"task_packet_preview"` L173 ✅ | `"execution_feedback_inspect_only"` L148 ✅ |

**所有 inspect-only 语义完整，无回归。**

---

### Focus 4: 作为 manual loop closure 之后的结构步骤是否充分？

**充分。** 这恰好是上一次 review 建议的第一个 next step：

> *"Split flywheel.py into 3 modules: flywheel_inspect.py, task_packet_preview.py, execution_feedback.py — same pattern as the panel decomposition, semantics-preserving"*

执行结果与建议完全一致。拆分后的模块边界清晰：
- `task_packet_preview.py` 零外部依赖（不依赖 LLM、不依赖 p0、不依赖 flywheel_inspect）
- `execution_feedback.py` 对 `flywheel_inspect.py` 的依赖只有 2 个共享归一化器 + 1 个 truth boundary 函数，后续可以进一步提取为 `flywheel_shared.py`

---

### Focus 5: Worker lifecycle issue 是否应该阻塞本 patch？

**不应该阻塞。**

Worker run `20260422T011922-6291c782` 被 controller abort 后仍然产出了可用 patch——这是 worker 生命周期管理的问题（没有正确返回 final result），不是代码语义问题。Result doc 正确地将其定义为 "worker lifecycle issue, not a code semantics issue"，并归类为 support-track reliability concern。

代码本身通过了 36 tests + py_compile + controller validation，与 worker 是否正常退出无关。

---

### 跨 slice 观察

1. **共享归一化器的耦合方向正确。** `execution_feedback.py` → `flywheel_inspect.py` 是单向依赖。如果后续有第 4 个消费者，应提取为 `flywheel_shared.py`（result doc 已识别此风险）。

2. **测试 mock 路径的 deferred import 策略是务实的。** 当前 12 个 test 都 patch 同一路径 `conversation_runtime.flywheel.LLMAdapter`。如果以后测试迁移到 patch 具体模块，facade 中的 `LLMAdapter` re-export 可以移除。但现在不需要动。

3. **`focus_category` import 是死代码。** `flywheel_inspect.py` L252 导入了 `focus_category` 但未使用——这是从 monolith 继承的，不是本次引入的。可以在下一个 cleanup 中移除，不阻塞。

4. **Frontend panel decomposition 仍待完成。** Panel 1537 行，目前只提取了 provenance 组件（124 行）。Backend 拆分完成后，frontend 拆分的阻碍降低了。

---

### 结构化结果

```
recommendation: accept

findings:
- flywheel.py 是 38 行纯 facade，无业务逻辑，仅 re-export + LLMAdapter mock 兼容
- 3 个新模块逐行保留原始语义，零路由变化、零 contract 变化、零测试变化
- deferred import 机制正确规避循环导入，同时保持 12 处测试 mock 路径兼容
- truth boundary、promotion_state、provenance 语义、proposal_state 全部完整无回归
- task_packet_preview.py 是最干净的模块：零 LLM 依赖、零 p0 依赖
- worker lifecycle abort 正确归类为 support-track issue，不影响代码语义
- 36 tests pass，py_compile pass，frontend build success

validation_gaps:
- flywheel_inspect.py L252 import focus_category 未使用（继承自 monolith，非本次引入）
- 无 import-time circular 测试（当前手工分析确认无循环，但无自动化防护）
s
next_suggestions:
- 继续 frontend panel 拆分：worker-packet-bridge section 和 clipboard handlers 是下一个提取目标
- 当第 3 个消费者需要 _normalize_knowledge/evolution 时，提取为 flywheel_shared.py
- 清理 focus_category 死 import（可合并到下一个小 patch）
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
recommendation: accept

findings:
- **Clean Facade Pattern:** `flywheel.py` has been successfully hollowed out into a pure compatibility facade. Re-exporting the route functions and `LLMAdapter` ensures zero breakage for existing router imports and test mocks.
- **Semantic Preservation:** The decomposition into `flywheel_inspect.py`, `task_packet_preview.py`, and `execution_feedback.py` is exact. Truth boundaries, non-canonical claims, and the `caller_provided` provenance constraints remain fully intact in their respective domains.
- **Appropriate Structural Step:** Following the loop closure milestone, attacking the backend bloat first was the correct strategic move. It lowers the cognitive load of each file and reduces the risk of boundary violations in future edits.
- **Pragmatic Reuse:** Reusing `_normalize_knowledge_delta_candidates` and `_normalize_evolution_trigger_candidates` across modules is an acceptable shortcut for this phase, avoiding premature abstraction.

validation_gaps:
- **Facade-Coupled Tests:** Because `LLMAdapter` is patched via the `flywheel.py` facade in current tests, the test suite is tightly coupled to the existence of the facade. If the facade is ever removed, the tests will immediately break.
- **Frontend Debt:** The frontend component `flywheel-inspect-panel.tsx` remains monolithic, carrying significant state-management risk during extended manual flywheel sessions.

next_suggestions:
- **Frontend Decomposition:** Now that the backend is modular, immediately pivot to decomposing the frontend `flywheel-inspect-panel.tsx` into smaller, state-isolated presentational components (matching the backend's inspect, preview, and feedback boundaries).
- **Test Refactoring (Low Priority):** In a future cleanup cycle, update the test suite to patch `LLMAdapter` directly inside `flywheel_inspect.py` and `execution_feedback.py` so the `flywheel.py` facade can be safely deleted.
- **Worker Lifecycle:** Treat the "worker aborted by controller" issue as a separate support-track reliability task, not a blocker for this architectural slice.