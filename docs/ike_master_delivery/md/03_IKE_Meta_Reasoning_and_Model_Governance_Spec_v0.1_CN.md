# IKE 元推理与模型治理规范 v0.1

## 1. 范围

本规范定义思考模型如何注册、选择、评估、降级、冻结、退休，以及如何吸收新模型进入系统。

## 2. 核心对象

治理核心对象包括 ThinkingModel、DomainParadigm、ModelSelectionRecord、ModelEvaluationRecord、GovernanceReview、ModelEvolutionEvent。

## 3. 选择策略

模型选择应综合任务类型、领域、证据形态、风险等级、置信度状态和历史表现。选择过程必须可解释并留下记录。

## 4. 更新策略

模型更新分为四层：参数级更新、组合级更新、模型增删，以及元规则级更新。

## 5. 治理节奏

建议建立周度运行复盘、月度模型评审、季度架构评审。治理不应依赖临时拍脑袋。
