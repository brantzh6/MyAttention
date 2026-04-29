# IKE Review Automation P2 Real L1 Operational Smoke Packet

Date: 2026-04-29

## Status

- lifecycle stage: Testing
- project level: L2
- project type: C
- default risk: R2
- controller owner: main controller
- execution owner: delegated worker

## Purpose

Verify that the accepted P1 review runner can launch a real L1 delegated review path without requiring an external manual review packet.

## Context

P1 accepted:

- `--execute none|qoder|openclaw`
- default prepare-only behavior
- no-write/no-delegate `--dry-run`
- bounded delegated execution through `--delegate-timeout`
- attempt-only done metadata

The remaining gap is operational: real qoder/openclaw execution was intentionally not claimed as verified.

## Goal

Run one bounded real L1 operational smoke using `scripts/review/run_l1_review.py`.

Preferred lane:

1. qoder, if it can return safely in the current environment
2. openclaw, if qoder is blocked and openclaw can return safely
3. no fallback patch unless wrapper contract drift is discovered

## Non-Goals

- Do not change product backend/frontend code.
- Do not change visual control surface UI files.
- Do not change `AGENTS.md`.
- Do not create L3 external zip packages.
- Do not treat reviewer output as promotion truth.
- Do not broaden the runner into a scheduler or persistent orchestration service.

## Allowed Writes

Allowed write scope:

- `.runtime\reviews\briefs\IKE_REVIEW_AUTOMATION_P2_REAL_L1_SMOKE.*`
- `.runtime\reviews\contexts\IKE_REVIEW_AUTOMATION_P2_REAL_L1_SMOKE.*`
- `.runtime\reviews\results\IKE_REVIEW_AUTOMATION_P2_REAL_L1_SMOKE.*`
- `.runtime\reviews\done\IKE_REVIEW_AUTOMATION_P2_REAL_L1_SMOKE.*`
- `D:\code\MyAttention\docs\IKE_REVIEW_AUTOMATION_P2_REAL_L1_OPERATIONAL_SMOKE_RESULT_2026-04-29.md`

If a code patch is required, stop and report blocker unless the issue is a clearly bounded wrapper contract drift inside:

- `D:\code\MyAttention\scripts\review\run_l1_review.py`
- `D:\code\MyAttention\scripts\review\README.md`

## Required Smoke Command

Run this first:

```powershell
python D:\code\MyAttention\scripts\review\run_l1_review.py `
  --cwd D:\code\MyAttention `
  --task-id IKE_REVIEW_AUTOMATION_P2_REAL_L1_SMOKE `
  --title "P2 real L1 operational smoke" `
  --target-brief docs\IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_PACKET_2026-04-29.md `
  --target-result docs\IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_RESULT_2026-04-29.md `
  --target-file scripts\review\run_l1_review.py `
  --target-file scripts\review\README.md `
  --validation "controller P1 validation passed" `
  --execute qoder `
  --delegate-timeout 1800
```

If qoder cannot be used safely, record the blocker and optionally try:

```powershell
python D:\code\MyAttention\scripts\review\run_l1_review.py `
  --cwd D:\code\MyAttention `
  --task-id IKE_REVIEW_AUTOMATION_P2_REAL_L1_SMOKE `
  --title "P2 real L1 operational smoke" `
  --target-brief docs\IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_PACKET_2026-04-29.md `
  --target-result docs\IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_RESULT_2026-04-29.md `
  --target-file scripts\review\run_l1_review.py `
  --target-file scripts\review\README.md `
  --validation "controller P1 validation passed" `
  --execute openclaw `
  --delegate-timeout 1800
```

## Acceptance Criteria

- Runner creates the expected `.runtime\reviews` artifact set.
- Delegate execution is attempted exactly once unless the first lane is blocked before launch.
- Done JSON records `delegate_attempted`, `delegate_command`, and `delegate_exit_code`.
- Non-zero delegate exit code is reported as smoke failure, not hidden.
- No L3 external zip is created.
- No product code is changed.

## Required Result

Create:

- `D:\code\MyAttention\docs\IKE_REVIEW_AUTOMATION_P2_REAL_L1_OPERATIONAL_SMOKE_RESULT_2026-04-29.md`

Include:

- summary
- command_run
- artifacts_created
- delegate_attempt_evidence
- wrapper_exit_code
- reviewer_output_status
- files_changed
- blocker_or_failure_if_any
- known_risks
- recommendation: `accept`, `accept_with_changes`, or `reject`
