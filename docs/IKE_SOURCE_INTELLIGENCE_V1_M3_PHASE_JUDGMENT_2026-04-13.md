# IKE Source Intelligence V1 - M3 Phase Judgment

Date: 2026-04-13
Phase: `M3 Noise Compression Through Existing Discovery Path`
Status: `approved_for_bounded_start`

## Purpose

Open one bounded `Source Intelligence V1` slice after the accepted `M2`
route-level loop proof.

## Why M3 Starts Now

The current question is no longer whether the existing discovery path can form
a loop.

The current question is whether the same path can reduce obvious source noise
without widening into:

- ranking-engine redesign
- canonical source truth
- identity resolution
- broad source lifecycle automation

## M3 Objective

Reduce one concrete noise pattern inside the current discovery path:

1. generic `domain` entries from a source like `github.com`
2. more specific objects from the same source such as `repository`
3. keep the more specific object when it already carries the stronger
   controller-usable signal

## Explicit Non-Goals

- no new source schema family
- no new compare/diff surface
- no identity merge across sources
- no source retirement logic
- no attention-policy redesign

## Exit Condition

`M3` is complete when the project has:

1. one bounded noise-compression helper or equivalent narrow implementation
2. one focused proof that specific source objects suppress redundant generic
   source-domain entries
3. one explicit result note describing the truth boundary of that compression
