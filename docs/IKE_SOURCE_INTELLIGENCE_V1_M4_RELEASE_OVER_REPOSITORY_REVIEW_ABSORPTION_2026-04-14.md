# IKE Source Intelligence V1 - M4 Release-Over-Repository Review Absorption

Date: 2026-04-14
Scope: `M4 Same-Repo Release Duplicate Compression In LATEST/FRONTIER`
Status: `selective_absorption_complete`

## Absorption Summary

This review wave is accepted.

- `claude`: accepted
- `chatgpt`: accepted
- `gemini`: accepted

## Accepted Corrections

### 1. Route-level proof should be symmetric

`M4` should not rely only on helper-level evidence for:

- `FRONTIER` positive compression
- `METHOD` negative preservation

Those route-level proofs have now been added.

### 2. Wording should match implementation exactly

The packet should say:

- `LATEST` / `FRONTIER`

instead of the broader phrase `timely focus`.

### 3. Naming should stay narrow

The packet should be understood as:

- `same-repo release duplicate compression heuristic`

not broad release superiority or lifecycle intelligence.

## Controller Judgment

- code-level: `accept`
- project/controller-level: `accept_with_changes`

## Closed Changes

The `with_changes` part is now closed:

1. route-level symmetry added
2. wording narrowed to exact focus names
3. naming narrowed to duplicate-compression semantics
