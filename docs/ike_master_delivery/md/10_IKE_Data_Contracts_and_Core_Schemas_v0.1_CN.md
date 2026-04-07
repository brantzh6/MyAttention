# IKE 数据契约与核心 Schema v0.1

## 1. 目的

本文定义 IKE 第一版可直接实现的数据契约与核心 Schema。

## 2. 包络层

所有持久化对象都应包含 id、kind、version、status、timestamps、provenance、confidence 和 references。

## 3. 一等对象

第一阶段的一等对象包括：Source、Observation、Entity、Relation、Claim、ThinkingModel、Paradigm、ResearchTask、Experiment、Decision、HarnessCase、EvaluationRecord。

## 4. 反模式

要避免模块间 schema 漂移、隐式枚举，以及缺失 provenance 和 version 字段的 payload。
