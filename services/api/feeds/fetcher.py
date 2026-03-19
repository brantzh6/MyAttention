"""
RSS Feed Fetcher - 多源并发抓取、解析、缓存
支持代理配置（集成 proxy-access 技能）
"""

import asyncio
import hashlib
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional

import aiohttp

from feeds.proxy_config import load_proxy_settings, normalize_proxy_mode, should_use_proxy

# 尝试导入 SOCKS 代理支持
try:
    import aiohttp_socks
    SOCKS_SUPPORT = True
except ImportError:
    SOCKS_SUPPORT = False


# 代理配置 - 基于 proxy-access 技能
# 默认代理地址，可通过环境变量覆盖
DEFAULT_HTTP_PROXY = "http://127.0.0.1:10808"
DEFAULT_SOCKS_PROXY = "socks5://127.0.0.1:10808"

# 从环境变量读取代理配置
HTTP_PROXY = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy") or DEFAULT_HTTP_PROXY
SOCKS_PROXY = os.environ.get("SOCKS_PROXY") or os.environ.get("socks_proxy") or DEFAULT_SOCKS_PROXY

# 海外源需要代理的域名列表
PROXY_DOMAINS = [
    "bloomberg.com",
    "wsj.com",
    "ft.com",
    "reuters.com",
    "cnbc.com",
    "marketwatch.com",
    "federalreserve.gov",
    "sec.gov",
    "huggingface.co",
    "technologyreview.com",
    "techcrunch.com",
    "theverge.com",
    "wired.com",
    "arstechnica.com",
    "seekingalpha.com",
    "openai.com",
    "anthropic.com",
    "deepmind.google",
    "ai.meta.com",
    "arxiv.org",
]


@dataclass
class FeedEntry:
    """单条信息流条目"""
    id: str
    title: str
    summary: str
    source_name: str
    source_id: str
    url: str
    published_at: datetime
    category: str
    importance: float = 0.5
    is_read: bool = False
    is_favorite: bool = False


@dataclass
class FeedSource:
    """RSS 信息源配置"""
    id: str
    name: str
    url: str
    category: str
    feed_type: str = "rss"          # rss | atom
    enabled: bool = True
    importance_boost: float = 0.0   # 来源的重要性加成
    tags: list = field(default_factory=list)
    proxy_mode: str = "auto"
    use_proxy: bool = False         # 是否使用代理


# ────────────────────────────────────────────────────
# 预置信息源
# 基于 MyAttention 信息源评价体系
# 分为 Tier S (权威) / Tier A (行业) / Tier B (社区) 三个层级
# ────────────────────────────────────────────────────
DEFAULT_SOURCES: list[FeedSource] = [
    # ═══════════════════════════════════════════════════════════════
    # AI 领域 - Tier S: 权威信息源 (厂商官方、顶级学术)
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="openai_blog",
        name="OpenAI Blog",
        url="https://openai.com/blog/rss.xml",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.25,
        tags=["OpenAI", "GPT", "大模型", "AGI", "权威"],
    ),
    FeedSource(
        id="anthropic",
        name="Anthropic Blog",
        url="https://www.anthropic.com/news",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.25,
        tags=["Claude", "AI安全", "大模型", "权威"],
        enabled=False,  # 暂时禁用，无RSS
    ),
    FeedSource(
        id="deepmind",
        name="Google DeepMind",
        url="https://deepmind.google/blog/rss.xml",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.22,
        tags=["DeepMind", "Google", "AlphaGo", "权威"],
    ),
    FeedSource(
        id="meta_ai",
        name="Meta AI Blog",
        url="https://ai.meta.com/blog/rss.xml",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.22,
        tags=["Meta", "LLaMA", "PyTorch", "开源", "权威"],
    ),
    FeedSource(
        id="google_ai",
        name="Google AI Blog",
        url="https://blog.google/technology/ai/rss/",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.20,
        tags=["Google", "Gemini", "AI", "权威"],
    ),
    FeedSource(
        id="arxiv_ai",
        name="arXiv cs.AI",
        url="https://rss.arxiv.org/rss/cs.AI",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.20,
        tags=["AI", "机器学习", "研究", "论文", "学术"],
    ),
    FeedSource(
        id="arxiv_cl",
        name="arXiv cs.CL (NLP)",
        url="https://rss.arxiv.org/rss/cs.CL",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.20,
        tags=["NLP", "大模型", "计算语言学", "学术"],
    ),
    FeedSource(
        id="arxiv_lg",
        name="arXiv cs.LG (ML)",
        url="https://rss.arxiv.org/rss/cs.LG",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.18,
        tags=["机器学习", "深度学习", "学术"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # AI 领域 - Tier A: 行业媒体 (中文)
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="jiqizhixin",
        name="机器之心",
        url="https://www.jiqizhixin.com/rss",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.18,
        tags=["AI", "机器学习", "深度学习", "大模型", "中文媒体"],
        enabled=False,  # RSS已失效
    ),
    FeedSource(
        id="qbitai",
        name="量子位",
        url="https://www.qbitai.com/feed",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.18,
        tags=["AI", "人工智能", "大模型", "量子计算", "中文媒体"],
    ),
    FeedSource(
        id="zhidx",
        name="新智元",
        url="https://www.zhidx.com/rss",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.16,
        tags=["AI", "大模型", "产业", "中文媒体"],
    ),
    FeedSource(
        id="aiera",
        name="AI Era",
        url="https://aiera.com.cn/feed/",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.14,
        tags=["AI", "人工智能", "大模型"],
    ),
    FeedSource(
        id="ai_tech_review",
        name="AI科技评论",
        url="https://www.leiphone.com/category/ai/rss",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.14,
        tags=["AI", "学术", "雷锋网"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # AI 领域 - Tier A: 行业媒体 (海外)
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="mit_tr_ai",
        name="MIT Technology Review AI",
        url="https://www.technologyreview.com/feed/",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.18,
        tags=["MIT", "AI", "深度报道", "权威"],
    ),
    FeedSource(
        id="venturebeat_ai",
        name="VentureBeat AI",
        url="https://venturebeat.com/category/ai/feed/",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.15,
        tags=["AI", "创业", "投资", "科技"],
    ),
    FeedSource(
        id="techcrunch_ai",
        name="TechCrunch AI",
        url="https://techcrunch.com/category/artificial-intelligence/feed/",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.14,
        tags=["AI", "创业", "投资"],
    ),
    FeedSource(
        id="wired_ai",
        name="WIRED AI",
        url="https://www.wired.com/tag/artificial-intelligence/feed/",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.13,
        tags=["AI", "科技", "未来"],
    ),
    FeedSource(
        id="the_information",
        name="The Information AI",
        url="https://theinformation.com/feed",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.16,
        tags=["AI", "科技", "深度", "独家"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # AI 领域 - Tier A: 中国大厂官方
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="alibaba_damo",
        name="阿里达摩院",
        url="https://damo.alibaba.com/rss",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.18,
        tags=["阿里", "通义千问", "大模型", "官方"],
    ),
    FeedSource(
        id="baidu_ai",
        name="百度AI",
        url="https://ai.baidu.com/feed",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.16,
        tags=["百度", "文心一言", "飞桨", "官方"],
    ),
    FeedSource(
        id="zhipu_ai",
        name="智谱AI",
        url="https://www.zhipuai.cn/rss",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.16,
        tags=["智谱", "GLM", "大模型", "国产"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # AI 领域 - Tier B: 社区平台
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="huggingface",
        name="Hugging Face Blog",
        url="https://huggingface.co/blog/feed.xml",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.16,
        tags=["开源AI", "模型", "Transformer", "社区"],
    ),
    FeedSource(
        id="paperswithcode",
        name="Papers With Code",
        url="https://paperswithcode.com/rss",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.15,
        tags=["AI", "代码", "论文", "SOTA"],
    ),
    FeedSource(
        id="thebatch",
        name="The Batch (DeepLearning.AI)",
        url="https://read.deeplearning.ai/rss/",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.16,
        tags=["AI", "深度学习", "吴恩达", "周报"],
    ),
    FeedSource(
        id="import_ai",
        name="Import AI",
        url="https://importai.substack.com/feed",
        category="AI研究",
        feed_type="rss",
        importance_boost=0.15,
        tags=["AI", "研究", "周报"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # 国内财经 - Tier S: 权威官方
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="cninfo",
        name="巨潮资讯网",
        url="https://feedx.net/rss/cninfo.xml",
        category="财经",
        feed_type="rss",
        importance_boost=0.22,
        tags=["公告", "上市公司", "权威", "官方"],
    ),
    FeedSource(
        id="csrc",
        name="证监会",
        url="https://feedx.net/rss/csrc.xml",
        category="财经",
        feed_type="rss",
        importance_boost=0.22,
        tags=["监管", "政策", "权威", "官方"],
    ),
    FeedSource(
        id="pbc",
        name="中国人民银行",
        url="https://feedx.net/rss/pbc.xml",
        category="财经",
        feed_type="rss",
        importance_boost=0.22,
        tags=["央行", "货币政策", "权威", "官方"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # 国内财经 - Tier A: 专业媒体
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="cls",
        name="财联社",
        url="https://www.cls.cn/rss",
        category="财经",
        feed_type="rss",
        importance_boost=0.20,
        tags=["快讯", "财经", "A股", "实时"],
    ),
    FeedSource(
        id="cls_telegraph",
        name="财联社电报",
        url="https://www.cls.cn/nodeapi/telegraphs/rss",
        category="财经",
        feed_type="rss",
        importance_boost=0.22,
        tags=["快讯", "紧急", "A股", "实时"],
    ),
    FeedSource(
        id="caixin",
        name="财新网",
        url="https://weekly.caixin.com/rss.xml",
        category="财经",
        feed_type="rss",
        importance_boost=0.18,
        tags=["财经", "深度", "政策"],
    ),
    FeedSource(
        id="caixin_finance",
        name="财新金融",
        url="https://weekly.caixin.com/rss/finance.xml",
        category="财经",
        feed_type="rss",
        importance_boost=0.18,
        tags=["金融", "深度", "监管"],
    ),
    FeedSource(
        id="cs_com",
        name="中国证券报",
        url="https://feedx.net/rss/chinasecurities.xml",
        category="财经",
        feed_type="rss",
        importance_boost=0.18,
        tags=["证券", "A股", "权威"],
    ),
    FeedSource(
        id="stcn",
        name="证券时报",
        url="https://www.stcn.com/rss/",
        category="财经",
        feed_type="rss",
        importance_boost=0.16,
        tags=["证券", "A股", "深市"],
    ),
    FeedSource(
        id="cnstock",
        name="上海证券报",
        url="https://www.cnstock.com/rss/",
        category="财经",
        feed_type="rss",
        importance_boost=0.16,
        tags=["证券", "A股", "沪市"],
    ),
    FeedSource(
        id="eastmoney",
        name="东方财富",
        url="https://feedx.net/rss/eastmoney.xml",
        category="财经",
        feed_type="rss",
        importance_boost=0.15,
        tags=["A股", "股市", "财经"],
    ),
    FeedSource(
        id="yicai",
        name="第一财经",
        url="https://www.yicai.com/rss/",
        category="财经",
        feed_type="rss",
        importance_boost=0.16,
        tags=["财经", "新闻", "实时"],
    ),
    FeedSource(
        id="eeo",
        name="经济观察报",
        url="https://www.eeo.com.cn/rss.xml",
        category="财经",
        feed_type="rss",
        importance_boost=0.14,
        tags=["财经", "商业", "观察"],
    ),
    FeedSource(
        id="21jingji",
        name="21世纪经济报道",
        url="https://www.21jingji.com/rss/",
        category="财经",
        feed_type="rss",
        importance_boost=0.15,
        tags=["财经", "产业", "深度"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # 国内财经 - Tier B: 社区平台
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="xueqiu",
        name="雪球热榜",
        url="https://feedx.net/rss/xueqiu.xml",
        category="财经",
        feed_type="rss",
        importance_boost=0.12,
        tags=["投资", "社区", "A股"],
    ),
    FeedSource(
        id="sina_finance",
        name="新浪财经",
        url="https://rss.sina.com.cn/finance/market.xml",
        category="财经",
        feed_type="rss",
        importance_boost=0.12,
        tags=["股市", "行情", "A股"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # 海外财经 - Tier S: 权威官方
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="federal_reserve",
        name="美联储 (Federal Reserve)",
        url="https://www.federalreserve.gov/feeds/press_all.xml",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.25,
        tags=["Fed", "利率", "货币政策", "权威"],
    ),
    FeedSource(
        id="sec_edgar",
        name="SEC EDGAR",
        url="https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&count=20&output=atom",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.22,
        tags=["SEC", "财报", "公告", "美股"],
    ),
    FeedSource(
        id="hkex_news",
        name="港交所披露易",
        url="https://www.hkexnews.hk/rss/NewlyListedNews_rss.xml",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.20,
        tags=["港股", "公告", "披露"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # 海外财经 - Tier A: 国际媒体 (需要代理)
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="bloomberg",
        name="Bloomberg Markets",
        url="https://feeds.bloomberg.com/markets/news.rss",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.20,
        tags=["美股", "全球市场", "财经"],
        use_proxy=True,
    ),
    FeedSource(
        id="bloomberg_tech",
        name="Bloomberg Technology",
        url="https://feeds.bloomberg.com/technology/news.rss",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.18,
        tags=["科技股", "美股", "科技"],
        use_proxy=True,
    ),
    FeedSource(
        id="wsj",
        name="Wall Street Journal",
        url="https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.20,
        tags=["美股", "财经", "权威"],
        use_proxy=True,
    ),
    FeedSource(
        id="reuters",
        name="Reuters Business",
        url="https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.18,
        tags=["全球", "财经", "快讯"],
        use_proxy=True,
    ),
    FeedSource(
        id="cnbc",
        name="CNBC Markets",
        url="https://www.cnbc.com/id/10000664/device/rss/rss.html",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.16,
        tags=["美股", "全球市场", "投资"],
        use_proxy=True,
    ),
    FeedSource(
        id="ft",
        name="Financial Times",
        url="https://www.ft.com/rss/home",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.18,
        tags=["全球财经", "欧洲", "权威"],
        use_proxy=True,
    ),
    FeedSource(
        id="marketwatch",
        name="MarketWatch",
        url="https://feeds.content.dowjones.io/public/rss/mw_topstories",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.15,
        tags=["美股", "道琼斯", "行情"],
        use_proxy=True,
    ),

    # ═══════════════════════════════════════════════════════════════
    # 海外财经 - Tier A: 港股媒体
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="hkej",
        name="信报 (港股)",
        url="https://www1.hkej.com/rss/onlinenews_all.xml",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.16,
        tags=["港股", "香港财经"],
    ),
    FeedSource(
        id="hket",
        name="经济日报 (港股)",
        url="https://www.hket.com/rss/",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.14,
        tags=["港股", "投资"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # 海外财经 - Tier B: 数据平台
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="wallstreetcn",
        name="华尔街见闻",
        url="https://wallstreetcn.com/rss.xml",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.14,
        tags=["全球", "财经", "宏观"],
    ),
    FeedSource(
        id="seeking_alpha",
        name="Seeking Alpha",
        url="https://seekingalpha.com/feed",
        category="海外财经",
        feed_type="rss",
        importance_boost=0.14,
        tags=["美股", "分析", "投资"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # 科技商业 - Tier A: 行业媒体
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="36kr",
        name="36氪",
        url="https://36kr.com/feed",
        category="科技商业",
        feed_type="rss",
        importance_boost=0.12,
        tags=["科技", "创业", "商业"],
    ),
    FeedSource(
        id="huxiu",
        name="虎嗅",
        url="https://rss.huxiu.com/",
        category="科技商业",
        feed_type="rss",
        importance_boost=0.12,
        tags=["商业", "科技", "深度"],
    ),
    FeedSource(
        id="pingwest",
        name="品玩",
        url="https://www.pingwest.com/feed",
        category="科技商业",
        feed_type="rss",
        importance_boost=0.10,
        tags=["科技", "商业", "创新"],
    ),
    FeedSource(
        id="geekpark",
        name="极客公园",
        url="https://www.geekpark.net/rss",
        category="科技商业",
        feed_type="rss",
        importance_boost=0.10,
        tags=["科技", "创新", "产品"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # 科技商业 - Tier A: 国际科技媒体
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="techcrunch",
        name="TechCrunch",
        url="https://techcrunch.com/feed/",
        category="国际科技",
        feed_type="rss",
        importance_boost=0.14,
        tags=["科技", "创业", "国际"],
    ),
    FeedSource(
        id="theverge",
        name="The Verge",
        url="https://www.theverge.com/rss/index.xml",
        category="国际科技",
        feed_type="rss",
        importance_boost=0.13,
        tags=["科技", "数码", "消费电子"],
    ),
    FeedSource(
        id="arstechnica",
        name="Ars Technica",
        url="https://feeds.arstechnica.com/arstechnica/index",
        category="国际科技",
        feed_type="rss",
        importance_boost=0.12,
        tags=["科技", "科学", "深度"],
    ),
    FeedSource(
        id="wired",
        name="WIRED",
        url="https://www.wired.com/feed/rss",
        category="国际科技",
        feed_type="rss",
        importance_boost=0.12,
        tags=["科技", "文化", "未来"],
    ),

    # ═══════════════════════════════════════════════════════════════
    # 综合新闻 - Tier A
    # ═══════════════════════════════════════════════════════════════
    FeedSource(
        id="thepaper",
        name="澎湃新闻",
        url="https://www.thepaper.cn/rss.xml",
        category="国内",
        feed_type="rss",
        importance_boost=0.12,
        tags=["新闻", "国内", "时政"],
    ),
    FeedSource(
        id="jiemian",
        name="界面新闻",
        url="https://www.jiemian.com/rss.xml",
        category="国内",
        feed_type="rss",
        importance_boost=0.10,
        tags=["新闻", "商业"],
    ),
    FeedSource(
        id="ithome",
        name="IT之家",
        url="https://www.ithome.com/rss/",
        category="科技资讯",
        feed_type="rss",
        importance_boost=0.08,
        tags=["科技", "数码", "互联网"],
    ),
    FeedSource(
        id="sspai",
        name="少数派",
        url="https://sspai.com/feed",
        category="效率工具",
        feed_type="rss",
        importance_boost=0.06,
        tags=["效率", "工具", "数字生活"],
    ),
]

# 分类映射 - 将详细分类映射到标准分类
CATEGORY_MAPPING = {
    # 科技类
    "科技商业": "科技",
    "科技资讯": "科技",
    "商业科技": "科技",
    "科技前沿": "科技",
    "效率工具": "科技",
    # 财经类
    "财经": "财经",
    "海外财经": "海外财经",
    # 国内
    "国内": "国内",
    # 开发者
    "开发者": "开发者",
    # AI/国际
    "AI研究": "AI研究",
    "国际科技": "国际科技",
}

def map_category(category: str) -> str:
    """将详细分类映射到标准分类"""
    return CATEGORY_MAPPING.get(category, category)
_IMPORTANCE_KEYWORDS = {
    # 紧急/突发 (最高优先级 +0.3)
    0.30: ["突发", "重磅", "紧急", "重大", "首次", "历史性", "突破", "独家",
           "Breaking", "Urgent", "Alert", "重大利好", "重大利空", "暴涨", "暴跌",
           "涨停", "跌停", "熔断", "崩盘", "创历史新高", "创历史新低"],

    # AI/科技突破 (+0.25)
    0.25: ["GPT", "GPT-4", "GPT-5", "ChatGPT", "大模型", "LLM", "AGI",
           "OpenAI", "Claude", "DeepSeek", "Kimi", "通义千问", "文心一言",
           "人工智能", "神经网络", "深度学习", "突破", "里程碑",
           "新模型发布", "AI革命", "颠覆", "Sora", "多模态"],

    # 发布/官宣 (+0.20)
    0.20: ["发布", "官宣", "推出", "上市", "IPO", "挂牌", "开盘",
           "财报", "季报", "年报", "业绩预告", "分红", "配股",
           "新产品", "新技术", "新功能", "更新"],

    # 股市/财经重要动态 (+0.18)
    0.18: ["大涨", "大跌", "暴涨", "暴跌", "跳水", "拉升", "反弹",
           "牛市", "熊市", "震荡", "突破", "支撑位", "压力位",
           "央行", "降准", "降息", "加息", "美联储", "货币政策",
           "证监会", "监管", "新规", "政策"],

    # 投资/并购 (+0.15)
    0.15: ["融资", "并购", "收购", "合并", "投资", "估值", "独角兽",
           "IPO", "上市", "挂牌", "定增", "增发", "回购"],

    # AI/科技 (+0.12)
    0.12: ["AI", "人工智能", "芯片", "GPU", "英伟达", "NVIDIA",
           "半导体", "自动驾驶", "机器人", "人形机器人", "具身智能",
           "5G", "6G", "云计算", "云原生", "量子计算", "区块链"],

    # 国际/地缘政治 (+0.15)
    0.15: ["中美", "贸易战", "制裁", "关税", "出口管制",
           "地缘政治", "冲突", "战争", "危机"],

    # 产品/品牌 (+0.10)
    0.10: ["iPhone", "华为", "小米", "特斯拉", "Tesla", "苹果", "Apple",
           "谷歌", "Google", "微软", "Microsoft", "亚马逊", "Amazon",
           "Meta", "特斯拉", "比亚迪", "蔚来", "小鹏", "理想"],

    # 开发者/技术 (+0.08)
    0.08: ["开源", "GitHub", "Python", "Rust", "Go", "Kubernetes",
           "Docker", "云原生", "DevOps", "安全漏洞", "CVE"],
}

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
}

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _clean_html(text: str) -> str:
    """移除 HTML 标签并规范空白"""
    text = _HTML_TAG_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def _make_id(source_id: str, url: str, title: str) -> str:
    raw = f"{source_id}:{url or title}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _parse_datetime(text: str) -> datetime:
    """尽力解析多种日期格式"""
    if not text:
        return datetime.now(timezone.utc)
    text = text.strip()
    # RFC 2822 (RSS standard)
    try:
        return parsedate_to_datetime(text)
    except Exception:
        pass
    # ISO 8601 / 自定义格式
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S  %z",
        "%Y-%m-%d %H:%M:%S %z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f%z",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return datetime.now(timezone.utc)


# ────────────────────────────────────────────────────
# 领域特定重要性评分配置
# ────────────────────────────────────────────────────

# AI/大模型领域关键词
_AI_KEYWORDS = {
    # 紧急/重大突破 (+0.35)
    0.35: ["GPT-5", "GPT-4.5", "AGI", "通用人工智能", "人工智能突破", "AI突破",
           "大模型突破", "模型发布", "重大更新", "里程碑", "革命性", "颠覆性",
           "ChatGPT", "Claude 4", "Claude-4", "Gemini 2", "Gemini2", "o3", "o1",
           "DeepSeek-R2", "DeepSeek-V4", "Kimi k2", "通义千问3", "文心一言5",
           "Sora", "Sora视频", "视频生成", "多模态突破"],

    # 重要发布/更新 (+0.25)
    0.25: ["OpenAI", "Anthropic", "Google AI", "DeepMind", "Meta AI",
           "百度AI", "阿里AI", "腾讯AI", "字节AI", "智谱AI", "月之暗面",
           "新模型", "模型开源", "开源大模型", "LLM", "大语言模型",
           "AI Agent", "智能体", "AI应用", "AI产品", "AI芯片",
           "NVIDIA", "英伟达", "B200", "H200", "AI算力", "算力集群"],

    # 技术进展 (+0.18)
    0.18: ["Transformer", "Attention", "MoE", "多模态", "推理能力",
           "上下文", "长文本", "RAG", "向量数据库", "Embeddings",
           "微调", "Fine-tuning", "RLHF", "对齐", "安全", "AI安全"],

    # 行业动态 (+0.12)
    0.12: ["AI融资", "AI投资", "AI初创", "独角兽", "AI公司",
           "人工智能公司", "大模型公司", "AI创业", "AI估值", "AI营收"],
}

# 财经/股市领域关键词
_FINANCE_KEYWORDS = {
    # 紧急/重大政策 (+0.35)
    0.35: ["降准", "降息", "加息", "央行", "美联储", "FOMC", "利率决议",
           "重大利好", "重大利空", "暴涨", "暴跌", "熔断", "崩盘",
           "涨停潮", "跌停潮", "千股涨停", "千股跌停", "救市", "国家队",
           "财报超预期", "业绩暴增", "巨亏", "暴雷", "ST", "退市"],

    # 重要市场动态 (+0.25)
    0.25: ["A股", "港股", "美股", "纳斯达克", "道琼斯", "标普500",
           "上证指数", "深证成指", "创业板指", "科创板", "北交所",
           "牛市", "熊市", "突破", "创新高", "创新低", "放量", "缩量",
           "南向资金", "北向资金", "外资流入", "外资流出", "主力资金"],

    # 公司/行业 (+0.18)
    0.18: ["IPO", "上市", "新股", "次新股", "定增", "增发", "配股",
           "回购", "增持", "减持", "减持计划", "举牌", "要约收购",
           "并购重组", "重大资产重组", "借壳上市", "分拆上市",
           "季报", "年报", "中报", "业绩预告", "业绩快报"],

    # 宏观/政策 (+0.15)
    0.15: ["GDP", "CPI", "PPI", "PMI", "通胀", "通缩", "失业率",
           "财政政策", "货币政策", "监管", "证监会", "银保监会",
           "新规", "新政", "政策落地", "行业政策", "产业政策"],

    # 板块/概念 (+0.12)
    0.12: ["科技股", "AI概念股", "芯片股", "新能源", "光伏", "锂电",
           "医药", "白酒", "银行", "券商", "保险", "地产", "中字头"],
}

# 海外财经关键词
_GLOBAL_FINANCE_KEYWORDS = {
    # 全球市场重大事件 (+0.35)
    0.35: ["Fed", "Federal Reserve", "ECB", "BOE", "Interest Rate",
           "Rate Cut", "Rate Hike", "QE", "QT", "Recession", "Crisis",
           "Market Crash", "Flash Crash", "Circuit Breaker", "Black Monday"],

    # 美股重要动态 (+0.25)
    0.25: ["S&P 500", "Nasdaq", "Dow Jones", "Russell 2000", "VIX",
           "Apple", "Tesla", "NVIDIA", "Microsoft", "Google", "Amazon",
           "Meta", "Berkshire", "ETF", "ARK", "Cathie Wood",
           "Earnings Beat", "Earnings Miss", "Record High", "All-Time High"],

    # 商品/外汇 (+0.18)
    0.18: ["Gold", "Silver", "Crude Oil", "Brent", "WTI", "OPEC",
           "Bitcoin", "BTC", "Ethereum", "ETH", "Crypto", "Digital Currency",
           "USD", "DXY", "EUR/USD", "Fed Rate", "Treasury Yield", "10-Year"],
}

# 科技领域关键词
_TECH_KEYWORDS = {
    # 重大产品发布 (+0.30)
    0.30: ["iPhone", "iPad", "MacBook", "Apple Watch", "Vision Pro",
           "华为Mate", "华为P系列", "小米", "Xiaomi", "三星Galaxy",
           "特斯拉", "Model Y", "Model 3", "Cybertruck", "FSD",
           "新品发布", "新品上市", "重磅产品", "年度旗舰"],

    # 芯片/半导体 (+0.25)
    0.25: ["台积电", "TSMC", "ASML", "光刻机", "3nm", "2nm", "先进制程",
           "芯片突破", "国产芯片", "光刻胶", "EDA", "Chiplet", "先进封装",
           "英伟达", "NVIDIA", "AMD", "Intel", "高通", "华为麒麟"],

    # 前沿技术 (+0.18)
    0.18: ["量子计算", "Quantum", "核聚变", "可控核聚变", "6G", "5G-A",
           "具身智能", "人形机器人", "自动驾驶", "Robotaxi", "SpaceX",
           "星舰", "Starship", "火星", "脑机接口", "Neuralink"],
}


def _score_importance_by_domain(title: str, summary: str, category: str, boost: float) -> float:
    """按领域计算重要性评分"""
    title_text = f" {title} " * 3  # 标题权重更高
    summary_text = f" {summary} "
    combined = (title_text + summary_text).lower()

    # 基础分 + 来源加成
    score = 0.5 + boost

    # 选择对应领域的关键词配置
    domain_keywords = None
    if category in ["AI研究", "科技", "科技商业", "科技资讯", "商业科技", "科技前沿"]:
        # AI和科技类合并处理，但AI源用更多AI关键词
        domain_keywords = _AI_KEYWORDS
    elif category == "财经":
        domain_keywords = _FINANCE_KEYWORDS
    elif category == "海外财经":
        # 合并海外财经和通用财经关键词
        domain_keywords = {**_GLOBAL_FINANCE_KEYWORDS, **_FINANCE_KEYWORDS}
    elif category == "国际科技":
        domain_keywords = {**_TECH_KEYWORDS, **_AI_KEYWORDS}
    else:
        domain_keywords = _TECH_KEYWORDS

    # 计算关键词匹配得分
    matched_keywords = set()
    for weight, keywords in domain_keywords.items():
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in combined:
                # 避免同一关键词重复计分
                if kw_lower not in matched_keywords:
                    score += weight
                    matched_keywords.add(kw_lower)
                    # 标题匹配额外加分
                    if kw_lower in title_text.lower():
                        score += weight * 0.4

    # 通用紧急关键词（所有领域适用）
    urgent_keywords = ["突发", "breaking", "紧急", "urgent", "exclusive", "独家"]
    for kw in urgent_keywords:
        if kw.lower() in combined:
            score += 0.25

    return min(score, 1.0)


# 保留旧函数名兼容
_score_importance = _score_importance_by_domain


# ────────────────────────────────────────────────────
# Feed parser
# ────────────────────────────────────────────────────

def _parse_rss_xml(xml_text: str, source: FeedSource, limit: int = 20) -> list[FeedEntry]:
    """解析 RSS 2.0 / Atom XML，返回 FeedEntry 列表"""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    entries: list[FeedEntry] = []

    # RSS 2.0: <channel><item>...</item></channel>
    items = root.findall(".//item")

    # Atom: <feed><entry>...</entry></feed>
    if not items:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//atom:entry", ns)
        if not items:
            # Try without namespace
            items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    for item in items[:limit]:
        # NOTE: Element.__bool__ is False when it has no children,
        #       so always use `x is not None` instead of `x or fallback`.

        def _find(tag: str, *alt_tags: str) -> Optional[ET.Element]:
            el = item.find(tag)
            if el is not None:
                return el
            for t in alt_tags:
                el = item.find(t)
                if el is not None:
                    return el
            return None

        # ── 标题 ──
        title_el = _find("title", "{http://www.w3.org/2005/Atom}title")
        title = _clean_html(title_el.text) if title_el is not None and title_el.text else ""
        if not title:
            continue

        # ── 摘要 ──
        desc_el = _find(
            "description", "summary",
            "{http://www.w3.org/2005/Atom}summary",
            "{http://www.w3.org/2005/Atom}content",
        )
        summary = ""
        if desc_el is not None and desc_el.text:
            summary = _clean_html(desc_el.text)
            if len(summary) > 200:
                summary = summary[:200] + "..."

        # ── 链接 ──
        link_el = _find("link", "{http://www.w3.org/2005/Atom}link")
        url = ""
        if link_el is not None:
            url = link_el.get("href") or (link_el.text.strip() if link_el.text else "")

        # ── 发布时间 ──
        pub_el = _find(
            "pubDate", "published",
            "{http://www.w3.org/2005/Atom}published",
            "{http://www.w3.org/2005/Atom}updated",
        )
        published_at = _parse_datetime(pub_el.text if pub_el is not None else "")

        # ── 重要性 ──
        importance = _score_importance(title, summary, source.category, source.importance_boost)

        entry = FeedEntry(
            id=_make_id(source.id, url, title),
            title=title,
            summary=summary,
            source_name=source.name,
            source_id=source.id,
            url=url,
            published_at=published_at,
            category=source.category,
            importance=round(importance, 2),
        )
        entries.append(entry)

    return entries


# ────────────────────────────────────────────────────
# Fetcher (async, with caching)
# ────────────────────────────────────────────────────

_SOURCES_CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "feed_sources.json"


def _clone_default_sources() -> list[FeedSource]:
    return [FeedSource(**asdict(source)) for source in DEFAULT_SOURCES]


def _source_from_dict(data: dict) -> FeedSource:
    proxy_mode = normalize_proxy_mode(data.get("proxy_mode"), bool(data.get("use_proxy")))
    return FeedSource(
        id=str(data["id"]),
        name=str(data["name"]),
        url=str(data["url"]),
        category=str(data.get("category") or ""),
        feed_type=str(data.get("feed_type") or "rss"),
        enabled=bool(data.get("enabled", True)),
        importance_boost=float(data.get("importance_boost", 0.0) or 0.0),
        tags=list(data.get("tags") or []),
        proxy_mode=proxy_mode,
        use_proxy=proxy_mode == "always",
    )


def _source_to_dict(source: FeedSource) -> dict:
    payload = asdict(source)
    payload["proxy_mode"] = normalize_proxy_mode(source.proxy_mode, source.use_proxy)
    payload["use_proxy"] = payload["proxy_mode"] == "always"
    return payload


class FeedFetcher:
    """多源并发抓取器，带内存缓存"""

    def __init__(self, sources: list[FeedSource] | None = None, cache_ttl: int = 300):
        default_sources = sources or _clone_default_sources()
        self.sources = self._load_sources(default_sources)
        self.cache_ttl = cache_ttl          # 缓存有效期（秒）
        self._cache: dict[str, tuple[float, list[FeedEntry]]] = {}

    def _load_sources(self, default_sources: list[FeedSource]) -> list[FeedSource]:
        if not _SOURCES_CONFIG_PATH.exists():
            return default_sources

        try:
            raw = json.loads(_SOURCES_CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                loaded = [_source_from_dict(item) for item in raw if isinstance(item, dict)]
                if loaded:
                    return loaded
        except Exception as exc:
            print(f"[FeedFetcher] failed to load source config: {exc}")
        return default_sources

    def _save_sources(self) -> None:
        try:
            _SOURCES_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            payload = [_source_to_dict(source) for source in self.sources]
            _SOURCES_CONFIG_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            print(f"[FeedFetcher] failed to save source config: {exc}")

    async def _fetch_one(
        self,
        session: aiohttp.ClientSession,
        source: FeedSource,
    ) -> list[FeedEntry]:
        """抓取单个源，支持 SOCKS5/HTTP 代理"""
        # 检查缓存
        cached = self._cache.get(source.id)
        if cached and (time.time() - cached[0]) < self.cache_ttl:
            return cached[1]

        # 确定是否需要代理
        need_proxy = source.use_proxy
        if not need_proxy:
            # 自动检测是否需要代理（根据域名）
            for domain in PROXY_DOMAINS:
                if domain in source.url:
                    need_proxy = True
                    break

        # 尝试获取内容
        xml_text = None

        if need_proxy:
            # 使用代理访问
            print(f"[FeedFetcher] {source.name} using proxy")

            # 优先尝试 SOCKS 代理（更稳定）
            if SOCKS_SUPPORT:
                try:
                    connector = aiohttp_socks.ProxyConnector.from_url(SOCKS_PROXY)
                    async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as proxy_session:
                        async with proxy_session.get(
                            source.url,
                            headers=_HEADERS,
                            ssl=False,
                        ) as resp:
                            if resp.status == 200:
                                xml_text = await resp.text()
                                print(f"[FeedFetcher] {source.name} fetched via SOCKS proxy")
                except Exception as e:
                    print(f"[FeedFetcher] {source.name} SOCKS proxy failed: {e}")

            # 如果 SOCKS 失败，尝试 HTTP 代理
            if xml_text is None:
                try:
                    async with session.get(
                        source.url,
                        timeout=aiohttp.ClientTimeout(total=10, connect=5),
                        headers=_HEADERS,
                        ssl=False,
                        proxy=HTTP_PROXY,
                    ) as resp:
                        if resp.status == 200:
                            xml_text = await resp.text()
                            print(f"[FeedFetcher] {source.name} fetched via HTTP proxy")
                except Exception as e:
                    print(f"[FeedFetcher] {source.name} HTTP proxy failed: {e}")
        else:
            # 直接访问（国内源）
            try:
                async with session.get(
                    source.url,
                    timeout=aiohttp.ClientTimeout(total=8, connect=3),
                    headers=_HEADERS,
                    ssl=False,
                ) as resp:
                    if resp.status == 200:
                        xml_text = await resp.text()
            except asyncio.TimeoutError:
                print(f"[FeedFetcher] {source.name} timeout")
                return cached[1] if cached else []
            except Exception as e:
                print(f"[FeedFetcher] {source.name} fetch error: {e}")
                return cached[1] if cached else []

        if xml_text is None:
            return cached[1] if cached else []

        entries = _parse_rss_xml(xml_text, source)
        self._cache[source.id] = (time.time(), entries)
        print(f"[FeedFetcher] {source.name}: fetched {len(entries)} entries")
        return entries

    async def _fetch_one(
        self,
        session: aiohttp.ClientSession,
        source: FeedSource,
    ) -> list[FeedEntry]:
        """Fetch a single source with optional proxy support."""
        cached = self._cache.get(source.id)
        if cached and (time.time() - cached[0]) < self.cache_ttl:
            return cached[1]

        proxy_settings = load_proxy_settings()
        source.proxy_mode = normalize_proxy_mode(source.proxy_mode, source.use_proxy)
        source.use_proxy = source.proxy_mode == "always"
        need_proxy, proxy_reason = should_use_proxy(
            source.url,
            source.proxy_mode,
            proxy_settings,
            PROXY_DOMAINS,
        )
        http_proxy = proxy_settings.get("http_proxy") or HTTP_PROXY
        socks_proxy = proxy_settings.get("socks_proxy") or SOCKS_PROXY
        if need_proxy and not http_proxy and not socks_proxy:
            print(f"[FeedFetcher] {source.name} proxy requested but not configured, fallback direct")
            need_proxy = False

        xml_text = None

        if need_proxy:
            print(f"[FeedFetcher] {source.name} using proxy ({proxy_reason})")

            if SOCKS_SUPPORT and socks_proxy:
                try:
                    connector = aiohttp_socks.ProxyConnector.from_url(socks_proxy)
                    async with aiohttp.ClientSession(
                        connector=connector,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as proxy_session:
                        async with proxy_session.get(
                            source.url,
                            headers=_HEADERS,
                            ssl=False,
                        ) as resp:
                            if resp.status == 200:
                                xml_text = await resp.text()
                                print(f"[FeedFetcher] {source.name} fetched via SOCKS proxy")
                except Exception as exc:
                    print(f"[FeedFetcher] {source.name} SOCKS proxy failed: {exc}")

            if xml_text is None and http_proxy:
                try:
                    async with session.get(
                        source.url,
                        timeout=aiohttp.ClientTimeout(total=10, connect=5),
                        headers=_HEADERS,
                        ssl=False,
                        proxy=http_proxy,
                    ) as resp:
                        if resp.status == 200:
                            xml_text = await resp.text()
                            print(f"[FeedFetcher] {source.name} fetched via HTTP proxy")
                except Exception as exc:
                    print(f"[FeedFetcher] {source.name} HTTP proxy failed: {exc}")

            if xml_text is None:
                print(f"[FeedFetcher] {source.name} proxy fetch failed, fallback direct")

        if xml_text is None:
            try:
                async with session.get(
                    source.url,
                    timeout=aiohttp.ClientTimeout(total=8, connect=3),
                    headers=_HEADERS,
                    ssl=False,
                ) as resp:
                    if resp.status == 200:
                        xml_text = await resp.text()
            except asyncio.TimeoutError:
                print(f"[FeedFetcher] {source.name} timeout")
                return cached[1] if cached else []
            except Exception as exc:
                print(f"[FeedFetcher] {source.name} fetch error: {exc}")
                return cached[1] if cached else []

        if xml_text is None:
            return cached[1] if cached else []

        entries = _parse_rss_xml(xml_text, source)
        self._cache[source.id] = (time.time(), entries)
        print(f"[FeedFetcher] {source.name}: fetched {len(entries)} entries")
        return entries

    async def fetch_all(self, limit_per_source: int = 50) -> list[FeedEntry]:
        """并发抓取所有启用的源（限制并发数），合并后按时间排序。"""
        enabled = [s for s in self.sources if s.enabled]

        all_entries: list[FeedEntry] = []

        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(12)  # 最多12个并发请求

        async def fetch_with_limit(session, source):
            async with semaphore:
                return await self._fetch_one(session, source)

        # Fetch from registered sources
        if enabled:
            async with aiohttp.ClientSession() as session:
                tasks = [fetch_with_limit(session, src) for src in enabled]
                results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, list):
                    all_entries.extend(result[:limit_per_source])

        # Include imported items from cache
        registered_ids = {s.id for s in self.sources}
        for source_key, (ts, entries) in self._cache.items():
            if source_key not in registered_ids:
                all_entries.extend(entries[:limit_per_source])

        # 按发布时间倒序
        all_entries.sort(key=lambda e: e.published_at, reverse=True)
        return all_entries

    async def fetch_by_source(self, source_id: str) -> list[FeedEntry]:
        """抓取指定源，also checks imported cache"""
        source = next((s for s in self.sources if s.id == source_id), None)
        if source:
            async with aiohttp.ClientSession() as session:
                return await self._fetch_one(session, source)
        
        # Check if source_id exists in imported cache
        cached = self._cache.get(source_id)
        if cached:
            return cached[1]
        return []

    def get_sources(self) -> list[FeedSource]:
        return list(self.sources)

    def add_source(self, source: FeedSource) -> None:
        source.proxy_mode = normalize_proxy_mode(source.proxy_mode, source.use_proxy)
        source.use_proxy = source.proxy_mode == "always"
        self.sources.append(source)
        self._save_sources()

    def remove_source(self, source_id: str) -> bool:
        before = len(self.sources)
        self.sources = [s for s in self.sources if s.id != source_id]
        changed = len(self.sources) < before
        if changed:
            self._cache.pop(source_id, None)
            self._save_sources()
        return changed

    def toggle_source(self, source_id: str) -> Optional[bool]:
        for s in self.sources:
            if s.id == source_id:
                s.enabled = not s.enabled
                self._save_sources()
                return s.enabled
        return None

    def update_source_proxy_mode(self, source_id: str, proxy_mode: str) -> Optional[FeedSource]:
        normalized = normalize_proxy_mode(proxy_mode)
        for source in self.sources:
            if source.id == source_id:
                source.proxy_mode = normalized
                source.use_proxy = normalized == "always"
                self._cache.pop(source_id, None)
                self._save_sources()
                return source
        return None


# 全局单例
_fetcher: FeedFetcher | None = None


def get_feed_fetcher() -> FeedFetcher:
    """Get or create FeedFetcher instance, reload if sources changed"""
    global _fetcher
    if _fetcher is None:
        _fetcher = FeedFetcher()
    return _fetcher


def reload_feed_fetcher() -> FeedFetcher:
    """Force reload feed fetcher with new sources"""
    global _fetcher
    _fetcher = FeedFetcher()
    return _fetcher
