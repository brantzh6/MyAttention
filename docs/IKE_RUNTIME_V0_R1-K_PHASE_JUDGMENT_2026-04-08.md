# IKE Runtime v0 R1-K Phase Judgment

## Purpose

This note records the controller judgment for what should come immediately
after materially complete `R1-J`.

## Current Baseline

What is now materially true:

- `R1-J` closed the narrow DB-backed stability question without requiring a new
  patch
- runtime helper guardrails are materially stronger than before
- recent runtime phases are durably recorded and independently evidenced or
  controller-proven where appropriate

## Preserved Gap After R1-J

The next remaining narrow gap is:

- read-path reconstruction/controller surfaces still treat trusted packet
  inclusion through upstream existence checks rather than upstream relevance
  checks
- this distinction has been explicitly preserved several times and should no
  longer remain implicit

## Candidate Next Phases Considered

### Option A: Broader runtime/controller/application surface now

Why not now:

- the remaining gap is still inside current helper/read surfaces
- widening the platform would outrun unresolved trust semantics on the read path

### Option B: More DB-backed stability work now

Why not now:

- `R1-J` just established that the targeted DB-backed slices are currently
  repeatable
- continuing stability work now would not address the next preserved semantic
  gap

### Option C: Narrow read-path trust semantics alignment

Meaning:

- decide and harden whether trusted packet inclusion on read paths should remain
  existence-based or become relevance-aware
- keep the distinction explicit and truthful
- stay inside existing runtime helpers and tests

Why this is the right next phase:

- directly follows the most clearly preserved runtime gap from `R1-I` through
  `R1-J`
- remains narrow and helper-level
- avoids premature platform expansion

## Controller Decision

Accepted next phase:

- **`R1-K = Read-Path Trust Semantics Alignment`**

## What R1-K Should Include

1. inspect current trusted-packet inclusion on:
   - reconstructed work context
   - controller/project read surface
2. make the intended read-path trust rule explicit
3. harden tests so the distinction is no longer implicit or accidental
4. avoid collapsing read-path visibility semantics into write-path acceptance
   semantics unless justified

## What R1-K Should Not Include

- new runtime tables or object families
- broader API/UI/platform expansion
- notification/follow-up mesh
- graph/vector memory work
- benchmark/research integration

## Resulting Mainline Rule

After `R1-J`, the next phase should not widen the platform.

Open:

- `R1-K Read-Path Trust Semantics Alignment`

and keep it narrowly focused on helper/read-surface truthfulness.
