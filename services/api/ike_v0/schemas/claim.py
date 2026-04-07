"""
IKE v0 Claim Schema

Represents one claim/statement derived from observations in the v0 loop.

See: docs/IKE_SHARED_OBJECTS_V0.md
"""

from datetime import datetime
from typing import Optional, List, Literal

from pydantic import Field

from .envelope import SharedEnvelope


class Claim(SharedEnvelope):
    """
    IKE v0 Claim object.

    Represents one claim or statement derived from observations.
    Claims are structured interpretations that can be validated or refuted.

    Fields follow the v0 contract from IKE_SHARED_OBJECTS_V0.md.
    """

    # Override kind with specific literal type
    kind: Literal["claim"] = Field(default="claim", description="Object type discriminator")

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
