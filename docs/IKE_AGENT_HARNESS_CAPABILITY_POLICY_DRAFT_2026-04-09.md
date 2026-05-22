# IKE Agent Harness Capability Policy Draft

Date: 2026-04-09
Status: proposed

## Goal

Turn current lane behavior into explicit capability-policy intent.

This draft is not yet the final enforced configuration.
It is the controller baseline for the next hardening step.

## Lane Profiles

### `coding_high_reasoning`

Used for:

- OpenClaw coder
- Claude worker coding

Expected:

- high reasoning
- file read/write/edit within bounded workspace
- bounded shell execution
- validation commands allowed

Should be restricted against:

- broad repo-root mutation outside allowed workspace
- arbitrary destructive cleanup outside workspace/runtime root
- implicit environment reconfiguration
- unrestricted network access by default

### `review_high_reasoning`

Used for:

- OpenClaw reviewer
- OpenClaw kimi review
- Claude worker review

Expected:

- high reasoning
- read-heavy behavior
- structured result output
- optional bounded reproduction commands

Should be restricted against:

- arbitrary source edits unless explicitly allowed
- environment/package mutation
- broad destructive process commands
- unnecessary external network access

### `testing_bounded`

Used for:

- focused validation
- narrow suite execution

Expected:

- medium to high reasoning depending on packet
- bounded test execution
- log/result capture

Should be restricted against:

- broad workspace mutation
- unrelated service/process teardown

### `evolution_high_reasoning`

Used for:

- synthesis
- evolution guidance
- method-change proposals

Expected:

- high reasoning
- mostly read-only plus result writing

Should be restricted against:

- direct product/source mutation by default

## Current Truth

### OpenClaw

- reasoning support exists
- high thinking default exists
- isolated workspaces exist
- explicit lane capability policy is not yet durably enforced

### Claude worker

- run-root separation exists
- durable artifacts exist
- capability allowlist is still broad
- hardened capability policy remains future work

## Controller Rule

Do not describe current lane configuration as if these capability profiles are
already fully enforced.

Treat this draft as:

- the next hardening baseline
- not a completed security claim

## Current Metadata Baseline

The first policy-shaped metadata baseline is now materially present across the
main automated lanes.

Current named metadata fields:

- `capability_profile`
- `write_scope`
- `network_policy`

Current intended defaults:

- `coding_high_reasoning`
  - `write_scope = bounded allowed-write set`
  - `network_policy = restricted`
- `review_high_reasoning`
  - `write_scope = []`
  - `network_policy = disabled`

Truthful boundary:

- these values are currently policy intent and audit metadata
- they are not yet proof of hard runtime enforcement
