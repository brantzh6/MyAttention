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

## Current Mainline Pointer

Active mainline:

```text
source_intelligence_quality_resumption
```

Current active task packet:

```text
docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_PACKET_2026-05-02.md
```

Current task result:

```text
docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_RESULT_2026-05-02.md
```

Current task state:

```text
implemented locally; validation passed; initial L1 review flagged a false-person-seed issue; fixed locally; scoped L1 re-review accepted
```

Latest accepted source-intelligence result:

```text
docs/IKE_SOURCE_INTELLIGENCE_QUALITY_RESUMPTION_IMPLEMENTATION_RESULT_2026-05-01.md
```

Current parallel UI lane:

```text
Antigravity Visual Control Surface
```

Current gate:

```text
GitHub-triggered Codex review plus local controller absorption
```

Default PR/review rule:

```text
implementation that needs GitHub visibility or cloud review must go through a bounded PR
```

Rationale:

- GitHub PRs are the stable review surface for Codex Cloud and other reviewers.
- PR-local artifacts prevent review truth from living only in chat or task links.
- Controller still owns promotion; GitHub/Codex review is evidence, not acceptance.

Current worktree state:

```text
dirty; requires scoped review prep; broad push forbidden
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
- What is the active task packet?
- Which lane does the user request touch?
- Is the worktree clean enough for direct scoped work?

If these cannot be answered in 5 minutes, stop and update `CURRENT_OPERATIONS.md` or `CURRENT_MAINLINE_CONTROL_2026-05-02.md` before coding.

### 2. Classify The Request

Every new request is classified into exactly one bucket:

- `mainline`: advances source intelligence quality
- `ui_lane`: Antigravity or `/control` visual surface work
- `review_gate`: GitHub/Codex review, finding absorption, PR readiness
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

UI work may continue independently, but it must not redefine mainline truth.

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
10. Trigger or wait for GitHub/Codex review from the PR surface.
11. Absorb findings locally and push scoped fixes.
12. Controller decides promotion.

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
- GitHub/Codex review output is missing for a promotion candidate
- required repo-local review, absorption, or execution packet is missing for a new implementation branch
- dirty worktree candidate exceeds one lane
- a delegate tries to change architecture or promotion authority

## Current Next Step

Prepare scoped GitHub/Codex L1 review for:

```text
docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_RESULT_2026-05-02.md
```

Candidate files:

- `services/api/feeds/source_contracts.py`
- `services/api/feeds/source_postprocess.py`
- `services/api/feeds/source_semantics.py`
- `services/api/routers/feeds.py`
- `services/api/tests/test_source_discovery_identity.py`
- `docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_PACKET_2026-05-02.md`
- `docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_RESULT_2026-05-02.md`

Do not include unrelated dirty worktree files.
