# IKE Single Controller Risk Note

Date: 2026-04-11
Status: controller risk note

## Purpose

Record the current project-delivery risk that development continuity still
depends too heavily on a single controller thread of context.

## Risk

The project now has:

- stronger governance
- stronger runtime truth
- stronger delegation contracts

But actual development continuity is still fragile because:

1. task prioritization is still mostly controlled by one active controller
2. many strategic transitions still depend on that controller preserving
   long-session context
3. support and research tracks are not yet fully converted into durable,
   self-explanatory operational packets

## Why This Matters

Runtime v0 is supposed to reduce exactly this risk for the system itself.

If project development remains permanently dependent on a single controller
holding context informally, then the project is not yet living the model it is
trying to build.

## Current Mitigations

Current mitigations already exist:

- durable docs
- mainline map
- unified task landscape
- governance index
- runtime truth core
- delegated packet model

## Remaining Gaps

The current main gaps are:

1. Runtime v0 exit not yet fully closed
2. active-surface document compression not yet installed
3. support tracks not yet fully converted into smaller operational packets
4. research lines still too closure-dependent on controller follow-through

## Controller Rule

The project should treat reduction of single-controller fragility as a real
governance objective, not only a side effect.

## Immediate Follow-up

1. complete Runtime v0 exit criteria and final closure
2. install active-surface compression
3. keep converting major lines into durable packetized surfaces
