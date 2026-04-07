"""
IKE v0 ResearchTask Mapper

Maps existing task substrate (Task, optional TaskContext) to explicit v0
ResearchTask objects.

This is a pure adapter layer - no DB writes, no runtime changes.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ike_v0.types.ids import generate_ike_id, IKEKind
from ike_v0.schemas.research_task import ResearchTask

if __name__ == "__main__":
    # For type checking only - avoid circular imports at runtime
    pass


# Status mapping from Task status to ResearchTask status
TASK_TO_RESEARCH_STATUS = {
    "pending": "draft",
    "confirmed": "open",
    "executing": "in_progress",
    "completed": "completed",
    "failed": "blocked",
    "rejected": "cancelled",
    "expired": "cancelled",
}

# Priority is preserved as-is from task substrate (int 0-3)
# No mapping needed - numeric comparability is maintained


def _infer_trigger_type_from_source_type(source_type: Optional[str]) -> str:
    """
    Infer trigger_type from source_type for evolution/health substrate.

    This is a narrow, safe inference for the current runtime substrate:
    - evolution-detected issues -> governance
    - system_health / health checks -> gap
    - anti_crawl / access issues -> gap
    - everything else -> manual

    Keep this narrow and explicit. Do not invent broad trigger semantics.
    """
    if not source_type:
        return "manual"

    source_lower = source_type.lower()

    # Evolution-detected quality or process issues -> governance trigger
    if "evolution" in source_lower:
        return "governance"

    # Health/quality gaps -> gap trigger
    if "health" in source_lower or "quality" in source_lower:
        return "gap"

    # Access/crawl issues -> gap trigger
    if "anti_crawl" in source_lower or "blocked" in source_lower:
        return "gap"

    # Default: manual trigger
    return "manual"


def map_task_to_research_task(
    task: Any,
    task_context: Optional[Any] = None,
    infer_trigger_type: bool = True,
) -> ResearchTask:
    """
    Materialize a v0 ResearchTask from a persisted Task.

    This mapper is wired for the evolution/health task substrate as the
    first v0.1 starter slice. It preserves numeric priority semantics and
    strengthens traceability back to the original task substrate.

    Args:
        task: Task ORM object or dict-like with task fields.
              Expected fields: id, title, description, goal, task_type, priority,
              status, source_type, assigned_brain, context_id, parent_task_id,
              created_at, updated_at, artifact_refs (optional)
        task_context: Optional TaskContext object for additional context.
                      Expected fields: id, title, goal, artifact_refs (optional)
        infer_trigger_type: Whether to infer trigger_type from source_type.
                            Defaults to True for runtime-backed mapping.

    Returns:
        ResearchTask object with v0 contract fields populated

    Mapping notes:
        - id: generated typed ID
        - task_type: from task.task_type or inferred
        - title: task.title
        - goal: task.goal or task.description
        - trigger_type: inferred from source_type via _infer_trigger_type_from_source_type
        - input_refs: context_id + artifact_refs from context/task
        - priority: preserved from task.priority (int 0-3)
        - owner_brain: task.assigned_brain
        - status: mapped via TASK_TO_RESEARCH_STATUS
        - provenance: includes full substrate trace (task_id, context_id, source_type, artifacts)
        - references: context_id, parent_task_id, artifact_refs
    """
    now = datetime.now(timezone.utc)

    # Extract fields from task (handle both ORM and dict)
    if hasattr(task, "__dict__"):
        t = task.__dict__
        # SQLAlchemy adds _sa_instance_state, filter it
        t = {k: v for k, v in t.items() if k != "_sa_instance_state"}
    else:
        t = task

    def get_field(name: str, default=None):
        if isinstance(t, dict):
            return t.get(name, default)
        return getattr(task, name, default)

    # Build research task ID
    rt_id = generate_ike_id(IKEKind.RESEARCH_TASK)

    # Task type
    task_type_val = get_field("task_type", "workflow")
    task_type = str(task_type_val) if task_type_val else "workflow"

    # Title and goal
    title = get_field("title", "Untitled Research Task")
    goal = get_field("goal") or get_field("description", "No goal specified")

    # Trigger type inference - narrowed for evolution/health substrate
    trigger_type = "manual"
    if infer_trigger_type:
        source_type = get_field("source_type")
        trigger_type = _infer_trigger_type_from_source_type(source_type)

    # Input refs - collect from context and task artifacts
    input_refs: List[str] = []
    context_id = get_field("context_id")
    if context_id:
        input_refs.append(str(context_id))

    # Include artifact refs from task if available (evolution substrate)
    artifact_refs = get_field("artifact_refs")
    if artifact_refs and isinstance(artifact_refs, list):
        for ref in artifact_refs:
            if ref and ref not in input_refs:
                input_refs.append(str(ref))

    # Priority: preserve as numeric from task substrate (0-3)
    priority_val = get_field("priority", 2)
    if isinstance(priority_val, int):
        priority = priority_val
    else:
        # Fallback: try to convert, default to 2 (medium)
        try:
            priority = int(priority_val)
        except (ValueError, TypeError):
            priority = 2

    # Owner brain - preserve from task substrate
    owner_brain = get_field("assigned_brain")

    # Status mapping
    task_status = get_field("status", "pending")
    status = TASK_TO_RESEARCH_STATUS.get(task_status, "draft")

    # Timestamps
    created_at = get_field("created_at") or now
    updated_at = get_field("updated_at") or now

    # Ensure timezone awareness
    if created_at and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if updated_at and updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)

    # Provenance - full trace back to original task substrate
    provenance: Dict[str, Any] = {
        "mapper": "map_task_to_research_task",
        "original_task_id": get_field("id"),
        "original_task_type": task_type,
        "original_status": task_status,
        "source_type": get_field("source_type"),
    }

    # Add context trace if available
    if task_context is not None:
        provenance["has_context"] = True
        if hasattr(task_context, "id"):
            provenance["context_id"] = str(task_context.id)
        elif isinstance(task_context, dict) and "id" in task_context:
            provenance["context_id"] = str(task_context["id"])

    # Add artifact trace if available
    if artifact_refs:
        provenance["artifact_count"] = len(artifact_refs)

    # References - build from context, parent task, and artifacts
    references: List[str] = []
    if context_id:
        references.append(str(context_id))
    parent_task_id = get_field("parent_task_id")
    if parent_task_id:
        references.append(str(parent_task_id))
    if artifact_refs and isinstance(artifact_refs, list):
        for ref in artifact_refs:
            if ref and ref not in references:
                references.append(str(ref))

    return ResearchTask(
        id=rt_id,
        kind="research_task",
        version="v0.1.0",
        status=status,
        created_at=created_at,
        updated_at=updated_at,
        provenance=provenance,
        confidence=0.5,
        references=references,
        task_type=task_type,
        title=title,
        goal=goal,
        trigger_type=trigger_type,
        input_refs=input_refs,
        priority=priority,
        owner_brain=owner_brain,
    )


def derive_research_task_from_entity_claim(
    observation: Any,
    entity: Any,
    claim: Any,
    task_type: str = "discovery",
    title: Optional[str] = None,
    goal: Optional[str] = None,
    assigned_brain: Optional[str] = None,
) -> ResearchTask:
    """
    Derive a provisional ResearchTask from Entity/Claim/Observation loop objects.

    This is a bounded glue helper for the v0.1 real loop. It creates a
    ResearchTask from already-created loop-middle objects (Observation,
    Entity, Claim), preserving explicit traceability through input_refs,
    references, and provenance.

    This helper is additive and does not replace map_task_to_research_task.
    It is for deriving tasks from the IKE loop itself, not from substrate.

    Args:
        observation: Observation object (required) - the source observation
        entity: Entity object (required) - the derived entity
        claim: Claim object (required) - the derived claim
        task_type: Type of research task (default: "discovery")
        title: Optional task title. If not provided, derived from claim statement
        goal: Optional task goal. If not provided, derived from claim statement
        assigned_brain: Optional assigned brain/agent for the task

    Returns:
        ResearchTask object with v0 contract fields populated

    Traceability:
        - input_refs: includes observation.id, entity.id, claim.id
        - references: includes observation.id, entity.id, claim.id
        - provenance: includes mapper name, source object IDs, derivation info

    Usage notes:
        - This is for loop-derived tasks, not substrate-mapped tasks
        - The resulting task is provisional (draft status)
        - Use in conjunction with bootstrap_chain_from_observation()
    """
    now = datetime.now(timezone.utc)

    # Extract IDs from objects (handle both objects and dicts)
    def get_id(obj: Any) -> str:
        if hasattr(obj, "id"):
            return obj.id
        if isinstance(obj, dict) and "id" in obj:
            return obj["id"]
        raise ValueError("Object must have an 'id' attribute or key")

    def get_kind(obj: Any) -> str:
        if hasattr(obj, "kind"):
            return obj.kind
        if isinstance(obj, dict) and "kind" in obj:
            return obj["kind"]
        return "unknown"

    obs_id = get_id(observation)
    entity_id = get_id(entity)
    claim_id = get_id(claim)

    # Build research task ID
    rt_id = generate_ike_id(IKEKind.RESEARCH_TASK)

    # Title and goal - derive from claim if not provided
    if title is None:
        # Try to get from claim object
        if hasattr(claim, "statement"):
            statement = claim.statement
        elif isinstance(claim, dict) and "statement" in claim:
            statement = claim["statement"]
        else:
            statement = "Investigate derived claim"
        title = f"Investigate: {statement[:50]}..." if len(statement) > 50 else f"Investigate: {statement}"

    if goal is None:
        if hasattr(claim, "statement"):
            goal = f"Validate claim: {claim.statement}"
        elif isinstance(claim, dict) and "statement" in claim:
            goal = f"Validate claim: {claim['statement']}"
        else:
            goal = "Validate the derived claim from observation"

    # Trigger type - derived from entity/claim path
    trigger_type = "gap"  # Entity/Claim derivation indicates a knowledge gap

    # Input refs - all source objects
    input_refs: List[str] = [obs_id, entity_id, claim_id]

    # Priority - default to medium (2) for derived tasks
    priority = 2

    # Status - draft for provisional tasks
    status = "draft"

    # Provenance - full trace to source objects
    provenance: Dict[str, Any] = {
        "mapper": "derive_research_task_from_entity_claim",
        "derivation_path": "observation -> entity/claim -> research_task",
        "source_observation_id": obs_id,
        "source_entity_id": entity_id,
        "source_claim_id": claim_id,
        "source_observation_kind": get_kind(observation),
        "source_entity_kind": get_kind(entity),
        "source_claim_kind": get_kind(claim),
    }

    # References - all source objects
    references: List[str] = [obs_id, entity_id, claim_id]

    return ResearchTask(
        id=rt_id,
        kind="research_task",
        version="v0.1.0",
        status=status,
        created_at=now,
        updated_at=now,
        provenance=provenance,
        confidence=0.5,
        references=references,
        task_type=task_type,
        title=title,
        goal=goal,
        trigger_type=trigger_type,
        input_refs=input_refs,
        priority=priority,
        owner_brain=assigned_brain,
    )
