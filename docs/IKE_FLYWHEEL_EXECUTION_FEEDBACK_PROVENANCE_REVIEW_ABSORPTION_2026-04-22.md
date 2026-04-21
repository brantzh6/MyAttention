# IKE Flywheel Execution Feedback Provenance Review Absorption

**Date:** 2026-04-22
**Reviewed result:** `IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21`
**Canonical review file:** [D:\code\MyAttention\docs\reviews\active\review_for_IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.md](/D:/code/MyAttention/docs/reviews/active/review_for_IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.md)

## Review Inputs

| Reviewer | Recommendation | Controller Use |
|---|---:|---|
| Kimi via claude-worker | accept | Accepted as internal review signal |
| Claude | accept | Accepted |
| ChatGPT | accept_with_changes | Accepted as debt framing |
| Gemini | accept | Accepted |

## Controller Judgment

**Decision:** accept.

This slice is accepted as a bounded provenance annotation layer for execution feedback inspect.

The accepted claim is narrow:

- pasted worker execution feedback can now carry structured caller-provided provenance
- provenance is echoed as `provenance_source=caller_provided`
- provenance remains `verified=false`
- provenance does not affect candidate truth state, review gates, promotion state, or canonical absorption

The stronger claim is explicitly rejected:

- this is not verified worker identity
- this is not artifact verification
- this is not packet/run binding validation
- this is not a trusted callback path
- this is not runtimeized execution-loop closure

## Absorbed Review Points

1. Provenance is structurally non-canonical and unverified.
2. AI prompt context may include provenance, but only with explicit caller-provided / not-verified framing.
3. Frontend display must continue to avoid making unverified provenance look trusted.
4. `controller_packet` remains advisory compression only; it must not become an action object or acceptance object.
5. Current provenance fields are sufficient for the manual bridge; do not keep adding form fields into the panel.
6. `flywheel.py` and `flywheel-inspect-panel.tsx` have crossed into decomposition debt.

## Deferred Debt

These are not blockers for this slice, but must stay visible:

- Add one partial-provenance test later if this route receives more hardening.
- Define a future verified-provenance model separately from `WorkerProvenance`.
- Keep verified provenance, artifact existence checks, packet/run binding, and trusted callback path as future runtime tasks.
- Stop expanding the current execution-feedback bridge unless it is a decomposition/hardening task.
- Split backend flywheel responsibilities before adding more semantics.
- Split frontend panel responsibilities before adding more manual workflow fields.

## Mainline Impact

The manual flywheel now has:

- AI-assisted conversation/flywheel inspect
- manual review/decision bridge
- manual worker packet bridge
- manual execution-feedback bridge
- caller-provided provenance annotation for worker feedback

This is enough to demonstrate a manual, AI-assisted flywheel path. The next mainline step should not be another bridge field expansion. The next step should either:

1. close the current manual loop with a documented end-to-end scenario, or
2. perform bounded decomposition so the current loop remains maintainable.

## Recommendation

Proceed, but do not describe this as provenance verification or trusted execution-loop completion.

