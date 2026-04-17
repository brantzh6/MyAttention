# IKE Agent Harness P4 Network Policy Result

Date: 2026-04-10
Status: accept_with_changes

## Summary

The first metadata-only `network_policy` baseline is now landed across:

- Claude worker
- OpenClaw delegation wrappers
- qoder bundle / launch chain

This does not yet enforce runtime network blocking.
It records controller intent and makes later enforcement auditable.

## Landed Defaults

- `coding_high_reasoning`:
  - `network_policy = restricted`
- `review_high_reasoning`:
  - `network_policy = disabled`

Current rule:

- these values are policy intent
- they are not yet a full sandbox guarantee

## Landed Scope

### Claude worker

Now carries `network_policy` through:

- packet input
- persisted run reload
- `meta.json`
- `final.json`
- harness result projection
- CLI parsing

### OpenClaw wrappers

Now carry `network_policy` through:

- `openclaw_delegate.py`
- `run_file_delegation.py`
- wrapper prompt metadata
- wrapper JSON outputs

### qoder chain

Now carries `network_policy` through:

- `create_task_bundle.py`
- `create_review_bundle.py`
- `qoder_delegate.py`
- `run_task.py`

## Validation

- `python -m unittest services.api.tests.test_claude_worker`
- `python -m compileall D:\code\MyAttention\services\api\claude_worker D:\code\MyAttention\scripts\acpx\openclaw_delegate.py D:\code\MyAttention\scripts\acpx\run_file_delegation.py D:\code\MyAttention\scripts\qoder\create_task_bundle.py D:\code\MyAttention\scripts\qoder\create_review_bundle.py D:\code\MyAttention\scripts\qoder\qoder_delegate.py D:\code\MyAttention\scripts\qoder\run_task.py`
- `python D:\code\MyAttention\scripts\acpx\openclaw_delegate.py --help`
- `python D:\code\MyAttention\scripts\acpx\run_file_delegation.py --help`
- `python D:\code\MyAttention\scripts\qoder\create_task_bundle.py --help`
- `python D:\code\MyAttention\scripts\qoder\create_review_bundle.py --help`
- `python D:\code\MyAttention\scripts\qoder\qoder_delegate.py --help`
- `python D:\code\MyAttention\scripts\qoder\run_task.py --help`

## Controller Judgment

`network_policy` is now part of the durable metadata vocabulary.

Truthful boundary:

- this is metadata-first hardening only
- it should not yet be described as enforced network isolation

## Recommendation

`accept_with_changes`
