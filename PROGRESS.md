# MyAttention 项目工作进度

## 2026-04-08 - Runtime R2-G1 service-discipline evidence and methodology PDF study packet

- added a durable `R2-G1` operational diagnosis:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G1_SERVICE_DISCIPLINE_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G1_SERVICE_DISCIPLINE_RESULT_2026-04-08.md)
- current truthful service result:
  - `GET /health` is currently healthy
  - the real gap is ambiguous local service ownership caused by duplicate
    `run_service.py` launchers across repo `.venv` and system Python
- fixed the controller baseline for live proof:
  - treat repo `.venv` + explicit `services/api/run_service.py` launch as the
    truthful service path
- prepared and launched a separate local-Claude methodology study packet over:
  - [D:\BaiduNetdiskDownload\万维钢·现代思维工具100讲\PDF](/D:/BaiduNetdiskDownload/%E4%B8%87%E7%BB%B4%E9%92%A2%C2%B7%E7%8E%B0%E4%BB%A3%E6%80%9D%E7%BB%B4%E5%B7%A5%E5%85%B7100%E8%AE%B2/PDF)
- extraction bundle added:
  - [D:\code\MyAttention\.runtime\methodology-pdf-study\stable_manifest.json](/D:/code/MyAttention/.runtime/methodology-pdf-study/stable_manifest.json)
  - [D:\code\MyAttention\.runtime\methodology-pdf-study\stable_texts](/D:/code/MyAttention/.runtime/methodology-pdf-study/stable_texts)
- active delegated run:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T152547-126e6d2a](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T152547-126e6d2a)
- because the full-corpus run did not quickly finalize, added a narrow batch recovery plan:
  - [D:\code\MyAttention\docs\IKE_THINKING_ARMORY_PDF_BATCH_PLAN_2026-04-08.md](/D:/code/MyAttention/docs/IKE_THINKING_ARMORY_PDF_BATCH_PLAN_2026-04-08.md)
- active batch delegated runs:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T155231-cb5e2538](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T155231-cb5e2538)
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T155231-4999aa1d](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T155231-4999aa1d)
- materialized the next narrow runtime packet:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-G2_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-G2_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G_EXECUTION_PACK_2026-04-08.md)
- active delegated coding run for `R2-G2`:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T153652-948b3f83](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T153652-948b3f83)
- controller validation for `R2-G2` is now durably recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G2_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G2_RESULT_MILESTONE_2026-04-08.md)
  - `39 passed, 1 warning`
  - live preflight currently reports `ready`
  - but the current single owner is still system `Python312`, not repo `.venv`
  - fresh repo `.venv` `uvicorn` on `8011` proved the new inspect route is live
  - preferred-owner mismatch is now machine-readable instead of implicit
- detached completion evidence is now explicitly recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G3_DETACHED_COMPLETION_NOTE_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G3_DETACHED_COMPLETION_NOTE_2026-04-09.md)
  - current truthful result:
    - local Claude runs remain useful
    - but detached completion is still not routine-hardened

## 2026-04-08 - Runtime R2-C1 narrow visible-surface proof landed

- completed the first narrow runtime-to-visible-surface proof:
  - runtime-backed project/work surface helper
  - narrow API read surface
  - settings-page runtime panel integration
- current truthful result:
  - `R2-C1 = accept_with_changes`
- controller validation passed:
  - targeted runtime-visible slice:
    - `34 passed, 28 warnings, 9 subtests passed`
  - combined DB-backed slice:
    - `89 passed, 1 warning`
- included one narrow DB-backed test-helper correction during landing:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_operational_closure.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_operational_closure.py)
    now re-reads the persisted runtime project row before reuse
- durable result added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-C1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-C1_RESULT_MILESTONE_2026-04-08.md)

## 2026-04-08 - Runtime R2-C materially complete and R2-D opened

- phase-level result now recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-C_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-C_RESULT_MILESTONE_2026-04-08.md)
- current truthful judgment:
  - `R2-C = materially complete with fallback review coverage`
- accepted next runtime phase:
  - `R2-D Runtime Project Bootstrap Alignment`
- next real gap is no longer visible-surface shape, but live runtime project
  presence in the active DB
- durable next-phase docs added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-D_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-D_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-D_PROJECT_BOOTSTRAP_PLAN_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-D_PROJECT_BOOTSTRAP_PLAN_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-D_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-D_EXECUTION_PACK_2026-04-08.md)

## 2026-04-08 - Runtime R2-D1 explicit bootstrap proof landed

- completed the first narrow runtime project bootstrap proof:
  - explicit runtime-project bootstrap helper
  - narrow bootstrap API route
  - live bootstrap + inspect proof for:
    - `myattention-runtime-mainline`
- current truthful result:
  - `R2-D1 = accept_with_changes`
- controller validation passed:
  - targeted backend slice:
    - `30 passed, 28 warnings, 9 subtests passed`
  - live proof:
    - `GET /health` healthy
    - bootstrap route returned `200`
    - inspect route returned the bootstrapped runtime project surface
- durable result added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-D1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-D1_RESULT_MILESTONE_2026-04-08.md)

## 2026-04-08 - Runtime R2-D materially complete and R2-E opened

- phase-level result now recorded:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-D_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-D_RESULT_MILESTONE_2026-04-08.md)
- current truthful judgment:
  - `R2-D = materially complete with mixed delegated/controller evidence`
- accepted next runtime phase:
  - `R2-E Runtime Surface Activation Narrow Integration`
- next real gap is no longer runtime project presence itself, but direct
  settings-surface usability for the explicit bootstrap path
- durable next-phase docs added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-E_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-E_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-E_SURFACE_ACTIVATION_PLAN_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-E_SURFACE_ACTIVATION_PLAN_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-E_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-E_EXECUTION_PACK_2026-04-08.md)

## 2026-04-08 - Runtime R2-E explicit settings-surface activation proof landed

- completed the first narrow runtime-surface activation proof:
  - explicit activation button in the runtime-unavailable settings surface
  - explicit bootstrap API call from the visible surface
  - no automatic bootstrap on page load
- current truthful result:
  - `R2-E1 = accept_with_changes`
- controller validation passed:
  - `npx tsc --noEmit`
  - `GET /health` healthy
  - bootstrap route returned `200`
  - inspect route returned the bootstrapped runtime project surface
- durable records added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-E1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-E1_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-E_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-E_RESULT_MILESTONE_2026-04-08.md)

## 2026-04-08 - Runtime R2-F visible benchmark queue bridge landed

- completed the next narrow visible/runtime step after `R2-E`:
  - explicit benchmark-candidate import route
  - explicit settings-surface action to send the current reviewed benchmark candidate into runtime review
- current truthful result:
  - `R2-F1 = accept_with_changes`
- controller validation passed:
  - benchmark-bridge + router slice:
    - `31 passed, 28 warnings, 9 subtests passed`
  - `npx tsc --noEmit`
- truthful boundary preserved:
  - imported benchmark candidates become `pending_review` runtime packets only
  - they do not auto-promote to trusted memory
- durable records added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-F1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-F1_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-F_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-F_RESULT_MILESTONE_2026-04-08.md)

## 2026-04-08 - Runtime R2-G opened around service stability and delegated closure

- accepted the next narrow runtime phase after `R2-F`:
  - `R2-G Runtime Service Stability And Delegated Closure Hardening`
- current truthful reason:
  - runtime truth and visible/runtime bridges are now materially real
  - the next real blockers are operational:
    - local API process instability during live proof
    - incomplete delegated final artifacts in Claude worker runs
- durable next-phase docs added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-G_SERVICE_STABILITY_PLAN_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-G_SERVICE_STABILITY_PLAN_2026-04-08.md)
- also added durable lane-quality records:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_OPENCLAW_VS_CLAUDE_CODING_BASELINE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_OPENCLAW_VS_CLAUDE_CODING_BASELINE_2026-04-08.md)
  - [D:\code\MyAttention\docs\CLAUDE_WORKER_RUNTIME_HARDENING_REQUIREMENTS_2026-04-08.md](/D:/code/MyAttention/docs/CLAUDE_WORKER_RUNTIME_HARDENING_REQUIREMENTS_2026-04-08.md)

## 2026-04-08 - Runtime R1-J phase opened after R1-I

- accepted the next narrow runtime phase after materially complete `R1-I`:
  - `R1-J DB-backed Runtime Test Stability Hardening`
- fixed the next remaining runtime gap as:
  - DB-backed proof repeatability
  - fixture/setup isolation
  - FK-ordering determinism
  rather than new runtime-truth semantics
- durable phase docs added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J_DB_TEST_STABILITY_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J_DB_TEST_STABILITY_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J_EXECUTION_PACK_2026-04-08.md)
- packet/docs/results entrypoints now exist for:
  - `R1-J1` coding
  - `R1-J2` review
  - `R1-J3` testing
  - `R1-J4` evolution
- current controller judgment:
  - next work should stabilize DB-backed runtime proof
  - not widen platform/API/UI/memory surface

## 2026-04-08 - Runtime R1-J1 and R1-J3 repeated DB-backed proof green

- ran repeated DB-backed controller validation for the `R1-J` target slices
- combined truth-adjacent slice:
  - `8` consecutive runs
  - `118 passed, 1 warning` each run
- DB-backed runtime-core slice:
  - `4` consecutive runs
  - `84 passed, 1 warning` each run
- current truthful controller conclusion:
  - no new coding patch is currently justified for `R1-J1`
  - the preserved transient `R1-I3` issue remains a watch item, not an
    actively reproducible blocker
- durable records added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J1_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J3_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J3_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J_STATUS_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J_STATUS_MILESTONE_2026-04-08.md)

## 2026-04-08 - Runtime R1-J materially complete

- completed `R1-J2` delegated review with local Claude:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T030929-9b3d64b3](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T030929-9b3d64b3)
- completed `R1-J4` local Claude evolution
- current truthful phase conclusion:
  - `R1-J = materially complete with mixed delegated/controller evidence`
- durable records added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J2_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J2_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J4_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J4_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J_RESULT_MILESTONE_2026-04-08.md)
- durable method upgrade:
  - repeated targeted green runs are acceptable stability-phase closure evidence
  - historical transient failures alone do not justify speculative patches

## 2026-04-08 - Runtime R1-K phase opened after R1-J

- accepted the next narrow runtime phase after materially complete `R1-J`:
  - `R1-K Read-Path Trust Semantics Alignment`
- fixed the next remaining runtime gap as:
  - read-path trusted packet visibility still depends on existence checks
  - the read/write trust distinction is preserved but not yet explicit enough
- durable phase docs added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-K_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-K_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-K_READ_PATH_TRUST_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-K_READ_PATH_TRUST_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-K_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-K_EXECUTION_PACK_2026-04-08.md)
- packet/docs/results entrypoints now exist for:
  - `R1-K1` coding
  - `R1-K2` review
  - `R1-K3` testing
  - `R1-K4` evolution

## 2026-04-08 - Runtime R1-K materially complete

- completed `R1-K1` read-path trust alignment coding:
  - `operational_closure` and `project_surface` now use upstream relevance,
    not mere existence, for trusted packet visibility on the current read path
- updated focused tests to separate:
  - active current work
  - trusted upstream completed work
- controller validation passed:
  - focused read-path slice:
    - `29 passed, 1 warning`
  - combined truth-adjacent slice:
    - `120 passed, 1 warning`
- durable records added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-K1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-K1_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-K3_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-K3_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-K_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-K_RESULT_MILESTONE_2026-04-08.md)
- current truthful conclusion:
  - `R1-K = materially complete with mixed delegated/controller evidence`

## 2026-04-08 - Runtime R2-A consolidated readiness review opened

- accepted the next runtime phase after materially complete `R1-K`:
  - `R2-A Runtime v0 Consolidated Readiness Review`
- durable controller docs added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_CONSOLIDATED_REVIEW_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_CONSOLIDATED_REVIEW_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_REVIEW_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_REVIEW_PACK_2026-04-08.md)
- current controller judgment:
  - do not invent another narrow helper patch by default
  - synthesize `R1-C` through `R1-K` first
  - use that review to decide whether any broader runtime integration is justified

## 2026-04-08 - Runtime single-file review pack prepared

- compressed the current runtime-v0 review request into one portable file:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_SINGLE_FILE_REVIEW_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_SINGLE_FILE_REVIEW_PACK_2026-04-08.md)
- the pack includes:
  - review prompt
  - current runtime scope
  - stable architecture decisions
  - `R1-C` through `R1-K` phase summaries
  - materially complete vs mixed-evidence areas
  - current risks
  - current controller judgment
- purpose:
  - allow cross-model review without requiring a large supporting file set first

## 2026-04-08 - Runtime R2-A returned review absorbed

- read and synthesized the returned cross-model runtime review:
  - [D:\code\MyAttention\docs\review-for%20IKE_RUNTIME_V0_SINGLE_FILE_REVIEW_PACK_2026-04-08.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_V0_SINGLE_FILE_REVIEW_PACK_2026-04-08.md)
- durable controller synthesis added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_REVIEW_SYNTHESIS_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_REVIEW_SYNTHESIS_2026-04-08.md)
- current controller interpretation:
  - direction remains `on_track`
  - `R2-A` remains the correct active phase
  - broader integration is not yet opened
  - `R2-A` now explicitly includes debt settlement for:
    - `force=True`
    - retained notes
  - `R1-J` method-rule formalization
  - second benchmark / procedural memory can no longer remain implicit carry items

## 2026-04-08 - Runtime R2-A debt settlement executed

- durably closed the carried `force=True` review debt as a closure-discipline
  item rather than an open runtime semantics gap
- unified retained runtime notes into one backlog surface:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_RETAINED_NOTES_UNIFIED_BACKLOG_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_RETAINED_NOTES_UNIFIED_BACKLOG_2026-04-08.md)
- formalized the `R1-J` repeated-green stability rule into a dedicated runtime
  method-rules document:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_METHOD_RULES_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_METHOD_RULES_2026-04-08.md)
- durable debt-settlement result added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_DEBT_SETTLEMENT_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_DEBT_SETTLEMENT_RESULT_2026-04-08.md)

## 2026-04-08 - Runtime R2-A readiness gate closed; R2-B opened

- durable readiness-gate result added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_READINESS_GATE_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_READINESS_GATE_RESULT_2026-04-08.md)
- current truthful controller judgment:
  - runtime is now a strong runtime-base candidate
  - broader integration is still gated
- accepted next runtime phase:
  - `R2-B Debt Recovery And Narrow Runtime Proof Gate`
- durable next-phase docs added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B_DEBT_AND_NARROW_INTEGRATION_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B_DEBT_AND_NARROW_INTEGRATION_PLAN.md)
- strategic long-horizon scheduling is now explicit:
  - [D:\code\MyAttention\docs\IKE_STRATEGIC_SCHEDULING_NOTE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_STRATEGIC_SCHEDULING_NOTE_2026-04-08.md)

## 2026-04-08 - Runtime R2-B execution surface materialized

- added the first narrow `R2-B` packet set for the real task lifecycle proof:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-B1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-B1_CODING_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-B2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-B2_REVIEW_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-B3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-B3_TEST_BRIEF.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-B4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-B4_EVOLUTION_BRIEF.md)
- added phase execution pack:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B_EXECUTION_PACK_2026-04-08.md)
- current next action:
  - execute `R2-B1`

## 2026-04-08 - Runtime R2-B4 evolution materially executed

- absorbed the first real task lifecycle proof into durable runtime method rules
- five new rules added to `docs/IKE_RUNTIME_V0_METHOD_RULES_2026-04-08.md`:
  - Rule 4: canonical lifecycle path is proven and durable
  - Rule 5: delegate claims must use runtime-owned ClaimContext
  - Rule 6: WorkContext is derivative, never a second truth source
  - Rule 7: memory packets require upstream task linkage before trust
  - Rule 8: lease lifecycle is phase-aligned
- preserved future items remain explicit:
  - kernel-to-benchmark bridge proof
  - long-horizon scheduling for second concept benchmark and procedural memory
  - production worker lifecycle beyond test-level proof
- durable evolution record added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-B4_RESULT_MILESTONE_2026-04-08.md)
- current `R2-B` status now shows:
  - `R2-B1` coding materially executed
  - `R2-B3` testing materially executed
  - `R2-B4` evolution materially executed
  - `R2-B2` review still running in local Claude lane
- next controller action: complete `R2-B2`, then make full `R2-B` gate judgment

## 2026-04-08 - Runtime R2-B delegated coding lane started

- materialized `.runtime/delegation` execution entrypoints for:
  - `R2-B1` coding
  - `R2-B2` review
  - `R2-B3` testing
  - `R2-B4` evolution
- started local Claude worker coding run for:
  - `R2-B1 First Real Task Lifecycle Proof`
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T043044-81696251](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T043044-81696251)

## 2026-04-08 - Runtime R1-I1 operational guardrails green

- corrected the first delegated `R1-I1` coding result with a narrow
  controller-side fix
- fixed wrong-project explicit-alignment test setup by committing the secondary
  project before using its `project_id`
- stabilized upstream relevance reason labels to use enum-name casing
- operational guardrail validation now passes:
  - `23 passed, 1 warning`
  - `114 passed, 1 warning` for the combined
    `operational_closure + work_context + memory_packets` slice
- durable records added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I1_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I1_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-I1_OPERATIONAL_GUARDRAILS_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-I1_OPERATIONAL_GUARDRAILS_RESULT.md)
- current truthful judgment:
  - `R1-I1 = accept_with_changes`
- next active action:
  - `R1-I2`

## 2026-04-08 - Runtime R1-I2 delegated review durably absorbed

- ran a real local Claude delegated review for `R1-I2`:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T020524-5c3c572a](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T020524-5c3c572a)
- delegated review confirms:
  - archived explicit alignment is correctly rejected
  - no-active-context handling is explicitly bounded
  - trusted promotion uses upstream relevance checks
  - the patch stayed within the existing helper boundary
- preserved note:
  - reconstruction still uses existence-based checks on the read path
- durable records added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I2_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I2_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-I2_OPERATIONAL_GUARDRAILS_REVIEW_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-I2_OPERATIONAL_GUARDRAILS_REVIEW_RESULT.md)
- current truthful judgment:
  - `R1-I2 = accept_with_changes`
- next active action:
  - `R1-I3`

## 2026-04-08 - Runtime R1-I3 testing durably absorbed

- controller-side testing leg completed for `R1-I`:
  - compile check passed
  - `operational_closure` narrow suite: `23 passed, 1 warning`
  - combined truth-adjacent suite:
    - `operational_closure + work_context + memory_packets + project_surface`
    - `118 passed, 1 warning`
- preserved note:
  - one first-pass combined DB-backed run showed a transient foreign-key
    failure before an immediate clean rerun
- durable records added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I3_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I3_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-I3_OPERATIONAL_GUARDRAILS_TEST_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-I3_OPERATIONAL_GUARDRAILS_TEST_RESULT.md)
- current truthful judgment:
  - `R1-I3 = accept_with_changes`
- next active action:
  - `R1-I4`

## 2026-04-08 - Runtime R1-I evolution and phase result durably absorbed

- ran local Claude evolution analysis for `R1-I4`
- evolution confirms these should now be treated as durable runtime/method rules:
  - archived explicit alignment rejection
  - bounded runtime-domain errors for context-alignment failures
  - relevance-based upstream verification for trusted packet promotion
- explicitly preserved for later:
  - read-path reconstruction still uses existence checks rather than relevance checks
  - broader surface expansion remains deferred
- durable records added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I4_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I4_RESULT_MILESTONE_2026-04-08.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-I4_OPERATIONAL_GUARDRAILS_EVOLUTION_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-I4_OPERATIONAL_GUARDRAILS_EVOLUTION_RESULT.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I_RESULT_MILESTONE_2026-04-08.md)
- current truthful judgment:
  - `R1-I4 = accept_with_changes`
  - `R1-I = materially complete with mixed delegated/controller evidence`

## 2026-04-08 - Runtime R1-H materially complete; R1-I opened

- `R1-H` is now materially complete for the current delegated-evidence
  recovery scope:
  - `R1-D`
  - `R1-E`
  - `R1-F`
  - `R1-G`
  are all independently evidenced across coding/review/testing/evolution
- added phase-level result:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_RESULT_MILESTONE_2026-04-08.md)
- accepted next runtime phase:
  - `R1-I Operational Guardrail Hardening`
- added next-phase controller docs and execution pack:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I_PHASE_JUDGMENT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I_PHASE_JUDGMENT_2026-04-08.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I_OPERATIONAL_GUARDRAILS_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I_OPERATIONAL_GUARDRAILS_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-I_EXECUTION_PACK_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-I_EXECUTION_PACK_2026-04-08.md)

## 2026-04-08 - Runtime R1-H recovery wave complete for R1-D

- recovered `R1-D2` as a real local Claude delegated review run:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T164557-47ca6931](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T164557-47ca6931)
- recovered `R1-D3` as a real local Claude delegated testing artifact:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T164816-2a5d159d](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T164816-2a5d159d)
- refreshed phase evidence now shows:
  - `R1-D`
  - `R1-E`
  - `R1-F`
  - `R1-G`
  are all fully delegated across coding/review/testing/evolution
- durable recovery note added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_R1-D_RECOVERY_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_R1-D_RECOVERY_RESULT_2026-04-08.md)
- current truthful judgment:
  - `R1-H` can now be treated as materially complete for the current recovery scope

## 2026-04-08 - Runtime R1-H recovery wave complete for R1-E

- recovered `R1-E2` as a real local Claude delegated review run:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T163513-8ee4c053](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T163513-8ee4c053)
- recovered `R1-E3` as a real local Claude delegated testing artifact:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T163905-4c250ac5](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T163905-4c250ac5)
- recovered `R1-E4` as a real local Claude delegated evolution artifact:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T163711-b67fb56e](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T163711-b67fb56e)
- refreshed phase evidence now shows:
  - `R1-E` is fully delegated across coding/review/testing/evolution
  - `R1-D` is now the last recent runtime phase still carrying fallback
    non-coding lanes
- durable recovery note added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_R1-E_RECOVERY_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_R1-E_RECOVERY_RESULT_2026-04-08.md)
- current `R1-H` next target is now:
  - `R1-D2`
  - `R1-D3`

## 2026-04-07 - Runtime R1-G review provenance hardened

- `R1-G1` no longer only exists as a packet/plan; review-submission provenance
  is now materially hardened in:
  - [D:\code\MyAttention\services\api\runtime\memory_packets.py](/D:/code/MyAttention/services/api/runtime/memory_packets.py)
  - [D:\code\MyAttention\services\api\runtime\operational_closure.py](/D:/code/MyAttention/services/api/runtime/operational_closure.py)
- key hardening now in place:
  - `review_submitted_by_id` is recorded alongside `review_submitted_by`
  - nested `review_submission` metadata now mirrors the acceptance-side shape
  - `transition_packet_to_review(...)` now uses the packet's real
    `created_by_kind/created_by_id` instead of hardcoding `delegate`
  - empty review-submission actor ids are now rejected
  - `services/api/tests/conftest.py` now also cleans runtime tables for
    `test_runtime_v0_project_surface.py`
- validation passed:
  - `3 passed, 48 deselected, 1 warning` for the narrow
    `test_runtime_v0_memory_packets.py` provenance slice
  - `2 passed, 8 deselected, 1 warning` for the DB-backed
    `test_runtime_v0_operational_closure.py` provenance slice
  - `4 passed, 1 warning` for standalone `test_runtime_v0_project_surface.py`
- broader combined DB-backed validation now also passes:
  - `65 passed, 1 warning` for
    `project_surface + operational_closure + memory_packets`
- current truthful judgment:
  - `R1-G1 = accept_with_changes`
- the earlier cross-suite DB-backed persistence interaction was confirmed as a
  test-isolation issue and is now resolved by shared runtime table cleanup
- durable records added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-G1_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-G1_RESULT_MILESTONE_2026-04-07.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-G1_REVIEW_PROVENANCE_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-G1_REVIEW_PROVENANCE_RESULT.md)
- controller fallback review/testing/evolution records also added:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-G2_REVIEW_PROVENANCE_REVIEW_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-G2_REVIEW_PROVENANCE_REVIEW_FALLBACK.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-G3_REVIEW_PROVENANCE_TEST_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-G3_REVIEW_PROVENANCE_TEST_FALLBACK.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-G4_REVIEW_PROVENANCE_EVOLUTION_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-G4_REVIEW_PROVENANCE_EVOLUTION_FALLBACK.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-G_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-G_RESULT_MILESTONE_2026-04-07.md)
- current phase-level truthful judgment:
  - `R1-G = materially complete with fallback review coverage`

## 2026-04-07 - Runtime R1-E1 project-surface alignment green

- `R1-E1` no longer only exists as a packet/plan; the narrow project-surface
  alignment helper path is now implemented in:
  - [D:\code\MyAttention\services\api\runtime\operational_closure.py](/D:/code/MyAttention/services/api/runtime/operational_closure.py)
- DB-backed proof now covers:
  - explicit alignment of `RuntimeProject.current_work_context_id`
  - default alignment to the active runtime-owned work context
  - refusal to follow archived context after runtime truth moves forward
- validation passed:
  - `8 passed, 1 warning` for `test_runtime_v0_operational_closure.py`
  - `97 passed, 1 warning` for the combined
    `operational_closure + work_context + memory_packets` slice
- two narrow controller-found issues were corrected without widening scope:
  - alignment metadata wrote a raw `datetime` into JSON-backed project metadata
  - archival-path test moved a task to `DONE` without the required
    `result_summary`
- current truthful judgment:
  - `R1-E1 = accept_with_changes`
- durable records added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-E1_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-E1_RESULT_MILESTONE_2026-04-07.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-E1_PROJECT_SURFACE_ALIGNMENT_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-E1_PROJECT_SURFACE_ALIGNMENT_RESULT.md)
- controller fallback review/testing/evolution records also added:
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-E2_PROJECT_SURFACE_ALIGNMENT_REVIEW_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-E2_PROJECT_SURFACE_ALIGNMENT_REVIEW_FALLBACK.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-E3_PROJECT_SURFACE_ALIGNMENT_TEST_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-E3_PROJECT_SURFACE_ALIGNMENT_TEST_FALLBACK.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-E4_PROJECT_SURFACE_ALIGNMENT_EVOLUTION_FALLBACK.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-E4_PROJECT_SURFACE_ALIGNMENT_EVOLUTION_FALLBACK.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-E_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-E_RESULT_MILESTONE_2026-04-07.md)
- current phase-level truthful judgment:
  - `R1-E = materially complete with fallback review coverage`
- next active runtime phase accepted:
  - `R1-F Controller Runtime Read Surface`
- the preserved next gap is no longer project pointer truth
- it is controller-facing current runtime visibility from existing truth
- added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-F_PHASE_JUDGMENT_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-F_PHASE_JUDGMENT_2026-04-07.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-F_CONTROLLER_READ_SURFACE_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-F_CONTROLLER_READ_SURFACE_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-F_EXECUTION_PACK_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-F_EXECUTION_PACK_2026-04-07.md)
- `R1-F` is now also materialized into `.runtime/delegation` entrypoints for:
  - coding
  - review
  - testing
  - evolution
- `R1-F1` is now materially executed:
  - [D:\code\MyAttention\services\api\runtime\project_surface.py](/D:/code/MyAttention/services/api/runtime/project_surface.py)
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_project_surface.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_project_surface.py)
- validation passed:
  - `4 passed, 1 warning`
  - `101 passed, 1 warning` for the combined
    `project_surface + operational_closure + work_context + memory_packets` slice
- current truthful judgment:
  - `R1-F1 = accept_with_changes`
  - `R1-F = materially complete with fallback review coverage`
- durable records added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-F1_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-F1_RESULT_MILESTONE_2026-04-07.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R1-F1_CONTROLLER_READ_SURFACE_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R1-F1_CONTROLLER_READ_SURFACE_RESULT.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-F_RESULT_MILESTONE_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-F_RESULT_MILESTONE_2026-04-07.md)
- next active runtime phase accepted:
  - `R1-G Review Provenance Hardening`
- preserved next gap:
  - runtime review-submission and acceptance attribution is still narrower than
    the rest of the truth model
- added:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-G_PHASE_JUDGMENT_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-G_PHASE_JUDGMENT_2026-04-07.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-G_REVIEW_PROVENANCE_PLAN.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-G_REVIEW_PROVENANCE_PLAN.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-G_EXECUTION_PACK_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-G_EXECUTION_PACK_2026-04-07.md)
- `R1-G` is now also materialized into `.runtime/delegation` entrypoints for:
  - coding
  - review
  - testing
  - evolution

## 2026-04-07 - Runtime R1-C5/R1-C6 diagnosis

- controller localized the wide-suite DB failures to a real pytest harness gap:
  `test_runtime_v0_schema_foundation.py` expects `db_session`, but the repo
  currently has no shared `conftest.py` fixture provider
- controller fixed the `R1-C5` assignment-truth decision for `v0`:
  - `runtime_tasks.owner_kind/owner_id` is the durable truth source for
    `EXPLICIT_ASSIGNMENT`
- added durable diagnosis note:
  [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-C5_C6_DIAGNOSIS_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-C5_C6_DIAGNOSIS_2026-04-07.md)
- updated mainline order:
  - `R1-C6` should go before `R1-C5`
  - `R1-C5` now has a fixed v0 truth source after that
- added decision record:
  [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-C5_ASSIGNMENT_TRUTH_OPTIONS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-C5_ASSIGNMENT_TRUTH_OPTIONS.md)
- controller also narrowed `R1-C5` into explicit assignment-truth options and
  recorded a v0 recommendation:
  [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-C5_ASSIGNMENT_TRUTH_OPTIONS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-C5_ASSIGNMENT_TRUTH_OPTIONS.md)

## 当前总目标

MyAttention 的主线没有变化，仍然围绕三条大脑推进：

- 信息大脑：高质量信息收集、事实层沉淀、趋势分析、深度总结。
- 知识大脑：面向世界知识体系的结构化组织、权威理解、前沿研究和跨学科关联。
- 进化大脑：自动测试、真实运行监控、问题发现、问题归并、恢复与优化路径建议。

## 当前判断

项目不是从零开始，而是在已有聊天、知识库、记忆、信息源管理、测试问题中心和部分自我进化能力的基础上，进入“按主线重新收口”的阶段。

新增判断：

- `docs/ike_master_delivery/` 已成为新的顶层设计输入。
- 当前结论不是 `fresh start`，而是 `IKE-guided migration`。
- 已新增 `docs/IKE_MIGRATION_ALIGNMENT.md`，用于明确 IKE 与现有代码基线的映射关系、可复用资产、需要重构的结构以及第一阶段迁移切片。
- 已新增 `docs/IKE_V0_EXECUTION_PLAN.md`，将第一阶段迁移切片收敛为可执行的 v0 闭环计划，明确 v0 只证明一个真实、可检查、可重复的 IKE 端到端循环。
- 已新增 `docs/IKE_SHARED_OBJECTS_V0.md`，明确 v0 阶段的最小一等对象契约、统一 envelope、对象关系规则以及与现有运行时对象的初步映射。
- 已新增 `docs/IKE_RUNTIME_MIGRATION_SEQUENCE.md`，明确 IKE 迁移不从 repo 重写开始，而是按运行时切片、共享对象、最小 API / UI / harness 闭环渐进推进。
- 已新增 `docs/IKE_V0_IMPLEMENTATION_SLICES.md`，把 v0 闭环拆成可委派、可验收、可组合的实现切片，并明确哪些切片适合外包、哪些切片必须保留主控判断。
- 已新增 `docs/IKE_V0_DELEGATION_BACKLOG.md`，把 v0 切片进一步压成可直接委派给 qoder/openclaw 的 bounded tasks，并明确第一批推荐委派顺序与禁止外包的控制性部分。
- 已新增 `docs/IKE_V0_TASK_PACKETS.md`，明确当前 v0 第一批任务包的委派策略：`openclaw-glm` 负责编码实现，`openclaw-kimi` 负责分析/复核，`qoder` 暂保留为后续更稳定的半自动实现通道。

新增共识：

- 主控 agent 和后续进化大脑都不应机械附和需求，而应主动研究、分析、评估可行性、识别错误方向并及时纠偏。
- 项目推进按循环反馈优化过程进行，而不是按线性顺序一路向前。
- 过程产物、关键决策、有效/无效方法都需要持续沉淀到仓库中。
- `IKE Runtime v0` 现已被明确为 IKE 的第一阶段 runtime 内核，不只解决 OpenClaw 的记忆连续性，也必须解决任务、决策与工作状态治理。
- 任务治理不再只被视为产品功能缺口，也被视为当前 controller/delegate 开发流程的核心缺口；后续若没有项目/任务/决策/next-action 的结构化状态内核，持续委派开发很难稳定推进。
- 已新增 `docs/IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md`，把任务治理的核心设计进一步收敛到显式状态机、Postgres/Redis/对象存储分工、lease、checkpoint、outbox、备份与恢复模型，避免后续实现先天漂移。
- 已新增 `docs/IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md`，明确文档、运行时状态、证据产物、记忆层四者的边界：文档负责设计与交接，运行时对象负责当前真相，artifact 负责证据留存，memory 负责选择性取回。
- 已新增 `docs/IKE_MAGMA_CHRONOS_MEMORY_RESEARCH_NOTE.md`，把 `Chronos` 与 `MAGMA` 两条研究线纳入当前 IKE 记忆判断：前者强化时间/事件优先，后者强化结构化/关系化记忆，但二者都不改变 `IKE Runtime v0` 先做 durable state kernel 的顺序。
- 已新增 `docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md`，把 `IKE Runtime v0` 的最小数据模型、事务边界、outbox、lease、checkpoint、读路径与恢复策略进一步压成实现前约束，减少后续一边编码一边重新定义状态语义的风险。
- 已新增 `docs/IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md`，把 controller / delegate / reviewer / runtime / scheduler / user 六类角色的任务状态迁移权限显式化，避免后续实现出现 delegate 自行完结、runtime 隐式验收或状态语义漂移。
- 已将当前 `IKE Runtime v0` 设计压成一份单文件可交叉 review 里程碑包：`docs/IKE_RUNTIME_V0_REVIEW_MILESTONE_2026-04-04.md` 顶部直接内嵌 review prompt，便于下一轮跨模型审查在不重读全部设计树的情况下直接挑战状态机、权限矩阵、存储分层与恢复模型。
- 已新增 `docs/IKE_LONG_HORIZON_BACKLOG_AND_DECISION_LOG.md`，专门承接“有长期价值但当前不做”的方向，避免每轮 review 只收缩当下范围，结果把真正重要但延后的方向丢掉。
- 已新增 `docs/IKE_THINKING_MODELS_AND_METHOD_ARMORY.md`，把此前散落在问题建模、研究方法、benchmark 方法中的“思考模型武器库”重新收成顶层总纲，明确 thinking models 在执行方法之上。
- 已把早些时候通过聊天完成、但容易丢失的交叉 review 结果正式纳入 handoff 参考：
  - `docs/B4 review result.md`
  - `docs/review-for IKE_RUNTIME_V0_REVIEW_MILESTONE_2026-04-04.md`

当前最重要的事情不是继续铺新功能，而是：

1. 把信息大脑的数据底座做稳。
2. 把进化大脑做成真正可用的系统入口，而不是零散监控能力的集合。
3. 把运行流程、文档和任务状态固定下来，避免主线漂移。

## 新知识存储结构完成度

### 已完成

- Phase 1 已落地：
  - `ObjectStore` 抽象
  - `LocalObjectStore`
  - `raw_ingest` 原始层
  - `/api/feeds/import` 原始层持久化
- Phase 2 已部分落地：
  - `/api/feeds/import` 已支持写入 `raw_ingest + sources + feed_items + cache`
  - `/api/feeds` 已支持 `cache / db / hybrid`
  - `feed_items` 已开始承担事实层角色

### 尚未完成

- `feed_enrichments`
- `feed_aggregates`
- 信息到知识的完整自动转化闭环
- 面向学科组织的世界知识结构
- 知识大脑所需的权威理解层、前沿研究层和交叉学科层

结论：新的知识/信息存储结构**没有全部完成**，当前只完成了底座和部分事实层，离完整闭环还有明显距离。

## 当前优先级

### P0

- 固化本机运行流程，保证 web standalone 不再因为静态资源缺失而退化成裸 HTML。
- 修正前端关键入口的编码污染和页面结构问题。
- 给进化大脑独立页面、导航入口和即时自测入口。

### P1

- 将进化大脑从“日志和接口探针”升级到“真实 UI 巡检 + 核心链路自测”。
- 继续推进信息大脑事实层和富化层。
- 让文档、任务状态和真实代码进展保持同步。

## 本轮已完成

### 运行流程

- `manage.py` 已新增 web standalone 静态资源同步逻辑：
  - `.next/static -> .next/standalone/.next/static`
  - `public -> .next/standalone/public`
- 这一步是为了固化之前手工修复过的 CSS 404 问题。

### 前端结构

- 已修复并重写关键入口中的乱码污染：
  - `services/web/app/layout.tsx`
  - `services/web/components/ui/sidebar.tsx`
  - `services/web/app/page.tsx`
  - `services/web/app/chat/page.tsx`
- 已新增独立页面：
  - `services/web/app/evolution/page.tsx`
  - `services/web/components/evolution/evolution-dashboard.tsx`
- 已在进化大脑页面增加“立即自测”入口。
- 已将系统监控从通知设置中移出：
  - `services/web/app/settings/notifications/page.tsx`
  - `services/web/components/settings/notifications-config.tsx`

### 进化大脑

- 已接入真实浏览器 UI 巡检：
  - `services/web/scripts/ui-smoke-check.mjs`
  - 当前覆盖 `/chat`、`/evolution`
- 已将 UI 巡检接入自动进化自测主循环：
  - `services/api/feeds/auto_evolution.py`
- 已修正 `chat-voting-canary` 的超时误报：
  - 不再等待整个长答案结束
  - 现在以“至少两个模型成功返回，且已进入裁决合成阶段”为通过标准
- 当前手动执行 `POST /api/evolution/self-test/run` 已返回 `healthy=true`

### 主线澄清

- 已重新确认：当前主线仍然是“信息大脑存储底座 + 进化大脑可用化”。
- 已明确：当前并没有完成完整的知识大脑结构化存储。
- 已新增大脑控制层研究文档：
  - `docs/BRAIN_CONTROL_RESEARCH.md`
  - 覆盖 agent team、A2A、长期任务、嵌套子任务、长期记忆与保底运行层
- 已新增研究索引与分轨研究文档：
  - `docs/RESEARCH_INDEX.md`
  - `docs/TASK_AND_WORKFLOW_MODEL_RESEARCH.md`
  - `docs/SOURCE_INTELLIGENCE_RESEARCH.md`
  - `docs/MEMORY_ARCHITECTURE_RESEARCH.md`
  - `docs/KNOWLEDGE_LIFECYCLE_RESEARCH.md`
  - `docs/METHOD_EFFECTIVENESS_AND_SKILL_RESEARCH.md`
  - `docs/METHOD_INTELLIGENCE_RESEARCH.md`
  - `docs/DEEP_RESEARCH_METHOD_RESEARCH.md`
  - 已将“任务/工作流”和“知识生命周期”从单一讨论中拆开，方便后续独立设计
- 已进一步明确：来源发现与来源执行必须分开；并非所有信息都应进入持续抓取
- 已明确：深度研究方法值得作为主线方法底座吸收，但投票只能作为研究中的比较/复核工具，而不能替代 source plan、evidence log 和 fact base
- 已新增受控任务外包策略文档：
  - `docs/CONTROLLED_DELEGATION_STRATEGY.md`
  - 明确主控不外包、结构化交接、结果回收、验收门禁和版本记录要求
  - 将“高 token 编码/评审任务外包”正式纳入多脑协作第一阶段实施范围
- 已新增程序性知识架构文档：
  - `docs/SOP_AND_PROCEDURAL_KNOWLEDGE_ARCHITECTURE.md`
  - 明确 Method / SOP / Playbook / Skill / Policy 都属于正式知识对象
  - 明确自然语言主体 + 结构化元数据 + 版本管理 + 效果评估的统一方向
  - 明确进化大脑后续不只优化代码，也要优化方法、SOP、技能和策略本身

## Latest Implementation Update

- `IKE Runtime v0` `R1-B` has been re-audited against the live repo state.
- Current controller judgment:
  - lifecycle-proof planning is complete enough
  - `R1-B1` coding proof is now real
  - the project now has a dedicated lifecycle-proof test artifact
  - controller live validation passed across lifecycle/state/event suites
  - `R1-B2` review and `R1-B4` evolution still did not recover delegated durable results in this pass
  - controller fallback review/evolution have now been recorded so the milestone is still durable
- This means the current runtime gap is now:
  - recovery of the delegated review/evolution lanes
  - not additional lifecycle semantics planning

- Implemented the first task-and-brain control-plane foundation in the running system:
  - task workflow fields on `tasks`
  - `task_contexts`, `task_artifacts`, `task_relations`
  - `brain_profiles`, `brain_routes`, `brain_policies`, `brain_fallbacks`
- Added live control-plane bootstrap and inspection:
  - `GET /api/brains/control-plane`
- Connected `auto_evolution` to the new runtime model:
  - self-test writes context snapshots and events
  - collection health writes context snapshots and events
- Added runtime visibility endpoints for the evolution brain:
  - `GET /api/evolution/contexts`
  - `GET /api/evolution/contexts/{context_id}`
- Reworked the evolution page into a real runtime dashboard that now shows:
  - active contexts
  - latest snapshots
  - recent events
  - recent artifacts
  - context task lists
- Implemented the first source-intelligence control object layer:
  - `source_plans`
  - `source_plan_items`
  - `POST /api/sources/plans`
  - `GET /api/sources/plans`
- Verification completed:
  - migration `007`, `008`, `009`
  - backend unit tests
  - frontend `next build`
  - API smoke tests
  - `manage.py health --json`

## 下一步

1. 已完成 `Phase 3` 的第一份上位设计：`docs/PROBLEM_FRAMING_AND_METHOD_SELECTION.md`，明确问题类型、思维模型、方法和执行路由的 `V1` 框架。
2. 已完成 `Phase 4` 的第一份专项设计：`docs/SOURCE_INTELLIGENCE_ARCHITECTURE.md`，明确来源发现/来源执行分层、来源对象模型、冷热策略、Search/LLM/Feed/Agent 关系和 source intelligence 作为信息流上游控制层的定位。
3. 已完成 `Phase 4` 的第二份专项设计：`docs/MEMORY_ARCHITECTURE.md`，明确五层记忆分层、统一元字段、回忆策略、物理存储方案和 `task/procedural memory` 的短期优先级。
4. 已完成 `Phase 6` 的第一份前置设计：`docs/TASK_AND_WORKFLOW_MODEL.md`，明确 `Context / Task / Artifact / Event / Relation` 五类核心对象、四类任务、状态机、持续任务建模与事件/产物分离。
5. 已完成 `Phase 6` 的第二份核心设计：`docs/BRAIN_CONTROL_ARCHITECTURE.md`，明确 `Brainstem / Cerebellum / Cortex` 三层、`chief + specialist brains` 角色、受控协作拓扑、配置层和降级保底路径。
6. 已完成 `Phase 7` 的首版上位设计与研究：
   - `docs/VERSIONED_INTELLIGENCE_ARCHITECTURE.md`
   - `docs/TEMPORAL_AND_VERSIONED_DATA_RESEARCH.md`
   明确哪些对象必须版本化、版本通用字段、版本变化闭环、时间性数据分类，以及当前阶段不应仓促引入独立 TSDB 的判断。
7. 已完成进入编码前的主线收口判断：`docs/IMPLEMENTATION_READINESS_CHECKPOINT.md`。
   当前结论是：已具备进入下一轮主线编码的条件，最适合先落地“任务基础设施 + 大脑配置层”，其后是 source intelligence 基础对象层和 task/procedural memory。
8. 继续给进化大脑补“问题归因、恢复建议、去噪”，但作为服务主线的支线而不是新的主线。
9. 持续收口本机运行稳定性，避免 API/Web 因 watchdog 与运行模式漂移再次失稳。
## Latest Implementation Update

- First implementation batch has started for `task foundation + brain configuration`.
- Applied `migrations/007_task_brain_foundation.sql` to local PostgreSQL and verified the new tables exist in `myattention_utf8`.
- Extended the legacy task system instead of replacing it, so existing `testing/evolution/task_processor` flows remain compatible while new workflow concepts are added underneath.
- Added schema/model support for:
  - `task_contexts`
  - `task_artifacts`
  - `task_relations`
  - `brain_profiles`
  - `brain_routes`
  - `brain_policies`
  - `brain_fallbacks`
- Added the first minimal control-plane service in `services/api/brains/control_plane.py`.
- Added `GET /api/brains/control-plane`, which now returns `200` and bootstraps default brain profiles and routes on first access.
- Verified locally:
  - model compilation passes
  - 10 unit tests pass
  - migration `007` applied successfully
  - `/api/brains/control-plane` returns `200`
  - `python manage.py health --json` returns overall `healthy`

## Immediate Next Step

- Continue the first implementation batch by wiring the evolution subsystem onto the new task/context/artifact model, so automatic health checks and self-test loops become real daemon tasks instead of ad hoc background routines.
- Chat has now started using the brain control plane for live routing decisions via `build_execution_plan(...)` instead of relying only on the legacy task router/model picker.
- `POST /api/chat` now emits `brain_plan` in the SSE stream and persists it into assistant-message metadata, so the routing decision survives reloads and is no longer only an in-flight runtime detail.
- The chat UI now renders a lightweight brain-route card showing route id, primary brain, supporting brains, and thinking framework for assistant turns.
- Added unit coverage for execution-plan selection in `services/api/tests/test_brain_execution_plan.py`.
- Source intelligence is now surfaced in the frontend at `/settings/sources`:
  - source plans can be created from topic/focus/objective inputs
  - persisted plans are listed with candidate items, authority score, strategy, and review cadence
  - candidate items can be promoted into real managed sources through the existing subscribe endpoint
- Source-plan lifecycle has been extended beyond one-shot creation:
  - `POST /api/sources/plans/{plan_id}/refresh` now re-runs discovery and updates item status/rationale/evidence
  - `POST /api/sources/plans/{plan_id}/items/{item_id}/subscribe` now promotes a plan item into a managed source and marks the item as `subscribed`
  - the sources settings UI now supports in-place plan review refresh and item-level subscription with visible item status
- Source-plan versioning is now live:
  - migration `011_source_plan_versions.sql`
  - `source_plans.current_version / latest_version`
  - `source_plan_versions`
  - `GET /api/sources/plans/{plan_id}/versions`
  - refresh and subscribe actions now create version records with diff/evaluation metadata
- Refresh quality gating has been strengthened:
  - source-plan diff now compares average authority score, evidence delta, trusted-source delta, and authority-tier regressions
  - refresh evaluation now emits `gate_signals`
  - source-plan versions now capture a richer change summary instead of only score-drop/stale counts
  - the sources UI now surfaces recent version deltas and highlights when a newer candidate version is pending review
- Source-plan review cadence is now connected to the automatic evolution loop:
  - `review_cadence_days` now drives recurring scheduled refresh through auto-evolution
  - `last_reviewed_at / next_review_due_at / last_review_trigger` are now stored and returned on source plans
  - auto-evolution now persists source-plan review snapshots into `source_intelligence` task context runtime data
  - evolution status now includes `source_plan_review` results and degrades if recurring source-plan review fails
- Added a project-level version management specification:
  - `docs/VERSION_MANAGEMENT.md`
  - clarifies Git/file versioning vs. runtime intelligence object versioning
- Verified:
  - `POST /api/sources/plans` returns `200`
  - `GET /api/sources/plans` returns `200`
  - `POST /api/sources/plans/{plan_id}/refresh` returns `200`
  - `POST /api/sources/plans/{plan_id}/items/{item_id}/subscribe` returns `200`
  - `/settings/sources` returns `200`
  - frontend type-check passes
- Duplicate source-plan control is now live:
  - repeated `topic + focus` creation reuses the same plan and advances its version
  - duplicate active plans with the same merge key are merged toward a canonical plan and older rows are marked `inactive/merged`
  - source-plan list responses now canonicalize duplicate topic/focus entries before they reach the UI
- Current known gap:
  - duplicate control is now stable for repeated plan creation, including whitespace variants
  - some existing Chinese topic text in old source-plan rows is still encoding-corrupted and needs a separate storage/display fix
- Improved source-intelligence and evolution visualization:
  - source-plan cards are now split into clearer layers: plan status, version/review status, and grouped source candidates
  - source candidates are grouped into subscribed / watch / review buckets instead of one long flat list
  - evolution contexts now show guidance, clearer event labels, clearer artifact labels, and a manual-adoption suggestions area
- Current known UI gap:
  - source-plan topic text corruption still makes some Chinese topics unreadable
  - evolution suggestions are still heuristic hints, not yet model-generated design/UX recommendations
- Added `docs/ATTENTION_MODEL_RESEARCH.md`:
  - clarified that attention should not be limited to feed URLs
  - introduced a unified attention-object model for source / person / community / repository / organization / event / topic / method
  - defined `Attention Dimensions V1`, policy-driven ranking, portfolio balancing, and why current source-plan quality is still structurally limited
- Added `docs/ATTENTION_POLICY_ARCHITECTURE.md`:
  - defined `attention candidate / policy / evaluation / decision / review` objects
  - clarified that attention should be policy-driven, versioned, and gate-controlled rather than hardcoded scoring
- Delegation path via `acpx -> openclaw` is now operational with a bounded recovery workflow:
  - dedicated OpenClaw coding agent routing works
  - `scripts/acpx/openclaw_delegate.py` can recover results from session history when shell output is unreliable
  - current behavioral limitation is prompt drift when the delegated agent scans the repo freely
  - mitigation now added: `scripts/acpx/build_context_packet.py` builds UTF-8 bounded context packets so the main controller can send only the necessary excerpts
- Delegation has now been upgraded to a file-based protocol:
  - `scripts/acpx/run_file_delegation.py` sends only brief/context/output paths
  - delegated agents are expected to write structured UTF-8 JSON artifacts back to disk
  - this is now the preferred mode for bounded coding/review/analysis tasks, with free-form prompt delegation treated as fallback only
- Homepage feed freshness perception has been tightened:
  - default feed sort now starts with time order instead of importance order
  - the feed page now shows a freshness summary card with:
    - current snapshot state
    - latest content timestamp
    - current sort mode
  - this closes the most misleading gap where backend collection was current but the UI looked stale because cached data was shown first without clear explanation
  - fixed the implementation direction as `search + LLM dynamic discovery` under `policy + versioning + quality gate` constraints
- Attention policy foundation is now live in source intelligence:
  - migration `012_attention_policy_foundation.sql`
  - `attention_policies`
  - `attention_policy_versions`
  - `services/api/attention/policies.py`
- Source discovery now resolves a persisted attention policy per focus and applies policy-driven portfolio selection:
  - `POST /api/sources/discover` now returns `policy_id / policy_version / portfolio_summary`
  - candidates now carry `object_bucket / policy_score / gate_status / selection_reason`
  - current implementation still uses domain-backed candidates, but selection is no longer a pure score sort
- Source-plan creation and refresh now persist attention-policy metadata:
  - source plans now surface `policy_id / policy_version / policy_name / policy_decision_status`
  - source-plan items now retain attention evidence such as `object_bucket` and `selection_reason`
- The sources UI now shows the active attention policy and current policy gate decision on each plan card.
- Verified:
  - migration `012_attention_policy_foundation.sql` applied successfully
  - `POST /api/sources/discover` returns `200` with live policy metadata
  - `POST /api/sources/plans` returns `200` with persisted policy metadata
  - Python compile passes for `attention/policies.py`, `routers/feeds.py`, and `db/models.py`
  - attention-policy unit tests pass
  - frontend type-check passes
  - `python manage.py health --json` returns overall `healthy`
- Current known gap:
  - policy-driven selection is now live, but candidate quality is still too community-heavy for method topics such as multi-agent research
  - the next iteration should expand candidate object types beyond pure domains and improve method-topic query planning before UI redesign
- Source discovery is no longer limited to domain-only identity:
  - GitHub/GitLab/Hugging Face results can now normalize into `repository` objects
  - Reddit results can now normalize into `community` objects
  - X/Twitter profile URLs can now normalize into `person` objects
- Method-intelligence attention policy has been upgraded to `v2`:
  - policy execution now carries strategy-specific query templates
  - default policy seeding now supports in-place upgrades, not only first-time inserts
  - discovery now reflects the upgraded `policy_version`
- Verified on live discovery:
  - `POST /api/sources/discover` for `multi agent research + method` now returns `policy_version=2`
  - returned queries now come from policy templates instead of the old fixed method-query list
  - returned candidates now include object-level identities such as `repository`
  - portfolio summary for this sample now reached `accepted` with four distinct buckets instead of collapsing into a single low-diversity portfolio
- Current known gap:
  - the system now produces object-level candidates, but many community-domain results are still noisy
  - the next implementation step should introduce a true discovery-adapter layer so generic web search becomes one channel rather than the only candidate generator
- Auto-evolution now detects silent source-intelligence quality drift instead of only transport/runtime failures:
  - source-plan review runtime now audits every active plan for:
    - stale policy versions
    - missing required buckets
    - insufficient bucket diversity
    - method plans that are still dominated by plain domains
    - accepted plans that still contain only `needs_review` candidates
  - new quality findings now surface in:
    - `GET /api/evolution/status`
    - `GET /api/evolution/contexts`
    - `GET /api/testing/issues`
  - `Source Plan Review Daemon` now records both process snapshots and quality snapshots into task artifacts and memory
- Verified on live runtime:
  - `api/evolution/status` now exposes `source_plan_quality` as a tracked component
  - existing legacy method plans were automatically flagged as degraded instead of silently remaining `accepted`
  - `api/testing/issues` now contains `source_plan_quality` issues for outdated or low-diversity plans
- Current known gap:
  - source-plan quality drift is now detected, but not yet auto-remediated
  - log-health still overcounts SQL statement noise as critical errors and should be filtered separately
- Fixed a real chat regression that the previous self-test missed:
  - normal single-chat requests were broken because persisted `brain_profiles` still contained stale default models such as `qwen-max`
  - `services/api/brains/control_plane.py` now upgrades existing persisted brain-profile defaults when the shipped control-plane spec changes, instead of only creating missing profiles
  - `services/api/feeds/auto_evolution.py` now includes a dedicated `chat-single-canary` in periodic self-test coverage
  - the single-chat canary now checks the real default `/api/chat` path instead of only relying on the voting path
  - self-test session timeout was widened so the single-chat canary is not falsely killed by the outer `aiohttp` session timeout before its own request-level timeout
- Verified live after restart:
  - `POST /api/chat` now returns real assistant content again on the default non-voting path
  - `GET /api/evolution/status` now reports:
    - `chat-single-canary -> ok=true`
    - `chat-voting-canary -> ok=true`
    - `self_test.healthy = true`
- Current known gap:
  - evolution still reports `critical_log_errors`, but this is now log-noise degradation rather than chat-path failure
- Closed the next evolution-loop gap for source intelligence:
  - `source_plan_quality` issues are now marked `auto_processible` when the drift is repairable by a refresh cycle
  - auto-evolution now immediately processes auto-fixable source-plan quality tasks instead of only creating pending issues
  - repeated detections now also retrigger processing instead of only incrementing occurrence counts
  - `services/api/feeds/task_processor.py` now supports a `refresh_source_plan` recovery strategy for system-health issues tied to a source plan
- Reduced health-check noise so evolution status is closer to reality:
  - `services/api/feeds/log_monitor.py` now filters SQLAlchemy engine statement noise from quick health checks and error pattern aggregation
  - quick health is no longer dominated by cached SQL statements and task update SQL
- Verified:
  - source-plan quality issues now appear as `auto_processible=true` in `api/testing/issues`
  - quick health check now drops from hundreds of fake critical issues to a single real runtime error
- Current known gap:
  - `api/evolution/status` can still temporarily show stale `critical_log_errors` snapshots until the next loop writes a fresh filtered snapshot
  - one real runtime error remains in current quick health: `Local LLM decision failed: 'str' object has no attribute 'content'`
- Closed the next real evolution-loop blocker:
  - `services/api/feeds/ai_brain.py` now normalizes local LLM responses instead of assuming every provider returns an object with `.content`
  - this fixes the runtime error `Local LLM decision failed: 'str' object has no attribute 'content'`
  - `services/api/feeds/auto_evolution.py` now uses a shorter single-chat canary prompt with a wider request timeout budget so the canary no longer times out under normal runtime load
  - `services/api/feeds/log_monitor.py` now filters asyncpg connection-termination noise emitted during cancelled request cleanup, so quick health no longer stays red because of benign pool cleanup
- Verified live:
  - `POST /api/evolution/self-test/run` now returns `healthy = true`
  - both `chat-single-canary` and `chat-voting-canary` now pass in the same self-test snapshot
  - `GET /api/evolution/health/quick` now returns `status = healthy` with `critical_count = 0`
- 2026-03-24: `acpx -> openclaw` 委派链路进入可用状态。当前前台 shell 回显仍有缺陷，但专用 OpenClaw coding agent 已可通过 `acpx` 创建 session、提交 prompt，并通过 `sessions history/show` 结构化回收结果。新增 helper: `/D:/code/MyAttention/scripts/acpx/openclaw_delegate.py`。
- 2026-03-24: 信息流 Redis 主缓存链路已核实生效。
  - `POST /api/feeds/refresh` 会触发 `FeedFetcher` 写入 Redis `feed_cache:*`
  - 实测已生成 19 个键，例如 `feed_cache:36kr`、`feed_cache:bloomberg`、`feed_cache:ithome`
  - 当前信息流缓存不再只是进程内 `_cache` 和前端本地缓存，后端已具备 Redis 热缓存层
- 2026-03-24: 首页信息流 freshness 可视化继续收口。
  - `services/web/components/feed/feed-list.tsx` 现在会显示后端同步状态、读取模式、缓存层、最近入库时间和近 1 小时新增条数
  - `GET /api/feeds/health` 现已返回 `storage.cache_layers=["memory","redis"]`
  - 用户现在可以区分“前端本地快照”和“后端采集是否真的在持续更新”
- 2026-03-24: 智能对话慢路径诊断与进化监控增强。
  - 确认 `/api/chat` 并非“无响应”，SSE 首事件在 ~0.02-0.16s 内即可返回，问题主要是模型生成总耗时波动较大
  - 前端聊天默认模型不再使用旧默认 `qwen-max`，已切换为 `qwen3.5-plus`
  - `auto_evolution` 的聊天 canary 现在会把“响应过慢”作为异常条件之一，而不只是检查 HTTP 200 和是否有内容
- 2026-03-24: `acpx` 受控外包进入并发阶段。
  - 项目级 `acpx` 路由已落地在 [D:\code\MyAttention\.acpxrc.json](/D:/code/MyAttention/.acpxrc.json)
  - 当前并发角色：
    - `openclaw-qwen` -> `myattention-coder` -> `modelstudio/qwen3.5-plus`
    - `openclaw-glm` -> `myattention-glm-coder` -> `modelstudio/glm-5`
    - `openclaw-reviewer` -> `myattention-reviewer` -> `modelstudio/glm-5`
  - `openclaw_delegate.py` / `run_file_delegation.py` 已支持显式 `agent_alias`
  - 并发外包已完成一轮真实任务与复核：`glm` 的 source-quality 提案被接受，`qwen` 的 freshness 提案因缺少可执行 patch 被拒绝
- 2026-03-24: Source intelligence 修复了一个核心结构问题。
  - attention policy 之前按 `domain` 去重，导致同一平台只能保留一个对象，例如最多一个 `github.com`
  - 现已改为按 `object_key/url` 去重，`method` 主题下可以同时保留多个 GitHub repo
  - `source-method-v1` attention policy 已升级到 `v4`
  - `organization` 已进入候选对象层级，不再只能作为普通 domain 处理
- 2026-03-24: Source intelligence frontier/watch lane advanced to object-aware v3/v6 policies.
  - Added first-class `release`, `event`, and `signal` object recognition to discovery.
  - Added frontier/latest/method query templates for release notes, maintainer signals, and HN/Reddit reactions.
  - Fixed policy versioning gap: `source-frontier-v1` upgraded to `v3`; `source-method-v1` upgraded to `v6`.
  - Live `/api/sources/discover` now returns frontier policy `v3` with implementation objects alongside authority results, but still `needs_review`; upstream frontier/research discovery remains the next blocker.
- 2026-03-24: Source discovery quality loop advanced again on the mainline.
  - Fixed a live regression in `services/api/routers/feeds.py` where candidate score composition accidentally passed `activity_freshness` and `follow_score` as separate `min(...)` arguments, collapsing most candidates below the selection threshold.
  - Added generic media penalties for `method/frontier` discovery and promoted repo/release relation hints into real `person/organization` candidate seeds instead of leaving them as passive metadata only.
  - Added `follow_score`-aware frontier/method quality signals and upgraded `source-frontier-v1` to `v5` with an explicit `signal` quota.
  - Live discovery now surfaces maintainer people objects in method/frontier results; `multi agent research + method` remains `accepted`, while `openclaw + frontier` is still `needs_review` because the current frontier gate still expects a research bucket for what is behaving like a tool/project frontier topic.
- 2026-03-24: Recorded a mainline source-intelligence strategy correction.
  - Source value is contextual, not absolute.
  - The same object/source can legitimately serve multiple topics and multiple task intents.
  - Future attention design should evolve from simple `topic -> source` thinking toward `object + task intent + role in context`.
  - This correction is now part of the attention-policy architecture to prevent future quality work from regressing into global source suppression.

- 2026-03-24: Recorded a mainline capability gap for complex-source retrieval and anti-bot adaptation. Current RSS/API/generic-fetch/search paths are not sufficient for sources that require browser context, dynamic rendering, or anti-bot-aware acquisition.
- 2026-03-29: Consolidated three review lanes around the IKE v0 milestone.
  - Review consensus now treats the current branch as a valid migration seam, not yet a full v0 proof point.
  - Added `docs/IKE_MIGRATION_EXIT_CRITERIA.md` to define the difference between a present migration seam and a proven migration slice.
  - Added `docs/IKE_V0_1_LOOP_PLAN.md` to lock the next milestone onto one inspectable real loop instead of widening transitional API surface area.
  - Reaffirmed that durable `GET /{type}/{id}` retrieval remains out of scope until object access, identity, and reconstruction semantics are real.
- 2026-03-30: Completed the first real three-brain benchmark pass for `B1 harness`.
  - `B1-S1` now produces a live trend bundle from real discovery outputs.
  - `B1-S2` now produces an evidence-grounded meaning summary instead of a pure entity inventory.
  - `B1-S3` now produces a bounded relevance judgment and one bounded next action.
  - Generated a readable report at `D:\code\MyAttention\.runtime\benchmarks\ike_b1_harness_report.md`.
  - Clarified benchmark stage boundaries:
    - `B1 = signal + meaning + relevance hint`
    - `B2 = concept deepening + research trigger`
## 2026-04-01 - B5 Continued Study Plan

- Added `IKE_B5_CONTINUED_STUDY_PLAN.md` to formalize the next benchmark step
  after the first real `harness` study closure.
- Locked the current truthful benchmark state:
  - `study`
  - `partially_applicable`
  - `continue_study`
- Defined the next bounded question:
  - whether `LeoYeAI/openclaw-master-skills` is concept-defining or merely
    ecosystem-adjacent for `harness`.
- Completed the first `B5` continued-study analysis:
  - `LeoYeAI/openclaw-master-skills` is now treated as
    `ecosystem_relevant`, not `implementation_relevant`.
- Regenerated the live `B4` harness report so the benchmark surface uses the
  corrected tier result.
- Added a formal method for critical entity discovery and major event capture so
  IKE benchmark conclusions are less exposed to generic search adjacency.
- Added a Claude Code reference plan that treats `D:\claude-code` as a primary
  local technical artifact and `.qoder/repowiki` as structured secondary
  interpretation.
- Added a controller-accepted Claude Code B1 mapping and cut the next bounded
  packet on `memdir` as the highest-value reusable pattern study.
- Completed controller-level Claude Code `memdir` study and identified typed
  procedural memory plus background extraction as the strongest reusable pattern
  cluster so far.
- Cut the next bounded packet for a procedural-memory prototype plan instead of
  jumping directly to implementation.
- Converged the procedural-memory prototype down to `procedure` records at
  `task_closure` only, and cut the first bounded implementation packet.
- Defined the next bridge step: a narrow closure adapter from existing IKE
  completion artifacts into procedural-memory v1.
- Accepted reviewed benchmark study closure as the first truthful upstream
  producer for explicit procedural-memory payloads, and cut the next bounded
  implementation packet.
- Corrected `/settings/ike` so benchmark body content now has real bilingual
  support for the current harness artifact instead of label-only bilingual UI.
- Added a compact cross-model review pack:
  - `docs/IKE_CROSS_MODEL_REVIEW_MILESTONE_2026-04-03.md`
  - `docs/IKE_CROSS_MODEL_REVIEW_PROMPT_2026-04-03.md`
- Added a project-specific agent harness contract:
  - `docs/PROJECT_AGENT_HARNESS_CONTRACT.md`
  - defines controller/delegate boundaries, routing, review gate, truthfulness rules, and QA expectations for OpenClaw/Codex/Qoder contributors
- Absorbed the latest B4 cross-model review into planning:
  - reinforced that critical entity judgment remains the main upstream weakness
  - recorded method-generalization risk from relying on a single visible benchmark case
- Added follow-up plans:
  - `docs/IKE_ENTITY_JUDGMENT_STRENGTHENING_PLAN.md`
  - `docs/IKE_SECOND_BENCHMARK_SELECTION_PLAN.md`
- Added a controller note for the first B5 entity-review packet:
  - no current `harness` entity is justified as `concept_defining`
  - strongest implementation object remains `slowmist/openclaw-security-practice-guide`
  - strongest ecosystem object remains `LeoYeAI/openclaw-master-skills`
- Added a second-benchmark shortlist:
  - `agent memory`
  - `permissions`
  - `coordinator`
  with `agent memory` as the current preferred next benchmark candidate
- Absorbed the first external `IKE Runtime v0` review round into the runtime
  design tree.
- Compressed the v0 runtime task state machine to:
  - `inbox`
  - `ready`
  - `active`
  - `waiting`
  - `review_pending`
  - `done`
  - `failed`
- Moved `blocked`, `cancelled`, and `dropped` out of the first-cut durable v0
  state list and into waiting semantics / controller actions / event records.
- Added explicit `MemoryPacket` trust semantics:
  - `draft -> pending_review -> accepted`
- Added task-type lease-expiry recovery policy instead of leaving recovery to
  open-ended operator interpretation.
- Added explicit JSONB discipline so canonical task state, acceptance semantics,
  waiting semantics, lease policy, and primary references cannot silently drift
  into extension blobs.
- Updated the runtime review milestone brief so the next cross-model review sees
  the tightened design rather than the earlier wider state model.
- Added `docs/IKE_RUNTIME_EVOLUTION_ROADMAP.md` so `IKE Runtime` now has an
  explicit long-horizon version path and does not rely only on v0 design
  documents plus ad hoc future recollection.
- Added `docs/IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md` so the runtime line
  now has an explicit first-build slice, implementation prerequisites,
  acceptance checks, and deferred-work boundary before coding starts.
- Added `docs/IKE_RUNTIME_V0_IMPLEMENTATION_PACKETS.md` so the first runtime
  kernel build is now decomposed into bounded controller-ready implementation
  packets instead of one large implementation jump.
- Added `docs/IKE_RUNTIME_V0_DELEGATION_BACKLOG.md` and
  `docs/IKE_RUNTIME_V0_PACKET_R0-A_BRIEF.md` so the runtime line now has a
  concrete first-wave delegation order and a ready-to-send brief for the first
  schema packet.
- Added `docs/IKE_RUNTIME_V0_PACKET_R0-B_BRIEF.md` so the second runtime
  packet now has an equally explicit controller-ready brief for compressed
  task-state semantics.
- Added `docs/IKE_RUNTIME_V0_PACKET_R0-C_BRIEF.md` so the first recovery /
  lease / event packet now also has a bounded delegate-ready brief.
- Added `docs/IKE_RUNTIME_V0_PACKET_R0-D_BRIEF.md` and
  `docs/IKE_RUNTIME_V0_PACKET_R0-E_BRIEF.md` so `WorkContext` and
  `MemoryPacket` now also have explicit truthful controller-ready briefs.
- Added `docs/IKE_RUNTIME_V0_PACKET_R0-F_BRIEF.md` so the Redis acceleration /
  rebuild packet is now also bounded before implementation starts.
- Added `docs/IKE_RUNTIME_V0_FIRST_WAVE_PACKET_INDEX.md` so the first runtime
  implementation wave now has a single controller-facing packet index instead
  of only scattered briefs.
- Materialized the first runtime delegation packet in `.runtime/delegation` for
  `R0-A Core Runtime Schema Foundation`, including brief, context, and result
  template files.
- Materialized the second runtime delegation packet in `.runtime/delegation`
  for `R0-B Compressed Task State Machine Semantics`, including brief, context,
  and result template files.
- Materialized the third runtime delegation packet in `.runtime/delegation`
  for `R0-C Task Event Log and Lease Semantics`, including brief, context, and
  result template files.
- Materialized the remaining first-wave runtime delegation packets in
  `.runtime/delegation` for:
  - `R0-D WorkContext`
  - `R0-E MemoryPacket`
  - `R0-F Redis acceleration / rebuild`
  so the full first-wave runtime kernel now has bounded delegate-ready handoff materials.
- Added `docs/IKE_RUNTIME_V0_IMPLEMENTATION_EXECUTION_PACK_2026-04-05.md` so
  the full first-wave runtime kernel can now be reviewed or handed off from a
  single file instead of scattered docs plus `.runtime` references.
- Added `docs/PROJECT_DURABLE_RECORDING_AND_GIT_DISCIPLINE.md` and linked it
  from the project harness contract so durable recording and milestone-to-Git
  archival are now explicit project rules rather than chat-only reminders.
- Expanded `R1-B` into a full durable execution surface:
  - delegate-ready `R1-B2 / R1-B3 / R1-B4` packet materials
  - `IKE_RUNTIME_V0_R1-B_EXECUTION_PACK_2026-04-06.md`
  - `IKE_RUNTIME_V0_R1-B_RESULT_MILESTONE_2026-04-06.md`
  - `review-for IKE_RUNTIME_V0_R1-B_RESULT_MILESTONE_2026-04-06.md`
  so the current lifecycle-proof mainline no longer depends on one coding brief
  plus chat reconstruction.
- Added a blank review-result file for the runtime execution pack so future
  external reviews can be written back into a stable, predictable file path.
- Absorbed the first runtime implementation execution-pack review:
  - added global stop conditions
  - expanded `R0-A` to the full first-wave table footprint
  - added `WorkContext` reconstruction proof expectation
  - added `MemoryPacket` trust-boundary proof expectation
  - added controller pre-review reminders for `R0-B` and `R0-E`
- Formalized a review-process rule:
  - every meaningful review must produce both `now_to_absorb` and
    `future_to_preserve`
  - deferred-but-valuable directions must be written into the long-horizon
    backlog instead of disappearing after short-horizon scope narrowing
- Added a stable review template for the eventual `R0-A` result so execution
  and acceptance can use the same predictable review-file pattern as milestone reviews.
- 2026-04-05: `IKE Runtime v0` `R0-A` delegate execution completed and controller-reviewed. Current verdict: `accept_with_changes`. Durable review recorded in [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-A_CORE_SCHEMA_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-A_CORE_SCHEMA_RESULT.md). `runtime_task_relations` explicitly preserved as deferred, not forgotten or silently treated as implemented.
- 2026-04-05: `IKE Runtime v0` `R0-B` initial delegate result was rejected, then corrected through a narrow fix packet. Current verdict: `accept_with_changes`. Durable review recorded in [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-B_TASK_STATE_SEMANTICS_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-B_TASK_STATE_SEMANTICS_RESULT.md). Core correction: delegate `ready -> active` now requires claim-gated semantics instead of blanket direct allow.
- 2026-04-05: `IKE Runtime v0` `R0-C` delegate execution completed and controller-reviewed. Current verdict: `accept_with_changes`. Durable review recorded in [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-C_EVENTS_LEASES_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-C_EVENTS_LEASES_RESULT.md). Main retained hardening risk: append-only discipline is still stronger at API intent than at in-memory container sealing.
- 2026-04-05: `IKE Runtime v0` `R0-D` delegate execution completed and controller-reviewed. Current verdict: `accept_with_changes`. Durable review recorded in [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-D_WORK_CONTEXT_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-D_WORK_CONTEXT_RESULT.md). `WorkContext` is now acceptable as a derived snapshot carrier, not a second truth source.
- 2026-04-05: `IKE Runtime v0` `R0-E` first delegate result was rejected, then corrected through a narrow fix packet. Current verdict: `accept_with_changes`. Durable review recorded in [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-E_MEMORY_PACKET_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-E_MEMORY_PACKET_RESULT.md). Core correction: accepted packets now require explicit upstream linkage before they can become trusted for recall.
- 2026-04-05: `IKE Runtime v0` `R0-F` delegate execution completed and controller-reviewed. Current verdict: `accept_with_changes`. Durable review recorded in [D:\code\MyAttention\docs\review-for IKE_RUNTIME_R0-F_REDIS_REBUILD_RESULT.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_R0-F_REDIS_REBUILD_RESULT.md). Redis acceleration is now acceptable as a command-builder baseline; Postgres remains truth and Redis loss degrades performance rather than durable state.
- 2026-04-05: Added `docs/IKE_RUNTIME_V0_FIRST_WAVE_RESULT_MILESTONE_2026-04-05.md` and matching `review-for ...` template so the executed runtime first wave can be reviewed from one durable packet instead of scattered per-packet files.
- 2026-04-06: Added a first-class independent testing leg and a first-class independent evolution leg to the project method:
  - `docs/PROJECT_TEST_AGENT_AND_VALIDATION_MATRIX.md`
  - `docs/PROJECT_EVOLUTION_LOOP_AND_METHOD_UPGRADE.md`
  and updated the project harness contract so coding, review, testing, and evolution are now explicitly distinct collaboration responsibilities instead of relying on controller memory alone.
- 2026-04-06: Absorbed the new first-wave runtime result reviews into a concrete second-wave plan:
  - added `docs/IKE_RUNTIME_V0_SECOND_WAVE_HARDENING_PLAN.md`
  - fixed next priority around claim hardening, memory upstream existence verification, migration validation, and force-path restriction
  - preserved future-value items such as DB-level append-only enforcement, lease renewal/heartbeat hardening, queryable upstream trust, first real task lifecycle proof, and narrow kernel-to-benchmark integration
- 2026-04-06: Converted runtime second-wave into an explicit multi-agent cycle:
  - added `docs/IKE_RUNTIME_V0_SECOND_WAVE_MULTI_AGENT_CYCLE.md`
  - added `R1-A1` coding brief
  - added `R1-A2` review brief
  - added `R1-A3` test brief
  - added `R1-A4` evolution brief
  so the next runtime phase is no longer "coding first, everything else later".
- 2026-04-06: Materialized `R1-A1` into executable delegation artifacts:
  - `.runtime/delegation/briefs/ike-runtime-r1-a1-hardening-glm.md`
  - `.runtime/delegation/contexts/ike-runtime-r1-a1-hardening-glm.md`
  - `.runtime/delegation/results/ike-runtime-r1-a1-hardening-glm.json`
  and added a stable review template at `docs/review-for IKE_RUNTIME_R1-A1_HARDENING_RESULT.md`.
- 2026-04-06: Materialized the rest of the `R1-A` second-wave multi-agent cycle:
  - `R1-A2` review packet
  - `R1-A3` test packet
  - `R1-A4` evolution packet
  so second-wave is now runnable as controller + coding + review + testing + evolution rather than coding-only.
- 2026-04-06: `R1-A1` delegate execution completed. Controller review recorded in `docs/review-for IKE_RUNTIME_R1-A1_HARDENING_RESULT.md` with current verdict `accept_with_changes`. Main retained hardening gaps:
  - `role=None` legacy softness on force-path restriction
  - upstream-truth verification still depends on caller-supplied callback wiring
- 2026-04-06: `R1-A2` review delegate session timed out via `openclaw-kimi`; result file remained template-only, so controller review currently carries the usable review leg for `R1-A1`.
- 2026-04-06: recovered `openclaw-kimi` reviewer/evolution channel by fixing reviewer agent model route from `bailian-coding-plan/kimi-k2.5` to `modelstudio/kimi-k2.5`, reset reviewer main session, verified minimal probe, and successfully reran `R1-A2` + `R1-A4`.
- 2026-04-06: cleaned OpenClaw alias layer in `.acpxrc.json`; added canonical `openclaw-coder`, routed `openclaw-kimi` to `myattention-kimi-review`, retained `openclaw-qwen` only as legacy compatibility alias, and documented the alias map.
- 2026-04-06: standardized backup OpenClaw profiles on `bailian/qwen3.6-plus` by switching `myattention-coder` and `myattention-reviewer` off mixed model routes.
- 2026-04-06: executed `R1-A3` independent hardening tests and converted the testing leg from planned to real. Recorded durable results for:
  - `36` state-machine tests passed
  - `49` memory-packet trust tests passed
  - `7` migration-validation-support tests passed
  in `.runtime/delegation/results/ike-runtime-r1-a3-hardening-test.json` and `docs/review-for IKE_RUNTIME_R1-A3_HARDENING_TEST_RESULT.md`.
- 2026-04-06: clarified that second-wave remaining weaknesses are now tested residual risks, not unverified suspicions:
  - legacy `role=None` force-path softness
  - caller-supplied upstream verifier trust contract
- 2026-04-06: packaged `R1-A1~R1-A4` into a single durable second-wave milestone:
  - `docs/IKE_RUNTIME_V0_R1-A_RESULT_MILESTONE_2026-04-06.md`
  - `docs/review-for IKE_RUNTIME_V0_R1-A_RESULT_MILESTONE_2026-04-06.md`
  so future review can start from one hardening-cycle summary instead of separate packet results.
- 2026-04-06: converted the post-`R1-A` controller judgment into a concrete next narrow cycle instead of a vague “more hardening” note:
  - `docs/IKE_RUNTIME_V0_SECOND_WAVE_ENFORCEMENT_CYCLE.md`
  - `docs/IKE_RUNTIME_V0_PACKET_R1-A5_CODING_BRIEF.md`
  - `docs/IKE_RUNTIME_V0_PACKET_R1-A6_REVIEW_BRIEF.md`
  - `docs/IKE_RUNTIME_V0_PACKET_R1-A7_TEST_BRIEF.md`
  - `docs/IKE_RUNTIME_V0_PACKET_R1-A8_EVOLUTION_BRIEF.md`
  and matching `.runtime/delegation` materials.
- 2026-04-06: executed `R1-A5` enforcement coding and rejected it after live controller-side pytest validation. The cycle is working correctly:
  - coding made a bounded attempt
  - controller validation caught real regressions
  - next step is not expansion, but a corrected narrow follow-up
- 2026-04-06: executed `R1-A5-FIX` and accepted it with changes after live pytest:
  - `42` state-machine tests passed
  - `7` migration-validation-support tests passed
  - `49` memory-packet tests still passed
  The corrected state is now:
  - legal claim path restored
  - `role=None` force bypass still closed
  - migration-validation invocation stabilized
- 2026-04-06: completed the rest of the enforcement cycle with Kimi review/evolution:
  - `R1-A6` review ran successfully
  - `R1-A8` evolution ran successfully
  Controller judgment after the full cycle:
  - `R1-B` is conditionally ready
  - no extra narrow enforcement pass is required first
- 2026-04-06: opened `R1-B` as the next active runtime phase and materialized
  the first lifecycle-proof coding packet. The mainline target is now one real
  task path:
  - `inbox -> ready -> active -> review_pending -> done`
- 2026-04-07: diagnosed delegated review/evolution lane failure as local
  OpenClaw provider/auth drift rather than packet semantics. Corrected local
  routes so:
  - `myattention-kimi-review -> modelstudio/kimi-k2.5`
  - `myattention-reviewer -> bailian/qwen3.6-plus`
  and cleared stale session auth overrides.
- 2026-04-07: verified both `openclaw-kimi` and `openclaw-reviewer` with
  minimal `OK` probes after route repair.
- 2026-04-07: reran `R1-B2` review and `R1-B4` evolution successfully through
  the delegated lane. `R1-B` now has real coding/review/testing/evolution
  results and no longer depends on controller fallback because of lane
  transport failure.
- 2026-04-07: promoted the next runtime mainline from scattered `R1-B`
  residuals into an explicit `R1-C` phase:
  - `docs/IKE_RUNTIME_V0_R1-C_TRUTH_LAYER_PLAN.md`
  - `R1-C1` coding
  - `R1-C2` review
  - `R1-C3` testing
  - `R1-C4` evolution
  The new phase is intentionally narrow: remove executable legacy
  `allow_claim=True`, move delegate claim truth into runtime-owned verification,
  and absorb lifecycle-proof method rules durably.
- 2026-04-07: evaluated local Claude worker feasibility using
  `cc-worker-mcp-complete-package.zip`. Judgment:
  - direction is correct
  - useful as a new bounded coding lane
  - current machine is not execution-ready because `claude` is not on `PATH`
  - package needs a harness-result adapter before becoming a first-class lane
- 2026-04-07: Materialized `R1-C` into executable `.runtime/delegation`
  entrypoints for all four legs:
  - `R1-C1` coding
  - `R1-C2` review
  - `R1-C3` testing
  - `R1-C4` evolution
  and added `docs/IKE_RUNTIME_V0_R1-C_EXECUTION_PACK_2026-04-07.md` so the
  truth-layer phase now has a single durable execution/review handoff.
## 2026-04-07 Runtime Update

- `IKE Runtime v0` active mainline is now `R1-C`.
- `R1-C1` truth-layer coding is materially implemented:
  - executable `allow_claim=True` access is closed for CLAIM_REQUIRED transitions
  - `TransitionRequest` now carries `claim_context`
  - `ClaimVerifier` / `InMemoryClaimVerifier` now exist as the runtime truth adapter boundary
- Controller-side narrow runtime validation passed:
  - `256 passed`
  - `test_runtime_v0_state_machine.py`
  - `test_runtime_v0_task_state_semantics.py`
  - `test_runtime_v0_events_and_leases.py`
  - `test_runtime_v0_lifecycle_proof.py`
- Wider runtime sweep also ran:
  - `417 passed, 35 errors`
  - current failing area is DB-backed schema-foundation tests due missing `db_session` fixture/environment
  - this is recorded as a testing-lane/environment gap, not a proven `R1-C1` semantic regression
- Durable records added:
  - `docs/IKE_RUNTIME_V0_R1-C1_RESULT_MILESTONE_2026-04-07.md`
  - `docs/review-for IKE_RUNTIME_R1-C1_TRUTH_LAYER_RESULT.md`
# 2026-04-07 19:xx Controller Update

- `R1-C6` progressed from "missing `db_session` fixture" to a narrower, truthful
  blocker.
- Added repo-level runtime pytest fixture:
  - [D:\code\MyAttention\services\api\tests\conftest.py](/D:/code/MyAttention/services/api/tests/conftest.py)
- Controller rerun now proves:
  - fixture absence is no longer the primary blocker
  - local `MyAttentionPostgres` service is stopped
  - `localhost:5432` is unreachable
  - DB-backed runtime schema tests currently fail with `ConnectionRefusedError`
- Current mainline implication:
  - `R1-C6` is partially complete at the test-harness layer
  - next true blocker is environment restoration
  - `R1-C5` remains queued behind restored DB-backed runtime test truth
## 2026-04-07 - Runtime R1-C7 allow_claim removal green

- removed deprecated `allow_claim` compatibility parameter from:
  - [D:\code\MyAttention\services\api\runtime\state_machine.py](/D:/code/MyAttention/services/api/runtime/state_machine.py)
- updated runtime tests to reflect the new truthful surface:
  - `allow_claim` keyword is now rejected instead of tolerated as a no-op
- claim-related runtime validation remains green:
  - `194 passed, 1 warning`
- `R1-C` truth-layer work is now materially complete

## 2026-04-07 - Runtime R1-C5 Postgres-backed claim verifier green

- added narrow service-layer runtime truth implementation:
  - [D:\code\MyAttention\services\api\runtime\postgres_claim_verifier.py](/D:/code/MyAttention/services/api/runtime/postgres_claim_verifier.py)
- added DB-backed verifier tests:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_postgres_claim_verifier.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_postgres_claim_verifier.py)
- fixed test fixtures to align with current runtime DB truth:
  - lease rows need valid `heartbeat_at`
  - active lease linkage must respect task/lease foreign-key ordering
- targeted verifier validation now passes:
  - `4 passed, 1 warning`
- combined narrow DB-backed runtime validation now passes:
  - `57 passed, 1 warning`
- current mainline gap has moved past `R1-C5/R1-C6`
- materialized the next narrow follow-up:
  - `R1-C7` remove deprecated `allow_claim` compatibility surface

## 2026-04-07 - Runtime R1-C6 schema foundation green

- controller restored the local DB-backed runtime test path:
  - recovered `MyAttentionPostgres`
  - verified `localhost:5432`
  - applied `migrations/013_runtime_v0_kernel_foundation.sql` to the current DB
- added repo-level pytest DB fixture support at:
  - [D:\code\MyAttention\services\api\tests\conftest.py](/D:/code/MyAttention/services/api/tests/conftest.py)
- corrected schema-foundation test fixtures so they align with runtime truth:
  - partial-index assertion casing
  - `waiting` fixtures require `waiting_reason/waiting_detail`
  - `done` fixtures require `result_summary`
- DB-backed runtime validation now passes:
  - `53 passed, 1 warning`
- current mainline order is now:
  - `R1-C6` complete
  - `R1-C5` next

## 2026-04-07 - Runtime R1-D operational-closure phase materialized

- accepted next runtime phase after materially complete `R1-C`:
  - `R1-D Operational Closure Layer`
- narrowed the next proof to:
  - runtime-backed `WorkContext` reconstruction
  - runtime-backed trusted `MemoryPacket` promotion
  - no second truth source
- added full `R1-D` packet set:
  - `R1-D1` coding
  - `R1-D2` review
  - `R1-D3` testing
  - `R1-D4` evolution
- added single-file execution pack:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-D_EXECUTION_PACK_2026-04-07.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-D_EXECUTION_PACK_2026-04-07.md)
- added `.runtime/delegation` brief/context/result entrypoints for all four
  `R1-D` legs

## 2026-04-07 - Runtime R1-D1 operational-closure coding green

- added narrow DB-backed closure helper:
  - [D:\code\MyAttention\services\api\runtime\operational_closure.py](/D:/code/MyAttention/services/api/runtime/operational_closure.py)
- added DB-backed closure tests:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_operational_closure.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_operational_closure.py)
- proved:
  - runtime-backed `WorkContext` reconstruction
  - active-context persistence without second-truth drift
  - trusted `MemoryPacket` promotion tied to reviewed upstream linkage
- narrow DB-backed proof:
  - `5 passed, 1 warning`
- combined closure/work-context/memory validation:
  - `94 passed, 1 warning`
- current controller judgment:
  - `R1-D1 = accept_with_changes`
- controller review now durably recorded:
  - `review-for IKE_RUNTIME_R1-D1_OPERATIONAL_CLOSURE_RESULT.md`
- preserved follow-ups, not blockers:
  - review-submission attribution is still delegate-only in the new helper
  - `RuntimeProject.current_work_context_id` is not yet updated by the
    persistence path
- current phase milestone now also exists:
  - `IKE_RUNTIME_V0_R1-D_RESULT_MILESTONE_2026-04-07.md`
- controller fallback review/testing/evolution records now also exist for:
  - `R1-D2`
  - `R1-D3`
  - `R1-D4`
- `R1-D` is now judged materially complete with fallback review coverage
- next active runtime phase accepted:
  - `R1-E Project Surface Alignment`
- current `R1-E` target is narrow:
  - align `RuntimeProject.current_work_context_id`
  - prove project-facing current work visibility comes from runtime truth
- `R1-E` execution entrypoints now also exist:
  - `R1-E1` coding
  - `R1-E2` review
  - `R1-E3` testing
  - `R1-E4` evolution

## 2026-04-07 - Runtime R1-G review provenance materially complete; R1-H opened

- `R1-G1` review-provenance hardening is now materially executed with DB-backed
  proof:
  - truthful review submission now records both actor kind and actor id
  - `transition_packet_to_review(...)` no longer hardcodes `delegate`
  - empty review actor ids are rejected
- combined DB-backed provenance/runtime slice now passes with:
  - `65 passed, 1 warning`
- `R1-G` is now judged:
  - `materially complete with fallback review coverage`
- preserved next gap is no longer runtime truth semantics
- next active runtime phase accepted:
  - `R1-H Independent Delegated Evidence Recovery`
- `R1-H` is intentionally narrow:
  - recover durable delegated review/testing/evolution evidence for recent
    runtime phases
  - keep controller fallback explicit as backup rather than primary proof path
  - do not open new runtime truth objects or wider platform surfaces
- `R1-H` packet set and single-file execution pack now exist:
  - `R1-H1` coding
  - `R1-H2` review
  - `R1-H3` testing
  - `R1-H4` evolution

## 2026-04-07 - Runtime R1-H1 delegated evidence recovery support green

- added a narrow controller-facing helper for recent runtime phase evidence:
  - [D:\code\MyAttention\services\api\runtime\phase_evidence.py](/D:/code/MyAttention/services/api/runtime/phase_evidence.py)
- added focused tests:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_phase_evidence.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_phase_evidence.py)
- the helper now classifies durable lane artifacts as:
  - `delegated`
  - `fallback`
  - `missing`
- narrow validation passed:
  - `2 passed, 1 warning`
- current artifact scan now truthfully shows:
  - `R1-D`: delegated = `coding, evolution`; fallback = `review, testing`
  - `R1-E`: delegated = `coding`; fallback = `review, testing, evolution`
  - `R1-F`: delegated = `coding`; fallback = `review, testing, evolution`
  - `R1-G`: delegated = `coding, testing`; fallback = `review, evolution`
- current controller judgment:
  - `R1-H1 = accept_with_changes`
- remaining work is no longer “find the gap”, but recover or durably normalize
  the missing delegated evidence through `R1-H2 ~ R1-H4`

## 2026-04-07 - Runtime R1-H recovery order fixed

- added durable fallback review/testing/evolution absorption for `R1-H1`:
  - `R1-H2`
  - `R1-H3`
  - `R1-H4`
- fixed the first controller recovery order for delegated evidence:
  1. `R1-G2`, `R1-G4`
  2. `R1-F2`, `R1-F3`, `R1-F4`
  3. `R1-E2`, `R1-E3`, `R1-E4`
  4. `R1-D2`, `R1-D3`
- current mainline gap is now explicit:
  - not new runtime truth semantics
  - not broader platform surface
  - but recovering independent delegated evidence where fallback still carries
    recent runtime phases
- generated durable runtime phase evidence snapshot artifacts:
  - [D:\code\MyAttention\.runtime\runtime-phase-evidence\runtime_phase_evidence_snapshot_2026-04-07.json](/D:/code/MyAttention/.runtime/runtime-phase-evidence/runtime_phase_evidence_snapshot_2026-04-07.json)
  - [D:\code\MyAttention\.runtime\runtime-phase-evidence\runtime_phase_evidence_snapshot_2026-04-07.md](/D:/code/MyAttention/.runtime/runtime-phase-evidence/runtime_phase_evidence_snapshot_2026-04-07.md)

## 2026-04-07 - Runtime R1-H status and next target fixed

- `R1-H` is now durably recorded as:
  - `in_progress`
- current `R1-H` state is no longer vague:
  - `R1-H1` materially executed
  - `R1-H2 ~ R1-H4` absorbed as controller fallback review/testing/evolution
  - next work is actual delegated evidence recovery
- immediate next recovery target is now fixed at:
  - `R1-G2`
  - `R1-G4`
- after `R1-G`, the next recovery wave remains:
  - `R1-F2`
  - `R1-F3`
  - `R1-F4`

## 2026-04-08 - Runtime R1-H first recovery wave complete for R1-G

- recovered `R1-G2` as a real local Claude delegated review run:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T161215-9fcbce81](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T161215-9fcbce81)
- recovered `R1-G4` as a real local Claude delegated evolution artifact:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T161425-67c1b6af](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T161425-67c1b6af)
- refreshed the phase evidence snapshot:
  - `R1-G` is now fully delegated across all four lanes
  - `R1-F` is now the next fallback-heavy recovery target
- durable recovery note now exists:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_R1-G_RECOVERY_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_R1-G_RECOVERY_RESULT_2026-04-08.md)

## 2026-04-08 - Runtime R1-H partial recovery wave complete for R1-F

- recovered `R1-F2` as a real local Claude delegated review run:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T161728-b61ffe5c](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T161728-b61ffe5c)
- recovered `R1-F4` as a real local Claude delegated evolution artifact:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T161900-ae8a1c14](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T161900-ae8a1c14)
- refreshed the phase evidence snapshot:
  - `R1-F` now has delegated `coding, review, evolution`
  - only `R1-F3` testing remains fallback-backed
- durable partial recovery note now exists:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_R1-F_PARTIAL_RECOVERY_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_R1-F_PARTIAL_RECOVERY_RESULT_2026-04-08.md)

## 2026-04-08 - Runtime R1-H full recovery wave complete for R1-F

- recovered `R1-F3` as a real local Claude delegated testing artifact:
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260407T162513-41c9650f](/D:/code/MyAttention/.runtime/claude-worker/runs/20260407T162513-41c9650f)
- refreshed the phase evidence snapshot:
  - `R1-F` is now fully delegated across coding/review/testing/evolution
  - `R1-E` is now the next fallback-heavy recovery target
- durable full recovery note now exists:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-H_R1-F_RECOVERY_RESULT_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-H_R1-F_RECOVERY_RESULT_2026-04-08.md)
- 2026-04-08: Added R2-B1 lifecycle proof controller comparison; focused validation passed (`19 passed, 1 warning`) and recorded in `docs/IKE_RUNTIME_V0_R2-B1_RESULT_MILESTONE_2026-04-08.md`.
- 2026-04-08: Restored local system runtime for controller work:
  - web `127.0.0.1:3000` reachable
  - API `127.0.0.1:8000/health` healthy
- 2026-04-08: Recorded `R2-B1` as a durable controller-recovered coding result after the local Claude worker produced the correct bounded diff but did not emit a final artifact within the comparison window.
- 2026-04-08: Added an explicit coding comparison note for `R2-B1` at `docs/IKE_RUNTIME_V0_R2-B1_CODING_COMPARISON_2026-04-08.md`.
- 2026-04-08: Materialized `R2-B3` as durable focused testing evidence with `214 passed, 1 warning`.
- 2026-04-08: Added `docs/IKE_RUNTIME_V0_R2-B_STATUS_MILESTONE_2026-04-08.md` so `R2-B` no longer depends on chat reconstruction while `R2-B2` review is still running.
- 2026-04-08: Closed the `R2-B` lifecycle-proof subtrack as a durable mixed-evidence result and moved the active remaining `R2-B` target to the kernel-to-benchmark bridge proof.
- 2026-04-08: Materialized the remaining `R2-B` bridge-proof target into a full packet set (`R2-B5 ~ R2-B8`) plus a single execution pack, so the mainline no longer depends on reconstructing the next step from planning notes.
- 2026-04-08: Executed `R2-B5` as a narrow DB-backed benchmark bridge proof. Added `runtime/benchmark_bridge.py` plus `test_runtime_v0_benchmark_bridge.py` and proved a reviewed benchmark procedural-memory candidate can enter runtime as a `pending_review` packet without bypassing the runtime trust gate (`7 passed, 1 warning`; combined slice `87 passed, 1 warning`).
- 2026-04-08: Materialized `R2-B7` as durable testing evidence for the bridge proof. The benchmark bridge slice and the combined closure/project-surface/memory slice are both green, so `R2-B` no longer depends on chat reconstruction for bridge validation.
- 2026-04-08: Materialized `R2-B8` as durable evolution guidance for the bridge proof. Runtime method guidance now explicitly preserves the rule that benchmark-originated candidates may only enter runtime as `pending_review` packets until accepted by the runtime truth gate.
- 2026-04-08: Materialized `R2-B6` as an independent delegated review result for the bridge proof and closed `R2-B` as a durable consolidated runtime milestone. The next active phase is now `R2-C Runtime-to-Visible-Surface Narrow Integration`.
- 2026-04-09: Hardened `R2-G` service-preflight truth with a strict preferred-owner gate. `service_preflight` and the runtime preflight inspect route now support `strict_preferred_owner`, and the current `8000` live snapshot truthfully resolves to `ambiguous` when the listener is the non-preferred system Python owner (`67 passed, 28 warnings, 9 subtests passed`).
- 2026-04-09: Surfaced strict runtime service preflight on the existing settings runtime panel. The page now requests strict preflight server-side and can display status, preferred-owner state, and mismatch warning without widening into a broad operations UI. Frontend compile passed, and the current strict helper snapshot on `8000` remains truthfully `ambiguous`.
- 2026-04-09: Recovered API availability on `8000` after clearing project-related `run_service.py` processes, but the listener still reappeared under system `Python312`. Recorded this as an environment-level owner reclaim note rather than pretending service ownership was normalized.
- 2026-04-09: Added machine-readable owner-chain diagnosis to `service_preflight`. The current `8000` strict snapshot now shows not only `preferred_mismatch` but `parent_preferred_child_mismatch`, which narrows the live-proof blocker from generic drift to interpreter/ownership-chain drift.
- 2026-04-09: Added machine-readable code-fingerprint and code-freshness surfacing to `service_preflight`, routed the new fields through `/api/ike/v0/runtime/service-preflight/inspect`, and surfaced `Code Freshness` on the settings runtime panel. Strict freshness mismatch can now truthfully downgrade live proof to `ambiguous` once a controller supplies an expected fingerprint (`71 passed, 28 warnings, 9 subtests passed`).
- 2026-04-09: Added explicit `host/port` targeting to the runtime service-preflight inspect route so controller live proof is no longer hardcoded to `8000`. Route and preflight slices are green (`72 passed, 28 warnings, 9 subtests passed`), but fresh alternate-port live proof is still blocked by launch-path / served-code drift.
- 2026-04-09: Fixed the next `R2-G` target at launch-path discipline. Current blocker is no longer missing preflight observability; it is proving one controller-acceptable fresh launch path whose live route reflects current workspace code.
- 2026-04-09: Completed a fresh alternate-port live proof on `8013`. The live route now truthfully returns `owner_chain`, `code_fingerprint`, and `code_freshness`; when the current fingerprint is supplied, `code_freshness.status = match`. Remaining `R2-G` ambiguity is now isolated to launch-path / interpreter ownership (`parent_preferred_child_mismatch`), not served-code freshness.
- 2026-04-09: Added machine-readable `repo_launcher` evidence to `service_preflight`, surfaced it through the inspect route and the settings runtime panel, and confirmed the current `8000` baseline is now characterized as: preferred-owner mismatch, parent-preferred child mismatch, but repo-launcher match. Remaining `R2-G` work is now the controller acceptability rule for that combination.
- 2026-04-09: Added machine-readable `controller_acceptability` to `service_preflight`, routed it through the inspect endpoint and visible runtime panel, and fixed the next `R2-G` target as an explicit controller usage rule for `bounded_live_proof_ready`.
