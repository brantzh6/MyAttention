# IKE Codex 执行 Backlog 与前 100 项任务 v0.1

## 1. 目的

本文把前面的架构设计压缩成一份适合 Codex 驱动实施的执行 backlog。

## 2. 任务分桶

前 100 项任务分为：仓库骨架、共享 schema、持久化、observation 摄取、知识装配、模型治理骨架、工作流、任务/实验/决策引擎、harness、API 接口与运维。

## 3. 排序规则

优先打通最窄的端到端切片：observation → entity/claim extraction → research task → experiment stub → decision record → harness record。

## 4. 交付节奏

Codex 应按小批次推进，以契约优先提交；每次接口变化都应同步更新 harness。
