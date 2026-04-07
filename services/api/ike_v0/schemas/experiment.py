"""
IKE v0 Experiment Schema

Represents one deliberate experiment created to test a hypothesis
or compare alternatives in the v0 loop.

See: docs/IKE_SHARED_OBJECTS_V0.md
"""

from datetime import datetime
from typing import Optional, List, Literal

from pydantic import Field

from .envelope import SharedEnvelope


class Experiment(SharedEnvelope):
    """
    IKE v0 Experiment object.

    Represents one deliberate experiment created to test a hypothesis
    or compare alternatives. Not yet executed - this is the contract/plan layer.

    Fields follow the v0 contract from IKE_SHARED_OBJECTS_V0.md.
    """

    # Override kind with specific literal type
    kind: Literal["experiment"] = Field(default="experiment", description="Object type discriminator")

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
