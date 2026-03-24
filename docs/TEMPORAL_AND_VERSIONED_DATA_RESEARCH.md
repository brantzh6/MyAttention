# 时间化与版本化数据研究

> 目标：为 MyAttention 研究“时间维度变化过程”应如何记录、追踪、管理，明确哪些数据属于时间序列、哪些属于事件流、哪些属于版本对象，以及是否需要引入专门时序数据库。

---

## 1. 研究问题

MyAttention 后续会持续演化的不只是代码，还包括：

- 认知框架
- 方法选择
- 任务状态
- 知识理解
- 记忆沉淀
- 来源评估
- 测试基线
- 进化策略

因此必须回答：

1. 哪些数据天然是时间序列
2. 哪些数据更像事件流
3. 哪些数据必须做版本对象
4. 什么时候需要专门 TSDB
5. 当前阶段应优先设计什么，而不是先引新系统

---

## 2. 初步结论

### 2.1 有时间维度，不等于应该立刻上 TSDB

这是最重要的纠偏。

“数据随时间变化”不自动等于：

- InfluxDB
- Prometheus
- TimescaleDB

因为 MyAttention 的时间性数据至少有四种，它们的结构完全不同。

### 2.2 当前更关键的是设计“时间化语义”，不是仓促选库

短期优先级应该是：

1. 先分清数据类型
2. 先定义统一时间字段和版本语义
3. 先用 PostgreSQL + Object Storage 承载 V1
4. 采样量和聚合复杂度上来后，再决定是否引 TSDB

---

## 3. 时间性数据分类 V1

### 3.1 指标时间序列 `metric_series`

典型例子：

- self-test pass rate
- source success rate
- collection lag
- voting quality score
- task backlog
- latency

特点：

- append-only
- 数值型
- 高频采样可能较多
- 强聚合需求

适合：

- 快照表
- 时序扩展
- 可后续迁到 TSDB

### 3.2 事件流 `event_stream`

典型例子：

- task 状态流转
- source 被升级/降级/淘汰
- 某次恢复动作执行
- 某个 brain route 被切换

特点：

- 面向“发生了什么”
- 不只是数值
- 更像审计历史

适合：

- append-only event log
- PostgreSQL 事件表

### 3.3 版本对象 `versioned_object`

典型例子：

- 认知框架 V1 -> V2
- 方法策略 V3 -> V4
- 某知识条目当前理解的版本演进
- 某 source profile 的评估版本

特点：

- 面向“某对象在不同时间的状态”
- 需要 lineage
- 需要回滚和比较

适合：

- 版本表
- lineage 关系
- bitemporal 或至少 valid-time 设计

### 3.4 原始观测与证据 `raw_evidence`

典型例子：

- 原始 feed 内容
- 原始日志
- 截图
- 外部研究文档快照
- UI 巡检结果附件

特点：

- 体积可能大
- 格式多样
- 主要服务回放和取证

适合：

- object storage + metadata index

---

## 4. 是否需要 TSDB

### 4.1 当前不建议立即引入独立 TSDB

原因：

- 当前阶段更缺的是时间/版本语义，而不是存储性能
- 主问题还不是高频时序计算，而是对象、任务、知识和方法的版本追踪
- 系统复杂度已经较高，再引入新基础设施收益不成正比

### 4.2 未来可能需要 TSDB 的信号

当出现这些情况时再评估：

- 指标采样频率明显上升
- retention / downsampling 成为刚需
- 监控聚合查询明显变重
- 时间窗分析成为日常核心工作台
- 单靠 PostgreSQL 指标快照已明显吃力

### 4.3 更现实的技术路线

V1：

- PostgreSQL
- Object Storage
- Qdrant
- Redis

V2 再评估：

- TimescaleDB
- 或其他与 PostgreSQL 更贴近的时序扩展

---

## 5. 统一时间字段建议

后续设计里，不能只保留一个 `created_at`。

至少要明确这些时间字段语义：

- `created_at`
  - 记录创建时间
- `updated_at`
  - 记录最近修改时间
- `observed_at`
  - 系统观测到某现象的时间
- `event_at`
  - 事件实际发生时间
- `published_at`
  - 来源内容发布时间
- `ingested_at`
  - 系统摄取时间
- `valid_from`
  - 当前版本开始生效时间
- `valid_to`
  - 当前版本失效时间
- `superseded_at`
  - 被新版本替代时间

这一步很关键，因为：

- 不同问题对“时间”关注的是不同语义
- 没有语义区分，后面会混淆时效性、发现时间和事实发生时间

---

## 6. 版本对象的最小通用结构

后续很多实体都应共享类似版本字段：

- `entity_id`
- `entity_type`
- `version`
- `parent_version`
- `change_reason`
- `effective_from`
- `effective_to`
- `status`
- `evaluation_result`
- `created_by`
- `created_at`
- `metadata`

这套结构可用于：

- cognition version
- method version
- task plan version
- knowledge version
- memory version
- source policy version

---

## 7. 与各主线的关系

### 7.1 信息大脑

需要时间化：

- 来源表现
- 来源更新频率
- 主题热度
- 事实时效性

需要版本化：

- source profile
- source plan
- source policy

### 7.2 知识大脑

需要时间化：

- 事实发生时间
- 发表时间
- 当前理解的适用时期

需要版本化：

- 知识条目
- 权威理解
- 前沿研究解读

### 7.3 进化大脑

需要时间化：

- self-test 历史
- issue 发生与恢复时间
- 质量趋势

需要版本化：

- policy
- skill / playbook
- diagnosis template
- evaluation method

---

## 8. 短期研究结论

1. 先不要把“时间维度”简单等同于 TSDB。
2. MyAttention 至少要同时处理 `metric_series / event_stream / versioned_object / raw_evidence` 四类时间性数据。
3. 当前最优先的是统一时间字段语义和版本对象语义。
4. V1 以 PostgreSQL + Object Storage 为主，不急于增加专门 TSDB。
5. 后续正式设计应进入 `VERSIONED_INTELLIGENCE_ARCHITECTURE.md`。
