# IKE Runtime v0 - R2-I16 Result Milestone

Date: 2026-04-10
Phase: `R2-I16 Canonical Owner-Chain Reclaim`
Status: `completed`

## Scope

Reclaim canonical `127.0.0.1:8000` onto the reviewed Windows redirector owner
chain after `R2-I15` proved the controller-decision route existed but the live
launch path could still fall back to `blocked_owner_mismatch`.

This packet is operationally narrow.
It does not add new runtime semantics.

## What Was Proven

Canonical `127.0.0.1:8000` can now again reach the reviewed promotable local
Windows shape when launched through the repo `uvicorn.exe` chain:

- `controller_acceptability = acceptable_windows_venv_redirector`
- `controller_promotion = controller_confirmation_required`
- `decision.recommended_action = controller_confirmation_required`

## Live Evidence

### 1. Reclaimed Canonical Preflight Shape

Live canonical request:

```json
{
  "self_check_current_code": true,
  "strict_code_freshness": true
}
```

now returns:

- `owner_chain.status = parent_preferred_child_mismatch`
- `repo_launcher.status = parent_and_child_repo_launcher_match`
- `windows_venv_redirector.status = windows_venv_redirector_candidate`
- `code_freshness.status = match`
- `controller_acceptability.status = acceptable_windows_venv_redirector`
- `controller_promotion.status = controller_confirmation_required`

### 2. Reclaimed Controller-Decision Surface

Live canonical controller-decision request now returns:

- `decision.recommended_action = controller_confirmation_required`
- `decision.target_status = canonical_accepted`
- `decision.eligible = true`
- `truth_boundary.inspect_only = true`
- `truth_boundary.mutates_acceptance = false`

### 3. Launch-Method Discovery

The reclaim result also clarified one important local Windows distinction:

- launching canonical `8000` through `.venv\\Scripts\\uvicorn.exe` preserves a
  repo-launcher chain that satisfies the reviewed Windows redirector rule
- launching via direct `python run_service.py` in the current environment can
  still fall back to `repo_launcher_mismatch`

So the current reviewed live-operational baseline is narrower than
"any repo-launched Python process".

## Mainline Meaning

The runtime mainline now has both:

- an explicit controller-facing decision inspect surface
- a live canonical `8000` service that again reaches the reviewed
  `controller_confirmation_required` shape

This restores the mainline to the same truthful decision edge as before the
temporary launch regression:

- the controller may inspect a promotion-eligible shape live
- but acceptance is still not mutated automatically

## Validation

Live checks run:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/ike/v0/runtime/service-preflight/inspect' -Method Post -ContentType 'application/json' -Body '{"self_check_current_code":true,"strict_code_freshness":true}'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/ike/v0/runtime/service-preflight/controller-decision/inspect' -Method Post -ContentType 'application/json' -Body '{"self_check_current_code":true,"strict_code_freshness":true}'
```

Observed result:

- canonical `8000` healthy
- canonical preflight again returns `acceptable_windows_venv_redirector`
- canonical controller-decision inspect again returns
  `controller_confirmation_required`

## Controller Judgment

- `R2-I16 = accept_with_changes`

## Remaining Gaps

This still does not prove:

1. automatic controller acceptance mutation
2. persisted controller decision recording
3. detached supervision
4. scheduler semantics

It also leaves one clarified documentation/discipline gap:

5. the current machine-readable `canonical_launch` field still describes the
   `python run_service.py` path, while the currently validated live Windows
   redirector shape was reclaimed through `.venv\\Scripts\\uvicorn.exe`

That gap should be resolved explicitly rather than left implicit.
