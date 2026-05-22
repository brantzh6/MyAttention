# AI Entry Useful Packet Selection (P0)

Date: 2026-05-18
Lane: controller / AI conversation entry
SDLC stage: Design
Risk: R2
Truth status: non-canonical controller packet

## Objective

Select the next useful AI-entry-originated bounded packet now that the Flywheel
V1 loop has proven it can consume a real delegated worker result through
execution-feedback inspect.

This packet is selection/design only. It must not implement code.

## Mainline Context

Accepted mainline evidence:

- `/chat -> /evolution` can carry transient chat provenance into the Flywheel reviewer note.
- Task-packet preview can generate copy-ready delegate handoff packets.
- Execution-feedback inspect can consume a real worker result.
- The real worker-result feedback loop was reviewed and accepted with changes.

Current active gap:

```text
Make AI conversation entry select a useful next bounded packet and carry it
through the reviewed loop without automatic execution or promotion.
```

## Dirty-Tree Constraint

The current worktree is over budget.

Latest classifier summary:

```text
total: 172
recommendation: requires_scoped_review_prep
largest group: flywheel_readiness: 72
```

Because of this, the selected next packet must be prepared as a scoped lane
package before implementation. No implementation work should start from the
shared dirty worktree until the selected file set is named and reviewable.

## Required Selection Criteria

Select exactly one next packet that:

1. Starts from AI conversation entry, not from generic Flywheel infrastructure.
2. Produces user-facing value in the evolution loop.
3. Does not treat raw chat as canonical truth.
4. Reuses the accepted inspect-only packet/feedback loop.
5. Has a bounded file set and validation commands.
6. Can be reviewed locally before any GitHub/Codex promotion review.
7. Can be split cleanly from the existing dirty tree.

## Candidate Direction

Preferred candidate unless contradicted by local evidence:

```text
AI chat "turn into task packet" action:
From a chat message, generate a visible candidate packet preview with
chat-origin provenance, allow the controller to copy the delegate handoff,
and make the next review/feedback step explicit.
```

Non-goals:

- no automatic execution
- no automatic persistence
- no canonical memory absorption
- no generic chat redesign
- no broad runtime repair
- no dirty-tree cleanup mixed into product implementation

## Required Output

Write:

```text
tasks/codex/ai_entry_useful_packet_selection_result_2026-05-18.md
```

The result must include:

- selected packet title
- why this is the next mainline packet
- scoped file candidates
- validation commands
- review gate
- dirty-tree handling plan
- known risks
- recommendation: `accept`, `accept_with_changes`, or `reject`
- stop condition

## Stop Condition

Stop after the selection result is written and reviewed. Do not implement the
selected packet in this task.
