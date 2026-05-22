# IKE Runtime v0 - R2-G Result Milestone

Date: 2026-04-09
Phase: `R2-G Runtime Service Stability And Delegated Closure Hardening`

## Summary

`R2-G` is now materially complete.

This phase did not normalize the canonical `8000` service into the preferred
repo-owned launch path.

It did complete the narrower goals required for truthful controller operation:

- machine-readable service observability
- machine-readable owner/launcher/code-freshness diagnosis
- explicit controller acceptability interpretation
- truthful distinction between bounded alternate-port live proof and canonical
  service proof

## What Is Now True

The runtime service surface can now expose and evaluate:

- `preferred_owner`
- `owner_chain`
- `code_fingerprint`
- `code_freshness`
- `repo_launcher`
- `controller_acceptability`

The controller rule is now explicit:

- `ready + canonical_ready`:
  - acceptable for canonical live proof
- `ambiguous + bounded_live_proof_ready`:
  - acceptable only for bounded alternate-port live proof
- `ambiguous + blocked_owner_mismatch`:
  - not acceptable
- `ambiguous + blocked_code_freshness`:
  - not acceptable
- `down`:
  - not acceptable

## What Was Proven

1. Canonical `8000` is observable but still not controller-acceptable.
2. Fresh alternate-port live proof can now return the latest preflight schema.
3. Fresh-code live proof can now be established using an explicit expected
   fingerprint.
4. The remaining ambiguity is launch-path / interpreter ownership drift, not
   missing preflight fields or stale route logic.

## Remaining Open Gap

The remaining unresolved issue is:

- canonical service launch-path normalization

More specifically:

- repo launcher evidence can be present
- but the live listener can still drift to a system `Python312` child
- so the canonical service remains blocked by owner mismatch

## Truthful Judgment

- `R2-G = materially complete`

## Controller Recommendation

Open the next narrow phase around canonical service normalization.

Do not reopen `R2-G` for more observability fields unless a new operational
blind spot is discovered.
