# 受控任务外包与多脑协作策略 V1

## 1. 定位

本文件定义 MyAttention 在当前阶段如何使用外部智能体/子智能体协作完成高消耗任务。

它不是“把任务丢出去”的策略，而是：

- 多层大脑协作的第一步现实落地
- 主控大脑保持决策权、验收权、回滚权
- 用受控的任务简报、结构化产物和版本记录来降低 token 消耗

当前实现通道以 `acpx` 为主，但协议和对象模型不绑定单一工具。

## 2. 核心原则

### 2.1 主控不外包

以下职责必须始终由主控大脑承担：

- 项目主线和优先级判断
- 问题建模、思维模型和方法选择
- 风险判断和最终路线决策
- 外包结果验收、拒绝、回滚
- 版本接受与淘汰决策

### 2.2 外包是协作，不是卸责

外包任务必须满足：

- 边界清晰
- 输入充分
- 输出可验证
- 失败可回收
- 回来后可审查

任何“发出去但拿不回结果、拿回结果但无法判断质量”的模式都视为失败模式。

### 2.3 结构化交接是强制要求

每个外包任务都必须有结构化简报，并要求结构化回包。

禁止：

- 口头式模糊委派
- 没有验收标准的开放式请求
- 没有版本信息的结果接收

### 2.4 外包对象优先选高 token、低主控耦合任务

优先外包：

- coding-heavy
- review-heavy
- bounded research
- UI/视觉巡检
- 独立 bug 定位

不优先外包：

- 架构主控
- 主线优先级判断
- 认知框架定稿
- 跨模块高风险改动仲裁

## 3. 为什么现在就要做

当前单线程主控推进存在明显瓶颈：

- coding 任务消耗大量 token
- review/UI/资料整理会挤占主线推理预算
- 高消耗但边界清晰的子任务不外包，会持续拖慢主线

因此，受控外包不是可选优化，而是当前资源约束下的高优先级策略。

## 4. 任务适配判断

一个任务只有同时满足以下条件，才应进入外包候选：

1. 边界清晰
2. 可给出明确输入
3. 有明确产物形式
4. 可通过测试或审查验证
5. 失败不会直接破坏主控链路

### 4.1 适合外包的第一批任务类型

- 前端 UI 巡检与修复建议
- 独立页面样式/层级问题修复
- 局部模块代码实现
- 测试补齐
- 独立 bug 根因定位
- source discovery 某个适配器原型
- 独立 research 比较任务

### 4.2 不适合直接外包的任务类型

- 主线阶段切换
- 系统主架构定稿
- 大脑控制层最终策略
- 版本接受/拒绝决策
- 高风险数据迁移总控
- 进化大脑主控逻辑裁决

## 5. 外包任务简报模板

每个外包任务至少应包含以下字段：

- `task_id`
- `title`
- `task_type`
- `problem_type`
- `thinking_framework`
- `method`
- `scope`
- `inputs`
- `constraints`
- `expected_outputs`
- `validation`
- `stop_conditions`
- `version_refs`

### 5.1 最小示例

```text
task_id: delegated-ui-001
title: Fix feed freshness perception on homepage
task_type: implementation
problem_type: interface_quality
thinking_framework: diagnostics
method: bounded coding task
scope:
  - services/web/components/feed/feed-list.tsx
inputs:
  - current homepage shows stale-feeling feed because local cache loads first
constraints:
  - do not change backend APIs
  - do not remove offline fallback
expected_outputs:
  - patch summary
  - changed files
  - validation result
validation:
  - type-check passes
  - homepage shows last refresh time and clearer freshness state
stop_conditions:
  - if backend contract mismatch is required, stop and report
version_refs:
  - roadmap phase: source intelligence / feed loop stabilization
```

## 6. 结果回收协议

每个外包结果必须结构化返回，至少包含：

- `result_summary`
- `files_changed`
- `artifacts`
- `validation`
- `known_risks`
- `recommendation`

主控收到后只能做这三种决策：

- `accept`
- `accept_with_changes`
- `reject`

任何结果若无法归入这三类，说明外包协议设计失败。

## 7. 版本管理要求

外包任务必须进入版本记录，至少包含：

- `delegation_id`
- `initiator`
- `agent_channel`
- `brief_version`
- `response_version`
- `accepted_status`
- `decision_reason`
- `related_commit`

这意味着：

- Git 继续管理代码/文档变更
- 系统内部版本记录管理“为什么这次外包被接受或拒绝”

## 8. 与多脑协作架构的关系

本策略是 `BRAIN_CONTROL_ARCHITECTURE` 的第一阶段落地：

- 主控脑：发起、约束、验收
- 专家脑/外部 agent：完成边界清晰的执行任务
- 小脑层：后续应负责调度、队列和状态
- 脑干层：保证主控和系统保底运行

因此，外包策略不是独立模块，而是多脑协作的现实实现入口。

## 9. 当前推荐执行顺序

### P0

- 建立受控外包规则和版本记录
- 明确第一批可外包任务类型

### P1

- 用 `acpx` 跑第一批 bounded coding/review 任务
- 评估是否真的降低 token 消耗、提升主线效率

### P2

- 将外包任务纳入任务系统与大脑控制层
- 让受控委派成为正式协作拓扑的一部分

## 10. 第一批建议试点

- 信息流首页 freshness 感知修复
- source discovery 质量对比研究
- source discovery 某一对象类型适配器原型
- evolution/problem center 页面信息层级改造
- 局部测试补齐与 review

## 11. 当前边界

当前版本仍然是 `V1`，不应被视为最终协作体系。

它的目标不是“完美的 agent team”，而是：

- 先把主控与执行分层
- 先把高 token 任务从主线程安全拆出去
- 先把结果回收、验收和版本记录做起来

后续会与以下文档继续收敛：

- `docs/TASK_AND_WORKFLOW_MODEL.md`
- `docs/BRAIN_CONTROL_ARCHITECTURE.md`
- `docs/VERSIONED_INTELLIGENCE_ARCHITECTURE.md`

## 12. Current acpx/OpenClaw Working Mode

The current transport is usable, but with a known shell-output limitation.

- `acpx -> openclaw` session creation works.
- Dedicated OpenClaw coding agent routing works.
- Prompt execution completes and is persisted in `acpx` session history.
- Limitation: foreground shell output from `acpx openclaw prompt/exec` is not reliably rendered on this machine.

Current workaround:

- Submit via `acpx`
- Recover results via:
  - `acpx --format json openclaw sessions history <name> --limit N`
  - `acpx --format json openclaw sessions show <name>`
- Helper script:
  - `/D:/code/MyAttention/scripts/acpx/openclaw_delegate.py`

This keeps delegation inside the `acpx` control plane while preserving:

- session ownership
- agent routing
- history/audit recovery
- main-controller acceptance control

## 13. Context Packet Rule

Delegated tasks must not be sent as open-ended "go read the repo" prompts.

The current stable rule is:

- main controller prepares a bounded context packet
- packet includes only the files/excerpts needed for the task
- delegated agent is instructed to use only that packet
- results are recovered through `acpx` session history or explicit output

This reduces three failure modes:

- repo-wide context drift
- agent falling back to generic project-summary behavior
- hidden reads that are hard to audit

Current helper scripts:

- `/D:/code/MyAttention/scripts/acpx/openclaw_delegate.py`
- `/D:/code/MyAttention/scripts/acpx/build_context_packet.py`
- `/D:/code/MyAttention/scripts/acpx/run_file_delegation.py`

## 14. File-Based Delegation Protocol

The preferred execution mode is now file-based delegation.

Flow:

1. Main controller prepares:
   - brief file
   - context packet file
   - expected output schema
2. Delegated agent receives only:
   - brief path
   - context path
   - output path
3. Delegated agent writes a UTF-8 JSON result file.
4. Main controller validates:
   - output exists
   - output parses
   - schema is acceptable
5. Only then is the result considered for acceptance.

Why this is preferred:

- avoids shell/stdout instability
- avoids Windows console encoding traps
- makes outputs durable and auditable
- aligns delegation with task/artifact/version objects

Rule:

- free-form prompt delegation is now fallback only
- file-based delegation is the default mode for coding, review, and bounded analysis tasks

- session ownership
- bounded task routing
- structured result recovery
- controller-side acceptance and rollback
