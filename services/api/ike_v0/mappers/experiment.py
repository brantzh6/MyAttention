"""
IKE v0 Experiment Mapper

Maps research tasks and inputs to explicit v0 Experiment objects.

This is a pure adapter layer - no DB writes, no runtime changes.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ike_v0.types.ids import generate_ike_id, IKEKind
from ike_v0.schemas.experiment import Experiment


def create_source_plan_comparison_experiment(
    task_ref: str,
    input_ref_a: str,
    input_ref_b: str,
    hypothesis: str,
    title: Optional[str] = None,
    method_ref: Optional[str] = None,
) -> Experiment:
    """
    Create a source_plan_comparison experiment stub.

    This is a bounded helper for creating the first experiment type.
    It remains additive and does not require runtime integration.

    Args:
        task_ref: Reference to the parent ResearchTask
        input_ref_a: First input reference (e.g., source plan A)
        input_ref_b: Second input reference (e.g., source plan B)
        hypothesis: The hypothesis being tested
        title: Optional experiment title (auto-generated if not provided)
        method_ref: Optional method/protocol reference (defaults to "source_plan_comparison:v0.1")

    Returns:
        Experiment object with v0 contract fields populated
    """
    now = datetime.now(timezone.utc)

    # Generate experiment ID
    exp_id = generate_ike_id(IKEKind.EXPERIMENT)

    # Default title if not provided
    if title is None:
        title = "Source Plan Comparison"

    # Default method reference
    if method_ref is None:
        method_ref = "source_plan_comparison:v0.1"

    # Build provenance
    provenance: Dict[str, Any] = {
        "mapper": "create_source_plan_comparison_experiment",
        "experiment_type": "source_plan_comparison",
        "input_count": 2,
    }

    # Build references list
    references: List[str] = [task_ref]

    return Experiment(
        id=exp_id,
        kind="experiment",
        version="v0.1.0",
        status="draft",
        created_at=now,
        updated_at=now,
        provenance=provenance,
        confidence=0.5,
        references=references,
        task_ref=task_ref,
        experiment_type="source_plan_comparison",
        title=title,
        hypothesis=hypothesis,
        method_ref=method_ref,
        input_refs=[input_ref_a, input_ref_b],
        evidence_refs=[],
        result_summary=None,
    )
