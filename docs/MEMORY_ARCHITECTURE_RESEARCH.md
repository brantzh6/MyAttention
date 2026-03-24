# 记忆架构研究

> 目标：为 MyAttention 的长期进化、任务连续性、知识沉淀和方法复用建立前置记忆研究，避免把“记忆”误简化为聊天上下文或向量库。

---

## 1. 为什么记忆是短期优先项

如果没有清晰的记忆架构，后面这些能力都会失真：

- 进化大脑无法积累经验
- 有效方法无法沉淀
- 失败路径会反复踩坑
- 复杂任务无法跨轮推进
- 知识会“存了很多”，但很难回忆出真正有用的部分

所以记忆不是后期增强，而是基础设施。

---

## 2. 主要参考

### 2.1 LangGraph Persistence

参考：

- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

关键点：

- `thread` 表示执行上下文
- `checkpoint` 表示执行过程中的可恢复状态
- 可回放、可 time-travel、可恢复

启发：

- MyAttention 后续任务和 agent team 协作必须有 checkpoint 语义
- 不能把长任务状态只放内存

---

### 2.2 LangMem

参考：

- [LangMem conceptual guide](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/)

关键点：

- 长期记忆分为：
  - `semantic`
  - `episodic`
  - `procedural`

启发：

- 这三分法对 MyAttention 很有价值
- 但还不够，需要再加上 task/session 维度

---

## 3. MyAttention 需要的记忆分层

后续建议至少分 5 层：

### 3.1 Session Memory

作用：

- 单次对话或单次研究会话的上下文

特点：

- 生命周期短
- 可压缩
- 可丢弃

适合保存：

- 最近消息
- 当前任务背景
- 当前推理中间状态

---

### 3.2 Task Memory

作用：

- 单个任务/工作流的执行记忆

特点：

- 与 `task_id / context_id` 绑定
- 需要 checkpoint
- 需要恢复能力

适合保存：

- 当前阶段
- 子任务关系
- 中间结果
- 执行轨迹
- 失败原因

---

### 3.3 Semantic Memory

作用：

- 长期事实、概念、偏好、知识对象

适合保存：

- 用户偏好
- 项目事实
- 学科知识
- 来源属性
- 已确认的方法知识

---

### 3.4 Episodic Memory

作用：

- 过去发生过什么

适合保存：

- 成功修复案例
- 失败案例
- 某次研究过程
- 某次调试路径

价值：

- 对进化大脑特别关键
- 因为“经验”主要存在于 episodic memory

---

### 3.5 Procedural Memory

作用：

- 系统如何做事

适合保存：

- 提示词策略
- 恢复策略
- 调试流程
- 研究流程
- skill / playbook / policy

价值：

- 这是进化真正沉淀成能力的地方

---

## 4. 记忆对象不应全部进向量库

当前容易犯的错误是：

- 记忆 = embedding + similarity search

这不够。

更合理的是：

- Session / Task state
  - PostgreSQL
  - checkpoint store
- Semantic facts
  - PostgreSQL + Qdrant
- Episodic cases
  - PostgreSQL + object storage + retrieval index
- Procedural memory
  - versioned docs / policy store / skill library

向量检索只是记忆回忆的一部分，不是全部。

---

## 5. 记忆回忆效率问题

“不忘记”和“能快速回忆”是两个不同问题。

后续必须解决：

1. 什么应该长期保留
2. 什么应该压缩
3. 什么应该归档
4. 什么应该只在特定任务下回忆

因此记忆系统后续至少应支持：

- recency-based recall
- task-scoped recall
- semantic recall
- authority-aware recall
- episodic case retrieval
- procedural rule retrieval

---

## 6. 对进化大脑的意义

进化大脑如果没有记忆，只会不断重复：

- 发现同类问题
- 做同类分析
- 给出同类建议

但不会真正进化。

它至少需要记住：

- 哪类问题之前出现过
- 以前怎么定位
- 哪种修复有效
- 哪种修复无效
- 哪种方法后来被淘汰
- 哪种方法后来沉淀成 skill / playbook

所以进化大脑真正依赖的不是“更多日志”，而是：

- episodic memory
- procedural memory

---

## 7. 短期建设建议

短期不建议一口气做完整多层记忆系统。

更现实的顺序是：

1. 明确记忆分层
2. 先补 task memory / procedural memory 的正式存储设计
3. 再补 episodic 经验沉淀
4. 最后再做更复杂的跨层回忆策略

因为对当前主线最有价值的是：

- 让进化大脑记住“怎么做过、是否有效”
- 让研究过程记住“为什么这样判断”

---

## 8. 研究结论

1. 记忆不是聊天上下文，也不只是向量库。
2. 至少要分 `session / task / semantic / episodic / procedural` 五层。
3. 进化能力最依赖的是 `episodic + procedural`。
4. 记忆回忆必须按任务、时间、语义、权威性分层，而不能只靠相似度检索。
5. 短期应优先建设 task memory 和 procedural memory 的正式基础。

---

## 9. 下一步正式设计文档

- `MEMORY_ARCHITECTURE.md`

重点应包括：

- memory layers
- storage mapping
- recall strategies
- compression / archive rules
- evolution memory capture rules
