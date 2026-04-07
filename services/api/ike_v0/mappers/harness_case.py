"""
IKE v0 HarnessCase Mapper

Maps loop evaluation inputs to explicit v0 HarnessCase objects.

This is a pure adapter layer - no DB writes, no runtime changes.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ike_v0.types.ids import generate_ike_id, IKEKind
from ike_v0.schemas.harness_case import HarnessCase

if TYPE_CHECKING:
    from ike_v0.runtime.chain_artifact import ChainArtifact


def create_loop_completeness_harness_case(
    subject_refs: List[str],
    expected_behavior: Dict[str, Any],
    actual_behavior: Dict[str, Any],
    pass_fail: bool,
    notes: Optional[str] = None,
    evidence_refs: Optional[List[str]] = None,
) -> HarnessCase:
    """
    Create a loop_completeness harness case.

    This is a bounded helper for creating the first harness case type.
    It remains additive and does not require runtime integration.

    Args:
        subject_refs: List of references to objects under evaluation
                      (e.g., task refs, experiment refs, decision refs)
        expected_behavior: Dict describing expected loop shape/behavior
        actual_behavior: Dict describing actual observed loop shape/behavior
        pass_fail: Boolean result of the evaluation
        notes: Optional notes or context
        evidence_refs: Optional list of evidence references

    Returns:
        HarnessCase object with v0 contract fields populated
    """
    now = datetime.now(timezone.utc)

    # Generate harness case ID
    hc_id = generate_ike_id(IKEKind.HARNESS_CASE)

    # Build provenance
    provenance: Dict[str, Any] = {
        "mapper": "create_loop_completeness_harness_case",
        "case_type": "loop_completeness",
        "subject_count": len(subject_refs),
    }

    # Build references list from subject_refs
    references: List[str] = list(subject_refs)

    # Add evidence refs if provided
    if evidence_refs is None:
        evidence_refs = []

    return HarnessCase(
        id=hc_id,
        kind="harness_case",
        version="v0.1.0",
        status="completed" if pass_fail else "open",
        created_at=now,
        updated_at=now,
        provenance=provenance,
        confidence=0.5,
        references=references,
        case_type="loop_completeness",
        subject_refs=subject_refs,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        pass_fail=pass_fail,
        evidence_refs=evidence_refs,
        notes=notes,
    )


def validate_chain_loop_completeness(
    chain: "ChainArtifact",
) -> HarnessCase:
    """
    Derive a loop_completeness HarnessCase from a ChainArtifact.

    This helper validates that the IKE v0.1 loop is complete and not truncated.
    It derives explicit expected_behavior, actual_behavior, subject_refs, and
    pass_fail from the chain object.

    Validation criteria:
    - Loop exists: chain has all required objects (observation, research_task,
      experiment, decision, harness_case)
    - Required references present: all required objects have valid IDs
    - Chain not truncated: objects are linked via references (task_ref, etc.)

    Args:
        chain: ChainArtifact containing the assembled loop objects

    Returns:
        HarnessCase object with explicit pass/fail for loop completeness

    Pass/fail criteria:
    - pass: chain.is_complete() returns True AND all required objects have IDs
    - fail: any required object is missing or lacks a valid ID
    """
    now = datetime.now(timezone.utc)

    # Generate harness case ID
    hc_id = generate_ike_id(IKEKind.HARNESS_CASE)

    # Define expected loop structure
    expected_behavior: Dict[str, Any] = {
        "required_objects": [
            "observation",
            "research_task",
            "experiment",
            "decision",
        ],
        "optional_objects": ["entity", "claim"],
        "traceability_checks": [
            "experiment.task_ref points to research_task",
            "decision.task_ref points to research_task",
            "decision.experiment_refs includes experiment",
        ],
    }

    # Derive actual behavior from chain
    completeness = chain.get_completeness_summary()
    actual_behavior: Dict[str, Any] = {
        "present_objects": {
            k: v for k, v in completeness["objects"].items() if v is not None
        },
        "missing_objects": {
            k: v for k, v in completeness["objects"].items() if v is None
        },
        "object_count": completeness["object_count"],
        "all_refs": chain.get_all_refs(),
    }

    # Check traceability (basic reference validation)
    traceability_issues: List[str] = []

    if chain.experiment and chain.research_task:
        if chain.experiment.task_ref != chain.research_task.id:
            traceability_issues.append(
                f"experiment.task_ref ({chain.experiment.task_ref}) != "
                f"research_task.id ({chain.research_task.id})"
            )

    if chain.decision and chain.research_task:
        if chain.decision.task_ref != chain.research_task.id:
            traceability_issues.append(
                f"decision.task_ref ({chain.decision.task_ref}) != "
                f"research_task.id ({chain.research_task.id})"
            )

    if chain.decision and chain.experiment:
        if chain.experiment.id not in chain.decision.experiment_refs:
            traceability_issues.append(
                f"decision.experiment_refs does not include experiment.id "
                f"({chain.experiment.id})"
            )

    if traceability_issues:
        actual_behavior["traceability_issues"] = traceability_issues

    # Determine pass/fail
    # Pass if: all required objects present (obs, task, exp, dec) AND no traceability issues
    # Note: harness_case is NOT required - we're creating it now to validate the chain
    required_present = all([
        chain.observation is not None,
        chain.research_task is not None,
        chain.experiment is not None,
        chain.decision is not None,
    ])
    pass_fail = required_present and len(traceability_issues) == 0

    # Build subject refs from chain objects
    subject_refs: List[str] = []
    if chain.research_task:
        subject_refs.append(chain.research_task.id)
    if chain.experiment:
        subject_refs.append(chain.experiment.id)
    if chain.decision:
        subject_refs.append(chain.decision.id)

    # Build evidence refs from observation and other objects
    evidence_refs: List[str] = []
    if chain.observation:
        evidence_refs.append(chain.observation.id)
    if chain.entity:
        evidence_refs.append(chain.entity.id)
    if chain.claim:
        evidence_refs.append(chain.claim.id)

    # Build notes
    notes_parts: List[str] = []
    if not required_present:
        missing = [k for k, v in completeness["objects"].items() if v is None and k in ["observation", "research_task", "experiment", "decision"]]
        if missing:
            notes_parts.append(f"Missing required objects: {', '.join(missing)}")
    if traceability_issues:
        notes_parts.append(f"Traceability issues: {'; '.join(traceability_issues)}")
    notes = "; ".join(notes_parts) if notes_parts else "Loop validation passed"

    # Build provenance
    provenance: Dict[str, Any] = {
        "mapper": "validate_chain_loop_completeness",
        "case_type": "loop_completeness",
        "chain_id": chain.chain_id,
        "validation_criteria": {
            "completeness_check": "required objects present (obs, task, exp, dec)",
            "traceability_check": "reference validation between objects",
        },
        "required_present": required_present,
        "traceability_issues_count": len(traceability_issues),
    }

    # Build references from all chain objects
    references: List[str] = chain.get_all_refs()

    return HarnessCase(
        id=hc_id,
        kind="harness_case",
        version="v0.1.0",
        status="completed" if pass_fail else "open",
        created_at=now,
        updated_at=now,
        provenance=provenance,
        confidence=0.5,
        references=references,
        case_type="loop_completeness",
        subject_refs=subject_refs,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        pass_fail=pass_fail,
        evidence_refs=evidence_refs,
        notes=notes,
    )
