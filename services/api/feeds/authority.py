"""
信息源权威分级系统 (Authority Tier System)

基于来源的官方性、行业地位、历史积淀进行自动分级：
- Tier S: 权威官方（政府、央行、顶级学术、厂商官方）
- Tier A: 行业头部（专业媒体、行业KOL）
- Tier B: 社区平台（聚合站点、社交媒体）
- Tier C: 待评估（新增来源）
"""

import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class AuthorityResult:
    tier: str  # S, A, B, C
    score: float  # 0-1
    reason: str


class AuthorityClassifier:
    """AI 驱动的权威性分类器"""

    # === Tier S 模式：官方/权威机构 ===
    TIER_S_PATTERNS = [
        # 政府/监管
        r"\.gov\.cn$",
        r"\.gov\.\w+$",
        r"(央行|证监会|银保监会|财政部|发改委|科技部|教育部)",
        r"(fedralreserve|ecb\.europa|bankofengland)",
        # 学术
        r"arxiv\.org",
        r"(nature|science)\.com$",
        r"ieee\.org",
        r"acm\.org",
        # AI 厂商官方
        r"openai\.com",
        r"anthropic\.com",
        r"deepmind\.google",
        r"ai\.meta\.com",
        r"developer\.microsoft",
        r"cloud\.google",
        # 交易所
        r"(sec|edgar)\.gov",
        r"hkexnews\.hk",
        r"cninfo\.com",
    ]

    # === Tier A 模式：行业头部媒体 ===
    TIER_A_PATTERNS = [
        # 中文财经头部
        r"caixin\.com",
        r"cls\.cn",
        r"qbitai\.com",
        r"jiqizhixin\.com",
        r"zhidx\.com",
        r"yicai\.com",
        r"eeo\.com\.cn",
        r"21jingji\.com",
        # 中文科技
        r"36kr\.com",
        r"huxiu\.com",
        r"pingwest\.com",
        r"geekpark\.net",
        # 国际财经头部
        r"bloomberg\.com",
        r"reuters\.com",
        r"ft\.com",
        r"wsj\.com",
        r"cnbc\.com",
        r"marketwatch\.com",
        # 国际科技
        r"technologyreview\.com",
        r"theverge\.com",
        r"wired\.com",
        r"arstechnica\.com",
        r"techcrunch\.com",
    ]

    # === Tier B 模式：社区/聚合平台 ===
    TIER_B_PATTERNS = [
        r"xueqiu\.com",
        r"雪球",
        r"hackernews",
        r"reddit\.com",
        r"twitter\.com",
        r"x\.com",
        r"weibo\.com",
        r"zhihu\.com",
        r"douban\.com",
        r"medium\.com",
        r"substack\.com",
        r"huggingface\.co",
        r"github\.com",
    ]

    # 权威加成配置
    TIER_BOOST = {
        "S": 0.25,
        "A": 0.18,
        "B": 0.12,
        "C": 0.0,
    }

    def __init__(self):
        self._tier_s_re = [re.compile(p, re.I) for p in self.TIER_S_PATTERNS]
        self._tier_a_re = [re.compile(p, re.I) for p in self.TIER_A_PATTERNS]
        self._tier_b_re = [re.compile(p, re.I) for p in self.TIER_B_PATTERNS]

    def classify(self, url: str, name: str = "", category: str = "") -> AuthorityResult:
        """
        根据 URL、名称、分类进行权威性分级

        Returns:
            AuthorityResult: (tier, score, reason)
        """
        url_lower = url.lower()
        name_lower = name.lower() if name else ""
        category_lower = category.lower() if category else ""

        combined = f"{url_lower} {name_lower} {category_lower}"

        # 1. 模式匹配 Tier S
        for pattern in self._tier_s_re:
            if pattern.search(combined):
                return AuthorityResult(
                    tier="S",
                    score=0.9,
                    reason="匹配权威官方来源"
                )

        # 2. 模式匹配 Tier A
        for pattern in self._tier_a_re:
            if pattern.search(combined):
                return AuthorityResult(
                    tier="A",
                    score=0.7,
                    reason="匹配行业头部媒体"
                )

        # 3. 模式匹配 Tier B
        for pattern in self._tier_b_re:
            if pattern.search(combined):
                return AuthorityResult(
                    tier="B",
                    score=0.5,
                    reason="匹配社区/聚合平台"
                )

        # 4. 基于分类推断
        if category_lower:
            tier = self._infer_from_category(category_lower)
            if tier:
                return AuthorityResult(
                    tier=tier,
                    score=0.6,
                    reason=f"基于分类推断: {category}"
                )

        # 5. 默认 Tier C (待评估)
        return AuthorityResult(
            tier="C",
            score=0.3,
            reason="待评估"
        )

    def _infer_from_category(self, category: str) -> Optional[str]:
        """基于分类推断权威等级"""
        category_map = {
            "AI研究": "S",  # AI 研究类通常较权威
            "财经": "A",
            "海外财经": "A",
            "科技商业": "B",
            "科技资讯": "B",
            "国内": "B",
            "开发者": "B",
        }
        return category_map.get(category)

    def get_importance_boost(self, tier: str) -> float:
        """获取权威等级对应的重要性加成"""
        return self.TIER_BOOST.get(tier.upper(), 0.0)

    async def evaluate_with_ai(
        self,
        url: str,
        name: str,
        category: str,
        llm_client=None
    ) -> AuthorityResult:
        """
        使用 AI 进行更精确的权威性评估（可选）

        当模式匹配不够确定时，调用 LLM 进行评估
        """
        if llm_client is None:
            return self.classify(url, name, category)

        prompt = f"""评估以下信息来源的权威性（0-1分）：
        名称：{name}
        URL：{url}
        类别：{category}

        评估维度：
        1. 机构背书：是政府、央行、上市公司、知名研究机构吗？
        2. 历史积淀：来源存在多久了？
        3. 行业认可：在该领域的影响力如何？

        直接返回数字分数，不要其他解释。"""

        try:
            response = await llm_client.chat([
                {"role": "user", "content": prompt}
            ])
            score = float(response.content.strip())

            # 将分数映射到等级
            if score >= 0.8:
                tier = "S"
            elif score >= 0.6:
                tier = "A"
            elif score >= 0.4:
                tier = "B"
            else:
                tier = "C"

            return AuthorityResult(
                tier=tier,
                score=score,
                reason="AI 评估"
            )
        except Exception:
            # AI 评估失败，回退到模式匹配
            return self.classify(url, name, category)


# 全局单例
_classifier: Optional[AuthorityClassifier] = None


def get_authority_classifier() -> AuthorityClassifier:
    """获取权威分类器实例"""
    global _classifier
    if _classifier is None:
        _classifier = AuthorityClassifier()
    return _classifier