# IKE Migration Exit Criteria

This document defines the conditions under which a transitional IKE v0 layer
can be considered complete enough to advance, and the conditions required
before old MyAttention structures can stop being the source of truth.

It exists to prevent a common migration failure mode:

- APIs or schemas exist
- demo paths work
- but the system has not actually crossed a trustworthy migration boundary

IKE migration is complete only when contracts, runtime behavior, inspectability,
and operational truth all line up.

## 1. Why This Document Exists

Recent review convergence from internal voting plus external model reviews
arrived at the same conclusion:

- the current branch is a valid migration seam
- the transitional API is honest
- but the project is not yet at a full v0 proof point

That means we need explicit exit criteria so the project does not confuse:

- "schema and preview endpoints exist"

with:

- "the migration slice is truly working"

## 2. Principles

Migration exit criteria must preserve these rules:

1. No fake durability.
   - A route or object must not imply stable retrieval unless stable retrieval
     is actually supported end to end.

2. No semantic drift.
   - If object semantics or status vocabularies drift away from IKE contracts,
     the drift must be corrected immediately.

3. No invisible loops.
   - A claimed vertical slice is not complete unless the chain can be inspected
     without reading raw logs.

4. No clean-slate fantasy.
   - Existing substrates may remain in place during migration, but the system
     must make it clear what is still transitional and what has become canonical.

## 3. Exit Levels

### 3.1 Slice-Proven Exit

A migration slice is considered proven when all of the following are true:

1. The slice has explicit schemas.
2. The slice has bounded adapters/mappers.
3. The slice has automated tests for schema and route behavior.
4. The slice exposes an inspectable surface.
5. The slice uses current runtime substrates honestly, without pretending to
   have a canonical store that does not yet exist.

This is the level reached by the current IKE v0 milestone for:

- Observation
- Decision preview
- HarnessCase preview

### 3.2 Loop-Proven Exit

The first real v0 proof point is reached only when one full loop is inspectable:

`Observation -> Entity/Claim -> ResearchTask -> Experiment -> Decision -> HarnessCase`

The loop is considered proven only if:

1. It starts from a real substrate already present in the running system.
2. Each object in the chain is visible through an inspectable surface.
3. The chain is inspectable without reading raw logs.
4. The chain preserves provenance and references across the full loop.
5. At least one harness check validates that the chain is complete.

### 3.3 Source-of-Truth Exit

An old structure can stop being the source of truth only when:

1. The new IKE object contract is stable for that slice.
2. Stable identity rules are defined.
3. Deterministic reconstruction is possible.
4. Object access semantics are implemented and tested.
5. Operational workflows no longer depend on the legacy representation.

Until then, the old structure remains the source of truth and the IKE layer is
an additive migration layer.

## 4. What Does Not Count As Exit

These do not qualify as migration completion:

- preview endpoints alone
- typed IDs alone
- schema files alone
- test-only isolated router proofs
- object-shaped JSON without inspectable chain semantics

These are useful migration assets, but they are not exit points.

## 5. Current Status

Current status after the IKE v0 milestone:

- Transitional object contracts: present
- Transitional preview/inspect API: present
- Honest provisional envelope semantics: present
- Full inspectable real loop: not yet present
- Internal object access abstraction: not yet present
- Stable durable retrieval: intentionally not present

Conclusion:

- The current branch is a valid migration milestone.
- It is not yet the full v0 proof point.

## 6. Immediate Next Exit Target

The next required exit target is:

### v0.1 Loop-Proven Exit

Required outcomes:

1. One real runtime-backed loop is executed.
2. The loop is inspectable end to end.
3. The loop does not require raw log reading.
4. It uses current substrates honestly.
5. It does not introduce fake durable object retrieval.

## 7. Later Exit Target

Only after v0.1 loop proof should the project move toward:

- internal object access abstraction
- then canonical store semantics
- then stable retrieval surfaces

That sequence is mandatory.

The project must not jump directly from preview endpoints to durable `GET by id`
without passing through object access and stable identity criteria first.
