# IKE Runtime v0 - R2-H7 Live Promotable Shape Result

Date: 2026-04-10
Phase: `R2-H Canonical Service Launch Path Normalization`
Packet: `R2-H7 Live Promotable Shape Proof`

## Scope

Run one real canonical-port preflight against the currently running local
service on `127.0.0.1:8000` using the current runtime code fingerprint.

The goal is narrow:

- confirm whether the live canonical service can now reach the reviewed
  Windows redirector intermediate state
- confirm whether the new `controller_promotion` field reports it as
  promotion-eligible

## Live Commands

```powershell
try { (Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 5).Content } catch { $_.Exception.Message }

$env:PYTHONPATH='D:\code\MyAttention\services\api'; @'
from pprint import pprint
from runtime.service_preflight import _build_code_fingerprint, run_preflight_sync
fingerprint = _build_code_fingerprint().get('fingerprint')
print(f'fingerprint={fingerprint}')
result = run_preflight_sync(
    strict_preferred_owner=True,
    expected_code_fingerprint=fingerprint,
    strict_code_freshness=True,
)
print(result.status.value)
print(result.summary)
pprint(result.details.get('code_freshness'))
pprint(result.details.get('controller_acceptability'))
pprint(result.details.get('controller_promotion'))
'@ | python -

$procId = (Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object -ExpandProperty OwningProcess -First 1)
if ($procId) {
  Get-CimInstance Win32_Process -Filter "ProcessId = $procId" |
    Select-Object ProcessId,ParentProcessId,Name,CommandLine | Format-List
  $parentId = (Get-CimInstance Win32_Process -Filter "ProcessId = $procId").ParentProcessId
  if ($parentId) {
    Get-CimInstance Win32_Process -Filter "ProcessId = $parentId" |
      Select-Object ProcessId,ParentProcessId,Name,CommandLine | Format-List
  }
}
```

## Observed Result

- `/health` returned healthy
- computed fingerprint:
  - `16bbb9eadb112bfc`
- preflight returned:
  - `status = ambiguous`
  - this remains expected because strict preferred-owner still sees the child
    interpreter mismatch
- but the controller-facing narrow result is now:
  - `controller_acceptability.status = acceptable_windows_venv_redirector`
  - `acceptable = true`
  - `controller_confirmation_required = true`
- and the new promotion result is:
  - `controller_promotion.status = controller_confirmation_required`
  - `eligible = true`
  - `target_status = canonical_accepted`

## Live Process Evidence

Observed listener process:

- child listener:
  - `"C:\Users\jiuyou\AppData\Local\Programs\Python\Python312\python.exe" D:\code\MyAttention\services\api\run_service.py --host 127.0.0.1 --port 8000`
- parent launcher:
  - `"D:\code\MyAttention\.venv\Scripts\python.exe" D:\code\MyAttention\services\api\run_service.py --host 127.0.0.1 --port 8000`

This matches the reviewed Windows venv redirector interpretation:

- repo launcher evidence is intact
- canonical launch path is intact
- code freshness is now explicitly matched
- the remaining difference is the documented Windows redirector child
  interpreter shape

## Controller Judgment

- `R2-H7 = accept_with_changes`

## Why Accept With Changes

This is the first durable proof in the real local environment that the
canonical `8000` service can reach a promotion-eligible reviewed shape.

What still remains is narrow and explicit:

1. controller must still decide whether this specific live shape is now enough
   to treat canonical service proof as accepted
2. if the project wants a durable acceptance record, that record still needs to
   be written above the inspect layer
