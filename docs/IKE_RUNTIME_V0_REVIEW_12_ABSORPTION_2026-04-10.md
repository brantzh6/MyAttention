# IKE Runtime v0 - Review #12 Absorption

Date: 2026-04-10
Source reviews:

- [D:\code\MyAttention\docs\review-for%20IKE_RUNTIME_V0_R2-I12_FAILURE_REVIEW_PACK_2026-04-10.md](/D:/code/MyAttention/docs/review-for%2520IKE_RUNTIME_V0_R2-I12_FAILURE_REVIEW_PACK_2026-04-10.md)

## Review Outcome

External review convergence:

- direction: `on_track`
- shared recommendation: `accept_with_changes`
- quality signal:
  - Claude: `A-`
  - ChatGPT: materially useful, `accept_with_changes`
  - Gemini: materially useful, `accept_with_changes`

## Shared Findings We Absorb

### 1. Failure-path honesty improvement is real

The reviews correctly converge on the same core judgment:

- `R2-I10/R2-I11` is a meaningful quality improvement
- the helper no longer over-trusts rollback-expired ORM state on failure
- the route surface now truthfully exposes durable partial failure facts

This should be treated as a real strengthening of the runtime truth boundary,
not as cosmetic cleanup.

### 2. The `task.__dict__` fallback needs explicit explanation

The reviews correctly flag the fallback access pattern:

- [D:\code\MyAttention\services\api\runtime\db_backed_lifecycle_proof.py](/D:/code/MyAttention/services/api/runtime/db_backed_lifecycle_proof.py)

Using `task.__dict__.get("status", ...)` is technically justified here because:

- rollback can leave ORM attribute access in an expired or detached state
- the fallback is only meant to produce a best-effort failure report seed
- durable truth is still re-read from Postgres immediately afterward when
  possible

This concern has already been absorbed as a code comment, and should be treated
as settled for this packet unless later code changes make the comment stale.

### 3. Repeated and overlapping proof claims must remain bounded

The reviews correctly reinforce a boundary that we should keep explicit:

- repeated-run isolation proof is useful
- overlapping-run isolation proof is useful
- neither result should be overread as a broad scheduler or production
  concurrency guarantee

Current packet wording already keeps this bounded, and that honesty boundary
should remain preserved in later docs.

## Findings We Record But Do Not Turn Into Immediate Packet Changes

### 1. Router split pressure remains active

The reviews continue to flag growth in:

- [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)

We absorb this as an active architecture watch item, not as a forced split in
the middle of the current failure-honesty packet.

### 2. Process debt is now explicit, not forgotten

The reviews correctly re-raise:

- `force=True` role restriction follow-through
- retained notes unified backlog
- second concept benchmark formal scheduling
- procedural memory formal scheduling

These are not part of the narrow runtime patch itself, but they must remain
durably visible. They should not keep reappearing only in transient chat.

### 3. Review-pack naming hygiene should be cleaner

One review correctly noted that current packet naming can be confusing:

- the review pack filename is `R2-I12`
- the code packet being reviewed is the `R2-I10/R2-I11` failure-honesty work

We do not need to rename the current artifact retroactively, but future review
packs should state the relationship more explicitly.

## Controller Absorption Decision

Absorb now:

- treat `R2-I10/R2-I11` as a real failure-honesty milestone
- keep the helper/route semantics exactly bounded as currently documented
- treat the comment clarification on failure fallback as the immediate code
  follow-through requested by review

Do not absorb as current claim:

- broad task-platform durability
- detached supervision guarantees
- live service recovery orchestration
- generalized concurrency guarantees

## Recommended Next Narrow Direction

Preferred immediate next step after this absorption:

- settle one narrow post-review packet above `R2-I11`
- either:
  - record a compact controller-facing phase judgment for the failure-honesty
    lane, or
  - open the next bounded runtime edge without widening into supervision or
    scheduler semantics

Parallel non-runtime process debt should be handled durably in backlog/index
artifacts, not left in chat memory.

## Controller Judgment

Review #12 is materially useful and is now absorbed.
