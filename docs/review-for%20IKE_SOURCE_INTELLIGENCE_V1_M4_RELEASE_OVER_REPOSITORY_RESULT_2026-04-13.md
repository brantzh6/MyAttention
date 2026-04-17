# claude

Now let me read the actual code — the new compression helper and the tests.
Let me also check the `_repository_base_object_key` helper and the call site to understand the compression chain.
已完整阅读所有 in-scope 文件。以下是 review：

---

## Review: IKE_SOURCE_INTELLIGENCE_V1_M4_RELEASE_OVER_REPOSITORY_RESULT_2026-04-13

---

### Findings

**1. [正面] M3 和 M4 的压缩逻辑互为正交，链式执行正确**

调用顺序（L1968-1969）：
```
ranked = _compress_generic_domain_candidates(ranked, body.focus)
ranked = _compress_release_repository_overlap(ranked, body.focus)[: max(body.limit * 4, 24)]
```

M3 先移除 generic domain 重复，M4 再移除 same-repo release/repository 重复。两者作用于不同的 `item_type` 对（domain vs specific；repository vs release），不会冲突。执行顺序不影响最终结果——两个压缩器可以按任意顺序调用，结果相同。

**2. [正面] Focus 边界严格且合理**

- LATEST / FRONTIER：release 是更有时效性的信号，优先于 repository ✅
- METHOD：repository 是实现基准对象，应保留 ✅
- 逻辑一致：timely focus 要时效性，method focus 要实现细节。这个 focus 分离是正确的产品决策。

**3. [正面] 三层测试覆盖了关键边界**

Helper-level：
- ✅ LATEST focus + competitive release → repository 被移除
- ✅ METHOD focus → 两者都保留（即使 release 更强）
- ✅ LATEST focus + weak release → repository 被保留

Route-level：
- ✅ 端到端证明 `/api/sources/discover` 在 LATEST focus 下移除 same-repo repository

M3 review 中我提到的缺失边界 case（specific score 明显低于被压缩对象）在 M4 中得到了补充——`test_release_overlap_compression_keeps_repository_when_release_is_not_competitive` 使用 repo=0.85/release=0.60 验证了这个场景。同时 M3 也补充了对应的 `test_noise_compression_keeps_generic_domain_when_specific_is_not_competitive`（L233-253）。

**4. [低] `_repository_base_object_key` 对 release URL 格式有硬编码假设**

函数通过 `"/release/"` 子串来从 release object_key 中提取 repository base：

```python
if item_type == "release" and "/release/" in key:
    return key.split("/release/", 1)[0]
```

这假设所有 release 的 object_key 都包含 `/release/`。对 GitHub releases（`github.com/org/repo/release/latest`）来说是正确的。但如果未来有 PyPI、npm 等非 GitHub release source，这个提取逻辑会失效（返回空字符串，压缩不生效）。

**影响**：不是 bug——失效时只是保留了 repository（安全降级）。但值得记录为未来 release source 扩展时的注意项。

**5. [正面] 阈值设计与 M3 保持一致**

`best_release >= max(score - 0.02, 0.38)` — 与 M3 的 generic domain 压缩完全相同的阈值逻辑。这意味着两个压缩器有统一的"materially competitive"定义，便于理解和维护。

---

### Open Questions

**1. 两个压缩器是否应该抽象为一个通用的 "same-source overlap compressor"？**

M3（generic domain vs specific）和 M4（repository vs release）共享相同的模式：
- 收集"更好"候选的 best score per key
- 遍历候选列表，移除"较弱"的同 key 条目
- 相同的阈值逻辑

当前两个独立函数是合理的（scope 清晰，各自只做一件事）。但如果未来出现第三个同模式的压缩器，应该考虑抽象。不阻碍当前 packet。

**2. 压缩链会不会过度删除？**

理论上：一个 `github.com` domain candidate 可能被 M3 移除，同时一个 `github.com/org/repo` repository candidate 又被 M4 移除，最终只剩一个 release。在 LATEST focus 下这是合理的（release 是最有时效价值的）。但如果 controller 需要看到完整的 source 层级（domain → repo → release），当前压缩链会把中间层都去掉。目前的 truth boundary 声明已经覆盖了这个限制——"not source-wide ranking optimality"。

---

### Recommendation

**`accept`**

**理由：**

- 压缩规则窄、focus 边界清晰且合理（timely only）
- 与 M3 正交，链式执行无冲突
- 三层测试覆盖了 accept / reject / focus-boundary 的关键 case
- 阈值与 M3 一致，维护成本低
- 没有新增 API surface
- 50 个测试全部通过，无回归
- truth boundary 诚实，next decision edge 正确指向不应继续同一模式

**注意项（非 blocker）：**

- `_repository_base_object_key` 的 `/release/` 硬编码在非 GitHub source 扩展时需要更新
- 这是 noise compression 系列的一个好的停止点——M3 + M4 已经覆盖了两个最明显的 overlap family，继续同模式 patch 边际收益递减

# chatgpt
**findings**

**1. 这一步总体成立，但我会给 `accept_with_changes`，不是纯 `accept`。**
从结果文档、plan、router 实现和两份测试一起看，这次确实做成了一个**很窄的 same-repo overlap compression slice**：在 `LATEST` 和 `FRONTIER` 下，如果同一 repo 的 `release` 候选已经“足够有竞争力”，就压掉对应的 `repository` 候选；`METHOD` 不变，弱 `release` 不压 `repository`。这个主 claim 和实现是基本一致的，没有夸大成“release 普遍优于 repository”或“Source Intelligence 已具备更强的生命周期理解”。

**2. 范围控制是好的，属于一个可辩护的窄 heuristic，不是 ranking redesign。**
实现点非常集中：

* 通过 `_candidate_identity(...)` 把 GitHub/GitLab 的 `/releases` 与 `/releases/tag/...` 识别成 `release`
* 用 `_repository_base_object_key(...)` 把 `release` 回落到所属 repo 键
* 通过 `_compress_release_repository_overlap(...)` 做同 repo 压缩
* 且只在 `LATEST` / `FRONTIER` 生效
  这说明你们是在做一个特定 family 的 overlap compression，不是在偷偷堆一个通用排序引擎。这个边界我认可。

**3. “materially competitive” 的实现是诚实但朴素的，目前可接受。**
压缩条件是：

* 只看同 repo 的 best release 分数
* repository 只有在 `best_release >= max(repo_score - 0.02, 0.38)` 时才被压掉

这不是一个宏大的语义判断，而是一个很朴素的“足够接近/不弱太多”的 heuristic。
它的好处是可解释、可测试、边界窄。
它的限制也很明显：这不是“release 更重要”的一般理论，只是一个局部去重规则。只要后续文案继续保持克制，我认为这条线是可以接受的。

**4. helper 级覆盖是完整的，但 route 级证据还不够对称。**
我看到 helper 级已经覆盖了三件关键事：

* `LATEST` 下 release 压 repository
* `METHOD` 下 repository 保留
* release 不够强时 repository 保留

这组 helper tests 是够的。
但 route 级我看到的明确 proof 只有一条：

* `/api/sources/discover` 在 `latest` focus 下，返回 `release`，且不再返回同 repo `repository`

这里有一个小但实际的缺口：
结果文档声称 **`LATEST` 和 `FRONTIER`** 都能 prefer release over same-repo repository，且 `METHOD` 保持 baseline object；但 route 级并没有对 `FRONTIER` 做对称证明，也没有对 `METHOD` 做 route 级“确实保留 repository”的证明。
这不至于推翻当前结论，但会影响“结果文档的完整度”。

**5. 这是一个好的 stop point，后续不该继续默认沿“repository vs release”这一条线 patch 下去。**
这一点我和结果文档是一致的。现在这一步之所以健康，是因为它选的是一个很具体、争议很小的 overlap pattern：
**同 repo，timely/frontier focus，release 和 repository 重复出现。**
再继续沿同模式 patch，比如：

* release vs repo overview page
* release vs repo tags
* release vs changelog page
* release vs docs homepage

就很容易把这条线拖进 ad hoc ranking patching。
所以这一步做完以后，最正确的动作是停，不是继续顺着它补。

**6. 这里有一个细小但值得注意的措辞风险：`timely focus` 这个叫法略微比实现更宽。**
代码实际上只在 `LATEST` 和 `FRONTIER` 生效，不在 `METHOD` 生效。
把这两个一起概括成 `timely focus` 大体可以理解，但 `FRONTIER` 并不等同于严格时间新近性，它更像“前沿相关性”。所以更精确的说法其实应该是：
**“latest/frontier focus overlap compression”**
而不是更泛的 “timely focus”。
这不大，但对你们现在这种很强调边界诚实的项目来说，措辞最好尽量和实现一一对应。

---

**open_questions**

**1. 你们是否愿意把结果文档里的主表述从 `timely focus` 收紧成 `LATEST/FRONTIER focus`？**
这样会更贴实现，也更不容易被外部解读成“所有偏时效场景都已具备 release superiority heuristic”。

**2. 是否要补两条很小的 route-level 对称测试？**
我最建议补的是：

* `frontier` 下，同 repo release 可压 repository
* `method` 下，同 repo release 不压 repository

现在 helper 已经证明了这两件事，但 route 级还没完全对称。补完后，结果文档会更扎实。

**3. 你们是否要把这条 heuristic 明确命名成 `same-repo release duplicate compression`，而不是更泛的 release-over-repository？**
因为当前它处理的是“重复与稀释”，不是“release generally better than repository”。命名越窄，后续越不容易被误用成一般 ranking rule。

**4. 下一步是不是应该强制换 family，而不是继续 patch 同类 overlap？**
我建议是。
这条线最好的后续纪律不是“继续把 release 相关都收拾干净”，而是“到这里为止，下一步只能选 clearly distinct family，或者直接转向更高价值的质量改进”。

---

**recommendation**

**accept_with_changes**

我的理由是：

* **accept**：因为这一步确实是一个窄、真实、实现与文档大体一致的 overlap-compression slice，且没有明显拉宽 Source Intelligence 的边界。
* **with_changes**：因为还需要两类收口动作：

  1. **把文案收得更精确**：把 `timely focus` 收紧为 `LATEST/FRONTIER focus`，把 `release-over-repository` 更明确地解释为 **same-repo duplicate compression heuristic**。
  2. **补 route-level 对称证明**：至少补 `FRONTIER` 的正向 route proof；最好顺手补 `METHOD` 的负向 route proof。

一句话结论：

**这一步可以通过，而且是一个健康的小型去重压缩；但它的正确价值在于“压掉同 repo 的明显重复”，不在于宣称 release 已经在更广义上优于 repository。**



# gemini
**IKE Sentinel (治理代理) 审查模式已激活。**

正在对包 `IKE_SOURCE_INTELLIGENCE_V1_M4_RELEASE_OVER_REPOSITORY_RESULT_2026-04-13` 执行边界断言与代码物理验证。

基于提供的实现路由 (`feeds.py`) 和测试证据，以下是针对 M4 (Release-Over-Repository Compression) 的结案审查报告：

### 1. 核心发现 (Findings)

* **物理真实性与主张一致 (Truthfulness)：** 代码层面的实现完全符合文档声明。你引入了 `_compress_release_repository_overlap` 辅助函数，它在最后关头（取 Top N 前）物理切除了冗余的 `repository` 对象，且仅当同源的 `release` 对象得分具备竞争力（`>= max(score - 0.02, 0.38)`）时才执行。这是一种安全、保守的降噪策略。
* **边界防御极佳 (Boundary Defense)：** * 你在开头实施了强制短路：`if focus not in {SourceDiscoveryFocus.LATEST, SourceDiscoveryFocus.FRONTIER}: return candidates`。这完美保护了 `METHOD` 焦点，因为对于方法论研究，Repository 本身（源码、架构）远比单次 Release 更具持久价值。
    * 你的键值提取逻辑 `_repository_base_object_key` 精准识别了 `domain/owner/repo/release/...` 模式，并且对非标准 Release（如 `domain:release`）安全地返回了空字符串，避免了误伤无辜的主域候选源。
* **测试覆盖闭环 (Test Closure)：** 路由级别的 `test_sources_discover_latest_focus_prefers_release_over_repository_for_same_repo` 测试用例成功证明了：给定完全相同的 Repo，`LATEST` 发现现在会返回 `release` 并抑制基础的 `repository`。

### 2. 遗留观测与架构提问 (Open Questions)

这不再是阻塞性问题，而是指导下一阶段（M5）的架构反思：

* **同构降噪的扩展性 (Extension of Compression)：** 目前的逻辑是硬编码针对 `repository` 和 `release` 的。未来如果有 `organization` 和 `person` 的重叠（例如一个人就是那个组织的唯一发声者），或者 `event` 和 `domain` 的重叠，我们是否要在 `feeds.py` 中堆积无数个特化的 `_compress_x_y_overlap` 函数？ 
* **降噪在 Plan Refresh 阶段的遗留：** M4 只在 `discover` 的结果列表里做了降噪。如果一个早期版本（M3）创建的 `SourcePlan` 已经同时 `subscribed` 了某个 Repo 及其 Release，目前的 Refresh 逻辑似乎并不会主动去剔除（Stale）那个多余的 Repo。

### 3. 最终判定 (Recommendation)

这是一个极其克制、干净的手术刀式切片。没有破坏基础引擎，却实实在在地提高了 `LATEST` 情报视野的信噪比。系统不再把一个库的“代码更新”和“发布公告”当作两个独立的源塞给大模型处理了。

**Recommendation: `accept`**

**哨兵结语：** 你的战术收缩很成功，M4 是一个优秀的停顿点。同意停止继续在 Repository vs Release 的细枝末节上修补。建议立即向更高价值的 M5 推进（例如真正的质量过滤或者跨源的身份折叠）。已记录 M4 并批准合并。