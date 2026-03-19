# Phase 2 信息流事实层落库实施计划

> 目标：把信息流主链路从“以内存缓存为事实来源”推进到“以 PostgreSQL `feed_items` 为事实来源，内存缓存仅做短期性能层”。

---

## 1. Phase 目标

本阶段完成 4 件事：

1. 建立 `feed_items` 的标准化持久化写入链路
2. 建立 `source_key -> sources.id` 的稳定映射
3. 让 `/api/feeds/import` 和内部抓取链路具备写入 `feed_items` 的能力
4. 为 `/api/feeds` 从缓存读切换到数据库读做好兼容层

完成后应具备的能力：

- 信息流条目有稳定历史，不再只存在于 `FeedFetcher._cache`
- 单条信息可以追溯到 `raw_ingest`
- `feed_items` 可作为后续富化、聚类、趋势分析的事实层
- `/api/feeds` 仍可用，但底层可逐步切换到数据库

---

## 2. 本阶段边界

### 2.1 在范围内

- `feed_items` 标准化写入服务
- `source_key` 到 `sources` 的映射策略
- `/api/feeds/import` 双写：`raw_ingest + feed_items + cache`
- 内部抓取链路的最小双写接入
- 数据库读取适配层
- Phase 2 自动化测试和烟测

### 2.2 不在范围内

- 富化层入库
- embedding / Qdrant 写入
- 聚类、趋势、深度总结
- 全量替换前端接口
- 大规模历史回填

---

## 3. 核心设计

### 3.1 事实层原则

- `raw_ingest` 负责原始对象追溯
- `feed_items` 负责标准化事实条目
- `FeedFetcher._cache` 只做短缓存，不再作为长期事实层

### 3.2 最小数据流

```text
import/fetch
  -> raw_ingest
  -> normalize
  -> feed_items
  -> cache injection
  -> /api/feeds read adapter
```

### 3.3 标准化字段

至少写入：

- `source_id`
- `external_id`
- `title`
- `summary`
- `content`
- `url`
- `importance`
- `published_at`
- `fetched_at`
- `extra`

建议在 `extra` 中保留：

- 原始分类
- 来源显示名
- 原始 source_key
- `raw_ingest_id`
- 导入方式

### 3.4 source 映射策略

Phase 2 先采用保守策略：

- 已存在同 `url` 或同 `name` 的 source：复用
- 不存在时：
  - 对 `import` 来源建立最小 `Source`
  - `type = rss`
  - `enabled = true`
  - `status = ok`
  - `config.extra.imported = true`

---

## 4. 代码落点

- `services/api/feeds/`
  - 新增 `persistence.py`
  - 或新增 `feed_item_store.py`
- `services/api/routers/feeds.py`
- `services/api/db/models.py`
- `services/api/db/`
  - 如需要，补 repository / query helper
- `services/api/tests/`
  - `test_feed_item_persistence.py`
  - `test_feeds_import_flow.py`

---

## 5. 实施顺序

### Step 1：写入服务

- 新增 `persist_feed_item(...)`
- 输入：
  - `raw_ingest` 记录
  - 标准化后的导入条目
- 输出：
  - `FeedItem`
  - 是否新建 / 是否重复

### Step 2：source 解析

- 新增 `resolve_source_for_import(...)`
- 根据 `source_key / source_name / link` 找到或创建 `Source`

### Step 3：import 双写

- `/api/feeds/import` 改成：
  - 先写 `raw_ingest`
  - 再写 `feed_items`
  - 最后注入缓存
- 返回值增加：
  - `persisted`
  - `duplicates`
  - `errors`

### Step 4：读取适配层

- 新增数据库读取适配方法
- 先不完全切掉缓存
- `/api/feeds` 增加受控开关：
  - 默认仍兼容现有行为
  - 可在开发环境切换数据库读做验证

---

## 6. 测试计划

必须覆盖：

- `persist_feed_item` 新建与去重
- `resolve_source_for_import` 的复用与创建
- `/api/feeds/import` 的 `raw_ingest + feed_items + cache` 端到端路径
- 数据库读取适配层返回格式

至少要做的验证：

- 同一 `source_key + external_id` 重复导入不会产生重复事实条目
- `feed_items.extra.raw_ingest_id` 能追溯到原始层
- 新条目导入后仍能在 `/api/feeds` 中看到

---

## 7. 风险与控制

### 风险 1：source 误建太多

控制：

- Phase 2 先偏保守
- 只在缺失时创建最小 source
- 后续再做 source 合并规则

### 风险 2：双写后缓存和数据库不一致

控制：

- 顺序固定为 `raw -> fact -> cache`
- 一旦 `feed_items` 写失败，不注入缓存

### 风险 3：一次性切换读路径导致回归

控制：

- 先加读取适配层和开关
- 不在 Phase 2 里强行全量切换

---

## 8. 验收标准

满足以下条件即可视为 Phase 2 完成：

- `feed_items` 有稳定写入链路
- `/api/feeds/import` 已完成 `raw_ingest + feed_items + cache` 双写
- 至少一条内部抓取链路完成最小接入
- `/api/feeds` 已具备数据库读取适配能力
- 有对应自动化测试和真实烟测
