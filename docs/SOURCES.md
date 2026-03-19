# 信息源评价体系

## 设计理念

MyAttention 采用**多层次信息源评价体系**，将信息源按权威性和价值分为四个层级：

```
┌─────────────────────────────────────────────────────────────┐
│                    信息源金字塔模型                          │
├─────────────────────────────────────────────────────────────┤
│                        /\                                    │
│                       /  \      Tier S: 权威信息              │
│                      /────\     官方发布、顶级学术             │
│                     /      \    (第一时间、最高准确度)          │
│                    /────────\                                │
│                   /          \   Tier A: 行业信息              │
│                  /────────────\  专业媒体、核心厂商             │
│                 /              \ (深度分析、独家视角)           │
│                /────────────────\                            │
│               /                  \ Tier B: 社区信息            │
│              /────────────────────\ 技术社区、投资者社区        │
│             /                      \(讨论、情绪、趋势)          │
│            /────────────────────────\                        │
│           /                          \ Tier C: 相关信息        │
│          /────────────────────────────\ 社交媒体、自媒体        │
│                                             (补充、传播)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 评价维度

| 维度 | 权重 | 说明 |
|------|------|------|
| **权威性** | 30% | 官方来源 > 权威媒体 > 普通媒体 > 自媒体 |
| **时效性** | 25% | 首发速度、更新频率 |
| **准确性** | 25% | 历史准确率、是否更正、信源可追溯 |
| **深度性** | 15% | 分析深度、原创内容占比 |
| **可获取性** | 5% | RSS 支持、订阅便捷性、付费门槛 |

---

## 一、AI 领域信息源体系

### Tier S: 权威信息（必订阅）

| 名称 | 类型 | URL | 订阅方式 | 价值说明 |
|------|------|-----|----------|----------|
| **OpenAI Blog** | 厂商官方 | https://openai.com/blog | RSS、邮件 | GPT 系列发布，行业风向标 |
| **Google DeepMind** | 厂商官方 | https://deepmind.google | RSS、邮件 | AlphaGo、AlphaFold 等突破 |
| **Meta AI Blog** | 厂商官方 | https://ai.meta.com/blog | RSS、邮件 | LLaMA、PyTorch 开源贡献 |
| **Anthropic Blog** | 厂商官方 | https://www.anthropic.com/news | RSS、邮件 | Claude 系列、AI 安全 |
| **arXiv cs.AI/cs.LG** | 学术预印本 | https://arxiv.org | RSS | 最新研究，学术前沿 |
| **NeurIPS/ICML/CVPR** | 学术会议 | 各自官网 | 邮件列表 | 顶级会议论文首发 |

### Tier A: 行业信息（重点订阅）

#### 中文 AI 媒体

| 名称 | URL | 订阅方式 | 特点 |
|------|-----|----------|------|
| **机器之心** | https://www.jiqizhixin.com | RSS、公众号 | 国内最早 AI 专业媒体，深度报道 |
| **量子位** | https://www.qbitai.com | RSS、公众号 | 产业报道全面，智库报告 |
| **新智元** | https://www.zhidx.com | 公众号 | AI 产业新闻，智库报告 |
| **AI科技评论** | https://www.leiphone.com/category/ai | 公众号 | 学术报道强 |

#### 海外 AI 媒体

| 名称 | URL | 订阅方式 | 特点 |
|------|-----|----------|------|
| **MIT Tech Review AI** | https://www.technologyreview.com/topic/artificial-intelligence | RSS、邮件 | 学术权威视角 |
| **VentureBeat AI** | https://venturebeat.com/category/ai | RSS | 创投融资视角 |
| **The Verge AI** | https://www.theverge.com/ai-artificial-intelligence | RSS | 科技深度报道 |

#### 中国大厂

| 名称 | 订阅方式 | 特点 |
|------|----------|------|
| **阿里巴巴达摩院** | 公众号 | 基础研究、应用落地 |
| **百度 AI** | 公众号 | 文心一言、飞桨 |
| **腾讯 AI Lab** | 公众号 | 游戏、医疗、内容 AI |
| **字节跳动 AI Lab** | 公众号 | 推荐算法、内容生成 |
| **华为诺亚方舟** | 公众号 | 基础研究、昇腾生态 |
| **智谱 AI** | 公众号 | GLM 系列、国产大模型 |

### Tier B: 社区信息

| 名称 | URL | 订阅方式 | 特点 |
|------|-----|----------|------|
| **Hugging Face** | https://huggingface.co | RSS、邮件 | 开源模型中心，Daily Papers |
| **Papers With Code** | https://paperswithcode.com | RSS | 论文+代码+SOTA 排行榜 |
| **GitHub AI Topics** | https://github.com/topics/ai | RSS | 开源项目、代码实现 |
| **Reddit r/MachineLearning** | https://www.reddit.com/r/MachineLearning | RSS | 学术讨论、论文解读 |
| **知乎 AI 话题** | https://www.zhihu.com/topic/19551275 | RSS | 深度讨论、专栏文章 |

### Tier C: 相关信息

| 名称 | 类型 | 说明 |
|------|------|------|
| **Twitter/X AI 账号** | 社交媒体 | @ylecun, @karpathy, @sama 等大佬动态 |
| **YouTube AI 频道** | 视频平台 | Two Minute Papers, 3Blue1Brown |
| **B站 AI UP 主** | 视频平台 | 李沐、跟李沐学 AI |
| **36氪 AI 频道** | 科技媒体 | 创投融资视角 |

### 投资视角

| 名称 | URL | 订阅方式 | 特点 |
|------|-----|----------|------|
| **a16z AI** | https://a16z.com/ai | RSS、邮件 | Andreessen Horowitz AI 投资 |
| **Sequoia AI** | https://www.sequoiacap.com | 邮件 | 红杉资本 AI 投资 |
| **ARK Invest** | https://ark-invest.com/research | 邮件 | 技术趋势投资分析 |

---

## 二、国内财经信息源体系

### Tier S: 权威信息（必订阅）

| 名称 | URL | 订阅方式 | 价值说明 |
|------|-----|----------|----------|
| **中国人民银行** | https://www.pbc.gov.cn | 公众号、官网 | 货币政策、利率决议、公开市场操作 |
| **中国证监会** | https://www.csrc.gov.cn | 公众号、官网 | 证券监管政策、IPO 审批 |
| **国家统计局** | https://www.stats.gov.cn | 公众号、官网 | GDP、CPI、PMI 官方数据 |
| **国务院** | https://www.gov.cn | 公众号、官网 | 重大政策、国务院常务会议 |
| **国家发改委** | https://www.ndrc.gov.cn | 公众号、官网 | 宏观经济政策、产业政策 |
| **巨潮资讯网** | https://www.cninfo.com.cn | RSS、官网 | 上市公司公告权威来源 |

### Tier A: 行业信息（重点订阅）

#### 专业财经媒体

| 名称 | URL | 订阅方式 | 特点 |
|------|-----|----------|------|
| **财新网** | https://www.caixin.com | RSS、公众号 | 深度报道，宏观经济权威 |
| **财联社** | https://www.cls.cn | APP、公众号 | 7×24 小时快讯，投资者必备 |
| **中国证券报** | https://www.cs.com.cn | RSS、公众号 | 证监会指定披露媒体 |
| **证券时报** | https://www.stcn.com | RSS、公众号 | 深交所指定披露媒体 |
| **第一财经** | https://www.yicai.com | RSS、公众号 | 实时财经新闻，电视节目 |
| **21世纪经济报道** | https://www.21jingji.com | 公众号 | 产业报道深入 |
| **华尔街见闻** | https://wallstreetcn.com | APP、公众号 | 全球财经，宏观分析 |

#### 券商研究

| 券商 | 研究所公众号 | 首席/团队 | 特点 |
|------|-------------|-----------|------|
| **中金公司** | 中金点睛 | 刘鹤、彭文生 | 国际视野，H 股研究强 |
| **中信证券** | 中信证券研究 | 诸建芳、秦培景 | 综合实力强 |
| **国泰君安** | 国泰君安证券研究 | 花长春、李少君 | 策略研究知名 |
| **海通证券** | 海通研究 | 姜超、荀玉根 | 宏观研究深入 |
| **广发证券** | 广发研究 | 郭磊、戴康 | 宏观经济分析扎实 |
| **安信证券** | 安信研究 | 高善文、陈果 | 市场关注度高 |

#### 研报平台

| 名称 | URL | 特点 |
|------|-----|------|
| **慧博投研** | https://www.hibor.com.cn | 研报聚合，覆盖全券商 |
| **东方财富研报** | https://data.eastmoney.com/report | 免费研报获取 |
| **萝卜投研** | https://robo.datayes.com | 数据驱动分析 |

### Tier B: 社区信息

| 名称 | URL | 特点 | 注意事项 |
|------|-----|------|----------|
| **雪球** | https://xueqiu.com | 投资者社交，大 V 众多 | 需辨别质量 |
| **集思录** | https://www.jisilu.cn | 低风险投资社区 | 质量较高 |
| **东方财富股吧** | https://guba.eastmoney.com | 股民讨论热烈 | 噪音多，谨慎甄别 |

### Tier C: 相关信息

| 名称 | 类型 | 说明 |
|------|------|------|
| **微博财经大 V** | 社交媒体 | 信息传播快，需辨别 |
| **知乎财经话题** | 知识平台 | 深度分析，质量参差 |
| **公众号矩阵** | 自媒体 | 补充视角 |

### 数据平台

| 名称 | URL | 费用 | 特点 |
|------|-----|------|------|
| **Wind** | https://www.wind.com.cn | 高（机构） | 终端数据最全面 |
| **同花顺 iFinD** | https://www.10jqka.com.cn | 中高 | 性价比高 |
| **东方财富 Choice** | https://choice.eastmoney.com | 中等 | 性价比高 |
| **新浪财经** | https://finance.sina.com.cn | 免费 | 免费行情 |

### 重要数据日历

| 时间 | 数据/事件 | 发布机构 | 重要程度 |
|------|-----------|----------|----------|
| 每月 1 日 | PMI | 统计局 | 高 |
| 每月 9-10 日 | CPI/PPI | 统计局 | 高 |
| 每月 10-15 日 | 社融/M2 | 央行 | 高 |
| 每季度首月 15 日后 | GDP | 统计局 | 极高 |
| 年末 | 中央经济工作会议 | 国务院 | 极高 |
| 3 月两会 | 政府工作报告 | 国务院 | 极高 |

---

## 三、国际财经信息源体系

### Tier S: 权威信息（必订阅）

| 名称 | URL | 订阅方式 | 价值说明 |
|------|-----|----------|----------|
| **美联储** | https://www.federalreserve.gov | RSS | 全球最重要央行，FOMC 会议纪要 |
| **SEC EDGAR** | https://www.sec.gov/edgar | RSS | 美股财报、内幕交易、13F 官方来源 |
| **IMF** | https://www.imf.org | RSS、邮件 | 全球宏观经济权威 |
| **世界银行** | https://www.worldbank.org | RSS、邮件 | 发展中国家数据 |
| **港交所披露易** | https://www.hkexnews.hk | RSS | 港股公告官方来源 |
| **FRED** | https://fred.stlouisfed.org | RSS | 美联储经济数据，最权威 |

### Tier A: 行业信息（重点订阅）

#### 国际财经媒体

| 名称 | URL | 订阅方式 | 特点 | 费用 |
|------|-----|----------|------|------|
| **Bloomberg** | https://www.bloomberg.com | 终端/APP | 全球金融第一信源 | $24,000/年（终端） |
| **Wall Street Journal** | https://www.wsj.com | RSS、APP | 美国财经新闻旗舰 | $39.99/月 |
| **Financial Times** | https://www.ft.com | RSS、APP | 国际视角，欧洲权威 | $39/月 |
| **Reuters** | https://www.reuters.com | RSS | 新闻通讯社，最快发布 | 免费 |
| **CNBC** | https://www.cnbc.com | RSS | 实时市场，CEO 访谈 | 免费/Pro $29.99/月 |

#### 投行研究

| 投行 | 研究门户 | 获取方式 | 特点 |
|------|----------|----------|------|
| **Goldman Sachs** | https://www.goldmansachs.com/insights | 机构客户 | 宏观研究顶级 |
| **Morgan Stanley** | https://www.morganstanley.com/ideas | 机构客户 | 科技股研究强 |
| **JPMorgan** | https://www.jpmorgan.com/insights | 机构客户 | 固定收益研究强 |

#### 科技媒体（美股投资必备）

| 名称 | URL | 订阅方式 | 特点 |
|------|-----|----------|------|
| **TechCrunch** | https://techcrunch.com | RSS | 创投、初创公司权威 |
| **The Information** | https://theinformation.com | 付费订阅 | 深度科技报道，独家多 |
| **Stratechery** | https://stratechery.com | 付费订阅 | Ben Thompson 深度分析 |

#### 港股媒体

| 名称 | URL | 订阅方式 | 特点 |
|------|-----|----------|------|
| **信报** | https://www1.hkej.com | 免费+付费 | 香港财经老牌权威 |
| **经济日报** | https://www.hket.com | 免费+付费 | 投资理财实用 |
| **AAStocks** | https://www.aastocks.com | 免费 | 港股数据首选 |

### Tier B: 社区信息

| 名称 | URL | 特点 | 注意事项 |
|------|-----|------|----------|
| **Seeking Alpha** | https://seekingalpha.com | 众包分析，电话会议记录 | Premium 更有价值 |
| **Reddit r/investing** | https://www.reddit.com/r/investing | 投资者讨论 | 信息需甄别 |
| **Reddit r/wallstreetbets** | https://www.reddit.com/r/wallstreetbets | 散户情绪指标 | 高风险，谨慎参考 |
| **Value Investors Club** | https://valueinvestorsclub.com | 高质量价值投资分析 | 180 天延迟公开 |

### Tier C: 相关信息

| 名称 | 类型 | 说明 |
|------|------|------|
| **Twitter/X 财经账号** | 社交媒体 | 实时信息、市场情绪 |
| **YouTube 财经频道** | 视频平台 | 深度分析、访谈 |
| **Substack 财经通讯** | 邮件通讯 | 独立分析师观点 |

### 数据平台

| 名称 | URL | 费用 | 特点 |
|------|-----|------|------|
| **Yahoo Finance** | https://finance.yahoo.com | 免费 | 免费、API 友好 |
| **TradingView** | https://www.tradingview.com | Freemium | 图表专业 |
| **Finviz** | https://finviz.com | 免费/Elite | 筛选器强大 |
| **Trading Economics** | https://tradingeconomics.com | Freemium | 全球宏观数据 |

---

## 四、RSS 订阅清单

### AI 领域

```xml
<!-- 核心厂商 -->
<feed>https://openai.com/blog/rss.xml</feed>
<feed>https://deepmind.google/rss.xml</feed>
<feed>https://ai.meta.com/blog/rss.xml</feed>

<!-- 学术 -->
<feed>https://arxiv.org/rss/cs.AI</feed>
<feed>https://arxiv.org/rss/cs.LG</feed>
<feed>https://huggingface.co/daily-papers/rss</feed>

<!-- 媒体 -->
<feed>https://www.jiqizhixin.com/rss</feed>
<feed>https://www.qbitai.com/rss</feed>
<feed>https://www.technologyreview.com/feed/topic/artificial-intelligence</feed>
<feed>https://venturebeat.com/category/ai/feed</feed>
```

### 国内财经

```xml
<!-- 官方 -->
<feed>https://www.stats.gov.cn/rss</feed>
<feed>https://www.pbc.gov.cn/rss</feed>

<!-- 媒体 -->
<feed>https://www.caixin.com/rss/rss_finance.xml</feed>
<feed>https://www.cs.com.cn/rss</feed>
<feed>https://www.stcn.com/rss</feed>

<!-- 公告 -->
<feed>https://www.cninfo.com.cn/rss</feed>
```

### 国际财经

```xml
<!-- 官方 -->
<feed>https://www.federalreserve.gov/feeds/press_all.xml</feed>
<feed>https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&output=atom</feed>

<!-- 媒体 -->
<feed>https://www.reuters.com/finance/rss</feed>
<feed>https://www.cnbc.com/id/10000664/device/rss/rss.html</feed>
<feed>https://feeds.bbci.co.uk/news/business/rss.xml</feed>

<!-- 科技 -->
<feed>https://techcrunch.com/feed</feed>
<feed>https://venturebeat.com/feed</feed>
```

---

## 五、订阅工具推荐

| 工具 | URL | 特点 | 适用场景 |
|------|-----|------|----------|
| **Feedly** | https://feedly.com | 主流 RSS 阅读，AI 推荐 | 个人日常使用 |
| **Inoreader** | https://www.inoreader.com | 高级过滤，规则功能强 | 需要精细筛选 |
| **RSSHub** | https://docs.rsshub.app | 万物皆可 RSS | 国内外网站订阅 |
| **Pocket** | https://getpocket.com | 稍后阅读 | 离线保存 |
| **Newsletter** | 各平台邮件订阅 | 直接推送邮箱 | 不用 RSS 的信源 |

---

## 六、使用策略建议

### 信息分级策略

```
每日必看 (Tier S + Tier A 核心)
├── 官方数据发布
├── 核心媒体快讯
└── 重点厂商/投行动态

每周回顾 (Tier A + Tier B)
├── 行业深度报道
├── 研报精选
└── 社区热门讨论

每月整理 (全层级)
├── 行业报告
├── 会议论文精选
└── 投资机构观点
```

### 信息过滤原则

1. **官方优先**: 政策、数据以官方渠道为准
2. **交叉验证**: 重要信息多源比对
3. **噪音过滤**: 社区信息需辨别质量
4. **时效管理**: 快讯看速度，深度看质量
5. **成本控制**: 优先免费，按需付费

---

## 七、未来扩展

### 待添加信息源

- [ ] 产业政策追踪
- [ ] 专利数据库
- [ ] 人才流动监测
- [ ] 供应链信息
- [ ] 地缘政治风险

### 自动化采集

- [ ] RSS 自动抓取入库
- [ ] 关键词预警推送
- [ ] 信息源健康监控
- [ ] 重要性自动评分