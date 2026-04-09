# Current Mainline Handoff

## Purpose

This document is the shortest reliable handoff for another agent or engineer to continue the current mainline without re-deriving project state from the full conversation history.

It is intentionally operational, not visionary.

## Latest Override

This section overrides older runtime phase notes below when they conflict.

- `R2-G14` controller-acceptability rule is now durably fixed:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G14_CONTROLLER_ACCEPTABILITY_RULE_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G14_CONTROLLER_ACCEPTABILITY_RULE_RESULT_2026-04-09.md)
  - current controller rule:
    - `ready + canonical_ready`:
      - acceptable for canonical live proof
    - `ambiguous + bounded_live_proof_ready`:
      - acceptable only for bounded alternate-port live proof
    - `ambiguous + blocked_owner_mismatch`:
      - not acceptable
    - `ambiguous + blocked_code_freshness`:
      - not acceptable
    - `down`:
      - not acceptable
- `R2-G` phase result is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G_RESULT_MILESTONE_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G_RESULT_MILESTONE_2026-04-09.md)
  - current truthful judgment:
    - `R2-G = materially complete`
  - current controller interpretation:
    - service observability is now sufficient
    - bounded alternate-port live proof is now explicitly controller-acceptable
    - canonical `8000` service proof remains blocked by launch-path / interpreter ownership drift
- active runtime phase is now:
  - `R2-H Canonical Service Launch Path Normalization`
  - durable phase judgment:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-H_PHASE_JUDGMENT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-H_PHASE_JUDGMENT_2026-04-09.md)
  - current controller judgment:
    - no more `R2-G` observability growth is needed by default
    - next work should normalize one controller-acceptable canonical launch path
  - durable phase plan:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-H_PLAN_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-H_PLAN_2026-04-09.md)
- `R2-H1` canonical launch baseline is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-H1_RESULT_MILESTONE_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-H1_RESULT_MILESTONE_2026-04-09.md)
  - current truthful judgment:
    - `R2-H1 = accept_with_changes`
  - current controller interpretation:
    - canonical launch command is now machine-readable and visible
    - canonical live service normalization is still pending
    - next work should attempt one bounded canonical restart using the explicit launch path
- `R2-H2` bounded canonical restart is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-H2_RESULT_MILESTONE_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-H2_RESULT_MILESTONE_2026-04-09.md)
  - current truthful judgment:
    - `R2-H2 = accept_with_changes`
  - current controller interpretation:
    - canonical `8000` now serves the latest preflight schema
    - canonical code freshness is no longer the blocker
    - remaining blocker is interpreter ownership drift (`blocked_owner_mismatch`)
- `R2-H3` interpreter-drift diagnosis is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-H3_WINDOWS_INTERPRETER_DRIFT_NOTE_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-H3_WINDOWS_INTERPRETER_DRIFT_NOTE_2026-04-09.md)
  - current controller interpretation:
    - the parent repo interpreter is real
    - the child listener still resolves to system `Python312`
    - this may be a genuine drift or a Windows `.venv` process-shape quirk
    - do not relax the canonical rule until that distinction is reviewed
- `R2-H4` Windows redirector diagnosis is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-H4_WINDOWS_REDIRECTOR_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-H4_WINDOWS_REDIRECTOR_RESULT_2026-04-09.md)
  - current truthful judgment:
    - `R2-H4 = accept_with_changes`
  - current controller interpretation:
    - helper/test evidence now classifies the current process shape as
      `windows_venv_redirector_candidate`
    - controller acceptability is still unchanged and still blocked
- next narrow decision note is now prepared:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-H5_ACCEPTABILITY_DECISION_PLAN_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-H5_ACCEPTABILITY_DECISION_PLAN_2026-04-09.md)
- repository/workspace isolation work is now formally prepared:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RESTRUCTURE_AND_WORKSPACE_ISOLATION_PLAN_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RESTRUCTURE_AND_WORKSPACE_ISOLATION_PLAN_2026-04-09.md)
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RESTRUCTURE_INVENTORY_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RESTRUCTURE_INVENTORY_2026-04-09.md)
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RESTRUCTURE_BACKUP_AND_ROLLBACK_CHECKLIST_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RESTRUCTURE_BACKUP_AND_ROLLBACK_CHECKLIST_2026-04-09.md)
  - [D:\code\MyAttention\docs\IKE_OPENCLAW_WORKSPACE_REWRITE_PLAN_2026-04-09.md](/D:/code/MyAttention/docs/IKE_OPENCLAW_WORKSPACE_REWRITE_PLAN_2026-04-09.md)
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_RUNTIME_ROOT_REWRITE_PLAN_2026-04-09.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_RUNTIME_ROOT_REWRITE_PLAN_2026-04-09.md)
  - current controller interpretation:
    - workspace pollution risk is now formally accepted as real
    - migration should proceed as controlled parallel-root migration, not blind in-place rename

- collaboration baseline is now fixed as:
  - `GPT / Codex` = controller and decision routing
  - `Claude Code` + `OpenClaw` = routine automatable execution chain
  - latest `Qwen3.6 Plus` should be preferred for Qwen-backed routine coding/review work
  - manual `Claude / Gemini / GPT` review remains milestone/high-risk support only, not daily mainline dependency
  - durable routing reference:
    - [D:\code\MyAttention\docs\PROJECT_AGENT_HARNESS_CONTRACT.md](/D:/code/MyAttention/docs/PROJECT_AGENT_HARNESS_CONTRACT.md)

- `R2-G1` service-discipline diagnosis is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G1_SERVICE_DISCIPLINE_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G1_SERVICE_DISCIPLINE_RESULT_2026-04-08.md)
  - current truthful judgment:
    - `R2-G1 = accept_with_changes`
  - current controller evidence:
    - `GET /health` currently returns `200`
    - `8000` currently has a single listener
    - duplicate `run_service.py` launchers still exist across repo `.venv` and system `Python312`
  - current controller interpretation:
    - the main operational risk is ambiguous service ownership during live proof
    - repo `.venv` + explicit `services/api/run_service.py` should be treated as the truthful baseline
- methodology PDF study packet is now durably prepared and delegated to local Claude:
  - [D:\code\MyAttention\docs\IKE_THINKING_ARMORY_PDF_STUDY_PACKET_2026-04-08.md](/D:/code/MyAttention/docs/IKE_THINKING_ARMORY_PDF_STUDY_PACKET_2026-04-08.md)
  - extracted corpus bundle:
    - [D:\code\MyAttention\.runtime\methodology-pdf-study\stable_manifest.json](/D:/code/MyAttention/.runtime/methodology-pdf-study/stable_manifest.json)
    - [D:\code\MyAttention\.runtime\methodology-pdf-study\stable_texts](/D:/code/MyAttention/.runtime/methodology-pdf-study/stable_texts)
  - active local Claude worker run:
    - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T152547-126e6d2a](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T152547-126e6d2a)
- methodology PDF study batch recovery is now also prepared:
  - [D:\code\MyAttention\docs\IKE_THINKING_ARMORY_PDF_BATCH_PLAN_2026-04-08.md](/D:/code/MyAttention/docs/IKE_THINKING_ARMORY_PDF_BATCH_PLAN_2026-04-08.md)
  - active batch A run:
    - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T155231-cb5e2538](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T155231-cb5e2538)
  - active batch B run:
    - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T155231-4999aa1d](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T155231-4999aa1d)
- methodology PDF execution truth is now durably recorded at:
  - [D:\code\MyAttention\docs\IKE_THINKING_ARMORY_PDF_EXECUTION_STATUS_2026-04-09.md](/D:/code/MyAttention/docs/IKE_THINKING_ARMORY_PDF_EXECUTION_STATUS_2026-04-09.md)
  - current controller interpretation:
    - corpus extraction is ready
    - full-corpus, batch, and micro-batch Claude runs still lack durable final artifacts
    - direct Claude CLI recovery attempts also timed out
    - current blocker is delegated completion/throughput, not missing inputs

- `R2-C1` runtime-backed visible-surface proof is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-C1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-C1_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R2-C1 = accept_with_changes`
  - current controller evidence:
    - targeted runtime-visible slice:
      - `34 passed, 28 warnings, 9 subtests passed`
    - combined DB-backed slice:
      - `89 passed, 1 warning`
  - current controller interpretation:
    - one narrow runtime-backed visible surface is now real
    - do not widen this into broad UI/runtime integration yet
    - `R2-C2 / R2-C3 / R2-C4` still need durable closure
- active runtime phase is now:
  - `R2-C Runtime-to-Visible-Surface Narrow Integration`
  - current next work should stay on:
    - review
    - testing
    - evolution
    for the narrow visible-surface proof
- `R2-C` phase result is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-C_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-C_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R2-C = materially complete with fallback review coverage`
- active runtime phase is now:
  - `R2-D Runtime Project Bootstrap Alignment`
  - current controller judgment:
    - visible runtime surface exists, but live runtime project truth is still absent
    - next work should bootstrap one truthful runtime project presence path
    - do not widen into broad UI/runtime integration or knowledge-base/runtime merge
- `R2-D1` runtime project bootstrap coding is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-D1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-D1_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R2-D1 = accept_with_changes`
  - current controller evidence:
    - targeted backend slice:
      - `30 passed, 28 warnings, 9 subtests passed`
    - live proof:
      - `POST /api/ike/v0/runtime/project-surface/bootstrap` returned `200`
      - `POST /api/ike/v0/runtime/project-surface/inspect` resolved the bootstrapped project
- `R2-D` phase result is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-D_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-D_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R2-D = materially complete with mixed delegated/controller evidence`
- active runtime phase is now:
  - `R2-E Runtime Surface Activation Narrow Integration`
  - current controller judgment:
    - explicit runtime bootstrap now works live
    - next remaining narrow gap is direct settings-surface usability
    - broader UI/runtime integration remains closed
- `R2-E1` settings-surface activation proof is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-E1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-E1_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R2-E1 = accept_with_changes`
  - current controller evidence:
    - `npx tsc --noEmit` passed
    - `GET /health` returned `200`
    - `POST /api/ike/v0/runtime/project-surface/bootstrap` returned `200`
    - `POST /api/ike/v0/runtime/project-surface/inspect` returned the bootstrapped runtime project surface
- `R2-E` phase result is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-E_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-E_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R2-E = materially complete with fallback review coverage`
- current controller rule after `R2-E`:
  - keep runtime activation explicit
  - do not widen this into broad UI/runtime integration
  - visible-surface growth must remain runtime-truth-backed
- active runtime phase is now:
  - `R2-F Visible Benchmark Queue Bridge Narrow Integration`
  - current controller judgment:
    - the next narrow step after runtime activation is one explicit benchmark-to-runtime review action
    - imported benchmark candidates must remain `pending_review`
    - broader benchmark/runtime fusion remains closed
- `R2-F1` visible benchmark queue bridge is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-F1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-F1_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R2-F1 = accept_with_changes`
  - current controller evidence:
    - benchmark-bridge + router slice:
      - `31 passed, 28 warnings, 9 subtests passed`
    - `npx tsc --noEmit` passed
    - live route proof was not accepted due local API process instability
- `R2-F` phase result is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-F_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-F_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R2-F = materially complete with fallback review coverage`
- current controller rule after `R2-F`:
  - visible benchmark actions may create reviewable runtime packets
  - they must not auto-create trusted memory
  - broad benchmark/runtime integration is still closed
- active runtime phase is now:
  - `R2-G Runtime Service Stability And Delegated Closure Hardening`
  - current controller judgment:
    - runtime truth and narrow visible/runtime bridges are materially real
    - the next immediate blockers are operational reliability, not new truth semantics
    - local API process instability and incomplete delegated finalization are now the main runtime risks
- accepted next-phase docs:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G_SERVICE_STABILITY_PLAN_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G_SERVICE_STABILITY_PLAN_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-G2_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-G2_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G_EXECUTION_PACK_2026-04-08.md)
- `R2-G2` service preflight result is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G2_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G2_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R2-G2 = accept_with_changes`
  - current controller evidence:
    - `39 passed, 1 warning`
    - live preflight snapshot currently returns `ready`
    - current live owner count is `1`
    - current observed listener is system `Python312`, not repo `.venv`
    - preferred-owner evaluation is now machine-readable and currently returns:
      - `preferred_mismatch`
    - live route proof succeeded under fresh repo `.venv` `uvicorn` on `8011`
  - current controller interpretation:
    - machine-readable live-proof readiness is now real
    - route semantics are real
    - remaining gap is stale service ownership policy, not route logic
- `R2-G4` strict preferred-owner gate is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G4_STRICT_PREFERRED_OWNER_GATE_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G4_STRICT_PREFERRED_OWNER_GATE_RESULT_2026-04-09.md)
  - current truthful judgment:
    - `R2-G4 = accept_with_changes`
  - current controller evidence:
    - combined service-preflight + router slice:
      - `67 passed, 28 warnings, 9 subtests passed`
    - live helper snapshot:
      - `run_preflight_sync(port=8000, strict_preferred_owner=True)`
      - returned `ambiguous`
      - `details.preferred_owner.status = preferred_mismatch`
  - current controller interpretation:
    - stale service ownership is still unresolved
    - but current mismatch is no longer silently misclassified as `ready`
    - controller can now require preferred-owner match for live proof
- `R2-G5` visible preflight surfacing is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G5_VISIBLE_PREFLIGHT_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G5_VISIBLE_PREFLIGHT_RESULT_2026-04-09.md)
  - current truthful judgment:
    - `R2-G5 = accept_with_changes`
  - current controller evidence:
    - `npx tsc --noEmit` passed
    - strict preflight helper snapshot on current `8000`:
      - `status = ambiguous`
      - summary:
        - `Ambiguous: port ownership unclear`
  - current controller interpretation:
    - the strict preferred-owner gate is now ready to surface on the existing runtime settings panel
    - stale service ownership may still keep the live page on old behavior until the active API process is restarted on latest code
- `R2-G6` owner reclaim note is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G6_OWNER_RECLAIM_NOTE_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G6_OWNER_RECLAIM_NOTE_2026-04-09.md)
  - current controller evidence:
    - `8000` was explicitly cleared and recovered
    - `GET /health` is back to `200`
    - current listener owner is still system `Python312`
  - current controller interpretation:
    - API availability is restored
    - service ownership normalization is still not achieved
    - preferred-owner strict preflight remains the truthful live-proof gate
- `R2-G7` owner-chain diagnosis is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G7_OWNER_CHAIN_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G7_OWNER_CHAIN_RESULT_2026-04-09.md)
  - current controller evidence:
    - strict live snapshot on current `8000` now reports:
      - `preferred_owner.status = preferred_mismatch`
      - `owner_chain.status = parent_preferred_child_mismatch`
  - current controller interpretation:
    - the mismatch is no longer just generic stale ownership
    - the preferred repo-owned launcher is present in the parent chain
    - the actual listener still drifts to a system-Python child
- `R2-G8` live-route stale-code note is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G8_LIVE_ROUTE_STALE_CODE_NOTE_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G8_LIVE_ROUTE_STALE_CODE_NOTE_2026-04-09.md)
  - current controller interpretation:
    - current `8000` route semantics are real
    - but the active `8000` service still does not expose the latest `service_preflight` field set
    - for newest `R2-G` fields, local helper/test evidence is currently stronger than live `8000` route evidence
- `R2-G9` code-freshness surfacing is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G9_CODE_FRESHNESS_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G9_CODE_FRESHNESS_RESULT_2026-04-09.md)
  - current truthful judgment:
    - `R2-G9 = accept_with_changes`
  - current controller evidence:
    - service-preflight + router slice:
      - `71 passed, 28 warnings, 9 subtests passed`
    - `python -m compileall` for preflight/router passed
    - `npx tsc --noEmit` passed
    - current local helper snapshot reports:
      - `status = ambiguous`
      - `preferred_owner.status = preferred_mismatch`
      - `owner_chain.status = parent_preferred_child_mismatch`
      - `code_fingerprint.fingerprint = 2c1cb7cf783aa7b4`
      - `code_freshness.status = unchecked`
  - current controller interpretation:
    - preflight can now carry machine-readable code-fingerprint data
    - strict code-freshness mismatch can now downgrade live proof to `ambiguous`
    - current `8000` route may still be stale until service ownership/code freshness is normalized
- `R2-G10` targeted preflight route support is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G10_TARGETED_PREFLIGHT_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G10_TARGETED_PREFLIGHT_RESULT_2026-04-09.md)
  - current truthful judgment:
    - `R2-G10 = accept_with_changes`
  - current controller evidence:
    - service-preflight + router slice:
      - `72 passed, 28 warnings, 9 subtests passed`
    - router compile passed
    - preflight inspect can now target explicit alternate `host/port`
  - current controller interpretation:
    - live-proof targeting is no longer hardcoded to `8000`
    - fresh alternate-port live proof is still blocked by launch-path / served-code drift
    - the next remaining `R2-G` blocker is launch-path discipline, not missing inspectability
- next narrow `R2-G` target is now explicitly fixed at:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G11_LAUNCH_PATH_DISCIPLINE_PLAN_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G11_LAUNCH_PATH_DISCIPLINE_PLAN_2026-04-09.md)
  - current controller interpretation:
    - remaining `R2-G` work should stay on launch-path discipline and served-code freshness normalization
    - do not widen into supervision, deployment automation, or a new runtime truth phase
- `R2-G11` fresh alternate-port live proof is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G11_RESULT_MILESTONE_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G11_RESULT_MILESTONE_2026-04-09.md)
  - current truthful judgment:
    - `R2-G11 = accept_with_changes`
  - current controller evidence:
    - fresh `8013` live route returns latest fields:
      - `owner_chain`
      - `code_fingerprint`
      - `code_freshness`
    - when the current fingerprint is supplied:
      - `code_freshness.status = match`
    - overall live proof still remains `ambiguous` because:
      - `preferred_owner.status = preferred_mismatch`
      - `owner_chain.status = parent_preferred_child_mismatch`
  - current controller interpretation:
    - fresh-code live route proof is now real
    - served-code freshness is no longer the main unresolved blocker
    - remaining `R2-G` ambiguity is now isolated to launch-path / interpreter ownership discipline
- `R2-G12` repo-launcher surfacing is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G12_REPO_LAUNCHER_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G12_REPO_LAUNCHER_RESULT_2026-04-09.md)
  - current truthful judgment:
    - `R2-G12 = accept_with_changes`
  - current controller evidence:
    - service-preflight + router slice:
      - `74 passed, 28 warnings, 9 subtests passed`
    - compile passed
    - `npx tsc --noEmit` passed
    - current helper snapshot on `8000` reports:
      - `preferred_owner.status = preferred_mismatch`
      - `owner_chain.status = parent_preferred_child_mismatch`
      - `repo_launcher.status = parent_and_child_repo_launcher_match`
  - current controller interpretation:
    - remaining `R2-G` work is now a controller acceptability rule question
    - observability is no longer the limiting factor
- `R2-G13` controller acceptability surfacing is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G13_CONTROLLER_ACCEPTABILITY_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G13_CONTROLLER_ACCEPTABILITY_RESULT_2026-04-09.md)
  - current truthful judgment:
    - `R2-G13 = accept_with_changes`
  - current controller evidence:
    - router + service-preflight slice:
      - `76 passed, 28 warnings, 9 subtests passed`
    - compile passed
    - `npx tsc --noEmit` passed
    - current helper snapshot on `8000` reports:
      - `controller_acceptability.status = blocked_owner_mismatch`
  - current controller interpretation:
    - `R2-G` has moved from observability hardening to controller rule hardening
- next narrow `R2-G` target is now fixed at:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G14_CONTROLLER_ACCEPTABILITY_RULE_PLAN_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G14_CONTROLLER_ACCEPTABILITY_RULE_PLAN_2026-04-09.md)
  - current controller interpretation:
    - the next real question is not another field
    - it is the explicit usage rule for `bounded_live_proof_ready`
- active delegated execution for `R2-G2`:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T153652-948b3f83](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T153652-948b3f83)
- detached completion pressure is now durably recorded at:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G3_DETACHED_COMPLETION_NOTE_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G3_DETACHED_COMPLETION_NOTE_2026-04-09.md)
  - current controller evidence:
    - `R2-G2` coding run still times out under detached wait
    - thinking-armory PDF batch A still times out under detached wait
    - thinking-armory PDF batch B still times out under detached wait
  - current controller interpretation:
    - detached completion reliability remains an active hardening gap
    - do not treat these runs as accepted delegated closure
- coding-lane baseline is now durably recorded at:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_OPENCLAW_VS_CLAUDE_CODING_BASELINE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_OPENCLAW_VS_CLAUDE_CODING_BASELINE_2026-04-08.md)
- Claude worker hardening requirements are now durably recorded at:
  - [D:\code\MyAttention\docs\CLAUDE_WORKER_RUNTIME_HARDENING_REQUIREMENTS_2026-04-08.md](/D:/code/MyAttention/docs/CLAUDE_WORKER_RUNTIME_HARDENING_REQUIREMENTS_2026-04-08.md)

- `R1-K1` read-path trust coding is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-K1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-K1_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R1-K1 = accept_with_changes`
  - current controller evidence:
    - focused read-path slice:
      - `29 passed, 1 warning`
    - combined truth-adjacent slice:
      - `120 passed, 1 warning`
- `R1-K3` testing is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-K3_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-K3_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R1-K3 = accept_with_changes`
- `R1-K` phase result is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-K_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-K_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R1-K = materially complete with mixed delegated/controller evidence`
- current controller rule after `R1-K`:
  - current runtime read-path trusted packet visibility should be treated as
    relevance-aware on the existing helper/read surfaces
  - do not widen platform/API/UI scope from this helper-level alignment alone
- active runtime phase is now:
  - `R2-A Runtime v0 Consolidated Readiness Review`
- accepted next-phase docs:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_CONSOLIDATED_REVIEW_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_CONSOLIDATED_REVIEW_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_REVIEW_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_REVIEW_PACK_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_SINGLE_FILE_REVIEW_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_SINGLE_FILE_REVIEW_PACK_2026-04-08.md)
- returned review is now durably synthesized at:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_REVIEW_SYNTHESIS_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_REVIEW_SYNTHESIS_2026-04-08.md)
- current controller clarification after returned review:
  - `R2-A` remains the correct active phase
  - broader integration is not yet opened
  - `R2-A` must first settle closure-discipline debt and then make the broader
    integration gate explicit
- `R2-A` debt settlement is now durably recorded at:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_DEBT_SETTLEMENT_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_DEBT_SETTLEMENT_RESULT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_RETAINED_NOTES_UNIFIED_BACKLOG_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_RETAINED_NOTES_UNIFIED_BACKLOG_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_METHOD_RULES_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_METHOD_RULES_2026-04-08.md)
- `R2-A` readiness gate is now durably recorded at:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_READINESS_GATE_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_READINESS_GATE_RESULT_2026-04-08.md)
- current controller gate result:
  - runtime is a strong runtime-base candidate
  - broader integration is still not yet opened
- active runtime phase is now:
  - `R2-B Debt Recovery And Narrow Runtime Proof Gate`
- accepted next-phase docs:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B_DEBT_AND_NARROW_INTEGRATION_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B_DEBT_AND_NARROW_INTEGRATION_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-B1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-B1_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-B2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-B2_REVIEW_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-B3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-B3_TEST_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-B4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-B4_EVOLUTION_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B_EXECUTION_PACK_2026-04-08.md)
- `.runtime/delegation` entrypoints now also exist for:
  - `R2-B1` coding
  - `R2-B2` review
  - `R2-B3` testing
  - `R2-B4` evolution
- current active delegated execution:
  - `R2-B1` coding via local Claude worker is in progress:
    - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T043044-81696251](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T043044-81696251)
- current controller-side comparison:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_lifecycle_proof.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_lifecycle_proof.py)
    passes focused validation with `19 passed, 1 warning`
  - current controller recommendation:
    - `accept_with_changes`
- strategic scheduling note added:
  - [D:\code\MyAttention\docs\IKE_STRATEGIC_SCHEDULING_NOTE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_STRATEGIC_SCHEDULING_NOTE_2026-04-08.md)

- `R1-I` is now materially complete with mixed delegated/controller evidence:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R1-I = materially complete with mixed delegated/controller evidence`
- active runtime phase is now:
  - `R1-J DB-backed Runtime Test Stability Hardening`
- accepted next-phase docs:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J_DB_TEST_STABILITY_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J_DB_TEST_STABILITY_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-J1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-J1_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-J2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-J2_REVIEW_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-J3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-J3_TEST_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-J4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-J4_EVOLUTION_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J_EXECUTION_PACK_2026-04-08.md)
- current controller judgment after `R1-I`:
  - do not widen runtime truth or platform surface
  - fix DB-backed repeatability and fixture determinism first
  - treat transient rerun-only greenness as a remaining hardening gap, not as a
    semantic/runtime-truth redesign trigger
- `R1-J1` coding is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J1_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R1-J1 = accept_with_changes`
  - controller finding:
    - no new coding patch is currently justified
    - repeated DB-backed validation is green across the targeted slices
- `R1-J3` testing is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J3_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J3_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R1-J3 = accept_with_changes`
  - current controller evidence:
    - `8x` repeated combined truth-adjacent DB-backed slice:
      - `118 passed, 1 warning` each run
    - `4x` repeated DB-backed runtime-core slice:
      - `84 passed, 1 warning` each run
- current `R1-J` status note:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J_STATUS_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J_STATUS_MILESTONE_2026-04-08.md)
- current `R1-J` controller interpretation:
  - the phase no longer points to an obvious coding patch
  - next question is whether review/evolution should absorb the repeated green
    evidence as sufficient closure for this narrow stability phase
- `R1-J2` delegated review is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J2_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J2_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R1-J2 = accept_with_changes`
- `R1-J4` evolution is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J4_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J4_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R1-J4 = accept`
- `R1-J` phase result is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R1-J = materially complete with mixed delegated/controller evidence`
- current controller rule after `R1-J`:
  - repeated targeted green DB-backed runs are sufficient closure evidence for a
    narrow stability phase
  - do not invent speculative patches after historical transient failures if
    current reproducibility is green
- active runtime phase is now:
  - `R1-K Read-Path Trust Semantics Alignment`
- accepted next-phase docs:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-K_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-K_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-K_READ_PATH_TRUST_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-K_READ_PATH_TRUST_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-K1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-K1_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-K2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-K2_REVIEW_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-K3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-K3_TEST_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-K4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-K4_EVOLUTION_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-K_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-K_EXECUTION_PACK_2026-04-08.md)
- current controller judgment after `R1-J`:
  - do not keep grinding stability work when targeted repeatability is green
  - next real runtime gap is explicit read-path trusted packet semantics

- `R1-I1` operational-guardrail coding is now green and durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I1_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-I1_OPERATIONAL_GUARDRAILS_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-I1_OPERATIONAL_GUARDRAILS_RESULT.md)
  - current truthful judgment:
    - `R1-I1 = accept_with_changes`
  - controller validation now passes:
    - `23 passed, 1 warning`
    - `114 passed, 1 warning`
- `R1-I2` delegated review is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I2_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I2_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-I2_OPERATIONAL_GUARDRAILS_REVIEW_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-I2_OPERATIONAL_GUARDRAILS_REVIEW_RESULT.md)
  - current truthful judgment:
    - `R1-I2 = accept_with_changes`
- `R1-I3` testing is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I3_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I3_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-I3_OPERATIONAL_GUARDRAILS_TEST_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-I3_OPERATIONAL_GUARDRAILS_TEST_RESULT.md)
  - current truthful judgment:
    - `R1-I3 = accept_with_changes`
- `R1-I4` evolution is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I4_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I4_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-I4_OPERATIONAL_GUARDRAILS_EVOLUTION_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-I4_OPERATIONAL_GUARDRAILS_EVOLUTION_RESULT.md)
  - current truthful judgment:
    - `R1-I4 = accept_with_changes`
- `R1-I` phase result is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I_RESULT_MILESTONE_2026-04-08.md)
  - current truthful judgment:
    - `R1-I = materially complete with mixed delegated/controller evidence`
- Active runtime phase is now `R1-I`, not `R1-H`.
- `R1-H` is now materially complete for the current delegated-evidence recovery
  scope:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_RESULT_MILESTONE_2026-04-08.md)
- accepted next runtime phase is now:
  - `R1-I Operational Guardrail Hardening`
- next-phase controller docs:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I_OPERATIONAL_GUARDRAILS_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I_OPERATIONAL_GUARDRAILS_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-I1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-I1_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-I2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-I2_REVIEW_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-I3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-I3_TEST_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-I4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-I4_EVOLUTION_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I_EXECUTION_PACK_2026-04-08.md)
- `R1-D` recovery under `R1-H` is now complete:
  - `R1-D2` delegated review recovered from:
    - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T164557-47ca6931](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T164557-47ca6931)
  - `R1-D3` delegated testing recovered from:
    - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T164816-2a5d159d](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T164816-2a5d159d)
  - refreshed phase evidence now shows:
    - `R1-D`, `R1-E`, `R1-F`, and `R1-G` are all fully delegated
  - durable recovery note:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_R1-D_RECOVERY_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_R1-D_RECOVERY_RESULT_2026-04-08.md)
  - current controller judgment:
    - `R1-H` can now be treated as materially complete for the current recovery scope
  - phase-level result:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_RESULT_MILESTONE_2026-04-08.md)
- `R1-E` recovery under `R1-H` is now complete:
  - `R1-E2` delegated review recovered from:
    - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T163513-8ee4c053](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T163513-8ee4c053)
  - `R1-E3` delegated testing recovered from:
    - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T163905-4c250ac5](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T163905-4c250ac5)
  - `R1-E4` delegated evolution recovered from:
    - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T163711-b67fb56e](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T163711-b67fb56e)
  - refreshed phase evidence now shows:
    - `R1-E`: delegated = `coding, review, testing, evolution`
    - `R1-D`: delegated = `coding, evolution`; fallback = `review, testing`
  - durable recovery note:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_R1-E_RECOVERY_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_R1-E_RECOVERY_RESULT_2026-04-08.md)
  - current next `R1-H` target is now:
    - `R1-D2`
    - `R1-D3`
- Active runtime phase is now `R1-H`, not `R1-G`.
- `R1-H1` delegated-evidence recovery support is now materially executed:
  - [D:\code\MyAttention\services\api\runtime\phase_evidence.py](/D:/code/MyAttention/services/api/runtime/phase_evidence.py)
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_phase_evidence.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_phase_evidence.py)
  - narrow validation:
    - `2 passed, 1 warning`
  - current artifact scan:
    - `R1-D`: delegated = `coding, evolution`; fallback = `review, testing`
    - `R1-E`: delegated = `coding`; fallback = `review, testing, evolution`
    - `R1-F`: delegated = `coding`; fallback = `review, testing, evolution`
    - `R1-G`: delegated = `coding, testing`; fallback = `review, evolution`
  - current truthful judgment:
    - `R1-H1 = accept_with_changes`
  - durable result:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H1_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H1_RESULT_MILESTONE_2026-04-07.md)
  - controller review:
    - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-H1_EVIDENCE_RECOVERY_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-H1_EVIDENCE_RECOVERY_RESULT.md)
- controller fallback records now also exist for:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-H2_EVIDENCE_RECOVERY_REVIEW_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-H2_EVIDENCE_RECOVERY_REVIEW_FALLBACK.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-H3_EVIDENCE_RECOVERY_TEST_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-H3_EVIDENCE_RECOVERY_TEST_FALLBACK.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-H4_EVIDENCE_RECOVERY_EVOLUTION_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-H4_EVIDENCE_RECOVERY_EVOLUTION_FALLBACK.md)
- current recovery target order is now durably recorded at:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_TARGET_RECOVERY_ORDER_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_TARGET_RECOVERY_ORDER_2026-04-07.md)
- current phase status note now also exists:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_STATUS_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_STATUS_MILESTONE_2026-04-07.md)
- immediate next target is now durably fixed at:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_NEXT_TARGET_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_NEXT_TARGET_2026-04-07.md)
- the first `R1-H` recovery wave is now also recorded at:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_R1-G_RECOVERY_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_R1-G_RECOVERY_RESULT_2026-04-08.md)
- the second `R1-H` partial recovery wave is now also recorded at:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_R1-F_PARTIAL_RECOVERY_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_R1-F_PARTIAL_RECOVERY_RESULT_2026-04-08.md)
- the completed `R1-F` recovery wave is now also recorded at:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_R1-F_RECOVERY_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_R1-F_RECOVERY_RESULT_2026-04-08.md)
- current runtime phase evidence snapshot artifacts now also exist at:
  - [D:\code\MyAttention\.runtime\runtime-phase-evidence\runtime_phase_evidence_snapshot_2026-04-07.json](/D:/code/MyAttention/.runtime/runtime-phase-evidence/runtime_phase_evidence_snapshot_2026-04-07.json)
  - [D:\code\MyAttention\.runtime\runtime-phase-evidence\runtime_phase_evidence_snapshot_2026-04-07.md](/D:/code/MyAttention/.runtime/runtime-phase-evidence/runtime_phase_evidence_snapshot_2026-04-07.md)
  - [D:\code\MyAttention\.runtime\runtime-phase-evidence\runtime_phase_evidence_snapshot_2026-04-08.json](/D:/code/MyAttention/.runtime/runtime-phase-evidence/runtime_phase_evidence_snapshot_2026-04-08.json)
  - [D:\code\MyAttention\.runtime\runtime-phase-evidence\runtime_phase_evidence_snapshot_2026-04-08.md](/D:/code/MyAttention/.runtime/runtime-phase-evidence/runtime_phase_evidence_snapshot_2026-04-08.md)
- `R1-G` review-provenance hardening is now materially complete with
  independent delegated evidence:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-G_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-G_RESULT_MILESTONE_2026-04-07.md)
- next active runtime phase is now judged as:
  - `R1-H Independent Delegated Evidence Recovery`
- next-phase controller docs:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_PHASE_JUDGMENT_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_PHASE_JUDGMENT_2026-04-07.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_DELEGATED_EVIDENCE_RECOVERY_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_DELEGATED_EVIDENCE_RECOVERY_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-H1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-H1_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-H2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-H2_REVIEW_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-H3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-H3_TEST_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-H4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-H4_EVOLUTION_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_EXECUTION_PACK_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_EXECUTION_PACK_2026-04-07.md)
- `.runtime/delegation` entrypoints now also exist for:
  - `R1-H1` coding
  - `R1-H2` review
  - `R1-H3` testing
  - `R1-H4` evolution
- Active runtime phase remains `R1-G`, and `R1-G1` is now materially executed.
- `R1-G1` review-provenance hardening is now implemented in:
  - [D:\code\MyAttention\services\api\runtime\memory_packets.py](/D:/code/MyAttention/services/api/runtime/memory_packets.py)
  - [D:\code\MyAttention\services\api\runtime\operational_closure.py](/D:/code/MyAttention/services/api/runtime/operational_closure.py)
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_memory_packets.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_memory_packets.py)
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_operational_closure.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_operational_closure.py)
- proven narrow validation:
  - `3 passed, 48 deselected, 1 warning` for the review-provenance slice in
    `test_runtime_v0_memory_packets.py`
  - `2 passed, 8 deselected, 1 warning` for the DB-backed review-provenance
    slice in `test_runtime_v0_operational_closure.py`
  - `4 passed, 1 warning` for standalone `test_runtime_v0_project_surface.py`
- current truthful judgment:
  - `R1-G1 = accept_with_changes`
- durable result:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-G1_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-G1_RESULT_MILESTONE_2026-04-07.md)
- controller review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-G1_REVIEW_PROVENANCE_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-G1_REVIEW_PROVENANCE_RESULT.md)
- controller fallback records now also exist for:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-G2_REVIEW_PROVENANCE_REVIEW_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-G2_REVIEW_PROVENANCE_REVIEW_FALLBACK.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-G3_REVIEW_PROVENANCE_TEST_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-G3_REVIEW_PROVENANCE_TEST_FALLBACK.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-G4_REVIEW_PROVENANCE_EVOLUTION_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-G4_REVIEW_PROVENANCE_EVOLUTION_FALLBACK.md)
- phase-level truthful judgment:
  - `R1-G = materially complete with fallback review coverage`
- durable phase record:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-G_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-G_RESULT_MILESTONE_2026-04-07.md)
- the previously observed cross-suite DB-backed interaction is now resolved:
  - `services/api/tests/conftest.py` now also isolates
    `test_runtime_v0_project_surface.py`
  - combined `project_surface + operational_closure + memory_packets`
    validation now passes with:
    - `65 passed, 1 warning`
- Active runtime phase is now `R1-E`, not `R1-D`.
- `R1-D` operational-closure phase is now materially complete with fallback
  review coverage.
- `R1-E1` project-surface alignment is now materially executed:
  - [D:\code\MyAttention\services\api\runtime\operational_closure.py](/D:/code/MyAttention/services/api/runtime/operational_closure.py)
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_operational_closure.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_operational_closure.py)
  - narrow validation:
    - `8 passed, 1 warning`
  - combined truth-adjacent validation:
    - `97 passed, 1 warning`
  - current truthful judgment:
    - `R1-E1 = accept_with_changes`
  - durable result:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-E1_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-E1_RESULT_MILESTONE_2026-04-07.md)
  - controller review:
    - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-E1_PROJECT_SURFACE_ALIGNMENT_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-E1_PROJECT_SURFACE_ALIGNMENT_RESULT.md)
- `R1-E` phase record now also exists:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-E_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-E_RESULT_MILESTONE_2026-04-07.md)
- controller fallback records now exist for:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-E2_PROJECT_SURFACE_ALIGNMENT_REVIEW_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-E2_PROJECT_SURFACE_ALIGNMENT_REVIEW_FALLBACK.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-E3_PROJECT_SURFACE_ALIGNMENT_TEST_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-E3_PROJECT_SURFACE_ALIGNMENT_TEST_FALLBACK.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-E4_PROJECT_SURFACE_ALIGNMENT_EVOLUTION_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-E4_PROJECT_SURFACE_ALIGNMENT_EVOLUTION_FALLBACK.md)
- current phase-level truthful judgment:
  - `R1-E = materially complete with fallback review coverage`
- current `R1-E` phase focus remains narrow:
  - align `RuntimeProject.current_work_context_id`
  - preserve project-facing current-work visibility as runtime-derived truth
  - do not broaden into UI/API/runtime-surface expansion yet
- next active runtime phase is now judged as:
  - `R1-F Controller Runtime Read Surface`
- next-phase controller docs:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-F_PHASE_JUDGMENT_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-F_PHASE_JUDGMENT_2026-04-07.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-F_CONTROLLER_READ_SURFACE_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-F_CONTROLLER_READ_SURFACE_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-F1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-F1_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-F2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-F2_REVIEW_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-F3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-F3_TEST_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-F4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-F4_EVOLUTION_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-F_EXECUTION_PACK_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-F_EXECUTION_PACK_2026-04-07.md)
- `.runtime/delegation` entrypoints now also exist for:
  - `R1-F1` coding
  - `R1-F2` review
  - `R1-F3` testing
  - `R1-F4` evolution
- `R1-F1` controller read surface is now materially executed:
  - [D:\code\MyAttention\services\api\runtime\project_surface.py](/D:/code/MyAttention/services/api/runtime/project_surface.py)
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_project_surface.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_project_surface.py)
  - narrow validation:
    - `4 passed, 1 warning`
  - combined truth-adjacent validation:
    - `101 passed, 1 warning`
  - current truthful judgment:
    - `R1-F1 = accept_with_changes`
  - durable result:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-F1_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-F1_RESULT_MILESTONE_2026-04-07.md)
  - controller review:
    - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-F1_CONTROLLER_READ_SURFACE_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-F1_CONTROLLER_READ_SURFACE_RESULT.md)
- `R1-F` phase record now also exists:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-F_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-F_RESULT_MILESTONE_2026-04-07.md)
- controller fallback records now exist for:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-F2_CONTROLLER_READ_SURFACE_REVIEW_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-F2_CONTROLLER_READ_SURFACE_REVIEW_FALLBACK.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-F3_CONTROLLER_READ_SURFACE_TEST_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-F3_CONTROLLER_READ_SURFACE_TEST_FALLBACK.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-F4_CONTROLLER_READ_SURFACE_EVOLUTION_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-F4_CONTROLLER_READ_SURFACE_EVOLUTION_FALLBACK.md)
- current phase-level truthful judgment:
  - `R1-F = materially complete with fallback review coverage`
- next active runtime phase is now judged as:
  - `R1-G Review Provenance Hardening`
- next-phase controller docs:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-G_PHASE_JUDGMENT_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-G_PHASE_JUDGMENT_2026-04-07.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-G_REVIEW_PROVENANCE_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-G_REVIEW_PROVENANCE_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-G1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-G1_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-G2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-G2_REVIEW_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-G3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-G3_TEST_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-G4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-G4_EVOLUTION_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-G_EXECUTION_PACK_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-G_EXECUTION_PACK_2026-04-07.md)
- `.runtime/delegation` entrypoints now also exist for:
  - `R1-G1` coding
  - `R1-G2` review
  - `R1-G3` testing
  - `R1-G4` evolution
- `R1-C` truth-layer work is materially complete:
  - `R1-C6` DB-backed schema-foundation is green:
    - `53 passed, 1 warning`
  - `R1-C5` Postgres-backed claim verification is green:
    - `4 passed, 1 warning`
    - combined narrow DB-backed evidence:
      - `57 passed, 1 warning`
  - `R1-C7` removed the deprecated `allow_claim` compatibility surface from
    `runtime.state_machine.validate_transition`
  - claim-related runtime suites remain green:
    - `194 passed, 1 warning`
- Current runtime controller judgment:
  - do not continue reopening truth-layer semantics
  - open `R1-D Operational Closure Layer`
  - next proof should be:
    - runtime-backed `WorkContext` reconstruction
    - runtime-backed trusted `MemoryPacket` promotion
  - without introducing a second truth source
- `R1-D1` coding is now materially executed:
  - [D:\code\MyAttention\services\api\runtime\operational_closure.py](/D:/code/MyAttention/services/api/runtime/operational_closure.py)
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_operational_closure.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_operational_closure.py)
  - narrow DB-backed proof:
    - `5 passed, 1 warning`
  - combined closure/work-context/memory validation:
    - `94 passed, 1 warning`
  - current truthful judgment:
    - `R1-D1 = accept_with_changes`
  - controller review:
    - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-D1_OPERATIONAL_CLOSURE_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-D1_OPERATIONAL_CLOSURE_RESULT.md)
  - next natural actions:
    - `R1-D2`
    - `R1-D3`
    - `R1-D4`
  - controller fallback records now also exist for:
    - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-D2_OPERATIONAL_CLOSURE_REVIEW_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-D2_OPERATIONAL_CLOSURE_REVIEW_FALLBACK.md)
    - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-D3_OPERATIONAL_CLOSURE_TEST_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-D3_OPERATIONAL_CLOSURE_TEST_FALLBACK.md)
    - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-D4_OPERATIONAL_CLOSURE_EVOLUTION_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-D4_OPERATIONAL_CLOSURE_EVOLUTION_FALLBACK.md)
  - current phase completion note:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-D_PHASE_COMPLETION_NOTE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-D_PHASE_COMPLETION_NOTE_2026-04-07.md)
  - next active runtime phase is now judged as:
    - `R1-E Project Surface Alignment`
  - next-phase controller docs:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-E_PHASE_JUDGMENT_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-E_PHASE_JUDGMENT_2026-04-07.md)
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-E_PROJECT_SURFACE_ALIGNMENT_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-E_PROJECT_SURFACE_ALIGNMENT_PLAN.md)
  - current `R1-E` packet set now exists:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-E1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-E1_CODING_BRIEF.md)
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-E2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-E2_REVIEW_BRIEF.md)
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-E3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-E3_TEST_BRIEF.md)
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-E4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-E4_EVOLUTION_BRIEF.md)
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-E_EXECUTION_PACK_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-E_EXECUTION_PACK_2026-04-07.md)
- Current `R1-D` packet set now exists:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-D1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-D1_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-D2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-D2_REVIEW_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-D3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-D3_TEST_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-D4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-D4_EVOLUTION_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-D_EXECUTION_PACK_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-D_EXECUTION_PACK_2026-04-07.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-D1_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-D1_RESULT_MILESTONE_2026-04-07.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-D_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-D_RESULT_MILESTONE_2026-04-07.md)
- `R1-C1` has been materially executed and controller-corrected.
- Truthful `R1-C1` status:
  - `allow_claim=True` no longer grants executable access on CLAIM_REQUIRED transitions
  - `TransitionRequest` now carries `claim_context` instead of `allow_claim`
  - `leases.py` now contains a `ClaimVerifier` adapter boundary and `InMemoryClaimVerifier`
  - narrow runtime validation passed:
    - `256 passed` across:
      - `test_runtime_v0_state_machine.py`
      - `test_runtime_v0_task_state_semantics.py`
      - `test_runtime_v0_events_and_leases.py`
      - `test_runtime_v0_lifecycle_proof.py`
  - wider runtime sweep was partially blocked by existing DB test fixture/environment gaps:
    - `417 passed, 35 errors`
    - initial blocker was missing `db_session` fixture in schema-foundation DB tests
    - current blocker is now narrower and environment-level:
      - runtime DB pytest harness exists
      - local `MyAttentionPostgres` service is stopped
      - port `5432` is not reachable
      - DB-backed suite currently fails with `ConnectionRefusedError`, not fixture absence
- Current controller judgment:
  - `R1-C1 = accept_with_changes`
  - review/evolution results now also exist as durable payloads, even though the outer OpenClaw shell still timed out during recovery
  - next natural follow-up is not more truth-layer design
  - it is:
    - `R1-C6` is now complete as DB-backed schema-foundation truth:
      - local Postgres restored
      - runtime kernel migration applied to current DB
      - `test_runtime_v0_schema_foundation.py` now passes with:
        - `53 passed, 1 warning`
    - `R1-C5` is now also materially complete:
      - `services/api/runtime/postgres_claim_verifier.py` exists
      - explicit assignment now verifies through:
        - `runtime_tasks.owner_kind/owner_id`
      - active lease now verifies through:
        - `runtime_tasks.current_lease_id`
        - `runtime_worker_leases`
      - targeted DB-backed verifier suite passes with:
        - `4 passed, 1 warning`
      - combined narrow DB-backed runtime evidence passes with:
        - `57 passed, 1 warning`
    - next natural follow-up is no longer `R1-C5/R1-C6`
    - it is:
      - remove deprecated `allow_claim` from downstream call sites and then from the pure-logic API surface
    - current next-packet docs:
      - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-C7_ALLOW_CLAIM_REMOVAL_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-C7_ALLOW_CLAIM_REMOVAL_PLAN.md)
      - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-C7_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-C7_CODING_BRIEF.md)
    - `R1-C7` is now also materially complete:
      - deprecated `allow_claim` compatibility parameter removed from
        `runtime.state_machine.validate_transition`
      - claim-related runtime suites remain green:
        - `194 passed, 1 warning`
    - current runtime controller task is no longer another `R1-C` follow-up
    - it is to open the next runtime phase judgment from a stabilized
      truth-layer baseline
  - current single-file milestone:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-C_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-C_RESULT_MILESTONE_2026-04-07.md)
  - current diagnosis note:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-C5_C6_DIAGNOSIS_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-C5_C6_DIAGNOSIS_2026-04-07.md)
  - current assignment-truth options:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-C5_ASSIGNMENT_TRUTH_OPTIONS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-C5_ASSIGNMENT_TRUTH_OPTIONS.md)

## Mainline Goal

The current mainline is:

1. Improve `source intelligence` quality so the information flywheel produces usable attention objects.
2. Keep `evolution brain` on the mainline, but distinguish it from watchdog/rule-engine behavior.
3. Reduce token pressure by using controlled delegation for bounded coding/review/analysis tasks.
4. Reframe visible IKE validation around real-world benchmark cases, not just technical inspect pages.
5. Improve critical entity judgment and event capture so benchmark conclusions are not driven by generic search adjacency.
6. Define `IKE Runtime v0` as the minimal memory/task/decision control kernel needed for both OpenClaw runtime continuity and controller/delegate engineering continuity.
7. Strengthen the missing independent `testing` leg and independent `evolution` leg so development quality does not rely only on coding delegates plus controller review.
8. Start `IKE Runtime v0` second-wave with hardening and one real task lifecycle proof, not with broader platform expansion.
9. Run second-wave as an explicit multi-agent cycle: controller + coding + review + testing + evolution, not coding/review alone.

Do not open new broad architecture branches before these are stabilized.

Latest runtime second-wave status:

- `R1-A1` hardening has been executed and controller-reviewed as `accept_with_changes`.
- `R1-A2` Kimi review lane has been restored and is operational again after the reviewer-channel fix.
- `R1-A3` test lane is now real, not placeholder-only:
  - `36` state-machine tests passed
  - `49` memory-packet tests passed
  - `7` migration-validation-support tests passed
- `R1-A` now has a single-file result milestone for cross-model review:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-A_RESULT_MILESTONE_2026-04-06.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-A_RESULT_MILESTONE_2026-04-06.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_V0_R1-A_RESULT_MILESTONE_2026-04-06.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_V0_R1-A_RESULT_MILESTONE_2026-04-06.md)
- Remaining second-wave known soft spots are now independently tested residual risks, not unverified assumptions:
  - legacy `role=None` force-path softness
  - caller-supplied upstream verifier trust contract
- The next controller judgment is now explicit:
  - do not start `R1-B` yet
  - run one more narrow enforcement cycle first:
    - `R1-A5` coding
    - `R1-A6` review
    - `R1-A7` testing
    - `R1-A8` evolution
- Current execution status:
  - `R1-A5` coding was executed
  - first attempt was rejected:
    - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-A5_ENFORCEMENT_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-A5_ENFORCEMENT_RESULT.md)
  - narrow correction pass then succeeded with `accept_with_changes`:
    - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-A5_FIX_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-A5_FIX_RESULT.md)
  - current stable outcome:
    - legal claim path restored
    - `role=None` force bypass remains closed
    - migration-validation subset now passes under the controller invocation pattern
  - `R1-A6` review and `R1-A8` evolution have now also executed successfully via `openclaw-kimi`
  - current controller judgment:
    - `R1-B` is conditionally ready
    - no further narrow enforcement packet is required before beginning one real task lifecycle proof
    - but these are still preserved future items, not forgotten:
      - remove legacy `allow_claim=True`
      - move delegate identity verification into service/runtime truth layer
      - add live Postgres migration up/down proof
- `R1-B` has now been materialized as the next active mainline:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-B_LIFECYCLE_PROOF_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-B_LIFECYCLE_PROOF_PLAN.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-B1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-B1_CODING_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-B2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-B2_REVIEW_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-B3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-B3_TEST_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-B4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-B4_EVOLUTION_BRIEF.md)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r1-b1-lifecycle-proof-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r1-b1-lifecycle-proof-glm.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-B_EXECUTION_PACK_2026-04-06.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-B_EXECUTION_PACK_2026-04-06.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-B_RESULT_MILESTONE_2026-04-06.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-B_RESULT_MILESTONE_2026-04-06.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_V0_R1-B_RESULT_MILESTONE_2026-04-06.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_V0_R1-B_RESULT_MILESTONE_2026-04-06.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-B1_LIFECYCLE_PROOF_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-B1_LIFECYCLE_PROOF_RESULT.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-B2_LIFECYCLE_REVIEW_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-B2_LIFECYCLE_REVIEW_FALLBACK.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-B4_LIFECYCLE_EVOLUTION_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-B4_LIFECYCLE_EVOLUTION_FALLBACK.md)
- Current truthful `R1-B` execution status:
  - `R1-B1` coding has now produced a dedicated lifecycle-proof test artifact
  - controller-side live pytest validation passed across lifecycle/state/event suites
  - `R1-B3` testing evidence is now real, but controller-side
  - delegated review/evolution lanes timed out again in this pass
  - controller fallback review/evolution have been recorded so the milestone is durable
  - the active remaining gap is now delegated reviewer/evolution lane recovery, not lifecycle-proof absence

Benchmark reference:

- [D:\code\MyAttention\docs\IKE_REAL_WORLD_BENCHMARKS.md](/D:/code/MyAttention/docs/IKE_REAL_WORLD_BENCHMARKS.md)
- [D:\code\MyAttention\docs\IKE_ENTITY_DISCOVERY_AND_EVENT_CAPTURE_METHOD.md](/D:/code/MyAttention/docs/IKE_ENTITY_DISCOVERY_AND_EVENT_CAPTURE_METHOD.md)
- [D:\code\MyAttention\docs\IKE_CLAUDE_CODE_REFERENCE_PLAN.md](/D:/code/MyAttention/docs/IKE_CLAUDE_CODE_REFERENCE_PLAN.md)
- [D:\code\MyAttention\docs\IKE_CLAUDE_CODE_B1_MAPPING.md](/D:/code/MyAttention/docs/IKE_CLAUDE_CODE_B1_MAPPING.md)
- [D:\code\MyAttention\docs\IKE_CLAUDE_CODE_B2_MEMDIR_STUDY.md](/D:/code/MyAttention/docs/IKE_CLAUDE_CODE_B2_MEMDIR_STUDY.md)
- [D:\code\MyAttention\docs\IKE_CROSS_MODEL_REVIEW_MILESTONE_2026-04-03.md](/D:/code/MyAttention/docs/IKE_CROSS_MODEL_REVIEW_MILESTONE_2026-04-03.md)
- [D:\code\MyAttention\docs\IKE_CROSS_MODEL_REVIEW_PROMPT_2026-04-03.md](/D:/code/MyAttention/docs/IKE_CROSS_MODEL_REVIEW_PROMPT_2026-04-03.md)
- [D:\code\MyAttention\docs\PROJECT_AGENT_HARNESS_CONTRACT.md](/D:/code/MyAttention/docs/PROJECT_AGENT_HARNESS_CONTRACT.md)
- [D:\code\MyAttention\docs\PROJECT_DURABLE_RECORDING_AND_GIT_DISCIPLINE.md](/D:/code/MyAttention/docs/PROJECT_DURABLE_RECORDING_AND_GIT_DISCIPLINE.md)
- [D:\code\MyAttention\docs\IKE_ENTITY_JUDGMENT_STRENGTHENING_PLAN.md](/D:/code/MyAttention/docs/IKE_ENTITY_JUDGMENT_STRENGTHENING_PLAN.md)
- [D:\code\MyAttention\docs\IKE_SECOND_BENCHMARK_SELECTION_PLAN.md](/D:/code/MyAttention/docs/IKE_SECOND_BENCHMARK_SELECTION_PLAN.md)
- [D:\code\MyAttention\docs\IKE_B5_HARNESS_ENTITY_REVIEW_CONTROLLER_NOTE.md](/D:/code/MyAttention/docs/IKE_B5_HARNESS_ENTITY_REVIEW_CONTROLLER_NOTE.md)
- [D:\code\MyAttention\docs\IKE_SECOND_BENCHMARK_SHORTLIST.md](/D:/code/MyAttention/docs/IKE_SECOND_BENCHMARK_SHORTLIST.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_SUBPROJECT_DECISION.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_SUBPROJECT_DECISION.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md)
- [D:\code\MyAttention\docs\IKE_MAGMA_CHRONOS_MEMORY_RESEARCH_NOTE.md](/D:/code/MyAttention/docs/IKE_MAGMA_CHRONOS_MEMORY_RESEARCH_NOTE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_REVIEW_MILESTONE_2026-04-04.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_REVIEW_MILESTONE_2026-04-04.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_EVOLUTION_ROADMAP.md](/D:/code/MyAttention/docs/IKE_RUNTIME_EVOLUTION_ROADMAP.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_PACKETS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_PACKETS.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DELEGATION_BACKLOG.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DELEGATION_BACKLOG.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-A_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-A_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-B_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-B_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-C_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-C_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-D_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-D_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-E_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-E_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-F_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-F_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_FIRST_WAVE_PACKET_INDEX.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_FIRST_WAVE_PACKET_INDEX.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_EXECUTION_PACK_2026-04-05.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_EXECUTION_PACK_2026-04-05.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_V0_IMPLEMENTATION_EXECUTION_PACK_2026-04-05.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_V0_IMPLEMENTATION_EXECUTION_PACK_2026-04-05.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_FIRST_WAVE_RESULT_MILESTONE_2026-04-05.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_FIRST_WAVE_RESULT_MILESTONE_2026-04-05.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_V0_FIRST_WAVE_RESULT_MILESTONE_2026-04-05.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_V0_FIRST_WAVE_RESULT_MILESTONE_2026-04-05.md)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-a-core-schema-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-a-core-schema-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-a-core-schema-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-a-core-schema-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-a-core-schema-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-a-core-schema-glm.json)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-A_CORE_SCHEMA_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-A_CORE_SCHEMA_RESULT.md)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-b-task-state-semantics-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-b-task-state-semantics-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-b-task-state-semantics-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-b-task-state-semantics-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-b-task-state-semantics-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-b-task-state-semantics-glm.json)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-c-events-leases-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-c-events-leases-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-c-events-leases-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-c-events-leases-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-c-events-leases-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-c-events-leases-glm.json)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-d-work-context-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-d-work-context-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-d-work-context-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-d-work-context-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-d-work-context-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-d-work-context-glm.json)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-e-memory-packets-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-e-memory-packets-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-e-memory-packets-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-e-memory-packets-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-e-memory-packets-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-e-memory-packets-glm.json)
- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-f-redis-rebuild-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-f-redis-rebuild-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-f-redis-rebuild-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-f-redis-rebuild-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-f-redis-rebuild-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-f-redis-rebuild-glm.json)
- [D:\code\MyAttention\docs\IKE_LONG_HORIZON_BACKLOG_AND_DECISION_LOG.md](/D:/code/MyAttention/docs/IKE_LONG_HORIZON_BACKLOG_AND_DECISION_LOG.md)
- [D:\code\MyAttention\docs\IKE_THINKING_MODELS_AND_METHOD_ARMORY.md](/D:/code/MyAttention/docs/IKE_THINKING_MODELS_AND_METHOD_ARMORY.md)
- [D:\code\MyAttention\docs\B4 review result.md](/D:/code/MyAttention/docs/B4%20review%20result.md)
- [D:\code\MyAttention\docs\review-for IKE_RUNTIME_V0_REVIEW_MILESTONE_2026-04-04.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_V0_REVIEW_MILESTONE_2026-04-04.md)

## Operating Mode

Default mode:

- I act as the main controller.
- Implementation work should usually be delegated to qoder/openclaw or other bounded agents.
- I should primarily provide:
  - architecture framing
  - task decomposition
  - constraints
  - review
  - acceptance decisions

Exception mode:

- Direct code edits are allowed only when the user explicitly wants a fast, bounded corrective action or when delegation is unavailable.
- Even then, keep the patch narrow and preserve the mainline boundary.

## What Is Already True

### Runtime

- API/Web/Redis/Postgres/watchdog are running locally.
- Feed collection is automatic.
- Redis is now part of the feed cache path.

### Source Intelligence

- Discovery is no longer domain-only.
- Current object types include:
  - `domain`
  - `repository`
  - `person`
  - `organization`
  - `community`
  - `release`
  - `signal`
  - `event`
- `source-frontier-v1` is currently at policy version `6`.
- `source-method-v1` is currently at policy version `7`.

### Controlled Delegation

- `acpx + openclaw` file-based delegation works.
- Main control must remain local.
- Current routing:
  - `openclaw-glm` for coding-heavy delegation
  - `openclaw-qwen` for general execution
  - `openclaw-kimi` / reviewer for review and long-context analysis

## Important Corrections Already Made

These are not optional style preferences; they are mainline corrections.

### 1. Source value is contextual

Do not treat a source like `36kr` as globally good or globally bad.

Correct model:

- the same object/source can serve multiple topics
- the same object/source can serve multiple task intents
- value depends on `role in context`

Examples:

- `36kr` can be valid for `latest intelligence / industry signal`
- the same `36kr` item should not dominate `authoritative understanding`

### 2. Topic is not the only top-level axis

Avoid falling back to:

- `topic -> source`

Prefer thinking in:

- `object`
- `task intent`
- `role in context`
- `object relations`

### 3. Evolution brain is not the watchdog

Current system still contains too much watchdog/rule-engine logic.

Correct split:

- `watchdog/rule layer`: keepalive, thresholds, restart, simple checks
- `evolution layer`: model-assisted understanding, prioritization, diagnosis, policy adjustment, procedural improvement

## Current Mainline Problems

### P0. Source Intelligence Quality Is Still Not Good Enough

Status:

- direction is much better than before
- quality is still not at “research-grade”

Symptoms:

- generic search still influences candidate generation too much
- `person` is present but still weak relative to how a real researcher tracks people
- relationship structure is still shallow
- old plans/noisy plans dilute useful changes

### P0. Critical Entity Judgment Is Still Too Weak

Status:

- the benchmark shape is now visible and directionally useful
- the most important people, repositories, and organizations are still not reliably correct

Symptoms:

- generic discovery adjacency still pulls in nearby but non-defining entities
- authority and identity verification are still too weak
- structured summaries are not yet fully separated from primary technical artifacts
- major events are not yet captured through a repeatable multi-signal method
- entity tiers still need stronger tier reasons and authority grounding
- current benchmark success is still concentrated on one visible concept case
- current truthful baseline is that `harness` still has no justified
  `concept_defining` entity

### P0. Claude Code Strategic Reference Is Not Yet Turned Into Reusable Method

Status:

- local primary artifact is available
- first-pass mapping is now in place
- no bounded reusable pattern has been carried through to IKE yet

Next focus:

- `memdir` study first
- then a procedural-memory prototype plan
- then a minimal procedural-memory prototype
- then a closure-adapter bridge into existing IKE completion artifacts
- then benchmark-study-closure as the first truthful payload source
- then permission/coordinator packets

### P0. Evolution Brain Does Not Yet Detect “Workspace Usability” Well

Status:

- it detects runtime/quality issues
- it does **not** yet reliably detect:
  - noisy task surfaces
  - stale/irrelevant historical tasks
  - garbled titles / dirty data
  - “page is technically up but operationally confusing”

### P0. Task Surface Is Not Clean Enough

Current issues:

- repeated historical `source-plan` quality tasks
- old pending/failed tasks still mixed with active ones
- some titles/descriptions remain garbled
- `settings/sources` does not yet make the active improvements obvious enough

## Most Recent Effective Changes

### Source Role-in-Context Changes

The current code now does all of the following:

- normalizes media subdomains like `m.36kr.com` and `eu.36kr.com` into `36kr.com`
- treats contextual tech media differently by focus:
  - `latest` -> positive signal role
  - `frontier` -> weaker signal role
  - `method` -> weaker still
- classifies contextual tech media as `signal` instead of `authority` in `frontier/latest`

Files:

- `D:\\code\\MyAttention\\services\\api\\routers\\feeds.py`
- `D:\\code\\MyAttention\\services\\api\\attention\\policies.py`
- `D:\\code\\MyAttention\\services\\api\\tests\\test_source_discovery_identity.py`
- `D:\\code\\MyAttention\\services\\api\\tests\\test_attention_policy_foundation.py`

### Live Impact Confirmed

For `openclaw + frontier`, the current live portfolio now looks closer to:

- `person/community`
- `signal`
- `implementation`

instead of letting a tech media domain sit in the `authority` bucket.

## What To Do Next

### 0. Absorb The B4 Cross-Model Review Result

The latest cross-model review reinforced, not overturned, the current mainline.

Most important accepted takeaways:

- project goal and controller/delegate method remain sound
- critical entity judgment is still the main upstream quality risk
- benchmark shape is ahead of evidence quality
- procedural memory is truthful but still only candidate-level
- a second semantically different benchmark will be needed to test method generalization

### 0.5 Absorb The First B5 Harness Entity Review

Current accepted conclusion:

- there is still no justified `concept_defining` entity in the current harness benchmark
- strongest implementation object:
  - `slowmist/openclaw-security-practice-guide`
- strongest ecosystem object:
  - `LeoYeAI/openclaw-master-skills`

This should remain the truthful baseline until stronger evidence appears.

### 1. Clean the Active Work Surface

Do this before adding more discovery complexity.

Tasks:

- separate active issues from historical task instances
- archive or demote obviously stale legacy issues
- sanitize garbled task/source-plan titles
- make `settings/sources` default to active/recently-updated plans only

Acceptance:

- a user can open the task surface and immediately tell:
  - what is currently wrong
  - what is historical noise
  - which source plans are active and worth reviewing

### 2. Strengthen Person-Centered Discovery

Current `person` support is still not enough.

Tasks:

- improve active discovery of:
  - maintainers
  - researchers
  - speakers
  - lead authors
  - core contributors
- strengthen relation hints:
  - `person -> repo`
  - `person -> organization`
  - `person -> topic`
  - `person -> release/signal`

Acceptance:

- `person` candidates appear as first-class attention objects for `method` and `frontier`
- a relevant maintainer/researcher can outrank generic domain noise

### 3. Make Evolution Brain Judge the Workspace, Not Just Runtime

Tasks:

- add issue hygiene checks
- add work-surface usability checks
- promote “active surface prioritization” into evolution outputs

Acceptance:

- evolution can flag:
  - stale noisy task surfaces
  - garbled/dirty titles
  - source-plan views dominated by historical noise

### 4. Use Real-World Benchmark Cases For Visible Validation

The current pure inspect-style IKE page was not user-comprehensible enough.

Next visible IKE work should be judged against a benchmark like:

- harness / openclaw / AI-agent trend detection and project relevance

Acceptance:

- the visible output explains:
  - what changed
  - which entities matter
  - what the concept means
  - why it matters to this project
  - what next action should follow

### 5. Treat B1 As Real But Partial Success

Current benchmark progress:

- B1 now works as a real benchmark report
- B4 evidence layering now works as a benchmark-method upgrade
- the first real `study_result -> decision_handoff` closure now exists for
  `harness`
- current truthful state for `harness` is:
  - recommendation level: `study`
  - applicability: `partially_applicable`
  - decision handoff: `continue_study`
- the next benchmark-method step is not a new concept:
  - it is `B5 continued study`
  - focused on concept-definition quality and applicability tightening
- `B5` already produced one important correction:
  - `LeoYeAI/openclaw-master-skills` should be treated as
    `ecosystem_relevant`
  - not `implementation_relevant`
  - because it behaves like a curated skill catalog/distribution surface, not
    an evaluation-method repository
- but B1 should be treated as:
  - `signal + meaning + relevance hint`
- not yet as:
  - full research trigger
  - full evolution action engine

Do not keep polishing B1 ranking forever.

The next benchmark mainline is:

- [D:\code\MyAttention\docs\IKE_B2_CONCEPT_TRIGGER_PLAN.md](/D:/code/MyAttention/docs/IKE_B2_CONCEPT_TRIGGER_PLAN.md)

The next priority is:

- concept deepening
- entity tiering
- explicit mainline gap mapping
- bounded research/prototype trigger

The benchmark has now advanced further:

- B2 now produces:
  - entity tiers
  - narrowed gap mapping
  - recommendation level
  - bounded study trigger packet

The next benchmark mainline is:

- [D:\code\MyAttention\docs\IKE_B3_DEEPENING_PLAN.md](/D:/code/MyAttention/docs/IKE_B3_DEEPENING_PLAN.md)
- [D:\code\MyAttention\docs\IKE_TASK_CLOSURE_PLAN.md](/D:/code/MyAttention/docs/IKE_TASK_CLOSURE_PLAN.md)

The next benchmark-method mainline is:

- [D:\code\MyAttention\docs\IKE_B4_EVIDENCE_LAYER_PLAN.md](/D:/code/MyAttention/docs/IKE_B4_EVIDENCE_LAYER_PLAN.md)

Reason:

- current benchmark structure is now useful
- current benchmark evidence quality is still too exposed to generic discovery bias
- the next upgrade is explicit evidence-layer separation before stronger ranking or adoption decisions

## Delegation Guidance

Use delegation aggressively for bounded tasks.

Good delegation tasks:

- code review / challenge
- source quality analysis
- bounded frontend cleanup
- candidate generation experiments
- test additions

Do not delegate:

- top-level architecture control
- mainline priority changes
- acceptance / merge decisions
- source-intelligence strategy corrections

## Commands / Validation Patterns

Useful validation commands:

```powershell
python manage.py health --json
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/api/sources/discover' -ContentType 'application/json' -Body (@{ topic = 'openclaw'; focus = 'frontier'; limit = 8 } | ConvertTo-Json)
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/evolution/tasks?page=1&page_size=20'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/sources/plans'
```

Relevant tests:

```powershell
D:\code\MyAttention\.venv\Scripts\python.exe -m unittest tests.test_source_discovery_identity tests.test_attention_policy_foundation
```

## Final Warning

Do not mistake “more object types” for “quality solved”.

The mainline is still blocked by:

- active-surface clarity
- person-centered discovery quality
- model-assisted evolution reasoning replacing pure rule/watchdog thinking
## 2026-04-05 Runtime Update

- `IKE Runtime v0` `R0-A` has now been executed through the delegate channel and controller-reviewed.
- Current verdict: `accept_with_changes`
- Durable result review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-A_CORE_SCHEMA_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-A_CORE_SCHEMA_RESULT.md)

- `IKE Runtime v0` `R0-B` has also been executed through the delegate channel, corrected via a narrow fix packet, and controller-reviewed.
- Current verdict: `accept_with_changes`
- Durable result review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-B_TASK_STATE_SEMANTICS_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-B_TASK_STATE_SEMANTICS_RESULT.md)

Important runtime notes:

- `R0-A` currently covers the 9-table first-wave kernel surface defined by the active brief.
- `runtime_task_relations` remains deferred and preserved as a future runtime object candidate.
- Live PostgreSQL migration execution is still not confirmed in-controller because the current `.venv` lacks `pytest`; this remains a hardening follow-up, not a design reversal.
- `R0-B` is now acceptable as baseline after fix, but still carries two hardening notes:
  - `allow_claim` remains caller-asserted rather than object-backed
  - `force=True` on waiting updates must remain tightly controlled

- `IKE Runtime v0` `R0-C` has been executed through the delegate channel and controller-reviewed.
- Current verdict: `accept_with_changes`
- Durable result review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-C_EVENTS_LEASES_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-C_EVENTS_LEASES_RESULT.md)

Current `R0-C` note:

- event/lease/recovery semantics are now in place as baseline
- append-only discipline is still stronger at API contract level than at sealed in-memory structure level

- `IKE Runtime v0` `R0-D` has been executed through the delegate channel and controller-reviewed.
- Current verdict: `accept_with_changes`
- Durable result review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-D_WORK_CONTEXT_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-D_WORK_CONTEXT_RESULT.md)

Current `R0-D` note:

- `WorkContext` is now acceptable as derived snapshot carrier
- one-active-context enforcement still primarily depends on DB-level uniqueness plus caller discipline

- `IKE Runtime v0` `R0-E` has been executed through the delegate channel and controller-reviewed.
- Current verdict: `accept_with_changes`
- Durable result review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-E_MEMORY_PACKET_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-E_MEMORY_PACKET_RESULT.md)

Current `R0-E` note:

- packet lifecycle and trust boundary are now acceptable as v0 baseline
- explicit upstream linkage is now required for acceptance and trusted recall
- stronger linkage queryability and DB-backed upstream verification remain future hardening work
- fixed delegate result:
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-e-fix-memory-packets-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-e-fix-memory-packets-glm.json)

- `IKE Runtime v0` `R0-F` has been executed through the delegate channel and controller-reviewed.
- Current verdict: `accept_with_changes`
- Durable result review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-F_REDIS_REBUILD_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-F_REDIS_REBUILD_RESULT.md)

Current `R0-F` note:

- Redis acceleration/rebuild is now acceptable as a command-builder baseline
- Postgres remains truth and Redis loss degrades performance rather than durable state
- real execution adapter, observability, and tighter incremental sync discipline remain future hardening work

## 2026-04-06 Runtime Second-Wave Entry

- `R1-A` is now defined as a multi-agent hardening cycle:
  - coding
  - review
  - testing
  - evolution
- Current multi-agent cycle files:
  - [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r1-a1-hardening-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r1-a1-hardening-glm.md)
  - [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r1-a1-hardening-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r1-a1-hardening-glm.md)
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-a1-hardening-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-a1-hardening-glm.json)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-A1_HARDENING_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-A1_HARDENING_RESULT.md)
  - [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r1-a2-hardening-review-kimi.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r1-a2-hardening-review-kimi.md)
  - [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r1-a2-hardening-review-kimi.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r1-a2-hardening-review-kimi.md)
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-a2-hardening-review-kimi.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-a2-hardening-review-kimi.json)
  - [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r1-a3-hardening-test.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r1-a3-hardening-test.md)
  - [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r1-a3-hardening-test.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r1-a3-hardening-test.md)
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-a3-hardening-test.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-a3-hardening-test.json)
  - [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r1-a4-hardening-evolution-kimi.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r1-a4-hardening-evolution-kimi.md)
  - [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r1-a4-hardening-evolution-kimi.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r1-a4-hardening-evolution-kimi.md)
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-a4-hardening-evolution-kimi.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-a4-hardening-evolution-kimi.json)

Current `R1-A1` note:

- delegate execution completed
- controller verdict is currently `accept_with_changes`
- core improvement is real, but two soft spots remain:
  - `role=None` still leaves a legacy force-path softness
  - upstream truth still depends on a caller-supplied verifier callback

Current `R1-A2` note:

- `openclaw-kimi` session timed out
- result file remained template-only
- usable review currently comes from controller review, not delegate review
## 2026-04-06 Kimi Channel Recovery

- `openclaw-kimi` reviewer/evolution channel recovered
- root cause:
  - reviewer agents in `C:\Users\jiuyou\.openclaw\openclaw.json`
  - were pinned to `bailian-coding-plan/kimi-k2.5`
  - that route returned `401 Incorrect API key provided`
- fixed by switching:
  - `myattention-reviewer`
  - `myattention-kimi-review`
  to:
  - `modelstudio/kimi-k2.5`
- reviewer main session reset after model-route fix
- real delegated packets now working again:
  - `R1-A2` review
  - `R1-A4` evolution
- reference:
  - `D:\code\MyAttention\docs\OPENCLAW_KIMI_CHANNEL_FIX_2026-04-06.md`
## 2026-04-06 OpenClaw Alias Cleanup

- `.acpxrc.json` alias layer cleaned up
- canonical usage now:
  - `openclaw-coder`
  - `openclaw-glm`
  - `openclaw-kimi`
  - `openclaw-kimi-review`
  - `openclaw-reviewer`
- `openclaw-qwen` retained only as legacy compatibility alias
- `openclaw-kimi` now routes to:
  - `agent:myattention-kimi-review:main`
- `openclaw-reviewer` remains:
  - `agent:myattention-reviewer:main`
- backup profiles now standardized on:
  - `bailian/qwen3.6-plus`
  for:
  - `myattention-coder`
  - `myattention-reviewer`
- reference:
  - `D:\code\MyAttention\docs\OPENCLAW_AGENT_ALIAS_MAP_2026-04-06.md`

## 2026-04-07 Review/Evolution Lane Recovery

- reviewer/evolution transport root cause was narrowed to local OpenClaw route
  drift, not packet semantics
- actual bad state was:
  - `myattention-kimi-review -> bailian-coding-plan/kimi-k2.5`
  - `myattention-reviewer -> bailian-coding-plan/kimi-k2.5`
  - both polluted by stale `authProfileOverride = bailian-coding-plan:default`
- corrected live local split is now:
  - `myattention-kimi-review -> modelstudio/kimi-k2.5`
  - `myattention-reviewer -> bailian/qwen3.6-plus`
- both lanes passed minimal `OK` probes after correction
- `R1-B2` and `R1-B4` were then rerun and recovered as real delegated results
- reference:
  - `D:\code\MyAttention\docs\OPENCLAW_REVIEW_EVOLUTION_ROUTE_RECOVERY_2026-04-07.md`

## 2026-04-07 R1-B Lifecycle Milestone Truth

- `R1-B1` coding proof is real:
  - dedicated proof file exists at:
    - `D:\code\MyAttention\services\api\tests\test_runtime_v0_lifecycle_proof.py`
- `R1-B3` testing is real:
  - controller live validation passed at `201` runtime tests
- `R1-B2` review is now a real delegated result, not fallback-only
- `R1-B4` evolution is now a real delegated result, not fallback-only
- current truthful judgment:
  - `R1-B` = `accept_with_changes`
- remaining change is substantive:
  - remove legacy `allow_claim=True` path once truth-layer verification is
    runtime-native

## 2026-04-07 R1-C Activation

- `R1-B` is no longer waiting on transport recovery
- the next active runtime mainline is now:
  - `R1-C` truth-layer integration
- reference:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-C_TRUTH_LAYER_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-C_TRUTH_LAYER_PLAN.md)
- first packet set:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-C1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-C1_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-C2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-C2_REVIEW_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-C3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-C3_TEST_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R1-C4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R1-C4_EVOLUTION_BRIEF.md)
- controller judgment:
  - do not open broader kernel integration yet
  - first remove executable legacy claim softness and move delegate claim truth
    into runtime-owned verification

## 2026-04-07 R1-C Execution Materialized

- `R1-C` is now no longer only a docs-level phase plan
- `.runtime/delegation` execution entrypoints now exist for all four legs:
  - `R1-C1` coding
  - `R1-C2` review
  - `R1-C3` testing
  - `R1-C4` evolution
- single-file execution pack added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-C_EXECUTION_PACK_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-C_EXECUTION_PACK_2026-04-07.md)
- current truthful state:
  - `R1-C` has durable execution entrypoints
  - it has not yet produced coding/review/test/evolution results
  - next natural action is executing `R1-C1`, not further planning expansion

## 2026-04-07 R1-C6 Narrow Runtime Truth Update

- repository-level pytest fixture now exists at:
  - [D:\code\MyAttention\services\api\tests\conftest.py](/D:/code/MyAttention/services/api/tests/conftest.py)
- this removes the original `db_session` fixture absence as the primary blocker
- controller-side targeted rerun now shows the next truthful blocker:
  - `MyAttentionPostgres` service is stopped
  - `localhost:5432` is unreachable
  - DB-backed runtime schema tests fail with:
    - `ConnectionRefusedError: [WinError 1225]`
- current controller interpretation:
  - `R1-C6` is partially completed at the test-harness layer
  - remaining blocker is environment/service restoration, not runtime semantics

## 2026-04-08 R2-B1 Real Task Lifecycle Proof Recovered

- local system runtime is currently back up:
  - web `127.0.0.1:3000` reachable
  - API `127.0.0.1:8000/health` returns healthy
- `R2-B1` coding now has a durable controller-recovered result:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B1_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R2-B1_REAL_TASK_LIFECYCLE_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R2-B1_REAL_TASK_LIFECYCLE_RESULT.md)
- comparison note added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B1_CODING_COMPARISON_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B1_CODING_COMPARISON_2026-04-08.md)
- truthful controller judgment:
  - `R2-B1 = accept_with_changes`
- current interpretation:
  - the local Claude worker found the right narrow patch shape
  - but the run did not emit a final durable artifact in time
  - acceptance therefore comes from controller-side diff review plus focused validation
- validated commands:
  - `python -m pytest services/api/tests/test_runtime_v0_lifecycle_proof.py -q`
  - `python -m pytest services/api/tests/test_runtime_v0_lifecycle_proof.py services/api/tests/test_runtime_v0_events_and_leases.py services/api/tests/test_runtime_v0_task_state_semantics.py -q`

## 2026-04-08 R2-B Testing Evidence Materialized

- `R2-B3` now has durable focused testing evidence:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B3_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B3_RESULT_MILESTONE_2026-04-08.md)
- exact focused validation result:
  - `214 passed, 1 warning`
- `R2-B` phase status is now explicitly recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B_STATUS_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B_STATUS_MILESTONE_2026-04-08.md)
- truthful current state:
  - `R2-B1` coding = controller-recovered and accepted with changes
  - `R2-B3` testing = controller-evidenced and accepted with changes
  - `R2-B2` review = still running in local Claude review lane
  - `R2-B4` evolution = not yet materially executed

## 2026-04-08 R2-B Lifecycle Subtrack Closed

- the lifecycle-proof subtrack inside `R2-B` now has a durable consolidated result:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B_LIFECYCLE_SUBTRACK_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B_LIFECYCLE_SUBTRACK_RESULT_2026-04-08.md)
- `R2-B2` is truthfully recorded as controller fallback review:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R2-B2_REAL_TASK_LIFECYCLE_REVIEW_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R2-B2_REAL_TASK_LIFECYCLE_REVIEW_FALLBACK.md)
- `R2-B4` has a real evolution result milestone:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md)
- truthful interpretation:
  - lifecycle proof subtrack is materially complete
  - `R2-B` itself is still not complete
  - next target is now:
    - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B_NEXT_TARGET_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B_NEXT_TARGET_2026-04-08.md)
    - kernel-to-benchmark bridge proof

## 2026-04-08 R2-B Bridge Proof Materialized

- the remaining open proving step inside `R2-B` now has a durable plan:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B_BRIDGE_PROOF_PLAN_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B_BRIDGE_PROOF_PLAN_2026-04-08.md)
- packet set created:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-B5_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-B5_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-B6_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-B6_REVIEW_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-B7_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-B7_TEST_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-B8_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-B8_EVOLUTION_BRIEF.md)
- single-file execution entry:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B_BRIDGE_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B_BRIDGE_EXECUTION_PACK_2026-04-08.md)
- `.runtime/delegation` entrypoints now exist for:
  - `R2-B5` coding
  - `R2-B6` review
  - `R2-B7` testing
  - `R2-B8` evolution

## 2026-04-08 R2-B5 Bridge Proof Executed

- `R2-B5` coding now has a durable result:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B5_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B5_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R2-B5_BRIDGE_PROOF_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R2-B5_BRIDGE_PROOF_RESULT.md)
- narrow bridge proof implemented at:
  - [D:\code\MyAttention\services\api\runtime\benchmark_bridge.py](/D:/code/MyAttention/services/api/runtime/benchmark_bridge.py)
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_benchmark_bridge.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_benchmark_bridge.py)
- truthful judgment:
  - `R2-B5 = accept_with_changes`
- proof established:
  - reviewed benchmark candidate -> runtime `pending_review` packet
  - no auto-promotion to trusted memory
  - no new runtime object family
  - no regression in closure/project-surface/memory-packet combined slice
- validation:
  - bridge slice = `7 passed, 1 warning`
  - combined slice = `87 passed, 1 warning`
- current next target:
  - `R2-B6` delegated review

## 2026-04-08 R2-B7 Bridge Validation Materialized

- `R2-B7` now has durable testing evidence:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B7_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B7_RESULT_MILESTONE_2026-04-08.md)
- validation results:
  - bridge slice = `7 passed, 1 warning`
  - combined slice = `87 passed, 1 warning`
- truthful judgment:
  - `R2-B7 = accept_with_changes`
- remaining `R2-B` open lanes are now:
  - `R2-B6` review
  - `R2-B8` evolution

## 2026-04-08 R2-B8 Bridge Evolution Materialized

- `R2-B8` now has a durable evolution result:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B8_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B8_RESULT_MILESTONE_2026-04-08.md)
- durable runtime method guidance now absorbs:
  - reviewed benchmark candidate -> runtime `pending_review` packet
  - no direct benchmark -> trusted runtime memory promotion
  - runtime acceptance remains the only trust gate
- truthful judgment:
  - `R2-B8 = accept_with_changes`
- current remaining open `R2-B` lane:
  - `R2-B6` review

## 2026-04-08 R2-B6 Review Materialized

- `R2-B6` now has an independent delegated review result:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B6_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B6_RESULT_MILESTONE_2026-04-08.md)
- truthful judgment:
  - `R2-B6 = accept_with_changes`
- no severity-level findings were identified
- preserved risks remain narrow:
  - packet-metadata provenance is not append-only event provenance
  - malformed benchmark negative-path coverage can still improve

## 2026-04-08 R2-B Closed

- `R2-B` now has a durable consolidated result:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B_RESULT_MILESTONE_2026-04-08.md)
- truthful controller judgment:
  - `R2-B = accept_with_changes`
- `R2-B` is materially complete and sufficient to open the next narrow phase
- next active phase is now:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-C_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-C_PHASE_JUDGMENT_2026-04-08.md)
