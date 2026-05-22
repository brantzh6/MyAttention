# IKE Repository Restructure Backup And Rollback Checklist

Date: 2026-04-09
Status: required before migration

## Backup Checklist

### 1. Git checkpoint

- create a dedicated pre-migration branch
- stage the current durable docs/state
- create one pre-migration commit

Target intent:

- `codex/pre-ike-restructure-2026-04-09`

### 2. Cold filesystem backup

Create a full backup copy including ignored directories.

Recommended target:

- `D:\code\_backups\MyAttention-pre-ike-restructure-2026-04-09`

### 3. Agent/runtime backup

Create separate backup copies of:

- `D:\code\MyAttention\.runtime`
- `D:\code\MyAttention\.openclaw`
- `D:\code\MyAttention\.codex`
- `D:\code\MyAttention\memory`

### 4. Config snapshot

Export or copy current agent/workspace configs before editing them:

- OpenClaw agent configs
- Claude worker runtime config
- any path-sensitive launcher scripts

## Verification Before Switch

Before using `D:\code\IKE` as the main root, confirm:

- backend can start
- frontend can start
- runtime preflight still works
- delegated execution lanes still work
- no critical docs/path references still point only to the old root

## Rollback Checklist

### A. Code rollback

- switch back to the pre-migration git branch/commit

### B. Directory rollback

- restore the cold backup copy of `D:\code\MyAttention`

### C. Agent rollback

- restore previous OpenClaw workspace settings
- restore previous Claude worker runtime root
- restore previous controller working root if needed

## Do Not Start Migration Until

All are true:

- git checkpoint exists
- cold backup exists
- runtime/agent backup exists
- target directory structure has been reviewed
- switchover order is agreed
