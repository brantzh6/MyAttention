# Dirty Tree Containment Result

Date: 2026-05-18
Lane: governance / worktree operations
SDLC stage: Operations correction result
Risk: R2
Truth status: controller operations result

## summary

Dirty tree containment is now the active quality gate before the next
implementation packet.

The worktree is not in a promotion-ready state. It is over budget and contains
mixed tracked/untracked changes across Flywheel, AI entry, control surface,
runtime, review tooling, and governance artifacts.

## why_the_problem_recurred

Root causes:

1. Accepted artifacts were treated as "done" in conversation and docs, but not
   consistently moved into a scoped staging/PR package.
2. Active operations docs retained stale clean-state language while the actual
   classifier result had become over budget.
3. Automation previously counted low-value preparation as progress, allowing
   active packets to drift while dirty artifacts accumulated.
4. Multiple lanes touched overlapping frontend/Flywheel files without a
   mandatory scoped package boundary before the next lane started.
5. Review and absorption happened, but "post-absorption packaging" was not a
   required stop condition.

## current_evidence

Classifier command:

```text
python scripts/governance/classify_worktree.py --cwd D:\code\MyAttention --limit 12
```

Observed result:

```text
total: 172
recommendation: requires_scoped_review_prep
largest group: flywheel_readiness: 72
```

Current branch:

```text
codex/pre-ike-restructure-2026-04-09
```

## containment_decision

Do not start another implementation patch from the shared dirty tree.

Allowed next operations:

1. Write or update task/result/review/absorption artifacts.
2. Prepare one scoped package file list.
3. Review that package list.
4. Stage/push only after package scope is accepted.

Forbidden until scoped package acceptance:

1. New product implementation edits.
2. Broad staging.
3. Broad commit.
4. Mixed PR.
5. Opportunistic cleanup inside feature work.
6. Deleting untracked artifacts without explicit approval.

## first_scoped_package

First package to prepare:

```text
flywheel_readiness
```

Reason:

- It is the largest group.
- It contains the most recent accepted mainline loop evidence.
- It overlaps the next AI-entry implementation files.
- Reducing this group first creates a cleaner boundary for `AI Entry Task Packet Composer P0`.

## package_acceptance_criteria

The scoped package list must include:

- package name
- lane
- included files
- excluded files
- linked task packets
- linked result artifacts
- linked review artifacts
- linked absorption artifacts
- validation commands
- known risks
- recommendation

The package is not accepted if it includes unrelated runtime, source
intelligence, or generic governance changes.

## operations_rule_change

Add a post-absorption packaging rule:

```text
After any accepted implementation/test/UI/runtime slice, the controller must
either prepare a scoped package boundary or explicitly park the slice before
opening the next implementation slice.
```

This prevents "reviewed but unshipped" local truth from accumulating.

## validation_run

```text
git status --short --branch
python scripts/governance/classify_worktree.py --cwd D:\code\MyAttention --limit 12
```

Result: worktree remains over budget and requires scoped review prep.

## known_risks

- Preparing a scoped package list will not by itself clean the tree; staging or
  PR prep must happen only after scope acceptance.
- Some current tracked files may contain multiple accepted slices in one file,
  so package review must distinguish accepted context from candidate promotion
  scope.
- The controller must resist treating dirty-tree cleanup as the product
  mainline; it is a gate to resume safe mainline implementation.

## recommendation

`accept_with_changes`

Accept containment immediately and make `flywheel_readiness` scoped package
preparation the next operation before implementation.

## stop_condition

Stop after review and controller absorption of this containment result. Do not
stage, commit, push, or delete files in this packet.
