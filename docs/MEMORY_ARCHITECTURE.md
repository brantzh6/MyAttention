# 记忆架构设计 V1

> 本文档定义 MyAttention 的 `Memory Architecture` `V1`。
>
> 目标不是一次性做出终局记忆系统，而是先建立一个：
>
> - 分层清晰
> - 可追溯
> - 可恢复
> - 可扩展
> - 可被后续进化替换和升级
>
> 的记忆基础设施。

---

## 1. 文档定位

本设计解决的问题是：

- MyAttention 的“记忆”到底包含哪些层
- 哪些内容属于聊天历史，哪些不属于
- 复杂任务、研究过程、进化经验应该存在哪里
- 如何兼顾“不丢失”和“高效回忆”
- 如何为后续多大脑协作、方法迭代、知识演化预留空间

本设计不直接解决：

- 完整多脑协作协议
- 完整知识图谱结构
- 全量版本化智能体系
- 全量深度研究工作流

这些属于后续设计：

- `docs/TASK_AND_WORKFLOW_MODEL.md`
- `docs/BRAIN_CONTROL_ARCHITECTURE.md`
- `docs/KNOWLEDGE_ARCHITECTURE.md`
- `docs/VERSIONED_INTELLIGENCE_ARCHITECTURE.md`

---

## 2. 设计目标

### 2.1 核心目标

- 把“聊天上下文”“长期事实”“经验”“程序性方法”明确分开
- 让复杂任务和进化过程具有可恢复、可回放、可比较的记忆基础
- 为信息大脑、知识大脑、进化大脑提供统一的记忆语义
- 避免把“记忆”简化成向量库或聊天历史

### 2.2 架构目标

- 记忆必须分层，而不是一个混合大表
- 记忆回忆必须按任务、时间、语义、权威性等维度路由
- 记忆对象必须支持版本与时间演化
- 记忆存储要区分结构化数据、原始证据和语义索引

### 2.3 非目标

- 本阶段不追求全量自动记忆压缩
- 本阶段不追求所有历史数据都自动转成高质量知识
- 本阶段不把所有记忆都接入单一检索通道

---

## 3. 核心纠偏

### 3.1 记忆不等于聊天历史

聊天历史只是 `session memory` 的一个表现。

如果把全部记忆都等同于对话记录，后果是：

- 任务状态无法可靠恢复
- 研究过程不可回放
- 经验难以沉淀
- 方法演化没有承载对象

### 3.2 记忆不等于向量库

向量检索只适合其中一部分“语义回忆”场景。

它不适合作为：

- 任务状态存储
- 程序性方法存储
- 版本历史
- 事件流历史

### 3.3 记忆系统首先服务“可持续运行”

V1 的重点不是做出最聪明的记忆，而是先保证：

- 任务不会因为重启就失忆
- 进化不会不断重复踩坑
- 方法有效性有地方沉淀
- 后续研究和知识建设有可靠底座

---

## 4. 记忆分层 V1

MyAttention `V1` 至少分为五层记忆。

### 4.1 Session Memory

用途：

- 单次对话
- 单次研究会话
- 单次推理过程中的短期上下文

特点：

- 生命周期短
- 可压缩
- 可裁剪
- 允许丢弃部分中间状态

典型内容：

- 最近消息
- 当前会话摘要
- 当前会话临时参数
- 短期引用片段

### 4.2 Task Memory

用途：

- 单个任务或工作流的执行记忆

特点：

- 与 `task_id / context_id / workflow_id` 绑定
- 需要 checkpoint
- 需要支持恢复和重放

典型内容：

- 当前阶段
- 子任务关系
- 中间产物
- 执行轨迹
- 失败原因
- 恢复点

### 4.3 Semantic Memory

用途：

- 长期事实、概念、偏好、稳定知识对象

典型内容：

- 用户偏好
- 项目事实
- 学科结构
- 来源属性
- 已确认知识条目
- 已验证方法结论

### 4.4 Episodic Memory

用途：

- 记录过去发生过什么

典型内容：

- 某次修复过程
- 某次研究过程
- 某次问题定位过程
- 某次失败和恢复案例

价值：

- 这是进化大脑沉淀“经验”的核心载体

### 4.5 Procedural Memory

用途：

- 记录系统如何做事

典型内容：

- 提示词策略
- 修复流程
- 调试套路
- 研究方法
- skill / playbook / policy

价值：

- 这是“经验升级成能力”的核心载体

---

## 5. 记忆对象模型 V1

后续实现不应把所有层混成一个表，但可以共享统一元数据语义。

建议统一元字段：

- `memory_id`
- `memory_type`
- `scope_type`
- `scope_id`
- `title`
- `summary`
- `content`
- `source_type`
- `source_id`
- `created_at`
- `updated_at`
- `valid_from`
- `valid_to`
- `version`
- `parent_version`
- `confidence`
- `authority_level`
- `tags`
- `metadata`

说明：

- `memory_type` 对应五层中的一种
- `scope_type / scope_id` 用于绑定会话、任务、研究、知识对象等
- `valid_from / valid_to` 为后续时间化与版本化预留
- `metadata` 只承载不稳定扩展信息，不替代主字段

---

## 6. 回忆策略 V1

记忆系统不能只有一个“相似度搜索”入口。

V1 至少支持这些回忆模式：

### 6.1 Session Recall

用于：

- 当前聊天
- 当前研究上下文

优先维度：

- recency
- current conversation
- current task

### 6.2 Task-scoped Recall

用于：

- 恢复某个任务
- 查看某个任务做过什么

优先维度：

- `task_id`
- workflow lineage
- checkpoint time

### 6.3 Semantic Recall

用于：

- 找长期事实
- 找概念关联
- 找知识节点

优先维度：

- semantic similarity
- authority
- freshness / validity

### 6.4 Episodic Case Recall

用于：

- 找相似历史案例
- 找以前怎么修过
- 找以前怎么研究过

优先维度：

- problem type
- method
- outcome
- similarity

### 6.5 Procedural Recall

用于：

- 找适用方法
- 找已验证 skill / playbook / policy

优先维度：

- problem type
- thinking framework
- method
- effectiveness
- latest validated version

---

## 7. 物理存储方案 V1

V1 不建议为了“记忆”立即引入大量新基础设施。

### 7.1 PostgreSQL

用于：

- 结构化记忆元数据
- task memory
- semantic facts
- episodic record index
- procedural policies / playbooks index
- checkpoint metadata

### 7.2 Object Storage

用于：

- 原始研究资产
- 长日志归档
- 大型中间产物
- UI 巡检截图
- 证据快照
- 可回放附件

开发期可先用：

- `LocalObjectStore`

长期目标：

- `S3 / OSS / MinIO`

### 7.3 Qdrant

用于：

- semantic memory 的向量检索
- episodic case 的相似案例检索
- 长文档片段语义召回

### 7.4 Redis

用于：

- 短期工作态缓存
- 热记忆窗口
- 临时任务状态缓冲

注意：

- Redis 不是长期记忆事实层

---

## 8. 与三条主线的关系

### 8.1 信息大脑

需要记住：

- 来源评估结果
- 来源升级/降级历史
- 某次发现路径是否有效
- 哪类来源在什么主题下表现好

### 8.2 知识大脑

需要记住：

- 事实与解释的区分
- 学科结构
- 版本化理解
- 某结论的证据链和时间有效性

### 8.3 进化大脑

最依赖：

- episodic memory
- procedural memory

因为它真正需要记住的是：

- 哪类问题之前出现过
- 以前如何定位
- 哪种修复有效
- 哪种修复无效
- 哪类方法后来被淘汰
- 哪类方法后来被沉淀成 skill / playbook

---

## 9. V1 实施建议

V1 不追求一步做完全部层级，而是按价值顺序落地。

### 第一优先级

- `task memory`
- `procedural memory`

原因：

- 直接支撑进化大脑
- 直接支撑复杂任务恢复
- 直接支撑方法沉淀

### 第二优先级

- `episodic memory`

原因：

- 支撑经验复用
- 支撑问题归因和案例回忆

### 第三优先级

- `semantic memory` 的系统化升级

原因：

- 这会与知识大脑结构化建设深度耦合

### 第四优先级

- 高级记忆压缩与跨层回忆优化

---

## 10. 演化约束

本设计必须被视为 `V1`，不能写死成终局结构。

后续必须允许：

- 新增记忆层
- 调整回忆策略
- 增加版本化字段
- 调整对象分类
- 引入时间化 / 版本化专门基础设施

不应写死为：

- 固定五层永不变化
- 固定单一路由
- 固定单一数据库实现

---

## 11. 设计结论

1. 记忆不是聊天历史，也不是向量库。
2. V1 至少要分 `session / task / semantic / episodic / procedural` 五层。
3. 当前最值得优先落地的是 `task memory + procedural memory`。
4. 进化大脑最依赖的不是更多日志，而是 `episodic + procedural`。
5. 物理存储上，V1 以 `PostgreSQL + Object Storage + Qdrant + Redis` 为主，不急于引入更重的新系统。
6. 整个记忆架构必须天然支持未来的版本化、时间化和方法演化。
