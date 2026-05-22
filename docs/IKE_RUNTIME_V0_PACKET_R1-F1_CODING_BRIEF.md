# IKE Runtime v0 Packet R1-F1 Coding Brief

## Task ID

- `R1-F1`

## Goal

Implement one narrow controller-facing runtime read surface for current project
state.

## Required focus

Must assemble from existing runtime truth only:

1. `RuntimeProject`
2. active `RuntimeWorkContext`
3. current active/waiting tasks
4. latest finalized decision
5. latest trusted packet refs

Must not:

- create a persistent duplicate summary object
- broaden into UI/API rollout

## Required output

- helper/read-model implementation
- DB-backed proof that output is runtime-derived
- recommendation
