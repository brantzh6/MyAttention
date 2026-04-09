# IKE Runtime v0 R1-I Phase Judgment

## Purpose

This note records the controller judgment for what should come immediately
after materially complete `R1-H`.

## Current Baseline

What is now materially true:

- `R1-D`, `R1-E`, `R1-F`, and `R1-G` are all independently evidenced across
  coding/review/testing/evolution
- `R1-H` completed delegated-evidence recovery without reopening runtime truth
  semantics
- recent runtime phases are no longer primarily carried by controller fallback

## Preserved Gap After R1-H

The remaining gap is no longer evidence recovery.

It is:

- helper-level operational guardrails are still thinner than the recovered
  evidence now justifies
- independent review/testing surfaced real narrow risks around:
  - explicit alignment to stale/archived work contexts
  - upstream existence versus upstream state relevance
  - error behavior when the expected active context is missing

## Candidate Next Phases Considered

### Option A: Broader controller/runtime surface now

Why not now:

- runtime has just recovered independent evidence
- broadening surface area now would outrun the guardrails that the recovered
  evidence says still need tightening

### Option B: Notification/follow-up surfaces now

Why not now:

- still belongs to later capability growth
- does not address the narrow correctness gaps surfaced by independent lanes

### Option C: Narrow operational guardrail hardening

Meaning:

- harden the helper paths introduced in `R1-D` and `R1-E`
- keep work inside existing runtime truth objects and helper boundaries
- close the concrete stale-pointer and upstream-relevance guardrails now that
  independent review/testing has made them explicit

Why this is the right next phase:

- directly follows the recovered evidence
- turns real findings into narrow correctness improvements
- does not reopen runtime schema or widen platform scope

## Controller Decision

Accepted next phase:

- **`R1-I = Operational Guardrail Hardening`**

## What R1-I Should Include

1. reject explicit project-pointer alignment to non-active/archived
   `RuntimeWorkContext`
2. make no-active-context handling explicit instead of leaking raw ORM failure
3. tighten closure/trust validation where existence-only checks are no longer
   enough
4. keep all changes inside current runtime helpers and tests

## What R1-I Should Not Include

- new runtime object families
- broader controller/API/UI surface expansion
- notification mesh
- benchmark/research integration
- graph/vector memory work

## Resulting Mainline Rule

After `R1-H`, do not widen the runtime platform yet.

Open:

- `R1-I Operational Guardrail Hardening`

and keep it narrowly focused on correctness hardening surfaced by recovered
independent evidence.
