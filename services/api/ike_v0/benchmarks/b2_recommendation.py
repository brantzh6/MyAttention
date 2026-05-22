"""
IKE v0.1 B2-S3 Research Recommendation Helper

Produces a deterministic research recommendation level from B1/B2 benchmark evidence.

Output shape:
- level: one of observe|study (B2 is capped at study)
- rationale
- confidence
- trigger
- blockers
- limitations

Recommendation logic:
- observe: only signal/meaning, no clear gap alignment
- study: >=1 explicit mainline gap from B2-S2, evidence still indirect

B2 STAGE CAP:
- B2 is a research trigger stage, not prototype approval.
- B2 recommendation is capped at 'study' level.
- prototype/adopt_candidate require post-study validation (B3+ closure).

Current benchmark expectation for harness:
- level = study
- bounded trigger: inspect 2-3 implementation-relevant repositories

B4 Integration:
- Evidence layer quality shapes confidence and rationale
- Media/context-heavy evidence keeps recommendation conservative
- Strong authoritative/maintainer evidence can improve confidence (not level)

This is a pure, benchmark-local helper: no LLM calls, no external API calls.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .b1_harness import HarnessTrendBundle
from .b1_knowledge import KnowledgeSummary
from .b2_entity_tiers import B2EntityTiers
from .b2_gap_mapping import B2GapMappingResult
from .b4_evidence_layers import tag_ranked_entities, B4EvidenceLayers, EVIDENCE_LAYER_PRIORITY


@dataclass
class B2Recommendation:
    """
    Structured research recommendation for B2-S3 benchmark.

    Levels:
    - observe: only signal/meaning, no clear gap alignment
    - study: >=1 explicit mainline gap, evidence still indirect (B2 max level)
    
    Note: B2 is a research trigger stage. prototype/adopt_candidate require
    post-study validation (B3+ closure evidence) and are not produced at B2.
    """
    level: str  # observe|study|prototype|adopt_candidate
    rationale: str
    confidence: float  # 0.0 to 1.0
    trigger: str
    blockers: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    concept: str = "harness"
    benchmark_id: str = "B2-S3"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "level": self.level,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "trigger": self.trigger,
            "blockers": self.blockers,
            "limitations": self.limitations,
            "concept": self.concept,
            "benchmark_id": self.benchmark_id,
        }


def generate_research_recommendation(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    gap_mapping: B2GapMappingResult,
    entity_tiers: Optional[B2EntityTiers] = None,
    concept: str = "harness",
    evidence_layers: Optional[B4EvidenceLayers] = None,
) -> B2Recommendation:
    """
    Generate a research recommendation from B1/B2 benchmark evidence.

    Args:
        bundle: B1 trend bundle with ranked entities
        knowledge_summary: B1 knowledge summary
        gap_mapping: B2-S2 gap mapping result
        entity_tiers: Optional B2-S1 entity tiers
        concept: The concept being evaluated (default: "harness")
        evidence_layers: Optional B4 evidence layer tags

    Returns:
        B2Recommendation with level, rationale, confidence, trigger, blockers, limitations

    B4 Integration:
        - Evidence layer quality shapes confidence and rationale
        - Media/context-heavy evidence keeps recommendation conservative
        - Strong authoritative/maintainer evidence can improve confidence

    This is a pure helper: no LLM calls, no external API calls.
    """
    # Derive evidence layers if not provided
    if evidence_layers is None:
        evidence_layers = tag_ranked_entities(bundle.ranked_entities, topic=concept)

    # Determine recommendation level based on evidence
    level, level_reasons = _determine_recommendation_level(
        bundle=bundle,
        knowledge_summary=knowledge_summary,
        gap_mapping=gap_mapping,
        entity_tiers=entity_tiers,
        concept=concept,
    )

    # Build rationale with evidence layer context
    rationale = _build_rationale(level, level_reasons, gap_mapping, concept, evidence_layers)

    # Calculate confidence based on evidence strength including B4 layers
    confidence = _calculate_confidence(level, bundle, knowledge_summary, gap_mapping, evidence_layers)

    # Generate bounded trigger for next action
    trigger = _generate_trigger(level, entity_tiers, concept)

    # Identify blockers for advancing to next level
    blockers = _identify_blockers(level, entity_tiers, concept, evidence_layers)

    # Standard limitations for benchmark-local recommendations
    limitations = [
        "Recommendation is heuristic and benchmark-local",
        "Based solely on B1/B2 evidence without external validation",
        "Does not include hands-on prototype testing",
        "May not capture recent developments outside benchmark data",
    ]

    return B2Recommendation(
        level=level,
        rationale=rationale,
        confidence=confidence,
        trigger=trigger,
        blockers=blockers,
        limitations=limitations,
        concept=concept,
        benchmark_id="B2-S3",
    )


def _determine_recommendation_level(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    gap_mapping: B2GapMappingResult,
    entity_tiers: Optional[B2EntityTiers],
    concept: str,
) -> tuple:
    """
    Determine recommendation level based on evidence.

    Returns:
        Tuple of (level, list of reasons)
    """
    reasons = []

    # Count gaps with medium/high relevance
    aligned_gaps = [m for m in gap_mapping.mappings if m.relevance_score in ("high", "medium")]
    gap_count = len(aligned_gaps)

    # Check for implementation repositories
    impl_repo_count = 0
    if entity_tiers is not None:
        try:
            impl_tier = entity_tiers.implementation_relevant
            if hasattr(impl_tier, "entries"):
                impl_repo_count = sum(
                    1 for entry in impl_tier.entries
                    if hasattr(entry, "entity_type") and entry.entity_type == "repository"
                )
        except (AttributeError, TypeError):
            pass

    # Check entity count as signal strength indicator
    entity_count = len(bundle.ranked_entities)

    # Determine level based on evidence
    # B2 STAGE CAP: B2 is a research trigger stage, not prototype approval.
    # B2 recommendation must remain conservative (max: study).
    # prototype/adopt_candidate require post-study validation (B3+ closure evidence).
    # 
    # Level semantics:
    # - study: >=1 gap alignment, evidence still indirect (current harness case)
    # - observe: only signal/meaning, no clear gap alignment

    if gap_count >= 1:
        level = "study"
        reasons.append(f"Gap alignment present ({gap_count} gaps)")
        reasons.append("Evidence still indirect, no direct repository validation")
    elif entity_count >= 1:
        level = "observe"
        reasons.append("Signal and meaning present")
        reasons.append("No clear gap alignment yet")
    else:
        level = "observe"
        reasons.append("Limited evidence available")

    return level, reasons


def _build_rationale(
    level: str,
    level_reasons: List[str],
    gap_mapping: B2GapMappingResult,
    concept: str,
    evidence_layers: Optional[B4EvidenceLayers] = None,
) -> str:
    """Build human-readable rationale for the recommendation."""
    gap_ids = [m.gap_id for m in gap_mapping.mappings]

    # Build evidence quality context
    evidence_note = ""
    if evidence_layers and evidence_layers.tagged_entities:
        # Count evidence layer distribution
        layer_counts = {}
        for tag in evidence_layers.tagged_entities:
            layer_counts[tag.evidence_layer] = layer_counts.get(tag.evidence_layer, 0) + 1

        # Check if evidence is mostly weak (media_context or community_discourse)
        weak_count = layer_counts.get("media_context", 0) + layer_counts.get("community_discourse", 0)
        strong_count = layer_counts.get("authoritative_official", 0) + layer_counts.get("expert_maintainer", 0)
        impl_count = layer_counts.get("implementation_repository", 0)

        total = len(evidence_layers.tagged_entities)
        if total > 0:
            weak_ratio = weak_count / total
            strong_ratio = strong_count / total

            if weak_ratio > 0.5:
                evidence_note = " Evidence is predominantly media/context or community discourse."
            elif strong_ratio > 0.3 or impl_count > 0:
                evidence_note = " Evidence includes authoritative, maintainer, or implementation sources."

    if level == "study":
        rationale = (
            f"Recommendation for '{concept}': study level. "
            f"Aligned with {len(gap_mapping.mappings)} mainline gap(s): "
            f"{', '.join(gap_ids)}. "
            f"Evidence suggests potential value but requires validation. "
            f"{' '.join(level_reasons)}"
            f"{evidence_note}"
        )
    elif level == "observe":
        rationale = (
            f"Recommendation for '{concept}': observe level. "
            f"{' '.join(level_reasons)}. "
            f"Continue monitoring for stronger signals."
            f"{evidence_note}"
        )
    elif level == "prototype":
        rationale = (
            f"Recommendation for '{concept}': prototype level. "
            f"Strong alignment with {len(gap_mapping.mappings)} gap(s). "
            f"Implementation evidence supports hands-on evaluation. "
            f"{' '.join(level_reasons)}"
            f"{evidence_note}"
        )
    elif level == "adopt_candidate":
        rationale = (
            f"Recommendation for '{concept}': adopt candidate level. "
            f"Strong prototype evidence and readiness signals. "
            f"{' '.join(level_reasons)}"
            f"{evidence_note}"
        )
    else:
        rationale = f"Recommendation for '{concept}': {level}. {' '.join(level_reasons)}{evidence_note}"

    return rationale


def _calculate_confidence(
    level: str,
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    gap_mapping: B2GapMappingResult,
    evidence_layers: Optional[B4EvidenceLayers] = None,
) -> float:
    """
    Calculate confidence score based on evidence strength.

    Returns a float between 0.0 and 1.0.

    B4 Integration:
        - Strong evidence layers (authoritative, maintainer) boost confidence
        - Media/context-heavy evidence reduces confidence
        - Implementation repositories provide moderate boost
    """
    # Base confidence by level
    base_confidence = {
        "observe": 0.3,
        "study": 0.5,
        "prototype": 0.7,
        "adopt_candidate": 0.85,
    }

    confidence = base_confidence.get(level, 0.5)

    # Adjust based on entity count (more entities = more evidence)
    entity_count = len(bundle.ranked_entities)
    if entity_count >= 5:
        confidence += 0.1
    elif entity_count >= 3:
        confidence += 0.05

    # Adjust based on knowledge confidence
    if knowledge_summary and knowledge_summary.confidence:
        knowledge_conf = knowledge_summary.confidence
        confidence += (knowledge_conf - 0.5) * 0.2  # Scale knowledge influence

    # Adjust based on gap mapping strength
    high_relevance_gaps = sum(1 for m in gap_mapping.mappings if m.relevance_score == "high")
    if high_relevance_gaps >= 2:
        confidence += 0.1
    elif high_relevance_gaps >= 1:
        confidence += 0.05

    # B4 evidence layer adjustment
    if evidence_layers and evidence_layers.tagged_entities:
        total = len(evidence_layers.tagged_entities)
        if total > 0:
            # Count by layer
            strong_count = sum(
                1 for tag in evidence_layers.tagged_entities
                if tag.evidence_layer in ("authoritative_official", "expert_maintainer")
            )
            impl_count = sum(
                1 for tag in evidence_layers.tagged_entities
                if tag.evidence_layer == "implementation_repository"
            )
            weak_count = sum(
                1 for tag in evidence_layers.tagged_entities
                if tag.evidence_layer in ("media_context", "community_discourse")
            )

            strong_ratio = strong_count / total
            weak_ratio = weak_count / total

            # Strong evidence boosts confidence (up to +0.1)
            if strong_ratio > 0.3:
                confidence += 0.1
            elif strong_ratio > 0.1:
                confidence += 0.05

            # Implementation repos provide moderate boost
            if impl_count >= 2:
                confidence += 0.05

            # Weak evidence (media-heavy) reduces confidence
            if weak_ratio > 0.5:
                confidence -= 0.1
            elif weak_ratio > 0.3:
                confidence -= 0.05

    # Clamp to valid range
    confidence = max(0.1, min(0.95, confidence))

    return round(confidence, 2)


def _generate_trigger(
    level: str,
    entity_tiers: Optional[B2EntityTiers],
    concept: str,
) -> str:
    """
    Generate a bounded trigger for next action.

    For harness: inspect 2-3 implementation-relevant repositories.
    """
    if level == "study":
        # Get implementation-relevant repositories if available
        impl_repos = []
        if entity_tiers is not None:
            try:
                impl_tier = entity_tiers.implementation_relevant
                if hasattr(impl_tier, "entries"):
                    impl_repos = [
                        entry.entity_name
                        for entry in impl_tier.entries
                        if hasattr(entry, "entity_type") and entry.entity_type == "repository"
                    ]
            except (AttributeError, TypeError):
                pass

        if impl_repos:
            repo_list = ", ".join(impl_repos[:3])
            trigger = (
                f"Inspect {min(len(impl_repos), 3)} implementation-relevant "
                f"repositories ({repo_list}) to determine whether {concept} "
                f"patterns fit project evaluation needs."
            )
        else:
            trigger = (
                f"Inspect 2-3 implementation-relevant repositories to determine "
                f"whether {concept} patterns fit project evaluation needs. "
                f"Focus on repositories that demonstrate {concept} in practice."
            )

    elif level == "observe":
        trigger = (
            f"Continue monitoring {concept} trend for stronger gap alignment "
            f"signals. Review new entities and repositories quarterly."
        )

    elif level == "prototype":
        trigger = (
            f"Build a bounded prototype integrating {concept} patterns. "
            f"Define success criteria and evaluation metrics before implementation."
        )

    elif level == "adopt_candidate":
        trigger = (
            f"Prepare adoption plan for {concept}. Define integration points, "
            f"migration path, and rollback strategy."
        )

    else:
        trigger = f"Continue evaluation of {concept} with standard monitoring."

    return trigger


def _identify_blockers(
    level: str,
    entity_tiers: Optional[B2EntityTiers],
    concept: str,
    evidence_layers: Optional[B4EvidenceLayers] = None,
) -> List[str]:
    """Identify blockers for advancing to the next recommendation level."""
    blockers = []

    # Check evidence quality
    weak_evidence = False
    if evidence_layers and evidence_layers.tagged_entities:
        total = len(evidence_layers.tagged_entities)
        if total > 0:
            weak_count = sum(
                1 for tag in evidence_layers.tagged_entities
                if tag.evidence_layer in ("media_context", "community_discourse")
            )
            if weak_count / total > 0.5:
                weak_evidence = True

    if level == "observe":
        blockers.append("No clear mainline gap alignment identified")
        blockers.append("Limited evidence of practical implementation")
        if weak_evidence:
            blockers.append("Evidence quality is predominantly media/context or community discourse")

    elif level == "study":
        blockers.append("No direct repository content validation yet")
        blockers.append("Evidence remains indirect (trend-level only)")
        blockers.append("Requires hands-on evaluation to advance to prototype")
        if weak_evidence:
            blockers.append("Stronger authoritative or implementation evidence needed")

    elif level == "prototype":
        blockers.append("Requires successful prototype demonstration")
        blockers.append("Needs defined success criteria and metrics")
        blockers.append("Requires team capacity for bounded prototype")

    elif level == "adopt_candidate":
        blockers.append("Requires adoption plan approval")
        blockers.append("Needs integration roadmap and timeline")

    return blockers
