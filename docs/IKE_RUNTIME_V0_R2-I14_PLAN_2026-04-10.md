# IKE Runtime v0 - R2-I14 Plan

Date: 2026-04-10
Phase: `R2-I14 Promotion Readiness Self-Check`
Status: `candidate`

## Goal

Make the controller-facing preflight path capable of truthfully reaching the
reviewed Windows redirector acceptability result without requiring manual
fingerprint plumbing by the caller.

## Current Evidence

Observed on canonical `127.0.0.1:8000`:

1. default preflight request:
   - `code_freshness = unchecked`
   - `controller_acceptability = blocked_owner_mismatch`
2. explicit current fingerprint request:
   - `code_freshness = match`
   - `controller_acceptability = acceptable_windows_venv_redirector`
   - `controller_promotion = controller_confirmation_required`

## Proposed Shape

1. add the narrowest truthful self-check mechanism for canonical local
   preflight
2. preserve the semantics split:
   - self-check evidence
   - controller confirmation requirement
3. add focused tests proving:
   - the self-check does not fake freshness
   - mismatch still blocks
   - confirmation is still required for the Windows redirector path

## Success Condition

`R2-I14` should count as successful only if:

1. the controller-facing preflight surface can truthfully produce
   `code_freshness = match` for the current canonical local service without
   manual fingerprint copy/paste
2. the resulting status remains:
   - `controller_acceptability = acceptable_windows_venv_redirector`
   - `controller_promotion = controller_confirmation_required`
3. no automatic promotion action is introduced

## Failure Condition

`R2-I14` fails if it:

- invents freshness without a real comparison basis
- auto-promotes the service
- blurs reviewed acceptability into direct canonical-ready
- widens into deployment/service-management scope
