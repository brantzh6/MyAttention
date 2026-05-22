from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import ContextStatus, ContextType, Task, TaskArtifact, TaskContext, TaskHistory, TaskType


async def ensure_task_context(
    db: AsyncSession,
    *,
    context_type: str,
    owner_type: str,
    owner_id: str,
    title: str,
    goal: str,
    priority: int = 1,
) -> TaskContext:
    result = await db.execute(
        select(TaskContext).where(
            TaskContext.context_type == context_type,
            TaskContext.owner_type == owner_type,
            TaskContext.owner_id == owner_id,
            TaskContext.status == ContextStatus.ACTIVE.value,
        )
    )
    existing = result.scalars().first()
    if existing:
        if existing.title != title:
            existing.title = title
        if existing.goal != goal:
            existing.goal = goal
        return existing

    context = TaskContext(
        context_type=context_type,
        owner_type=owner_type,
        owner_id=owner_id,
        title=title,
        goal=goal,
        status=ContextStatus.ACTIVE.value,
        priority=priority,
        extra={},
    )
    db.add(context)
    await db.flush()
    return context


async def create_context_artifact(
    db: AsyncSession,
    *,
    context: TaskContext,
    task: Task | None,
    artifact_type: str,
    title: str,
    summary: str,
    payload: dict[str, Any],
    created_by: str = "system",
) -> TaskArtifact:
    artifact = TaskArtifact(
        context_id=context.id,
        task_id=task.id if task else None,
        artifact_type=artifact_type,
        version=1,
        parent_version=None,
        title=title,
        summary=summary,
        storage_ref="inline://metadata",
        content_ref="",
        created_by=created_by,
        extra=payload,
    )
    db.add(artifact)
    await db.flush()
    return artifact


async def record_context_event(
    db: AsyncSession,
    *,
    context: TaskContext,
    task: Task | None,
    event_type: str,
    action: str,
    result: str,
    reason: str,
    payload: dict[str, Any],
    performed_by: str = "system",
) -> TaskHistory:
    history = TaskHistory(
        task_id=task.id if task else None,
        context_id=context.id,
        event_type=event_type,
        action=action,
        result=result,
        from_status=None,
        to_status=task.status if task else None,
        reason=reason,
        details=payload,
        payload=payload,
        performed_by=performed_by,
    )
    db.add(history)
    await db.flush()
    return history


def build_context_task_defaults(
    *,
    context: TaskContext,
    task_type: str = TaskType.DAEMON.value,
    assigned_brain: str = "evolution-chief-brain",
) -> dict[str, Any]:
    return {
        "context_id": str(context.id),
        "task_type": task_type,
        "goal": context.goal,
        "assigned_brain": assigned_brain,
    }
