# IKE Runtime v0 R1-G Phase Judgment

## Purpose

This note records the controller judgment for what should come immediately
after materially complete `R1-F`.

## Current Baseline

What is now materially true:

- `R1-D` proved operational closure
- `R1-E` proved project pointer alignment to runtime truth
- `R1-F` proved one narrow controller-facing runtime read surface

## Preserved Gap After R1-F

The remaining runtime gap is not controller visibility.

It is:

- review-submission and acceptance provenance is still narrower than the rest of
  the runtime truth model
- some closure/memory transitions still rely on helper-local attribution shape
  instead of one clearer runtime-owned review provenance discipline

## Candidate Next Phases Considered

### Option A: Broader controller-facing API/UI exposure now

Why not now:

- still too early
- would expand surface area before review provenance is hardened

### Option B: Notification/follow-up surfaces now

Why not now:

- belongs to later capability growth
- should not precede tighter review/acceptance attribution

### Option C: Narrow review provenance hardening

Meaning:

- tighten how runtime records review submission and acceptance provenance for
  operational closure / memory-packet promotion paths
- keep it inside existing runtime objects and metadata discipline

Why this is the right next phase:

- directly follows the remaining `R1-D/R1-F` gaps
- improves runtime auditability without widening the platform

## Controller Decision

Accepted next phase:

- **`R1-G = Review Provenance Hardening`**

## What R1-G Should Include

1. narrow runtime-owned review submission/acceptance provenance discipline
2. tests proving reviewed closure/memory transitions keep truthful actor
   attribution
3. no new object family and no broad workflow marketplace expansion

## What R1-G Should Not Include

- broad UI/API rollout
- notifications/follow-up mesh
- benchmark fusion
- graph/retrieval work
- new runtime object families

## Resulting Mainline Rule

After `R1-F`, do not broaden the platform yet.

Open:

- `R1-G Review Provenance Hardening`

and keep it narrowly focused on runtime attribution truth.
