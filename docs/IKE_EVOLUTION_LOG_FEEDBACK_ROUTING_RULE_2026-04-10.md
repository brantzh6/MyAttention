# IKE Evolution Log Feedback Routing Rule

Date: 2026-04-10
Status: active controller rule

## Purpose

Define how runtime/application logs enter the evolution loop as feedback without
wasting high-cost reasoning lanes on repetitive operational noise.

Logs are a feedback source.
They are not automatically a controller task.

## Core Judgment

Log signals should enter the system in three layers:

1. low-cost monitoring and triage
2. bounded technical diagnosis
3. controller escalation only for high-risk or mainline-relevant cases

This keeps feedback coverage high while controlling token burn.

## Why This Rule Exists

Current project reality:

- logs contain real feedback about:
  - infrastructure degradation
  - source-collection health
  - cache failures
  - runtime/live-service drift
  - model/provider instability
- but many log events are:
  - repetitive
  - low-severity
  - non-semantic
  - operational rather than architectural

If all log feedback goes directly to the highest-cost reasoning lane, the
system becomes expensive and noisy.

## Feedback Classification

### Class A: acceleration / optional dependency degradation

Examples:

- Redis cache read/write failure
- cache miss amplification
- non-canonical notification delivery retry
- temporary search/provider timeout with fallback available

Meaning:

- performance or convenience degraded
- canonical truth path is still intact

Default handling:

- low-cost monitoring lane
- summarize, deduplicate, and trend
- do not escalate immediately

### Class B: operational health degradation

Examples:

- repeated Redis unavailability across many sources
- feed collection failures accumulating
- notification channels failing persistently
- service startup latency spikes
- repeated provider failures affecting normal work

Meaning:

- operational quality is degraded enough to affect ongoing delivery

Default handling:

- low-cost lane triages first
- bounded diagnosis lane may inspect code/config context
- escalate if persistent or cross-cutting

### Class C: canonical-truth or mainline risk

Examples:

- Postgres canonical truth inconsistency
- runtime task/event/lease truth mismatch
- canonical-service preflight drift
- live route/code-tree mismatch
- controller-visible semantics overstating reality

Meaning:

- possible runtime/mainline risk
- possible architecture or truth-boundary issue

Default handling:

- escalate to controller
- eligible for high-reasoning review and narrow coding packet

## Lane Routing Policy

### Lane 1: low-cost monitoring lane

Primary job:

- watch logs
- deduplicate
- cluster repeated failures
- classify severity
- decide whether to escalate

Recommended models:

- `kimi-k2.5`
- `qwen3.6-plus`

Recommended task types:

- log anomaly clustering
- repeated-error counting
- source-level degradation summaries
- infrastructure health snapshots
- "ignore vs watch vs escalate" judgment

Expected output:

1. error class
2. affected component
3. frequency / recurrence
4. likely impact
5. escalation recommendation

### Lane 2: bounded diagnosis lane

Primary job:

- inspect local code/config around an escalated log cluster
- determine whether the issue is:
  - environment
  - config
  - code
  - external dependency

Recommended models:

- `qwen3.6-plus`
- `glm-5`

Expected output:

1. probable cause
2. evidence path
3. minimal next action
4. whether controller review is needed

### Lane 3: controller lane

Primary job:

- absorb only the high-risk subset
- decide whether to open a mainline packet or an infra-maintenance packet

Use controller escalation only when:

- canonical truth may be affected
- controller-visible semantics may be false
- current mainline progress may be invalidated
- repeated operational degradation is now project-level

## Specific Rule For Redis Errors

Example signal:

- `redis read failed for cs_com: Error 22 connecting to localhost:6379`

Current classification:

- `Class A` by default

Why:

- Redis in this project is an acceleration layer, not canonical truth
- the error indicates local cache connectivity failure
- by itself, this does not imply Postgres truth loss or runtime semantic drift

Default routing:

- low-cost monitoring lane

Escalate only if one of these becomes true:

1. the failure is persistent across many sources
2. collection throughput or latency visibly degrades
3. recovery logic is broken or noisy enough to pollute operations
4. Redis-dependent runtime acceleration behavior becomes misleading at the
   controller-visible layer

## Evolution-System Meaning

Logs are part of evolution feedback, but different log classes should drive
different evolution actions.

### What low-cost monitoring should feed back

- recurring operational weak points
- noisy subsystems
- persistent external dependency failure patterns
- degradation trends over time

### What should become evolution tasks

- repeated and non-trivial failure clusters
- issues with trend persistence
- issues that change task/source-plan quality
- issues that indicate the current rules are insufficient

### What should not automatically become evolution tasks

- isolated one-off cache errors
- transient provider/network noise with successful fallback
- known optional dependency unavailability with no user-visible impact

## Recommended Operational Policy

1. Treat logs as a feedback substrate.
2. Route first-pass monitoring to low-cost fast models.
3. Escalate only clustered or high-risk findings.
4. Preserve the distinction between:
   - acceleration degradation
   - operational degradation
   - canonical-truth risk
5. Never let repetitive low-severity logs dominate the controller lane.

## Controller Judgment

This rule should be treated as active.

Logs are now explicitly part of evolution feedback, but default ownership for
log triage belongs to the low-cost monitoring lane, not the controller.
