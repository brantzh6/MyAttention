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

### Review Absorption Rule

Every meaningful review must be absorbed in two layers:

1. `now_to_absorb`
   - fixes, constraints, or scope changes that should affect the current packet
   - these must be written back into active docs/briefs immediately

2. `future_to_preserve`
   - valuable directions that are not current-scope work
   - these must be written into a durable backlog/decision log
   - they must not be left only in chat or omitted because they are "not now"

Do not treat:

- `not now`

as equivalent to:

- `not important`

Review is incomplete if future-value findings are not recorded durably.

## 9.1 Durable Recording Rule

Do not leave important project control information only in chat.

The following must be written into durable project artifacts when they occur:

- active mainline changes
- stable controller judgments
- meaningful review outcomes
- accepted method/rule changes
- preserved future-value findings
- packet-cycle results future work depends on

Preferred durable targets:

- `docs/CURRENT_MAINLINE_HANDOFF.md`
- `PROGRESS.md`
- `CHANGELOG.md`
- dedicated `docs/*.md`
- `docs/IKE_LONG_HORIZON_BACKLOG_AND_DECISION_LOG.md`

See:

- [D:\code\MyAttention\docs\PROJECT_DURABLE_RECORDING_AND_GIT_DISCIPLINE.md](/D:/code/MyAttention/docs/PROJECT_DURABLE_RECORDING_AND_GIT_DISCIPLINE.md)

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

## 11. Git Discipline

Git is part of the durability system for this project.

Milestones that change stable project state should not remain only in the
working tree for long.

At the next safe milestone, archive:

- review-absorbed design changes
- stable packet/result waves
- active mainline transitions
- accepted reusable method changes

See:

- [D:\code\MyAttention\docs\PROJECT_DURABLE_RECORDING_AND_GIT_DISCIPLINE.md](/D:/code/MyAttention/docs/PROJECT_DURABLE_RECORDING_AND_GIT_DISCIPLINE.md)

## 11. Independent Testing Leg

Testing is a first-class role, not a side effect of coding.

The current project must distinguish:

- coding
- review
- testing

Independent testing is required whenever a packet changes:

- runtime state semantics
- lease/recovery behavior
- trust boundaries
- memory acceptance
- visible benchmark truth claims

Reference:

- [D:\code\MyAttention\docs\PROJECT_TEST_AGENT_AND_VALIDATION_MATRIX.md](/D:/code/MyAttention/docs/PROJECT_TEST_AGENT_AND_VALIDATION_MATRIX.md)

## 12. Independent Evolution Leg

Evolution is also a first-class role, not just controller intuition.

It is responsible for:

- turning reviewed closures into procedural memory candidates
- preserving future-value review findings
- proposing durable method upgrades
- detecting benchmark theater and repeated failure patterns

Reference:

- [D:\code\MyAttention\docs\PROJECT_EVOLUTION_LOOP_AND_METHOD_UPGRADE.md](/D:/code/MyAttention/docs/PROJECT_EVOLUTION_LOOP_AND_METHOD_UPGRADE.md)

## 13. Multi-Agent Runtime Hardening Pattern

For high-risk runtime work, do not run a coding packet alone.

Default pattern:

1. controller packet
2. coding packet
3. review packet
4. test packet
5. evolution packet

Reference:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_SECOND_WAVE_MULTI_AGENT_CYCLE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_SECOND_WAVE_MULTI_AGENT_CYCLE.md)

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
