# Result: /control Live Ops-State Adapter Fix

Task ID: `control_live_ops_state_adapter_fix_2026_05_27`
Date: 2026-05-27
Status: Code fix complete, build validated

## Summary

Fixed the ops-state adapter path resolution to handle Next.js standalone runtime cwd (`services/web/.next/standalone`) and added graceful degradation for optional state fields. The adapter now correctly finds `ops/state/current_state.json` and `ops/pm-runs/latest.json` in both local dev and production standalone modes.

## Root Cause

**Primary Issue**: The `resolveOpsStatePath()` and `resolveRepoPath()` functions only added the repo root path (`../..`) when cwd basename was exactly `web`. In Next.js standalone runtime:
- cwd is `services/web/.next/standalone` (basename = `standalone`)
- The condition `path.basename(cwd) === 'web'` fails
- The repo root (4 levels up) is never added to candidate roots
- State files are not found, causing full STATIC_SNAPSHOT fallback

**Secondary Issue**: Unused strict field guard for `validation_state` (checked but never used in snapshot construction) and strict guards for `dirty_tree_state` and `next_action` that could degrade gracefully instead of forcing total fallback.

## Files Changed

1. **services/web/lib/control-surface/ops-state-adapter.ts**
   - Added Next standalone cwd detection (lines 32-36, 84-88)
   - Removed unused `validation_state` guard (line 142 removed)
   - Made `dirty_tree_state` and `next_action` optional with graceful degradation (lines 157-159, 225-235)

## Validation Run

```
npm --prefix services/web run build
```

Result: **SUCCESS**
- Compiled successfully
- Linting and type checking passed
- Generated static pages (13/13)
- /control route is dynamic (ƒ) - correctly force-dynamic

## Known Risks

1. **Path detection assumes standard Next.js standalone layout**: The fix assumes cwd basename is `standalone` and parent basename is `.next`. Non-standard deployments may need env var `IKE_OPS_STATE_PATH` override.

2. **Graceful degradation hides missing optional fields**: If `dirty_tree_state` or `next_action` are missing, the UI will show empty sections instead of explicit error indicators. This is acceptable per packet requirement "degrades optional sections without hiding all live state".

3. **No runtime validation yet**: Build passes but actual runtime behavior needs controller validation after this work.

## Recommendation

1. **Runtime validation**: Controller should run ike-operator post-merge validation to confirm `/control` returns `file_derived` provenance when state files exist.

2. **Smoke test addition**: Consider adding a focused smoke script to verify path resolution in both local dev and standalone modes.

3. **Env var documentation**: Document `IKE_OPS_STATE_PATH` override for non-standard deployment scenarios.

## Code Changes Detail

### Path Resolution Fix

```typescript
// Next standalone: running from services/web/.next/standalone
if (path.basename(cwd) === 'standalone' && path.basename(path.dirname(cwd)) === '.next') {
  // standalone -> .next -> web -> services -> repo root (4 levels up)
  candidateRoots.push(path.resolve(cwd, '..', '..', '..', '..'))
}
```

### Graceful Degradation Fix

```typescript
// Optional fields - degrade gracefully if missing
const dirtyTree = state?.dirty_tree_state
const nextAction = state?.next_action

// In snapshot construction:
operationsSplit: dirtyTree ? { ... } : undefined,
nextActions: nextAction ? [ { lane: nextAction.owner, action: nextAction.action } ] : []
```

## Stop Condition Met

- Code fix implemented
- Build validation passed
- Result artifact written
- Ready for controller review and runtime validation