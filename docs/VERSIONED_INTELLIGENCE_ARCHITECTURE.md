# 版本化智能架构设计 V1

> 本文档定义 MyAttention 的 `Versioned Intelligence Architecture` `V1`。
>
> 目标不是只给代码打版本，而是让系统能够追踪：
>
> - 认知是如何变化的
> - 方法是如何变化的
> - 任务计划是如何变化的
> - 知识和记忆是如何变化的
> - 这些变化带来了什么效果

---

## 1. 文档定位

本设计解决的问题是：

- MyAttention 哪些对象必须版本化
- 各类版本对象之间如何关联
- 版本变化需要记录哪些字段
- 版本如何与任务、记忆、知识、方法和运行结果联动

本设计不直接解决：

- 具体数据库表结构实现
- TSDB 选型
- 具体 Git 流程细节

这些会在后续实现和数据层设计中展开。

---

## 2. 核心目标

- 让版本化对象超越代码和文档，进入认知、方法、知识、任务和记忆层
- 让“为什么变”和“变得是否更好”都可追踪
- 支撑回滚、比较、评估和演化学习

---

## 3. 需要版本化的对象 V1

### 3.1 系统版本 `system_version`

范围：

- 代码
- 接口
- 部署基线
- 数据模型

### 3.2 设计版本 `design_version`

范围：

- 架构设计
- 模块设计
- 流程设计

### 3.3 认知版本 `cognition_version`

范围：

- 问题类型 taxonomy
- 思维模型
- 方法选择框架
- 路由规则

### 3.4 方法版本 `method_version`

范围：

- 深度研究方法
- source intelligence 策略
- 投票策略
- 质量评估策略
- skill / playbook

### 3.5 任务版本 `task_version`

范围：

- 任务计划
- 任务 refinement
- 工作流拆解

### 3.6 知识版本 `knowledge_version`

范围：

- 知识条目
- 学科结构
- 权威理解
- 前沿研究解读

### 3.7 记忆版本 `memory_version`

范围：

- procedural memory
- episodic memory 的归档版本
- task memory schema

---

## 4. 通用版本字段 V1

所有版本化对象后续至少共享这些字段：

- `version_id`
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

### 4.1 字段语义

- `version_id`
  - 本次版本记录唯一标识
- `entity_id`
  - 表示“这是同一个对象”的稳定主键
- `version`
  - 对象版本号
- `parent_version`
  - 版本 lineage
- `change_reason`
  - 为什么变
- `evaluation_result`
  - 变更后效果如何

---

## 5. 版本变化的最小闭环

任何重要版本变化后，都至少要回答：

1. 变了什么
2. 为什么变
3. 由谁发起
4. 何时生效
5. 预期改善什么
6. 实际结果如何
7. 如不理想回滚到哪里

也就是：

```text
previous version
  -> proposed change
  -> approved version
  -> effective period
  -> evaluation result
  -> keep / revise / rollback
```

---

## 6. 版本与任务系统的关系

版本变化不应悬空存在。

后续每次重要版本变化应尽量关联：

- `context_id`
- `task_id`
- `artifact_id`

例如：

- 某次认知框架调整
  - 应关联对应研究任务和评审 artifact
- 某次方法调整
  - 应关联测试结果和运行指标
- 某次 source policy 升级
  - 应关联实际来源表现数据

---

## 7. 版本与进化大脑的关系

进化大脑后续不只是发现问题，还应负责：

- 识别哪些策略应该升级版本
- 比较版本前后效果
- 决定是否保留、修订、淘汰

所以进化大脑要消费：

- policy versions
- method versions
- quality baseline versions
- evaluation history

---

## 8. 版本与时间维度的关系

版本对象天然包含时间维度，但不等于普通时间序列。

每个版本对象后续至少应支持：

- `created_at`
- `effective_from`
- `effective_to`
- `superseded_at`

这样才能表达：

- 何时创建
- 何时生效
- 何时被替代

---

## 9. V1 实施建议

短期不要试图把所有历史对象一次性全版本化。

### 第一优先级

- `method_version`
- `cognition_version`
- `evolution_policy_version`

原因：

- 这是当前最容易漂、也最需要可回溯的层

### 第二优先级

- `task_version`
- `knowledge_version`

### 第三优先级

- `memory_version`

---

## 10. 与 Git 的关系

Git 很重要，但不够。

Git 主要回答：

- 代码怎么变了

它不能天然回答：

- 当前认知框架是第几版
- 当前方法策略是第几版
- 哪次方法变化带来了改善
- 哪条知识理解现在处于哪个版本

所以：

- Git 是底层实现历史
- Versioned Intelligence 是系统语义历史

两者应关联，但不应互相替代。

---

## 11. 设计结论

1. MyAttention 的版本控制不能只靠代码版本。
2. 至少要版本化：系统、设计、认知、方法、任务、知识、记忆。
3. 当前最优先版本化的对象是认知、方法和进化策略。
4. 版本对象必须记录 lineage、原因和评估结果。
5. 版本化智能架构是后续真正“可进化”的基础，而不是文档附属物。
