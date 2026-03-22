# MyAttention 项目总计划

> 本文档是项目总纲。用于统一目标、能力边界、模块关系、架构原则、技术选型、部署思路、测试要求与研发运作方式。后续设计与编码必须与本文件保持一致。

关联专项设计：

- 信息流数据架构：`docs/FEED_DATA_ARCHITECTURE.md`
- 存储层架构：`docs/STORAGE_ARCHITECTURE.md`
- 研发方法与质量体系：`docs/ENGINEERING_METHOD.md`
- 编码与国际化规范：`docs/ENCODING_AND_I18N_STANDARD.md`
- 大脑控制层研究：`docs/BRAIN_CONTROL_RESEARCH.md`
- 大脑控制层设计：`docs/BRAIN_CONTROL_ARCHITECTURE.md`
- 问题建模与方法选择框架：`docs/PROBLEM_FRAMING_AND_METHOD_SELECTION.md`
- 研究索引：`docs/RESEARCH_INDEX.md`
- 任务与工作流研究：`docs/TASK_AND_WORKFLOW_MODEL_RESEARCH.md`
- 任务与工作流设计：`docs/TASK_AND_WORKFLOW_MODEL.md`
- 来源智能研究：`docs/SOURCE_INTELLIGENCE_RESEARCH.md`
- 来源智能架构：`docs/SOURCE_INTELLIGENCE_ARCHITECTURE.md`
- 记忆架构研究：`docs/MEMORY_ARCHITECTURE_RESEARCH.md`
- 记忆架构设计：`docs/MEMORY_ARCHITECTURE.md`
- 知识生命周期研究：`docs/KNOWLEDGE_LIFECYCLE_RESEARCH.md`
- 方法有效性与 skill 研究：`docs/METHOD_EFFECTIVENESS_AND_SKILL_RESEARCH.md`
- 方法情报与信息流前置索引研究：`docs/METHOD_INTELLIGENCE_RESEARCH.md`
- 深度研究方法研究：`docs/DEEP_RESEARCH_METHOD_RESEARCH.md`
- 变更与版本管理：`docs/CHANGE_MANAGEMENT.md`
- 统一版本管理规范：`docs/VERSION_MANAGEMENT.md`
- 版本化智能架构：`docs/VERSIONED_INTELLIGENCE_ARCHITECTURE.md`
- 时间化与版本化数据研究：`docs/TEMPORAL_AND_VERSIONED_DATA_RESEARCH.md`
- 实施准备检查点：`docs/IMPLEMENTATION_READINESS_CHECKPOINT.md`
- gstack skill 试用与评估：`docs/GSTACK_TRIAL_PLAN.md`
- 项目推进路线图：`docs/PROJECT_EXECUTION_ROADMAP.md`
- 部署运行模式设计：`docs/DEPLOYMENT_RUN_MODES.md`
- 部署自动化设计：`docs/DEPLOYMENT_AUTOMATION_DESIGN.md`

---

## 1. 项目定位

MyAttention 的长期目标不是一个单点聊天工具，也不是一个普通 RSS 阅读器，而是一个持续演化的智能系统：

- 以信息流为入口，持续感知世界变化
- 以知识体系为核心，沉淀结构化世界知识
- 以多模型对话为交互层，为用户提供研究、判断与决策支持
- 以自我测试和自我进化为保障，让系统持续发现问题、修正问题、提升质量

---

## 2. 核心目标

### 2.1 总目标

利用 AI 构建“信息大脑 + 知识大脑 + 进化大脑”三位一体的智能决策支持系统。

补充原则：

- 项目推进不以“顺着需求直接做”为目标，而以“研究、分析、纠偏后形成正确路线”为目标。
- 进化大脑和主控 agent 都必须具备质疑、评估、替代路线建议与纠偏能力。
- 整个项目是循环反馈优化过程，而不是单向线性过程。

### 2.2 分目标

#### A. 信息大脑

目标：

- 获取高质量、多来源、长期可追溯的信息
- 自动进行来源评估、内容打标、聚合、趋势分析与深度总结
- 支撑推荐、预警、专题研究、事件追踪
- 区分持续关注对象、低频复查对象和一次性知识导入对象

#### B. 知识大脑

目标：

- 将世界知识按学科、主题、实体、关系组织起来
- 形成“当前理解 + 权威共识 + 前沿研究 + 跨学科关联”的知识体系
- 支撑 RAG、知识图谱、知识推理与长期沉淀

#### C. 进化大脑

目标：

- 自动监控系统日志、任务失败、测试结果、性能波动
- 自动发现重复问题、生成任务、跟踪问题演进
- 为系统的迭代、优化与稳定运行提供闭环保障

---

## 3. 核心能力

系统长期要具备以下能力：

- 多源信息接入与抓取
- 来源质量评估与反爬适配
- 信息标准化、聚类、富化与趋势分析
- 知识抽取、知识组织、知识检索与知识推理
- 多模型对话、联网检索、RAG 与投票决策
- 用户记忆与长期上下文
- 自动化测试、日志监控、问题归并、自我优化

---

## 4. 核心模块

### 4.1 信息流模块

职责：

- 信息源接入
- 抓取、导入、标准化
- 原始数据归档
- 内容富化
- 热点、趋势、摘要、专题输出

子模块：

- Source Management
- Raw Ingest
- Feed Normalization
- Feed Enrichment
- Feed Aggregation
- Feed API

### 4.2 知识管理模块

职责：

- 知识库管理
- 文档切分与向量化
- 知识关联
- 知识指标管理

子模块：

- Knowledge Base Manager
- Vector Index
- Knowledge Metrics
- Feed-to-Knowledge Linker

### 4.3 知识大脑模块

职责：

- 学科体系组织
- 实体抽取
- 关系抽取
- 学科交叉与知识推理

子模块：

- Knowledge Graph
- Knowledge Categories
- Entity / Relation Extraction
- Cross-domain Reasoning

### 4.4 智能对话模块

职责：

- 用户交互入口
- 多模型调度
- RAG 检索
- 联网搜索
- 多模型投票

子模块：

- Chat Router
- LLM Adapter
- RAG Engine
- Search Integration
- Voting Engine

### 4.5 记忆模块

职责：

- 长期偏好
- 用户事实
- 决策记录
- 上下文召回

### 4.6 进化与测试模块

职责：

- 日志监控
- 问题检测与任务归并
- API 测试
- UI 测试
- 健康巡检
- 自我优化建议
- 方法研究
- 路线纠偏
- skill / playbook 沉淀

子模块：

- Log Monitor
- Test Runner
- Issue Center
- Task Processor
- Evolution Scheduler

### 4.7 通知与外部集成模块

职责：

- 消息推送
- 任务通知
- 外部 Agent / 工具集成

---

## 5. 模块联动关系

### 5.1 主数据主线

```text
外部信息源
  -> 信息流
  -> 原始层 / 标准层 / 富化层 / 聚合层
  -> 知识抽取
  -> 知识库 / 知识图谱
  -> 聊天 / 决策 / 总结 / 推荐
```

### 5.2 质量保障主线

```text
系统运行
  -> 日志 / 健康 / 测试结果
  -> 问题识别
  -> 去重归并
  -> 任务生成
  -> 修复 / 优化 / 策略调整
  -> 再测试 / 再监控
```

### 5.3 用户价值主线

```text
信息获取
  -> 信息理解
  -> 知识沉淀
  -> 对话研究
  -> 决策支持
  -> 长期学习与演化
```

---

## 6. 整体架构设计

### 6.1 逻辑架构

```text
Frontend
  -> API Gateway
     -> Feed Services
     -> Knowledge Services
     -> Chat Services
     -> Memory Services
     -> Evolution Services
     -> Notification Services
```

### 6.2 数据架构

信息流数据采用四层结构：

1. 原始层 `raw_ingest`
2. 标准条目层 `feed_items`
3. 富化分析层 `feed_enrichments`
4. 聚合分析层 `feed_aggregates`

知识层采用三类核心数据：

- 文档与向量
- 实体与关系
- 分类与指标

进化层采用三类核心数据：

- 日志与监控结果
- 测试结果
- 问题任务与处理历史

### 6.2.1 存储层拓扑

系统的长期存储层不是单一数据库，而是分层协作的组合：

- PostgreSQL：结构化事实、主业务表、任务状态、聚合分析结果
- Redis：缓存、短期去重键、任务缓冲、调度状态
- Qdrant：embedding、语义检索、相似内容召回、RAG 索引
- Object Storage：原始抓取对象、大体积附件、中间处理产物、快照归档

对象存储层必须从架构上预留扩展能力：

- 开发阶段实现：`LocalObjectStore`
- 生产阶段实现：`MinIO / S3 / OSS`

约束要求：

- 业务代码依赖统一对象存储接口，不直接把本地文件路径当作业务事实
- 所有原始层数据都应通过对象 ID 与元数据记录关联
- 单机文件系统只是开发部署形态，不是长期架构前提

### 6.3 关键架构原则

1. 缓存不是事实层。
2. 原始对象与结构化事实分离。
3. 富化结果与主事实分离。
4. 所有分析结果必须带版本号。
5. 所有任务处理必须可重试、可幂等。
6. 单机只是部署模式，不是架构前提。
7. 所有核心功能必须可被测试、可被监控、可被追溯。

---

## 7. 技术架构选型

### 7.1 当前主技术栈

- 前端：Next.js + React + TypeScript
- 后端：FastAPI + Python + asyncio
- 事实数据库：PostgreSQL
- 缓存与队列缓冲：Redis
- 向量数据库：Qdrant
- 原始对象层：对象存储抽象
- 本地开发对象层实现：LocalObjectStore
- 未来生产对象层实现：MinIO / S3 / OSS

### 7.2 为什么这样选

#### PostgreSQL

适合：

- 结构化事实
- 聚合分析
- 任务与状态
- 知识与信息关联

#### Redis

适合：

- 热点缓存
- 去重键
- 任务缓冲
- 调度状态

#### Qdrant

适合：

- embedding
- 相似性检索
- RAG 召回

#### 对象存储

适合：

- 原始 XML / HTML / JSON
- 中间处理产物
- PDF / 图片 / 截图
- 可重放数据

### 7.3 当前不引入

- Kafka
- Spark
- Flink
- ClickHouse
- 专用图数据库

理由：

- 当前阶段复杂度会显著上升
- 当前主问题仍是数据事实层未打通，而不是计算性能瓶颈

---

## 8. 部署架构考虑

### 8.1 当前阶段

- 单机开发 / 单机服务部署
- API 和前端可同机运行
- PostgreSQL 本地进程
- Redis 本地进程
- Qdrant 本地嵌入式或独立进程
- Object Store 使用本地目录实现

### 8.2 中期阶段

- API 与后台 worker 分离
- PostgreSQL / Redis / Qdrant 独立部署
- 原始层切换到 MinIO 或兼容 S3 的对象存储

### 8.3 长期阶段

- 多 worker 横向扩展
- 多环境部署：开发、测试、生产
- 以对象存储 + PostgreSQL + Redis + Qdrant 为核心基础设施

---

## 9. 测试要求

### 9.1 测试必须覆盖的层级

1. 单元测试
2. 集成测试
3. API 回归测试
4. 前端关键页面测试
5. E2E 测试
6. 健康检查与运行时巡检

### 9.2 每类改动的最低测试要求

#### 文档改动

- 检查与现有文档是否冲突

#### 单文件逻辑改动

- 至少运行直接相关测试
- 如果没有现成测试，至少做最小验证脚本

#### API 改动

- 需要接口级验证
- 需要兼容性确认

#### 数据模型 / 迁移改动

- 需要迁移验证
- 需要回滚或兼容说明

#### 前端页面改动

- 至少进行页面加载验证
- 关键交互需验证

### 9.3 自动化测试目标

- 自测任务可周期执行
- 测试失败自动产生日志与问题任务
- 重复问题自动归并
- 测试结果成为进化系统的输入

---

## 10. 自我进化要求

自我进化不是可选项，而是系统核心组件。

必须具备：

- 日志实时监控
- 问题自动识别
- 问题去重与归并
- 关键接口周期巡检
- 关键页面周期巡检
- 测试结果归档
- 问题历史追踪
- 为后续修复和优化生成任务

进化系统必须常驻运行，并在系统状态中可见。

---

## 11. 研发运作方式

后续研发必须遵守以下流程。

### 11.1 强制流程

1. 先确认目标和边界。
2. 先输出方案。
3. 先落设计文档。
4. 方案确认后再编码。
5. 编码后必须验证。
6. 验证结果必须记录。
7. 进度文档必须更新。

### 11.2 文档优先原则

任何中等及以上复杂度任务，在编码前必须至少具备以下之一：

- 设计文档更新
- 现有设计文档补充
- 专项方案文档

禁止直接跳过设计进入大规模编码。

### 11.3 变更分类规则

#### 小改动

- 单文件
- 低风险
- 不改结构

可在简要说明后直接编码，但仍要验证。

#### 中改动

- 影响多个模块
- 影响接口或数据流

必须先补设计文档，再实施。

#### 大改动

- 影响系统主线
- 改数据模型、主架构、部署模型、核心流程

必须先形成专项设计，再分阶段实施。

### 11.4 交付要求

每次任务交付必须包含：

- 做了什么
- 为什么这么做
- 验证了什么
- 还有什么风险或未完成项

---

## 12. 文档体系

建议以以下文档作为主骨架：

- `docs/PROJECT_MASTER_PLAN.md`
- `docs/SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/FEED_DATA_ARCHITECTURE.md`
- `docs/TESTING.md`
- `docs/DEPLOYMENT.md`
- `PROGRESS.md`

其中：

- `PROJECT_MASTER_PLAN.md` 负责总纲
- `SPEC.md` 负责产品定义
- `ARCHITECTURE.md` 负责系统架构总览
- `FEED_DATA_ARCHITECTURE.md` 负责信息流专项设计
- `TESTING.md` 负责测试策略
- `DEPLOYMENT.md` 负责部署模式
- `PROGRESS.md` 负责当前阶段和执行进度

---

## 13. 后续主线优先级

当前建议的主线优先级如下：

1. 信息流数据地基重构
2. 自我监控、测试和问题中心闭环
3. 信息大脑的来源评估、标签、趋势与总结
4. 知识大脑的学科体系和知识组织
5. 多机部署与可扩展基础设施

---

## 14. 当前执行约束

从本文件生效起，后续工作默认遵守以下约束：

- 先方案，后编码
- 先设计，后改造
- 必须测试，不能只改不验
- 必须记录，不能只做不留痕
- 必须让自我进化系统持续可观测

---

*版本：v0.1*
*状态：生效中*
*最后更新：2026-03-18*
