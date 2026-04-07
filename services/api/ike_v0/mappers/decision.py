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


def derive_decision_from_experiment(
    task: Any,
    experiment: Any,
    decision_outcome: str,
    rationale: Optional[str] = None,
    review_required: bool = False,
) -> Decision:
    """
    Derive a provisional Decision from loop ResearchTask and Experiment objects.

    This is a bounded glue helper for the v0.1 real loop. It creates a Decision
    from already-created loop objects (ResearchTask, Experiment), preserving
    explicit traceability through experiment_refs, references, and provenance.

    This helper is additive and does not replace create_experiment_evaluation_decision.
    It is for deriving decisions from the IKE loop itself, not from raw refs.

    Args:
        task: ResearchTask object (or dict-like) - the parent task
        experiment: Experiment object (or dict-like) - the experiment to evaluate
        decision_outcome: The outcome per IKE v0 spec (adopt, reject, defer, escalate)
        rationale: Optional explanation. If not provided, derived from experiment hypothesis
        review_required: Whether human review is needed (default False)

    Returns:
        Decision object with v0 contract fields populated

    Traceability:
        - task_ref: extracted from task.id
        - experiment_refs: [experiment.id]
        - references: includes task.id and experiment.id
        - provenance: includes mapper name, source object IDs, derivation info

    Usage notes:
        - This is for loop-derived decisions, not substrate-mapped decisions
        - The resulting decision is provisional (draft or pending_review status)
        - Use in conjunction with derive_research_task_from_entity_claim() and
          create_claim_validation_experiment()
    """
    now = datetime.now(timezone.utc)

    # Extract IDs from objects (handle both objects and dicts)
    def get_id(obj: Any) -> str:
        if hasattr(obj, "id"):
            return obj.id
        if isinstance(obj, dict) and "id" in obj:
            return obj["id"]
        raise ValueError("Object must have an 'id' attribute or key")

    def get_kind(obj: Any) -> str:
        if hasattr(obj, "kind"):
            return obj.kind
        if isinstance(obj, dict) and "kind" in obj:
            return obj["kind"]
        return "unknown"

    def get_field(obj: Any, field: str, default=None):
        if hasattr(obj, field):
            return getattr(obj, field)
        if isinstance(obj, dict) and field in obj:
            return obj.get(field)
        return default

    task_id = get_id(task)
    experiment_id = get_id(experiment)

    # Generate decision ID
    dec_id = generate_ike_id(IKEKind.DECISION)

    # Build experiment refs list
    experiment_refs: List[str] = [experiment_id]

    # Derive rationale from experiment if not provided
    if rationale is None:
        hypothesis = get_field(experiment, "hypothesis", "experiment hypothesis")
        rationale = f"Based on experiment results: {hypothesis}"

    # Build provenance with explicit traceability
    provenance: Dict[str, Any] = {
        "mapper": "derive_decision_from_experiment",
        "derivation_path": "research_task -> experiment -> decision",
        "source_task_id": task_id,
        "source_experiment_id": experiment_id,
        "source_task_kind": get_kind(task),
        "source_experiment_kind": get_kind(experiment),
        "decision_type": "experiment_evaluation",
        "experiment_count": 1,
    }

    # Build references list - includes task_ref and experiment_refs
    references: List[str] = [task_id, experiment_id]

    # Add evidence refs if experiment has them
    evidence_refs: List[str] = []
    exp_evidence = get_field(experiment, "evidence_refs", [])
    if exp_evidence:
        evidence_refs = list(exp_evidence)

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
        task_ref=task_id,
        experiment_refs=experiment_refs,
        decision_type="experiment_evaluation",
        decision_outcome=decision_outcome,
        rationale=rationale,
        evidence_refs=evidence_refs,
        review_required=review_required,
        review_status="pending" if review_required else None,
    )
