# IKE Source Intelligence V1 - M8 Panel Inspect Review Absorption

Date: 2026-04-15
Status: selective absorption completed

## Input Reviews

Absorbed:

- `claude`
- `chatgpt`
- `gemini`

## Accepted Points

1. `M8` should be described as a bounded dual-lane panel inspect surface, not a
   strong proof of epistemic independence.
2. `panel_summary` should be understood as verdict-overlap shape, not a broad
   merged panel assessment.
3. Stable-case proof should exist explicitly.
4. One-lane parse-failure / empty-lane behavior should be tested explicitly.
5. Panel usefulness must not be overclaimed into workflow, routing, or
   controller automation.

## Code Changes Applied

Two focused improvements were absorbed into the implementation:

1. `panel_signal` honesty fix
   - previously, `panel_signal` could appear as `stable` whenever there were no
     disagreed shared keys, even if one lane returned no judgments
   - now `stable` is only emitted when:
     - there is at least one shared candidate
     - there are no disagreed candidates
     - there are no asymmetric `primary_only` / `secondary_only` leftovers
   - otherwise the result is `mixed`

2. Focused validation additions
   - stable route proof
   - one-lane invalid JSON fallback proof

## Validation

```bash
python -m unittest tests.test_feeds_source_discovery_route tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_source_discovery_contract tests.test_attention_policy_foundation
python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py
```

Observed:

- `80 tests OK`
- compile passed

## Controller Judgment

Code-level:

- `accept`

Project-level:

- `accept_with_changes`

The `with_changes` items from this review are now closed.

## Stop Rule

`M8` remains:

- inspect-only
- non-persistent
- non-canonical
- non-workflow

It should not expand into voting, escalation, or controller auto-routing from
panel shape.
