# claude

Now let me read the actual code changes — the compression helper and the tests.
Now let me also check the call site to see how compression integrates into the discovery flow.
已完整阅读所有 5 个 in-scope 文件的相关部分。以下是 review：

---

## Review: IKE_SOURCE_INTELLIGENCE_V1_M3_NOISE_COMPRESSION_RESULT_2026-04-13

---

### Findings

**1. [正面] 压缩规则窄且可辩护**

`_compress_generic_domain_candidates` 的逻辑非常克制：
- 仅在 METHOD / FRONTIER / LATEST 三个 focus 下激活
- 仅移除 `item_type == "domain"` 的 candidate
- 仅当同域名下存在一个 specific candidate 且其 `authority_score >= max(domain_score - 0.02, 0.38)` 时才移除

`0.02` 容差和 `0.38` 下限是合理的保守阈值——避免一个刚好过线的弱 specific candidate 就把 domain 干掉。如果 domain 得分显著高于 specific candidate（> 0.02），domain 会被保留。

**2. [正面] 调用位置正确**

压缩在 ranking 之后、recommendation 生成之前执行（L1926），且接在 truncation `[: max(body.limit * 4, 24)]` 之前。这意味着：
- 压缩减少的是噪音 candidate 数量，不影响排序逻辑
- 压缩后的列表再做截断，不会因为压缩导致截断后的候选数量不足（不太可能，但逻辑正确）

**3. [正面] 测试覆盖了两个关键边界**

Helper-level 测试：
- ✅ 同域名有 specific candidate → generic domain 被移除
- ✅ 无同域名 specific candidate → generic domain 被保留

Route-level 测试：
- ✅ 端到端证明在 `/api/sources/discover` 请求中，`github.com` (domain) 被移除而 `github.com/openclaw/openclaw` (repository) 被保留

**4. [低] 缺少一个边界 case 的测试：specific candidate score 明显低于 domain score**

当前测试用例中 domain score=0.72，specific score=0.74，specific 更高。没有测试 domain score 明显高于 specific 的情况（例如 domain=0.85, specific=0.60）——按逻辑 `0.60 < max(0.85-0.02, 0.38) = 0.83`，domain 应该被保留。

这不是 bug（逻辑读起来是正确的），但缺少这个边界 case 的显式测试。不阻碍接受。

**5. [正面] 文档措辞诚实**

Result 文档和 Plan 文档的 truth boundary 完全一致，没有过度主张。"one obvious generic-domain duplication pattern is now compressed" — 准确。

---

### Open Questions

**1. 下一个值得压缩的 noise family 是什么？**

M3 解决了 generic domain vs specific object 的重复。Result 文档的 next decision edge 正确指出不应继续做同一类 patch。那么下一个最有价值的 noise family 是什么？可能的候选：
- 同一 repository 的不同 URL 变体（https vs http, trailing slash, www subdomain）
- 同一人/组织的不同平台出现（github profile vs x.com profile）

这个问题在 M3 scope 之外，但值得 controller 下一步判断。

**2. 压缩只在 discovery 阶段生效，refresh 是否也需要？**

当前 `_compress_generic_domain_candidates` 只在 `_run_source_discovery` 的 ranked 结果上调用。如果 plan refresh 重新发现了 generic domain candidate（理论上可能），refresh 路径是否也该压缩？目前不确定 refresh 是否复用同一条路径。不阻碍当前 packet。

---

### Recommendation

**`accept`**

**理由：**

- 压缩规则窄、保守、有明确的激活条件和阈值
- 调用位置正确（ranking 之后，truncation 之前）
- helper-level + route-level 双层测试覆盖
- 没有新增 API surface，没有改变现有行为的语义
- truth boundary 声明诚实
- 45 个测试全部通过，无回归
- 这是一个好的停止点——继续在同一模式上 patch 边际价值递减

# gemini
针对您提供的 **`IKE_SOURCE_INTELLIGENCE_V1_M2_LOOP_PROOF_RESULT_2026-04-13`** 压缩包及其相关上下文，我已完成对 `Source Intelligence V1` 第二里程碑（M2）的循环证明审计。

由于您之前的 `Runtime v0` 已经顺利结案，本次评审的重点在于：**Source Intelligence 的代码路径是否在不破坏既有边界的前提下，成功跑通了真实闭环。**

### IKE Sentinel：Source Intelligence V1 M2 评审报告

**判定结论：`ACCEPT` (准予通过)**

---

#### 1. 核心发现：循环证明的真实性 (Loop Truthfulness)
通过审查测试代码 `test_source_intelligence_m2_loop_reuses_existing_m1_path`，我确认了该系统已具备以下物理闭环能力：
* **初次发现到持久化：** 系统能将 `POST /sources/discover` 产生的主题驱动结果转化为持久化的 `Source Plan`。
* **带上下文的刷新：** `POST /sources/plans/{plan_id}/refresh` 不仅仅是数据的覆盖，它能正确更新并保留显性的“发现笔记”（Discovery Notes）。
* **历史回溯的完整性：** 版本历史（Version History）能准确反映从初始基准到刷新后的状态变化，证明了 M1 阶段建立的快照机制在 M2 循环中是稳健的。

#### 2. 边界合规性审计 (M1 Boundary Adherence)
本次 M2 证明严格遵守了之前设定的“哨兵禁令”：
* **无语义扩张：** 审计确认没有引入任何“交叉源身份识别”或“研究级质量”的过激声明。
* **API 稳定性：** 所有的循环操作均在现有的 M1 路由（如 `/sources/plans`）上运行，没有为了跑通循环而私自开辟临时的、非标准的 API 后门。
* **默认值的安全性：** 对于旧版本快照中缺失的新字段（如 `discovery_notes`），系统会强制序列化为默认的空列表，有效防止了读取端的崩溃。

#### 3. 验证缺口与风险提示
尽管准予通过，但以下物理细节需在 M3 或更高级别中关注：
* **质量判定依然是黑盒：** 目前的 Loop 证明了“数据能跑通”，但并没有证明发现的内容是否具备“操作价值”。
* **噪音压缩风险：** 随着刷新次数增加，版本快照中的冗余信息可能会导致存储膨胀，目前尚未看到明确的噪音过滤或压缩逻辑。

---

### 哨兵决策建议 (Next Decision Edge)

* **停止点建议：** 同意在该节点停止对 `M1` 路径存在性的重复验证。
* **下一步转向：** 既然循环已跑通，下一个切片应聚焦于 **质量改进（Quality Improvement）** 或 **噪音压缩（Noise Compression）**。

**状态更新：** `Source Intelligence V1 M2` 循环证明已记录在案。**批准进入下一质量驱动阶段。**

# chatgpt
**findings**

**1. 这一步总体是成立的，而且 claim 基本诚实。**
这包真正做成的是一个很窄的 noise-compression slice：在现有 discovery path 里，压掉“同源 generic domain + 同源更具体对象”这一类明显重复。实现就是 `_compress_generic_domain_candidates(...)`，规则也很克制：只在 `METHOD / FRONTIER / LATEST` 下生效，只针对 `item_type == "domain"`，并且只有当同域的更具体 candidate 已经“足够有竞争力”时才移除 generic domain。这个 claim 和结果文档里的表述是一致的，没有明显夸大成“排序系统升级”或“广义去噪能力”。

**2. 这条压缩规则是窄而且可辩护的。**
当前规则只处理一个非常具体的重复噪音模式：

* `github.com`
* `github.com/openclaw/openclaw`

这种 pair 在同一 discovery 结果里同时出现时，generic domain 往往只会稀释注意力，不会增加决策价值。
你们没有把它扩成“所有 generic 都压”“所有 domain 都弱于 specific”“跨源也做压缩”，这点是对的。它仍然是一个 bounded heuristic，不是 ranking redesign。

**3. helper 和 route 两层证明基本够用。**
我看到的测试覆盖是健康的：

* helper 级：有“压掉 generic domain”的正向测试，也有“没有同源 specific 替代时保留 generic domain”的负向测试；
* route 级：`/api/sources/discover` 的实际返回中，确认 repository 还在，而 `github.com` 这个 generic domain 被压掉。

这说明它不是只在 helper 里成立，而是真的进入了当前 discovery path。

**4. 这是一个不错的 stop point。**
结果文档里说得对：下一步不应该默认继续做“同类 generic/specific patching”。我同意。
因为这一步的价值在于它解决了一个非常明显、非常低争议的噪音模式。再继续沿这个方向 patch 下去，很容易变成一串 ad hoc ranking rules，把 Source Intelligence 慢慢拖进“半套排序引擎”。
所以这一步更适合被定义为：**一个成立的窄去噪 slice，做完就停。**

**5. 当前实现仍然有一个需要注意的语义点：它本质上在用 authority score 做“同源 specific 是否足够强”的近似判断。**
规则是：

* 先按 domain 找到 best specific score
* 如果 generic domain 的分数不比 best specific 明显高，并且 best specific 至少达到一个底线，就移除 generic

这在工程上合理，但也意味着：
这不是纯粹的“结构性去重”，而是“结构 + 近似竞争力”混合规则。
所以后续绝不能把它包装成“去噪逻辑已经更懂 source quality 了”。它仍然只是一个 bounded compression heuristic。

**6. 这一步没有明显拉宽项目边界，但已经靠近一个危险斜坡。**
现在还是安全的，因为：

* 没有新 API
* 没有 comparison / arbitration
* 没有 canonical source truth
* 没有 identity resolution

但再往前如果继续加：

* generic org vs specific repo
* generic media domain vs event page
* generic community vs specific thread
* generic person-handle vs specific role seed

这条线就会慢慢变成“规则堆叠式 ranking system”。
所以我会把这一步视为**可接受，但必须及时收口**。

---

**open_questions**

**1. 你们是否愿意把这条规则明确标成“same-source duplicate compression heuristic”，而不是更泛的 noise handling？**
现在它实际上处理的是一个非常具体的 family。命名越窄，后续越不容易被误扩。

**2. 后续如果还有 noise slice，是否会要求“distinct family”而不是继续沿 generic/specific domain 这个模式堆规则？**
我建议是要。否则很容易变成 patch-by-patch 的 ranking system。

**3. `LATEST` 也纳入这条规则是否是有意的长期选择？**
现在代码对 `LATEST` 也生效，这未必错，但它意味着新闻/最新动态场景下，generic source domain 也会被压。这个决定最好是明确的，而不是顺手跟 `METHOD/FRONTIER` 一起带上。

**4. 是否需要一个很小的 guardrail test：当 generic domain 显著高于“specific”时，不应被压掉？**
现在规则里已经有 `best_specific >= max(score - 0.02, 0.38)` 这种门槛，但测试里我只看到：

* same-domain specific exists -> drop
* no same-domain specific -> keep
  如果要补一条最有价值的测试，我会补“same-domain specific exists but not materially competitive -> keep generic”。

---

**recommendation**

**accept_with_changes**

原因很明确：

* **accept**：因为这一步确实是一个窄、真实、可验证的噪音压缩 slice，claim 也基本没有说大。
* **with_changes**：因为最该补的不是更多实现，而是更强的停止纪律和一个关键 guardrail test。

我的建议是：

1. 把这一步正式定性为
   **“one bounded same-source generic-domain compression heuristic landed”**
   不要说成更泛的 source-noise framework。
2. 补一条“specific 不够强时保留 generic”的 focused test。
3. 项目层面明确 stop rule：
   **M3 到这里停，不继续默认做同模式 patching；下一步要么换 distinct noise family，要么转向质量提升判断。**

一句话总结：

**这一步可以通过，而且是一个好的小胜利；但它的价值在于解决了一个明显重复噪音，不在于开启一条持续堆规则的 ranking 线。**
