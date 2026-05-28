# Weekly Controller Review - 2026-05-26

Controller: Codex
Truth status: controller-consumable review
Scope: close prior review, update mainline priorities, expose blockers, define next actions

## closure_status_of_last_review

| Prior action | Status | Evidence | Controller reading |
|---|---|---|---|
| Make Evolution Flywheel v1 runnable instead of document-only | partial | PR17 merged candidate extraction fix; PR18 merged conversation `extra` migration; PR19 merged current Qwen model defaults; PR20 merged at `4c54b34` and runtime operator verified `/api/evolution/contexts`, `/api/evolution/memories/task`, `/api/evolution/memories/procedural`, `/chat`, and `/evolution` return 200. See `tasks/codex/post_pr20_runtime_validation_absorption_2026-05-26.md`. | API and page surfaces are usable enough for inspect-only P0 continuation. Full product closure still requires browser L5 after `/control` lands. |
| Keep AI conversation entry connected to flywheel | completed_with_boundary | Accepted AI chat to flywheel evidence through multiple L3/L4/L5 artifacts; PR18/PR19 removed schema/model blockers; PR20 added missing evolution API surface. | AI entry is not the current blocker. Next validation should be integrated with post-PR14 `/control` runtime state. |
| Make `/control` the project single visible anchor | partial | PR14 is ready and mergeable. GitHub/Codex review found P1/P2 adapter path issues; fixes committed as `7a5fea2` and `bc54c74`, pushed, and second re-review triggered at comment `4542338740`. | `/control` is still not visible on main. This is the highest active promotion gate. |
| Convert PM from passive trigger to coordinator | completed | `ops/agents/openclaw-ike-pm.md`, `docs/IKE_OPERATIONS_KERNEL_P0.md`, PM schemas, PM workspace `AGENTS.md`, and registry were updated and independently reviewed. Absorption: `tasks/codex/openclaw_pm_coordinator_contract_absorption_2026-05-26.md`. | PM should judge progress/gates/blockers and escalate; it does not decide solution or promotion. |
| Keep runtime work out of controller lane | partial | Runtime boundary incident recorded in `tasks/codex/controller_runtime_boundary_incident_2026-05-26.md`; post-PR20 runtime validation was correctly handled by runtime operator. | Rule is now explicit, but enforcement depends on future controller discipline and task packets. |
| Repair automatic mainline progression | partial | OpenClaw PM produced trigger `ops/triggers/openclaw_pm_20260526_071500.json`; bridge dispatched Codex run `ops/bridge/runs/openclaw_codex_20260526_071828.json`; result artifact was written. | Automation can wake Codex, but prior run failed to make progress because PR20 merge authorization was unavailable. This is activity, not progress. |
| Reduce dirty tree risk | partial | PR20 merge required moving three untracked conflicting artifacts to `D:\code\_local-backups\MyAttention-pr20-untracked-conflicts-20260526`. `git status --short -uno` is clean on main, but full tree remains degraded by broad untracked artifacts. | Dirty tree is still a material operations risk and blocks broad new feature coding. |

## priority_changes

1. `/control` promotion moves to immediate priority because PR20 is merged and runtime-ready, while `/control` is still 404 on main.
2. Evolution Flywheel v1 continues, but the next useful validation is integrated browser/product validation after `/control` becomes visible and state-consistent.
3. AI conversation entry is no longer the active blocker; keep it in regression scope for the next L5 smoke.
4. PM automation is accepted as wakeup/coordinator infrastructure, but it must not be counted as mainline progress unless it causes an absorbed controller action.
5. Dirty-tree cleanup remains a gate, not a side preference: no broad feature work until remaining lanes are packaged, parked, or intentionally excluded.

## items_to_escalate

| Item | Severity | Why it matters | Required decision or action |
|---|---|---|---|
| PR14 promotion gate pending Codex second re-review | high | `/control` is the visible project anchor and still absent from main. | Absorb second re-review after `bc54c74`; if clean, merge PR14 and delegate runtime validation to `ike-operator`. |
| Root `AGENTS.md` missing | resolved_this_review | OpenClaw-triggered Codex run attempted to read it and produced avoidable error noise. | Minimal repo-root controller/delegate contract added in `AGENTS.md`; next OpenClaw-triggered Codex run should no longer fail this read. |
| Old automation/docs references drift | medium | Historical prompts reference missing `docs/CURRENT_OPERATIONS.md`; real truth is `ops/state/current_state.json`. | Normalize current automations/prompts to accepted source-of-truth paths. |
| Dirty tree remains degraded | high | Untracked artifacts already blocked/complicated PR20 merge pull and will keep creating collision risk. | Package or park remaining lanes one at a time; do not mix governance, runtime, UI, and feature code in one PR. |
| Runtime status still has degraded components | medium | `/api/evolution/status` has degraded auto-evolution signals; Redis status reporting is unreliable. | Route bounded diagnosis to `ike-operator` after PR14 runtime validation, unless it blocks the L5 smoke. |

## updated_next_actions

| Order | Action | Owner lane | Gate and validation | Stop condition |
|---|---|---|---|---|
| 1 | Absorb PR14 Codex second re-review for commit `bc54c74`. | codex-controller | GitHub/Codex review gate; prior P1 and P2 threads must be outdated/resolved or explicitly addressed. | PR14 is either clean for merge or has a bounded follow-up. |
| 2 | Merge PR14 if review is clean. | codex-controller | Expected head check; no unresolved actionable review threads. | PR14 merged or blocked with evidence. |
| 3 | Validate `/control` runtime visibility and state accuracy after merge. | ike-operator | L3 reachability plus L4 browser UI smoke on `http://127.0.0.1:3002/control`; no controller runtime operation. | `/control` visible and reflects `ops/state/current_state.json`, or operator returns blocker. |
| 4 | Run integrated AI chat to evolution flywheel browser smoke with `/control` state check. | test-runner with runtime/operator support | L5 product scenario: chat origin, flywheel handoff, inspect/preview, no auto-execution, state/control visibility. | Accepted evidence or bounded defect packet. |
| 5 | Package/park dirty-tree lanes. | codex-controller plus reviewer | One lane per PR/artifact set; independent review before absorption. | Dirty-tree status moves from degraded to controlled. |
| 6 | Validate next PM coordinator run after PR14 state update. | ike-pm | PM digest must distinguish configured/triggered/dispatched/absorbed/failed and must escalate blockers without deciding solution. | `ops/pm-runs/latest.json` is coherent and `/control` can display it. |

## controller_consumption

Codex should do next: wait only long enough for PR14 re-review signal; if Codex review returns clean, merge PR14 and immediately delegate runtime validation to `ike-operator`. While waiting, do not start broad feature work; only perform governance cleanup that directly reduces automation noise or dirty-tree risk.

PM should monitor next: PR14 review/merge/runtime-validation state, dirty-tree degraded status, and whether controller actions are absorbed into `ops/state/current_state.json`. PM should escalate if `/control` remains absent after PR14 is clean or merged.

`/control` should show next: PR20 runtime-ready status, PR14 `/control` promotion pending/re-review state, dirty-tree degraded status, PM coordinator latest run, and next controller action with owner lane and gate.

## weekly_mechanism

The weekly controller review automation is configured as `weekly-ike-controller-review` with Monday 09:30 cadence. The automation must write the next artifact under `tasks/codex/weekly_controller_review_YYYY-MM-DD.md` and close this review item-by-item before changing priorities.
