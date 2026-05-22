# IKE Runtime v0 R1-H Phase Judgment

## Purpose

This note records the controller judgment for what should come immediately
after materially complete `R1-G`.

## Current Baseline

What is now materially true:

- `R1-D` proved operational closure
- `R1-E` proved project pointer alignment to runtime truth
- `R1-F` proved one narrow controller-facing runtime read surface
- `R1-G` hardened review-submission provenance inside existing runtime
  metadata/object boundaries

## Preserved Gap After R1-G

The remaining gap is no longer runtime truth semantics.

It is:

- recent runtime phases still rely heavily on controller fallback review notes
  when delegated review/testing/evolution results are missing or unstable
- the project can move forward truthfully with fallback coverage, but that is
  weaker than having durable independent lane evidence
- widening the runtime platform further before this is tightened would reduce
  confidence in the multi-agent cycle

## Candidate Next Phases Considered

### Option A: broader controller/runtime surface now

Why not now:

- would widen the platform while independent evidence is still thin
- would add new surface before hardening the quality loop

### Option B: notification / follow-up surfaces now

Why not now:

- still belongs to later capability growth
- should not outrun review/testing/evolution evidence recovery

### Option C: independent delegated evidence recovery

Meaning:

- recover or normalize durable delegated review/testing/evolution evidence for
  the recent runtime phases
- keep controller fallback as a backup, not the primary proof path
- improve auditability of the second-wave multi-agent cycle without creating
  new runtime truth objects

Why this is the right next phase:

- directly addresses the biggest remaining quality gap after `R1-G`
- strengthens the real controller + coding + review + testing + evolution
  operating model
- keeps work narrow and does not reopen runtime semantics

## Controller Decision

Accepted next phase:

- **`R1-H = Independent Delegated Evidence Recovery`**

## What R1-H Should Include

1. recover or regenerate durable delegated review/testing/evolution evidence
   for the most recent runtime phases where fallback currently carries the load
2. make the difference between controller fallback and delegated evidence
   explicit in durable milestone records
3. add the narrowest controller-facing execution guidance needed to rerun or
   normalize missing delegated evidence

## What R1-H Should Not Include

- new runtime object families
- new runtime DB truth semantics
- broad controller UI/API work
- benchmark/research integration
- notification mesh
- graph/vector memory work

## Resulting Mainline Rule

After `R1-G`, do not widen the runtime platform yet.

Open:

- `R1-H Independent Delegated Evidence Recovery`

and keep it narrowly focused on restoring independent evidence for the existing
runtime phases.
