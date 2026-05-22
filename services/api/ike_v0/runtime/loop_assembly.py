"""
IKE v0.1 Full Loop Assembly Helper

Bounded helper for assembling the full IKE v0.1 loop in-process.

This is a pure composition layer - no DB writes, no runtime changes.
"""

from typing import Optional, Tuple

from ike_v0.schemas.observation import Observation
from ike_v0.schemas.entity import Entity
from ike_v0.schemas.claim import Claim
from ike_v0.runtime.chain_artifact import (
    ChainArtifact,
    bootstrap_chain_from_observation,
    attach_harness_validation,
)
from ike_v0.mappers.extraction import extract_entity_and_claim_from_observation
from ike_v0.mappers.research_task import derive_research_task_from_entity_claim
from ike_v0.mappers.experiment import create_claim_validation_experiment
from ike_v0.mappers.decision import derive_decision_from_experiment


def assemble_full_loop(
    observation: Observation,
    entity_type: str = "organization",
    canonical_key: Optional[str] = None,
    display_name: Optional[str] = None,
    claim_type: str = "capability",
    statement: Optional[str] = None,
    task_type: str = "discovery",
    experiment_hypothesis: Optional[str] = None,
    decision_outcome: str = "adopt",
) -> Tuple[ChainArtifact, Entity, Claim]:
    """
    Assemble the full IKE v0.1 loop in-process from a single Observation.

    This is a bounded proof helper that composes all accepted loop pieces:
    1. Bootstrap chain from observation
    2. Extract entity/claim from observation
    3. Derive research task from entity/claim
    4. Create claim-validation experiment
    5. Derive decision from experiment
    6. Attach harness validation to chain

    This helper is purely in-process and provisional:
    - no DB writes
    - no API changes
    - no new persistence behavior
    - returns assembled chain for inspection

    Args:
        observation: The starting Observation object (required)
        entity_type: Type of entity to extract (default: "organization")
        canonical_key: Optional canonical key for entity. If not provided,
                       generated from observation ID
        display_name: Optional display name for entity. If not provided,
                      derived from observation title
        claim_type: Type of claim to extract (default: "capability")
        statement: Optional claim statement. If not provided, derived from
                   observation summary
        task_type: Type of research task (default: "discovery")
        experiment_hypothesis: Optional hypothesis for experiment. If not
                               provided, derived from claim statement
        decision_outcome: Decision outcome (default: "adopt")

    Returns:
        Tuple of (ChainArtifact, Entity, Claim) where:
        - ChainArtifact is the completed loop chain with harness_case attached
        - Entity is the extracted entity
        - Claim is the extracted claim

    Usage notes:
        - This is a proof helper for end-to-end loop assembly
        - All objects are provisional (draft status)
        - Use chain.is_complete() to verify the loop is complete
        - Use chain.to_dict() to serialize for TaskArtifact persistence

    See also:
        - bootstrap_chain_from_observation()
        - extract_entity_and_claim_from_observation()
        - derive_research_task_from_entity_claim()
        - create_claim_validation_experiment()
        - derive_decision_from_experiment()
        - attach_harness_validation()
    """
    # Step 1: Bootstrap chain from observation
    chain = bootstrap_chain_from_observation(observation)

    # Step 2: Extract entity/claim from observation
    if canonical_key is None:
        canonical_key = f"derived_from:{observation.id}"
    if display_name is None:
        display_name = observation.title[:50] if len(observation.title) > 50 else observation.title
    if statement is None:
        statement = observation.summary[:100] if len(observation.summary) > 100 else observation.summary

    entity, claim = extract_entity_and_claim_from_observation(
        observation=observation,
        entity_type=entity_type,
        canonical_key=canonical_key,
        display_name=display_name,
        claim_type=claim_type,
        statement=statement,
    )

    # Step 3: Derive research task from entity/claim
    task = derive_research_task_from_entity_claim(
        observation=observation,
        entity=entity,
        claim=claim,
        task_type=task_type,
    )

    # Step 4: Create claim-validation experiment
    if experiment_hypothesis is None:
        experiment_hypothesis = f"Claim is valid: {statement}"

    experiment = create_claim_validation_experiment(
        task_ref=task.id,
        claim_ref=claim.id,
        hypothesis=experiment_hypothesis,
        evidence_refs=[observation.id, entity.id],
    )

    # Step 5: Derive decision from experiment
    decision = derive_decision_from_experiment(
        task=task,
        experiment=experiment,
        decision_outcome=decision_outcome,
    )

    # Step 6: Assemble chain with all objects
    chain = ChainArtifact(
        chain_id=chain.chain_id,
        observation=chain.observation,
        entity=entity,
        claim=claim,
        research_task=task,
        experiment=experiment,
        decision=decision,
    )

    # Step 7: Attach harness validation to close the loop
    chain = attach_harness_validation(chain)

    return (chain, entity, claim)
