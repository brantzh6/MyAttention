# IKE Source Intelligence V1 - M7 AI Judgment Inspect Review Absorption

Date: 2026-04-15
Scope: `M7 AI-Assisted Candidate Judgment Inspect`
Status: `selective_absorption_complete`

## Absorption Summary

This review wave is accepted selectively.

- `claude`: accepted
- `gemini`: accepted
- `chatgpt`: accepted

## Accepted Corrections

### 1. JSON parse failure should not become a 500

`M7` now handles malformed model output more honestly.

- fenced JSON is stripped before parsing
- invalid JSON falls back to an empty advisory result
- notes now include `ai_judgment_parse_status`

This keeps the lane inspect-only and bounded while avoiding a misleading hard
failure for a common LLM-output defect.

### 2. Normalization transparency should be more inspect-honest

`M7` now records:

- `discarded_judgments=<n>`

This makes it visible when the model produced extra or out-of-scope judgments
that were dropped during normalization.

### 3. Summary must be explicitly weaker than the normalized decision set

The truth boundary now explicitly states:

- model summary is advisory condensation, not the canonical decision set

This prevents the free-form summary string from being misread as stronger than
the normalized structured judgments.

## Controller Judgment

- code-level: `accept`
- project/controller-level: `accept_with_changes`

## Closed Changes

The `with_changes` part is now closed:

1. malformed JSON fallback added
2. discarded-judgment transparency added
3. summary honesty boundary tightened

## Stop Rule

This packet should stop here.

It should not expand directly into:

1. source-plan persistence
2. auto-follow / auto-subscribe
3. paneling or voting by default
4. generic orchestration around AI judgment

The next slice, if opened, should be a new bounded AI-judgment refinement,
not a silent workflow expansion.
