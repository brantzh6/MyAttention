# 知识生命周期研究

> 目标：研究 MyAttention 作为“世界知识系统”时，知识应如何分类、如何带时间、如何带事实与来源、如何支持跨学科洞察，以及哪些标准和主流体系值得借鉴。

---

## 1. 研究问题

MyAttention 的核心目标不是简单收文档，而是：

- 获取信息
- 识别事实
- 抽取知识
- 沉淀结构
- 形成洞察
- 驱动决策与进一步研究

因此知识体系至少要同时支持：

- 学科维度
- 时间维度
- 事实维度
- 来源/证据维度
- 跨学科维度

---

## 2. 权威分类与知识组织参考

### 2.1 UNESCO ISCED-F 2013

参考：

- [ISCED Fields of Education and Training 2013](https://uis.unesco.org/sites/default/files/documents/isced-fields-of-education-and-training-2013-en.pdf)
- [UNESCO ISCED overview](https://uis.unesco.org/en/topic/international-standard-classification-education-isced)

关键点：

- UNESCO 提供了全球广泛使用的教育/学科分类框架
- 是层级化结构：
  - broad
  - narrow
  - detailed
- 覆盖自然科学、数学、统计、ICT、工程、农业、医学、社会科学、新闻、商业、法律、艺术、人文学科等

价值：

- 可作为面向“世界知识”的顶层学科树起点
- 适合做跨国家、跨学科的通用分类骨架

限制：

- 它是“教育和培训”分类，不是完整知识哲学或科研知识图谱本体
- 对学派、争议、研究前沿、交叉领域表达不够

---

### 2.2 OECD Frascati / Fields of Science

参考：

- [Frascati Manual development](https://www.oecd.org/en/about/projects/frascati-manual-development.html)
- [Frascati Manual 2015 PDF](https://www.oecd.org/content/dam/oecd/en/publications/reports/2015/10/frascati-manual-2015_g1g57dcb/9789264239012-en.pdf)

关键点：

- OECD 的 Frascati 体系是全球科学技术统计的重要标准
- 面向 research & development 场景
- 更接近科研领域和研究活动组织方式

价值：

- 很适合做“研究活动 / 学术知识”视角下的学科组织
- 可与 UNESCO 学科树互补

限制：

- 偏科研统计与政策口径
- 不足以单独承载“世界知识全景”

---

### 2.3 Library of Congress Classification

参考：

- [Library of Congress Classification Outline](https://www.loc.gov/aba/cataloging/classification/lcco/)

关键点：

- Library of Congress 提供非常成熟的大类结构
- 大类覆盖：
  - 哲学、心理、宗教
  - 历史
  - 社会科学
  - 语言文学
  - 科学
  - 医学
  - 技术
  - 艺术

价值：

- 对“世界知识资源组织”很有价值
- 更适合做知识资源编目、馆藏组织、主题浏览参考

限制：

- 主要面向文献组织，而不是动态知识推理
- 有历史偏向和图书馆学偏向

---

### 2.4 ACM CCS

参考：

- [ACM Computing Classification System](https://www.acm.org/publications/computing-classification-system/css)

关键点：

- 计算机学科的层级分类体系
- 在计算机科学论文和数字图书馆里广泛使用

价值：

- 对计算机、AI、软件工程、HCI 等子学科的细粒度组织非常有帮助
- 可作为具体学科的“专业子分类树”模式参考

---

## 3. 知识组织与语义层参考

### 3.1 SKOS

参考：

- [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/)

关键点：

- SKOS 适合表示：
  - taxonomy
  - thesaurus
  - classification scheme
  - concept scheme

价值：

- 非常适合表示“学科树”“主题树”“概念层级”
- 能表达：
  - broader / narrower
  - prefLabel / altLabel
  - mapping relation

对 MyAttention 的启发：

- 学科、分支、流派、主题、专题都可以先用 SKOS 风格组织
- 这比一开始就全量上重本体更现实

---

### 3.2 Dublin Core

参考：

- [DCMI Metadata Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/)

关键点：

- Dublin Core 提供通用 metadata terms
- 包含：
  - title
  - creator
  - subject
  - type
  - language
  - temporal
  - provenance
  - valid

价值：

- 很适合作为知识对象、研究对象、信息对象的通用元数据层

---

### 3.3 PROV-O

参考：

- [W3C PROV-O](https://www.w3.org/TR/prov-o/)

关键点：

- PROV-O 是 provenance 的 W3C Recommendation
- 关注：
  - entity
  - activity
  - agent
  - wasGeneratedBy
  - wasDerivedFrom
  - wasAttributedTo

价值：

- 对“知识从哪来”“谁加工了它”“它基于哪些来源和步骤形成”至关重要
- 这对可信知识系统是基础能力

---

### 3.4 OWL-Time

参考：

- [W3C OWL-Time](https://www.w3.org/TR/owl-time/)

关键点：

- 用于表示时间点、时间区间、持续时间、时序关系

价值：

- 适合把“时间维度”建成正式结构，而不是只留一个 `created_at`
- 可支持：
  - 事件发生时间
  - 知识有效时间
  - 研究发表时间
  - 因果前后关系

---

### 3.5 BFO

参考：

- [Basic Formal Ontology](https://basic-formal-ontology.org/)

关键点：

- BFO 是上层本体，面向多领域信息整合

价值：

- 如果后续知识大脑需要更强形式化与跨领域统一语义，BFO 是值得研究的上层抽象

限制：

- 直接作为当前阶段主组织结构会过重

---

## 4. 时间维度与事实维度

### 4.1 时间不是附属字段，而是主维度

对不同知识类型，时间意义不同：

- 金融 / 政经 /市场
  - 时效性极强
  - 过时信息风险很高
- 科学研究
  - 需要看概念、理论、方法的演化
  - 旧研究不一定失效，但地位会变化
- 历史 / 社会 /文化
  - 需要保留事件顺序和版本演变

因此后续不能只用一个时间字段糊过去，至少应区分：

- `event_time`
- `publication_time`
- `ingest_time`
- `valid_time`
- `observed_time`
- `superseded_time`

---

### 4.2 事实维度不等于知识维度

后续应区分：

- `Event / Fact`
  - 世界上发生了什么
  - 例如：某公司发布产品、某研究发表、某政策实施
- `Claim / Interpretation`
  - 某来源如何解释这件事
- `Knowledge`
  - 经过整理、对齐、证据评估后形成的稳定结构
- `Insight`
  - 基于多事实、多知识、多时间序列形成的新判断

这四层不能混。

---

## 5. 知识生命周期

结合上面的标准与建模参考，MyAttention 更适合把知识生命周期理解为：

1. `Signal`
   - 新信息、新变化、新线索
2. `Event / Fact`
   - 对发生的事情形成基本事实记录
3. `Claim`
   - 来源如何描述、解释、评价这个事实
4. `Structured Knowledge`
   - 抽取实体、关系、概念、主张、证据后形成结构
5. `Canonical Understanding`
   - 当前权威理解 / 主流共识 / 代表性争议
6. `Insight`
   - 跨来源、跨学科、跨时间的高阶洞察
7. `Action / Decision Support`
   - 面向用户的建议、研究路线、风险提示、任务生成

这条链路里，每一步都需要不同 agent 参与。

---

## 6. 交叉洞察的意义

你的目标不是只做学科归档，而是要支持涌现和洞察。

这意味着系统未来必须支持：

- 跨学科概念映射
- 不同学科对同一对象的不同解释
- 时间序列上的知识迁移
- 多源主张冲突分析
- 从事件到理论、再从理论回到现实验证

这不是简单向量检索就能解决的，需要：

- 学科树
- 时间结构
- provenance
- claim / evidence / consensus / dispute 建模

---

## 7. 研究结论

1. 学科维度不能凭主观划分，应该优先参考：
   - UNESCO ISCED-F
   - OECD Frascati
   - Library of Congress
   - 具体领域的专业分类（如 ACM CCS）

2. 知识对象至少应有 5 类结构：
   - concept
   - event/fact
   - claim
   - evidence/source
   - insight

3. 时间维度必须正式建模，而不是只留普通时间戳。

4. provenance 必须是一等能力，否则很难建立可信知识体系。

5. 学科树适合先用 SKOS 风格做可维护的概念组织，再决定哪些部分需要升级到更重的本体层。

---

## 8. 下一步应产出的正式设计

- `docs/KNOWLEDGE_ARCHITECTURE.md`
- `docs/MEMORY_ARCHITECTURE.md`

重点应包括：

- 学科树来源与层级
- 知识对象类型
- 时间模型
- provenance 模型
- claim / evidence / consensus / dispute 模型
- 跨学科链接模型
- 从信息流到知识再到洞察的流水线
