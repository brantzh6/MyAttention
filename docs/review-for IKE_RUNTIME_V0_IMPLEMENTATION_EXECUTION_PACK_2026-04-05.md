# claude


# IKE Runtime v0 Implementation Execution Pack Review

## 1. 整体判断 (Overall Verdict)

**评分：A — 这是一个可以开始执行的 implementation plan。**

从上一次 review（04-03 架构设计）到这次（04-05 执行包），**项目做了正确的事**：

| 04-03 我提出的问题 | 04-05 的响应 |
|-------------------|-------------|
| 状态机语义需要锁定 | ✅ R0-B 专门处理 compressed state machine semantics |
| TaskEvent 作为一等对象 | ✅ R0-C 专门处理 event log + lease semantics |
| WorkContext 持久 vs 派生需要决定 | ✅ R0-D 明确定义为 "snapshot carrier, not second truth" |
| MemoryPacket 需要状态机和权限 | ✅ R0-E 专门处理 metadata + acceptance |
| Outbox / Redis 恢复细节 | ✅ R0-F 专门处理 redis rebuild |
| 需要 Implementation-Ready Spec | ✅ 整个文档就是这个 |

**关键判断**：04-03 的设计 milestone 和 04-05 的执行 milestone 之间的转换是干净的——没有丢失问题，没有假装已解决。

---

## 2. Packet 顺序评估

```
R0-A → R0-B → R0-C → R0-D → R0-E → R0-F
```

### 依赖关系验证

```
R0-A (Schema Foundation)
  ↓ 必须先有表结构
R0-B (State Machine Semantics)
  ↓ 状态机定义后才能记录状态事件
R0-C (Event Log + Lease)
  ↓ 事件和租约就位后，WorkContext 才能可靠快照
R0-D (WorkContext Carrier)
  ↓ 工作上下文定义后，Memory 才有锚点
R0-E (MemoryPacket)
  ↓ 以上所有 Postgres 对象就位后，才做 Redis 加速
R0-F (Redis Acceleration + Rebuild)
```

**判断：顺序正确，依赖链无环，无跳跃。** ✅

### 一个细微优化建议

R0-C（Event Log + Lease）和 R0-D（WorkContext）之间的依赖其实不是硬依赖——WorkContext 快照不一定需要 event log 先存在。但 **保持当前顺序更安全**，因为：

1. Event log 先就位意味着 R0-D 的实现可以从第一天就被审计
2. 如果 R0-D 先于 R0-C，WorkContext 的变更没有事件记录

**结论：不修改顺序。**

---

## 3. 逐 Packet 风险审查

### R0-A: Core Runtime Schema Foundation

| 维度 | 评估 |
|------|------|
| 范围清晰度 | ✅ 最窄的 packet，只建表 |
| Drift 风险 | 低 — schema 是确定性的 |
| Stop condition | 需要明确：schema migration 成功 + 可回滚 |

**⚠️ 唯一关注点**：schema 设计是否包含了所有 v0 对象？

需要验证 R0-A 的 schema 至少覆盖：
```
✅ ike_projects
✅ ike_tasks
✅ ike_decisions
✅ ike_memory_packets
✅ ike_work_contexts
✅ ike_task_events      ← 04-03 review 新增的一等对象
✅ ike_checkpoints      ← 04-03 review 新增的一等对象
✅ ike_outbox           ← 事务性 side-effect
```

如果 R0-A 的 schema 不包含 `ike_task_events`，那 R0-C 会被迫做 schema 变更，打破 packet 边界。

**建议**：确认 R0-A 的 schema 包含所有 6 个 packet 需要的表结构（哪怕某些表在 R0-A 阶段还是空的）。

---

### R0-B: Compressed Task State Machine Semantics

| 维度 | 评估 |
|------|------|
| 范围清晰度 | ✅ 聚焦状态机逻辑 |
| Drift 风险 | **中** — 状态机容易在实现时被"合理扩展" |
| Stop condition | 需要：状态转换矩阵 100% 覆盖 + enforcement 代码通过所有 transition 测试 |

**🔴 这是整个 first-wave 中语义风险最高的 packet。** 文档也正确识别了这一点。

关键检查项：

| 检查点 | 必须在 R0-B 完成时验证 |
|--------|----------------------|
| `waiting` vs `blocked` 有显式的 `waiting_for` / `blocked_by` 字段 | |
| `review_pending` → rejection 有明确的目标状态列表 | |
| 每个 state × role 组合有 allowed/forbidden 定义 | |
| 状态转换函数拒绝非法转换并抛出明确错误 | |
| 不存在 "catch-all" 转换（如 `any → cancelled`） | |

**建议**：R0-B 的 acceptance criteria 必须包含一个**完整的转换矩阵测试**，而不仅仅是 "happy path" 测试。

---

### R0-C: Task Event Log and Lease Semantics

| 维度 | 评估 |
|------|------|
| 范围清晰度 | ✅ Event log + lease 是两个紧密相关的概念 |
| Drift 风险 | 低 — event log 是 append-only，lease 有明确的超时语义 |
| Stop condition | 需要：event 记录可靠 + lease 超时自动触发状态转换 |

**⚠️ 需要关注的点**：

1. **Lease 并发竞争**：两个 delegate 同时 claim 同一个 task 时，必须用 PostgreSQL 的 `SELECT ... FOR UPDATE SKIP LOCKED` 或类似机制
2. **Event 不可变性**：TaskEvent 一旦写入，必须确保没有 UPDATE/DELETE 路径
3. **Lease heartbeat**：是否需要 heartbeat？如果 delegate 在执行中挂掉但 lease 未过期，系统如何感知？

**建议**：R0-C 需要明确 lease 的三个参数：
```
lease_duration: 默认多长？
lease_renewal: 是否支持续约？
lease_timeout_action: 超时后 task 去哪个状态？(active → failed? active → ready?)
```

---

### R0-D: WorkContext Snapshot Carrier

| 维度 | 评估 |
|------|------|
| 范围清晰度 | ✅ "carrier, not second truth" 定义明确 |
| Drift 风险 | **中高** — WorkContext 最容易膨胀成"什么都存" |
| Stop condition | 需要：WorkContext 可以从 task + artifact + memory 重建 |

**🔴 这是第二高风险的 packet。**

WorkContext 的核心陷阱：

```
正确用法：
  WorkContext = 快速恢复工作现场的快照
  丢了 → 可以从 Postgres truth 重建（代价是慢一点）

错误用法：
  WorkContext = 存储只在这里才有的状态
  丢了 → 信息永久丢失
```

**建议**：R0-D 必须有一个 **reconstruction test**：
```
测试步骤：
1. 创建 WorkContext 快照
2. 删除 WorkContext
3. 从 PostgreSQL 中的 task + events + decisions + memory 重建
4. 对比原始快照和重建结果
5. 差异必须为零（或差异仅限于可接受的缓存数据）
```

如果这个测试通不过，说明 WorkContext 已经变成了 second truth。

---

### R0-E: MemoryPacket Metadata and Acceptance

| 维度 | 评估 |
|------|------|
| 范围清晰度 | ✅ metadata + acceptance gate |
| Drift 风险 | **高** — memory 系统最容易被"合理地"加入自动信任 |
| Stop condition | 需要：delegate 创建的 memory 必须停留在 candidate 状态直到 controller 显式 accept |

**🔴 文档正确标记这是最容易 drift 的 packet。**

核心不可违反规则：

```
✅ delegate → create MemoryPacket(status=candidate)
✅ controller → accept/reject MemoryPacket
❌ delegate → create MemoryPacket(status=accepted)  [禁止]
❌ runtime → auto-promote candidate to accepted     [禁止]
❌ memory recall 返回 candidate 状态的 packet       [禁止]
```

**建议**：R0-E 必须有一个 **trust boundary test**：
```
测试步骤：
1. Delegate 创建 MemoryPacket(candidate)
2. 尝试直接改为 accepted → 必须失败
3. 尝试从 recall 接口查询 candidate packet → 必须不返回
4. Controller 显式 accept
5. 再次从 recall 接口查询 → 返回
```

---

### R0-F: Redis Acceleration and Recovery Rebuild

| 维度 | 评估 |
|------|------|
| 范围清晰度 | ✅ 加速 + 重建 |
| Drift 风险 | **中** — Redis 容易从"缓存"悄悄变成"truth" |
| Stop condition | 需要：Redis 全清后，从 PostgreSQL 完全重建，系统行为不变 |

**核心验证**：

```
Redis Purity Test:
1. 系统正常运行
2. FLUSHALL Redis
3. 触发 rebuild
4. 验证所有队列、lease、hot pointer 恢复
5. 验证没有数据丢失

如果这个测试通不过 → Redis 已经成为 truth source → 设计有误
```

**⚠️ 具体需要关注的 Redis key 类型**：

| Key 类型 | 可以从 PG 重建？ | 风险 |
|----------|-----------------|------|
| Task queues | ✅ 从 task status 重建 | 低 |
| Active leases | ⚠️ 需要特殊处理 | 中 — rebuild 时 lease 状态不确定 |
| Dedupe windows | ❌ 可能丢失 | 低 — 最多导致短期重复处理 |
| Hot pointers | ✅ 从 PG 重建 | 低 |

**建议**：R0-F 需要明确 rebuild 时 active lease 的处理策略：
- 选项 A：所有 active lease 视为过期，task 回到 `ready`
- 选项 B：从 `ike_task_events` 中最后一条 lease claim 事件恢复
- 推荐选项 A（更安全，代价只是 task 被 re-claim）

---

## 4. Guardrails 验证

文档列出的 5 条不可协商的 guardrails：

| Guardrail | 在 packet 设计中的体现 | 评估 |
|-----------|---------------------|------|
| Postgres as truth | R0-A schema 在 PG | ✅ |
| Redis as acceleration only | R0-F 定义为 rebuild from PG | ✅ |
| WorkContext 可重建 | R0-D 定义为 carrier not truth | ✅ 需要 reconstruction test 验证 |
| MemoryPacket 需要 controller review | R0-E 有 acceptance gate | ✅ 需要 trust boundary test 验证 |
| Controller review gate | R0-B state machine 中 `review_pending → done` 仅 controller | ✅ |

**所有 5 条 guardrails 在设计中都有体现。需要通过测试验证落地。**

---

## 5. 缺失的 Stop Conditions

每个 packet 应该有显式的 stop/abort 条件。我注意到文档没有统一定义。

**建议增加的全局 stop conditions**：

```
任何 packet 执行中发现以下情况时，立即停止并上报 controller：

1. 需要修改非 allowed_files 中的文件
2. 发现 R0-A schema 不足以支撑当前 packet 的需求
3. 发现需要引入新的一等对象
4. 发现状态转换规则与 R0-B 定义冲突
5. 发现 Redis 需要存储非可重建数据
6. 发现 MemoryPacket 需要跳过 controller review
7. 发现 WorkContext 需要存储非可派生数据
```

---

## 6. 推荐的执行启动方式

### 立即可以开始的

```
✅ R0-A: Core Runtime Schema Foundation
  - 风险最低
  - 确定性最高
  - 是所有后续 packet 的前置
  - 产出物明确：Alembic migration + 可回滚
```

### R0-A 的具体 acceptance criteria 建议

```
R0-A 完成条件：
1. Alembic migration 文件存在且可执行
2. alembic upgrade head 成功
3. alembic downgrade -1 成功（可回滚）
4. 所有 v0 表创建完成：
   - ike_projects
   - ike_tasks
   - ike_decisions
   - ike_task_events
   - ike_memory_packets
   - ike_work_contexts
   - ike_checkpoints
   - ike_outbox
5. 关键字段有约束：
   - task.status 有 CHECK constraint（限制为合法状态）
   - task_event 无 UPDATE/DELETE（或通过 trigger 防止）
   - memory_packet.acceptance_status 有 CHECK constraint
6. 不包含任何业务逻辑代码（纯 schema）
```

---

## 7. 总结评分

| 维度 | 评分 | 说明 |
|------|------|------|
| Packet 分解 | A | 6 个 packet 边界清晰、依赖正确 |
| 执行顺序 | A | 依赖链无环、无跳跃 |
| 风险识别 | A | 正确标识了 R0-B 和 R0-E 为最高风险 |
| Guardrails | A | 5 条不可协商规则明确 |
| Stop conditions | B | 需要补充全局和 per-packet stop conditions |
| Delegation 材料 | A | brief/context/result 三件套齐全 |
| 从 04-03 review 的闭环 | A+ | 所有上次提出的问题都有对应 packet |

**整体评分：A**

**批准状态：✅ 批准开始执行 R0-A。**

执行前最后确认：
1. R0-A schema 是否包含所有 8 张表
2. 每个 packet 补充显式 stop conditions
3. R0-B 和 R0-E 在执行前再做一次 controller pre-review

项目从"设计→执行"的转换是干净的。可以开始了。

# GPT
Based on the **IKE Runtime v0 Implementation Execution Pack**, here's my review and analysis:

---

## 1. **Overall Verdict**

The first-wave runtime design is well-structured for controlled execution, with a clear and narrow focus on establishing a **truthful runtime kernel**. The prioritization of **schema foundation**, **task state machine semantics**, and **WorkContext management** aligns with the overall direction of building a robust and stable runtime, particularly emphasizing **state management** and **memory integrity**.

However, some risks need to be carefully monitored, especially around **state transitions** and **memory packet handling**. The proposed milestones are appropriately sequenced, and the first execution packet (`R0-A`) is the correct starting point. The biggest concern at this stage is the potential for **drifting semantics** if tasks are rushed, particularly in **MemoryPacket** management.

## 2. **Top Risks in the First-Wave Execution Plan**

* **Fake Durability Risk**: As the design emphasizes the separation of Redis for acceleration and Postgres for truth, it's critical to ensure that **Redis does not accidentally become the authoritative store**. If object states are stored in Redis or if **WorkContext** becomes overextended, it could cause discrepancies in state recovery, leading to **semantically unreliable behavior**.
* **`WorkContext` Object Drift**: The `WorkContext` is well-suited for short-term state management, but if it is misused or overextended, it may end up becoming a catch-all for all runtime states. This could undermine the system's integrity and make **state recovery** difficult later on.
* **MemoryPacket Overuse**: The **MemoryPacket** metadata and its acceptance procedure should not be prematurely elevated to a trusted state without adequate validation and upstream review. Overuse of **MemoryPacket** in early stages may lead to false positive memory retention and drift.

## 3. **Packet Order Corrections (if any)**

* The current packet order is sound, with a clear progression:

  * **R0-A**: Core Runtime Schema Foundation
  * **R0-B**: Compressed Task State Machine Semantics
  * **R0-C**: Task Event Log and Lease Semantics
  * **R0-D**: WorkContext Snapshot Carrier
  * **R0-E**: MemoryPacket Metadata and Acceptance
  * **R0-F**: Redis Acceleration and Recovery Rebuild

However, I recommend **starting with R0-B** sooner than later. While **R0-A** should establish the base schema, **R0-B** is crucial for handling how tasks are transitioned through states and ensuring that **state machine semantics** are not oversimplified or prone to errors. Delaying the state machine setup could lead to later stages having to backtrack, especially if **MemoryPacket** and task transitions are not fully aligned with schema and semantic decisions.

## 4. **Packet Scope Corrections (if any)**

* **R0-E**: **MemoryPacket Metadata and Acceptance** should not be rushed into “trusted snapshot” mode. Its role must remain **candidate-level** during the first wave, with careful scrutiny of its integrity and transition before being accepted as part of the core workflow. Oversight here will prevent unnecessary backtracking.
* **R0-F** (Redis Acceleration and Recovery Rebuild) may require more documentation on **how Redis will maintain temporary task states** during recovery scenarios. This should be more clearly tied to the **state recovery rules** to ensure there is no confusion between temporary acceleration and permanent storage.

Overall, while the scope is well-defined for v0, the packaging of tasks and memory states should be done with precision to avoid accidental over-extension into false capability.

## 5. **First Recommended Packet to Execute**

The first packet to execute remains **R0-A (Core Runtime Schema Foundation)**, as it is the foundation upon which all subsequent layers will be built. However, **R0-B (Compressed Task State Machine Semantics)** should follow soon after to ensure that state transitions are cleanly integrated into the runtime kernel. Delaying the state machine will risk introducing problems down the line.

## 6. **What Must Still Be Tightened Before Implementation**

Before starting implementation, I recommend tightening the following areas:

1. **WorkContext Boundaries**: Ensure **WorkContext** is **not misused** as a secondary truth store. It should act purely as a snapshot carrier for state recovery, not a repository for full task state.
2. **MemoryPacket Acceptance Process**: Solidify the process for **MemoryPacket** metadata acceptance. The current state allows too much flexibility; the acceptance rules need to be enforced with **more robust validation** before allowing memory packets to influence the runtime's state.
3. **State Transition Semantics**: The handling of `active -> waiting`, `active -> blocked`, and `review_pending -> done` transitions needs **clearer cause-based semantics** rather than relying solely on labels. Define explicit metadata to ensure tasks are truly paused or blocked based on clear criteria.

## 7. **Non-Negotiable Guardrails**

As the milestone documents specify, the following guardrails must remain intact:

* **Postgres as the canonical truth source**.
* **Redis as an acceleration layer only**, not a persistence layer.
* **WorkContext as a snapshot carrier**, not a secondary source of truth.
* **MemoryPacket as a candidate** for memory state, not a full memory object.
* **Controller review gate** over all reviewable work to prevent self-acceptance.

These guardrails are essential to maintaining the integrity of the system during its early stages and preventing it from unintentionally overextending into unreliable states.

---

**Final Recommendation:**

* **Execute R0-A**, but plan to **follow up quickly with R0-B** to solidify task state machine semantics.
* Focus on tightening **WorkContext boundaries** and **MemoryPacket validation** to ensure that you’re not prematurely elevating them to trusted states.
* Ensure **task transitions** are well-defined by cause, not just labels.

This approach will keep the project moving forward without risking future drift or rework.

# gemini
针对 2026-04-05 的 `IKE Runtime v0` 实施执行包（Implementation Execution Pack），这是对 IKE 从“架构设计”进入“工程落地”阶段的深度 Review。

### 1. 总体结论 (Overall Verdict)
**结论：准予执行。**
该执行包展示了极其罕见的**工程克制力**。你没有选择从 UI 或复杂的图数据库开始，而是选择了最枯燥但最核心的“真理层”建设。这种“分包（Packetized）”执行模式配合严苛的 `PROJECT_AGENT_HARNESS_CONTRACT`，能有效防止 AI 在编码过程中产生的“语义漂移（Semantic Drift）”和“虚假持久化”。

---

### 2. 执行路径审核 (Execution Path Analysis)

你规划的 R0-A 到 R0-F 的顺序逻辑严密：
1.  **R0-A (Schema Foundation):** 定义静态结构，这是所有逻辑的基础。
2.  **R0-B (State Machine):** 赋予数据生命周期，这是最危险但也最关键的语义层。
3.  **R0-C (Events & Leases):** 引入时间轴和所有权，解决并发与可追溯性。
4.  **R0-D (WorkContext):** 解决任务恢复的载体问题。
5.  **R0-E (MemoryPacket):** 知识的初步沉淀。
6.  **R0-F (Recovery Rebuild):** 系统的最后一道防线。

**评价：** 这是一个典型的**自底向上（Bottom-up）**稳健路径。

---

### 3. 核心风险与防御策略 (Core Risks & Defense)

基于执行包内容，我认为以下三个风险点需要你在 R0-A 启动后立即保持高度警惕：

* **R0-B 的语义坍塌风险：** `inbox` 到 `triaged` 再到 `ready` 的过程，如果完全交给 Delegate 编写，可能会导致状态机逻辑过于宽松。
    * *建议：* 在 R0-B 的验证（Validation）环节，必须包含**负向测试用例**（例如：强行从未经 Review 的状态跳到 `done` 必须被数据库约束拦截）。
* **WorkContext 的“第二真理”陷阱：** 你在护栏中明确提到“WorkContext 是可重建的载体，而非第二真理”。
    * *风险：* 在实际编码中，Delegate 往往会为了省事，将某些关键业务字段只存在 `WorkContext` 的 JSON 负载里，而不去更新 Postgres 的结构化字段。
    * *对策：* 强制要求任何影响任务决策的字段必须在 Postgres Schema 中有对应列，`WorkContext` 仅用于存放“过程快照”。
* **MemoryPacket 的“信任污染”：** R0-E 是最容易产生“虚假能力”的环节。如果生成的记忆包没有经过严格的 `Study Closure` 验证，系统会迅速堆积大量垃圾知识。

---

### 4. 关键护栏审核 (Guardrail Review)

你设定的“不可谈判护栏（Non-Negotiable Guardrails）”是此项目的灵魂：
* **Postgres as Truth:** 确保了系统的确定性。
* **Redis as Acceleration:** 避免了将临时缓存当成持久化存储的行业通病。
* **Controller Review Gate:** 保持了人类（或高级 Controller）对系统进化的最后否决权。

---

### 5. 针对实施的微调建议 (Tactical Recommendations)

1.  **关于 R0-A 的原子性：** 在执行 R0-A 时，建议立即包含 `Outbox` 表的定义。因为一旦进入 R0-B，任何状态变更都应该伴随一条审计日志或副作用事件，这需要 Outbox 模式的支持以保证原子性。
2.  **细化中止条件（Stop Conditions）：** 在每个 Packet 的 brief 中，建议增加一条：“若发现当前 Schema 无法支撑未来 R0-E 的记忆提取逻辑，立即停止执行并汇报”，防止架构债务过早产生。
3.  **重视 R0-F 的早介入：** 虽然恢复重建是最后一包，但 R0-A 的表结构设计必须考虑“可恢复性”（如：必须有 `updated_at` 和 `version` 戳）。

### 总结
你现在的状态就像是在为一台即将长途跋涉的赛车构建**极其坚固的底盘**。

* **Milestone 2026-04-03** 解决了“我们要去哪（Goal）”的问题。
* **Milestone 2026-04-04** 解决了“我们怎么保证不出事（Safety）”的问题。
* **Milestone 2026-04-05 (当前)** 解决了“我们要从哪颗螺丝钉拧起（Execution）”的问题。

**下一步建议：立即启动 R0-A Core Runtime Schema Foundation 的执行。** 

如果你需要对 R0-A 的具体 Schema 细节进行深度挑战，请提供 R0-A 的具体字段定义文件。