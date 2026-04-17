# IKE Source Intelligence V1 M13 Plan - 2026-04-15

## Goal

Add a bounded `selective_absorption` advisory layer to existing panel
responses so controller-facing action suggestions become visible without
introducing workflow or persistence.

## Write Set

- `D:\code\MyAttention\services\api\feeds\ai_judgment.py`
- `D:\code\MyAttention\services\api\routers\feeds.py`
- `D:\code\MyAttention\services\api\tests\test_ai_judgment_substrate.py`
- `D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`

## Intended Behavior

For existing panel surfaces:

- discovery candidate panel inspect
- source-plan version-change panel inspect

return:

- `ready_to_follow`
- `ready_to_suppress`
- `needs_manual_review`
- `watch_candidates`
- bounded controller notes

## Stop Rule

`M13` stops at advisory derivation and surface exposure.

It must not:

- persist any absorption result
- mutate plans or versions
- claim controller acceptance
- introduce automatic promotion
