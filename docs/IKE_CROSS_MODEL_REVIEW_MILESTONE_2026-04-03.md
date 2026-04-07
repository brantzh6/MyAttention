# IKE Cross-Model Review Milestone 2026-04-03

## Purpose

This is the shortest review packet for another strong model to evaluate the current IKE mainline.

It is not a full project archive.
It is a milestone brief.

## 1. Project Goal

IKE is not a generic chat app and not a simple feed reader.

The project goal is to build a long-running intelligence system with:

- `Information Brain`
  - detect meaningful world changes
  - identify critical entities, communities, organizations, repositories, and events
- `Knowledge Brain`
  - turn those signals into structured concept understanding, relations, and usable knowledge
- `Evolution Brain`
  - decide what matters to the project itself
  - trigger bounded research/prototype work
  - improve methods, workflows, and memory over time

The current standard is:

- no fake capability
- no fake durability
- no semantic drift carried forward
- no uncontrolled implementation sprawl

## 2. Core Working Method

The project is developed with a controller/delegate model.

Controller responsibilities:

- architecture framing
- task decomposition
- acceptance criteria
- review and rejection of drift
- milestone shaping

Delegate responsibilities:

- bounded coding
- bounded review
- bounded analysis

Implementation protocol:

1. define a bounded packet
2. limit allowed files
3. define validation
4. force structured result
5. review before acceptance
6. immediately correct semantic drift if discovered

Current practical routing:

- `openclaw-glm`
  - bounded coding
- `openclaw-kimi`
  - analysis / review / long-context synthesis
- `qoder`
  - secondary / semi-automatic coding path

## 3. Current Mainline

The visible benchmark case is currently:

- `harness`

The intended proof is not:

- “we can inspect objects”

The intended proof is:

- information brain can detect and shape an emerging concept
- knowledge brain can explain what it is and what it is not
- evolution brain can decide whether it is relevant to IKE and what action level it deserves
- study closure can produce explicit procedural-memory candidates without hallucinating memory content

## 4. What Is Already Working

### A. IKE v0 migration seam exists

There is now a real IKE object layer, mapper layer, and transitional API layer.

Important principle already adopted:

- do **not** expose fake durable `GET /{type}/{id}` APIs before a real object access/store layer exists
- use truthful transitional operations instead:
  - `preview`
  - `inspect`
  - `generate`

### B. Harness benchmark has advanced beyond raw trend detection

Current benchmark progression:

- `B1`
  - signal + meaning + relevance hint
- `B2`
  - concept trigger
  - entity tiers
  - recommendation level
  - bounded trigger packet
- `B3`
  - working definition
  - boundary / non-boundary
  - mechanism-to-gap mapping
  - applicability judgment
- `closure`
  - study_result
  - decision_handoff
  - task_closure

### C. Procedural memory v1 now exists as a truthful prototype

Most important current rule:

- procedural memory is **not** auto-inferred from arbitrary closures
- first safe source is:
  - reviewed benchmark study closure

Current procedural memory v1:

- `procedure` only
- file-based local storage
- explicit payload only
- no automatic recall injection
- no fake generated lesson/confidence/how_to_apply

### D. Claude Code is now treated as a strategic engineering reference

Not just as a case study, but as a source of reusable engineering method.

Current conclusion:

- `memdir` is the highest-value subsystem to borrow from first

What matters in `memdir`:

- typed memory taxonomy
- bounded memory entrypoint/index
- selective recall
- post-task memory extraction

## 5. Visible UI Status

Main visible page:

- `/settings/ike`

Current visible improvements:

- benchmark story shape is understandable
- study closure is visible
- procedural-memory candidate is visible
- content layer now has:
  - English only
  - Chinese only
  - bilingual compare mode

Important limitation:

- content bilingual support is still benchmark-specific and bounded
- it is not yet a general i18n/content system

## 6. Biggest Current Weaknesses

### Weakness 1. Critical entity judgment is still not good enough

This is the most important quality problem.

The system shape is improving, but the identified people / organizations / repositories are still not reliably the most important ones.

Current failure mode:

- nearby entities are still too easily mistaken for concept-defining entities

### Weakness 2. Benchmark methods still need stronger evidence discipline

Need more explicit use of:

- authoritative official sources
- expert / maintainer sources
- implementation repositories
- community discourse
- media context
- primary technical artifacts
- cross-reference graph reasoning

### Weakness 3. Evolution-trigger quality is still only partial

Current state:

- the system can trigger study
- it cannot yet be trusted to trigger method adoption decisions by itself

### Weakness 4. Procedural memory is still candidate-level

Current state:

- explicit candidate exists
- reviewed pipeline exists
- but it is not yet a stable reusable memory loop for the whole project

## 7. Current Strategic Direction

The next stage is not “more UI”.

The next stage is:

1. improve critical entity discovery and authority verification
2. continue `harness` study with better object selection
3. connect benchmark study closure to procedural memory in a stable truthful way
4. keep learning from Claude Code engineering patterns
5. prepare a more reliable evolution-grade method trigger, not just a better summary

## 8. Immediate Next Plan

### Near-term

- continue refining benchmark entity judgment
- continue `harness` with one more bounded study packet
- continue improving evidence layering and concept-defining entity selection
- keep `/settings/ike` as a truthful benchmark surface, not a fake product shell

### Medium-term

- turn benchmark closure into a stable procedural-memory producer
- turn procedural-memory candidates into reviewed reusable method memory
- study Claude Code `permissions` and `coordinator` after `memdir`

## 9. What Needs Review

Another model should specifically judge:

1. Is the current project goal still coherent and ambitious in the right way?
2. Is the controller/delegate development method sound enough for long-running AI-assisted engineering?
3. Is the `harness` benchmark proving the right thing, or is it still too shallow?
4. Is procedural memory being introduced in a truthful and useful way?
5. Is the Claude Code borrowing strategy focused on the right subsystems?
6. What should the next real milestone be?

# Project Agent Harness Contract

## Purpose

This document defines how external or delegated AI coding agents should be harnessed for work in `D:\code\MyAttention`.

It is project-specific.
It is not a generic AI collaboration standard.
It is the shortest operational contract for:

- `OpenClaw`
- `Codex`
- `Qoder`
- other bounded coding/review agents

Use this when another developer or agent needs to contribute directly to this project without drifting from the established working method.

## 1. First Principle

This project uses a **controller + delegates** model.

Default rule:

- controller owns strategy, task shaping, review, and acceptance
- delegates own bounded implementation, bounded review, and bounded analysis

Do not treat any delegated coding agent as the project owner.

## 2. What Is Never Delegated

The following remain with the main controller:

- top-level project goal changes
- mainline priority changes
- architecture branch selection
- source-intelligence strategy changes
- evolution-brain strategy changes
- acceptance/rejection of delivered work
- semantic conflict resolution

If a task starts requiring one of these, stop and escalate.

## 3. What Is Usually Delegated

These are the preferred delegate categories:

- bounded coding tasks
- bounded UI changes
- bounded tests
- bounded bug fixes
- bounded analysis/research packets
- bounded review packets
- bounded adapter/mapping work

The delegate should receive one task with one scope and one expected result.

## 4. Current Practical Routing

Use the narrowest fitting agent.

### `openclaw-glm`

Use for:

- coding-heavy packets
- small to medium bounded implementation tasks
- additive prototype work
- tightly constrained code corrections

Do not use for:

- final architecture judgment
- broad refactors without strict file limits

### `openclaw-kimi`

Use for:

- review
- long-context analysis
- synthesis of competing options
- bounded research shape decisions

Do not use for:

- primary implementation

### `qoder`

Use for:

- secondary or semi-automatic coding execution
- cases where local IDE-style execution is useful

Current caveat:

- do not depend on qoder as the only unattended execution path

### `codex`

Inside this project, Codex should usually behave as:

- main controller
- review gate
- task packet author
- architecture and method shaper

Codex should not silently revert to being the default primary coder.

## 5. Mandatory Input for Every Delegated Task

Every delegated task must include:

1. `task_id`
2. `goal`
3. `allowed_files`
4. `forbidden_changes`
5. `required_context`
6. `validation`
7. `stop_conditions`
8. `delivery_format`

If one of these is missing, the task is underspecified.

## 6. Mandatory Output for Every Delegated Task

Every delegated result must include:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

Allowed recommendations:

- `accept`
- `accept_with_changes`
- `reject`

If blocked, return:

- blocker
- what was attempted
- what is missing

## 7. File and Scope Discipline

Default patch rules:

- change only allowed files
- use the smallest safe patch
- do not broaden scope
- do not mix unrelated fixes
- do not add dependencies unless explicitly requested
- do not fake backend support in frontend code

If the delegate needs another file outside scope:

- stop
- report the exact file and reason

Do not silently include it.

## 8. Truthfulness Rules

Delegates must not invent capability.

This includes:

- fake durable APIs
- fake translations
- fake memory extraction
- fake benchmark conclusions
- fake source authority
- fake fallback data in place of real runtime data

If the data is missing or weak:

- say so explicitly
- keep the result bounded

## 9. Review Gate

No delegated result is final until reviewed by the controller.

Default controller review criteria:

- missing validation -> reject or accept_with_changes
- broadened scope -> reject
- semantic drift -> reject
- strategy drift -> reject
- bounded patch with evidence -> eligible for acceptance

Important project rule:

- if semantic or structural drift is discovered, correct it immediately
- do not carry known wrong semantics forward

## 10. Quality Assurance Standard

Delegated work is not considered complete just because code compiles.

Each task must satisfy the right QA level for its type.

### For coding tasks

Minimum:

- relevant tests pass, or a precise reason is reported
- no obvious contract drift
- no hidden file changes outside scope

### For review tasks

Minimum:

- findings are prioritized
- file references are explicit
- risks and missing validation are called out

### For research/analysis tasks

Minimum:

- evidence source type is clear
- confidence is bounded and honest
- recommendation does not exceed evidence quality

### For UI tasks

Minimum:

- type-check passes
- visible behavior matches the task brief
- no fake/demo data if the task is supposed to show live/runtime state

## 11. Project-Specific Strategic Boundaries

Delegates must preserve these already-made corrections.

### Source intelligence

Do not regress to:

- domain-only thinking
- `topic -> source` as the only model

Prefer:

- object
- task intent
- role in context
- relation-aware judgment

### Evolution

Do not collapse evolution into watchdog behavior.

Preserve the split:

- watchdog = keepalive / threshold / runtime guard
- evolution = model-assisted diagnosis / prioritization / procedural improvement

### IKE validation

Do not treat a technical inspect page as sufficient proof of IKE value.

Visible validation should increasingly prove:

- world change detection
- concept/entity understanding
- project relevance judgment
- bounded research / closure / memory improvement

## 12. Current High-Priority Risks

New contributors should be aware of these before coding:

1. critical entity judgment is still weak
2. source-intelligence quality is not research-grade yet
3. benchmark story shape is ahead of benchmark evidence quality
4. procedural memory is still narrow and truthfulness-sensitive
5. evolution is still too rule-heavy in places

Do not accidentally optimize the visible shell while ignoring these.

## 13. Recommended Working Sequence

For a new delegated contributor:

1. read this file
2. read [D:\code\MyAttention\AGENTS.md](/D:/code/MyAttention/AGENTS.md)
3. read [D:\code\MyAttention\docs\CURRENT_MAINLINE_HANDOFF.md](/D:/code/MyAttention/docs/CURRENT_MAINLINE_HANDOFF.md)
4. read the exact task brief
5. read only the necessary context files
6. execute the bounded task
7. validate
8. return structured result

## 14. Success Condition

This harness contract is working if another strong coding agent can:

- enter the project quickly
- avoid architecture drift
- execute a bounded task correctly
- return an auditable result
- survive controller review without major rework

If not, the harness is incomplete and must be tightened.

# IKE Claude Code Research Decision

## Decision

Do **not** split Claude Code research into a separate project yet.

Current decision:

- continue Claude Code research **inside the current IKE project**
- treat it as a strategic reference track
- only split into a standalone project later if the extracted patterns become clearly reusable across multiple projects

## Why Not Split Now

### 1. The current value is still IKE-directed

The current research is not generic enough yet.

It is being used to improve:

- IKE procedural memory
- IKE controller/delegate engineering
- IKE task closure
- IKE active work surface clarity
- IKE long-running AI-assisted development method

That means the nearest proof of value is still inside IKE.

### 2. Splitting now would create premature divergence

A separate repo would immediately create:

- another planning surface
- another review surface
- another maintenance surface
- risk of method drift between research and implementation

At the current maturity level, that cost is higher than the benefit.

### 3. The right test is “can this improve IKE in practice?”

The current stage should answer:

- does `memdir`-inspired procedural memory improve our workflow?
- do Claude-style constraints improve collaboration quality?
- do closure-to-memory patterns survive real benchmark use?

Until those answers are stronger, a separate project would mostly be organizational overhead.

## What To Do Now

Continue the Claude Code line in the current project as a staged reference track.

### Stage 1. Mapping

Already underway:

- subsystem mapping
- identify which parts are strategically valuable

### Stage 2. Focused study

Current focus order:

1. `memdir`
2. `permissions`
3. `coordinator`

### Stage 3. IKE-local prototype

Only borrow patterns through narrow prototypes:

- procedural memory
- truthful closure adapter
- bounded task/memory loops

### Stage 4. Validate inside real IKE work

Prove value through:

- benchmark closure
- procedural-memory candidates
- improved controller/delegate quality

## When To Split Into A New Project

Only split later if most of these become true:

1. at least 2-3 extracted patterns are clearly project-agnostic
2. the patterns are no longer tightly tied to IKE semantics
3. another project would plausibly benefit from the same harness/memory/runtime layer
4. the standalone surface is clearer than keeping it embedded

Examples of possible future standalone outcomes:

- agent memory harness
- AI development control plane
- procedural-memory runtime
- task closure / decision handoff toolkit

## Current Recommendation

Short-term recommendation:

- **research inside IKE**

Medium-term recommendation:

- **update the starter kit with validated lessons**

Long-term recommendation:

- **consider a standalone project only after the reusable layer is proven**
