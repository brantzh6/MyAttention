# Review: OpenClaw PM Trigger / Codex Controller Boundary - 2026-05-25

Reviewer lane: `myattention-kimi-review`  
Controller: Codex  
Review packet: `tasks/codex/openclaw_pm_trigger_controller_boundary_review_packet_2026-05-25.md`  
Date: 2026-05-25

---

## 1. Findings (Ordered by Severity)

### 1.1 HIGH: Controller Authority Preservation - CORRECT

**Observation:** The correction explicitly preserves Codex as the controller.

**Evidence from `openclaw-ike-pm.md`:**
- "It does not replace Codex as controller."
- "`requested_controller_action` is advisory context only."
- "The Codex controller may ignore or supersede the advisory action."

**Evidence from `controller_wakeup_prompt.md`:**
- "OpenClaw is not the controller. You are."
- "Treat `requested_controller_action` as advisory context."
- "PM `forbidden_actions` constrain PM/delegate behavior by default. They do not prevent Codex from doing controller-owned work."

**Impact:** HIGH - The controller authority boundary is correctly established.

### 1.2 HIGH: PM Advisory Non-Binding - CORRECT

**Observation:** The trigger contract explicitly prevents PM advisories from constraining controller decisions.

**Evidence from schema (`openclaw_pm_trigger_v1.schema.json`):**
```json
"requested_controller_action": {
  "description": "Advisory PM observation for controller attention. This is not a binding instruction; Codex controller may supersede it after reading current project truth."
}
```

**Evidence from PM role file:**
- "`requested_controller_action` is advisory context only. It must be phrased as a PM observation, not an imperative that constrains Codex."
- "If PM detects that its previous trigger advisory is stale or already superseded, it should still wake Codex... but the advisory should say: `controller should inspect current_state and choose the next mainline action; prior PM advisory may be stale`."

**Impact:** HIGH - PM cannot block mainline progress through stale advisories.

### 1.3 MEDIUM: PM Forbidden Scope - CORRECT

**Observation:** PM is explicitly forbidden from controller-owned work.

**Evidence from `openclaw-ike-pm.md`:**
```markdown
## Forbidden
- task authoring
- source edits
- runtime operation
- review
- review absorption
- promotion decision
- GitHub issue/PR creation for IKE task management
```

**Evidence from trigger `forbidden_actions`:**
```json
"forbidden_actions": [
  "do not edit source outside the authorized cleanup packet scope",
  "do not operate runtime services",
  "do not decide promotion",
  "do not absorb review",
  "do not start a duplicate Codex run without checking the controller lease"
]
```

**Impact:** MEDIUM - PM scope is correctly bounded.

### 1.4 MEDIUM: Schema Validation - PASSED

**Observation:** All validation checks passed.

**Verification:**
```powershell
python -m json.tool ops\schemas\openclaw_pm_trigger_v1.schema.json
# Result: Valid JSON schema

python scripts\ops\validate_openclaw_pm_digest.py ops\pm-runs\latest.json
# Result: VALID

python scripts\ops\check_controller_gate.py --claim accepted_project_truth
# Result: PASS
```

**Impact:** MEDIUM - Technical validation confirms schema and digest integrity.

### 1.5 LOW: Bridge/Trigger Compatibility - PRESERVED

**Observation:** The correction maintains backward compatibility with the bridge protocol.

**Evidence from trigger file (`openclaw_pm_20260524_220300.json`):**
- `bridge.status`: "dispatched"
- `bridge.dispatch_mode`: "detached"
- Schema version: 1
- All required fields present

**Impact:** LOW - Existing triggers remain valid and processable.

### 1.6 LOW: Schema `forbidden_actions` Constraint - CORRECT

**Observation:** The schema includes a `not/contains` constraint preventing PM from forbidding task authoring.

**Evidence from schema:**
```json
"forbidden_actions": {
  "not": {
    "contains": {
      "const": "do not author tasks"
    }
  },
  "description": "PM/delegate boundaries by default. These must not prohibit Codex controller-owned decisions or task authoring when gates allow them."
}
```

**Impact:** LOW - Schema-level protection against PM overreach.

---

## 2. Open Questions

1. **Stale Advisory Detection:** The PM role file mentions detecting stale advisories, but does not specify the mechanism. How does PM determine if its prior advisory is "stale or already superseded"?

2. **Controller Supersede Documentation:** When Codex supersedes a PM advisory, is there a required documentation pattern (e.g., `tasks/codex/controller_superseded_pm_advisory_*.md`)?

3. **Trigger Archive Retention:** The PM role mentions optional archive to `ops/pm-runs/history/`. Is there a retention policy for trigger files in `ops/triggers/`?

---

## 3. Validation Gaps

None. All required validation passed:
- JSON schema is valid
- PM digest validates against schema
- Controller gate check passes

---

## 4. Governance Gaps

### 4.1 Controller Authority: PASSED
Codex remains controller. PM is explicitly not the controller.

### 4.2 Advisory Non-Binding: PASSED
`requested_controller_action` is advisory only. Schema and role file both enforce this.

### 4.3 PM Scope Boundaries: PASSED
PM is forbidden from task authoring, source edits, runtime operation, review, absorption, and promotion.

### 4.4 Bridge Compatibility: PASSED
Trigger format and bridge protocol remain compatible.

### 4.5 Schema Enforcement: PASSED
Schema prevents PM from forbidding controller-owned actions like task authoring.

---

## 5. Runtime Truth Gaps

None introduced by this correction. Current runtime state from `latest.json`:
- `decision`: "quiet"
- `status`: "ok"
- `staleness_minutes`: 111 (within 240 threshold)
- `controller_action_needed`: false
- `runtime_state.reachability_status`: ready

The PM correctly determined no trigger was needed at 00:03:00.

---

## 6. Recommendation

**accept**

The correction successfully establishes:

1. **Codex as controller** - Explicitly stated in both PM role and controller wakeup prompt
2. **PM advisory non-binding** - `requested_controller_action` is advisory context only
3. **PM scope boundaries** - Forbidden from task authoring, source edits, runtime, review, absorption, promotion
4. **Bridge/trigger compatibility** - Schema and existing triggers remain valid
5. **Validation gates** - All checks pass

The controller may now:
- Treat PM triggers as wakeup signals and evidence only
- Supersede stale PM advisories when project truth indicates a better action
- Proceed with controller-owned work (task authoring, review absorption, promotion decision) when gates allow

---

## Review Stop Condition

Review artifact written. No files edited. No OpenClaw cron run. No promotion decision made.
