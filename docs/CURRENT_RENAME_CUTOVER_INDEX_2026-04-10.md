# Current Rename And Cutover Index

Date: 2026-04-10
Status: active support track

## Purpose

This is the compact entry file for repository restructure, rename, and cutover.

## Current Rename Goal

Move toward:

- `D:\code\IKE` as canonical project root
- isolated agent/runtime roots outside the controller project tree
- visible identity normalization to `IKE`

without:

- breaking compatibility-critical internals
- breaking current runtime work
- doing a blind full-repository rename

## Current Status

- pre-migration git checkpoint exists
- cold backup exists
- isolated OpenClaw workspaces exist
- Claude worker run root has been externalized
- `D:\code\IKE` clean parallel root exists
- visible/runtime identity normalization is in progress
- final controller cutover has not happened yet

## Most Relevant Files

- restructure plan:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RESTRUCTURE_AND_WORKSPACE_ISOLATION_PLAN_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RESTRUCTURE_AND_WORKSPACE_ISOLATION_PLAN_2026-04-09.md)
- restructure inventory:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RESTRUCTURE_INVENTORY_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RESTRUCTURE_INVENTORY_2026-04-09.md)
- backup / rollback:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RESTRUCTURE_BACKUP_AND_ROLLBACK_CHECKLIST_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RESTRUCTURE_BACKUP_AND_ROLLBACK_CHECKLIST_2026-04-09.md)
- phase-1 result:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RESTRUCTURE_PHASE1_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RESTRUCTURE_PHASE1_RESULT_2026-04-09.md)
- cutover readiness:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RESTRUCTURE_CUTOVER_READINESS_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RESTRUCTURE_CUTOVER_READINESS_2026-04-09.md)
- phase-2 rename plan:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_PHASE2_PLAN_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_PHASE2_PLAN_2026-04-09.md)
- compatibility remainder:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_COMPATIBILITY_REMAINDER_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_COMPATIBILITY_REMAINDER_2026-04-09.md)

## Most Relevant Landed Phase-2 Results

- backend/runtime identity:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D1_BACKEND_RUNTIME_IDENTITY_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D1_BACKEND_RUNTIME_IDENTITY_RESULT_2026-04-09.md)
- reasoning/service label:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D2_REASONING_AND_SERVICE_LABEL_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D2_REASONING_AND_SERVICE_LABEL_RESULT_2026-04-09.md)
- runtime project key:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D3_RUNTIME_PROJECT_KEY_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D3_RUNTIME_PROJECT_KEY_RESULT_2026-04-09.md)
- visible/runtime title cleanup:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D5_RUNTIME_VISIBLE_TITLE_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D5_RUNTIME_VISIBLE_TITLE_RESULT_2026-04-09.md)
- web metadata title:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D6_WEB_METADATA_TITLE_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D6_WEB_METADATA_TITLE_RESULT_2026-04-09.md)
- web package identity:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D7_WEB_PACKAGE_IDENTITY_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D7_WEB_PACKAGE_IDENTITY_RESULT_2026-04-09.md)
- sidebar branding:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D8_SIDEBAR_BRANDING_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D8_SIDEBAR_BRANDING_RESULT_2026-04-09.md)
- notification visible identity:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D11_NOTIFICATION_VISIBLE_IDENTITY_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D11_NOTIFICATION_VISIBLE_IDENTITY_RESULT_2026-04-09.md)
- chat system prompt identity:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D12_CHAT_SYSTEM_PROMPT_IDENTITY_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D12_CHAT_SYSTEM_PROMPT_IDENTITY_RESULT_2026-04-09.md)
- feed cache namespace:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D13_FEED_CACHE_NAMESPACE_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D13_FEED_CACHE_NAMESPACE_RESULT_2026-04-10.md)
- voting prompt identity:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D14_VOTING_PROMPT_IDENTITY_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D14_VOTING_PROMPT_IDENTITY_RESULT_2026-04-10.md)

## Controller Judgment

This track is active because shared-root pollution was real.
It is still a support track, not permission to do a full uncontrolled rename sweep.
