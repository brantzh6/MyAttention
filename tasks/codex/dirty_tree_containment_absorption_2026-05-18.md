# Controller Absorption: Dirty Tree Containment

Date: 2026-05-18
Controller decision: `accept`
Lane: governance / worktree operations
Truth status: controller operations decision

## absorbed_artifacts

- Packet: `tasks/codex/dirty_tree_containment_p0_2026-05-18.md`
- Result: `tasks/codex/dirty_tree_containment_result_2026-05-18.md`
- Review: `docs/reviews/active/review_for_dirty_tree_containment_2026-05-18.md`
- Runtime review source: `.runtime/reviews/results/DIRTY_TREE_CONTAINMENT_REVIEW_2026_05_18.md`

## decision

Accept dirty-tree containment as an active quality gate.

No new implementation patch should start from the shared dirty tree until a
scoped package boundary is accepted.

## why_this_happened

The repeated dirty-tree problem was caused by execution artifacts and reviewed
changes being accepted as local truth without an immediate packaging step.
Multiple lanes then continued from the same shared dirty workspace, and active
docs drifted from actual classifier state.

## active_rule

After each accepted implementation/test/UI/runtime slice, the controller must
immediately choose one:

1. prepare a scoped stage/PR package for that lane
2. park the slice with an explicit blocker
3. reject or supersede the artifacts

Do not open the next implementation slice while the previous accepted slice is
still only local dirty-tree truth.

## next_operation

Prepare a scoped package list for:

```text
flywheel_readiness
```

Reason: it is the largest dirty group and overlaps the next AI-entry
implementation files.

## stop_condition

Do not stage, commit, push, delete, or implement until the scoped package file
list is produced and accepted.
