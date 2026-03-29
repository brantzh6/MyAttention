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


def map_task_to_research_task(
    task: Any,
    task_context: Optional[Any] = None,
    infer_trigger_type: bool = True,
) -> ResearchTask:
    """
    Materialize a v0 ResearchTask from a persisted Task.

    Args:
        task: Task ORM object or dict-like with task fields
        task_context: Optional TaskContext object for additional context
        infer_trigger_type: Whether to infer trigger_type from task data

    Returns:
        ResearchTask object with v0 contract fields populated

    Mapping notes:
        - id: generated typed ID
        - task_type: from task.task_type or inferred
        - title: task.title
        - goal: task.goal or task.description
        - trigger_type: inferred from source_type or "manual"
        - input_refs: from context or empty
        - priority: preserved from task.priority (int 0-3)
        - owner_brain: task.assigned_brain
        - status: mapped via TASK_TO_RESEARCH_STATUS
        - provenance: includes mapping metadata and original task_id for traceability
        - references: includes context_id if present
    """
    now = datetime.now(timezone.utc)

    # Extract fields from task (handle both ORM and dict)
    if hasattr(task, "__dict__"):
        t = task.__dict__
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

    # Trigger type inference
    trigger_type = "manual"
    if infer_trigger_type:
        source_type = get_field("source_type", "")
        if source_type:
            if "anti_crawl" in source_type:
                trigger_type = "gap"
            elif "evolution" in source_type:
                trigger_type = "governance"
            elif "health" in source_type:
                trigger_type = "gap"
            else:
                trigger_type = "manual"

    # Input refs
    input_refs: List[str] = []
    context_id = get_field("context_id")
    if context_id:
        input_refs.append(str(context_id))

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

    # Owner brain
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

    # Provenance - includes trace back to original task substrate
    provenance: Dict[str, Any] = {
        "mapper": "map_task_to_research_task",
        "original_task_type": task_type,
        "original_status": task_status,
        "source_type": get_field("source_type"),
        "original_task_id": get_field("id"),  # Trace back to original task
    }
    if task_context is not None:
        provenance["has_context"] = True

    # References
    references: List[str] = []
    if context_id:
        references.append(str(context_id))
    parent_task_id = get_field("parent_task_id")
    if parent_task_id:
        references.append(str(parent_task_id))

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
