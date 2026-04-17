# IKE Memory Tiers And Retention Rule

Date: 2026-04-11
Status: controller baseline

## Purpose

Define the current memory tiers so the project does not confuse chat history,
document archive, runtime truth, and future reviewed memory.

## Memory Tiers

### Tier 0 - Chat Working Context

Examples:

- current conversation
- temporary discussion
- short-lived back-and-forth

Rule:

- useful for work
- not canonical
- may be lost

### Tier 1 - Durable Project Archive

Examples:

- result milestone docs
- review docs
- governance docs
- handoff docs
- progress and changelog

Rule:

- current primary durable project memory shell
- should be written whenever important progress or review occurs

### Tier 2 - Canonical Runtime Truth

Examples:

- runtime tasks
- runtime decisions
- runtime task events
- runtime work contexts
- runtime memory packets

Rule:

- canonical for the runtime domain
- not replaced by loose docs or chat

### Tier 3 - Future Reviewed Knowledge Memory

Examples:

- reviewed methodological summaries
- accepted research synthesis
- trusted knowledge assets that should influence IDE/runtime behavior later

Rule:

- should not be created directly from raw chat
- should emerge from reviewed and retained material

## Retention Rule

If something matters beyond the current session, it must move upward:

- Tier 0 -> Tier 1
- or Tier 0 -> Tier 2 through explicit runtime recording

If it stays only in Tier 0, the project must assume it can be lost.

## Current Meaning For The Project

This rule is especially important because:

- runtime is still being built
- project delivery currently relies on doc retention
- many important reviews previously existed only in chat

That pattern must not continue.
