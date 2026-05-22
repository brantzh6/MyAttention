# IKE Existing Codebase Assessment and Incremental Development Plan v0.1

## 1. Purpose

This document aligns the IKE design set with the current MyAttention repository so Codex can evolve the system from the existing codebase instead of rebuilding from zero. The goal is to identify what already exists, what can be reused directly, what needs refactoring, and what should be added in phases.

## 2. Current repository reality

The repository is already a monorepo with `services/api` and `services/web`, plus root-level operational tooling, docs, migrations, infrastructure, scripts, and a PNPM workspace. The backend is a FastAPI application; the frontend is a Next.js app. The documented runtime stack already assumes PostgreSQL, Redis, and Qdrant. The progress log also shows an explicit move toward layered feed persistence, object storage abstraction, and test-driven architecture before implementation.

The most important implication is that IKE should be implemented as a controlled transformation of MyAttention, not as a greenfield rewrite.

## 3. What already exists and should be preserved

### 3.1 Runtime and packaging skeleton

Keep and reuse:
- root monorepo shape;
- `services/api` as the initial application runtime;
- `services/web` as the initial user interface runtime;
- root `package.json` and PNPM workspace conventions;
- root operational scripts such as `manage.py` and watchdog-style runtime helpers.

### 3.2 Backend domain skeleton

The backend already exposes strong top-level module namespaces:
- `feeds/`
- `knowledge/`
- `rag/`
- `llm/`
- `memory/`
- `pipeline/`
- `storage/`
- `notifications/`
- `routers/`
- `tests/`

These should become the seed modules for Information Brain, Knowledge Brain, and the first operational parts of Evolution Brain.

### 3.3 Router surface already in place

The existing routers indicate the first real control surface of the product:
- chat
- conversations
- evolution
- feeds
- feishu
- memories
- models
- rag
- settings
- system
- testing

This is valuable because it means the future IKE API surface does not need to start from a blank OpenAPI plan.

### 3.4 Persistence and testing direction already started

The progress notes and current test files show that the project has already begun work on:
- raw ingest keys;
- feed persistence helpers;
- local object storage abstraction;
- collection health;
- task processor system health.

This is exactly the right place to attach the first codified IKE harness and governance loops.

## 4. Mapping the current codebase to IKE

| Existing module | Near-term IKE role | Notes |
|---|---|---|
| `feeds/` | Information Brain core | Keep as the canonical source ingestion and signal extraction area. |
| `knowledge/` | Knowledge Brain seed | Extend from current graph and search helpers into structured field models and claim layers. |
| `rag/` | Knowledge access runtime | Keep as retrieval engine; do not confuse it with the full Knowledge Brain. |
| `memory/` | Shared memory layer seed | Expand toward shared memory objects rather than chat-only memory. |
| `pipeline/` | Workflow orchestration seed | Good home for task and experiment flows before a separate worker app becomes necessary. |
| `routers/evolution.py` | Evolution Brain control seed | Use as the first evolution control API rather than replacing it. |
| `routers/testing.py` | Harness gateway seed | Grow into the first harness execution surface. |
| `storage/` + object store work | Shared artifact substrate | Keep and harden. |
| `tests/` | First regression harness seed | Expand from module tests into layered harness suites. |

## 5. What should not be rewritten

Codex should explicitly avoid rewriting these areas unless a concrete blocker is found:
- FastAPI app bootstrap and router registration;
- basic web app shell in `services/web`;
- current DB / Redis / Qdrant assumptions;
- root workspace and docker entry points;
- existing feed storage and health work already reflected in tests and progress logs.

The rule is simple: preserve running skeletons and refactor inward.

## 6. Gaps between current code and target IKE

### 6.1 Conceptual gaps

The current repository expresses the three-brain idea at the documentation level, but not yet as fully governed system contracts. Missing pieces include:
- first-class Thinking Model objects;
- first-class Paradigm objects;
- meta-reasoning governance state;
- explicit task / experiment / decision engine contracts;
- shared object envelope and memory promotion rules.

### 6.2 Architectural gaps

Missing or incomplete architecture for IKE includes:
- stable package boundaries inside the backend;
- a dedicated schemas layer shared across routers and workers;
- clear separation between API models and domain models;
- an event contract for background workflows;
- runtime topology for harness workers and governance review jobs.

### 6.3 Product gaps

The current system already supports chat, feeds, memory, and knowledge-base style features, but IKE still needs product surfaces for:
- paradigm library inspection;
- research card lifecycle;
- experiment review;
- decision promotion and adoption history;
- governance review dashboards.

## 7. Recommended incremental transformation plan

### Phase A - Stabilize and wrap what exists

Do first:
- freeze external folder names that are already good enough;
- add a shared schema package inside the backend repository;
- define canonical object envelopes without changing every implementation at once;
- add a thin compatibility layer so routers can return the new envelopes gradually.

### Phase B - Refactor core modules in place

Refactor next:
- move feed persistence and raw ingest work behind stable service interfaces;
- promote `knowledge/graph.py` and `rag/engine.py` into explicit domain services;
- introduce `workflow/` and `governance/` packages alongside existing modules;
- connect `routers/testing.py` to first-class harness runs and artifacts.

### Phase C - Add missing IKE-first capabilities

Then add:
- Thinking Model registry;
- Domain Paradigm registry;
- Task / Experiment / Decision engine;
- Governance review jobs;
- research card views and admin console surfaces.

### Phase D - Extract only when pressure is real

Only after the modular monolith is stable:
- extract worker runtime if async load grows;
- extract harness runner if evaluation cost dominates;
- extract console app if governance UX becomes large enough.

## 8. Codex implementation guidance

Codex should treat the repository as a living system and follow these rules:
- prefer additive package creation over destructive moves in the first pass;
- keep current routers alive while introducing new services behind them;
- write migration shims before deep refactors;
- preserve test coverage and extend it case by case;
- land schema-first contracts before large workflow changes.

A good first implementation sequence is:
1. create `schemas/`, `objects/`, `workflow/`, and `governance/` packages under `services/api` or `packages/` depending on the chosen repo step;
2. wrap current feed and knowledge modules with service interfaces;
3. update routers to consume service interfaces rather than local implementation logic;
4. add first harness artifacts and first governance review record types;
5. add UI views only after contracts stabilize.

## 9. Definition of success

This alignment document succeeds if Codex can start coding while respecting three constraints:
- no greenfield rewrite;
- no collapse back into router-centric logic;
- no loss of the current working skeleton.

The practical target is an upgraded MyAttention codebase that gradually becomes IKE through explicit contracts, shared objects, governance loops, and harness-backed evolution.
