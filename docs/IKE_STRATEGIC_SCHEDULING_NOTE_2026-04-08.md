# IKE Strategic Scheduling Note

## Purpose

This note records the formal scheduling decision for two repeatedly deferred
strategic items:

1. second concept benchmark
2. procedural memory evolution

These are still deferred.
They are no longer unscheduled.

## Scheduled Placement

### 1. Second Concept Benchmark

Planned placement:

- **after `R2-B`**
- target placement:
  - `R2-C` if the runtime gate passes cleanly
  - otherwise remain deferred until the next runtime gate is cleared

Reason:

- runtime should first prove one narrow kernel-to-benchmark bridge
- then benchmark generalization can resume on a stronger kernel base

### 2. Procedural Memory Evolution

Planned placement:

- **after `R2-B`**
- target placement:
  - `R2-C` or `R3`, depending on runtime gate outcome and memory-kernel
    confidence

Reason:

- procedural memory should not re-expand while runtime task/truth closure is
  still being gated
- but it is strategically accepted and should no longer remain an implicit
  carry item

## Controller Rule

After this note:

- neither item should be described as "we still remember it"
- both should be described as:
  - formally scheduled
  - strategically accepted
  - awaiting the `R2-B` gate result
