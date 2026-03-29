"""
IKE v0 Observation Schema

Represents one externally observed unit before it becomes structured interpretation.
Maps onto current raw_ingest + feed_items for the v0 loop.

See: docs/IKE_SHARED_OBJECTS_V0.md
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal

from pydantic import BaseModel, Field

from .envelope import SharedEnvelope


class Observation(BaseModel):
    """
    IKE v0 Observation object.

    Represents one externally observed unit before it becomes structured
    interpretation. Not yet a claim or accepted fact.

    Fields follow the v0 contract from IKE_SHARED_OBJECTS_V0.md.
    """

    # Shared envelope fields
    id: str = Field(..., description="Unique identifier (IKE typed ID)")
    kind: Literal["observation"] = Field(default="observation", description="Object type discriminator")
    version: str = Field(default="v0.1.0", description="Schema version")
    status: str = Field(default="draft", description="Lifecycle status")
    created_at: datetime = Field(..., description="Creation timestamp (UTC, timezone-aware)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC, timezone-aware)")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Origin and derivation metadata")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    references: List[str] = Field(default_factory=list, description="Related object references")

    # Observation-specific fields
    source_ref: str = Field(..., description="Reference to the source (e.g., source ID or domain)")
    raw_ref: Optional[str] = Field(None, description="Reference to raw ingest object if available")
    observed_at: datetime = Field(..., description="When the observation was made (UTC)")
    captured_at: datetime = Field(..., description="When the observation was captured/persisted (UTC)")
    title: str = Field(..., description="Observation title")
    summary: str = Field(..., description="Observation summary")
    content_ref: Optional[str] = Field(None, description="Reference to full content (e.g., URL or storage key)")
    content_excerpt: Optional[str] = Field(None, description="Excerpt of the content")
    signal_type: str = Field(default="feed_item", description="Type of signal (e.g., 'feed_item', 'raw_ingest')")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
