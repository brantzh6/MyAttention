"""
IKE v0.1 B2-S4 Research Trigger Packet Helper

Produces a deterministic research trigger packet from B1/B2 benchmark evidence.

Output shape:
- packet_id
- concept
- derived_from
- task_type
- bounded_task
- inputs
- success_criteria
- no_go_conditions
- timebox
- output_artifact
- fallback_action

Current benchmark expectation for harness:
- task_type = study
- bounded_task: inspect up to 3 implementation-relevant repositories
- Focus: documentation/pattern inspection only (no implementation, no forking, no code audit)

This is a pure, benchmark-local helper: no LLM calls, no external API calls.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime, timezone

from .b1_harness import HarnessTrendBundle
from .b1_knowledge import KnowledgeSummary
from .b2_entity_tiers import B2EntityTiers
from .b2_gap_mapping import B2GapMappingResult
from .b2_recommendation import B2Recommendation


@dataclass
class B2TriggerPacket:
    """
    Structured research trigger packet for B2-S4 benchmark.

    Fields:
    - packet_id: Unique identifier for the packet
    - concept: The concept this packet addresses
    - derived_from: List of benchmark IDs this packet derives from
    - task_type: One of observe|study|prototype|adopt
    - bounded_task: Specific, bounded task description
    - inputs: List of required inputs for the task
    - success_criteria: List of criteria for task success
    - no_go_conditions: Conditions that would abort the task
    - timebox: Time allocation for the task
    - output_artifact: Expected output artifact
    - fallback_action: Alternative action if primary task cannot proceed
    """
    packet_id: str
    concept: str
    derived_from: List[str]
    task_type: str  # observe|study|prototype|adopt
    bounded_task: str
    inputs: List[str]
    success_criteria: List[str]
    no_go_conditions: List[str]
    timebox: str
    output_artifact: str
    fallback_action: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "packet_id": self.packet_id,
            "concept": self.concept,
            "derived_from": self.derived_from,
            "task_type": self.task_type,
            "bounded_task": self.bounded_task,
            "inputs": self.inputs,
            "success_criteria": self.success_criteria,
            "no_go_conditions": self.no_go_conditions,
            "timebox": self.timebox,
            "output_artifact": self.output_artifact,
            "fallback_action": self.fallback_action,
            "created_at": self.created_at,
        }


def generate_trigger_packet(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    gap_mapping: B2GapMappingResult,
    recommendation: B2Recommendation,
    entity_tiers: Optional[B2EntityTiers] = None,
    concept: str = "harness",
) -> B2TriggerPacket:
    """
    Generate a research trigger packet from B1/B2 benchmark evidence.

    Args:
        bundle: B1 trend bundle with ranked entities
        knowledge_summary: B1 knowledge summary
        gap_mapping: B2-S2 gap mapping result
        recommendation: B2-S3 recommendation
        entity_tiers: Optional B2-S1 entity tiers
        concept: The concept being evaluated (default: "harness")

    Returns:
        B2TriggerPacket with bounded task, inputs, success criteria, etc.

    This is a pure helper: no LLM calls, no external API calls.
    """
    # Generate packet ID from concept and timestamp
    packet_id = _generate_packet_id(concept, recommendation.level)

    # Determine derived_from based on available benchmark outputs
    derived_from = _build_derived_from(gap_mapping, recommendation)

    # Determine task type from recommendation level
    task_type = _map_level_to_task_type(recommendation.level)

    # Build bounded task based on recommendation and entity tiers
    bounded_task = _build_bounded_task(recommendation, entity_tiers, concept)

    # Define inputs required for the task
    inputs = _build_inputs(bundle, knowledge_summary, gap_mapping, recommendation, entity_tiers, concept)

    # Define success criteria for the task
    success_criteria = _build_success_criteria(recommendation, entity_tiers, concept)

    # Define no-go conditions
    no_go_conditions = _build_no_go_conditions(recommendation, concept)

    # Define timebox based on task type
    timebox = _build_timebox(task_type)

    # Define output artifact
    output_artifact = _build_output_artifact(task_type, concept)

    # Define fallback action
    fallback_action = _build_fallback_action(recommendation, concept)

    return B2TriggerPacket(
        packet_id=packet_id,
        concept=concept,
        derived_from=derived_from,
        task_type=task_type,
        bounded_task=bounded_task,
        inputs=inputs,
        success_criteria=success_criteria,
        no_go_conditions=no_go_conditions,
        timebox=timebox,
        output_artifact=output_artifact,
        fallback_action=fallback_action,
    )


def _generate_packet_id(concept: str, level: str) -> str:
    """Generate a unique packet ID from concept and level."""
    # Create a deterministic ID based on concept and level
    content = f"{concept}-{level}-B2-S4"
    hash_suffix = hashlib.sha256(content.encode()).hexdigest()[:8]
    return f"B2-S4-{concept.upper()[:8]}-{level.upper()}-{hash_suffix}"


def _build_derived_from(gap_mapping: B2GapMappingResult, recommendation: B2Recommendation) -> List[str]:
    """Build list of benchmark IDs this packet derives from."""
    derived = ["B1-S1", "B1-S2"]  # Always derived from B1 signal and knowledge

    # Add B2-S1 if entity tiers were used
    # Add B2-S2 if gap mapping has results
    if gap_mapping and gap_mapping.mappings:
        derived.append("B2-S2")

    # Add B2-S3 if recommendation exists
    if recommendation and recommendation.level:
        derived.append("B2-S3")

    return derived


def _map_level_to_task_type(level: str) -> str:
    """Map recommendation level to task type."""
    level_to_task = {
        "observe": "observe",
        "study": "study",
        "prototype": "prototype",
        "adopt_candidate": "adopt",
    }
    return level_to_task.get(level, "study")


def _build_bounded_task(
    recommendation: B2Recommendation,
    entity_tiers: Optional[B2EntityTiers],
    concept: str,
) -> str:
    """Build bounded task description based on recommendation level."""
    level = recommendation.level

    if level == "study":
        # For harness: inspect up to 3 implementation-relevant repositories
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

        # Build natural wording based on repo count
        if len(impl_repos) == 1:
            repo_spec = f" the '{impl_repos[0]}' repository"
        elif len(impl_repos) >= 2:
            repo_spec = f" up to {min(len(impl_repos), 3)} implementation-relevant repositories"
        else:
            repo_spec = " 2-3 implementation-relevant repositories"

        return (
            f"Inspect{repo_spec} related to '{concept}'. "
            f"Focus on documentation and pattern inspection only. "
            f"Validate whether {concept} evaluation patterns are directly applicable to project needs. "
            f"No implementation, no forking, no code-quality audit."
        )

    elif level == "observe":
        return (
            f"Monitor '{concept}' trend signals quarterly. "
            f"Track new entities, repositories, and discourse patterns. "
            f"Document any shifts in gap alignment."
        )

    elif level == "prototype":
        return (
            f"Build a bounded prototype integrating '{concept}' patterns. "
            f"Define success criteria and evaluation metrics before implementation. "
            f"Timeboxed to 2-week sprint with clear exit criteria."
        )

    elif level == "adopt":
        return (
            f"Prepare adoption plan for '{concept}'. "
            f"Define integration points, migration path, and rollback strategy. "
            f"Include risk assessment and team readiness evaluation."
        )

    else:
        return f"Continue evaluation of '{concept}' with standard monitoring."


def _build_inputs(
    bundle: HarnessTrendBundle,
    knowledge_summary: KnowledgeSummary,
    gap_mapping: B2GapMappingResult,
    recommendation: B2Recommendation,
    entity_tiers: Optional[B2EntityTiers],
    concept: str,
) -> List[str]:
    """Build list of required inputs for the task."""
    inputs = []

    # Always include B1 outputs
    inputs.append(f"B1 trend bundle for '{concept}' ({len(bundle.ranked_entities)} entities)")
    inputs.append(f"B1 knowledge summary (confidence: {knowledge_summary.confidence if knowledge_summary else 'N/A'})")

    # Include B2-S2 gap mapping if available
    if gap_mapping and gap_mapping.mappings:
        gap_ids = [m.gap_id for m in gap_mapping.mappings]
        inputs.append(f"B2-S2 gap mapping: {', '.join(gap_ids)}")

    # Include B2-S3 recommendation
    inputs.append(f"B2-S3 recommendation level: {recommendation.level if recommendation and recommendation.level else 'N/A'}")

    # Include entity tiers if available
    if entity_tiers:
        try:
            impl_count = len(entity_tiers.implementation_relevant.entries) if entity_tiers.implementation_relevant else 0
            inputs.append(f"B2-S1 entity tiers: {impl_count} implementation-relevant entities")
        except (AttributeError, TypeError):
            pass

    return inputs


def _build_success_criteria(
    recommendation: B2Recommendation,
    entity_tiers: Optional[B2EntityTiers],
    concept: str,
) -> List[str]:
    """Build success criteria for the task."""
    level = recommendation.level

    if level == "study":
        criteria = [
            f"Documented analysis of each inspected repository's approach to {concept}",
            "Clear determination of pattern applicability to project needs",
            "Identification of at least 2-3 key insights or patterns",
            "Decision on whether to proceed to prototype or continue observing",
        ]
    elif level == "observe":
        criteria = [
            "Quarterly trend summary document",
            "Updated entity list with signal scores",
            "Assessment of any new gap alignments",
        ]
    elif level == "prototype":
        criteria = [
            f"Working prototype demonstrating {concept} integration",
            "Documented evaluation metrics and results",
            "Clear go/no-go recommendation for adoption",
        ]
    elif level == "adopt":
        criteria = [
            "Complete adoption plan with timeline",
            "Risk assessment and mitigation strategies",
            "Team readiness confirmation",
        ]
    else:
        criteria = ["Task completion documentation"]

    return criteria


def _build_no_go_conditions(recommendation: B2Recommendation, concept: str) -> List[str]:
    """Build no-go conditions that would abort the task."""
    level = recommendation.level

    if level == "study":
        return [
            f"No implementation-relevant repositories found for '{concept}'",
            "Repositories lack documentation or are inaccessible",
            "Pattern mismatch with project architecture is immediately obvious",
            "Project priorities shift away from evaluation improvements",
        ]
    elif level == "observe":
        return [
            "Trend signals disappear completely",
            "Concept becomes obsolete or superseded",
        ]
    elif level == "prototype":
        return [
            "Study phase recommends against proceeding",
            "Resource constraints prevent prototype development",
            "Technical incompatibility discovered during study",
        ]
    elif level == "adopt":
        return [
            "Prototype fails to meet success criteria",
            "Team capacity insufficient for adoption",
            "Higher-priority initiatives take precedence",
        ]
    else:
        return ["Task no longer aligned with project goals"]


def _build_timebox(task_type: str) -> str:
    """Build timebox based on task type."""
    timeboxes = {
        "observe": "Ongoing: quarterly review, 2-4 hours per quarter",
        "study": "1-2 weeks: 4-8 hours total for repository inspection and analysis",
        "prototype": "2-week sprint: dedicated development time with daily check-ins",
        "adopt": "4-6 weeks: phased rollout with milestone reviews",
    }
    return timeboxes.get(task_type, "Timebox to be determined based on task scope")


def _build_output_artifact(task_type: str, concept: str) -> str:
    """Build expected output artifact description."""
    if task_type == "study":
        return f"Study report: '{concept} Pattern Inspection Findings' with go/no-go recommendation"
    elif task_type == "observe":
        return f"Quarterly trend summary: '{concept} Monitoring Report'"
    elif task_type == "prototype":
        return f"Prototype demo + evaluation report: '{concept} Integration Prototype Results'"
    elif task_type == "adopt":
        return f"Adoption plan document: '{concept} Integration Roadmap'"
    else:
        return "Task completion report"


def _build_fallback_action(recommendation: B2Recommendation, concept: str) -> str:
    """Build fallback action if primary task cannot proceed."""
    level = recommendation.level

    if level == "study":
        return (
            f"If repository inspection cannot proceed, return to observe level. "
            f"Continue monitoring '{concept}' trend for stronger signals or more accessible implementation examples."
        )
    elif level == "observe":
        return (
            f"If trend signals weaken, archive '{concept}' monitoring and reallocate attention to higher-priority trends."
        )
    elif level == "prototype":
        return (
            f"If prototype development is blocked, extend study phase with deeper technical analysis. "
            f"Consider engaging with repository maintainers for clarification."
        )
    elif level == "adopt":
        return (
            f"If adoption is blocked, return to prototype phase for additional validation. "
            f"Reassess readiness criteria and address identified gaps."
        )
    else:
        return "Reassess recommendation level and adjust task accordingly"
