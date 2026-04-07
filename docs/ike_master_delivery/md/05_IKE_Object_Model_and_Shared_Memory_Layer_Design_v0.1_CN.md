# IKE 对象模型与共享记忆层设计稿 v0.1

## 1. 对象层

统一对象层应至少包含 Source、Observation、Entity、Relation、Claim、Event、Concept、ThinkingModel、Paradigm、ResearchTask、Experiment、Decision、HarnessCase、GovernanceReview。

## 2. 共享记忆层

建议的记忆分层包括：观察记忆、证据记忆、结构化知识记忆、研究工作记忆、治理记忆、长期采纳记忆。

## 3. 读写边界

信息大脑写入 observation 与 source evaluation；知识大脑写入实体、关系与观点；进化大脑写入任务、实验和决策；治理层写入模型选择与评审记录。

## 4. 生命周期

对象应从 observation 演化到结构化解释，再进入任务、实验与采纳/退休流程，整个生命周期必须可检查。
