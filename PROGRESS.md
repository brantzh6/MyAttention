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
  - `docs/KNOWLEDGE_LIFECYCLE_RESEARCH.md`
  - `docs/METHOD_EFFECTIVENESS_AND_SKILL_RESEARCH.md`
  - `docs/METHOD_INTELLIGENCE_RESEARCH.md`
  - 已将“任务/工作流”和“知识生命周期”从单一讨论中拆开，方便后续独立设计

## 下一步

1. 给进化大脑继续补“问题归因、恢复建议、去噪”，避免只会报错不会判断。
2. 回到存储主线，继续完成 Phase 2 收口和 Phase 3 设计实施。
3. 持续收口本机运行稳定性，避免 API/Web 因 watchdog 与运行模式漂移再次失稳。
