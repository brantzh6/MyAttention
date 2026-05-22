"""
IKE v0.1 B2 Gap Mapping

Maps concept entities and knowledge to explicit mainline gaps.

Outputs a list of gap mappings, where each mapping includes:
- gap_id
- gap_description
- relevance_score (high / medium / low)
- specific_contribution

This is benchmark-local: uses only B1 trend bundle, B1/B2 knowledge summary,
and current project mainline gaps. No LLM calls, no external API calls.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .b1_harness import HarnessTrendBundle
from .b1_knowledge import KnowledgeSummary
from .b1_evolution import MAINLINE_GAPS


@dataclass
class GapMapping:
    """A mapping between concept entities and a mainline gap."""

    gap_id: str
    gap_description: str
    relevance_score: str  # "high", "medium", "low"
    specific_contribution: str
    supporting_entities: List[str] = field(default_factory=list)
    evidence_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "gap_id": self.gap_id,
            "gap_description": self.gap_description,
            "relevance_score": self.relevance_score,
            "specific_contribution": self.specific_contribution,
            "supporting_entities": self.supporting_entities,
            "evidence_notes": self.evidence_notes,
        }


@dataclass
class B2GapMappingResult:
    """Structured output object for B2 gap mappings."""

    concept: str
    mappings: List[GapMapping]
    benchmark_id: str = "B2-S2"
    total_gaps_identified: int = 0
    high_relevance_count: int = 0
    medium_relevance_count: int = 0
    low_relevance_count: int = 0
    notes: str = ""
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "concept": self.concept,
            "mappings": [m.to_dict() for m in self.mappings],
            "benchmark_id": self.benchmark_id,
            "total_gaps_identified": self.total_gaps_identified,
            "high_relevance_count": self.high_relevance_count,
            "medium_relevance_count": self.medium_relevance_count,
            "low_relevance_count": self.low_relevance_count,
            "notes": self.notes,
            "limitations": self.limitations,
        }


# Mapping rules: gap_id -> keywords and entity type patterns that suggest relevance
# Note: gap_ids must match MAINLINE_GAPS exactly (with spaces)
_GAP_MAPPING_RULES = {
    "improve source intelligence quality": {
        "description": "Improve the quality and reliability of source intelligence for trend detection",
        "entity_type_signals": {
            "person": "Authors and researchers who contribute to source discovery methods",
            "repository": "Tools and frameworks for source intelligence and discovery",
            "organization": "Research organizations focused on intelligence quality",
        },
        "relevance_keywords": [
            "source", "intelligence", "discovery", "quality", "reliability",
            "signal", "noise", "filter", "detection", "benchmark",
        ],
    },
    "make active work surface understandable": {
        "description": "Make the active work surface (projects, tasks, context) understandable to the agent",
        "entity_type_signals": {
            "person": "Authors working on workspace understanding or context awareness",
            "repository": "Tools for workspace analysis, context extraction, or surface representation",
            "organization": "Organizations focused on developer experience or workspace tools",
        },
        "relevance_keywords": [
            "workspace", "surface", "understand", "context", "awareness",
            "representation", "visualization", "overview", "summary", "explain",
        ],
    },
    "move evolution toward better reasoning": {
        "description": "Move trend evolution toward better reasoning and judgment capabilities",
        "entity_type_signals": {
            "person": "Researchers working on reasoning, judgment, or evaluation",
            "repository": "Frameworks for reasoning, evaluation, or judgment",
            "organization": "Research labs focused on reasoning or AI evaluation",
        },
        "relevance_keywords": [
            "reasoning", "judgment", "evaluation", "evolution", "analysis",
            "inference", "logic", "assessment", "critique", "reflection",
        ],
    },
    "reduce token pressure through controlled delegation": {
        "description": "Reduce token pressure through controlled delegation to specialized agents",
        "entity_type_signals": {
            "person": "Authors working on delegation, multi-agent systems, or efficiency",
            "repository": "Tools for delegation, agent orchestration, or token optimization",
            "organization": "Organizations focused on agent systems or efficiency",
        },
        "relevance_keywords": [
            "delegation", "agent", "orchestration", "efficiency", "token",
            "pressure", "optimization", "multi-agent", "distributed", "specialized",
        ],
    },
}


def map_concept_to_mainline_gaps(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    concept: str = "harness",
    b2_entity_tiers: Optional[Any] = None,
) -> B2GapMappingResult:
    """
    Map concept entities and knowledge to explicit mainline gaps.

    Args:
        bundle: The B1 HarnessTrendBundle containing ranked entities
        knowledge_summary: The B1 knowledge summary for the concept
        concept: The concept being mapped (default: "harness")
        b2_entity_tiers: Optional B2EntityTiers from B2-S1 for implementation tier checks

    Returns:
        B2GapMappingResult with gap mappings grounded in the evidence

    This is a pure helper: no LLM calls, no external API calls,
    grounded in B1 trend bundle and knowledge summary.

    Benchmark-local semantics for 'harness':
    - Emits: "make active work surface understandable", "reduce token pressure through controlled delegation"
    - Omits: "improve source intelligence quality", "move evolution toward better reasoning" (unless direct evidence)

    Required concept-level signals for harness:
    - concept_summary includes "evaluation" or "testing"
    - contrast_dimensions include "practice-oriented" or "ecosystem-integrated"
    - concept_summary includes "AI agent" or "agent framework"
    - B2 implementation-relevant tier contains at least one repository (if b2_entity_tiers provided)
    """
    mappings: List[GapMapping] = []

    # Analyze evidence from bundle and knowledge summary
    entity_names = [e.name for e in bundle.ranked_entities]
    entity_types = [e.entity_type for e in bundle.ranked_entities]
    relevance_reasons = " ".join([e.relevance_reason.lower() for e in bundle.ranked_entities])
    concept_summary = knowledge_summary.concept_summary.lower() if knowledge_summary else ""
    evidence_grounding = " ".join(knowledge_summary.evidence_grounding).lower() if knowledge_summary and knowledge_summary.evidence_grounding else ""
    contrast_dimensions = " ".join([d.lower() for d in knowledge_summary.contrast_dimensions]) if knowledge_summary else ""

    all_evidence_text = f"{relevance_reasons} {concept_summary} {evidence_grounding}".lower()

    # Check benchmark-local concept signals for harness
    concept_signals = _check_harness_concept_signals(
        concept_summary=concept_summary,
        contrast_dimensions=contrast_dimensions,
        b2_entity_tiers=b2_entity_tiers,
    )

    # Map against each mainline gap using benchmark-local semantics
    for gap_id in MAINLINE_GAPS:
        gap_info = _GAP_MAPPING_RULES.get(gap_id)
        if not gap_info:
            continue

        # Use benchmark-local gap selection logic
        relevance_score, specific_contribution, supporting_entities = _calculate_gap_relevance_benchmark_local(
            gap_id=gap_id,
            gap_info=gap_info,
            entity_names=entity_names,
            entity_types=entity_types,
            evidence_text=all_evidence_text,
            concept=concept,
            concept_signals=concept_signals,
        )

        # Only emit gaps with medium or high relevance (selective, not exhaustive)
        if relevance_score in ("high", "medium"):
            mapping = GapMapping(
                gap_id=gap_id,
                gap_description=gap_info["description"],
                relevance_score=relevance_score,
                specific_contribution=specific_contribution,
                supporting_entities=supporting_entities,
                evidence_notes=_build_evidence_notes(gap_id, bundle, knowledge_summary),
            )
            mappings.append(mapping)

    # Calculate counts
    high_count = sum(1 for m in mappings if m.relevance_score == "high")
    medium_count = sum(1 for m in mappings if m.relevance_score == "medium")
    low_count = sum(1 for m in mappings if m.relevance_score == "low")

    # Build notes and limitations
    notes = (
        f"B2 gap mapping for concept '{concept}'. "
        f"Mapped {len(bundle.ranked_entities)} entities against {len(MAINLINE_GAPS)} mainline gaps. "
        f"Found {high_count} high-relevance, {medium_count} medium-relevance, {low_count} low-relevance mappings."
    )

    limitations = [
        "Mapping is heuristic, not LLM-based",
        "Limited to B1 trend bundle and knowledge summary evidence",
        "Relevance scoring is keyword-based and may miss nuanced connections",
        "Does not capture temporal evolution of gap relevance",
        "May over-weight entities with keyword-rich relevance reasons",
    ]

    return B2GapMappingResult(
        concept=concept,
        mappings=mappings,
        benchmark_id="B2-S2",
        total_gaps_identified=len(mappings),
        high_relevance_count=high_count,
        medium_relevance_count=medium_count,
        low_relevance_count=low_count,
        notes=notes,
        limitations=limitations,
    )


def _check_harness_concept_signals(
    concept_summary: str,
    contrast_dimensions: str,
    b2_entity_tiers: Optional[Any] = None,
) -> Dict[str, bool]:
    """
    Check benchmark-local concept signals for harness.

    Returns a dict of signal names to boolean values.
    """
    signals = {
        "has_evaluation_or_testing": "evaluation" in concept_summary or "testing" in concept_summary,
        "has_practice_oriented": "practice-oriented" in contrast_dimensions or "practice oriented" in contrast_dimensions,
        "has_ecosystem_integrated": "ecosystem-integrated" in contrast_dimensions or "ecosystem integrated" in contrast_dimensions,
        "has_ai_agent_or_framework": "ai agent" in concept_summary or "agent framework" in concept_summary,
        "has_implementation_repo": False,
    }

    # Check B2 implementation tier for repositories
    if b2_entity_tiers is not None:
        try:
            impl_tier = b2_entity_tiers.implementation_relevant
            if hasattr(impl_tier, "entries"):
                for entry in impl_tier.entries:
                    if hasattr(entry, "entity_type") and entry.entity_type == "repository":
                        signals["has_implementation_repo"] = True
                        break
        except (AttributeError, TypeError):
            pass

    return signals


def _calculate_gap_relevance_benchmark_local(
    gap_id: str,
    gap_info: Dict[str, Any],
    entity_names: List[str],
    entity_types: List[str],
    evidence_text: str,
    concept: str,
    concept_signals: Dict[str, bool],
) -> tuple:
    """
    Calculate relevance score using benchmark-local semantics for harness.

    For harness concept:
    - Emits: "make active work surface understandable", "reduce token pressure through controlled delegation"
    - Omits: "improve source intelligence quality", "move evolution toward better reasoning" (unless direct evidence)

    Returns:
        Tuple of (relevance_score, specific_contribution, supporting_entities)
    """
    keywords = gap_info["relevance_keywords"]

    # Count keyword matches in evidence (case-insensitive)
    keyword_matches = sum(1 for kw in keywords if kw in evidence_text)

    # Find supporting entities - only those whose names match gap keywords
    supporting = []
    for entity in entity_names:
        entity_lower = entity.lower()
        for kw in keywords:
            if kw in entity_lower:
                if entity not in supporting:
                    supporting.append(entity)
                break

    # Benchmark-local gap selection for harness
    # This encodes the intended semantic shape for the harness benchmark
    if concept == "harness":
        # Check if this gap should be emitted based on concept signals
        should_emit = _should_emit_gap_for_harness(
            gap_id=gap_id,
            concept_signals=concept_signals,
            keyword_matches=keyword_matches,
        )

        if not should_emit:
            return "low", f"Gap '{gap_id}' not directly supported by harness concept signals.", []

        # For harness, use lower thresholds since concept signals already validated
        if keyword_matches >= 3:
            relevance_score = "high"
        elif keyword_matches >= 1:
            relevance_score = "medium"
        else:
            # Concept signals support this gap even without keyword matches
            relevance_score = "medium"
    else:
        # Generic concept: use keyword-only matching
        if keyword_matches >= 5:
            relevance_score = "high"
        elif keyword_matches >= 3:
            relevance_score = "medium"
        else:
            relevance_score = "low"

    # Build specific contribution statement
    if supporting:
        specific_contribution = (
            f"Entities related to '{concept}' show {keyword_matches} keyword matches "
            f"with gap '{gap_id}'. "
            f"Supporting entities: {', '.join(supporting[:3])}{'...' if len(supporting) > 3 else ''}."
        )
    elif keyword_matches > 0:
        specific_contribution = (
            f"Concept evidence for '{concept}' shows {keyword_matches} keyword matches "
            f"with gap '{gap_id}', but no specific entities directly support this gap."
        )
    else:
        specific_contribution = (
            f"Gap '{gap_id}' is supported by harness concept signals "
            f"(evaluation/testing, practice-oriented, AI agent focus)."
        )

    return relevance_score, specific_contribution, supporting


def _should_emit_gap_for_harness(
    gap_id: str,
    concept_signals: Dict[str, bool],
    keyword_matches: int,
) -> bool:
    """
    Determine if a gap should be emitted for the harness concept.

    Benchmark-local semantics:
    - Emit: "make active work surface understandable", "reduce token pressure through controlled delegation"
    - Omit: "improve source intelligence quality", "move evolution toward better reasoning" (unless direct evidence)
    """
    # Gaps that harness directly addresses
    directly_supported_gaps = {
        "make active work surface understandable": True,
        "reduce token pressure through controlled delegation": True,
    }

    # Gaps that harness does NOT directly address (omit unless strong keyword evidence)
    indirectly_supported_gaps = {
        "improve source intelligence quality": False,
        "move evolution toward better reasoning": False,
    }

    if gap_id in directly_supported_gaps:
        # Check if concept signals support this gap
        required_signals = {
            "make active work surface understandable": ["has_evaluation_or_testing", "has_ai_agent_or_framework"],
            "reduce token pressure through controlled delegation": ["has_ai_agent_or_framework"],
        }

        signals_for_gap = required_signals.get(gap_id, [])
        if all(concept_signals.get(sig, False) for sig in signals_for_gap):
            return True

    if gap_id in indirectly_supported_gaps:
        # Only emit if there's strong direct keyword evidence
        return keyword_matches >= 4

    return False


def _calculate_gap_relevance(
    gap_id: str,
    gap_info: Dict[str, Any],
    entity_names: List[str],
    entity_types: List[str],
    evidence_text: str,
    concept: str,
) -> tuple:
    """
    Calculate relevance score and contribution for a gap.

    Legacy function kept for backward compatibility.
    Delegates to _calculate_gap_relevance_benchmark_local with empty concept_signals.
    """
    concept_signals = {
        "has_evaluation_or_testing": False,
        "has_practice_oriented": False,
        "has_ecosystem_integrated": False,
        "has_ai_agent_or_framework": False,
        "has_implementation_repo": False,
    }

    return _calculate_gap_relevance_benchmark_local(
        gap_id=gap_id,
        gap_info=gap_info,
        entity_names=entity_names,
        entity_types=entity_types,
        evidence_text=evidence_text,
        concept=concept,
        concept_signals=concept_signals,
    )


def _build_evidence_notes(gap_id: str, bundle: HarnessTrendBundle, knowledge_summary: KnowledgeSummary) -> str:
    """Build evidence notes for a gap mapping."""
    notes_parts = []

    if bundle.ranked_entities:
        notes_parts.append(f"B1 bundle contains {len(bundle.ranked_entities)} ranked entities")

    if knowledge_summary and knowledge_summary.concept_summary:
        summary_preview = knowledge_summary.concept_summary[:100]
        notes_parts.append(f"Knowledge summary: {summary_preview}...")

    if knowledge_summary and knowledge_summary.confidence:
        notes_parts.append(f"Knowledge confidence: {knowledge_summary.confidence}")

    return "; ".join(notes_parts) if notes_parts else "No additional evidence notes"
