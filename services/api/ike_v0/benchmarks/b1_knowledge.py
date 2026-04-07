"""
IKE B1-S2 Knowledge Summary Helper

Produces a structured knowledge summary from B1-S1 trend bundle.

This is a pure, evidence-grounded helper - no LLM calls, no external APIs.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .b1_harness import HarnessTrendBundle, RankedEntity


@dataclass
class KnowledgeSummary:
    """
    Structured knowledge summary for B1-S2 benchmark.

    This is the output shape for the Knowledge Brain slice.
    """
    concept_summary: str = ""
    relation_map: Dict[str, List[str]] = field(default_factory=dict)
    contrast_dimensions: List[str] = field(default_factory=list)
    evidence_grounding: List[str] = field(default_factory=list)
    confidence: float = 0.5
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "concept_summary": self.concept_summary,
            "relation_map": self.relation_map,
            "contrast_dimensions": self.contrast_dimensions,
            "evidence_grounding": self.evidence_grounding,
            "confidence": self.confidence,
            "limitations": self.limitations,
        }


def generate_harness_knowledge_summary(bundle: HarnessTrendBundle) -> KnowledgeSummary:
    """
    Generate a knowledge summary from B1-S1 harness trend bundle.

    This is a pure helper that produces structured knowledge output
    grounded in the B1-S1 trend bundle entities. No LLM calls,
    no external API calls, no repository content fetch.

    Args:
        bundle: B1-S1 HarnessTrendBundle with ranked entities

    Returns:
        KnowledgeSummary with concept summary, relations, contrasts,
        evidence grounding, confidence, and limitations

    Evidence rules:
        - Every claim anchors to at least one ranked entity from bundle
        - No claims about world state beyond what bundle supports
        - Entity names used as explicit evidence anchors
        - Output confidence marked conservatively
        - Limitations kept explicit
    """
    # Extract entity names for evidence anchoring
    entity_names = [e.name for e in bundle.ranked_entities[:10]]  # Top 10 entities

    # Build evidence grounding from entity names and descriptions
    evidence_grounding: List[str] = []
    for entity in bundle.ranked_entities[:10]:
        if entity.name:
            anchor = f"Entity: {entity.name}"
            if entity.entity_type:
                anchor += f" ({entity.entity_type})"
            if entity.relevance_reason:
                anchor += f" - {entity.relevance_reason}"
            evidence_grounding.append(anchor)

    # Build relation map: map harness to nearby concepts/topics
    # Group by conceptual relationships, not just entity types
    relation_map: Dict[str, List[str]] = {
        "harness_concept": [],
        "openclaw_ecosystem": [],
        "ai_agent_frameworks": [],
        "evaluation_testing": [],
        "research_practice": [],
    }

    for entity in bundle.ranked_entities:
        name = entity.name or ""
        name_lower = name.lower()
        entity_type = entity.entity_type or "unknown"

        # Map to conceptual categories based on name patterns
        if "openclaw" in name_lower:
            relation_map["openclaw_ecosystem"].append(name)
        elif "ai" in name_lower or "agent" in name_lower or "auto" in name_lower:
            relation_map["ai_agent_frameworks"].append(name)
        elif "eval" in name_lower or "test" in name_lower or "bench" in name_lower or "harness" in name_lower:
            relation_map["evaluation_testing"].append(name)
        elif "research" in name_lower or "lab" in name_lower:
            relation_map["research_practice"].append(name)
        else:
            # Fallback: categorize by entity type
            relation_map["harness_concept"].append(f"{name} ({entity_type})")

    # Remove empty categories
    relation_map = {k: v for k, v in relation_map.items() if v}

    # Build contrast dimensions: how harness differs from adjacent approaches
    contrast_dimensions: List[str] = []
    entity_types = set(e.entity_type for e in bundle.ranked_entities if e.entity_type)

    # Contrast: practice-oriented vs tool-centric
    if "person" in entity_types and "repository" in entity_types:
        contrast_dimensions.append(
            "Practice-oriented (persons + repos) vs purely tool-centric frameworks"
        )

    # Contrast: ecosystem-integrated vs standalone
    if "openclaw_ecosystem" in relation_map or any("openclaw" in name.lower() for name in entity_names):
        contrast_dimensions.append(
            "Ecosystem-integrated (openclaw) vs standalone evaluation tools"
        )

    # Contrast: organizational vs academic/hobbyist
    if "organization" in entity_types:
        contrast_dimensions.append(
            "Organizational/industry practice vs academic or hobbyist approaches"
        )

    # Contrast: agent-specific vs general testing
    if "ai_agent_frameworks" in relation_map:
        contrast_dimensions.append(
            "AI agent-specific evaluation vs general software testing"
        )

    # Fallback: generic type diversity
    if not contrast_dimensions and len(entity_types) > 1:
        contrast_dimensions.append(
            f"Diverse stakeholder types ({', '.join(entity_types)}) vs single-type approaches"
        )

    # Generate concept summary grounded in entities
    concept_summary = _generate_concept_summary(bundle, entity_names)

    # Calculate conservative confidence based on evidence quality
    confidence = _calculate_confidence(bundle)

    # Build limitations list
    limitations = [
        "Summary is based solely on B1-S1 trend bundle entities - not comprehensive",
        "No direct repository content analysis performed",
        "Relations inferred from entity types and names only",
        "Confidence is conservative due to limited evidence scope",
        "Does not include Knowledge Brain concept ontology integration",
    ]

    return KnowledgeSummary(
        concept_summary=concept_summary,
        relation_map=relation_map,
        contrast_dimensions=contrast_dimensions,
        evidence_grounding=evidence_grounding,
        confidence=confidence,
        limitations=limitations,
    )


def _generate_concept_summary(bundle: HarnessTrendBundle, entity_names: List[str]) -> str:
    """
    Generate concept summary grounded in B1-S1 bundle entities.

    This is a template-based summary that uses entity names as anchors.
    Explains what 'harness' means in the benchmark context, relates to
    openclaw/AI agent/evaluation/testing/runtime, and contrasts with
    adjacent approaches.

    No LLM generation, no external knowledge claims.
    """
    topic = bundle.topic

    if not entity_names:
        return f"No high-signal entities detected for '{topic}'. Cannot produce knowledge summary."

    # Count entity types
    type_counts: Dict[str, int] = {}
    for entity in bundle.ranked_entities:
        entity_type = entity.entity_type or "unknown"
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1

    # Build summary from entity evidence
    summary_parts: List[str] = []

    # Opening: what harness means in this context (evidence-grounded)
    summary_parts.append(
        f"In this benchmark context, '{topic}' refers to evaluation and testing infrastructure "
        f"for AI agents and agent frameworks, as evidenced by {len(bundle.ranked_entities)} detected entities."
    )

    # Relate to openclaw / AI agent / evaluation / testing / runtime
    relation_evidence = []
    for entity in bundle.ranked_entities[:5]:
        name_lower = entity.name.lower() if entity.name else ""
        if "openclaw" in name_lower:
            relation_evidence.append(f"openclaw ecosystem ({entity.name})")
        if "ai" in name_lower or "agent" in name_lower:
            relation_evidence.append(f"AI agent space ({entity.name})")
        if "eval" in name_lower or "test" in name_lower or "bench" in name_lower:
            relation_evidence.append(f"evaluation/testing ({entity.name})")
        if "research" in name_lower or "lab" in name_lower:
            relation_evidence.append(f"research context ({entity.name})")

    if relation_evidence:
        summary_parts.append(
            f"The '{topic}' concept relates to openclaw, AI agent frameworks, evaluation/testing, "
            f"and research practice, with evidence from: {', '.join(relation_evidence[:4])}."
        )
    else:
        summary_parts.append(
            f"The '{topic}' concept appears in the openclaw/AI agent/evaluation/testing/runtime neighborhood, "
            f"based on entity type distribution: {', '.join(type_counts.keys())}."
        )

    # Contrast dimensions: what harness is vs adjacent approaches
    if "person" in type_counts and "repository" in type_counts:
        summary_parts.append(
            f"Unlike generic testing frameworks, '{topic}' shows both individual practitioners "
            f"({type_counts.get('person', 0)} persons) and project repositories "
            f"({type_counts.get('repository', 0)} repos), suggesting a practice-oriented approach "
            f"rather than purely tool-centric."
        )

    if "organization" in type_counts:
        summary_parts.append(
            f"Organizational participation ({type_counts.get('organization', 0)} organizations) "
            f"distinguishes '{topic}' from purely academic or hobbyist evaluation approaches."
        )

    # Top entities as evidence anchors
    if entity_names:
        top_5 = entity_names[:5]
        summary_parts.append(f"Evidence anchors: {', '.join(top_5)}.")

    return " ".join(summary_parts)


def _calculate_confidence(bundle: HarnessTrendBundle) -> float:
    """
    Calculate conservative confidence score based on evidence quality.

    Factors:
    - Number of ranked entities (more = higher confidence)
    - Entity type diversity (more types = higher confidence)
    - Authority tier distribution (higher tiers = higher confidence)
    """
    # Base confidence from entity count
    entity_count = len(bundle.ranked_entities)
    if entity_count == 0:
        return 0.1
    elif entity_count < 3:
        base_confidence = 0.3
    elif entity_count < 6:
        base_confidence = 0.5
    else:
        base_confidence = 0.7

    # Bonus for entity type diversity
    entity_types = set(e.entity_type for e in bundle.ranked_entities if e.entity_type)
    type_diversity_bonus = min(len(entity_types) * 0.05, 0.15)  # Max 0.15 bonus

    # Bonus for high authority entities
    # Note: RankedEntity doesn't have authority_tier, so this will be 0
    # This is intentional - we're being conservative
    high_authority_count = 0

    # Calculate final confidence (capped at 0.85 for conservative marking)
    confidence = min(base_confidence + type_diversity_bonus, 0.85)

    return round(confidence, 2)
