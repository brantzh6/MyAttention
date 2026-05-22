# IKE Runtime v0 - Review #11 Absorption

Date: 2026-04-10
Source review:

- [D:\code\MyAttention\docs\review-for%20IKE_RUNTIME_V0_R2-I1_SINGLE_FILE_REVIEW_PACK_2026-04-10.md](/D:/code/MyAttention/docs/review-for%2520IKE_RUNTIME_V0_R2-I1_SINGLE_FILE_REVIEW_PACK_2026-04-10.md)

## Review Outcome

External review judgment:

- score: `B+`
- direction: `on_track`
- recommendation: `accept_with_changes`

## What We Absorb

### 1. Semantic correction is required

`R2-I1` should be described as:

- a live-service-adjacent **state-machine lifecycle proof**

It should **not** be overstated as:

- a DB-backed runtime lifecycle proof
- a Postgres-backed lifecycle fact path

Why:

- the current proof runs through the live canonical service
- but the proof itself uses in-memory lifecycle execution and
  `InMemoryClaimVerifier`
- therefore it proves route honesty + lifecycle semantics, not yet the full
  PG-backed truth path

### 2. Router growth should be watched

The review correctly flags that:

- [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)

is approaching a split threshold.

Current rule:

- do not split immediately just for aesthetics
- but do not add many more runtime endpoints into the same file without an
  explicit split plan

### 3. Long-running backlog debt remains real

The review correctly re-raises:

- `force=True` role restriction follow-through
- retained notes unified backlog
- second concept benchmark formal scheduling
- procedural memory formal scheduling

These are not newly created risks, but they remain active process debt.

## What We Do Not Absorb As Immediate Mainline Change

We do **not** automatically make the next step:

- broad DB-backed lifecycle platform work

But we do absorb the narrower next question:

- whether to prove one PG-backed lifecycle path above the current proof route

## Recommended Next Narrow Direction

Preferred next runtime direction:

- `R2-I5 DB-backed lifecycle proof`

Goal:

- prove one lifecycle path through real PG-backed runtime truth
- keep scope narrow
- do not widen into general task CRUD or scheduler semantics

Fallback acceptable direction if mainline capacity is constrained:

- settle the carried debt items before opening `R2-I5`

## Controller Judgment

Review #11 is materially useful and should be treated as absorbed.
