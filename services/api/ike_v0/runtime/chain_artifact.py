"""
IKE v0.1 Chain Artifact Helper

Bounded helper for assembling and persisting one IKE v0.1 loop chain
into the existing TaskArtifact substrate.

This is a pure adapter layer - no DB writes, no runtime changes.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ike_v0.schemas.observation import Observation
from ike_v0.schemas.entity import Entity
from ike_v0.schemas.claim import Claim
from ike_v0.schemas.research_task import ResearchTask
from ike_v0.schemas.experiment import Experiment
from ike_v0.schemas.decision import Decision
from ike_v0.schemas.harness_case import HarnessCase


def reconstruct_chain_from_payload(payload: Dict[str, Any]) -> "ChainArtifact":
    """
    Reconstruct a ChainArtifact from a stored payload dict.

    This is the inverse of chain.to_dict() - it rebuilds the ChainArtifact
    from serialized data (e.g., from TaskArtifact.extra).

    Args:
        payload: Dict from chain.to_dict() or TaskArtifact.extra

    Returns:
        Reconstructed ChainArtifact object
    """
    def _reconstruct(kind: str, data: Optional[Dict[str, Any]]):
        """Helper to reconstruct an object from dict."""
        if data is None:
            return None
        kind_map = {
            "observation": Observation,
            "entity": Entity,
            "claim": Claim,
            "research_task": ResearchTask,
            "experiment": Experiment,
            "decision": Decision,
            "harness_case": HarnessCase,
        }
        schema_class = kind_map.get(kind)
        if schema_class is None:
            return None
        return schema_class(**data)

    return ChainArtifact(
        chain_id=payload.get("chain_id", "unknown"),
        observation=_reconstruct("observation", payload.get("observation")),
        entity=_reconstruct("entity", payload.get("entity")),
        claim=_reconstruct("claim", payload.get("claim")),
        research_task=_reconstruct("research_task", payload.get("research_task")),
        experiment=_reconstruct("experiment", payload.get("experiment")),
        decision=_reconstruct("decision", payload.get("decision")),
        harness_case=_reconstruct("harness_case", payload.get("harness_case")),
    )


ARTIFACT_TYPE_IKE_CHAIN = "ike_v0_chain"


class ChainArtifact:
    """
    Represents one assembled IKE v0.1 loop chain artifact.

    This is a transitional container that holds the chain objects
    for inspection and potential persistence via TaskArtifact.

    Attributes:
        chain_id: Unique identifier for this chain
        created_at: When the chain was assembled
        observation: The starting Observation object
        entity: Optional Entity derived from observation
        claim: Optional Claim derived from observation/entity
        research_task: ResearchTask derived from the loop
        experiment: Experiment stub for the task
        decision: Decision based on experiment results
        harness_case: HarnessCase validating loop completeness
    """

    def __init__(
        self,
        chain_id: str,
        observation: Observation,
        entity: Optional[Entity] = None,
        claim: Optional[Claim] = None,
        research_task: Optional[ResearchTask] = None,
        experiment: Optional[Experiment] = None,
        decision: Optional[Decision] = None,
        harness_case: Optional[HarnessCase] = None,
    ):
        self.chain_id = chain_id
        self.created_at = datetime.now(timezone.utc)
        self.observation = observation
        self.entity = entity
        self.claim = claim
        self.research_task = research_task
        self.experiment = experiment
        self.decision = decision
        self.harness_case = harness_case

    def is_complete(self) -> bool:
        """
        Check if the chain has all required objects.

        Returns True if the chain has at minimum:
        - observation
        - research_task
        - experiment
        - decision
        - harness_case

        Entity and Claim are optional.
        """
        required = [
            self.observation,
            self.research_task,
            self.experiment,
            self.decision,
            self.harness_case,
        ]
        return all(obj is not None for obj in required)

    def get_all_refs(self) -> List[str]:
        """
        Collect all object references in the chain.

        Returns a list of all object IDs in the chain.
        """
        refs = []
        if self.observation:
            refs.append(self.observation.id)
        if self.entity:
            refs.append(self.entity.id)
        if self.claim:
            refs.append(self.claim.id)
        if self.research_task:
            refs.append(self.research_task.id)
        if self.experiment:
            refs.append(self.experiment.id)
        if self.decision:
            refs.append(self.decision.id)
        if self.harness_case:
            refs.append(self.harness_case.id)
        return refs

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the chain to a dictionary for storage.

        Returns a dict representation suitable for TaskArtifact.extra payload.
        """
        return {
            "chain_id": self.chain_id,
            "created_at": self.created_at.isoformat(),
            "is_complete": self.is_complete(),
            "observation": self.observation.model_dump(mode="json") if self.observation else None,
            "entity": self.entity.model_dump(mode="json") if self.entity else None,
            "claim": self.claim.model_dump(mode="json") if self.claim else None,
            "research_task": self.research_task.model_dump(mode="json") if self.research_task else None,
            "experiment": self.experiment.model_dump(mode="json") if self.experiment else None,
            "decision": self.decision.model_dump(mode="json") if self.decision else None,
            "harness_case": self.harness_case.model_dump(mode="json") if self.harness_case else None,
            "all_refs": self.get_all_refs(),
        }

    def get_completeness_summary(self) -> Dict[str, Any]:
        """
        Get a summary of chain completeness for inspection.

        Returns a dict showing which objects are present and their IDs.
        """
        return {
            "chain_id": self.chain_id,
            "is_complete": self.is_complete(),
            "objects": {
                "observation": self.observation.id if self.observation else None,
                "entity": self.entity.id if self.entity else None,
                "claim": self.claim.id if self.claim else None,
                "research_task": self.research_task.id if self.research_task else None,
                "experiment": self.experiment.id if self.experiment else None,
                "decision": self.decision.id if self.decision else None,
                "harness_case": self.harness_case.id if self.harness_case else None,
            },
            "object_count": len([obj for obj in [
                self.observation, self.entity, self.claim,
                self.research_task, self.experiment, self.decision, self.harness_case
            ] if obj is not None]),
        }


def assemble_chain_artifact(
    chain_id: str,
    observation: Observation,
    entity: Optional[Entity] = None,
    claim: Optional[Claim] = None,
    research_task: Optional[ResearchTask] = None,
    experiment: Optional[Experiment] = None,
    decision: Optional[Decision] = None,
    harness_case: Optional[HarnessCase] = None,
) -> ChainArtifact:
    """
    Assemble one IKE v0.1 loop chain artifact.

    This is a bounded helper that creates a ChainArtifact container
    from the provided loop objects.

    Args:
        chain_id: Unique identifier for this chain
        observation: The starting Observation object (required)
        entity: Optional Entity derived from observation
        claim: Optional Claim derived from observation/entity
        research_task: ResearchTask derived from the loop
        experiment: Experiment stub for the task
        decision: Decision based on experiment results
        harness_case: HarnessCase validating loop completeness

    Returns:
        ChainArtifact object containing the assembled chain

    Usage notes:
        - observation is required; other objects are optional
        - the chain can be assembled incrementally as objects are created
        - use is_complete() to check if all required objects are present
        - use to_dict() to serialize for TaskArtifact persistence
    """
    return ChainArtifact(
        chain_id=chain_id,
        observation=observation,
        entity=entity,
        claim=claim,
        research_task=research_task,
        experiment=experiment,
        decision=decision,
        harness_case=harness_case,
    )


def build_chain_artifact_payload(
    chain: ChainArtifact,
    context_id: Optional[str] = None,
    task_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a payload dict suitable for TaskArtifact persistence.

    This helper prepares the chain data for storage via the existing
    TaskArtifact substrate.

    Args:
        chain: The ChainArtifact to serialize
        context_id: Optional context ID for linkage
        task_id: Optional task ID for linkage

    Returns:
        Dict suitable for TaskArtifact.extra payload
    """
    payload = chain.to_dict()

    # Add linkage metadata
    if context_id:
        payload["context_id"] = context_id
    if task_id:
        payload["task_id"] = task_id

    # Add artifact type marker
    payload["artifact_type_marker"] = ARTIFACT_TYPE_IKE_CHAIN

    return payload


def bootstrap_chain_from_observation(
    observation: Observation,
    chain_id: Optional[str] = None,
) -> ChainArtifact:
    """
    Bootstrap a new IKE v0.1 loop chain from an Observation.

    This is the first glue step for starting a runtime-backed loop.
    It creates a minimal ChainArtifact with only the observation populated,
    ready for incremental assembly of the remaining loop objects.

    This helper is purely additive and runtime-scoped:
    - no DB writes
    - no durable identity promise (chain_id is provisional)
    - no automatic triggering

    Args:
        observation: The starting Observation object (required)
        chain_id: Optional chain identifier. If not provided, generates
                  a provisional ID in format 'ike_chain:{uuid}'

    Returns:
        ChainArtifact with observation populated, other objects None

    Usage notes:
        - This is the entry point for starting a new IKE loop
        - The returned chain can be incrementally built up using
          assemble_chain_artifact() or by setting attributes directly
        - Use to_dict() or build_chain_artifact_payload() to serialize
          for TaskArtifact persistence when ready
    """
    if chain_id is None:
        chain_id = f"ike_chain:{uuid4()}"

    return ChainArtifact(
        chain_id=chain_id,
        observation=observation,
    )


def attach_harness_validation(chain: ChainArtifact) -> ChainArtifact:
    """
    Attach HarnessCase validation to a populated chain.

    This is the final glue step that closes the first inspectable loop.
    It runs loop-completeness validation on the chain and attaches the
    resulting HarnessCase back to the chain.

    This helper is purely additive:
    - reuses existing validate_chain_loop_completeness() behavior
    - returns a new ChainArtifact with harness_case attached
    - no DB writes
    - no persistence changes

    Args:
        chain: ChainArtifact with observation, research_task, experiment,
               and decision populated (harness_case may be None)

    Returns:
        New ChainArtifact with harness_case attached from validation

    Usage notes:
        - This closes the loop: Observation -> Entity/Claim -> ResearchTask
          -> Experiment -> Decision -> HarnessCase
        - The returned chain should be complete if all required objects
          were present in the input chain
        - Use is_complete() to verify the chain is now complete
        - Use to_dict() to serialize for TaskArtifact persistence

    See also:
        - validate_chain_loop_completeness() in ike_v0.mappers.harness_case
    """
    from ike_v0.mappers.harness_case import validate_chain_loop_completeness

    # Run loop-completeness validation
    harness_case = validate_chain_loop_completeness(chain)

    # Return new chain with harness_case attached
    return ChainArtifact(
        chain_id=chain.chain_id,
        observation=chain.observation,
        entity=chain.entity,
        claim=chain.claim,
        research_task=chain.research_task,
        experiment=chain.experiment,
        decision=chain.decision,
        harness_case=harness_case,
    )
