# IKE Runtime v0 R1-I Operational Guardrails Plan

## Goal

Convert the narrow correctness gaps exposed by independently recovered review
and testing lanes into explicit runtime guardrails.

## Scope

`R1-I` stays inside the existing runtime helper layer.

Primary targets:

1. `align_project_current_work_context(...)`
2. `get_project_current_work_context(...)`
3. `promote_reviewed_memory_packet(...)`
4. trusted upstream verification helpers used by closure/recall

## Required Hardening

### 1. Archived-context rejection

The explicit `work_context_id` path must not align a project pointer to an
archived or otherwise non-active `RuntimeWorkContext`.

### 2. No-active-context handling

Project-pointer alignment and project current-work read helpers should fail
through explicit runtime-domain behavior rather than leaking raw ORM/lookup
errors.

### 3. Upstream state relevance

Where runtime trust currently verifies upstream existence only, tighten the
minimum relevance checks that are necessary for trusted closure/memory paths.

### 4. Keep truth boundaries unchanged

Do not:

- add new runtime tables
- introduce a second truth source
- broaden into UI/API rollout

## Expected Deliverables

- one narrow coding packet
- one narrow review packet
- one narrow testing packet
- one narrow evolution packet

## Acceptance Standard

`R1-I` is acceptable only if:

- explicit stale-pointer alignment is prevented
- expected error paths become explicit and bounded
- trust checks become stricter without widening platform semantics
- combined runtime truth-adjacent validation stays green
