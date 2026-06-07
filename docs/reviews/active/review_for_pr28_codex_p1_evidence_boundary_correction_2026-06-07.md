# Review: PR #28 Codex P1 Evidence Boundary Correction

Date: 2026-06-07
Reviewer: ike-reviewer (independent)
Target worktree: `D:/code/MyAttention/.claude/worktrees/l5-save-state-pkg`

## Findings

### Q1: Are all false claims that active state/runtime files exist in the PR/base removed?

**PASS.** All false claims removed:

- Removed false claim that `ops/state/current_state.json` and `ops/runtime/latest.json` exist unchanged in the base (deleted lines 62-70 from original result file)
- New section "External controller-workspace evidence (NOT in PR package)" correctly states both files are "absent from base and PR"
- Absorption file adds clarifying finding: "Controller workspace state (`ops/state/current_state.json`, `ops/runtime/latest.json`) was external evidence for controller decision-making, NOT PR package contents."
- Grep search confirms no remaining false claims about these files being in the base/package

### Q2: Is the distinction between Git package evidence, controller-workspace accepted state, and ephemeral runtime truth now correct?

**PASS.** Distinction is now explicit:

- `ops/state/current_state.json` labeled as "controller-owned mutable operational truth"
- `ops/runtime/latest.json` labeled as "observed ephemeral runtime truth"
- Both marked "absent from base and PR"
- Note clarifies: "They are NOT included in or validated from the PR package"
- Validation note states: "JSON parsing and controller-gate checks were performed against controller workspace files, NOT PR package files"

### Q3: Are file counts and validations factual?

**PASS.** Counts and validations corrected:

- Total allowed scope files changed from (12) to (10)
- Entries 4 and 5 (the false state file claims) removed from numbered list
- Remaining entries correctly re-numbered 1-10
- Validation table: removed false JSON parsing and controller-gate checks against PR files
- Added validation check: "`git ls-tree -r --name-only HEAD` confirms no active state files" [PASS]
- Note clarifies external evidence vs package validation boundary

### Q4: Is the changed scope limited to authorized correction files?

**PASS.** Git status confirms:

| File | Expected | Status |
|------|----------|--------|
| `tasks/codex/isolated_origin_main_l5_milestone_save_state_result_2026-06-07.md` | Allowed | Modified |
| `tasks/codex/isolated_origin_main_l5_milestone_save_state_absorption_2026-06-07.md` | Allowed | Modified |
| `tasks/codex/pr28_codex_p1_evidence_boundary_correction_result_2026-06-07.md` | Allowed (new result) | Untracked |

All three match the "Allowed Files" section in the correction packet. No other files changed.

### Q5: Does the package remain inspect-only and promotion-reviewable?

**PASS.** Inspect-only boundary preserved:

- Result file validation: "Milestone wording remains `inspect_only`" [PASS]
- Absorption file: "The package remains explicitly `inspect_only`"
- No source, runtime, or active state files added to the package
- `git ls-tree` confirms `ops/state/current_state.json` and `ops/runtime/latest.json` absent from HEAD
- Package contains only milestone evidence and protocol files

## Validation Gaps

None identified. The correction packet validation requirements were met:

- `git ls-tree -r --name-only HEAD` confirms both active state paths absent
- `git diff --check` passes (only LF/CRLF warnings)
- `git status --short` contains only allowed correction files
- No false claims about active state files in base/package
- No source, runtime, or active state file added

## Recommendation

**PASS.** Correction is complete, factual, and bounded. All five review questions answered satisfactorily. The correction properly separates Git package evidence from controller-workspace external evidence without altering the inspect-only package scope or adding unauthorized files.

Controller may proceed to next gate (GitHub/Codex re-review or commit authorization).