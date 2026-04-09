# Claude Worker Runtime Hardening Requirements

## Current Truth

Claude worker is now a valid local coding/review substrate candidate.

It is **not** yet a hardened independent delegated-runtime lane.

## Highest-Priority Gaps

1. **Durable completion reliability**
- coding or review work may materially happen
- but `final.json` may still be missing inside the acceptable time box
- this breaks delegated closure

2. **Live subprocess/runtime truth**
- abort/finalization truth is better than before
- but still not system-level proven for stubborn real subprocess cases

3. **Detached run discipline**
- run ownership, resume, and finalization remain too close to single-process assumptions
- still not equivalent to a detached job supervisor

4. **Result collision and auditability**
- repeated task/result writes must stay audit-safe
- result identity must remain run-unique and reviewable

## Required Follow-Up

### P1
- harden final artifact completion
- ensure a completed run always yields a durable final artifact or a truthful failed status

### P2
- harden detached abort truth
- confirm process exit before durable aborted completion

### P3
- add black-box CLI end-to-end tests
- cover `start / wait / fetch / abort` through the real CLI path

### P4
- tighten harness result integration
- make it easier to write into `.runtime/delegation/results/*.json` without overwriting prior evidence

## Acceptance Upgrade Condition

Claude worker can be upgraded from:
- `usable local lane`

to:
- `routine delegated coding/review lane`

only after:
- reliable final artifact completion
- stable detached finalization semantics
- stronger live subprocess evidence
