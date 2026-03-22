import asyncio
import hashlib

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from enum import Enum
from urllib.parse import urlparse

from sqlalchemy import String as SqlString, cast, or_, select
from sqlalchemy.orm import joinedload

from config import get_settings
from attention import apply_attention_policy, resolve_attention_policy
from db.models import FeedItem as FeedItemModel
from db.models import Source as SourceModel
from db.models import AttentionPolicy as AttentionPolicyModel
from db.models import SourcePlan as SourcePlanModel
from db.models import SourcePlanItem as SourcePlanItemModel
from db.models import SourcePlanVersion as SourcePlanVersionModel
from feeds.fetcher import PROXY_DOMAINS, get_feed_fetcher, FeedSource as _FeedSource, FeedEntry, reload_feed_fetcher, map_category, reload_feed_fetcher
from feeds.authority import get_authority_classifier
from feeds.persistence import (
    build_import_feed_extra,
    build_import_source_url,
    persist_import_feed_item,
    resolve_source_for_import,
)
from feeds.proxy_config import load_proxy_settings, normalize_proxy_mode, should_use_proxy
from feeds.raw_ingest import persist_import_item_raw
from knowledge.web_search import AliyunWebSearch
from db import get_db, AsyncSession

router = APIRouter()


# ── Response models ──────────────────────────────────

class SourceType(str, Enum):
    RSS = "rss"
    WEB = "web"
    API = "api"


class SourceStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


class ProxyMode(str, Enum):
    AUTO = "auto"
    ALWAYS = "always"
    NEVER = "never"


class Source(BaseModel):
    id: str
    name: str
    type: SourceType
    url: str
    category: str
    tags: List[str] = []
    enabled: bool = True
    status: SourceStatus = SourceStatus.OK
    last_fetched: Optional[datetime] = None
    success_rate: float = 100.0
    proxy_mode: ProxyMode = ProxyMode.AUTO
    proxy_effective: bool = False
    proxy_reason: str = "direct"


class SourceCreate(BaseModel):
    name: str
    type: SourceType = SourceType.RSS
    url: str
    category: str
    tags: List[str] = []
    enabled: bool = True
    proxy_mode: ProxyMode = ProxyMode.AUTO


class SourceProxyUpdate(BaseModel):
    proxy_mode: ProxyMode


class FeedItem(BaseModel):
    id: str
    title: str
    summary: str
    source: str
    source_id: str
    source_type: SourceType
    url: str
    published_at: datetime
    category: str
    importance: float
    is_read: bool = False
    is_favorite: bool = False


class FeedsReadBackend(str, Enum):
    CACHE = "cache"
    DB = "db"
    HYBRID = "hybrid"


class SourceDiscoveryFocus(str, Enum):
    LATEST = "latest"
    AUTHORITATIVE = "authoritative"
    FRONTIER = "frontier"
    METHOD = "method"


class SourceDiscoveryRequest(BaseModel):
    topic: str = Field(..., min_length=2, description="需要研究或持续关注的主题")
    focus: SourceDiscoveryFocus = Field(SourceDiscoveryFocus.AUTHORITATIVE, description="发现目标")
    limit: int = Field(12, ge=3, le=30, description="返回候选源数量")


class SourceDiscoveryCandidate(BaseModel):
    item_type: str = "domain"
    object_key: str = ""
    domain: str
    name: str
    url: str
    authority_tier: str
    authority_score: float
    recommendation: str
    recommendation_reason: str
    evidence_count: int
    matched_queries: List[str]
    sample_titles: List[str]
    sample_snippets: List[str]
    object_bucket: str = "authority"
    policy_id: str = ""
    policy_version: int = 1
    policy_score: float = 0.0
    gate_status: str = "candidate"
    selection_reason: str = ""


class SourceDiscoveryResponse(BaseModel):
    topic: str
    focus: SourceDiscoveryFocus
    queries: List[str]
    policy_id: str = ""
    policy_version: int = 1
    portfolio_summary: Dict[str, Any] = {}
    candidates: List[SourceDiscoveryCandidate]


class SourcePlanCreateRequest(BaseModel):
    topic: str = Field(..., min_length=2, description="需要持续跟踪的主题")
    focus: SourceDiscoveryFocus = Field(SourceDiscoveryFocus.AUTHORITATIVE, description="建源重点")
    objective: str = Field("", description="为什么要关注这个主题")
    limit: int = Field(12, ge=3, le=30)
    review_cadence_days: int = Field(14, ge=1, le=180)


class SourcePlanItemResponse(BaseModel):
    id: str
    item_type: str
    object_key: str
    name: str
    url: str
    authority_tier: str
    authority_score: float
    monitoring_mode: str
    execution_strategy: str
    review_cadence_days: int
    rationale: str
    status: str
    evidence: Dict[str, Any]
    object_bucket: str = ""
    gate_status: str = ""
    selection_reason: str = ""


class SourcePlanResponse(BaseModel):
    id: str
    topic: str
    focus: str
    objective: str
    planning_brain: str
    status: str
    review_status: str
    review_cadence_days: int
    current_version: int = 1
    latest_version: int = 1
    policy_id: str = ""
    policy_version: int = 1
    policy_name: str = ""
    policy_decision_status: str = ""
    last_reviewed_at: Optional[datetime] = None
    next_review_due_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[SourcePlanItemResponse] = []


class SourcePlanVersionResponse(BaseModel):
    id: str
    version_number: int
    parent_version: Optional[int] = None
    trigger_type: str
    decision_status: str
    change_reason: str = ""
    change_summary: Dict[str, Any] = {}
    evaluation: Dict[str, Any] = {}
    created_by: str
    accepted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


# ── Import models ────────────────────────────────────

class ImportItem(BaseModel):
    """Single item from info-processor output."""
    id: str
    title: str
    link: str = ""
    summary: str = ""
    content: str = ""
    source: str = ""
    source_name: str = ""
    source_type: str = "rss"
    category: str = ""
    category_name: str = ""
    secondary_tags: List[str] = []
    urgency: float = 0.5
    urgency_factors: Dict[str, Any] = {}
    language: str = "zh"
    published_at: Optional[str] = None
    processed_at: Optional[str] = None
    metadata: Dict[str, Any] = {}


class FeedsImportRequest(BaseModel):
    """Batch import request from info-processor."""
    items: List[ImportItem]
    stats: Dict[str, Any] = {}


class FeedsImportResponse(BaseModel):
    """Import result summary."""
    status: str
    imported: int = 0
    persisted: int = 0
    duplicates: int = 0
    errors: int = 0
    items: List[str] = Field(default_factory=list, description="IDs of imported items")


# ── Endpoints ────────────────────────────────────────

def _source_to_api_model(source: _FeedSource) -> Source:
    proxy_settings = load_proxy_settings()
    proxy_mode = normalize_proxy_mode(getattr(source, "proxy_mode", None), getattr(source, "use_proxy", False))
    proxy_effective, proxy_reason = should_use_proxy(
        source.url,
        proxy_mode,
        proxy_settings,
        PROXY_DOMAINS,
    )
    success_count = max(0, int(getattr(source, "success_count", 0) or 0))
    failure_count = max(0, int(getattr(source, "failure_count", 0) or 0))
    total_attempts = success_count + failure_count
    success_rate = 100.0 if total_attempts == 0 else round((success_count / total_attempts) * 100.0, 2)
    status_value = getattr(source, "status", SourceStatus.OK.value)
    try:
        status = SourceStatus(status_value)
    except ValueError:
        status = SourceStatus.OK

    return Source(
        id=str(source.id),
        name=source.name,
        type=SourceType(getattr(source, "type", SourceType.RSS.value)),
        url=source.url,
        category=source.category or "",
        tags=list(getattr(source, "tags", []) or []),
        enabled=bool(getattr(source, "enabled", True)),
        status=status,
        last_fetched=getattr(source, "last_fetched", None),
        success_rate=success_rate,
        proxy_mode=ProxyMode(proxy_mode),
        proxy_effective=proxy_effective,
        proxy_reason=proxy_reason,
    )


def _normalize_domain(value: str) -> str:
    parsed = urlparse(value if "://" in value else f"https://{value}")
    domain = parsed.netloc or parsed.path
    return domain.lower().removeprefix("www.")


def _candidate_identity(url: str, focus: SourceDiscoveryFocus) -> tuple[str, str, str, str, str]:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    domain = _normalize_domain(parsed.netloc or parsed.path)
    path_segments = [segment for segment in (parsed.path or "").split("/") if segment]

    if domain in {"github.com", "gitlab.com"} and len(path_segments) >= 2:
        owner, repo = path_segments[0], path_segments[1]
        object_key = f"{domain}/{owner}/{repo}".lower()
        canonical_url = f"https://{domain}/{owner}/{repo}"
        display_name = f"{owner}/{repo}"
        return "repository", object_key, display_name, canonical_url, domain

    if domain == "huggingface.co" and len(path_segments) >= 2:
        owner, repo = path_segments[0], path_segments[1]
        object_key = f"{domain}/{owner}/{repo}".lower()
        canonical_url = f"https://{domain}/{owner}/{repo}"
        display_name = f"{owner}/{repo}"
        return "repository", object_key, display_name, canonical_url, domain

    if domain == "reddit.com" and len(path_segments) >= 2 and path_segments[0].lower() == "r":
        community = path_segments[1]
        object_key = f"{domain}/r/{community}".lower()
        canonical_url = f"https://{domain}/r/{community}"
        display_name = f"r/{community}"
        return "community", object_key, display_name, canonical_url, domain

    if domain in {"x.com", "twitter.com"} and path_segments:
        handle = path_segments[0]
        if handle.lower() not in {"home", "search", "explore", "i", "settings", "messages"}:
            object_key = f"{domain}/{handle}".lower()
            canonical_url = f"https://{domain}/{handle}"
            display_name = f"@{handle}"
            return "person", object_key, display_name, canonical_url, domain

    object_key = domain.lower()
    canonical_url = url if url.startswith("http") else f"https://{domain}"
    return "domain", object_key, domain, canonical_url, domain


def _normalize_plan_topic(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _topic_merge_key(value: str) -> str:
    normalized = _normalize_plan_topic(value)
    compact = "".join(normalized.split())
    return compact or normalized


def _source_plan_match_score(plan: SourcePlanModel) -> tuple[int, int, datetime]:
    return (
        int(plan.current_version or 0),
        len(list(plan.items or [])),
        plan.updated_at or plan.created_at or datetime.min.replace(tzinfo=timezone.utc),
    )


def _source_plan_owner_key(topic: str, focus: SourceDiscoveryFocus | str) -> str:
    focus_value = focus.value if isinstance(focus, SourceDiscoveryFocus) else str(focus)
    topic_key = _topic_merge_key(topic)
    digest = hashlib.sha1(f"{focus_value}:{topic_key}".encode("utf-8")).hexdigest()[:16]
    return f"source-plan:{focus_value}:{digest}"


def _discovery_queries(topic: str, focus: SourceDiscoveryFocus, execution_policy: Optional[Dict[str, Any]] = None) -> list[str]:
    topic = topic.strip()
    query_templates = list(dict(execution_policy or {}).get("query_templates", []))
    if query_templates:
        rendered = []
        for template in query_templates:
            query = str(template).format(topic=topic).strip()
            if query and query not in rendered:
                rendered.append(query)
        if rendered:
            return rendered
    if focus == SourceDiscoveryFocus.LATEST:
        return [
            f"{topic} 最新 动态 官方",
            f"{topic} latest news official",
            f"{topic} release notes blog",
        ]
    if focus == SourceDiscoveryFocus.FRONTIER:
        return [
            f"{topic} frontier research lab paper",
            f"{topic} 最新 研究 论文 实验室",
            f"{topic} conference workshop research",
        ]
    if focus == SourceDiscoveryFocus.METHOD:
        return [
            f"{topic} open source framework github docs",
            f"{topic} skill workflow agent community",
            f"{topic} best practices benchmark",
        ]
    return [
        f"{topic} 官方 权威 机构",
        f"{topic} authoritative source organization",
        f"{topic} review standard society institute",
    ]


def _discovery_recommendation(
    focus: SourceDiscoveryFocus,
    tier: str,
    evidence_count: int,
) -> tuple[str, str]:
    if tier == "S":
        return "subscribe", "权威等级高，适合作为长期关注对象"
    if focus in {SourceDiscoveryFocus.FRONTIER, SourceDiscoveryFocus.METHOD} and tier == "A" and evidence_count >= 2:
        return "subscribe", "在前沿或方法情报场景下，多次命中，适合长期观察"
    if focus == SourceDiscoveryFocus.LATEST and tier in {"A", "B"}:
        return "monitor", "适合作为动态观察源，但需继续校准其质量"
    if tier == "A":
        return "monitor", "具备一定权威性，建议先纳入观察而非直接固化"
    return "review", "候选源价值未稳定，建议人工复核或继续搜索"


def _focus_category(focus: SourceDiscoveryFocus) -> str:
    if focus == SourceDiscoveryFocus.METHOD:
        return "开发者"
    if focus == SourceDiscoveryFocus.FRONTIER:
        return "AI研究"
    if focus == SourceDiscoveryFocus.LATEST:
        return "科技"
    return "AI研究"


def _candidate_to_attention_payload(candidate: SourceDiscoveryCandidate) -> Dict[str, Any]:
    return {
        "item_type": candidate.item_type,
        "object_key": candidate.object_key,
        "domain": candidate.domain,
        "name": candidate.name,
        "url": candidate.url,
        "authority_tier": candidate.authority_tier,
        "authority_score": candidate.authority_score,
        "recommendation": candidate.recommendation,
        "recommendation_reason": candidate.recommendation_reason,
        "evidence_count": candidate.evidence_count,
        "matched_queries": list(candidate.matched_queries),
        "sample_titles": list(candidate.sample_titles),
        "sample_snippets": list(candidate.sample_snippets),
        "object_bucket": candidate.object_bucket,
        "policy_id": candidate.policy_id,
        "policy_version": candidate.policy_version,
        "policy_score": candidate.policy_score,
        "gate_status": candidate.gate_status,
        "selection_reason": candidate.selection_reason,
    }


def _attention_policy_name(policy_id: str) -> str:
    if policy_id == "source-latest-v1":
        return "Latest Intelligence Attention V1"
    if policy_id == "source-frontier-v1":
        return "Frontier Research Attention V1"
    if policy_id == "source-method-v1":
        return "Method Intelligence Attention V1"
    return "Authoritative Source Attention V1"


def _source_id_from_object_key(object_key: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in object_key.lower())
    return cleaned.strip("_") or "discovered_source"


def _execution_strategy_for_candidate(
    candidate: SourceDiscoveryCandidate,
    focus: SourceDiscoveryFocus,
) -> str:
    domain = candidate.domain.lower()
    if candidate.item_type in {"repository", "community", "person"}:
        return "agent_assisted"
    if any(token in domain for token in ("github.com", "reddit.com", "x.com", "twitter.com")):
        return "agent_assisted"
    if any(token in domain for token in ("arxiv.org", "openreview.net", "nature.com", "science.org")):
        return "review_capture"
    if focus == SourceDiscoveryFocus.LATEST:
        return "feed_or_fetch"
    if focus in {SourceDiscoveryFocus.FRONTIER, SourceDiscoveryFocus.METHOD}:
        return "search_review"
    return "review_capture"


def _review_cadence_for_candidate(
    candidate: SourceDiscoveryCandidate,
    focus: SourceDiscoveryFocus,
    default_days: int,
) -> int:
    if candidate.recommendation == "subscribe" and focus == SourceDiscoveryFocus.LATEST:
        return min(default_days, 3)
    if focus in {SourceDiscoveryFocus.FRONTIER, SourceDiscoveryFocus.METHOD}:
        return min(max(default_days, 7), 14)
    if candidate.authority_tier == "S":
        return max(default_days, 30)
    return default_days


def _serialize_source_plan_item(item: SourcePlanItemModel) -> SourcePlanItemResponse:
    evidence = dict(item.evidence or {})
    return SourcePlanItemResponse(
        id=str(item.id),
        item_type=item.item_type,
        object_key=item.object_key,
        name=item.name,
        url=item.url or "",
        authority_tier=item.authority_tier or "C",
        authority_score=item.authority_score or 0.0,
        monitoring_mode=item.monitoring_mode,
        execution_strategy=item.execution_strategy,
        review_cadence_days=item.review_cadence_days,
        rationale=item.rationale or "",
        status=item.status,
        evidence=evidence,
        object_bucket=str(evidence.get("object_bucket", "")),
        gate_status=str(evidence.get("gate_status", "")),
        selection_reason=str(evidence.get("selection_reason", "")),
    )


def _serialize_source_plan(plan: SourcePlanModel) -> SourcePlanResponse:
    items = sorted(list(plan.items or []), key=lambda item: (item.authority_score or 0.0), reverse=True)
    extra = dict(plan.extra or {})
    policy_meta = dict(extra.get("attention_policy", {}) or {})
    latest_evaluation = dict(extra.get("latest_evaluation", {}) or {})
    return SourcePlanResponse(
        id=str(plan.id),
        topic=plan.topic,
        focus=plan.focus,
        objective=plan.objective or "",
        planning_brain=plan.planning_brain,
        status=plan.status,
        review_status=plan.review_status,
        review_cadence_days=plan.review_cadence_days,
        current_version=plan.current_version or 1,
        latest_version=plan.latest_version or 1,
        policy_id=str(policy_meta.get("policy_id", "")),
        policy_version=int(policy_meta.get("policy_version", 1) or 1),
        policy_name=str(policy_meta.get("policy_name", "")),
        policy_decision_status=str(latest_evaluation.get("decision_status", "")),
        last_reviewed_at=_parse_datetime_value(extra.get("last_reviewed_at")),
        next_review_due_at=_parse_datetime_value(extra.get("next_review_due_at")),
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        items=[_serialize_source_plan_item(item) for item in items],
    )


def _serialize_source_plan_version(version: SourcePlanVersionModel) -> SourcePlanVersionResponse:
    return SourcePlanVersionResponse(
        id=str(version.id),
        version_number=version.version_number,
        parent_version=version.parent_version,
        trigger_type=version.trigger_type,
        decision_status=version.decision_status,
        change_reason=version.change_reason or "",
        change_summary=dict(version.change_summary or {}),
        evaluation=dict(version.evaluation or {}),
        created_by=version.created_by,
        accepted_at=version.accepted_at,
        created_at=version.created_at,
    )


def _snapshot_source_plan(plan: SourcePlanModel) -> Dict[str, Any]:
    items = []
    for item in sorted(list(plan.items or []), key=lambda value: value.object_key):
        items.append(
            {
                "item_type": item.item_type,
                "object_key": item.object_key,
                "name": item.name,
                "url": item.url or "",
                "authority_tier": item.authority_tier or "C",
                "authority_score": float(item.authority_score or 0.0),
                "monitoring_mode": item.monitoring_mode,
                "execution_strategy": item.execution_strategy,
                "review_cadence_days": int(item.review_cadence_days or plan.review_cadence_days or 14),
                "rationale": item.rationale or "",
                "status": item.status,
                "evidence": dict(item.evidence or {}),
            }
        )
    return {
        "topic": plan.topic,
        "focus": plan.focus,
        "objective": plan.objective or "",
        "review_cadence_days": int(plan.review_cadence_days or 14),
        "items": items,
    }


def _snapshot_source_plan_from_payload(
    *,
    topic: str,
    focus: str,
    objective: str,
    review_cadence_days: int,
    items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    normalized_items = []
    for item in sorted(items, key=lambda value: value["object_key"]):
        normalized_items.append(
            {
                "item_type": item["item_type"],
                "object_key": item["object_key"],
                "name": item["name"],
                "url": item.get("url", ""),
                "authority_tier": item.get("authority_tier", "C"),
                "authority_score": float(item.get("authority_score", 0.0)),
                "monitoring_mode": item.get("monitoring_mode", "review"),
                "execution_strategy": item.get("execution_strategy", "search_review"),
                "review_cadence_days": int(item.get("review_cadence_days", review_cadence_days)),
                "rationale": item.get("rationale", ""),
                "status": item.get("status", "active"),
                "evidence": dict(item.get("evidence", {})),
            }
        )
    return {
        "topic": topic,
        "focus": focus,
        "objective": objective or "",
        "review_cadence_days": int(review_cadence_days or 14),
        "items": normalized_items,
    }


def _parse_datetime_value(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _build_review_schedule_metadata(
    plan: SourcePlanModel,
    *,
    reviewed_at: datetime,
    trigger_type: str,
    result_count: int,
) -> Dict[str, Any]:
    next_due = reviewed_at + timedelta(days=int(plan.review_cadence_days or 14))
    return {
        "last_reviewed_at": reviewed_at.isoformat(),
        "next_review_due_at": next_due.isoformat(),
        "last_review_trigger": trigger_type,
        "last_refresh_result_count": result_count,
    }


async def _apply_source_plan_refresh(
    db: AsyncSession,
    *,
    plan: SourcePlanModel,
    limit: int,
    trigger_type: str,
    change_reason: str,
) -> SourcePlanModel:
    focus = SourceDiscoveryFocus(plan.focus)
    previous_snapshot = _snapshot_source_plan(plan)
    previous_current_version = int(plan.current_version or 1)
    normalized_trigger = trigger_type.strip().lower() if trigger_type else "manual_refresh"
    if normalized_trigger not in {"manual_refresh", "scheduled_refresh", "manual_rebuild"}:
        normalized_trigger = "manual_refresh"
    reviewed_at = datetime.now(timezone.utc)

    await _refresh_source_plan_items(db, plan, focus, plan.review_cadence_days, limit)
    candidate_snapshot = _snapshot_source_plan(plan)
    diff = _diff_source_plan_snapshots(previous_snapshot, candidate_snapshot)
    evaluation = _evaluate_source_plan_refresh(diff)
    next_version = int(plan.latest_version or plan.current_version or 1) + 1

    if evaluation["decision_status"] == "accepted":
        plan.current_version = next_version
        plan.latest_version = next_version
        plan.review_status = "accepted"
    else:
        _apply_source_plan_snapshot(plan, previous_snapshot)
        plan.latest_version = next_version
        plan.review_status = "needs_review"

    plan.extra = {
        **dict(plan.extra or {}),
        **_build_review_schedule_metadata(
            plan,
            reviewed_at=reviewed_at,
            trigger_type=normalized_trigger,
            result_count=len(candidate_snapshot.get("items", [])),
        ),
        "latest_diff": diff,
        "latest_evaluation": evaluation,
    }

    db.add(
        _build_source_plan_version_record(
            plan,
            version_number=next_version,
            parent_version=previous_current_version,
            trigger_type=normalized_trigger,
            decision_status=evaluation["decision_status"],
            change_reason=change_reason,
            change_summary=diff,
            plan_snapshot=candidate_snapshot,
            evaluation=evaluation,
        )
    )
    await db.commit()

    refreshed = (
        await db.execute(
            select(SourcePlanModel)
            .where(SourcePlanModel.id == plan.id)
            .options(joinedload(SourcePlanModel.items))
        )
    ).scalars().unique().one()
    return refreshed


def _apply_source_plan_snapshot(plan: SourcePlanModel, snapshot: Dict[str, Any]) -> None:
    plan.topic = snapshot.get("topic", plan.topic)
    plan.focus = snapshot.get("focus", plan.focus)
    plan.objective = snapshot.get("objective", plan.objective)
    plan.review_cadence_days = int(snapshot.get("review_cadence_days", plan.review_cadence_days or 14))

    existing_by_key = {item.object_key: item for item in list(plan.items or [])}
    snapshot_keys = set()

    for payload in snapshot.get("items", []):
        object_key = payload["object_key"]
        snapshot_keys.add(object_key)
        existing = existing_by_key.get(object_key)
        if existing is None:
            plan.items.append(
                SourcePlanItemModel(
                    item_type=payload.get("item_type", "domain"),
                    object_key=object_key,
                    name=payload["name"],
                    url=payload.get("url", ""),
                    authority_tier=payload.get("authority_tier", "C"),
                    authority_score=float(payload.get("authority_score", 0.0)),
                    monitoring_mode=payload.get("monitoring_mode", "review"),
                    execution_strategy=payload.get("execution_strategy", "search_review"),
                    review_cadence_days=int(payload.get("review_cadence_days", plan.review_cadence_days)),
                    rationale=payload.get("rationale", ""),
                    evidence=dict(payload.get("evidence", {})),
                    status=payload.get("status", "active"),
                )
            )
            continue

        existing.name = payload["name"]
        existing.url = payload.get("url", "")
        existing.authority_tier = payload.get("authority_tier", "C")
        existing.authority_score = float(payload.get("authority_score", 0.0))
        existing.monitoring_mode = payload.get("monitoring_mode", "review")
        existing.execution_strategy = payload.get("execution_strategy", "search_review")
        existing.review_cadence_days = int(payload.get("review_cadence_days", plan.review_cadence_days))
        existing.rationale = payload.get("rationale", "")
        existing.evidence = dict(payload.get("evidence", {}))
        existing.status = payload.get("status", "active")

    for object_key, existing in existing_by_key.items():
        if object_key not in snapshot_keys:
            plan.items.remove(existing)


def _diff_source_plan_snapshots(previous: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
    previous_items = {item["object_key"]: item for item in previous.get("items", [])}
    current_items = {item["object_key"]: item for item in current.get("items", [])}
    authority_rank = {"S": 4, "A": 3, "B": 2, "C": 1}

    added = sorted(key for key in current_items if key not in previous_items)
    removed = sorted(key for key in previous_items if key not in current_items)
    stale = sorted(
        key for key, item in current_items.items()
        if item.get("status") == "stale" and previous_items.get(key, {}).get("status") != "stale"
    )
    subscribed = sorted(
        key for key, item in current_items.items()
        if item.get("status") == "subscribed" and previous_items.get(key, {}).get("status") != "subscribed"
    )

    score_deltas: list[Dict[str, Any]] = []
    largest_drop = 0.0
    authority_regressions: list[Dict[str, Any]] = []
    for key in sorted(set(previous_items) & set(current_items)):
        before_score = float(previous_items[key].get("authority_score", 0.0))
        after_score = float(current_items[key].get("authority_score", 0.0))
        delta = round(after_score - before_score, 4)
        if delta != 0:
            score_deltas.append({"object_key": key, "before": before_score, "after": after_score, "delta": delta})
        if delta < largest_drop:
            largest_drop = delta

        before_tier = str(previous_items[key].get("authority_tier", "C") or "C")
        after_tier = str(current_items[key].get("authority_tier", "C") or "C")
        if authority_rank.get(after_tier, 0) < authority_rank.get(before_tier, 0):
            authority_regressions.append(
                {
                    "object_key": key,
                    "before_tier": before_tier,
                    "after_tier": after_tier,
                }
            )

    def _average_score(items: Dict[str, Dict[str, Any]]) -> float:
        if not items:
            return 0.0
        return round(
            sum(float(item.get("authority_score", 0.0)) for item in items.values()) / len(items),
            4,
        )

    def _evidence_total(items: Dict[str, Dict[str, Any]]) -> int:
        total = 0
        for item in items.values():
            evidence = item.get("evidence", {}) or {}
            total += int(evidence.get("evidence_count", 0) or 0)
        return total

    def _trusted_count(items: Dict[str, Dict[str, Any]]) -> int:
        return sum(
            1
            for item in items.values()
            if str(item.get("authority_tier", "C") or "C") in {"S", "A"}
        )

    previous_average_score = _average_score(previous_items)
    current_average_score = _average_score(current_items)
    previous_evidence_total = _evidence_total(previous_items)
    current_evidence_total = _evidence_total(current_items)
    previous_trusted_count = _trusted_count(previous_items)
    current_trusted_count = _trusted_count(current_items)

    return {
        "added": added,
        "removed": removed,
        "stale": stale,
        "subscribed": subscribed,
        "score_deltas": score_deltas,
        "authority_regressions": authority_regressions,
        "summary": {
            "previous_item_count": len(previous_items),
            "current_item_count": len(current_items),
            "added_count": len(added),
            "removed_count": len(removed),
            "stale_count": len(stale),
            "subscribed_count": len(subscribed),
            "largest_score_drop": largest_drop,
            "previous_average_score": previous_average_score,
            "current_average_score": current_average_score,
            "average_score_delta": round(current_average_score - previous_average_score, 4),
            "previous_evidence_total": previous_evidence_total,
            "current_evidence_total": current_evidence_total,
            "evidence_delta": current_evidence_total - previous_evidence_total,
            "previous_trusted_count": previous_trusted_count,
            "current_trusted_count": current_trusted_count,
            "trusted_count_delta": current_trusted_count - previous_trusted_count,
            "authority_regression_count": len(authority_regressions),
        },
    }


def _evaluate_source_plan_refresh(diff: Dict[str, Any]) -> Dict[str, Any]:
    summary = dict(diff.get("summary", {}))
    largest_drop = float(summary.get("largest_score_drop", 0.0))
    stale_count = int(summary.get("stale_count", 0))
    removed_count = int(summary.get("removed_count", 0))
    average_score_delta = float(summary.get("average_score_delta", 0.0))
    evidence_delta = int(summary.get("evidence_delta", 0))
    trusted_count_delta = int(summary.get("trusted_count_delta", 0))
    authority_regression_count = int(summary.get("authority_regression_count", 0))

    decision_status = "accepted"
    reasons: list[str] = []
    risk_signals: list[str] = []
    confidence = 0.8

    if largest_drop <= -0.15:
        decision_status = "needs_review"
        risk_signals.append("largest authority_score drop exceeded threshold")
        confidence -= 0.25
    if stale_count >= max(2, int(summary.get("previous_item_count", 0) / 2)):
        decision_status = "needs_review"
        risk_signals.append("too many tracked candidates became stale in a single refresh")
        confidence -= 0.15
    if removed_count > 0:
        decision_status = "needs_review"
        risk_signals.append("candidate set lost previously tracked objects")
        confidence -= 0.1
    if average_score_delta <= -0.08:
        decision_status = "needs_review"
        risk_signals.append("average authority score regressed materially")
        confidence -= 0.15
    if authority_regression_count > 0:
        decision_status = "needs_review"
        risk_signals.append("one or more tracked candidates regressed in authority tier")
        confidence -= 0.1
    if evidence_delta < 0 and trusted_count_delta < 0:
        decision_status = "needs_review"
        risk_signals.append("both evidence support and trusted-source count regressed")
        confidence -= 0.1

    if risk_signals:
        reasons.extend(risk_signals)
    else:
        reasons.append("refresh produced no high-risk degradations")

    return {
        "decision_status": decision_status,
        "confidence": max(0.1, round(confidence, 2)),
        "reasons": reasons,
        "gate_signals": {
            "largest_score_drop": largest_drop,
            "average_score_delta": average_score_delta,
            "evidence_delta": evidence_delta,
            "trusted_count_delta": trusted_count_delta,
            "authority_regression_count": authority_regression_count,
            "stale_count": stale_count,
            "removed_count": removed_count,
        },
    }


def _build_source_plan_version_record(
    plan: SourcePlanModel,
    *,
    version_number: int,
    parent_version: Optional[int],
    trigger_type: str,
    decision_status: str,
    change_reason: str,
    change_summary: Dict[str, Any],
    plan_snapshot: Dict[str, Any],
    evaluation: Dict[str, Any],
) -> SourcePlanVersionModel:
    accepted_at = datetime.now(timezone.utc) if decision_status == "accepted" else None
    return SourcePlanVersionModel(
        plan_id=plan.id,
        version_number=version_number,
        parent_version=parent_version,
        trigger_type=trigger_type,
        decision_status=decision_status,
        change_reason=change_reason,
        change_summary=change_summary,
        plan_snapshot=plan_snapshot,
        evaluation=evaluation,
        created_by=plan.planning_brain,
        accepted_at=accepted_at,
    )


def _find_existing_source_for_object(candidate: SourceDiscoveryCandidate):
    fetcher = get_feed_fetcher()
    return next(
        (
            src for src in fetcher.get_sources()
            if src.id == _source_id_from_object_key(candidate.object_key)
            or (src.url or "").rstrip("/").lower() == (candidate.url or "").rstrip("/").lower()
        ),
        None,
    )


def _subscribe_candidate_to_source(
    candidate: SourceDiscoveryCandidate,
    focus: SourceDiscoveryFocus,
) -> Source:
    fetcher = get_feed_fetcher()
    source_id = _source_id_from_object_key(candidate.object_key)
    existing = _find_existing_source_for_object(candidate)
    if existing is not None:
        return _source_to_api_model(existing)

    tags = [focus.value, "discovered", candidate.authority_tier, candidate.item_type]
    new_source = _FeedSource(
        id=source_id,
        name=candidate.name,
        url=candidate.url,
        category=_focus_category(focus),
        tags=tags,
        enabled=True,
        proxy_mode=ProxyMode.AUTO.value,
        use_proxy=False,
    )
    fetcher.add_source(new_source)
    return _source_to_api_model(new_source)


async def _refresh_source_plan_items(
    db: AsyncSession,
    plan: SourcePlanModel,
    focus: SourceDiscoveryFocus,
    review_cadence_days: int,
    limit: int,
) -> SourcePlanModel:
    discovery = await _run_source_discovery(
        SourceDiscoveryRequest(topic=plan.topic, focus=focus, limit=limit),
        db,
    )

    existing_by_key = {item.object_key: item for item in list(plan.items or [])}
    discovered_keys: set[str] = set()

    for candidate in discovery.candidates:
        discovered_keys.add(candidate.object_key)
        review_days = _review_cadence_for_candidate(candidate, focus, review_cadence_days)
        strategy = _execution_strategy_for_candidate(candidate, focus)
        rationale = (
            f"{candidate.recommendation_reason}；执行策略={strategy}；"
            f"证据命中 {candidate.evidence_count} 次。"
        )
        existing = existing_by_key.get(candidate.object_key)
        subscribed = _find_existing_source_for_object(candidate) is not None

        payload = {
            "name": candidate.name,
            "url": candidate.url,
            "authority_tier": candidate.authority_tier,
            "authority_score": candidate.authority_score,
            "monitoring_mode": candidate.recommendation,
            "execution_strategy": strategy,
            "review_cadence_days": review_days,
            "rationale": rationale,
            "evidence": {
                "matched_queries": candidate.matched_queries,
                "sample_titles": candidate.sample_titles,
                "sample_snippets": candidate.sample_snippets,
                "evidence_count": candidate.evidence_count,
                "object_bucket": candidate.object_bucket,
                "policy_id": candidate.policy_id,
                "policy_version": candidate.policy_version,
                "policy_score": candidate.policy_score,
                "gate_status": candidate.gate_status,
                "selection_reason": candidate.selection_reason,
            },
            "status": "subscribed" if subscribed else "active",
        }

        if existing is None:
            plan.items.append(
                SourcePlanItemModel(
                    item_type=candidate.item_type,
                    object_key=candidate.object_key,
                    **payload,
                )
            )
        else:
            for key, value in payload.items():
                setattr(existing, key, value)

    for object_key, item in existing_by_key.items():
        if object_key not in discovered_keys and item.status != "subscribed":
            item.status = "stale"

    plan.review_status = "reviewed"
    plan.extra = {
        **dict(plan.extra or {}),
        "queries": discovery.queries,
        "attention_policy": {
            "policy_id": discovery.policy_id,
            "policy_version": discovery.policy_version,
            "policy_name": _attention_policy_name(discovery.policy_id),
        },
        "latest_portfolio_summary": discovery.portfolio_summary,
        "last_refresh_result_count": len(discovery.candidates),
        "last_refreshed_at": datetime.now(timezone.utc).isoformat(),
    }
    return plan


def _domain_quality_adjustment(domain: str, focus: SourceDiscoveryFocus) -> float:
    domain = domain.lower()
    positive = {
        SourceDiscoveryFocus.METHOD: (
            "github.com",
            "openreview.net",
            "arxiv.org",
            "docs.",
            "readthedocs",
            "anthropic.com",
            "openai.com",
            "langchain.com",
            "langchain-ai.github.io",
            "microsoft.github.io",
            "developer.aliyun.com",
            "openclaw.cc",
        ),
        SourceDiscoveryFocus.FRONTIER: (
            "arxiv.org",
            "openreview.net",
            "nature.com",
            "science.org",
            "acm.org",
            "ieee.org",
            ".edu",
            ".ac.",
        ),
        SourceDiscoveryFocus.AUTHORITATIVE: (
            ".gov",
            ".gov.cn",
            ".edu",
            ".org",
            "who.int",
            "oecd.org",
            "w3.org",
        ),
        SourceDiscoveryFocus.LATEST: (
            "reuters.com",
            "bloomberg.com",
            "ft.com",
            "wsj.com",
            "techcrunch.com",
            "theverge.com",
            "wired.com",
        ),
    }
    negative = (
        "toutiao.com",
        "baijiahao.baidu.com",
        "bilibili.com",
        "weibo.com",
        "zhihu.com",
        "csdn.net",
        "blog.csdn.net",
        "m.blog.csdn.net",
    )

    score = 0.0
    if any(token in domain for token in positive.get(focus, ())):
        score += 0.25
    if any(token in domain for token in negative):
        score -= 0.3
    if domain.startswith("m."):
        score -= 0.1
    return score


async def _run_source_discovery(body: SourceDiscoveryRequest, db: AsyncSession) -> SourceDiscoveryResponse:
    search = AliyunWebSearch()
    classifier = get_authority_classifier()
    policy = await resolve_attention_policy(db, body.focus)
    queries = _discovery_queries(body.topic, body.focus, dict(policy.execution_policy or {}))
    aggregated: dict[str, dict[str, Any]] = {}

    for query in queries:
        result = await asyncio.to_thread(
            search.search,
            query,
            search.ENGINE_ADVANCED,
            search.TIME_ONE_MONTH if body.focus == SourceDiscoveryFocus.LATEST else search.TIME_NO_LIMIT,
            True,
            False,
            True,
            body.limit,
        )
        if not result.get("success"):
            continue

        for item in result.get("results", []):
            domain = _normalize_domain(item.link or item.source or "")
            if not domain:
                continue
            item_type, object_key, display_name, canonical_url, source_domain = _candidate_identity(
                item.link or f"https://{domain}",
                body.focus,
            )

            authority = classifier.classify(item.link or source_domain, item.title, _focus_category(body.focus))
            adjusted_score = max(0.0, min(1.0, authority.score + _domain_quality_adjustment(source_domain, body.focus)))
            candidate = aggregated.setdefault(
                object_key,
                {
                    "item_type": item_type,
                    "object_key": object_key,
                    "domain": source_domain,
                    "name": display_name,
                    "url": canonical_url,
                    "authority_tier": authority.tier,
                    "authority_score": adjusted_score,
                    "evidence_count": 0,
                    "matched_queries": [],
                    "sample_titles": [],
                    "sample_snippets": [],
                },
            )
            candidate["authority_tier"] = authority.tier if adjusted_score >= candidate["authority_score"] else candidate["authority_tier"]
            candidate["authority_score"] = max(candidate["authority_score"], adjusted_score)
            candidate["evidence_count"] += 1
            if query not in candidate["matched_queries"]:
                candidate["matched_queries"].append(query)
            if item.title and len(candidate["sample_titles"]) < 3:
                candidate["sample_titles"].append(item.title)
            snippet = (item.snippet or item.main_text or "").strip()
            if snippet and len(candidate["sample_snippets"]) < 2:
                candidate["sample_snippets"].append(snippet[:220])

    ranked = sorted(
        [item for item in aggregated.values() if item["authority_score"] >= 0.45],
        key=lambda item: (item["authority_score"], item["evidence_count"]),
        reverse=True,
    )[: body.limit]

    candidates: list[SourceDiscoveryCandidate] = []
    for item in ranked:
        recommendation, reason = _discovery_recommendation(
            body.focus,
            item["authority_tier"],
            item["evidence_count"],
        )
        candidates.append(
            SourceDiscoveryCandidate(
                item_type=item["item_type"],
                object_key=item["object_key"],
                domain=item["domain"],
                name=item["name"],
                url=item["url"],
                authority_tier=item["authority_tier"],
                authority_score=item["authority_score"],
                recommendation=recommendation,
                recommendation_reason=reason,
                evidence_count=item["evidence_count"],
                matched_queries=item["matched_queries"],
                sample_titles=item["sample_titles"],
                sample_snippets=item["sample_snippets"],
            )
        )

    attention_result = apply_attention_policy(
        policy,
        body.focus,
        [_candidate_to_attention_payload(candidate) for candidate in candidates],
        body.limit,
    )
    return SourceDiscoveryResponse(
        topic=body.topic,
        focus=body.focus,
        queries=queries,
        policy_id=attention_result.policy_id,
        policy_version=attention_result.policy_version,
        portfolio_summary=attention_result.portfolio_summary,
        candidates=[SourceDiscoveryCandidate(**payload) for payload in attention_result.selected],
    )
    return Source(
        id=source.id,
        name=source.name,
        type=SourceType.RSS,
        url=source.url,
        category=source.category,
        tags=source.tags,
        enabled=source.enabled,
        proxy_mode=ProxyMode(proxy_mode),
        proxy_effective=proxy_effective,
        proxy_reason=proxy_reason,
    )


def _feed_source_public_id(source: SourceModel, extra: dict[str, Any]) -> str:
    source_key = extra.get("source_key")
    if source_key:
        return str(source_key)
    config = source.config or {}
    configured_key = config.get("source_key")
    if configured_key:
        return str(configured_key)
    return str(source.id)


def _db_feed_to_api_model(item: FeedItemModel) -> FeedItem:
    source = item.source
    extra = item.extra or {}
    source_type = source.type.value if hasattr(source.type, "value") else str(source.type or "rss")
    category = source.category or extra.get("category_name") or extra.get("raw_category") or ""
    return FeedItem(
        id=item.external_id or str(item.id),
        title=item.title,
        summary=item.summary or "",
        source=source.name if source else (extra.get("source_name") or ""),
        source_id=_feed_source_public_id(source, extra) if source else str(item.source_id),
        source_type=SourceType(source_type),
        url=item.url or "",
        published_at=item.published_at or item.fetched_at,
        category=category,
        importance=item.importance or 0.5,
        is_read=False,
        is_favorite=False,
    )


async def _get_db_feeds(
    db: AsyncSession,
    *,
    source_id: Optional[str],
    category: Optional[str],
    limit: int,
) -> list[FeedItem]:
    stmt = (
        select(FeedItemModel)
        .options(joinedload(FeedItemModel.source))
        .join(FeedItemModel.source)
    )

    if source_id:
        stmt = stmt.where(
            or_(
                cast(SourceModel.id, SqlString) == source_id,
                SourceModel.config.op("->>")("source_key") == source_id,
                SourceModel.url == build_import_source_url(source_id),
            )
        )

    if category:
        stmt = stmt.where(SourceModel.category == category)

    stmt = stmt.order_by(
        FeedItemModel.published_at.desc().nullslast(),
        FeedItemModel.fetched_at.desc(),
        FeedItemModel.created_at.desc(),
    ).limit(limit)

    result = await db.execute(stmt)
    return [_db_feed_to_api_model(item) for item in result.scalars().all()]


async def _get_cache_feeds(
    *,
    source_id: Optional[str],
    category: Optional[str],
    limit: int,
) -> list[FeedItem]:
    fetcher = get_feed_fetcher()

    if source_id:
        entries = await fetcher.fetch_by_source(source_id)
    else:
        entries = await fetcher.fetch_all()

    if category:
        entries = [e for e in entries if map_category(e.category) == category or _match_category(e.category, category)]

    entries = entries[:limit]
    return [
        FeedItem(
            id=e.id,
            title=e.title,
            summary=e.summary,
            source=e.source_name,
            source_id=e.source_id,
            source_type=SourceType.RSS,
            url=e.url,
            published_at=e.published_at,
            category=e.category,
            importance=e.importance,
            is_read=e.is_read,
            is_favorite=e.is_favorite,
        )
        for e in entries
    ]


def _merge_feed_results(db_items: list[FeedItem], cache_items: list[FeedItem], limit: int) -> list[FeedItem]:
    merged: list[FeedItem] = []
    seen: set[str] = set()

    for item in db_items + cache_items:
        dedupe_key = item.url or item.id
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        merged.append(item)

    merged.sort(key=lambda item: item.published_at, reverse=True)
    return merged[:limit]


@router.get("/feeds", response_model=List[FeedItem])
async def get_feeds(
    source_id: Optional[str] = Query(None, description="?????"),
    category: Optional[str] = Query(None, description="?????"),
    limit: int = Query(200, ge=1, le=500),
    backend: Optional[FeedsReadBackend] = Query(None, description="?????cache/db/hybrid"),
    db: AsyncSession = Depends(get_db),
):
    """???????? cache / db / hybrid ???"""
    settings = get_settings()
    configured_backend = getattr(settings, "feeds_read_backend", "hybrid")
    active_backend = (backend.value if backend else configured_backend or "hybrid").strip().lower()

    if active_backend == FeedsReadBackend.CACHE.value:
        return await _get_cache_feeds(source_id=source_id, category=category, limit=limit)

    db_items = await _get_db_feeds(db, source_id=source_id, category=category, limit=limit)
    if active_backend == FeedsReadBackend.DB.value:
        return db_items

    cache_items = await _get_cache_feeds(source_id=source_id, category=category, limit=limit)
    return _merge_feed_results(db_items, cache_items, limit)


@router.get("/feeds/health")
async def get_feed_collection_health(db: AsyncSession = Depends(get_db)):
    """Return durable collection health for the feed pipeline."""
    from feeds.collection_health import collect_collection_health_snapshot

    return await collect_collection_health_snapshot(db)


@router.post("/feeds/refresh")
async def refresh_feeds():
    """强制刷新所有信息源（清除缓存）"""
    fetcher = get_feed_fetcher()
    fetcher._cache.clear()
    entries = await fetcher.fetch_all()
    return {"status": "ok", "count": len(entries)}


@router.get("/sources", response_model=List[Source])
async def get_sources():
    """获取所有信息源配置"""
    fetcher = get_feed_fetcher()
    sources = fetcher.get_sources()
    return [_source_to_api_model(s) for s in sources]


@router.post("/sources", response_model=Source)
async def create_source(body: SourceCreate):
    """添加新信息源"""
    fetcher = get_feed_fetcher()
    source_id = body.name.lower().replace(" ", "_")
    new = _FeedSource(
        id=source_id,
        name=body.name,
        url=body.url,
        category=body.category,
        tags=body.tags,
        enabled=body.enabled,
        proxy_mode=body.proxy_mode.value,
        use_proxy=body.proxy_mode == ProxyMode.ALWAYS,
    )
    fetcher.add_source(new)
    return _source_to_api_model(new)


@router.post("/sources/discover", response_model=SourceDiscoveryResponse)
async def discover_sources(body: SourceDiscoveryRequest, db: AsyncSession = Depends(get_db)):
    """
    Discover candidate sources for a topic using web search + authority scoring.

    This is a minimum source-intelligence step:
    - topic-driven
    - not limited to existing RSS list
    - produces candidates for long-term monitoring decisions
    """
    return await _run_source_discovery(body, db)


@router.get("/sources/plans", response_model=List[SourcePlanResponse])
async def list_source_plans(db: AsyncSession = Depends(get_db)):
    """List persisted source-intelligence plans."""
    stmt = (
        select(SourcePlanModel)
        .options(joinedload(SourcePlanModel.items))
        .order_by(SourcePlanModel.updated_at.desc().nullslast(), SourcePlanModel.created_at.desc())
    )
    plans = (await db.execute(stmt)).scalars().unique().all()
    canonical_plans: dict[tuple[str, str], SourcePlanModel] = {}
    for plan in plans:
        key = (_topic_merge_key(plan.topic), plan.focus)
        existing = canonical_plans.get(key)
        if existing is None:
            canonical_plans[key] = plan
            continue
        existing_version = int(existing.current_version or existing.latest_version or 1)
        candidate_version = int(plan.current_version or plan.latest_version or 1)
        if candidate_version > existing_version or (plan.updated_at or plan.created_at) > (existing.updated_at or existing.created_at):
            canonical_plans[key] = plan
    return [_serialize_source_plan(plan) for plan in canonical_plans.values()]


@router.get("/sources/plans/{plan_id}/versions", response_model=List[SourcePlanVersionResponse])
async def list_source_plan_versions(plan_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(SourcePlanVersionModel)
        .join(SourcePlanModel, SourcePlanModel.id == SourcePlanVersionModel.plan_id)
        .where(cast(SourcePlanModel.id, SqlString) == plan_id)
        .order_by(SourcePlanVersionModel.version_number.desc(), SourcePlanVersionModel.created_at.desc())
    )
    versions = (await db.execute(stmt)).scalars().all()
    return [_serialize_source_plan_version(version) for version in versions]


@router.post("/sources/plans", response_model=SourcePlanResponse)
async def create_source_plan(
    body: SourcePlanCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a persisted source-intelligence plan from topic-driven discovery.

    This is the first brain-facing control object for the information brain:
    it stores what to watch, why to watch it, and how it should be reviewed.
    """
    existing_stmt = (
        select(SourcePlanModel)
        .where(
            SourcePlanModel.status == "active",
            SourcePlanModel.focus == body.focus.value,
        )
        .options(joinedload(SourcePlanModel.items))
    )
    existing_plans = (await db.execute(existing_stmt)).scalars().unique().all()
    requested_owner_key = _source_plan_owner_key(body.topic, body.focus)
    matching_plans = [
        plan
        for plan in existing_plans
        if (
            _topic_merge_key(plan.topic) == _topic_merge_key(body.topic)
            or (plan.owner_id or "") == requested_owner_key
            or _topic_merge_key(body.topic) in {
                _topic_merge_key(alias)
                for alias in list(dict(plan.extra or {}).get("topic_aliases", []))
                if alias
            }
        )
    ]
    existing_plan = None
    if matching_plans:
        matching_plans.sort(key=_source_plan_match_score, reverse=True)
        existing_plan = matching_plans[0]
        if len(matching_plans) > 1:
            for duplicate_plan in matching_plans[1:]:
                duplicate_plan.status = "inactive"
                duplicate_plan.review_status = "merged"
                duplicate_plan.extra = {
                    **dict(duplicate_plan.extra or {}),
                    "merged_into_plan_id": str(existing_plan.id),
                    "merge_reason": "Merged duplicate source plan with the same normalized topic and focus.",
                    "merged_at": datetime.now(timezone.utc).isoformat(),
                }
    if existing_plan is not None:
        existing_plan.topic = body.topic
        existing_plan.owner_id = requested_owner_key
        if body.objective.strip():
            existing_plan.objective = body.objective.strip()
        existing_plan.review_cadence_days = body.review_cadence_days
        existing_plan.extra = {
            **dict(existing_plan.extra or {}),
            "queries": _discovery_queries(body.topic, body.focus),
            "topic_merge_key": _topic_merge_key(body.topic),
            "topic_aliases": sorted(
                {
                    *set(dict(existing_plan.extra or {}).get("topic_aliases", [])),
                    body.topic.strip(),
                }
            ),
        }
        refreshed = await _apply_source_plan_refresh(
            db,
            plan=existing_plan,
            limit=body.limit,
            trigger_type="manual_rebuild",
            change_reason="Reused existing source plan for the same normalized topic and focus.",
        )
        return _serialize_source_plan(refreshed)

    discovery = await _run_source_discovery(
        SourceDiscoveryRequest(topic=body.topic, focus=body.focus, limit=body.limit),
        db,
    )

    plan = SourcePlanModel(
        topic=body.topic,
        focus=body.focus.value,
        objective=body.objective or f"Build and maintain a source plan for {body.topic}.",
        owner_type="system",
        owner_id=_source_plan_owner_key(body.topic, body.focus),
        planning_brain="source-intelligence-brain",
        status="active",
        review_status="draft",
        review_cadence_days=body.review_cadence_days,
        extra={
            "queries": discovery.queries,
            "attention_policy": {
                "policy_id": discovery.policy_id,
                "policy_version": discovery.policy_version,
                "policy_name": _attention_policy_name(discovery.policy_id),
            },
            "latest_portfolio_summary": discovery.portfolio_summary,
        },
    )
    plan.extra = {
        **dict(plan.extra or {}),
        "topic_aliases": [body.topic.strip()],
        "topic_merge_key": _topic_merge_key(body.topic),
    }
    db.add(plan)
    await db.flush()

    created_items_payload: list[Dict[str, Any]] = []
    for candidate in discovery.candidates:
        review_days = _review_cadence_for_candidate(candidate, body.focus, body.review_cadence_days)
        strategy = _execution_strategy_for_candidate(candidate, body.focus)
        evidence = {
            "matched_queries": candidate.matched_queries,
            "sample_titles": candidate.sample_titles,
            "sample_snippets": candidate.sample_snippets,
            "evidence_count": candidate.evidence_count,
            "object_bucket": candidate.object_bucket,
            "policy_id": candidate.policy_id,
            "policy_version": candidate.policy_version,
            "policy_score": candidate.policy_score,
            "gate_status": candidate.gate_status,
            "selection_reason": candidate.selection_reason,
        }
        rationale = (
            f"{candidate.recommendation_reason}；执行策略={strategy}；"
            f"证据命中 {candidate.evidence_count} 次。"
        )
        created_items_payload.append(
            {
                "item_type": candidate.item_type,
                "object_key": candidate.object_key,
                "name": candidate.name,
                "url": candidate.url,
                "authority_tier": candidate.authority_tier,
                "authority_score": candidate.authority_score,
                "monitoring_mode": candidate.recommendation,
                "execution_strategy": strategy,
                "review_cadence_days": review_days,
                "rationale": rationale,
                "status": "active",
                "evidence": evidence,
            }
        )
        db.add(
            SourcePlanItemModel(
                plan_id=plan.id,
                item_type=candidate.item_type,
                object_key=candidate.object_key,
                name=candidate.name,
                url=candidate.url,
                authority_tier=candidate.authority_tier,
                authority_score=candidate.authority_score,
                monitoring_mode=candidate.recommendation,
                execution_strategy=strategy,
                review_cadence_days=review_days,
                rationale=rationale,
                evidence=evidence,
                status="active",
            )
        )

    initial_snapshot = _snapshot_source_plan_from_payload(
        topic=plan.topic,
        focus=plan.focus,
        objective=plan.objective or "",
        review_cadence_days=plan.review_cadence_days,
        items=created_items_payload,
    )
    created_at = datetime.now(timezone.utc)
    plan.current_version = 1
    plan.latest_version = 1
    plan.review_status = "accepted"
    plan.extra = {
        **dict(plan.extra or {}),
        **_build_review_schedule_metadata(
            plan,
            reviewed_at=created_at,
            trigger_type="initial_create",
            result_count=len(created_items_payload),
        ),
    }
    db.add(
        _build_source_plan_version_record(
            plan,
            version_number=1,
            parent_version=None,
            trigger_type="initial_create",
            decision_status="accepted",
            change_reason="Initial source plan created from topic-driven discovery.",
            change_summary={"summary": {"previous_item_count": 0, "current_item_count": len(initial_snapshot.get("items", []))}},
            plan_snapshot=initial_snapshot,
            evaluation={"decision_status": "accepted", "confidence": 1.0, "reasons": ["initial source plan baseline"]},
        )
    )

    await db.commit()

    result = await db.execute(
        select(SourcePlanModel)
        .where(SourcePlanModel.id == plan.id)
        .options(joinedload(SourcePlanModel.items))
    )
    persisted = result.scalars().unique().one()
    return _serialize_source_plan(persisted)


@router.post("/sources/plans/{plan_id}/refresh", response_model=SourcePlanResponse)
async def refresh_source_plan(
    plan_id: str,
    limit: int = Query(12, ge=3, le=30),
    trigger_type: str = Query("manual_refresh"),
    db: AsyncSession = Depends(get_db),
):
    """Re-run discovery for an existing source plan and update candidate states."""
    stmt = (
        select(SourcePlanModel)
        .where(cast(SourcePlanModel.id, SqlString) == plan_id)
        .options(joinedload(SourcePlanModel.items))
    )
    plan = (await db.execute(stmt)).scalars().unique().one_or_none()
    if plan is None:
        raise HTTPException(status_code=404, detail="Source plan not found")

    refreshed = await _apply_source_plan_refresh(
        db,
        plan=plan,
        limit=limit,
        trigger_type=trigger_type,
        change_reason=(
            "Scheduled source-plan refresh from topic-driven discovery."
            if trigger_type == "scheduled_refresh"
            else "Manual source-plan refresh from topic-driven discovery."
        ),
    )
    return _serialize_source_plan(refreshed)


@router.post("/sources/discover/{domain}/subscribe", response_model=Source)
async def subscribe_discovered_source(
    domain: str,
    body: SourceDiscoveryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Convert a discovered domain into a tracked source.

    This does not auto-invent a verified RSS endpoint. It subscribes to the
    discovered site URL as a managed source entry so the project can continue
    calibrating and later refine fetch strategy.
    """
    discovery = await _run_source_discovery(body, db)
    candidate = next((item for item in discovery.candidates if item.domain == _normalize_domain(domain)), None)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Discovered candidate not found")

    return _subscribe_candidate_to_source(candidate, body.focus)


@router.post("/sources/plans/{plan_id}/items/{item_id}/subscribe", response_model=Source)
async def subscribe_source_plan_item(
    plan_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Promote a source-plan item into a managed source and mark the plan item as subscribed."""
    stmt = (
        select(SourcePlanItemModel)
        .join(SourcePlanModel, SourcePlanModel.id == SourcePlanItemModel.plan_id)
        .where(
            cast(SourcePlanModel.id, SqlString) == plan_id,
            cast(SourcePlanItemModel.id, SqlString) == item_id,
        )
        .options(joinedload(SourcePlanItemModel.plan).joinedload(SourcePlanModel.items))
    )
    item = (await db.execute(stmt)).scalars().unique().one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Source plan item not found")

    candidate = SourceDiscoveryCandidate(
        item_type=item.item_type,
        object_key=item.object_key,
        domain=_normalize_domain(item.url or item.object_key),
        name=item.name,
        url=item.url or "",
        authority_tier=item.authority_tier or "C",
        authority_score=item.authority_score or 0.0,
        recommendation=item.monitoring_mode,
        recommendation_reason=item.rationale or "",
        evidence_count=int((item.evidence or {}).get("evidence_count", 0)),
        matched_queries=list((item.evidence or {}).get("matched_queries", [])),
        sample_titles=list((item.evidence or {}).get("sample_titles", [])),
        sample_snippets=list((item.evidence or {}).get("sample_snippets", [])),
        object_bucket=str((item.evidence or {}).get("object_bucket", "")),
        policy_id=str((item.evidence or {}).get("policy_id", "")),
        policy_version=int((item.evidence or {}).get("policy_version", 1) or 1),
        policy_score=float((item.evidence or {}).get("policy_score", 0.0) or 0.0),
        gate_status=str((item.evidence or {}).get("gate_status", "")),
        selection_reason=str((item.evidence or {}).get("selection_reason", "")),
    )
    previous_snapshot = _snapshot_source_plan(item.plan)
    source = _subscribe_candidate_to_source(candidate, SourceDiscoveryFocus(item.plan.focus))
    item.status = "subscribed"
    item.execution_strategy = item.execution_strategy or "feed_or_fetch"
    current_snapshot = _snapshot_source_plan(item.plan)
    diff = _diff_source_plan_snapshots(previous_snapshot, current_snapshot)
    next_version = int(item.plan.latest_version or item.plan.current_version or 1) + 1
    item.plan.current_version = next_version
    item.plan.latest_version = next_version
    item.plan.review_status = "accepted"
    item.plan.extra = {
        **dict(item.plan.extra or {}),
        "latest_diff": diff,
        "latest_evaluation": {
            "decision_status": "accepted",
            "confidence": 1.0,
            "reasons": ["plan item promoted into managed source"],
        },
    }
    db.add(
        _build_source_plan_version_record(
            item.plan,
            version_number=next_version,
            parent_version=max(next_version - 1, 1),
            trigger_type="manual_subscribe",
            decision_status="accepted",
            change_reason=f"Promoted source-plan item {item.object_key} into managed source.",
            change_summary=diff,
            plan_snapshot=current_snapshot,
            evaluation={"decision_status": "accepted", "confidence": 1.0, "reasons": ["plan item promoted into managed source"]},
        )
    )
    await db.commit()
    return source


@router.delete("/sources/{source_id}")
async def delete_source(source_id: str):
    """删除信息源"""
    fetcher = get_feed_fetcher()
    removed = fetcher.remove_source(source_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"status": "deleted"}


@router.post("/sources/{source_id}/toggle")
async def toggle_source(source_id: str):
    """切换信息源启用/禁用"""
    fetcher = get_feed_fetcher()
    new_state = fetcher.toggle_source(source_id)
    if new_state is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"source_id": source_id, "enabled": new_state}


@router.put("/sources/{source_id}/proxy", response_model=Source)
async def update_source_proxy(source_id: str, body: SourceProxyUpdate):
    fetcher = get_feed_fetcher()
    source = fetcher.update_source_proxy_mode(source_id, body.proxy_mode.value)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return _source_to_api_model(source)


@router.post("/sources/{source_id}/refresh")
async def refresh_source(source_id: str):
    """手动刷新指定信息源"""
    fetcher = get_feed_fetcher()
    # 清除该源缓存
    fetcher._cache.pop(source_id, None)
    entries = await fetcher.fetch_by_source(source_id)
    return {"status": "ok", "source_id": source_id, "count": len(entries)}


@router.post("/sources/reload")
async def reload_sources():
    """重新加载所有信息源配置"""
    fetcher = reload_feed_fetcher()
    return {
        "status": "ok",
        "message": "Sources reloaded",
        "count": len(fetcher.sources)
    }


# ── Import endpoint ──────────────────────────────────

def _parse_import_datetime(dt_str: Optional[str]) -> datetime:
    """Parse ISO datetime string, fallback to now."""
    if not dt_str:
        return datetime.now(timezone.utc)
    try:
        # Handle various ISO formats
        dt_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


# Category mapping from info-processor to MyAttention categories
_CATEGORY_MAP = {
    "TECH": "科技",
    "WORLD": "国际",
    "CHINA": "国内",
    "FINANCE_CN": "财经",
    "FINANCE_INTL": "海外财经",
    "SOCIAL": "社交",
}

# Also map lowercase variants from gatherer
_CATEGORY_MAP.update({k.lower(): v for k, v in _CATEGORY_MAP.items()})
_CATEGORY_MAP.update({
    "tech": "科技",
    "world": "国际",
    "china": "国内",
    "finance_cn": "财经",
    "finance_intl": "海外财经",
    "social": "社交",
})

# Reverse mapping for filtering (Chinese -> English keys)
_CATEGORY_REVERSE_MAP = {v: k for k, v in _CATEGORY_MAP.items()}


def _match_category(entry_category: str, filter_category: str) -> bool:
    """Check if entry's category matches the filter using mapping."""
    if not filter_category:
        return True

    # Import mapping from fetcher
    from feeds.fetcher import CATEGORY_MAPPING

    # Get standard category for entry
    entry_standard = CATEGORY_MAPPING.get(entry_category, entry_category)

    # Direct match with standard category
    return entry_standard == filter_category


@router.post("/feeds/import", response_model=FeedsImportResponse)
async def import_feeds(body: FeedsImportRequest, db: AsyncSession = Depends(get_db)):
    """
    批量导入 info-processor 处理后的信息项。
    
    Phase 1 先做双落点：
    1. 原始导入内容进入对象存储 + raw_ingest 元数据
    2. 继续注入 FeedFetcher 内存缓存，保持现有 /api/feeds 可用
    """
    fetcher = get_feed_fetcher()
    
    imported_ids = []
    persisted_count = 0
    duplicates = 0
    errors = 0
    
    # Collect existing IDs for dedup
    existing_ids = set()
    for _, (_, entries) in fetcher._cache.items():
        for e in entries:
            existing_ids.add(e.id)
    
    # Group imported items by source
    by_source: Dict[str, list] = {}
    
    for item in body.items:
        try:
            payload = item.model_dump() if hasattr(item, "model_dump") else item.dict()
            source_key = item.source or "_imported"
            registered_source = next((src for src in fetcher.get_sources() if src.id == source_key), None)
            resolved_source_name = item.source_name or (registered_source.name if registered_source else source_key)
            resolved_source_url = registered_source.url if registered_source else ""
            resolved_category = _CATEGORY_MAP.get(
                item.category,
                item.category_name or (registered_source.category if registered_source else item.category),
            )
            resolved_tags = item.secondary_tags or (registered_source.tags if registered_source else [])
            fetched_at = _parse_import_datetime(item.processed_at or item.published_at)

            raw_result = await persist_import_item_raw(
                db,
                source_key=source_key,
                external_id=item.id,
                payload=payload,
                fetched_at=fetched_at,
            )

            try:
                async with db.begin_nested():
                    source = await resolve_source_for_import(
                        db,
                        source_key=source_key,
                        source_name=resolved_source_name,
                        source_type=item.source_type,
                        source_url=resolved_source_url,
                        category=resolved_category,
                        tags=resolved_tags,
                    )

                    persisted = await persist_import_feed_item(
                        db,
                        source=source,
                        external_id=item.id,
                        title=item.title,
                        summary=item.summary,
                        content=item.content or item.summary,
                        url=item.link,
                        importance=item.urgency,
                        published_at=_parse_import_datetime(item.published_at),
                        fetched_at=fetched_at,
                        extra=build_import_feed_extra(
                            raw_ingest_id=str(raw_result.record.id) if raw_result.record.id else None,
                            source_key=source_key,
                            source_name=resolved_source_name,
                            source_type=item.source_type,
                            category=item.category,
                            category_name=item.category_name,
                            metadata=item.metadata,
                            urgency_factors=item.urgency_factors,
                            secondary_tags=item.secondary_tags,
                            language=item.language,
                        ),
                    )
            except Exception as exc:
                raw_result.record.parse_status = "error"
                raw_result.record.error_message = str(exc)[:1000]
                response_meta = dict(raw_result.record.response_meta or {})
                response_meta.update(
                    {
                        "persist_error": str(exc)[:500],
                        "source_key": source_key,
                    }
                )
                raw_result.record.response_meta = response_meta
                await db.flush()
                errors += 1
                continue

            raw_result.record.parse_status = "persisted" if persisted.created else "duplicate"
            response_meta = dict(raw_result.record.response_meta or {})
            response_meta.update(
                {
                    "source_id": str(source.id) if source.id else None,
                    "feed_item_id": str(persisted.record.id) if persisted.record.id else None,
                    "feed_item_created": persisted.created,
                }
            )
            raw_result.record.response_meta = response_meta
            raw_result.record.error_message = None
            await db.flush()

            if item.id in existing_ids or not persisted.created:
                duplicates += 1
                continue
            persisted_count += 1

            category = _CATEGORY_MAP.get(item.category, item.category_name or item.category)
            entry = FeedEntry(
                id=item.id,
                title=item.title,
                summary=item.summary[:200] + "..." if len(item.summary) > 200 else item.summary,
                source_name=resolved_source_name,
                source_id=source_key,
                url=item.link,
                published_at=_parse_import_datetime(item.published_at),
                category=category,
                importance=item.urgency,
            )

            if source_key not in by_source:
                by_source[source_key] = []
            by_source[source_key].append(entry)

            imported_ids.append(item.id)
            existing_ids.add(item.id)

        except Exception:
            errors += 1
    
    # Inject into FeedFetcher cache
    import time as _time
    for source_key, entries in by_source.items():
        cached = fetcher._cache.get(source_key)
        if cached:
            # Merge with existing cache entries
            existing_entries = list(cached[1])
            existing_entries.extend(entries)
            # Sort by published time and dedup
            existing_entries.sort(key=lambda e: e.published_at, reverse=True)
            fetcher._cache[source_key] = (_time.time(), existing_entries)
        else:
            entries.sort(key=lambda e: e.published_at, reverse=True)
            fetcher._cache[source_key] = (_time.time(), entries)
    
    return FeedsImportResponse(
        status="ok" if imported_ids else "empty",
        imported=len(imported_ids),
        persisted=persisted_count,
        duplicates=duplicates,
        errors=errors,
        items=imported_ids[:50],  # Limit returned IDs
    )


# ── 一键转知识库 ───────────────────────────────────────

class ToKnowledgeBaseRequest(BaseModel):
    """转入知识库请求"""
    kb_id: str = Field(..., description="目标知识库ID")
    notes: Optional[str] = Field(None, description="可选备注")
    extract_deep: bool = Field(False, description="是否进行深度提取(L3)")


class ToKnowledgeBaseResponse(BaseModel):
    """转入知识库响应"""
    success: bool
    knowledge_link_id: Optional[str] = None
    document_id: Optional[str] = None
    message: str


@router.post("/feeds/{item_id}/to-knowledge-base", response_model=ToKnowledgeBaseResponse)
async def feed_to_knowledge_base(
    item_id: str,
    body: ToKnowledgeBaseRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    将信息流条目转入指定知识库

    实现信息闭环：信息 -> 知识
    """
    from knowledge import get_kb_manager, Document as KbDocument
    from knowledge import Document as KbDocument

    try:
        # 1. 尝试从内存缓存中获取 FeedEntry
        fetcher = get_feed_fetcher()
        feed_entry = None
        source_name = "未知来源"

        # 搜索所有缓存的 feed 条目
        for source_key, (_, entries) in fetcher._cache.items():
            for entry in entries:
                if entry.id == item_id:
                    feed_entry = entry
                    source_name = entry.source_name
                    break
            if feed_entry:
                break

        content = ""
        title = ""
        url = ""
        category = ""
        importance = 0.5

        if feed_entry:
            # 使用内存条目
            content = feed_entry.summary or ""
            title = feed_entry.title
            url = feed_entry.url
            category = feed_entry.category
            importance = feed_entry.importance
        else:
            # 尝试从数据库获取
            from db.models import FeedItem
            from sqlalchemy import select
            result = await db.execute(
                select(FeedItem).where(FeedItem.id == item_id)
            )
            db_item = result.scalar_one_or_none()

            if not db_item:
                return ToKnowledgeBaseResponse(
                    success=False,
                    message="信息条目不存在"
                )

            # 使用数据库条目
            content = db_item.content or db_item.summary or ""
            title = db_item.title
            url = db_item.url or ""
            category = db_item.category or ""
            importance = db_item.importance or 0.5
            source_name = "未知来源"

        # 2. 获取内容（如果需要深度提取）
        if body.extract_deep and content:
            from feeds.depth_fetcher import get_depth_fetcher
            depth_fetcher = get_depth_fetcher()
            try:
                depth_content = await depth_fetcher.fetch_depth_3(
                    content=content,
                    title=title,
                    category=category,
                    llm_client=None
                )
                if depth_content.extracted_data and "error" not in depth_content.extracted_data:
                    content = f"{content}\n\n## 深度分析\n"
                    for key, value in depth_content.extracted_data.items():
                        if key != "置信度":
                            content += f"- {key}: {value}\n"
            except Exception as e:
                pass  # 深度提取失败不影响主流程

        # 3. 调用知识库管理器添加文档
        kb_manager = get_kb_manager()

        # 确保知识库存在
        kb = await kb_manager.get_knowledge_base(body.kb_id)
        if not kb:
            # 创建知识库
            kb = await kb_manager.create_knowledge_base(
                name=f"KB {body.kb_id[:8]}",
                description="从信息流转入"
            )

        # 创建文档并添加到知识库
        kb_doc = KbDocument(
            id=item_id,
            content=content,
            title=title,
            source=url,
            url=url,
            source_type="feed",
            kb_id=body.kb_id,
            metadata={
                "feed_item_id": item_id,
                "source": source_name,
                "category": category,
                "importance": importance,
                "imported_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        try:
            chunk_ids = await kb_manager.add_document(kb_doc, body.kb_id)
            document_id = item_id
        except Exception as e:
            return ToKnowledgeBaseResponse(
                success=False,
                message=f"添加到知识库失败: {str(e)}"
            )

        # 4. 创建关联记录（如果数据库连接可用）
        try:
            from db.models import KnowledgeLink
            from sqlalchemy import select

            # 检查数据库中是否有对应的 feed_item (通过 external_id 或其他方式)
            # 这里我们跳过数据库记录，因为 feed items 主要在内存中
            link_id = None
        except Exception:
            link_id = None  # 数据库记录失败不影响主流程

        return ToKnowledgeBaseResponse(
            success=True,
            knowledge_link_id=link_id,
            document_id=document_id,
            message="已成功转入知识库"
        )

    except Exception as e:
        return ToKnowledgeBaseResponse(
            success=False,
            message=f"转入知识库失败: {str(e)}"
        )


@router.get("/feeds/{item_id}/knowledge-links", response_model=List[Dict])
async def get_feed_knowledge_links(item_id: str, db: AsyncSession = Depends(get_db)):
    """获取信息条目关联的知识库列表"""
    from db.models import KnowledgeLink
    from sqlalchemy import select

    result = await db.execute(
        select(KnowledgeLink).where(KnowledgeLink.feed_item_id == item_id)
    )
    links = result.scalars().all()

    return [
        {
            "id": str(link.id),
            "kb_id": link.knowledge_base_id,
            "status": link.status,
            "linked_at": link.linked_at.isoformat() if link.linked_at else None,
            "notes": link.notes
        }
        for link in links
    ]
