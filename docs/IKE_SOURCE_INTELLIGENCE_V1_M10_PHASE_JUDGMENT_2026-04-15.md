# IKE Source Intelligence V1 - M10 Phase Judgment

Date: 2026-04-15
Phase: `M10 Judgment Substrate Extraction`
Status: `activated`

## Why This Slice

`M7` / `M8` / `M9` proved that AI-assisted judgment and multi-lane disagreement
can participate in `Source Intelligence`.

The next bounded step should not add more panel semantics.
It should reduce route-local accumulation and move the judgment kernel toward a
future reusable capability.

## Scope

Create one internal extraction step that:

1. moves generic AI judgment helper logic out of `routers/feeds.py`
2. keeps current route contracts unchanged
3. keeps all current truth boundaries unchanged
4. preserves inspect-only behavior
5. makes future reuse easier for non-source routes

## Out Of Scope

This slice does not attempt:

1. new API routes
2. persistence or workflow
3. merged panel verdicts
4. generic controller automation
5. broad architecture redesign
