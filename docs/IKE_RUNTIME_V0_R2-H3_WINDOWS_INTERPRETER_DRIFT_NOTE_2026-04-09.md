# IKE Runtime v0 - R2-H3 Windows Interpreter Drift Note

Date: 2026-04-09
Phase: `R2-H Canonical Service Launch Path Normalization`

## Observation

After a bounded canonical restart on `8000`, the live process chain is:

1. parent:
- `D:\\code\\MyAttention\\.venv\\Scripts\\python.exe`
- `D:\\code\\MyAttention\\services\\api\\run_service.py --host 127.0.0.1 --port 8000`

2. child listener:
- `C:\\Users\\jiuyou\\AppData\\Local\\Programs\\Python\\Python312\\python.exe`
- `D:\\code\\MyAttention\\services\\api\\run_service.py --host 127.0.0.1 --port 8000`

The canonical service is now serving the latest preflight schema, but
`controller_acceptability` still reports:

- `blocked_owner_mismatch`

## Why This Matters

This creates a new interpretation risk:

- the current rule may still be correctly identifying an undesirable drift
- or it may be over-classifying a Windows `.venv` launch behavior that still
  preserves the repo launcher and the correct service entry

## What Is Known

- repo launcher evidence is present in both parent and child
- the parent process matches the preferred repo interpreter
- the live listener does not match the preferred repo interpreter
- the canonical service now serves the latest landed preflight fields

## What Is Not Yet Proven

- whether this parent/child interpreter split is:
  - a Windows virtualenv implementation detail
  - a uvicorn/process-launch quirk
  - or a genuine launch-path integrity problem

## Truthful Judgment

- `R2-H3 = diagnosis_only`

## Controller Recommendation

Do not widen the canonical-ready rule yet.

Next work should be a bounded review/diagnosis step:

- determine whether Windows repo-venv launches legitimately materialize as a
  system-Python child while preserving the repo launch contract
- then decide whether the canonical acceptability rule should remain strict or
  be refined for this specific pattern
