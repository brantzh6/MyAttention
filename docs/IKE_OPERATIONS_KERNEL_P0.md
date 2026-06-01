# IKE Operations Kernel P0

Date: 2026-05-20
Truth status: accepted with changes absorbed

## Purpose

This is the minimum local operations kernel required to keep IKE moving as a
verifiable product instead of a code-only project.

It is not a full IEF implementation.

## External Accepted Inputs

The runtime operator details are governed by:

- `docs/RUNTIME_OPERATOR_LOOP_PROTOCOL_2026-05-09.md`

That document is an external runtime protocol input to this P0 package. This
package does not replace it; it makes runtime state mandatory in the project
state machine.

## Source Of Truth

The current machine-readable state is:

- `ops/state/current_state.json`
- `ops/pm-runs/latest.json`

This file must be updated whenever the controller claims meaningful mainline
progress, runtime readiness, review absorption, or validation status.

## Core Rule

IKE progress is real only when it is visible in artifacts and gates:

- runtime evidence
- task packet
- result artifact
- independent review artifact
- test evidence
- controller absorption
- state update

Chat-only progress is not project truth.

Delegated execution artifacts are evidence. The controller must not silently
rewrite delegated result artifacts. If an artifact has encoding or formatting
defects, the issue must be recorded and corrected through a delegate, fixer, or
review lane.

Run the structural controller gate check before treating state as accepted:

```powershell
python scripts/ops/check_controller_gate.py --claim accepted_project_truth
```

## State Sections

`current_state.json` must include:

- product state
- runtime state
- validation state
- governance state
- runner state
- review state
- dirty tree state
- Hermes trigger state
- next controller action

Runtime state is mandatory. IKE is an evolving product, not just source code.

## Runtime Gate

Before product validation, the controller must consume fresh runtime evidence.

Two layers are required:

1. Reachability: API/Web/routes respond.
2. Product runtime: the intended user path behaves correctly.

HTTP 200 is not product proof.

## Validation Gate

Validation levels:

- L0 static/syntax/type/build
- L1 unit
- L2 API contract
- L3 live runtime integration
- L4 browser UI smoke
- L5 end-to-end product scenario
- L6 manual or external milestone review

For current mainline product claims:

- L4 is the minimum evidence for UI path usability.
- L5 is required before saying the flywheel is genuinely usable end to end.

## Artifact Quality Gate

All task packets, result artifacts, review artifacts, and absorption artifacts
must satisfy:

- UTF-8 text
- no mojibake markers such as `â`, `�`, or corrupted arrows
- ASCII punctuation by default
- no non-ASCII punctuation unless the packet explicitly requires it
- no PowerShell text output used to author project files

Reviewer duties include checking artifact quality. Encoding defects are not
controller cleanup chores; they are execution or review findings.

Active JSON control-plane artifacts (`ops/state/observed_state.json`,
`ops/state/pm_control_state.json`, `ops/runtime/latest.json`, and all
bridge run JSON files) must be written as UTF-8 without BOM. The shared
helper `scripts/ops/ops_encoding_helpers.ps1` provides `Write-JsonUtf8NoBom`;
delegated state writers must use it or equivalent `[System.Text.UTF8Encoding]`
with BOM disabled and must validate no leading `EF BB BF`.

Live `/control` marker check is required for Web health classification:
the runtime probe must verify that `/control` returns HTTP 200 containing
both `file_derived` and `PM Watch Digest` markers. Web status is `healthy`
only when both root `/` and `/control` satisfy their respective conditions.
Missing markers or unreachable `/control` -> `degraded`.

## Runner Registry



Runner truth is stored in:

- `ops/runners/registry.json`

Runners are execution surfaces, not controllers. Every runner must use an
IKE-specific agent profile and bounded task packet.

Unvalidated runners may be listed for planning, but they cannot be used for
unattended IKE work until a separate runner validation packet records evidence.

## Hermes Boundary

Hermes is backup trigger-only. The preferred local project-management operator
is OpenClaw `ike-pm`.

Allowed:

- read state
- detect stalls
- write `ops/triggers/*.json`

Forbidden:

- task authoring
- GitHub issue or PR creation for IKE tasks
- source edits
- review absorption
- promotion decisions
- priority changes

Hermes must not rely on long-term memory. Its IKE behavior is defined by:

- `ops/agents/hermes-ike-trigger.md`

## OpenClaw PM And Runtime Operators

OpenClaw is the preferred local operations surface for IKE:

- `ike-pm`: project coordinator, progress/gate auditor, and blocker escalator
- `ike-operator`: runtime readiness operator

These agents have isolated OpenClaw workspaces:

- `D:\code\_agent-runtimes\openclaw-workspaces\ike-pm`
- `D:\code\_agent-runtimes\openclaw-workspaces\ike-operator`

Their repo-side contracts are:

- `ops/agents/openclaw-ike-pm.md`
- `ops/agents/openclaw-ike-operator.md`

Their workspace-side contracts are:

- `D:\code\_agent-runtimes\openclaw-workspaces\ike-pm\AGENTS.md`
- `D:\code\_agent-runtimes\openclaw-workspaces\ike-operator\AGENTS.md`

OpenClaw `ike-pm` is not a passive trigger-only watchdog. It coordinates the
project control loop by judging whether progress is real, whether the current
next action is actionable, whether gates are coherent, and whether a blocker
requires controller consultation. It must not decide the solution itself when a
controller decision or authorization is required.

OpenClaw `ike-pm` may write only PM coordination evidence and controller
triggers:

- `ops/pm-runs/latest.json`
- `ops/pm-runs/history/openclaw_pm_run_*.json`
- `ops/triggers/openclaw_pm_*.json`

PM run digests are operational evidence only. They make automation health,
project progress, blockers, and coordination needs visible to the controller
and `/control`; they do not decide promotion or task scope.
OpenClaw `ike-operator` may write only packet-specified runtime result
artifacts.

Neither OpenClaw agent may author tasks, accept reviews, decide promotion, or
change mainline priorities. When `ike-pm` finds a blocker, it asks Codex to
decide or authorize the resolution path; it does not silently choose one.

## OpenClaw To Codex Bridge

OpenClaw `ike-pm` does not just write a passive trigger. When a coordination
condition is met, it must call the approved bridge:

```powershell
python D:\code\MyAttention\scripts\ops\openclaw_codex_bridge.py --mode wake --detached --source openclaw-ike-pm --reason <reason> --trigger <trigger_path>
```

The bridge invokes `codex exec` with the controller wakeup prompt:

- `ops/codex/controller_wakeup_prompt.md`

The bridge owns:

- Codex process invocation
- detached dispatch for cron-safe handoff
- controller lease handling
- duplicate-run prevention
- trigger dispatch status
- bridge run metadata under `ops/bridge/runs/`
- trigger validation against `ops/schemas/openclaw_pm_trigger_v1.schema.json`

Lease files:

- `ops/state/codex_controller_lease.json`
- `ops/state/codex_controller_lease.lock`

If the controller lease is active, the bridge must not start a second Codex
run. It records `busy` and leaves the trigger available for a later run.

Escalation policy:

- 3 consecutive `deferred_busy` bridge results for the same trigger, or
- a trigger older than 12 hours that has not reached `dispatched`

In either case, `ike-pm` may emit `controller_bridge_escalation`, but the bridge
must still respect the active controller lease.

Codex completion must write a controller result artifact under `tasks/codex/`
and update `ops/state/current_state.json` when real project progress occurs.

## Agent Profiles

IKE-specific profiles:

- `ops/agents/hermes-ike-trigger.md`
- `ops/agents/openclaw-ike-pm.md`
- `ops/agents/openclaw-ike-operator.md`
- `ops/agents/ike-runtime-operator.md`
- `ops/agents/ike-test-runner.md`
- `ops/agents/ike-reviewer.md`
- `ops/agents/ike-ui-worker.md`
- `ops/agents/ike-coding-worker.md`

Do not mix these responsibilities into a generic main-agent persona.

## Hard Gates

1. No runtime state, no product validation claim.
2. No task packet, no delegated execution.
3. No independent review, no controller absorption.
4. No test artifact, no completion claim.
5. No L4/L5 evidence, no UI/product closure claim.
6. Dirty tree degraded means no new feature coding.
7. Hermes triggers wake the controller; they do not decide work.
8. `accepted_project_truth` claims must pass `scripts/ops/check_controller_gate.py`.
9. No accepted delegated result with unresolved artifact-quality defects.

## Current Accepted Boundary

This operations kernel P0 has been independently reviewed and absorbed.

Accepted review artifacts:

- `docs/reviews/active/review_for_operations_kernel_p0_2026-05-20.md`
- `docs/reviews/active/review_for_operations_kernel_p0_recheck_2026-05-20.md`
- `tasks/codex/operations_kernel_p0_absorption_2026-05-20.md`

Remaining future work:

- integrate `scripts/ops/check_controller_gate.py` into a hook or CI job
- define escalation when Hermes triggers are ignored
- validate Gemini and Qoder runner activation packets
- add live-runtime L3 and product E2E L5 validation for the Flywheel V1 path
