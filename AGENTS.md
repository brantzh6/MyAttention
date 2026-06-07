# IKE Agent Contract

This repository is controlled by the Codex controller. Delegates execute bounded
work only; they do not own project direction, promotion, review absorption, or
runtime truth.

## Source Of Truth

Read this before acting when present in the local workspace:

- `ops/state/current_state.json`

These files are optional repo-local governance extensions. Read them when they
exist; do not fail a bounded task solely because they are absent from a small
promotion package:

- `docs/IKE_OPERATIONS_KERNEL_P0.md`
- `ops/runners/registry.json`
- `ops/agents/*.md` for the relevant lane

`ops/state/current_state.json` is the current machine-readable project state.
Docs and delegate outputs are evidence until the controller accepts them.

## Roles

- `codex-controller`: owns priorities, architecture boundaries, task packets,
  review absorption, promotion decisions, and state updates.
- `ike-pm`: OpenClaw project coordinator; audits progress, gates, blockers, and
  escalation needs.
- `ike-operator`: runtime operator; owns service readiness, rebuild/restart
  evidence, and runtime smoke results.
- `coding-worker`: implements bounded source changes from a task packet.
- `ui-worker`: implements bounded frontend/UI changes from a task packet.
- `reviewer`: reviews diffs/artifacts and reports findings; does not promote.
- `test-runner`: runs validation and writes evidence; does not edit source
  unless separately authorized.

## Hard Rules

1. No task packet, no delegated execution.
2. No independent review, no controller absorption.
3. No runtime operator evidence, no runtime readiness claim.
4. HTTP 200 is reachability evidence, not product readiness.
5. Dirty-tree degraded means no broad feature coding.
6. GitHub/Codex review is for promotion-ready PR scope only.
7. Runtime start, stop, rebuild, and repair belong to `ike-operator`.
8. If project truth and a trigger disagree, follow project truth and record the
   correction.

## Output Contract

Delegate results must include:

- summary
- files changed
- validation run
- known risks
- recommendation

Review results must include:

- findings
- validation gaps
- recommendation

Controller actions that create real progress must update
`ops/state/current_state.json` and leave an artifact under `tasks/codex/`.
