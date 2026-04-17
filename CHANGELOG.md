# MyAttention 变更日志

> 用于记录项目级重要变更、阶段性能力提升和兼容性调整。详细设计变更请结合 `docs/` 下的专项文档阅读。

---

## [Unreleased]

### Added

- 2026-04-15: Added a bounded `Source Intelligence V1 M11` version-judgment
  inspect slice. The project can now run advisory AI judgment over persisted
  source-plan version changes through
  `POST /api/sources/plans/{plan_id}/versions/{version_number}/judge/inspect`.
  This reuses the internal `feeds.ai_judgment` substrate on a second surface,
  stays inspect-only, does not mutate source plans, and does not override the
  persisted refresh evaluation.
- 2026-04-15: Closed the `M11` review loop. The packet wording now more
  explicitly says it judges bounded refresh-change targets rather than the
  source-plan version as a whole, a `snapshot_only` fallback proof was added,
  a missing-version `404` route proof was added, and the returned `gemini`
  review was rejected as mixed-context drift back to `M10`.
- 2026-04-15: Added a bounded `Source Intelligence V1 M12` version-panel
  inspect slice. The project can now run dual-model panel judgment over
  persisted source-plan version change targets through
  `POST /api/sources/plans/{plan_id}/versions/{version_number}/judge/panel/inspect`.
  This reuses both the version-target extraction from `M11` and the existing
  multi-model judgment substrate, while staying inspect-only and non-mutating.
- 2026-04-15: Closed the `M12` review loop. Packet wording now stays at the
  honest level of a bounded dual-lane panel inspect, and one failure-path test
  now proves malformed secondary output still yields a truthful mixed panel
  signal instead of a falsely stable result.
- 2026-04-13: Added a bounded `Source Intelligence V1 M3` noise-compression
  slice on the existing discovery path. The current implementation now
  suppresses redundant generic `domain` candidates when the same source already
  yields a materially competitive specific object such as a `repository`. The
  change stays inside the current `feeds.py` discovery flow, adds no new API
  surface, and is covered by focused helper- and route-level tests.
- 2026-04-13: Closed the `Source Intelligence V1 M3` review loop with
  selective absorption. The packet wording is now explicitly narrowed to a
  `same-source generic-domain compression heuristic`, a new guardrail test now
  proves generic domains remain when the specific candidate is not materially
  competitive, and the returned `gemini` review was rejected because it drifted
  back to the older `M2` loop-proof scope.
- 2026-04-13: Added a bounded `Source Intelligence V1 M4`
  release-over-repository compression slice. In `LATEST` and `FRONTIER`, the
  current discovery path now suppresses a same-repo `repository` candidate when
  a materially competitive `release` candidate already exists. `METHOD`
  remains unchanged, and weak release candidates do not suppress the
  repository.
- 2026-04-14: Closed the `Source Intelligence V1 M4` review loop. The packet
  wording now matches the implementation more exactly (`LATEST` / `FRONTIER`
  instead of broader `timely focus`), route-level symmetry proof now covers
  `FRONTIER` positive compression and `METHOD` negative preservation, and the
  packet is now explicitly framed as a same-repo duplicate-compression
  heuristic rather than a broad release-superiority rule.
- 2026-04-14: Added a bounded `Source Intelligence V1 M5` quality slice for
  contextual tech-media article pages. In `LATEST` / `FRONTIER`, article pages
  from a narrow contextual-media set such as `36kr` are now classified as
  `signal` instead of flat `domain` entries, while `METHOD` remains on the
  conservative path. This improves object quality without adding new API
  surface.
- 2026-04-14: Closed the `Source Intelligence V1 M5` review loop. The bounded
  publisher set was tightened by removing `medium.com` and `substack.com`,
  explicit `FRONTIER` proof and negative page-boundary proof were added, and
  the packet wording now more accurately describes a bounded publisher/article
  family rather than a broader media slice.
- 2026-04-14: Added a bounded `Source Intelligence V1 M6` quality slice for
  GitHub repo thread pages. Issue, discussion, and pull-request pages can now
  be classified as `signal` inside the current discovery path, while plain repo
  pages remain unchanged. This stays bounded to GitHub and does not widen into
  a broader collaboration-platform ontology.
- 2026-04-14: Added an explicit AI-driven evolution-kernel note so recent
  heuristic-heavy source-intelligence slices are not misread as the project's
  final architecture. The project now durably records that information brain,
  knowledge brain, evolution brain, and the cross-cutting scientific
  methodology layer remain the core north-star, while hard-coded slices are
  temporary cleanup and normalization scaffolds.
- 2026-04-14: Added a bounded `Source Intelligence V1 M7`
  AI-assisted-candidate-judgment inspect lane. The current discovery surface
  can now pass a bounded candidate subset into a model prompt and return
  advisory `follow` / `review` / `ignore` judgments without writing source
  truth or auto-promoting anything. This is the first explicit step that
  reintroduces AI participation above the cleaned discovery baseline.
- 2026-04-15: Closed the `Source Intelligence V1 M7` review loop. Malformed
  model JSON now falls back to an empty bounded advisory result instead of a
  500, notes now expose discarded-judgment transparency, and the truth
  boundary explicitly states that the free-form summary is advisory
  condensation rather than the canonical decision set.
- 2026-04-15: Added a bounded `Source Intelligence V1 M8` panel-inspect
  slice. The same judged candidate subset can now be sent through two model
  lanes, and the route exposes agreement/disagreement shape without merging
  the outputs into canonical truth or workflow actions.

- 2026-04-13: Added `R2-I19` operator-substrate proof for `Runtime v0`.
  This packet does not add new runtime APIs or scheduler semantics; it
  formalizes that the existing runtime project read surface and controller-
  facing inspect routes now satisfy the exit requirement that runtime truth has
  at least one real consuming controller/operator use path.

- 2026-04-13: Closed the `R2-I18` validated review loop with selective
  absorption. The packet now has an explicit changed-basis supersession test,
  the no-task-anchor rejection test uses `pytest.raises`, and the returned
  mixed-context `gemini` review was explicitly rejected rather than absorbed.
  The GitHub review-pack copy was also refreshed so external review docs use
  repo-relative links instead of local absolute filesystem paths.

- 2026-04-12: Closed the focused local validation loop for `R2-I18`. After
  restoring the PostgreSQL service, the DB-backed
  `tests/test_runtime_v0_controller_acceptance.py` slice now passes locally,
  and the combined focused packet
  (`tests/test_runtime_v0_controller_acceptance.py` +
  `tests/test_routers_ike_v0.py`) also passes. The `R2-I18` blocker note and
  result milestone now reflect that this packet is locally validated rather
  than still environment-blocked.

- 2026-04-12: Corrected the local `R2-I18` validation story and repaired the
  pytest surface around it. `tests/conftest.py` no longer forces PostgreSQL
  connection for every pytest file through an autouse cleanup dependency, so
  the focused router/runtime inspect slice now passes under pytest again. The
  remaining blocker is now stated truthfully as environment-level PostgreSQL
  unavailability for `tests/test_runtime_v0_controller_acceptance.py`, not a
  generic import/pytest timeout story.

- 2026-04-11: Added a bounded `Source Intelligence V1` activation packet so
  the project no longer treats source quality as a known bottleneck without an
  execution entry. The new packet includes:
  - a phase judgment
  - an implementation-start packet
  - an explicit M1 scope
  - a coding brief
  - a single review-request file
  and upgrades `Source Intelligence V1` from background preparation to the
  next product-capability start line beneath the true runtime mainline.
- 2026-04-11: Added a document-compression and active-surface policy so
  durable documentation growth does not become hidden controller drag. The
  project now has an explicit rule that only a small set of maps, indexes,
  packets, and handoffs count as active continuation surface; other documents
  remain durable evidence but not default first-read material.
- 2026-04-11: Added an explicit agent-harness boundary-proof packet so the
  harness line can prove what is materially isolated, what is only
  metadata-backed, and what is still unproven. This keeps future sandboxing
  claims honest and gives the harness line one concrete next proof task.
- 2026-04-11: Added a minimum-feasibility note for `Knowledge Brain` so this
  line now has a truthful launch condition instead of remaining an undefined
  future aspiration. The note explicitly keeps `Knowledge Brain` below
  `Runtime v0` and `Source Intelligence V1` in current priority.
- 2026-04-11: Added a compact strategic follow-up tracker so the accepted
  outputs from the project-level strategic review now have one durable summary
  surface instead of remaining scattered across multiple docs.
- 2026-04-11: Added a single-file review request for the current strategic
  follow-up package so external/project-level review can be requested without
  reconstructing the absorbed document set by hand.
- 2026-04-11: Tightened `Source Intelligence V1 M1` into an implementation
  landing decision, minimal writeset, and direct task packet. Current
  controller judgment is now explicit: the first M1 coding lane should land on
  the existing `routers/feeds.py` discovery/source-plan path rather than
  opening a parallel source-intelligence stack.
- 2026-04-11: Added a single-file `Source Intelligence V1 M1` delivery pack and
  an agent-harness boundary-proof checklist/result template. The current
  controller follow-up wave is now easier to hand off for implementation and
  easier to execute consistently for proof-oriented support tracks.
- 2026-04-11: Landed the first agent-harness boundary-proof result. Current
  truthful claim boundary is now explicit: OpenClaw workspace isolation and
  shared metadata coverage are materially proven, Claude external run-root is
  now artifact-proven via a fake local sample under the external run root, and
  hard sandbox enforcement remains unproven.
- 2026-04-11: Added a direct multi-agent execution packet for
  `Source Intelligence V1 M1`, including coding/review/testing/evolution
  briefs. The line can now be delegated without rebuilding packet structure
  from the surrounding strategy docs.
- 2026-04-11: Added a compact execution/review package entry so the current
  `Source Intelligence V1 M1` execution wave and `Agent Harness Boundary Proof`
  result wave can be sent to other models or weekly review as one package.
- 2026-04-11: Added `.runtime/delegation` entrypoints for
  `Source Intelligence V1 M1` across coding/review/testing/evolution so the
  current packet can be executed directly without rebuilding prompts from docs.
- 2026-04-11: Added direct Claude send packages for the current
  `Source Intelligence V1 M1` lane and `Agent Harness Boundary Proof` lane, so
  these packets can now be handed to Claude Code without extra controller-side
  repackaging.
- 2026-04-11: Started the first real Claude worker coding run for
  `Source Intelligence V1 M1` under the external run root. Initial status is
  `running`; detached wait timeout was observed but does not indicate failure.
- 2026-04-11: Added a durable delivery-governance baseline to prevent AI
  coding acceleration from outrunning recoverability. The project now has
  explicit controller documents for:
  - environment separation
  - change promotion gates
  - release and rollback discipline
  plus a compact governance index linked from the mainline map and agent
  harness contract.
- 2026-04-11: Extended the governance baseline with implementation-facing
  delivery controls:
  - staging / production identity plan
  - release promotion checklist
  - backup and restore inventory
  - updated P1 implementation queue
  This turns the governance layer from principles-only into a concrete next
  execution set for environment separation and release discipline.
- 2026-04-11: Added an explicit project-governance <-> runtime alignment
  baseline. The project now has durable controller docs explaining:
  - why current governance is a pre-runtime shell rather than a parallel system
  - how task / decision / memory / work-context concepts should align
  - how memory tiers should be separated so chat is not treated as canonical
    memory
  - what the first concrete alignment queue should be
- 2026-04-11: Added a unified task-landscape controller map so the project now
  has one durable place to judge:
  - what is the true mainline
  - what is support work
  - what is research work
  - whether each line is actually on track
  This is intended to reduce project drift from “many important threads” being
  treated as if they were all equal-priority mainlines.
- 2026-04-11: Added first concrete environment config templates for
  `staging-runtime` and `prod-runtime` under `config/runtime/`, so the
  governance line now has direct configuration landing points rather than only
  policy docs.
- 2026-04-11: Added a repeatable research pipeline and output templates for the
  thinking-armory / methodology study line. This narrows that line from
  open-ended reading into explicit batch-review -> synthesis -> retention
  closure.
- 2026-04-11: Absorbed the project-level strategic review into a controller
  action document. The review's main accepted effects are:
  - Runtime v0 now needs an explicit exit criterion
  - Source Intelligence must stop remaining a known bottleneck without an
    implementation start packet
  - documentation scale now needs active-surface compression rather than just
    continued growth
- 2026-04-11: Added an explicit `Runtime v0` exit-criteria document and a
  separate single-controller continuity risk note. This turns two strategic
  concerns into durable controller artifacts instead of leaving them as review
  commentary.
- 2026-04-11: Added durable `R2-I18` controller acceptance record boundary
  support:
  - new helper: `runtime/controller_acceptance.py`
  - new inspect route:
    `POST /api/ike/v0/runtime/service-preflight/controller-decision/record/inspect`
  - new explicit record route:
    `POST /api/ike/v0/runtime/service-preflight/controller-decision/record`
  The implementation reuses existing runtime truth tables, keeps the scope
  fixed to `canonical_service_acceptance`, supports idempotent reuse and
  explicit supersession, and rejects writes when no runtime task exists to
  anchor the required audit event. Compile validation passed; full runtime
  test execution is still pending due environment-level timeout during local
  test execution.
- 2026-04-10: Added durable `R2-H6` controller-promotion readiness records.
  Runtime service preflight now exposes `controller_promotion` so the
  controller-facing inspect result distinguishes:
  - direct canonical-ready shapes that can be promoted now
  - reviewed Windows redirector shapes that remain promotion-eligible but
    require explicit controller confirmation
  - blocked shapes that remain non-promotable
  This remains inspect-only and does not add automatic promotion or a mutable
  controller action.
- 2026-04-10: Added durable `R2-H7` live canonical-service evidence. On the
  current local Windows environment, canonical `127.0.0.1:8000` now reaches
  the reviewed `acceptable_windows_venv_redirector` shape when code freshness
  is explicitly matched, and `controller_promotion` reports it as
  promotion-eligible with explicit controller confirmation still required.
- 2026-04-10: Added durable `R2-H8` controller decision brief consolidating
  the `R2-H5 -> R2-H7` chain. Current recommendation is
  `accept_with_changes`: treat the reviewed Windows redirector shape as the
  accepted local canonical proof baseline, while keeping the exception narrow
  and explicitly documented.
- 2026-04-10: Added `R2-I First Real Task Lifecycle On Canonical Service` as
  the candidate next runtime phase, explicitly gated on controller acceptance
  of the current `R2-H` canonical Windows proof path.
- 2026-04-10: Added a durable Claude Code provider-switching note, recording:
  - provider lookup via `cc-switch`
  - default routine preference for latest `qwen3.6`
  - manual switch path for the stronger `glm-5.1` backend/business-logic lane
- 2026-04-10: Added the candidate `R2-I` runtime planning layer:
  - phase judgment
  - phase plan
  - execution pack
  - coding/review/test/evolution briefs
  The target remains narrow: one live-service-adjacent lifecycle proof on top
  of the accepted canonical service baseline, not a broad task runner.
- 2026-04-10: Added durable `R2-I1` results for a new inspect-style runtime
  lifecycle proof route:
  - `POST /api/ike/v0/runtime/task-lifecycle/proof/inspect`
  The route is now live on the canonical local service, returns an auditable
  lifecycle proof payload, and explicitly preserves the truth boundary that it
  is inspect-only and not a general task-runner API.
- 2026-04-10: Added `R2-I2`/`R2-I3` follow-up records for the new lifecycle
  proof route, including:
  - a single-file external review pack
  - a controller review checkpoint
  - a broader targeted test slice combining the lifecycle helper and router
    surface
- 2026-04-10: Added `R2-I4` evolution judgment, clarifying that the next
  narrow runtime question is now read-surface alignment above the new proof
  route, not whether the canonical service can host the proof at all.
- 2026-04-10: Added the candidate `R2-I5 PG-Backed Lifecycle Proof` packet to
  answer the main semantic gap raised by review #11: the difference between a
  live state-machine proof and a durable PG-backed lifecycle fact path.
- 2026-04-10: Added durable `R2-I5` results for a narrow PG-backed lifecycle
  proof helper. The runtime now has one verified lifecycle path through
  `runtime_tasks`, `runtime_task_events`, `runtime_worker_leases`, and
  `PostgresClaimVerifier`, closing the main semantic gap identified by review
  #11.
- 2026-04-10: Added durable `R2-I6` read-surface alignment results above the
  new PG-backed lifecycle proof. The runtime now also has one verified path
  showing that durable lifecycle truth can be reconstructed into a work
  context, aligned onto the project pointer, and reflected by the existing
  project read surface without inventing active work.
- 2026-04-10: Added the candidate `R2-I7 DB-Backed Inspect Surface` packet so
  the next runtime step is explicitly framed as controller-visible inspection
  of the durable proof path, not a drift into general execution semantics.
- 2026-04-10: Added durable `R2-I7` results for a bounded controller-facing
  DB-backed proof inspect route:
  - `POST /api/ike/v0/runtime/task-lifecycle/db-proof/inspect`
  The route truthfully exposes one persisted proof-shaped lifecycle result and
  explicitly states that it is inspect-only, bounded, non-detached, and not a
  general task runner.
- 2026-04-10: Added the candidate `R2-I8 Repeated Proof Hardening` packet so
  the next runtime edge is explicitly narrowed to repeated-run safety for the
  durable proof lane rather than broader orchestration drift.
- 2026-04-10: Added durable `R2-I8` repeated-run hardening results for the
  DB-backed proof lane. The runtime test surface now explicitly proves that
  two sequential proof runs keep distinct project/task/lease/event identities
  and remain query-isolated, while still not claiming broad concurrency
  semantics.
- 2026-04-10: Added the candidate `R2-I9 Concurrent Proof Boundary` packet so
  the next runtime edge is explicitly narrowed to overlapping-run safety,
  rather than letting repeated-run success be overread as full concurrency
  capability.
- 2026-04-10: Added durable `R2-I9` overlapping-run isolation results for the
  DB-backed proof lane. The runtime test surface now explicitly proves that
  two overlapping proof runs using separate threads/sessions keep distinct
  durable identities and remain query-isolated. This also hardened the test
  cleanup path by explicitly disposing the async engine pool after the
  threaded proof.
- 2026-04-10: Added the candidate `R2-I10 Abort And Failure Boundary` packet
  so the next runtime edge is explicitly narrowed to failure honesty for the
  bounded proof lane, not broader supervision semantics.
- 2026-04-10: Added durable `R2-I10` failure-honesty results for the
  DB-backed proof helper. Failed proof runs now re-read durable task/event
  truth after rollback and report durable `final_status` plus durable
  `persisted_event_count`, instead of trusting stale in-memory ORM state.
- 2026-04-10: Added the candidate `R2-I11 Route-Level Failure Honesty` packet
  so the next runtime edge is explicitly narrowed to controller-visible route
  honesty on failure, not retries or detached supervision.
- 2026-04-10: Added durable `R2-I11` route-level failure-honesty results for
  the DB-backed proof inspect surface. The controller-visible route is now
  explicitly tested to preserve durable failure summary fields and stable
  truth-boundary flags when the bounded proof reports a partial durable
  failure.
- 2026-04-10: Added the candidate `R2-I12 Failure Review Pack` packet so the
  next runtime edge is explicitly narrowed to review packaging of the new
  failure-honesty evidence, not a fresh execution-semantics branch.
- 2026-04-10: Added durable `Review #12` absorption records for the
  `R2-I10/R2-I11` failure-honesty packet. External review converged on
  `accept_with_changes`, the requested clarification around the
  `task.__dict__` fallback has been absorbed, and the current runtime claim
  boundary remains explicitly narrow:
  - durable failure truth is improved
  - route-level failure honesty is improved
  - no broad detached supervision or scheduler claim is added
- 2026-04-10: Added the candidate `R2-I13 Live Route Freshness Closure`
  packet after observing a new canonical-service gap:
  - current code and focused tests include the DB-backed inspect route
  - canonical `127.0.0.1:8000` remains healthy
  - but the live route currently returns `404 Not Found`
  The next runtime edge is therefore no longer only semantic review
  absorption; it is live route freshness closure without widening into a broad
  service-management lane.
- 2026-04-10: Added durable `R2-I13` live route freshness-closure results.
  After a controlled canonical-service refresh, canonical `127.0.0.1:8000`
  now exposes and successfully serves the DB-backed inspect route live:
  - `POST /api/ike/v0/runtime/task-lifecycle/db-proof/inspect`
  This closes the live route freshness gap. It also clarified a narrower
  follow-up gap:
  - default preflight still leaves `code_freshness = unchecked`
  - but explicit current-fingerprint preflight reaches the reviewed
    `acceptable_windows_venv_redirector` path
- 2026-04-10: Added the candidate `R2-I14 Promotion Readiness Self-Check`
  packet so the next runtime edge is explicitly narrowed to controller-usable
  self-check of current code freshness for canonical local preflight, without
  widening into service orchestration or auto-promotion semantics.
- 2026-04-10: Added durable `R2-I14` promotion-readiness self-check results.
  Runtime service preflight now supports one explicit local self-check path:
  - `self_check_current_code = true`
  With `strict_code_freshness = true`, canonical `127.0.0.1:8000` can now
  truthfully reach the reviewed Windows redirector status without manual
  fingerprint copy/paste:
  - `controller_acceptability = acceptable_windows_venv_redirector`
  - `controller_promotion = controller_confirmation_required`
  This remains confirmation-gated and does not introduce automatic promotion.
- 2026-04-10: Added an evolution feedback routing rule for logs. Logs are now
  explicitly treated as a feedback substrate, but default triage ownership is
  assigned to a low-cost monitoring lane. The rule distinguishes:
  - acceleration degradation
  - operational degradation
  - canonical-truth risk
  and records that Redis/cache-style failures should not automatically occupy
  the controller lane.
- 2026-04-10: Added durable `P1 Minimal Log Feedback Integration` results.
  Existing collection-health and log-analysis task pathways now carry explicit
  routing metadata so Redis/cache-style failures default to low-cost monitoring
  instead of implicitly competing for controller attention, while canonical
  runtime/preflight risk remains escalatable.
- 2026-04-10: Added durable `R2-I15` controller-decision inspect results.
  Runtime now exposes one explicit controller-facing decision surface above
  preflight:
  - `POST /api/ike/v0/runtime/service-preflight/controller-decision/inspect`
  The new route makes recommendation shape and non-mutation boundary flags
  explicit, while truthfully preserving the difference between:
  - decision inspection
  - actual controller acceptance
  Live canonical `8000` now exposes the route, but the current owner chain
  still reports `blocked_owner_mismatch`, so the live recommendation remains
  `not_ready_for_controller_acceptance`.
- 2026-04-10: Added durable `R2-I16` canonical owner-chain reclaim results.
  Canonical `127.0.0.1:8000` has now been brought back onto the reviewed local
  Windows redirector shape, so live runtime preflight and the new
  controller-decision inspect route again return:
  - `acceptable_windows_venv_redirector`
  - `controller_confirmation_required`
  This also clarified an important remaining gap: the currently validated live
  Windows launch discipline aligns with the repo `uvicorn.exe` chain more
  cleanly than direct `python run_service.py`, so the documented
  `canonical_launch` baseline still needs explicit reconciliation.
- 2026-04-10: Added durable `R2-I17` canonical-launch baseline alignment
  results. The machine-readable `canonical_launch` field is now platform-aware
  and on Windows reflects the same repo `uvicorn.exe` launch chain that is
  currently validated live on canonical `8000`, while preserving fallback to
  the existing `python run_service.py` form outside that case.
- 2026-04-10: Added a controller-confirmation review pack and decision brief
  for the current `R2-I17` live runtime state, plus a gated next-phase
  judgment for `R2-I18 Controller Acceptance Record Boundary`. This keeps the
  next edge explicit without prematurely widening runtime semantics before the
  current live baseline is reviewed.
- 2026-04-10: Added a narrow plan and coding brief for `R2-I18 Controller
  Acceptance Record Boundary`. The preferred landing is now explicit:
  reuse `runtime_decisions`, `runtime_task_events`, and work-context
  `latest_decision_id` rather than opening a new approval subsystem.
- 2026-04-11: Added an explicit API contract and idempotency policy for
  `R2-I18 Controller Acceptance Record Boundary`. The next runtime packet now
  has a fixed narrow shape: separate inspect/write routes, idempotent reuse
  for repeated same-basis confirmation, explicit supersession for materially
  changed eligible basis, and explicit rejection when current truth is no
  longer confirmation-eligible.
- 2026-04-11: Added a minimal write-set boundary for `R2-I18`. The next
  packet is now constrained to a small runtime helper, a bounded router
  extension, minimal read-surface alignment, and focused tests, rather than a
  broad runtime refactor.
- 2026-04-11: Added an implementation task packet for `R2-I18` so the next
  delegated coding lane can start from one bounded handoff file instead of
  reconstructing context from scattered planning notes.
- 2026-04-10: Added a compact documentation index layer for the active
  mainline:
  - `CURRENT_MAINLINE_MAP_2026-04-10.md`
  - `CURRENT_RUNTIME_MAINLINE_INDEX_2026-04-10.md`
  - `CURRENT_RENAME_CUTOVER_INDEX_2026-04-10.md`
  - `CURRENT_AGENT_HARNESS_INDEX_2026-04-10.md`
  This is a documentation-structure hardening step to reduce controller
  overhead and avoid relying on long accumulated handoff files as the only
  navigation path.
- 2026-04-10: Extended the first machine-readable agent-harness metadata
  baseline across Claude worker, OpenClaw wrappers, and qoder with:
  - `write_scope`
  - `network_policy`
  Current defaults are now explicit at the metadata layer:
  - `coding_high_reasoning -> restricted`
  - `review_high_reasoning -> disabled`
  These fields are now durably recorded for auditability and later
  enforcement, but are not yet claimed as hard sandbox enforcement.
- 2026-04-10: Renamed the browser feed IndexedDB namespace from
  `myattention_cache` to `ike_cache` as a narrow cutover-visible identity
  cleanup. This affects only derived cache data, not durable runtime truth.
- 2026-04-10: Updated the LLM voting system prompt to identify as `IKE`
  instead of `MyAttention`, keeping the change narrow to visible model output
  while leaving logger and compatibility namespaces untouched.
- 2026-04-10: Extended practical `sandbox_identity` coverage to OpenClaw and
  qoder so Claude worker, OpenClaw, and qoder now all emit a machine-readable
  sandbox identity. This improves auditability and later enforcement
  readiness, but is not yet full sandbox lifecycle enforcement.
- 2026-04-09: Added durable `R2-H5` result records for the reviewed Windows
  redirector acceptability rule. `service_preflight` now reports
  `acceptable_windows_venv_redirector` for the narrow reviewed Option B shape,
  keeps `controller_confirmation_required = true`, and no longer reuses the
  broader `bounded_live_proof_ready` status for this canonical Windows case.
- 2026-04-09: Added durable `R2-G14` controller-acceptability rule records,
  explicitly separating:
  - canonical live proof
  - bounded alternate-port live proof
  - blocked owner-mismatch and code-freshness cases
- 2026-04-09: Added phase-level `R2-G` result records, clarifying that service
  observability and bounded fresh live proof are materially complete, while the
  remaining blocker is canonical launch-path normalization rather than missing
  service-preflight diagnosis.
- 2026-04-09: Opened `R2-H Canonical Service Launch Path Normalization` as the
  next narrow runtime phase after materially complete `R2-G`.
- 2026-04-09: Added durable `R2-H1` result records and a narrow `R2-H` plan,
  making the controller-acceptable canonical launch command machine-readable in
  `service_preflight` and visible in the settings runtime panel, while keeping
  canonical live normalization explicitly pending.
- 2026-04-09: Added durable `R2-H2` result records after a bounded canonical
  restart on `8000`, proving the canonical service now serves the latest
  preflight schema while the remaining blocker has narrowed to interpreter
  ownership drift rather than code freshness.
- 2026-04-09: Added durable `R2-H3` diagnosis records for the Windows
  parent-repo/child-system interpreter split now observed on canonical `8000`,
  preserving this as a review item instead of prematurely relaxing the
  controller acceptability rule.
- 2026-04-09: Added durable `R2-H4` diagnosis records, making the current
  parent-repo/child-system process shape machine-readable as a
  `windows_venv_redirector_candidate`, while preserving the current blocked
  controller rule pending a deliberate acceptability decision.
- 2026-04-09: Added repository/workspace isolation planning artifacts for the
  future `MyAttention -> IKE` migration, including:
  - a root restructuring plan
  - a migration inventory
  - a backup-and-rollback checklist

- 2026-04-08: Added durable `R2-G1` service-discipline evidence, clarifying
  that the current operational risk is ambiguous API ownership rather than
  permanent downtime. The controller baseline now treats repo `.venv` +
  `services/api/run_service.py` as the truthful local launch path for live
  proof.
- 2026-04-08: Added a bounded methodology PDF study packet for local Claude
  over the extracted corpus from
  `D:\BaiduNetdiskDownload\万维钢·现代思维工具100讲\PDF`, including:
  - UTF-8 extracted text artifacts in
    `.runtime/methodology-pdf-study/stable_texts`
  - a stable manifest for numbered text files
  - an active local Claude worker run to judge which tools/models are
    candidates for the future IKE thinking armory
- 2026-04-08: Added a batch-recovery plan for the methodology PDF study so the
  original full-corpus run remains preserved while narrower batch A / batch B
  review runs can complete more reliably.
- 2026-04-08: Added `R2-G2` as the next narrow runtime coding packet for
  service-preflight hardening, with an active local Claude delegated coding run
  focused on machine-readable live-proof readiness rather than new runtime
  semantics.
- 2026-04-08: Added durable `R2-G2` controller validation results for the
  service-preflight helper. The runtime can now truthfully classify live proof
  as `ready/ambiguous/down`, but current live ownership still points at system
  `Python312` rather than the preferred repo `.venv` baseline. A fresh repo
  `.venv` `uvicorn` instance on `8011` proved the new inspect route works live,
  so the remaining issue is stale service ownership rather than route logic.
  Preferred-owner mismatch is now machine-readable in the preflight output.
- 2026-04-09: Added durable detached-completion evidence for local Claude
  worker runs, confirming that several active coding/review runs still time out
  under detached wait and should not yet be treated as routine unattended
  delegated closure.
- 2026-04-08: Added durable `R2-C1` result records for the first narrow
  runtime-backed visible-surface proof, including:
  - a runtime project/work read helper
  - a narrow `ike_v0` runtime project-surface inspect route
  - settings-surface integration that truthfully shows runtime data or bounded
    unavailability
  - combined DB-backed validation at `89 passed, 1 warning`
- 2026-04-08: Added phase-level `R2-C` result records and opened
  `R2-D Runtime Project Bootstrap Alignment` as the next narrow runtime phase,
  clarifying that the next live gap is runtime project presence rather than
  visible-surface shape.
- 2026-04-08: Added durable `R2-D1` result records for an explicit runtime
  project bootstrap path, including a narrow bootstrap route and a live
  bootstrap+inspect proof for `myattention-runtime-mainline`.
- 2026-04-08: Added phase-level `R2-D` result records and opened
  `R2-E Runtime Surface Activation Narrow Integration` as the next narrow
  runtime phase, clarifying that the next gap is direct settings-surface
  usability rather than runtime project presence itself.
- 2026-04-08: Added durable `R2-E1` result records for the first explicit
  settings-surface activation proof, including:
  - a user-triggered runtime activation button in the runtime-unavailable panel
  - a narrow bootstrap call from the settings surface
  - live bootstrap + inspect validation for `myattention-runtime-mainline`
- 2026-04-08: Added phase-level `R2-E` result records, clarifying that
  runtime surface activation is now materially complete as a narrow proof and
  broader UI/runtime integration remains closed.
- 2026-04-08: Added durable `R2-F1` result records for the first visible
  benchmark-to-runtime review bridge, including:
  - a narrow benchmark candidate import endpoint
  - a settings-surface action to send the reviewed benchmark candidate into runtime review
  - explicit preservation of `pending_review` status rather than trusted-memory promotion
- 2026-04-08: Added phase-level `R2-F` result records, clarifying that the
  visible benchmark queue bridge is materially complete as a narrow proof and
  broad benchmark/runtime integration remains closed.
- 2026-04-08: Added `R2-G Runtime Service Stability And Delegated Closure Hardening`
  as the next narrow runtime phase, clarifying that the main remaining risks are
  operational reliability rather than new runtime truth semantics.
- 2026-04-08: Added durable coding-lane and worker-hardening notes:
  - `docs/IKE_RUNTIME_OPENCLAW_VS_CLAUDE_CODING_BASELINE_2026-04-08.md`
  - `docs/CLAUDE_WORKER_RUNTIME_HARDENING_REQUIREMENTS_2026-04-08.md`

- 2026-04-08: Added durable `R1-K1`, `R1-K3`, and phase-level `R1-K` result
  records, closing the read-path trust semantics phase with mixed
  delegated/controller evidence and promoting upstream relevance as the
  explicit trusted-packet rule for the current runtime read surfaces.
- 2026-04-08: Added `R2-A Runtime v0 Consolidated Readiness Review` as the
  next controller phase after materially complete `R1-K`, including phase
  judgment, consolidated review plan, and a concise runtime-v0 review pack.
- 2026-04-08: Added a single-file runtime-v0 cross-model review pack:
  - `docs/IKE_RUNTIME_V0_SINGLE_FILE_REVIEW_PACK_2026-04-08.md`
  so the current runtime base can be reviewed without assembling the full doc tree.
- 2026-04-08: Added durable `R2-A` review synthesis after returned
  cross-model review, clarifying that runtime direction remains on track but
  broader integration is still gated behind debt settlement and consolidated
  readiness judgment.
- 2026-04-08: Added `R2-A` debt-settlement records:
  - unified retained runtime notes backlog
  - formalized runtime method rules
  - durably closed the carried `force=True` review debt as a closure-discipline item
- 2026-04-08: Added `R2-A` readiness-gate result, clarifying that the runtime
  base is now a strong candidate kernel but broader integration is still gated,
  and opened `R2-B` as the next narrow runtime proof phase.
- 2026-04-08: Added a strategic scheduling note so the second concept benchmark
  and procedural memory evolution are now formally scheduled after `R2-B`
  instead of remaining implicit carry items.
- 2026-04-08: Materialized `R2-B` into a narrow execution surface for the first
  real task lifecycle proof, with coding/review/test/evolution briefs and a
  phase execution pack.

- 2026-04-08: Added `R1-J DB-backed Runtime Test Stability Hardening` as the
  next narrow runtime phase after `R1-I`, including phase judgment, plan,
  execution pack, packet briefs, and `.runtime/delegation` entrypoints for
  coding/review/testing/evolution.
- 2026-04-08: Added durable `R1-J1` and `R1-J3` result records showing repeated
  DB-backed runtime slices are currently stable under controller reruns, so no
  new stability patch is presently justified.
- 2026-04-08: Added durable `R1-J2`, `R1-J4`, and phase-level `R1-J` result
  records, closing the narrow DB-backed stability phase with mixed
  delegated/controller evidence and promoting repeated targeted green runs as a
  valid no-patch stability-phase closure rule.
- 2026-04-08: Added `R1-K Read-Path Trust Semantics Alignment` as the next
  narrow runtime phase after `R1-J`, with phase judgment, plan, execution pack,
  packet briefs, and `.runtime/delegation` entrypoints for
  coding/review/testing/evolution.

- 2026-04-08: Added durable `R1-I1` result records after controller-side
  correction of the first operational-guardrail coding pass:
  - `docs/IKE_RUNTIME_V0_R1-I1_RESULT_MILESTONE_2026-04-08.md`
  - `docs/review-for IKE_RUNTIME_R1-I1_OPERATIONAL_GUARDRAILS_RESULT.md`
- 2026-04-08: Added durable `R1-I2` delegated review records after a real
  local Claude review run:
  - `docs/IKE_RUNTIME_V0_R1-I2_RESULT_MILESTONE_2026-04-08.md`
  - `docs/review-for IKE_RUNTIME_R1-I2_OPERATIONAL_GUARDRAILS_REVIEW_RESULT.md`
- 2026-04-08: Added durable `R1-I3` testing records for operational guardrails:
  - `docs/IKE_RUNTIME_V0_R1-I3_RESULT_MILESTONE_2026-04-08.md`
  - `docs/review-for IKE_RUNTIME_R1-I3_OPERATIONAL_GUARDRAILS_TEST_RESULT.md`
- 2026-04-08: Added durable `R1-I4` evolution records and phase-level
  `R1-I` milestone:
  - `docs/IKE_RUNTIME_V0_R1-I4_RESULT_MILESTONE_2026-04-08.md`
  - `docs/review-for IKE_RUNTIME_R1-I4_OPERATIONAL_GUARDRAILS_EVOLUTION_RESULT.md`
  - `docs/IKE_RUNTIME_V0_R1-I_RESULT_MILESTONE_2026-04-08.md`

- 2026-04-08: Marked `R1-H` materially complete for the current delegated-evidence
  recovery scope and opened the next runtime phase:
  - `R1-I Operational Guardrail Hardening`
  - added phase judgment, plan, packet briefs, execution pack, and
    `.runtime/delegation` entrypoints for `R1-I1 ~ R1-I4`

- 2026-04-08: Completed the `R1-H` recovery wave for `R1-D` using local
  Claude delegated artifacts:
  - `R1-D2` review recovered
  - `R1-D3` testing recovered
  - refreshed phase evidence now shows `R1-D`, `R1-E`, `R1-F`, and `R1-G`
    are all fully delegated across coding/review/testing/evolution
  - `R1-H` can now be treated as materially complete for the current recovery
    scope
  - added durable recovery note:
    - `docs/IKE_RUNTIME_V0_R1-H_R1-D_RECOVERY_RESULT_2026-04-08.md`

- 2026-04-08: Completed the `R1-H` recovery wave for `R1-E` using local
  Claude delegated artifacts:
  - `R1-E2` review recovered
  - `R1-E3` testing recovered
  - `R1-E4` evolution recovered
  - refreshed phase evidence now shows `R1-E` is fully delegated across
    coding/review/testing/evolution
  - `R1-D` is now the next `R1-H` recovery target
  - added durable recovery note:
    - `docs/IKE_RUNTIME_V0_R1-H_R1-E_RECOVERY_RESULT_2026-04-08.md`

- 2026-04-07: Completed `R1-G1` review provenance hardening:
  - tightened `transition_to_review(...)` metadata with:
    - `review_submitted_by_id`
    - nested `review_submission`
  - made `transition_packet_to_review(...)` derive review provenance from the
    packet's real creator role/id instead of hardcoding `delegate`
  - added malformed attribution rejection for empty review-submission actor ids
  - included `test_runtime_v0_project_surface.py` in shared runtime table
    cleanup to remove a previously observed cross-suite DB-backed interaction
  - validation passed with:
    - `3 passed, 48 deselected, 1 warning`
    - `2 passed, 8 deselected, 1 warning`
    - `4 passed, 1 warning` for standalone `project_surface`
    - `65 passed, 1 warning` for the combined
      `project_surface + operational_closure + memory_packets` slice

- 2026-04-07: Added durable `R1-G` result records and controller fallback
  review/testing/evolution coverage so review-provenance hardening no longer
  depends on chat-only controller state.

- Added `docs/IKE_RUNTIME_V0_R1-E1_RESULT_MILESTONE_2026-04-07.md` and
  `docs/review-for IKE_RUNTIME_R1-E1_PROJECT_SURFACE_ALIGNMENT_RESULT.md` so
  the first `R1-E` result is durable and does not depend on chat-only controller
  state.

- Added `docs/IKE_RUNTIME_V0_R1-E_RESULT_MILESTONE_2026-04-07.md` plus
  controller fallback records for:
  - `R1-E2` review
  - `R1-E3` testing
  - `R1-E4` evolution
  so the `R1-E` phase now has durable phase-level review coverage even without
  recovered independent delegated lane artifacts.

- Added the next runtime phase judgment and packet set for:
  - `R1-F Controller Runtime Read Surface`
  so the mainline now moves from project-pointer alignment to one narrow
  controller-facing runtime read surface without opening broader UI/API work.

- Materialized `R1-F` into `.runtime/delegation` entrypoints for:
  - `R1-F1` coding
  - `R1-F2` review
  - `R1-F3` testing
  - `R1-F4` evolution
  so the next runtime phase now has an execution surface, not just docs-level
  phase judgment.

- 2026-04-07: Completed `R1-F1` controller runtime read surface:
  - added `services/api/runtime/project_surface.py`
  - added `services/api/tests/test_runtime_v0_project_surface.py`
  - proved controller-facing current project visibility can be assembled from
    existing runtime truth only
  - validation passed with:
    - `4 passed, 1 warning`
    - `101 passed, 1 warning` on the combined truth-adjacent slice
- 2026-04-07: Added durable `R1-F` result records and controller fallback
  review/testing/evolution coverage so the full phase no longer depends on
  chat-only controller state.

- Added the next runtime phase judgment and packet set for:
  - `R1-G Review Provenance Hardening`
  so the mainline now moves from controller-facing read visibility to narrower
  review/acceptance attribution hardening without widening the platform.

- Materialized `R1-G` into `.runtime/delegation` entrypoints for:
  - `R1-G1` coding
  - `R1-G2` review
  - `R1-G3` testing
  - `R1-G4` evolution
  so the new phase has an execution surface immediately instead of only docs.

- Added `docs/IKE_RUNTIME_V0_R1-C5_ASSIGNMENT_TRUTH_OPTIONS.md` to turn the
  `R1-C5` assignment-truth ambiguity into explicit controller options and a v0
  recommendation instead of leaving it as an implicit coding assumption

- Added `docs/IKE_RUNTIME_V0_R1-C5_C6_DIAGNOSIS_2026-04-07.md` to record the
  controller-side truth that:
  - `R1-C6` is a concrete pytest DB-harness restoration task
  - `R1-C5` is still blocked on clarifying explicit assignment truth in the
    runtime schema

- Added `docs/IKE_RUNTIME_V0_R1-C1_RESULT_MILESTONE_2026-04-07.md` and
  `docs/review-for IKE_RUNTIME_R1-C1_TRUTH_LAYER_RESULT.md` so the current
  truth-layer hardening result is durable and no longer depends on chat history
  or a partially populated delegation result template

- 新增受控任务外包策略文档，明确主控不外包、结构化交接、结果回收与版本记录要求
- 新增第一批受控外包任务候选清单，用于把高 token 的 coding/review/research 子任务纳入多脑协作试点
- 新增程序性知识架构文档，明确自然语言 SOP、Method、Playbook、Skill、Policy 属于正式知识层并应进入版本与评估体系
- 新增项目总计划，统一主线目标、核心模块、研发流程和测试要求
- 新增信息流数据架构设计，明确 `raw_ingest / feed_items / feed_enrichments / feed_aggregates`
- 新增存储层架构设计，明确 `PostgreSQL + Redis + Qdrant + Object Storage`
- 新增研发方法与质量保障体系，明确方案先行、设计先行、测试门槛和进化闭环
- 新增变更与版本管理规则，明确项目版本、架构版本、进化策略版本和记录要求
- 新增 `ObjectStore` 抽象与 `LocalObjectStore` 本地实现
- 新增 `raw_ingest` ORM 模型、SQL 迁移和原始层写入服务
- 新增 `/api/feeds/import` 的原始层持久化接入，保留现有缓存注入行为
- 新增跨平台运行配置：`config/runtime/local-process.toml`、`container.toml`、`distributed.toml`
- 新增本机 override 示例：`config/runtime/local-process.local.example.toml`
- 新增跨平台开发包装脚本，覆盖 Windows PowerShell、Linux shell 和 macOS `.command`
- 新增前端环境模板：`services/web/.env.local.example`
- 新增启动器日志目录与查看能力：`.runtime/logs/` 和 `manage.py logs <component>`

### Changed

- 2026-04-08: Narrow-corrected `R1-I1` operational guardrails:
  - fixed wrong-project explicit-alignment test setup
  - stabilized upstream relevance reason strings to enum-name labels
  - validation now passes with:
    - `23 passed, 1 warning`
    - `114 passed, 1 warning` on the combined
      `operational_closure + work_context + memory_packets` slice

- 2026-04-07: Completed `R1-E1` project-surface alignment:
  - `RuntimeProject.current_work_context_id` can now be aligned to the
    runtime-owned active `RuntimeWorkContext`
  - project-facing current active work can be resolved through the project
    pointer without introducing a second truth source
  - corrected two narrow issues during controller validation:
    - JSON serialization for alignment metadata timestamps
    - DB-backed test fixture update path that violated the existing
      `DONE -> result_summary` constraint
  - validation now passes with:
    - `8 passed, 1 warning` for the narrow `operational_closure` suite
    - `97 passed, 1 warning` for the combined
      `operational_closure + work_context + memory_packets` slice

- 2026-04-07: Completed `R1-C7` truth-surface cleanup:
  - removed deprecated `allow_claim` from
    `runtime.state_machine.validate_transition`
  - updated runtime tests so `allow_claim` is now rejected rather than treated
    as a compatibility no-op
  - claim-related runtime suites remain green with `194 passed, 1 warning`

- 2026-04-07: Completed `R1-C5` narrow Postgres-backed claim-truth integration:
  - added `services/api/runtime/postgres_claim_verifier.py`
  - explicit assignment now verifies through `runtime_tasks.owner_kind/owner_id`
  - active lease now verifies through `runtime_tasks.current_lease_id` plus
    `runtime_worker_leases`
  - added `services/api/tests/test_runtime_v0_postgres_claim_verifier.py`
  - targeted verifier suite passes with `4 passed, 1 warning`
  - combined narrow DB-backed runtime evidence passes with
    `57 passed, 1 warning`
  - materialized the next narrow follow-up as:
    - `docs/IKE_RUNTIME_V0_R1-C7_ALLOW_CLAIM_REMOVAL_PLAN.md`
    - `docs/IKE_RUNTIME_V0_PACKET_R1-C7_CODING_BRIEF.md`

- 2026-04-07: Completed `R1-C6` DB-backed schema-foundation restoration:
  - restored local Postgres reachability
  - applied runtime kernel migration `013`
  - added repo-level pytest fixture support in
    `services/api/tests/conftest.py`
  - aligned schema-foundation test fixtures with runtime truth
  - `services/api/tests/test_runtime_v0_schema_foundation.py` now passes with
    `53 passed, 1 warning`

- 2026-04-07: Reordered `R1-C` narrow follow-ups based on controller diagnosis:
  - `R1-C6` now comes first because wide runtime DB failures are a real
    fixture/harness gap
  - `R1-C5` now uses `runtime_tasks.owner_kind/owner_id` as the `v0`
    explicit-assignment truth source once `R1-C6` is complete

- 2026-04-07: Controller-corrected `R1-C1` truth-layer coding so runtime claim
  semantics now align on one rule:
  - executable `allow_claim=True` access is closed for CLAIM_REQUIRED transitions
  - `TransitionRequest` now carries `claim_context`
  - `ClaimVerifier` / `InMemoryClaimVerifier` now define the runtime truth
    adapter boundary
  - narrow runtime validation passed with `256` tests
  - wider runtime sweep revealed a separate DB fixture/environment gap
    (`417 passed, 35 errors`) rather than a proven truth-layer regression

- 2026-04-07: Materialized `R1-C` into executable `.runtime/delegation`
  entrypoints for coding, review, testing, and evolution, and added
  `docs/IKE_RUNTIME_V0_R1-C_EXECUTION_PACK_2026-04-07.md` as the single-file
  controller/review/execution handoff for the truth-layer phase.

- Re-audited `IKE Runtime v0` `R1-B` against the current live repo state and
  recorded the truthful controller judgment:
  - lifecycle component semantics already exist in runtime logic/tests
  - `R1-B1` now has a dedicated lifecycle-proof test artifact
  - controller live pytest validation passed across lifecycle/state/event suites
  - delegated `R1-B2` review and `R1-B4` evolution still timed out without durable results
  - controller fallback review/evolution were recorded so the lifecycle-proof milestone is still reviewable
  - the active gap is now delegated reviewer/evolution lane recovery rather than more planning

- Added a first-class independent testing-leg document and validation matrix so
  coding, review, and testing are no longer treated as the same function in
  current project delivery
- Added a project-level durable-recording and Git-discipline rule so important
  controller judgments, review outcomes, and reusable method changes no longer
  depend on chat history or long-lived dirty working trees alone
- Added a first-class evolution-loop and method-upgrade document so reviewed
  closures, future-preserve findings, and procedural memory candidates have a
  durable promotion path instead of living only in controller judgment
- Updated the project harness contract to explicitly require independent testing
  and independent evolution legs for the current project method
- Added both the independent testing leg and independent evolution leg to the
  long-horizon backlog/current method structure so they are preserved as active
  project directions
- Added a concrete second-wave runtime hardening plan so the project now moves
  from first-wave kernel execution into:
  - claim/trust/migration hardening first
  - then one real task lifecycle proof
  - then narrow kernel integration
  instead of drifting into premature platform expansion
- Added a multi-agent second-wave runtime cycle so hardening is now explicitly
  structured as:
  - coding
  - review
  - testing
  - evolution
  rather than only a coding packet followed by ad hoc controller follow-up
- Materialized the first second-wave runtime hardening packet into
  `.runtime/delegation`, including a coding brief, context packet, result
  template, and stable review-result file for `R1-A1`
- Materialized the remaining `R1-A` multi-agent runtime hardening packets into
  `.runtime/delegation` for:
  - review
  - testing
  - evolution
  so second-wave now has a complete bounded collaboration cycle
- Executed `R1-A1` second-wave hardening via delegate and recorded controller
  review with `accept_with_changes`; the patch materially tightened claim/trust
  semantics but still preserves two known soft spots:
  - `role=None` legacy force-path softness
  - caller-supplied upstream verifier trust
- Restored the broken `openclaw-kimi` review/evolution lane by correcting the
  underlying OpenClaw agent model route, then verified both review and
  evolution packets execute successfully again
- Cleaned up OpenClaw alias semantics so the active lanes are now:
  - primary coding: `openclaw-glm`
  - primary review/evolution: `openclaw-kimi`
  - backup coding: `openclaw-coder` (`qwen3.6-plus`)
  - backup review: `openclaw-reviewer` (`qwen3.6-plus`)
- Executed the independent `R1-A3` hardening test packet and recorded durable
  test evidence:
  - `36` state-machine tests passed
  - `49` memory-packet trust tests passed
  - `7` migration-validation-support tests passed
  The remaining second-wave weaknesses are now explicitly tested residual risks,
  not unvalidated assumptions
- Added a single-file `R1-A` result milestone plus matching `review-for ...`
  template so future cross-model review can start from one durable second-wave
  summary instead of four separate packet result files
- Added the next narrow second-wave enforcement cycle so runtime work does not
  jump into `R1-B` prematurely; materialized:
  - `R1-A5` coding
  - `R1-A6` review
  - `R1-A7` testing
  - `R1-A8` evolution
  as both docs-level packet briefs and `.runtime/delegation` entry points
- Executed `R1-A5` coding and rejected it in controller review because live
  pytest disproved two claimed closures:
  - claim hardening broke the legal claim path by binding delegate proof to role kind
  - migration-validation path normalization still resolved the wrong migration root
- Executed a narrow `R1-A5-FIX` correction pass and accepted it with changes:
  - restored the legal claim path
  - preserved closure of the `role=None` force bypass
  - fixed migration-validation path normalization so the controller-side subset now passes
- Executed `R1-A6` review and `R1-A8` evolution via `openclaw-kimi`, completing the
  second-wave enforcement cycle as a real multi-agent loop rather than controller-only follow-up
- Added the first real runtime lifecycle proof track (`R1-B`) and materialized
  its first coding packet so the mainline now moves from pure hardening into a
  narrow truthful state/event lifecycle proof
- Expanded `R1-B` from a single coding brief into a full four-leg executable
  cycle with:
  - delegate-ready review/test/evolution packets
  - a single-file execution pack
  - a result milestone file
  - a stable `review-for ...` result template
- IKE benchmark progression is now explicitly staged:
  - `B1` is treated as `signal + meaning + relevance hint`
  - `B2` is the next benchmark stage: `concept deepening + research trigger`
- The harness benchmark now produces a real three-brain report instead of only inspect-oriented internal artifacts
- `/settings/ike` now renders real bilingual benchmark body content for the
  current harness story instead of only bilingual labels
- Added a compact cross-model review packet so external review can start from
  one milestone brief and one prompt instead of the full document tree
- Added a project-specific agent harness contract for OpenClaw/Codex/Qoder
  contributors, covering task packets, review rules, truthfulness constraints,
  and bounded QA expectations
- Added `IKE Runtime v0` subproject decision, clarifying that the first runtime
  kernel of IKE must cover memory, task, decision, and work-context control
  rather than memory alone
- Clarified that task governance is now a dual-front requirement:
  it must improve both OpenClaw runtime continuity and the project's own
  controller/delegate engineering continuity
- Added a dedicated task-state and storage architecture document for
  `IKE Runtime v0`, locking in explicit task states, transition discipline,
  Postgres/Redis/object-storage responsibilities, leases, checkpoints, outbox,
  and recovery rules before implementation
- Added a companion document-and-memory governance document for `IKE Runtime v0`,
  clarifying that docs are necessary but not the runtime truth model, and that
  stable operation requires explicit separation between runtime state, artifacts,
  documents, and recall memory
- Added a research note on `MAGMA` and `Chronos`, clarifying how their
  memory ideas should influence IKE: adopt typed, temporal, event-aware, and
  relation-aware memory principles, but keep the first implementation step as a
  durable runtime state kernel rather than jumping straight to a graph-memory engine
- Added an implementation-grade data-model and transaction-boundary design for
  `IKE Runtime v0`, specifying minimum tables, transactional write units, read
  paths, leases, outbox discipline, and recovery rules before any build begins
- Added an explicit role-permission and state-transition matrix for
  `IKE Runtime v0`, clarifying which actors may move tasks, decisions, and
  memory packets between states and which transitions require controller review
- Added a focused single-file cross-model review packet for the current
  `IKE Runtime v0` design milestone so external review can target the state
  machine, permission matrix, storage split, and recovery model before
  implementation begins
- Absorbed the first external `IKE Runtime v0` review round into the design:
  - compressed the v0 task state machine
  - moved `blocked/cancelled/dropped` out of the durable v0 state list
  - added explicit `MemoryPacket` acceptance flow
  - added task-type lease-expiry recovery policy
  - added explicit JSONB discipline to prevent hidden canonical state
- Added a long-horizon backlog and decision log so strategically valuable but
  deferred directions are explicitly preserved instead of disappearing between
  review rounds
- Added a first explicit thinking-model armory document so benchmark methods,
  deep research, and runtime governance can be routed from top-layer reasoning
  models instead of only from execution habits
- Added `IKE_RUNTIME_EVOLUTION_ROADMAP.md` so `IKE Runtime` now has an
  explicit v0 -> v0.1 -> v1 -> v2 capability path instead of relying on
  short-horizon implementation docs alone
- Added `IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md` to lock the first runtime
  build slice, prerequisites, acceptance checks, and deferred work before any
  implementation begins
- Added `IKE_RUNTIME_V0_IMPLEMENTATION_PACKETS.md` to break the first runtime
  build slice into bounded controller-ready implementation packets instead of
  treating the runtime kernel as one large undifferentiated task
- Added runtime delegation prep artifacts:
  - `IKE_RUNTIME_V0_DELEGATION_BACKLOG.md`
  - `IKE_RUNTIME_V0_PACKET_R0-A_BRIEF.md`
  - `IKE_RUNTIME_V0_PACKET_R0-B_BRIEF.md`
  - `IKE_RUNTIME_V0_PACKET_R0-C_BRIEF.md`
  - `IKE_RUNTIME_V0_PACKET_R0-D_BRIEF.md`
  - `IKE_RUNTIME_V0_PACKET_R0-E_BRIEF.md`
  - `IKE_RUNTIME_V0_PACKET_R0-F_BRIEF.md`
  - `IKE_RUNTIME_V0_FIRST_WAVE_PACKET_INDEX.md`
  so the first runtime packet can be handed to a coding delegate without
  reinterpreting the full design tree on the fly
- Materialized the first runtime delegation packet into `.runtime/delegation`:
  - `briefs/ike-runtime-r0-a-core-schema-glm.md`
  - `contexts/ike-runtime-r0-a-core-schema-glm.md`
  - `results/ike-runtime-r0-a-core-schema-glm.json`
  so `R0-A` no longer exists only as design intent
- Materialized the second runtime delegation packet into `.runtime/delegation`:
  - `briefs/ike-runtime-r0-b-task-state-semantics-glm.md`
  - `contexts/ike-runtime-r0-b-task-state-semantics-glm.md`
  - `results/ike-runtime-r0-b-task-state-semantics-glm.json`
  so compressed task-state semantics now also have an executable handoff form
- Materialized the third runtime delegation packet into `.runtime/delegation`:
  - `briefs/ike-runtime-r0-c-events-leases-glm.md`
  - `contexts/ike-runtime-r0-c-events-leases-glm.md`
  - `results/ike-runtime-r0-c-events-leases-glm.json`
  so the first lease/recovery packet now also has an executable handoff form
- Materialized the remaining first-wave runtime delegation packets into
  `.runtime/delegation`:
  - `ike-runtime-r0-d-work-context-glm`
  - `ike-runtime-r0-e-memory-packets-glm`
  - `ike-runtime-r0-f-redis-rebuild-glm`
  so the full first-wave runtime kernel packet set now has executable handoff forms
- Added `IKE_RUNTIME_V0_IMPLEMENTATION_EXECUTION_PACK_2026-04-05.md` as a
  single-file review/execution pack for the whole first-wave runtime kernel,
  combining packet order, review focus, and concrete handoff links
- Added a blank review-result template:
  - `docs/review-for IKE_RUNTIME_V0_IMPLEMENTATION_EXECUTION_PACK_2026-04-05.md`
  so future cross-model reviews can be recorded with stable naming instead of
  ad hoc chat-only responses
- Absorbed the first review of the runtime implementation execution pack:
  - added global stop conditions
  - expanded `R0-A` so the first schema packet covers the full first-wave table footprint
  - added reconstruction/trust-boundary proof expectations for `R0-D` and `R0-E`
  - added explicit controller pre-review reminders for `R0-B` and `R0-E`
- Updated the review process so every meaningful review must now produce both:
  - `now_to_absorb`
  - `future_to_preserve`
  and added runtime-review-derived future items into the long-horizon backlog
- Added a stable review template for the first runtime execution packet result:
  - `docs/review-for IKE_RUNTIME_R0-A_CORE_SCHEMA_RESULT.md`
- Recorded previously chat-only cross-model review artifacts into the durable
  handoff reference set so they are less likely to disappear between sessions
- Added follow-up planning after the latest B4 review:
  - an entity-judgment strengthening plan
  - a second-benchmark selection plan to reduce method overfitting to `harness`
- Added a controller note for the first B5 harness entity review and recorded
  the current truthful baseline that `harness` still has no justified
  `concept_defining` entity
- Added a second-benchmark shortlist with `agent memory` as the current
  preferred next candidate

- 主架构文档已明确对象存储属于正式存储层，不再仅隐含在专项设计中
- 部署文档已补充开发期 `LocalObjectStore` 和生产期 `MinIO / S3 / OSS` 的扩展路径
- 项目文档体系已明确：中大型改动必须先确认方案和设计，再开始编码
- 信息流 Phase 1 已从纯规划进入首批代码落地阶段
- `manage.py` 已重构为跨平台、配置化的运行控制面，支持 `setup/start/stop/status/health`
- 旧 `start.bat` 已从硬编码 Docker 启动脚本收敛为薄包装入口
- `manage.py` 已进一步改为直接执行命令并修正运行状态判定，`status` 现在以健康检查补足 dev 进程派生场景
- 当前开发机 `local-process` 已接入真实 PostgreSQL/Redis 本机进程启动命令
- Web 本机启动已切换为更稳定的后台服务模式，并支持 standalone 产物启动
- 前端知识库页面类型定义已修复，`npm run build` 可通过
- `manage.py health` 已纳入 `auto_evolution` 聚合状态
- API / Web 启动方式已调整为后台运行并自动落盘 stdout/stderr，减少黑色窗口依赖
- 新增独立 `runtime_watchdog.py`，本机运行现在可由守护进程巡检 `postgres/redis/api/web/auto_evolution`
- `manage.py` 已支持 `start/stop watchdog`、`start/stop infra`、`start/stop postgres`、`start/stop redis`
- Windows 停止受控进程已改为优先使用 `taskkill /T /F`，减少后台残留
- `local-process` 默认 API 命令已切为非 `--reload` 的后台托管模式，避免后台运行产生多余控制台与派生进程
- PostgreSQL 本机 override 已改为优先直接启动 `postgres.exe`，减少通过 `pg_ctl` 间接拉起时的额外控制台包装
- 本机启动策略已调整为“应用层托管、基础设施显式启动”：
  - `start dev` 默认不再自动拉起 `postgres/redis`
  - `watchdog` 默认不再自动重启 `postgres/redis`
  - API 已恢复为由 `manage.py status` 准确显示 `pid/meta/log_path`
- `manage.py` 已支持基于配置的 Windows Service 基础设施托管，当前本机 PostgreSQL / Redis 已切到 service 模式
- `manage.py logs postgres|redis` 现在可读取配置中的真实服务日志路径
- 新增服务化部署专项文档 `docs/SERVICE_DEPLOYMENT_ARCHITECTURE.md`
- 新增 Windows / Linux / macOS 服务模板目录 `scripts/services/`
- `manage.py status` 已显式展示基础设施运行模式与 service 信息
- `manage.py` 已支持 `api/web/watchdog` 的可选 service 模式识别与控制
- 新增 Windows 应用层 NSSM 模板脚本，用于后续将 API / Web / Watchdog 注册为服务
- 已确认当前黑色窗口问题与 API 的 `process` 模式相关，而不是 PostgreSQL / Redis service
- `manage.py status` / `health` 现已支持识别“配置为进程模式但机器上仍残留旧 service”的状态
- 当前稳定 Windows 本机方案已收敛为：
  - `postgres / redis / web / watchdog` 使用 service
  - `api` 保持 `manage.py` 后台进程
  - 失败的 `MyAttentionApi` service 不再作为当前基线
- `LocalObjectStore` 现已保存 `.meta.json` 侧车元数据，`head()` 可返回 `content_type / content_encoding`
- `raw_ingest` 对象 key 已改为 Windows 安全、稳定可重放的格式，不再把 URL 直接落为文件名
- `storage` 与 `feeds` 包入口已改为惰性导出，降低测试与工具链对重依赖模块的耦合
- 新增 Phase 1 最小自动化测试，覆盖对象存储元数据和原始对象 key 生成
- 新增 `services/api/feeds/persistence.py`，提供导入来源解析与 `feed_items` 持久化能力
- `/api/feeds/import` 已从“原始层 + 缓存”升级为“原始层 + `feed_items` + 缓存”双写
- 导入响应新增 `persisted` 计数，用于区分缓存注入和事实层落库
- 已对齐 `FeedItem.metadata` 列映射，以及 `sources` 表相关 PostgreSQL enum 名称，修复真实库环境下的落库失败
- 已通过真实烟测验证：导入新条目时会自动创建/复用 `sources`，并写入 `feed_items`
- `/api/feeds` 已支持 `cache / db / hybrid` 读取模式，默认走 `hybrid`
- `/api/feeds` 的 `source_id` 过滤已兼容抓取器 source key 与数据库 source 记录
- 导入链路已改为逐条 nested transaction，避免单条失败把整个 session 打成 pending rollback
- 新增 `feeds_read_backend` 配置项，用于控制默认信息流读取后端

### Notes

- 当前仍处于架构与实施设计收敛阶段，后续阶段性交付建议继续以 `Unreleased` 累积，待形成明确里程碑后再切分版本号
- 本机进程模式当前已具备统一控制入口，但基础设施自动拉起仍依赖本机 override 配置补齐启动命令
- 当前机器已经完成 PostgreSQL、Redis、API、Web 的本机进程拉起，`manage.py health --json` 返回整体 `healthy`
- 当前仅剩一个可见 `cmd.exe` 为外部 Ollama 相关进程，不属于 MyAttention 启动链
- 当前机型的 PostgreSQL / Redis 已以 Windows Service 方式运行，进一步降低黑色控制台窗口出现概率
- Added feed collection health monitoring, including `GET /api/evolution/collection-health`, `GET /api/feeds/health`, and system status integration.
- Added durable import status tracking on `raw_ingest`, including `persisted / duplicate / error` states and trace metadata back to `feed_items`.
- Backfilled legacy `raw_saved` rows that could be matched to existing `feed_items`, reducing false degradation in collection health reporting.
- Added collection-health-to-task-center wiring, so `auto_evolution` can create deduplicated `system_health` tasks when feed collection degrades.
- Added tests for collection health issue generation and confirmed that healthy collection snapshots do not create unnecessary tasks.
- Added source-level collection diagnostics (`pending_sources_1h`, `error_sources_24h`) to collection health snapshots and task payloads.
- Fixed a local Windows frontend runtime regression where the residual `MyAttentionWeb` service kept serving `.next/standalone/server.js` instead of the current source frontend.
- Updated `manage.py` to stop residual process-mode web services before launch, validate stale Windows PIDs via `tasklist`, and resolve npm scripts as `npm.cmd run <script>` in detached mode.
- Reset local web startup back to process-mode source launch, restoring the expected current frontend on port `3000`.
- Closed the MVP self-evolution loop for feed collection health: `system_health` tasks can now auto-trigger the pipeline, verify recovery through collection health, and persist remediation evidence in task history.
- Added `/api/evolution/mvp-status` as a trial-run status surface for self-test, collection health, pipeline state, recent actions, and active blockers.
- Updated collection health issue generation so feed collection degradations are auto-processible by the self-evolution task pipeline.
- Fixed a runtime reliability gap where `MyAttentionWatchdog` had been installed as a manual-start service, allowing the frontend to stay down with no active recovery process.
- Hardened Windows service installation so `MyAttentionApi`, `MyAttentionWeb`, and `MyAttentionWatchdog` now use auto-start plus service failure restart policies.
- Verified watchdog-based frontend recovery by stopping `web` and confirming the watchdog restarted it successfully.
- Promoted the live `MyAttentionPostgres` and `MyAttentionRedis` services to `AUTO_START` with failure restart policies so a reboot no longer leaves core infrastructure down by default.
- Fixed conversation/message ORM drift against PostgreSQL by mapping `Conversation.extra` and `Message.extra` back onto the existing `metadata` columns.
- Restored `use_voting=true` conversation creation and conversation listing after the schema mismatch had broken the chat conversation layer.
- Added browser-based UI smoke checks for `/chat` and `/evolution`, and wired them into `auto_evolution` self-test instead of relying only on API/status probes.
- Added `POST /api/evolution/self-test/run` and an evolution dashboard action so self-test can be triggered on demand.
- Fixed `chat-voting-canary` false negatives by validating the real voting chain up to synthesis start, rather than waiting for the entire long-form final answer to finish streaming.
- Added `docs/TASK_AND_WORKFLOW_MODEL.md`, defining first-class `Context / Task / Artifact / Event / Relation` objects, four task classes, explicit state transitions, and daemon-task modeling.
- Added `docs/BRAIN_CONTROL_ARCHITECTURE.md`, defining `Brainstem / Cerebellum / Cortex`, chief-plus-specialist roles, controlled collaboration topology, and fallback/degrade paths.
- Added `docs/VERSIONED_INTELLIGENCE_ARCHITECTURE.md`, formalizing versioned cognition, method, task, knowledge, and memory objects beyond plain code versioning.
- Added `docs/TEMPORAL_AND_VERSIONED_DATA_RESEARCH.md`, clarifying temporal data categories, shared time-field semantics, and why TSDB should not be introduced prematurely.
- Added migration `migrations/007_task_brain_foundation.sql`, extending the legacy task system with `task_contexts`, task workflow columns, artifacts, relations, and brain control plane tables.
- Added ORM foundation for the first control-plane implementation in `services/api/db/models.py`, including `TaskContext`, `TaskArtifact`, `TaskRelation`, `BrainProfile`, `BrainRoute`, `BrainPolicy`, and `BrainFallback`.
- Added `services/api/brains/control_plane.py` with default brain profile and route seeds for `brainstem`, `chief`, `dialog`, `source_intelligence`, `research`, `knowledge`, `evolution`, and `coding`.
- Added `GET /api/brains/control-plane`, which bootstraps default brain configuration on first access and returns the live control-plane view from PostgreSQL.
- Added unit coverage for the new schema and default control-plane seeds:
  - `services/api/tests/test_task_brain_foundation_models.py`
  - `services/api/tests/test_brain_control_plane_defaults.py`
- Added evolution runtime visibility endpoints:
  - `GET /api/evolution/contexts`
  - `GET /api/evolution/contexts/{context_id}`
- Reworked the evolution dashboard so it now shows live contexts, snapshots, events, artifacts, and context-level task lists instead of only summary status cards.
- Added migration `migrations/009_source_intelligence_plans.sql` for the first source-intelligence control objects:
  - `source_plans`
  - `source_plan_items`
- Added persisted source-intelligence planning APIs:
  - `POST /api/sources/plans`
  - `GET /api/sources/plans`
- Added helper coverage for evolution context summaries and source-plan strategy rules:
  - `services/api/tests/test_evolution_context_views.py`
  - `services/api/tests/test_source_plan_helpers.py`
- Added chat-side brain routing integration:
  - `services/api/brains/control_plane.py` now builds live execution plans for interactive dialog.
  - `services/api/routers/chat.py` now emits `brain_plan` over SSE and stores it in assistant-message metadata.
  - `services/api/routers/conversations.py` now returns message metadata so brain routing survives conversation reloads.
- Updated the chat UI to surface the live brain route on assistant messages, making the current route/primary brain/supporting brains visible in the conversation instead of hidden in backend logs.
- Added `services/api/tests/test_brain_execution_plan.py` to protect execution-plan selection behavior.
- Added a first source-intelligence UI surface in `services/web/components/settings/sources-manager.tsx`:
  - create source plans from topic/focus/objective
  - render persisted source plan candidates
  - promote plan items into real managed sources through the subscribe endpoint
- Extended source-plan lifecycle management:
  - `services/api/routers/feeds.py` now supports source-plan refresh and plan-item subscription endpoints
  - source-plan items now transition through visible statuses such as `active`, `stale`, and `subscribed`
  - the sources UI now supports manual plan review refresh and plan-item promotion in place
- Added source-plan version management:
  - `migrations/011_source_plan_versions.sql`
  - `source_plans.current_version / latest_version`
  - `source_plan_versions`
  - `GET /api/sources/plans/{plan_id}/versions`
  - refresh/subscribe now emit versioned diff + evaluation records instead of silently overwriting plan state
- Strengthened source-plan refresh quality gating:
  - refresh diff now tracks average authority score, evidence delta, trusted-source delta, and authority-tier regressions
  - refresh evaluation now emits structured `gate_signals`
  - the sources UI now shows recent version deltas and makes current-vs-latest version drift visible
- Connected source-plan review cadence to auto-evolution:
  - recurring scheduled refresh now runs from the auto-evolution loop
  - source plans now expose `last_reviewed_at / next_review_due_at / last_review_trigger`
  - source-plan review snapshots now persist into the `source_intelligence` runtime context
  - evolution status now reports `source_plan_review` and degrades when this recurring review loop fails
- Added `docs/VERSION_MANAGEMENT.md` to separate Git/file versioning from runtime intelligence-object versioning.
- Added canonical duplicate control for repeated source-plan creation:
  - owner keys are now ASCII-safe hashed identifiers instead of raw topic text
  - repeated `topic + focus` creation now reuses a single source plan and advances its version
  - duplicate active plans are merged toward a canonical plan and older rows are marked `inactive/merged`
  - source-plan list responses now canonicalize duplicate topic/focus entries before they reach the UI
- Improved source-intelligence and evolution UI readability:
  - source plans now separate plan summary, version history, and grouped candidate sources
  - source candidates are grouped into subscribed / watch / review sections instead of one flat list
  - evolution now adds context guidance, clearer event/artifact labels, and manual-adoption suggestions for non-automatic improvements such as UI rework
- Added attention-policy persistence and runtime selection for source intelligence:
  - `migrations/012_attention_policy_foundation.sql`
  - `attention_policies`
  - `attention_policy_versions`
  - `services/api/attention/policies.py`
- `POST /api/sources/discover` is now policy-aware:
  - returns `policy_id / policy_version / portfolio_summary`
  - candidate results now include `object_bucket / policy_score / gate_status / selection_reason`
  - discovery is no longer a pure authority sort; it now applies policy-driven portfolio balancing and gate checks
- Source-plan creation and refresh now persist attention-policy metadata into plan and item state:
  - source plans expose active policy metadata to the UI
  - source-plan items retain attention evidence such as bucket, gate status, and selection rationale
- Updated the sources UI so each plan now shows the active attention policy and current policy gate decision instead of hiding that logic in backend state.
- Promoted source discovery from pure domain identity toward object identity:
  - GitHub/GitLab/Hugging Face URLs can now normalize into `repository` objects
  - Reddit URLs can now normalize into `community` objects
  - X/Twitter profile URLs can now normalize into `person` objects
- Upgraded the method-intelligence attention policy to `v2`:
  - execution policy now carries query templates
  - default policy seeding now upgrades persisted policies instead of only creating missing rows
  - live discovery now reflects upgraded policy versions in API output
- `POST /api/sources/discover` for method topics now returns:
  - `policy_version=2`
  - policy-driven query plans
  - object-level candidates such as `repository`
  - improved portfolio summaries with clearer diversity signals
- Added source-intelligence quality drift detection to auto-evolution:
  - runtime source-plan review now audits active plans for outdated policy versions, missing required buckets, insufficient diversity, domain-only method plans, and accepted plans that still have no selected candidates
  - `api/evolution/status` now reports `source_plan_quality` alongside source-plan review
  - `api/testing/issues` now records structured `source_plan_quality` issues when legacy or low-quality plans silently drift away from current attention-policy expectations
- Added regression tests for source-plan quality issue generation in `services/api/tests/test_auto_evolution_self_test.py`.
- Fixed a missed critical chat regression on the default non-voting path:
  - persisted brain-profile defaults are now upgraded in place when shipped control-plane defaults change, preventing stale models like `qwen-max` from lingering in runtime routing
  - auto-evolution self-test now includes a dedicated `chat-single-canary` for the normal `/api/chat` path instead of only covering voting
  - widened the outer self-test HTTP session timeout so the single-chat canary is no longer falsely reported as `TimeoutError` before its own request timeout budget expires
- Verified live:
  - normal `/api/chat` streaming returns assistant content again
  - both `chat-single-canary` and `chat-voting-canary` now pass in `api/evolution/status`
- Added the next step of the evolution/source-intelligence closed loop:
  - repairable `source_plan_quality` issues are now created as `auto_processible=true`
  - auto-evolution now processes those source-plan quality tasks immediately instead of only recording them
  - repeated detections can retrigger processing rather than only increment dedupe counters
  - system-health task recovery now supports `refresh_source_plan` for source-plan quality/review issues
- Reduced false-red evolution health noise:
  - `services/api/feeds/log_monitor.py` now filters SQLAlchemy statement noise from quick health checks and error-pattern analysis
  - quick health now surfaces real runtime errors instead of hundreds of cached SQL fragments
- Closed the next evolution-loop runtime gap:
  - `services/api/feeds/ai_brain.py` now normalizes local LLM responses so providers that return plain strings no longer crash local decision routing with `'str' object has no attribute 'content'`
  - `services/api/feeds/auto_evolution.py` now uses a shorter single-chat canary prompt plus a wider timeout budget so default-chat health checks stop flapping under normal latency
  - `services/api/feeds/log_monitor.py` now filters benign asyncpg connection-termination noise produced during cancelled request cleanup, preventing quick health from staying red after successful self-tests
- Verified live:
  - `POST /api/evolution/self-test/run` returns `healthy=true`
  - `chat-single-canary` and `chat-voting-canary` both pass in the same snapshot
  - `GET /api/evolution/health/quick` now returns `status=healthy` and `critical_count=0`
- Added controlled `acpx/openclaw` delegation workaround using session-history recovery, plus a reusable helper script at `/D:/code/MyAttention/scripts/acpx/openclaw_delegate.py`.
- Added bounded delegation packet support for `acpx`/OpenClaw:
  - `scripts/acpx/openclaw_delegate.py` now supports `prompt` and `exec` modes
  - `scripts/acpx/build_context_packet.py` builds UTF-8 context packets from selected file excerpts
  - delegation guidance updated so the main controller sends constrained context instead of repo-wide free-form prompts
- Added file-based delegation runner:
  - `scripts/acpx/run_file_delegation.py`
  - delegation can now target a bounded brief/context pair and require the delegated agent to write a structured UTF-8 JSON result file
- Improved homepage feed freshness perception:
  - feed homepage now starts in time-order mode
  - added a freshness summary card showing snapshot state, latest content time, and current sort mode
  - reduced the stale-looking mismatch caused by cache-first rendering without clear user-facing status
- Verified Redis-backed feed cache is now live for source refresh:
  - `POST /api/feeds/refresh` populates `feed_cache:*` keys in local Redis
  - live cache keys now include sources such as `36kr`, `bloomberg`, and `ithome`
  - feed caching is no longer only in-process memory plus frontend local storage
- Surfaced backend feed freshness state on the homepage:
  - feed list now shows backend read mode, cache layers, last ingested item time, and 1-hour ingest counts
  - `GET /api/feeds/health` now exposes `storage.cache_layers`, including Redis when active
  - homepage freshness messaging now reflects both frontend snapshot state and backend collection state
- Tightened chat responsiveness defaults and monitoring:
  - chat UI no longer defaults to the stale `qwen-max` entry; default model is now `qwen3.5-plus`
  - evolution self-test now treats severe chat slowness as a degraded runtime condition instead of only checking for HTTP success/content presence
- Added concurrent controlled delegation routing:
  - project-level `acpx` aliases now distinguish `openclaw-qwen`, `openclaw-glm`, and `openclaw-reviewer`
  - delegation helpers now accept explicit `agent_alias` and safely emit UTF-8 JSON on Windows
  - OpenClaw `myattention-coder` agent now uses `modelstudio/qwen3.5-plus` instead of the older `qwen3-coder-plus`
- Improved source-intelligence object selection:
  - attention policy selection now dedupes by `object_key/url` instead of `domain`
  - `source-method-v1` advanced to policy version `4`
  - source discovery now recognizes `organization` objects in addition to `repository / person / community / domain`
- Added first-class frontier/change object recognition in source discovery: `release`, `event`, and `signal`.
- Upgraded attention policies: `source-frontier-v1 -> v3`, `source-method-v1 -> v6`.
- Added frontier query templates for release notes, maintainers, and community reaction signals.
- Fixed a source-discovery scoring regression that was suppressing nearly all candidates after adding person/activity signals.
- Improved method/frontier candidate quality:
  - generic media domains are now penalized in `method`/`frontier`
  - related GitHub owners can be promoted into real `person` candidates instead of staying only as relation metadata
  - `person.follow_score` now contributes to attention-policy scoring
- Upgraded `source-frontier-v1` to `v5` with explicit `signal` quota so frontier discovery can reserve room for change/reaction objects.
- Recorded a source-intelligence strategy correction:
  - sources such as `36kr` should not be treated as globally good/bad
  - source value must be evaluated by task intent and role in context
  - long-term attention design should evolve from `topic -> source` toward `object + task intent + role in context`

- Recorded a new mainline capability gap:
  - complex-source retrieval and anti-bot adaptation are still missing as first-class information-acquisition capabilities
  - current `RSS / API / generic fetch / search` paths are not sufficient for sources such as WeChat articles, social platforms, and other browser-context / dynamically rendered pages
- Added IKE review-convergence planning documents:
  - `docs/IKE_MIGRATION_EXIT_CRITERIA.md`
  - `docs/IKE_V0_1_LOOP_PLAN.md`
- Locked the next IKE milestone onto one honest, inspectable runtime loop instead of expanding transitional API breadth.
- Reaffirmed that durable `GET /{type}/{id}` retrieval is still out of scope until object access, identity, and reconstruction semantics are real.
## 2026-04-01

- planning: added `B5` continued-study plan for the `harness` benchmark after
  the first real study closure
- benchmark: locked current `harness` state to `study / partially_applicable /
  continue_study`
- benchmark: corrected `openclaw-master-skills` from
  `implementation_relevant` to `ecosystem_relevant` in the live harness
  benchmark artifacts
- docs: add entity discovery/event capture method and Claude Code reference
  plan; extend B4 evidence layers with primary local artifact and structured
  secondary interpretation
- docs: add Claude Code B1 mapping and B2 memdir study plan; prepare bounded
  delegation packet for memdir analysis
- docs: add Claude Code B2 memdir study and update reference-plan progress
- docs: add B3 prototype decision and procedural-memory v1 implementation
  packet
- 2026-04-05: Executed `IKE Runtime v0` packet `R0-A` through OpenClaw GLM and completed controller review. Accepted with changes. Recorded current absorption items and future-preserve items in the stable runtime result review file.
- 2026-04-05: Executed `IKE Runtime v0` packet `R0-B`, rejected the first result, then accepted a narrow fix with changes. Delegate claim semantics for `ready -> active` are now claim-gated rather than blanket-allowed.
- 2026-04-05: Executed `IKE Runtime v0` packet `R0-C` and accepted it with changes. Event/lease/recovery helpers are now present as the first truthful baseline for runtime auditability and recovery.
- 2026-04-05: Executed `IKE Runtime v0` packet `R0-D` and accepted it with changes. WorkContext reconstruction helpers now exist as the first truthful snapshot-carrier baseline.
- 2026-04-05: Executed `IKE Runtime v0` packet `R0-E`, rejected the first result, then accepted a narrow trust-boundary fix with changes. Accepted packets now require explicit upstream linkage before they can become trusted for recall.
- 2026-04-05: Executed `IKE Runtime v0` packet `R0-F` and accepted it with changes. Redis acceleration/rebuild now exists as a truthful command-generation baseline, while real Redis execution, observability, and tighter incremental sync discipline remain future hardening work.
- 2026-04-05: Added a single-file runtime first-wave result milestone plus matching blank review file so future cross-model review can evaluate `R0-A ~ R0-F` as one kernel baseline instead of reconstructing state from scattered packet reviews.
- Fixed OpenClaw Kimi reviewer channel drift: reviewer agents had been pinned to an invalid `bailian-coding-plan/kimi-k2.5` auth route. Switched reviewer/evolution agents back to `modelstudio/kimi-k2.5`, reset the polluted reviewer session, and restored real `R1-A2` review + `R1-A4` evolution packet execution.
- Cleaned OpenClaw local alias semantics: added `openclaw-coder`, split `openclaw-kimi` onto the dedicated `myattention-kimi-review` session, kept `openclaw-reviewer` as the generic reviewer route, and documented `openclaw-qwen` as legacy compatibility only.
- Standardized backup OpenClaw lanes on `qwen3.6-plus`: `myattention-coder` and `myattention-reviewer` now use `bailian/qwen3.6-plus`, leaving `openclaw-glm` and `openclaw-kimi` as the primary specialized lanes.
- 2026-04-07: Corrected reviewer/evolution lane config drift in local
  OpenClaw:
  - `myattention-kimi-review` restored to `modelstudio/kimi-k2.5`
  - `myattention-reviewer` restored to `bailian/qwen3.6-plus`
  - stale `bailian-coding-plan:default` session overrides cleared
- 2026-04-07: Verified both reviewer lanes with minimal prompt-mode probes and
  reran `R1-B2` review plus `R1-B4` evolution successfully. `R1-B` now has
  real delegated results on all four legs: coding, review, testing, and
  evolution.
- 2026-04-07: Added `docs/IKE_CLAUDE_WORKER_MCP_FEASIBILITY_2026-04-07.md`
  after evaluating the local Claude worker MCP package. Current conclusion:
  feasible and valuable as a new bounded coding lane, but not yet a drop-in
  replacement for the full OpenClaw stack because:
  - `claude` is not installed/on `PATH`
  - result schema still needs adaptation to project harness expectations
- 2026-04-07: Opened `R1-C` as the next active runtime phase and turned the
  remaining `R1-B` substantive changes into a narrow truth-layer packet set:
  - remove executable legacy `allow_claim=True`
  - move delegate claim truth into runtime-owned verification
  - durably absorb lifecycle-proof method rules into the project harness
# 2026-04-07

## Added

- `services/api/tests/conftest.py`
  - adds a narrow sync-style adapter over the existing async runtime DB session
    for DB-backed pytest suites

## Changed

- `IKE_RUNTIME_V0_R1-C5_C6_DIAGNOSIS_2026-04-07.md`
  - now records that `R1-C6` fixture restoration is partially complete and the
    remaining blocker is local Postgres reachability
- `CURRENT_MAINLINE_HANDOFF.md`
  - now records that `db_session` fixture absence is no longer the primary
    blocker for `R1-C6`
- `PROGRESS.md`
  - now records the narrowed `R1-C6` blocker:
    `MyAttentionPostgres` stopped / `localhost:5432` unreachable
- 2026-04-07: Accepted `R1-D Operational Closure Layer` as the next runtime
  phase after materially complete `R1-C`. Added `R1-D1 ~ R1-D4` packet briefs,
  a single-file execution pack, and `.runtime/delegation` entrypoints for the
  coding/review/testing/evolution legs. `R1-D` is intentionally narrowed to
  runtime-backed `WorkContext` reconstruction and trusted `MemoryPacket`
  promotion without introducing a second truth source.
- 2026-04-07: Executed `R1-D1` as a narrow DB-backed operational-closure proof.
  Added `runtime/operational_closure.py` plus
  `test_runtime_v0_operational_closure.py`. The runtime kernel now has a
  truthful helper path for:
  - reconstructing `WorkContext` from canonical runtime truth
  - persisting one active context per project without second-truth drift
  - promoting reviewed upstream work into trusted accepted `MemoryPacket`
    records
  Validation passed:
  - `5 passed, 1 warning` for the narrow DB-backed closure suite
  - `94 passed, 1 warning` for the combined closure/work-context/memory suite
- 2026-04-07: Added durable controller review for `R1-D1` and kept the verdict
  at `accept_with_changes`. Preserved two follow-up items without reopening the
  phase:
  - review-submission attribution in the helper is still delegate-only
  - project-level `current_work_context_id` is not yet updated by the new
    persistence path
- 2026-04-07: Added a single-file `R1-D` result milestone so the operational
  closure phase no longer needs to be reconstructed from the execution pack,
  handoff, and `R1-D1` result separately.
- 2026-04-07: Added controller-side fallback records for `R1-D2 ~ R1-D4` so
  the operational-closure phase now has durable review/testing/evolution
  judgments even before independent delegated lanes are recovered.
- 2026-04-07: Marked `R1-D` materially complete with fallback review coverage
  and opened the next narrow runtime phase:
  - `R1-E Project Surface Alignment`
  This next step is intentionally limited to project-level
  `current_work_context_id` truth alignment and controller-facing current-work
  visibility, not broad UI/runtime expansion.
- 2026-04-07: Materialized `R1-E` into a full controller-ready packet set plus
  a single-file execution pack so the next runtime phase no longer depends on
  reconstructing packet boundaries from the phase judgment alone.
- 2026-04-07: Marked `R1-G Review Provenance Hardening` materially complete
  with fallback review coverage after DB-backed proof of truthful review
  provenance. Preserved the next remaining quality gap as independent delegated
  review/testing/evolution evidence recovery, not a new runtime truth semantic
  hole.
- 2026-04-07: Opened `R1-H Independent Delegated Evidence Recovery` as the next
  active runtime phase. Added a narrow phase judgment, delegated-evidence
  recovery plan, `R1-H1 ~ R1-H4` packet briefs, a single-file execution pack,
  and `.runtime/delegation` entrypoints for coding/review/testing/evolution.
- 2026-04-07: Executed `R1-H1` as a narrow controller-facing evidence support
  slice. Added `runtime/phase_evidence.py` plus
  `test_runtime_v0_phase_evidence.py` so recent runtime phases can now be
  classified truthfully as delegated/fallback/missing based on durable
  delegated result artifacts, without introducing new runtime truth objects.
- 2026-04-07: Fixed the first durable `R1-H` recovery order after the new
  phase-evidence helper made the gap explicit. Recovery priority is now:
  - `R1-G` review/evolution
  - `R1-F` review/testing/evolution
  - `R1-E` review/testing/evolution
  - `R1-D` review/testing
  This keeps the next mainline work on independent delegated evidence recovery,
  not on reopening runtime semantics.
- 2026-04-07: Recorded `R1-H` as `in_progress` and fixed the immediate next
  concrete recovery target at `R1-G2` + `R1-G4`. Updated fallback result
  payloads for `R1-H2 ~ R1-H4` so the phase no longer depends on pending
  shells, and added durable status/next-target notes for controller handoff.
- 2026-04-08: Recovered the first `R1-H` target wave for `R1-G` using local
  Claude delegated artifacts. `R1-G2` now has a real delegated review run and
  `R1-G4` now has a real delegated evolution artifact. The refreshed phase
  evidence snapshot shows `R1-G` is fully delegated across coding/review/
  testing/evolution, and the next recovery target moves forward to `R1-F`.
- 2026-04-08: Recovered `R1-F2` and `R1-F4` using local Claude delegated
  artifacts. `R1-F` is no longer fallback-heavy; only `R1-F3` testing remains
  fallback-backed. The immediate `R1-H` next target is now narrowed to
  `R1-F3`.
- 2026-04-08: Recovered `R1-F3` using a local Claude delegated testing
  artifact. The refreshed phase evidence snapshot now shows `R1-F` is fully
  delegated across coding/review/testing/evolution, and the next `R1-H`
  recovery target moves forward to `R1-E`.
- 2026-04-08: Recorded R2-B1 lifecycle proof controller comparison and focused validation; kept scope bounded to `services/api/tests/test_runtime_v0_lifecycle_proof.py`.
- 2026-04-08: Restored the local runtime surface so controller work can continue against a live system again: web is reachable on `3000` and API health is back on `8000`.
- 2026-04-08: Added a durable `R2-B1` controller-recovered coding result plus a separate coding comparison note, preserving the distinction between a good bounded Claude diff and a completed delegated artifact.
- 2026-04-08: Added durable `R2-B3` focused test evidence (`214 passed, 1 warning`) and a dedicated `R2-B` status milestone so the phase can be tracked truthfully while review/evolution are still pending.
- 2026-04-08: Closed the `R2-B` lifecycle-proof subtrack with durable coding/review/testing/evolution records; kept `R2-B` itself open and explicitly shifted the next remaining gate item to the kernel-to-benchmark bridge proof.
- 2026-04-08: Materialized the remaining `R2-B` kernel-to-benchmark bridge target into controller-ready briefs, `.runtime/delegation` entrypoints, and a single execution pack.
- 2026-04-08: Executed `R2-B5` bridge proof and added a narrow DB-backed benchmark bridge helper plus tests. Reviewed benchmark candidates can now be imported into runtime as `pending_review` memory packets without auto-promotion to trusted recall, and the combined closure/project-surface/memory slice remains green (`87 passed, 1 warning`).
- 2026-04-08: Added durable `R2-B7` validation evidence for the bridge proof (`7 passed, 1 warning`; combined slice `87 passed, 1 warning`).
- 2026-04-08: Added durable `R2-B8` evolution guidance for the bridge proof, keeping broader integration closed while preserving the new narrow bridge rule.
- 2026-04-08: Added durable `R2-B6` review evidence and closed `R2-B` as a consolidated runtime milestone. Opened `R2-C` as the next narrow integration phase.
- 2026-04-09: Hardened `R2-G` service-preflight truth with a strict preferred-owner gate. Added optional `strict_preferred_owner` handling to `runtime/service_preflight.py`, routed it through `/api/ike/v0/runtime/service-preflight/inspect`, and proved the current `8000` surface truthfully downgrades to `ambiguous` when the live listener is the non-preferred system Python owner.
- 2026-04-09: Surfaced strict runtime service preflight on the existing settings runtime panel. `services/web/app/settings/ike/page.tsx` now loads strict preflight server-side and `ike-workspace-manager.tsx` displays the narrow machine-readable service status, preferred-owner state, and mismatch warning without widening into a broad runtime operations UI.
- 2026-04-09: Recorded that `8000` health was recovered but ownership still reclaims to system `Python312` even after an explicit clear-and-restart attempt. This is now tracked as an environment/process-discipline issue, not misreported as runtime service normalization.
- 2026-04-09: Added machine-readable owner-chain diagnosis to `runtime/service_preflight.py`. Strict live snapshots can now distinguish plain preferred-owner mismatch from the more specific `parent_preferred_child_mismatch` case seen on `8000`.
- 2026-04-09: Added machine-readable code-fingerprint and code-freshness surfacing to `runtime/service_preflight.py`, extended the preflight inspect route to carry the new fields, and surfaced `Code Freshness` on the settings runtime panel. Strict freshness mismatch can now be treated as a truthful `ambiguous` live-proof gate when an expected fingerprint is provided.
- 2026-04-09: Added explicit `host/port` targeting to the runtime service-preflight inspect route so controller live proof is no longer hardcoded to `8000`. The route capability is now real, but fresh alternate-port live proof is still blocked by launch-path and served-code drift.
- 2026-04-09: Fixed the next narrow `R2-G` target at launch-path discipline. The remaining blocker is now proving one controller-acceptable fresh launch path with current-code live route behavior, not adding more preflight fields.
- 2026-04-09: Completed a fresh alternate-port live proof on `8013`. The live route now returns the latest `owner_chain`, `code_fingerprint`, and `code_freshness` fields; with the current fingerprint supplied, code freshness closes cleanly. Remaining `R2-G` ambiguity is now isolated to launch-path / interpreter ownership drift.
- 2026-04-09: Added machine-readable `repo_launcher` evidence to `service_preflight`, exposed it through the inspect route, and surfaced it on the settings runtime panel. The remaining `R2-G` question is now controller acceptability, not missing launch-path observability.
- 2026-04-09: Added machine-readable `controller_acceptability` to `service_preflight`, exposed it through the inspect route and runtime panel, and fixed the next `R2-G` target at an explicit controller rule for `bounded_live_proof_ready`.
- 2026-04-09: Executed repository-restructure phase 1. Added a pre-migration checkpoint branch/commit, created cold and runtime backups, created a parallel clean project root at `D:\code\IKE`, rewrote OpenClaw agent workspaces to isolated roots under `D:\code\_agent-runtimes\openclaw-workspaces\...`, and moved the default Claude worker run-root out of the repo while keeping result integration compatible.
- 2026-04-09: Executed a cutover-readiness cleanup pass for the repository restructure. Hardened the isolated-workspace sync exclusions, removed copied runtime/build artifacts from `D:\code\IKE`, re-synced the parallel root/workspaces, and confirmed the new root is now materially clean.
- 2026-04-09: Added a controller inventory of rename/cutover blockers and fixed the next restructure move at a narrow phase-2 rename pass focused on service/deployment artifacts, launch-path references, and local runtime config.
- 2026-04-09: Landed the first narrow phase-2 rename patch by parameterizing the Windows service installer. `install-app-services.ps1` now defaults to `D:\code\IKE`, derives service names from `ServicePrefix=IKE`, and is future-root ready without forcing a live service rewrite.
- 2026-04-09: Landed the second narrow phase-2 rename patch by normalizing the Windows WinSW templates and Windows service README. The Windows service templates now target `D:\code\IKE` and `IKE*` application service names, while the live installed services remain unchanged.
- 2026-04-09: Landed the third narrow phase-2 rename patch by normalizing Linux systemd and macOS launchd templates. Service/deployment templates now point at `/opt/ike` and `ike`-scoped identities instead of the old `myattention` paths and labels.
- 2026-04-09: Landed the first phase-2 runtime-config normalization patch. Local runtime config defaults and docker-compose identities now point toward `IKE`, while current local infra service compatibility remains preserved where it still matters.
- 2026-04-09: Landed the first phase-2 delegation-script normalization patch. qoder bundle generators no longer hardcode the old root for handoff/AGENTS refs, the qoder delegate prompt no longer hardcodes `MyAttention`, and the default OpenClaw delegate session now uses `ike-coder`.
- 2026-04-09: Landed the first narrow phase-2 backend/runtime identity patch. API-facing service identity now uses `IKE API`, system-health container checks now accept canonical `ike-*` names with legacy alias compatibility, and the default coding DashScope model is now `qwen3.6-plus`.
- 2026-04-09: Added a durable automated reasoning baseline for the routine execution chain. OpenClaw high-thinking defaults are now explicitly recorded, Claude worker now defaults to `qwen3.6-plus`, and settings/system runtime service labels now use `IKE API`.
- 2026-04-09: Landed the narrow runtime project-key normalization patch so new visible/runtime bootstrap actions now default to `ike-runtime-mainline`.
- 2026-04-09: Landed the narrow runtime preflight test-path normalization patch. Service-preflight and router tests no longer hardcode `D:\code\MyAttention` path hints; preferred-owner, repo-launcher, and `run_service.py` fixture paths are now derived from the active repo root so the planned `D:\code\IKE` cutover does not break these test slices.
- 2026-04-09: Landed the narrow Windows uninstaller normalization patch. The app-service uninstall script now defaults to `ServicePrefix = IKE`, bringing uninstall behavior into line with the earlier install-side parameterization without touching live services by itself.
- 2026-04-09: Landed the narrow runtime visible-title normalization patch so the IKE settings runtime bootstrap action now creates `IKE Runtime Mainline` instead of `MyAttention Runtime Mainline`.
- 2026-04-09: Landed the narrow web metadata-title normalization patch so the app-level browser title now presents as `IKE - 智能决策支持系统`.
- 2026-04-09: Landed the narrow web package-identity normalization patch so the web workspace now uses `@ike/web` instead of `@myattention/web`.
- 2026-04-09: Landed the narrow sidebar-branding normalization patch so the main web sidebar and footer now present `IKE` instead of `MyAttention`.
- 2026-04-09: Landed the narrow runtime comment-normalization patch so remaining runtime/test comment examples no longer treat `D:\code\MyAttention` as the future canonical root.
- 2026-04-09: Added a durable Anthropic/CREAO agent-harness research note. The current IKE direction remains aligned, but the note makes explicit that true per-run sandbox enforcement, capability policy, and sandbox/task identity binding are still missing.
- 2026-04-09: Added a durable DeerFlow 2.0 research note. The note records DeerFlow as a strong reference for long-horizon orchestration, dynamic sub-agents, Docker-native sandboxing, and memory layering, while preserving our current rule that runtime-core hardening still comes before broader tool/plugin expansion.
- 2026-04-09: Added a durable agent-harness enforcement plan and updated the project harness contract. The next harness step is now explicit: move from path isolation alone toward sandbox identity, capability policy, and environment lifecycle separation.
- 2026-04-09: Added a durable automated-lane capability matrix and a compatibility remainder note for the repository rename stream. Remaining `MyAttention` references are now explicitly split into safe-to-rename versus compatibility-sensitive items instead of being left as an undifferentiated backlog.
- 2026-04-09: Added durable drafts for sandbox metadata and lane capability policy. The next harness hardening step is now explicitly framed as metadata-first sandbox identity plus named capability profiles, not a hand-wavy claim that isolated directories already solve sandboxing.
- 2026-04-09: Added a synthesis note for the external Windows-redirector Review #10. The review's approval of narrow Option B is consistent with current controller judgment, but its long-tail carry-forward issue list needed correction because several earlier runtime items were already materially closed later in the mainline.
- 2026-04-09: Landed a narrow chat visible-identity patch so the chat surface now defaults to `qwen3.6-plus` and stores locale under `ike.locale`.
## 2026-04-09 P2-D11 Notification Visible Identity Normalized

- durable result:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D11_NOTIFICATION_VISIBLE_IDENTITY_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D11_NOTIFICATION_VISIBLE_IDENTITY_RESULT_2026-04-09.md)
- normalized:
  - notification settings test copy now uses `IKE`
  - backend notification test titles and button text now use `IKE`
  - legacy task notification source label now uses `IKE 任务系统`

## 2026-04-09 P2-D12 Chat System Prompt Identity Normalized

- durable result:
  - [D:\code\MyAttention\docs\IKE_REPOSITORY_RENAME_P2D12_CHAT_SYSTEM_PROMPT_IDENTITY_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RENAME_P2D12_CHAT_SYSTEM_PROMPT_IDENTITY_RESULT_2026-04-09.md)
- normalized:
  - backend chat system prompt now identifies the assistant as `IKE`
  - internal `myattention.chat` logger namespace remains intentionally preserved

## 2026-04-09 Agent Harness P1 Claude Metadata Landed

- durable result:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_P1_CLAUDE_METADATA_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_P1_CLAUDE_METADATA_RESULT_2026-04-09.md)
- landed:
  - Claude worker packets and run artifacts now carry lane / reasoning / sandbox metadata
  - metadata now flows through `meta.json`, `final.json`, harness result projection, CLI start args, and persisted-run reload

## 2026-04-09 Agent Harness P1 OpenClaw Metadata Landed

- durable result:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_P1_OPENCLAW_METADATA_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_P1_OPENCLAW_METADATA_RESULT_2026-04-09.md)
- landed:
  - OpenClaw delegation entrypoints now accept explicit `lane` / `reasoning_mode`
  - wrapper output and generated prompt contract now carry those same fields

## 2026-04-10 Highest Reasoning Default Tightened

- durable result:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_HIGHEST_REASONING_DEFAULT_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_HIGHEST_REASONING_DEFAULT_RESULT_2026-04-10.md)
- landed:
  - OpenClaw verified as already using `thinkingDefault = high`
  - Claude worker and OpenClaw delegation wrappers now default `reasoning_mode` to `high`
  - controller policy now treats highest available automated reasoning as the default

## 2026-04-10 Agent Harness P1 Qoder Metadata Landed

- durable result:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_P1_QODER_METADATA_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_P1_QODER_METADATA_RESULT_2026-04-10.md)
- landed:
  - qoder bundle and launch scripts now carry explicit `lane` / `reasoning_mode`
  - qoder routine default reasoning mode is now `high`

## 2026-04-10 Agent Harness P2 Profile Defaults Landed

- durable result:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_P2_PROFILE_DEFAULTS_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_P2_PROFILE_DEFAULTS_RESULT_2026-04-10.md)
- landed:
  - Claude worker, OpenClaw, and qoder now share `sandbox_kind` / `capability_profile` defaults
  - the common delegated-run metadata vocabulary now spans `lane`, `reasoning_mode`, `sandbox_kind`, and `capability_profile`

## 2026-04-11 Claude Worker Real-Run Gap Clarified

- durable note:
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_REAL_RUN_GAP_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_REAL_RUN_GAP_2026-04-11.md)
- clarified:
  - the first real Claude worker coding run did not fail only because of a
    short detached wait window
  - the intended multi-line task packet was not delivered intact to the Claude
    session
  - detached durable finalization also did not close after owner exit

## 2026-04-11 Platform Neutralization And Linux Cutover Prep Added

- durable notes:
  - [D:\code\MyAttention\docs\IKE_PLATFORM_NEUTRALIZATION_AUDIT_2026-04-11.md](/D:/code/MyAttention/docs/IKE_PLATFORM_NEUTRALIZATION_AUDIT_2026-04-11.md)
  - [D:\code\MyAttention\docs\IKE_LINUX_CUTOVER_READINESS_2026-04-11.md](/D:/code/MyAttention/docs/IKE_LINUX_CUTOVER_READINESS_2026-04-11.md)
- clarified:
  - cross-platform intent already exists in project design
  - but active harness/runtime execution still contains Windows-heavy seams
  - Linux cutover should be treated as an active preparation track rather than
    a later cleanup

## 2026-04-11 Claude Worker P1 Hardening Packet Prepared

- durable packet:
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_CROSS_PLATFORM_HARDENING_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_CROSS_PLATFORM_HARDENING_PACKET_2026-04-11.md)
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_CODING_BRIEF_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_CODING_BRIEF_2026-04-11.md)
- narrowed:
  - the next worker hardening move is now fixed at two issues only
  - cross-platform prompt delivery
  - durable detached finalization

## 2026-04-11 Claude Worker P1 Delivery Pack Prepared

- durable packet:
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_IMPLEMENTATION_TASK_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_IMPLEMENTATION_TASK_PACKET_2026-04-11.md)
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_DELIVERY_PACK_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_DELIVERY_PACK_2026-04-11.md)
- runtime delegation entrypoints added for:
  - coding
  - review
  - testing

## 2026-04-11 Claude Worker P1 Hardening Landed

- durable result:
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_RESULT_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_RESULT_2026-04-11.md)
- landed:
  - Claude worker prompt delivery now uses a Python-controlled detached wrapper
    path for real runs
  - detached `wait` / `fetch` can now finalize from durable stdout/stderr/exitcode
    artifacts
  - focused tests passed and one real smoke run succeeded

## 2026-04-11 External Method Discovery Baseline Added

- durable docs:
  - [D:\code\MyAttention\docs\IKE_EXTERNAL_METHOD_DISCOVERY_AND_ABSORPTION_2026-04-11.md](/D:/code/MyAttention/docs/IKE_EXTERNAL_METHOD_DISCOVERY_AND_ABSORPTION_2026-04-11.md)
  - [D:\code\MyAttention\docs\IKE_HERMES_SKILL_ABSORPTION_NOTE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_HERMES_SKILL_ABSORPTION_NOTE_2026-04-11.md)
- clarified:
  - external agent systems should be absorbed through source evidence,
    runtime-behavior evidence, and agent-interview evidence together
  - Hermes is now recorded as the first formal sample in that lane

## 2026-04-11 Scope Control And Broad Strategy Review Pack Added

- durable docs:
  - [D:\code\MyAttention\docs\IKE_SCOPE_CONTROL_AND_BUILD_STRATEGY_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SCOPE_CONTROL_AND_BUILD_STRATEGY_2026-04-11.md)
  - [D:\code\MyAttention\docs\IKE_PROJECT_SCOPE_AND_STRATEGY_REVIEW_PACK_2026-04-11.md](/D:/code/MyAttention/docs/IKE_PROJECT_SCOPE_AND_STRATEGY_REVIEW_PACK_2026-04-11.md)
  - [D:\code\MyAttention\docs\review-for IKE_PROJECT_SCOPE_AND_STRATEGY_REVIEW_PACK_2026-04-11.md](/D:/code/MyAttention/docs/review-for%20IKE_PROJECT_SCOPE_AND_STRATEGY_REVIEW_PACK_2026-04-11.md)
- clarified:
  - the project now has an explicit build-vs-adapt-vs-defer baseline
  - broad external review can now target scope risk and perfectionism-driven
    overexpansion directly

## 2026-04-12 Scope And Strategy Review Absorbed

- durable absorption:
  - [D:\code\MyAttention\docs\IKE_SCOPE_AND_STRATEGY_REVIEW_ABSORPTION_2026-04-12.md](/D:/code/MyAttention/docs/IKE_SCOPE_AND_STRATEGY_REVIEW_ABSORPTION_2026-04-12.md)
- controller decisions updated:
  - governance expansion freezes by default
  - research tracks freeze unless they directly unblock active priorities
  - the first real narrow I->K discovery loop is now a top strategic target

## 2026-04-12 First AI-Domain Discovery Loop Packet Prepared

- durable docs:
  - [D:\code\MyAttention\docs\IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_PHASE_JUDGMENT_2026-04-12.md](/D:/code/MyAttention/docs/IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_PHASE_JUDGMENT_2026-04-12.md)
  - [D:\code\MyAttention\docs\IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_PLAN_2026-04-12.md](/D:/code/MyAttention/docs/IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_PLAN_2026-04-12.md)
  - [D:\code\MyAttention\docs\IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_PACKET_2026-04-12.md](/D:/code/MyAttention/docs/IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_PACKET_2026-04-12.md)
- clarified:
  - the first real discovery proof is now the next practical project target
  - `Source Intelligence V1 M1` is explicitly tied to that loop rather than
    treated as an independent expansion line

## 2026-04-12 First AI-Domain Discovery Loop Delivery Pack Prepared

- durable docs:
  - [D:\code\MyAttention\docs\IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_DELIVERY_PACK_2026-04-12.md](/D:/code/MyAttention/docs/IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_DELIVERY_PACK_2026-04-12.md)
  - [D:\code\MyAttention\docs\IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_CLAUDE_SEND_PACKAGE_2026-04-12.md](/D:/code/MyAttention/docs/IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_CLAUDE_SEND_PACKAGE_2026-04-12.md)
- runtime delegation entrypoints added for the first narrow discovery-loop task

## 2026-04-12 First AI-Domain Discovery Loop Result Landed

- durable docs:
  - [D:\code\MyAttention\docs\IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_RESULT_2026-04-12.md](/D:/code/MyAttention/docs/IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_RESULT_2026-04-12.md)
  - [D:\code\MyAttention\docs\IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_EVALUATION_2026-04-12.md](/D:/code/MyAttention/docs/IKE_AI_DOMAIN_DISCOVERY_LOOP_P1_EVALUATION_2026-04-12.md)
- discovered:
  - Anthropic's session/harness/sandbox split is the strongest current
    reference pattern for durable external execution architecture
  - Hermes confirms a practical print-vs-interactive execution split
  - the first loop produced controller-usable signal rather than only broad
    inspiration

## 2026-04-12 Source Discovery Contract Narrowed Toward M1

- code:
  - [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
  - [D:\code\MyAttention\services\api\tests\test_source_discovery_contract.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_contract.py)
- changed:
  - `SourceDiscoveryRequest` now accepts bounded `task_intent` and `interest_bias`
  - `SourceDiscoveryResponse` now returns explicit `notes` and `truth_boundary`
  - discovery candidates now expose additional bounded semantic fields without
    replacing the existing response contract
  - method-focus reddit thread identity now normalizes toward community-level
    capture, matching the existing helper expectation
- validated with focused source-discovery/source-plan tests and compile checks

## 2026-04-13 Runtime v0 Restart-Recovery Closure Added

- durable docs:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I20_PHASE_JUDGMENT_2026-04-13.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I20_PHASE_JUDGMENT_2026-04-13.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I20_PLAN_2026-04-13.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I20_PLAN_2026-04-13.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I20_RESTART_RECOVERY_RESULT_2026-04-13.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I20_RESTART_RECOVERY_RESULT_2026-04-13.md)
- clarified:
  - `Runtime v0` exit criterion `D` is now materially satisfied
  - the accepted claim is narrow:
    - durable runtime truth survives interruption
    - work context can be reconstructed from canonical truth
    - recovered state can be re-exposed through the existing project/operator surface
  - no detached daemon, scheduler, or worker-session recovery claim was added

## 2026-04-13 Runtime v0 Final Exit Review Pack Prepared

- durable docs:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I21_PHASE_JUDGMENT_2026-04-13.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I21_PHASE_JUDGMENT_2026-04-13.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I21_PLAN_2026-04-13.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I21_PLAN_2026-04-13.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_EXIT_REVIEW_PACK_2026-04-13.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_EXIT_REVIEW_PACK_2026-04-13.md)
  - [D:\code\MyAttention\docs\review-for IKE_RUNTIME_V0_EXIT_REVIEW_PACK_2026-04-13.md](/D:/code/MyAttention/docs/review-for%20IKE_RUNTIME_V0_EXIT_REVIEW_PACK_2026-04-13.md)
- clarified:
  - Runtime v0 now has one compact final review edge
  - the next default move is review and selective absorption
  - further runtime packet growth should not continue by default without a new
    explicit gap

## 2026-04-13 Runtime v0 Exit Review Absorbed

- durable docs:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_EXIT_HANDOFF_2026-04-13.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_EXIT_HANDOFF_2026-04-13.md)
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_EXIT_REVIEW_ABSORPTION_2026-04-13.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_EXIT_REVIEW_ABSORPTION_2026-04-13.md)
- clarified:
  - Runtime v0 is now accepted as the first trustworthy operating kernel
  - criterion `A` is now aligned as materially satisfied
  - criterion `F` is now formalized through an explicit exit handoff
  - subsequent work should move above Runtime v0 instead of continuing
    runtime-local packet growth

## 2026-04-13 Source Intelligence V1 Became Active Mainline

- durable docs:
  - [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_ACTIVE_MAINLINE_TRANSITION_2026-04-13.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_ACTIVE_MAINLINE_TRANSITION_2026-04-13.md)
  - [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M2_PHASE_JUDGMENT_2026-04-13.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M2_PHASE_JUDGMENT_2026-04-13.md)
  - [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M2_PLAN_2026-04-13.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M2_PLAN_2026-04-13.md)
  - [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M2_EXECUTION_PACKET_2026-04-13.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M2_EXECUTION_PACKET_2026-04-13.md)
- clarified:
  - Runtime v0 is now accepted substrate rather than active growth line
  - the active project edge is now one real discovery loop through the
    existing source-intelligence M1 path

## 2026-04-13 Source Intelligence V1 M2 Loop Proof Added

- durable docs:
  - [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M2_LOOP_PROOF_RESULT_2026-04-13.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M2_LOOP_PROOF_RESULT_2026-04-13.md)
  - [D:\code\MyAttention\docs\review-for IKE_SOURCE_INTELLIGENCE_V1_M2_LOOP_PROOF_RESULT_2026-04-13.md](/D:/code/MyAttention/docs/review-for%20IKE_SOURCE_INTELLIGENCE_V1_M2_LOOP_PROOF_RESULT_2026-04-13.md)
- validated:
  - `python -m unittest tests.test_feeds_source_discovery_route tests.test_source_plan_helpers tests.test_source_discovery_contract tests.test_source_discovery_identity`
  - `42 tests OK`
  - `python -m py_compile D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`
- clarified:
  - the existing M1 route path now supports one bounded route-level loop shape
  - next work should shift from continuity proof to quality or noise judgment

## 2026-04-13 Source Intelligence V1 M2 Loop Review Absorbed

- durable docs:
  - [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M2_LOOP_PROOF_REVIEW_ABSORPTION_2026-04-13.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M2_LOOP_PROOF_REVIEW_ABSORPTION_2026-04-13.md)
- clarified:
  - `M2` is accepted as a bounded route-level loop proof
  - it is not a broad real-loop or semantic-quality closure
  - the next slice should move to quality improvement or noise compression
- 2026-04-15: Improved `Source Intelligence V1` panel inspect output from shallow agreement counts to structured insight. Added consensus/disagreement insight surfaces, bounded follow-up hints, and provider-aware default model resolution for multi-provider panel lanes. Recorded Claude Code chain validation for this packet.
- 2026-04-15: tightened `M8` panel inspect semantics and validation. `panel_signal` now requires full overlap to report `stable`; asymmetric lane failure remains visible as `mixed`. Added explicit stable-path and invalid-secondary-path route proofs. Documented multi-model judgment as a future reusable capability direction rather than permanent route-local logic.
- 2026-04-15: extracted the generic AI judgment kernel into `services/api/feeds/ai_judgment.py` while preserving existing source-intelligence route contracts. Recorded Claude Code chain validation for this bounded internal refactor and the controller-side integration repair that closed it.
- 2026-04-15: followed `M10` review by tightening the extraction claim and adding direct substrate tests for `feeds.ai_judgment`. This makes the reuse claim depend on explicit module-level proof, not only route-level regression coverage.
- 2026-04-15: added a bounded selective-absorption advisory layer on top of the existing panel outputs. The reusable judgment substrate now derives controller-facing advisory buckets for both discovery-panel and version-panel surfaces, but remains inspect-only and explicitly non-canonical.
- 2026-04-17: added a milestone policy so the project can distinguish checkpoint snapshots from reviewable milestones and archive-worthy boundaries before promoting a snapshot.
# 2026-04-17

## Added

- `docs/IKE_VISION_DESIGN_ARCHITECTURE_PATH_ALIGNMENT_2026-04-17.md` to
  stabilize the relationship between unchanged project vision, current design
  expression, staged architecture, and adjustable implementation path

## Changed

- clarified in active-surface docs that:
  - IKE's objective remains an AI-driven evolution system
  - the brains are layered rather than flat
  - `world model` and `thinking tools / scientific methodology` are
    cross-cutting layers
  - `Runtime v0` is accepted substrate and dependency component, not the final
    product identity
- synced the same framing into README, review-entry docs, and the web
  knowledge/evolution pages so external reviewers and operators see the same
  objective/path distinction
