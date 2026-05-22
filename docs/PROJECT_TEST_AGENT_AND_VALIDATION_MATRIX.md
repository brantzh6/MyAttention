# Project Test Agent and Validation Matrix

## Purpose

This document defines the missing independent testing leg in the current
controller + delegates model.

The project already has:

- implementation delegates
- review/analysis delegates
- controller review

What it does not yet have as a first-class mechanism is:

- independent validation ownership
- explicit validation depth by task type
- a stable rule for when testing is separate from coding and review

This document fixes that gap.

## 1. First Principle

Testing is not the same as:

- coding
- review
- architecture judgment

Coding answers:

- what changed

Review answers:

- what is risky or semantically wrong

Testing answers:

- does the bounded change actually behave correctly under the required checks

These must not silently collapse into one role.

## 2. Roles

### Controller

Owns:

- required validation depth
- acceptance threshold
- conflict resolution when validation and review disagree

Does not:

- treat "delegate said tests passed" as sufficient by itself

### Coding Delegate

Owns:

- minimum local validation required by the packet
- reporting exactly what was run

Does not own:

- final validation judgment

### Review Delegate

Owns:

- semantic drift detection
- scope drift detection
- truthfulness review

Does not own:

- final execution correctness judgment

### Test Agent

Owns:

- independent validation of bounded behavior
- regression checks for recently corrected semantics
- verification that packet success criteria are actually met

Does not own:

- final architecture judgment
- final acceptance

## 3. Test Agent Categories

### Runtime Test Agent

Use for:

- state-machine packets
- lease/recovery packets
- storage boundary packets
- rebuild/recovery packets

Primary focus:

- transition correctness
- idempotency
- rebuild behavior
- recovery behavior

### Acceptance Test Agent

Use for:

- benchmark packets
- UI packets
- closure packets
- packets with explicit success criteria

Primary focus:

- task goal met or not
- visible/output behavior
- artifact truthfulness

### Regression Test Agent

Use for:

- any packet touching recently corrected semantics

Primary focus:

- confirm previously fixed drift has not reappeared

## 4. Validation Levels

### Level 0: Reported Only

Use only for:

- pure planning/docs packets
- bounded analysis packets with no runtime impact

Minimum:

- no code changed
- evidence source types stated

### Level 1: Local Bounded Validation

Use for:

- small additive code packets

Minimum:

- relevant unit tests
- import/type sanity
- exact commands reported

### Level 2: Independent Packet Validation

Use for:

- core semantics packets
- runtime packets
- trust-boundary packets
- memory acceptance packets

Minimum:

- coding delegate validation
- controller or separate test-agent validation
- negative-path check where applicable

### Level 3: Cross-Boundary Validation

Use for:

- rebuild/recovery
- closure-to-memory
- benchmark-to-decision
- state + storage + retrieval interactions

Minimum:

- end-to-end bounded scenario
- recovery or replay scenario
- explicit known limits

## 5. Validation Matrix

### Coding Packet

Required minimum:

- Level 1

Upgrade to Level 2 when:

- state semantics change
- trust boundary changes
- controller flags high semantic risk

### Runtime Kernel Packet

Required minimum:

- Level 2

Typical checks:

- schema compatibility
- transition rules
- lease expiry behavior
- rebuild/recovery path

### Benchmark Packet

Required minimum:

- Level 2

Typical checks:

- evidence source type clarity
- no fake authority
- no fake live data
- recommendation does not exceed evidence

### Memory Packet / Closure Packet

Required minimum:

- Level 2

Typical checks:

- trust boundary
- upstream linkage
- accepted vs draft recall eligibility

### UI Packet

Required minimum:

- Level 1

Upgrade to Level 2 when:

- page claims live/runtime truth
- packet changes visible benchmark or closure interpretation

## 6. Mandatory Validation Questions

Every non-trivial packet should be checked against these:

1. Did the packet change only the allowed files?
2. Did the packet preserve the current contract?
3. Did the packet reintroduce a previously corrected drift?
4. Did the packet prove the success criteria, or only compile?
5. Did the packet claim live truth without proving it?

## 7. Required Review-to-Test Escalation

Review must escalate to independent testing when it finds:

- trust-boundary ambiguity
- state-transition ambiguity
- recovery ambiguity
- durability ambiguity
- benchmark theater risk
- memory hallucination risk

Do not accept these with review alone.

## 8. Output Requirements for Test Work

Every independent test pass/fail result should include:

1. `task_id`
2. `validation_level`
3. `scenarios_run`
4. `commands_run`
5. `pass_fail`
6. `gaps_not_tested`
7. `risks_remaining`
8. `recommendation`

## 9. Current Project Upgrade Direction

Immediate gap to close:

- testing is still too implicit and packet-local

Near-term upgrade:

- make runtime, benchmark, and closure packets routinely require explicit
  independent validation

Longer-term direction:

- IKE Runtime should carry validation events and validation ownership as
  first-class task/decision context
