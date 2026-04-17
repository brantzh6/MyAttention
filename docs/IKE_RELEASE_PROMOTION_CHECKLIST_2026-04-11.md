# IKE Release Promotion Checklist

Date: 2026-04-11
Status: controller checklist

## Purpose

Provide the smallest practical checklist for promoting a candidate from
development into staging or production.

## Checklist

### 1. Scope frozen

- bounded packet or release scope is written down
- unrelated changes are excluded

### 2. Review complete

- controller review completed
- external review results archived if required
- unresolved findings are explicitly tracked

### 3. Validation complete

- required compile/tests completed
- required runtime proof completed
- validation gaps are explicitly documented

### 4. Archive complete

- result doc written
- review doc written if applicable
- changelog/progress updated if materially relevant

### 5. Git checkpoint complete

- change committed
- milestone or release tag created if accepted
- rollback pointer exists for risky changes

### 6. Environment target explicit

- target is one of:
  - `staging-runtime`
  - `prod-runtime`
- target root is explicit
- target ports are explicit
- target DB / Redis / Qdrant identity is explicit

### 7. Backup or restore readiness explicit

- DB backup or restore point exists if needed
- runtime artifact archive location is known
- config version is known

### 8. Promotion decision explicit

- final controller status is one of:
  - `accept`
  - `accept_with_changes`
  - `reject`
  - `defer`

### 9. Post-promotion validation complete

- health endpoint checked
- canonical runtime path checked
- key regression surface checked

### 10. Rollback path still valid

- rollback target version is known
- rollback owner is known
- rollback procedure is not blocked by missing artifacts

## Controller Rule

If any required checklist item is unknown, the promotion is not ready.
