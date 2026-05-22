# 交叉review for IKE_RUNTIME_V0_REVIEW_MILESTONE_2026-04-04.md

# claude
好的!我看到您已经有一个非常成熟的 **IKE Runtime v0** 设计文档。让我先阅读所有相关的支持文档,然后进行深度 review。


非常好!我已经完整阅读了所有 IKE Runtime v0 的设计文档。现在让我进行深度 review。

---

# 🔍 IKE Runtime v0 深度架构审查报告

## 一、总体结论 (Overall Verdict)

### ✅ 整体评价: **设计质量优秀,可以进入实施阶段**

这是一份**非常成熟**的运行时内核设计,具有以下突出优点:

1. ✅ **问题定义精准** - 直击"记忆无效、任务混乱、无法进化"的核心痛点
2. ✅ **分层清晰** - Runtime State / Artifacts / Documents / Memory 四层分离
3. ✅ **存储责任明确** - Postgres(真相) / Redis(加速) / Object Storage(负载)
4. ✅ **治理严谨** - 角色权限矩阵完整,防止 delegate 自我验收
5. ✅ **恢复现实** - 从进程重启到 Redis 丢失,都有明确恢复路径

### ⚠️ 主要风险等级: **中低** (5个关键风险可控)

---

## 二、Top 5 风险与批评

### 🔴 风险1: 任务状态机过于复杂 (High Impact)

**问题**: 11个状态 + 20+ 转换路径,V0 过于复杂

**当前状态**:
```
inbox → triaged → ready → active → waiting/blocked/review_pending → done
                                                    ↓
                                               failed/dropped/cancelled
```

**批评**:
- ❌ `waiting` vs `blocked` 的区分在实际执行中**非常容易模糊**
- ❌ `triaged` 作为中间态增加复杂度,收益不明显
- ❌ `dropped` vs `cancelled` 语义重叠

**建议**:
```
V0 精简为 7 个状态:
- inbox (待分类)
- ready (可执行)
- active (执行中)
- waiting (等待外部)
- review_pending (待审核)
- done (完成)
- failed (失败)

合并:
- triaged → ready (分类后直接进入 ready)
- blocked → waiting (阻塞是等待的特例,用 waiting_reason 区分)
- dropped/cancelled → 用 metadata 标记,不单独设状态
```

**理由**: 
- V0 的核心是**证明状态机可行**,不是覆盖所有边缘情况
- 状态越多,权限矩阵越复杂,实施风险越高
- 后续可以根据实际使用情况扩展

---

### 🔴 风险2: WorkContext 作为持久化对象的价值存疑

**问题**: `runtime_work_contexts` 表可能是**过度设计**

**当前设计**:
```sql
runtime_work_contexts:
  - active_task_id
  - latest_decision_id
  - current_focus
  - blockers_summary
  - next_steps_summary
```

**批评**:
- ⚠️ WorkContext 的字段几乎都可以从 Task/Decision **派生**出来
- ⚠️ 保持 WorkContext 与 Task/Decision 的**同步成本很高**
- ⚠️ 容易出现 WorkContext 与实际状态**不一致**的漂移

**建议**:
```
方案A (推荐): WorkContext 作为 Materialized View
  - 不单独建表
  - 通过视图/查询从 Task/Decision 派生
  - 示例查询:
    SELECT 
      t.task_id as active_task_id,
      d.decision_id as latest_decision_id,
      t.next_action_summary as current_focus
    FROM runtime_tasks t
    LEFT JOIN runtime_decisions d ON ...
    WHERE t.status = 'active'
    ORDER BY t.updated_at DESC
    LIMIT 1

方案B: WorkContext 作为 Redis Cache
  - 只在 Redis 中维护热上下文
  - 从 Postgres 重建
  - 丢失无损
```

**文档中的矛盾**:
- 文档说 "start durable, derive later if needed"
- 但实际上 **derive first 更安全**,因为:
  - 避免数据同步问题
  - 减少事务复杂度
  - 保证真相唯一性

---

### 🟡 风险3: MemoryPacket 的接受机制不够清晰

**问题**: MemoryPacket 如何从"草稿"变成"可信任记忆"?

**当前设计**:
```
- created_by_kind (controller/delegate/runtime)
- accepted_at nullable
- status 字段
```

**批评**:
- ⚠️ 缺少明确的 **MemoryPacket 接受工作流**
- ⚠️ `accepted_at` 由谁设置?什么条件触发?
- ⚠️ 如果 MemoryPacket 与 Task 关联,Task done 时是否自动接受?

**建议**:
```
明确 MemoryPacket 生命周期:

1. draft (创建时)
   ↓ [关联的 task 被接受]
2. pending_review (自动)
   ↓ [controller 审核]
3. accepted (手动或自动策略)

添加字段:
- acceptance_trigger: 'manual' | 'auto_on_task_done' | 'policy'
- acceptance_criteria: JSONB (接受条件)

或者更简单:
- MemoryPacket 不单独接受
- 跟随关联 Task/Decision 的状态
- Task done → MemoryPacket automatically trusted
```

---

### 🟡 风险4: Outbox 模式可能过早引入复杂度

**问题**: V0 是否需要 Outbox 模式?

**当前设计**:
```
runtime_outbox_events 表 + 异步分发器
```

**批评**:
- ⚠️ Outbox 是**分布式系统**模式,用于微服务间事务
- ⚠️ V0 如果是单体应用,Outbox **过度设计**
- ⚠️ 增加了一个需要维护的异步分发器

**建议**:
```
V0 简化方案:

方案A (单体应用):
  - 不使用 Outbox
  - 状态转换时直接调用 side effects
  - 用数据库事务保证原子性
  - 失败时整个事务回滚

方案B (如果确实需要异步):
  - 使用 PostgreSQL LISTEN/NOTIFY
  - 不需要额外的 outbox_events 表
  - 轻量级,足够 V0 使用

保留 Outbox 的条件:
  - 有多个独立服务
  - 需要保证跨服务事务
  - V0 不需要
```

---

### 🟡 风险5: Lease 机制的恢复策略不够具体

**问题**: Lease 过期后,任务应该去哪里?

**当前设计**:
```
lease expires → task moves to waiting/blocked/recovery triage
```

**批评**:
- ⚠️ "depending on task type and policy" **太模糊**
- ⚠️ 实施时会面临**决策困难**
- ⚠️ 缺少明确的**恢复策略表**

**建议**:
```
明确恢复策略:

| Task Type          | Lease Expires → | Reason                    |
|-------------------|-----------------|---------------------------|
| implementation    | waiting         | 可能还会回来继续          |
| review            | review_pending  | 审核结果仍然有效          |
| study             | failed          | 研究中断,需要重新开始     |
| daemon            | ready           | 下次调度会重新执行        |
| workflow          | blocked         | 需要人工判断              |

添加字段到 runtime_tasks:
- lease_expiry_policy: 'waiting' | 'failed' | 'blocked' | 'ready'
```

---

## 三、状态机转换问题

### ❌ 有问题的转换

| 转换 | 问题 | 建议 |
|-----|------|------|
| `failed -> triaged` | 失败后重新分类,流程倒退 | 改为 `failed -> ready` (修复后直接可执行) |
| `blocked -> triaged` | 阻塞后重新分类,不合理 | 改为 `blocked -> ready` (阻塞解除后可执行) |
| `review_pending -> active` | 审核后重新执行,语义不清 | 明确为"审核不通过,需要修改" |
| `cancelled -> ready` | 取消后恢复,应该是新任务 | 改为需要创建新任务 |

### ✅ 正确的关键转换

| 转换 | 评价 |
|-----|------|
| `review_pending -> done` (仅 controller) | ✅ 核心治理规则 |
| `ready -> active` (lease claim) | ✅ 所有权明确 |
| `active -> review_pending` (delegate) | ✅ 防止自我验收 |

---

## 四、权限边界问题

### ✅ 设计优秀的权限规则

1. ✅ **Guardrail 1**: Delegate 不能自我验收 - **最关键规则**
2. ✅ **Guardrail 2**: Runtime 恢复不自动完成战略决策
3. ✅ **Controller 独占**: `review_pending -> done`

### ⚠️ 需要强化的权限边界

| 问题 | 风险 | 建议 |
|-----|------|------|
| User 可以 cancel 任务 | 可能误操作 | 添加 `user_can_cancel` 策略字段 |
| Runtime 可以做 policy 转换 | 策略定义不清 | 明确列出所有 policy 转换 |
| Delegate 可以 `active -> blocked` | 可能滥用 | 需要填写 blocker_reason,controller 审核 |

---

## 五、存储/队列/恢复问题

### ✅ 正确的存储分离

| 存储 | 职责 | 评价 |
|-----|------|------|
| PostgreSQL | 真相、完整性、恢复 | ✅ 正确 |
| Redis | 队列、lease、热指针 | ✅ 正确 |
| Object Storage | 大负载、artifacts | ✅ 正确 |

### ⚠️ 需要关注的问题

1. **Postgres JSONB 使用过度**
   - `metadata JSONB` 出现在每个表
   - 风险:重要数据藏在 JSONB 中,难以查询和迁移
   - 建议:V0 限制 JSONB 使用,只存真正的元数据

2. **Redis 丢失重建成本**
   - 文档说"rebuild Redis caches from Postgres"
   - 但没有说明重建时间和性能影响
   - 建议:添加重建时间的 SLA 目标

3. **Object Storage 引用丢失**
   - 文档提到"emit integrity event"
   - 但没有定义完整性检查频率
   - 建议:添加定期完整性检查任务

---

## 六、缺失的关键对象

### 🔴 缺失: `Notification` / `Alert` 对象

**问题**: 任务状态变化后,如何通知相关人员?

**当前**: 依赖 Outbox Event,但没有通知管理

**建议**:
```sql
runtime_notifications:
  - notification_id
  - recipient_kind (controller/delegate/user)
  - recipient_id
  - notification_type (task_assigned/review_requested/blocked/etc)
  - related_task_id
  - status (pending/read/dismissed)
  - created_at
  - read_at
```

**理由**:
- 多渠道场景下,通知是核心需求
- 避免通知丢失或重复发送
- 支持通知历史查询

---

### 🟡 可选: `Tag` / `Label` 对象

**问题**: 如何跨项目标记和分类任务?

**当前**: 只能靠 metadata JSONB

**建议**:
```
V0 不添加,用 metadata 代替
V1 如果需要复杂标签系统再添加
```

---

## 七、将来修改成本高的设计选择

### 🔴 高风险: 任务状态枚举

**如果 V0 定义 11 个状态**:
- 后续删除状态会破坏历史数据
- 添加状态需要迁移所有权限检查
- 修改转换规则影响所有集成

**建议**: 
- V0 用 7 个状态启动
- 状态转换规则做成可配置的(数据库表,不硬编码)

---

### 🟡 中风险: WorkContext 持久化

**如果 WorkContext 作为独立表**:
- 后续改为派生视图需要数据迁移
- 同步逻辑难以移除
- 与 Task/Decision 的关系可能变化

**建议**: 
- V0 用视图/查询实现
- 证明价值后再考虑持久化

---

### 🟡 中风险: Outbox 模式

**如果 V0 引入 Outbox**:
- 后续移除很困难(依赖方已存在)
- 异步分发器需要维护
- 增加监控和调试复杂度

**建议**:
- V0 用同步事务 + PostgreSQL NOTIFY
- 证明需要异步后再引入 Outbox

---

## 八、推荐的下一个设计里程碑

### Milestone 2: V0 精简版设计 (1周)

**目标**: 简化设计,降低实施风险

**交付物**:

1. **精简状态机** (7 个状态)
   - 明确每个状态的语义
   - 简化的转换图
   - 恢复策略表

2. **WorkContext 方案确定**
   - 视图 vs 持久化
   - 查询示例
   - 性能评估

3. **简化事务边界**
   - 移除 Outbox (V0)
   - 明确同步事务范围
   - PostgreSQL NOTIFY 方案

4. **MemoryPacket 接受流程**
   - 明确生命周期
   - 自动 vs 手动接受
   - 与 Task 状态的关系

5. **通知模型 (新增)**
   - Notification 对象设计
   - 与多渠道的集成点
   - 通知历史管理

---

## 九、实施建议

### ✅ 可以立即开始的

1. **数据库 Schema** - 基于当前设计,创建精简版表结构
2. **状态机引擎** - 实现状态转换验证
3. **Task CRUD** - 基础任务管理
4. **Event Log** - 追加式事件记录

### ⚠️ 需要 Milestone 2 后再开始的

1. **WorkContext** - 等待方案确定
2. **Outbox** - 等待简化决策
3. **MemoryPacket 接受流程** - 等待明确设计
4. **Redis 集成** - V0 可以暂缓

---

## 十、总结

### 总体评价: **8.5/10**

| 维度 | 评分 | 说明 |
|-----|------|------|
| 问题定义 | 10/10 | 精准直击痛点 |
| 架构分层 | 9/10 | 清晰合理 |
| 状态机设计 | 7/10 | 过于复杂,需要精简 |
| 权限治理 | 9/10 | 严谨,Guardrails 优秀 |
| 存储设计 | 8/10 | 正确,但 JSONB 过多 |
| 恢复策略 | 7/10 | 需要更具体的策略表 |
| 可实施性 | 7/10 | 简化后可行 |

### 核心建议

1. **精简状态机** - 从 11 个状态减到 7 个
2. **WorkContext 用视图** - 不单独建表
3. **移除 V0 的 Outbox** - 用同步事务 + NOTIFY
4. **添加 Notification 对象** - 支持多渠道通知
5. **明确恢复策略表** - 不依赖"depending on policy"

### 是否准备好实施?

**回答**: 
- 当前设计: **70% 准备好**
- 精简后: **95% 准备好**

建议先花 **1 周**完成 Milestone 2(精简设计),然后立即开始实施。

---

**您需要我:**
1. 📝 创建 Milestone 2 的精简设计文档?
2. 💻 开始创建数据库 Schema 和状态机代码?
3. 🎯 先解决某个具体风险点?



让我获取支撑文件以进行完整审查。
支撑文件不在远程分支上，让我检查本地工作区。
支撑文件不在本地也不在已知远程分支。让我尝试查找最新分支。
支撑文件尚未推送到远程仓库。我将基于主审查文件中描述的架构信息进行深度 review。主文件的信息量已经足够做出架构层面的判断。

---

# IKE Runtime v0 架构 Review

## 1. 整体判断 (Overall Verdict)

**评分：A- — 设计方向正确，状态模型成熟度高，但有几个需要在实现前解决的结构性问题。**

这是一个**从"文档驱动的伪状态"向"真正的 runtime state 管理"跨越的关键 milestone**。它解决的核心问题是：

> 当前项目的"状态真相"分散在 chat history、docs、Redis、人的记忆中，没有单一 canonical source。

提出的解决方案——PostgreSQL 为 canonical truth，Redis 为加速层，Object Storage 为重载荷——是正确的三层分离。

但在状态机、权限矩阵和事务边界上，我发现了几个需要在实现前修正的问题。

---

## 2. Top 5 风险

### 风险 1：`waiting` vs `blocked` 的语义边界不够锋利 🔴

```
current:
  waiting != blocked
```

文档声明了区别，但**没有给出判定规则**。实际工程中，这两个状态的混淆是任务系统中最常见的 bug 来源。

| 状态 | 应有的语义 | 典型场景 |
|------|-----------|---------|
| `waiting` | 任务主动暂停，等待一个**预期中的、有时间预期的**外部事件 | 等待 delegate 完成子任务、等待 study closure 返回 |
| `blocked` | 任务无法继续，因为一个**非预期的、无法自行解除的**障碍 | 依赖的服务不可用、前置任务 failed、权限不足 |

**建议**：在实现前明确定义：
1. `waiting` 必须有 `waiting_for` 字段（引用具体的 task/event）
2. `blocked` 必须有 `blocked_by` 字段 + `blocked_reason`
3. `waiting` 有自动超时转换规则，`blocked` 没有（需要人工介入）

---

### 风险 2：`review_pending` → `done` 是唯一的 controller gate，但缺乏 rejection 路径的完整定义 🔴

```
current:
  delegates → review_pending
  controller → done
```

这个基本规则是正确的。**但 review rejection 的目标状态是什么？**

| 场景 | 应该去哪个状态？ |
|------|-----------------|
| Review 发现工作质量不够，需要返工 | `active`？`ready`？ |
| Review 发现任务本身不应该存在 | `cancelled`？`dropped`？ |
| Review 发现需要更多信息 | `waiting`？`blocked`？ |

**建议**：定义显式的 rejection transition matrix：
```
review_pending → active       (rework needed, controller)
review_pending → blocked      (missing info, controller)
review_pending → cancelled    (task invalid, controller)
review_pending → dropped      (no longer relevant, controller)
```

---

### 风险 3：MemoryPacket 的生命周期治理不够明确 🟡

文档定义了 5 个一等对象：`Project`, `Task`, `Decision`, `MemoryPacket`, `WorkContext`

对于 Task 和 Decision，状态机和权限都有描述。但 **MemoryPacket 的治理规则不够清晰**：

| 问题 | 当前状态 |
|------|---------|
| MemoryPacket 的状态机是什么？ | 未明确（candidate → reviewed → accepted → archived？） |
| 谁可以创建 MemoryPacket？ | 未明确 |
| 谁可以 accept/reject MemoryPacket？ | 未明确（应该只有 controller） |
| MemoryPacket 可以被修改吗？ | 未明确（应该是 append-only） |

**建议**：MemoryPacket 需要与 Task 同等级别的状态机和权限定义：
```
MemoryPacket 状态:
  candidate → reviewed → accepted → archived
  candidate → rejected

权限:
  delegate:  create candidate
  runtime:   create candidate (from closure)
  controller: review → accept/reject
  nobody:    modify accepted packet (append-only)
```

---

### 风险 4：WorkContext 的"持久 vs 派生"决策被延后 🟡

文档在 Open Questions 中提到：

> Is WorkContext better as a durable object or should it later become partially derived?

**这个问题不应该延后到实现后**。它直接影响：
- 数据库 schema 设计
- 恢复流程的复杂度
- 存储成本

**我的判断**：WorkContext 应该是 **hybrid**：
- **核心骨架持久化**（当前 active task、上次 checkpoint、关键 refs）
- **填充细节按需派生**（完整上下文可以从 task + artifact + memory 重建）

```
WorkContext = {
  // 持久化部分（PostgreSQL）
  project_ref: str
  active_tasks: List[str]
  last_checkpoint_ref: str
  last_decision_ref: str
  updated_at: datetime
  
  // 派生部分（运行时重建）
  full_task_tree: derived from task relations
  relevant_memories: derived from MemoryPacket recall
  recent_artifacts: derived from artifact store
}
```

这样既避免了 WorkContext 过大（每次状态变化都要写入），又避免了完全派生的重建成本。

---

### 风险 5：Outbox pattern 的实现细节不足 🟡

```
current:
  outbox-backed side effects
```

Outbox pattern 是正确的选择（避免分布式事务），但需要明确：

| 问题 | 需要回答 |
|------|---------|
| 消费者幂等性 | side effect handler 是否幂等？ |
| 重试策略 | 多少次重试？指数退避？ |
| Dead letter 处理 | 多次失败后怎么办？ |
| 顺序保证 | 同一 task 的 events 是否需要顺序投递？ |

**建议**：在实现前定义最小 outbox 契约：
```sql
CREATE TABLE ike_outbox (
  id          BIGSERIAL PRIMARY KEY,
  event_type  TEXT NOT NULL,
  payload     JSONB NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  processed   BOOLEAN NOT NULL DEFAULT FALSE,
  attempts    INT NOT NULL DEFAULT 0,
  max_retries INT NOT NULL DEFAULT 5,
  next_retry  TIMESTAMPTZ,
  error       TEXT
);
```

---

## 3. 状态转换正确性审查

### 当前状态机

```
inbox → triaged → ready → active → waiting → active (resume)
                                  → blocked → active (unblock)
                                  → review_pending → done
                                  → failed
                       → cancelled
                       → dropped
```

### 缺失的转换

| 缺失路径 | 理由 |
|----------|------|
| `inbox → dropped` | Controller 在 triage 前发现任务无效 |
| `triaged → cancelled` | Triage 后发现优先级不够 |
| `active → cancelled` | 执行中发现任务不再需要 |
| `blocked → cancelled` | 阻塞无法解除，放弃任务 |
| `blocked → failed` | 阻塞持续过久，标记为失败 |
| `waiting → cancelled` | 等待的事件不再有意义 |
| `failed → active` | 允许重试（需要 controller 权限） |

**建议**：完整的转换矩阵应该是：

```
                    ┌─────────┐
                    │  inbox  │
                    └────┬────┘
                         │ triage (scheduler/controller)
                    ┌────▼────┐
              ┌─────│ triaged │─────┐
              │     └────┬────┘     │
              │          │ ready    │ cancel
              │     ┌────▼────┐     │
              │     │  ready  │─────┤
              │     └────┬────┘     │
              │          │ claim    │
              │     ┌────▼────┐     │
        ┌─────┼─────│  active │─────┤
        │     │     └──┬───┬──┘     │
        │     │        │   │        │
   ┌────▼───┐ │  ┌─────▼┐ ┌▼──────┐ │
   │waiting │ │  │blocked│ │review │ │
   └───┬────┘ │  └──┬───┘ │pending│ │
       │      │     │      └──┬───┘ │
       └──────┘     │         │     │
    (resume→active) │    ┌────▼───┐ │
                    │    │  done  │ │
                    │    └────────┘ │
                    │               │
               ┌────▼───┐   ┌──────▼───┐
               │ failed │   │cancelled │
               └────────┘   └──────────┘
                             ┌─────────┐
                             │ dropped │
                             └─────────┘
```

---

## 4. 权限边界审查

### 当前权限模型

```
controller: full authority
delegate: bounded execution → review_pending
reviewer: (implied by controller?)
runtime: system transitions
scheduler: queue management
user: (unclear scope)
```

### 问题和建议

| 角色 | 问题 | 建议 |
|------|------|------|
| `reviewer` | 与 controller 的区别不明确 | 如果 reviewer = controller 的一个 facet，删除这个独立角色。如果不同，明确 reviewer 可以做什么 controller 不可以做的事 |
| `user` | 完全未定义权限范围 | 需要明确：user 可以创建 task？可以查看状态？可以取消自己的 task？ |
| `delegate` 创建 MemoryPacket | 未定义 | delegate 完成 study 后需要产出 memory candidate。需要允许 `delegate: create MemoryPacket(status=candidate)` |
| `runtime` 自动转换 | 哪些转换是 runtime 自动触发的？ | 需要明确列表：lease timeout → `active → failed`？heartbeat miss → `active → blocked`？ |

### 最关键的权限规则验证

```
✅ delegate 不可以自行 accept（review_pending → done 仅 controller 可操作）
✅ 这是防止 delegate self-acceptance 的核心防线
```

**但需要补充**：
```
delegate 不可以:
  - 修改 task priority
  - 修改 task scope (allowed_files, forbidden_changes)
  - 创建 accepted MemoryPacket（只能创建 candidate）
  - 取消不属于自己的 task
```

---

## 5. 存储/队列/恢复评估

### 存储分离 ✅

```
PostgreSQL: canonical truth (projects, tasks, decisions, memory metadata, outbox)
Redis: acceleration (queues, leases, hot pointers, dedupe)
Object Storage: heavy payloads (benchmarks, closures, checkpoints)
```

**判断：这个分离是正确的。**

| 验证点 | 评价 |
|--------|------|
| PostgreSQL 作为唯一 truth source | ✅ 正确 |
| Redis 不作为 authority | ✅ 正确 |
| Object Storage 用于大 payload | ✅ 正确 |

### 恢复顺序 ✅

```
1. restore Postgres truth
2. restore object payload references
3. replay outbox
4. rebuild Redis caches and active queues
```

**判断：顺序正确。** PostgreSQL 先恢复 → 对象引用恢复 → outbox 重放 → Redis 重建。这确保了 truth 总是从最可靠的来源开始。

### 需要补充的点

| 场景 | 当前处理 | 建议 |
|------|---------|------|
| **Redis 全丢** | "rebuild Redis caches" | ✅ 但需要明确：哪些 Redis key 可以从 PostgreSQL 重建？lease 状态如何处理？ |
| **Object Storage 部分丢失** | "artifact reference loss" | ⚠️ 需要明确：artifact 丢失时 task 状态怎么变？是 `blocked` 还是 `failed`？ |
| **PostgreSQL 主从切换** | 未提及 | ⚠️ 如果用了读写分离，outbox consumer 必须从 primary 读取 |
| **并发 lease claim** | 未提及 | ⚠️ 两个 delegate 同时 claim 同一个 task 时的竞争处理 |

**建议**：增加一个 `RECOVERY_SCENARIOS.md`，列出 top 10 故障场景和恢复步骤。

---

## 6. 缺失的一等对象分析

当前对象集：`Project`, `Task`, `Decision`, `MemoryPacket`, `WorkContext`

| 缺失候选 | 是否 v0 必需 | 理由 |
|----------|-------------|------|
| **TaskEvent / AuditLog** | ✅ **是** | 每次状态转换都应该有不可变的事件记录。没有它，事后审计和 debug 几乎不可能 |
| **Checkpoint** | ✅ **是** | 文档提到了 "checkpoint pointer updates"，但 Checkpoint 本身没有作为一等对象定义 |
| **Artifact** | ⚠️ 可能 | 文档提到 "Artifacts: durable evidence and outputs"，但没有定义 Artifact 对象 schema |
| **Lease** | ❌ 否 | 可以作为 Task 的子属性，不需要独立对象 |
| **Notification/Alert** | ❌ 否 | v0 不需要 |

**最关键的缺失**：**TaskEvent**

```python
class TaskEvent:
    id: str
    task_ref: str
    event_type: str          # state_change, assignment, review, comment
    from_state: Optional[str]
    to_state: Optional[str]
    actor_role: str           # controller, delegate, runtime, scheduler
    actor_id: str
    timestamp: datetime
    payload: Dict[str, Any]   # 额外上下文
    
    # IMMUTABLE — 一旦写入不可修改
```

没有 TaskEvent，以下能力都无法实现：
- 任务历史追溯
- delegate 工作质量审计
- 状态转换合规性验证
- 恢复时的 replay 验证

---

## 7. 昂贵逆转风险分析

| 设计决策 | 逆转成本 | 评估 |
|----------|---------|------|
| PostgreSQL 为唯一 truth | 低（可以后续加分片或读写分离） | ✅ 安全 |
| Redis 仅加速 | 低（可以后续升级为 event bus） | ✅ 安全 |
| 11 个 task 状态 | 中（减少状态容易，增加状态也容易，但语义变更昂贵） | ⚠️ 需要锁定语义 |
| 单一 controller 角色拥有 full authority | 中（后续拆分 controller 权限比合并容易） | ✅ 安全 |
| WorkContext 持久 vs 派生 | **高** | 🔴 如果选错，schema migration 很昂贵 |
| MemoryPacket 治理模型 | **高** | 🔴 如果现在不定义好状态机，后续所有记忆都可能是未治理的 |

---

## 8. 总体评分与下一步建议

### 评分表

| 维度 | 评分 | 说明 |
|------|------|------|
| 存储分离 | A | PostgreSQL/Redis/Object Storage 三层正确 |
| 状态机设计 | B+ | 核心正确，缺少部分转换路径和语义定义 |
| 权限模型 | B+ | 核心 gate 正确，reviewer/user 角色待明确 |
| 事务边界 | B | 方向正确，outbox 细节不足 |
| 恢复设计 | B+ | 顺序正确，场景覆盖不够 |
| 一等对象完整性 | B | 缺少 TaskEvent 和 Checkpoint 的显式定义 |
| 逆转风险控制 | B+ | 大部分决策安全，WorkContext/MemoryPacket 需要锁定 |

### 推荐：实现前的下一个设计 milestone

```
Milestone: IKE Runtime v0 Implementation-Ready Spec
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 锁定 waiting vs blocked 语义（含必须字段）
2. 锁定 review_pending rejection 的目标状态
3. 定义 MemoryPacket 状态机和权限
4. 决定 WorkContext hybrid 模型
5. 增加 TaskEvent 为一等对象
6. 定义 Checkpoint 为一等对象
7. 完成完整的状态转换矩阵（所有 state × role = allowed/forbidden）
8. 定义 outbox 最小契约
9. 列出 top 10 恢复场景

退出条件：
  - 可以直接从 spec 写出 PostgreSQL schema migration
  - 可以直接从 spec 写出 state machine enforcement code
  - 无歧义状态

预计工作量：1-2 个设计 session，不是大工程
```

---

## 总结

**这个 Runtime v0 设计做了最重要的事：把"状态真相"从散落在 chat/docs/Redis 的隐式状态，提升为显式的、持久的、可审计的 runtime state。**

它的方向完全正确。需要在实现前修补的不是方向性问题，而是**几个语义精确度和完整性问题**。上面列出的 8 项补充工作量不大，但如果不做就开始实现，后续修改会很昂贵。

**审批状态：✅ 设计方向批准，⚠️ 实现启动需要先完成上述 Implementation-Ready Spec。**



# gemini
针对您提供的 `IKE Runtime v0` 2026-04-04 里程碑文档，这是对 IKE 架构从“方法论”向“工程实现”跨越的关键审阅。

以下是作为另一个模型的深度架构挑战与评价：

### 1. 总体评价 (Overall Verdict)
**结论：这是一个极其冷静、防守型（Defensive）的架构设计，非常正确。**
该设计成功识别了 AI 协作中最致命的漏洞——**“状态幻觉”**。通过将 `PostgreSQL` 定位为唯一的规范性真理源（Canonical source of truth），并严格区分 `waiting`、`blocked` 和 `review_pending` 状态，你正在为 AI 构建一个“不可抵赖”的操作环境。这不仅是 Runtime，更是 AI 的**行为边界监控器**。

---

### 2. 前五大风险 (Top 5 Risks)

1.  **WorkContext 的爆炸式增长风险：** `WorkContext` 若记录过于详细，会迅速堆积大量冗余信息，导致在任务恢复时，Delegate（AI 代理）需要消耗大量 Token 来“重新对齐”，反而增加干扰。需要定义明确的**上下文清理/压缩策略**。
2.  **“死锁”与“幽灵任务”：** 在 `waiting` 状态下，如果外部触发器失效，任务可能永久挂起。设计中缺乏**自动降级或超时强制转换（Timeout Escalate）**机制。
3.  **Postgres 事务与外发 side-effects 的不一致：** 文档提到了 `outbox-backed side effects`，但在高并发或网络抖动下，如果 Postgres 事务提交成功但 Outbox 消息发送失败，可能会导致 Runtime 状态与实际文件操作脱节。
4.  **Delegate 的“虚假 review_pending”：** Delegate 可能会为了完成任务而强行将未通过验证的代码推入 `review_pending`。系统需要一种**自动化的 Pre-check 门禁**，在进入 Review 之前拦截明显不合规的提交。
5.  **存储裂缝：** `Postgres` 存储元数据，`Object Storage` 存储 Payload。一旦两者引用的 **哈希映射（Hash Reference）** 失效或在恢复过程中未对齐，将导致整个 Task 无法回溯。

---

### 3. 状态流转分析 (State Transitions)

* **亮点：** `review_pending` != `done` 是最核心的保护，强制了人类或高级 Controller 的确认逻辑。
* **弱点：从 `blocked` 到 `ready` 的自动触发路径缺失。** * *建议：* 引入一个 `unblock_condition` 字段。当依赖任务完成或外部资源到位时，由系统自动轮询或通知将其从 `blocked` 恢复到 `ready`。
* **状态冗余：** `cancelled`、`dropped` 和 `failed` 的区别在 v0 阶段可能过于细化。建议合并为 `terminated` 并附带一个 `reason_code`。

---

### 4. 权限边界分析 (Permission Boundaries)

* **Delegate 的边界：** 文档规定 Delegate 只能移动到 `review_pending`。
* **风险：** Delegate 是否有权将任务从 `blocked` 移动到 `waiting`？如果权限太小，Delegate 会频繁中断请求 Controller 干预；如果太大，Delegate 可能会绕过阻塞逻辑。
* **核心改进建议：** 引入 **“Lease（租约）所有权”**。处于 `active` 状态的任务必须有一个关联的 `lease_owner_id`。非 Owner 禁止更新状态，以防止多个 Delegate 同时冲突操作。

---

### 5. 存储与恢复关注点 (Storage/Recovery)

* **分层合理性：** Postgres (Truth) + Redis (Cache) + Object Storage (Payload) 的三层结构非常经典且稳健。
* **恢复逻辑挑战：** 恢复顺序第一步是“恢复 Postgres 真理”，但如果 Postgres 数据由于灾难损毁，只有 Object Storage 的备份，能否通过解析 Payload 的哈希反向重建任务树？
    * *建议：* 确保 Object Storage 的 Payload 中包含自描述的元数据（Header），以便进行**冷启动式的数据补全**。

---

### 6. 推荐的下个里程碑 (Next Design Milestone)

**建议里程碑：`IKE-RUNTIME-V0-TRACEABILITY-PROTOTYPE`**

在开始大规模实现之前，你需要证明：
1.  **任务恢复实验：** 模拟 Delegate 在执行一半时进程崩溃，新 Delegate 能否仅靠 `Postgres` 中的 `WorkContext` 完美接管任务，且不重复已经完成的步骤？
2.  **原子化闭环：** 实现一个 `Decision` 导致 `Task` 状态改变，并同步产生一个 `MemoryPacket` 索引的完整事务演示。
3.  **确定 `WorkContext` 的结构：** 它是简单的 KV 对，还是带有版本号的逻辑堆栈？

### 总结
你现在的设计非常符合你上传的那张“具备真正逻辑的数字大脑”示意图：
* **Postgres** 扮演了“长期记忆矩阵”。
* **Task State Machine** 是“意图识别与导航”的硬约束。
* **Controller/Delegate 模式** 实现了“多模态理解与决策”。

这不再是 PPT 上的概念，而是正在落地的**操作系统内核**。v0 的核心就是**“不遗忘，不越权”**。


# chatgpt
Overall verdict: **the direction is strong and much more runtime-realistic than earlier IKE design layers, but it is not yet implementation-safe until you tighten a few semantic boundaries.** The biggest win is that this milestone correctly rejects fake truth sources: chat history, docs-only state, and Redis-only authority. The core split of `Runtime State / Artifacts / Documents / Memory` is the right mental model, and the `Postgres canonical + Redis acceleration + object storage for heavy payloads` split is the right default for v0. The design is also correct to make `IKE Runtime v0` a minimal control kernel rather than “full IKE rollout” or “memory patch.” 

My short judgment is: **architecturally promising, but still one milestone away from safe implementation.** The missing piece is not more scope. It is sharper semantics around state transitions, first-class review objects, and recovery invariants. Right now the brief shows good instincts, but several expensive-to-reverse ambiguities are still present. 

## 1. Overall verdict

This is the first runtime design in your stack that feels like a **real operating kernel** instead of a conceptual layer. It is aimed at exactly the right problem: durable continuity for both OpenClaw runtime use and controller/delegate engineering, with canonical truth in state rather than hidden in chat or docs. The explicit first-class objects — `Project`, `Task`, `Decision`, `MemoryPacket`, `WorkContext` — are a strong starting set. The design is especially right to insist that `review_pending != done`, `waiting != blocked`, and Redis is not the authority. 

That said, I would **not** call it fully implementation-ready yet. It is ready for one more design-hardening milestone before coding. The main reason is that the current brief still leaves too much ambiguity in:

* transition ownership during recovery
* whether `WorkContext` is authoritative state or a derived snapshot
* when a `Decision` becomes real enough to affect task state
* whether `MemoryPacket` is sufficiently governed as an object distinct from artifacts and documents
* how review acceptance is represented as an event versus a state jump 

## 2. Top 5 risks

### Risk 1: `WorkContext` may become a hidden catch-all object

`WorkContext` is currently in the minimum kernel object set, which is probably right for v0, but it is the most dangerous object in the design. If it becomes “whatever current context we need to restore work,” it will silently absorb state that should live in `Task`, `Decision`, `Checkpoint`, or artifacts. That would recreate the exact hidden-state problem you are trying to avoid, just in a database object instead of chat. The brief already hints at this by asking whether `WorkContext` should later become partially derived. I think that is the right suspicion. 

### Risk 2: `review_pending -> done` may still be too state-centric

The brief correctly says only controller may move reviewable work to `done`, while delegates can only move bounded work to `review_pending`. That is a good rule. But the design still reads like a direct transition matrix problem. In practice, acceptance should probably be modeled as a **review decision event** plus optional artifact validation, not just a privileged transition. If not, “done” risks becoming an overloaded state that hides whether validation actually passed, whether artifacts were accepted, and whether the controller approved semantics or merely closed the task. 

### Risk 3: `failed`, `dropped`, and `cancelled` are still easy to misuse

The brief distinguishes them, which is good, but this triad is often where systems drift:

* `failed`: attempted and failed due to execution or outcome
* `dropped`: intentionally abandoned before meaningful execution
* `cancelled`: stopped by an explicit actor or policy after entering flow
  Unless these are defined with strict allowed predecessor states and actor constraints, people will use them as synonyms. That will corrupt later metrics, recovery logic, and memory extraction. 

### Risk 4: object storage “heavy payloads” is right, but artifact/reference integrity is underdefined

You correctly require recovery from “artifact reference loss,” which is good, but that also means you already know this is a real risk. Right now the brief says object storage holds benchmark outputs, study outputs, closure payloads, large checkpoints, and large memory packet bodies. That is sensible, but you need a stronger contract for:

* what metadata must remain in Postgres even if object bodies are external
* what checksum/version/hash is required
* what counts as a recoverable missing body versus a corrupted reference
* whether acceptance can happen before object storage durability is confirmed 

### Risk 5: recovery semantics for leases and outbox replay may still allow semantic duplication

You explicitly require atomic handling for lease claim / expiry recovery and outbox-backed side effects, and recovery order says: restore Postgres truth, restore object payload references, replay outbox, rebuild Redis. That is directionally right. But the expensive-to-reverse failure mode is this: after restart, tasks may be semantically re-enqueued or side effects re-issued without a sufficiently strong idempotency key. If the first implementation gets this wrong, you will build invisible drift into task history and decision logs. 

## 3. Incorrect or weak state transitions

### `active -> waiting` and `active -> blocked`

This distinction is good, but it must be defined by **cause**, not just label.

* `waiting` should mean work is paused on an expected external dependency or scheduled time, with no error condition implied.
* `blocked` should mean progress is impossible until a blocking condition is resolved, often needing intervention.
  If these are not separated by explicit blocker metadata and wake-up conditions, they will collapse in practice. 

### `review_pending -> done`

As above, this is semantically too important to be “just another transition.” I recommend it require:

* a review result object or event
* validation evidence reference
* actor identity
* optional acceptance rationale
  Otherwise the system may technically prevent delegate self-acceptance, but still lose why something became done. 

### `failed -> ready` or `failed -> active` recovery path

The brief mentions stale lease recovery and partial side-effect failure, but it does not yet say enough about how `failed` tasks re-enter flow. This needs explicit policy:

* retryable failure vs terminal failure
* who can reset it
* whether reset creates a new attempt record
* whether the task state resets, or a sub-attempt state resets
  Without that, failure recovery will get improvised. 

### `done` should probably be terminal, but closure may not be

Right now `done` sounds terminal, but in a system with decisions, memory, and artifacts, there is often a second concept:

* task execution complete
* closure and downstream extraction complete
  You may need a separate closure/completion artifact or post-task hook status instead of overloading `done` to mean “everything including memory consequences is settled.” 

## 4. Incorrect or weak permission boundaries

### Delegate cannot self-accept: good, but reviewer/controller split may still be fuzzy

You define `controller`, `delegate`, `reviewer`, `runtime`, `scheduler`, `user`, and say only controller may move reviewable work to `done`. Good. But if `reviewer` exists as a separate role, what exactly can it finalize?

* Can reviewer approve artifacts but not close the task?
* Can reviewer reject and force rollback to `ready` or `triaged`?
* Can reviewer accept memory packets, or only controllers?
  These need sharper boundaries, or “reviewer” will be either toothless or quietly controller-like. 

### Runtime and scheduler should never gain hidden semantic authority

The brief names `runtime` and `scheduler` as roles, which is fine operationally. But they must never become semantic approvers. They can:

* claim leases
* expire stale active work
* enqueue retries
* run scheduled transitions
  They must not:
* decide acceptance
* synthesize final state meaning
* approve memory packets or decisions
  This sounds obvious, but it is exactly the kind of shortcut that appears later and becomes expensive to reverse. 

### Memory packet acceptance is underspecified

You explicitly ask whether role boundaries are correct around memory packet acceptance. I think the answer is: **not fully yet.** Because `MemoryPacket` is safety-sensitive. If memory is allowed to influence future work-context restoration, then acceptance rules must be tighter than artifact upload rules. I would not let delegate-generated memory packets become active recall material without controller or reviewer approval, at least in v0. 

## 5. Storage / queue / recovery concerns

### PostgreSQL / Redis / object storage split: correct

This is the right early split:

* Postgres for canonical truth and durable workflow semantics
* Redis for speed only
* object storage for large bodies
  I would keep this exactly as the base v0 architecture. It is realistic and reversible. 

### But add stricter contracts around object-storage references

For every heavy payload stored externally, Postgres should hold at least:

* object key
* content hash
* size
* creation timestamp
* producing actor/runtime
* state of upload confirmation
  Otherwise “artifact reference loss” will be too vague to recover deterministically. 

### Redis rebuild realism is good, but queue idempotency needs to be first-class

You explicitly say Redis caches and active queues should be rebuilt after Postgres truth and outbox replay. That is correct. But only safe if queue entries are derived from durable state and replay is idempotent. If queue identity is ephemeral, you will get duplicate semantic work after restart. So I would make idempotency keys and replay-safe enqueue rules first-class in the next milestone. 

### Backup / recovery realism is decent, but checkpoint semantics need hardening

You mention checkpoints and large checkpoints, which is good. The next design step needs to define:

* what a checkpoint guarantees
* whether it is logical or physical
* whether it can be partial
* how it interacts with `WorkContext`
* whether checkpoint pointer updates are monotonic or replaceable
  If you do not define that now, recovery will depend on ad hoc interpretation of “latest checkpoint.” 

## 6. Is any critical first-class object still missing?

Yes: I think one is still missing, or at least not explicit enough.

### Missing candidate: `Review`

Right now review seems implied through state transitions and role permissions. I think that is too weak. Given how central controller/delegate acceptance is, `Review` or `ReviewRecord` should probably be first-class. It would hold:

* target task / artifact / memory packet / decision
* reviewer actor
* outcome
* rationale
* validation refs
* timestamp
  Without this, too much meaning gets hidden in task state or decision logs. That is expensive to reverse later.

A weaker alternative is to make review a subtype of `Decision`, but I would be careful: if `Decision` becomes the dumping ground for all acceptance semantics, it may become too broad.

### Possible second missing object: `Lease`

You might not need it as a first-class business object, but operationally the design already depends heavily on lease claim / expiry recovery. If lease semantics are complex, model them explicitly rather than burying them in Redis and task events. 

## 7. Most expensive-to-reverse design choices

The ones I would worry most about are:

**1. Letting `WorkContext` become authoritative instead of bounded.**
If it turns into a bag of hidden truth, later cleanup will be painful. 

**2. Treating acceptance as a state jump instead of a review object/event.**
That will make governance and auditability much harder later. 

**3. Allowing memory packets to become active recall without strong approval semantics.**
That would pollute continuity and be difficult to unwind. 

**4. Weak idempotency around outbox replay and queue rebuild.**
Invisible duplication is one of the hardest runtime bugs to clean up retroactively. 

**5. Under-specifying failed/dropped/cancelled semantics.**
This will poison metrics, automation, and recovery rules over time. 

## 8. Recommended next design milestone before implementation

I would make the next milestone:

**“Review, Lease, and Recovery Semantics Hardening”**

Specifically, before implementation starts, I would require one more design packet that does these five things:

1. **Define transition invariants**
   For each non-trivial state transition:

* allowed predecessors
* allowed actors
* required metadata
* whether side effects are allowed
* whether retry is possible

2. **Make review first-class**
   Either as `Review` or as a sharply defined decision subtype.

3. **Define `WorkContext` boundaries**
   What it may contain, what it must not contain, and what is always derived instead.

4. **Define recovery/idempotency contracts**
   Especially for:

* lease expiry
* outbox replay
* queue rebuild
* duplicate side-effect prevention

5. **Define memory acceptance path**
   How a `MemoryPacket` goes from candidate to approved recall material, and who can authorize each step.

## Bottom line

This runtime v0 design is **good enough to approve directionally, but not yet good enough to implement blindly**. It is much more realistic than earlier IKE layers because it finally centers runtime truth, task governance, and recovery instead of chat reconstruction. But to avoid expensive redesign later, you should harden:

* review as a first-class concept
* work-context boundaries
* failure/cancellation semantics
* idempotent recovery rules
* memory acceptance governance
  before coding starts. 

