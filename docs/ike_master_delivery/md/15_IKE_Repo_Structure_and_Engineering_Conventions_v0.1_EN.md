# IKE Repo Structure and Engineering Conventions v0.1

## 1. Purpose

This document defines the engineering conventions for the first implementable version of IKE. Its goal is to give Codex and human developers a stable repository shape, naming policy, quality gate, and day-to-day operating model so the system can be built without structural drift.

This document is intentionally practical. It does not redefine the conceptual architecture; it translates the previously defined system boundaries, data contracts, API surfaces, and governance rules into repository-level conventions.

## 2. Design principles

The repository should optimize for:
- fast iteration in a modular monolith shape;
- strong contracts between modules before service extraction;
- schema-first development for shared objects and artifacts;
- English-first source documents for long-term LLM collaboration;
- deterministic quality gates through harness, tests, and review artifacts.

The repository should explicitly avoid:
- early microservice decomposition;
- business logic spread across routers, scripts, and notebooks;
- duplicate schema definitions in multiple modules;
- hidden workflow state in ad hoc files;
- domain logic encoded only in prompts.

## 3. Recommended repository form

The recommended starting point is a monorepo with one application runtime and a small set of reusable internal packages.

```text
ike/
  apps/
    api/
    worker/
    console/
  packages/
    core/
    schemas/
    objects/
    memory/
    information/
    knowledge/
    evolution/
    thinking_models/
    governance/
    workflow/
    harness/
    observability/
    common/
  docs/
    architecture/
    specs/
    product/
    decisions/
  data/
    seeds/
    fixtures/
    eval/
    paradigm_packs/
  scripts/
  infra/
  tests/
  .github/
```

This shape supports A and B stage execution while leaving a clean path toward C and D.

## 4. Top-level directories

### 4.1 `apps/`
Runtime entry points. Keep them thin.

- `apps/api/`: HTTP and internal control APIs.
- `apps/worker/`: background job workers, schedulers, orchestration entry points.
- `apps/console/`: admin and governance UI, or a placeholder package if UI is deferred.

### 4.2 `packages/`
Internal packages that contain durable business logic.

Recommended packages:
- `core/`: shared abstractions, IDs, result envelopes, error types.
- `schemas/`: canonical Pydantic or JSON schema definitions.
- `objects/`: object constructors, lifecycle helpers, validation wrappers.
- `memory/`: shared memory read/write services and projection logic.
- `information/`: ingestion, source management, signal extraction, watchlists.
- `knowledge/`: entity extraction, relation building, claim management, field models.
- `evolution/`: concept tracking, direction finding, adoption planning.
- `thinking_models/`: reasoning models, paradigm packs, model registry.
- `governance/`: meta-reasoning policies, reviews, promotion/freeze/retire rules.
- `workflow/`: tasks, experiments, decisions, orchestration policies.
- `harness/`: suites, scorers, reports, fixtures, evaluation runtime.
- `observability/`: logging, metrics, traces, review dashboards.
- `common/`: utilities with truly cross-cutting use only.

### 4.3 `docs/`
Documentation is first-class code-adjacent material.

Suggested structure:
- `docs/architecture/`: system-level documents.
- `docs/specs/`: module specs, schemas, interface notes.
- `docs/product/`: product surfaces and user flows.
- `docs/decisions/`: architecture decision records.

### 4.4 `data/`
Checked-in low-volume data used for bootstrap, testing, and evaluation.

Suggested content:
- `seeds/`: default sources, starter paradigms, starter thinking models.
- `fixtures/`: deterministic development fixtures.
- `eval/`: benchmark and harness datasets.
- `paradigm_packs/`: structured paradigm starter packs by domain.

### 4.5 `infra/`
Local and deployable infrastructure definitions:
- docker compose;
- queue and worker profiles;
- secrets templates;
- environment templates;
- deployment notes.

### 4.6 `tests/`
Cross-package tests that verify contracts and integrated behavior. Package-local unit tests may also live beside the code if that improves ownership.

## 5. Language and documentation policy

The source-of-truth policy is:

- Primary editable spec source: English Markdown.
- Translation layer: Chinese Markdown.
- Review/export artifact: Chinese DOCX.
- File names: ASCII only.

This rule should apply to future architecture, product, and governance specifications. The goal is to maximize compatibility with LLM-assisted iteration while keeping review materials readable for the current team.

## 6. Naming conventions

### 6.1 Files and directories
- Use lowercase snake_case for Python files and directories.
- Use ASCII only for file names.
- Use clear semantic names over abbreviations.

Examples:
- `task_engine.py`
- `model_registry.py`
- `research_task_service.py`

### 6.2 Classes and types
- Use PascalCase for classes and DTOs.
- Domain objects should be explicit: `ResearchTask`, `ThinkingModel`, `DecisionRecord`.

### 6.3 IDs
Use typed prefixed IDs everywhere. Avoid anonymous UUIDs in application-facing contexts.

Examples:
- `src_...`
- `obs_...`
- `ent_...`
- `rel_...`
- `tsk_...`
- `exp_...`
- `dec_...`
- `mdl_...`
- `prg_...`

## 7. Module ownership and dependency rules

The dependency direction should remain inward and stable.

Recommended rule set:
- `apps/*` may depend on all packages, but should contain almost no business logic.
- `workflow/` may orchestrate `information/`, `knowledge/`, `evolution/`, `thinking_models/`, `governance/`, `harness/`.
- `governance/` may read from all domains but should write mainly through explicit policies and decision interfaces.
- `schemas/` and `core/` should not depend on domain packages.
- `common/` must not become a dumping ground.

Forbidden patterns:
- `information/` directly depending on `console/`.
- `schemas/` importing runtime services.
- routers making governance decisions inline.
- prompts becoming the only expression of policy.

## 8. Code layout inside packages

Each package should use a predictable shape.

Suggested internal layout:
```text
package_name/
  __init__.py
  models.py
  service.py
  repository.py
  policies.py
  selectors.py
  adapters.py
  errors.py
  tests/
```

Not every package needs every file, but the shape should stay familiar.

A more explicit alternative for larger packages:
```text
knowledge/
  entities/
  relations/
  claims/
  field_models/
  services/
  repositories/
  policies/
  tests/
```

Use whichever form keeps boundaries clearer.

## 9. Schema-first development rule

Any object that crosses one of these boundaries must have a canonical schema:
- package boundary;
- API boundary;
- workflow artifact boundary;
- persistence boundary for durable objects;
- harness artifact boundary.

Canonical schemas should live in `packages/schemas/`.

Recommended substructure:
```text
packages/schemas/
  envelope/
  sources/
  observations/
  entities/
  relations/
  claims/
  tasks/
  experiments/
  decisions/
  thinking_models/
  paradigms/
  governance/
  harness/
```

No package should redefine these shapes locally.

## 10. Persistence conventions

Suggested storage roles:
- relational database: durable canonical objects and workflow state;
- object storage: large artifacts, reports, snapshots, raw captures;
- vector store: embeddings and retrieval surfaces;
- cache/queue: short-lived execution state.

Rules:
- persistent domain state must not live only in queues;
- object storage keys must be traceable back to canonical IDs;
- schema version must travel with durable artifacts;
- write paths should emit structured events where meaningful.

## 11. API and router conventions

HTTP routers should be thin translation layers.

Rules:
- request validation -> service call -> structured response;
- no hidden side effects in routers;
- no direct repository composition in routers;
- long-running work should return task IDs and progress handles.

Suggested API grouping:
- `/sources`
- `/observations`
- `/entities`
- `/relations`
- `/claims`
- `/tasks`
- `/experiments`
- `/decisions`
- `/thinking-models`
- `/paradigms`
- `/governance`
- `/harness`
- `/health`

## 12. Workflow and job conventions

Jobs should be explicit objects, not implicit code paths.

Required qualities:
- idempotent handlers;
- resumable task steps where possible;
- typed payloads;
- structured status transitions;
- emitted review artifacts.

Long-running workflows should prefer:
- task record;
- substep state;
- artifact emission;
- event trail.

## 13. Prompt and model integration conventions

Prompts are configuration, not the source of truth for business rules.

Rules:
- prompts live in versioned files, not buried in code strings;
- prompts reference explicit object fields and policy inputs;
- model choices must be logged with rationale and execution metadata;
- structured output schemas should be enforced whenever possible.

Suggested path:
```text
packages/thinking_models/prompts/
packages/evolution/prompts/
packages/harness/prompts/
```

## 14. Test and harness conventions

Testing should exist at four layers:
- unit tests for package logic;
- contract tests for schemas and interfaces;
- workflow integration tests;
- harness suites for system-level evaluation.

Recommended directories:
```text
tests/
  contract/
  integration/
  workflow/
  harness/
```

Each package may also keep focused unit tests locally.

## 15. Configuration conventions

Use explicit typed config.

Suggested shape:
- `env.example`
- `settings/base.py`
- `settings/local.py`
- `settings/test.py`
- `settings/prod.py`

Rules:
- no silent fallback to production-like values;
- secrets must not be committed;
- feature flags must be named and documented;
- experimental flags should map to tasks or decisions where possible.

## 16. Logging and observability conventions

Every major action should generate structured logs with stable fields.

Minimum common fields:
- timestamp
- request_id
- task_id
- object_id
- module
- action
- outcome
- model_id when relevant
- policy_id when relevant

Key events to capture:
- source ingestion
- entity merge
- claim update
- task creation
- experiment start/end
- decision promotion/freeze/retire
- harness run summary
- model selection record

## 17. Engineering review rituals

Recommended rhythms:
- daily: active task and blocker review;
- weekly: harness deltas, schema changes, module drift review;
- bi-weekly: paradigm pack and thinking-model change review;
- monthly: architecture simplification and service-boundary review.

No major boundary change should happen without a short ADR in `docs/decisions/`.

## 18. Branching and version control conventions

Suggested approach:
- short-lived feature branches;
- PRs scoped to one concern;
- schema changes reviewed with migration notes;
- docs updated in the same PR as behavior changes.

Commit style should be plain and scoped:
- `feat(tasks): add experiment acceptance policy`
- `docs(governance): define freeze and retire states`
- `refactor(knowledge): split relation merge service`

## 19. Anti-patterns to avoid

Codex and human developers should avoid:
- creating many services before module seams are stable;
- adding alternative schemas instead of evolving canonical ones;
- burying lifecycle transitions in UI code;
- mixing evaluation artifacts with canonical business state;
- letting notebooks become production logic;
- creating giant `utils.py` or `helpers.py` buckets;
- treating English Markdown specs as optional.

## 20. What Codex should build first

First build wave:
1. repo skeleton;
2. canonical schema package;
3. API app shell;
4. worker app shell;
5. task/experiment/decision core objects;
6. source/observation objects;
7. harness runner skeleton;
8. config/logging foundation;
9. docs and ADR template.

Second build wave:
1. knowledge object services;
2. thinking model registry;
3. governance policies;
4. bootstrap data loaders;
5. first story templates.

## 21. Migration path

This repository shape is optimized for the A and B stages. It should not be mistaken for the final topology.

Expected evolution:
- Stage A: modular monolith in one deployable unit.
- Stage B: stronger internal package boundaries and async execution.
- Stage C: selective runtime separation for worker-heavy or evaluation-heavy paths.
- Stage D: portfolio-style governance and more independent runtime surfaces where justified.

The repository should preserve this path without forcing it too early.

## 22. Final recommendation

Treat repository structure as a governance tool, not just a folder tree. If the repo shape is disciplined, Codex can generate code safely. If the repo shape is vague, every subsequent document loses power.

The first implementation should therefore prioritize:
- stable package seams;
- canonical schemas;
- thin app entry points;
- explicit workflow objects;
- harness-linked development;
- English Markdown as the durable specification layer.
