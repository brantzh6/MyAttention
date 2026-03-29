"""
IKE v0 Decision Schema

Represents one deliberate decision made in the v0 loop,
typically after evaluating experiments or evidence.

See: docs/IKE_SHARED_OBJECTS_V0.md
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal

from pydantic import BaseModel, Field


class Decision(BaseModel):
    """
    IKE v0 Decision object.

    Represents one deliberate decision made after evaluating experiments
    or evidence. This is the record/contract layer - not execution.

    Fields follow the v0 contract from IKE_SHARED_OBJECTS_V0.md.
    """

    # Shared envelope fields (explicitly defined for clarity)
    id: str = Field(..., description="Unique identifier (IKE typed ID)")
    kind: Literal["decision"] = Field(default="decision", description="Object type discriminator")
    version: str = Field(default="v0.1.0", description="Schema version")
    status: str = Field(default="draft", description="Lifecycle status (draft, pending_review, approved, rejected, implemented, cancelled)")
    created_at: datetime = Field(..., description="Creation timestamp (UTC, timezone-aware)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC, timezone-aware)")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Origin and derivation metadata")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    references: List[str] = Field(default_factory=list, description="Related object references")

    # Decision-specific fields
    task_ref: str = Field(..., description="Reference to parent ResearchTask")
    experiment_refs: List[str] = Field(default_factory=list, description="References to experiments that informed this decision")
    decision_type: str = Field(..., description="Type of decision (e.g., 'experiment_evaluation')")
    decision_outcome: Literal["adopt", "reject", "defer", "escalate"] = Field(..., description="Outcome of the decision per IKE v0 spec")
    rationale: str = Field(..., description="Rationale explaining the decision")
    evidence_refs: List[str] = Field(default_factory=list, description="References to evidence supporting this decision")
    review_required: bool = Field(default=False, description="Whether this decision requires human review")
    review_status: Optional[str] = Field(None, description="Review status if review_required is True (pending, approved, rejected)")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
