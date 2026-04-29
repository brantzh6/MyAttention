from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SourceDiscoveryFocus(str, Enum):
    LATEST = "latest"
    AUTHORITATIVE = "authoritative"
    FRONTIER = "frontier"
    METHOD = "method"


class SourceDiscoveryInterestBias(str, Enum):
    AUTHORITY = "authority"
    FRONTIER = "frontier"
    COMMUNITY = "community"
    METHOD = "method"


class SourceDiscoveryRequest(BaseModel):
    task_intent: str = Field("", description="discovery task intent")
    interest_bias: Optional[SourceDiscoveryInterestBias] = Field(
        None, description="signal preference bias"
    )
    topic: str = Field(..., min_length=2, description="需要研究或持续关注的主题")
    focus: SourceDiscoveryFocus = Field(
        SourceDiscoveryFocus.AUTHORITATIVE, description="发现目标"
    )
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
    activity_freshness: float = 0.0
    follow_score: float = 0.0
    inferred_roles: List[str] = []
    related_entities: List[Dict[str, str]] = []
    matched_queries: List[str]
    sample_titles: List[str]
    sample_snippets: List[str]
    object_bucket: str = "authority"
    policy_id: str = ""
    policy_version: int = 1
    policy_score: float = 0.0
    gate_status: str = "candidate"
    selection_reason: str = ""
    source_nature: str = "mixed"
    temperature: str = "medium"
    recommended_mode: str = ""
    recommended_execution_strategy: str = ""
    why_relevant: str = ""
    confidence_note: str = ""
    canonical_ref: str = ""
    candidate_endpoints: List[str] = []


class SourceDiscoveryResponse(BaseModel):
    topic: str
    focus: SourceDiscoveryFocus
    task_intent: str = ""
    interest_bias: SourceDiscoveryInterestBias = SourceDiscoveryInterestBias.AUTHORITY
    queries: List[str]
    policy_id: str = ""
    policy_version: int = 1
    portfolio_summary: Dict[str, Any] = {}
    notes: List[str] = []
    truth_boundary: List[str] = []
    candidates: List[SourceDiscoveryCandidate]
