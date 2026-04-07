# IKE Runtime v0 Packet R1-A1 Coding Brief

## Task ID

- `R1-A1`

## Goal

Implement the second-wave hardening changes required before broader runtime
integration.

## Scope

Hardening only:

- claim semantics
- memory upstream existence verification
- force-path restriction
- migration validation support

Do not broaden into:

- new runtime objects
- graph or semantic memory
- UI surfaces
- scheduler expansion

## Required Outcomes

1. claim permission is no longer merely caller-asserted
2. trusted `MemoryPacket` acceptance checks upstream existence, not only linkage
   presence
3. force-paths are restricted to controller/runtime-appropriate flows
4. migration verification support is stronger than first-wave baseline

## Validation Expectations

- relevant unit/integration tests
- explicit negative-path checks
- migration-oriented verification where feasible

## Stop Conditions

Stop and escalate if the patch requires:

- new first-class tables or runtime object types
- redesign of the v0 state model
- broad schema expansion outside current hardening needs

## Delivery

Return the standard structured result format.
