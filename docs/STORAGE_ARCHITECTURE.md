# 存储层架构设计

> 目标：为 MyAttention 建立一个可从单机开发平滑演进到多机部署的统一存储架构，明确对象存储、关系库、缓存、向量库的职责边界，以及原始层、事实层、富化层、聚合层的落地方式。

---

## 1. 设计目标

### 1.1 核心目标

- 为信息大脑、知识大脑、进化大脑提供统一的数据底座
- 保证原始数据可追溯、可重放、可重处理
- 保证结构化事实可查询、可统计、可聚合
- 保证语义检索与主事实存储分离
- 保证单机开发模式与未来分布式部署使用同一套抽象

### 1.2 架构目标

- 本地开发可直接运行
- 后续可切换到 MinIO / S3 / OSS 而不修改业务逻辑
- API 层不依赖具体文件路径
- 处理流水线依赖对象 ID 和元数据，而不是本地路径
- 存储职责清晰，不出现“缓存当事实库”的情况

### 1.3 非目标

- 本阶段不引入大数据平台
- 本阶段不引入专用图数据库
- 本阶段不追求复杂冷热分层策略自动化

---

## 2. 总体存储拓扑

```text
                   +----------------------+
                   |  Object Storage      |
                   | raw blobs / artifacts|
                   +----------+-----------+
                              |
                              v
+-------------+      +--------+---------+      +-----------------+
|   Redis     | <--> |   PostgreSQL     | <--> |     Qdrant      |
| cache/queue |      | facts / metadata |      | vector retrieval|
+-------------+      +------------------+      +-----------------+
```

### 2.1 角色划分

- Object Storage：保存原始对象、大附件、中间产物、快照
- PostgreSQL：保存结构化事实、对象元数据、任务状态、分析结果
- Redis：保存缓存、去重短键、队列缓冲、调度状态
- Qdrant：保存 embedding、相似检索索引、RAG 检索向量

### 2.2 基本原则

1. 原始对象不直接塞进 PostgreSQL 主表。
2. PostgreSQL 是事实层，不是大对象归档层。
3. Redis 只做加速层和缓冲层，不做长期事实层。
4. Qdrant 只做语义层，不做主事实层。
5. 所有原始层处理都通过对象 ID 和元数据关联。

---

## 3. 存储层分工

### 3.1 Object Storage

适合保存：

- 原始 RSS XML
- 原始网页 HTML
- 原始 API JSON
- PDF / 图片 / 截图
- 中间处理结果
- 大模型输入输出归档
- 抓取快照和重放数据

约束：

- 业务代码不直接拼接本地磁盘路径
- 所有对象通过 `object_key` 标识
- 支持后端实现切换：本地文件系统 -> S3 兼容对象存储

### 3.2 PostgreSQL

适合保存：

- `raw_ingest` 元数据
- `feed_items` 事实条目
- `feed_enrichments` 富化结果
- `feed_aggregates_*` 聚合结果
- 任务、日志分析结果、测试结果
- 知识链接、用户交互、指标快照

约束：

- 原始大对象正文不作为主存储方式写入表字段
- 所有结构化分析要有版本号和时间戳
- 事实层和富化层尽量拆表，不堆进单个 JSON 字段

### 3.3 Redis

适合保存：

- 热门信息流分页缓存
- 临时去重键
- 队列缓冲
- 调度器心跳
- 临时状态和速率限制数据

约束：

- Redis 中的数据可以丢
- Redis 不承担长期历史保留

### 3.4 Qdrant

适合保存：

- feed item embeddings
- knowledge embeddings
- 相似文章召回索引
- 聚类辅助向量索引

约束：

- 向量记录必须能回溯到 PostgreSQL 主记录
- 删除、重建、迁移时要以主事实层为准

---

## 4. 对象存储抽象

### 4.1 统一接口

建议定义统一接口 `ObjectStore`：

```python
class ObjectStore:
    async def put_bytes(self, key: str, data: bytes, content_type: str | None = None) -> ObjectRef: ...
    async def get_bytes(self, key: str) -> bytes: ...
    async def exists(self, key: str) -> bool: ...
    async def delete(self, key: str) -> None: ...
    async def head(self, key: str) -> ObjectMeta: ...
    async def list_prefix(self, prefix: str) -> list[ObjectMeta]: ...
```

### 4.2 开发期实现

- `LocalObjectStore`
- 存储位置建议：`services/api/data/object_store/`
- 作用：本地开发、单机验证、无对象存储服务时运行

### 4.3 生产期实现

- `S3CompatibleObjectStore`
- 支持：
  - MinIO
  - Amazon S3
  - 阿里云 OSS
  - 其他兼容 S3 API 的对象存储

### 4.4 设计要求

- 业务层不直接感知是本地文件还是 OSS
- API 层只接触 `object_key`、元数据、签名访问能力
- 对象命名必须稳定且可按前缀扫描

---

## 5. 元数据模型

### 5.1 原始对象元数据表 `raw_ingest`

建议字段：

- `id`
- `source_id`
- `fetch_job_id`
- `object_key`
- `storage_backend`
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
- `created_at`

用途：

- 定位原始对象
- 记录抓取上下文
- 作为后续标准化和重放的入口

### 5.2 事实层关联

建议 `feed_items` 至少包含：

- `raw_ingest_id`
- `canonical_url`
- `content_hash`
- `dedupe_key`
- `cluster_id`
- `published_at`
- `fetched_at`
- `normalized_at`

建议富化层记录：

- `feed_item_id`
- `pipeline_version`
- `model_version`
- `importance_score`
- `credibility_score`
- `topic_labels`
- `entity_summary`
- `summary_short`
- `summary_long`

---

## 6. 对象命名与目录建议

### 6.1 推荐对象键格式

```text
raw/{source_id}/{yyyy}/{mm}/{dd}/{object_id}.xml.gz
raw/{source_id}/{yyyy}/{mm}/{dd}/{object_id}.html.gz
raw/{source_id}/{yyyy}/{mm}/{dd}/{object_id}.json.gz
artifacts/{stage}/{yyyy}/{mm}/{dd}/{object_id}.json.gz
attachments/{source_id}/{yyyy}/{mm}/{dd}/{object_id}.pdf
```

### 6.2 命名原则

- 按来源和日期做前缀分桶
- 使用稳定对象 ID，避免用原始标题作为文件名
- 压缩文本类原始对象
- 元数据记录 `content_hash`，支持去重和一致性校验

---

## 7. 部署模式

### 7.1 开发模式

- PostgreSQL：本机进程
- Redis：本机进程
- Qdrant：本地模式或本机进程
- Object Storage：`LocalObjectStore`

适合：

- 单机开发
- 本地联调
- 无容器环境

### 7.2 单机生产/过渡模式

- PostgreSQL：单机服务
- Redis：单机服务
- Qdrant：单机服务
- Object Storage：MinIO

适合：

- 小规模私有部署
- 从开发模式升级到可维护环境

### 7.3 多机扩展模式

- PostgreSQL：独立数据库实例
- Redis：独立缓存/队列实例
- Qdrant：独立向量服务
- Object Storage：S3 / OSS / MinIO 集群
- Worker：独立 ingest / enrich / aggregate 进程

适合：

- 数据量持续增长
- 处理任务和 API 解耦
- 多节点扩容

---

## 8. 数据流与存储落点

```text
抓取
  -> Object Storage 写入原始对象
  -> PostgreSQL 写 raw_ingest 元数据

标准化
  -> PostgreSQL 写 feed_items / feed_item_versions

富化
  -> PostgreSQL 写 feed_enrichments / entities / tags
  -> Qdrant 写 embeddings

聚合
  -> PostgreSQL 写 daily aggregates / trends

展示与检索
  -> API 从 PostgreSQL 取事实
  -> Redis 做热点缓存
  -> Qdrant 做语义检索补充
```

---

## 9. 迁移策略

### 9.1 当前状态

- 运行态信息流仍有部分依赖内存缓存
- 原始层未形成统一对象存储抽象
- `/api/feeds` 仍未完全切到数据库事实层

### 9.2 目标状态

- 所有导入和抓取先落对象存储与元数据
- 标准化结果进入 PostgreSQL
- `/api/feeds` 从 PostgreSQL 读取
- Redis 只做热点缓存

### 9.3 分阶段实施

#### Phase 1

- 引入 `ObjectStore` 接口
- 实现 `LocalObjectStore`
- 新增 `raw_ingest` 表

#### Phase 2

- 改造抓取和导入链路，先落原始层
- 标准化写入 `feed_items`
- 建立 `raw_ingest -> feed_items` 关联

#### Phase 3

- 富化结果拆表
- 接入 embeddings 与相似检索
- 聚类、事件簇、主题标签入库

#### Phase 4

- 聚合分析表和趋势表落地
- 为总结、推荐、研究专题提供稳定数据源

#### Phase 5

- 切换对象存储后端到 MinIO / S3 / OSS
- 引入独立 worker
- 完成单机到多机部署迁移

---

## 10. 验收要求

- 开发模式下可在无容器环境运行
- 同一业务逻辑可切换 `LocalObjectStore` 与 S3 兼容实现
- `raw_ingest` 能完整记录原始对象定位和抓取上下文
- `/api/feeds` 最终不再直接依赖进程内缓存作为事实来源
- 原始对象、事实记录、向量记录之间可相互追溯

---

## 11. 与其他文档关系

- 项目总纲：[PROJECT_MASTER_PLAN.md](./PROJECT_MASTER_PLAN.md)
- 系统总架构：[ARCHITECTURE.md](./ARCHITECTURE.md)
- 信息流数据分层：[FEED_DATA_ARCHITECTURE.md](./FEED_DATA_ARCHITECTURE.md)
- 部署设计：[DEPLOYMENT.md](./DEPLOYMENT.md)
