# IKE Review Automation P1 Execution Bridge Packet

Date: 2026-04-29

## Status

- lifecycle stage: Design
- project level: L2
- project type: C
- default risk: R2
- review cadence: L1 delegated review after implementation
- controller owner: main controller
- implementation owner: delegated worker

## Purpose

P0 made review artifacts deterministic, but it still stops at printed commands.

P1 should make the L1 path operational enough for daily SDLC use without returning to frequent manual external review packets.

## Problem

The current runner can prepare:

- canonical local review request
- context packet
- result placeholder
- done metadata
- qoder/openclaw command hints

It does not yet:

- execute a selected review delegate
- record whether execution was attempted
- distinguish prepared-only from executed review runs
- provide a reliable controller status summary

This keeps the review lane partially manual and slows daily development.

## Goal

Add a bounded execution bridge to the existing review runner so a controller can choose:

- `prepare` only
- `execute qoder`
- `execute openclaw`

The runner must remain conservative: it may launch the delegate wrapper, but it must not promote, accept, or rewrite reviewer output.

## Non-Goals

- Do not create L3 external zip packaging.
- Do not call web review services.
- Do not change `AGENTS.md`.
- Do not change product backend or frontend behavior.
- Do not implement GitHub PR creation or Codex PR review in P1.
- Do not auto-resolve findings.
- Do not make reviewer output authoritative without controller review.

## Allowed Files

Implementation scope is limited to:

- `D:\code\MyAttention\scripts\review\run_l1_review.py`
- `D:\code\MyAttention\scripts\review\README.md`
- `D:\code\MyAttention\docs\IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_RESULT_2026-04-29.md`

If another file is needed, stop and report before editing.

## Required Design

Add an explicit execution mode, for example:

- `--execute none`
- `--execute qoder`
- `--execute openclaw`

Default must remain no execution.

Expected behavior:

- `--dry-run` never writes files and never executes delegates.
- `--execute none` writes artifacts only.
- `--execute qoder` writes artifacts, then invokes the existing qoder delegate wrapper with the generated brief/context/result/done paths.
- `--execute openclaw` writes artifacts, then invokes the existing openclaw delegate wrapper with the generated brief path.
- all delegate process results are captured into controller-readable status output.
- non-zero delegate exit code returns non-zero from the runner.
- the runner does not parse reviewer judgment as promotion.

## Done Metadata

The done JSON should continue to exist and add only minimal status fields such as:

- `status`
- `execute`
- `delegate_attempted`
- `delegate_command`
- `delegate_exit_code`

Do not make the JSON a new source of runtime truth beyond review artifact identity and attempt status.

## Acceptance Criteria

- L1 prepare-only behavior remains backward compatible.
- `--dry-run --execute qoder` prints intent but does not execute.
- invalid execution mode is rejected by argparse.
- qoder and openclaw commands still match their wrapper `--help` interfaces.
- successful prepare-only run creates the same artifact set as P0.
- delegated execution failure returns non-zero and leaves artifacts for diagnosis.
- README documents prepare-only and delegated execution modes.

## Required Validation

Run:

```powershell
python D:\code\MyAttention\scripts\review\run_l1_review.py --help
python D:\code\MyAttention\scripts\review\run_l1_review.py --cwd D:\code\MyAttention --task-id IKE_REVIEW_AUTOMATION_P1_PREPARE_SMOKE --title "P1 prepare smoke" --target-brief docs\IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_PACKET_2026-04-29.md --target-result docs\IKE_REVIEW_AUTOMATION_P0_RESULT_2026-04-29.md --validation "prepare smoke" --dry-run
python D:\code\MyAttention\scripts\review\run_l1_review.py --cwd D:\code\MyAttention --task-id IKE_REVIEW_AUTOMATION_P1_DRY_EXECUTE_SMOKE --title "P1 dry execute smoke" --target-brief docs\IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_PACKET_2026-04-29.md --target-result docs\IKE_REVIEW_AUTOMATION_P0_RESULT_2026-04-29.md --execute qoder --dry-run
python -m py_compile D:\code\MyAttention\scripts\review\run_l1_review.py
```

If real delegate execution is available in the worker environment, also run one bounded qoder execution against this packet. If not available, report it as a blocker or known risk, not as a fake success.

## Required Result Format

The delegated worker must create:

- `D:\code\MyAttention\docs\IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_RESULT_2026-04-29.md`

The result must include:

- summary
- files_changed
- why_this_solution
- validation_run
- delegation evidence or blocker
- known_risks
- recommendation: `accept`, `accept_with_changes`, or `reject`

## Controller Review Rule

After implementation, run L1 delegated review by default using the review automation path. Do not request manual external review unless the implementation broadens scope, changes review authority boundaries, or touches runtime/promotion semantics.
