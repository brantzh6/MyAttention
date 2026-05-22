# IKE Milestone Policy

Date: 2026-04-17
Status: controller baseline

## Purpose

Define when a bounded piece of work is only a checkpoint, when it qualifies
as a milestone, and what must exist before the result is considered durable.

This policy exists so IKE can keep moving without confusing:

- ad hoc progress snapshots
- reviewable milestones
- long-term archive points

## Definitions

### Checkpoint

A checkpoint is a safety snapshot.

Use it when the goal is to avoid losing work, not to claim completion.

Typical signs:

- work has moved forward but is still in flight
- validation is partial
- review has not yet returned
- the result is useful for recovery, but not yet for formal acceptance

### Milestone

A milestone is a bounded result with enough evidence to review, absorb, and
rely on.

Typical signs:

- the scope is narrow and explicit
- the result has been validated
- a review packet exists
- review feedback can be absorbed cleanly
- the result is durable enough to commit and tag

### Archive Point

An archive point is a milestone or larger boundary that should remain easy to
recover, replay, or compare later.

Use it when:

- the work changed a major surface
- rollback matters
- the result will likely be referenced again

## Milestone Criteria

Treat a result as a milestone only when most of the following are true:

1. the scope is bounded and named
2. the result has a clear claim boundary
3. validation was run on the changed surface
4. the result can be reviewed externally
5. the review outcome is either accepted or absorbed with explicit changes
6. the result is committed to git
7. the result can be traced through docs, tests, and handoff

If item 1 or 2 is missing, it is not a milestone.

If item 3 or 4 is missing, it is a checkpoint only.

If item 6 is missing, it is not durable.

## Required Artifacts

A proper milestone should usually include:

- `phase_judgment`
- `plan`
- `result`
- `review request`
- `review absorption`
- validation commands
- git commit or tag when appropriate

Not every checkpoint needs all of these. A milestone usually does.

## Decision Rule

Use this rule of thumb:

- `checkpoint` if the work is useful but still moving
- `milestone` if the work is bounded, validated, and reviewable
- `archive point` if the result should be easy to recover or compare later

## Release Relation

Not every milestone is a release.

A milestone becomes release-relevant only if it affects one of these:

- runtime behavior
- environment identity
- controller truth
- persistence contract
- promotion / rollback boundary

## Practical Policy

For IKE, the safe default is:

1. do frequent checkpoints
2. promote only clear milestones
3. archive major boundaries
4. do not call something a milestone just because it is large

## Example From Current Project

The current project snapshot that was pushed to GitHub is best treated as a
checkpoint unless it is paired with a completed review/absorption boundary.

If a review pack, validation, and absorption exist, then it can be promoted
to milestone status.

## Operating Note

This policy should be used together with:

- release and rollback policy
- delivery governance index
- active mainline map
- current handoff
