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
The flywheel can now produce a copy-ready inspect-only delegate handoff packet
and a copy-ready execution-feedback return packet, with one smoke worker result
and one product-use worker result consumed through review and controller
absorption. Runtime operator repaired API startup, runtime review accepted the
repair, live task-packet preview route validation is accepted, and the
chat-origin guided path is accepted as the first visible AI-entry/Flywheel
product-use slice. Manual candidate-selection friction is reduced with a
reviewed UI-only filter and deterministic smoke coverage. The post-preview
next action is now explicit in the UI without introducing fake candidates,
automatic delegation, or promotion. The first small bounded product-use worker
packet after that gate cleaned copied packet output for cross-tool readability.
The readable copied packets have now been used to run one real delegated worker
result through execution-feedback inspect, with local L1 review and controller
absorption. The next gap is making the AI conversation entry select a useful
next bounded packet and carry it through this same reviewed loop without
automatic execution or promotion.
```

Current accepted flywheel evidence:

```text
Flywheel V1 browser smoke and loop closure summary are accepted as the working evidence baseline.
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

Status: accepted handoff-preview evidence; backend inspect route chain,
browser smoke, candidate packet preview, inspect-only handoff preview, manual
candidate filtering, post-preview next-action visibility, ASCII-safe copied
packet generation, and one real worker-result execution-feedback inspect loop
are accepted.
Current accepted slice: task-packet preview can return a controller-ready
`candidate_packet`; the manual absorption panel can filter candidate rows while
preserving original indexes for controller selection.

Allowed next work:

- one bounded AI-entry-originated flywheel vertical-slice packet
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

Status: accepted into mainline; `/chat` can hand transient inspect input to the existing flywheel inspect surface.

Current accepted slice: `/chat -> /evolution` handoff now carries transient
provenance into the Flywheel reviewer note, so typed preview/handoff can retain
chat origin without making raw chat canonical truth.

Current validation state: deterministic browser smoke now validates the
chat-originated path through typed preview and execution-feedback closure. The
preview payload preserves reviewer note provenance, carries
`explicit_non_canonical=true`, and the loop closure summary remains
inspect-only / non-canonical.

Allowed next work:

- select a small product-facing bounded delegate packet to run through the
  accepted inspect-only loop
- keep execution feedback as reviewed evidence, not automatic promotion
- preserve raw conversation as non-canonical
- expose review-gated next actions
- reuse existing `conversation_runtime` and source semantics

Hard boundaries:

- no generic chat expansion
- no raw chat as truth
- no broad memory/persistence work without L3

### Lane 3: Mainline Project Control Surface

Owner: controller plus Gemini CLI UI delegate.

Status: accepted into mainline; `/control` provides the static project control surface anchor.

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
- Gemini UI output requires local review and controller absorption; GitHub/Codex
  review is reserved for promotion-ready PR versions

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

Status: over budget as of 2026-05-18; containment accepted.

Current observed classifier result:

```text
total: 178
recommendation: requires_scoped_review_prep
largest group: flywheel_readiness
```

Rule:

- no broad commit or mixed PR
- every implementation goes through a lane-specific branch/PR
- any local quarantine evidence is optional and unpublished; delegates must recreate or recover bounded files through clean branch/PR work, not rely on the quarantine ref
- no new implementation patch starts from the shared dirty tree until the
  scoped package boundary is accepted

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
run a real delegated worker result through execution-feedback inspect
```

Purpose:

```text
The copy-ready forward and return packet path is accepted. Runtime operator
restored API readiness, live task-packet preview route validation is accepted,
the chat-origin guided path is accepted, manual candidate-selection filtering
is accepted, the post-preview next action is explicit, and copied packets are
ASCII-safe after local review and full browser smoke. The next packet should
move from inspect-only loop infrastructure toward real user-facing AI
conversation/flywheel workflow value.
```

Parallel delegated UI task:

```text
tasks/codex/project_control_surface_p1_gemini_ui_packet_2026-05-11.md
```

Flywheel follow-up after the AI bridge:

```text
chat-originated context -> candidate_packet -> filtered manual selection -> explicit post-preview next action -> ASCII-safe copy-ready delegate packet -> execution feedback inspect.
```

The controller owns scope and acceptance for all three lanes.

## Controller Decision

Recommendation: accept_with_changes.

Reason:

- prior source-intelligence work was useful but over-narrowed as a top-level mainline
- Flywheel V1 plus AI entry are the product mainline
- control-surface UI is required to keep multi-agent work aligned
- GitHub-triggered Codex review is a promotion gate only, not the default loop for small changes
- Gemini CLI is the current UI delegate for bounded local UI packets; GitHub PR
  remains the collaboration/promotion surface when the UI slice is ready to
  publish

Next controller action:

1. prepare the `flywheel_readiness` scoped package boundary to reduce dirty-tree risk
2. dispatch `AI Entry Task Packet Composer P0` only after the scoped package boundary is accepted
3. keep chat input transient and non-canonical unless a later promotion decision says otherwise
4. use local review first for the next bounded implementation; reserve GitHub/Codex review for promotion-ready PR scope
5. keep runtime operator follow-ups for Redis process accounting, standalone server smoke, and watchdog registration out of the mainline unless they block active validation
6. keep source-intelligence work as support, not mainline displacement
