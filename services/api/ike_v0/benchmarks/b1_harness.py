"""
IKE B1 Harness Benchmark Helper

Detects harness trend bundle from source-intelligence discovery outputs
and ranks relevant entities.

This is a bounded helper for the B1 benchmark - not a generic trend platform.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RankedEntity:
    """A ranked entity relevant to the harness benchmark."""
    name: str
    entity_type: str  # person, repository, organization, community
    signal_score: float  # 0.0 to 1.0
    relevance_reason: str
    source_refs: List[str] = field(default_factory=list)


@dataclass
class HarnessTrendBundle:
    """
    Structured trend bundle for the B1 harness benchmark.

    This is the output shape for the information brain slice.
    """
    topic: str = "harness"
    benchmark_id: str = "B1-S1"
    signal_summary: str = ""
    ranked_entities: List[RankedEntity] = field(default_factory=list)
    supporting_candidates: List[Dict[str, Any]] = field(default_factory=list)
    notes: str = ""
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "topic": self.topic,
            "benchmark_id": self.benchmark_id,
            "signal_summary": self.signal_summary,
            "ranked_entities": [
                {
                    "name": e.name,
                    "entity_type": e.entity_type,
                    "signal_score": e.signal_score,
                    "relevance_reason": e.relevance_reason,
                    "source_refs": e.source_refs,
                }
                for e in self.ranked_entities
            ],
            "supporting_candidates": self.supporting_candidates,
            "notes": self.notes,
            "limitations": self.limitations,
        }


# Entity types that are meaningful for B1 benchmark ranking
B1_MEANINGFUL_ENTITY_TYPES = {"person", "repository", "organization", "community", "project"}

# Entity types to de-emphasize (keep as supporting context only)
B1_DEEMPHASIZED_TYPES = {"event", "domain", "media", "article", "news", "blog", "website"}


def reshape_discovery_to_benchmark_entities(
    candidates: List[Dict[str, Any]],
    topic: str = "harness",
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Reshape live discovery output toward benchmark-meaningful entities.

    This helper filters and categorizes raw discovery candidates into:
    1. Primary entities: person, repository, organization, community, project
    2. Supporting context: event, domain, generic media (kept for context only)

    Args:
        candidates: List of raw candidate dicts from discovery output
        topic: The topic for context (default: "harness")

    Returns:
        Tuple of (primary_entities, supporting_context) where:
        - primary_entities: Candidates that can be ranked as benchmark entities
        - supporting_context: Candidates kept for context but not top-ranked
    """
    primary_entities: List[Dict[str, Any]] = []
    supporting_context: List[Dict[str, Any]] = []

    for candidate in candidates:
        entity_type = candidate.get("type", "").lower()
        name = candidate.get("name", "")

        # Skip if no name
        if not name:
            continue

        # Check if this is a meaningful entity type for B1
        if entity_type in B1_MEANINGFUL_ENTITY_TYPES:
            primary_entities.append(candidate)
        # Check if this is a de-emphasized type
        elif entity_type in B1_DEEMPHASIZED_TYPES:
            supporting_context.append(candidate)
        # Unknown types: try to infer from description/name
        else:
            description = candidate.get("description", "").lower()
            # Check if description suggests a meaningful entity
            if any(kw in description for kw in ["person", "author", "maintainer", "developer"]):
                candidate["type"] = "person"
                primary_entities.append(candidate)
            elif any(kw in description for kw in ["repo", "repository", "github", "project"]):
                candidate["type"] = "repository"
                primary_entities.append(candidate)
            elif any(kw in description for kw in ["org", "organization", "company", "team"]):
                candidate["type"] = "organization"
                primary_entities.append(candidate)
            elif any(kw in description for kw in ["community", "forum", "discord", "slack"]):
                candidate["type"] = "community"
                primary_entities.append(candidate)
            else:
                # Default to supporting context
                supporting_context.append(candidate)

    return primary_entities, supporting_context


def rank_harness_entities(
    candidates: List[Dict[str, Any]],
    topic: str = "harness",
    context_topics: Optional[List[str]] = None,
) -> List[RankedEntity]:
    """
    Rank candidate entities by signal value for the harness benchmark.

    This helper takes raw candidate entities (e.g., from source-intelligence
    discovery) and ranks them by their likely signal value for understanding
    the harness trend.

    Ranking criteria:
    - Entity type priority: person > repository > organization > community
    - Keyword relevance to harness, openclaw, AI agent, evaluation, testing
    - Avoid generic media dominance

    Args:
        candidates: List of candidate entity dicts with fields like:
            - name: str
            - type: str (person, repository, organization, community, media, etc.)
            - description: str (optional)
            - source_ref: str or list (optional)
            - relevance_keywords: list (optional)
        topic: The main topic (default: "harness")
        context_topics: Related topics for relevance scoring

    Returns:
        List of RankedEntity objects sorted by signal_score (descending)
    """
    if context_topics is None:
        context_topics = ["openclaw", "AI agent", "evaluation", "testing", "runtime", "skill", "agent"]

    # Entity type priority (higher = more signal for this benchmark)
    # B1 benchmark prioritizes: person > repository > organization > community
    type_priority = {
        "person": 1.0,
        "repository": 0.9,
        "organization": 0.7,
        "community": 0.6,
        "project": 0.8,
        # De-emphasized types (should be filtered out before ranking)
        "media": 0.1,
        "article": 0.1,
        "news": 0.1,
        "event": 0.1,
        "domain": 0.1,
        "blog": 0.1,
        "website": 0.1,
    }

    # Keywords that indicate high relevance
    high_relevance_keywords = [
        topic.lower(),
        "openclaw",
        "ai agent",
        "agent",
        "evaluation",
        "testing",
        "runtime",
        "skill",
        "benchmark",
        "orchestration",
        "verification",
    ]

    ranked: List[RankedEntity] = []

    for candidate in candidates:
        name = candidate.get("name", "")
        entity_type = candidate.get("type", "unknown").lower()
        description = candidate.get("description", "").lower()
        source_ref = candidate.get("source_ref", [])
        if isinstance(source_ref, str):
            source_ref = [source_ref]

        # Skip if no name
        if not name:
            continue

        # Calculate type priority score
        type_score = type_priority.get(entity_type, 0.3)

        # Calculate keyword relevance score
        text_to_search = f"{name} {description}".lower()
        keyword_matches = sum(1 for kw in high_relevance_keywords if kw in text_to_search)
        keyword_score = min(keyword_matches / len(high_relevance_keywords), 1.0)

        # Combined signal score (type weighted 60%, keywords 40%)
        signal_score = (type_score * 0.6) + (keyword_score * 0.4)

        # Generate relevance reason
        matched_keywords = [kw for kw in high_relevance_keywords if kw in text_to_search]
        if matched_keywords:
            relevance_reason = f"Matches: {', '.join(matched_keywords[:3])}"
        else:
            relevance_reason = f"Related to {topic} ecosystem"

        ranked.append(RankedEntity(
            name=name,
            entity_type=entity_type,
            signal_score=round(signal_score, 2),
            relevance_reason=relevance_reason,
            source_refs=source_ref,
        ))

    # Sort by signal_score descending
    ranked.sort(key=lambda e: e.signal_score, reverse=True)

    return ranked


def detect_harness_trend_bundle(
    discovery_results: List[Dict[str, Any]],
    topic: str = "harness",
) -> HarnessTrendBundle:
    """
    Detect harness trend bundle from source-intelligence discovery outputs.

    This is the main entry point for the B1-S1 benchmark. It consumes
    discovery result payloads and produces a structured trend bundle.

    Args:
        discovery_results: List of discovery result dicts. Each dict may contain:
            - entities: List of entity dicts
            - candidates: List of candidate dicts
            - signals: List of signal dicts
            Must be provided - no mock data fallback.
        topic: The topic to detect (default: "harness")

    Returns:
        HarnessTrendBundle with ranked entities and signal summary.
        If no entities/candidates found, returns bundle with empty ranked_entities.

    Raises:
        ValueError: If discovery_results is None or empty

    Notes:
        - This is a bounded helper, not a generic trend engine
        - Requires real discovery_results input - no mock data fallback
        - Returns honest empty result if no entities detected
    """
    # Require real discovery results - no mock data fallback
    if discovery_results is None:
        raise ValueError("detect_harness_trend_bundle requires discovery_results input - no mock data fallback")

    if not discovery_results:
        raise ValueError("detect_harness_trend_bundle requires non-empty discovery_results list")

    # Extract all candidates from discovery results
    all_candidates: List[Dict[str, Any]] = []
    for result in discovery_results:
        if "candidates" in result:
            all_candidates.extend(result["candidates"])
        if "entities" in result:
            all_candidates.extend(result["entities"])

    # Reshape discovery output toward benchmark-meaningful entities
    primary_entities, supporting_context = reshape_discovery_to_benchmark_entities(all_candidates, topic=topic)

    # Rank only primary entities (person, repository, organization, community)
    ranked_entities = rank_harness_entities(primary_entities, topic=topic)

    # Combine supporting context with any remaining unranked candidates
    all_supporting = supporting_context + [c for c in all_candidates if c not in primary_entities]

    # Generate signal summary
    if ranked_entities:
        top_entities = ranked_entities[:5]
        entity_names = [e.name for e in top_entities]
        signal_summary = f"Detected {len(ranked_entities)} benchmark entities related to '{topic}'. "
        signal_summary += f"Top signals: {', '.join(entity_names)}."
    else:
        signal_summary = f"No high-signal benchmark entities detected for '{topic}'."

    # Build trend bundle
    bundle = HarnessTrendBundle(
        topic=topic,
        benchmark_id="B1-S1",
        signal_summary=signal_summary,
        ranked_entities=ranked_entities[:20],  # Top 20 benchmark entities
        supporting_candidates=all_supporting[:50],  # Keep up to 50 supporting context items
        notes="This is a bounded benchmark helper for B1-S1. Entity ranking prioritizes persons, repositories, organizations, and communities. Events, domains, and generic media are kept as supporting context only.",
        limitations=[
            "Ranking is heuristic-based, not ML-trained",
            "Does not yet connect to Knowledge Brain for concept summaries",
            "Does not yet produce Evolution Brain action recommendations",
            "Requires real source-intelligence discovery_results input",
            "De-emphasizes event/domain/media types in favor of person/repository/organization/community",
        ],
    )

    return bundle



