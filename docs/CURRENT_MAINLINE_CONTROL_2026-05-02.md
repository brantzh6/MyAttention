# Current Mainline Control

Date: 2026-05-02

Truth status: controller-authored active control note; non-canonical promotion truth.

Operations entry:

```text
docs/CURRENT_OPERATIONS.md
```

Read `CURRENT_OPERATIONS.md` first for execution order, WIP limits, and dirty worktree handling. Use this file for current lane state and mainline pointer details.

## Controller Diagnosis

The project has drifted into too many simultaneously visible artifacts. The immediate problem is not lack of work; it is loss of a single controller-facing answer to:

- where the mainline is now
- which lane owns each active thread
- what review gate is required before promotion
- how to prevent the dirty worktree from blocking scoped progress

This note is the current control surface for those questions.

## Current Mainline Position

Mainline priority remains:

1. Improve source intelligence quality.
2. Make active work surfaces understandable.
3. Move evolution away from watchdog/rule checks toward better reasoning.
4. Reduce token pressure through controlled delegation.

Current active mainline phase:

```text
source_intelligence_quality_resumption
```

Latest accepted mainline implementation result:

```text
docs/IKE_SOURCE_INTELLIGENCE_QUALITY_RESUMPTION_IMPLEMENTATION_RESULT_2026-05-01.md
```

Current pending mainline result:

```text
docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_RESULT_2026-05-02.md
```

Pending state:

```text
implemented locally; target tests passed; initial L1 review flagged a false-person-seed issue; fixed locally; scoped L1 re-review accepted; controller L2 absorption recorded
```

Accepted change:

- GitHub issue and discussion identity recognition now applies across all source-discovery focuses.

Controller interpretation:

- This is accepted as a bounded source-intelligence quality slice.
- It does not close source intelligence quality as a mainline.
- The next mainline task must be another bounded source-intelligence quality packet, not a UI task, not review automation, and not broad cleanup.

## Active Lanes

### Lane 1: Mainline Source Intelligence

Owner: controller plus delegated coding/review/test agents.

Status: active.

Allowed next work:

- one bounded source-intelligence quality packet
- narrow allowed files
- explicit validation command
- GitHub/Codex review after push

Do not mix:

- `/control` UI work
- Antigravity visual work
- review automation implementation
- archive/index cleanup
- flywheel runtime broadening

### Lane 2: GitHub/Codex Review Gate

Owner: GitHub-triggered Codex review plus local controller absorption.

Status: gate, not implementation lane.

Required shape:

```text
local Codex implementation
  -> scoped branch / PR
  -> GitHub-triggered Codex review
  -> local Codex consumes findings
  -> local fix push
  -> repeated review until no actionable findings
  -> controller promotion decision
```

PR policy:

- any implementation intended for GitHub/Codex review must use a bounded PR
- PR descriptions must be reviewable from GitHub alone
- source review, review absorption, and execution packet must be committed or explicitly linked
- for new implementation branches, prefer `docs/reviews/active/`, `docs/reviews/absorbed/`, and `tasks/codex/`
- existing `docs/IKE_*.md` packets remain valid only when this control note or `CURRENT_OPERATIONS.md` names them as the active contract

Boundary:

- GitHub/Codex review is evidence.
- It is not promotion authority.
- Local Codex may fix findings but must not accept its own fix as final.

### Lane 3: Antigravity Visual Control Surface

Owner: Antigravity UI delegate.

Status: independent UI lane.

Allowed work:

- `services/web/app/control/*`
- `services/web/components/control/*`
- `services/web/lib/control-surface/*`
- matching Visual Control Surface packet/result docs

Hard boundaries:

- no backend runtime truth changes
- no scheduler/persistence changes
- no promotion semantics
- no fake live state
- static dashboard must remain labeled as static/provenance-bound evidence

Antigravity output is not accepted until controller review and validation are recorded.

### Lane 4: Dirty Worktree Governance

Owner: controller.

Status: active blocker for broad push; not allowed to consume the mainline by default.

Current observed classifier result:

```text
total: 222
groups_with_entries: 9
recommendation: requires_scoped_review_prep
```

This means broad push is not allowed. It does not mean mainline must stop.

## Dirty Worktree Handling Plan

Use a lane-preserving plan instead of trying to clean everything at once.

### Step 1: Freeze Broad Pushes

No broad commit, broad branch push, or mixed PR from the current dirty worktree.

Allowed:

- read-only classification
- docs-only controller notes
- scoped branch prep
- lane-specific task packets

### Step 2: Pick One Promotion Candidate At A Time

A promotion candidate must fit one lane:

- mainline source intelligence
- visual control surface
- review automation
- governance cleanup
- flywheel readiness

If a candidate needs files from multiple lanes, split it.

### Step 3: Use Scoped Prep Before PR

Before any PR:

1. run `python scripts/governance/classify_worktree.py --cwd D:/code/MyAttention`
2. list the candidate files
3. verify they stay inside one lane
4. create or switch to a scoped branch
5. stage only the candidate files
6. run lane validation
7. push PR for GitHub/Codex review

### Step 4: Reduce The Worktree By Accepted Groups

Reduction order:

1. governance docs that define the active state
2. source-intelligence mainline slice
3. visual control surface UI lane
4. review automation lane
5. remaining flywheel/evolution docs and code
6. archive/index review artifacts

Reason:

- governance docs restore orientation
- mainline stays moving
- UI remains independent
- lower-priority historical artifacts do not block the next mainline packet

### Step 5: Stop Conditions

Stop and report instead of pushing if:

- candidate files cross more than one lane
- validation cannot be run
- GitHub review output is unavailable
- the PR contains stale historical artifacts not needed for the candidate
- a UI task implies backend runtime truth
- a source-intelligence task implies scheduler/persistence changes

## Layered Review Requirements

Every non-trivial task must pass layered review before promotion.

### L0: Controller Scope Review

Purpose:

- confirm one task, one lane, one result
- confirm risk level
- confirm allowed files and validation

Required before:

- delegation
- local implementation
- PR creation

Failure result:

- reject or rewrite packet

### L1: Code/Artifact Review

Purpose:

- inspect the actual diff or result artifact
- find correctness bugs, contract drift, fake truth, missing tests

Acceptable reviewers:

- GitHub/Codex review for PR diffs
- delegated L1 reviewer for local artifacts
- controller fallback only for small corrective patches

Failure result:

- accept_with_changes or reject

### L2: Integration Review

Purpose:

- confirm the slice works with neighboring contracts
- confirm validation evidence is enough
- confirm no lane boundary was crossed

Required for:

- source-intelligence route/contract changes
- flywheel/runtime changes
- review automation tooling
- UI changes that summarize project truth

Failure result:

- do not promote; create a bounded fix packet

### L3: Reinforced Governance Review

Required if task touches:

- memory or persistence
- task orchestration or scheduler logic
- worker/harness execution contracts
- runtime truth or promotion boundaries
- permissions, deletion, or self-modification rules
- incident remediation

L3 requires:

- explicit design packet
- design review
- implementation review
- test validation
- controller promotion decision

## Immediate Next Task

Current task is:

```text
docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_PACKET_2026-05-02.md
```

Purpose:

- add deterministic relation hints for GitHub issue/discussion/pull signal objects so they stay connected to repository and owner context.

Packet must include:

- one quality problem
- one expected behavioral improvement
- allowed files
- excluded files
- validation commands
- stop conditions
- GitHub/Codex review expectation

Implementation has been completed locally. Do not promote before scoped GitHub/Codex L1 review and controller L2 absorption.

## Controller Decision

Recommendation: accept_with_changes.

Reason:

- mainline direction is correct
- GitHub-triggered Codex review is the right gate
- Antigravity can run independently as UI delegate
- current dirty worktree is over budget and must be handled by lane-specific scoped promotion
- the missing piece is a single active controller surface plus a next mainline packet

Next controller action:

1. prepare a scoped PR/review candidate for `docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_RESULT_2026-05-02.md`
2. keep Antigravity UI independent
3. use scoped PR plus GitHub/Codex review for the next promoted code slice
