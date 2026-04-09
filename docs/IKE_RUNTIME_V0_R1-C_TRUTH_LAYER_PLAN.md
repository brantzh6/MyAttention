# IKE Runtime v0 R1-C Truth-Layer Integration Plan

## Purpose

`R1-B` proved one real narrow lifecycle path:

- `inbox -> ready -> active -> review_pending -> done`

The next runtime phase should not broaden into UI, scheduler, or graph memory.

It should absorb the remaining substantive hardening items from `R1-B`:

1. remove legacy executable dependence on `allow_claim=True`
2. move delegate identity verification into runtime-owned truth checks
3. convert the lifecycle-proof method into durable project/runtime rules

This is the truthful next phase for `IKE Runtime v0`.

## 1. Controller Judgment

Current judgment after `R1-B`:

- lifecycle proof is real
- review/test/evolution legs are real
- main remaining weakness is not transport anymore
- main remaining weakness is executable truth-layer hardness

This means:

- do not open `R1-D` or broader integration yet
- do not expand into runtime UI
- do not add new first-class runtime domains yet
- first absorb the truth-layer and method-upgrade items exposed by `R1-B`

## 2. Core Problems To Fix

### 2.1 Legacy `allow_claim=True` Still Exists In Executable Path

Current truthful state:

- `R1-B1` is accepted with changes
- proof path still relies on legacy `allow_claim=True`
- `ClaimContext` exists, but runtime truth still depends partly on caller
  assertion

This is acceptable for the proof milestone.
It is not acceptable as the next stable baseline.

### 2.2 Delegate Identity Verification Is Not Yet Runtime-Owned

Current truthful state:

- service/controller code still carries too much responsibility for verifying
  delegate legitimacy
- runtime kernel should own the truth rule for whether a delegate can claim or
  continue work

### 2.3 Lifecycle-Proof Method Needs Durable Promotion

`R1-B4` evolution result surfaced reusable method rules:

- narrow lifecycle proof template
- explicit scope exclusion list
- no new first-class objects
- live pytest requirement
- now/future absorption split

These should stop living only in result artifacts.

## 3. R1-C Shape

### R1-C1 Coding

Purpose:

- move `ready -> active` and adjacent claim-required transitions toward
  runtime-owned truth verification

Bounded focus:

- remove legacy dependence on `allow_claim=True` from the lifecycle proof path
- introduce/strengthen a runtime truth callback or adapter that verifies:
  - delegate identity
  - assignment/lease/task linkage
- keep existing state machine shape

Do not:

- redesign the whole task model
- add scheduler work
- add new UI/API surfaces

### R1-C2 Review

Purpose:

- verify the truth-layer hardening did not reintroduce fake claim semantics

Required focus:

- runtime-owned verification vs caller assertion
- no review-boundary regression
- no broad object expansion

### R1-C3 Testing

Purpose:

- prove the truth-layer hardening is real

Required focus:

- lifecycle path still passes
- illegal delegate claim path fails
- controller-only `review_pending -> done` still holds
- event ordering still survives

### R1-C4 Evolution

Purpose:

- absorb the method upgrades exposed by `R1-B` and `R1-C`

Required focus:

- promote narrow lifecycle-proof template into durable rule
- require explicit scope exclusion lists in future proof packets
- capture whether runtime now needs first explicit method-upgrade event support

## 4. Not Yet

`R1-C` should not include:

- benchmark/kernel integration
- procedural-memory promotion states as executable runtime object changes
- notifications
- graph memory
- broad observation/kernel integration
- new task board/UI work

Those remain later-phase items.

## 5. Success Standard

`R1-C` is successful if:

1. lifecycle proof no longer depends on executable `allow_claim=True`
2. delegate identity/claim truth is runtime-owned rather than mainly
   controller-owned
3. lifecycle proof still passes through real tests
4. method upgrades from `R1-B` are durably absorbed into project/runtime rules

## 6. Follow-On Judgment

Only after `R1-C` succeeds should the controller decide whether to open:

- `R1-D` narrow kernel integration

That later phase should connect the kernel to one narrow real path.
It should not be opened while executable truth semantics are still soft.
