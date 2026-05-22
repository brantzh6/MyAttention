# IKE Hermes Skill Absorption Note

Date: 2026-04-11
Status: controller absorption note

## Source

- Hermes repository:
  - [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Hermes README:
  - [README.md](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/README.md)
- Hermes Claude Code skill:
  - [skills/autonomous-ai-agents/claude-code/SKILL.md](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/skills/autonomous-ai-agents/claude-code/SKILL.md)

## Why It Matters

Hermes is relevant to IKE because it combines several things that also matter
to our mainline:

- self-improving agent framing
- memory and recall claims
- delegation and parallelization
- skills as durable procedural memory
- multiple execution backends

The README explicitly claims:

- a built-in learning loop and persistent memory
- delegates and parallelizes isolated subagents
- scheduled automations
- multiple terminal backends rather than laptop-only execution

Those are directly adjacent to IKE runtime and harness work.

## Key Extracted Mechanisms

### 1. Mode split for Claude Code

The Hermes Claude Code skill makes a strong distinction between:

- `print mode (-p)` for one-shot non-interactive work
- interactive PTY/tmux mode for long-running multi-turn work

This is a useful design distinction for IKE.

### 2. Automation-first use of print mode

Hermes treats print mode as preferred for most coding automation and explicitly
includes structured JSON and piped stdin usage.

This matches the direction we just used to harden our own Claude worker.

### 3. Agent as orchestrator, not only executor

Hermes is not just “one model answering”.

The README frames it as a system with:

- memory
- skills
- delegation
- scheduled automation
- multiple backends

That is closer to a runtime/controller stack than to a simple chat agent.

### 4. Agent dialogue as part of method discovery

Because Hermes itself is an agent system, its own user-facing explanations can
be interrogated as a signal source.

That should become part of IKE external-method discovery.

## What IKE Should Absorb Now

### A. Explicit lane split

IKE should explicitly separate:

- one-shot bounded delegate lanes
- interactive long-running delegate lanes

### B. External task memory

Hermes emphasizes durable task tracking and orchestration rather than relying
on one model to remember everything.

IKE should continue moving project and runtime task state away from chat memory
and toward durable task surfaces.

### C. Agent interview as a formal signal

IKE should allow “talk to the external agent itself” as part of method
discovery, but only as one evidence channel among several.

## What IKE Should Not Blindly Copy

### A. Self-description as truth

Hermes claims many capabilities in README and skills.

IKE should not absorb those claims directly without:

- source review
- observed behavior
- narrow local validation

### B. Architecture wholesale

IKE should not copy Hermes as a whole system.

IKE has its own controller/runtime/governance constraints, and the useful move
is selective absorption of mechanisms, not imitation.

## Immediate Next Absorption Targets

1. formalize `one-shot vs interactive` delegate lane split in our harness docs
2. add a durable external-method absorption lane to the project task map
3. later, if useful, run a direct agent interview with Hermes and compare its
   answers against source and behavior

## Current Recommendation

`accept_with_changes`

Hermes is a high-value external reference for IKE, especially on skills,
delegation, memory, and orchestration. But the correct move is selective,
validated absorption rather than direct copying.
