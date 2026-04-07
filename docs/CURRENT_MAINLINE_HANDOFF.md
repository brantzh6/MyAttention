# Current Mainline Handoff

## Purpose

This document is the shortest reliable handoff for another agent or engineer to continue the current mainline without re-deriving project state from the full conversation history.

It is intentionally operational, not visionary.

## Mainline Goal

The current mainline is:

1. Improve `source intelligence` quality so the information flywheel produces usable attention objects.
2. Keep `evolution brain` on the mainline, but distinguish it from watchdog/rule-engine behavior.
3. Reduce token pressure by using controlled delegation for bounded coding/review/analysis tasks.
4. Reframe visible IKE validation around real-world benchmark cases, not just technical inspect pages.
5. Improve critical entity judgment and event capture so benchmark conclusions are not driven by generic search adjacency.
6. Define `IKE Runtime v0` as the minimal memory/task/decision control kernel needed for both OpenClaw runtime continuity and controller/delegate engineering continuity.
7. Strengthen the missing independent `testing` leg and independent `evolution` leg so development quality does not rely only on coding delegates plus controller review.
8. Start `IKE Runtime v0` second-wave with hardening and one real task lifecycle proof, not with broader platform expansion.
9. Run second-wave as an explicit multi-agent cycle: controller + coding + review + testing + evolution, not coding/review alone.

Do not open new broad architecture branches before these are stabilized.

Latest runtime second-wave status:

- `R1-A1` hardening has been executed and controller-reviewed as `accept_with_changes`.
- `R1-A2` Kimi review lane has been restored and is operational again after the reviewer-channel fix.
- `R1-A3` test lane is now real, not placeholder-only:
  - `36` state-machine tests passed
  - `49` memory-packet tests passed
  - `7` migration-validation-support tests passed
- `R1-A` now has a single-file result milestone for cross-model review:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-A_RESULT_MILESTONE_2026-04-06.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-A_RESULT_MILESTONE_2026-04-06.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_V0_R1-A_RESULT_MILESTONE_2026-04-06.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_V0_R1-A_RESULT_MILESTONE_2026-04-06.md)
- Remaining second-wave known soft spots are now independently tested residual risks, not unverified assumptions:
  - legacy `role=None` force-path softness
  - caller-supplied upstream verifier trust contract
- The next controller judgment is now explicit:
  - do not start `R1-B` yet
  - run one more narrow enforcement cycle first:
    - `R1-A5` coding
    - `R1-A6` review
    - `R1-A7` testing
    - `R1-A8` evolution
- Current execution status:
  - `R1-A5` coding was executed
  - first attempt was rejected:
    - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-A5_ENFORCEMENT_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-A5_ENFORCEMENT_RESULT.md)
  - narrow correction pass then succeeded with `accept_with_changes`:
    - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-A5_FIX_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-A5_FIX_RESULT.md)
  - current stable outcome:
    - legal claim path restored
    - `role=None` force bypass remains closed
    - migration-validation subset now passes under the controller invocation pattern
  - `R1-A6` review and `R1-A8` evolution have now also executed successfully via `openclaw-kimi`
  - current controller judgment:
    - `R1-B` is conditionally ready
    - no further narrow enforcement packet is required before beginning one real task lifecycle proof
    - but these are still preserved future items, not forgotten:
      - remove legacy `allow_claim=True`
      - move delegate identity verification into service/runtime truth layer
      - add live Postgres migration up/down proof
- `R1-B` has now been materialized as the next active mainline:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-B_LIFECYCLE_PROOF_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-B_LIFECYCLE_PROOF_PLAN.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-B1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-B1_CODING_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-B2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-B2_REVIEW_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-B3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-B3_TEST_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-B4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-B4_EVOLUTION_BRIEF.md)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r1-b1-lifecycle-proof-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r1-b1-lifecycle-proof-glm.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-B_EXECUTION_PACK_2026-04-06.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-B_EXECUTION_PACK_2026-04-06.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-B_RESULT_MILESTONE_2026-04-06.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-B_RESULT_MILESTONE_2026-04-06.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_V0_R1-B_RESULT_MILESTONE_2026-04-06.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_V0_R1-B_RESULT_MILESTONE_2026-04-06.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-B1_LIFECYCLE_PROOF_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-B1_LIFECYCLE_PROOF_RESULT.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-B2_LIFECYCLE_REVIEW_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-B2_LIFECYCLE_REVIEW_FALLBACK.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-B4_LIFECYCLE_EVOLUTION_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-B4_LIFECYCLE_EVOLUTION_FALLBACK.md)
- Current truthful `R1-B` execution status:
  - `R1-B1` coding has now produced a dedicated lifecycle-proof test artifact
  - controller-side live pytest validation passed across lifecycle/state/event suites
  - `R1-B3` testing evidence is now real, but controller-side
  - delegated review/evolution lanes timed out again in this pass
  - controller fallback review/evolution have been recorded so the milestone is durable
  - the active remaining gap is now delegated reviewer/evolution lane recovery, not lifecycle-proof absence

Benchmark reference:

- [D:\code\MyAttention\docs\IKE_REAL_WORLD_BENCHMARKS.md](/D:/code/MyAttention/docs/IKE_REAL_WORLD_BENCHMARKS.md)
- [D:\code\MyAttention\docs\IKE_ENTITY_DISCOVERY_AND_EVENT_CAPTURE_METHOD.md](/D:/code/MyAttention/docs/IKE_ENTITY_DISCOVERY_AND_EVENT_CAPTURE_METHOD.md)
- [D:\code\MyAttention\docs\IKE_CLAUDE_CODE_REFERENCE_PLAN.md](/D:/code/MyAttention/docs/IKE_CLAUDE_CODE_REFERENCE_PLAN.md)
- [D:\code\MyAttention\docs\IKE_CLAUDE_CODE_B1_MAPPING.md](/D:/code/MyAttention/docs/IKE_CLAUDE_CODE_B1_MAPPING.md)
- [D:\code\MyAttention\docs\IKE_CLAUDE_CODE_B2_MEMDIR_STUDY.md](/D:/code/MyAttention/docs/IKE_CLAUDE_CODE_B2_MEMDIR_STUDY.md)
- [D:\code\MyAttention\docs\IKE_CROSS_MODEL_REVIEW_MILESTONE_2026-04-03.md](/D:/code/MyAttention/docs/IKE_CROSS_MODEL_REVIEW_MILESTONE_2026-04-03.md)
- [D:\code\MyAttention\docs\IKE_CROSS_MODEL_REVIEW_PROMPT_2026-04-03.md](/D:/code/MyAttention/docs/IKE_CROSS_MODEL_REVIEW_PROMPT_2026-04-03.md)
- [D:\code\MyAttention\docs\PROJECT_AGENT_HARNESS_CONTRACT.md](/D:/code/MyAttention/docs/PROJECT_AGENT_HARNESS_CONTRACT.md)
- [D:\code\MyAttention\docs\PROJECT_DURABLE_RECORDING_AND_GIT_DISCIPLINE.md](/D:/code/MyAttention/docs/PROJECT_DURABLE_RECORDING_AND_GIT_DISCIPLINE.md)
- [D:\code\MyAttention\docs\IKE_ENTITY_JUDGMENT_STRENGTHENING_PLAN.md](/D:/code/MyAttention/docs/IKE_ENTITY_JUDGMENT_STRENGTHENING_PLAN.md)
- [D:\code\MyAttention\docs\IKE_SECOND_BENCHMARK_SELECTION_PLAN.md](/D:/code/MyAttention/docs/IKE_SECOND_BENCHMARK_SELECTION_PLAN.md)
- [D:\code\MyAttention\docs\IKE_B5_HARNESS_ENTITY_REVIEW_CONTROLLER_NOTE.md](/D:/code/MyAttention/docs/IKE_B5_HARNESS_ENTITY_REVIEW_CONTROLLER_NOTE.md)
- [D:\code\MyAttention\docs\IKE_SECOND_BENCHMARK_SHORTLIST.md](/D:/code/MyAttention/docs/IKE_SECOND_BENCHMARK_SHORTLIST.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_SUBPROJECT_DECISION.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_SUBPROJECT_DECISION.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md)
- [D:\code\MyAttention\docs\IKE_MAGMA_CHRONOS_MEMORY_RESEARCH_NOTE.md](/D:/code/MyAttention/docs/IKE_MAGMA_CHRONOS_MEMORY_RESEARCH_NOTE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_REVIEW_MILESTONE_2026-04-04.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_REVIEW_MILESTONE_2026-04-04.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_EVOLUTION_ROADMAP.md](/D:/code/MyAttention/docs/IKE_RUNTIME_EVOLUTION_ROADMAP.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_PACKETS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_PACKETS.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DELEGATION_BACKLOG.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DELEGATION_BACKLOG.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-A_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-A_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-B_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-B_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-C_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-C_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-D_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-D_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-E_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-E_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-F_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-F_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_FIRST_WAVE_PACKET_INDEX.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_FIRST_WAVE_PACKET_INDEX.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_EXECUTION_PACK_2026-04-05.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_EXECUTION_PACK_2026-04-05.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_V0_IMPLEMENTATION_EXECUTION_PACK_2026-04-05.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_V0_IMPLEMENTATION_EXECUTION_PACK_2026-04-05.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_FIRST_WAVE_RESULT_MILESTONE_2026-04-05.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_FIRST_WAVE_RESULT_MILESTONE_2026-04-05.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_V0_FIRST_WAVE_RESULT_MILESTONE_2026-04-05.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_V0_FIRST_WAVE_RESULT_MILESTONE_2026-04-05.md)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-a-core-schema-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-a-core-schema-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-a-core-schema-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-a-core-schema-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-a-core-schema-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-a-core-schema-glm.json)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-A_CORE_SCHEMA_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-A_CORE_SCHEMA_RESULT.md)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-b-task-state-semantics-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-b-task-state-semantics-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-b-task-state-semantics-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-b-task-state-semantics-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-b-task-state-semantics-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-b-task-state-semantics-glm.json)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-c-events-leases-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-c-events-leases-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-c-events-leases-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-c-events-leases-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-c-events-leases-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-c-events-leases-glm.json)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-d-work-context-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-d-work-context-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-d-work-context-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-d-work-context-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-d-work-context-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-d-work-context-glm.json)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-e-memory-packets-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-e-memory-packets-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-e-memory-packets-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-e-memory-packets-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-e-memory-packets-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-e-memory-packets-glm.json)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-f-redis-rebuild-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-f-redis-rebuild-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-f-redis-rebuild-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-f-redis-rebuild-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-f-redis-rebuild-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-f-redis-rebuild-glm.json)
- [D:\code\MyAttention\docs\IKE_LONG_HORIZON_BACKLOG_AND_DECISION_LOG.md](/D:/code/MyAttention/docs/IKE_LONG_HORIZON_BACKLOG_AND_DECISION_LOG.md)
- [D:\code\MyAttention\docs\IKE_THINKING_MODELS_AND_METHOD_ARMORY.md](/D:/code/MyAttention/docs/IKE_THINKING_MODELS_AND_METHOD_ARMORY.md)
- [D:\code\MyAttention\docs\B4 review result.md](/D:/code/MyAttention/docs/B4%20review%20result.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_V0_REVIEW_MILESTONE_2026-04-04.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_V0_REVIEW_MILESTONE_2026-04-04.md)

## Operating Mode

Default mode:

- I act as the main controller.
- Implementation work should usually be delegated to qoder/openclaw or other bounded agents.
- I should primarily provide:
  - architecture framing
  - task decomposition
  - constraints
  - review
  - acceptance decisions

Exception mode:

- Direct code edits are allowed only when the user explicitly wants a fast, bounded corrective action or when delegation is unavailable.
- Even then, keep the patch narrow and preserve the mainline boundary.

## What Is Already True

### Runtime

- API/Web/Redis/Postgres/watchdog are running locally.
- Feed collection is automatic.
- Redis is now part of the feed cache path.

### Source Intelligence

- Discovery is no longer domain-only.
- Current object types include:
  - `domain`
  - `repository`
  - `person`
  - `organization`
  - `community`
  - `release`
  - `signal`
  - `event`
- `source-frontier-v1` is currently at policy version `6`.
- `source-method-v1` is currently at policy version `7`.

### Controlled Delegation

- `acpx + openclaw` file-based delegation works.
- Main control must remain local.
- Current routing:
  - `openclaw-glm` for coding-heavy delegation
  - `openclaw-qwen` for general execution
  - `openclaw-kimi` / reviewer for review and long-context analysis

## Important Corrections Already Made

These are not optional style preferences; they are mainline corrections.

### 1. Source value is contextual

Do not treat a source like `36kr` as globally good or globally bad.

Correct model:

- the same object/source can serve multiple topics
- the same object/source can serve multiple task intents
- value depends on `role in context`

Examples:

- `36kr` can be valid for `latest intelligence / industry signal`
- the same `36kr` item should not dominate `authoritative understanding`

### 2. Topic is not the only top-level axis

Avoid falling back to:

- `topic -> source`

Prefer thinking in:

- `object`
- `task intent`
- `role in context`
- `object relations`

### 3. Evolution brain is not the watchdog

Current system still contains too much watchdog/rule-engine logic.

Correct split:

- `watchdog/rule layer`: keepalive, thresholds, restart, simple checks
- `evolution layer`: model-assisted understanding, prioritization, diagnosis, policy adjustment, procedural improvement

## Current Mainline Problems

### P0. Source Intelligence Quality Is Still Not Good Enough

Status:

- direction is much better than before
- quality is still not at “research-grade”

Symptoms:

- generic search still influences candidate generation too much
- `person` is present but still weak relative to how a real researcher tracks people
- relationship structure is still shallow
- old plans/noisy plans dilute useful changes

### P0. Critical Entity Judgment Is Still Too Weak

Status:

- the benchmark shape is now visible and directionally useful
- the most important people, repositories, and organizations are still not reliably correct

Symptoms:

- generic discovery adjacency still pulls in nearby but non-defining entities
- authority and identity verification are still too weak
- structured summaries are not yet fully separated from primary technical artifacts
- major events are not yet captured through a repeatable multi-signal method
- entity tiers still need stronger tier reasons and authority grounding
- current benchmark success is still concentrated on one visible concept case
- current truthful baseline is that `harness` still has no justified
  `concept_defining` entity

### P0. Claude Code Strategic Reference Is Not Yet Turned Into Reusable Method

Status:

- local primary artifact is available
- first-pass mapping is now in place
- no bounded reusable pattern has been carried through to IKE yet

Next focus:

- `memdir` study first
- then a procedural-memory prototype plan
- then a minimal procedural-memory prototype
- then a closure-adapter bridge into existing IKE completion artifacts
- then benchmark-study-closure as the first truthful payload source
- then permission/coordinator packets

### P0. Evolution Brain Does Not Yet Detect “Workspace Usability” Well

Status:

- it detects runtime/quality issues
- it does **not** yet reliably detect:
  - noisy task surfaces
  - stale/irrelevant historical tasks
  - garbled titles / dirty data
  - “page is technically up but operationally confusing”

### P0. Task Surface Is Not Clean Enough

Current issues:

- repeated historical `source-plan` quality tasks
- old pending/failed tasks still mixed with active ones
- some titles/descriptions remain garbled
- `settings/sources` does not yet make the active improvements obvious enough

## Most Recent Effective Changes

### Source Role-in-Context Changes

The current code now does all of the following:

- normalizes media subdomains like `m.36kr.com` and `eu.36kr.com` into `36kr.com`
- treats contextual tech media differently by focus:
  - `latest` -> positive signal role
  - `frontier` -> weaker signal role
  - `method` -> weaker still
- classifies contextual tech media as `signal` instead of `authority` in `frontier/latest`

Files:

- `D:\\code\\MyAttention\\services\\api\\routers\\feeds.py`
- `D:\\code\\MyAttention\\services\\api\\attention\\policies.py`
- `D:\\code\\MyAttention\\services\\api\\tests\\test_source_discovery_identity.py`
- `D:\\code\\MyAttention\\services\\api\\tests\\test_attention_policy_foundation.py`

### Live Impact Confirmed

For `openclaw + frontier`, the current live portfolio now looks closer to:

- `person/community`
- `signal`
- `implementation`

instead of letting a tech media domain sit in the `authority` bucket.

## What To Do Next

### 0. Absorb The B4 Cross-Model Review Result

The latest cross-model review reinforced, not overturned, the current mainline.

Most important accepted takeaways:

- project goal and controller/delegate method remain sound
- critical entity judgment is still the main upstream quality risk
- benchmark shape is ahead of evidence quality
- procedural memory is truthful but still only candidate-level
- a second semantically different benchmark will be needed to test method generalization

### 0.5 Absorb The First B5 Harness Entity Review

Current accepted conclusion:

- there is still no justified `concept_defining` entity in the current harness benchmark
- strongest implementation object:
  - `slowmist/openclaw-security-practice-guide`
- strongest ecosystem object:
  - `LeoYeAI/openclaw-master-skills`

This should remain the truthful baseline until stronger evidence appears.

### 1. Clean the Active Work Surface

Do this before adding more discovery complexity.

Tasks:

- separate active issues from historical task instances
- archive or demote obviously stale legacy issues
- sanitize garbled task/source-plan titles
- make `settings/sources` default to active/recently-updated plans only

Acceptance:

- a user can open the task surface and immediately tell:
  - what is currently wrong
  - what is historical noise
  - which source plans are active and worth reviewing

### 2. Strengthen Person-Centered Discovery

Current `person` support is still not enough.

Tasks:

- improve active discovery of:
  - maintainers
  - researchers
  - speakers
  - lead authors
  - core contributors
- strengthen relation hints:
  - `person -> repo`
  - `person -> organization`
  - `person -> topic`
  - `person -> release/signal`

Acceptance:

- `person` candidates appear as first-class attention objects for `method` and `frontier`
- a relevant maintainer/researcher can outrank generic domain noise

### 3. Make Evolution Brain Judge the Workspace, Not Just Runtime

Tasks:

- add issue hygiene checks
- add work-surface usability checks
- promote “active surface prioritization” into evolution outputs

Acceptance:

- evolution can flag:
  - stale noisy task surfaces
  - garbled/dirty titles
  - source-plan views dominated by historical noise

### 4. Use Real-World Benchmark Cases For Visible Validation

The current pure inspect-style IKE page was not user-comprehensible enough.

Next visible IKE work should be judged against a benchmark like:

- harness / openclaw / AI-agent trend detection and project relevance

Acceptance:

- the visible output explains:
  - what changed
  - which entities matter
  - what the concept means
  - why it matters to this project
  - what next action should follow

### 5. Treat B1 As Real But Partial Success

Current benchmark progress:

- B1 now works as a real benchmark report
- B4 evidence layering now works as a benchmark-method upgrade
- the first real `study_result -> decision_handoff` closure now exists for
  `harness`
- current truthful state for `harness` is:
  - recommendation level: `study`
  - applicability: `partially_applicable`
  - decision handoff: `continue_study`
- the next benchmark-method step is not a new concept:
  - it is `B5 continued study`
  - focused on concept-definition quality and applicability tightening
- `B5` already produced one important correction:
  - `LeoYeAI/openclaw-master-skills` should be treated as
    `ecosystem_relevant`
  - not `implementation_relevant`
  - because it behaves like a curated skill catalog/distribution surface, not
    an evaluation-method repository
- but B1 should be treated as:
  - `signal + meaning + relevance hint`
- not yet as:
  - full research trigger
  - full evolution action engine

Do not keep polishing B1 ranking forever.

The next benchmark mainline is:

- [D:\code\MyAttention\docs\IKE_B2_CONCEPT_TRIGGER_PLAN.md](/D:/code/MyAttention/docs/IKE_B2_CONCEPT_TRIGGER_PLAN.md)

The next priority is:

- concept deepening
- entity tiering
- explicit mainline gap mapping
- bounded research/prototype trigger

The benchmark has now advanced further:

- B2 now produces:
  - entity tiers
  - narrowed gap mapping
  - recommendation level
  - bounded study trigger packet

The next benchmark mainline is:

- [D:\code\MyAttention\docs\IKE_B3_DEEPENING_PLAN.md](/D:/code/MyAttention/docs/IKE_B3_DEEPENING_PLAN.md)
- [D:\code\MyAttention\docs\IKE_TASK_CLOSURE_PLAN.md](/D:/code/MyAttention/docs/IKE_TASK_CLOSURE_PLAN.md)

The next benchmark-method mainline is:

- [D:\code\MyAttention\docs\IKE_B4_EVIDENCE_LAYER_PLAN.md](/D:/code/MyAttention/docs/IKE_B4_EVIDENCE_LAYER_PLAN.md)

Reason:

- current benchmark structure is now useful
- current benchmark evidence quality is still too exposed to generic discovery bias
- the next upgrade is explicit evidence-layer separation before stronger ranking or adoption decisions

## Delegation Guidance

Use delegation aggressively for bounded tasks.

Good delegation tasks:

- code review / challenge
- source quality analysis
- bounded frontend cleanup
- candidate generation experiments
- test additions

Do not delegate:

- top-level architecture control
- mainline priority changes
- acceptance / merge decisions
- source-intelligence strategy corrections

## Commands / Validation Patterns

Useful validation commands:

```powershell
python manage.py health --json
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/api/sources/discover' -ContentType 'application/json' -Body (@{ topic = 'openclaw'; focus = 'frontier'; limit = 8 } | ConvertTo-Json)
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/evolution/tasks?page=1&page_size=20'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/sources/plans'
```

Relevant tests:

```powershell
D:\code\MyAttention\.venv\Scripts\python.exe -m unittest tests.test_source_discovery_identity tests.test_attention_policy_foundation
```

## Final Warning

Do not mistake “more object types” for “quality solved”.

The mainline is still blocked by:

- active-surface clarity
- person-centered discovery quality
- model-assisted evolution reasoning replacing pure rule/watchdog thinking
## 2026-04-05 Runtime Update

- `IKE Runtime v0` `R0-A` has now been executed through the delegate channel and controller-reviewed.
- Current verdict: `accept_with_changes`
- Durable result review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-A_CORE_SCHEMA_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-A_CORE_SCHEMA_RESULT.md)

- `IKE Runtime v0` `R0-B` has also been executed through the delegate channel, corrected via a narrow fix packet, and controller-reviewed.
- Current verdict: `accept_with_changes`
- Durable result review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-B_TASK_STATE_SEMANTICS_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-B_TASK_STATE_SEMANTICS_RESULT.md)

Important runtime notes:

- `R0-A` currently covers the 9-table first-wave kernel surface defined by the active brief.
- `runtime_task_relations` remains deferred and preserved as a future runtime object candidate.
- Live PostgreSQL migration execution is still not confirmed in-controller because the current `.venv` lacks `pytest`; this remains a hardening follow-up, not a design reversal.
- `R0-B` is now acceptable as baseline after fix, but still carries two hardening notes:
  - `allow_claim` remains caller-asserted rather than object-backed
  - `force=True` on waiting updates must remain tightly controlled

- `IKE Runtime v0` `R0-C` has been executed through the delegate channel and controller-reviewed.
- Current verdict: `accept_with_changes`
- Durable result review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-C_EVENTS_LEASES_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-C_EVENTS_LEASES_RESULT.md)

Current `R0-C` note:

- event/lease/recovery semantics are now in place as baseline
- append-only discipline is still stronger at API contract level than at sealed in-memory structure level

- `IKE Runtime v0` `R0-D` has been executed through the delegate channel and controller-reviewed.
- Current verdict: `accept_with_changes`
- Durable result review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-D_WORK_CONTEXT_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-D_WORK_CONTEXT_RESULT.md)

Current `R0-D` note:

- `WorkContext` is now acceptable as derived snapshot carrier
- one-active-context enforcement still primarily depends on DB-level uniqueness plus caller discipline

- `IKE Runtime v0` `R0-E` has been executed through the delegate channel and controller-reviewed.
- Current verdict: `accept_with_changes`
- Durable result review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-E_MEMORY_PACKET_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-E_MEMORY_PACKET_RESULT.md)

Current `R0-E` note:

- packet lifecycle and trust boundary are now acceptable as v0 baseline
- explicit upstream linkage is now required for acceptance and trusted recall
- stronger linkage queryability and DB-backed upstream verification remain future hardening work
- fixed delegate result:
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-e-fix-memory-packets-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-e-fix-memory-packets-glm.json)

- `IKE Runtime v0` `R0-F` has been executed through the delegate channel and controller-reviewed.
- Current verdict: `accept_with_changes`
- Durable result review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-F_REDIS_REBUILD_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-F_REDIS_REBUILD_RESULT.md)

Current `R0-F` note:

- Redis acceleration/rebuild is now acceptable as a command-builder baseline
- Postgres remains truth and Redis loss degrades performance rather than durable state
- real execution adapter, observability, and tighter incremental sync discipline remain future hardening work

## 2026-04-06 Runtime Second-Wave Entry

- `R1-A` is now defined as a multi-agent hardening cycle:
  - coding
  - review
  - testing
  - evolution
- Current multi-agent cycle files:
  - [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r1-a1-hardening-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r1-a1-hardening-glm.md)
  - [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r1-a1-hardening-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r1-a1-hardening-glm.md)
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-a1-hardening-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-a1-hardening-glm.json)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-A1_HARDENING_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-A1_HARDENING_RESULT.md)
  - [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r1-a2-hardening-review-kimi.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r1-a2-hardening-review-kimi.md)
  - [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r1-a2-hardening-review-kimi.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r1-a2-hardening-review-kimi.md)
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-a2-hardening-review-kimi.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-a2-hardening-review-kimi.json)
  - [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r1-a3-hardening-test.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r1-a3-hardening-test.md)
  - [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r1-a3-hardening-test.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r1-a3-hardening-test.md)
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-a3-hardening-test.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-a3-hardening-test.json)
  - [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r1-a4-hardening-evolution-kimi.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r1-a4-hardening-evolution-kimi.md)
  - [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r1-a4-hardening-evolution-kimi.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r1-a4-hardening-evolution-kimi.md)
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-a4-hardening-evolution-kimi.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-a4-hardening-evolution-kimi.json)

Current `R1-A1` note:

- delegate execution completed
- controller verdict is currently `accept_with_changes`
- core improvement is real, but two soft spots remain:
  - `role=None` still leaves a legacy force-path softness
  - upstream truth still depends on a caller-supplied verifier callback

Current `R1-A2` note:

- `openclaw-kimi` session timed out
- result file remained template-only
- usable review currently comes from controller review, not delegate review
## 2026-04-06 Kimi Channel Recovery

- `openclaw-kimi` reviewer/evolution channel recovered
- root cause:
  - reviewer agents in `C:\Users\jiuyou\.openclaw\openclaw.json`
  - were pinned to `bailian-coding-plan/kimi-k2.5`
  - that route returned `401 Incorrect API key provided`
- fixed by switching:
  - `myattention-reviewer`
  - `myattention-kimi-review`
  to:
  - `modelstudio/kimi-k2.5`
- reviewer main session reset after model-route fix
- real delegated packets now working again:
  - `R1-A2` review
  - `R1-A4` evolution
- reference:
  - `D:\code\MyAttention\docs\OPENCLAW_KIMI_CHANNEL_FIX_2026-04-06.md`
## 2026-04-06 OpenClaw Alias Cleanup

- `.acpxrc.json` alias layer cleaned up
- canonical usage now:
  - `openclaw-coder`
  - `openclaw-glm`
  - `openclaw-kimi`
  - `openclaw-kimi-review`
  - `openclaw-reviewer`
- `openclaw-qwen` retained only as legacy compatibility alias
- `openclaw-kimi` now routes to:
  - `agent:myattention-kimi-review:main`
- `openclaw-reviewer` remains:
  - `agent:myattention-reviewer:main`
- backup profiles now standardized on:
  - `bailian/qwen3.6-plus`
  for:
  - `myattention-coder`
  - `myattention-reviewer`
- reference:
  - `D:\code\MyAttention\docs\OPENCLAW_AGENT_ALIAS_MAP_2026-04-06.md`

## 2026-04-07 Review/Evolution Lane Recovery

- reviewer/evolution transport root cause was narrowed to local OpenClaw route
  drift, not packet semantics
- actual bad state was:
  - `myattention-kimi-review -> bailian-coding-plan/kimi-k2.5`
  - `myattention-reviewer -> bailian-coding-plan/kimi-k2.5`
  - both polluted by stale `authProfileOverride = bailian-coding-plan:default`
- corrected live local split is now:
  - `myattention-kimi-review -> modelstudio/kimi-k2.5`
  - `myattention-reviewer -> bailian/qwen3.6-plus`
- both lanes passed minimal `OK` probes after correction
- `R1-B2` and `R1-B4` were then rerun and recovered as real delegated results
- reference:
  - `D:\code\MyAttention\docs\OPENCLAW_REVIEW_EVOLUTION_ROUTE_RECOVERY_2026-04-07.md`

## 2026-04-07 R1-B Lifecycle Milestone Truth

- `R1-B1` coding proof is real:
  - dedicated proof file exists at:
    - `D:\code\MyAttention\services\api\tests\test_runtime_v0_lifecycle_proof.py`
- `R1-B3` testing is real:
  - controller live validation passed at `201` runtime tests
- `R1-B2` review is now a real delegated result, not fallback-only
- `R1-B4` evolution is now a real delegated result, not fallback-only
- current truthful judgment:
  - `R1-B` = `accept_with_changes`
- remaining change is substantive:
  - remove legacy `allow_claim=True` path once truth-layer verification is
    runtime-native
