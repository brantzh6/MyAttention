# IKE Source Intelligence V1 M13 Phase Judgment - 2026-04-15

## Judgment

`M13` is approved as the next bounded slice after `M12`.

The correct next move is not another inspect route. It is a bounded
controller-facing advisory layer on top of the existing panel outputs.

## Why This Slice

`M7` through `M12` proved:

- single-model inspect on discovery candidates
- dual-lane panel inspect on discovery candidates
- reusable internal judgment substrate
- single-model inspect on version change targets
- dual-lane panel inspect on version change targets

What is still missing is a minimal operational bridge:

- not workflow
- not persistence
- not voting
- not automation

But a truthful suggestion layer that says:

- what looks safe to follow
- what looks safe to suppress
- what should stay in watch
- what must stay in manual review

## Scope

Bounded scope for `M13`:

- add reusable selective-absorption advisory derivation to the internal
  judgment substrate
- surface the advisory output on the existing panel routes only
- keep all outputs inspect-only and non-canonical

Out of scope:

- persisted panel outcomes
- automatic source-plan mutation
- generic workflow engine
- controller replacement
