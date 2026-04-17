# IKE Evolution Log Feedback - P1 Plan

Date: 2026-04-10
Phase: `P1 Minimal Log Feedback Integration`
Status: `candidate`

## Goal

Connect log-derived signals into the evolution/task surface in the narrowest
possible way while preserving:

- runtime mainline priority
- low-cost-first routing
- controller noise control

## Current Existing Building Blocks

Already present:

- collection health snapshot + issue builder:
  - [D:\code\MyAttention\services\api\feeds\collection_health.py](/D:/code/MyAttention/services/api/feeds/collection_health.py)
- auto evolution loops:
  - [D:\code\MyAttention\services\api\feeds\auto_evolution.py](/D:/code/MyAttention/services/api/feeds/auto_evolution.py)
- log analysis scheduler:
  - [D:\code\MyAttention\services\api\pipeline\log_analysis_scheduler.py](/D:/code/MyAttention/services/api/pipeline/log_analysis_scheduler.py)
- task processor:
  - [D:\code\MyAttention\services\api\feeds\task_processor.py](/D:/code/MyAttention/services/api/feeds/task_processor.py)

## Proposed Narrow Shape

1. introduce one explicit feedback classification layer for log/system issues
2. make Redis/cache-style failures default to:
   - acceleration degradation
   - observe/cluster, not direct controller escalation
3. keep canonical-truth-risk log signals eligible for direct escalation
4. add focused tests proving the routing split

## Preferred First Coverage

Only cover a small set of issue classes first:

1. Redis/cache connectivity failures
2. provider/network timeout clusters
3. collection health degradation
4. canonical runtime/preflight drift

## Success Condition

`P1` succeeds only if:

1. the existing log/system task path becomes more selective
2. repetitive low-severity operational noise is reduced
3. canonical-risk signals remain escalatable
4. no broad new subsystem is introduced

## Failure Condition

`P1` fails if it:

- creates a new log platform instead of a narrow integration layer
- hides canonical-risk signals
- routes everything into observe-only
- widens into a new mainline
