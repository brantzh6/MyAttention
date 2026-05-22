# claude


让我先读取这个 result 文件。
现在读取变更涉及的代码。
再看一下 `_build_related_candidate_seed` 的完整返回部分。
已掌握完整上下文。以下是 review：

---

## Review: IKE_SOURCE_INTELLIGENCE_V1_M1_PERSON_SIGNAL_SEED_RESULT_2026-04-12

**判定: `accept`**

---

### 变更范围确认

| 维度 | 评估 |
|------|------|
| 范围是否 bounded | ✅ 仅扩展 signal→person 的 seeding 路径，无新 API |
| 是否改变 top-level 发现策略 | ✅ 否，仅在现有 discovery path 内部增强 |
| 是否引入新依赖 | ✅ 否 |
| truth boundary 是否准确 | ✅ 明确声明不是 research-grade、不做 cross-source identity resolution |

---

### 代码变更质量

#### `_candidate_relation_hints` (feeds.py:1549-1566)

新增了 `signal` 类型的处理分支：

- `x.com/*/status/*` → 提取 handle → 产出 `{"relation": "author", "item_type": "person", "object_key": "x.com/{handle}"}`
- `twitter.com/*/status/*` → 同样处理
- 保留原有的 `source_stream` relation hint

**质量判断：**
- handle 提取逻辑清晰：`split("x.com/", 1)[1].split("/status/", 1)[0].strip("/")`
- 有 `if handle:` 保护，避免空 handle 产出空 person
- `related[:3]` 的上限截断保持不变，signal 场景最多产出 author + source_stream = 2 条，不会溢出
- x.com 和 twitter.com 并行处理，覆盖了两种 URL 形式

**无问题。**

#### `_build_related_candidate_seed` (feeds.py:1598-1652)

新增了 `author` relation 的处理：

- `relation == "author"` + `focus in {METHOD, FRONTIER}` → `inferred_roles = ["builder"]`
- `follow_score = 0.07`（低于 maintainer 的 0.1，高于默认的 0.04）

**设计判断正确：**
- "从一条推文推断出的 person" 的确信度应低于 "从一个 repo 推断出的 owner"
- `builder` role 的权重（0.07）在 `_person_follow_score` 的 role_map 中排最低档（0.05），合理反映了这是弱信号
- `authority_score = max(0.45, min(0.92, parent_score - 0.08))` 保持了原有的保守降分策略

**无问题。**

---

### 测试覆盖

| 测试 | 覆盖内容 | 评估 |
|------|---------|------|
| `test_x_status_signal_emits_person_relation_hint` (identity:109) | x.com status → author person hint | ✅ 验证了完整的 hint 结构 |
| `test_author_relation_can_seed_builder_person_candidate` (identity:125) | author hint → builder person seed | ✅ 验证了 item_type、url、inferred_roles、follow_score |

两个测试形成完整链路：**signal URL → relation hint → person seed**。

---

### 战略层面判断

这个 slice 标志着 M1 从 read-surface realism（inspection proof）**回到了产品能力推进**（discovery quality improvement）。

从战略 review 的角度看，这正是之前建议的方向：versions realism lane 已经 closed，应该转向真正的 discovery 能力。这个 person signal seed 是正确的下一步：

- **直接服务于项目声明的 weakness**："person discovery is still too weak"（AGENTS.md mainline blockers）
- **在现有 path 内增强**，没有开新 API 或新 track
- **产出是有限度的**：从社交信号推断 person 是 weak signal seeding，不是 strong identity resolution。truth boundary 准确地声明了这一点

---

### 小风险点（不阻塞 accept）

1. **twitter.com vs x.com 的 object_key 不统一**：从 `x.com/openclaw/status/123` 提取的 person key 是 `x.com/openclaw`，从 `twitter.com/openclaw/status/123` 提取的是 `twitter.com/openclaw`。同一个人可能产生两个不同的 person candidate。这是已知的 cross-source identity resolution 缺失，truth boundary 已声明，后续可处理。

2. **`related[:3]` 截断**：signal 类型产出 author + source_stream = 2 条，当前安全。但如果未来增加更多 relation 类型，需注意截断可能丢弃有价值的 hint。

---

### 结论

`accept`

原因：
1. 变更 bounded，仅在现有 discovery path 内增强 person seeding
2. 代码逻辑清晰，防御性编程到位（空 handle 保护、分数上下限截断、role 强度分级）
3. 测试覆盖了完整的 signal→hint→seed 链路
4. 直接回应了项目声明的 person discovery weakness
5. truth boundary 准确，没有过度声称
6. 标志着 M1 从 inspection proof 回到产品能力推进，方向正确

# gemini
**IKE Sentinel (治理代理) 已激活。**

执行上下文：`Source Intelligence V1 M1` 最终真实性审查（Realism Review）。
审查标准：`IKE_SENTINEL_PROTOCOL.md` (方向对齐、方法验证、真实性)

针对提交的 `IKE_SOURCE_INTELLIGENCE_V1_M1_VERSIONS_REALISM_REVIEW_PACK_2026-04-12.zip` 及其包含的系列证明文件，本哨兵已完成深度审计。

---

### 1. 审计发现 (Findings)

* **严重程度：低 (Minor) —— 验证了“鲁棒的平庸”：**
    该 Packet 成功证明了 API 在极端不完整的数据下（Sparse history, Uniform needs_review）依然能保持物理上的可用性。这排除了“由于数据缺失导致 UI 或 API 崩溃”的低级技术风险。
* **严重程度：中 (Medium) —— 确认了“读语义”的严格受限：**
    通过 `LATEST_SPARSE_REFRESH` 和 `UNIFORM_NEEDS_REVIEW` 两个案例，你向 Delegate 强加了一个关键的治理共识：**`GET /versions` 仅仅是一个回望窗口，它不包含任何“自动仲裁”或“多版本比较”的逻辑。** 这极大地降低了 Source Intelligence 层的逻辑复杂度。
* **严重程度：战略 (Strategic Warning) —— 最后的缓冲区：**
    你已经在 `REPEATED_REFRESH_EVALUATION_REVIEW_ABSORPTION` 中明确拒绝了哨兵此前的“立即硬锁”建议，理由是“关闭已开启的边界路径”。本哨兵接受这一理由，但判定**此路径已达物理终点**。

### 2. 验证缺口与开放问题 (Validation Gaps)

* **缺少跨 Page 验证：** 目前的测试均基于 Mock 返回的少量固定版本。当 `SourcePlan` 演化出 50+ 版本时，Descending Order（降序排列）与数据库索引的物理性能表现未被验证。
* **影子状态风险：** 虽然 API 返回了默认值，但前端或下游调用方是否会因为收到大量的 `empty list` 或 `needs_review` 而产生逻辑死循环？这属于“集成层幻觉”，目前仅靠文档约束。

### 3. 总体判定 (Overall Verdict)

**判定：`accept_with_changes`**

**修改要求 (Changes Required)：**
1.  **物理封印 (Physical Seal)：** 在合并此 Packet 后，必须在 `feeds.py` 相关路由附近添加明显的治理注释：`// IKE_SENTINEL_GOVERNANCE: READ-ONLY SURFACE CLOSED. DO NOT ADD COMPARISON OR ARBITRATION LOGIC HERE.`
2.  **强制回归 (Forced Return)：** 此 Packet 是 Source Intelligence M1 阶段的最后一个合法封包。**禁止**发起 M2 阶段。下一个 Packet 必须回到 `Runtime v0` 的 R2-Integration 轨道。

---

### 4. 针对审查请求 (Review Request) 的逐项答复

1.  **版本查看真实性是否已关闭？** 是的。通过覆盖“稀疏历史”和“全量待审”两个极端案例，该读取路径的边缘情况已摸清。
2.  **证明是否严格受限于 Read 语义？** 是。代码中利用 `plan_snapshot` 进行序列化的逻辑非常纯粹。
3.  **稀疏历史是否为正确的最终检查？** 是。这是分布式系统中最常见的非原子性写入导致的中间状态。
4.  **是否需要额外验证？** 不需要。目前的数据结构足以支持 M1 的目标。
5.  **是否符合范围压缩战略？** **勉强符合**。它通过“明确不做比较/仲裁”实现了功能上的快速收敛，而不是无休止的开发。

**哨兵结语：**
该支线任务现已宣告正式终结。你已经为 Source Intelligence 盖好了盖子。**现在，请把手术刀拿回 Runtime 内核，去解决那些真正令你头疼的数据库事务一致性问题。**

# chatgpt
**findings**

**1. High — 这一步方向上可以接受，但它是 Source Intelligence 重新“动起来”的第一步，所以边界必须比 versions realism 更严。**
和前一条 `versions realism` lane 不同，这次已经不是单纯补 read-surface realism，而是开始做一个小的 discovery-quality 改进：把 social `signal` 结果有条件地 seed 成 `person` candidate。这个方向本身不算偏航，因为它确实更接近你们写的 M1 目标——提升 `person/object discovery quality`。
但也正因为如此，它比前几轮更容易把 Source Intelligence 再次拉宽。它已经从“证明现有 surface 可读”迈向“对候选对象做更强推断”。所以这一步不是不能做，而是**必须被视为一个窄 seed slice，不得自动外推成 identity resolution、actor graph、person discovery lane 重启。**

**2. High — `signal -> person` 这个切片选得基本对，但只能停在“seed”，不能被包装成“识别”。**
这次最合理的地方，是它没有去做跨源身份解析，也没有宣称“识别出作者”，而只是对 `x.com/.../status/...` / `twitter.com/.../status/...` 这种强结构化 social signal，提一个 bounded 的 `author -> person` relation hint，再把这个 hint 转成一个保守的 person seed。
这在工程上是说得过去的，因为这里的 handle 确实是 status URL 的直接组成部分，不是从自由文本里猜出来的。
但语义上必须继续坚持：**这是 handle-level person seed，不是 research-grade person identity。** 这条线一旦被说成“发现维护者/作者”，就会迅速越界。

**3. High — `author -> builder` 的推断目前是可接受的，但它已经在语义上踩到敏感边界，后续不能再抬高。**
从代码看，你们刻意把 repository `owner -> maintainer` 和 social status `author -> builder` 分开了，而且 `builder` 的 `follow_score` 也明显弱于 `maintainer`。这点是对的。
这说明你们理解到：**发了一条状态，不等于拥有仓库；说了项目，不等于就是 maintainer。**
不过我要明确提醒：`author -> builder` 已经是一个非零语义推断了。它之所以现在还能接受，是因为：

* 只对 `author` relation 生效
* 只在 `METHOD/FRONTIER` focus 下生效
* 用的是 `builder`，不是 `maintainer`
* 分值提升是 modest，不是强抬升

所以这一步的 review 结论不是“这个推断很强”，而是“**它当前够保守，所以暂时过线**”。后续不能顺着这条路把 `builder` 再往 `maintainer`、`core contributor`、`project owner` 抬。

**4. Medium — relation-hint 逻辑总体真实且克制，但 `source_stream -> domain=url.lower()` 这一支和 `author -> person` 并置后，容易让下游误以为 social actor 已经被更完整地结构化。**
从函数形态看，status signal 现在会同时产生：

* `author -> person`
* `source_stream -> domain`
  这本身没错，但要注意展示层和下游解释层。因为一旦 signal、person、stream 三层对象同时出现，系统看起来就会“像是已经开始做 actor/activity graph”。
  实际上它现在还远没到那一步，只是把一个 handle seed 补出来了。这个解释边界需要继续压住，否则很容易被误读成 Source Intelligence 已经在做更完整的人-活动关系抽取。

**5. Medium — 测试覆盖对这一个 slice 来说基本够用，但还缺一类最重要的负向边界测试：不要把无关 social signal 轻易抬成人。**
目前测试覆盖了两件关键事：

* helper 级：`x status -> author person hint`
* helper/route 级：`author relation -> builder seed`，以及路由上 person candidate 确实能出现
  这对当前 slice 是够的。
  但如果只补一类测试，我会优先补**负向保守性测试**，例如：
* 普通讨论型 status、无明确项目关联的 social post，不应轻易 seed 成高优先 person
* 非 METHOD/FRONTIER focus 下不应抬 `builder`
* 同一 handle 不应因为多条 status 迅速被错误“强化”为更强角色
  也就是说，这条 lane 现在最大缺口不是“能不能 seed”，而是“**什么时候不该 seed 或不该强化**”。

**6. Medium — 这一步仍然和当前 scope compression 基本对齐，但前提是它被当成一个孤立的 bounded patch，而不是 person discovery 子主线的起点。**
从项目层面看，这次没有新开 API surface，没有改顶层 strategy，也没有做 cross-source identity resolution，这些都对。
所以它目前还没有违反之前的范围压缩判断。
但它比 versions realism 更危险，因为它开始触碰“对象质量改进”本身，而不是只补 surface。
所以我的判断是：**可以做，但必须作为一个非常明确的、一次性的 M1 bounded slice 被收住。**

---

**validation gaps / open questions**

**1. 最需要补的是负向边界，而不是更多正向示例。**
我最想确认的是：

* 哪些 social signal 不应该生成 person seed？
* 哪些情形下即使生成了 person seed，也不应该给 `builder`？
* 是否存在因为 title/snippet 中带有 “maintainer / author / creator” 等词，就把普通传播者错误抬成 builder 的风险？
  当前材料对“正向成立”证明得够了，对“负向不误伤”还不够。

**2. 还缺一个“不会升级成 identity resolution”的防漂移说明。**
虽然文档已经写了“不 add cross-source identity resolution”，这很好。
但最好再补一句更硬的话：
**x.com handle person seed 只是 source-local candidate，不应被跨域并表为 canonical person identity。**
因为这正是后续最容易失控的地方。

**3. route-level realism 还没有覆盖多 signal 聚合下的人物强化边界。**
现在 route test 证明了从单个 x status 能 seed 出一个 person candidate。
但如果同一 handle 多次出现、不同 snippets 带不同角色词，系统会不会不小心把一个“builder seed”逐步强化成看起来像稳定 identity/object？这类边界现在还没证明。

---

**recommendation**

**accept_with_changes**

原因如下：

* **accept**，因为这一步作为 “versions realism 之后的下一个窄 slice” 是成立的，且选点合理。它确实比继续补 read realism 更接近 M1 的真实目标：改善 `person/object discovery quality`。
* **with_changes**，因为这一步已经开始进入“对象推断”区域，天然比之前几轮更容易越界。它必须被严格锁定在：

  * social status 结构化 author hint
  * bounded person seed
  * conservative `builder` inference
  * no cross-source identity resolution
  * no role escalation

我的最终判断一句话是：

**这一步可以过，但它标志着 Source Intelligence 从“读面证明”重新进入“对象质量改进”，所以后续最重要的不是继续往前推，而是立刻补上负向边界，并把这条线重新收窄成一个 seed，而不是让它长成 person discovery 主线。**

