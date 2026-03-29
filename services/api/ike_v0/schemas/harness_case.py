"""
IKE v0 HarnessCase Schema

Represents one validation harness case for evaluating loop completeness
and traceability in the v0 IKE loop.

See: docs/IKE_SHARED_OBJECTS_V0.md
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal

from pydantic import BaseModel, Field


class HarnessCase(BaseModel):
    """
    IKE v0 HarnessCase object.

    Represents one validation harness case for evaluating loop completeness
    and traceability. This is the meta-evaluation layer - not execution.

    Fields follow the v0 contract from IKE_SHARED_OBJECTS_V0.md.
    """

    # Shared envelope fields (explicitly defined for clarity)
    id: str = Field(..., description="Unique identifier (IKE typed ID)")
    kind: Literal["harness_case"] = Field(default="harness_case", description="Object type discriminator")
    version: str = Field(default="v0.1.0", description="Schema version")
    status: str = Field(default="draft", description="Lifecycle status (draft, open, completed, archived)")
    created_at: datetime = Field(..., description="Creation timestamp (UTC, timezone-aware)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC, timezone-aware)")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Origin and derivation metadata")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    references: List[str] = Field(default_factory=list, description="Related object references")

    # HarnessCase-specific fields
    case_type: str = Field(..., description="Type of harness case (e.g., 'loop_completeness')")
    subject_refs: List[str] = Field(..., description="References to objects under evaluation (Task, Experiment, Decision)")
    expected_behavior: Dict[str, Any] = Field(..., description="Expected behavior/shape for this harness case")
    actual_behavior: Dict[str, Any] = Field(..., description="Actual observed behavior/shape")
    pass_fail: bool = Field(..., description="Pass/fail result of the harness evaluation")
    evidence_refs: List[str] = Field(default_factory=list, description="References to evidence supporting this evaluation")
    notes: Optional[str] = Field(None, description="Additional notes or context for this harness case")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
