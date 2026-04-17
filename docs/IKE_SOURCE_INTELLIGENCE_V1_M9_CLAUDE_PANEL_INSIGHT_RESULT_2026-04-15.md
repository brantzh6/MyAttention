# IKE Source Intelligence V1 - M9 Claude Panel Insight Result

Date: 2026-04-15
Status: implementation completed and controller-reviewed
Recommendation: accept_with_changes

## Scope

This packet improves the inspect-only multi-model judgment lane so it is no
longer limited to count aggregation.

Landing area:

- [feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## What Changed

The panel inspect route now returns structured insight, not only aggregate
counts.

Route:

- `POST /api/sources/discover/judge/panel/inspect`

Bounded additions:

1. `panel_insights.consensus_worthy`
   - high-confidence shared verdicts worth acting on carefully
2. `panel_insights.disagreement_worthy`
   - disagreement objects classified by divergence type
   - `polarized`
   - `uncertainty-driven`
   - `conviction-gap`
   - `threshold-gap`
3. `panel_insights.follow_up_hints`
   - bounded next-step hints derived from the disagreement pattern
4. provider-aware default model resolution
   - qwen lane defaults to effective qwen default model
   - anthropic lane defaults to `claude-3-5-sonnet-20241022`
   - openai lane defaults to `gpt-4o`
   - ollama lane defaults to `qwen2:7b`

## Why This Is Valuable

This is the first bounded panel slice where disagreement is treated as signal,
not garbage.

The route still does not make canonical decisions, but it now exposes:

- where models converge strongly
- where they split in useful ways
- which splits imply ambiguity
- which splits imply opportunity or a boundary calibration problem

That makes the panel usable for AI-assisted review and controller diagnosis,
instead of only for shallow voting telemetry.

## Claude Delegation Outcome

The implementation was delegated to Claude Code and then controller-reviewed.

Practical result:

- ACP Claude exec produced the useful code shape
- controller review accepted the core direction
- controller added one narrow corrective patch:
  - provider-aware default model resolution for the secondary lane

## Validation

Commands run:

```bash
python -m unittest tests.test_feeds_source_discovery_route tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_source_discovery_contract tests.test_attention_policy_foundation
python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py
```

Observed result:

- `78 tests OK`
- compile passed

## Truth Boundary

This packet does not:

- persist panel results
- merge panel output into canonical truth
- create a voting workflow
- auto-follow or auto-subscribe
- replace controller review

It remains an inspect-only advisory lane.

## Remaining Gaps

1. The route is still a two-lane panel, not a full multi-expert framework.
2. There is no merged controller decision object yet.
3. The current Claude worker detached runtime path still has a real-run gap;
   this packet was completed through the ACP Claude exec lane instead.
4. Methodology-driven dynamic judgment frameworks are still future work.

## Controller Judgment

Code-level judgment:

- `accept`

Project-level judgment:

- `accept_with_changes`

Reason for `with_changes`:

- the product slice is good and bounded
- but Claude Code chain validation is only partially complete because ACP exec
  succeeded while the detached Claude worker lane remains unreliable in this
  scenario
