# Current Active Artifacts

Date: 2026-04-30

Truth status: manually curated active index; non-canonical promotion truth.

## GitHub/Codex Review

| Artifact | Status | Owner/Lane | Next Action |
| --- | --- | --- | --- |
| `https://github.com/brantzh6/MyAttention/pull/1` | merged | GitHub/Codex review | Keep historical review evidence only; mainline can continue from the merge commit. |
| `docs/IKE_SCOPED_GITHUB_CODEX_REVIEW_PREP_2026-04-29.md` | active prep record | controller governance | Keep scoped PR separate from dirty controller worktree. |
| `docs/IKE_PR1_GITHUB_CODEX_REVIEW_FINDINGS_REVIEW_ABSORPTION_2026-04-30.md` | active review absorption | GitHub/Codex review | Records the two actionable findings now fixed locally. |

## Review Automation

| Artifact | Status | Owner/Lane | Next Action |
| --- | --- | --- | --- |
| `docs/IKE_REVIEW_CADENCE_AND_AUTOMATION_POLICY_2026-04-29.md` | active policy | review automation governance | Use as current review cadence boundary. |
| `docs/IKE_REVIEW_AUTOMATION_P0_IMPLEMENTATION_PACKET_2026-04-29.md` | accepted packet | review automation | Keep as PR #1 scope evidence. |
| `docs/IKE_REVIEW_AUTOMATION_P0_RESULT_2026-04-29.md` | accepted result | review automation | Historical note: PR #1 review outcome was later resolved and merged. |
| `docs/IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_PACKET_2026-04-29.md` | accepted packet | review automation | Keep delegated execution bridge bounded. |
| `docs/IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_RESULT_2026-04-29.md` | accepted result | review automation | Historical note: PR #1 review outcome was later resolved and merged. |
| `docs/IKE_REVIEW_AUTOMATION_P2_REAL_L1_OPERATIONAL_SMOKE_PACKET_2026-04-29.md` | accepted-with-changes packet | review automation | Require controller verification of result-file completion. |
| `docs/IKE_REVIEW_AUTOMATION_P2_REAL_L1_OPERATIONAL_SMOKE_RESULT_2026-04-29.md` | accepted-with-changes result | review automation | Do not treat wrapper success as completed review output. |

## Flywheel Readiness

| Artifact | Status | Owner/Lane | Next Action |
| --- | --- | --- | --- |
| `docs/IKE_FLYWHEEL_INSPECT_DECISION_READINESS_TAGS_P0_PACKET_2026-04-29.md` | accepted packet | flywheel readiness | Keep inspect-only truth boundary. |
| `docs/IKE_FLYWHEEL_INSPECT_DECISION_READINESS_TAGS_P0_RESULT_2026-04-29.md` | accepted result | flywheel readiness | Historical note: PR #1 review outcome was later resolved and merged. |

## Visual Control Surface

| Artifact | Status | Owner/Lane | Next Action |
| --- | --- | --- | --- |
| `services/web/app/control/page.tsx` | accepted UI progress surface | visual control surface | Shows mainline, UI line, and governance line together. |
| `services/web/lib/control-surface/types.ts` | accepted snapshot contract | visual control surface | Canonical shape for the static control surface snapshot. |
| `services/web/lib/control-surface/static-snapshot.ts` | accepted static snapshot | visual control surface | Static estimate only; no backend runtime truth change. |
| `docs/IKE_VISUAL_CONTROL_SURFACE_P1_PROGRESS_DASHBOARD_RESULT_2026-04-30.md` | accepted result | visual control surface | Documents the new progress dashboard surface. |
| `docs/IKE_VISUAL_CONTROL_SURFACE_P0_REVIEW_ABSORPTION_2026-04-29.md` | accepted-with-changes review absorption | visual control surface | Follow-up is now implemented and absorbed; keep as prior finding record. |
| `docs/IKE_VISUAL_CONTROL_SURFACE_P0_PROVENANCE_FOLLOWUP_PACKET_2026-04-29.md` | accepted follow-up packet | UI implementation delegate | Keep static provenance boundary visible. |
| `docs/IKE_VISUAL_CONTROL_SURFACE_P0_PROVENANCE_FOLLOWUP_RESULT_2026-04-29.md` | accepted result | visual control surface | Build passed; no backend/runtime truth change. |
| `docs/IKE_VISUAL_CONTROL_SURFACE_P0_PROVENANCE_FOLLOWUP_REVIEW_ABSORPTION_2026-04-30.md` | accepted review absorption | visual control surface | L1 findings fixed and absorbed. |

## Governance / Worktree Cleanup

| Artifact | Status | Owner/Lane | Next Action |
| --- | --- | --- | --- |
| `docs/IKE_WORKTREE_DOC_KNOWLEDGE_GOVERNANCE_PLAN_2026-04-29.md` | active design plan | governance | Use active-state manifest as Phase 1 implementation. |
| `docs/IKE_MAINLINE_STATE_MANIFEST_P0_PACKET_2026-04-29.md` | accepted packet | documentation/governance worker | Keep active state manifest current. |
| `docs/CURRENT_MAINLINE_STATE.json` | accepted active state | documentation/governance worker | Use as active governance source. |
| `docs/CURRENT_ACTIVE_ARTIFACTS.md` | accepted active index | documentation/governance worker | Keep active artifacts compact. |
| `docs/CURRENT_REVIEW_QUEUE.md` | accepted review queue | documentation/governance worker | Keep open reviews visible. |
| `docs/CURRENT_MAINLINE_HANDOFF_COMPACT_2026-04-30.md` | accepted compact handoff | controller governance | Use this as the first-read continuation surface. |
| `docs/IKE_MAINLINE_STATE_MANIFEST_P0_RESULT_2026-04-29.md` | accepted result | documentation/governance worker | Use as manifest P0 evidence. |
| `scripts/governance/classify_worktree.py` | accepted tool | governance tooling | Run before scoped review prep. |
| `scripts/governance/README.md` | accepted usage note | governance tooling | Keep classifier usage documented. |
| `codex/dirty-quarantine-20260506:docs/IKE_DIRTY_WORKTREE_CLASSIFIER_P0_PACKET_2026-04-30.md` | quarantined local evidence | governance tooling | Historical classifier packet preserved in quarantine only; not an active continuation dependency. |
| `codex/dirty-quarantine-20260506:docs/IKE_DIRTY_WORKTREE_CLASSIFIER_P0_RESULT_2026-04-30.md` | quarantined local evidence | governance tooling | Historical classifier result preserved in quarantine only; current active classifier truth comes from rerunning `scripts/governance/classify_worktree.py`. |
| `docs/IKE_WORKTREE_ARCHIVE_INDEX_PLAN_P0_RESULT_2026-04-30.md` | accepted-with-changes plan | governance cleanup | Use as planning boundary; no movement authorized. |
| `docs/IKE_WORKTREE_ARCHIVE_INDEX_PLAN_P0_REVIEW_ABSORPTION_2026-04-30.md` | accepted review absorption | governance cleanup | Latest observed planning count: 197 entries, 9 groups. |
| `docs/IKE_DIRTY_WORKTREE_RECONCILIATION_DOCS_ONLY_RESULT_2026-04-30.md` | accepted result | governance cleanup | Documents the docs-only cleanup slice for controller-facing surfaces. |
| `docs/IKE_CURRENT_CONTINUATION_HISTORY_RECONCILIATION_RESULT_2026-04-30.md` | accepted result | controller continuation | Removes stale PR #1 wait semantics from active surfaces. |
| `docs/IKE_ACTIVE_SURFACES_HISTORY_ONLY_RECONCILIATION_RESULT_2026-04-30.md` | accepted result | controller continuation | Confirms the active surfaces are history-only for PR #1 wait wording. |
| `docs/IKE_DIRTY_WORKTREE_SCOPED_CLEANUP_PLANNING_RESULT_2026-04-30.md` | accepted result | governance cleanup | Plans the next bounded cleanup node for the mixed worktree. |
| `docs/IKE_DIRTY_WORKTREE_SCOPED_CLEANUP_PACKET_2026-04-30.md` | accepted packet | governance cleanup | Historical packet that defined the docs-only scoped cleanup slice. |
| `docs/IKE_DIRTY_WORKTREE_SCOPED_CLEANUP_PACKET_RESULT_2026-04-30.md` | accepted result | governance cleanup | Accepts the docs-only scoped cleanup packet as the next bounded node. |
| `docs/IKE_CONTROLLER_SURFACE_HISTORY_AUDIT_PACKET_2026-04-30.md` | accepted packet | controller continuation | Historical packet for auditing the active surfaces for live blocker wording. |
| `docs/IKE_CONTROLLER_SURFACE_HISTORY_AUDIT_RESULT_2026-04-30.md` | accepted result | controller continuation | Confirms the active surfaces are history-only. |
| `docs/IKE_LONG_HANDOFF_HISTORY_NOTE_NORMALIZATION_PACKET_2026-04-30.md` | accepted packet | controller continuation | Historical packet that normalized the remaining long-handoff PR #1 wording into evidence-only text. |
| `docs/IKE_LONG_HANDOFF_HISTORY_NOTE_NORMALIZATION_RESULT_2026-04-30.md` | accepted result | controller continuation | Confirms the long handoff is evidence-only for the remaining PR #1 wording. |
| `docs/IKE_LONG_HANDOFF_REVIEW_TIME_OBSERVATION_NORMALIZATION_PACKET_2026-04-30.md` | accepted packet | controller continuation | Historical packet that normalized the remaining review-time observation wording in the long handoff. |
| `docs/IKE_LONG_HANDOFF_REVIEW_TIME_OBSERVATION_NORMALIZATION_RESULT_2026-04-30.md` | accepted result | controller continuation | Confirms the long handoff review-time observation is historical evidence. |
| `docs/IKE_LONG_HANDOFF_BLOCKER_NOTE_NORMALIZATION_PACKET_2026-04-30.md` | accepted packet | controller continuation | Historical packet that normalized remaining blocker-style wording in the long handoff. |
| `docs/IKE_LONG_HANDOFF_BLOCKER_HISTORY_NORMALIZATION_PACKET_2026-04-30.md` | accepted packet | controller continuation | Historical packet that normalized the remaining blocker-style wording in the long handoff into historical evidence. |
| `docs/IKE_LONG_HANDOFF_BLOCKER_HISTORY_NORMALIZATION_RESULT_2026-04-30.md` | accepted result | controller continuation | Confirms the long handoff blocker-style wording is historical evidence. |
| `docs/IKE_LONG_HANDOFF_FINAL_BLOCKER_HISTORY_NORMALIZATION_PACKET_2026-04-30.md` | accepted packet | controller continuation | Historical packet that normalized the last remaining current-blocker phrases in the long handoff. |
| `docs/IKE_LONG_HANDOFF_FINAL_BLOCKER_HISTORY_NORMALIZATION_RESULT_2026-04-30.md` | accepted result | controller continuation | Confirms the long handoff no longer contains live-looking current-blocker phrases. |
| `docs/IKE_SOURCE_INTELLIGENCE_QUALITY_RESUMPTION_PACKET_2026-04-30.md` | active packet | source intelligence quality | Resumes the next bounded source-intelligence quality slice. |
| `docs/IKE_SOURCE_INTELLIGENCE_QUALITY_RESUMPTION_RESULT_2026-04-30.md` | accepted result | source intelligence quality | Confirms the next bounded node is source-intelligence quality resumption. |
| `docs/IKE_SOURCE_INTELLIGENCE_QUALITY_RESUMPTION_IMPLEMENTATION_RESULT_2026-05-01.md` | accepted result | source intelligence quality | GitHub issue/discussion identity recognition now applies across all source-discovery focuses. |
| `docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_PACKET_2026-05-02.md` | active packet | source intelligence quality | Adds repository and owner relation hints for GitHub repo-scoped signal objects. |
| `docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_RESULT_2026-05-02.md` | accepted result | source intelligence quality | Locally fixed to avoid false person seeds; scoped GitHub/Codex L1 re-review accepted. |
| `docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_REVIEW_ABSORPTION_2026-05-02.md` | accepted review absorption | source intelligence quality | Captures the accepted re-review and controller absorption for the fixed slice. |
| `docs/IKE_ARCHIVE_INDEX_SCHEMA_P0_RESULT_2026-04-30.md` | accepted schema | governance cleanup | Use for index-only archive/review identity packets. |
| `docs/IKE_ARCHIVE_INDEX_SCHEMA_P0_REVIEW_ABSORPTION_2026-04-30.md` | accepted review absorption | governance cleanup | L1 findings fixed; movement manifest design deferred. |
| `docs/archive/REVIEW_ARTIFACT_IDENTITY_INDEX_2026-04.md` | accepted index-only artifact | review artifact governance | Representative review identity map; no rename/move authorized. |
| `docs/IKE_REVIEW_ARTIFACT_IDENTITY_INDEX_P0_RESULT_2026-04-30.md` | accepted result | review artifact governance | Historical note: PR #1 payload was not available at the time of the access check. |
| `docs/IKE_PR1_CODEX_REVIEW_ACCESS_HISTORY_ONLY_RESULT_2026-04-30.md` | accepted result | review artifact governance | Converts the access check into history-only evidence. |
| `docs/IKE_REVIEW_ARTIFACT_IDENTITY_INDEX_P0_REVIEW_ABSORPTION_2026-04-30.md` | accepted review absorption | review artifact governance | No L1 findings. |
| `docs/archive/ARCHIVE_INDEX_2026-04.md` | accepted-with-changes index-only artifact | documentation archive governance | Representative April docs index; no movement authorized. |
| `docs/IKE_DOC_ARCHIVE_INDEX_2026_04_P0_RESULT_2026-04-30.md` | accepted-with-changes result | documentation archive governance | Bundle-dir P1 finding fixed. |
| `docs/IKE_DOC_ARCHIVE_INDEX_2026_04_P0_REVIEW_ABSORPTION_2026-04-30.md` | accepted review absorption | documentation archive governance | Records delegated review and controller fallback fix. |
