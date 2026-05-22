"""
IKE v0 Extraction Mapper

Bounded helper for extracting Entity and Claim objects from a single Observation.

This is a pure adapter layer - no DB writes, no runtime changes, no LLM inference.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from ike_v0.types.ids import generate_ike_id, IKEKind
from ike_v0.schemas.entity import Entity
from ike_v0.schemas.claim import Claim
from ike_v0.schemas.observation import Observation


def extract_entity_and_claim_from_observation(
    observation: Observation,
    entity_type: str,
    canonical_key: str,
    display_name: str,
    claim_type: str,
    statement: str,
    aliases: List[str] = None,
) -> Tuple[Entity, Claim]:
    """
    Extract one Entity and one Claim from a single Observation.

    This is a bounded helper that creates explicit Entity and Claim objects
    from caller-supplied extraction results. It does not perform inference.

    Args:
        observation: The source Observation object
        entity_type: Type of entity (e.g., 'organization', 'person', 'technology')
        canonical_key: Canonical identifier for the entity
        display_name: Human-readable display name for the entity
        claim_type: Type of claim (e.g., 'capability', 'relationship', 'event')
        statement: The claim statement in natural language
        aliases: Optional list of alternative names for the entity

    Returns:
        Tuple of (Entity, Claim) with v0 contract fields populated

    Traceability:
        - Entity.references includes the observation ID
        - Entity.provenance includes source observation info
        - Claim.subject_refs includes the entity ID
        - Claim.source_observation_refs includes the observation ID
        - Claim.evidence_refs includes the observation ID
        - Claim.references includes both entity and observation IDs
    """
    now = datetime.now(timezone.utc)

    # Generate IDs
    entity_id = generate_ike_id(IKEKind.ENTITY)
    claim_id = generate_ike_id(IKEKind.CLAIM)

    # Default aliases
    if aliases is None:
        aliases = []

    # Build Entity provenance
    entity_provenance: Dict[str, Any] = {
        "mapper": "extract_entity_and_claim_from_observation",
        "source_observation_id": observation.id,
        "source_signal_type": observation.signal_type,
        "extraction_method": "manual",
    }

    # Build Entity references
    entity_references: List[str] = [observation.id]

    # Create Entity
    entity = Entity(
        id=entity_id,
        kind="entity",
        version="v0.1.0",
        status="draft",
        created_at=now,
        updated_at=now,
        provenance=entity_provenance,
        confidence=0.5,  # Conservative default per v0 guidance
        references=entity_references,
        entity_type=entity_type,
        canonical_key=canonical_key,
        display_name=display_name,
        aliases=aliases,
    )

    # Build Claim provenance
    claim_provenance: Dict[str, Any] = {
        "mapper": "extract_entity_and_claim_from_observation",
        "source_observation_id": observation.id,
        "derived_from_entity_id": entity_id,
        "extraction_method": "manual",
    }

    # Build Claim references - includes entity and observation
    claim_references: List[str] = [entity_id, observation.id]

    # Create Claim
    claim = Claim(
        id=claim_id,
        kind="claim",
        version="v0.1.0",
        status="draft",
        created_at=now,
        updated_at=now,
        provenance=claim_provenance,
        confidence=0.5,  # Conservative default per v0 guidance
        references=claim_references,
        claim_type=claim_type,
        statement=statement,
        subject_refs=[entity_id],  # Links to the extracted entity
        evidence_refs=[observation.id],  # Observation as evidence
        source_observation_refs=[observation.id],
    )

    return (entity, claim)
