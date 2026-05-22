# 实施准备检查点 V1

> 本文档用于判断：MyAttention 当前是否已经具备进入下一轮编码实施的条件，以及哪些部分可以开始做、哪些部分仍不应贸然编码。

---

## 1. 结论先行

当前已经具备进入**下一轮主线编码**的条件。

但不是“所有大方向都已定稿”，而是：

- 上位框架已足够支撑短期实施
- 可以进入受控实现
- 仍有若干高层主题保留继续研究，不应阻塞当前主线

更准确地说：

**现在已经适合开始“Phase 4/6 的第一批实现”，不适合直接做完整终局系统。**

---

## 2. 已经足够稳定、可进入编码的部分

### 2.1 问题建模与方法选择框架

文档：

- `docs/PROBLEM_FRAMING_AND_METHOD_SELECTION.md`

判断：

- 已足够作为 V1 路由依据
- 后续会迭代，但不妨碍短期落地

### 2.2 来源智能架构

文档：

- `docs/SOURCE_INTELLIGENCE_ARCHITECTURE.md`

判断：

- 已足够支撑第一批 source intelligence 数据模型和控制层实现

适合先做：

- source object / source endpoint 模型
- source classification 与 monitoring mode
- source plan 基础存储

### 2.3 记忆架构

文档：

- `docs/MEMORY_ARCHITECTURE.md`

判断：

- 已足够支撑 `task memory + procedural memory` 第一批实现

适合先做：

- task memory 数据模型
- procedural memory / playbook / policy 存储基础

### 2.4 任务与工作流模型

文档：

- `docs/TASK_AND_WORKFLOW_MODEL.md`

判断：

- 已足够支撑第一批 `Context / Task / Artifact / Event / Relation` 落库

适合先做：

- 任务核心表
- 状态机事件表
- artifact 元数据表

### 2.5 大脑控制架构

文档：

- `docs/BRAIN_CONTROL_ARCHITECTURE.md`

判断：

- 已足够支撑 V1 的脑配置层，不需要等到所有 team 细节完备

适合先做：

- `brain_profile`
- `brain_route`
- `brain_policy`
- `brain_fallback`

---

## 3. 还不应贸然编码的部分

### 3.1 全量深度研究工作流

原因：

- 仍缺 `DEEP_RESEARCH_ARCHITECTURE.md`
- 仍缺与知识结构层的正式对接

### 3.2 全量知识大脑结构化层

原因：

- 仍缺 `KNOWLEDGE_ARCHITECTURE.md`
- 学科、时间、事实、解释等维度尚未正式设计收口

### 3.3 终局级版本化/时间化实现

原因：

- 已有上位设计和研究
- 但还不适合立即做全量实现
- 应先在最关键对象上局部应用版本语义

### 3.4 完整多脑自治协作 runtime

原因：

- V1 架构已足够
- 但如果现在直接做复杂 agent runtime，会过早膨胀范围

---

## 4. 当前最合理的编码切入点

### 第一优先级

#### A. 任务基础设施 V1

建议实现：

- `contexts`
- `tasks`
- `task_events`
- `artifacts`
- `relations`

原因：

- 它会直接支撑：
  - 进化大脑
  - 多脑协作
  - 后续 source intelligence 流程

#### B. 大脑配置层 V1

建议实现：

- `brain_profiles`
- `brain_routes`
- `brain_policies`
- `brain_fallbacks`

原因：

- 这是“智能对话配置”升级为“脑控制平面”的第一刀

### 第二优先级

#### C. Source Intelligence 基础对象层

建议实现：

- `source_objects`
- `source_endpoints`
- `source_plans`
- `source_reviews`

原因：

- 这是信息流从固定 RSS 走向目标驱动建源的第一刀

### 第三优先级

#### D. Task / Procedural Memory

建议实现：

- `task_memory`
- `procedural_memory`
- `playbook_versions`

原因：

- 直接支撑进化大脑从“发现问题”走向“积累经验”

---

## 5. 编码顺序建议

建议顺序：

1. 任务基础设施
2. 大脑配置层
3. source intelligence 基础对象层
4. task/procedural memory

原因：

- 先有任务和脑控制层，后续 source intelligence 和 evolution 才不会继续漂浮在散逻辑上

---

## 6. 当前需要坚持的边界

进入编码后，仍然要坚持：

- 不把 V1 文档当终局真理
- 不在实现阶段随意扩大范围
- 不把研究线和实现线混成一锅
- 每实现一层都要回写版本、进度、变更和测试

---

## 7. 检查点结论

1. 当前已经不需要继续扩散上位设计才能启动下一轮编码。
2. 最适合开始编码的是：任务基础设施 + 大脑配置层。
3. source intelligence 和记忆应紧随其后落地。
4. 深度研究全流程、知识终局结构、复杂多脑 runtime 仍应继续先设计后实施。
