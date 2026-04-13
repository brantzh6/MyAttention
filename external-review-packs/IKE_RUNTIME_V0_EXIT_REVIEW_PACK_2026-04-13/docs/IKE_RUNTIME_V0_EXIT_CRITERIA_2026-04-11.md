# IKE Runtime v0 Exit Criteria

Date: 2026-04-11
Status: controller baseline

## Purpose

Define the explicit `done / exit` boundary for `IKE Runtime v0`.

This document exists to prevent Runtime v0 from continuing as an endless
sequence of narrow internal proofs without a clear handoff into the next
product-capability line.

## Core Question

After Runtime v0 is complete, what should the system be able to do that it
cannot reliably do today?

## Exit Standard

Runtime v0 should be considered complete when the project has a truthful,
controller-governed runtime kernel that can:

1. represent one active project in durable runtime truth
2. represent bounded tasks and decisions durably
3. reconstruct current work context from canonical truth
4. record one explicit controller acceptance decision durably
5. expose that state through controller-facing inspect surfaces
6. survive restart or session loss without losing the current operational state

Runtime v0 is **not** required to complete:

1. full scheduler semantics
2. detached daemon fleet supervision
3. broad multi-project orchestration
4. advanced memory/knowledge intelligence
5. full product-facing Source Intelligence behavior

## Practical Done Criteria

Runtime v0 is done when all of the following are true:

### A. Core truth objects are materially real

- `RuntimeProject`
- `RuntimeTask`
- `RuntimeDecision`
- `RuntimeTaskEvent`
- `RuntimeWorkContext`
- `RuntimeMemoryPacket`

Meaning:

- they are not only designed
- they are implemented and used in at least one truthful path

### B. One truthful project/task lifecycle path is closed

The system can prove one bounded path from:

- project
- to task
- to decision
- to work context
- to controller-visible read surface

without inventing fake state.

### C. Controller decision lane is real

The system can:

- inspect current confirmation-eligible state
- record one explicit controller acceptance decision
- reflect that decision back through runtime truth

### D. Restart recovery is materially demonstrated

After process/session interruption, the current runtime state can be recovered
from durable truth rather than reconstructed from chat memory alone.

### E. Runtime truth has at least one consuming caller or operator use path

Runtime v0 should not exit as a pure internal kernel with no consumer.

At minimum, one of the following must be true:

1. controller/governance process actively uses runtime truth as the current
   operational state source
2. one next capability packet explicitly depends on runtime truth as substrate

### F. Remaining gaps are explicitly out of scope, not hidden incompleteness

Anything not included in Runtime v0 exit must be explicitly named as:

- next phase
- support track
- or later backlog

## Current Status Against Exit Criteria

### A. Core truth objects are materially real

- status:
  - mostly satisfied

### B. One truthful project/task lifecycle path is closed

- status:
  - materially satisfied

### C. Controller decision lane is real

- status:
  - materially implemented through `R2-I18`
  - validation closure still blocked on current-machine environment issue

### D. Restart recovery is materially demonstrated

- status:
  - materially satisfied through `R2-I20`

### E. Runtime truth has a consuming caller or operator use path

- status:
  - materially satisfied through `R2-I19`

### F. Remaining gaps are explicitly out of scope

- status:
  - partially satisfied
  - many non-goals are documented, but the final exit handoff still needs to be
    written more cleanly

## What Runtime v0 Completion Means

If Runtime v0 exits successfully, the project will have something it does not
fully have today:

- one trustworthy runtime task/decision/memory kernel that the controller can
  actually use as the current project operational substrate

That is the handoff point for:

- Source Intelligence V1
- future Knowledge Brain packets
- future Evolution Brain upgrade

## What Runtime v0 Completion Does Not Mean

Runtime v0 completion does not mean:

- the full IKE product is complete
- autonomous project management is complete
- memory architecture is complete
- source intelligence is solved
- evolution is model-driven

It only means the project has finished the first trustworthy operating kernel.

