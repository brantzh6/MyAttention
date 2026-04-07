# IKE Claude Code B3 Prototype Decision

## Purpose

This document records the controller decision after reviewing the `B3`
procedural-memory prototype plan.

It defines what enters the first IKE prototype and what stays out.

## Source Inputs

Reviewed inputs:

- `D:\code\MyAttention\docs\IKE_CLAUDE_CODE_B3_PROCEDURAL_MEMORY_PROTOTYPE_PLAN.md`
- `D:\code\MyAttention\.runtime\delegation\results\ike-claude-code-b3-procedural-memory-plan-kimi.json`

## Controller Decision

Recommendation:

- `accept_with_changes`

Reason:

- the overall direction is correct
- the proposed scope is still too wide if taken literally
- IKE should start with a narrower prototype than the delegated plan suggests

## Accepted Trigger Order

### Primary trigger

- `task_closure`

Why:

- clearest completion boundary
- best match for extracting durable procedural lessons
- least likely to capture mid-stream noise

### Deferred triggers

Do not include in first prototype:

- `decision_handoff`
- `study_result`

Why:

- both are valuable later
- both are more likely to create premature or overlapping captures in v1

## Accepted Initial Taxonomy

First prototype should support only:

- `procedure`

Do not include initially:

- `source_judgment`
- `user_preference`
- broad `feedback`

Why:

- these are all useful categories
- but the first prototype needs one clean test:
  - can IKE extract durable procedural lessons from bounded task completion?

If that test fails, a broader taxonomy only increases noise.

## Accepted Memory Shape

The first prototype should use a minimal structured record:

- `memory_type`
- `title`
- `lesson`
- `why_it_mattered`
- `how_to_apply`
- `confidence`
- `source_artifact_ref`
- `created_from`
- `created_at`

Optional later:

- `applicability_scope`

## Storage Decision

The first prototype should remain file-based and local.

Why:

- lowest implementation risk
- easiest to inspect
- easiest to delete or reset
- consistent with the bounded nature of the prototype

But:

- do not copy Claude Code's full filesystem memory system wholesale
- do not introduce a full `MEMORY.md` index in the first prototype

First version should prefer:

- flat procedure records
- one directory
- human-inspectable format

## Retrieval Decision

The first prototype should not implement full relevance-based recall yet.

Why:

- retrieval is important
- but extraction usefulness must be validated first

So first prototype should focus on:

- writing good procedure records
- loading them only in a bounded inspection/testing path

Not yet:

- injecting them into broad active context automatically

## What Must Remain Derivable

Do not store as memory:

- raw source content
- entity ranking outputs
- task plans
- current attention state
- file paths / code facts / repository structure
- generic benchmark summaries

## Prototype Success Criteria

The first procedural-memory prototype succeeds if:

1. it captures `procedure` records only at `task_closure`
2. each record is inspectable and obviously derived from a bounded task
3. records contain durable lessons rather than summaries
4. the first 3 to 5 captured records appear useful on review

## Prototype Failure Criteria

The first procedural-memory prototype fails if:

- it behaves like automatic note spam
- it stores derivable content
- it captures ephemeral task chatter instead of durable procedure
- it requires heavy retrieval logic just to look useful

## Next Packet

Next packet:

- `IKE procedural memory prototype implementation`

Scope:

- minimal `procedure` record model
- trigger only at `task_closure`
- file-based local persistence
- no auto-injection into general context
