from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import FeedItem as FeedItemModel
from db.models import Source as SourceModel
from db.models import SourceStatus as SourceStatusEnum
from db.models import SourceType as SourceTypeEnum


_IMPORT_SOURCE_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass
class FeedItemPersistResult:
    record: FeedItemModel
    source: SourceModel
    created: bool


def normalize_import_source_key(source_key: str) -> str:
    cleaned = _IMPORT_SOURCE_PATTERN.sub("_", (source_key or "").strip())
    cleaned = cleaned.strip("._-")
    return cleaned or "imported"


def build_import_source_url(source_key: str) -> str:
    return f"import://{normalize_import_source_key(source_key)}"


def map_import_source_type(source_type: str | None) -> SourceTypeEnum:
    value = (source_type or "rss").strip().lower()
    if value == SourceTypeEnum.WEB.value:
        return SourceTypeEnum.WEB
    if value == SourceTypeEnum.API.value:
        return SourceTypeEnum.API
    return SourceTypeEnum.RSS


async def resolve_source_for_import(
    db: AsyncSession,
    *,
    source_key: str,
    source_name: str,
    source_type: str,
    source_url: str,
    category: str,
    tags: list[str] | None = None,
) -> SourceModel:
    source_key = source_key or "_imported"
    source_name = source_name or source_key
    normalized_url = source_url.strip() if source_url else build_import_source_url(source_key)

    result = await db.execute(
        select(SourceModel).where(
            or_(
                SourceModel.url == normalized_url,
                SourceModel.name == source_name,
            )
        )
    )
    source = result.scalars().first()
    if source is not None:
        return source

    source = SourceModel(
        name=source_name,
        type=map_import_source_type(source_type),
        url=normalized_url,
        category=category or "",
        tags=tags or [],
        enabled=True,
        status=SourceStatusEnum.OK,
        config={
            "imported": True,
            "source_key": source_key,
            "source_type": source_type or "rss",
            "source_name": source_name,
        },
    )
    db.add(source)
    await db.flush()
    return source


def build_import_feed_extra(
    *,
    raw_ingest_id: str | None,
    source_key: str,
    source_name: str,
    source_type: str,
    category: str,
    category_name: str,
    metadata: dict[str, Any] | None,
    urgency_factors: dict[str, Any] | None,
    secondary_tags: list[str] | None,
    language: str,
) -> dict[str, Any]:
    return {
        "imported": True,
        "raw_ingest_id": raw_ingest_id,
        "source_key": source_key,
        "source_name": source_name,
        "source_type": source_type,
        "raw_category": category,
        "category_name": category_name,
        "metadata": metadata or {},
        "urgency_factors": urgency_factors or {},
        "secondary_tags": secondary_tags or [],
        "language": language,
    }


async def persist_import_feed_item(
    db: AsyncSession,
    *,
    source: SourceModel,
    external_id: str,
    title: str,
    summary: str,
    content: str,
    url: str,
    importance: float,
    published_at: datetime,
    fetched_at: datetime,
    extra: dict[str, Any],
) -> FeedItemPersistResult:
    result = await db.execute(
        select(FeedItemModel).where(
            FeedItemModel.source_id == source.id,
            FeedItemModel.external_id == external_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return FeedItemPersistResult(record=existing, source=source, created=False)

    record = FeedItemModel(
        source_id=source.id,
        external_id=external_id,
        title=title,
        summary=summary,
        content=content,
        url=url,
        importance=importance,
        published_at=published_at,
        fetched_at=fetched_at,
        extra=extra,
    )
    db.add(record)
    await db.flush()
    return FeedItemPersistResult(record=record, source=source, created=True)
