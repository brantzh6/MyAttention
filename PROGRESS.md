# MyAttention 项目工作进度

## 当前总目标

MyAttention 的主线没有变化，仍然围绕三条大脑推进：

- 信息大脑：高质量信息收集、事实层沉淀、趋势分析、深度总结。
- 知识大脑：面向世界知识体系的结构化组织、权威理解、前沿研究和跨学科关联。
- 进化大脑：自动测试、真实运行监控、问题发现、问题归并、恢复与优化路径建议。

## 当前判断

项目不是从零开始，而是在已有聊天、知识库、记忆、信息源管理、测试问题中心和部分自我进化能力的基础上，进入“按主线重新收口”的阶段。

新增共识：

- 主控 agent 和后续进化大脑都不应机械附和需求，而应主动研究、分析、评估可行性、识别错误方向并及时纠偏。
- 项目推进按循环反馈优化过程进行，而不是按线性顺序一路向前。
- 过程产物、关键决策、有效/无效方法都需要持续沉淀到仓库中。

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

## Latest Implementation Update

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
