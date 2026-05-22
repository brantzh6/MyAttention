# IKE Runtime v0 R2-H Plan

## Goal

Normalize the canonical runtime API service so controller validation can rely on
the main service path instead of bounded alternate-port proof.

## Current Baseline

The canonical launch path is now explicit:

- repo interpreter:
  - `D:\\code\\MyAttention\\.venv\\Scripts\\python.exe`
- service entry:
  - `D:\\code\\MyAttention\\services\\api\\run_service.py`

## Narrow Execution Order

1. `R2-H1`
- expose canonical launch command in preflight and settings surface

2. `R2-H2`
- attempt one controller-bounded canonical restart using the explicit canonical
  command
- gather live preflight evidence immediately after restart

3. `R2-H3`
- if ownership still drifts, record the smallest truthful diagnosis of where
  the drift occurs:
  - launcher
  - interpreter
  - parent/child chain
  - served-code freshness

## Non-Goals

- no supervisor rewrite
- no daemon framework
- no broad deployment system
- no runtime truth redesign
