# IKE External Method Discovery And Absorption

Date: 2026-04-11
Status: controller baseline

## Purpose

Define how IKE should discover, evaluate, and absorb high-value external AI
agent methods, skills, and orchestration patterns.

This exists to prevent important external advances from being:

- noticed once
- discussed in chat
- partially remembered
- then lost

## Problem

Many of the most relevant external projects are not ordinary libraries.

They are themselves:

- agents
- agent runtimes
- skill systems
- memory systems
- orchestration systems

That means IKE should not treat them only as code to read.

IKE should also treat them as systems that can be:

- inspected in source
- exercised in behavior
- interviewed through agent interaction

## Core Rule

External agent-method absorption should use three evidence channels together:

1. source evidence
2. runtime behavior evidence
3. agent-interview evidence

No single channel is sufficient by itself.

## Evidence Channels

### 1. Source evidence

Read:

- repo README
- architecture docs
- skills
- key runtime files
- issues / discussions when needed

Use this to establish what the system claims and how it is designed.

### 2. Runtime behavior evidence

Run or observe the system when possible:

- CLI behavior
- session lifecycle
- memory behavior
- task routing
- automation behavior
- parallel/delegate behavior

Use this to establish what the system actually does.

### 3. Agent-interview evidence

When the external system is itself an agent, IKE may talk to it directly.

Examples:

- ask Hermes how it manages task distribution
- ask Claude Code how it recommends structuring long-running coding work
- ask a hosted agent system how it separates one-shot from interactive work

Use this to extract:

- internal operating assumptions
- intended usage patterns
- failure handling
- design tradeoffs

## Important Truth Boundary

Agent-interview evidence is useful, but it is not authoritative by itself.

Why:

- agents can overstate capabilities
- agents may describe ideal behavior rather than actual behavior
- an agent may summarize its own architecture inaccurately

So the controller rule is:

- use agent dialogue as a high-value signal source
- never use it as the sole truth source for adoption

## Standard Absorption Pipeline

### Step 1. Discovery

Capture one external signal:

- repo
- paper
- docs page
- skill
- architecture writeup
- live agent conversation

### Step 2. Durable capture

Write one durable note with:

- source
- date
- why it matters
- target IKE layer

### Step 3. Structured absorption judgment

Decide:

- adopt now
- adopt later
- reject
- watch only

### Step 4. Narrow packet

If adoption is approved, create one bounded implementation or governance
packet.

### Step 5. Validation

Prove the adopted idea in IKE:

- unit
- component
- harness
- staging

as appropriate

### Step 6. Runtime-compatible memory

Record the result so the idea has:

- origin
- absorption status
- related packets
- superseding decisions

## Recommended Record Types

### External signal note

- external project / skill / method found

### Absorption note

- what IKE should borrow
- what it should not borrow

### Implementation packet

- narrow adoption task

### Result milestone

- what actually landed

## Agent Interview Protocol

When talking to an external agent, ask targeted questions:

1. how do you separate short one-shot tasks from long interactive tasks
2. how do you keep task state from disappearing
3. how do you isolate parallel workers
4. what are your failure modes
5. what should not be copied blindly

Then compare the answers against:

- the source
- the observed behavior

## Current Controller Decision

IKE should formally add an `external method absorption` lane.

This lane is a support track for:

- runtime
- harness
- memory
- source intelligence
- governance

It is not an excuse for random research drift.

## First Sample

- [D:\code\MyAttention\docs\IKE_HERMES_SKILL_ABSORPTION_NOTE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_HERMES_SKILL_ABSORPTION_NOTE_2026-04-11.md)
