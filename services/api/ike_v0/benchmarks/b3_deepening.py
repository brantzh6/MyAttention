"""
IKE v0.1 B3 Concept Deepening + Applicability Review Helper

Produces a deterministic concept deepening review from B1/B2 benchmark evidence.

Output shape:
- working_definition: testable definition, not just summary
- boundary_positive: what clearly falls inside the concept
- boundary_negative: what clearly falls outside
- competing_interpretations: alternative ways to understand the concept
- best_fit_interpretation: most appropriate interpretation for this project
- mechanism_to_gap_mapping: how concept mechanisms address mainline gaps
- applicability_judgment: not_applicable|partially_applicable|directly_applicable
- target_ike_layer: which IKE layer this concept most directly applies to
- evidence_quality: assessment of evidence strength
- next_action: recommended next step

Current harness expectation:
- target_ike_layer: evolution layer evaluation operations
- applicability_judgment: partially_applicable (B2-only evidence cannot be directly_applicable)

Note: directly_applicable requires post-study closure evidence, not B2-only evidence.

This is a pure, benchmark-local helper: no LLM calls, no external API calls.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .b1_harness import HarnessTrendBundle
from .b1_knowledge import KnowledgeSummary
from .b2_entity_tiers import B2EntityTiers
from .b2_gap_mapping import B2GapMappingResult
from .b2_recommendation import B2Recommendation
from .b2_trigger_packet import B2TriggerPacket


@dataclass
class B3ConceptDeepening:
    """
    Structured concept deepening review for B3 benchmark.

    Fields:
    - working_definition: Testable definition of the concept
    - boundary_positive: What clearly falls inside the concept
    - boundary_negative: What clearly falls outside the concept
    - competing_interpretations: Alternative interpretations
    - best_fit_interpretation: Most appropriate interpretation for this project
    - mechanism_to_gap_mapping: How concept mechanisms address gaps
    - applicability_judgment: not_applicable|partially_applicable|directly_applicable
    - target_ike_layer: Which IKE layer this concept applies to
    - evidence_quality: Assessment of evidence strength
    - next_action: Recommended next step
    """
    working_definition: str
    boundary_positive: List[str]
    boundary_negative: List[str]
    competing_interpretations: List[str]
    best_fit_interpretation: str
    mechanism_to_gap_mapping: List[Dict[str, str]]
    applicability_judgment: str  # not_applicable|partially_applicable|directly_applicable
    target_ike_layer: str
    evidence_quality: Dict[str, Any]
    next_action: str
    concept: str = "harness"
    benchmark_id: str = "B3-S1"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "working_definition": self.working_definition,
            "boundary_positive": self.boundary_positive,
            "boundary_negative": self.boundary_negative,
            "competing_interpretations": self.competing_interpretations,
            "best_fit_interpretation": self.best_fit_interpretation,
            "mechanism_to_gap_mapping": self.mechanism_to_gap_mapping,
            "applicability_judgment": self.applicability_judgment,
            "target_ike_layer": self.target_ike_layer,
            "evidence_quality": self.evidence_quality,
            "next_action": self.next_action,
            "concept": self.concept,
            "benchmark_id": self.benchmark_id,
        }


def generate_concept_deepening(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    gap_mapping: B2GapMappingResult,
    recommendation: B2Recommendation,
    trigger_packet: Optional[B2TriggerPacket] = None,
    entity_tiers: Optional[B2EntityTiers] = None,
    concept: str = "harness",
) -> B3ConceptDeepening:
    """
    Generate a concept deepening review from B1/B2 benchmark evidence.

    Args:
        bundle: B1 trend bundle with ranked entities
        knowledge_summary: B1 knowledge summary
        gap_mapping: B2-S2 gap mapping result
        recommendation: B2-S3 recommendation
        trigger_packet: Optional B2-S4 trigger packet
        entity_tiers: Optional B2-S1 entity tiers
        concept: The concept being evaluated (default: "harness")

    Returns:
        B3ConceptDeepening with working definition, boundaries, applicability, etc.

    This is a pure helper: no LLM calls, no external API calls.
    """
    # Generate working definition from knowledge summary and entity evidence
    working_definition = _build_working_definition(bundle, knowledge_summary, concept)

    # Define concept boundaries
    boundary_positive = _build_boundary_positive(bundle, entity_tiers, concept)
    boundary_negative = _build_boundary_negative(concept)

    # Identify competing interpretations
    competing_interpretations = _build_competing_interpretations(concept)

    # Select best fit interpretation for this project
    best_fit_interpretation = _select_best_fit_interpretation(
        bundle, knowledge_summary, gap_mapping, concept
    )

    # Map concept mechanisms to mainline gaps
    mechanism_to_gap_mapping = _build_mechanism_to_gap_mapping(gap_mapping, concept)

    # Determine applicability judgment
    applicability_judgment = _determine_applicability_judgment(
        bundle, knowledge_summary, gap_mapping, recommendation, concept
    )

    # Identify target IKE layer
    target_ike_layer = _identify_target_ike_layer(bundle, gap_mapping, concept)

    # Assess evidence quality
    evidence_quality = _assess_evidence_quality(bundle, knowledge_summary, entity_tiers, recommendation)

    # Determine next action
    next_action = _determine_next_action(recommendation, trigger_packet, applicability_judgment, concept)

    return B3ConceptDeepening(
        working_definition=working_definition,
        boundary_positive=boundary_positive,
        boundary_negative=boundary_negative,
        competing_interpretations=competing_interpretations,
        best_fit_interpretation=best_fit_interpretation,
        mechanism_to_gap_mapping=mechanism_to_gap_mapping,
        applicability_judgment=applicability_judgment,
        target_ike_layer=target_ike_layer,
        evidence_quality=evidence_quality,
        next_action=next_action,
        concept=concept,
        benchmark_id="B3-S1",
    )


def _build_working_definition(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    concept: str,
) -> str:
    """Build a testable working definition of the concept."""
    # Extract key themes from knowledge summary
    concept_summary = knowledge_summary.concept_summary if knowledge_summary else ""

    if concept == "harness":
        # For harness: focus on evaluation/testing infrastructure
        return (
            f"'{concept}' is defined as: structured infrastructure for evaluation and testing "
            f"of AI agent capabilities, providing repeatable benchmarks, measurable outcomes, "
            f"and integration patterns for embedding evaluation into development workflows. "
            f"Testable criteria: (1) provides measurable evaluation metrics, "
            f"(2) supports repeatable test execution, "
            f"(3) integrates with existing development tooling."
        )
    else:
        # Generic definition based on knowledge summary
        return (
            f"'{concept}' is defined as: {concept_summary[:200] if concept_summary else 'concept under evaluation'}. "
            f"Working definition derived from B1 knowledge summary and entity evidence."
        )


def _build_boundary_positive(
    bundle: HarnessTrendBundle,
    entity_tiers: Optional[B2EntityTiers],
    concept: str,
) -> List[str]:
    """Build list of what clearly falls inside the concept boundary."""
    boundaries = []

    if concept == "harness":
        boundaries = [
            "AI agent evaluation frameworks and benchmarks",
            "Testing infrastructure for agent capabilities",
            "Measurement tools for agent performance",
            "Integration patterns for evaluation in workflows",
            "Repositories demonstrating harness implementation",
        ]

        # Add specific entities if available
        if entity_tiers:
            try:
                impl_tier = entity_tiers.implementation_relevant
                if hasattr(impl_tier, "entries"):
                    for entry in impl_tier.entries[:3]:
                        if hasattr(entry, "entity_name"):
                            boundaries.append(f"Implementation: {entry.entity_name}")
            except (AttributeError, TypeError):
                pass
    else:
        boundaries = [
            f"Entities and repositories directly addressing '{concept}'",
            "Implementation examples and patterns",
            "Documentation and usage guides",
        ]

    return boundaries


def _build_boundary_negative(concept: str) -> List[str]:
    """Build list of what clearly falls outside the concept boundary."""
    if concept == "harness":
        return [
            "General AI/ML model training frameworks (not evaluation-specific)",
            "One-off evaluation scripts without repeatable structure",
            "Purely theoretical discussions without implementation",
            "Evaluation tools for non-agent systems (e.g., traditional ML models)",
            "Marketing materials without technical substance",
        ]
    else:
        return [
            f"Topics tangentially related to '{concept}' but not core to it",
            "Generic tools without specific applicability",
            "Outdated or superseded approaches",
        ]


def _build_competing_interpretations(concept: str) -> List[str]:
    """Build list of competing interpretations of the concept."""
    if concept == "harness":
        return [
            "Interpretation A: harness as lightweight testing wrappers around agent calls",
            "Interpretation B: harness as comprehensive evaluation platform with metrics dashboards",
            "Interpretation C: harness as integration layer connecting agents to existing test frameworks",
            "Interpretation D: harness as research tool for comparative agent analysis",
        ]
    else:
        return [
            f"Interpretation A: narrow view of '{concept}' focused on specific use cases",
            f"Interpretation B: broad view of '{concept}' as general-purpose framework",
            f"Interpretation C: '{concept}' as integration pattern rather than standalone tool",
        ]


def _select_best_fit_interpretation(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    gap_mapping: B2GapMappingResult,
    concept: str,
) -> str:
    """Select the best fit interpretation for this project context."""
    if concept == "harness":
        # Based on gap mapping (work surface + delegation), interpretation C fits best
        return (
            "Interpretation C: harness as integration layer connecting agents to existing "
            "test frameworks and evaluation workflows. Best fit because: (1) aligns with "
            "'make active work surface understandable' gap, (2) supports 'controlled delegation' "
            "through structured evaluation interfaces, (3) matches practice-oriented evidence "
            "from B1 benchmark entities."
        )
    else:
        return (
            f"Best fit interpretation selected based on gap alignment and entity evidence. "
            f"Derived from {len(bundle.ranked_entities)} entities and {len(gap_mapping.mappings)} aligned gaps."
        )


def _build_mechanism_to_gap_mapping(
    gap_mapping: B2GapMappingResult,
    concept: str,
) -> List[Dict[str, str]]:
    """Build mapping from concept mechanisms to mainline gaps."""
    mappings = []

    for gap in gap_mapping.mappings:
        if gap.relevance_score in ("high", "medium"):
            mechanism = _identify_mechanism_for_gap(gap.gap_id, concept)
            mappings.append({
                "gap_id": gap.gap_id,
                "gap_description": gap.gap_description,
                "mechanism": mechanism,
                "relevance_score": gap.relevance_score,
            })

    return mappings


def _identify_mechanism_for_gap(gap_id: str, concept: str) -> str:
    """Identify the mechanism by which the concept addresses a gap."""
    if concept == "harness":
        mechanisms = {
            "make active work surface understandable": (
                "Provides structured evaluation interfaces that make agent capabilities "
                "and limitations visible and measurable within the development workflow."
            ),
            "reduce token pressure through controlled delegation": (
                "Enables bounded evaluation tasks that can be delegated to specialized "
                "agent instances with clear success criteria and resource limits."
            ),
            "improve source intelligence quality": (
                "Offers systematic evaluation patterns for assessing source quality "
                "through repeatable agent-based analysis."
            ),
            "move evolution toward better reasoning": (
                "Provides benchmark infrastructure for measuring and comparing "
                "agent reasoning capabilities across iterations."
            ),
        }
        return mechanisms.get(gap_id, f"Mechanism for {gap_id} under evaluation")
    else:
        return f"Concept mechanism addressing {gap_id}"


def _determine_applicability_judgment(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    gap_mapping: B2GapMappingResult,
    recommendation: B2Recommendation,
    concept: str,
) -> str:
    """
    Determine applicability judgment.

    Returns one of: not_applicable, partially_applicable, directly_applicable

    Important:
    - directly_applicable requires post-study evidence (prototype or adopt_candidate from closure).
    - B2 recommendation is capped at 'study' level (research trigger, not approval).
    - Therefore B3 with B2-only evidence is at most partially_applicable.
    - Study level indicates indirect evidence only - at most partially_applicable.
    """
    # Count aligned gaps with medium/high relevance
    aligned_gaps = sum(1 for g in gap_mapping.mappings if g.relevance_score in ("high", "medium"))

    # Check recommendation level
    rec_level = recommendation.level if recommendation else "observe"

    # Check entity count as evidence strength
    entity_count = len(bundle.ranked_entities)

    # Determine applicability
    # B3 STAGE CAP: B3 with B2-only evidence cannot be directly_applicable.
    # directly_applicable: requires post-study closure evidence (prototype/adopt from actual study result)
    # partially_applicable: study level or observe with gaps (evidence still indirect)
    # not_applicable: no gap alignment
    if rec_level in ("prototype", "adopt_candidate") and aligned_gaps >= 2 and entity_count >= 3:
        # This branch is only reachable with post-study closure evidence
        return "directly_applicable"
    elif rec_level in ("study", "prototype", "adopt_candidate") and aligned_gaps >= 1:
        # B2 study level = partially_applicable (indirect evidence)
        return "partially_applicable"
    elif aligned_gaps >= 1 and rec_level == "observe":
        return "partially_applicable"
    else:
        return "not_applicable"


def _identify_target_ike_layer(
    bundle: HarnessTrendBundle,
    gap_mapping: B2GapMappingResult,
    concept: str,
) -> str:
    """Identify which IKE layer this concept most directly applies to."""
    if concept == "harness":
        # For harness, based on gap mapping and entity evidence
        # Most likely: evolution layer evaluation operations
        gap_ids = [g.gap_id for g in gap_mapping.mappings]

        if "make active work surface understandable" in gap_ids:
            return "evolution layer evaluation operations"
        elif "reduce token pressure through controlled delegation" in gap_ids:
            return "evolution layer delegation patterns"
        else:
            return "evolution layer evaluation operations"  # Default for harness
    else:
        # Generic layer assignment based on evidence
        if len(bundle.ranked_entities) >= 5:
            return "evolution layer (strong entity evidence)"
        elif len(bundle.ranked_entities) >= 2:
            return "evolution layer (moderate entity evidence)"
        else:
            return "signal layer (limited entity evidence)"


def _assess_evidence_quality(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    entity_tiers: Optional[B2EntityTiers],
    recommendation: B2Recommendation,
) -> Dict[str, Any]:
    """Assess the quality of evidence supporting the concept."""
    entity_count = len(bundle.ranked_entities)
    knowledge_conf = knowledge_summary.confidence if knowledge_summary else 0.5
    rec_conf = recommendation.confidence if recommendation else 0.5

    # Count implementation repositories
    impl_repo_count = 0
    if entity_tiers:
        try:
            impl_tier = entity_tiers.implementation_relevant
            if hasattr(impl_tier, "entries"):
                impl_repo_count = sum(
                    1 for e in impl_tier.entries
                    if hasattr(e, "entity_type") and e.entity_type == "repository"
                )
        except (AttributeError, TypeError):
            pass

    # Calculate overall quality score
    quality_score = min(1.0, (
        (entity_count / 10.0) * 0.3 +  # Entity count contribution (max 30%)
        knowledge_conf * 0.3 +  # Knowledge confidence (max 30%)
        rec_conf * 0.2 +  # Recommendation confidence (max 20%)
        (min(impl_repo_count, 5) / 5.0) * 0.2  # Implementation repos (max 20%)
    ))

    # Determine quality level
    if quality_score >= 0.7:
        quality_level = "high"
    elif quality_score >= 0.4:
        quality_level = "medium"
    else:
        quality_level = "low"

    return {
        "entity_count": entity_count,
        "knowledge_confidence": knowledge_conf,
        "recommendation_confidence": rec_conf,
        "implementation_repos": impl_repo_count,
        "overall_quality_score": round(quality_score, 2),
        "quality_level": quality_level,
    }


def _determine_next_action(
    recommendation: B2Recommendation,
    trigger_packet: Optional[B2TriggerPacket],
    applicability_judgment: str,
    concept: str,
) -> str:
    """Determine recommended next action based on deepening review."""
    if applicability_judgment == "not_applicable":
        return (
            f"Concept '{concept}' assessed as not applicable. "
            f"Recommend archiving trend monitoring and reallocating attention to higher-priority concepts."
        )

    if trigger_packet:
        return (
            f"Proceed with B2-S4 trigger packet ({trigger_packet.packet_id}). "
            f"Task type: {trigger_packet.task_type}. "
            f"Focus: {trigger_packet.bounded_task[:100]}..."
        )

    if recommendation:
        return (
            f"Follow B2-S3 recommendation: {recommendation.level} level. "
            f"Trigger: {recommendation.trigger[:100] if recommendation.trigger else 'See recommendation details'}..."
        )

    return f"Continue monitoring '{concept}' trend for stronger applicability signals."
