# IKE Scoped GitHub/Codex Review Prep

Date: 2026-04-29

## Decision

Prepare a scoped GitHub/Codex review branch before continuing more product implementation.

## Why

The active worktree is not reviewable as a single unit:

- current branch: `codex/ike-visual-control-surface`
- dirty/untracked entries: approximately `161`
- mixed areas: review automation, flywheel backend/tests, source intelligence, evolution UI, historical docs, visual branch design

Pushing the full worktree would make Codex review low signal and would mix the visual-control branch with unrelated product and governance work.

## Scoped Review Candidate

Create a clean branch for the recent accepted mainline work:

- branch: `codex/ike-scoped-review-20260429`
- local base: `6578d55`
- GitHub PR base: `origin/codex/pre-ike-restructure-2026-04-09`
- review type: GitHub PR / Codex review

## Include

Review automation:

- `scripts/review/run_l1_review.py`
- `scripts/review/README.md`
- `docs/IKE_REVIEW_CADENCE_AND_AUTOMATION_POLICY_2026-04-29.md`
- `docs/IKE_REVIEW_AUTOMATION_P0_IMPLEMENTATION_PACKET_2026-04-29.md`
- `docs/IKE_REVIEW_AUTOMATION_P0_RESULT_2026-04-29.md`
- `docs/IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_PACKET_2026-04-29.md`
- `docs/IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_RESULT_2026-04-29.md`
- `docs/IKE_REVIEW_AUTOMATION_P2_REAL_L1_OPERATIONAL_SMOKE_PACKET_2026-04-29.md`
- `docs/IKE_REVIEW_AUTOMATION_P2_REAL_L1_OPERATIONAL_SMOKE_RESULT_2026-04-29.md`

Flywheel inspect decision readiness:

- `services/api/conversation_runtime/flywheel_inspect.py`
- selected readiness assertions in `services/api/tests/test_flywheel_inspect_route.py`
- dependency closure only: `services/api/feeds/source_contracts.py`
- dependency closure only: `services/api/feeds/ai_judgment.py`
- dependency closure only: `services/api/feeds/source_semantics.py`
- dependency closure only: `services/api/feeds/source_postprocess.py`
- `docs/IKE_FLYWHEEL_INSPECT_DECISION_READINESS_TAGS_P0_PACKET_2026-04-29.md`
- `docs/IKE_FLYWHEEL_INSPECT_DECISION_READINESS_TAGS_P0_RESULT_2026-04-29.md`

Controller handoff:

- scoped additions in `docs/CURRENT_MAINLINE_HANDOFF.md`

## Exclude

Do not include in this scoped push:

- broad historical docs not tied to the accepted 2026-04-29 nodes
- source-intelligence hardening files
- `services/web/components/evolution/*`
- visual-control UI implementation files
- execution-feedback / worker-return evidence implementation changes not part of the readiness node
- unrelated `deliverables/` or review-pack archives

## Review Gate

Proceed to GitHub/Codex review after:

1. clean worktree branch is created
2. selected files/patches are applied
3. target tests pass
4. diff is small enough to be reviewable
5. controller confirms no unrelated dirty files were copied into the branch

## Validation Target

Run:

```powershell
$env:PYTHONPATH='D:\code\MyAttention\services\api'
python -m pytest D:\code\MyAttention\services\api\tests\test_flywheel_inspect_route.py D:\code\MyAttention\services\api\tests\test_conversation_runtime_route.py
python D:\code\MyAttention\scripts\review\run_l1_review.py --help
python -m py_compile D:\code\MyAttention\scripts\review\run_l1_review.py
```

For source-intelligence dependency-closure validation, set a coding-endpoint shaped Qwen key explicitly instead of relying on local `.env`:

```powershell
$env:QWEN_API_KEY='sk-sp-test'
python -m pytest D:\code\MyAttention\services\api\tests\test_ai_judgment_substrate.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py
```

## Controller Rule

Do not push the mixed dirty worktree. Push only the clean scoped branch.
