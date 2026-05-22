# IKE Runtime v0 R2-H Phase Judgment

## Phase

`R2-H = Canonical Service Launch Path Normalization`

## Why This Phase Exists

After materially complete `R2-G`, the remaining runtime-service blocker is no
longer observability.

The remaining gap is operational normalization of the canonical service:

- the canonical `8000` service can still run with:
  - repo-owned launcher evidence in the parent chain
  - but a system `Python312` child as the actual listener
- controller-bounded alternate-port live proof is now acceptable
- canonical service proof is still blocked by owner mismatch

## Intended Scope

- define one controller-acceptable canonical launch path
- reduce parent/child interpreter drift for the main API service
- make canonical service ownership evidence repeatable

## Explicit Non-Goals

- no new runtime truth objects
- no broad service supervisor redesign
- no broad UI/runtime redesign
- no benchmark/runtime scope expansion

## Controller Judgment

`R2-H` is the correct next narrow phase because:

- `R2-G` already established truthful observability
- the remaining blocker is canonical launch-path normalization
- broader runtime readiness should not advance while canonical service proof
  still depends on ambiguous ownership
