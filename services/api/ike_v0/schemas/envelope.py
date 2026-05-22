"""
IKE v0 Shared Envelope Schema

This module defines the minimum shared envelope contract for all IKE v0 objects.
All v0 objects (Observation, Entity, Claim, ResearchTask, Experiment, Decision)
carry this common envelope for inspectability, provenance, and state tracking.

See: docs/IKE_SHARED_OBJECTS_V0.md
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


class SharedEnvelope(BaseModel):
    """
    Common envelope for all IKE v0 objects.

    This base class defines the shared fields that all IKE v0 objects carry.
    Subclasses should override the 'kind' field with a Literal type for their
    specific object type.

    Fields:
        id: Unique identifier for the object (IKE typed ID format)
        kind: Object type discriminator (e.g., 'observation', 'entity', 'claim')
        version: Schema version string (e.g., 'v0.1.0')
        status: Lifecycle status (e.g., 'draft', 'active', 'archived')
        created_at: Object creation timestamp (UTC, timezone-aware)
        updated_at: Last modification timestamp (UTC, timezone-aware)
        provenance: Origin and derivation metadata
        confidence: Confidence score 0.0-1.0
        references: List of related object references
    """

    id: str = Field(..., description="Unique identifier (IKE typed ID)")
    kind: str = Field(..., description="Object type discriminator")
    version: str = Field(default="v0.1.0", description="Schema version")
    status: str = Field(default="draft", description="Lifecycle status")
    created_at: datetime = Field(default_factory=_utc_now, description="Creation timestamp (UTC, timezone-aware)")
    updated_at: datetime = Field(default_factory=_utc_now, description="Last update timestamp (UTC, timezone-aware)")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Origin and derivation metadata")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    references: List[str] = Field(default_factory=list, description="Related object references")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
