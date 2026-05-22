# IKE Source Intelligence V1 - M2 Execution Packet

Date: 2026-04-13
Phase: `M2 Route-Level Loop Proof Through Existing M1 Path`
Status: `execution_ready`

## Goal

Use the already-landed `Source Intelligence V1 M1` code path to prove one
bounded route-level loop and prepare the next quality/noise judgment slice.

## Existing Implementation Surface To Use

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- `POST /sources/discover`
- `POST /sources/plans`
- `POST /sources/plans/{plan_id}/refresh`
- `GET /sources/plans/{plan_id}/versions`

## Required Output

1. one bounded result note
2. one evaluation note
3. one explicit next-slice decision:
   - continue quality improvement
   - compress/noise-reduction
   - or stop this lane

## Guardrails

1. do not widen into source-platform redesign
2. do not invent canonical source truth
3. do not claim research-grade quality
4. stay on the existing M1 path
