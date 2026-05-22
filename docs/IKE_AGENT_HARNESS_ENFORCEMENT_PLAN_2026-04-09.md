# IKE Agent Harness Enforcement Plan

Date: 2026-04-09
Status: proposed

## Purpose

Convert the current IKE harness from:

- role rules
- path isolation
- external run roots

into a stronger execution model with first-class:

- sandbox identity
- capability policy
- environment lifecycle
- runtime binding

## Current Truth

The current system is already directionally aligned:

- controller/delegate split is explicit
- OpenClaw workspaces are isolated
- Claude worker run-root is externalized
- runtime truth for task/decision/memory/work-context is explicit

But enforcement is still incomplete:

- per-run sandbox identity is not first-class
- execution capability policy is still too permissive
- environment lifecycle is not yet modeled separately from run truth
- runtime task lease is not strongly bound to actual execution sandbox

## Enforcement Targets

### 1. Sandbox Identity

Every delegated run should carry a machine-readable sandbox identity:

- `sandbox_kind`
- `sandbox_root`
- `workspace_root`
- `environment_snapshot_id` (if any)
- `task_id`
- `run_id`

This identity should be recorded in run artifacts and be available to the
controller.

### 2. Capability Policy

Each lane should have explicit capability policy:

- allowed tools
- disallowed tools
- write boundaries
- network policy
- destructive-command policy

This should be configured per lane, not implied by prompt text alone.

### 3. Environment Lifecycle

Separate these three things:

1. execution sandbox
2. reusable environment snapshot
3. runtime truth/state

Normal task execution should not silently mutate reusable environment truth.

### 4. Runtime Binding

Runtime task truth should eventually know:

- which sandbox executed the run
- which workspace was used
- which environment snapshot was used
- whether the run was delegated or controller-recovered

## Narrow Phase Sequence

### Phase A. Metadata hardening

- add sandbox identity fields to delegated run metadata
- expose them in durable result artifacts
- do not change execution behavior yet

### Phase B. Capability policy hardening

- define lane-level capability baselines for:
  - Claude worker coding
  - Claude worker review
  - OpenClaw coding
  - OpenClaw review
- remove or narrow broad defaults where possible

### Phase C. Environment lifecycle separation

- define a reusable environment snapshot concept
- keep ordinary task runs separate from environment-update runs

### Phase D. Runtime/task binding

- bind task/run/sandbox identity in runtime evidence
- keep this as metadata binding first, not broad schema expansion

## Non-Goals

- do not replace runtime truth with sandbox state
- do not widen current task/memory scope just because sandboxing is improved
- do not turn agent execution runtime into the controller

## Current Controller Judgment

This is the right next harness evolution after workspace isolation.

The next gain is not “more agents.”

It is:

- better bounded execution
- better auditability
- stronger truth about what actually ran, where, and under what permissions
