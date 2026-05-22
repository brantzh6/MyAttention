# IKE Evolution Log Feedback Packet - P1 Coding Brief

Date: 2026-04-10
Packet: `P1`
Type: `coding`
Phase: `P1 Minimal Log Feedback Integration`

## Objective

Add one narrow routing layer so log-derived feedback enters the evolution/task
surface with the correct severity and escalation behavior.

## Existing Code Surface

- log-analysis task creation:
  - [D:\code\MyAttention\services\api\pipeline\log_analysis_scheduler.py](/D:/code/MyAttention/services/api/pipeline/log_analysis_scheduler.py)
- collection-health issue building:
  - [D:\code\MyAttention\services\api\feeds\collection_health.py](/D:/code/MyAttention/services/api/feeds/collection_health.py)
- auto-evolution loops:
  - [D:\code\MyAttention\services\api\feeds\auto_evolution.py](/D:/code/MyAttention/services/api/feeds/auto_evolution.py)
- task routing / dedupe:
  - [D:\code\MyAttention\services\api\feeds\task_processor.py](/D:/code/MyAttention/services/api/feeds/task_processor.py)

## Required Outcome

Produce the smallest safe implementation that:

1. classifies log/system issues into:
   - acceleration degradation
   - operational degradation
   - canonical-truth risk
2. keeps Redis/cache-style failures out of direct controller/high-priority
   escalation by default
3. preserves escalation for real canonical-risk signals

## Guardrails

Do not:

- invent a new observability subsystem
- broaden into a general incident platform
- change runtime canonical-truth semantics
- turn all log issues into automatic tasks

## Validation Expectation

At minimum:

- focused unit tests for the new routing logic
- compile/import checks
- one durable result note explaining exactly what got routed differently

## Suggested Lane

Prefer OpenClaw `qwen3.6-plus` or Claude Code `glm-5.1` for bounded
implementation, then return to controller review.
