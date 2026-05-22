# IKE Delivery Governance P1 Implementation Queue

Date: 2026-04-11
Status: next actions

## Purpose

Turn the new governance baseline into the smallest practical execution queue.

## P1 Tasks

### 1. Formalize staging runtime identity

Deliver:

- one explicit staging root
- one explicit staging port set
- one explicit staging DB / Redis naming rule

Minimum result:

- staging is no longer just a concept

Current implementation document:

- [D:\code\MyAttention\docs\IKE_STAGING_PRODUCTION_IDENTITY_PLAN_2026-04-11.md](/D:/code/MyAttention/docs/IKE_STAGING_PRODUCTION_IDENTITY_PLAN_2026-04-11.md)
- config templates:
  - [D:\code\MyAttention\config\runtime\staging.local.example.toml](/D:/code/MyAttention/config/runtime/staging.local.example.toml)
  - [D:\code\MyAttention\config\runtime\prod.local.example.toml](/D:/code/MyAttention/config/runtime/prod.local.example.toml)

### 2. Formalize production identity boundaries

Deliver:

- one explicit prod root or deploy target
- one explicit "what may write prod" rule
- one explicit "what may not write prod" rule

Minimum result:

- delegate and self-evolution lanes cannot be mistaken for prod writers

### 3. Install release checkpoint discipline

Deliver:

- milestone tag naming rule
- pre-risk checkpoint rule
- release tag rule

Minimum result:

- every accepted milestone becomes recoverable by git pointer

### 4. Install backup inventory

Deliver:

- DB backup location/rule
- runtime artifact archive rule
- knowledge/vector snapshot rule if applicable

Minimum result:

- rollback is tied to real recoverable assets, not just code

Current implementation document:

- [D:\code\MyAttention\docs\IKE_BACKUP_AND_RESTORE_INVENTORY_2026-04-11.md](/D:/code/MyAttention/docs/IKE_BACKUP_AND_RESTORE_INVENTORY_2026-04-11.md)

### 5. Add promotion checklist

Deliver:

- one compact release checklist covering:
  - review
  - validation
  - archive
  - tag
  - rollback pointer

Minimum result:

- promotion stops being chat-driven

Current implementation document:

- [D:\code\MyAttention\docs\IKE_RELEASE_PROMOTION_CHECKLIST_2026-04-11.md](/D:/code/MyAttention/docs/IKE_RELEASE_PROMOTION_CHECKLIST_2026-04-11.md)

## Recommended Order

1. staging runtime identity
2. release checkpoint discipline
3. promotion checklist
4. backup inventory
5. production identity boundary hardening

## Controller Rule

Do not start broad infrastructure automation before these minimum boundaries
are explicit in project files.
