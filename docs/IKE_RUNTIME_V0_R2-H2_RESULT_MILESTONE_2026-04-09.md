# IKE Runtime v0 - R2-H2 Result Milestone

Date: 2026-04-09
Phase: `R2-H Canonical Service Launch Path Normalization`

## Summary

A bounded canonical restart on `8000` was executed using the explicit repo
launch path:

- `D:\\code\\MyAttention\\.venv\\Scripts\\python.exe`
- `D:\\code\\MyAttention\\services\\api\\run_service.py`

The service was successfully restored on `8000` and now serves the latest
preflight schema, including `canonical_launch`.

However, the resulting live preflight still reports:

- `preferred_owner.status = preferred_mismatch`
- `owner_chain.status = parent_preferred_child_mismatch`
- `controller_acceptability.status = blocked_owner_mismatch`

So canonical code freshness is no longer the blocker.

The remaining blocker is interpreter ownership drift.

## Live Evidence

- `GET /health` returned `200`
- `POST /api/ike/v0/runtime/service-preflight/inspect`
  returned:
  - `status = ambiguous`
  - `repo_launcher.status = parent_and_child_repo_launcher_match`
  - `canonical_launch.status = defined`
  - `controller_acceptability.status = blocked_owner_mismatch`

## Truthful Judgment

- `R2-H2 = accept_with_changes`

## Controller Interpretation

This is progress because:

- canonical `8000` is no longer serving stale preflight code
- the explicit canonical launch command is now live on the canonical service

This is not full normalization because:

- preferred interpreter ownership still drifts

## Next Narrow Step

Treat the next task as a diagnosis/hardening step for interpreter ownership
drift, not as another code-freshness or observability task.
