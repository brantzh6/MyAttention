# Independent Review: OpenClaw PM Trigger Mechanism

Date: 2026-05-24
Reviewer: Claude Code (independent reviewer)
Scope: OpenClaw ike-pm trigger mechanism and Codex health-watch automation

## Summary

The OpenClaw PM trigger mechanism is architecturally sound and mostly conforms to the stated design intents. The primary violation is **Design Intent 4**: the stall threshold gate is not mechanically enforced by the OpenClaw PM agent. At least one PM digest (`openclaw_pm_run_20260524_151200.json`) reports `decision: quiet` with `staleness_minutes: 265`, which violates the mandatory trigger rule. The JSON schema includes a constraint that should prevent this, but the schema appears not to be applied by the PM agent during digest writing.

The Codex health-watch automation correctly identifies as a secondary monitoring role and does not usurp the primary PM trigger. The bridge correctly respects controller leases and produces appropriate busy/dispatched metadata.

**Recommendation: accept_with_changes** — The mechanism is functional but requires enforcement of the stall threshold gate at the OpenClaw agent level, not just schema validation.

---

## Findings (Ordered by Severity)

### F1 (Critical): Stall threshold gate violation

**File:** `ops/pm-runs/history/openclaw_pm_run_20260524_151200.json`

**Evidence:**
```json
{
  "decision": "quiet",
  "staleness_minutes": 265,
  "evidence": ["last_real_progress_at ... is ~265 minutes old, under 4-hour staleness threshold"]
}
```

**Violation:** `staleness_minutes >= 240` must not produce `decision: quiet`. The digest claims 265 minutes is "under 4-hour threshold" which is factually incorrect (265 > 240).

**Impact:** The PM failed to trigger when mainline was genuinely stalled. This defeats the primary purpose of the automation. The Codex health-watch correctly detected this violation and created an incident, but the PM should have triggered on its own.

**Root cause:** The schema constraint (`ops/schemas/openclaw_pm_run_digest_v1.schema.json` lines 81-110) uses JSON Schema `allOf` to require `decision != quiet` when `staleness_minutes >= 240`. However, the OpenClaw agent appears to write the digest without validating against the schema. The schema guard is reactive, not proactive.

**Additional occurrences:** Historical grep shows 19 PM runs with `staleness_minutes >= 200` and `decision: quiet`. Of these, several exceed 240:
- `openclaw_pm_run_20260521_084000.json`: staleness=267, decision=quiet
- `openclaw_pm_run_20260521_091000.json`: staleness=297, decision=quiet
- `openclaw_pm_run_20260521_041000.json`: staleness=266, decision=quiet
- `openclaw_pm_run_20260521_201000.json`: staleness=274, decision=quiet
- `openclaw_pm_run_20260522_054000.json`: staleness=256, decision=quiet
- `openclaw_pm_run_20260522_221200.json`: staleness=247, decision=quiet
- `openclaw_pm_run_20260523_164200.json`: staleness=264, decision=quiet
- `openclaw_pm_run_20260524_041200.json`: staleness=267, decision=quiet
- `openclaw_pm_run_20260524_151200.json`: staleness=265, decision=quiet

These indicate a systematic issue, not a one-time error.

---

### F2 (Medium): Bridge result trigger path mismatch

**File:** `ops/bridge/runs/openclaw_codex_20260524_074236.json`

**Evidence:**
```json
{
  "run_id": "openclaw_codex_20260524_074236",
  "trigger": "D:\\code\\MyAttention\\ops\\triggers\\openclaw_pm_20260524_153900.json"
}
```

**Observation:** The bridge run timestamp (074236 = 07:42:36 UTC) does not match the trigger file timestamp (153900 = 15:39:00+08:00). The trigger was created later than the bridge run it references.

**Impact:** This creates a data integrity question. The bridge metadata claims dispatch based on a trigger that did not exist at dispatch time. The `ops/triggers/openclaw_pm_20260524_153900.json` trigger file does show `bridge.status: dispatched` with `run_id: openclaw_codex_20260524_074236`, suggesting the bridge updated the trigger after dispatch, but the因果关系 is reversed in the bridge result file.

**Likely cause:** The bridge writes the trigger path into the result after dispatch, and the trigger file was created by a PM run that happened after the bridge already started a detached process for a prior trigger. The PM digest at 15:39 reused an existing dispatched run's PID 42336.

---

### F3 (Minor): Stale lease file not cleaned

**File:** `ops/state/codex_controller_lease.json`

**Evidence:**
```json
{
  "status": "running_detached",
  "expires_at": "2026-05-24T09:42:36+00:00"
}
```

**Observation:** At PM run time 15:39+08:00 (07:39 UTC), the lease has not expired (expires at 09:42 UTC). However, the PM digest evidence says "Controller lease openclaw_codex_20260524_024516 expired; no active lease" which references a different lease ID.

**Impact:** Low. The lease mechanism works, but there is confusion in evidence about which lease is being referenced. The lease cleanup in `release_lease()` (lines 177-191 of `openclaw_codex_bridge.py`) only removes the lock file if it matches the run_id, which is correct.

---

### F4 (Minor): Evidence sentence format inconsistent

**File:** `ops/agents/openclaw-ike-pm.md` lines 73-75

**Contract:** "Every digest evidence sentence that mentions the threshold must include both numbers: the computed `staleness_minutes` and `240`."

**Violation:** Multiple digests mention staleness without citing the threshold number 240 explicitly in the evidence array. Example from `openclaw_pm_run_20260524_151200.json`:
- Evidence: "last_real_progress_at ... is ~265 minutes old, under 4-hour staleness threshold" — missing explicit "threshold is 240" statement.

**Impact:** Low. The contract is meant to prevent ambiguity, but the violation is in formatting, not logic (though the logic was also wrong in this case).

---

## Conformance Matrix

| Design Intent | Status | Evidence |
|---------------|--------|----------|
| **1. OpenClaw ike-pm is primary trigger** | CONFORMS | `ops/agents/openclaw-ike-pm.md` line 5-7: "ike-pm is the local OpenClaw project-management operator... replaces Hermes as the preferred local progress trigger". `automation.toml` line 5: "OpenClaw `ike-pm` is the primary automatic trigger for mainline continuation." |
| **2. Codex remains controller, not second PM** | CONFORMS | `automation.toml` forbids: writing `mainline_auto_continue_result_*.md`, authoring product task packets, editing source files, operating runtime, claiming mainline progress. `ops/bridge/README.md` line 16: "Codex remains the controller and promotion decider." |
| **3. Codex health-watch only detects and reports** | CONFORMS | `automation.toml` line 39-42: "Allowed action when unhealthy: Write or append one incident artifact... Forbidden actions: Do not write mainline_auto_continue_result_*.md... Do not claim mainline progress." |
| **4. Stall threshold mechanical: staleness >= 240 → not quiet** | VIOLATED | `openclaw_pm_run_20260524_151200.json`: decision=quiet, staleness_minutes=265. Schema constraint exists but is not enforced by PM agent. |
| **5. Automation-health artifacts don't update progress** | CONFORMS | `tasks/codex/openclaw_pm_health_incident_2026-05-24.md` lines 15-16: "This artifact is automation-health evidence only. It must not update `last_real_progress_at` and must not be counted as product/mainline progress." |
| **6. Bridge respects lease, avoids duplicates** | CONFORMS | `openclaw_codex_bridge.py` lines 78-82: `lease_is_active()` checks status and expiration. Lines 379-401: returns `status: busy` when lease active. Lines 143-159: lock file prevents concurrent acquisition. |
| **7. PM/bridge failure produces controller incident** | CONFORMS | `tasks/codex/openclaw_pm_health_incident_2026-05-24.md` includes: summary, evidence, impacted component, violated rule, recommended owner lane (`openclaw-ike-pm`), and stop condition. The incident is controller-consumable. |

---

## Validation Performed

1. Read all contract and schema files in scope.
2. Read latest PM digest (`ops/pm-runs/latest.json`) and 3 recent history digests.
3. Read 2 trigger files and 1 bridge result to verify dispatch chain.
4. Read current state (`ops/state/current_state.json`) to verify `last_real_progress_at` definition.
5. Read controller lease file to verify active/busy detection.
6. Grep for all `decision: quiet` digests (38 found).
7. Grep for all `staleness_minutes >= 200` (19 found, 9 with staleness >= 240 and decision quiet).
8. Read incident artifact to verify stop condition and owner lane format.
9. Verified schema constraint logic in `openclaw_pm_run_digest_v1.schema.json` lines 81-110.

---

## Open Risks

1. **Schema not enforced at write time:** The JSON schema constraint is correct, but OpenClaw agents do not validate digests against schema before writing. The constraint is defensive, not preventative.

2. **Evidence chain of custody:** The bridge result/trigger timestamp mismatch suggests the bridge metadata may be updated after dispatch, which could confuse forensic analysis of automation behavior.

3. **Codex health-watch dependency:** The mechanism relies on Codex health-watch to detect PM gate violations. If Codex automation also fails (e.g., due to spawn EPERM), no secondary detection exists.

4. **Historical violations:** At least 9 prior PM runs violated the stall gate. This indicates the OpenClaw agent logic needs correction, not just a one-time fix.

---

## Recommendation

**accept_with_changes**

The mechanism architecture is correct and 6 of 7 design intents are satisfied. The stall threshold violation (Intent 4) is a critical defect that must be fixed at the OpenClaw agent level.

**Required changes:**

1. OpenClaw `ike-pm` agent must enforce the stall threshold gate in its execution logic, not rely on schema validation after write.
2. The PM agent should validate digest against schema before writing to `ops/pm-runs/latest.json`.
3. The bridge should write the trigger path to the result file at dispatch time, not update it retroactively.
4. Evidence sentences citing staleness must include both computed value and threshold (240) as per contract.

**Optional improvements:**

1. Add a CI or hook that validates PM digests against schema after write and alerts on violations.
2. Consider adding a staleness_hours or staleness_threshold_met field to make the gate decision more explicit.
3. Clean up historical invalid digests or mark them with a correction note.

---

## Review Artifact Metadata

- Review type: independent mechanism audit
- Reviewer: Claude Code (prompted as independent reviewer)
- No source files modified
- No services run
- No OpenClaw cron triggered
- No git operations performed