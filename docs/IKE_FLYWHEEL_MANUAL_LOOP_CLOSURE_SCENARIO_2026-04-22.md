# IKE Flywheel Manual Loop Closure Scenario

**Date:** 2026-04-22
**Status:** Scenario executed once

Execution result:

- [D:\code\MyAttention\docs\IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_RESULT_2026-04-22.md](/D:/code/MyAttention/docs/IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_RESULT_2026-04-22.md)

## Purpose

This document fixes the current short-term loop target before the project adds more bridge fields.

The current goal is not full runtime automation. The current goal is a bounded, AI-assisted manual loop:

```text
manual information input
-> AI-assisted flywheel inspect
-> human/controller selection
-> worker task packet
-> delegated worker execution
-> execution feedback inspect
-> controller absorption decision
```

This is enough to prove the information -> knowledge -> evolution flywheel without pretending the system already has verified execution provenance or automatic canonical absorption.

## Current Loop Assets

1. **Information entry**
   - UI: evolution flywheel inspect panel
   - Backend: `POST /api/conversation-runtime/flywheel/inspect`
   - Boundary: AI output is candidate material only.

2. **Knowledge/evolution candidate review**
   - UI: manual selection in the flywheel panel
   - Output: review, decision, and absorption packets
   - Boundary: selected labels are still controller discussion material, not persistence.

3. **Worker task packet**
   - Backend: `POST /api/conversation-runtime/flywheel/task-packet/preview`
   - UI: coding/review/test packet generation
   - Boundary: packet is an instruction draft, not automatic delegation.

4. **Delegated execution**
   - Current dev lane: `claude-worker`
   - Current practical route: one-shot bounded tasks
   - Boundary: controller owns acceptance; worker output is not accepted by default.

5. **Execution feedback return**
   - Backend: `POST /api/conversation-runtime/flywheel/execution-feedback/inspect`
   - UI: paste worker result and optional caller-provided provenance
   - Boundary: provenance is annotation only, not verification.

## Accepted Scenario

Use this exact scenario shape for the next manual demonstration:

1. User provides one bounded information segment.
2. Controller runs flywheel inspect.
3. Controller selects at most two knowledge candidates, two evolution triggers, and one worker lane.
4. Controller generates one worker packet.
5. One worker executes one bounded task.
6. Controller pastes the worker result with optional run/provider/model/artifact annotation.
7. Execution feedback inspect returns candidate knowledge deltas, candidate evolution triggers, advisory operational notes, and unverified provenance echo.
8. Controller decides whether the loop produced useful knowledge/evolution material.

## Non-Claims

This scenario does not prove:

- verified worker identity
- artifact existence
- packet/run binding
- automatic persistence
- automatic task scheduling
- automatic promotion into canonical knowledge

## Next Review Point

The next meaningful review point should be after one of these is complete:

1. an end-to-end manual scenario result using the path above, or
2. a bounded decomposition result that splits `flywheel.py` and `flywheel-inspect-panel.tsx` without changing semantics.

Do not open review for every small cleanup.
