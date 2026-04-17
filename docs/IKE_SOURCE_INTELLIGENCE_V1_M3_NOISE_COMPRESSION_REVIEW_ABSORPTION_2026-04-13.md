# IKE Source Intelligence V1 - M3 Noise Compression Review Absorption

Date: 2026-04-13
Scope: `M3 Same-Source Generic-Domain Compression Heuristic`
Status: `selective_absorption_complete`

## Absorption Summary

This review wave is accepted selectively.

- `claude`: accepted
- `chatgpt`: accepted
- `gemini`: rejected

## Why `gemini` Was Rejected

The returned `gemini` review drifted back to `M2` loop-proof language and did
not actually review the current `M3` packet.

It should not be absorbed into the `M3` controller judgment.

## Accepted Corrections

### 1. Naming should stay narrow

`M3` should be described as:

- `same-source generic-domain compression heuristic`

not as broad source-noise handling or ranking improvement.

### 2. Add one key guardrail test

The implementation should explicitly prove that the generic `domain` is kept
when the same-source specific candidate exists but is not materially
competitive.

This test has now been added.

### 3. Stop rule must remain explicit

`M3` is a good stop point for this family.

The next slice should be:

1. one clearly distinct noise-compression family
2. or one bounded quality-improvement slice

It should not continue patching the same generic/specific family by default.

## Controller Judgment

- code-level: `accept`
- project/controller-level: `accept_with_changes`

## Closed Changes

The `with_changes` part is now closed:

1. terminology narrowed
2. guardrail test added
3. stop rule made explicit again
