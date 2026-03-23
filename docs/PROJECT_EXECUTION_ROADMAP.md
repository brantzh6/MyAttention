# 项目推进路线图

## 1. 目的

本路线图回答四个问题：

- 一共分几个阶段
- 关键里程碑是什么
- 当前任务优先级如何排
- 多条交叉任务线如何避免信息和状态混乱

这不是一次性终局路线图。

这是 `V1` 执行路线图，后续会随认知框架、方法体系、实现基础设施一起迭代。

## 2. 路线图总览

项目按 8 个阶段推进：

1. `Phase 0` 运行基线与质量入口
2. `Phase 1` 原始层与对象存储
3. `Phase 2` 信息事实层与基础持久化
4. `Phase 3` 认知控制框架 V1
5. `Phase 4` source intelligence 与记忆架构
6. `Phase 5` 深度研究与知识结构化
7. `Phase 6` 多大脑协作与进化大脑升级
8. `Phase 7` 版本化智能架构与分布式演进

其中：

- `Phase 0-2` 是基础层
- `Phase 3-4` 是控制层
- `Phase 5-6` 是智能层
- `Phase 7` 是长期演进层

## 3. 当前阶段判断

当前不是从零开始。
当前是：

- 已有部分聊天、知识库、信息流、测试、进化能力
- 但主线、方法、数据底座、控制层还没有完全收拢

当前真正的工作重心不是继续散点加功能，而是：

1. 把信息抓取和持久化底座做稳
2. 把进化大脑做成可用的质量和演化入口
3. 把问题类型、方法选择、任务协同和版本控制抽象成上层框架

## 4. 阶段计划

### Phase 0：运行基线与质量入口

目标：

- 本机开发环境可稳定运行
- 前端不再频繁退化
- 进化大脑具备真实可见入口
- 至少能做基础 UI 巡检和核心链路自测

当前状态：

- 大部分已完成

已完成：

- 本机 `api/web/postgres/redis/watchdog` 运行方案
- 独立进化大脑页面
- 浏览器 UI 巡检
- 基础投票 canary
- 对话、前端、编码一批关键修复

未完成：

- 前端质量基线还不够稳定
- 进化大脑仍偏“探测 + 规则”

里程碑：

- `M0`: 本机开发环境稳定运行
- `M1`: 进化大脑成为正式入口，不再是零散接口

### Phase 1：原始层与对象存储

目标：

- 建立原始对象层和存储抽象

当前状态：

- 已完成

已落地：

- `ObjectStore`
- `LocalObjectStore`
- `raw_ingest`
- `/api/feeds/import` 原始层持久化

里程碑：

- `M2`: 原始数据可追溯、可重放、可扩展到对象存储

### Phase 2：信息事实层与基础持久化

目标：

- 让信息流不再只依赖运行时缓存
- 让 `feed_items` 成为事实层
- 建立信息获取的可靠基础

当前状态：

- 部分完成

已落地：

- `/api/feeds/import` 写入 `raw_ingest + sources + feed_items + cache`
- `/api/feeds` 支持 `cache / db / hybrid`

未完成：

- `feed_items` 完全切主
- 信息层级分页与历史管理
- 富化闭环
- 来源智能还未真正接管 source planning

里程碑：

- `M3`: 信息流主事实层稳定
- `M4`: source discovery 不再只是固定 RSS 列表

### Phase 3：认知控制框架 V1

目标：

- 解决“到底这是什么问题、该用什么思维模型和方法”

设计产物：

- `PROBLEM_FRAMING_AND_METHOD_SELECTION.md`

核心内容：

- 问题类型 taxonomy
- 思维模型/思考框架
- 方法选择规则
- 执行路由原则
- 明确哪些问题不该直接套深度研究

当前状态：

- 未正式设计

里程碑：

- `M5`: 有可运行、可演化的认知控制框架 `V1`

### Phase 4：source intelligence 与记忆架构

目标：

- 建立“知道去哪里找、为什么找、是否持续关注”的能力
- 建立任务/经验/程序性记忆基础

设计产物：

- `SOURCE_INTELLIGENCE_ARCHITECTURE.md`
- `MEMORY_ARCHITECTURE.md`

核心内容：

- 来源发现与来源执行分离
- authority / signal / frontier / community 分类
- 冷 / 温 / 热对象分层
- task / episodic / procedural / semantic memory

当前状态：

- 已完成研究与正式设计，未进入实施

里程碑：

- `M6`: source intelligence V1 可运行
- `M7`: 记忆分层 V1 可落盘、可回忆、可追溯

### Phase 5：深度研究与知识结构化

目标：

- 把高价值研究任务纳入结构化研究骨架
- 把知识从“文档/RAG”推进到“学科/事实/时间/解释/边界”结构

设计产物：

- `DEEP_RESEARCH_ARCHITECTURE.md`
- `KNOWLEDGE_ARCHITECTURE.md`

核心内容：

- `research_brief`
- `source_plan`
- `evidence_log`
- `fact_base`
- `interpretation_map`
- `boundary_map`
- `tension_map`
- `handoff`

当前状态：

- 已有方法研究，未正式设计

里程碑：

- `M8`: 深度研究方法进入系统主工作流
- `M9`: 知识结构化不再只是 RAG 文档堆积

### Phase 6：多大脑协作与进化大脑升级

目标：

- 从单脑/单线程推进到分层多脑协作
- 让进化大脑具备观察、归因、恢复、方法评估能力

设计产物：

- `BRAIN_CONTROL_ARCHITECTURE.md`
- `TASK_AND_WORKFLOW_MODEL.md`

核心内容：

- 持续任务 / 一次性任务 / 嵌套子任务
- 脑干 / 小脑 / 皮层式分层
- chief / specialists 协作
- supervisor / handoff / review / debate / fallback

当前状态：

- 已完成 `TASK_AND_WORKFLOW_MODEL.md` 与 `BRAIN_CONTROL_ARCHITECTURE.md`，待进入后续版本化与深度研究专项设计

里程碑：

- `M10`: 多任务调度和多脑协作 V1
- `M11`: 进化大脑具备模型驱动的诊断与方法评估

### Phase 7：版本化智能架构与分布式演进

目标：

- 支撑系统、认知、知识、任务、方法、记忆的持续版本演化
- 为未来分布式 worker / object storage / service mesh / A2A 留足空间

设计产物：

- `VERSIONED_INTELLIGENCE_ARCHITECTURE.md`
- `TEMPORAL_AND_VERSIONED_DATA_RESEARCH.md`

当前状态：

- 已完成首版研究与正式设计，待后续与任务系统、记忆层、知识层和数据模型接轨

核心内容：

- 系统版本
- 设计版本
- 认知版本
- 方法版本
- 任务版本
- 知识版本
- 记忆版本
- 指标时间序列 / 事件流 / 版本化对象

当前状态：

- 仅完成问题识别，未正式研究/设计

里程碑：

- `M12`: 版本化与时间化架构 V1
- `M13`: 具备走向分布式演进的基础

## 5. 当前优先级

### P0：必须先收口

- Phase 2 信息事实层继续收口
- Phase 3 认知控制框架 V1
- Phase 4 source intelligence / memory 设计
- 进化大脑质量基线继续加固

### P1：紧随其后

- 受控任务外包策略落地（先从 coding-heavy / review-heavy 子任务开始）
- 深度研究主工作流设计
- 知识结构化设计
- 多任务模型与多脑协作设计

### P2：在基础稳定后推进

- 版本化智能架构
- 时间化数据模型与可能的 TSDB 评估
- 分布式演进和 service mesh 级设计

## 6. 关键依赖关系

必须明确几个依赖：

- 没有稳定事实层，source intelligence 容易空转
- 没有认知控制框架，方法选择会混乱
- 没有 source intelligence，深度研究会继续依赖临时搜索
- 没有记忆架构，进化无法沉淀经验
- 没有任务/协作模型，多脑协同无法落地
- 没有版本架构，进化结果不可追溯
- 没有受控任务外包策略，主控上下文会被高 token 执行任务持续挤压

## 7. 如何避免交叉任务把信息搞乱

这是路线图里最关键的一部分。

### 7.1 用“主线 + 支线”而不是“并行散射”

同一时期只允许一个主线：

- 当前主线：信息抓取基础 + 记忆基础 + 认知控制框架前置

其他工作只能作为支线服务主线，不能抢主线。

### 7.2 每个任务必须挂到一个阶段和一个主问题

每个任务至少要有：

- `phase`
- `problem_type`
- `primary_goal`
- `depends_on`
- `produces`

否则不进入执行。

### 7.3 区分四类任务

- `research`
- `design`
- `implementation`
- `validation`

不能把这四类任务混成一个“做这个功能”的口头任务。

### 7.4 先研究结论，再出设计，再编码

如果 research 没收敛：
- 不能提前编码大实现

如果 design 没确认：
- 不能同时多人多线乱改

### 7.5 每条线都有独立产物

例如：

- source intelligence 线：
  - research
  - architecture
  - implementation plan
- memory 线：
  - research
  - architecture
  - storage model

这样不会把不同线索混在一份文档里。

### 7.6 统一入口文档必须持续回写

以下文件必须始终同步：

- `docs/PROJECT_MASTER_PLAN.md`
- `docs/PROJECT_EXECUTION_ROADMAP.md`
- `PROGRESS.md`
- `CHANGELOG.md`

研究文档只负责深度，不负责总览。
总览必须回写到总计划和路线图。

### 7.7 版本化所有“认知层”对象

后续所有这些都不能只保留当前值：

- 问题类型
- 思维模型
- 方法选择规则
- 任务计划
- 研究结论
- 知识结论

否则交叉任务一定会混乱且无法回溯。

## 8. 当前下一步

按当前优先级，下一步建议顺序是：

1. `PROBLEM_FRAMING_AND_METHOD_SELECTION.md`
2. `SOURCE_INTELLIGENCE_ARCHITECTURE.md`
3. `MEMORY_ARCHITECTURE.md`

这三份完成后，再进入：

4. `TASK_AND_WORKFLOW_MODEL.md`
5. `BRAIN_CONTROL_ARCHITECTURE.md`

最后再进入：

6. `DEEP_RESEARCH_ARCHITECTURE.md`
7. `VERSIONED_INTELLIGENCE_ARCHITECTURE.md`

## 9. 当前结论

现在已经有路线图，但之前不够完整。

当前版本的完整判断是：

- 阶段已经可以清晰划分
- 关键里程碑已经能明确
- 优先级已经可以稳定排序
- 交叉任务防乱机制也已经可定义

接下来真正关键的，不是再继续口头分解，而是把 `Phase 3-4` 的设计文档正式落下来。
