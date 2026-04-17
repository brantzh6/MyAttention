# IKE Runtime v0 - R2-I17 Phase Judgment

Date: 2026-04-10
Phase: `R2-I17 Canonical Launch Baseline Alignment`
Status: `candidate next packet inside R2-I`

## Why This Packet Exists

`R2-I16` reclaimed canonical `8000` onto the reviewed Windows redirector owner
chain, but it also exposed a remaining mismatch:

- the validated live Windows launch discipline was the repo `uvicorn.exe`
  chain
- the machine-readable `canonical_launch` field still described
  `python run_service.py`

That created an unnecessary honesty gap between:

- the documented canonical launch baseline
- the launch shape that was actually validated live

## Intended Scope

If opened, `R2-I17` should narrow to one question only:

- can the machine-readable `canonical_launch` surface be aligned with the
  currently validated Windows live launch discipline without widening runtime
  semantics?

## Explicit Non-Goals

- no service supervisor
- no detached restart policy
- no scheduler semantics
- no broad deployment rewrite

## Controller Judgment

`R2-I17` is the correct next packet if the remaining mainline gap is launch
baseline honesty rather than route existence or owner-chain acceptability.
