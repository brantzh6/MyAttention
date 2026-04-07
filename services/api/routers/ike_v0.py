"""
IKE v0 Preview API Router

Transitional preview-style endpoints for IKE v0 objects.
These endpoints expose provisional/experimental objects without implying durable storage.

See: docs/IKE_API_TRANSITION_PRINCIPLES.md
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from db.models import TaskArtifact
from ike_v0.mappers.decision import create_experiment_evaluation_decision
from ike_v0.mappers.harness_case import create_loop_completeness_harness_case
from ike_v0.mappers.observation import map_feed_item_to_observation
from ike_v0.runtime.chain_artifact import ChainArtifact, assemble_chain_artifact, ARTIFACT_TYPE_IKE_CHAIN


def _parse_iso_datetime(value):
    """
    Parse ISO format datetime string to timezone-aware datetime.
    Returns the value unchanged if it's already a datetime.
    Returns None if value is None.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    if isinstance(value, str):
        # Handle ISO format with Z suffix
        if value.endswith('Z'):
            value = value[:-1] + '+00:00'
        try:
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            return None
    return None


router = APIRouter(prefix="/ike/v0", tags=["ike-v0"])


# =============================================================================
# Request Models
# =============================================================================


class DecisionPreviewRequest(BaseModel):
    """
    Request model for Decision preview endpoint.

    Thin wrapper around create_experiment_evaluation_decision arguments.
    """
    task_ref: str
    experiment_refs: List[str]
    decision_outcome: Literal["adopt", "reject", "defer", "escalate"]
    rationale: str
    review_required: bool = False
    evidence_refs: Optional[List[str]] = None


class HarnessCasePreviewRequest(BaseModel):
    """
    Request model for HarnessCase preview endpoint.

    Thin wrapper around create_loop_completeness_harness_case arguments.
    """
    subject_refs: List[str]
    expected_behavior: Dict[str, Any]
    actual_behavior: Dict[str, Any]
    pass_fail: bool
    notes: Optional[str] = None
    evidence_refs: Optional[List[str]] = None


class ObservationInspectRequest(BaseModel):
    """
    Request model for Observation inspection endpoint.

    Thin wrapper around map_feed_item_to_observation arguments.
    Accepts dict-shaped feed_item for bounded inspection.
    """
    feed_item: Dict[str, Any]
    raw_ingest: Optional[Dict[str, Any]] = None
    signal_type: str = "feed_item"


class ChainInspectRequest(BaseModel):
    """
    Request model for IKE v0.1 chain inspection endpoint.

    Accepts artifact_id to lookup a stored chain artifact from TaskArtifact substrate.
    This is a transitional inspect-style endpoint, not durable GET retrieval.
    """
    artifact_id: str


# =============================================================================
# Response Envelope
# =============================================================================


class ObjectRef(BaseModel):
    """
    Reference metadata for provisional IKE v0 objects.
    """
    id: str
    kind: str
    id_scope: str = "provisional"
    stability: str = "experimental"
    permalink: Optional[str] = None


class PreviewResponse(BaseModel):
    """
    Transitional response envelope for IKE v0 preview endpoints.

    Explicitly marks objects as provisional/experimental.
    """
    ref: ObjectRef
    data: Dict[str, Any]


# =============================================================================
# Preview Endpoints
# =============================================================================


@router.post("/decisions/preview", response_model=PreviewResponse)
async def preview_decision(request: DecisionPreviewRequest, response: Response):
    """
    Generate a provisional Decision object.

    Uses the bounded create_experiment_evaluation_decision helper.
    Does not persist - returns a transient object for inspection.

    Response headers:
        X-IKE-Version: v0-experimental
        Cache-Control: no-store
    """
    # Create decision using existing mapper
    decision = create_experiment_evaluation_decision(
        task_ref=request.task_ref,
        experiment_refs=request.experiment_refs,
        decision_outcome=request.decision_outcome,
        rationale=request.rationale,
        review_required=request.review_required,
        evidence_refs=request.evidence_refs,
    )

    # Set transitional response headers
    response.headers["X-IKE-Version"] = "v0-experimental"
    response.headers["Cache-Control"] = "no-store"

    # Build response envelope
    return PreviewResponse(
        ref=ObjectRef(
            id=decision.id,
            kind=decision.kind,
            id_scope="provisional",
            stability="experimental",
            permalink=None,
        ),
        data=decision.model_dump(mode="json"),
    )


@router.post("/harness-cases/preview", response_model=PreviewResponse)
async def preview_harness_case(request: HarnessCasePreviewRequest, response: Response):
    """
    Generate a provisional HarnessCase object.

    Uses the bounded create_loop_completeness_harness_case helper.
    Does not persist - returns a transient object for inspection.

    Response headers:
        X-IKE-Version: v0-experimental
        Cache-Control: no-store
    """
    # Create harness case using existing mapper
    harness_case = create_loop_completeness_harness_case(
        subject_refs=request.subject_refs,
        expected_behavior=request.expected_behavior,
        actual_behavior=request.actual_behavior,
        pass_fail=request.pass_fail,
        notes=request.notes,
        evidence_refs=request.evidence_refs,
    )

    # Set transitional response headers
    response.headers["X-IKE-Version"] = "v0-experimental"
    response.headers["Cache-Control"] = "no-store"

    # Build response envelope
    return PreviewResponse(
        ref=ObjectRef(
            id=harness_case.id,
            kind=harness_case.kind,
            id_scope="provisional",
            stability="experimental",
            permalink=None,
        ),
        data=harness_case.model_dump(mode="json"),
    )


@router.post("/observations/inspect", response_model=PreviewResponse)
async def inspect_observation(request: ObservationInspectRequest, response: Response):
    """
    Materialize a provisional Observation from a feed_item.

    Uses the bounded map_feed_item_to_observation helper.
    Does not persist - returns a transient object for inspection.

    Response headers:
        X-IKE-Version: v0-experimental
        Cache-Control: no-store
    """
    # Normalize timestamps in feed_item before passing to mapper
    # This keeps timestamp parsing in the router layer, not the mapper
    feed_item = dict(request.feed_item)  # Copy to avoid mutating request
    for ts_field in ["published_at", "fetched_at", "created_at"]:
        if ts_field in feed_item:
            feed_item[ts_field] = _parse_iso_datetime(feed_item[ts_field])
    
    # Normalize timestamps in raw_ingest if present
    raw_ingest = dict(request.raw_ingest) if request.raw_ingest else None
    if raw_ingest and "created_at" in raw_ingest:
        raw_ingest["created_at"] = _parse_iso_datetime(raw_ingest["created_at"])

    # Create observation using existing mapper
    observation = map_feed_item_to_observation(
        feed_item=feed_item,
        raw_ingest=raw_ingest,
        signal_type=request.signal_type,
    )

    # Set transitional response headers
    response.headers["X-IKE-Version"] = "v0-experimental"
    response.headers["Cache-Control"] = "no-store"

    # Build response envelope
    return PreviewResponse(
        ref=ObjectRef(
            id=observation.id,
            kind=observation.kind,
            id_scope="provisional",
            stability="experimental",
            permalink=None,
        ),
        data=observation.model_dump(mode="json"),
    )


class ChainInspectResponse(BaseModel):
    """
    Response model for chain inspection endpoint.

    Returns the chain artifact with completeness summary.
    """
    ref: ObjectRef
    data: Dict[str, Any]
    completeness: Dict[str, Any]


async def _lookup_chain_artifact_from_substrate(db: AsyncSession, artifact_id: str) -> Optional[Dict[str, Any]]:
    """
    Lookup a chain artifact from the TaskArtifact substrate.

    Queries the TaskArtifact table by artifact_id and filters by
    artifact_type == 'ike_v0_chain'.

    Args:
        db: Async database session
        artifact_id: The TaskArtifact UUID to lookup

    Returns:
        The chain payload dict from TaskArtifact.extra, or None if not found
    """
    result = await db.execute(
        select(TaskArtifact).where(
            TaskArtifact.id == artifact_id,
            TaskArtifact.artifact_type == ARTIFACT_TYPE_IKE_CHAIN,
        )
    )
    artifact = result.scalar_one_or_none()
    return artifact.extra if artifact else None


@router.post("/chains/inspect", response_model=ChainInspectResponse)
async def inspect_chain(
    request: ChainInspectRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Inspect one IKE v0.1 loop chain artifact from TaskArtifact substrate.

    This endpoint looks up a stored chain artifact by artifact_id and
    returns it in a transitional provisional envelope with completeness summary.

    This is an inspect-style endpoint, not durable GET retrieval.
    The chain is read from TaskArtifact substrate, not assembled inline.

    Response headers:
        X-IKE-Version: v0-experimental
        Cache-Control: no-store
    """
    # Lookup chain artifact from TaskArtifact substrate
    chain_payload = await _lookup_chain_artifact_from_substrate(db, request.artifact_id)

    if chain_payload is None:
        raise HTTPException(
            status_code=404,
            detail=f"Chain artifact not found: {request.artifact_id}. "
                   "Chain artifacts are stored in TaskArtifact substrate with type 'ike_v0_chain'."
        )

    # Set transitional response headers
    response.headers["X-IKE-Version"] = "v0-experimental"
    response.headers["Cache-Control"] = "no-store"

    # Build response from stored payload
    # The payload already contains the serialized chain data
    chain_id = chain_payload.get("chain_id", request.artifact_id)

    return ChainInspectResponse(
        ref=ObjectRef(
            id=chain_id,
            kind="ike_chain",
            id_scope="provisional",
            stability="experimental",
            permalink=None,
        ),
        data=chain_payload,
        completeness={
            "chain_id": chain_id,
            "is_complete": chain_payload.get("is_complete", False),
            "objects": chain_payload.get("objects", {}),
            "object_count": len([v for v in chain_payload.get("objects", {}).values() if v]),
        },
    )
