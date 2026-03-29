# IKE API Transition Principles

## Purpose

This document records the controller decision and reusable research lessons from the first IKE v0 API-shape debate.

It exists to prevent a common migration failure:

- exposing an interface that implies capabilities the runtime does not actually have yet

This is a transition document, not the final API specification.

## Current Decision

For IKE v0:

- do **not** expose standard `GET /{type}/{id}` as if all IKE objects are durable canonical resources
- do expose a small transitional API surface focused on:
  - create
  - generate
  - extract
  - derive
  - preview
  - inspect

Reason:

- the current system has stable object generation contracts
- the current system does **not** yet have a stable canonical object store / retrieval path
- therefore a standard `GET by id` surface would create a false affordance

## Research Lessons To Reuse

### 1. Interface must reflect current capability, not target ambition

When the backend can generate objects but cannot yet durably retrieve them,
the API must describe generation and inspection, not stable storage.

Bad pattern:

- expose a stable-looking resource interface too early

Good pattern:

- expose the smallest honest interface that matches current runtime truth

### 2. Avoid false affordances

A route such as:

- `GET /ike/v0/entities/{id}`

implies:

- stable identity
- durable retrieval
- meaningful 404 semantics
- client-side caching safety

If those guarantees are not yet real, the route is dishonest.

That dishonesty is especially dangerous for coding agents and automation,
because they will treat the route as contractually stable.

### 3. Prefer transitional verbs over premature resource promises

At this stage, these are safer patterns:

- `POST /v0/entities/extract`
- `POST /v0/claims/derive`
- `POST /v0/research-tasks/generate`
- `POST /v0/.../preview`
- `GET /v0/.../inspect/...`

These names signal:

- operation
- transformation
- inspection

not:

- durable canonical storage

### 4. Transitional APIs must still have a clear evolution path

The solution is not to create arbitrary one-off endpoints forever.

The transition path must stay explicit:

1. v0 transitional operation API
2. intermediate object access abstraction
3. stable canonical object store
4. standard object retrieval API

### 5. State honesty matters more than REST purity in v0

For v0, architecture honesty is more important than REST purity.

It is acceptable for the first API to be less standard if it:

- matches current capability
- avoids fake permanence
- minimizes later rework

## Transitional Response Contract

The first API should not return bare objects as if they are durable by default.

Instead, it should return an object together with explicit lifecycle metadata.

Recommended shape:

```json
{
  "ref": {
    "id": "ike:entity:...",
    "kind": "entity",
    "id_scope": "provisional",
    "stability": "experimental",
    "permalink": null
  },
  "data": {
    "...": "..."
  }
}
```

Minimum semantics:

- `id_scope`
  - `session`
  - `provisional`
  - `stable`
- `stability`
  - `experimental`
  - `provisional`
  - `stable`

This allows later migration without changing the overall client envelope shape.

## Minimum v0 API Direction

The first IKE v0 API packet should prefer:

- one or two bounded operation endpoints
- one inspect endpoint for session/provisional artifacts
- explicit experimental markers in response metadata

It should avoid:

- full CRUD
- collection/list semantics
- canonical retrieval guarantees
- persistence claims beyond what the runtime can prove

## Migration Path

### Stage A. Transitional operation API

Examples:

- `POST /v0/entities/extract`
- `POST /v0/claims/derive`
- `POST /v0/research-tasks/generate`
- `GET /v0/inspect/{scope}/{id}`

Guarantees:

- object generation works
- inspectability works
- durability is not promised

### Stage B. Object access abstraction

Introduce a backend object access layer that can resolve:

- transient objects
- session-scoped objects
- future persisted objects

This stage is primarily an internal seam.

### Stage C. Canonical store and stable retrieval

Only after:

- identity rules are stable
- storage semantics are stable
- reconstruction semantics are stable

should the system introduce:

- `GET /v1/{type}/{id}`

## Readiness Signals For Standard GET By ID

Do not promote to stable object retrieval until all of the following are true:

1. Referential integrity:
   - the same object ID reliably resolves to the same object
2. Identity policy:
   - duplicate submissions do not create arbitrary duplicate identities
3. Reconstruction:
   - the system can deterministically rebuild object identity from trusted substrate
4. Error semantics:
   - `404`, `not ready`, and `not persisted` are meaningfully distinguishable

## Controller Rule

If future packet proposals attempt to expose durable-looking retrieval before the runtime can support it,
that must be treated as a semantic drift and corrected immediately.
