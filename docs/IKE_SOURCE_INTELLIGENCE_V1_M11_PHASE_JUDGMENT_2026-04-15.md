# IKE Source Intelligence V1 M11 Phase Judgment

Date: 2026-04-15
Status: active bounded packet

## Judgment

`M11` should prove a second distinct use case for the internal AI judgment substrate.

The next slice should stay inside `Source Intelligence V1`, but stop expanding the
`/sources/discover/judge/*` family.

## Selected Slice

`M11 = source-plan version change judgment inspect`

Meaning:

- reuse the existing internal judgment substrate on top of `source-plan` version data
- judge bounded refresh/version change targets
- remain inspect-only
- do not mutate source plans
- do not override persisted `evaluation.decision_status`

## Why This Slice

- it proves `feeds.ai_judgment` is not locked to discovery candidates
- it stays on the active mainline
- it adds AI participation to a second truth-adjacent surface without opening workflow

## Out of Scope

- no persistence of AI judgments
- no panel/voting here
- no plan auto-promotion or auto-rollback
- no generic approval framework
