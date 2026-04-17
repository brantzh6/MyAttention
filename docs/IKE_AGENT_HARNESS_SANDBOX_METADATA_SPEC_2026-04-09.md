# IKE Agent Harness Sandbox Metadata Spec

Date: 2026-04-09
Status: accept_with_changes

## Purpose

Define the first machine-readable sandbox metadata shape for delegated runs.

This is a metadata-first phase.
It does not yet require broader execution-runtime redesign.

## Required Fields

Every delegated run should eventually carry:

- `sandbox_identity`
  - stable unique sandbox/workspace identifier
- `sandbox_kind`
  - `openclaw_workspace`
  - `claude_worker_run_root`
  - future kinds may be added explicitly
- `workspace_root`
  - actual mutable execution root for that run
- `runtime_root`
  - external runtime/artifact root when applicable
- `environment_mode`
  - `ephemeral`
  - `persistent_workspace`
  - `snapshot_based`
- `task_id`
  - if the run is tied to a runtime/controller task
- `run_id`
  - execution run identifier
- `lane`
  - `coding`
  - `review`
  - `testing`
  - `evolution`
- `model`
  - actual model used
- `reasoning_mode`
  - current thinking / reasoning mode when known

## Optional Fields

- `environment_snapshot_id`
- `result_root`
- `capability_profile`
- `write_scope`
- `network_policy`

## Current Planned Mapping

## Current P1 Landed Scope

The spec is no longer purely hypothetical.

Currently landed:

- Claude worker:
  - `lane`
  - `reasoning_mode`
  - `sandbox_identity`
  - `sandbox_kind`
  - `capability_profile`
  - `workspace_root`
  - `runtime_root`
  - `environment_mode`
- OpenClaw delegation entrypoints:
  - `lane`
  - `reasoning_mode`
  - `sandbox_kind`
  - `capability_profile`
- qoder bundle / launch chain:
  - `lane`
  - `reasoning_mode`
  - `sandbox_kind`
  - `capability_profile`

Still not fully landed:

- `write_scope`
- `network_policy`
- runtime-wide enforcement against these fields

## Current P3/P4 Landed Extension

The metadata vocabulary has now been extended further.

Currently also landed:

- `write_scope`
- `network_policy`

This means the current practical metadata set is now:

- `lane`
- `reasoning_mode`
- `sandbox_identity`
- `sandbox_kind`
- `capability_profile`
- `write_scope`
- `network_policy`
- `workspace_root`
- `runtime_root`
- `environment_mode`

Truthful boundary:

- these fields are now materially present
- full runtime enforcement against them is still future work

## Current P5 Identity Coverage

The first practical cross-lane `sandbox_identity` coverage is now materially
present across:

- Claude worker
- OpenClaw wrappers
- qoder chain

Current default identity shapes:

- Claude worker:
  - explicit packet/run identity
- OpenClaw:
  - `openclaw_workspace:<agent_alias>:<session>`
- qoder:
  - `qoder_workspace:<task_id>`

## Current Planned Mapping

### Claude worker

- `sandbox_kind = claude_worker_run_root`
- `workspace_root = packet.cwd`
- `runtime_root = external claude-worker root`
- `environment_mode = persistent_workspace`
- `lane = coding|review`

### OpenClaw

- `sandbox_kind = openclaw_workspace`
- `workspace_root = configured isolated workspace`
- `runtime_root = external agent-runtime root`
- `environment_mode = persistent_workspace`
- `lane = coding|review`

## Capability Profile Draft

Capability profiles should become explicit named values, for example:

- `coding_high_reasoning`
- `review_high_reasoning`
- `testing_bounded`
- `evolution_high_reasoning`

The profile should imply:

- expected tool access
- destructive command restrictions
- write policy
- network expectations

## Controller Judgment

This spec is intentionally narrow.

It is the safest next step because it:

- strengthens auditability
- creates a bridge from workspace isolation to true sandbox enforcement
- does not yet require a big runtime schema migration
