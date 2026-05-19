# Current Operations

Date: 2026-05-02

Truth status: controller operations runbook; active until replaced.

## Purpose

Governance says what must be true.

Operations says what to do next, in what order, and when to stop.

This file is the daily execution entry point for `D:\code\MyAttention`. It exists because the project now has too many historical docs for memory-based continuation to be reliable.

## First-Read Rule

At the start of every controller session, read only these files unless the task requires deeper context:

1. `AGENTS.md`
2. `docs/CURRENT_OPERATIONS.md`
3. `docs/CURRENT_MAINLINE_CONTROL_2026-05-02.md`
4. `docs/CURRENT_WEEKLY_REVIEW_ACTION_LEDGER.json`
5. the active task packet named by `CURRENT_MAINLINE_CONTROL`

Do not start by scanning all `docs/`.

Open older docs only when one of the active files points to them.

## Toolchain Incident Rule

Standard controller tools are part of operations, not optional convenience.

If a required standard tool fails, fix or explicitly record the tooling incident before falling back to a weaker workflow. Current standard tools include:

- `rg` for repository search
- `git` for worktree truth
- `python scripts/governance/classify_worktree.py` for scoped dirty-worktree classification
- lane validation commands named by the active packet

Do not silently replace a failed standard tool with ad hoc PowerShell scanning unless the fix is blocked and the blocker is recorded.

Current `rg` note:

```text
2026-05-06: bundled WindowsApps Codex rg failed with Access denied; user-level ripgrep 15.1.0 was installed through winget and now resolves from C:\Users\jiuyou\AppData\Local\Microsoft\WinGet\Links\rg.exe.
```

## Weekly Review Closure Rule

Weekly project review is a closed-loop control, not a passive summary.

Before producing a new strategic review, consume the previous review:

1. Read `docs/CURRENT_WEEKLY_REVIEW_ACTION_LEDGER.json`.
2. For every prior action, mark `completed`, `partial`, `not_started`, or `superseded`.
3. Record evidence for the status.
4. Convert accepted review conclusions into explicit priority changes, escalations, or next actions.
5. Only then add new review findings.

If closure evidence is insufficient, stop at closure gaps and do not run a greenfield review.

## Review Trigger Rule

Review gates are governance controls, not default waiting loops.

Local review is the default for ordinary scoped work:

1. Controller scope review.
2. Required validation commands.
3. Local Claude Code / delegated L1 review for small code changes, UI patches, packet updates, and review-finding fixes.
4. Controller absorption and promotion decision.

GitHub/Codex review is only triggered when the work is becoming a GitHub-visible promotion candidate:

- a PR is intended to be merged as a published project version
- cloud PR evidence is explicitly needed for cross-IDE collaboration
- the change crosses a runtime/API/integration boundary
- local review is unavailable or insufficient for the risk
- the user explicitly requests GitHub/Codex review

Do not trigger GitHub/Codex review for:

- small corrective patches after an already-understood finding
- docs or packet wording fixes
- local exploratory branches
- work that is not ready for promotion
- validation-only packets unless they are about to be promoted as the canonical test contract

If Codex review was already triggered accidentally, consume the result when it arrives, but do not wait on it as the current blocker unless the PR is the active promotion candidate.

## Execution Record And Reviewer Gate Rule

Every material project action must leave an auditable record before it can
become accepted project truth.

For implementation, test, runtime, UI, adapter, governance, and documentation
work, the minimum lifecycle is:

```text
task packet -> execution/result artifact -> independent reviewer artifact -> controller absorption
```

Rules:

- The controller may define scope, write packets, and make the final
  absorption decision, but must not accept material execution output without
  an independent reviewer artifact.
- The executor and reviewer must be different lanes whenever practical. If the
  same tool family is used, the review prompt must be separate, read-only, and
  explicitly framed as review.
- Runtime output must go through runtime review before controller absorption.
- Test execution output must be reviewed before it is used as promotion or
  acceptance evidence.
- UI implementation output must pass UI validation plus review before
  controller absorption.
- Governance or operations changes must be recorded and reviewed before they
  become the new operating rule.
- If reviewer dispatch fails, record the review-lane incident and either
  reroute to a working reviewer or mark the work as `pending_review`; do not
  silently absorb it as accepted.
- A controller direct edit is allowed only for very small corrective actions.
  If it changes behavior, runtime, governance, or project truth, it still
  requires a result note, reviewer artifact, and controller absorption.
- Read-only orientation commands, status checks, and artifact lookup do not
  require durable task packets, but any conclusion used for acceptance does.

This rule is the correction mechanism against controller-only drift.

## Agent Dispatch Matrix

The controller owns routing and acceptance. It must delegate execution and
validation through the narrowest working lane instead of absorbing every task.

Current practical dispatch surface:

| Lane | Primary delegate | Current command / surface | Gate |
| --- | --- | --- | --- |
| Controller / promotion | Codex main controller | current thread | never delegated |
| Design / plan review | Gemini CLI | native `gemini` CLI with packet file/stdin; verify artifact locally | controller absorption |
| Backend coding | OpenClaw GLM / Claude Code | OpenClaw through `acpx openclaw-*`; Claude Code through native `claude -p ... < <packet>` | local L1 review, tests |
| High-risk coding | Claude Code / OpenClaw GLM | explicit reinforced packet | code review, test, controller |
| UI design/dev | Gemini CLI for current UI implementation and review support | native `gemini` CLI with packet file/stdin; verify artifact locally | UI validation, review, controller |
| Code review | local Claude Code CLI | `python scripts\review\run_l1_review.py ... --execute claude-cli` | controller absorption |
| Runtime operator | Claude Code runtime operator | native `claude -p --permission-mode bypassPermissions --output-format text --add-dir D:\code\MyAttention < <runtime_operator_packet>` | runtime review before controller |
| Runtime review | Gemini CLI / Claude Code review | native CLI first; OpenClaw review only when gateway is ready | controller absorption |
| Test execution | Test agent, desired `claude-worker + qwen3.6-plus` | native Claude Code or Qoder CLI packet execution; qwen-backed adapter still needs proof | controller absorption |

Dispatch rule:

- use native local CLIs for local agents first: Claude Code, Gemini CLI, and
  Qoder CLI are local tools, not ACP-only lanes
- use `acpx` only for OpenClaw/ACP session agents or when a specific ACP
  session feature is required
- do not route Claude Code through `acpx claude`; the ACP Claude adapter is
  currently an incident surface, while native `claude -p` is proven
- if a lane has a working command, use it
- if the desired lane exists only as a role contract but not a proven adapter,
  record an adapter gap before falling back
- if a delegate cannot write the required artifact, capture its returned
  review/result into the repo-local artifact and record the tool failure
- if a delegate claims an artifact was written, verify it locally with
  `Test-Path`/read before accepting the result
- if a delegate broadens scope, stop the lane and escalate to controller
- if a task needs runtime truth, dispatch runtime operator first; do not let
  the controller perform runtime operations
- in a dirty worktree, review packets must distinguish current packet delta
  from accepted uncommitted context; otherwise scope-expansion findings are
  controller questions, not automatic rejection

Current mechanism gaps:

```text
2026-05-11:
- Gemini runtime review could read and review but failed to write the required
  repo-local review artifact because its file write tool errored on missing
  paths. Controller captured the returned review in
  docs/reviews/active/review_for_runtime_operator_handoff_preview_smoke_2026-05-11.md.
- The desired test lane `claude-worker + qwen3.6-plus` has a role contract but
  no proven project-level acpx adapter binding. Treat this as an adapter gap
  until a dispatch smoke proves the exact command/model binding.
- 2026-05-11 test-agent dispatch smoke through `acpx claude exec` did not
  return structured delegate output; it emitted ACP notification errors and no
  saved session. Treat the test lane as `partial` until adapter output is
  repaired or an alternate qwen-backed test adapter is configured.
- Historical note: the runtime operator path was previously attempted through
  `acpx claude`, but this is no longer the default. Use native Claude Code CLI
  for runtime operator packets.
- 2026-05-11 Gemini UI implementation through `acpx gemini` historically
  edited allowed UI files and ran `npm run build`, but failed to create a new
  result artifact through ACP file writes until it used a shell `New-Item`
  workaround. Do not treat this as the current preferred route; invoke Gemini
  CLI natively and verify artifacts locally.
- 2026-05-11 local Claude review dispatch for the Gemini UI packet produced ACP
  `session/update` parameter errors and no structured review result. Treat the
  Claude review lane as unavailable for this specific gate and require
  controller absorption plus validation evidence.

2026-05-13:
- `acpx` was upgraded from 0.3.1 to 0.7.0. `acpx claude exec` still failed
  for a simple structured-output smoke with `Internal error`, so the local
  Claude review lane must not use ACP Claude until repaired upstream or by a
  dedicated adapter fix.
- Native Claude Code CLI is usable: `claude -p --permission-mode
  bypassPermissions --output-format text` returned structured output in a
  smoke test.
- `scripts/review/run_l1_review.py --execute claude-cli` is now the preferred
  local L1 review runner. It sends the review prompt to Claude through stdin,
  captures stdout, and writes the canonical `.runtime/reviews/results/...`
  artifact.
- Historical Gemini-through-ACP evidence showed structured text but transient
  ENOENT file errors. Current default is native Gemini CLI, with controller
  verification of artifact existence and content.
- OpenClaw Kimi review is unavailable until the OpenClaw gateway is reachable.
  Current evidence: `openclaw status` reports gateway unreachable / scheduled
  task stopped, and `acpx openclaw-kimi exec` exits with ECONNREFUSED to
  127.0.0.1:18789. Do not route time-sensitive review gates to OpenClaw Kimi
  until the runtime operator repairs gateway readiness.

2026-05-17:
- Controller correction: do not use `acpx` as a universal wrapper for local
  CLIs. Claude Code, Qoder CLI, and Gemini CLI should be invoked natively by
  default. `acpx` remains appropriate for OpenClaw ACP/session agents and for
  explicit ACP session workflows only.
- The previous use of `acpx claude` for runtime/test delegation was a routing
  mistake, not a model choice. Native Claude Code CLI is the working local
  runtime/test fallback until a dedicated qwen-backed test adapter is proven.
```

## Review Gate Termination Rule

Review gates are governance controls, not infinite confirmation loops.

For a bounded PR, the controller may stop requesting further automated review and proceed to promotion decision when all of these are true:

1. The latest actionable findings have been explicitly accepted, rejected with reason, or fixed.
2. No unresolved review thread remains.
3. The fix does not expand scope, risk level, runtime truth, persistence, scheduler, worker execution, permission, or promotion semantics.
4. Required validation for the lane has passed or the validation gap is recorded in the promotion decision.
5. The PR is mergeable and the worktree classifier is clean.

Do not trigger another GitHub/Codex review only to confirm a low-risk wording, packet correction, or small local fix that can be reviewed by local Claude Code. Trigger another GitHub/Codex review only when the fix changes promotion-ready code behavior, crosses a lane boundary, changes validation surface, or introduces a new L3 risk.

Temporary review monitors are allowed only for active GitHub/Codex promotion reviews. They must be deleted after the review returns, the PR is promoted, or the controller terminates the gate. Do not create monitors for local review, small fixes, or non-promotion branches.

## Automation Reliability Rule

Recurring automation is runtime governance, not a promise created by a config
file alone.

After creating or materially changing a heartbeat automation, verify it before
depending on it:

1. Temporarily set a short smoke interval when the automation type allows it.
2. Confirm the heartbeat reaches the intended current thread.
3. Restore the intended cadence.
4. Record durable evidence: `status`, target thread, `last_run_at`,
   `next_run_at`, and whether an automation TOML exists.

An automation shown as `ACTIVE` is insufficient evidence by itself. If the
TOML file is missing, newly recreated, points at the wrong thread, or
`last_run_at` did not advance after the expected window, classify it as an
automation incident and fix the automation before relying on it for mainline
control.

Current automation incident note:

```text
2026-05-11: mainline-stall-watch did not wake the controller after the
expected stall window. Local evidence showed the automation row existed from
2026-05-09, but there was no successful run before the 2026-05-11 smoke
repair. The heartbeat TOML was recreated at 2026-05-11 08:58 local. After
smoke validation, the automation was restored as a 4-hour mainline-stall
fallback: if real mainline progress occurred in the last 4 hours, skip; if no
real mainline progress occurred for 4 hours or more, wake the current thread
with one bounded mainline continuation packet. Treat ACTIVE status without
smoke evidence as untrusted.

2026-05-11 follow-up: mainline-stall-watch showed scheduler run-state
advancing to last_run_at = 2026-05-11 13:58:48 and next_run_at =
2026-05-11 17:58:48, but the current thread/session logs did not show a
corresponding visible heartbeat message around that time. Treat this as a
delivery-visibility incident, not a scheduler-total-failure. Future checks must
separate scheduler state (`last_run_at`) from delivery state (visible heartbeat
or explicit DONT_NOTIFY/NOTIFY decision in the current thread). If a stalled
run should notify but no current-thread message appears, repair the automation
before relying on it.

2026-05-12 incident update: mainline-stall-watch target_thread_id was verified
as the current unarchived `主控` thread, so the issue was not a wrong thread.
A temporary 1-minute heartbeat smoke was attempted on the existing heartbeat
because Codex only allows one active heartbeat per thread. During the active
controller turn, `next_run_at` advanced but `last_run_at` did not advance and
no real `SMOKE_OK` message was delivered. Treat thread heartbeat as a reminder
layer only, not the sole executable fallback.

2026-05-12 repair: created `mainline-stall-watch-local-executor`, an ACTIVE
local cron automation scoped to `D:\code\MyAttention`, hourly cadence, local
execution environment. It checks for 4-hour mainline stalls and, only if
stalled, writes `tasks/codex/mainline_stall_resume_packet_<YYYY-MM-DD-HHMM>.md`
with owner lane, SDLC stage, gate, validation, and stop condition. This is the
current executable fallback. The original thread heartbeat remains ACTIVE at
4-hour cadence as a best-effort reminder, but it is not trusted by itself.

2026-05-12 04:09 follow-up: the thread heartbeat did deliver back to the
current controller thread. The local cron fallback, however, ran three times
and each run was blocked by `windows sandbox: setup refresh failed with status
exit code: 1` before it could read workspace files. The cron fallback was
paused to avoid repeated blocked inbox noise. The heartbeat created
`tasks/codex/mainline_stall_resume_packet_2026-05-12-0410.md` as the current
controller-consumable resume packet.

2026-05-13 correction: `mainline-stall-watch-local-executor` was paused again.
The stall automation should wake the controller thread only; it should not run
workspace work, create packets, operate runtime, or open new lanes. The active
heartbeat is the reminder layer, and the controller decides the next mainline
action after wakeup. The weekly project review automation remains paused while
controller-driven work is active, to avoid duplicate review lanes.

2026-05-14 limitation: wake-only heartbeat successfully reminds the controller
thread, but it does not by itself guarantee continued work after the reminder.
After a NOTIFY heartbeat, the controller must resume mainline work in the next
normal turn without waiting for another planning discussion. Treat this as a
human/controller continuity mechanism, not an autonomous executor. If autonomous
continuation is required later, it must be designed as a separate runtime-safe
executor loop with explicit workspace permissions, WIP limits, review gates,
and stop conditions.

2026-05-15 update: `mainline-stall-watch-local-executor` was restored as an
ACTIVE local fallback on a 2-hour cadence. It is constrained to one smallest
bounded mainline action after a 4-hour stall, must write a
`tasks/codex/mainline_auto_continue_result_<date>.md` artifact, and must stop
after that one action. It remains lower authority than the controller:
controller promotion, review-gate termination, runtime-service operations, and
GitHub/Codex promotion reviews are still not delegated to the automation.

2026-05-18 correction: the local executor was triggering, but its prompt
allowed ineffective progress such as updating indexes, writing wrapper packets,
or running classifiers while an active mainline packet already existed. The
executor prompt was tightened: if an active packet exists, it must dispatch or
execute that packet, write a hard blocker, or route runtime preconditions to the
runtime operator. It must not count artifact-index updates, review-queue
updates, classifier-only runs, or wrapper-packet creation as mainline progress.
```

## Current Mainline Pointer

Active mainline:

```text
flywheel_v1_ai_entry_control_surface
```

Current product objective:

```text
Build the first usable IKE evolution loop with an AI conversation entry and a visible project control surface.
```

Current recently accepted flywheel packet:

```text
tasks/codex/flywheel_v1_real_worker_execution_feedback_inspect_absorption_2026-05-18.md
```

The mainline has three first-class tasks:

1. `evolution_flywheel_v1`: make the inspect-only AI-assisted loop runnable end to end.
2. `ai_conversation_entry`: make AI conversation the product entry into typed candidates, controller packets, and review-gated next actions.
3. `project_control_surface`: make IKE's mainline, phase, capability gaps, progress, and active lanes visible in UI so control does not depend on chat memory.

Current accepted support slice:

```text
PR #2 merged at acf922c: GitHub signal relation hints improved source-intelligence input quality.
```

Current source-intelligence role:

```text
support lane for flywheel input quality, not the top-level product mainline.
```

Current UI/control-surface status:

```text
required mainline anchor; previous accepted UI evidence may exist only in a local quarantine snapshot and must be treated as optional. The clean PR path must recreate or recover the UI without depending on unpublished refs.
```

Current default gate:

```text
local validation plus local Claude Code/delegated L1 review, then controller absorption
```

GitHub/Codex gate:

```text
only for promotion-ready GitHub PR versions or explicitly requested cloud review
```

Rationale:

- GitHub PRs are the stable review surface for published project versions and cross-IDE collaboration.
- PR-local artifacts prevent review truth from living only in chat or task links.
- Controller still owns promotion; GitHub/Codex review is evidence, not acceptance.
- Routine local fixes should not block on Codex Cloud latency or manual triggers.

Current worktree state:

```text
over budget as of 2026-05-18; latest classifier total: 178;
recommendation: requires_scoped_review_prep; budget: max_entries=20,
max_groups=3
```

Current quarantine note:

```text
the oversized dirty snapshot was preserved locally during cleanup, but it is not a published collaboration dependency. Delegates must not rely on it; recreate or recover bounded UI files through a clean branch/PR.
```

## Session Loop

Every controller session follows this loop.

### 1. Orient

Run:

```powershell
git status --short --branch
python scripts/governance/classify_worktree.py --cwd D:\code\MyAttention --limit 5
```

Then answer:

- What is the active mainline?
- Which of the three mainline tasks does the request advance?
- Which lane does the user request touch?
- Is the worktree clean enough for direct scoped work?

If these cannot be answered in 5 minutes, stop and update `CURRENT_OPERATIONS.md` or `CURRENT_MAINLINE_CONTROL_2026-05-02.md` before coding.

### 2. Classify The Request

Every new request is classified into exactly one bucket:

- `mainline_flywheel`: advances the first usable evolution flywheel loop
- `mainline_ai_entry`: advances AI conversation as the entry into typed candidates and controller packets
- `mainline_control_surface`: advances the visible project/progress/capability anchor
- `source_intelligence_support`: improves source/person/signal quality in service of the flywheel
- `ui_lane`: Gemini CLI implementation work for the control surface or related UI
- `review_gate`: local review, GitHub/Codex promotion review, finding absorption, PR readiness
- `worktree_ops`: classify, split, stage, branch, or cleanup planning
- `governance`: changes to policy, lifecycle, or acceptance rules
- `incident`: broken validation, blocked branch, bad merge, lost state
- `parking_lot`: useful but not current

If a request spans multiple buckets, split it and choose the first executable slice.

### 3. Protect The Mainline

Mainline work gets priority unless:

- there is an incident
- a review gate blocks promotion
- dirty worktree state prevents a scoped PR
- the user explicitly chooses another lane

Control-surface UI is part of the mainline anchor when it makes project phase, capability gaps, or lane progress visible. Other UI work remains independent and must not redefine runtime truth.

### 4. Decide Action Type

Use this order:

1. If the task lacks scope, write or update a task packet.
2. If implementation is needed, delegate by default.
3. If the patch is very small and corrective, controller may edit directly.
4. If review feedback exists, absorb findings before new feature work.
5. If the worktree is mixed, do scoped prep before any PR.

### 5. Validate

Every completed task must record:

- files changed
- validation commands
- known risks
- recommendation: `accept`, `accept_with_changes`, or `reject`

Missing validation means no promotion.

Runtime environment is a first-class validation surface, separate from source
truth. When a task touches API startup, service dependencies, frontend/backend
integration, model provider configuration, scheduler/worker execution, or any
live route used by the mainline, validation must record both:

- code truth: compile, build, unit, lint, or static checks that apply to the
  changed files
- runtime truth: service startup command, actual bound URLs/ports, `/health`
  result, affected API route result, frontend route result when applicable,
  and dependency state as `healthy`, `degraded`, or `unavailable`

Runtime failures must not be hidden behind UI fallback data. A route may return
structured degraded state instead of 500 when a dependency is down, but the
response must identify `truth_plane: runtime_truth` or an equivalent explicit
runtime marker. Hardcoded runtime endpoints are an incident unless the packet
explicitly scopes a fixed local port. Prefer configurable runtime settings such
as `FRONTEND_BASE_URL` and record the effective value in validation evidence.

If code truth passes but runtime truth fails, the task is not promotion-ready.
Classify it as `accept_with_changes` only when the runtime gap is explicitly
bounded and the next repair packet is named.

Runtime operator loop:

- daily runtime assurance should be delegated to the local runtime operator,
  not absorbed into the main controller thread by default
- controller must not start, stop, restart, or repair runtime services
  directly; it may request runtime evidence and consume reviewed runtime
  summaries
- when a controller task needs runtime truth, the controller must create or
  reference a bounded runtime-operator packet and dispatch it to the runtime
  operator before making a readiness claim
- current primary runtime operator is local Claude Code through native
  `claude -p`; do not use `acpx claude` for this lane
- Qoder CLI is a runtime implementation delegate candidate
- Gemini CLI is a runtime design/review delegate candidate
- runtime operator output must pass runtime review before controller
  absorption; controller should receive only reviewed summaries, blockers, and
  decision requests unless deeper evidence is needed
- runtime operator may self-dispatch bounded implementation/recheck workers
  inside an authorized packet; only unresolved blockers or semantic decisions
  escalate to controller
- controller consumes the runtime operator report and decides whether the
  mainline is ready, degraded, or blocked
- current protocol:
  `docs/RUNTIME_OPERATOR_LOOP_PROTOCOL_2026-05-09.md`

## WIP Limits

Hard limits:

- max 1 active mainline implementation packet
- max 1 active UI implementation packet
- max 1 active review-gate absorption
- max 1 active worktree cleanup operation
- max 3 total active implementation/review nodes

If a fourth node appears, stop and close or park one node.

## Problem Intake Rule

New problems discovered during work do not automatically become current work.

Use this decision tree:

1. Does it break the active task validation?
   - yes: fix inside current task if in scope; otherwise stop and report blocker
2. Does it touch runtime truth, persistence, scheduler, harness, permissions, or promotion?
   - yes: escalate to reinforced governance and write a new packet
3. Is it same lane but outside current scope?
   - yes: add parking-lot note or next packet candidate
4. Is it another lane?
   - yes: park it; do not mix it into the current patch

## Dirty Worktree Operations

The worktree is currently over budget. Treat this as an operational constraint, not as the mainline itself.

Current containment decision:

```text
tasks/codex/dirty_tree_containment_absorption_2026-05-18.md
```

No new implementation patch should start from the shared dirty tree until a
scoped package boundary is accepted. First package to prepare:
`flywheel_readiness`.

Post-absorption packaging rule:

```text
After any accepted implementation/test/UI/runtime slice, the controller must
either prepare a scoped package boundary, explicitly park the slice, or reject/
supersede it before opening the next implementation slice.
```

Allowed while dirty:

- read/classify
- write controller notes
- write task packets
- prepare scoped candidates
- stage only lane-specific files after explicit selection

Forbidden while dirty:

- broad commit
- broad push
- mixed PR
- opportunistic cleanup inside feature work
- deleting untracked artifacts without explicit approval

Scoped PR checklist:

1. Run classifier.
2. Name the lane.
3. Name the candidate files.
4. Confirm candidate files stay in one lane.
5. Stage only those files.
6. Run lane validation.
7. Push a scoped branch.
8. Open or update a bounded GitHub PR.
9. Ensure the PR description links the repo-local task packet, review source, review absorption, changed files, validation, guardrails, non-goals, and known risks.
10. Run local Claude Code/delegated L1 review unless the PR is already a promotion-ready GitHub version.
11. Trigger GitHub/Codex review only when the PR is ready for merge/published version review or the user explicitly asks for it.
12. Absorb findings locally and push scoped fixes.
13. Controller decides promotion.

### PR Artifact Rule

For new implementation branches, prefer these repo-local artifacts:

- active review: `docs/reviews/active/review_for_<topic>_<date>.md`
- review absorption: `docs/reviews/absorbed/<topic>_review_absorption_<date>.md`
- execution packet: `tasks/codex/<topic>_execution_packet_<date>.md`

Current project compatibility note:

- Historical IKE packets and absorptions may still live under `docs/IKE_*.md`.
- Do not block an already scoped active packet only because it predates `tasks/codex/`.
- For new work, create the canonical artifact paths above unless `CURRENT_MAINLINE_CONTROL_2026-05-02.md` explicitly names an existing `docs/IKE_*.md` packet as the active contract.
- If a cloud/chat review has no repo-local artifact, create or request a repo-local review artifact before implementation.

### PR Description Minimum

Every bounded implementation PR should include:

- purpose
- source review artifact
- review absorption artifact
- execution packet
- files changed
- validation commands and results
- preserved guardrails
- non-goals
- known risks or follow-up debt

## Documentation Budget

Do not create a new durable doc unless it is one of:

- active controller surface
- task packet
- result report
- review absorption
- policy/runbook replacement

Prefer updating:

- `docs/CURRENT_OPERATIONS.md`
- `docs/CURRENT_MAINLINE_CONTROL_2026-05-02.md`
- `docs/CURRENT_ACTIVE_ARTIFACTS.md`
- `docs/CURRENT_REVIEW_QUEUE.md`

Historical docs are evidence, not first-read state.

## Stop Conditions

Stop and report if:

- active mainline cannot be named
- active task packet cannot be named
- request crosses lanes and cannot be split
- validation cannot be run
- required local review is missing for a non-promotion candidate
- GitHub/Codex review output is missing for an active promotion-ready GitHub candidate that explicitly required it
- required repo-local review, absorption, or execution packet is missing for a new implementation branch
- dirty worktree candidate exceeds one lane
- a delegate tries to change architecture or promotion authority

## Current Next Step

Current controller-owned next step:

```text
prepare flywheel_readiness scoped package boundary, then dispatch AI Entry Task Packet Composer P0
```

The copy-ready delegate packet export path, first real browser-smoke worker
result, and execution-feedback copy-ready return packet are accepted after
local review and controller absorption. Runtime operator restored API on port
8000, runtime review accepted the repair, and live task-packet preview route
validation is accepted. The chat-origin guided path UI is accepted after local
review, build, and full browser smoke. Manual candidate-selection friction is
reduced with a reviewed UI-only filter and deterministic browser smoke
coverage. The post-preview next action is explicit in the UI, and copied packet
builders are ASCII-safe after local review and browser smoke. Do not claim
production health: watchdog remains down as a non-blocking P2 runtime issue.

Runtime cleanup note: stale May 13 Next/smoke Node processes were cleaned
through a bounded runtime operator packet and absorbed by controller. Future
frontend dev/smoke servers must be explicitly stopped after validation.

Current delegated UI next step:

```text
tasks/codex/project_control_surface_p1_gemini_ui_packet_2026-05-11.md
```

Project Control Surface Anchor P0 is accepted into mainline as `/control`; P1
is now a Gemini CLI delegated UI packet and must pass local review/controller
absorption before it becomes accepted.

Current flywheel next step after AI bridge:

```text
accepted candidate_packet -> accepted copy-ready delegate packet export -> accepted smoke worker result -> accepted product-use return packet -> accepted runtime API repair -> accepted live Flywheel route validation -> accepted chat-origin guided path -> accepted manual candidate-selection filter -> accepted explicit post-preview next action -> accepted ASCII-safe copied packets -> accepted real worker execution-feedback inspect -> AI Entry Task Packet Composer P0 after dirty-tree package boundary
```

Do not start another source-intelligence quality slice until one product-use
Flywheel worker result has been consumed through execution feedback, or the
controller explicitly parks the mainline.

## Known Operations Caveat

2026-05-16: `scripts/review/run_l1_review.py` can write a complete review result
file while still marking the done JSON as `delegate_failed` if the Claude CLI
wrapper times out after output. Treat the review body as evidence only after
checking the result file, and track the wrapper timeout as harness debt rather
than product-code rejection.

2026-05-16: Claude Code diagnosed `mainline-stall-watch-local-executor` and
confirmed it was counting its own `mainline_auto_continue_result_*.md` output as
progress. The executor prompt was updated to use git-first and explicit
non-automation artifact checks only; no workspace-wide mtime scan is allowed.
