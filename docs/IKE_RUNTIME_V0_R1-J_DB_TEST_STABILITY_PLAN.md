# IKE Runtime v0 R1-J DB-backed Runtime Test Stability Hardening Plan

## Goal

Improve the repeatability of DB-backed runtime validation without changing the
runtime truth model.

## Scope

`R1-J` stays inside:

- runtime pytest fixture support
- DB-backed runtime test setup/cleanup
- narrow test-support helpers
- validation guidance and evidence recording

Primary targets:

1. `services/api/tests/conftest.py`
2. DB-backed runtime suites that touch:
   - `runtime_projects`
   - `runtime_work_contexts`
   - `runtime_memory_packets`
   - `runtime_tasks`
3. controller validation instructions for repeatable DB-backed proof

## Required Hardening

### 1. Deterministic fixture isolation

DB-backed runtime suites should not depend on cross-test ordering or leftover
rows from prior slices.

### 2. FK-safe setup ordering

Fixtures and test helpers must create parent runtime objects before child
objects consistently.

### 3. Repeatable combined-suite proof

The main truth-adjacent DB-backed combined slices should be able to pass
without controller relying on "rerun and it went green" as the proof method.

### 4. No semantic widening

Do not:

- change runtime state semantics
- introduce new truth objects
- widen platform read/write surfaces

## Expected Deliverables

- one narrow coding packet
- one narrow review packet
- one narrow testing packet
- one narrow evolution packet

## Acceptance Standard

`R1-J` is acceptable only if:

- DB-backed runtime suites are more deterministic than before
- controller can separate real semantic regressions from fixture instability
- combined runtime DB-backed validation no longer depends on transient reruns
- runtime truth semantics remain unchanged
