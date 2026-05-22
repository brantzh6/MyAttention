# IKE AI Domain Discovery Loop P1 Result

Date: 2026-04-12
Status: controller result

## Topic

- `agent harness patterns for coding agents`

## Candidate Inputs

- sources considered:
  - [Anthropic Managed Agents engineering note](https://www.anthropic.com/engineering/managed-agents)
  - [Hermes Agent README](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/README.md)
  - [Hermes Claude Code skill](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/skills/autonomous-ai-agents/claude-code/SKILL.md)
- objects considered:
  - `Anthropic Managed Agents`
  - `Hermes Agent`
  - `Hermes Claude Code skill`

## What Was Discovered

### 1. Session, harness, and sandbox should be separated explicitly

Anthropic's Managed Agents note makes the cleanest architectural split in this
topic set:

- `session`
- `harness`
- `sandbox`

The important point is not just naming.

The point is that each can fail or evolve independently, and the durable
session should stay outside the harness and sandbox. [source](https://www.anthropic.com/engineering/managed-agents)

### 2. Durable session outside the harness is a strong pattern

Anthropic explicitly states that the harness should be restartable and that the
session log should survive harness failure. [source](https://www.anthropic.com/engineering/managed-agents)

This is highly relevant to IKE because Runtime v0 is trying to become the
controller-usable durable task/decision/work-context substrate rather than
leaving continuation dependent on chat history.

### 3. Brain/hands decoupling is the right external-execution pattern

Anthropic frames the design as decoupling the "brain" from the "hands".
[source](https://www.anthropic.com/engineering/managed-agents)

This matches the current IKE direction:

- IKE should remain the judgment/governance/control layer
- external execution systems should be treated as hands/workbenches, not as
  canonical truth

### 4. Hermes confirms a practical two-mode orchestration split

The Hermes Claude Code skill clearly distinguishes:

- print mode for most one-shot tasks
- interactive PTY/tmux mode for long-running multi-turn tasks

[source](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/skills/autonomous-ai-agents/claude-code/SKILL.md)

This is not just a CLI trick.

It is an operational pattern for choosing the correct execution mode based on
task shape.

### 5. Hermes emphasizes delegation, parallelism, and skills as practical
operating surfaces

The Hermes README highlights:

- built-in learning loop
- persistent memory
- scheduled automations
- delegation and parallelization
- multiple terminal backends

[source](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/README.md)

This matters because it shows an external agent system treating execution,
memory, and skills as a unified operating environment rather than as isolated
features.

## Why It Matters To IKE

This first loop produced three controller-usable judgments:

1. `session outside harness` is now a stronger reference pattern for Runtime
   and harness thinking than many earlier abstract notes
2. `brain vs hands` is the correct framing for how IKE should relate to Claude
   Code, Hermes, and similar systems
3. `print vs interactive` should become an explicit execution-lane split in
   IKE harness policy

## What Should Be Absorbed Now

### A. Strengthen the session/harness/sandbox vocabulary

Anthropic's split should be used as a reference model when we talk about:

- runtime durable truth
- harness restartability
- execution isolation

### B. Keep external executors outside canonical truth

The discovery strengthens the existing IKE principle that external systems are
execution layers, not final truth sources.

### C. Formalize one-shot vs interactive execution modes

Hermes provides a practical operating rule that should be absorbed into IKE
harness policy:

- one-shot bounded task -> print/non-interactive lane
- long-running iterative task -> interactive session lane

## What Should Be Deferred

- full adoption of a general session log platform
- full adoption of Hermes as a system
- any broad meta-harness redesign
- any claim that IKE already has Anthropic-level decoupling

## Truth Boundary

- what this result proves:
  - the current project now has one real external-method discovery result in
    the AI domain that is specific, relevant, and controller-usable
  - the loop can produce absorption-grade conclusions rather than only broad
    inspiration
- what this result does not prove:
  - autonomous discovery maturity
  - production-grade source intelligence
  - a complete external-method ingestion pipeline

## Recommendation

- `accept_with_changes`

Reason:

- the loop produced useful signal
- but it is still controller-led and manually synthesized rather than a mature
  autonomous discovery capability
