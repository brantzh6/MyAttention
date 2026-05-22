# 方法有效性与 Skill 沉淀研究

> 目标：回答 MyAttention 在长期研发和进化过程中，如何识别哪些方法有效、哪些方法无效，如何记录，如何复制，以及如何把稳定有效的方法沉淀为可执行 skill。

---

## 1. 为什么这件事是核心问题

对 MyAttention 来说，后续会不断出现：

- 新的研究方法
- 新的 agent team 协作方式
- 新的测试方式
- 新的信息整理方式
- 新的知识抽取方式
- 新的修复与回归方法

如果没有方法评估机制，系统会出现两个问题：

1. 反复重复低效甚至无效的方法
2. 有效方法无法复制，只能靠个人经验

所以，项目后续不仅要管理代码和任务，还要管理“方法本身”。

---

## 2. 权威方法论参考

### 2.1 Evidence-Based Software Engineering

参考：

- [Evidence-Based Software Engineering and Systematic Reviews](https://www.routledge.com/Evidence-Based-Software-Engineering-and-Systematic-Reviews/Kitchenham-Budgen-Brereton/p/book/9780367575335)
- [Guidelines for performing Systematic Literature Reviews in Software Engineering](https://madeyski.e-informatyka.pl/download/Kitchenham07.pdf)

关键结论：

- 软件工程中的方法选择，不应只靠经验和直觉
- 应该基于：
  - 明确问题
  - 收集证据
  - 评估证据质量
  - 形成可复核结论
- Systematic review / evidence synthesis 是软件工程里被广泛接受的方法学基础

对 MyAttention 的启发：

- 后续对“研究方法”“调试方法”“UI 巡检方法”“多 agent 协作方法”的判断，不能只靠一次感觉好不好用
- 需要：
  - 明确场景
  - 明确成功指标
  - 记录对照结果
  - 形成复用结论

---

### 2.2 NIST AI RMF

参考：

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST AI RMF Core - Measure](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/)

关键结论：

- AI 系统的方法和控制措施，必须纳入：
  - test
  - evaluation
  - verification
  - validation
- 评估过程应该：
  - documented
  - repeatable
  - scalable
- 仅凭“看起来能工作”不足以形成可信方法

对 MyAttention 的启发：

- Skill、agent team 协作模式、自动恢复策略、知识抽取流程，都应该进入 TEVV 视角
- 也就是说，方法必须：
  - 可测试
  - 可验证
  - 可复现
  - 可回退

---

### 2.3 OpenAI Evals best practices

参考：

- [OpenAI Evaluation Best Practices](https://platform.openai.com/docs/guides/evaluation-best-practices)

关键结论：

- 对 AI 能力的判断，不能只靠少量主观体验
- 应该建立：
  - task-specific evals
  - representative samples
  - clear pass/fail criteria
  - regression tracking

对 MyAttention 的启发：

- “某个 skill 好不好用”“某个研究流程是否有效”也应该像 eval 一样管理
- 不是简单记一句“感觉不错”
- 而是要看它是否真的提高：
  - 问题发现率
  - 修复成功率
  - 研究质量
  - 交付效率

---

## 3. 方法有效性的最小判断模型

后续对任何方法、流程、skill、agent 协作模式，都建议按 5 个问题判断：

1. 它适用于什么场景？
2. 它的成功标准是什么？
3. 它比当前基线好在哪里？
4. 它的成本和噪音是什么？
5. 它能不能被别人重复使用？

如果这 5 个问题答不清，方法就还不适合沉淀成正式 skill。

---

## 4. MyAttention 推荐的“方法评估记录”结构

后续每种方法都应至少记录：

- `method_id`
- `name`
- `purpose`
- `scope`
- `inputs`
- `steps`
- `success_metrics`
- `failure_signals`
- `costs`
- `sample_runs`
- `result_summary`
- `reuse_recommendation`
- `status`
  - `trial`
  - `validated`
  - `deprecated`
  - `rejected`

---

## 5. 什么样的方法适合沉淀为 skill

不是所有好想法都应该变成 skill。

更适合沉淀为 skill 的方法，有这些特征：

- 场景清晰
- 输入输出清晰
- 步骤相对稳定
- 成功标准可写清
- 重复使用频率高
- 对质量或效率有明显提升

例如未来可能适合沉淀成 skill 的东西：

- “问题归因研究流程”
- “知识抽取与事实/主张分离流程”
- “跨学科洞察研究流程”
- “UI 巡检与问题归并流程”
- “设计前评审流程”

而不适合直接沉淀为 skill 的，通常是：

- 还在快速探索的想法
- 强依赖个人临场判断的方式
- 输入变化太大、流程不稳定的方法

---

## 6. 当前项目里 skill 的真实状态

### 6.1 gstack skills

当前已安装并记录试用规则的有：

- `plan-eng-review`
- `plan-design-review`
- `design-consultation`
- `review`
- `qa`
- `document-release`

从现有记录看：

- 已完成安装和试用规则制定
- **但尚未形成足够多的真实任务试跑证据**

也就是说，当前状态更准确地说是：

- `installed`
- `governed`
- `not yet sufficiently validated`

这意味着：

- 现在不能说“这些 skill 已经证明有效”
- 只能说“它们已进入受控试用”

### 6.2 acpx / A2A / agent-to-agent

当前环境里已经有：

- `acpx` skill

但当前项目里：

- 还没有把它正式接入主工作流
- 也没有形成可验证的 agent-to-agent 使用模式

所以它目前也不算“已验证有效的方法”。

---

## 7. 当前最需要补的不是更多 skill，而是方法治理

现阶段最缺的是：

1. 方法记录模板
2. 试用运行样本
3. 成功/失败判定标准
4. 可回归比较的基线
5. skill 沉淀门槛

如果没有这几样，skill 很容易变成：

- 装了一堆
- 偶尔用一下
- 但无法说明有没有价值

---

## 8. 推荐的项目级方法治理机制

建议后续把方法管理分成 4 层：

### A. `Method Registry`

记录：

- 有哪些方法在试用
- 用于什么场景
- 当前状态

### B. `Evaluation Log`

记录：

- 每次试跑
- 结果
- 发现的问题
- 是否有效

### C. `Validated Playbook`

只收已经验证有效的方法。

### D. `Skill Library`

只有真正稳定、可复制的方法，才升级成 skill。

---

## 9. 当前结论

1. 有效方法必须基于证据，而不是感觉。
2. 任何方法都要有适用范围、成功标准和失败信号。
3. gstack skill 当前仍处于“治理已建立、证据不足”的阶段。
4. acpx / agent-to-agent 目前也还没进入正式验证阶段。
5. 后续真正重要的是建立“方法注册 -> 试跑 -> 评估 -> 沉淀 -> skill 化”的闭环。

---

## 10. 下一步建议

在正式设计 `Brain Control Plane` 之前，建议再补两类文档：

1. `METHOD_REGISTRY.md`
   - 记录项目里有哪些方法正在试用

2. `VALIDATED_PLAYBOOK.md`
   - 只记录已经证明有效、可复制的方法

这样后面：

- 研究方法
- 调试方法
- agent team 协作方法
- 知识抽取方法
- 进化与恢复方法

都能逐步沉淀，而不是继续散落在对话和个人经验里。
