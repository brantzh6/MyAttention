# IKE Review Cadence And Automation Policy 2026-04-29

## Purpose

This policy corrects the current review drag.

The project should keep SDLC discipline, but day-to-day development should not require frequent manual external review. External cross-model review is reserved for true phase or risk gates.

## Core Change

Move from:

- frequent manual external review packets

To:

- daily SDLC review through delegated worker/reviewer lanes
- automated/CLI model review where available
- Codex review at GitHub PR boundaries
- manual cross-model review only at critical gates

## Review Levels

### L0 Controller Self-Check

Used for:

- trivial documentation updates
- no behavior change
- no promotion decision

Required:

- controller notes
- changed files
- validation if applicable

Not enough for:

- code behavior changes
- route/schema changes
- role/identity/scoring semantics

### L1 Delegated Daily Review

Default for normal implementation.

Primary lanes:

- code review:
  - `claude-worker + kimi-k2.5`
  - `claude-worker + glm-5.1`
  - `claude-worker + qwen3.6-plus`
- test/validation:
  - `claude-worker + glm-5`
  - `claude-worker + qwen3.6-plus` for frontend/UI

Required:

- delegated code review result
- validation command
- controller acceptance decision

Use for:

- bounded code patches
- UI implementation
- negative-boundary fixes
- helper extraction regularization after design acceptance

### L2 PR / Codex Review

Default for stage-level integration.

Trigger:

- branch ready for GitHub push / draft PR
- grouped milestone implementation
- broader diff promotion

Reviewer:

- Codex PR review on GitHub
- optional delegated local review before push

Required:

- scoped diff
- PR summary
- validation evidence
- known risks
- Codex review findings resolved or explicitly accepted

### L3 Manual Cross-Model Review

Reserved for critical gates.

Reviewers:

- Claude
- Gemini
- ChatGPT
- optionally Kimi / GLM / Qwen for role-specific review

Trigger only when:

- phase design changes
- architecture boundary changes
- route/schema/public contract changes
- identity resolution or role-strength semantics change
- persistence, scheduler, runtime truth, permissions, deletion, or self-modification changes
- promotion decision for a major milestone
- multiple L1/L2 reviewers disagree materially

Do not trigger for:

- every small implementation packet
- simple UI static surfaces
- negative-boundary guard additions
- doc-only progress records

## Model Routing

### Claude

Best for:

- architecture sanity
- implementation code review
- ambiguity and requirement drift
- long-form design critique

Suggested access:

- Qoder
- Gemini CLI wrapper if available

### Gemini

Best for:

- independent design critique
- broad system consistency review
- visual/product critique

Suggested access:

- Gemini CLI

### ChatGPT / Codex

Best for:

- controller synthesis
- PR review
- code-level reasoning
- SDLC enforcement
- final acceptance judgment

Suggested access:

- current Codex session
- GitHub PR review
- ChatGPT web only when needed for manual L3

### Kimi / GLM / Qwen

Best for:

- Kimi: strict code review and finding discovery
- GLM: implementation and validation reasoning
- Qwen: frontend/UI and multimodal/product review

Use through:

- `claude-worker`
- `openclaw`
- available local/CLI model routing

## Automation Target

Short term:

- keep review packets file-based and canonical
- make L1 review the default for implementation
- use L3 manual review only for phase/risk gates

Medium term:

- create scripts that can call:
  - Qoder/Claude review
  - Gemini CLI review
  - Codex/GitHub PR review
- collect all reviewer outputs into `docs/reviews/active/*`
- auto-generate an absorption checklist

Long term:

- a review orchestrator route or local command:

```text
ike review run --level L1 --target <packet-or-diff>
ike review run --level L3 --target <phase-design>
ike review absorb --review <review-file>
```

## Updated SDLC Cadence

For normal work:

1. Design
2. Delegated design/code review
3. Delegated implementation
4. Delegated code review
5. Controller validation
6. Controller acceptance
7. PR/Codex review at grouped milestone

For high-risk work:

1. Design
2. L3 manual cross-model review
3. Bounded implementation
4. L1 delegated code review
5. validation
6. L2 PR/Codex review
7. controller promotion decision

## Review Artifact Rules

Canonical review identity remains required:

- one local review request
- one external/manual review file when L3 is triggered
- one review absorption file

But for L1:

- no zip required
- no manual external packet required
- reviewer outputs can be pasted directly into the active review file or returned by delegate

For L2:

- GitHub PR is the review package
- Codex review comments are the review findings

For L3:

- keep the user-approved format:
  - local review request
  - external zip pack with no more than 10 entries
  - feedback/writeback file

## Controller Judgment

Recommendation: adopt immediately.

This policy preserves governance while removing unnecessary manual review drag. It also matches the user's requested model:

- daily work: SDLC + delegated model review
- milestone work: GitHub + Codex review
- critical gates: manual Claude/Gemini/ChatGPT review
