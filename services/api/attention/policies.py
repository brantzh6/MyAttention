from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import AttentionPolicy, AttentionPolicyVersion


@dataclass(frozen=True)
class AttentionPolicySpec:
    policy_id: str
    name: str
    focus: str
    description: str
    candidate_mix_policy: dict[str, Any]
    scoring_policy: dict[str, Any]
    gate_policy: dict[str, Any]
    execution_policy: dict[str, Any]
    version: int = 1
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class AttentionDecisionResult:
    selected: list[dict[str, Any]]
    policy_id: str
    policy_version: int
    portfolio_summary: dict[str, Any]


def _is_tool_project_frontier_topic(topic: str) -> bool:
    topic_value = (topic or "").strip().lower()
    if not topic_value:
        return False
    tool_markers = (
        "framework",
        "library",
        "sdk",
        "tool",
        "project",
        "platform",
        "agent",
        "openclaw",
        "langgraph",
        "autogen",
        "crewai",
        "haystack",
    )
    research_markers = (
        "benchmark",
        "evaluation",
        "survey",
        "paper",
        "research",
        "algorithm",
        "theory",
        "scientific",
        "study",
    )
    tool_score = sum(1 for marker in tool_markers if marker in topic_value)
    research_score = sum(1 for marker in research_markers if marker in topic_value)
    return tool_score > 0 and tool_score >= research_score


DEFAULT_ATTENTION_POLICIES: tuple[AttentionPolicySpec, ...] = (
    AttentionPolicySpec(
        policy_id="source-authoritative-v1",
        name="Authoritative Source Attention V1",
        focus="authoritative",
        description="Bias toward stable authority while preserving some diversity and review candidates.",
        candidate_mix_policy={
            "bucket_order": ["authority", "research", "community", "signal", "implementation"],
            "target_mix": {"authority": 4, "research": 3, "community": 2, "signal": 1, "implementation": 1},
            "minimum_distinct_buckets": 3,
        },
        scoring_policy={"prefer_tiers": ["S", "A"], "penalize_single_bucket_domination": True},
        gate_policy={"require_authority_bucket": True, "max_single_bucket_share": 0.65},
        execution_policy={
            "default_action": "promote_authority_then_review",
            "query_templates": [
                "{topic} official organization institute standard review",
                "{topic} site:.gov OR site:.edu OR site:.org",
                "{topic} society institute authoritative source",
            ],
        },
        version=3,
        extra={"surface": "source_intelligence", "version_label": "v3"},
    ),
    AttentionPolicySpec(
        policy_id="source-latest-v1",
        name="Latest Intelligence Attention V1",
        focus="latest",
        description="Balance timely signals with enough authoritative anchors to avoid noise drift.",
        candidate_mix_policy={
            "bucket_order": ["signal", "authority", "community", "research", "implementation"],
            "target_mix": {"signal": 4, "authority": 3, "community": 2, "research": 1, "implementation": 1},
            "minimum_distinct_buckets": 3,
        },
        scoring_policy={"prefer_tiers": ["S", "A", "B"], "timeliness_bias": True},
        gate_policy={"require_authority_bucket": True, "max_single_bucket_share": 0.6},
        execution_policy={
            "default_action": "monitor_with_fast_review",
            "query_templates": [
                "{topic} latest news official",
                "{topic} release notes blog update",
                "{topic} release notes changelog announcement",
                "{topic} maintainer author x twitter linkedin",
                "{topic} hacker news discussion reddit reaction",
                "{topic} Reuters Bloomberg announcement",
            ],
        },
        version=3,
        extra={"surface": "source_intelligence", "version_label": "v3"},
    ),
    AttentionPolicySpec(
        policy_id="source-frontier-v1",
        name="Frontier Research Attention V1",
        focus="frontier",
        description="Track frontier research through labs, papers, review venues, and community discussion.",
        candidate_mix_policy={
            "bucket_order": ["research", "authority", "community", "signal", "implementation"],
            "target_mix": {"research": 4, "authority": 2, "community": 2, "signal": 2, "implementation": 1},
            "minimum_distinct_buckets": 3,
        },
        scoring_policy={"prefer_tiers": ["S", "A"], "frontier_bias": True},
        gate_policy={"require_research_bucket": "conditional", "max_single_bucket_share": 0.6},
        execution_policy={
            "default_action": "review_and_watch",
            "query_templates": [
                "{topic} frontier research lab paper",
                "{topic} arxiv openreview benchmark",
                "{topic} release notes changelog maintainers",
                "{topic} workshop conference summit speakers",
                "{topic} maintainer lead author researcher profile",
                "{topic} x twitter linkedin speaker maintainer",
                "{topic} conference speaker 2024 2025 2026",
                "{topic} hacker news discussion reddit reaction",
                "{topic} conference workshop research",
            ],
        },
        version=6,
        extra={"surface": "source_intelligence", "version_label": "v6"},
    ),
    AttentionPolicySpec(
        policy_id="source-method-v1",
        name="Method Intelligence Attention V1",
        focus="method",
        description="Prioritize implementation venues, communities, and authoritative engineering references together.",
        candidate_mix_policy={
            "bucket_order": ["implementation", "authority", "community", "research", "signal"],
            "target_mix": {"implementation": 4, "authority": 2, "community": 2, "research": 2, "signal": 1},
            "minimum_distinct_buckets": 4,
        },
        scoring_policy={"prefer_tiers": ["A", "B", "S"], "diversity_bias": True},
        gate_policy={"require_implementation_bucket": True, "max_single_bucket_share": 0.55},
        execution_policy={
            "default_action": "watch_and_subscribe_mix",
            "query_templates": [
                "{topic} github open source repository stars maintainers",
                "{topic} site:github.com framework repo awesome list",
                "{topic} github releases changelog roadmap",
                "{topic} site:github.com contributor maintainer profile",
                "{topic} site:linkedin.com/in researcher author engineer",
                "{topic} maintainer researcher speaker x twitter blog {topic}",
                "{topic} core contributor maintainer speaker profile",
                "{topic} x twitter account maintainer researcher",
                "{topic} conference speaker maintainer profile 2024 2025 2026",
                "{topic} hacker news discussion reddit reaction",
                "{topic} company lab engineering blog {topic}",
                "{topic} organization lab team maintainers",
                "{topic} reddit hacker news forum community discussion",
                "{topic} benchmark evaluation best practices implementation",
            ],
        },
        version=7,
        extra={"surface": "source_intelligence", "version_label": "v7"},
    ),
)


def get_attention_policy_specs() -> tuple[AttentionPolicySpec, ...]:
    return DEFAULT_ATTENTION_POLICIES


async def ensure_attention_policies(db: AsyncSession) -> dict[str, int]:
    existing = await db.execute(select(AttentionPolicy))
    by_policy_id = {item.policy_id: item for item in existing.scalars().all()}

    created = 0
    version_rows = 0
    updated = 0
    for spec in DEFAULT_ATTENTION_POLICIES:
        policy = by_policy_id.get(spec.policy_id)
        if policy is None:
            policy = AttentionPolicy(
                policy_id=spec.policy_id,
                name=spec.name,
                focus=spec.focus,
                description=spec.description,
                problem_type="source_intelligence",
                thinking_framework="attention_model",
                candidate_mix_policy=spec.candidate_mix_policy,
                scoring_policy=spec.scoring_policy,
                gate_policy=spec.gate_policy,
                execution_policy=spec.execution_policy,
                status="active",
                current_version=spec.version,
                latest_version=spec.version,
                extra=spec.extra or {},
            )
            db.add(policy)
            await db.flush()
            db.add(
                AttentionPolicyVersion(
                    policy_id_ref=policy.id,
                    version_number=spec.version,
                    parent_version=None,
                    change_reason="Seed default attention policy",
                    candidate_mix_policy=spec.candidate_mix_policy,
                    scoring_policy=spec.scoring_policy,
                    gate_policy=spec.gate_policy,
                    execution_policy=spec.execution_policy,
                    decision_status="accepted",
                    created_by="system",
                    accepted_at=datetime.now(timezone.utc),
                    extra=spec.extra or {},
                )
            )
            created += 1
            version_rows += 1
            continue

        current_version = int(policy.current_version or 1)
        if spec.version > current_version:
            policy.name = spec.name
            policy.focus = spec.focus
            policy.description = spec.description
            policy.problem_type = "source_intelligence"
            policy.thinking_framework = "attention_model"
            policy.candidate_mix_policy = spec.candidate_mix_policy
            policy.scoring_policy = spec.scoring_policy
            policy.gate_policy = spec.gate_policy
            policy.execution_policy = spec.execution_policy
            policy.status = "active"
            policy.current_version = spec.version
            policy.latest_version = spec.version
            policy.extra = spec.extra or {}
            db.add(
                AttentionPolicyVersion(
                    policy_id_ref=policy.id,
                    version_number=spec.version,
                    parent_version=current_version,
                    change_reason="Upgrade default attention policy specification",
                    candidate_mix_policy=spec.candidate_mix_policy,
                    scoring_policy=spec.scoring_policy,
                    gate_policy=spec.gate_policy,
                    execution_policy=spec.execution_policy,
                    decision_status="accepted",
                    created_by="system",
                    accepted_at=datetime.now(timezone.utc),
                    extra=spec.extra or {},
                )
            )
            updated += 1
            version_rows += 1

    if created or version_rows:
        await db.commit()

    return {"created_policies": created, "updated_policies": updated, "created_versions": version_rows}


async def resolve_attention_policy(db: AsyncSession, focus: Any) -> AttentionPolicy:
    await ensure_attention_policies(db)
    focus_value = getattr(focus, "value", focus)
    stmt = (
        select(AttentionPolicy)
        .where(AttentionPolicy.focus == focus_value, AttentionPolicy.status == "active")
        .order_by(AttentionPolicy.current_version.desc(), AttentionPolicy.created_at.asc())
    )
    policy = (await db.execute(stmt)).scalars().first()
    if policy is None:
        fallback_stmt = (
            select(AttentionPolicy)
            .where(AttentionPolicy.policy_id == "source-authoritative-v1")
            .order_by(AttentionPolicy.current_version.desc())
        )
        policy = (await db.execute(fallback_stmt)).scalars().first()
    if policy is None:
        raise RuntimeError("No attention policy available")
    return policy


def _bucket_for_candidate(candidate: dict[str, Any], focus_value: str) -> str:
    item_type = str(candidate.get("item_type", "")).lower()
    domain = str(candidate.get("domain", "")).lower()
    url = str(candidate.get("url", "")).lower()
    authority_tier = str(candidate.get("authority_tier", "C") or "C").upper()
    contextual_tech_media = (
        "36kr.com",
        "huxiu.com",
        "ithome.com",
        "jiqizhixin.com",
        "techcrunch.com",
        "theverge.com",
        "wired.com",
        "substack.com",
        "medium.com",
    )

    if item_type == "repository":
        return "implementation"
    if item_type == "release":
        return "signal" if focus_value in {"latest", "frontier"} else "implementation"
    if item_type == "event":
        return "research" if focus_value == "frontier" else "signal"
    if item_type == "community":
        return "community" if focus_value != "latest" else "signal"
    if item_type == "person":
        if focus_value in {"method", "frontier"}:
            return "authority" if authority_tier in {"S", "A"} else "community"
        return "community" if focus_value == "latest" else "authority"
    if item_type == "organization":
        if any(token in domain for token in ("github.com", "gitlab.com", "huggingface.co")):
            return "implementation"
        return "authority"

    if any(token in domain for token in ("github.com", "gitlab.com", "huggingface.co", "pypi.org", "npmjs.com")):
        return "implementation"
    if any(token in domain for token in ("reddit.com", "news.ycombinator.com", "lobste.rs", "x.com", "twitter.com")):
        return "community" if focus_value != "latest" else "signal"
    if any(token in domain for token in ("arxiv.org", "openreview.net", "acm.org", "ieee.org", "nature.com", "science.org")):
        return "research"
    if any(token in domain for token in contextual_tech_media):
        if focus_value in {"latest", "frontier"}:
            return "signal"
        if focus_value == "method":
            return "community"
    if authority_tier == "S" or any(token in domain for token in (".gov", ".edu", ".org", "w3.org", "oecd.org", "who.int")):
        return "authority"
    if focus_value == "latest" and any(
        token in domain for token in ("reuters.com", "bloomberg.com", "ft.com", "wsj.com", "techcrunch.com", "theverge.com")
    ):
        return "signal"
    if "blog" in domain or "blog" in url:
        return "signal"
    return "authority" if authority_tier in {"S", "A"} else "community"


def _candidate_policy_score(candidate: dict[str, Any], bucket: str, preferred_tiers: list[str]) -> float:
    tier_rank = {"S": 4.0, "A": 3.0, "B": 2.0, "C": 1.0}
    bucket_bonus = {
        "authority": 0.25,
        "research": 0.2,
        "implementation": 0.18,
        "community": 0.1,
        "signal": 0.08,
    }
    item_type = str(candidate.get("item_type", "")).lower()
    if item_type == "person":
        if bucket == "authority":
            bucket_bonus["authority"] += 0.05
        if bucket == "community":
            bucket_bonus["community"] += 0.05
    tier = str(candidate.get("authority_tier", "C") or "C").upper()
    preferred_bonus = 0.1 if tier in preferred_tiers else 0.0
    follow_score = float(candidate.get("follow_score", 0.0) or 0.0)
    follow_bonus = min(0.12, follow_score * 0.8) if item_type == "person" else 0.0
    return round(
        float(candidate.get("authority_score", 0.0) or 0.0)
        + (tier_rank.get(tier, 1.0) / 10.0)
        + bucket_bonus.get(bucket, 0.0)
        + preferred_bonus
        + follow_bonus
        + min(0.15, float(candidate.get("evidence_count", 0) or 0) * 0.03),
        4,
    )


def _candidate_identity_key(candidate: dict[str, Any]) -> str:
    object_key = str(candidate.get("object_key", "") or "").strip().lower()
    if object_key:
        return object_key
    url = str(candidate.get("url", "") or "").strip().lower()
    if url:
        return url
    domain = str(candidate.get("domain", "") or "").strip().lower()
    if domain:
        return domain
    return str(candidate.get("name", "") or "").strip().lower()


def apply_attention_policy(
    policy: AttentionPolicy,
    focus: Any,
    candidates: list[dict[str, Any]],
    limit: int,
    *,
    topic: str = "",
) -> AttentionDecisionResult:
    focus_value = getattr(focus, "value", focus)
    mix = dict(policy.candidate_mix_policy or {})
    target_mix = {str(key): int(value) for key, value in dict(mix.get("target_mix", {})).items()}
    bucket_order = [str(item) for item in list(mix.get("bucket_order", []))]
    minimum_distinct_buckets = int(mix.get("minimum_distinct_buckets", 1) or 1)
    preferred_tiers = [str(item) for item in list((policy.scoring_policy or {}).get("prefer_tiers", []))]

    bucketed: dict[str, list[tuple[float, dict[str, Any]]]] = {}
    annotated_candidates: list[tuple[float, str, dict[str, Any]]] = []
    for candidate in candidates:
        bucket = _bucket_for_candidate(candidate, focus_value)
        score = _candidate_policy_score(candidate, bucket, preferred_tiers)
        enriched = {
            **candidate,
                "object_bucket": bucket,
                "policy_id": policy.policy_id,
                "policy_version": int(policy.current_version or 1),
                "policy_score": score,
                "gate_status": "candidate",
                "selection_reason": (
                    f"bucket={bucket}; authority={candidate.get('authority_tier', 'C')}; "
                    f"evidence={candidate.get('evidence_count', 0)}"
                ),
        }
        bucketed.setdefault(bucket, []).append((score, enriched))
        annotated_candidates.append((score, bucket, enriched))

    for values in bucketed.values():
        values.sort(key=lambda item: item[0], reverse=True)

    selected: list[dict[str, Any]] = []
    used_keys: set[str] = set()
    bucket_counts: dict[str, int] = {}

    for bucket in bucket_order:
        quota = min(max(target_mix.get(bucket, 0), 0), limit)
        if quota <= 0:
            continue
        for _, candidate in bucketed.get(bucket, []):
            candidate_key = _candidate_identity_key(candidate)
            if candidate_key in used_keys:
                continue
            selected.append({**candidate, "gate_status": "selected"})
            used_keys.add(candidate_key)
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
            if bucket_counts[bucket] >= quota or len(selected) >= limit:
                break
        if len(selected) >= limit:
            break

    if len(selected) < limit:
        for _, bucket, candidate in sorted(annotated_candidates, key=lambda item: item[0], reverse=True):
            candidate_key = _candidate_identity_key(candidate)
            if candidate_key in used_keys:
                continue
            selected.append({**candidate, "gate_status": "selected"})
            used_keys.add(candidate_key)
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
            if len(selected) >= limit:
                break

    selected_bucket_count = len({candidate.get("object_bucket") for candidate in selected if candidate.get("object_bucket")})
    dominant_share = 0.0
    if selected:
        dominant_share = max(bucket_counts.values(), default=0) / len(selected)

    gate_policy = dict(policy.gate_policy or {})
    needs_review = False
    reasons: list[str] = []
    if gate_policy.get("require_authority_bucket") and bucket_counts.get("authority", 0) == 0:
        needs_review = True
        reasons.append("missing authority bucket")
    require_research_bucket = gate_policy.get("require_research_bucket")
    if require_research_bucket == "conditional":
        require_research_bucket = focus_value == "frontier" and not _is_tool_project_frontier_topic(topic)

    if require_research_bucket and bucket_counts.get("research", 0) == 0:
        needs_review = True
        reasons.append("missing research bucket")
    if gate_policy.get("require_implementation_bucket") and bucket_counts.get("implementation", 0) == 0:
        needs_review = True
        reasons.append("missing implementation bucket")
    if selected_bucket_count < minimum_distinct_buckets:
        needs_review = True
        reasons.append("insufficient source diversity across buckets")
    max_single_bucket_share = float(gate_policy.get("max_single_bucket_share", 1.0) or 1.0)
    if dominant_share > max_single_bucket_share:
        needs_review = True
        reasons.append("single bucket dominated portfolio")

    if needs_review:
        selected = [
            {**candidate, "gate_status": "needs_review"}
            for candidate in selected
        ]
    elif not reasons:
        reasons.append("portfolio satisfied current diversity and gate requirements")

    return AttentionDecisionResult(
        selected=selected[:limit],
        policy_id=policy.policy_id,
        policy_version=int(policy.current_version or 1),
        portfolio_summary={
            "bucket_counts": bucket_counts,
            "distinct_bucket_count": selected_bucket_count,
            "dominant_bucket_share": round(dominant_share, 4),
            "decision_status": "needs_review" if needs_review else "accepted",
            "reasons": reasons,
            "topic_profile": "tool_project" if focus_value == "frontier" and _is_tool_project_frontier_topic(topic) else "research_or_general",
        },
    )
