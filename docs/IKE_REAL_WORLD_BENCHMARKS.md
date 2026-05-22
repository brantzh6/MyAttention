# IKE Real-World Benchmarks

## Purpose

This document defines real-world benchmark cases that IKE must eventually pass.

These are not synthetic demo flows.
They are reality-based tests for whether the system can:

- notice meaningful change in the world
- organize that change into usable knowledge
- connect that knowledge back to the project's own evolution

The benchmark is not satisfied by:

- raw API outputs
- isolated inspect pages
- internal object loops with no user-understandable value

## Benchmark Design Rule

Every benchmark should test all three brains together:

1. Information Brain
2. Knowledge Brain
3. Evolution Brain

The benchmark passes only if the system can show:

- what it detected
- why it matters
- how it is connected
- what action or project movement follows

## Benchmark B1: Harness / OpenClaw / AI Agent Trend

### Scenario

Assume:

- `openclaw`
- `AI agent`
- related tooling and methods

are already within the project's attention field.

Then a new concept or tool pattern becomes hot, such as:

- `harness`
- a new evaluation pattern
- a new skill pattern
- a new coordination pattern
- a new testing or runtime method

The system should not require the user to manually explain why it matters.

### Information Brain Expectations

The Information Brain should be able to:

1. detect that a concept like `harness` is becoming more prominent
2. identify the entities around it:
   - people
   - maintainers
   - projects
   - organizations
   - communities
3. identify which entities are likely high-signal or influential
4. connect the trend to already-followed topics such as:
   - `openclaw`
   - `AI agent`
   - evaluation
   - testing
   - runtime / orchestration

It is not enough to collect generic media coverage.
The system should increasingly weight:

- maintainers
- project repos
- release notes
- community discussions
- high-signal authors / experts

### Knowledge Brain Expectations

The Knowledge Brain should be able to produce:

1. a concise explanation of what `harness` means in context
2. the key variants or interpretations
3. the relation to adjacent methods:
   - testing
   - evaluation
   - benchmark
   - runtime inspection
   - agent verification
4. the differences from nearby concepts
5. the likely fit with already-followed project/tooling ecosystems

It is not enough to return disconnected snippets.
The system should organize:

- concept
- entities
- relations
- distinctions
- relevance to the project

### Evolution Brain Expectations

The Evolution Brain should be able to:

1. recognize that this trend is directly relevant to the project
2. explain why it is relevant
3. decide whether it should influence:
   - testing
   - skill design
   - source intelligence
   - review gates
   - runtime inspection
   - delegation workflow
4. create or recommend a bounded next action
5. avoid treating the trend as generic background noise

It is not enough to log the trend.
The trend should be able to move the project.

## Pass Criteria

This benchmark is passed only when the system can present a user-understandable output that answers:

1. What changed in the world?
2. Which people / projects / communities matter?
3. What does the new method or concept actually mean?
4. How is it related to what we already care about?
5. Why does it matter to this project right now?
6. What should the system do next because of it?

## Current Gap

Current IKE v0.1 work proves an internal inspectable loop, but it does not yet pass this benchmark.

Current gaps include:

- person-centered discovery is still too weak
- concept/entity/relation summaries are not yet presented as one coherent insight
- evolution can detect many runtime issues, but it does not yet reliably convert world change into project-moving action
- the current visible IKE workspace is still too inspect-oriented and not meaning-oriented

## Immediate Use

This benchmark should now be used as:

- a controller test case
- a prioritization filter
- a design constraint for the next visible milestone

Any new visible IKE surface should be judged against whether it helps the system move closer to this benchmark.

## Benchmark Stage Rule

Benchmarks should be understood in explicit stages.

### Stage 1: Signal / Meaning / Relevance Hint

This stage proves:

- the system can detect a concept
- identify related entities
- produce an initial meaning summary
- produce an initial relevance judgment

This stage is valuable, but it is not yet a full research trigger.

### Stage 2: Concept Deepening / Research Trigger

This stage proves:

- the system can separate concept-defining entities from merely related ones
- compare concept boundaries against nearby methods
- map the concept to current project gaps
- escalate to a bounded research or prototype packet

Future benchmark work should not confuse Stage 1 with Stage 2.

## Current Benchmark Method Risk

The current visible benchmark work is still concentrated on:

- `harness`

This is useful, but it creates a method-generalization risk.

The project should not assume that because one benchmark can progress through
`B1 -> B2 -> B3 -> closure`, the same method is already proven across other
concept types.

The next benchmark should therefore test:

- whether entity judgment survives a semantically different concept
- whether concept-deepening still works when the concept is more ambiguous
- whether recommendation and closure stay truthful outside the current case

## Long-Term Rule

IKE should not be judged mainly by whether it has:

- more APIs
- more schemas
- more pages

It should be judged by whether it can:

- perceive emerging methods, tools, and patterns
- connect them to prior world knowledge
- reason about project relevance
- and push the project forward with bounded, reviewable action
