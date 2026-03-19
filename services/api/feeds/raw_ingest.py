import gzip
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from db.models import RawIngest
from storage import get_object_store


@dataclass
class RawIngestResult:
    record: RawIngest
    created: bool


_OBJECT_COMPONENT_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def _safe_object_component(value: str, fallback: str, max_length: int) -> str:
    cleaned = _OBJECT_COMPONENT_PATTERN.sub("_", (value or "").strip())
    cleaned = cleaned.strip("._-")
    if not cleaned:
        return fallback
    return cleaned[:max_length]


def build_raw_object_key(source_key: str, fetched_at: datetime, external_id: str, suffix: str = "json.gz") -> str:
    safe_source = _safe_object_component(source_key or "_imported", "_imported", 64)
    identifier_source = external_id or str(uuid4())
    identifier_hash = hashlib.sha256(identifier_source.encode("utf-8")).hexdigest()[:24]
    safe_external = _safe_object_component(external_id or "", "item", 32)
    return (
        f"raw/{safe_source}/{fetched_at:%Y}/{fetched_at:%m}/{fetched_at:%d}/"
        f"{safe_external}-{identifier_hash}.{suffix}"
    )


async def persist_import_item_raw(
    db: AsyncSession,
    *,
    source_key: str,
    external_id: str,
    payload: dict[str, Any],
    fetched_at: datetime | None = None,
) -> RawIngestResult:
    fetched_at = fetched_at or datetime.now(timezone.utc)
    settings = get_settings()
    storage_backend = (settings.object_store_backend or "local").strip().lower()

    existing = await db.execute(
        select(RawIngest).where(
            RawIngest.source_key == source_key,
            RawIngest.external_id == external_id,
        )
    )
    existing_record = existing.scalar_one_or_none()
    if existing_record is not None:
        return RawIngestResult(record=existing_record, created=False)

    raw_json = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    compressed = gzip.compress(raw_json)
    content_hash = hashlib.sha256(raw_json).hexdigest()
    object_key = build_raw_object_key(source_key, fetched_at, external_id)

    object_store = get_object_store()
    ref = await object_store.put_bytes(
        object_key,
        compressed,
        content_type="application/json",
        content_encoding="gzip",
    )

    record = RawIngest(
        source_key=source_key,
        external_id=external_id,
        object_key=ref.key,
        storage_backend=storage_backend,
        content_type=ref.content_type,
        content_encoding=ref.content_encoding,
        content_hash=content_hash,
        size_bytes=ref.size_bytes,
        fetched_at=fetched_at,
        access_method="import",
        proxy_used=False,
        parse_status="raw_saved",
        request_meta={},
        response_meta={"imported": True},
    )
    db.add(record)
    await db.flush()
    return RawIngestResult(record=record, created=True)
