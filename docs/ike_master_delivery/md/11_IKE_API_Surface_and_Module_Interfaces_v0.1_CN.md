# IKE API 接口面与模块接口 v0.1

## 1. 外部 API 家族

建议的外部 API 家族包括：observations、knowledge、research、governance、harness、administration。

## 2. 内部接口

模块之间应通过应用层契约和事件通信，而不是直接共享数据库内部实现。

## 3. 响应标准

所有重要响应都应附带 provenance、confidence 和 traceability 信息。

## 4. 第一阶段接口集

第一阶段应优先实现 workflow 触发接口，以及 bootstrap 所需的对象 CRUD / 查询接口。
