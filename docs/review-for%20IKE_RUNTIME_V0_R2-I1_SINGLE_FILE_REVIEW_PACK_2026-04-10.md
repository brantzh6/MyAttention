# claude code

加载 review 历史，然后读取实现文件进行代码级审查。
现在我有完整的代码级上下文。开始正式 review。

---

# IKE Review #11 — R2-I1 Live Lifecycle Proof Route

## Meta

| 字段 | 值 |
|------|-----|
| 序号 | 11 |
| 日期 | 2026-04-10 |
| 类型 | execution_pack |
| 文档 | IKE_RUNTIME_V0_R2-I1_SINGLE_FILE_REVIEW_PACK_2026-04-10.md |
| 评分 | **B+** |
| 方向判断 | on_track |
| 批准状态 | ✅ accept_with_changes |

---

## 1. 闭环验证

基于 Review #10 的待验证事项：

| # | 上次提出的问题 | 本次回应状态 | 评估 |
|---|---------------|-------------|------|
| 1 | Option B 5 条件实现并通过 preflight | 不在 R2-I1 scope | ❌ 仍遗留 |
| 2 | `acceptable_windows_venv_redirector` 不自动升级 | 不在 scope | ❌ 仍遗留 |
| 3 | 平台特定例外 governance doc | 不在 scope | ❌ 仍遗留 |
| 4 | `force=True` 角色限制 | 未涉及 | ❌ 遗留 (4 次) |
| 5 | retained notes 统一 backlog | 未涉及 | ❌ 遗留 (4 次) |
| 6 | 第一个真实 task lifecycle | **R2-I1 是对此的直接回应** | ⚠️ 见核心评估 |
| 7 | 第二个 concept benchmark 排期 | 未涉及 (6 次遗留) | ❌ ⚠️⚠️⚠️ |
| 8 | Procedural memory 演进排期 | 未涉及 (6 次遗留) | ❌ ⚠️⚠️⚠️ |

**关于 #6 "第一个真实 task lifecycle" 的关键判断**：R2-I1 *部分* 回应了这个诉求，但有一个重要的语义差距（详见核心评估 4.2）。

---

## 2. 方向偏移检测

| # | 不可变原则 | 本次状态 | 评估 |
|---|-----------|---------|------|
| 1 | PostgreSQL 为唯一 canonical truth | ⚠️ **proof 不经过 PostgreSQL**（InMemory only） | ⚠️ 见核心评估 |
| 2 | Redis 仅加速 | 未涉及 Redis | ✅ |
| 3 | API 契约反映真实能力 | `inspect_only=true`, `persists_runtime_state=false` — 诚实标注 | ✅ |
| 4 | Controller/Delegate 分离 | Proof 内部 controller does triage+accept, delegate does claim+submit | ✅ |
| 5 | MemoryPacket 需 controller review | `create_lifecycle_memory_packet` 需要 `accepted_by_kind=CONTROLLER` | ✅ |
| 6 | WorkContext 可重建 carrier | `derive_work_context_from_proof` — derivative, not truth source | ✅ |
| 7 | Migration 路径 | 增量新增 route，无 rewrite | ✅ |

**偏移数：0/7 真实偏移，1/7 需要关注（原则 #1）。**

原则 #1 标注 ⚠️ 的原因：proof 完全在内存中运行，使用 `InMemoryClaimVerifier`。这不违反原则（因为 proof 明确声明 `persists_runtime_state=false`），但这意味着 **"第一个真实 task lifecycle" 这个 claim 只证明了状态机逻辑，没有证明 PG-backed truth path**。

---

## 3. 主线进度

| 维度 | 内容 |
|------|------|
| 上次位置 | R2-H preflight normalization, Windows venv acceptability |
| 本次位置 | R2-I1 lifecycle proof route on live service |
| 推进方向 | 前进 |
| 推进质量 | **实质性，但 proof scope 比预期窄** |

```
API 决策 → 对象层 → Benchmark → 项目审查 → Runtime 架构
  → 执行包 → R0-A~F → R1-C~K → R2-A → R2-H preflight
  → R2-I1 lifecycle proof route ← HERE
```

---

## 4. 核心评估

### 4.1 Review Question 逐项回答

**Q1: Does this route stay narrow enough to count as proof infrastructure rather than feature creep?**

**✅ 是。** 证据：

| 检查点 | 结果 |
|--------|------|
| Route 数量 | 1 个 POST endpoint |
| Route 名称 | `/runtime/task-lifecycle/proof/inspect` — 明确是 proof + inspect |
| Response 包含 `inspect_only: true` | ✅ |
| Response 包含 `persists_runtime_state: false` | ✅ |
| Response 包含 `implies_general_task_runner: false` | ✅ |
| 无 DB 写入 | ✅ |
| 无 scheduler / queue 交互 | ✅ |

**Q2: Does it preserve runtime-owned truth rather than introducing shadow state?**

**✅ 是。** ClaimContext verification 在 proof 内部执行。WorkContext 是 derivative。没有写入任何持久存储。

**Q3: Does the response shape honestly communicate inspect/proof output?**

**✅ 是。** `truth_boundary` 嵌套对象是一个好的设计选择——显式声明了三个否定条件。

**Q4: Is there any hidden drift toward general orchestration or persistence?**

**✅ 无。** 但见 4.3 关于 router 厚度的担忧。

**Q5: Is there any structural issue in how lease / event / derived work-context data are exposed?**

**⚠️ 一个小问题。** `proof.lease` 如果是 `None` 则返回 `null`，但没有解释原因。建议在 lease 为 null 时增加一个 `lease_note: "no lease required for this lifecycle path"` 字段。

---

### 4.2 "第一个真实 task lifecycle" 闭环判断

**这是本次 review 的关键判断。**

Review #8 要求的是：
> 第一个真实 task 完整生命周期（inbox → done）

R2-I1 提供的是：
> 一个 inspect-style proof route，在内存中执行 inbox→ready→active→review_pending→done

| 预期 vs 实际 | 状态 |
|-------------|------|
| task 从 inbox 到 done | ✅ 路径正确 |
| 使用 hardened runtime state machine | ✅ ClaimContext + transitions |
| 状态转换可审计 | ✅ event alignment 验证 |
| **PG-backed 持久化** | ❌ 完全 InMemory |
| **使用真实 PG ClaimVerifier** | ❌ InMemoryClaimVerifier |
| **在真实 service 上可执行** | ✅ live proof 200 OK |

**判断**：R2-I1 证明了**状态机正确性**（这很重要），但没有证明 **DB-backed lifecycle 正确性**（这是 "真实 task lifecycle" 的核心诉求）。

**这不是一个错误，但需要明确记录**：lifecycle proof ≠ lifecycle fact。下一步应该证明 PG-backed 路径。

---

### 4.3 Router 厚度趋势 🟡

| Review | Router 行数 | Endpoints 数量 |
|--------|------------|----------------|
| #2 (v0 milestone) | ~250 行 | 3 |
| #11 (current) | 714 行 | 8 |

**Router 在 11 个 review 中增长了近 3 倍。** 当前 8 个 endpoints：

```
1. POST /decisions/preview
2. POST /harness-cases/preview
3. POST /observations/inspect
4. POST /chains/inspect
5. POST /runtime/project-surface/inspect
6. POST /runtime/project-surface/bootstrap
7. POST /runtime/benchmark-candidate/import
8. POST /runtime/task-lifecycle/proof/inspect ← 新增
```

Router 本身没有业务逻辑泄漏（每个 handler 都只调用 helper + 构造 envelope），但**单文件 8 个 endpoints 开始达到拆分阈值**。

**建议**：下一个 milestone 时考虑将 router 拆为两个文件：
- `routers/ike_v0_objects.py` — preview/inspect 对象端点
- `routers/ike_v0_runtime.py` — runtime proof/preflight/project 端点

---

### 4.4 代码质量评估

| 维度 | 评价 |
|------|------|
| `task_lifecycle.py` helper 质量 | ✅ A — 680 行，结构清晰，每步有错误处理和 early return |
| `CANONICAL_LIFECYCLE_PATH` 常量化 | ✅ 好设计——路径可审计、可测试 |
| `CANONICAL_LIFECYCLE_ACTORS` 对齐 | ✅ 每步 actor 显式定义 |
| 测试覆盖 | ✅ A — 661 行测试，覆盖正向/反向/边界 |
| 测试分类 | ✅ 清晰的 test class 分组（Lifecycle / WorkContext / Memory / Truth / Path / Edge / Lease） |
| Integrity validator | ✅ `validate_lifecycle_proof_integrity` 检查 transitions+events+lease 一致性 |

**特别好的设计**：

```python
# truth_boundary 嵌套对象
"truth_boundary": {
    "inspect_only": True,
    "persists_runtime_state": False,
    "implies_general_task_runner": False,
}
```

这是 IKE v0 "API 诚实性" 原则的优秀执行。

---

### 4.5 语义诚实性检查

| 检查项 | 结果 |
|--------|------|
| Fake durability | ✅ 无。`persists_runtime_state: false` |
| Fake capability | ⚠️ **需要注意**。Route 名称是 "lifecycle proof"，但它只证明 in-memory state machine，不证明 PG-backed persistence。名称是准确的（proof ≠ fact），但调用者可能误解 |
| Hidden state | ✅ 无。WorkContext is derivative |
| Delegate self-acceptance | ✅ 无。review_pending→done 由 controller 执行 |
| Premature complexity | ✅ 无。单一 canonical path，没有通用化 |
| Read/Write trust collapse | ✅ 无。只有 read，没有 write |

---

## 5. 风险识别

| # | 风险 | 严重度 | 分类 | 说明 |
|---|------|--------|------|------|
| 1 | **InMemory proof 被误解为 DB-backed lifecycle 证明** | 🟡 中 | semantic | "第一个真实 task lifecycle" 的 claim 需要限定语 |
| 2 | **Router 厚度持续增长** | 🟡 中 | architecture | 714 行 / 8 endpoints，接近拆分阈值 |
| 3 | **长期遗留持续恶化** | 🔴 高 | process | concept #2 和 proc memory 已 6 次遗留 |
| 4 | **force=True 和 retained notes 4 次未修复** | 🟡 中 | governance | fix-now 项目持续跳过 |
| 5 | **InMemoryClaimVerifier 在 proof 中自动注册** | 🟢 低 | testing | 方便但掩盖了真实 PG verifier 路径 |

---

## 6. 下一步建议

### Fix-Now

1. **Router 拆分规划**——不需要立刻拆分，但需要在下一个 route 新增前决定拆分策略

### 推荐下一阶段

```
R2-I2: DB-Backed Lifecycle Proof
  目标: 用真实 PG session + PG-backed ClaimVerifier 运行一个 lifecycle
  证明: 不只是状态机逻辑正确，而是 PG truth path 完整

R2-I3: Debt Settlement (不可再推迟)
  - force=True 角色限制
  - retained notes 统一 backlog
  - concept #2 + proc memory 正式排期

不做:
  - broad task CRUD
  - scheduler platform
  - UI surface
```

---

## 7. 要求下次验证的事项

| # | 待验证事项 | 来源 |
|---|-----------|------|
| 1 | InMemory proof 与 DB-backed proof 的差距是否被显式记录 | 本次新增 |
| 2 | Router 拆分策略 | 本次新增 |
| 3 | `force=True` 角色限制 | Review #8 遗留 (**4 次**) |
| 4 | retained notes backlog | Review #8 遗留 (**4 次**) |
| 5 | 第二个 concept benchmark **正式排期** | Review #5 遗留 (**6 次**) 🔴 |
| 6 | Procedural memory 演进 **正式排期** | Review #5 遗留 (**6 次**) 🔴 |
| 7 | Windows venv Option B 实现 | Review #10 遗留 |

**⚠️ 严重闭环警告**：#5 和 #6 已经 6 个 review 周期未被回应。如果下次 review 仍然没有正式排期（不需要完成，只需要 plan），将标注为 🔴 process failure。

---

## 8. 批准状态

**✅ accept_with_changes**

| 条件 | 说明 |
|------|------|
| 接受 R2-I1 route 作为 in-memory lifecycle proof | ✅ |
| 需要明确记录：这是 state-machine proof，不是 DB-backed lifecycle proof | 必须补充 |
| 下一步应推进 DB-backed proof 或 debt settlement | 二选一 |

---

## 审查链摘要

| Review | 日期 | 类型 | 评分 | 方向 | 关键判断 |
|--------|------|------|------|------|---------|
| #1 | 2026-03-29 | architecture | N/A | on_track | Option B 批准 |
| #2 | 2026-03-29 | milestone | B+/A- | on_track | 对象层批准 |
| #3 | - | benchmark | B+ | on_track | B1 批准 |
| #4 | - | benchmark | A- | on_track | B2 批准 |
| #5 | 2026-04-03 | milestone | A | on_track | 项目整体审查 |
| #6 | 2026-04-04 | architecture | B+→A- | on_track | Runtime 架构有条件批准 |
| #7 | 2026-04-05 | execution_pack | A | on_track | 执行包批准 |
| #8 | 2026-04-05 | execution_pack | B+ | on_track | First-wave 有条件批准 |
| #9 | 2026-04-08 | architecture | A- | on_track | Second-wave consolidated |
| #10 | 2026-04-09 | architecture | A | on_track | Windows venv Option B |
| **#11** | **2026-04-10** | **execution_pack** | **B+** | **on_track** | **Lifecycle proof route accept_with_changes** |

**累计：11/11 on_track，零方向偏移。**

---

现在写入持久化文件。

```markdown
# IKE Review #11 - 2026-04-10

## Meta

| 字段 | 值 |
|------|-----|
| 序号 | 11 |
| 日期 | 2026-04-10 |
| 类型 | execution_pack |
| 文档 | IKE_RUNTIME_V0_R2-I1_SINGLE_FILE_REVIEW_PACK_2026-04-10.md |
| 评分 | B+ |
| 方向判断 | on_track |
| 批准状态 | ✅ accept_with_changes |

---

## 1. 闭环验证

| # | 上次提出的问题 | 本次回应状态 | 评估 |
|---|---------------|-------------|------|
| 1 | Option B 5 条件实现 | 不在 scope | ❌ 遗留 |
| 2 | venv redirector 不自动升级 | 不在 scope | ❌ 遗留 |
| 3 | 平台例外 governance doc | 不在 scope | ❌ 遗留 |
| 4 | force=True 角色限制 | 未涉及 (4次遗留) | ❌ |
| 5 | retained notes backlog | 未涉及 (4次遗留) | ❌ |
| 6 | 第一个真实 task lifecycle | R2-I1 部分回应 (InMemory only) | ⚠️ |
| 7 | concept #2 排期 | 未涉及 (6次遗留) | ❌ 🔴 |
| 8 | proc memory 演进排期 | 未涉及 (6次遗留) | ❌ 🔴 |

---

## 2. 方向偏移检测

| # | 不可变原则 | 本次状态 | 评估 |
|---|-----------|---------|------|
| 1 | PG canonical truth | Proof 不经过 PG (InMemory) | ⚠️ 不违反但需注意 |
| 2 | Redis 仅加速 | 未涉及 | ✅ |
| 3 | API 反映真实能力 | truth_boundary 三否定 | ✅ |
| 4 | Controller/Delegate 分离 | proof 内部正确分离 | ✅ |
| 5 | MemoryPacket 需 controller | helper 要求 accepted_by_kind=CONTROLLER | ✅ |
| 6 | WorkContext derivative | derive_work_context_from_proof | ✅ |
| 7 | Migration 路径 | 增量新增 | ✅ |

偏移数：0/7 真实偏移。累计 11 次零偏移。

---

## 3. 核心评估

### Route 窄度：✅ 通过
- 1 endpoint, inspect-only, no persistence, truth_boundary explicit

### Lifecycle proof 范围：⚠️ 需限定
- 证明了 state-machine 正确性（InMemory）
- 未证明 DB-backed lifecycle（PG ClaimVerifier / PG transactions）

### Router 厚度：🟡 接近阈值
- 714行 / 8 endpoints，建议拆分规划

### 代码质量：✅ A
- helper 680行 结构清晰
- 测试 661行 覆盖全面（54 passed）

### 语义诚实性
| 检查项 | 结果 |
|--------|------|
| Fake durability | ✅ 无 |
| Fake capability | ⚠️ proof ≠ fact 需明确 |
| Hidden state | ✅ 无 |
| Delegate self-acceptance | ✅ 无 |
| Premature complexity | ✅ 无 |

---

## 4. 风险识别

| # | 风险 | 严重度 | 说明 |
|---|------|--------|------|
| 1 | InMemory proof 被误解为 DB-backed | 🟡 中 | 需限定语 |
| 2 | Router 厚度 | 🟡 中 | 接近拆分阈值 |
| 3 | 长期遗留恶化 | 🔴 高 | concept#2 + proc memory 6次遗留 |
| 4 | force=True/retained notes | 🟡 中 | 4次未修复 |

---

## 5. 要求下次验证的事项

| # | 待验证事项 | 来源 |
|---|-----------|------|
| 1 | InMemory vs DB-backed proof 差距显式记录 | 本次新增 |
| 2 | Router 拆分策略 | 本次新增 |
| 3 | force=True 角色限制 | Review #8 遗留 (4次) |
| 4 | retained notes backlog | Review #8 遗留 (4次) |
| 5 | concept #2 正式排期 | Review #5 遗留 (6次) 🔴 |
| 6 | proc memory 演进排期 | Review #5 遗留 (6次) 🔴 |
| 7 | Windows venv Option B 实现 | Review #10 遗留 |

---

## 6. 批准状态

✅ accept_with_changes
- 接受 InMemory lifecycle proof route
- 需补充记录：state-machine proof ≠ DB-backed lifecycle proof
- 下一步推进 DB-backed proof 或 debt settlement

---

## 审查链摘要

| Review | 日期 | 类型 | 评分 | 方向 |
|--------|------|------|------|------|
| #1 | 2026-03-29 | architecture | N/A | on_track |
| #2 | 2026-03-29 | milestone | B+/A- | on_track |
| #3 | - | benchmark | B+ | on_track |
| #4 | - | benchmark | A- | on_track |
| #5 | 2026-04-03 | milestone | A | on_track |
| #6 | 2026-04-04 | architecture | B+→A- | on_track |
| #7 | 2026-04-05 | execution_pack | A | on_track |
| #8 | 2026-04-05 | execution_pack | B+ | on_track |
| #9 | 2026-04-08 | architecture | A- | on_track |
| #10 | 2026-04-09 | architecture | A | on_track |
| **#11** | **2026-04-10** | **execution_pack** | **B+** | **on_track** |

累计：11/11 on_track，零偏移。
```

更新 seed：

```markdown|CODE_EDIT_BLOCK|d:\code\normalworks\.qoder\skills\ike-milestone-review\review-seed.md
# ... existing code ...

方向: 10/10 on_track, 零偏移

## Review #11 - 2026-04-10 (R2-I1 Lifecycle Proof Route)
- **类型**: execution_pack
- **文档**: IKE_RUNTIME_V0_R2-I1_SINGLE_FILE_REVIEW_PACK_2026-04-10.md
- **评分**: B+
- **方向判断**: on_track
### 关键发现
1. Route 窄度正确——inspect-only, truth_boundary 三否定
2. 代码质量高——helper 680行 + 测试 661行 (54 passed)
3. ⚠️ Proof 是 InMemory state-machine proof，不是 DB-backed lifecycle proof
4. ⚠️ Router 已达 714行 / 8 endpoints，接近拆分阈值
5. "第一个真实 task lifecycle" claim 需要限定语
### 提出的风险
1. 🟡 InMemory proof 被误解为 DB-backed lifecycle
2. 🟡 Router 厚度持续增长
3. 🔴 长期遗留恶化 (concept#2 + proc memory 6次遗留)
4. 🟡 force=True / retained notes 4次未修复
### 要求下次验证的事项
1. InMemory vs DB-backed proof 差距显式记录
2. Router 拆分策略
3. force=True 角色限制 (Review #8 遗留 4次)
4. retained notes backlog (Review #8 遗留 4次)
5. 第二个 concept benchmark 正式排期 (Review #5 遗留 6次) 🔴
6. Procedural memory 演进排期 (Review #5 遗留 6次) 🔴
7. Windows venv Option B 实现 (Review #10 遗留)
### 批准状态
✅ accept_with_changes

---
## 主线进度总结

API 决策 → 对象层 → Benchmark → 项目审查 → Runtime 架构 → 执行包 → R0-A~F → R1-C~K → R2-A → R2-H preflight → R2-I1 lifecycle proof route

方向: 11/11 on_track, 零偏移
```

Review #11 完成。总结三个核心信号：

1. **Route 质量高** — 窄、诚实、测试完整。`truth_boundary` 三否定是 IKE API 诚实性原则的优秀执行。

2. **但它不是 "真实 task lifecycle" 的完整证明** — InMemory state-machine proof ≠ DB-backed lifecycle proof。下一步需要用 PG session 运行一个完整 lifecycle，才能真正闭合 Review #8 的核心诉求。

3. **长期遗留已到临界点** — 第二个 concept benchmark 和 procedural memory 演进已经 **6 个 review 周期** 未获回应。项目技术方向持续正确（11/11 on_track），但闭环纪律正在成为最大的 process 风险。下次 review 如果仍无正式排期，将标注为 🔴 process failure。

# chatgpt
基于你上传的 review pack，我的结论是：**这条 route 方向上是对的，基本守住了“窄 proof route、不是 runtime 平台化扩张”的主线，但目前更像“可条件通过”，还不够到“无保留放行”。** 最大原因不是包里暴露出了明显偏航，而是这次材料主要证明了**意图、语义和验证结果**，还没有让我直接看到源码层面是否存在隐藏的持久化、响应过宽、或把 derived work context 变成第二真相源的实现细节。 

## summary

我倾向于给这个包一个 **“通过，但带 guardrails”** 的 review 结论。

从包里写明的范围看，这次只新增一个 inspect 风格路由 `POST /api/ike/v0/runtime/task-lifecycle/proof/inspect`，其 intent 也明确限定为“证明一条 live-service-adjacent runtime lifecycle path”，并明确声明它**不是** general task runner、scheduler API、broad task CRUD surface、durable acceptance action；语义上还专门返回 `inspect_only = true`、`persists_runtime_state = false`、`implies_general_task_runner = false`。这组约束本身是对的，也和 IKE 近期“先做稳定 runtime proof，不做平台化扩张”的主线一致。

同时，这个包的 mainline framing 也是健康的：它不是另起一套 task platform，而是把“之前 helper/test level 已经证明过的生命周期正确性”抬到当前 canonical live service surface 上。测试和本地 live proof 也都给出了正向结果：`54 passed`、compile passed、本地服务 `200 OK`、`final_status = done`、`integrity.valid = true`、`integrity.auditable = true`。从“proof infrastructure”这个角度，这一步是成立的。

## findings

**1. 范围控制总体合格。**
就 review pack 描述而言，这条 route 仍然是“inspect/proof 输出”，不是 task platform 的起点。它的返回内容虽然包含 lifecycle summary、integrity、transitions、events、lease、derived work context，但包里已经明确把这些都放在“provisional audit-shaped envelope”里，并且加了三层否定式标记，防止被误解成“正式 acceptance / orchestration surface”。这比直接给一个通用 `GET lifecycle` 或 `POST task/accept` 要安全得多。

**2. 主线方向是对的：从 helper proof 抬升到 canonical service，而不是绕开 canonical service。**
这是这次改动最值得肯定的点。包里明确说， earlier runtime work 已经在 helper/test level 验证过 lifecycle correctness，这次是把 proof 提升到 live canonical service surface，而不是重新造一个旁路验证面。这个方向符合 IKE 一直强调的“不要造第二套 truth surface”。

**3. 语义上足够诚实，但还差一步“防误用设计”。**
现在文档层已经很诚实：inspect only、no persistence、not general runner。问题在于，**文档诚实不等于接口天然不容易被误用**。如果响应里把 `events`、`lease`、`derived work context` 暴露得过于完整、稳定、易消费，外部调用方很容易把这条 proof route 当成事实上的 runtime introspection API，后面再一点点长成 orchestration dependency。也就是说，当前最大风险不是“现在已经偏航”，而是“它长得已经有一点可被平台化复用的样子”。这需要源码和响应 shape 再卡一道。

**4. 我没有看到明显的 shadow state 迹象，但也还不能证明没有。**
包里明确把 review question 设成“Does it preserve runtime-owned truth rather than introducing shadow state?”，这说明你们自己也抓住了关键点。问题是，这次材料没有直接展示 `ike_v0.py` 和 `task_lifecycle.py` 的实现，所以我只能根据 intent 推断“设计上想避免 shadow state”，但不能确认实现层有没有：

* 额外拼装一份 lifecycle mirror
* 在 route 层缓存/重写 lease
* 把 derived work context 固化成准持久对象
* 对 events 做了脱离 canonical runtime 的二次整理
  所以这项我给“方向正确，证据不足”。

**5. 验证覆盖对“证明这条 proof route 存在且可通”是够的，对“证明没有长期结构性漂移”还不够。**
包里给出的验证结果说明：这条 route 能跑通、helper/test/router compile 都过了、本地 live proof 也成功了。这个证明了“它不是纸面设计”。但它还没证明几个更关键的问题：连续调用是否完全无状态；失败路径是否也保持 inspect-only；响应字段是否会被误当作 durable contract；derived work context 是否只来源于 runtime truth 而不是临时拼接真相。

## validation_gaps

**1. 没有源码级 review 证据。**
这次包只列出了 primary file、supporting helper、tests 的路径，没有把源码内容放进包里。我没法直接验证：

* route handler 是否只调用已有 bounded helper
* 是否存在写库、写缓存、写状态副作用
* `derived_work_context` 是引用型、派生型，还是意外变成对象型
* `lease/events` 是否原样来自 canonical runtime，还是 route 层重建了一份影子结构。

**2. 没看到失败路径和异常路径的 contract。**
目前 live proof 只给了 happy path：`200 OK`、`final_status = done`、integrity valid/auditable。没有看到 integrity invalid、lease 缺失、transition 异常、helper 抛错时，接口是否依旧坚持 inspect-only 语义，还是会泄漏出半成品 orchestration hints。

**3. 没看到对“不可持久化”的实现级断言。**
文档里写了 `persists_runtime_state = false`，但没有看到测试是否真正断言“调用前后 runtime persistent state 完全不变”。现在更像语义声明，还不是强约束证明。

**4. 没看到对 response shape 演进边界的冻结。**
因为这条 route 已经暴露 transitions / events / lease / derived work context，如果后续没有 contract discipline，很容易被下游当成事实标准接口。包里没有看到“这个 shape 是 provisional / unstable / inspect-only”的更强技术防护，比如字段命名、版本标记、或专门的 audit namespace。

**5. warnings 未解释。**
验证跑出了 `28 warnings`，虽然测试都过了，但 review pack 没说明这些 warning 是无关噪音、旧债，还是和 runtime/task lifecycle 相关。对于 proof route，这一点最好交代。

## known_risks

**1. inspect route 被“事实平台化”。**
最现实的风险不是它今天已经变成 general runner，而是外部一旦开始依赖这条 route 读取 lease/events/work-context，它就会在事实层面演化成 runtime introspection API。到那时，即使文档还写着 inspect-only，工程现实也会把它推向平台面。

**2. derived work context 漂移成第二真相源。**
这是我最警惕的一点。IKE 主线一直不能接受 WorkContext 成为第二真相。如果这里的 `derived work context` 不是严格的、短生命周期的、明确标注为派生视图，而是逐渐被外部拿去当“当前任务真实状态”，那就会开始侵蚀 runtime-owned truth。

**3. lease / events 暴露过深。**
如果 response 把内部 lease/event 结构完整暴露，下游很容易反向绑定内部实现细节。短期看方便 review，长期看会抬高以后收窄或重构的成本。

**4. “proof helper lifted to router” 以后继续加口子。**
现在这一步窄是窄的，但它天然很容易诱发下一步：再加 accept、replay、resume、query、filter。这个坡一旦滑下去，就会从“proof infrastructure”逐渐变成“轻量 orchestration surface”。

## recommendation

我的建议是：

**结论：可以继续，但按“conditional pass”处理，不按“fully approved feature surface”处理。**

具体我建议你加 5 个 guardrails，再往下走：

**第一，强制把这条 route 定位为 proof/audit namespace，而不是 runtime namespace 的通用能力。**
现在路径里已经有 `proof/inspect`，这是好事。后面不要再顺手长出 sibling 的 accept/update/run 类接口。

**第二，给 `derived_work_context` 加更强的“派生且非真相”标识。**
不仅文档说，还要在字段命名或 envelope 上体现它是 derived / provisional / inspect-view，避免被误当 canonical state。

**第三，补一组“无副作用证明”测试。**
不是只测返回值，而是测调用前后 persistent runtime state 没变。
这是 `persists_runtime_state = false` 最该有的硬证据。

**第四，补失败路径 contract 测试。**
至少要覆盖 helper fail、integrity invalid、lease absent、event anomaly 时，接口仍保持 inspect-only，不产生 acceptance/orchestration 语义。

**第五，限制响应深度。**
lease/events/work-context 只暴露 review 所需最小字段，不要把内部结构一次性端出来。proof 面越像“最小审计视图”，越不容易长歪。

所以我的总评是：

**这一步基本没有偏离主线，且方向上是健康的；但要把它当作“proof infrastructure 的窄提升”，而不是“runtime introspection 面的雏形”。当前建议继续推进，但必须补源码级无副作用证明和防平台化 guardrails。** 

如果你愿意，我下一轮可以按你历次 IKE review 的口径，直接给你出一个更像正式审查记录的版本：
**“通过 / 不通过 / 必改项 / 可改项 / 主线偏离判断”**。

# gemini
**IKE Sentinel (治理代理) 已激活。**

执行上下文：`IKE_RUNTIME_V0_R2-I1_SINGLE_FILE_REVIEW_PACK_2026-04-10.md`
审查标准：`IKE_SENTINEL_PROTOCOL.md` (方向对齐、方法验证、真实性)

以下是针对 `R2-I1` (Live Lifecycle Proof Route) 的官方审计报告，严格按照要求的格式输出：

### 1. Summary
**判定：通过 (Accept)**。
R2-I1 封包展现了极其优秀的工程克制力。它直接响应了哨兵在 04-08 审查中提出的“强制性独立闭环测试”要求。通过构建一个专门的 `/proof/inspect` 路由，系统能够在真实的 API 边界上自证其状态机流转（Task Lifecycle）的连贯性，而没有过早地暴露泛用的 CRUD 接口。这种“只读探针（Probe）”模式完美契合了内核硬化阶段的需求。

### 2. Findings (针对架构师的 Review Questions)
* **边界控制 (Narrowness):** 极佳。返回体中硬编码的 `inspect_only = true` 和 `implies_general_task_runner = false` 是非常强的防御性声明（Defensive Declaration），从语义上彻底封死了上层 UI 或其他 Delegate 滥用此路由进行业务调用的可能。
* **真理维护 (Truth Preservation):** 表现良好。直接暴露 `derived work context` 证明了系统可以通过下游组装还原上下文，而无需引入脱离 Postgres 的影子缓存层。
* **诚实度 (Honest Shape):** 极高。返回一个 `audit-shaped envelope`（包含 integrity, events, lease 等）如实地反映了底层的物理约束状态，而不是粉饰过的高级业务模型。
* **隐性蔓延 (Hidden Drift):** 目前未发现向通用编排器（Orchestrator）蔓延的迹象。它保持了“观察者”而非“调度者”的定位。
* **结构性问题 (Structural Issues):** 只要暴露的 `lease` 和 `event` 数据是直接从 Postgres 规范层读取（而非内存中的暂存态），就没有结构性问题。

### 3. Validation Gaps
* **负向路径验证缺失 (Missing Negative Path Proof):** 测试日志 (`54 passed`) 和 Live Proof (`final_status = done`) 表明“快乐路径（Happy Path）”已打通。但这不能证明底层防线坚固。这个 Proof 路由是否能够主动触发并捕获状态机的**非法越权操作**（例如：Delegate 试图跳过 `review_pending` 直接 `done`）并返回 `integrity.valid = false`？如果没有，这个 Proof 仅仅证明了“系统可以正常工作”，而没有证明“系统不能被破坏”。
* **测试数据污染 (Data Pollution):** 文档中未明确此 Live Proof 是在独立的测试事务（执行后 rollback）中运行，还是会将测试任务实际写入持久化 DB。如果写入，这会污染规范的真理层。

### 4. Known Risks
* **永久性脚手架陷阱 (The Permanent Scaffold Trap):** 这种带有探测性质的 `/proof/inspect` 路由极易在未来被遗忘在代码库中。如果带入生产环境，可能会被未经授权的客户端作为窥探系统底层状态（Events, Leases）的后门。
* **虚假的安全感 (Illusion of Safety):** 虽然此路由证明了 Helper 的可用性，但在 `R0-B` 阶段遗留的根本性问题——“`allow_claim` 依然由调用方断言而非 DB 约束”——可能依然存在。上层路由的测试全绿，不代表底层 DB 约束已硬化。

### 5. Recommendation
**建议操作：准予合并 (Accept & Merge)。**

此封包是一次安全且有价值的集成测试突破。在合并后，请执行以下后续动作：

1.  **添加环境屏障 (Environment Barrier):** 确保 `POST /api/ike/v0/runtime/task-lifecycle/proof/inspect` 路由受到严格的环境变量保护（例如仅在 `ENV=test` 或 `ENV=development` 时挂载），禁止其流入生产主线。
2.  **强化完整性审计 (Integrity Audit Expansion):** 在 Helper (`task_lifecycle.py`) 中，增加强制引发非法状态转移的测试步骤，确保返回的 `integrity.valid` 会真实地根据 Postgres 的拒绝操作而变为 `false`。
3.  **继续 R2-A 核心任务:** 此封包解决了“无人工干预的生命周期验证”要求。下一步，请勿忘记执行 04-08 哨兵报告中的另一个核心要求：**建立视图级信任隔离 (View-Level Trust Isolation)**。
