# IKE Review Automation P0 Implementation Packet 2026-04-29

## Purpose

Make the new review cadence operational.

This packet turns `IKE_REVIEW_CADENCE_AND_AUTOMATION_POLICY_2026-04-29.md` into a small implementation target without changing product runtime behavior.

## Problem

The project already has review/delegation scripts, but the workflow is still too manual:

- L1 daily review is not one-command enough
- L3 external review artifacts are overused because they are the most explicit path
- Qoder/OpenClaw review scripts exist but are not wrapped in a single project-level review lane
- GitHub/Codex review is not yet encoded as the stage-level default
- review absorption still relies too much on controller memory

## Existing Assets

Scripts already present:

- `D:\code\MyAttention\scripts\qoder\create_review_bundle.py`
- `D:\code\MyAttention\scripts\qoder\run_file_delegation.py`
- `D:\code\MyAttention\scripts\acpx\run_file_delegation.py`
- `D:\code\MyAttention\scripts\acpx\openclaw_delegate.py`

Role files already present:

- `D:\code\MyAttention\.qoder\agents\code-review-agent.md`
- `D:\code\MyAttention\.openclaw\agents\openclaw-kimi-review-agent.md`
- `D:\code\MyAttention\.qoder\agents\coding-agent.md`
- `D:\code\MyAttention\.openclaw\agents\openclaw-glm-coding-agent.md`

## P0 Goal

Create a project-level review runner design and minimal script surface for L1 review.

The first implementation should not orchestrate every model automatically. It should normalize the workflow so a controller can run one script to prepare and launch/record a bounded L1 review.

## Proposed Command Shape

Add a project-level script:

- `D:\code\MyAttention\scripts\review\run_l1_review.py`

Command:

```powershell
python D:\code\MyAttention\scripts\review\run_l1_review.py `
  --cwd D:\code\MyAttention `
  --task-id IKE_EXAMPLE_REVIEW `
  --title "Review bounded patch" `
  --target-brief docs\...md `
  --target-result docs\...md `
  --target-file services\api\...py `
  --validation "python -m pytest ..."
```

Outputs:

- `.runtime\reviews\briefs\<task-id>.md`
- `.runtime\reviews\contexts\<task-id>.md`
- `.runtime\reviews\results\<task-id>.md`
- `.runtime\reviews\done\<task-id>.json`

The runner may reuse `scripts/qoder/create_review_bundle.py` internally for the first version.

## P0 Behavior

The P0 runner should:

1. Create a canonical L1 review brief.
2. Create a context packet.
3. Create an empty result file.
4. Print next commands for available lanes:
   - Qoder code review lane
   - OpenClaw/Kimi review lane if configured
   - manual paste fallback
5. Record whether this is L1/L2/L3.
6. Refuse to create an L3 zip pack unless `--level L3` is explicitly provided.

## Non-Goals

- no backend API
- no UI
- no GitHub PR creation
- no fully automatic model fan-out
- no network automation
- no automatic acceptance
- no replacement of existing qoder/acpx scripts

## Required Files

Allowed implementation files:

- `scripts/review/run_l1_review.py`
- `scripts/review/README.md`
- optionally `scripts/review/__init__.py`

Allowed docs:

- `docs/IKE_REVIEW_AUTOMATION_P0_RESULT_2026-04-29.md`

Do not modify:

- product backend
- frontend UI
- existing qoder/openclaw role files unless a blocker requires it
- AGENTS.md

## Review Level Rules

The script must encode these defaults:

- default level: `L1`
- L1:
  - no zip
  - no external manual review packet
  - delegated review result is enough for controller review
- L2:
  - print GitHub PR/Codex review instructions
  - do not create external zip
- L3:
  - only when explicitly requested
  - create or point to external review package process
  - should remind user of the 10-entry zip rule

## Acceptance Criteria

- Can run without changing project product code.
- Creates deterministic UTF-8 Markdown/JSON review artifacts.
- Makes L1 the default and L3 explicit.
- Reuses or wraps existing review-bundle behavior instead of duplicating everything.
- Prints clear next commands for Qoder/OpenClaw/manual fallback.
- Includes a dry-run mode.

## Validation

Recommended validation:

```powershell
python D:\code\MyAttention\scripts\review\run_l1_review.py --help
python D:\code\MyAttention\scripts\review\run_l1_review.py `
  --cwd D:\code\MyAttention `
  --task-id IKE_REVIEW_AUTOMATION_SMOKE `
  --title "Smoke review automation" `
  --target-brief docs\IKE_REVIEW_CADENCE_AND_AUTOMATION_POLICY_2026-04-29.md `
  --target-result docs\IKE_REVIEW_AUTOMATION_P0_IMPLEMENTATION_PACKET_2026-04-29.md `
  --validation "no product code validation required" `
  --dry-run
```

## Expected Delegate Result

```text
summary:
files_changed:
why_this_solution:
validation_run:
known_risks:
recommendation: accept | accept_with_changes | reject
```

## Controller Judgment

Recommendation: proceed with L1 delegated implementation.

This is governance tooling, not product runtime. It can proceed in parallel with the Antigravity UI branch as long as it touches only `scripts/review/*` and the result doc.
