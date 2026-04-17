# IKE Source Intelligence V1 - M8 Phase Judgment

Date: 2026-04-15
Phase: `M8 AI Judgment Panel Inspect`
Status: `activated`

## Why This Slice

`M7` proved that one inspect-only AI judgment lane can participate above the
current cleaned discovery surface.

The next bounded step should not jump to persistence or orchestration.
It should only expose whether one bounded dual-lane panel sees the same
candidate subset in a way that yields useful verdict-overlap shape.

## Scope

Add one inspect-only panel route that:

1. reuses the existing discovery path
2. reuses the same bounded judged candidate subset
3. runs two bounded lane calls on the same candidate subset
4. exposes verdict-overlap agreement and disagreement shape
5. does not merge panel output into canonical truth

## Out Of Scope

This slice does not attempt:

1. panel voting or auto-majority decisions
2. persistence into source plans
3. controller auto-routing based on the panel
4. dynamic methodology-program generation
5. generalized multi-agent orchestration
