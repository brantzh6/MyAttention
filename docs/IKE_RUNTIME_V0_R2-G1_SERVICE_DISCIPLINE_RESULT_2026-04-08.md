# IKE Runtime v0 R2-G1 Service Discipline Result

## Scope

`R2-G1 = establish truthful local API service discipline evidence`

This is a narrow operational result, not a new runtime truth feature.

## What Was Checked

1. live health reachability
- `GET http://127.0.0.1:8000/health`

2. active port ownership
- `Get-NetTCPConnection -LocalPort 8000`

3. process launch ambiguity
- `Get-CimInstance Win32_Process ... CommandLine -match 'run_service|uvicorn|services\\\\api'`

## Current Truth

- live health on `127.0.0.1:8000` is currently healthy
- port `8000` is currently owned by a single listening process
- but the machine still has duplicate `run_service.py` processes alive across:
  - system Python
  - repo `.venv` Python
- duplicate launch paths also exist on `8001`

## Controller Interpretation

The immediate runtime problem is not that the API is always down.

The real problem is that live proof can still be polluted by ambiguous service ownership:
- one process may answer health
- a different process may be the one the controller intended to validate
- this weakens operational trust even when routes appear healthy

## Narrow Rule Established

For runtime live proof, the truthful service launch path should be treated as:

- repo-local `.venv` Python
- [D:\code\MyAttention\services\api\run_service.py](/D:/code/MyAttention/services/api/run_service.py)
- explicit host/port

Current controller expectation:
- prefer one explicit repo-owned API process for `8000`
- treat extra system-Python `run_service.py` processes as operational ambiguity
- do not over-claim live validation while duplicate launchers remain

## Evidence

- `GET /health` returned `200`
- `Get-NetTCPConnection -LocalPort 8000` showed one current listener
- `Get-CimInstance Win32_Process ...` showed duplicate `run_service.py` launchers across:
  - `.venv\\Scripts\\python.exe`
  - `Python312\\python.exe`

## Result

`R2-G1 = accept_with_changes`

## Remaining Gap

This result establishes truthful diagnosis and launch discipline, but does not yet:
- enforce single-owner process startup
- kill drifted duplicate launchers automatically
- provide a controller-safe bootstrap/teardown helper
