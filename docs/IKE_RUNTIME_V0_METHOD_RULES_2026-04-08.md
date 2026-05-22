# IKE Runtime v0 Method Rules

## Purpose

This file records runtime-specific method rules that have become durable enough
to guide future controller judgment.

These are not generic engineering slogans.
They are runtime-v0 operational rules earned through recent phases.

## Rule 1. Repeated Targeted Green Runs Can Close A Narrow Stability Phase

This rule was established by:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J_RESULT_MILESTONE_2026-04-08.md)

Meaning:

- for a narrow DB-backed runtime stability question,
- repeated targeted green runs,
- together with explicit distinction between historical transient issues and
  current reproducibility,
- are sufficient closure evidence even when no new coding patch is justified

Implications:

1. `no patch needed` is an acceptable outcome
2. historical transient failures alone do not justify speculative fixes
3. this rule applies to narrow targeted stability slices, not to arbitrary
   broader integration claims

## Rule 2. Materially Complete Is Not Fully Independently Proven

Meaning:

- a phase may be materially complete while still containing mixed delegated and
  controller evidence
- phase closure must keep that distinction explicit

Implications:

1. do not silently upgrade mixed-evidence closure into fully delegated proof
2. preserve fallback vs delegated evidence in result docs
3. broader integration gates must account for remaining mixed-evidence areas

## Rule 3. Read-Path And Write-Path Trust Semantics Must Stay Distinct

Meaning:

- trusted packet visibility on read paths is not automatically the same thing
  as write-path acceptance or trusted promotion semantics

Implications:

1. current helper/read surfaces should stay relevance-aware
2. future broader read surfaces must preserve the same distinction explicitly
3. no helper-level alignment should be used as a pretext for uncontrolled
   platform widening

## Rule 4. The Canonical Lifecycle Path Is Proven And Durable

This rule was established by:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md)

The lifecycle proof validates:

- `inbox -> ready -> active -> review_pending -> done`
- every transition in this path is structurally valid
- every actor in this path is permission-checked

Implications:

1. this path is now the v0 baseline, not a hypothetical design
2. no future phase should silently add shortcut transitions around this path
3. any extension must preserve the same permission/claim/event structure

## Rule 5. Delegate Claims Must Use Runtime-Owned ClaimContext

This rule was established by:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md)

The proof demonstrates:

- `ready -> active` transition requires `ClaimContext`
- `ClaimContext` is backed by runtime-verified lease
- `InMemoryClaimVerifier` provides the verification interface

Implications:

1. no delegate may claim a task without lease-backed verification
2. `ClaimVerifier` interface is now the required runtime boundary
3. future Postgres-backed verifier must preserve the same interface semantics

## Rule 6. WorkContext Is Derivative, Never A Second Truth Source

This rule was established by:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md)

The proof demonstrates:

- `derive_work_context_from_proof()` builds context from canonical state
- `WorkContext` reflects current task/project state, not independent truth
- context metadata includes `reconstructed_from: "canonical_state"`

Implications:

1. `WorkContext` should never be used as an authoritative state source
2. any future helper that reads context must treat it as a snapshot, not truth
3. reconstruction must always derive from runtime-owned canonical state

## Rule 7. Memory Packets Require Upstream Task Linkage Before Trust

This rule was established by:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md)

The proof demonstrates:

- `create_lifecycle_memory_packet()` requires `upstream_task_id`
- trusted packet status requires upstream linkage
- packets without upstream linkage remain untrusted

Implications:

1. no memory packet may become trusted without explicit upstream tie
2. this pattern must be preserved for kernel-to-benchmark bridge
3. future broader packet surfaces must preserve this linkage requirement

## Rule 8. Lease Lifecycle Is Phase-Aligned

This rule was established by:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md)

The proof demonstrates:

- lease is claimed at `ready -> active` transition
- lease is released at `active -> review_pending` submission
- lease events are auditable alongside state events

Implications:

1. lease lifecycle must stay aligned with lifecycle phases
2. lease release at review submission is now explicit, not optional
3. future lease renewal/heartbeat must preserve this phase alignment
