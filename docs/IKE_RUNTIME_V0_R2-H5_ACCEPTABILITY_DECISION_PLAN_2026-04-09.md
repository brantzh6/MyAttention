# IKE Runtime v0 - R2-H5 Acceptability Decision Plan

Date: 2026-04-09
Phase: `R2-H Canonical Service Launch Path Normalization`

## Decision

Should the following pattern remain blocked, or be accepted as canonical on
Windows?

- parent:
  - repo `.venv` interpreter
- child:
  - system `Python312`
- both parent and child:
  - repo `run_service.py`
- helper classification:
  - `windows_venv_redirector_candidate`

## Safe Rule Options

### Option A

Keep the current rule:

- any `preferred_mismatch` remains blocked

Pros:
- strict
- no risk of false canonical acceptance

Cons:
- may permanently block canonical acceptance for a normal Windows `.venv`
  launch shape

### Option B

Refine the canonical rule for this narrow pattern:

- accept when all are true:
  - `windows_venv_redirector_candidate = true`
  - `repo_launcher.status = parent_and_child_repo_launcher_match`
  - latest code is confirmed
  - service entry is the canonical repo `run_service.py`

Pros:
- controller can truthfully accept canonical Windows service proof

Cons:
- needs careful wording to avoid over-broad acceptance

## Current Controller Recommendation

Do not auto-apply Option B without a deliberate review decision.
