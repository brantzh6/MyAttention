"""
IKE v0.1 B4 Evidence Layer Tagger

Tags benchmark entities/candidates with explicit evidence layers:
- authoritative_official: official docs, org statements, release notes
- expert_maintainer: maintainers, core contributors, recognized practitioners
- implementation_repository: repos, implementation guides, technical patterns
- community_discourse: discussions, commentary, adoption chatter
- media_context: articles, news coverage, ecosystem framing (lowest priority)

This is a bounded helper that assigns evidence layers based on entity metadata
and direct heuristics only - no ML scoring, no external API calls.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .b1_harness import RankedEntity


@dataclass
class EvidenceLayerTag:
    """A single entity tagged with an evidence layer."""

    entity_name: str
    entity_type: str
    evidence_layer: str  # One of the 5 evidence layers
    reason: str  # Short rationale for the layer assignment
    source_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entity_name": self.entity_name,
            "entity_type": self.entity_type,
            "evidence_layer": self.evidence_layer,
            "reason": self.reason,
            "source_refs": self.source_refs,
        }


@dataclass
class B4EvidenceLayers:
    """Structured output for B4 evidence layer tagging."""

    tagged_entities: List[EvidenceLayerTag] = field(default_factory=list)
    topic: str = "harness"
    benchmark_id: str = "B4-S1"
    notes: str = ""
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tagged_entities": [e.to_dict() for e in self.tagged_entities],
            "topic": self.topic,
            "benchmark_id": self.benchmark_id,
            "notes": self.notes,
            "limitations": self.limitations,
        }


# Evidence layer priority (higher = stronger evidence)
EVIDENCE_LAYER_PRIORITY = {
    "authoritative_official": 5,
    "expert_maintainer": 4,
    "implementation_repository": 3,
    "community_discourse": 2,
    "media_context": 1,
}

# Valid evidence layers
VALID_EVIDENCE_LAYERS = set(EVIDENCE_LAYER_PRIORITY.keys())


def tag_evidence_layer(
    entity_name: str,
    entity_type: str,
    relevance_reason: str = "",
    description: str = "",
    source_refs: Optional[List[str]] = None,
) -> EvidenceLayerTag:
    """
    Tag a single entity with an evidence layer.

    Args:
        entity_name: Name of the entity
        entity_type: Type (person, repository, organization, community, etc.)
        relevance_reason: Relevance reason from B1 ranking
        description: Optional description of the entity
        source_refs: Optional list of source references

    Returns:
        EvidenceLayerTag with assigned layer and rationale

    Layer assignment heuristics:
        - authoritative_official: org-owned repos, official docs, release notes
        - expert_maintainer: persons identified as authors/maintainers/core
        - implementation_repository: repos with technical implementation patterns
        - community_discourse: community discussions, forums, discourse
        - media_context: articles, news, media coverage (lowest priority)
    """
    if source_refs is None:
        source_refs = []

    name_lower = entity_name.lower()
    type_lower = entity_type.lower()
    relevance_lower = relevance_reason.lower()
    desc_lower = description.lower()
    combined_text = f"{name_lower} {relevance_lower} {desc_lower}"

    # Check for authoritative_official signals
    authoritative_signals = [
        "official", "organization-owned", "org-owned", "release notes",
        "official documentation", "project documentation", "owned by",
    ]
    if any(sig in combined_text for sig in authoritative_signals):
        return EvidenceLayerTag(
            entity_name=entity_name,
            entity_type=entity_type,
            evidence_layer="authoritative_official",
            reason="Official or organization-owned source",
            source_refs=source_refs,
        )

    # Check for expert_maintainer signals (persons with direct technical ownership)
    maintainer_signals = [
        "author", "maintainer", "core", "founder", "creator",
        "primary", "principal", "lead", "owner",
    ]
    if type_lower == "person" and any(sig in combined_text for sig in maintainer_signals):
        return EvidenceLayerTag(
            entity_name=entity_name,
            entity_type=entity_type,
            evidence_layer="expert_maintainer",
            reason="Person identified as author, maintainer, or core contributor",
            source_refs=source_refs,
        )

    # Check for implementation_repository signals
    repo_signals = [
        "repository", "implementation", "framework", "tool", "library",
        "package", "sdk", "code", "github", "gitlab", "technical",
        "pattern", "integration", "practice guide",
    ]
    if type_lower == "repository" or any(sig in combined_text for sig in repo_signals):
        # Only assign implementation_repository if there's direct technical rationale
        if type_lower == "repository" or any(sig in combined_text for sig in ["implementation", "tool", "framework", "technical", "pattern"]):
            return EvidenceLayerTag(
                entity_name=entity_name,
                entity_type=entity_type,
                evidence_layer="implementation_repository",
                reason="Repository or technical implementation evidence",
                source_refs=source_refs,
            )

    # Check for community_discourse signals
    community_signals = [
        "community", "discussion", "forum", "discord", "slack", "reddit",
        "chatter", "adoption", "discourse", "practitioner", "commentary",
    ]
    if type_lower == "community" or any(sig in combined_text for sig in community_signals):
        return EvidenceLayerTag(
            entity_name=entity_name,
            entity_type=entity_type,
            evidence_layer="community_discourse",
            reason="Community discussion or practitioner discourse",
            source_refs=source_refs,
        )

    # Check for media_context signals (lowest priority)
    media_signals = [
        "article", "news", "media", "coverage", "blog", "write-up",
        "writeup", "announcement", "ecosystem trend",
    ]
    if type_lower in ["media", "article", "news", "blog"] or any(sig in combined_text for sig in media_signals):
        return EvidenceLayerTag(
            entity_name=entity_name,
            entity_type=entity_type,
            evidence_layer="media_context",
            reason="Media or news coverage (background context only)",
            source_refs=source_refs,
        )

    # Default fallback based on entity type
    if type_lower == "organization":
        return EvidenceLayerTag(
            entity_name=entity_name,
            entity_type=entity_type,
            evidence_layer="authoritative_official",
            reason="Organization entity (default to authoritative)",
            source_refs=source_refs,
        )
    elif type_lower == "person":
        return EvidenceLayerTag(
            entity_name=entity_name,
            entity_type=entity_type,
            evidence_layer="expert_maintainer",
            reason="Person entity (default to expert/maintainer)",
            source_refs=source_refs,
        )
    elif type_lower == "repository":
        return EvidenceLayerTag(
            entity_name=entity_name,
            entity_type=entity_type,
            evidence_layer="implementation_repository",
            reason="Repository entity (default to implementation)",
            source_refs=source_refs,
        )
    elif type_lower == "community":
        return EvidenceLayerTag(
            entity_name=entity_name,
            entity_type=entity_type,
            evidence_layer="community_discourse",
            reason="Community entity (default to discourse)",
            source_refs=source_refs,
        )
    else:
        # Unknown type: default to media_context (lowest priority)
        return EvidenceLayerTag(
            entity_name=entity_name,
            entity_type=entity_type,
            evidence_layer="media_context",
            reason=f"Unknown entity type '{entity_type}' (default to media context)",
            source_refs=source_refs,
        )


def tag_benchmark_evidence_layers(
    entities: List[Dict[str, Any]],
    topic: str = "harness",
) -> B4EvidenceLayers:
    """
    Tag a list of benchmark entities with evidence layers.

    Args:
        entities: List of entity dicts with fields:
            - name: str
            - type: str (person, repository, organization, community, etc.)
            - relevance_reason: str (optional)
            - description: str (optional)
            - source_refs: list (optional)
        topic: The topic for context (default: "harness")

    Returns:
        B4EvidenceLayers with all entities tagged

    This is a pure helper: no LLM calls, no external API calls.
    Uses only entity metadata and direct heuristics.
    """
    tagged: List[EvidenceLayerTag] = []

    for entity in entities:
        name = entity.get("name", "")
        entity_type = entity.get("type", "unknown")
        relevance_reason = entity.get("relevance_reason", "")
        description = entity.get("description", "")
        source_refs = entity.get("source_refs", [])

        if not name:
            continue

        tag = tag_evidence_layer(
            entity_name=name,
            entity_type=entity_type,
            relevance_reason=relevance_reason,
            description=description,
            source_refs=source_refs if isinstance(source_refs, list) else [],
        )
        tagged.append(tag)

    # Sort by evidence layer priority (highest first)
    tagged.sort(key=lambda e: EVIDENCE_LAYER_PRIORITY.get(e.evidence_layer, 0), reverse=True)

    # Build notes
    layer_counts = {}
    for t in tagged:
        layer_counts[t.evidence_layer] = layer_counts.get(t.evidence_layer, 0) + 1

    notes = (
        f"B4 evidence layer tagging for concept '{topic}'. "
        f"Total entities tagged: {len(tagged)}. "
        f"Distribution: {', '.join(f'{k}={v}' for k, v in sorted(layer_counts.items()))}. "
    )

    limitations = [
        "Tagging is heuristic-based, not ML-trained",
        "Uses only entity metadata and direct heuristics",
        "Does not inspect actual repository content",
        "May misclassify entities with ambiguous signals",
        "Media/context entities are de-emphasized but not filtered",
    ]

    return B4EvidenceLayers(
        tagged_entities=tagged,
        topic=topic,
        benchmark_id="B4-S1",
        notes=notes,
        limitations=limitations,
    )


def tag_ranked_entities(
    ranked_entities: List[RankedEntity],
    topic: str = "harness",
) -> B4EvidenceLayers:
    """
    Tag RankedEntity objects from B1 benchmark with evidence layers.

    Args:
        ranked_entities: List of RankedEntity objects from B1 ranking
        topic: The topic for context (default: "harness")

    Returns:
        B4EvidenceLayers with all entities tagged

    This is a convenience wrapper that converts RankedEntity to dict format.
    """
    # Convert RankedEntity to dict format
    entities = [
        {
            "name": e.name,
            "type": e.entity_type,
            "relevance_reason": e.relevance_reason,
            "source_refs": e.source_refs,
        }
        for e in ranked_entities
    ]

    return tag_benchmark_evidence_layers(entities, topic=topic)
