# IKE Environment Strategy

Date: 2026-04-11
Status: controller baseline

## Purpose

Define the minimum environment separation needed so IKE can keep evolving
without letting experiments, delegated runs, and stable operation contaminate
one another.

## Core Judgment

For IKE, traditional `dev / test / prod` is still necessary, but not enough.

The project needs four execution zones:

1. `controller-dev`
2. `sandbox-evolution`
3. `staging-runtime`
4. `prod-runtime`

## Zone Definitions

### 1. `controller-dev`

Purpose:

- main controller working environment
- feature development
- policy drafting
- runtime packet development
- local debugging

Allowed:

- code editing
- prompt editing
- contract editing
- schema candidate work
- local experiments

Not allowed:

- claiming stable truth from ad hoc runs
- treating local dirty state as accepted release state

Current practical mapping:

- controller root:
  - `D:\code\MyAttention`

### 2. `sandbox-evolution`

Purpose:

- delegated agent experimentation
- self-evolution proposals
- isolated coding/review runs
- tool or model comparison

Allowed:

- bounded patches
- bounded review outputs
- experimental prompts
- temporary run artifacts

Not allowed:

- direct mutation of controller truth
- direct mutation of stable runtime truth
- direct mutation of production memory or production services

Current practical mapping:

- OpenClaw workspaces:
  - `D:\code\_agent-runtimes\openclaw-workspaces\...`
- Claude worker run roots:
  - `D:\code\_agent-runtimes\claude-worker\runs`

### 3. `staging-runtime`

Purpose:

- pre-release verification
- milestone validation
- regression checks
- production-like launch-path confirmation

Allowed:

- deployment of release candidates only
- replay of reviewed packets
- runtime verification against fixed candidate versions

Not allowed:

- live exploratory coding
- uncontrolled prompt churn
- direct delegate experimentation

Target characteristics:

- separate workspace or deploy root
- separate ports
- separate database / Redis / knowledge stores
- release-candidate-only code and config

Current truthful state:

- this zone is not yet fully formalized
- parts of its role are currently being approximated by controlled local
  runtime checks

### 4. `prod-runtime`

Purpose:

- stable user-facing or durable operating environment
- long-lived truth surface
- only reviewed and promoted behavior

Allowed:

- accepted release bundles
- accepted config versions
- accepted schema versions
- accepted memory and runtime truth writes

Not allowed:

- direct experimental code
- direct self-evolution writes
- unreviewed delegate changes
- unbounded runtime mutation

## Separation Requirements

The four zones must be separated on more than code alone.

They must also separate:

1. code workspace
2. process/port space
3. database
4. cache/queue
5. vector or knowledge store
6. runtime artifacts
7. prompt / policy config

## Environment Matrix

### Code

- `controller-dev`:
  - mutable
- `sandbox-evolution`:
  - mutable but isolated
- `staging-runtime`:
  - candidate-only
- `prod-runtime`:
  - release-only

### Database

- dev DB must not be reused as prod DB
- staging DB must not be reused as prod DB
- evolution runs must not write prod DB

### Redis / Queue / Cache

- dev Redis must not be reused as prod Redis
- staging cache must not silently share prod keys
- local operational noise must not pollute production decision signals

### Knowledge / Memory

- experiment knowledge ingestion must not directly contaminate production truth
- reviewed memory promotion must be explicit
- controller truth and experimental notes must remain distinct

## Current Project Mapping

This is the current practical baseline, not the finished target architecture:

1. `controller-dev`
   - `D:\code\MyAttention`
2. `sandbox-evolution`
   - `D:\code\_agent-runtimes\openclaw-workspaces\...`
   - `D:\code\_agent-runtimes\claude-worker\runs`
3. `staging-runtime`
   - target state still to be formalized
4. `prod-runtime`
   - should remain separate from both of the above

## Immediate Rules

Effective immediately:

1. delegated agents must not use the shared controller root as their default
   mutable workspace
2. no self-evolution lane may directly change production services
3. no local experiment should be treated as accepted until it is archived into:
   - docs
   - git
   - or canonical runtime storage
4. staging and production must be treated as separate promotion targets, not
   aliases for the same local machine state

## What This Solves

This strategy is meant to stop a specific failure mode:

- a system that starts fast
- evolves by direct mutation
- accumulates mixed truths
- then can no longer prove what is stable, what is experimental, and what can
  be rolled back

IKE must not operate that way.
