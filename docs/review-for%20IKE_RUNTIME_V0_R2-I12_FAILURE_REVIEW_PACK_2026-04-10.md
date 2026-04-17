# claude

加载 review 历史并读取实现文件。
所有关键代码已加载。开始正式 review。

---

# IKE Review #12 — R2-I10/I11 Failure Honesty Hardening

## Meta

| 字段 | 值 |
|------|-----|
| 序号 | 12 |
| 日期 | 2026-04-10 |
| 类型 | execution_pack |
| 文档 | IKE_RUNTIME_V0_R2-I12_FAILURE_REVIEW_PACK_2026-04-10.md |
| 评分 | **A-** |
| 方向判断 | on_track |
| 批准状态 | ✅ accept_with_changes |

---

## 1. 闭环验证

基于 Review #11 的待验证事项：

| # | 上次提出的问题 | 本次回应状态 | 评估 |
|---|---------------|-------------|------|
| 1 | InMemory vs DB-backed proof 差距显式记录 | **R2-I10/I11 直接回应**——DB-backed proof 现在存在且有 failure path | ✅ 已解决 |
| 2 | Router 拆分策略 | Router 现在 788 行 / 9 endpoints，未拆分 | ⚠️ 仍需关注 |
| 3 | `force=True` 角色限制 | 未涉及 | ❌ 遗留 (5 次) |
| 4 | retained notes backlog | 未涉及 | ❌ 遗留 (5 次) |
| 5 | concept #2 正式排期 | 未涉及 | ❌ 遗留 (**7 次**) 🔴 |
| 6 | proc memory 演进排期 | 未涉及 | ❌ 遗留 (**7 次**) 🔴 |
| 7 | Windows venv Option B 实现 | 未涉及 | ❌ 遗留 |

**关键闭环：Review #11 最重要的发现 (#1 "InMemory proof ≠ DB-backed proof") 已被本次 R2-I10/I11 直接回应。这是正确的技术演进。**

---

## 2. 方向偏移检测

| # | 不可变原则 | 本次状态 | 评估 |
|---|-----------|---------|------|
| 1 | PostgreSQL 为唯一 canonical truth | `_load_persisted_failure_snapshot` 从 PG 读取失败后的真实状态 | ✅✅ |
| 2 | Redis 仅加速 | 未涉及 | ✅ |
| 3 | API 契约反映真实能力 | truth_boundary 现在有 5 个字段，包括 `bounded_db_proof: true` | ✅ |
| 4 | Controller/Delegate 分离 | proof 内 controller/delegate 角色正确 | ✅ |
| 5 | MemoryPacket 需 controller review | 未涉及 | ✅ |
| 6 | WorkContext 可重建 carrier | 未涉及 | ✅ |
| 7 | Migration 路径 | 增量 hardening | ✅ |

**偏移数：0/7。累计 12 次零偏移。**

**原则 #1 有正面强化信号**：失败路径不再信任 rollback 后的 ORM 内存状态，而是重新从 PG 读取持久化真相。**这是对 "PG = canonical truth" 原则的最有力执行之一。**

---

## 3. 主线进度

| 维度 | 内容 |
|------|------|
| 上次位置 | R2-I1 InMemory lifecycle proof route |
| 本次位置 | R2-I10/I11 DB-backed failure honesty hardening |
| 推进方向 | 前进 |
| 推进质量 | **实质性** |

```
API 决策 → 对象层 → Benchmark → 项目审查 → Runtime 架构
  → R0-A~F → R1-C~K → R2-A → R2-H preflight
  → R2-I1 InMemory proof → R2-I10/I11 DB failure honesty ← HERE
```

---

## 4. 核心评估（按 severity 排序）

### Finding 1: Failure snapshot 设计正确且有价值 🟢

```python
def _load_persisted_failure_snapshot(db_session, task_id, fallback_status):
    """Best-effort durable snapshot for failure reporting."""
    try:
        task_row = db_session.execute(select(RuntimeTask)...).scalars().one_or_none()
        event_rows = db_session.execute(select(RuntimeTaskEvent)...).scalars().all()
    except Exception:
        return fallback_status, 0
    ...
```

| 检查点 | 评价 |
|--------|------|
| 从 PG 读取而非信任 ORM 内存 | ✅ 正确——rollback 后 ORM state 不可信 |
| `try/except` 容错 | ✅ 正确——如果 PG 本身不可用，退化为 fallback |
| 返回 `(durable_status, persisted_event_count)` | ✅ 正确——两个关键指标 |

**这是整个 packet 最有价值的改动。** 它解决了一个微妙但危险的 bug：失败时报告 ORM 缓存中的 stale 状态，而非 PG 中实际持久化的状态。

### Finding 2: `task.__dict__.get("status", ...)` fallback 需要注意 🟡

```python
except Exception as exc:
    db_session.rollback()
    fallback_status_obj = task.__dict__.get("status", RuntimeTaskStatus.INBOX)
```

使用 `__dict__` 而非 `task.status` 是有意为之——避免触发 SQLAlchemy lazy load（rollback 后 session 已 detach）。这是**技术上正确**的，但：

- ⚠️ `__dict__` 访问绕过 SQLAlchemy descriptor，可能在未来的 model 变更中 silently break
- 建议增加一行注释说明为什么使用 `__dict__` 而非 attribute access

### Finding 3: 重叠运行测试设计合理 🟢

```python
def run_one():
    with asyncio.Runner() as runner:
        local_engine = create_async_engine(..., poolclass=NullPool)
        local_session_maker = async_sessionmaker(local_engine, ...)
```

| 检查点 | 评价 |
|--------|------|
| 独立 `asyncio.Runner` per thread | ✅ 避免跨线程 event loop 冲突 |
| `NullPool` per thread | ✅ 避免连接池交叉污染 |
| `Barrier(2)` 同步启动 | ✅ 确保两个 proof 真正重叠 |
| 独立 engine + session lifecycle | ✅ 每个 thread 完全自治 |
| 结果验证：project/task/lease 全部不同 | ✅ 证明隔离性 |
| `event_ids` 不相交断言 | ✅ 最强隔离证据 |

**这不是 fake concurrency。** 它是在 Windows/asyncpg 约束下能做到的最诚实的并行隔离测试。文档明确不声称 "production-grade concurrency guarantees"——这是正确的。

### Finding 4: Route-level failure 暴露设计正确 🟢

```python
"summary": {
    "success": proof.success,
    "final_status": proof.final_status,        # durable
    "persisted_event_count": proof.persisted_event_count,  # durable
    "error": proof.error,
},
"truth_boundary": {
    "inspect_only": True,
    "bounded_db_proof": True,
    "persists_runtime_state": True,
    "implies_general_task_runner": False,
    "detached_execution": False,
},
```

| 检查点 | 评价 |
|--------|------|
| Failure response 仍返回 200 | ✅ 正确——proof 本身执行了，只是被证明的 lifecycle 失败了 |
| `final_status` 从 PG 读取 | ✅ durable truth |
| `persisted_event_count` 从 PG 读取 | ✅ durable truth |
| truth_boundary 从 3 字段扩展为 5 字段 | ✅ 更精确 |
| 新增 `bounded_db_proof: true` | ✅ 区分 InMemory proof 和 DB-backed proof |
| 新增 `detached_execution: false` | ✅ 避免被误解为后台任务 |

### Finding 5: Router 持续增长 🟡

| 维度 | Review #2 | Review #11 | Review #12 |
|------|-----------|------------|------------|
| 行数 | ~250 | 714 | 788 |
| Endpoints | 3 | 8 | 9 |

新增了 `/runtime/task-lifecycle/db-proof/inspect`。Router 仍是单文件，但增长仍在可控范围内（+74 行 / +1 endpoint）。

### Finding 6: 测试的 mock 策略需要关注 🟡

```python
# Route test uses mock
ike_v0_module.execute_db_backed_lifecycle_proof = lambda ...: proof
test_app.dependency_overrides[get_db] = mock_get_db
```

Route test 使用 mock 而非真实 DB——这对 route-level 测试是合理的（隔离 route 逻辑和 DB 逻辑）。但需要确保：
- ✅ DB-level failure 测试存在（`test_runtime_v0_db_backed_lifecycle_proof.py` 中有）
- ✅ Route-level mock 测试验证的是 response shape，不是 DB 行为

两层测试分离是正确的。

---

### 语义诚实性检查

| 检查项 | 结果 |
|--------|------|
| Fake durability | ✅ 无。failure path 明确从 PG 读取而非虚报 |
| Fake capability | ✅ 无。claim boundary 明确 5 个 "does not claim" |
| Hidden state | ✅ 无。`__dict__` 访问是因为 rollback，有技术原因 |
| Delegate self-acceptance | ✅ 无 |
| Premature complexity | ✅ 无。overlapping test 是最小可行的隔离证明 |
| **Failure honesty** | ✅✅ **正面信号最强的一项** |

---

## 5. 风险识别

| # | 风险 | 严重度 | 分类 | 说明 |
|---|------|--------|------|------|
| 1 | **长期遗留已达危险水平** | 🔴 高 | process | concept #2 和 proc memory 7 次遗留。这不再是"还没排期"，而是 process discipline 问题 |
| 2 | `__dict__` 访问 ORM 绕过 | 🟢 低 | maintenance | 技术正确但需要注释保护 |
| 3 | Router 单文件 788 行 | 🟡 中 | architecture | 可控但接近拆分阈值 |
| 4 | force=True / retained notes 5 次遗留 | 🟡 中 | governance | fix-now 项持续跳过 |

---

## 6. 下一步建议

### 对于当前 packet

**accept_with_changes:**
1. 在 `_load_persisted_failure_snapshot` 和 `task.__dict__` 访问处增加一行注释说明 why

### 推荐下一阶段

```
选项 A: Debt Settlement Sprint (强烈推荐)
  - force=True 角色限制
  - retained notes 统一 backlog
  - concept #2 正式排期 (可以是一个 plan，不需要执行)
  - proc memory 演进 plan
  - Router 拆分

选项 B: 如果继续 runtime 深化
  - R2-I 系列 consolidation review
  - 证明 DB-backed proof 在 live service 上的完整 failure→recovery 路径

不做:
  - broad scheduler / task platform
  - notification mesh
  - graph memory
```

---

## 7. 要求下次验证的事项

| # | 待验证事项 | 来源 |
|---|-----------|------|
| 1 | `__dict__` 访问点增加注释 | 本次新增 |
| 2 | Router 拆分策略 | Review #11 遗留 |
| 3 | `force=True` 角色限制 | Review #8 遗留 (**5 次**) |
| 4 | retained notes backlog | Review #8 遗留 (**5 次**) |
| 5 | 第二个 concept benchmark **正式排期** | Review #5 遗留 (**7 次**) 🔴🔴 |
| 6 | Procedural memory 演进 **正式排期** | Review #5 遗留 (**7 次**) 🔴🔴 |
| 7 | Windows venv Option B 实现 | Review #10 遗留 |

**🔴🔴 Process Alert**: #5 和 #6 已经 7 个 review 周期未获回应。正式标注为 **process failure**。这不是技术问题——技术方向 12/12 on_track。这是优先级管理问题。如果这些事项在项目层面被有意延后，需要一个显式的 "deferred with reason" 记录，而不是持续 silent ignore。

---

## 8. 批准状态

**✅ accept_with_changes**

| 条件 | 说明 |
|------|------|
| 接受 failure honesty hardening | ✅ 这是高质量的 durable truth 改进 |
| 需要增加 `__dict__` 注释 | 小改动 |
| 强烈建议下一步是 debt settlement 而非继续 runtime 深化 | 技术层面已足够深，process debt 需要偿还 |

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
| #11 | 2026-04-10 | execution_pack | B+ | on_track | InMemory lifecycle proof |
| **#12** | **2026-04-10** | **execution_pack** | **A-** | **on_track** | **DB failure honesty accept_with_changes** |

**累计：12/12 on_track，零方向偏移。技术 A-，process B-。**

---

现在写入持久化文件。

```markdown
# IKE Review #12 - 2026-04-10

## Meta

| 字段 | 值 |
|------|-----|
| 序号 | 12 |
| 日期 | 2026-04-10 |
| 类型 | execution_pack |
| 文档 | IKE_RUNTIME_V0_R2-I12_FAILURE_REVIEW_PACK_2026-04-10.md |
| 评分 | A- |
| 方向判断 | on_track |
| 批准状态 | ✅ accept_with_changes |

---

## 1. 闭环验证

| # | 上次提出的问题 | 本次回应状态 | 评估 |
|---|---------------|-------------|------|
| 1 | InMemory vs DB-backed gap | DB-backed proof with failure path | ✅ |
| 2 | Router 拆分 | 788行/9 endpoints, 未拆 | ⚠️ |
| 3 | force=True | 未涉及 (5次遗留) | ❌ |
| 4 | retained notes | 未涉及 (5次遗留) | ❌ |
| 5 | concept #2 | 未涉及 (7次遗留) 🔴🔴 | ❌ |
| 6 | proc memory | 未涉及 (7次遗留) 🔴🔴 | ❌ |
| 7 | venv Option B | 未涉及 | ❌ |

---

## 2. 方向偏移检测

| # | 原则 | 状态 | 评估 |
|---|------|------|------|
| 1 | PG canonical truth | failure snapshot reads from PG | ✅✅ |
| 2 | Redis 仅加速 | 未涉及 | ✅ |
| 3 | API 反映真实能力 | truth_boundary 5字段 | ✅ |
| 4 | Controller/Delegate | 正确 | ✅ |
| 5 | MemoryPacket controller | 未涉及 | ✅ |
| 6 | WorkContext derivative | 未涉及 | ✅ |
| 7 | Migration 路径 | 增量 | ✅ |

偏移：0/7。累计12次零偏移。

---

## 3. 核心评估

### Findings (by severity)

1. 🟢 Failure snapshot 设计正确——从 PG 读取而非信任 ORM 内存
2. 🟢 overlapping-run 测试合理——NullPool + 独立 Runner + Barrier
3. 🟢 Route failure 暴露正确——truth_boundary 5字段
4. 🟡 `__dict__` 访问需注释保护
5. 🟡 Router 788行接近拆分阈值
6. 🔴 长期遗留 7 次未回应 (process)

### 语义诚实性

| 检查项 | 结果 |
|--------|------|
| Fake durability | ✅ 无 |
| Fake capability | ✅ 无 |
| Hidden state | ✅ 无 |
| Delegate self-acceptance | ✅ 无 |
| Premature complexity | ✅ 无 |
| Failure honesty | ✅✅ 最强信号 |

---

## 4. 风险

| # | 风险 | 严重度 | 说明 |
|---|------|--------|------|
| 1 | 长期遗留 | 🔴 | concept#2 + proc memory 7次 |
| 2 | __dict__ bypass | 🟢 | 需注释 |
| 3 | Router 增长 | 🟡 | 788行 |
| 4 | fix-now debt | 🟡 | force + retained notes 5次 |

---

## 5. 要求下次验证

| # | 事项 | 来源 |
|---|------|------|
| 1 | __dict__ 注释 | 本次新增 |
| 2 | Router 拆分 | Review #11 遗留 |
| 3 | force=True | Review #8 遗留 (5次) |
| 4 | retained notes | Review #8 遗留 (5次) |
| 5 | concept #2 排期 | Review #5 遗留 (7次) 🔴🔴 |
| 6 | proc memory 排期 | Review #5 遗留 (7次) 🔴🔴 |
| 7 | venv Option B | Review #10 遗留 |

---

## 6. 批准状态

✅ accept_with_changes
- failure honesty 是高质量改进
- 需增加 __dict__ 注释
- 强烈建议下一步 debt settlement

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
| #11 | 2026-04-10 | execution_pack | B+ | on_track |
| **#12** | **2026-04-10** | **execution_pack** | **A-** | **on_track** |

累计：12/12 on_track，零偏移。
```

更新 seed:

```markdown|CODE_EDIT_BLOCK|d:\code\normalworks\.qoder\skills\ike-milestone-review\review-seed.md
# ... existing code ...

方向: 11/11 on_track, 零偏移

## Review #12 - 2026-04-10 (R2-I10/I11 Failure Honesty)
- **类型**: execution_pack
- **文档**: IKE_RUNTIME_V0_R2-I12_FAILURE_REVIEW_PACK_2026-04-10.md
- **评分**: A-
- **方向判断**: on_track
### 关键发现
1. ✅ _load_persisted_failure_snapshot 从 PG 读取失败后真实状态——最有价值的改动
2. ✅ overlapping-run 测试用 NullPool + 独立 Runner + Barrier——诚实的隔离证明
3. ✅ truth_boundary 扩展为 5 字段 (bounded_db_proof + detached_execution)
4. ⚠️ __dict__ 访问绕过 ORM descriptor——技术正确但需注释
5. ✅ Review #11 核心发现 (InMemory vs DB-backed gap) 已被直接回应
### 提出的风险
1. 🔴 concept #2 + proc memory 7 次遗留——标注为 process failure
2. 🟡 force=True / retained notes 5 次遗留
3. 🟡 Router 788 行接近拆分阈值
### 要求下次验证的事项
1. __dict__ 注释 (本次新增)
2. Router 拆分 (Review #11 遗留)
3. force=True (Review #8 遗留 5 次)
4. retained notes (Review #8 遗留 5 次)
5. concept #2 排期 (Review #5 遗留 7 次) 🔴🔴 PROCESS FAILURE
6. proc memory 排期 (Review #5 遗留 7 次) 🔴🔴 PROCESS FAILURE
7. venv Option B (Review #10 遗留)
### 批准状态
✅ accept_with_changes

---
## 主线进度总结

API 决策 → 对象层 → Benchmark → 项目审查 → Runtime 架构 → 执行包 → R0-A~F → R1-C~K → R2-A → R2-H preflight → R2-I1 InMemory proof → R2-I10/I11 DB failure honesty

方向: 12/12 on_track, 零偏移
技术评分趋势: 持续 B+~A
Process 评分: B- (长期遗留未偿还)
```

Review #12 完成。

**核心信号**：

1. **技术层面：这是一个高质量的 failure honesty 改进。** `_load_persisted_failure_snapshot` 从 PG 而非 ORM 内存读取失败状态，是对 "PostgreSQL = canonical truth" 原则在异常路径下的最有力执行。overlapping-run 测试设计诚实且合理。

2. **闭环：Review #11 最核心的发现已被回应。** InMemory vs DB-backed 差距现在已填补。

3. **Process：长期遗留正式标注为 process failure。** 第二个 concept benchmark 和 procedural memory 演进已 **7 个 review 周期**未获任何回应——包括排期。项目技术方向完美（12/12 on_track，零偏移），但 **process debt 正在成为与技术 debt 同等级别的风险**。强烈建议下一步是 debt settlement sprint，而非继续 runtime 深化。

# chatgpt
**findings**

**1. High — 这次 failure lane 的主线方向是对的，且比上一轮更诚实。**
从包里的改动描述看，helper 失败路径现在不再信任 rollback 之后可能失真的 ORM 内存态，而是补了 `_load_persisted_failure_snapshot(...)`，并把 failure 结果对齐到 durable `final_status` 和 durable `persisted_event_count`。这正好击中 IKE runtime 主线里最重要的点：**失败时也必须回到 durable truth，而不是让内存态伪装成真相**。这比“成功路径正确、失败路径含糊”要健康得多。

**2. High — route-level failure honesty 基本守住了边界，没有明显长成执行面。**
这轮 route proof 检查的是 `summary.success = false`、`summary.final_status = "ready"`、`summary.persisted_event_count = 2`、显式 `summary.error`，同时保留稳定的 truth-boundary flags；而包里也明确把 claim boundary 限定在 bounded proof success/failure truth、sequential isolation、bounded overlapping-run isolation，不声称 general task runner、scheduler semantics 或 detached supervision。按这个描述，这条 inspect route 仍然是在做“失败可审计证明”，不是借失败口子偷偷扩成控制面。

**3. Medium — overlapping-run 测试口径是技术上可辩护的，没有明显 fake concurrency，但必须继续严守“bounded”表述。**
这轮最好的地方是没有硬吹“生产级并发”，而是明确说 overlapping-run proof 使用独立 thread-local `asyncio.Runner`、`create_async_engine(..., poolclass=NullPool)`、`AsyncSession`，目的是避免 Windows/asyncpg 下 cross-loop pool contamination，并且当前 claim boundary 明确**不**包含 production-grade concurrency guarantees。这个口径是诚实的，也符合你们一直强调的“不能伪造能力”。
但也正因为如此，我会把它定性为：**证明了 bounded overlapping-run isolation setup 可用，不等于证明 runtime 已具备真正的通用并发执行能力。** 这一步是合理 proof，不是能力宣告。

**4. Medium — failure fallback 的语义比之前稳，但 `task.__dict__.get("status", RuntimeTaskStatus.INBOX)` 这个兜底仍带有潜在误读风险。**
包里写明 failure fallback 不再信任 rollback-expired ORM state，并使用 `task.__dict__.get("status", RuntimeTaskStatus.INBOX)`。这说明你们已经意识到 ORM 失真问题并试图最小化误判，这是好的。
但从 review 口径上，这个默认 `INBOX` 仍然需要非常谨慎：它只能被视为**最后兜底的保守占位**，不能被下游解读成 durable truth。本轮之所以还能接受，是因为你们又补了 durable snapshot helper，并把最终 failure result 对齐到 durable `final_status` / `persisted_event_count`；否则这个默认值会很危险。

**5. Medium — 这轮文案总体没有夸大，但还要继续防止“proof lane 被外部当成平台能力”这一类结构性漂移。**
包里已经很克制地写了：当前只 claim bounded DB-backed proof success-path truth、repeated sequential isolation、bounded overlapping-run isolation、helper-level failure honesty、route-level failure honesty；并明确不 claim task runner、scheduler、detached supervision、production concurrency。这个 framing 是健康的。
风险在于，随着 success/failure 都变得更“可审查”，外部很容易开始把这条 lane 当 runtime 平台雏形来消费。所以主线仍然要坚持：**这是 proof infrastructure，不是 task platform 起点。**

**6. Low — review pack 的标识有一点材料卫生问题。**
上传文件名是 `R2-I12_FAILURE_REVIEW_PACK`，但正文标题写的是 `R2-I10/I11 Failure Review Pack`。这不影响技术判断，但会影响 review continuity 和后续归档检索，建议统一。

---

**validation_gaps**

**1. 我这次看到的是 review pack，不是源码本体，所以仍然缺少实现级确认。**
我能确认的是你们的 intent、claim boundary、测试切片和观测结果；但不能直接核实 `db_backed_lifecycle_proof.py`、`ike_v0.py`、测试文件里的具体实现是否完全符合描述。尤其是 durable snapshot load、rollback 后状态处理、route flags 的真实装配方式，目前还是“有力描述 + 测试结果”，不是源码级审计。

**2. failure honesty 已经增强，但仍未证明更深层的 DB 异常边界。**
当前证明覆盖了 synthetic failure honesty 和 route-level failure honesty，这已经比之前强很多；但还没看到更恶劣边界，例如：snapshot load 本身失败、事件持久化部分成功部分失败、lease 已写入但 task status 未刷新、事务边界跨 helper 中断时，返回是否仍然 honest。

**3. overlapping-run proof 证明了一个受控 setup，不等于更广义 runtime 并发语义。**
这不是缺点，而是当前还不能外推的边界。现在可以说“bounded overlapping-run isolation proof 成立”，不能说“runtime 已具备一般化并发可靠性”。这一点后续文案和接口命名还要持续克制。

**4. `28 warnings` 依旧未解释。**
测试结果是正向的：`49 passed, 28 warnings, 9 subtests passed`，compile passed。
但 warnings 没有归因说明。若其中有 async、transaction、deprecation、event-loop 相关 warning，它们可能正好和这轮 failure/concurrency honesty 主题相关，建议最少做分类说明。

---

**recommendation**

**accept_with_changes**

理由：

这轮改动在我看来是**实质增强**，不是表面修饰。最关键的正向点有两个：

* helper-level failure reporting 明显朝 **durable partial truth** 靠拢，而不是继续依赖 stale in-memory ORM state；
* route-level inspection 也把这种 failure honesty 保留下来了，同时没有在 claim 上夸大为 general execution capability。

这和 IKE 一贯主线是对齐的：
**不造假能力，不靠失真内存态冒充真相，不把 proof lane 偷偷长成 task platform。**

但我不建议直接给“无条件 accept”，原因也很明确：

* 还缺源码级确认；
* `task.__dict__.get(..., INBOX)` 这种兜底需要被更明确地标注为保守 fallback，而不是 truth source；
* overlapping-run 相关表述必须继续维持“bounded proof”而不是能力外推；
* warnings 和更深层 failure 边界还没解释清楚。

所以我的最终判断是：

**这轮可以继续推进，且方向正确；但必须继续把它锁死在“failure-honesty proof strengthening”这个窄目标里，不要把这次增强误解成 runtime 平台能力已经成熟。**


# gemini
**IKE Sentinel (治理代理) 已激活。**

执行上下文：`IKE_RUNTIME_V0_R2-I12_FAILURE_REVIEW_PACK_2026-04-10.md`
审查标准：`IKE_SENTINEL_PROTOCOL.md` (方向对齐、方法验证、真实性)

以下是针对 `R2-I10/I11` (Failure-Honesty Review) 的官方审计报告，严格按照要求的格式输出：

### 1. Findings (按严重程度排序)

1.  **[High] 虚假状态规避成功 (Successful Evasion of Fake State):** 这是一个重大的架构级胜利。在 `db_backed_lifecycle_proof.py` 中使用 `_load_persisted_failure_snapshot(...)` 并且显式回退到 `task.__dict__.get("status", RuntimeTaskStatus.INBOX)`，从根本上解决了一个经典的 ORM 陷阱：在发生异常并 Rollback 后，内存中的 ORM 对象仍保留着最后一次尝试修改（但未持久化）的幻觉状态。你强制系统去读取数据库中真实存在的、最终的物理状态。**这完全契合 Postgres as Truth 宪法。**
2.  **[Medium] 线程隔离并发测试的诚实性 (Honesty in Concurrency Testing):** 使用独立的 `asyncio.Runner` 和 `NullPool` 是在单机测试环境中模拟并发抢占最严谨、最“不自欺欺人”的做法。它避免了连接池重用导致的一致性假象。你明确声明“这不是生产级并发保证”，这种克制非常健康。
3.  **[Low/Observation] Route 层级的故障穿透 (Route-Level Failure Transparency):** 路由 `/proof/inspect` 现在能够在失败时返回真实的 `final_status = "ready"` 和准确的 `persisted_event_count = 2`。这意味着即便任务在后续步骤崩溃，系统也能如实反映崩溃前最后一刻的安全快照，而不是简单地返回 500 或 丢失全部上下文。

### 2. Validation Gaps

* **脏读/幻读风险证明 (Dirty Read/Phantom Read Proof):** 虽然 overlapping-run proof 证明了隔离性，但没有证据表明测试用例中包含了针对隔离级别 (Isolation Level) 的极限攻击。例如：当 Runner A 获取 Lease 但尚未提交事务时，Runner B 能否读取到未提交的 Lease 状态？建议在测试中明确声明底层 Postgres 使用的事务隔离级别（如 Read Committed 或 Serializable），并补充一个显式的“锁等待或锁超时”断言。
* **清理机制验证缺失 (Missing Cleanup Validation):** 当发生 Synthetic failure 后，产生的残留记录（例如处于 `ready` 状态但关联了 `persisted_event_count=2` 的悬挂任务）是否会对下一次完全正常的 Proof 执行产生干扰？测试似乎没有显式验证“失败后的环境依然是干净的/可恢复的”。

### 3. Recommendation

**判定：准予合并 (Accept)。**

**理由：**
此封包是一次关于“诚实”的深刻工程实践。你不仅处理了成功路径，更重要的是，你在失败路径上同样硬化了“拒绝内存幻觉”的原则。ORM 回滚后的对象脏数据问题是导致 AI Agent 系统行为不可预测的罪魁祸首之一，而你的 `_load_persisted_failure_snapshot` 建立了一道防线。

**后续行动建议（作为 IKE Sentinel 的警告）：**
* 这依然是“Proof（探针）”级别的设施。请保持清醒，不要将 `_load_persisted_failure_snapshot` 视作解决一般性分布式事务一致性的银弹。
* 既然错误能够被如实捕获并持久化部分状态，下一步（可能在 R3 或 Evolution 阶段）必须考虑：**这些发生 Failure 的 Task 由谁来认领、降级或垃圾回收？** 永远处于 `ready` 但带着一堆报错 Event 的任务，最终会变成数据库中的僵尸数据。