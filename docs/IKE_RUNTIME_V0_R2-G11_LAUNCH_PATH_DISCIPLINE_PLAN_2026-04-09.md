# IKE Runtime v0 - R2-G11 Launch-Path Discipline Plan

Date: 2026-04-09
Phase: `R2-G Runtime Service Stability And Delegated Closure Hardening`

## Why This Exists

`R2-G4 ~ R2-G10` made service-preflight truth increasingly explicit:

- preferred owner
- owner chain
- code fingerprint
- code freshness
- alternate host/port targeting

The remaining blocker is no longer observability.

It is now:

- repo `.venv` launch can still yield a system `Python312` listener child
- fresh alternate-port live proof is therefore not durably trustworthy
- current `8000` route can still lag latest workspace code

## Narrow Goal

Prove one truthful, repeatable launch path for a fresh API service such that:

1. listener owner is acceptable to controller
2. served route reflects current workspace code
3. strict service preflight can be evaluated live without ambiguity

## Non-Goals

This phase must not:

- introduce a service supervisor
- introduce a daemon manager
- broaden into deployment automation
- redefine runtime truth semantics
- replace the existing `run_service.py` contract without evidence

## Target Questions

1. Can repo `.venv` launch be made to produce a preferred listener directly?
2. If not, is `parent_preferred_child_mismatch` acceptable as the truthful baseline?
3. What is the smallest controller rule that distinguishes:
   - acceptable fresh launch
   - stale/ambiguous launch
4. What is the minimum live proof that confirms served code freshness?

## Candidate Work

### A. Launch-path evidence collection

- compare:
  - `python run_service.py`
  - `python -m uvicorn main:app`
  - any already accepted repo-local launcher path
- record:
  - parent process
  - listener process
  - command lines
  - live route freshness

### B. Acceptability rule

- decide whether `parent_preferred_child_mismatch` is:
  - reject
  - ambiguous
  - acceptable-under-bounds

### C. Fresh-code live proof

- prove at least one alternate-port service returns:
  - current `owner_chain`
  - current `code_fingerprint`
  - current `code_freshness`

## Success Criteria

- one launch path is documented as controller-acceptable
- one live alternate-port route returns latest preflight fields
- handoff no longer needs to treat all fresh live proof as operationally ambiguous

## Failure Criteria

- repeated attempts still produce unbounded launcher drift
- no launch path can serve current code without ambiguity
- the work starts expanding into supervision/deployment architecture

## Current Controller Recommendation

Keep `R2-G` active.

Do not open a broader runtime phase yet.

The next justified work is launch-path discipline, not more feature growth.
