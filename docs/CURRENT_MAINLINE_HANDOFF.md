# Current Mainline Handoff

## Purpose

This document is the shortest reliable handoff for another agent or engineer to continue the current mainline without re-deriving project state from the full conversation history.

It is intentionally operational, not visionary.

## Mainline Goal

The current mainline is:

1. Improve `source intelligence` quality so the information flywheel produces usable attention objects.
2. Keep `evolution brain` on the mainline, but distinguish it from watchdog/rule-engine behavior.
3. Reduce token pressure by using controlled delegation for bounded coding/review/analysis tasks.

Do not open new broad architecture branches before these are stabilized.

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
