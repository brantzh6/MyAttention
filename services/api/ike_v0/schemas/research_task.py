"""
IKE v0 ResearchTask Schema

Represents one deliberate inquiry created from a gap, signal, contradiction,
or governance action in the v0 loop.

See: docs/IKE_SHARED_OBJECTS_V0.md
"""

from datetime import datetime
from typing import Optional, List, Literal

from pydantic import Field

from .envelope import SharedEnvelope


class ResearchTask(SharedEnvelope):
    """
    IKE v0 ResearchTask object.

    Represents one deliberate inquiry created from a gap, signal, contradiction,
    or governance action. Not yet executed - this is the contract/plan layer.

    Fields follow the v0 contract from IKE_SHARED_OBJECTS_V0.md.
    """

    # Override kind with specific literal type
    kind: Literal["research_task"] = Field(default="research_task", description="Object type discriminator")

    # ResearchTask-specific fields
    task_type: str = Field(..., description="Type of research task (e.g., 'discovery', 'validation', 'comparison')")
    title: str = Field(..., description="Task title")
    goal: str = Field(..., description="Task goal/objective")
    trigger_type: str = Field(default="manual", description="What triggered this task (e.g., 'manual', 'gap', 'contradiction', 'governance')")
    input_refs: List[str] = Field(default_factory=list, description="References to input objects (observations, claims, etc.)")
    priority: int = Field(default=2, ge=0, le=3, description="Task priority (0=urgent, 1=high, 2=medium, 3=low) - preserved from task substrate")
    owner_brain: Optional[str] = Field(None, description="Assigned brain/agent responsible for this task")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
