"""
IKE v0 Decision Mapper

Maps research tasks and experiments to explicit v0 Decision objects.

This is a pure adapter layer - no DB writes, no runtime changes.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ike_v0.types.ids import generate_ike_id, IKEKind
from ike_v0.schemas.decision import Decision


def create_experiment_evaluation_decision(
    task_ref: str,
    experiment_refs: List[str],
    decision_outcome: str,
    rationale: str,
    review_required: bool = False,
    evidence_refs: Optional[List[str]] = None,
) -> Decision:
    """
    Create an experiment_evaluation decision record.

    This is a bounded helper for creating the first decision type.
    It remains additive and does not require runtime integration.

    Args:
        task_ref: Reference to the parent ResearchTask
        experiment_refs: List of experiment references that informed this decision
        decision_outcome: The outcome per IKE v0 spec (adopt, reject, defer, escalate)
        rationale: Explanation of why this decision was made
        review_required: Whether human review is needed (default False)
        evidence_refs: Optional additional evidence references

    Returns:
        Decision object with v0 contract fields populated
    """
    now = datetime.now(timezone.utc)

    # Generate decision ID
    dec_id = generate_ike_id(IKEKind.DECISION)

    # Build provenance
    provenance: Dict[str, Any] = {
        "mapper": "create_experiment_evaluation_decision",
        "decision_type": "experiment_evaluation",
        "experiment_count": len(experiment_refs),
    }

    # Build references list - include task_ref and experiment_refs
    references: List[str] = [task_ref] + experiment_refs

    # Add evidence refs if provided
    if evidence_refs is None:
        evidence_refs = []

    return Decision(
        id=dec_id,
        kind="decision",
        version="v0.1.0",
        status="pending_review" if review_required else "draft",
        created_at=now,
        updated_at=now,
        provenance=provenance,
        confidence=0.5,
        references=references,
        task_ref=task_ref,
        experiment_refs=experiment_refs,
        decision_type="experiment_evaluation",
        decision_outcome=decision_outcome,
        rationale=rationale,
        evidence_refs=evidence_refs,
        review_required=review_required,
        review_status="pending" if review_required else None,
    )
