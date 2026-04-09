# IKE Runtime v0 R2-G6 Owner Reclaim Note

## Scope

Record one truthful operational finding from `R2-G` service-discipline work.

This is an environment note, not a new runtime feature.

## What Was Attempted

Controller performed a narrow 8000 recovery attempt:

1. identified project-related `run_service.py --port 8000` processes
2. force-stopped the current repo and system Python `8000` processes
3. attempted an explicit repo `.venv` restart on `8000`
4. re-checked listener ownership and health

## What Was Observed

- after clearing the existing `8000` processes, the port temporarily had:
  - no listener
- explicit foreground launch from:
  - [D:\code\MyAttention\.venv\Scripts\python.exe](/D:/code/MyAttention/.venv/Scripts/python.exe)
  - [D:\code\MyAttention\services\api\run_service.py](/D:/code/MyAttention/services/api/run_service.py)
  did not immediately error
- after recovery, `GET /health` returned:
  - `200`
- but the resulting `8000` listener owner was still:
  - system `Python312`
  - running:
    - `D:\code\MyAttention\services\api\run_service.py --host 127.0.0.1 --port 8000`

## Truthful Interpretation

This means:

- current API availability is restored
- current ownership mismatch is still real
- and there is likely an external process restart / environment policy outside
  runtime code control that reclaims the listener under system Python

So the remaining blocker is not:
- route semantics
- runtime project surface
- benchmark bridge logic

It is:
- **environment-level service ownership discipline**

## Result

Current truthful controller interpretation:

- `8000` is healthy again
- `8000` is still not on the preferred repo-owned baseline
- preferred-owner strict preflight should remain the gate for live proof

## Follow-Up Pressure

Do not claim service ownership normalization yet.

Any next step should treat this as:
- environment/process-management hardening
- not runtime truth redesign
