# IKE Runtime v0 Packet R1-E1 Coding Brief

## Task ID

`IKE-RUNTIME-R1-E1`

## Goal

Implement the narrow project-surface alignment path:

- make `RuntimeProject.current_work_context_id` reflect runtime-owned active
  context truth
- prove project-facing current-work visibility is derived from runtime truth

## Scope

Allowed:

- narrow runtime helper/service integration for project pointer alignment
- narrow DB-backed proof path for project-surface visibility

Not allowed:

- broad UI/API expansion
- notification surfaces
- benchmark integration
- graph memory
- new runtime object families

## Acceptance Standard

1. project-level current context pointer is updated from runtime truth
2. active project context can be retrieved without inventing a second truth
3. existing closure-to-memory truth does not regress
