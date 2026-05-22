# IKE Second Benchmark Selection Plan

## Purpose

The current benchmark progression has been proven mainly on one visible case:

- `harness`

That is useful, but it introduces method-generalization risk.

The next benchmark should test whether the same `B1 -> B2 -> B3 -> closure`
path works on a second concept with different semantics.

## Why This Exists

Current risk:

- one benchmark may prove a local pattern
- it does not yet prove that the method generalizes

This plan exists to avoid overfitting the whole benchmark method to one topic.

## Selection Rule

The second benchmark should not be too similar to `harness`.

It should be:

- relevant to IKE
- meaningfully different in semantic shape
- likely to reveal whether entity judgment and concept deepening really work

## Good Candidate Properties

Prefer a concept that is at least one of:

- more ambiguous than `harness`
- more contested in meaning
- less repository-centered
- more method-like than tool-like
- more likely to expose weak authority judgment

## Candidate Types To Prefer

Examples of good benchmark classes:

- a method concept
- a coordination concept
- a memory concept
- a self-improvement concept
- an evaluation concept that is broader or more contested than `harness`

## Candidate Types To Avoid For Now

Avoid a second benchmark that is:

- too close to `harness`
- just another OpenClaw-adjacent repo pattern
- too easy to rank by GitHub activity alone
- mostly a news/media trend

## What The Second Benchmark Should Test

The second benchmark should challenge:

1. entity judgment
2. concept boundary quality
3. mechanism-to-gap mapping
4. recommendation-level discipline
5. closure quality

## Minimum Requirement

The second benchmark does not need a full UI first.

It only needs to prove:

- the same method works beyond the first case
- or reveal exactly where it breaks

## Success Condition

The second benchmark succeeds if it can reach at least:

- `B2` with stronger entity reasons than before

and ideally:

- `B3` with a credible concept boundary and applicability judgment

## Failure Condition

The second benchmark fails if it shows:

- the method only works on narrow repo-heavy cases
- entity judgment collapses under a different concept shape
- recommendation quality becomes obviously shallow

## Controller Note

Do not select the second benchmark just because it is currently popular.

Select it because it is the best stress test for:

- entity judgment
- method generalization
- truthful evolution triggering
