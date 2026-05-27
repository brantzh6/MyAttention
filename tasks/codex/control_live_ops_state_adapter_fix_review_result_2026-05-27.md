# Review Result: /control Live Ops-State Adapter Fix

Task ID: control_live_ops_state_adapter_fix_review_2026_05_27
Reviewer: local Claude Code reviewer
Date: 2026-05-27

## 1. Findings

### Path Resolution (Question 1)

**ACCEPTABLE** - The fix uses bounded, specific cwd detection rather than broad filesystem walking.

The implementation adds a single new candidate root for Next.js standalone:
```typescript
if (path.basename(cwd) === 'standalone' && path.basename(path.dirname(cwd)) === '.next') {
  candidateRoots.push(path.resolve(cwd, '..', '..', '..', '..'))
}
```

This is appropriately constrained:
- Checks exact basename patterns (`standalone`, `.next`)
- Resolves a fixed depth (4 levels) to repo root
- Does not walk upward searching arbitrarily
- Preserves the existing env var override (`IKE_OPS_STATE_PATH`) as highest priority
- Applied consistently to both `resolveOpsStatePath()` and `resolveRepoPath()`

No broad unsafe filesystem walking introduced.

### Graceful Degradation (Question 2)

**ACCEPTABLE** - The degradation is appropriately scoped.

The change removes strict guards for `dirty_tree_state` and `next_action`, allowing the snapshot to render with these fields as `undefined` or empty arrays. This is correct because:

1. **Required fields still fail fast**: `product_state`, `runtime_state`, `runner_state`, `governance_state`, `review_state` all retain strict guards that return `null` (triggering STATIC_SNAPSHOT fallback).

2. **Optional fields degrade cleanly**: `dirty_tree_state` → `operationsSplit: undefined`, `next_action` → `nextActions: []`. The UI can display empty sections without hiding the live state entirely.

3. **Removed dead guard**: The `validation_state` check was correctly removed - it was validated but never consumed in snapshot construction.

The packet requirement "degrades optional sections without hiding all live state" is satisfied.

### Scope (Question 3)

**SCOPED** - Only `ops-state-adapter.ts` changed. Changes are minimal and targeted:
- Lines 32-36, 84-88: Next standalone cwd detection
- Lines 157-159: Optional field handling
- Lines 225-235: Conditional snapshot fields
- Removed unused `validation_state` guard

No unrelated changes. No scope creep.

### Validation Evidence (Question 4)

**INSUFFICIENT FOR PROMOTION** - Build validation alone is inadequate.

The build passes but this does not confirm runtime behavior:
- No evidence that `/control` returns `file_derived` provenance when state files exist
- No evidence that the Next standalone path resolution works
- No evidence that the optional field degradation renders correctly in UI

The worker correctly noted this in "Known Risks" section.

## 2. Validation Gaps

1. **Runtime path resolution unverified**: Controller must verify `/control` returns `file_derived` provenance (not `static_fallback`) when `ops/state/current_state.json` exists.

2. **Next standalone detection untested**: The cwd detection logic assumes `process.cwd()` returns `.../services/web/.next/standalone`. This needs validation in an actual Next standalone deployment context.

3. **Graceful degradation UI validation**: Controller should verify that missing `dirty_tree_state` or `next_action` renders correctly (empty sections, not broken layout) in the /control page.

4. **PM digest resolution**: The `readPmRunDigest()` function uses `resolveRepoPath()` for `ops/pm-runs/latest.json`. This path resolution also needs runtime validation.

## 3. Recommendation

**ACCEPT_WITH_CHANGES**

The code change is technically sound and properly scoped. Path resolution uses bounded detection, graceful degradation is appropriately targeted, and scope is minimal. However, the work cannot be promoted to PR without runtime validation.

## 4. Required Controller Action

1. **Runtime validation required before PR**:
   - Start the Next.js dev server: `npm --prefix services/web run dev`
   - Verify `/control` returns `file_derived` provenance when `ops/state/current_state.json` exists
   - If standalone testing is available, verify the `.next/standalone` cwd path resolution

2. **Optional smoke test** (recommended):
   - Add a minimal script to exercise path resolution in both local dev and standalone contexts
   - Or document manual validation steps for future changes

3. **After validation passes**: Promote to PR with the current diff.

4. **Post-merge**: Consider documenting `IKE_OPS_STATE_PATH` override for non-standard deployment scenarios as noted in worker's recommendations.