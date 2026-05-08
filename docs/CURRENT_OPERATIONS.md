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

## Current Mainline Pointer

Active mainline:

```text
flywheel_v1_ai_entry_control_surface
```

Current product objective:

```text
Build the first usable IKE evolution loop with an AI conversation entry and a visible project control surface.
```

Current active task packet:

```text
tasks/codex/project_control_surface_anchor_p0_2026-05-06.md
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
clean after 2026-05-06 quarantine and scoped governance restore
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
- `ui_lane`: Antigravity implementation work for the control surface or related UI
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
tasks/codex/flywheel_v1_browser_smoke_result_2026-05-08.md
```

Close the remaining real browser click smoke for the `/chat` to flywheel handoff.

Current delegated UI next step:

```text
tasks/codex/project_control_surface_antigravity_brief_2026-05-06.md
```

Project Control Surface Anchor P0 is now accepted into mainline as `/control`; future UI work should update the snapshot or add live adapters only through a new packet.

Current flywheel next step after AI bridge:

```text
manual/delegated browser click smoke for /chat -> Open in Flywheel -> /evolution prefilled form -> manual inspect
```

Do not start another source-intelligence quality slice until the browser click smoke is closed or explicitly parked by controller decision.
