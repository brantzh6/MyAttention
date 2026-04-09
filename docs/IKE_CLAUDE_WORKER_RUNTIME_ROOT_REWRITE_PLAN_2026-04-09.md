# IKE Claude Worker Runtime Root Rewrite Plan

Date: 2026-04-09
Status: proposed

## Current Problem

Claude worker currently stores run artifacts inside the product tree:

- `D:\code\MyAttention\.runtime\claude-worker`

This mixes:

- product repository state
- delegated run artifacts
- large operational logs
- long-lived controller evidence

inside one root.

## Target State

Move Claude worker runtime artifacts to an external runtime root, for example:

- `D:\code\_ike-runtime\claude-worker`

## What Should Move

- worker run directories
- durable `meta.json`
- `events.ndjson`
- `final.json`
- `summary.md`
- `patch.diff`

## What Should Stay In The Project Repo

Only project-owned code and durable docs:

- `services/api/claude_worker/`
- tests
- docs that describe the worker lane

The worker implementation stays in the repo.
The worker run store moves out.

## Migration Sequence

1. create external Claude runtime root
2. copy current run-store contents
3. update worker configuration/default paths
4. run one toy proof
5. run one bounded project proof
6. confirm result paths are now external

## Acceptance Criteria

- Claude worker still runs coding/review tasks
- durable artifacts are produced under external runtime root
- no new run artifacts are written under the canonical repo root by default

## Non-Goals

- do not turn Claude worker into controller
- do not redesign task/memory truth
- do not broaden the worker surface during path migration
