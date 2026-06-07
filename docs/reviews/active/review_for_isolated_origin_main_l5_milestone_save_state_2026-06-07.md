# Review: Isolated Origin/Main L5 Milestone Save-State Package

Date: 2026-06-07
Reviewer: IKE reviewer (independent)
Review Packet: `tasks/codex/isolated_origin_main_l5_milestone_save_state_review_packet_2026-06-07.md`
Target: `tasks/codex/isolated_origin_main_l5_milestone_save_state_result_2026-06-07.md`

## Findings

### HIGH: "Staged" Claim is False

**Location**: Result line 82

**Finding**: The result states "Package is **staged** but NOT committed." This is factually incorrect. Verification shows:

- `git diff --cached --name-only` returns empty output (0 files)
- `git status --porcelain` shows 10 files, all unstaged:
  - 2 unstaged modifications (` M`)
  - 8 untracked files (`??`)

**Why this matters**: A "staged" claim implies files are in the Git index ready for commit. The actual state shows nothing has been added to the index. The package is prepared but unstaged.

**How to apply**: Controller must correct the result artifact to state "Package is prepared but NOT staged or committed" and ensure future results accurately reflect Git state.

### HIGH: Exclusions Verification Incorrect

**Location**: Result lines 72-76

**Finding**: The result claims excluded files are "NOT present":

```
- `config/runtime/local-process.local.toml` - NOT present ✓
- `services/api/config.py` - NOT present ✓
```

Verification shows these files ARE present in the worktree:

- `Test-Path config/runtime/local-process.local.toml` → "EXCLUDED PRESENT"
- `Test-Path services/api/config.py` → "EXCLUDED PRESENT"

However, `git status --porcelain` shows no modifications to these files, meaning they exist unchanged from the base (`origin/main`).

**Why this matters**: The packet exclusion rule means "do not modify these files in the package" not "ensure these files don't exist." Since they exist in `origin/main` and are unchanged, the correct statement is "present in base, unchanged" not "NOT present."

**How to apply**: Controller must correct the result to accurately describe excluded file state as "present in base, unchanged from origin/main."

### MEDIUM: File Count Discrepancy

**Location**: Result line 42-54

**Finding**: The result claims "Total allowed scope files (12)" but the numbered list shows only items 1-11. Item 12 is missing.

Actual count from packet allowed scope: 11 files listed in packet section "Allowed Package Scope."

The 12 count appears to be an arithmetic error or miscount.

**How to apply**: Controller must correct the count to 11 or explain the 12th file if it exists elsewhere.

### LOW: Git Status Output Incomplete

**Location**: Result lines 28-38

**Finding**: The quoted `git status` output shows 8 files but actual status shows 10 files. The result artifact itself (`tasks/codex/isolated_origin_main_l5_milestone_save_state_result_2026-06-07.md`) is present in the worktree but omitted from the quoted status.

**How to apply**: The quoted output should match actual `git status` or explicitly note "excluding result artifact."

### NO ISSUE: Checkmark Encoding

**Location**: Throughout result file

**Finding**: The review packet asked to assess "mojibake checkmark sequences." Verification shows:

- All ✓ characters are proper Unicode U+2713 (UTF-8 encoding: E2 9C 93)
- No corrupted byte sequences detected
- No mojibake patterns (e.g., "âœ", "âœ"")

The checkmarks are valid UTF-8, not mojibake.

## Validation Gaps

| Check | Status | Gap |
|-------|--------|-----|
| Worktree based on `origin/main` | PASS | None |
| Four merge commits ancestors | PASS | Verified via `git merge-base --is-ancestor` |
| `git diff --check` | PASS | LF/CRLF warnings only |
| JSON parsing `current_state.json` | PASS | None |
| JSON parsing `latest.json` | PASS | None |
| Controller gate script | PASS | None |
| `inspect_only` claim preserved | PASS | Verified in codebase and result |
| "Staged" claim verification | FAIL | **0 files staged, contradicts result** |
| Excluded file presence | FAIL | **Files present but result claims "NOT present"** |

## Governance Gaps

1. **Result artifact accuracy**: The result contains factual inaccuracies about Git state (staging status, file presence) that contradict observed evidence. Per AGENTS.md, review output is evidence for the controller, and inaccurate evidence can mislead controller decisions.

2. **Output contract violation**: The result violates the AGENTS.md output contract requirement for accurate evidence. Findings must be correct; recommendation must be grounded in observed state.

3. **No independent review blocking**: Per Hard Rule 2 ("No independent review, no controller absorption"), the controller should not absorb this package until the result artifact is corrected.

## Positive Observations

1. **Correct base**: Worktree is correctly based on `origin/main` (commit `c5a060b`).

2. **Merge commits verified**: All four required merge commits (`e0c3a4c`, `b451a77`, `339fdcc`, `c5a060b`) are ancestors of `origin/main`.

3. **No excluded dirty-tree modifications**: Excluded files exist in base but are unchanged. The packet correctly excludes modifications to those files, not their existence.

4. **Scope bounded**: Only allowed package files are present in the working tree modifications/untracked set.

5. **`inspect_only` preserved**: The milestone wording is explicitly `inspect_only` throughout the package. No merge, release, or promotion authorization is implied.

6. **Stop condition honored**: The package stopped before commit, push, PR, or merge as required by the packet.

## Recommendation

**REJECT for absorption until artifact corrected.**

The package scope and isolation are correct, but the result artifact contains factual inaccuracies that violate the output contract. The controller must:

1. Correct the "staged" claim to "prepared, not staged"
2. Correct the excluded file descriptions to "present in base, unchanged"
3. Correct the file count from 12 to 11
4. Update the quoted git status to match actual output

After correction, re-review should pass and controller may proceed with absorption per a separate controller packet.

---

**Reviewer status**: Read-only review complete. Stopped per packet instructions. No edits to source, package, result, Git, branches, or runtime.