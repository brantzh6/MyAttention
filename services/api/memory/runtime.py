from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import ProceduralMemory, Task, TaskContext, TaskMemory


async def record_task_memory(
    db: AsyncSession,
    *,
    context: TaskContext,
    task: Task | None,
    memory_kind: str,
    title: str,
    summary: str,
    content: str,
    payload: dict[str, Any],
    created_by: str = "system",
) -> TaskMemory:
    memory = TaskMemory(
        context_id=context.id,
        task_id=task.id if task else None,
        memory_kind=memory_kind,
        title=title,
        summary=summary,
        content=content,
        created_by=created_by,
        extra=payload,
    )
    db.add(memory)
    await db.flush()
    return memory


async def upsert_procedural_memory(
    db: AsyncSession,
    *,
    memory_key: str,
    name: str,
    problem_type: str,
    thinking_framework: str,
    method_name: str,
    applicability: str,
    procedure: str,
    effectiveness_score: float,
    validation_status: str,
    source_kind: str,
    source_ref: str,
    payload: dict[str, Any],
) -> ProceduralMemory:
    result = await db.execute(
        select(ProceduralMemory).where(ProceduralMemory.memory_key == memory_key)
    )
    existing = result.scalars().first()
    if existing:
        existing.name = name
        existing.problem_type = problem_type
        existing.thinking_framework = thinking_framework
        existing.method_name = method_name
        existing.applicability = applicability
        existing.procedure = procedure
        existing.effectiveness_score = effectiveness_score
        existing.validation_status = validation_status
        existing.source_kind = source_kind
        existing.source_ref = source_ref
        existing.last_validated_at = datetime.now(timezone.utc)
        existing.extra = payload
        return existing

    memory = ProceduralMemory(
        memory_key=memory_key,
        name=name,
        problem_type=problem_type,
        thinking_framework=thinking_framework,
        method_name=method_name,
        applicability=applicability,
        procedure=procedure,
        effectiveness_score=effectiveness_score,
        validation_status=validation_status,
        source_kind=source_kind,
        source_ref=source_ref,
        last_validated_at=datetime.now(timezone.utc),
        extra=payload,
    )
    db.add(memory)
    await db.flush()
    return memory
