# IKE Delivery Governance Index

Date: 2026-04-11
Status: controller baseline

## Purpose

This is the compact entry file for project delivery governance.

Use it when the question is not "what feature are we building" but:

- where should it run
- how does a change move from experiment to stable runtime
- how do we recover when an evolution step is wrong

## Scope

This governance layer sits above:

- runtime mainline
- agent harness contracts
- rename / cutover work

It defines how those lines move safely from development into stable operation.

## Core Documents

- environment strategy:
  - [D:\code\MyAttention\docs\IKE_ENVIRONMENT_STRATEGY_2026-04-11.md](/D:/code/MyAttention/docs/IKE_ENVIRONMENT_STRATEGY_2026-04-11.md)
- change promotion policy:
  - [D:\code\MyAttention\docs\IKE_CHANGE_PROMOTION_POLICY_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CHANGE_PROMOTION_POLICY_2026-04-11.md)
- release and rollback policy:
  - [D:\code\MyAttention\docs\IKE_RELEASE_AND_ROLLBACK_POLICY_2026-04-11.md](/D:/code/MyAttention/docs/IKE_RELEASE_AND_ROLLBACK_POLICY_2026-04-11.md)
- immediate implementation queue:
  - [D:\code\MyAttention\docs\IKE_DELIVERY_GOVERNANCE_P1_IMPLEMENTATION_QUEUE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_DELIVERY_GOVERNANCE_P1_IMPLEMENTATION_QUEUE_2026-04-11.md)
- staging/prod identity plan:
  - [D:\code\MyAttention\docs\IKE_STAGING_PRODUCTION_IDENTITY_PLAN_2026-04-11.md](/D:/code/MyAttention/docs/IKE_STAGING_PRODUCTION_IDENTITY_PLAN_2026-04-11.md)
- release promotion checklist:
  - [D:\code\MyAttention\docs\IKE_RELEASE_PROMOTION_CHECKLIST_2026-04-11.md](/D:/code/MyAttention/docs/IKE_RELEASE_PROMOTION_CHECKLIST_2026-04-11.md)
- backup and restore inventory:
  - [D:\code\MyAttention\docs\IKE_BACKUP_AND_RESTORE_INVENTORY_2026-04-11.md](/D:/code/MyAttention/docs/IKE_BACKUP_AND_RESTORE_INVENTORY_2026-04-11.md)
- document compression and active-surface policy:
  - [D:\code\MyAttention\docs\IKE_DOCUMENT_COMPRESSION_AND_ACTIVE_SURFACE_POLICY_2026-04-11.md](/D:/code/MyAttention/docs/IKE_DOCUMENT_COMPRESSION_AND_ACTIVE_SURFACE_POLICY_2026-04-11.md)
- platform neutralization audit:
  - [D:\code\MyAttention\docs\IKE_PLATFORM_NEUTRALIZATION_AUDIT_2026-04-11.md](/D:/code/MyAttention/docs/IKE_PLATFORM_NEUTRALIZATION_AUDIT_2026-04-11.md)
- Linux cutover readiness:
  - [D:\code\MyAttention\docs\IKE_LINUX_CUTOVER_READINESS_2026-04-11.md](/D:/code/MyAttention/docs/IKE_LINUX_CUTOVER_READINESS_2026-04-11.md)

## Why This Exists

Other AI coding projects often fail after the initial acceleration phase
because they never install durable answers for:

1. environment separation
2. controller review and promotion gates
3. rollback and restoration discipline

This governance set exists to prevent IKE from repeating that pattern.

## Current Controller Decision

The project should now operate with four distinct execution zones:

1. `controller-dev`
2. `sandbox-evolution`
3. `staging-runtime`
4. `prod-runtime`

No self-evolving lane may directly mutate `prod-runtime`.

## Relation To Current Mainline

This is not a replacement for the runtime mainline.

It is the governance shell that keeps runtime progress promotable,
recoverable, auditable, and increasingly cross-platform.

Related alignment documents:

- [D:\code\MyAttention\docs\IKE_PROJECT_RUNTIME_ALIGNMENT_2026-04-11.md](/D:/code/MyAttention/docs/IKE_PROJECT_RUNTIME_ALIGNMENT_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_PROJECT_RUNTIME_ALIGNMENT_P1_QUEUE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_PROJECT_RUNTIME_ALIGNMENT_P1_QUEUE_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_MEMORY_TIERS_AND_RETENTION_RULE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_MEMORY_TIERS_AND_RETENTION_RULE_2026-04-11.md)
- single-controller continuity risk:
  - [D:\code\MyAttention\docs\IKE_SINGLE_CONTROLLER_RISK_NOTE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SINGLE_CONTROLLER_RISK_NOTE_2026-04-11.md)
- external method absorption baseline:
  - [D:\code\MyAttention\docs\IKE_EXTERNAL_METHOD_DISCOVERY_AND_ABSORPTION_2026-04-11.md](/D:/code/MyAttention/docs/IKE_EXTERNAL_METHOD_DISCOVERY_AND_ABSORPTION_2026-04-11.md)
