"""
IKE v0 ResearchTask Schema

Represents one deliberate inquiry created from a gap, signal, contradiction,
or governance action in the v0 loop.

See: docs/IKE_SHARED_OBJECTS_V0.md
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal

from pydantic import BaseModel, Field


class ResearchTask(BaseModel):
    """
    IKE v0 ResearchTask object.

    Represents one deliberate inquiry created from a gap, signal, contradiction,
    or governance action. Not yet executed - this is the contract/plan layer.

    Fields follow the v0 contract from IKE_SHARED_OBJECTS_V0.md.
    """

    # Shared envelope fields
    id: str = Field(..., description="Unique identifier (IKE typed ID)")
    kind: Literal["research_task"] = Field(default="research_task", description="Object type discriminator")
    version: str = Field(default="v0.1.0", description="Schema version")
    status: str = Field(default="draft", description="Lifecycle status (draft, open, in_progress, blocked, completed, cancelled)")
    created_at: datetime = Field(..., description="Creation timestamp (UTC, timezone-aware)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC, timezone-aware)")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Origin and derivation metadata")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    references: List[str] = Field(default_factory=list, description="Related object references")

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
