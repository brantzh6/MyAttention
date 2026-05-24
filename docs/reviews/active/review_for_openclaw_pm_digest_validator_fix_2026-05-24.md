# Re-Review: OpenClaw PM Digest Validator Fix

Date: 2026-05-24
Reviewer: Claude Code (independent reviewer)
Scope: Follow-up fix for F1 (stall threshold gate violation)
Prior review: `review_for_openclaw_pm_trigger_mechanism_2026-05-24.md`

---

## 1. Summary

The fix addresses the critical F1 finding from the prior review by implementing mechanical enforcement of the stall threshold gate. The validator (`scripts/ops/validate_openclaw_pm_digest.py`) is dependency-free, correctly rejects `decision: quiet` when `staleness_minutes >= 240`, and is now contractually required before PM run completion. Validation testing confirms expected behavior: VALID for compliant digests, INVALID for quiet+265 combination.

**Recommendation: accept** — The fix directly addresses F1 with appropriate mechanical enforcement.

---

## 2. Findings (Ordered by Severity)

### F1-FIX (Resolved): Stall threshold gate now mechanically enforced

**Prior violation:** PM digest `openclaw_pm_run_20260524_151200.json` reported `decision: quiet` with `staleness_minutes: 265`.

**Fix implemented:**

1. **Schema constraint** (`ops/schemas/openclaw_pm_run_digest_v1.schema.json` lines 81-110): JSON Schema `allOf` conditional that requires `decision != quiet` and `controller_action_needed: true` when `staleness_minutes >= 240`.

2. **Executable validator** (`scripts/ops/validate_openclaw_pm_digest.py` lines 90-100):
   ```python
   if staleness >= STALE_THRESHOLD_MINUTES:
       if decision == "quiet":
           return fail(
               "decision quiet is forbidden when "
               f"staleness_minutes={staleness} >= {STALE_THRESHOLD_MINUTES}"
           )
       if controller_action_needed is not True:
           return fail(...)
   ```

3. **Contract requirement** (`ops/agents/openclaw-ike-pm.md` lines 156-168): PM must validate digest before run completion. Invalid `latest.json` constitutes a failed PM run regardless of cron exit status.

**Validation assessment:**
- `python scripts\ops\validate_openclaw_pm_digest.py ops\pm-runs\latest.json` → VALID
- `python scripts\ops\validate_openclaw_pm_digest.py ops\pm-runs\history\openclaw_pm_run_20260524_151200.json` → INVALID (as expected for quiet+265)

**Status: FIXED.** The mechanical rejection is now in place.

---

### F2 (Low): Validator dependency-free status confirmed

**Observation:** The validator uses only `argparse`, `json`, `sys`, `pathlib.Path`, and `typing.Any` — all from Python standard library.

**Contract requirement:** "This validator is intentionally dependency-free because `jsonschema` may not be installed in the local runtime." (line 168)

**Status: CONFORMS.** No third-party packages required. Suitable for Windows local runtime.

---

### F3 (Low): Schema additionalProperties: false prevents drift

**Observation:** Schema line 111 sets `additionalProperties: false`, which prevents PM agents from adding non-schema fields that could bypass validation.

**Status: GOOD PRACTICE.** Ensures schema evolution is intentional.

---

### F4 (Minor): Contract validation step placement

**File:** `ops/agents/openclaw-ike-pm.md` lines 156-168

**Observation:** The contract specifies validation must run before a PM run is "considered complete" but does not specify whether validation should block the write or run post-write with correction.

**Quote:** "If validation fails, the PM must correct the digest and rerun validation."

**Assessment:** This is correct failure-mode behavior. The validator is post-write but pre-completion. The PM must fix and revalidate. This ensures the file on disk is always the PM's current state, not an intermediate that passes validation but differs from what the PM intended.

**Status: ACCEPTABLE DESIGN.** No change needed.

---

## 3. F1 Status: FIXED

The prior F1 finding identified that the stall threshold gate was not mechanically enforced. The fix implements:

1. Schema-level constraint (reactive defense)
2. Executable validator with explicit rejection logic (mechanical enforcement)
3. Contract requirement that invalid digest = failed PM run (accountability)

The validator correctly rejects the specific violation pattern (quiet + staleness >= 240) and provides clear error messaging. Validation testing confirms the fix works as intended.

---

## 4. Validation Assessment

| Test Case | Input | Expected | Actual | Status |
|-----------|-------|----------|--------|--------|
| Compliant digest | `latest.json` | VALID | VALID | PASS |
| Invalid quiet+265 | `openclaw_pm_run_20260524_151200.json` | INVALID | INVALID | PASS |
| JSON parse | Both files | Success | Success | PASS |
| Schema structure | Both files | Required fields present | Present | PASS |

**Overall validation: PASS.** The validator behaves correctly for both compliant and non-compliant inputs.

---

## 5. Open Risks

1. **PM agent compliance:** The validator enforces the rule, but the PM agent must actually run it. If the agent skips validation and writes an invalid digest, the violation persists until the next scheduled check. This is a process compliance risk, not a technical gap.

2. **Historical invalid digests:** Nine prior PM runs with `decision: quiet` and `staleness_minutes >= 240` remain in history. The incident (`openclaw_pm_health_incident_2026-05-24.md`) documents the pattern but does not require cleanup. These are evidentiary artifacts and should not be deleted, but could be annotated.

3. **No automated alerting:** There is no cron or hook that alerts on validation failure outside the PM run itself. If the PM agent fails silently, detection relies on the Codex health-watch secondary monitor.

4. **Schema enforcement gap:** The JSON Schema constraint is correct but requires a JSON Schema validator to use. The Python validator duplicates this logic. Both should stay in sync. Consider adding a comment in the schema pointing to the Python validator as the canonical enforcement.

---

## 6. Recommendation

**accept**

The fix directly addresses F1 with appropriate mechanical enforcement. The validator is dependency-free, correct, and contractually required. Validation testing confirms expected behavior. The remaining risks are process/compliance issues, not technical defects in the fix itself.

---

## Review Artifact Metadata

- Review type: independent re-review of F1 fix
- Prior review: `review_for_openclaw_pm_trigger_mechanism_2026-05-24.md`
- Files reviewed:
  - `ops/agents/openclaw-ike-pm.md`
  - `ops/schemas/openclaw_pm_run_digest_v1.schema.json`
  - `scripts/ops/validate_openclaw_pm_digest.py`
  - `tasks/codex/openclaw_pm_health_incident_2026-05-24.md`
  - `docs/reviews/active/review_for_openclaw_pm_trigger_mechanism_2026-05-24.md`
- Validation evidence: controller-reported test results
- No source files modified
- No services run
- No OpenClaw cron triggered
- No git operations performed