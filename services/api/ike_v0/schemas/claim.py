"""
IKE v0 Claim Schema

Represents one claim/statement derived from observations in the v0 loop.

See: docs/IKE_SHARED_OBJECTS_V0.md
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal

from pydantic import BaseModel, Field


class Claim(BaseModel):
    """
    IKE v0 Claim object.

    Represents one claim or statement derived from observations.
    Claims are structured interpretations that can be validated or refuted.

    Fields follow the v0 contract from IKE_SHARED_OBJECTS_V0.md.
    """

    # Shared envelope fields (explicitly defined for clarity)
    id: str = Field(..., description="Unique identifier (IKE typed ID)")
    kind: Literal["claim"] = Field(default="claim", description="Object type discriminator")
    version: str = Field(default="v0.1.0", description="Schema version")
    status: str = Field(default="draft", description="Lifecycle status (draft, proposed, validated, refuted, archived)")
    created_at: datetime = Field(..., description="Creation timestamp (UTC, timezone-aware)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC, timezone-aware)")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Origin and derivation metadata")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    references: List[str] = Field(default_factory=list, description="Related object references")

    # Claim-specific fields
    claim_type: str = Field(..., description="Type of claim (e.g., 'capability', 'relationship', 'event')")
    statement: str = Field(..., description="The claim statement in natural language")
    subject_refs: List[str] = Field(..., description="References to subject entities this claim is about")
    evidence_refs: List[str] = Field(default_factory=list, description="References to supporting evidence")
    source_observation_refs: List[str] = Field(..., description="References to source observations")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
