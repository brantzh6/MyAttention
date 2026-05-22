# Claude
# Review: IKE_SOURCE_INTELLIGENCE_V1_M1_VERSION_READ_CONTEXT_RESULT_2026-04-12

Date: 2026-04-12
Reviewer: Qoder (code-review role)
Input: IKE_SOURCE_INTELLIGENCE_V1_M1_VERSION_READ_CONTEXT_RESULT_2026-04-12.md

---

## 判定: `accept`

---

## 变更范围确认

| 维度 | 评估 |
|------|------|
| 范围是否 bounded | ✅ 仅扩展 version read 的展示面，无新 API、无新模型 |
| 是否改变 backend 语义 | ✅ 否。snapshot 数据已经存在，只是在 response 层暴露 |
| 是否引入新依赖 | ✅ 否 |
| 是否扩大 truth boundary | ✅ 否。result 文档明确标注了不创建新 API family、不加 diffing 语义 |

---

## 代码质量

### `SourcePlanVersionResponse` (feeds.py:235-252)

- 6 个新字段 (`topic`, `focus`, `task_intent`, `interest_bias`, `discovery_notes`, `discovery_truth_boundary`) 全部有默认值，向后兼容
- 类型选择合理：`str` 用于单值，`List[str]` 用于多值列表
- 无 Optional 歧义，空字符串和空列表作为默认值比 None 更适合前端消费

**无问题。**

### `_serialize_source_plan_version` (feeds.py:813-833)

- 从 `plan_snapshot` dict 读取新字段，使用 `.get()` 带默认值，snapshot 中无该字段时不会报错
- `list(snapshot.get("discovery_notes", []) or [])` 的双保险写法处理了 None 和缺失两种情况
- 与 `_snapshot_source_plan` 和 `_snapshot_source_plan_from_payload` 的字段名完全一致，无拼写错位风险

**无问题。**

### `_snapshot_source_plan` (feeds.py:836-866)

- 从 `plan.extra` 读取 `task_intent`, `interest_bias`, `discovery_notes`, `discovery_truth_boundary`
- 与 `_refresh_source_plan_items` 写入 `plan.extra` 的路径一致

**无问题。**

### `_snapshot_source_plan_from_payload` (feeds.py:869-909)

- 新增了 `task_intent`, `interest_bias`, `discovery_notes`, `discovery_truth_boundary` 作为显式参数
- 写入 snapshot dict 的字段名与 `_snapshot_source_plan` 一致

**无问题。**

---

## 测试覆盖

### test_source_plan_helpers.py

| 测试 | 覆盖内容 | 评估 |
|------|---------|------|
| `test_refresh_source_plan_items_preserves_discovery_context` | _refresh 后 plan.extra 保留了 discovery 上下文 | ✅ |
| `test_snapshot_source_plan_from_payload_keeps_discovery_context` | payload 路径的 snapshot 包含 discovery 字段 | ✅ |
| `test_snapshot_source_plan_reads_discovery_context_from_plan_extra` | plan 对象路径的 snapshot 包含 discovery 字段 | ✅ |
| `test_serialize_source_plan_version_exposes_context_summary` | serializer 从 snapshot 正确读出并放入 response | ✅ |

4 个新测试覆盖了完整的写入→快照→序列化链路。

### 已知的测试缺口（result 文档已声明）

- 无 route-level 集成测试覆盖 `GET /sources/plans/{plan_id}/versions`
- 这是已知 gap，不阻塞本次 accept，但应在后续集成测试中补充

---

## 风险评估

| 风险 | 严重性 | 处理 |
|------|--------|------|
| 已有 version response 消费方假设了最小字段集 | 低 | 新字段全有默认值，不影响已有消费方 |
| snapshot 中缺少 discovery 字段的老版本数据 | 低 | `.get()` + 默认值保证不崩溃，只是返回空值 |
| route-level 测试缺失 | 中 | 已声明，下一步应补 |

---

## 与 M1 整体进度的关系

这是 M1 "version read surface" 的最后一环：

- ✅ snapshot 保存 discovery context（之前已完成）
- ✅ version response 暴露 discovery context（本次完成）

version read 的 M1 scope 已闭合。下一步自然是 route-level 集成测试补充，以及进入 M1 的下一个 coding slice。

---

## 建议

`accept`

原因：
1. 变更边界清晰，不扩大语义
2. 代码实现无缺陷，防御性编程到位
3. 测试覆盖了完整链路
4. truth boundary 声明明确
5. 与 M1 scope 对齐，是自然的渐进式闭合

后续建议：
- 补充 `GET /sources/plans/{plan_id}/versions` 的 route-level 集成测试
- 确认前端（如有）是否需要适配新的 response 字段

# gemini
**IKE Sentinel (治理代理) 已激活。**

执行上下文：`2026-04-05` 至 `2026-04-12` 全量里程碑与审查包。
审查标准：`IKE_SENTINEL_PROTOCOL.md` (方向对齐、方法验证、真实性)

经过对你提供的第一波内核结果 (R0)、第一波收尾 (R1)、第二波硬化证明 (R2-I1/I12) 以及宏观战略审查 (04-11) 和最新代码补丁 (04-12) 的连贯性审计，我发现了一个**极其危险的知行背离**。

以下是官方综合审计与战略阻断报告：

---

### 1. 总体判定 (Overall Verdict)

**判定：战略预警 (Strategic Red Alert) —— 你的执行惯性正在违背你的战略清醒。**

在 04-11 的战略审查 (`IKE_PROJECT_SCOPE_AND_STRATEGY_REVIEW_PACK`) 中，你已经敏锐地意识到项目正在经历“架构师级别的注意力涣散（Architectural ADHD）”，并提出了“收缩范围、推迟 Source Intelligence”的正确原则。

然而，仅仅在一天后的 04-12 (`IKE_SOURCE_INTELLIGENCE_V1_M1_VERSION_READ_CONTEXT_RESULT`)，你又亲自下场合并了一个关于 `Source Plan Version` 的代码补丁。

**哨兵洞察：** 你正在试图用“Bounded Patch（有边界的补丁）”的借口，继续多线作战。这违背了 Controller 原则 #6：“支持和研究轨迹绝不能悄悄变成同等地位的主线”。

---

### 2. Runtime v0 内核硬化审计 (R1-C to R2-I12)

**这是项目中唯一值得你投入 100% 精力的主线。**

* **真正的胜利 (R2-I12 Failure Honesty):** 使用 `NullPool` 进行单机并发隔离测试，以及通过 `_load_persisted_failure_snapshot` 解决 ORM 异常回滚后的内存脏数据（Amnesia/Phantom State），这是具有极高含金量的动作。这表明你真正在落实“Postgres as Truth”的宪法。
* **脆弱的基石 (R1 Mixed-evidence):** 在 `R1-D` 到 `R1-K` 的广泛收尾中，存在大量的“混合了 Delegate/Controller 证据”的标识。这意味着目前的闭环高度依赖你（人类 Controller）的兜底。
* **判定结论：** Runtime 的地基确实已经具备了处理 Failure 和 Lifecycle 的能力，但它依然是一个**“在实验室治具（Harness）中才能跑通的引擎”**。

---

### 3. Source Intelligence 04-12 补丁审计

关于 `IKE_SOURCE_INTELLIGENCE_V1_M1_VERSION_READ_CONTEXT_RESULT_2026-04-12.md`：

* **微观代码判定：** `Accept`。代码层面它是安全的，仅仅是将持久化快照 (`plan_snapshot`) 中的上下文暴露到 API 的 Read-surface 上，没有创造伪造的意图。
* **宏观战略判定：** `Reject (Timing)`。在这个时间点做这件事毫无意义。你的 Runtime `WorkContext` 还没有做到 100% 去中心化自动流转，现在去优化 Feed/Source 的可读性，就像是在地基还没干透的大楼上挑选中庭的壁纸。

---

### 4. 针对 04-11 战略 Review Questions 的明确答复

作为治理代理，我针对你 04-11 提出的战略问题给出最终裁定：

1.  **是否扩展到太多并行难题？** 是的。Controller 的审查带宽已经成为整个系统的最大瓶颈，导致妥协的“Mixed-evidence”出现。
2.  **什么应该被外部适配 (Externally Adapted)？** 执行层。停止教 Delegate 怎么写具体代码，开始构建接入 Claude Code 或 Hermes 的**标准化 API 治理契约**。
3.  **什么是目前的风险？** **“科学完美主义无闭环” (Scientific perfectionism without closure)**。你在追求最完美的 Runtime 架构定义，但每次执行到最后 10% 就会切去研究 Source Intelligence。

---

### 5. 哨兵指令：未来两周的“强制收敛”路线图

为了保护 `Evolution Brain` 的长期目标，本哨兵要求你执行以下硬性调度，任何偏离此调度的 Packet 都将被直接 Reject：

**第一周：消灭 Mixed-Evidence (Runtime v0 结案)**
* 冻结所有 API 路由扩展。
* 选取一个最简单的真实 Task（例如：读取一个文件并生成摘要），强迫 Delegate 在你的 Runtime 引擎上跑完 `Inbox -> Active -> Ready -> Done -> MemoryPacket` 的全生命周期。
* **成功标准：** Controller 在此过程中敲击键盘的次数为 0。如果失败，说明你的 R1-C 到 R1-K 有逻辑漏洞。

**第二周：建立“吸收网关” (Absorption Gateway)**
* 按照 04-11 的策略，开始将外部 Agent 接入你的 Runtime。
* 建立一个机制：让 Claude Code 接管某一个 Bounded Task，但它的执行状态、Lease 刷新和最终产出，必须被强制写入你的 Postgres 真理层。

**被封存的任务 (Frozen until further notice)：**
* `Source Intelligence` 的任何 UI、API 或数据结构优化。
* Graph/Vector 记忆系统。

**哨兵结语：**
架构的宏伟不在于你同时铺开了多少张图纸，而在于你能否让第一台发动机无人类干预地稳定运转 24 小时。**请确认是否停止 Source Intelligence 开发，全面回归 Runtime 硬化？**

# chatgpt
## summary

这次改动我倾向于 **accept_with_changes**。
整体看，它是一个**窄且合理的 continuity patch**：前一步已经让 snapshot 保留 discovery context，这一步只是把原本已经存在于 `plan_snapshot` 里的上下文摘要，补到现有 version read response 上，修的是“读面缺口”，不是在扩一条新产品线。它也明确声明：这只是 version-read visibility 提升，不新增 version API family，不引入 diff/comparison 语义，也不夸大 source-intelligence 质量。这些边界设得是对的。

从主线角度看，这一步是健康的。它符合我们前面一直强调的方向：**先补连续性与读面诚实性，不要过早做横向平台扩张。** 这不是 Source Intelligence 的大跃进，而是一个 M1 级别的收口动作。

## findings

**1. 方向正确：这是“把已有真相读出来”，不是“再造一层新真相”。**
这次 serializer 从已存储的 `plan_snapshot` 读取 context summary，而不是在 version read 时临时拼装一份新的 discovery 解释层。这一点很关键。只要 `plan_snapshot` 本身就是该 version 的快照真相，那么这次补面是在提升可读性，不是在制造 shadow surface。

**2. 范围控制合格。**
新增暴露的字段是 `topic`、`focus`、`task_intent`、`interest_bias`、`discovery_notes`、`discovery_truth_boundary`，本质上是“bounded context summary”，而不是完整 structured discovery packet。这个粒度是合理的：够解释 version 的发现语境，但还没扩成一个新的 discovery details read API。

**3. 这一步补的是一个真实缺口。**
包里写得很清楚：snapshot continuity 已经有了，但 version read response 还看不到这部分 context。这个缺口如果不补，Source Intelligence 的 version surface 会出现“写入时保留了上下文，读取时却看不见”的不对称，长期会削弱版本读面的可解释性。修这个缺口是值得的。

**4. 语义边界整体诚实，但已经开始接近“response shape 变宽”的敏感区。**
你们自己也列出了已知风险：version response shape broader，且目前还没有专门覆盖 `GET /sources/plans/{plan_id}/versions` 的 route-level test。这个自我判断是准确的。现在这一步还没越界，但它已经到了一个需要更强 discipline 的位置：后面不能顺着“既然已有 context summary”继续加 comparison、diff、explain、packet replay 之类能力。

## validation_gaps

**第一，缺 route-level 版本读取测试。**
这是这次最明确的缺口，而且你们自己已经指出来了。当前验证覆盖了 discovery contract、identity、plan helpers、feeds source discovery route，以及 `feeds.py` / tests 的编译，但还没有专门钉住 `GET /sources/plans/{plan_id}/versions` 的路由级返回断言。对于这类“只是把已有快照内容读出来”的 patch，最需要的就是 route-level contract test。

**第二，需要确认字段的空值与回溯兼容行为。**
如果历史 version 的 `plan_snapshot` 没有完整 context summary，这个 response 是返回 `null`、空字符串，还是省略字段？包里没有说明。这个不一定是大问题，但如果不定下来，后面消费方会自己脑补 contract。

**第三，需要确认 `discovery_truth_boundary` 不会被外部误读成“质量背书”。**
包里已经声明“不 claim stronger source-intelligence quality”，这是对的。
但一旦 truth-boundary 字段出现在 response 里，外部很容易把它误当成“这个版本已经更可信/更强”。这需要测试和文档都明确：它是边界说明，不是质量评级。

## known_risks

**1. version response shape 逐步变成事实上的 richer API。**
这次仍然是窄 patch，但一旦 consumers 开始依赖这些 context 字段，后续再收窄会变难。所以要尽早把它定义成“bounded summary contract”，而不是“未来 discovery packet 的雏形”。

**2. plan_snapshot 读面可能被外部误当作完整 discovery truth。**
现在只读 summary 是好的，但也容易诱导下游说：“既然 version 已经有这些字段，那就继续把更多 discovery internals 塞出来。”这条坡要提前防住。

**3. Source Intelligence 有重新变宽的风险。**
从项目战略上看，Source Intelligence 现在应当是“下一条 product-capability start line 的准备面”，而不是新的并列主线。这个 patch 本身没有扩张，但它属于那种很容易一连串小步把 surface 做宽的类型，所以后续必须更克制。

## recommendation

**accept_with_changes**

我建议通过，但带两项必补动作：

**第一，补一个专门的 route-level test，直接钉 `GET /sources/plans/{plan_id}/versions` 的 response contract。**
重点断言这 6 个 context summary 字段来自 `plan_snapshot`，并且只是一层 summary，不触发额外 comparison/diff semantics。

**第二，把 contract 文案再收紧一点。**
明确这组字段是：

* version-scoped summary
* snapshot-derived
* bounded
* non-comparative
* non-quality-claiming

我的最终判断是：

**这一步是对的，值得做，而且符合当前项目“补连续性，不扩平台面”的战略边界；但它还只是一个窄 M1 continuity closure，不应该被解释成 Source Intelligence 已经开始大面积铺开。** 

如果你愿意，我下一轮可以继续按 IKE 的长期 review continuity，直接给你一个更硬的版本：
**“通过 / 必改项 / 主线边界判断 / 是否允许继续扩下一步”**。
