# Controller Absorption: Post-L5 Milestone And Dirty Tree Audits

Date: 2026-06-07
Controller: codex-controller

## Decisions

### Milestone Package Audit

Decision: `accept_with_correction`

Accepted:

- The first usable L5 inspect-only milestone evidence chain is bounded.
- The current controller worktree is diverged and dirty.
- A promotion/save-state package must use an isolated clean branch/worktree.

Rejected finding:

- The audit claimed PRs #24-#27 are absent from `main`.
- The audit checked stale local `main` at `0bfc83f`.
- Canonical `origin/main` is at `c5a060b` and contains merge commits
  `e0c3a4c`, `b451a77`, `339fdcc`, and `c5a060b`.

Correction:

- Local `main` drift is a workspace maintenance issue.
- It is not a project-truth discrepancy and does not invalidate the accepted
  milestone.
- Reviewer protocol now requires separate local-main and origin-main checks.

### Dirty Tree Reduction Audit

Decision: `accept_with_changes`

Accepted:

- Dirty tree remains degraded with three tracked modifications and extensive
  untracked operations/evidence content.
- Broad cleanup or broad staging is forbidden.
- The product `services/api/config.py` change and its focused test form one
  plausible bounded package.

Rejected recommendation:

- Do not delete `data/`, screenshots, or broad generated/evidence patterns
  based only on naming. `data/` may contain runtime or user data, and evidence
  retention needs an explicit policy.

## Current Controller Decision

1. Preserve the accepted first usable L5 inspect-only milestone.
2. Treat `origin/main` as canonical Git main truth while recording local
   `main` drift.
3. Keep broad feature coding blocked.
4. Next, form one isolated clean promotion/save-state package for the accepted
   milestone and one separately reviewed product-source package for the
   database URL override.

## Validation

- `git merge-base --is-ancestor e0c3a4c origin/main`: passed
- `git merge-base --is-ancestor b451a77 origin/main`: passed
- `git merge-base --is-ancestor 339fdcc origin/main`: passed
- `git merge-base --is-ancestor c5a060b origin/main`: passed
- Current runtime evidence: `ops/runtime/latest.json` reports `all_healthy`

## Known Risks

- Local `main` remains stale because it is checked out in another worktree.
- The controller worktree remains heavily dirty.
- Evidence retention and ignore policy remain undefined.

## Recommendation

`accept_with_changes`
