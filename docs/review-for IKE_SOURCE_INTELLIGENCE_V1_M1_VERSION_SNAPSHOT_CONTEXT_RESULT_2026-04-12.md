# Review Request

Please review:

- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_VERSION_SNAPSHOT_CONTEXT_RESULT_2026-04-12.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_VERSION_SNAPSHOT_CONTEXT_RESULT_2026-04-12.md)
- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py](/D:/code/MyAttention/services/api/tests/test_source_plan_helpers.py)

Focus on:

1. Whether version snapshots should preserve `task_intent` / `interest_bias`
2. Whether preserving `discovery_notes` and `discovery_truth_boundary` in
   snapshots is the right bounded move
3. Whether this patch stays narrow and M1-aligned
4. Any hidden compatibility risk in broadening snapshot shape
5. Any missing validation around version-read surfaces

Please return:

- findings first, ordered by severity
- then validation gaps or open questions
- then recommendation:
  - `accept`
  - `accept_with_changes`
  - `reject`
