# Phase 1 对象存储与原始层实施计划

> 目标：完成信息流架构改造的第一阶段，为后续“信息流事实层落库”建立可执行底座。该阶段只做基础设施和最小接入，不追求把整条信息流链路一次性改完。

---

## 1. Phase 目标

本阶段要完成 4 件事：

1. 定义统一 `ObjectStore` 抽象接口
2. 落地 `LocalObjectStore`
3. 建立 `raw_ingest` 元数据模型与迁移
4. 打通最小原始层写入路径

完成后应具备的能力：

- 本地无容器环境可运行
- 原始对象可以通过统一接口写入本地对象层
- PostgreSQL 中有可追溯的 `raw_ingest` 元数据
- 后续 `feed_items` 持久化改造有明确挂接点

---

## 2. 本阶段边界

### 2.1 在范围内

- `ObjectStore` 接口定义
- `LocalObjectStore` 实现
- 对象键生成规则
- `raw_ingest` 表设计与迁移
- `raw_ingest` 的数据库模型和最小写入服务
- 最小可验证的写入链路
- 配置项与运行模式说明

### 2.2 不在范围内

- 全量替换 `/api/feeds` 数据来源
- 完整 `feed_items` 双写改造
- 富化层入库
- 聚合层入库
- 多机部署和云对象存储切换

---

## 3. 目标代码落点

建议新增或修改的区域：

- `services/api/storage/`
  - `base.py`
  - `local.py`
  - `factory.py`
- `services/api/config.py`
- `services/api/db/models.py`
- `migrations/006_raw_ingest.sql`
- `services/api/feeds/`
  - 新增原始层写入服务或仓储模块
- `services/api/tests/`
  - `ObjectStore`
  - `raw_ingest`
  - 最小写入链路测试

---

## 4. 数据设计

### 4.1 `ObjectStore` 最小接口

建议最小接口：

```python
class ObjectStore:
    async def put_bytes(self, key: str, data: bytes, content_type: str | None = None) -> ObjectRef: ...
    async def get_bytes(self, key: str) -> bytes: ...
    async def exists(self, key: str) -> bool: ...
    async def delete(self, key: str) -> None: ...
    async def head(self, key: str) -> ObjectMeta: ...
```

说明：

- Phase 1 先不做复杂签名 URL 和批量列举
- 只保留后续链路一定会用到的最小能力

### 4.2 `raw_ingest` 表建议字段

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

设计原则：

- 原始对象正文不进表
- 表里只放元数据、追溯信息和状态信息

---

## 5. 实施顺序

### Step 1：存储抽象

- 新建 `storage/base.py`
- 定义 `ObjectStore`、`ObjectRef`、`ObjectMeta`
- 新建 `storage/factory.py`
- 支持通过配置返回 `LocalObjectStore`

### Step 2：本地对象存储实现

- 新建 `storage/local.py`
- 目标目录：`services/api/data/object_store/`
- 支持：
  - 写入字节
  - 读取字节
  - 文件存在判断
  - 删除
  - 元数据读取

### Step 3：对象键规则

建议格式：

```text
raw/{source_id}/{yyyy}/{mm}/{dd}/{object_id}.json.gz
raw/{source_id}/{yyyy}/{mm}/{dd}/{object_id}.html.gz
raw/{source_id}/{yyyy}/{mm}/{dd}/{object_id}.xml.gz
```

要求：

- 对象键稳定
- 不依赖标题
- 支持后续迁移到 S3 兼容对象存储

### Step 4：数据库迁移

- 新增 `migrations/006_raw_ingest.sql`
- 建表
- 增加必要索引：
  - `source_id`
  - `fetched_at`
  - `content_hash`
  - `object_key`

### Step 5：最小写入服务

- 新增原始层写入服务
- 输入：字节流 + 元数据
- 输出：
  - 对象写入 `ObjectStore`
  - 元数据写入 `raw_ingest`

### Step 6：最小接入点

本阶段只选一个接入点打通，不一次性改整条链路。

推荐优先级：

1. `/api/feeds/import`
2. 内部抓取入口

理由：

- `import` 更可控
- 更容易构造最小验证
- 风险更低

---

## 6. 测试计划

### 6.1 必须有的测试

- `LocalObjectStore` 读写测试
- `LocalObjectStore` 删除与存在判断测试
- `raw_ingest` 迁移执行测试
- 原始层写入服务测试
- 最小接入点端到端验证

### 6.2 验证内容

- 原始对象能落到本地对象目录
- `raw_ingest` 能正确记录对象键和元数据
- `content_hash` 和 `size_bytes` 正确
- 写入失败时有可追溯错误
- 本地运行不依赖 Docker

### 6.3 暂不要求

- UI 自动化
- 大规模性能压测
- 多机兼容验证

---

## 7. 风险与控制

### 风险 1：一次性改太多

控制：

- Phase 1 只打底座
- 只选一个最小接入点

### 风险 2：对象层设计过重

控制：

- 只做最小接口
- 不在 Phase 1 引入 S3 兼容实现

### 风险 3：写入成功但后续链路没接住

控制：

- 只承诺原始层与元数据层打通
- `feed_items` 改造放到 Phase 2

### 风险 4：本地文件实现污染业务逻辑

控制：

- 业务代码只依赖 `ObjectStore`
- 不直接拼接本地磁盘路径

---

## 8. 验收标准

满足以下条件即视为 Phase 1 完成：

- `ObjectStore` 抽象存在并可用
- `LocalObjectStore` 可在本地运行
- `raw_ingest` 迁移成功
- 至少一个接入点完成原始层写入
- 有对应测试和验证结果
- 文档、进度、变更记录完成更新

---

## 9. 与 gstack 试用的关系

这份文档建议作为重启 Codex 后第一次 gstack 试用输入。

推荐顺序：

1. 用 `plan-eng-review` 审一遍本计划
2. 编码完成后用 `review`
3. 接口打通后做最小验证
4. 如果涉及页面联调，再考虑 `qa`

评估重点：

- 是否帮助发现架构遗漏
- 是否改善测试计划完整性
- 是否显著增加无效流程成本

使用结果需记录到：

- `docs/SKILL_EVALUATION_LOG.md`

---

## 10. 下一阶段衔接

Phase 1 完成后，进入 Phase 2：

- `feed_items` 持久化
- `raw_ingest -> feed_items` 关联
- `/api/feeds` 向事实层切换前的双写准备
