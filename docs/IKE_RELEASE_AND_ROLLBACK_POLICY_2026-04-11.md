# IKE Release And Rollback Policy

Date: 2026-04-11
Status: controller baseline

## Purpose

Define the minimum release and recovery discipline needed so IKE can survive
bad evolution steps, bad patches, bad prompts, and bad environment changes.

## Core Rule

If the project cannot return to a previously trusted state, it is not under
control.

## Recovery Layers

IKE needs three recovery layers:

1. code rollback
2. config rollback
3. data/runtime rollback

Rolling back only one of the three is often insufficient.

## Code Rollback Policy

### Branch Baseline

The project should keep at least:

- `main`
  - accepted recoverable truth
- `codex/*`, `feature/*`, or equivalent working branches
  - active implementation
- `release/*` when preparing a staged release
  - release candidate stabilization

### Commit Rule

Every milestone-level change must be committed.

If a state is important enough to mention in review or docs, it is important
enough to exist in git.

### Tag Rule

Every accepted milestone should receive a tag.

Suggested examples:

- `milestone/runtime-r2-i18`
- `release/2026-04-11-staging-1`
- `rollback/pre-cutover-2026-04-11`

### Pre-Risk Checkpoint Rule

Before high-risk changes, create a checkpoint:

1. clean branch or named branch position
2. git commit if needed
3. tag or explicit rollback pointer

High-risk changes include:

- schema changes
- root path cutover
- environment migration
- memory contract changes
- service identity changes

## Config Rollback Policy

Configuration must be versioned, not treated as ambient local state.

This includes:

- prompts
- provider routing
- model defaults
- agent contracts
- runtime local process config
- deployment templates

A release is not recoverable if code can be rolled back but config cannot.

## Data And Runtime Rollback Policy

Before risky promotions, preserve recoverable copies of:

1. database
2. Redis or queue state if operationally relevant
3. vector / knowledge store snapshots where relevant
4. runtime artifacts needed for audit

At minimum, the project must be able to answer:

- what code version was running
- what config version was active
- what data snapshot or backup corresponds to it

## Release Sequence

The minimum release sequence should be:

1. candidate branch prepared
2. validation completed
3. docs and review archived
4. release commit created
5. release tag created
6. staging deployment or promotion
7. production promotion only after staging acceptance

## Rollback Triggers

Rollback should be considered immediately when any of the following appears:

1. canonical runtime path fails after promotion
2. task/decision truth becomes ambiguous
3. memory or knowledge surfaces are unexpectedly polluted
4. service launch path no longer matches reviewed baseline
5. self-evolution changes controller behavior without explicit approval

## Rollback Actions

Rollback is not one action.

It should be executed as a bounded packet:

1. identify target rollback version
2. restore code
3. restore config
4. restore data if needed
5. validate canonical service path
6. archive rollback result

## Production Safety Rule

`prod-runtime` must be able to reject or survive a bad evolution candidate.

That means:

- no direct delegate write path into production
- no auto-promotion without controller gate
- no irreplaceable local-only state

## Immediate Minimum Standard

Effective immediately, the project should treat the following as mandatory:

1. every meaningful milestone must be committed
2. every accepted milestone should be tagged
3. every review result worth keeping must be written into docs and committed
4. every high-risk operation must have a rollback pointer
5. every environment promotion must be tied to a known code + config state

## Practical Meaning For IKE

IKE is trying to build a system that can reason, evolve, and coordinate
delegated work.

That increases the cost of weak rollback discipline, not lowers it.

The stronger the system becomes, the more important it is that it cannot
silently evolve past the point where it can be recovered.
