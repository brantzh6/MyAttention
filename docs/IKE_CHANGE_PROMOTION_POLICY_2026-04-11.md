# IKE Change Promotion Policy

Date: 2026-04-11
Status: controller baseline

## Purpose

Define how a change moves from experiment to stable runtime without allowing
self-evolution or delegated coding to silently become production truth.

## Core Rule

No change is production truth because an agent produced it.

A change becomes promotable only after it passes the full controller chain.

## Promotion Flow

The required flow is:

1. `proposal`
2. `bounded implementation or analysis`
3. `review`
4. `validation`
5. `archive`
6. `promotion decision`
7. `release`

## Stage 1 - Proposal

Every non-trivial change must begin as one of:

- task packet
- coding brief
- review brief
- milestone plan
- bounded controller directive

Minimum required fields:

1. scope
2. files or surfaces allowed
3. constraints
4. validation target
5. stop conditions

## Stage 2 - Bounded Implementation Or Analysis

Implementation may be done by:

- Codex direct bounded patch
- Claude Code
- OpenClaw
- qoder
- another approved delegate lane

But the delegate output is still only a candidate.

Delegate outputs must remain structured:

1. summary
2. files changed
3. validation run
4. known risks
5. recommendation

## Stage 3 - Review

No delegated patch is final before controller review.

Review may be:

- controller review
- external model review
- targeted code review
- architecture review

Review output must explicitly distinguish:

1. findings
2. validation gaps
3. recommendation

## Stage 4 - Validation

Promotion requires explicit validation evidence.

Minimum acceptable validation depends on packet type, but must include some of:

- compile check
- focused tests
- integration tests
- live runtime proof
- migration check
- rollback feasibility check

Missing validation means:

- `accept_with_changes`
- or `reject`

It does not mean silent acceptance.

## Stage 5 - Archive

A change is not retained just because it was discussed in chat.

Before promotion, the project must archive the relevant change record into at
least one durable form:

- git commit
- milestone document
- review result document
- canonical runtime record

If it is not archived, the system should assume it can be lost.

## Stage 6 - Promotion Decision

Only the controller may decide:

- accept
- accept_with_changes
- reject
- defer

Delegates may recommend.
They may not self-accept.

## Stage 7 - Release

Only accepted changes may enter:

- `staging-runtime`
- or `prod-runtime`

Promotion order must be:

1. `sandbox-evolution` or `controller-dev`
2. `staging-runtime`
3. `prod-runtime`

Direct `sandbox-evolution -> prod-runtime` promotion is prohibited.

## Change Classes

### Class A - Safe Local Change

Examples:

- small bounded bug fix
- focused route extension
- narrow test addition
- documentation correction

Minimum gate:

- compile or focused validation
- controller review
- git archive

### Class B - Runtime Behavior Change

Examples:

- new runtime route
- state machine behavior change
- canonical preflight change
- controller decision boundary change

Minimum gate:

- focused tests
- controller review
- milestone/result doc
- release note

### Class C - Environment / Data / Schema / Memory Change

Examples:

- migration
- memory contract change
- knowledge-base wiring
- production config change
- release process change

Minimum gate:

- explicit rollback note
- backup readiness
- staging validation
- controller acceptance

### Class D - Self-Evolution Or Auto-Modification Rule Change

Examples:

- changing what the system may rewrite automatically
- changing what agents may mutate directly
- changing review bypass rules

Minimum gate:

- explicit controller review
- explicit risk note
- explicit rollback plan
- no direct prod landing

## Forbidden Shortcuts

The following are prohibited:

1. chat-only acceptance
2. delegate self-acceptance
3. direct experimental patch to production
4. mixing unrelated fixes into one promotion unit
5. letting self-evolution rewrite controller governance without review

## Self-Evolution Constraint

Self-evolution may produce:

1. proposal
2. candidate patch
3. validation result
4. promotion request

Self-evolution may not directly produce:

1. production truth
2. accepted release state
3. controller acceptance

## Current Controller Rule

For IKE, acceleration is allowed.

Unbounded promotion is not.

The project should optimize for:

- fast candidate generation
- strict promotion discipline

not for:

- immediate mutation of the stable system
