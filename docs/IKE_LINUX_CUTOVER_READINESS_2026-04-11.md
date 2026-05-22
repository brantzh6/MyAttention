# IKE Linux Cutover Readiness

Date: 2026-04-11
Status: controller preparation note

## Purpose

Prepare the repo for a later move from the current Windows development machine
to a Linux-first development and runtime environment.

## Why This Matters

Linux is the more likely long-term runtime environment.

If the current local development baseline keeps depending on Windows quoting,
`.cmd`, WMI, `taskkill`, or PowerShell behaviors, then the project will keep
passing local checks while remaining under-proven for its intended host class.

## Readiness Split

### Already favorable for Linux cutover

- runtime and harness logic is largely written in Python
- service templates already exist for Linux and macOS
- governance already separates dev / sandbox / staging / prod
- externalized agent/runtime roots reduce direct repo pollution

### Not yet ready enough

- Claude worker real-run path is not yet proven cross-platform
- some local validation still assumes Windows process behavior
- Windows-specific proof rules are currently mixed into active controller
  continuation material
- no Linux-first harness validation matrix is yet installed as a required gate

## Required Pre-Cutover Actions

### 1. Harness path hardening

- fix Claude worker prompt delivery so long prompts do not depend on Windows
  command-line behavior
- prove durable finalize on a real run
- keep owner/child lifecycle truth portable

### 2. Validation normalization

- define `unit -> component -> harness -> staging` acceptance layers
- require at least component + harness proof for agent/runtime claims
- stop treating mock-only or fake-process-only proof as enough

### 3. Config and binary resolution

- move binary discovery toward explicit config or Python-managed resolution
- avoid assuming `%APPDATA%\\npm` or `.cmd` as the primary contract

### 4. Linux-first test pack

- add one narrow Linux cutover packet for:
  - claude worker
  - OpenClaw/acpx wrapper resolution
  - runtime service preflight core behavior
  - config/runtime root path semantics

## Current Blocking Items

### Blocking item A

`claude_worker` real detached run proof is not yet reliable enough.

### Blocking item B

Current local Windows process-shape work is truthful for this machine, but it
must remain a local exception path rather than the general runtime baseline.

## Controller Recommendation

Do not treat Linux cutover as a later cleanup project.

Treat it as an active support track now:

- first neutralize the harness/runtime core
- then move the development environment
- then re-run the higher acceptance layers on Linux

## Recommendation

`accept_with_changes`

The project is directionally ready for Linux-first migration, but not yet
operationally ready without a narrow cross-platform hardening wave.
