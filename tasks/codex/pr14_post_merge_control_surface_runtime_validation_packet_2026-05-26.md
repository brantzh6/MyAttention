# Runtime Operator Packet - PR14 Post-Merge /control Validation

Task ID: `pr14_post_merge_control_surface_runtime_validation_2026_05_26`
Owner lane: `ike-operator`
Requested by: `codex-controller`
Status: pending PR14 merge

## Goal

After PR14 is merged into `main`, validate that the local runtime serves the
merged `/control` project surface and that the page reflects current project
truth from `ops/state/current_state.json`.

## Preconditions

- PR14 is merged into `main`.
- Controller has pulled or otherwise made merged main available locally.
- Runtime operations are authorized for `ike-operator` only.

## Allowed Actions

- Inspect current API/web/postgres/redis process state.
- Rebuild or restart the web service only if needed to serve merged main.
- Run read-only HTTP/browser checks against local runtime.
- Write one runtime result artifact under `tasks/codex/`.

## Forbidden Actions

- Do not edit source code.
- Do not stage, commit, push, merge, or resolve GitHub threads.
- Do not change project priorities.
- Do not mark PR14 accepted; controller owns absorption.

## Required Checks

1. Confirm code truth:
   - local main includes PR14 merge commit
   - `/control` route exists in the served build source
2. Confirm reachability:
   - `http://127.0.0.1:3002/control` returns 200
   - `http://127.0.0.1:3002/chat` returns 200
   - `http://127.0.0.1:3002/evolution` returns 200
   - `http://127.0.0.1:8000/health` returns 200
3. Confirm product surface:
   - `/control` displays current mainline priorities
   - `/control` shows PR20 runtime-ready state
   - `/control` shows PR14/control-surface state after merge
   - `/control` shows PM/automation health from `ops/pm-runs/latest.json` when available
   - `/control` does not claim runtime/product readiness beyond accepted state
4. Confirm browser quality:
   - no blocking render error
   - no obvious mojibake in visible controller/project text
   - no major layout overlap at desktop width

## Validation Output

Write:

`tasks/codex/pr14_post_merge_control_surface_runtime_validation_result_2026-05-26.md`

Include:

- summary
- runtime commands run
- service states before and after any restart
- URLs checked and status codes
- browser observations
- screenshots path if captured
- known risks
- recommendation: `accept`, `accept_with_changes`, or `reject`

## Stop Condition

Stop after writing the result artifact. Escalate to controller if `/control`
cannot be served, if rebuild/restart fails, or if the page contradicts
`ops/state/current_state.json`.
