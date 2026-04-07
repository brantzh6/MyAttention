# IKE Entity Judgment Strengthening Plan

## Purpose

This plan addresses the most important current quality weakness:

- critical entity judgment is still not reliable enough

The current benchmark shape is useful, but nearby or ecosystem-adjacent objects
are still too easily mistaken for concept-defining entities.

This is now a mainline quality problem, not a side issue.

## Why This Matters

Weak entity judgment pollutes the whole chain:

1. Information Brain picks the wrong objects
2. Knowledge Brain builds concept summaries on weak representatives
3. Evolution Brain escalates the wrong study packet
4. Closure and procedural-memory candidates become less trustworthy

Improving this layer is upstream work for all later benchmark and memory quality.

## Goal

Strengthen entity judgment so benchmark conclusions are based on:

- verified identity
- authority/role evidence
- evidence-layer quality
- cross-reference support
- concept-defining reasons

and not mainly on:

- search adjacency
- keyword overlap
- simple neighborhood relevance

## Main Questions

For each candidate entity, the system should increasingly answer:

1. Who or what is this object?
2. What role does it have in this concept space?
3. Is it:
   - concept-defining
   - ecosystem-relevant
   - implementation-relevant
   - merely adjacent
4. What evidence justifies that classification?
5. What authority basis supports that judgment?

## Required Method Upgrade

### 1. Identity verification

Every important entity should increasingly carry identity evidence such as:

- maintainer / author / contributor role
- official organization affiliation
- repository ownership and activity
- expert / researcher / practitioner role

### 2. Authority verification

The system should increasingly distinguish:

- authoritative official
- expert maintainer
- implementation repository
- community discourse
- media context

No single layer should dominate by default.

### 3. Tier reason

Each tiered entity should ideally carry:

- tier
- tier reason
- evidence type
- authority basis

This should make the classification auditable.

### 4. Cross-reference graph

Entity judgment should increasingly use:

- who references whom
- which repo is maintained by whom
- which docs cite which concepts
- which community threads connect to which artifacts

This is especially important for new or emerging concepts.

### 5. Primary artifact preference

When available, judgment should prefer:

- primary technical artifacts
- official docs
- maintainer-authored material

over:

- generic summaries
- secondary commentary
- nearby but weakly related objects

## Immediate Scope

Apply this first to:

- `harness`

Do not generalize too early.
First prove that entity judgment can improve on one benchmark path.

## Expected Outputs

The next bounded work should improve these benchmark elements:

1. `concept_defining` entries
   - either establish one with strong reasons
   - or explicitly conclude that none exists yet in the current evidence pool

2. `ecosystem_relevant` entries
   - separate genuinely relevant ecosystem objects from weak adjacency

3. `implementation_relevant` entries
   - justify why an object is directly useful for IKE implementation or study

4. entity-facing evidence notes
   - enough to survive review

## Success Condition

This plan succeeds when the benchmark can explain not only:

- which entities were selected

but also:

- why these entities deserve their tier
- why nearby alternatives were not selected

## Failure Condition

This plan fails if the next round still produces:

- adjacent-object summaries
- weak concept-defining tiers
- keyword-based justifications with little authority grounding
