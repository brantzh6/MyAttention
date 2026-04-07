"""
IKE B1-S3 Evolution Judgment Helper

Produces an evolution-brain judgment from B1-S1 trend bundle and B1-S2 knowledge summary.

This is a pure, evidence-grounded helper - no LLM calls, no external APIs, no strategy rewrite.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .b1_harness import HarnessTrendBundle
from .b1_knowledge import KnowledgeSummary


@dataclass
class EvolutionJudgment:
    """
    Structured evolution judgment for B1-S3 benchmark.

    This is the output shape for the Evolution Brain slice.
    """
    relevance_judgment: str = ""
    gap_alignment: List[str] = field(default_factory=list)
    proposed_action: str = ""
    limitations: List[str] = field(default_factory=list)
    confidence: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "relevance_judgment": self.relevance_judgment,
            "gap_alignment": self.gap_alignment,
            "proposed_action": self.proposed_action,
            "limitations": self.limitations,
            "confidence": self.confidence,
        }


# Current project mainline gaps for alignment
MAINLINE_GAPS = [
    "improve source intelligence quality",
    "make active work surface understandable",
    "move evolution toward better reasoning",
    "reduce token pressure through controlled delegation",
]


def generate_evolution_judgment(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
) -> EvolutionJudgment:
    """
    Generate an evolution judgment from B1-S1 and B1-S2 outputs.

    This is a pure helper that produces a bounded evolution-brain judgment.
    No LLM calls, no external API calls, no strategy rewrite.

    Args:
        bundle: B1-S1 HarnessTrendBundle with ranked entities
        knowledge_summary: B1-S2 KnowledgeSummary with concept analysis

    Returns:
        EvolutionJudgment with relevance, gap alignment, proposed action,
        limitations, and conservative confidence

    Decision rules:
        - Trend must touch at least one current mainline goal to matter
        - Relevance judgment must anchor to B1-S1/S2 evidence
        - Confidence must be conservative
        - No strategy rewrite
        - Gap alignment must map to named current mainline gaps

    Action rules:
        - One primary action only
        - Action must be bounded and implementable without new infrastructure
        - Success criteria must be verifiable
    """
    # Determine relevance judgment based on evidence
    relevance_judgment = _determine_relevance(bundle, knowledge_summary)

    # Align to mainline gaps
    gap_alignment = _align_to_gaps(bundle, knowledge_summary)

    # Propose one bounded action
    proposed_action = _propose_action(bundle, knowledge_summary, gap_alignment)

    # Build limitations list
    limitations = [
        "Judgment is based solely on B1-S1/S2 evidence - not comprehensive world knowledge",
        "Action proposal is bounded to current infrastructure - no new capabilities assumed",
        "Confidence is conservative due to limited evidence scope",
        "Does not include full evolution-brain reasoning pipeline integration",
    ]

    # Calculate conservative confidence
    confidence = _calculate_judgment_confidence(bundle, knowledge_summary, gap_alignment)

    return EvolutionJudgment(
        relevance_judgment=relevance_judgment,
        gap_alignment=gap_alignment,
        proposed_action=proposed_action,
        limitations=limitations,
        confidence=confidence,
    )


def _determine_relevance(bundle: HarnessTrendBundle, knowledge_summary: KnowledgeSummary) -> str:
    """
    Determine relevance judgment anchored to B1-S1/S2 evidence.

    The trend must touch at least one current mainline goal to be judged relevant.
    """
    topic = bundle.topic
    entity_count = len(bundle.ranked_entities)

    if entity_count == 0:
        return f"No evidence detected for '{topic}'. Cannot determine relevance to mainline goals."

    # Check if trend touches mainline gaps
    concept_lower = knowledge_summary.concept_summary.lower()

    relevance_indicators = []

    # Check alignment with each mainline gap
    if "source" in concept_lower or "intelligence" in concept_lower:
        relevance_indicators.append("source intelligence quality")

    if "work surface" in concept_lower or "understandable" in concept_lower or "visible" in concept_lower:
        relevance_indicators.append("active work surface understandability")

    if "reasoning" in concept_lower or "evolution" in concept_lower:
        relevance_indicators.append("evolution reasoning capability")

    if "token" in concept_lower or "delegation" in concept_lower:
        relevance_indicators.append("token pressure reduction through delegation")

    # Check entity types for relevance signals
    entity_types = set(e.entity_type for e in bundle.ranked_entities if e.entity_type)
    if "repository" in entity_types or "person" in entity_types:
        relevance_indicators.append("practice-oriented evidence (persons/repos)")

    # Build relevance judgment
    if relevance_indicators:
        indicators_str = ", ".join(relevance_indicators)
        return (
            f"The '{topic}' trend is RELEVANT to current mainline goals. "
            f"Evidence anchors: {entity_count} entities detected. "
            f"Touches mainline gaps: {indicators_str}. "
            f"Knowledge summary confirms positioning in openclaw/AI agent/evaluation neighborhood."
        )
    else:
        return (
            f"The '{topic}' trend shows LIMITED relevance to current mainline goals. "
            f"Evidence: {entity_count} entities detected, but no clear alignment with "
            f"source intelligence, work surface, reasoning evolution, or delegation gaps. "
            f"May represent adjacent but non-prioritized area."
        )


def _align_to_gaps(bundle: HarnessTrendBundle, knowledge_summary: KnowledgeSummary) -> List[str]:
    """
    Align trend to named current mainline gaps.

    Returns list of gap names that the trend aligns with.
    """
    aligned_gaps: List[str] = []
    concept_lower = knowledge_summary.concept_summary.lower()
    relation_keys = list(knowledge_summary.relation_map.keys())

    # Gap 1: improve source intelligence quality
    if any(kw in concept_lower for kw in ["source", "intelligence", "discovery", "detection"]):
        aligned_gaps.append("improve source intelligence quality")
    if "openclaw_ecosystem" in relation_keys or "evaluation_testing" in relation_keys:
        if "improve source intelligence quality" not in aligned_gaps:
            aligned_gaps.append("improve source intelligence quality")

    # Gap 2: make active work surface understandable
    if any(kw in concept_lower for kw in ["work surface", "understandable", "visible", "inspect"]):
        aligned_gaps.append("make active work surface understandable")
    if knowledge_summary.contrast_dimensions:
        # Contrast dimensions suggest effort to make concepts understandable
        if "make active work surface understandable" not in aligned_gaps:
            aligned_gaps.append("make active work surface understandable")

    # Gap 3: move evolution toward better reasoning
    if any(kw in concept_lower for kw in ["reasoning", "evolution", "evaluation", "benchmark"]):
        aligned_gaps.append("move evolution toward better reasoning")
    if "ai_agent_frameworks" in relation_keys or "research_practice" in relation_keys:
        if "move evolution toward better reasoning" not in aligned_gaps:
            aligned_gaps.append("move evolution toward better reasoning")

    # Gap 4: reduce token pressure through controlled delegation
    if any(kw in concept_lower for kw in ["delegation", "token", "efficiency", "skill"]):
        aligned_gaps.append("reduce token pressure through controlled delegation")

    return aligned_gaps


def _propose_action(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    gap_alignment: List[str],
) -> str:
    """
    Propose one bounded, implementable action.

    Action must be bounded and implementable without new infrastructure.
    Success criteria must be verifiable.
    """
    if not gap_alignment:
        return (
            "NO ACTION: Trend does not align with current mainline gaps. "
            "Recommend monitoring for future relevance signals."
        )

    # Prioritize action based on strongest gap alignment
    primary_gap = gap_alignment[0]

    if "source intelligence" in primary_gap:
        return (
            f"PRIMARY ACTION: Integrate top 3 ranked entities from B1-S1 bundle "
            f"as explicit source intelligence candidates. "
            f"Success criteria: entities added to source discovery watchlist within 1 iteration. "
            f"Evidence anchors: {', '.join([e.name for e in bundle.ranked_entities[:3]])}."
        )

    elif "work surface" in primary_gap:
        return (
            f"PRIMARY ACTION: Add B1-S2 concept summary and relation map to active work surface "
            f"as context for current evolution tasks. "
            f"Success criteria: concept summary visible in next evolution task context. "
            f"Evidence anchors: {knowledge_summary.concept_summary[:100]}..."
        )

    elif "reasoning" in primary_gap:
        return (
            f"PRIMARY ACTION: Use B1-S2 contrast dimensions to inform next evolution reasoning step. "
            f"Success criteria: contrast dimensions referenced in evolution task rationale. "
            f"Evidence anchors: {', '.join(knowledge_summary.contrast_dimensions[:2])}."
        )

    elif "delegation" in primary_gap:
        return (
            f"PRIMARY ACTION: Evaluate top-ranked repository entities for skill delegation candidates. "
            f"Success criteria: at least 1 repository evaluated for delegation potential. "
            f"Evidence anchors: {', '.join([e.name for e in bundle.ranked_entities[:3] if e.entity_type == 'repository'])}."
        )

    else:
        return (
            f"PRIMARY ACTION: Monitor trend for stronger alignment signals. "
            f"Success criteria: re-evaluate after next B1-S1 discovery cycle. "
            f"Current evidence: {len(bundle.ranked_entities)} entities, {len(gap_alignment)} gap alignments."
        )


def _calculate_judgment_confidence(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    gap_alignment: List[str],
) -> float:
    """
    Calculate conservative confidence for evolution judgment.

    Factors:
    - Number of ranked entities (more = higher confidence)
    - Number of gap alignments (more = higher confidence)
    - Knowledge summary quality (evidence grounding, etc.)
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
        base_confidence = 0.6

    # Bonus for gap alignments
    gap_bonus = min(len(gap_alignment) * 0.1, 0.2)  # Max 0.2 bonus

    # Bonus for knowledge summary quality
    knowledge_bonus = 0.0
    if knowledge_summary.evidence_grounding:
        knowledge_bonus += 0.05
    if knowledge_summary.relation_map:
        knowledge_bonus += 0.05

    # Calculate final confidence (capped at 0.75 for conservative marking)
    confidence = min(base_confidence + gap_bonus + knowledge_bonus, 0.75)

    return round(confidence, 2)
