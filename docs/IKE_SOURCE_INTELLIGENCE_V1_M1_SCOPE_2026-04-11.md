# IKE Source Intelligence V1 M1 Scope

Date: 2026-04-11
Status: controller M1 scope

## M1 Name

`Topic -> Candidate Source Intelligence Inspect`

## M1 Goal

Implement one narrow backend capability that accepts a topic-oriented request
and returns a structured candidate source/object result set with bounded V1
classification and strategy hints.

## M1 User Value

This first slice should already improve:

- source discovery quality
- person/object discovery quality
- source-plan preparation quality

without pretending the system already has:

- full source lifecycle automation
- full source-plan truth management
- production-grade discovery reliability

## Input Shape

Required:

- `topic`

Optional:

- `task_intent`
- `interest_bias`
- `limit`

Recommended `interest_bias` values:

- `authority`
- `frontier`
- `community`
- `method`

## Output Shape

Top-level fields:

- `topic`
- `task_intent`
- `interest_bias`
- `candidates`
- `notes`
- `truth_boundary`

Each candidate should include:

- `object_name`
- `object_type`
- `source_nature`
- `temperature`
- `recommended_mode`
- `recommended_execution_strategy`
- `why_relevant`
- `confidence_note`

Optional candidate enrichments:

- `canonical_ref`
- `candidate_endpoints`
- `signals`

## Preferred Technical Shape

Preferred first landing:

1. one narrow helper module
2. one request/response model
3. one inspect-style API route
4. focused helper and router tests

## Explicit M1 Non-Goals

- no full source database schema rollout
- no automatic promote/demote/retire loop
- no broad collector integration
- no UI management console
- no claim that the result is canonical source truth
- no attempt to solve all topic taxonomies at once

## Acceptance Boundary

M1 is complete if all are true:

1. a topic-driven request can be submitted
2. the result returns multiple structured candidates
3. each candidate carries bounded V1 classification
4. strategy recommendation is explicit
5. truth-boundary language is explicit
6. focused tests exist
7. the patch does not broaden into fetcher rewrite or source-plan governance

## Recommendation

`accept`

This is the right first coding slice for `Source Intelligence V1`.
