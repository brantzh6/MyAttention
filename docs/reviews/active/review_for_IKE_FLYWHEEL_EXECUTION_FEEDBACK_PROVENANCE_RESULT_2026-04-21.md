# Review For IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21

Canonical review target:

- [D:\code\MyAttention\docs\IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.md](/D:/code/MyAttention/docs/IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.md)

Review pack:

- [D:\code\MyAttention\.runtime\review-packs\IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.zip](/D:/code/MyAttention/.runtime/review-packs/IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.zip)
- [D:\code\MyAttention\.runtime\review-packs\IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21_FILE_LIST.md](/D:/code/MyAttention/.runtime/review-packs/IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21_FILE_LIST.md)

## Review Request

Please review the execution-feedback provenance slice.

Focus:

1. Whether caller-provided worker provenance is clearly non-canonical and unverified.
2. Whether provenance context can improve AI-driven review/decision flow without creating fake trust.
3. Whether the frontend/backend contract is minimally sufficient for manual worker-result return.
4. Whether any acceptance blocker exists before continuing the flywheel mainline.

Non-goals:

1. Do not require persistence.
2. Do not require automatic worker execution.
3. Do not require automatic knowledge/evolution promotion.
4. Do not require verified worker identity yet.

Expected review format:

```text
recommendation: accept | accept_with_changes | reject

findings:
- ...

validation_gaps:
- ...

next_suggestions:
- ...
```

## Worker Run Notes

- `20260421T060852-7a9a5dc1`: coding run via `qwen-bailian-coding / glm-5`; aborted by controller after long no-output wait.
- `20260421T061546-e50646df`: coding retry via `z-ai / glm-5.1`; failed with provider `429 Rate limit reached for requests`.
- `20260421T062156-4ae63ff8`: coding retry via `qwen-bailian-coding / glm-5`; succeeded and reported validation pass.

## Claude Worker Kimi Review

run_id: `20260421T062753-213f8f3a`

recommendation: accept

findings:

- Provenance is correctly marked as caller-provided and unverified in `WorkerProvenance`.
- Provenance does not alter truth state semantics; `promotion_state` remains `inspect_only`.
- Provenance context is included in the AI prompt only when fields are provided and is explicitly marked unverified.
- Response notes include `provenance_source=caller_provided` and `provenance_verified=false`.
- Backend tests cover provided provenance and missing provenance.
- Frontend API contract matches backend fields.
- Frontend displays provenance with inspect-only / caller-provided / unverified badge.

validation_gaps:

- None from Kimi review.

next_suggestions:

- Consider one partial-provenance test in a later hardening slice.
- Document provenance spoofing risk for future API integrators when this route becomes public.

## External Review Results

Write reviewer results below this line.

# claude

Now reading all the code files.
Now reading the new tests and checking the frontend changes.
Let me check the frontend provenance input UI and display.
I now have all the context needed. Here is my structured review.

---

## Review: IKE Flywheel Execution Feedback Provenance (2026-04-21)

**Slice summary:** Adds a minimal, inspect-only provenance layer to the existing execution feedback bridge — 4 optional caller-provided identity fields (`worker_run_id`, `worker_provider`, `worker_model`, `worker_artifact_ref`) echoed back as a structured `WorkerProvenance` object with hardcoded `provenance_source="caller_provided"` and `verified=False`.

**Delta from prior slice:** contracts.py +22 lines, flywheel.py +34 lines, tests +124 lines, api-client.ts +15 lines, panel +95 lines. Router unchanged.

---

### Reviewer 1: Trust-Boundary Specialist

**Focus: Is caller-provided provenance clearly non-canonical and unverified?**

| Check | Verdict |
|-------|---------|
| `WorkerProvenance` hardcodes `provenance_source="caller_provided"` and `verified=False` | ✅ No codepath to set `verified=True` |
| Truth boundary extended with 2 provenance disclaimers (L369–371) | ✅ Explicit and unambiguous |
| AI prompt section gated by field presence, marked `"caller-provided, not verified"` (L603) | ✅ Clean injection |
| Prompt section excluded entirely when all fields empty (verified by test L898–900) | ✅ No phantom context |
| Notes include `provenance_source=caller_provided` and `provenance_verified=false` | ✅ Auditable |
| Frontend badge: `inspect-only / caller-provided / 未验证` on amber background | ✅ Visually distinct |
| Provenance does NOT alter `promotion_state`, `truth_status`, `review_gate`, or candidate semantics | ✅ Zero trust escalation |

The trust model is structurally correct. The backend wraps caller fields with fixed trust metadata that the caller cannot influence. There is no path from provenance to any canonical state change.

---

### Reviewer 2: Contract & Integration Specialist

**Focus: Is the frontend/backend contract minimally sufficient?**

| Layer | What changed | Assessment |
|-------|-------------|------------|
| **Request** (contracts.py L294–298) | 4 optional `Field("")` fields with `(not verified)` descriptions | Minimal. Optional by default. |
| **Response** (contracts.py L335) | `provenance: WorkerProvenance = WorkerProvenance()` | Always present, always populated. |
| **`WorkerProvenance`** (contracts.py L301–314) | 4 echo fields + 2 trust metadata fields | Clean model. No mutation surface. |
| **TS interface** (api-client.ts L247–254) | `FlywheelWorkerProvenance` with all required fields | Correct — backend always returns all fields with defaults. |
| **TS request** (api-client.ts L240–244) | 4 optional fields | Matches Python `Field("")`. |
| **Frontend call** (panel L672–676) | `trim() \|\| undefined` — sends only non-empty fields | Clean. Avoids sending whitespace-only. |
| **Frontend input** (panel L1336–1380) | 4-column compact grid in dashed border | Minimal. Clearly marked optional + inspect-only. |
| **Frontend display** (panel L1407–1444) | Conditional render only when any field non-empty, amber badge | Correct gating. No display for empty provenance. |

The contract is symmetric: request adds optional fields, backend wraps with trust metadata, response echoes everything. No surplus. TS types match Python models exactly.

---

### Reviewer 3: Test & Robustness Specialist

**Focus: Are the new tests structurally sound?**

| Test | What it verifies | Assessment |
|------|-----------------|------------|
| `test_execution_feedback_inspect_with_provenance_echoed_unverified` (L822–891) | All 4 fields echoed, `provenance_source`, `verified=False`, notes, truth boundary, **and prompt content** via in-mock assertions | ✅ Strong. The in-mock prompt verification (L828–832) is the best pattern seen in this test file. |
| `test_execution_feedback_inspect_missing_provenance_valid` (L893–944) | Empty provenance remains valid, prompt does NOT contain provenance section, defaults echoed | ✅ Correct edge-case coverage. |

**Test debt:**
- No partial-provenance test (e.g., only `worker_run_id` provided, others empty). Kimi review already flagged this for a later hardening slice. Low risk — the conditional in `_build_execution_feedback_prompt` (L601) is a simple OR gate, not a complex conditional.
- Total execution feedback tests now at 4 (was 2). Coverage improving.

**Validation pass:** 21 tests, all green. Frontend build succeeded.

---

### Cross-Slice Observations

1. **Panel at 1601 lines.** This slice added +95. Decomposition is now overdue — the provenance input/display pattern is a clean extraction candidate for a sub-component.

2. **Provenance naming is collision-safe.** The result doc correctly notes that `worker_run_id` etc. with explicit `provenance_source="caller_provided"` won't collide with future verified identity fields — as long as verified identity uses a different model (e.g., `VerifiedWorkerIdentity`), not the same field names with a `verified=True` flag.

3. **AI prompt leakage risk is acknowledged and mitigated.** The prompt explicitly tells the AI the provenance is caller-provided. If the AI hallucinates additional provenance details, the `WorkerProvenance` response object will NOT contain them — only the 4 exact fields from the request are echoed. The hallucination risk is contained to `feedback_summary` text, which is already non-canonical.

4. **Delegation execution was rough** — 3 runs needed (abort, rate-limit, success). The review-for doc honestly documents this. No impact on code quality.

---

### Structured Result

```
recommendation: accept

findings:
- Provenance is structurally non-canonical: hardcoded caller_provided/unverified with no escalation path
- Trust boundary extended with 2 provenance-specific disclaimers
- AI prompt injection gated correctly — no phantom provenance in empty-field case
- In-mock prompt verification is the strongest test pattern in this file
- Contract is symmetric and minimally sufficient across all layers
- Frontend display correctly gated with visible unverified badge
- No changes to candidate truth state, promotion_state, or review_gate

validation_gaps:
- No partial-provenance test (deferred to hardening, low risk)
- Panel now 1601 lines — decomposition increasingly urgent

next_suggestions:
- Extract provenance input/display into a sub-component during panel decomposition
- Add one partial-provenance test in the next hardening slice
- When verified worker identity is introduced, use a distinct model name to avoid collision with WorkerProvenance
```

# chatgpt
本轮 review 对象是压缩包 **`IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.zip`**。
我按“不能只看第一层”的要求完整解包并审阅了这些文件：

* `MANIFEST.md`
* `docs/IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.md`
* `docs/reviews/active/review_for_IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.md`
* `services/api/conversation_runtime/contracts.py`
* `services/api/conversation_runtime/flywheel.py`
* `services/api/routers/conversation_runtime.py`
* `services/api/tests/test_flywheel_inspect_route.py`
* `services/web/components/evolution/flywheel-inspect-panel.tsx`
* `services/web/lib/api-client.ts`

我没有在这里亲自重跑测试，所以文档里写的测试通过与前端 build 通过，我视为包内声明，不当成我本地复验过的事实。

# 总体结论

**结论：`accept_with_changes`。**

这轮是一个**方向正确、范围守住、而且补的是上一轮真正缺口**的 follow-up。
上一轮我建议优先补 provenance contract，而不是继续堆更多“反思语义”。这次确实做的是这个：

* 给 execution feedback inspect request 增加最小 provenance 输入
* 在 response 里返回结构化 provenance
* 明确 provenance 是 `caller_provided` 且 `verified=False`
* truth boundary、prompt、前端显示都强调“未验证、非 canonical”

这和我们一直强调的主线一致：

* 不 fake trust
* 不把 pasted feedback 当 truth
* 不因为有了 worker/run/artifact 字段就假装 provenance 已经可信
* 不把 execution feedback bridge 推成自动执行/自动吸收层

所以方向上，我认可。

但我不给纯 `accept`，因为仍然有几处需要继续压住：

1. **provenance 现在只是 caller-provided echo，不是可信 provenance**
2. **`controller_packet` 继续像 action object 靠近的风险还在**
3. **前端 panel 与 backend `flywheel.py` 继续变厚**
4. **这轮解决的是 provenance annotation，不是 execution loop runtimeization**

---

# 做对了什么

## 1. provenance 的语义边界基本写对了

这是这轮最重要的正确点。

现在你们没有把新增字段命名成“verified worker identity”之类会误导的东西，而是：

* request 允许传：

  * `worker_run_id`
  * `worker_provider`
  * `worker_model`
  * `worker_artifact_ref`
* response 统一封成 `WorkerProvenance`
* 并明确：

  * `provenance_source="caller_provided"`
  * `verified=False`

这就把当前 slice 的真实地位说清楚了：

> 这是人为贴回的 provenance context，不是系统确认过的 provenance truth。

这个边界是对的。

## 2. prompt 里带 provenance，但没有把它升格为 truth

`flywheel.py` 里把 provenance 作为“caller-provided, not verified”上下文放进 prompt，这也是合理的。
因为这轮想证明的是：

* provenance 能不能帮助 AI 更好地反思 worker 结果
* 但不会因此产生 fake trust

目前做法是：

* AI 能看到 provenance
* 同时 prompt 里明确写了它未验证
* response 里也继续保留未验证标识

这个设计是诚实的。

## 3. 前端显示也足够克制

前端没有把 provenance 做成“可信 badge”或“runtime-linked identity”，而是加了明显的 inspect-only / caller-provided / 未验证 展示。
这很好，因为很多系统的问题不是后端错，而是 UI 把不可信东西展示得太像可信。
这轮没有犯这个错。

## 4. 它补的是正确缺口

上一轮 execution feedback bridge 最大的问题就是 provenance 太弱，只是自由文本 pasted result。
现在补的正好是：

* 这条反馈来自谁
* 对应哪个 run
* 哪个 provider/model
* 哪个 artifact ref

虽然还不可信，但至少**有结构了**。
对当前人工飞轮来说，这是有价值的。

---

# 最重要的 5 个问题

## 问题 1：当前 provenance 只是“结构化自述”，不是“可验证 provenance”

这是当前最重要的提醒。

现在这个 slice 成立的是：

> the system can carry and display caller-provided provenance context

它**没有**成立：

* verified worker identity
* artifact existence verification
* packet-to-run binding validation
* model/provider authenticity
* execution record truth

也就是说，这轮补的是：

**provenance annotation**

不是：

**provenance verification**

这个区别必须一直说清楚，不然很容易被误读成：
“现在 worker provenance 已经有了，可信度问题解决了。”

没有解决。

---

## 问题 2：`controller_packet` 仍然有社会语义过强的风险

这轮 execution feedback inspect 仍然返回：

* `operational_advice`
* `controller_packet`
* `suggested_next_step`
* `reason_tags`

虽然 `advisory_scope=execution_feedback_inspect_only` 和 `truth_status=non_canonical` 已经压住了不少风险，但从社会语义上它还是很像：

> 系统在给 controller 整理一个下一步动作包

当前之所以还能接受，是因为你们写了足够多的边界说明。
但这依然是后续最容易被误用成 workflow contract 的位置。

**建议：**
继续明确：

* provenance route returns reflection context only
* not a decision record
* not an execution record
* not a controller acceptance object

---

## 问题 3：`flywheel.py` 和 `flywheel-inspect-panel.tsx` 继续变厚

这是连续几轮都在积累的工程债。

### backend

`flywheel.py` 现在已经承担：

* inspect
* task packet preview
* execution feedback inspect
* prompt building
* operational advice
* controller packet
* provenance packaging

### frontend

`flywheel-inspect-panel.tsx` 现在承担：

* inspect input
* review bridge
* absorption bridge
* decision bridge
* worker packet copy
* feedback paste
* provenance inputs
* provenance display

这说明你们已经把当前 flywheel line 推成了一个**人工微流程工作台**。
目前还没越界，但再继续往这两个文件里加能力，就会很危险。

**建议：**
这轮之后优先级应该是：

* 先停
* 或先拆层
* 不要继续在一个 panel 和一个 flywheel module 上叠语义

---

## 问题 4：这轮证明的是“provenance-aware reflection”，不是“execution feedback loop 已可信”

这个叙述风险要明确指出。

现在成立的是：

> pasted worker result can carry caller-provided provenance and be reflected on with that context

没有成立的是：

* runtime execution loop
* trusted worker callback path
* verified artifact handoff
* execution result absorption
* formal controller acceptance flow

所以这轮不能被讲成：

* execution loop 更完整了
* provenance 问题已解决
* worker return path 已可信

准确表述应该是：

> execution feedback inspect now supports bounded provenance annotation.

---

## 问题 5：前端 provenance 字段目前够用，但再继续加就会滑向半结构化 workflow form

现在加四个 provenance 字段是合理的：

* run_id
* provider
* model
* artifact_ref

但如果后面继续加：

* validator
* execution duration
* token usage
* branch/ref
* packet checksum
* reviewer identity

这个 panel 就会开始变成一个手填 workflow form。

而你前面已经明确纠偏过：

* IKE 不是固定表单平台
* AI conversation 是核心入口
* form 只是 review/confirmation surface

所以 provenance 输入现在够了，再多就会走偏。

---

# materially complete 的部分

我认为这轮已经 materially complete 的有：

1. execution feedback inspect route 的最小 provenance contract
2. `caller_provided + unverified` 的 truth boundary
3. provenance 进入 prompt 的 bounded context
4. provenance 在 response 与前端上的透明展示
5. 不影响当前 `promotion_state` / `review_gate` / truth semantics
6. 保持 inspect-only、non-canonical、manual 路径

这些目标都完成了。

---

# 仍然 mixed / 需要记账的部分

1. provenance 还不是 verified provenance
2. execution feedback 还不是 formal execution object
3. `controller_packet` 仍然容易被社会语义上误读成 action object
4. `flywheel.py` 和 panel 的厚度继续积累
5. 这轮是 annotation，不是 runtime loop hardening

---

# 是否建议接受

**建议：`accept_with_changes`。**

### 接受理由

* 方向对
* 切片窄
* 边界诚实
* 真正补了上一轮缺口
* 没有引入 fake trust 或 fake automation

### `with_changes` 的意思

不是要求回去重做这包，而是建议后续明确记账：

1. **verified provenance 仍然是未来问题，不要把当前 caller-provided echo 讲成已解决**
2. **不要继续给 controller packet 增更多执行/决策语义**
3. **不要再往 panel 里加更多 provenance 表单字段**
4. **这轮之后优先考虑拆层或停住，而不是继续加桥**

---

# 推荐的下一步

我建议优先顺序如下：

## 第一优先：停住这条线

这条 execution feedback bridge 现在已经有：

* feedback inspect
* bounded reflection
* minimal provenance annotation

对当前人工飞轮来说已经够证明自己了。
现在更该做的是吸收和判断，而不是继续细化这个 bridge。

## 第二优先：如果一定要继续动代码，优先拆层

不是加功能，而是：

* flywheel backend 分层
* panel 子组件拆分
* contract/builders 抽离

## 第三优先：把 provenance 的“未来真问题”记进 roadmap

不是现在实现，而是明确写进 roadmap：

* verified provenance
* artifact existence checks
* packet/run binding
* trusted callback path

---

# 一句话总结

**这轮是一个方向正确、边界诚实、值得接受的 provenance follow-up；它把 execution feedback 从“纯 pasted text”推进到了“带最小结构化 provenance 的反思输入”，但这仍然只是 provenance annotation，不是 provenance verification，更不是 execution loop 的可信 runtime 化。**

# gemini
**IKE Sentinel (治理代理) 审查模式已激活。**

> **当前审查目标声明 (Review Target Statement)**
> **正在审查的文档/包：** `IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21`
> **涉及核心代码：** `contracts.py`, `flywheel.py`, `test_flywheel_inspect_route.py`, `flywheel-inspect-panel.tsx`
> **审查范围：** 执行反馈出处（Execution Feedback Provenance）层的边界安全性、零信任声明以及前后端物理对齐。

基于提供的 M阶段/飞轮 (Flywheel) 代码实现与测试证据，以下是针对本次结案请求的深度架构级审查报告：

### 1. 核心发现 (Findings)

* **极佳的零信任防伪造设计 (Zero-Trust by Design):** 这是本次提交最亮眼的地方。你在 `contracts.py` 中定义输入请求 `FlywheelExecutionFeedbackInspectRequest` 时，只允许调用方传入基础的 string 字段（如 `worker_run_id`）。而在 `flywheel.py` 的响应组装中，你**硬编码**了 `provenance_source="caller_provided"` 和 `verified=False`。这意味着无论调用方（或恶意脚本）如何在 API payload 中伪造“已验证”状态，系统在输出和入参给大模型时，都强制将其降级为“未经验证的调用方提供（Caller-Provided）”。这死死守住了事实边界。
* **安全的 Prompt 上下文护栏 (Safe Context Injection):** 在将 `worker_run_id` 等信息喂给底层 LLMAdapter 时，你不仅传递了数据，还显式在 prompt 中追加了免责声明，告知模型这只是外部参考信息。这有效防止了大模型因为看到了看似权威的 "run_id" 而产生“过度确信（Overconfidence）”的幻觉。
* **严格的非规范性维持 (Non-Canonical Maintenance):** 引入溯源（Provenance）信息并没有让路由的性质发生改变，它仍然牢牢待在 `inspect-only` 的笼子里。UI 组件 `flywheel-inspect-panel.tsx` 也很诚实地渲染了“未经验证 (unverified)”的徽章。

### 2. 验证缺口与遗留观测 (Validation Gaps & Architectural Notes)

本次提交非常严谨，没有阻塞性缺陷。但作为哨兵，我记录以下几点以备未来演进：

* **TypeScript 契约的完整性:** 在提供的 `api-client.ts` 截断代码中，没有直接看到 `WorkerProvenance` 的 `interface` 定义。虽然 `flywheel-inspect-panel.tsx` 能够通过 `result.provenance.worker_run_id` 访问，请确保前端的 TS 类型定义与后端的 Pydantic 模型严格对齐，特别是显式声明 `verified: boolean` 和 `provenance_source: string`。
* **未来验证层 (Future Verification Layer) 的占位:** 目前 `verified=False` 是在 `run_execution_feedback_inspect` 中硬编码的。未来的 M 阶段如果要引入真正的机器身份校验（例如通过签名或内部 Worker JWT 校验），你需要在这里引入一个前置的拦截器（Interceptor）或校验中间件来将这个字段合法地翻转为 `True`。当前的硬编码是 Phase 0 / 早期飞轮的最优解。

### 3. 最终判定 (Recommendation)

本次切片非常精准地解决了一个实际的痛点（人工 Review 时需要知道结果是哪个 Agent/Run 跑出来的），同时**没有**牺牲系统的事实底线。你证明了你可以通过“增加信息维度”来赋能人类，而不必同时“赋予机器写权限”。

**Recommendation: `accept` (通过，无需修改直接合并)**

**哨兵结语:** 防御性编程（Defensive Programming）在架构边界处得到了完美体现。方向极其正确，代码可执行性高，且未未来向“可验证凭证（Verifiable Credentials）”进化留下了干净的接口。批准闭环此任务！