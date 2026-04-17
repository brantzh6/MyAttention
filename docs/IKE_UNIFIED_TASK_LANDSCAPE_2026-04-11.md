# IKE Unified Task Landscape

Date: 2026-04-11
Status: controller operational map

## Purpose

Provide one compact controller-facing map of the current project work
landscape.

This document answers:

1. what is the true active mainline
2. what support tracks exist
3. what research tracks exist
4. whether each line is on track
5. what the next step is for each line

## Classification Rule

The project should distinguish three work classes:

1. `active mainline`
2. `active support track`
3. `research / long-horizon track`

Not every important line is a mainline.

## Current Active Mainline

### 1. IKE Runtime v0

Class:

- `active mainline`

Purpose:

- make runtime task / decision / memory truth real
- close controller-governed operational task management
- create the real future home for memory and task management

Current state:

- materially on track
- runtime truth core is real
- multiple narrow runtime packets are landed through `R2-I18`
- current visible blocker is not conceptual drift but validation and
  operational closure on the current machine

Current immediate edge:

- finish `R2-I18` validation closure
- keep runtime narrow and truthful
- avoid widening into detached supervisor or broad orchestration claims
- define Runtime v0 exit criteria so refinement has a real handoff boundary
- reduce single-controller continuity fragility by making runtime the actual
  operational substrate rather than chat-memory continuation

Expectation judgment:

- `on_track`

Primary entry:

- [D:\code\MyAttention\docs\CURRENT_RUNTIME_MAINLINE_INDEX_2026-04-10.md](/D:/code/MyAttention/docs/CURRENT_RUNTIME_MAINLINE_INDEX_2026-04-10.md)

## Current Next Product-Capability Start Line

### 2. Source Intelligence V1

Class:

- `next product-capability start line`

Purpose:

- improve upstream source quality
- turn topic-driven discovery and classification into a real bounded system
  capability
- reduce dependence on fixed source lists and ad hoc discovery

Current state:

- on track to start
- research exists
- architecture exists
- implementation start packet now exists
- M1 scope and coding brief now exist
- landing decision and implementation task packet now exist
- coding has not started yet

Current immediate edge:

- hand the M1 packet to a bounded coding/review lane
- keep the first slice narrow:
  - inspect-style or helper-style
  - no broad collector rewrite
  - no fake claim of research-grade source intelligence
- the line now has a direct multi-agent packet for coding/review/testing/
  evolution execution

Expectation judgment:

- `on_track`

Primary entry:

- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_PHASE_JUDGMENT_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_PHASE_JUDGMENT_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_IMPLEMENTATION_START_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_IMPLEMENTATION_START_PACKET_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_SCOPE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_SCOPE_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_CODING_BRIEF_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_CODING_BRIEF_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_IMPLEMENTATION_TASK_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_IMPLEMENTATION_TASK_PACKET_2026-04-11.md)

## Current Active Support Tracks

### 3. Delivery governance and rollback discipline

Class:

- `active support track`

Purpose:

- keep project acceleration recoverable
- prevent self-evolution and delegated work from silently becoming production
  truth

Current state:

- on track
- baseline governance docs exist
- implementation-facing docs now exist for staging/prod identity, promotion
  checklist, and backup inventory
- this line is now useful, not just conceptual

Current immediate edge:

- convert staging/prod identity from documents into real config and deployment
  baselines
- add active-surface compression so documentation scale does not become hidden
  controller drag

Expectation judgment:

- `on_track`

Primary entry:

- [D:\code\MyAttention\docs\IKE_DELIVERY_GOVERNANCE_INDEX_2026-04-11.md](/D:/code/MyAttention/docs/IKE_DELIVERY_GOVERNANCE_INDEX_2026-04-11.md)

### 4. Project governance <-> runtime alignment

Class:

- `active support track`

Purpose:

- keep current project task/memory governance compatible with future runtime
  truth
- avoid building two conflicting management systems

Current state:

- on track
- alignment baseline is now explicit
- memory tiers are now explicit
- this line is still mostly semantic/governance work, not yet automatic system
  migration

Current immediate edge:

- apply alignment rules to active project task surfaces and retention habits

Expectation judgment:

- `on_track`

Primary entry:

- [D:\code\MyAttention\docs\IKE_PROJECT_RUNTIME_ALIGNMENT_2026-04-11.md](/D:/code/MyAttention/docs/IKE_PROJECT_RUNTIME_ALIGNMENT_2026-04-11.md)

### 5. Agent harness hardening

Class:

- `active support track`

Purpose:

- keep delegated execution bounded, auditable, and increasingly sandboxed

Current state:

- on track
- isolated workspaces exist
- metadata vocabulary is materially landed through write-scope/network-policy
  and sandbox-identity layers
- full enforcement is not complete yet

Current immediate edge:

- avoid overstating current sandbox quality
- keep future hardening narrow and implementation-backed
- complete one explicit boundary-proof packet so current harness claims are
  evidence-backed rather than phrased only as controller caution
- use a checklist/result-template pair so the proof can be executed and
  reviewed consistently

Expectation judgment:

- `on_track`

Primary entry:

- [D:\code\MyAttention\docs\CURRENT_AGENT_HARNESS_INDEX_2026-04-10.md](/D:/code/MyAttention/docs/CURRENT_AGENT_HARNESS_INDEX_2026-04-10.md)

### 6. Rename / cutover / workspace isolation

Class:

- `active support track`

Purpose:

- reduce workspace pollution
- prepare safe eventual migration from `MyAttention` to `IKE`

Current state:

- partially on track
- important cleanup and isolation groundwork exists
- but this line should no longer compete with runtime for top priority

Current immediate edge:

- keep this line narrow
- only do the pieces that directly unblock runtime, governance, or deployment
  hygiene

Expectation judgment:

- `on_track_but_not_top_priority`

Primary entry:

- [D:\code\MyAttention\docs\CURRENT_RENAME_CUTOVER_INDEX_2026-04-10.md](/D:/code/MyAttention/docs/CURRENT_RENAME_CUTOVER_INDEX_2026-04-10.md)

### 7. Evolution feedback routing

Class:

- `active support track`

Purpose:

- treat logs as real feedback
- keep low-value operational noise out of the controller lane

Current state:

- materially landed at a narrow level
- currently useful as a support rule, not a dominant project line

Current immediate edge:

- only extend when it supports runtime observability or operational triage
- keep the larger Evolution Brain upgrade as a later dedicated line, not a
  vague background promise

Expectation judgment:

- `on_track`

Primary entry:

- [D:\code\MyAttention\docs\IKE_EVOLUTION_LOG_FEEDBACK_ROUTING_RULE_2026-04-10.md](/D:/code/MyAttention/docs/IKE_EVOLUTION_LOG_FEEDBACK_ROUTING_RULE_2026-04-10.md)

## Current Research / Long-Horizon Tracks

### 8. Methodology / thinking-tool armory ingestion

Class:

- `research / long-horizon track`

Purpose:

- extract durable method and thinking tools
- decide which parts should later inform IDE/runtime behavior

Current state:

- inputs and study packets exist
- corpus extraction is ready
- execution has not yet closed into strong durable synthesis artifacts
- the value is real, but the line is not yet operationally mature

Current immediate edge:

- move from "reading / delegated run attempts" to reviewed synthesis packets
- classify outputs into:
  - archival-only
  - controller-useful
  - future runtime-ingest candidate
- use the explicit research pipeline rather than open-ended execution attempts
- do not overread this line as near-term product delivery

Expectation judgment:

- `valuable_but_not_yet_closed`

Primary entry:

- [D:\code\MyAttention\docs\IKE_THINKING_ARMORY_PDF_EXECUTION_STATUS_2026-04-09.md](/D:/code/MyAttention/docs/IKE_THINKING_ARMORY_PDF_EXECUTION_STATUS_2026-04-09.md)
- [D:\code\MyAttention\docs\IKE_THINKING_ARMORY_RESEARCH_PIPELINE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_THINKING_ARMORY_RESEARCH_PIPELINE_2026-04-11.md)

### 9. Knowledge Brain feasibility

Class:

- `research / long-horizon track`

Purpose:

- define the first narrow knowledge-structuring packet that can consume
  existing project substrate honestly

Current state:

- feasibility baseline now exists
- not yet an active implementation line
- should remain narrowly scoped when started

Current immediate edge:

- do not open broad knowledge-architecture coding
- later choose one small first feasibility packet over existing feed/runtime
  substrate

Expectation judgment:

- `useful_but_not_yet_active`

Primary entry:

- [D:\code\MyAttention\docs\IKE_KNOWLEDGE_BRAIN_MINIMUM_FEASIBILITY_NOTE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_KNOWLEDGE_BRAIN_MINIMUM_FEASIBILITY_NOTE_2026-04-11.md)

### 10. Managed agents / CREAO / DeerFlow / related external research

Class:

- `research / long-horizon track`

Purpose:

- understand how external agent systems solve harness, sandbox, or workflow
  problems that may matter for IKE

Current state:

- useful as reference scanning
- not yet a mainline delivery lane
- should stay subordinate to actual runtime and governance implementation

Current immediate edge:

- synthesize only if the output affects:
  - agent harness design
  - staging/prod separation
  - controller/runtime boundary decisions

Expectation judgment:

- `useful_reference_not_mainline`

## Current Controller Priority Order

1. `IKE Runtime v0`
2. `Source Intelligence V1`
3. `Delivery governance and rollback discipline`
4. `Project governance <-> runtime alignment`
5. `Agent harness hardening`
6. `Rename / cutover / workspace isolation`
7. `Evolution feedback routing`
8. `Methodology / thinking-tool armory ingestion`
9. `Methodology / thinking-tool armory ingestion`
10. `Knowledge Brain feasibility`
11. other external research tracks

## Current Risk Rule

If a support or research track starts taking energy away from runtime without a
clear unblock reason, it should be deprioritized.

The project currently needs convergence more than additional track growth.
