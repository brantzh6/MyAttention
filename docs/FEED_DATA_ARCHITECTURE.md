# 信息流数据架构与系统设计

> 目标：把当前“抓取后展示”的信息流，升级为“可长期沉淀、可分析、可演化、可分布式扩展”的数据系统，为信息大脑、知识大脑、自我进化提供底座。

---

## 1. 背景

当前项目已经具备：

- 信息源抓取、分类、代理与反爬处理
- 聊天、知识库、记忆、自我进化
- PostgreSQL / Redis / Qdrant 的基本技术栈

但当前信息流主链路仍以运行时缓存为主：

- `FeedFetcher._cache` 仍是事实来源之一
- `/api/feeds` 主要返回内存中的 `FeedEntry`
- `/api/feeds/import` 当前主要注入内存缓存，而不是稳定落库
- `feed_items`、`source_metrics`、`knowledge_links` 等表虽然存在，但还没有成为主数据闭环

这会直接限制后续能力：

- 趋势分析
- 长周期深度总结
- 来源质量评估
- 主题演化与事件聚类
- 知识抽取重跑
- 多进程 / 多机器扩展

因此，本次设计的核心任务不是增加一个新功能，而是重构“信息流的数据地基”。

---

## 2. 设计目标

### 2.1 业务目标

- 支撑长期信息沉淀，而不是只支撑实时展示
- 支撑后续的信息大脑：打标、推荐、质量评估、趋势分析、深度总结
- 支撑后续的知识大脑：从信息流稳定抽取知识，并可反复重跑
- 支撑自我进化：基于真实数据而不是短暂缓存做评测和优化

### 2.2 架构目标

- 单机开发可运行
- 架构上预留未来多机部署能力
- 原始数据、结构化数据、语义数据、聚合数据职责分离
- API 层不依赖本地文件路径或进程内缓存
- 存储实现可替换：本地文件系统 -> S3/OSS/MinIO 时不改业务逻辑

### 2.3 非目标

- 本阶段不引入大数据平台（Spark / Flink / ClickHouse）
- 本阶段不引入专门图数据库
- 本阶段不追求极致实时流式处理，优先保证结构正确与可演进

---

## 3. 核心结论

### 3.1 必须采用分层存储

信息流不能只保留最终摘要，也不能把所有内容都塞进一个 `feed_items` 表。必须至少拆成四层：

1. 原始层 `raw_ingest`
2. 标准条目层 `feed_items`
3. 富化分析层 `feed_enrichments`
4. 聚合分析层 `feed_aggregates`

### 3.2 必须采用对象存储抽象

原始层最终要面向对象存储设计，而不是把本地文件系统当作长期架构前提。

实现策略：

- 开发阶段：`LocalObjectStore`
- 生产/扩展阶段：`S3CompatibleObjectStore`

业务代码只依赖统一接口，不直接依赖本地路径。

### 3.3 PostgreSQL 是信息流事实库

未来的信息流事实来源必须是 PostgreSQL，而不是 `FeedFetcher._cache`。

`_cache` 只能保留为：

- 抓取短缓存
- API 热数据缓存前置层
- 失败回退层

不能继续作为主事实层。

### 3.4 Qdrant 不是主存储

Qdrant 的职责应限定为：

- 语义检索
- 近似重复检测
- 主题/事件相似性搜索
- RAG 上下文召回

不承担原始数据、结构化事实、聚合分析的主存储职责。

---

## 4. 目标架构

```text
信息源 / RSS / Web / API
        |
        v
Ingest Worker
        |
        +--> Raw Object Store
        |      - 原始 XML / HTML / JSON / PDF / 截图
        |
        +--> PostgreSQL.raw_ingest
               - 原始对象元数据
               - 抓取状态
               - 代理 / 反爬结果
        |
        v
Normalize Worker
        |
        +--> PostgreSQL.feed_items
        +--> PostgreSQL.feed_item_versions
        +--> PostgreSQL.feed_clusters
        |
        v
Enrichment Worker
        |
        +--> PostgreSQL.feed_enrichments
        +--> PostgreSQL.feed_entities
        +--> PostgreSQL.feed_tags
        +--> Qdrant.feed_item_vectors
        |
        v
Aggregate Worker
        |
        +--> PostgreSQL.feed_aggregates_daily
        +--> PostgreSQL.feed_source_metrics_daily
        +--> PostgreSQL.feed_topic_trends
        |
        v
API / Chat / Knowledge / Evolution
        |
        +--> Redis cache
```

---

## 5. 存储职责划分

### 5.1 对象存储

职责：

- 保存原始抓取结果
- 保存中间处理产物
- 保存附件和快照

典型对象：

- RSS 原始 XML
- 网页原始 HTML
- API 原始 JSON
- PDF / 图片 / 截图
- 深度抽取输入输出
- AI 摘要前后的原始语料快照

开发期实现：

- 本地目录，例如 `data/object_store/...`

长期实现：

- MinIO / S3 / OSS

### 5.2 PostgreSQL

职责：

- 所有结构化事实数据
- 所有处理状态
- 所有分析结果与聚合结果
- 与知识库、任务系统、交互系统的关联

PostgreSQL 是信息流的事实数据库。

### 5.3 Redis

职责：

- 热门信息流查询缓存
- 去重短键
- 任务队列缓冲
- 调度器状态
- API 热点分页缓存

Redis 不保存长期事实，只承担临时加速层。

### 5.4 Qdrant

职责：

- 文本 embedding
- 相似文章召回
- 近重复检测辅助
- 聊天/RAG 召回

---

## 6. 数据分层设计

### 6.1 原始层

#### 目标

- 保证可追溯
- 保证可重跑
- 保留多版本抓取快照

#### 建议对象前缀

```text
raw/{source_id}/{yyyy}/{mm}/{dd}/{object_id}.xml.gz
raw/{source_id}/{yyyy}/{mm}/{dd}/{object_id}.html.gz
raw/{source_id}/{yyyy}/{mm}/{dd}/{object_id}.json.gz
artifacts/{pipeline_stage}/{yyyy}/{mm}/{dd}/{object_id}.json.gz
```

#### 建议表：`raw_ingest`

建议字段：

- `id`
- `source_id`
- `fetch_job_id`
- `object_key`
- `content_type`
- `content_encoding`
- `content_hash`
- `size_bytes`
- `fetched_at`
- `http_status`
- `access_method`
- `proxy_used`
- `anti_crawl_status`
- `request_meta`
- `response_meta`
- `parse_status`
- `error_message`

说明：

- 原始内容本体不进表
- 表里只存元数据和定位信息

### 6.2 标准条目层

#### 目标

- 为展示、分析、知识抽取提供统一条目模型
- 解决不同来源格式不一致的问题

现有表 `feed_items` 可继续保留，但需要升级为真正主事实表。

建议新增/补强字段：

- `canonical_url`
- `raw_ingest_id`
- `content_hash`
- `language`
- `region`
- `published_at`
- `fetched_at`
- `normalized_at`
- `dedupe_key`
- `cluster_id`
- `author`
- `source_authority_score_snapshot`
- `status`

建议新增表：`feed_item_versions`

作用：

- 保存同一条内容多次抓取后的版本变化
- 用于检测编辑更新、补充信息、标题变更

### 6.3 富化分析层

#### 目标

- 不污染主事实表
- 允许分析模型反复演进

建议表：

- `feed_enrichments`
- `feed_entities`
- `feed_topics`
- `feed_tags`
- `feed_sentiment`
- `feed_claims`

`feed_enrichments` 可保存：

- 重要度
- 可信度
- 时效性
- 事件性
- 学科归类
- 行业归类
- AI 摘要
- 长摘要
- 质量评分
- 模型版本
- 富化时间

设计原则：

- 主体结构字段用独立列
- 灵活字段可用 `JSONB`
- 每次富化要带 `model_version` / `pipeline_version`

### 6.4 聚合分析层

#### 目标

- 为趋势分析、月报、专题总结提供高效查询

建议表：

- `feed_aggregates_daily`
- `feed_source_metrics_daily`
- `feed_topic_trends`
- `feed_cluster_metrics_daily`

典型指标：

- 每日文章数
- 每日来源产出数
- 每日主题热度
- 热度增速
- 来源命中率
- 来源知识转化率
- 来源阅读率 / 收藏率 / 引用率

---

## 7. 新的处理流水线

### 7.1 流水线阶段

#### 阶段 1：抓取

输入：

- 信息源配置

输出：

- 原始对象写入对象存储
- 元数据写入 `raw_ingest`

#### 阶段 2：标准化

输入：

- `raw_ingest`

输出：

- `feed_items`
- `feed_item_versions`

#### 阶段 3：去重与聚类

输入：

- 新写入的 `feed_items`

输出：

- `feed_clusters`
- `feed_cluster_members`

#### 阶段 4：富化

输入：

- `feed_items`
- `feed_clusters`

输出：

- 标签
- 实体
- 摘要
- 情绪
- 可信度
- embedding

#### 阶段 5：聚合

输入：

- 条目事实
- 富化结果
- 交互结果
- 知识转化结果

输出：

- 各类日报 / 周报 / 趋势表

### 7.2 执行方式

当前阶段建议保守实现：

- 仍然使用 Python + FastAPI 后台任务
- 但把处理逻辑拆成独立 worker 模块

建议拆为：

- `ingest_worker`
- `normalize_worker`
- `enrichment_worker`
- `aggregate_worker`

后续扩展时，可将其独立部署为多进程服务。

---

## 8. 服务边界调整

### 8.1 FeedFetcher 的新职责

保留：

- 源配置读取
- 抓取
- 代理决策
- 短期缓存

移除“事实来源”职责：

- 不再由 `FeedFetcher._cache` 直接代表信息流全量事实

### 8.2 `/api/feeds` 的新职责

当前：

- 主要从 `FeedFetcher._cache` 返回数据

目标：

- 从 PostgreSQL 的 `feed_items + enrichments + interactions` 读取
- Redis 只作为热点缓存

### 8.3 `/api/feeds/import` 的新职责

当前：

- 向内存缓存注入数据

目标：

- 写原始层或标准层
- 完成持久化
- 触发后续处理任务

### 8.4 Chat / Knowledge / Evolution 的依赖方式

目标统一为：

- Chat 从结构化条目和向量层读取
- Knowledge 从条目事实层抽取
- Evolution 从聚合分析层读取指标

不直接依赖抓取缓存。

---

## 9. 推荐技术选型

### 9.1 当前阶段

- API / Orchestration: FastAPI
- Facts / Aggregates: PostgreSQL
- Queue / Cache: Redis
- Embeddings / Similarity: Qdrant
- Raw objects: Local filesystem via object-store adapter

### 9.2 后续扩展阶段

- Raw objects: MinIO / S3 / OSS
- Worker deployment: 独立进程或容器化
- Scheduling: 保留现有调度器，后续可接 Redis 队列

### 9.3 当前不引入

- Kafka
- Spark
- Flink
- ClickHouse
- 图数据库

原因：

- 当前阶段复杂度过高
- 主问题还不是计算性能，而是事实层未形成

---

## 10. 开发期与生产期模式

### 10.1 开发期

- 单机运行
- PostgreSQL 本地进程
- Redis 本地进程
- Qdrant 本地嵌入式
- Object store 使用本地目录

### 10.2 生产/扩展期

- API 与 worker 分离部署
- PostgreSQL 独立实例
- Redis 独立实例
- Qdrant 独立实例
- 对象存储改为 MinIO / S3 / OSS

### 10.3 关键兼容原则

- 业务代码不依赖本地路径
- 业务代码不依赖单进程缓存
- 所有阶段任务要可重试、可幂等

---

## 11. 实施路线图

### Phase 1：打地基

目标：

- 建立对象存储抽象
- 建立 `raw_ingest`
- 改造导入链路持久化

交付：

- `ObjectStore` 接口
- `LocalObjectStore`
- `raw_ingest` 表
- `feeds/import` 落库

### Phase 2：信息流主链路落库

目标：

- 让 `feed_items` 成为事实层

交付：

- 抓取后标准化写 `feed_items`
- `/api/feeds` 改读数据库
- 交互数据闭环

### Phase 3：富化与聚类

目标：

- 为趋势分析和知识抽取建立分析层

交付：

- enrichment 表
- cluster 表
- embedding 写入

### Phase 4：趋势与总结

目标：

- 建立长期分析能力

交付：

- 日/周/月聚合表
- 趋势分析 API
- 深度总结 API

### Phase 5：分布式化

目标：

- 从单机平滑扩展到多机

交付：

- 对象存储切换
- worker 独立部署
- Redis 驱动任务队列

---

## 12. 关键设计原则

1. 原始层必须可重放。
2. API 层不直接依赖抓取缓存。
3. 缓存不是事实。
4. 原始对象与结构化事实分离。
5. 富化结果与原始事实分离。
6. 所有分析结果都必须带版本信息。
7. 所有任务都必须具备幂等性。
8. 单机实现只是部署模式，不是架构前提。

---

## 13. 对现有系统的影响

### 影响模块

- `services/api/feeds/fetcher.py`
- `services/api/routers/feeds.py`
- `services/api/db/models.py`
- `migrations/*`
- `services/api/pipeline/*`
- `services/api/knowledge/*`
- `services/api/feeds/evolution.py`

### 风险点

- 现有前端依赖 `/api/feeds` 的响应结构，需要保持兼容
- 现有缓存式逻辑与落库式逻辑会并存一段时间
- 需要处理历史内存导入数据无法完全回溯的问题

### 兼容策略

- 先双写
- 再双读验证
- 最后切换主读路径

---

## 14. 文档与交接要求

本设计落地后，每一阶段实施都必须补充：

- 迁移脚本
- API 变更说明
- 数据回填策略
- 回滚策略
- 运行验证步骤

后续实现文档建议继续追加到：

- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `PROGRESS.md`

---

*版本：v0.1*
*状态：已批准，待实施*
*最后更新：2026-03-18*
