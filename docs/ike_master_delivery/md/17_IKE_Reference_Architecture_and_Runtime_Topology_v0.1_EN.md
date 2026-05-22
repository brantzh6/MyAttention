# IKE Reference Architecture and Runtime Topology v0.1

## 1. Purpose

This document defines the recommended reference architecture and runtime topology for evolving MyAttention into IKE without discarding the current FastAPI + Next.js + PostgreSQL + Redis + Qdrant stack. It is intended for Codex implementation planning, not marketing.

## 2. Baseline runtime assumptions

The current repository already documents and organizes around these baseline assumptions:
- FastAPI backend in `services/api`;
- Next.js frontend in `services/web`;
- PostgreSQL as the primary structured store;
- Redis as cache and queue/state substrate;
- Qdrant as vector index;
- object storage abstraction being introduced for raw and large artifacts.

The reference architecture keeps these choices and layers IKE capabilities on top.

## 3. Recommended v0 runtime topology

```text
Browser / Admin UI
        |
        v
 Next.js console (services/web)
        |
        v
 FastAPI app (services/api)
   |        |         |         |
   |        |         |         +--> Notification adapters
   |        |         +------------> LLM / embedding providers
   |        +----------------------> Redis (queue, cache, locks)
   +-------------------------------> PostgreSQL (objects, tasks, decisions)
                 |
                 +---------------> Qdrant (semantic retrieval)
                 |
                 +---------------> Object store (raw artifacts, reports)

 Background worker(s)
   - ingestion jobs
   - enrichment jobs
   - harness runs
   - experiment runs
   - governance review jobs
```

This should begin as a modular monolith with separate process roles, not as a distributed microservice mesh.

## 4. Logical architecture layers

### 4.1 Product and control layer

User-facing and operator-facing surfaces:
- research workspace;
- entity and paradigm views;
- governance review console;
- harness reports;
- system and health views.

Initial runtime mapping:
- `services/web` for human-facing UI;
- selected FastAPI routers for machine-facing control APIs.

### 4.2 Application interface layer

The control API surface should remain router-based at first, organized around these families:
- system and settings;
- information flows;
- knowledge and retrieval;
- conversations and memories;
- evolution and governance;
- testing and harness.

### 4.3 Domain services layer

This is where most new work should concentrate. Domain services should sit behind routers and orchestrators.

Recommended service groups:
- Information services
- Knowledge services
- Thinking model services
- Governance services
- Workflow services
- Harness services
- Memory projection services

### 4.4 Artifact and memory layer

All durable outputs should be represented as first-class objects, not scattered files. This layer spans:
- relational objects and state in PostgreSQL;
- embeddings and vector search in Qdrant;
- raw inputs and generated files in object storage;
- fast transient state in Redis.

### 4.5 Execution layer

Background execution should be isolated from HTTP request lifecycles. At v0 this can still live inside the same repository and even the same codebase, but separate entry points should exist for:
- job worker;
- scheduler / tick runner;
- harness runner;
- offline rebuild commands.

## 5. Brain-to-runtime mapping

### 5.1 Information Brain

Runtime responsibilities:
- source registration;
- watchlists;
- crawlers and feed collectors;
- raw ingest;
- normalization;
- source quality scoring;
- signal extraction.

Recommended initial mapping:
- current `feeds/` module;
- current `routers/feeds.py`;
- Redis-backed queueing;
- PostgreSQL-backed normalized item store;
- object store for raw captures.

### 5.2 Knowledge Brain

Runtime responsibilities:
- entity extraction;
- relation creation;
- claim management;
- field model updates;
- retrieval and grounding;
- memory promotion.

Recommended initial mapping:
- current `knowledge/` and `rag/` modules;
- `routers/rag.py`, chat-related routers, and future knowledge routers;
- PostgreSQL for structured objects;
- Qdrant for retrieval;
- optional offline rebuild workers.

### 5.3 Evolution Brain

Runtime responsibilities:
- concept emergence tracking;
- self-relevance analysis;
- direction finding;
- task generation;
- experiment planning;
- adoption decisions;
- governance review.

Recommended initial mapping:
- current `routers/evolution.py` and `routers/testing.py` as control seeds;
- future `workflow/`, `governance/`, and `thinking_models/` services;
- worker-based execution for experiment and review jobs.

## 6. Shared substrate topology

### PostgreSQL

Use as the canonical state store for:
- entities;
- relations;
- claims;
- tasks;
- experiments;
- decisions;
- governance reviews;
- source and observation metadata.

### Redis

Use for:
- job queueing;
- temporary workflow state;
- dedupe locks;
- rate limit state;
- cacheable projections.

Do not allow Redis to become the only source of truth for durable workflow state.

### Qdrant

Use for:
- document chunk embeddings;
- retrieval indexes;
- optional semantic lookup for claims, observations, and paradigm notes.

### Object storage

Use for:
- raw captures;
- HTML snapshots;
- imported documents;
- harness reports;
- experiment artifacts;
- generated exports.

## 7. Process topology recommendation

### v0 process set

Recommended first process roles:
- `api`: FastAPI server
- `web`: Next.js dev/prod server
- `worker`: background worker loop
- `scheduler`: periodic tick runner

This can still run under docker compose and local scripts.

### v1 optional expansion

Add only when required:
- `harness-worker`
- `offline-rebuild-worker`
- `governance-review-worker`
- `console-admin` if the UI becomes large enough to separate concerns

## 8. Runtime flows that matter most

### Flow 1 - Information ingest
1. register or update source;
2. enqueue fetch;
3. persist raw artifact;
4. normalize to observations/items;
5. optionally enrich;
6. emit downstream workflow events.

### Flow 2 - Knowledge update
1. select new or changed artifacts;
2. extract entities, relations, and claims;
3. write structured objects;
4. update retrieval index;
5. publish knowledge update records.

### Flow 3 - Evolution trigger
1. detect concept or anomaly signal;
2. run self-relevance evaluation;
3. generate or update task;
4. design experiment if needed;
5. record decision or governance review requirement.

### Flow 4 - Harness and governance
1. run targeted harness suite;
2. produce evaluation artifacts;
3. attach results to experiments and reviews;
4. update model and decision policies.

## 9. Anti-patterns to avoid

Do not let the runtime evolve into these shapes:
- HTTP routers directly owning core business logic;
- Qdrant used as a substitute for durable structured state;
- Redis holding long-lived workflow truth;
- one giant worker with all job classes mixed together and no artifact discipline;
- prompts acting as the only model of domain logic;
- immediate microservice extraction before modular contracts stabilize.

## 10. Codex implementation priorities

Codex should implement runtime topology in this order:
1. stabilize one API process and one worker process;
2. standardize DB, Redis, Qdrant, and object-store adapters;
3. introduce event-like internal workflow contracts;
4. isolate harness execution from request handling;
5. add governance review jobs only after task and experiment state is stable.

## 11. Definition of success

The reference architecture is successful when the system can:
- ingest information durably;
- promote it into structured knowledge;
- trigger tasks and experiments from new signals;
- evaluate itself through harness runs;
- do all of the above on the current runtime stack without a rewrite.

That is the correct architectural bridge from MyAttention to IKE.
