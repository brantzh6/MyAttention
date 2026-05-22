# IKE Source Intelligence V1 - M10 Judgment Substrate Result

Date: 2026-04-15
Phase: `M10 Judgment Substrate Extraction`
Status: `materially_landed`
Recommendation: `accept_with_changes`

## Scope

Extract the generic AI judgment / panel-insight kernel out of
`routers/feeds.py` into a more reusable internal module while keeping existing
route contracts unchanged.

## Landing Area

- [feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [ai_judgment.py](/D:/code/MyAttention/services/api/feeds/ai_judgment.py)
- [test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## What Landed

A new internal module now exists:

- `services/api/feeds/ai_judgment.py`

It now owns the generic substrate parts:

1. provider-aware default model resolution
2. JSON parsing with fence stripping and malformed fallback
3. normalization of raw AI judgment payloads
4. verdict-overlap comparison
5. disagreement / consensus insight derivation
6. shared judgment / panel insight models used by the route layer

`feeds.py` now imports and uses this substrate.

The route contract did not change.

## Controller Review Of Claude Output

Claude Code successfully created the new internal module and moved most of the
generic logic in the right direction.

But the first landed patch was incomplete:

- the router still called old private helper names in a few places
- this caused runtime `NameError` failures in focused tests

Controller then applied a narrow corrective patch:

1. switch route call-sites to imported substrate functions
2. turn remaining local `_compare_*` / `_derive_*` functions into thin wrappers
   over the substrate so existing tests and compatibility names still work

So this is a real delegated success, but not a zero-touch acceptance.

## Validation

```bash
python -m unittest tests.test_feeds_source_discovery_route tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_source_discovery_contract tests.test_attention_policy_foundation
python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\feeds\ai_judgment.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py
```

Observed:

- `80 tests OK`
- compile passed

## Why This Matters

This is the first real step from project-private route logic toward a reusable
internal judgment capability shape.

It does not yet make the capability fully generic, but it moves the core
judgment machinery behind a dedicated internal module instead of leaving it as
ad hoc route-local code.

The most accurate claim is:

- first reusable internal judgment substrate step

## Truth Boundary

This packet does not:

- add persistence
- create workflow automation
- merge panel output into canonical truth
- make a generic controller engine
- expose a new public API surface

It is a bounded internal extraction only.

## Controller Judgment

Code-level:

- `accept`

Project-level:

- `accept_with_changes`

Reason for `with_changes`:

- the substrate direction is correct
- the initial Claude patch was incomplete and required controller repair
- the extraction is still partial because public route models and route-specific
  request/response shapes remain in `feeds.py`
