# Controller Absorption: Isolated Origin/Main L5 Milestone Save-State Package

Date: 2026-06-07
Controller: codex-controller

## Decision

`accept`

## Accepted Evidence

- Packet:
  `tasks/codex/isolated_origin_main_l5_milestone_save_state_packet_2026-06-07.md`
- Corrected result:
  `tasks/codex/isolated_origin_main_l5_milestone_save_state_result_2026-06-07.md`
- Initial review:
  `docs/reviews/active/review_for_isolated_origin_main_l5_milestone_save_state_2026-06-07.md`
- Re-review:
  `docs/reviews/active/review_for_isolated_origin_main_l5_milestone_save_state_rereview_2026-06-07.md`

## Absorbed Findings

- The isolated package is based on canonical `origin/main` at `c5a060b`.
- Required PR #24-#27 merge commits are ancestors of `origin/main`.
- The package contains only bounded milestone, automation-protocol, and
  acceptance-evidence files.
- No excluded controller dirty-tree lane entered the package.
- Controller workspace state (`ops/state/current_state.json`, `ops/runtime/latest.json`)
  was external evidence for controller decision-making, NOT PR package contents.
- The initial result artifact was rejected for factual and encoding defects.
- Delegate correction and independent re-review resolved all prior findings.
- The package remains explicitly `inspect_only`.

## Promotion Decision

The package is approved for a bounded GitHub save-state PR.

Approval permits:

- add final review and absorption evidence to the isolated package;
- stage only the approved bounded package;
- commit and push the isolated branch;
- open a PR against `main`;
- request GitHub/Codex promotion review.

Approval does not permit:

- merge before promotion review absorption;
- broad dirty-tree staging;
- runtime operation;
- database cutover;
- automatic execution or promotion capability.

## Next Gate

Create the bounded GitHub PR and request GitHub/Codex promotion review. Stop
before merge.
