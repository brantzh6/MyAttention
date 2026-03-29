"""
IKE v0 HarnessCase Mapper

Maps loop evaluation inputs to explicit v0 HarnessCase objects.

This is a pure adapter layer - no DB writes, no runtime changes.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ike_v0.types.ids import generate_ike_id, IKEKind
from ike_v0.schemas.harness_case import HarnessCase


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
