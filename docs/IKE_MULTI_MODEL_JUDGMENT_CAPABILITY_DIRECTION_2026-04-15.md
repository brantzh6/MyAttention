# IKE Multi-Model Judgment Capability Direction

Date: 2026-04-15
Status: active direction note

## Core Decision

Multi-model review / judgment should not continue as a collection of project-
private route tricks.

The preferred direction is:

1. incubate inside the current project on bounded slices
2. keep the semantics capability-shaped from now on
3. later extract it into a reusable judgment capability once at least two
   distinct project use cases have proven it

## Why

If the panel logic is embedded too deeply into current Source Intelligence
business semantics, it will become:

- hard to reuse
- hard to evolve
- hard to apply to other agent/controller tasks

What should remain reusable is not the current source schema, but the judgment
pattern:

- multiple AI lanes
- per-lane outputs
- consensus shape
- disagreement shape
- opportunity-carrying disagreement
- bounded follow-up hints
- explicit truth boundary

## Practical Rule

Current `M7` / `M8` / `M9` are allowed to live in project code, but they should
be treated as incubation for a future reusable capability.

That means future slices should prefer:

- inspect-first
- non-canonical outputs
- explicit truth boundaries
- portable semantics over project-specific naming where possible

And avoid:

- silent coupling to only one business route
- hidden merges
- premature workflow automation
- irreversible persistence semantics

## Near-Term Interpretation

For now:

- `Source Intelligence` remains the proving ground
- the judgment panel remains project-local

But controller-level design should assume this can later become:

- a reusable review substrate
- a disagreement-intelligence lane
- a shared AI judgment capability for other agents and brains
