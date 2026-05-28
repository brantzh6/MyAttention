# PR14 Codex Feedback Absorption - Fallback Root Fix

Date: 2026-05-26
Owner: codex-controller
PR: https://github.com/brantzh6/MyAttention/pull/14

## Summary

GitHub/Codex re-review after commit `7a5fea2` returned a clean top-level comment,
but GraphQL review-thread inspection showed one remaining non-outdated P2 thread
in `services/web/lib/control-surface/ops-state-adapter.ts`.

The finding was valid: when `process.cwd()` is the repo root, the fallback list
also tried `../..`, which can escape to a host-level parent and read an unrelated
`ops/state/current_state.json`.

## Fix

Commit `bc54c74` constrains fallback root discovery:

- accepts `cwd` directly
- allows parent traversal only when `cwd` is explicitly `services/web`
- applies the same bounded-root rule to both ops-state and repo-relative file
  lookup

## Validation

Run from PR14 worktree:

```powershell
npm --prefix services/web run build
git diff --check
```

Result:

- Next.js build passed.
- `/control` remains dynamic in build output.
- `git diff --check` reported no whitespace errors.

## Re-review

Second re-review trigger:

- comment: https://github.com/brantzh6/MyAttention/pull/14#issuecomment-4542338740
- commit: `bc54c74`

## Recommendation

Do not merge PR14 until Codex re-review confirms both prior threads are outdated,
resolved, or otherwise non-actionable.
