# /control Live Ops-State Pre-PR Runtime Validation

Task ID: control_live_ops_state_pre_pr_runtime_validation_2026_05_27
Operator: ike-operator
Date: 2026-05-27 10:41 GMT+8
Worktree: D:\code\_worktrees\MyAttention-control-live-ops-state
Branch: codex/control-live-ops-state-2026-05-27
Changed file: services/web/lib/control-surface/ops-state-adapter.ts

---

## 1. Summary

The ops-state-adapter.ts fix was built and exercised in the isolated worktree. After building, starting the Next standalone server on port 3002, and probing /control, the page renders live-derived data from ops/state/current_state.json instead of the previous STATIC_SNAPSHOT fallback. All three expected signals are present: Source Kind shows "file_derived" (not "manual_curated"), Provenance Source Label reads "Ops State Sync (from codex-controller)", and the "PM Watch Digest" section is visible with the latest PM run digest. No server or render errors were observed. Verdict: accept.

## 2. Commands Run

1. `cd D:\code\_worktrees\MyAttention-control-live-ops-state; git branch --show-current` -- confirmed branch `codex/control-live-ops-state-2026-05-27`
2. `git diff --stat HEAD` -- 1 file changed, 25 insertions, 22 deletions in ops-state-adapter.ts
3. `git diff HEAD -- services/web/lib/control-surface/ops-state-adapter.ts` -- reviewed the full diff
4. Copied `ops/state/current_state.json` and `ops/pm-runs/latest.json` from main repo into the worktree
5. `npm --prefix services/web run build` -- build succeeded, /control listed as dynamic (141 B)
6. `node .next/standalone/server.js` with PORT=3002 -- server started, ready in 86ms
7. `Invoke-WebRequest http://127.0.0.1:3002/control` -- 200 OK, full HTML content verified
8. `Invoke-WebRequest http://127.0.0.1:3002/chat` -- 200 OK
9. `Invoke-WebRequest http://127.0.0.1:3002/evolution` -- 200 OK
10. `Invoke-WebRequest http://127.0.0.1:8000/health` -- 200 OK

## 3. Validation Evidence

### /control live-derived rendering confirmed

The rendered HTML from the worktree server contains these signals:

| Expected Signal | Expected Value | Observed | Match |
|----------------|---------------|----------|-------|
| Source Kind | file_derived | `file_derived` | YES |
| Truth Status | derived | `derived` | YES |
| Source Label | Ops State Sync | `Ops State Sync (from codex-controller)` | YES |
| Provenance caveat | derived from ops/state/current_state.json | `Derived from ops/state/current_state.json. Status is accepted_project_truth but UI presentation is derived.` | YES |
| PM digest visible | "PM Watch Digest" section present | Section renders with decision "monitoring", status "caveat", checked_at "2026-05-27T10:25:00+08:00", staleness 173 min, 11 evidence items | YES |
| Previous static fallback | manual_curated | NOT present | YES (correctly replaced) |

All three probes from the packet requirement are satisfied:
- "Ops State Sync" -- confirmed in Source Label
- "PM Watch Digest" -- confirmed as rendered section with full digest data
- Source kind behavior -- "file_derived", derived from current_state.json, not static

### Route probes

| Route | Status | Notes |
|-------|--------|-------|
| /control | 200 | Live ops-state data rendered |
| /chat | 200 | Unchanged |
| /evolution | 200 | Unchanged |
| /health (API) | 200 | {"status":"healthy","version":"0.1.0"} |

### Code change reviewed (ops-state-adapter.ts diff)

Two categories of fix in the diff:

1. **Standalone cwd resolution**: Added detection for Next.js standalone mode. When cwd is `.../.next/standalone`, the adapter now resolves repo root as 4 levels up (`standalone/.next/web/services/repo-root`). This was added to both `resolveOpsStatePath()` and `resolveRepoPath()`.

2. **Graceful degradation**: Removed hard-fail guards for `validation_state` (not in current_state.json), and changed `dirty_tree_state` and `next_action` from required-fail to optional. The snapshot construction now conditionally includes `operationsSplit` (undefined if dirtyTree is missing) and `nextActions` (empty array if nextAction is missing) rather than returning null.

The current_state.json in the worktree contains all required fields plus the optional ones that were previously causing fallback (dirty_tree_state, next_action). The adapter now reads and renders them correctly.

## 4. Runtime Errors

No errors observed. The Next standalone server started cleanly, no stderr output, no console.error messages in server logs, and the rendered HTML contains no error indicators.

## 5. Verdict

**accept**

The ops-state-adapter fix achieves its goal: /control renders file_derived live data from ops/state/current_state.json with PM digest visible. The two changes (standalone cwd resolution + graceful degradation for optional fields) are minimal, bounded, and do not alter product behavior beyond enabling the existing adapter to read ops state in the Next standalone execution context.

## 6. Controller Next Action

Promote the worktree branch to main via PR and rerun post-merge runtime validation to confirm live ops-state rendering survives the merge. Then run the integrated AI chat -> evolution -> /control product smoke as the next gate.
