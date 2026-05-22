# IKE Claude Worker Real Run Gap

Date: 2026-04-11
Status: controller gap note

## Purpose

Record the current real-run gap discovered while starting the first Claude
worker coding lane for `Source Intelligence V1 M1`.

## Run

- run_id:
  - `20260411T112415-babf2099`
- run_dir:
  - `D:\code\_agent-runtimes\claude-worker\runs\20260411T112415-babf2099`
- task_id:
  - `source-intelligence-v1-m1-coding-001`

## Observed Facts

- the run directory was created successfully
- `meta.json`, `events.ndjson`, `summary.md`, and `patch.diff` were written
- `events.ndjson` only contains the `started` event
- `final.json` was never written
- the projected result file was never written
- the recorded `child_pid` was no longer alive when later inspected

## Root-Cause Split

### Gap 1. Prompt delivery path is not currently trustworthy

Claude session logs show the real session only received:

- `Complete this task in one turn.`

It did not receive the intended long packet body containing:

- required files
- output path
- execution constraints
- JSON contract

This indicates the current Windows `claude.cmd` prompt delivery path is not
reliably transmitting the full multi-line prompt as intended.

### Gap 2. Detached finalize contract is not actually closed

The current CLI `start` flow writes durable startup artifacts and then exits.

When that owner process exits, no durable finisher remains to:

- collect the final child result
- write `final.json`
- write the harness result projection

So even if the child exits, the run can remain durably stuck at
`status = running`.

## What This Means

This is not only a one-off usage mistake.

It is also not sufficient to say the earlier worker package was simply wrong.

The more accurate controller judgment is:

- earlier worker hardening covered a narrower baseline
- this real run exercised a more realistic path
- that path exposed two gaps not yet closed:
  - real prompt delivery
  - durable detached finalization

## Truth Boundary

The Claude worker should currently be judged as:

- unit level:
  - materially covered
- fake-process hardening:
  - materially covered
- real-run harness closure:
  - not yet proven

## Required Next Packet

One narrow hardening packet should now target:

- cross-platform prompt delivery for real Claude runs
- durable real-run finalization after owner exit
- one truthful end-to-end harness proof:
  - `start -> real prompt delivery -> child exit -> final.json -> result projection`

## Recommendation

`accept_with_changes`

Reason:

- the worker remains useful as a bounded lane
- but it is not yet strong enough to claim real detached harness closure
