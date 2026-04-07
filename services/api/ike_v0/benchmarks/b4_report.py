"""
IKE v0.1 B4 Benchmark Report Composer

Composes a complete benchmark report including B4 evidence layers for the harness case.

Output shape:
- concept: The concept being evaluated
- benchmark_id: Report identifier
- b1_bundle: B1 trend bundle with ranked entities
- b1_knowledge: B1 knowledge summary
- b2_tiers: B2 entity tier classification
- b2_gaps: B2 gap mapping
- b2_recommendation: B2 research recommendation
- b2_trigger_packet: B2 research trigger packet
- b3_deepening: B3 concept deepening review
- b4_evidence: B4 evidence layer tagging and summary
- closure_example: Optional closure example (study result + decision handoff)

This is a bounded, additive helper: no router changes, no UI changes, no infrastructure changes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .b1_harness import HarnessTrendBundle
from .b1_knowledge import KnowledgeSummary
from .b2_entity_tiers import B2EntityTiers, classify_benchmark_entity_tiers
from .b2_gap_mapping import B2GapMappingResult
from .b2_recommendation import B2Recommendation, generate_research_recommendation
from .b2_trigger_packet import B2TriggerPacket, generate_trigger_packet
from .b3_deepening import B3ConceptDeepening, generate_concept_deepening
from .b4_evidence_layers import B4EvidenceLayers, tag_ranked_entities, EVIDENCE_LAYER_PRIORITY


@dataclass
class B4BenchmarkReport:
    """
    Complete benchmark report including B4 evidence layers.

    This report composes all benchmark stages (B1-B4) into a single
    structured object suitable for UI presentation or analysis.
    """
    concept: str
    benchmark_id: str = "B4-S3"
    b1_bundle: Optional[HarnessTrendBundle] = None
    b1_knowledge: Optional[KnowledgeSummary] = None
    b2_tiers: Optional[B2EntityTiers] = None
    b2_gaps: Optional[B2GapMappingResult] = None
    b2_recommendation: Optional[B2Recommendation] = None
    b2_trigger_packet: Optional[B2TriggerPacket] = None
    b3_deepening: Optional[B3ConceptDeepening] = None
    b4_evidence: Optional[B4EvidenceLayers] = None
    closure_example: Optional[Dict[str, Any]] = None
    notes: str = ""
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        b1_bundle = self.b1_bundle.to_dict() if self.b1_bundle else None
        b1_knowledge = self.b1_knowledge.to_dict() if self.b1_knowledge else None
        b2_tiers = self.b2_tiers.to_dict() if self.b2_tiers else None
        b2_gaps = self.b2_gaps.to_dict() if self.b2_gaps else None
        b2_recommendation = self.b2_recommendation.to_dict() if self.b2_recommendation else None
        b2_trigger_packet = self.b2_trigger_packet.to_dict() if self.b2_trigger_packet else None
        b3_deepening = self.b3_deepening.to_dict() if self.b3_deepening else None
        b4_evidence = self.b4_evidence.to_dict() if self.b4_evidence else None
        if b4_evidence is not None:
            b4_evidence["evidence_summary"] = _build_evidence_summary(self.b4_evidence)

        return {
            "concept": self.concept,
            "benchmark_id": self.benchmark_id,
            "b1_bundle": b1_bundle,
            "b1_knowledge": b1_knowledge,
            "b2_tiers": b2_tiers,
            "b2_gaps": b2_gaps,
            "b2_recommendation": b2_recommendation,
            "b2_trigger_packet": b2_trigger_packet,
            "b3_deepening": b3_deepening,
            "b4_evidence": b4_evidence,
            "closure_example": self.closure_example,
            "notes": self.notes,
            "limitations": self.limitations,
            # Backward-compatible aliases for the current benchmark story page.
            "bundle": b1_bundle,
            "knowledge": b1_knowledge,
            "tiers": b2_tiers,
            "gaps": b2_gaps,
            "recommendation": b2_recommendation,
            "trigger_packet": b2_trigger_packet,
            "deepening": b3_deepening,
        }


def compose_b4_benchmark_report(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    concept: str = "harness",
    closure_example: Optional[Dict[str, Any]] = None,
) -> B4BenchmarkReport:
    """
    Compose a complete B4 benchmark report from B1/B2/B3/B4 components.

    Args:
        bundle: B1 trend bundle with ranked entities
        knowledge_summary: B1 knowledge summary
        concept: The concept being evaluated (default: "harness")
        closure_example: Optional closure example dict with study_result/decision_handoff

    Returns:
        B4BenchmarkReport with all benchmark stages composed

    This is a pure helper: no LLM calls, no external API calls.
    """
    # B2-S1: Entity tier classification (will use B4 evidence internally)
    b2_tiers = classify_benchmark_entity_tiers(bundle, concept=concept)

    # B2-S2: Gap mapping
    b2_gaps = _compose_gap_mapping(bundle, knowledge_summary, concept)

    # B4: Evidence layer tagging (used by B2 recommendation)
    b4_evidence = tag_ranked_entities(bundle.ranked_entities, topic=concept)

    # B2-S3: Research recommendation (uses B4 evidence)
    b2_recommendation = generate_research_recommendation(
        bundle=bundle,
        knowledge_summary=knowledge_summary,
        gap_mapping=b2_gaps,
        entity_tiers=b2_tiers,
        concept=concept,
        evidence_layers=b4_evidence,
    )

    # B2-S4: Trigger packet
    b2_trigger = generate_trigger_packet(
        bundle=bundle,
        knowledge_summary=knowledge_summary,
        gap_mapping=b2_gaps,
        recommendation=b2_recommendation,
        entity_tiers=b2_tiers,
        concept=concept,
    )

    # B3: Concept deepening
    b3_deepening = generate_concept_deepening(
        bundle=bundle,
        knowledge_summary=knowledge_summary,
        gap_mapping=b2_gaps,
        recommendation=b2_recommendation,
        trigger_packet=b2_trigger,
        entity_tiers=b2_tiers,
        concept=concept,
    )

    # Build evidence layer summary
    evidence_summary = _build_evidence_summary(b4_evidence)

    # Build report notes
    notes = _build_report_notes(concept, b2_tiers, b2_gaps, b2_recommendation, b4_evidence)

    # Standard limitations
    limitations = [
        "Report is heuristic and benchmark-local",
        "Evidence layers assigned via heuristics, not manual review",
        "Does not include hands-on prototype validation",
        "Entity rankings based on discovery output, not direct inspection",
    ]

    return B4BenchmarkReport(
        concept=concept,
        benchmark_id="B4-S3",
        b1_bundle=bundle,
        b1_knowledge=knowledge_summary,
        b2_tiers=b2_tiers,
        b2_gaps=b2_gaps,
        b2_recommendation=b2_recommendation,
        b2_trigger_packet=b2_trigger,
        b3_deepening=b3_deepening,
        b4_evidence=b4_evidence,
        closure_example=closure_example,
        notes=notes,
        limitations=limitations,
    )


def _compose_gap_mapping(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    concept: str,
) -> B2GapMappingResult:
    """Compose gap mapping from B1 evidence."""
    # Import here to avoid circular dependency
    from .b2_gap_mapping import map_concept_to_mainline_gaps
    return map_concept_to_mainline_gaps(bundle, knowledge_summary, concept=concept)


def _build_evidence_summary(b4_evidence: B4EvidenceLayers) -> Dict[str, Any]:
    """Build a compact evidence layer summary."""
    if not b4_evidence or not b4_evidence.tagged_entities:
        return {
            "total_entities": 0,
            "layer_distribution": {},
            "priority_order": list(EVIDENCE_LAYER_PRIORITY.keys()),
            "strongest_evidence": None,
            "weakest_evidence": None,
        }

    # Count by layer
    layer_counts = {}
    for tag in b4_evidence.tagged_entities:
        layer_counts[tag.evidence_layer] = layer_counts.get(tag.evidence_layer, 0) + 1

    # Find strongest and weakest evidence present
    present_layers = [l for l in EVIDENCE_LAYER_PRIORITY.keys() if layer_counts.get(l, 0) > 0]
    strongest = present_layers[0] if present_layers else None
    weakest = present_layers[-1] if present_layers else None

    return {
        "total_entities": len(b4_evidence.tagged_entities),
        "layer_distribution": layer_counts,
        "priority_order": list(EVIDENCE_LAYER_PRIORITY.keys()),
        "strongest_evidence": strongest,
        "weakest_evidence": weakest,
        "tagged_entities": [tag.to_dict() for tag in b4_evidence.tagged_entities],
    }


def _build_report_notes(
    concept: str,
    b2_tiers: B2EntityTiers,
    b2_gaps: B2GapMappingResult,
    b2_recommendation: B2Recommendation,
    b4_evidence: B4EvidenceLayers,
) -> str:
    """Build human-readable report notes."""
    # Count entities by tier
    concept_defining_count = len(b2_tiers.concept_defining.entries) if b2_tiers.concept_defining else 0
    ecosystem_count = len(b2_tiers.ecosystem_relevant.entries) if b2_tiers.ecosystem_relevant else 0
    impl_count = len(b2_tiers.implementation_relevant.entries) if b2_tiers.implementation_relevant else 0

    # Count gaps
    gap_count = len(b2_gaps.mappings) if b2_gaps else 0

    # Evidence summary
    evidence_note = ""
    if b4_evidence and b4_evidence.tagged_entities:
        strong_count = sum(
            1 for tag in b4_evidence.tagged_entities
            if tag.evidence_layer in ("authoritative_official", "expert_maintainer")
        )
        if strong_count > 0:
            evidence_note = f" Includes {strong_count} strong evidence entities (official/maintainer)."

    notes = (
        f"B4 benchmark report for '{concept}'. "
        f"Entity tiers: {concept_defining_count} concept-defining, {ecosystem_count} ecosystem-relevant, {impl_count} implementation-relevant. "
        f"Gap alignment: {gap_count} mainline gaps. "
        f"Recommendation: {b2_recommendation.level if b2_recommendation else 'N/A'} level."
        f"{evidence_note}"
    )

    return notes


def get_evidence_layer_priority_order() -> List[str]:
    """
    Get the canonical evidence layer priority order (highest to lowest).

    Returns:
        List of layer names in priority order
    """
    return [
        "authoritative_official",
        "expert_maintainer",
        "implementation_repository",
        "community_discourse",
        "media_context",
    ]


def summarize_evidence_quality(b4_evidence: B4EvidenceLayers) -> Dict[str, Any]:
    """
    Summarize evidence quality from B4 evidence layers.

    Args:
        b4_evidence: B4 evidence layer tags

    Returns:
        Dictionary with quality summary metrics
    """
    if not b4_evidence or not b4_evidence.tagged_entities:
        return {
            "quality_assessment": "no_evidence",
            "strong_ratio": 0.0,
            "weak_ratio": 0.0,
            "recommendation": "Cannot assess - no evidence available",
        }

    total = len(b4_evidence.tagged_entities)
    strong_count = sum(
        1 for tag in b4_evidence.tagged_entities
        if tag.evidence_layer in ("authoritative_official", "expert_maintainer")
    )
    impl_count = sum(
        1 for tag in b4_evidence.tagged_entities
        if tag.evidence_layer == "implementation_repository"
    )
    weak_count = sum(
        1 for tag in b4_evidence.tagged_entities
        if tag.evidence_layer in ("media_context", "community_discourse")
    )

    strong_ratio = strong_count / total
    weak_ratio = weak_count / total

    # Determine quality assessment
    if strong_ratio >= 0.4:
        quality = "strong"
        recommendation = "Evidence quality supports confident decision-making"
    elif strong_ratio >= 0.2 or impl_count >= 2:
        quality = "moderate"
        recommendation = "Evidence is sufficient for study-level decisions; prototype requires validation"
    elif weak_ratio <= 0.5:
        quality = "limited"
        recommendation = "Evidence is predominantly indirect; recommend continued observation"
    else:
        quality = "weak"
        recommendation = "Evidence is predominantly media/context; cannot support confident decisions"

    return {
        "quality_assessment": quality,
        "strong_ratio": round(strong_ratio, 2),
        "weak_ratio": round(weak_ratio, 2),
        "implementation_count": impl_count,
        "total_entities": total,
        "recommendation": recommendation,
    }
