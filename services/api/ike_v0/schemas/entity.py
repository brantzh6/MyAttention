"""
IKE v0 Entity Schema

Represents one identified entity extracted from observations in the v0 loop.

See: docs/IKE_SHARED_OBJECTS_V0.md
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal

from pydantic import BaseModel, Field


class Entity(BaseModel):
    """
    IKE v0 Entity object.

    Represents one identified entity extracted from observations.
    Entities are structured interpretations with canonical identity.

    Fields follow the v0 contract from IKE_SHARED_OBJECTS_V0.md.
    """

    # Shared envelope fields (explicitly defined for clarity)
    id: str = Field(..., description="Unique identifier (IKE typed ID)")
    kind: Literal["entity"] = Field(default="entity", description="Object type discriminator")
    version: str = Field(default="v0.1.0", description="Schema version")
    status: str = Field(default="draft", description="Lifecycle status (draft, active, archived)")
    created_at: datetime = Field(..., description="Creation timestamp (UTC, timezone-aware)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC, timezone-aware)")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Origin and derivation metadata")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    references: List[str] = Field(default_factory=list, description="Related object references")

    # Entity-specific fields
    entity_type: str = Field(..., description="Type of entity (e.g., 'organization', 'person', 'technology')")
    canonical_key: str = Field(..., description="Canonical identifier/key for this entity")
    display_name: str = Field(..., description="Human-readable display name")
    aliases: List[str] = Field(default_factory=list, description="Alternative names or aliases")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
