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
    plan_a_ref: str,
    plan_b_ref: str,
    hypothesis: str,
    title: Optional[str] = None,
    method_ref: Optional[str] = None,
    source_domain: Optional[str] = None,
    plan_versions: Optional[Dict[str, str]] = None,
) -> Experiment:
    """
    Create a source_plan_comparison experiment for runtime-backed source intelligence.

    This helper is adapted for real source-plan or source-plan-version references
    in the source-intelligence loop. It accepts explicit plan references rather
    than generic input_ref_a/input_ref_b.

    Args:
        task_ref: Reference to the parent ResearchTask
        plan_a_ref: Reference to source plan A (e.g., source_plan:uuid or source_plan_version:uuid)
        plan_b_ref: Reference to source plan B (e.g., source_plan:uuid or source_plan_version:uuid)
        hypothesis: The hypothesis being tested (e.g., "Plan A has better coverage than Plan B")
        title: Optional experiment title (auto-generated if not provided)
        method_ref: Optional method/protocol reference (defaults to "source_plan_comparison:v0.1")
        source_domain: Optional source domain for additional provenance (e.g., "github.com", "huggingface.co")
        plan_versions: Optional dict mapping plan refs to version identifiers for traceability

    Returns:
        Experiment object with v0 contract fields populated

    Runtime wiring notes:
        - plan_a_ref and plan_b_ref should reference actual source-plan or source-plan-version objects
        - source_domain helps trace back to the source intelligence substrate
        - plan_versions provides explicit version traceability when comparing plan versions
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

    # Build input refs list
    input_refs: List[str] = [plan_a_ref, plan_b_ref]

    # Build provenance with enhanced traceability for compared inputs
    provenance: Dict[str, Any] = {
        "mapper": "create_source_plan_comparison_experiment",
        "experiment_type": "source_plan_comparison",
        "input_count": 2,
        "plan_a_ref": plan_a_ref,
        "plan_b_ref": plan_b_ref,
    }

    # Add source domain to provenance if provided
    if source_domain:
        provenance["source_domain"] = source_domain

    # Add plan versions to provenance if provided
    if plan_versions:
        provenance["plan_versions"] = plan_versions

    # Build references list - includes task_ref and input refs
    references: List[str] = [task_ref, plan_a_ref, plan_b_ref]

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
        input_refs=input_refs,
        evidence_refs=[],
        result_summary=None,
    )


def create_claim_validation_experiment(
    task_ref: str,
    claim_ref: str,
    hypothesis: str,
    title: Optional[str] = None,
    evidence_refs: Optional[List[str]] = None,
    method_ref: Optional[str] = None,
) -> Experiment:
    """
    Create a claim_validation experiment for validating derived claims.

    This is a bounded helper for creating experiments that validate claims
    derived from observations via entity/claim extraction. It is additive
    to the existing source_plan_comparison helper and addresses the semantic
    mismatch of using source-plan comparison for claim-derived tasks.

    Args:
        task_ref: Reference to the parent ResearchTask
        claim_ref: Reference to the Claim being validated
        hypothesis: The hypothesis being tested (e.g., "The claim is valid")
        title: Optional experiment title (auto-generated if not provided)
        evidence_refs: Optional list of supporting evidence references
        method_ref: Optional method/protocol reference (defaults to "claim_validation:v0.1")

    Returns:
        Experiment object with v0 contract fields populated

    Usage notes:
        - This helper is for claim-derived ResearchTasks from J1-B path
        - The claim_ref should reference an actual Claim object
        - evidence_refs can include observation IDs, entity IDs, or other supporting refs
    """
    now = datetime.now(timezone.utc)

    # Generate experiment ID
    exp_id = generate_ike_id(IKEKind.EXPERIMENT)

    # Default title if not provided
    if title is None:
        title = "Claim Validation"

    # Default method reference
    if method_ref is None:
        method_ref = "claim_validation:v0.1"

    # Build input refs list - claim is the primary input
    input_refs: List[str] = [claim_ref]

    # Build evidence refs
    if evidence_refs is None:
        evidence_refs = []

    # Build provenance with explicit traceability
    provenance: Dict[str, Any] = {
        "mapper": "create_claim_validation_experiment",
        "experiment_type": "claim_validation",
        "claim_ref": claim_ref,
        "evidence_count": len(evidence_refs),
    }

    # Build references list - includes task_ref, claim_ref, and evidence refs
    references: List[str] = [task_ref, claim_ref] + evidence_refs

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
        experiment_type="claim_validation",
        title=title,
        hypothesis=hypothesis,
        method_ref=method_ref,
        input_refs=input_refs,
        evidence_refs=evidence_refs,
        result_summary=None,
    )
