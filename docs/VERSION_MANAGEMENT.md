# 版本管理规范

## 1. 目的

MyAttention 的版本管理不能只依赖 Git commit。项目同时在演化：

- 代码与部署实现
- 架构与设计方案
- 认知框架与方法体系
- 任务与工作流
- 来源智能与知识对象
- 记忆与进化策略

本规范用于回答 4 个问题：

1. 当前版本是什么
2. 它从哪里演化而来
3. 为什么发生变化
4. 变化后效果如何

---

## 2. 版本层次

### 2.1 代码与文件版本

由 Git 管理：

- 源代码
- 文档
- 迁移脚本
- 测试
- 配置模板

要求：

- 所有实现改动必须可在 Git diff 中追踪
- 重要阶段能力变化必须进入 `CHANGELOG.md`
- 设计/实现偏离必须回写文档

### 2.2 项目变更版本

由项目文档管理：

- `CHANGELOG.md`
- `PROGRESS.md`

作用：

- 记录阶段性能力变化
- 记录兼容性调整
- 记录主线状态
- 记录已验证结果

### 2.3 系统内部对象版本

由数据库/对象存储内的版本对象管理：

- source plan version
- task/artifact version
- memory version
- knowledge version
- method/policy version
- cognition version

这些版本不能只存在 Git 中，因为它们描述的是系统运行期对象的演化，而不是文件编辑历史。

---

## 3. 通用版本字段

所有内部版本化对象应尽量具备以下语义字段：

- `version_number`
- `parent_version`
- `trigger_type`
- `decision_status`
- `change_reason`
- `change_summary`
- `evaluation`
- `created_by`
- `accepted_at`
- `created_at`

说明：

- `trigger_type`：为什么触发变化，例如 `initial_create`、`manual_refresh`、`manual_subscribe`
- `decision_status`：变化是否被接受，例如 `accepted`、`needs_review`
- `change_summary`：前后差异摘要
- `evaluation`：质量判断、风险、理由

---

## 4. 当前项目基线

### 4.1 已经具备

- Git 作为代码/文档版本控制
- `CHANGELOG.md` 作为项目级变更日志
- `PROGRESS.md` 作为主线进度状态
- `source_plan_versions` 作为第一类运行期版本对象

### 4.2 正在推进

- task / artifact / memory 的版本化
- 认知框架与方法策略版本化
- 进化大脑对版本变化效果的评估

### 4.3 还未完成

- 知识对象版本化
- 统一版本比较视图
- 回滚策略标准化

---

## 5. 变更接受原则

系统内部对象变化不应默认覆盖当前状态。

推荐流程：

1. 生成候选变化
2. 记录候选版本
3. 比较与前一版本的差异
4. 输出评估结果
5. 决定：
   - `accepted`
   - `needs_review`
   - `rejected`
6. 保留 lineage

---

## 6. 与主线关系

版本管理不是附属治理，而是进化能力的一部分。

没有版本管理，系统就无法可靠回答：

- 为什么这个 source 被提升或降级
- 为什么某种方法被采用或淘汰
- 为什么某次认知策略改变了
- 某次变化是否真的让系统变好

因此：

- Git 解决“文件如何变化”
- 内部版本对象解决“智能系统为何变化”

