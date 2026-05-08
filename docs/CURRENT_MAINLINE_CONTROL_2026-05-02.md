# Current Mainline Control

Date: 2026-05-06

Truth status: controller-authored active control note; non-canonical promotion truth.

Operations entry:

```text
docs/CURRENT_OPERATIONS.md
```

Read `CURRENT_OPERATIONS.md` first for execution order, WIP limits, and dirty-worktree handling.

## Controller Diagnosis

The project has too many historical documents and too little visible operational anchoring. The controller recently over-narrowed the mainline to `source_intelligence_quality_resumption`; that is a support lane, not the product objective.

The corrected mainline is:

1. Build the first usable IKE evolution flywheel.
2. Make AI conversation the entry into that flywheel.
3. Make project progress, phase, capability maturity, gaps, and lane ownership visible in UI so the controller, user, and delegates keep the same target.

This note is the current control surface for those questions.

## Current Mainline Position

Current active mainline phase:

```text
flywheel_v1_ai_entry_control_surface
```

Current product objective:

```text
Build the first usable IKE evolution loop with an AI conversation entry and a visible project control surface.
```

Latest accepted support implementation:

```text
PR #2 / acf922c: GitHub signal relation hints improved source-intelligence input quality.
```

Current mainline gap:

```text
The target system is not visible enough, and the AI conversation surface is not yet connected to the inspect-only flywheel entry.
```

Required anchor:

```text
UI must show IKE's mainline, phase, core goals, current capability state, capability gaps, and multi-lane progress.
```

Capability model to show:

- information brain
- knowledge brain
- evolution brain
- world model
- thinking methods / method arsenal

Controller interpretation:

- Flywheel V1 and AI entry are the product mainline.
- Control-surface UI is not cosmetic; it is operations infrastructure.
- Source intelligence remains important, but it serves the flywheel by improving input quality and candidate-object judgment.
- More source-intelligence slices should not displace the visible anchor or flywheel closure work.

## Active Lanes

### Lane 1: Mainline Flywheel V1

Owner: controller plus delegated backend/review/test agents.

Status: active; backend inspect route chain validated on 2026-05-07.

Allowed next work:

- one bounded end-to-end flywheel vertical-slice packet
- inspect-only conversation input
- controller packet generation
- task packet preview
- worker packet bridge
- execution-feedback return
- review-gated controller decision

Hard boundaries:

- no fake autonomous execution
- no automatic promotion
- no persistence/runtime truth expansion without L3
- no delegate self-acceptance

### Lane 2: Mainline AI Conversation Entry

Owner: controller plus backend/CC delegate.

Status: active; next implementation should be a UI-only bridge from `/chat` to the existing flywheel inspect surface.

Allowed next work:

- connect the AI conversation entry to typed candidate objects and controller packets
- preserve raw conversation as non-canonical
- expose review-gated next actions
- reuse existing `conversation_runtime` and source semantics

Hard boundaries:

- no generic chat expansion
- no raw chat as truth
- no broad memory/persistence work without L3

### Lane 3: Mainline Project Control Surface

Owner: controller plus Antigravity UI delegate.

Status: delegated to Antigravity UI on branch `codex/project-control-surface-ui-20260507`.

Purpose:

- keep the mainline visible
- show three mainline tasks: flywheel, AI entry, project control surface
- show capability maturity and gaps for information brain, knowledge brain, evolution brain, world model, and thinking methods
- show active lanes, owners, PR/review gates, and blocked/next actions

Allowed work:

- `services/web/app/control/*`
- `services/web/components/control/*`
- `services/web/lib/control-surface/*`
- matching control-surface task/result/review artifacts

Hard boundaries:

- static snapshot must be explicitly labeled as static/provenance-bound evidence
- no fake live state
- no backend runtime truth changes unless a separate L3 packet authorizes them
- Antigravity output requires GitHub PR review and controller acceptance

### Lane 4: Source Intelligence Support

Owner: controller plus backend/CC delegate.

Status: support lane.

Allowed work:

- improve person/source/signal quality when it directly improves flywheel inputs
- maintain shared source semantics used by conversation runtime
- run bounded tests and local review before promotion; use GitHub/Codex only for promotion-ready GitHub versions or explicit cloud review

Not allowed:

- displace Flywheel V1 / AI entry / control surface as the top-level mainline
- continue heuristic accumulation without a visible flywheel benefit

### Lane 5: Review Gate

Owner: local reviewer / GitHub-triggered Codex review when warranted, plus local controller absorption.

Status: gate, not implementation lane.

Default shape:

```text
scoped branch
  -> validation
  -> local Claude Code/delegated L1 review
  -> local controller consumes findings
  -> scoped fix when needed
  -> controller promotion decision
```

GitHub/Codex shape:

```text
promotion-ready GitHub PR
  -> GitHub/Codex review if cloud review is required
  -> local controller consumes findings
  -> scoped fix push when needed
  -> repeat GitHub/Codex only for material promotion-surface changes
  -> controller promotion decision
```

Boundary:

- GitHub/Codex review is promotion evidence, not a default work loop.
- It is not promotion authority.
- Local Codex may fix findings but must not accept its own fix as final.
- The controller must terminate the gate when findings are absorbed, no unresolved thread remains, scope and risk did not expand, validation is recorded, and the PR is mergeable. Do not create an infinite final-review loop for low-risk doc or packet wording fixes.

### Lane 6: Dirty Worktree Governance

Owner: controller.

Status: clean as of 2026-05-06; keep it clean.

Current observed classifier result:

```text
total: 0
recommendation: clean
```

Rule:

- no broad commit or mixed PR
- every implementation goes through a lane-specific branch/PR
- any local quarantine evidence is optional and unpublished; delegates must recreate or recover bounded files through clean branch/PR work, not rely on the quarantine ref

## Layered Review Requirements

Every non-trivial task must pass layered review before promotion.

### L0: Controller Scope Review

Confirm one task, one lane, one result, risk level, allowed files, and validation.

### L1: Code/Artifact Review

Use local Claude Code/delegated L1 review for small scoped code, UI, docs, and packet changes. Use GitHub/Codex review only when the PR is a promotion-ready GitHub version, cloud evidence is required, local review is insufficient, or the user explicitly requests it. Controller fallback is allowed only for very small corrective patches with validation evidence.

### L2: Integration Review

Required for:

- flywheel/runtime route or contract changes
- AI conversation entry behavior
- UI changes that summarize project truth
- source-intelligence route/contract changes
- review automation tooling

### L3: Reinforced Governance Review

Required if a task touches:

- memory or persistence
- task orchestration or scheduler logic
- worker/harness execution contracts
- runtime truth or promotion boundaries
- permissions, deletion, or self-modification rules
- incident remediation

## Immediate Next Task

Current controller-owned task:

```text
tasks/codex/ai_conversation_entry_bridge_p0_2026-05-07.md
```

Purpose:

```text
Implement the smallest UI-only bridge that lets a chat turn enter the existing flywheel inspect workflow without making raw chat canonical truth.
```

Parallel delegated UI task:

```text
tasks/codex/project_control_surface_antigravity_brief_2026-05-06.md
```

Flywheel follow-up after the AI bridge:

```text
Run browser-level smoke for /chat -> /evolution flywheel inspect -> task preview -> execution feedback inspect.
```

The controller owns scope and acceptance for all three lanes.

## Controller Decision

Recommendation: accept_with_changes.

Reason:

- prior source-intelligence work was useful but over-narrowed as a top-level mainline
- Flywheel V1 plus AI entry are the product mainline
- control-surface UI is required to keep multi-agent work aligned
- GitHub-triggered Codex review is a promotion gate only, not the default loop for small changes
- Antigravity can implement the UI only through a bounded GitHub branch/PR

Next controller action:

1. publish the flywheel and AI-entry audit results as a scoped PR
2. implement or delegate the UI-only chat-to-flywheel bridge
3. keep Antigravity UI work on its GitHub branch/PR
4. run browser-level Flywheel V1 smoke after the bridge exists
