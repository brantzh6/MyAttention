# IKE Runtime OpenClaw vs Claude Coding Baseline

## Scope

This is a truthful baseline comparison, not a full apples-to-apples benchmark.

The strongest current comparable coding evidence is `R2-B1`:
- one bounded runtime lifecycle proof packet
- Claude coding lane produced the correct live diff direction
- controller completed recovery/acceptance because durable final artifact closure was incomplete

## Claude Coding Lane Evidence

- delegated run:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T043044-81696251](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T043044-81696251)
- truthful status:
  - run remained incomplete from a durable-final-artifact perspective
- controller-recovered result:
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r2-b1-real-task-lifecycle-coding.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r2-b1-real-task-lifecycle-coding.json)

## What Claude Proved

- bounded coding direction was correct
- patch scope stayed narrow
- controller-side validation succeeded after recovery

## What Claude Did Not Yet Prove

- stable delegated finalization for the packet
- independent coding closure without controller recovery

## OpenClaw Baseline Status

Current runtime mainline evidence does not yet provide a same-packet, same-timebox, same-validation completed OpenClaw coding run that is directly comparable to the above Claude run.

So the truthful comparison status is:
- **not a full dual-lane benchmark yet**
- **Claude has enough evidence to remain a valid coding lane**
- **OpenClaw is not yet measured against the same packet under identical conditions**

## Controller Conclusion

- Claude coding lane is currently:
  - `usable`
  - `controller-recoverable`
  - `not yet independently closure-stable`
- A real dual-lane benchmark should use:
  - one packet
  - one time box
  - one validation matrix
  - one controller acceptance rubric
