from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from db.models import FeedItem, RawIngest


def _to_iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _age_hours(now: datetime, value: datetime | None) -> float | None:
    if value is None:
        return None
    return round(max(0.0, (now - value).total_seconds() / 3600), 2)


def summarize_collection_health(snapshot: dict[str, Any]) -> dict[str, Any]:
    counts = snapshot["counts"]
    freshness = snapshot["freshness"]
    ratios = snapshot["ratios"]

    total_raw = counts["raw_ingest_total"]
    total_items = counts["feed_items_total"]
    raw_24h = counts["raw_ingest_24h"]
    raw_1h = counts["raw_ingest_1h"]
    feed_24h = counts["feed_items_24h"]
    errors_24h = counts["raw_errors_24h"]
    durable_24h = counts["raw_durable_24h"]
    pending_1h = counts["raw_pending_1h"]
    durable_ratio = ratios["durable_ratio_24h"]
    last_raw_age = freshness["last_raw_ingest_age_hours"]

    if total_raw == 0 and total_items == 0:
        return {
            "status": "healthy",
            "state": "idle",
            "message": "No collection history yet.",
        }

    if raw_24h > 0 and durable_24h == 0 and feed_24h == 0:
        return {
            "status": "unhealthy",
            "state": "write_blocked",
            "message": "Raw items were collected but no durable downstream result was recorded.",
        }

    if raw_1h >= 5 and pending_1h >= max(3, raw_1h // 2):
        return {
            "status": "degraded",
            "state": "backlog",
            "message": "Collection is active, but too many raw items are still unresolved.",
        }

    if errors_24h >= 3 and raw_24h > 0 and errors_24h >= max(3, raw_24h // 2):
        return {
            "status": "degraded",
            "state": "high_error_rate",
            "message": "Recent collection has a high raw ingest error rate.",
        }

    if last_raw_age is not None and last_raw_age > 24:
        return {
            "status": "degraded",
            "state": "stalled",
            "message": "Collection history exists, but no new raw ingest has arrived in the last 24 hours.",
        }

    return {
        "status": "healthy",
        "state": "active",
        "message": "Collection pipeline is active and persisting data.",
    }


def build_collection_health_issue(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    summary = snapshot.get("summary") or {}
    status = summary.get("status", "healthy")
    if status == "healthy":
        return None

    counts = snapshot.get("counts") or {}
    priority = 1 if status == "unhealthy" else 2
    severity = "critical" if status == "unhealthy" else "warning"
    state = summary.get("state", "unknown")
    pending_sources = snapshot.get("pending_sources_1h") or []
    error_sources = snapshot.get("error_sources_24h") or []
    title = f"Feed collection health degraded: {state}"
    source_summary_parts: list[str] = []
    if pending_sources:
        source_summary_parts.append(
            "pending_sources="
            + ", ".join(f"{item['source_key']}({item['pending_count']})" for item in pending_sources[:5])
        )
    if error_sources:
        source_summary_parts.append(
            "error_sources="
            + ", ".join(f"{item['source_key']}({item['error_count']})" for item in error_sources[:5])
        )
    description = (
        f"{summary.get('message', 'Collection health issue detected.')}\n"
        f"raw_ingest_1h={counts.get('raw_ingest_1h', 0)}, "
        f"raw_durable_24h={counts.get('raw_durable_24h', 0)}, "
        f"raw_pending_1h={counts.get('raw_pending_1h', 0)}, "
        f"raw_errors_24h={counts.get('raw_errors_24h', 0)}"
    )
    if source_summary_parts:
        description = f"{description}\n" + " | ".join(source_summary_parts)
    return {
        "priority": priority,
        "severity": severity,
        "title": title,
        "description": description,
        "source_type": "system_health",
        "source_id": "feed_collection",
        "category": "quality",
        "auto_processible": True,
        "source_data": {
            "type": "feed_collection_health",
            "task_type": f"system_health_{status}",
            "status": status,
            "state": state,
            "summary": summary,
            "pending_sources_1h": pending_sources,
            "error_sources_24h": error_sources,
            "snapshot": snapshot,
        },
    }


async def collect_collection_health_snapshot(
    db: AsyncSession,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    last_hour = now - timedelta(hours=1)
    last_day = now - timedelta(hours=24)

    raw_total = await db.scalar(select(func.count()).select_from(RawIngest)) or 0
    feed_total = await db.scalar(select(func.count()).select_from(FeedItem)) or 0

    raw_1h = await db.scalar(
        select(func.count()).select_from(RawIngest).where(RawIngest.fetched_at >= last_hour)
    ) or 0
    raw_24h = await db.scalar(
        select(func.count()).select_from(RawIngest).where(RawIngest.fetched_at >= last_day)
    ) or 0
    raw_pending_1h = await db.scalar(
        select(func.count()).select_from(RawIngest).where(
            RawIngest.fetched_at >= last_hour,
            RawIngest.parse_status.in_(["pending", "raw_saved"]),
        )
    ) or 0
    feed_1h = await db.scalar(
        select(func.count()).select_from(FeedItem).where(FeedItem.fetched_at >= last_hour)
    ) or 0
    feed_24h = await db.scalar(
        select(func.count()).select_from(FeedItem).where(FeedItem.fetched_at >= last_day)
    ) or 0
    raw_errors_24h = await db.scalar(
        select(func.count()).select_from(RawIngest).where(
            RawIngest.fetched_at >= last_day,
            or_(
                RawIngest.error_message.is_not(None),
                RawIngest.parse_status.in_(["error", "failed"]),
            ),
        )
    ) or 0
    raw_durable_24h = await db.scalar(
        select(func.count()).select_from(RawIngest).where(
            RawIngest.fetched_at >= last_day,
            RawIngest.parse_status.in_(["persisted", "duplicate"]),
        )
    ) or 0
    raw_duplicate_24h = await db.scalar(
        select(func.count()).select_from(RawIngest).where(
            RawIngest.fetched_at >= last_day,
            RawIngest.parse_status == "duplicate",
        )
    ) or 0
    raw_pending_24h = await db.scalar(
        select(func.count()).select_from(RawIngest).where(
            RawIngest.fetched_at >= last_day,
            RawIngest.parse_status.in_(["pending", "raw_saved"]),
        )
    ) or 0
    active_sources_24h = await db.scalar(
        select(func.count(func.distinct(RawIngest.source_key))).where(RawIngest.fetched_at >= last_day)
    ) or 0

    last_raw_ingest = await db.scalar(select(func.max(RawIngest.fetched_at)))
    last_feed_item = await db.scalar(select(func.max(FeedItem.fetched_at)))

    top_sources_result = await db.execute(
        select(
            RawIngest.source_key,
            func.count().label("raw_count"),
            func.max(RawIngest.fetched_at).label("last_seen"),
        )
        .where(RawIngest.fetched_at >= last_day)
        .group_by(RawIngest.source_key)
        .order_by(desc("raw_count"), desc("last_seen"))
        .limit(5)
    )

    top_sources = [
        {
            "source_key": row.source_key,
            "raw_count": int(row.raw_count or 0),
            "last_seen": _to_iso(row.last_seen),
        }
        for row in top_sources_result
    ]

    pending_sources_result = await db.execute(
        select(
            RawIngest.source_key,
            func.count().label("pending_count"),
            func.max(RawIngest.fetched_at).label("last_seen"),
        )
        .where(
            RawIngest.fetched_at >= last_hour,
            RawIngest.parse_status.in_(["pending", "raw_saved"]),
        )
        .group_by(RawIngest.source_key)
        .order_by(desc("pending_count"), desc("last_seen"))
        .limit(5)
    )
    pending_sources_1h = [
        {
            "source_key": row.source_key,
            "pending_count": int(row.pending_count or 0),
            "last_seen": _to_iso(row.last_seen),
        }
        for row in pending_sources_result
    ]

    error_sources_result = await db.execute(
        select(
            RawIngest.source_key,
            func.count().label("error_count"),
            func.max(RawIngest.fetched_at).label("last_seen"),
        )
        .where(
            RawIngest.fetched_at >= last_day,
            or_(
                RawIngest.error_message.is_not(None),
                RawIngest.parse_status.in_(["error", "failed"]),
            ),
        )
        .group_by(RawIngest.source_key)
        .order_by(desc("error_count"), desc("last_seen"))
        .limit(5)
    )
    error_sources_24h = [
        {
            "source_key": row.source_key,
            "error_count": int(row.error_count or 0),
            "last_seen": _to_iso(row.last_seen),
        }
        for row in error_sources_result
    ]

    durable_ratio_24h = round((raw_durable_24h / raw_24h), 3) if raw_24h else 1.0
    persist_ratio_24h = round((feed_24h / raw_24h), 3) if raw_24h else 1.0

    snapshot = {
        "timestamp": now.isoformat(),
        "storage": {
            "object_store_backend": get_settings().object_store_backend,
            "feeds_read_backend": getattr(get_settings(), "feeds_read_backend", "hybrid"),
        },
        "counts": {
            "raw_ingest_total": int(raw_total),
            "feed_items_total": int(feed_total),
            "raw_ingest_1h": int(raw_1h),
            "raw_ingest_24h": int(raw_24h),
            "feed_items_1h": int(feed_1h),
            "feed_items_24h": int(feed_24h),
            "raw_errors_24h": int(raw_errors_24h),
            "raw_durable_24h": int(raw_durable_24h),
            "raw_duplicate_24h": int(raw_duplicate_24h),
            "raw_pending_1h": int(raw_pending_1h),
            "raw_pending_24h": int(raw_pending_24h),
            "active_sources_24h": int(active_sources_24h),
        },
        "freshness": {
            "last_raw_ingest_at": _to_iso(last_raw_ingest),
            "last_feed_item_at": _to_iso(last_feed_item),
            "last_raw_ingest_age_hours": _age_hours(now, last_raw_ingest),
            "last_feed_item_age_hours": _age_hours(now, last_feed_item),
        },
        "ratios": {
            "durable_ratio_24h": durable_ratio_24h,
            "persist_ratio_24h": persist_ratio_24h,
        },
        "top_sources_24h": top_sources,
        "pending_sources_1h": pending_sources_1h,
        "error_sources_24h": error_sources_24h,
    }
    snapshot["summary"] = summarize_collection_health(snapshot)
    return snapshot
