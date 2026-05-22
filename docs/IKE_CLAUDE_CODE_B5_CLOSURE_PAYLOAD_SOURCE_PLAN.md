# IKE Claude Code B5 Closure Payload Source Plan

## Purpose

After the closure adapter was corrected, the next question is:

- what component should produce the explicit procedural-memory closure payload?

The adapter is now truthful.
It no longer invents:

- `lesson`
- `why_it_mattered`
- `how_to_apply`
- `confidence`

So these fields must come from an explicit upstream step.

## Main Principle

Do not hide judgment inside the adapter.

If a procedural memory is worth saving, the system should be able to point to
an explicit producer of:

- the lesson
- why it mattered
- how to apply it
- confidence

## Candidate Producers

### 1. Controller-reviewed study closure

Best first candidate.

Why:

- existing benchmark study closures already contain bounded findings
- explicit review exists
- low risk of synthetic memory spam

### 2. Structured decision handoff

Possible second candidate.

Why:

- decisions often contain durable rationale
- but still risk over-capturing intermediate judgments

### 3. Generic task closure automation

Not first.

Why:

- too easy to create noisy memory
- closure semantics are not mature enough yet

## First Recommended Source

Start with:

- reviewed benchmark `study_closure`

That means the first real producer should be:

- a bounded payload builder from reviewed study result / closure artifacts

not:

- a generic runtime-wide closure generator

## Success Condition

`B5` succeeds if IKE can identify one truthful upstream producer for explicit
procedural-memory payloads without falling back to heuristic inference.
