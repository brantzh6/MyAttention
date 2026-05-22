"""
IKE v0 Procedural Memory Schema

Represents one durable procedural lesson captured at task closure.

See: docs/IKE_CLAUDE_CODE_B3_PROTOTYPE_DECISION.md
"""

from datetime import datetime
from typing import Optional, Literal

from pydantic import Field

from .envelope import SharedEnvelope


class ProceduralMemory(SharedEnvelope):
    """
    IKE v0 Procedural Memory object.

    Represents one durable procedural lesson captured from task closure.
    This is the minimal structured record for the v1 prototype.

    Fields follow the B3 prototype decision from IKE_CLAUDE_CODE_B3_PROTOTYPE_DECISION.md.
    """

    # Override kind with specific literal type
    kind: Literal["procedure"] = Field(default="procedure", description="Object type discriminator")

    # Procedural memory specific fields (per B3 prototype decision)
    memory_type: Literal["procedure"] = Field(default="procedure", description="Memory category - only 'procedure' in v1")
    title: str = Field(..., description="Short title for the procedural lesson")
    lesson: str = Field(..., description="The core procedural lesson learned")
    why_it_mattered: str = Field(..., description="Why this lesson mattered in context")
    how_to_apply: str = Field(..., description="Concrete guidance on how to apply this lesson")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this lesson (0.0 to 1.0)")
    source_artifact_ref: str = Field(..., description="Reference to the source artifact (e.g., task closure ID)")
    created_from: Literal["task_closure"] = Field(default="task_closure", description="Trigger point that created this memory")
    created_at: datetime = Field(..., description="When the memory was created (UTC)")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
