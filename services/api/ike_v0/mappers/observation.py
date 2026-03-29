"""
IKE v0 Observation Mapper

Maps existing persisted feed inputs (FeedItem, optional RawIngest) to
explicit v0 Observation objects.

This is a pure adapter layer - no DB writes, no runtime changes.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ike_v0.types.ids import generate_ike_id, IKEKind
from ike_v0.schemas.observation import Observation


def map_feed_item_to_observation(
    feed_item: Any,
    raw_ingest: Optional[Any] = None,
    signal_type: str = "feed_item",
) -> Observation:
    """
    Materialize a v0 Observation from a persisted FeedItem.

    Args:
        feed_item: FeedItem ORM object or dict-like with feed item fields
        raw_ingest: Optional RawIngest object for content reference
        signal_type: Type identifier for the signal (default: "feed_item")

    Returns:
        Observation object with v0 contract fields populated

    Mapping notes:
        - id: generated typed ID
        - source_ref: feed_item.source_id (UUID -> string)
        - raw_ref: raw_ingest.object_key if available
        - observed_at: feed_item.published_at or fetched_at
        - captured_at: feed_item.fetched_at or created_at
        - title: feed_item.title
        - summary: feed_item.summary or extracted_summary
        - content_ref: feed_item.url or raw_ingest.object_key
        - content_excerpt: feed_item.content or extracted_summary excerpt
        - signal_type: provided or default
        - confidence: derived from feed_item.importance if available
        - provenance: includes mapping metadata
        - references: includes source_ref
    """
    now = datetime.now(timezone.utc)

    # Extract fields from feed_item (handle both ORM and dict)
    if hasattr(feed_item, "__dict__"):
        fi = feed_item.__dict__
        # SQLAlchemy adds _sa_instance_state, filter it
        fi = {k: v for k, v in fi.items() if k != "_sa_instance_state"}
    else:
        fi = feed_item

    # Helper to get attribute or key
    def get_field(name: str, default=None):
        if isinstance(fi, dict):
            return fi.get(name, default)
        return getattr(feed_item, name, default)

    # Build observation ID
    obs_id = generate_ike_id(IKEKind.OBSERVATION)

    # Source reference
    source_id = get_field("source_id")
    source_ref = str(source_id) if source_id else "unknown"

    # Raw reference
    raw_ref = None
    if raw_ingest is not None:
        if hasattr(raw_ingest, "object_key"):
            raw_ref = raw_ingest.object_key
        elif isinstance(raw_ingest, dict) and "object_key" in raw_ingest:
            raw_ref = raw_ingest.get("object_key")

    # Timestamps
    observed_at = get_field("published_at") or get_field("fetched_at") or now
    captured_at = get_field("fetched_at") or get_field("created_at") or now

    # Ensure timezone awareness
    if observed_at and observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=timezone.utc)
    if captured_at and captured_at.tzinfo is None:
        captured_at = captured_at.replace(tzinfo=timezone.utc)

    # Content fields
    title = get_field("title", "Untitled Observation")
    summary = get_field("summary") or get_field("extracted_summary", "")
    content_ref = get_field("url") or (raw_ref if raw_ref else None)
    content_excerpt = get_field("content") or get_field("extracted_summary")

    # Confidence from importance
    importance = get_field("importance")
    confidence = float(importance) if importance is not None else 0.5
    confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]

    # Provenance
    provenance: Dict[str, Any] = {
        "mapper": "map_feed_item_to_observation",
        "source_type": signal_type,
    }
    extra = get_field("extra") or get_field("metadata")
    if extra:
        provenance["feed_extra"] = extra

    # References
    references = [source_ref] if source_ref else []
    if raw_ref:
        references.append(raw_ref)

    return Observation(
        id=obs_id,
        kind="observation",
        version="v0.1.0",
        status="draft",
        created_at=now,
        updated_at=now,
        provenance=provenance,
        confidence=confidence,
        references=references,
        source_ref=source_ref,
        raw_ref=raw_ref,
        observed_at=observed_at,
        captured_at=captured_at,
        title=title,
        summary=summary,
        content_ref=content_ref,
        content_excerpt=content_excerpt,
        signal_type=signal_type,
    )
