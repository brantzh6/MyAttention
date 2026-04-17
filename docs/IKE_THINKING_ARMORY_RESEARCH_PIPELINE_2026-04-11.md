# IKE Thinking Armory Research Pipeline

Date: 2026-04-11
Status: controller baseline

## Purpose

Turn the methodology / thinking-tool study line into a repeatable research
pipeline instead of an open-ended reading task.

## Problem

The current PDF study line has:

- valid inputs
- valid study packets
- some delegated execution evidence

But it does not yet have a stable closure pattern from raw materials to
reviewed retained output.

## Required Research Stages

Every research batch should move through these stages:

1. `source_ready`
2. `extracted`
3. `batch_reviewed`
4. `synthesis_drafted`
5. `controller_reviewed`
6. `retained`
7. `runtime_candidate` or `archive_only`

## Stage Meaning

### 1. `source_ready`

Inputs exist and are stable:

- original files known
- manifest known
- scope fixed

### 2. `extracted`

Machine-readable extracted text exists:

- extracted files saved
- stable manifest written

### 3. `batch_reviewed`

One bounded batch returns a durable result:

- not just running
- not just queued
- not just discussed in chat

### 4. `synthesis_drafted`

Batch outputs are turned into one higher-level synthesis note.

### 5. `controller_reviewed`

The synthesis is reviewed for:

- signal quality
- overclaiming
- applicability to IKE

### 6. `retained`

The reviewed synthesis is archived into docs as durable retained knowledge.

### 7. `runtime_candidate` or `archive_only`

Final classification:

- `runtime_candidate`
  - may later influence IDE/runtime behavior
- `archive_only`
  - useful to keep, but not a runtime behavior candidate

## Output Types

Each batch should produce at most three durable outputs:

1. batch result note
2. synthesis note
3. candidate classification note

## Controller Rule

Do not treat "model read a lot of material" as progress.

Progress only counts when a durable batch or synthesis artifact exists.

## Current Meaning For The Active PDF Line

The methodology / thinking-armory line is currently between:

- `extracted`
- and incomplete `batch_reviewed`

So the next acceptable milestone is not "keep reading."

It is:

- one durable batch-reviewed artifact

## Recommended Next Packet

1. recover one small batch closure
2. write one batch result doc
3. write one synthesis doc over that batch
4. classify it as:
   - `runtime_candidate`
   - or `archive_only`
