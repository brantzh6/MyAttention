"""
IKE v0 Entity Schema

Represents one identified entity extracted from observations in the v0 loop.

See: docs/IKE_SHARED_OBJECTS_V0.md
"""

from datetime import datetime
from typing import Optional, List, Literal

from pydantic import Field

from .envelope import SharedEnvelope


class Entity(SharedEnvelope):
    """
    IKE v0 Entity object.

    Represents one identified entity extracted from observations.
    Entities are structured interpretations with canonical identity.

    Fields follow the v0 contract from IKE_SHARED_OBJECTS_V0.md.
    """

    # Override kind with specific literal type
    kind: Literal["entity"] = Field(default="entity", description="Object type discriminator")

    # Entity-specific fields
    entity_type: str = Field(..., description="Type of entity (e.g., 'organization', 'person', 'technology')")
    canonical_key: str = Field(..., description="Canonical identifier/key for this entity")
    display_name: str = Field(..., description="Human-readable display name")
    aliases: List[str] = Field(default_factory=list, description="Alternative names or aliases")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
