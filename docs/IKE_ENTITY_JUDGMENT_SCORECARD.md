# IKE Entity Judgment Scorecard

## Purpose

This scorecard is the bounded evaluation frame for deciding whether an entity is:

- `concept_defining`
- `ecosystem_relevant`
- `implementation_relevant`
- or only adjacent

It exists because current benchmark work still relies too much on proximity and
generic discovery adjacency.

## Dimensions

Each candidate entity should be judged on these dimensions.

Use explicit notes, not only a single total score.

### 1. Identity confidence

Questions:

- Do we know clearly what this entity is?
- Is it really a `person`, `organization`, `repository`, or something else?
- Is there enough direct evidence to trust that classification?

### 2. Authority confidence

Questions:

- Does this entity have an official, maintainer, or expert role?
- Is it central enough to influence the concept?
- Is its role direct or merely adjacent?

### 3. Concept-defining confidence

Questions:

- Does this entity help define what the concept is?
- Does it shape boundary or interpretation?
- Would removing it weaken our definition of the concept?

### 4. Implementation usefulness confidence

Questions:

- Does this entity contain directly inspectable technical patterns?
- Is it useful for a bounded study or prototype decision?
- Is the relevance real or only neighbor-level?

### 5. Evidence-layer quality

Primary evidence should be tagged as:

- `authoritative_official`
- `expert_maintainer`
- `implementation_repository`
- `community_discourse`
- `media_context`
- `primary_local_artifact`
- `structured_secondary_interpretation`

The quality of the top layer matters more than the number of weak layers.

### 6. Cross-reference support

Questions:

- Is the entity referenced by other strong entities?
- Does it connect cleanly into the current concept graph?
- Does it stand alone, or is it independently reinforced?

## Expected Output Form

Each evaluated entity should ideally produce:

- `entity_name`
- `entity_type`
- `identity_confidence`
- `authority_confidence`
- `concept_defining_confidence`
- `implementation_usefulness_confidence`
- `primary_evidence_layer`
- `cross_reference_support`
- `recommended_tier`
- `tier_reason`
- `missing_evidence`

## Controller Rule

The scorecard should not force every benchmark to have a `concept_defining`
entity.

It is acceptable to conclude:

- current evidence does not yet justify any `concept_defining` entity

That is better than promoting a weak adjacent object.
