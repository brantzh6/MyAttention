# IKE Thinking Models and Method Armory

## Purpose

This document defines the top-layer "weapon library" for IKE.

It exists to separate:

- **thinking models**
  - how to frame and reason about a problem
- **execution methods**
  - how to investigate or operate once the thinking model is chosen

Without this layer, the system will continue to confuse:

- "what kind of problem is this?"
- "what method should be used?"
- "what search or benchmark steps should run?"

That confusion causes method drift.

## 1. Layering Rule

IKE should reason in three layers:

### Layer A: Thinking Models

Top-level reasoning frames.

Questions answered:

- what kind of problem is this
- what lens should be applied
- what should count as evidence
- what should *not* be overemphasized

### Layer B: Execution Methods

Operational approaches chosen after a thinking model is selected.

Examples:

- benchmark research loop
- source-plan-first deep research
- entity discovery and event capture
- closure-to-memory extraction

### Layer C: Concrete Tactics

Low-level operational actions.

Examples:

- where to search
- what queries to use
- which repos/topics/orgs to inspect
- how to score and compare evidence

## 2. Core Thinking Models

These are the primary reasoning frames IKE should be able to use.

### 2.1 Mechanism Analysis

Question:

- how does this actually work?

Use when:

- evaluating a technique, architecture, runtime, harness, memory system, or
  coordination method

Primary outputs:

- mechanism description
- moving parts
- dependency chain
- likely failure points

Do not overuse when:

- the problem is mainly about actors, incentives, or authority

### 2.2 System Layering

Question:

- which layers exist, and what belongs where?

Use when:

- boundaries are unclear
- one concern is being overloaded into another
- architecture is drifting

Primary outputs:

- layer map
- ownership boundaries
- interface boundaries
- anti-collapse guardrails

### 2.3 Causal Trace

Question:

- what caused this current state or event?

Use when:

- diagnosing regressions
- understanding major incidents
- reconstructing task or benchmark evolution

Primary outputs:

- causal chain
- trigger event
- propagation path
- leverage points

### 2.4 Boundary and Non-Boundary Analysis

Question:

- what is this, and what is it not?

Use when:

- concept meaning is fuzzy
- adjacent concepts are easily confused
- benchmark entities may be nearby but not defining

Primary outputs:

- working definition
- non-boundary list
- competing interpretations
- current best-fit interpretation

### 2.5 Evidence Hierarchy Review

Question:

- what evidence should count more?

Use when:

- generic search adjacency is too weak
- authority, directness, and primary artifacts matter

Primary outputs:

- evidence layer map
- authority ranking
- direct-vs-indirect evidence judgment
- confidence decomposition

### 2.6 Actor and Authority Mapping

Question:

- who matters, and why do they matter?

Use when:

- emerging concepts involve people, orgs, maintainers, institutions, or
  communities

Primary outputs:

- actor list
- authority basis
- role-in-concept
- concept-defining vs ecosystem-adjacent split

### 2.7 Relation and Network Mapping

Question:

- how are the relevant entities connected?

Use when:

- influence, citation, maintenance, ownership, or propagation relationships
  matter

Primary outputs:

- relation graph
- influence path
- reference path
- implementation path

### 2.8 Temporal and Evolutionary Analysis

Question:

- how is this changing over time?

Use when:

- events matter
- releases matter
- task state evolution matters
- benchmark meaning changes with time

Primary outputs:

- event timeline
- phase changes
- stability/volatility judgment
- trigger windows

### 2.9 Applicability and Gap-Mapping

Question:

- how does this help *our* project, and through what mechanism?

Use when:

- deciding whether an external concept should become a study, prototype, or
  adoption candidate

Primary outputs:

- touched gap
- mechanism-to-gap mapping
- applicability level
- recommendation level

### 2.10 Decision and Escalation Framing

Question:

- what should be done next?

Use when:

- current evidence is sufficient for action classification

Primary outputs:

- observe
- study
- prototype
- adopt_candidate
- defer
- reject

## 3. Routing Rules

Use the top-layer model first, then choose methods.

### 3.1 If the problem is "what is this concept really?"

Start with:

- boundary and non-boundary analysis
- actor and authority mapping
- evidence hierarchy review

Then use:

- benchmark research loop
- entity discovery

### 3.2 If the problem is "can this improve IKE?"

Start with:

- mechanism analysis
- applicability and gap mapping
- system layering

Then use:

- study packet
- closure / decision handoff

### 3.3 If the problem is "what happened and why?"

Start with:

- causal trace
- temporal and evolutionary analysis

Then use:

- event capture
- recovery analysis

### 3.4 If the problem is "which objects are truly important?"

Start with:

- actor and authority mapping
- evidence hierarchy review
- relation and network mapping

Then use:

- wide discovery
- object extraction
- entity judgment scorecard

### 3.5 If the problem is "where should this live architecturally?"

Start with:

- system layering
- mechanism analysis

Then use:

- architecture design packet
- migration/alignment analysis

## 4. Method Families Under the Armory

These are execution methods that sit under the thinking-model layer.

### 4.1 Benchmark Research Method

Use for:

- emerging topic evaluation
- concept -> entity -> trigger -> closure progression

### 4.2 Entity Discovery and Event Capture

Use for:

- wide discovery
- candidate pool formation
- authority verification
- event significance capture

### 4.3 Source-Plan-First Deep Research

Use for:

- structured deep research
- evidence collection before synthesis

### 4.4 Closure-to-Memory Extraction

Use for:

- deriving procedural memory candidates from accepted work

### 4.5 Runtime Governance Analysis

Use for:

- state machine
- task control
- role/permission design
- recovery and resilience

## 5. Evidence Rules Across All Models

No thinking model should collapse into:

- generic search ranking
- unweighted adjacency
- purely rhetorical synthesis

All models must preserve:

- evidence type
- authority basis
- directness
- uncertainty
- non-fit scenarios

## 6. Current Mainline Use

### Harness Benchmark

Current primary models:

- boundary and non-boundary analysis
- actor and authority mapping
- evidence hierarchy review
- applicability and gap mapping

### Claude Code Runtime Research

Current primary models:

- mechanism analysis
- system layering
- applicability and gap mapping

### IKE Runtime v0

Current primary models:

- system layering
- mechanism analysis
- temporal and evolutionary analysis
- decision and escalation framing

## 7. Current Recommendation

From now on, major research or architecture work should explicitly identify:

1. which thinking model(s) are in use
2. which execution method(s) are selected under them
3. what evidence rules apply

This is the only stable way to prevent:

- method drift
- benchmark theater
- architecture confusion
- searching before thinking

