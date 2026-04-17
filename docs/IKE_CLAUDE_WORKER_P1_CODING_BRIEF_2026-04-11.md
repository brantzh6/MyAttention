# IKE Claude Worker P1 Coding Brief

Date: 2026-04-11
Status: controller coding brief

## Task ID

- `claude-worker-p1`

## Goal

Make the current Claude worker real-run path more cross-platform and more
durably truthful.

## Problem

The first real Claude worker coding run exposed two concrete issues:

- the multi-line task packet was not delivered intact to the Claude session
- the run stayed durably `running` even after the child was gone

## Intended Scope

- harden prompt delivery in `services/api/claude_worker/worker.py`
- harden durable finalize behavior for detached real runs
- add the smallest focused tests needed to prove the new behavior

## Constraints

- prefer cross-platform Python mechanisms
- do not make PowerShell or Windows `.cmd` semantics the main contract
- no daemon/job supervisor
- no broad architecture rewrite
- no fake-process-only proof for the main acceptance claim

## Preferred Direction

- prefer stdin or an equivalent Python-controlled input path for long prompts
- keep Windows-specific behavior in the smallest possible branch
- make `fetch` / `wait` truthfully converge once the child has already exited

## Required Output

1. `summary`
2. `files_changed`
3. `validation_run`
4. `known_risks`
5. `recommendation`
