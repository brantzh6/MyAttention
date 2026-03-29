"""
IKE v0 Experiment Schema

Represents one deliberate experiment created to test a hypothesis
or compare alternatives in the v0 loop.

See: docs/IKE_SHARED_OBJECTS_V0.md
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal

from pydantic import BaseModel, Field

from .envelope import SharedEnvelope


class Experiment(BaseModel):
    """
    IKE v0 Experiment object.

    Represents one deliberate experiment created to test a hypothesis
    or compare alternatives. Not yet executed - this is the contract/plan layer.

    Fields follow the v0 contract from IKE_SHARED_OBJECTS_V0.md.
    """

    # Shared envelope fields (explicitly defined for clarity)
    id: str = Field(..., description="Unique identifier (IKE typed ID)")
    kind: Literal["experiment"] = Field(default="experiment", description="Object type discriminator")
    version: str = Field(default="v0.1.0", description="Schema version")
    status: str = Field(default="draft", description="Lifecycle status (draft, open, in_progress, completed, cancelled)")
    created_at: datetime = Field(..., description="Creation timestamp (UTC, timezone-aware)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC, timezone-aware)")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Origin and derivation metadata")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    references: List[str] = Field(default_factory=list, description="Related object references")

    # Experiment-specific fields
    task_ref: str = Field(..., description="Reference to parent ResearchTask")
    experiment_type: str = Field(..., description="Type of experiment (e.g., 'source_plan_comparison')")
    title: str = Field(..., description="Experiment title")
    hypothesis: str = Field(..., description="Hypothesis being tested")
    method_ref: str = Field(..., description="Reference to method/protocol for this experiment")
    input_refs: List[str] = Field(default_factory=list, description="References to input objects for the experiment")
    evidence_refs: List[str] = Field(default_factory=list, description="References to evidence objects produced by the experiment")
    result_summary: Optional[str] = Field(None, description="Summary of experiment results (populated after execution)")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
