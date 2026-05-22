# IKE Runtime v0 - R2-I14 Phase Judgment

Date: 2026-04-10
Phase: `R2-I14 Promotion Readiness Self-Check`
Status: `candidate next packet inside R2-I`

## Why This Packet Exists

`R2-I13` closed the live route freshness gap, but it exposed a new narrower
controller-facing gap:

1. default live preflight requests leave `code_freshness = unchecked`
2. under that default shape, live preflight reports:
   - `controller_acceptability = blocked_owner_mismatch`
   - `controller_promotion = not_promotable`
3. if the caller supplies the current expected fingerprint explicitly, the same
   live service reports:
   - `controller_acceptability = acceptable_windows_venv_redirector`
   - `controller_promotion = controller_confirmation_required`

So the reviewed Windows redirector acceptability path exists, but it is not
yet self-closing from the controller-facing default path.

## Intended Scope

If opened, `R2-I14` should narrow to one question only:

- can the controller-facing preflight surface truthfully self-check current
  code freshness for the canonical local service without requiring manual
  fingerprint copy/paste?

## Explicit Non-Goals

- no automatic promotion mutation
- no service manager
- no scheduler semantics
- no broad runtime orchestration work

## Controller Judgment

`R2-I14` is the correct next packet if the current goal is to close the gap
between reviewed promotion semantics and the default controller-visible
preflight path.
