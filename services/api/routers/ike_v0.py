"""
IKE v0 Preview API Router

Transitional preview-style endpoints for IKE v0 objects.
These endpoints expose provisional/experimental objects without implying durable storage.

See: docs/IKE_API_TRANSITION_PRINCIPLES.md
"""

from dataclasses import asdict
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
from runtime.project_surface import (
    bootstrap_runtime_project_surface,
    build_latest_project_runtime_read_surface,
)
from runtime.benchmark_bridge import (
    BenchmarkBridgeError,
    import_benchmark_candidate_into_runtime_project,
)
from runtime.service_preflight import run_preflight


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


class RuntimeProjectSurfaceInspectRequest(BaseModel):
    """Request model for narrow runtime project surface inspection."""
    project_key: Optional[str] = None


class RuntimeProjectSurfaceBootstrapRequest(BaseModel):
    """Request model for explicit runtime project bootstrap."""
    project_key: str
    title: str
    current_phase: Optional[str] = None
    priority: int = 1


class RuntimeBenchmarkCandidateImportRequest(BaseModel):
    """Request model for explicit visible-surface to runtime review bridge."""
    project_key: str
    candidate_payload: Dict[str, Any]


class RuntimeServicePreflightInspectRequest(BaseModel):
    """Request model for runtime service preflight inspection."""
    host: Optional[str] = None
    port: Optional[int] = None
    strict_preferred_owner: bool = False
    expected_code_fingerprint: Optional[str] = None
    strict_code_freshness: bool = False


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


class RuntimeProjectSurfaceInspectResponse(BaseModel):
    """Response model for runtime project surface inspection."""
    ref: ObjectRef
    data: Dict[str, Any]


class RuntimeBenchmarkCandidateImportResponse(BaseModel):
    """Response model for benchmark candidate bridge import."""
    ref: ObjectRef
    data: Dict[str, Any]


class RuntimeServicePreflightInspectResponse(BaseModel):
    """Response model for runtime service preflight inspection."""
    ref: ObjectRef
    data: Dict[str, Any]


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


@router.post("/runtime/project-surface/inspect", response_model=RuntimeProjectSurfaceInspectResponse)
async def inspect_runtime_project_surface(
    request: RuntimeProjectSurfaceInspectRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Inspect one narrow runtime-backed project surface for visible integration.

    This remains inspect-style and experimental. It does not imply a broad
    runtime API or durable public retrieval contract.
    """
    surface = await db.run_sync(
        lambda sync_session: build_latest_project_runtime_read_surface(
            sync_session,
            project_key=request.project_key,
        )
    )
    if surface is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Runtime project surface not available. "
                "No runtime project currently exists for the requested key."
            ),
        )

    response.headers["X-IKE-Version"] = "v0-experimental"
    response.headers["Cache-Control"] = "no-store"

    return RuntimeProjectSurfaceInspectResponse(
        ref=ObjectRef(
            id=f"runtime_project_surface:{surface.project_id}",
            kind="runtime_project_surface",
            id_scope="provisional",
            stability="experimental",
            permalink=None,
        ),
        data=asdict(surface),
    )


@router.post("/runtime/project-surface/bootstrap", response_model=RuntimeProjectSurfaceInspectResponse)
async def bootstrap_runtime_project_surface_endpoint(
    request: RuntimeProjectSurfaceBootstrapRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Explicitly bootstrap one runtime project presence path for the visible surface.
    """
    surface = await db.run_sync(
        lambda sync_session: bootstrap_runtime_project_surface(
            sync_session,
            project_key=request.project_key,
            title=request.title,
            current_phase=request.current_phase,
            priority=request.priority,
        )
    )

    response.headers["X-IKE-Version"] = "v0-experimental"
    response.headers["Cache-Control"] = "no-store"

    return RuntimeProjectSurfaceInspectResponse(
        ref=ObjectRef(
            id=f"runtime_project_surface:{surface.project_id}",
            kind="runtime_project_surface",
            id_scope="provisional",
            stability="experimental",
            permalink=None,
        ),
        data=asdict(surface),
    )


@router.post(
    "/runtime/benchmark-candidate/import",
    response_model=RuntimeBenchmarkCandidateImportResponse,
)
async def import_runtime_benchmark_candidate_endpoint(
    request: RuntimeBenchmarkCandidateImportRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Explicitly import one reviewed benchmark candidate into runtime pending_review.

    This endpoint remains narrow:
    - requires an existing runtime project
    - imports only reviewed benchmark candidate payloads
    - does not promote the packet to accepted/trusted memory
    """
    try:
        packet = await db.run_sync(
            lambda sync_session: import_benchmark_candidate_into_runtime_project(
                sync_session,
                request.project_key,
                request.candidate_payload,
            )
        )
    except BenchmarkBridgeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    response.headers["X-IKE-Version"] = "v0-experimental"
    response.headers["Cache-Control"] = "no-store"

    return RuntimeBenchmarkCandidateImportResponse(
        ref=ObjectRef(
            id=f"runtime_memory_packet:{packet.memory_packet_id}",
            kind="runtime_memory_packet",
            id_scope="provisional",
            stability="experimental",
            permalink=None,
        ),
        data={
            "memory_packet_id": str(packet.memory_packet_id),
            "project_id": str(packet.project_id),
            "packet_type": packet.packet_type,
            "status": packet.status.value if hasattr(packet.status, "value") else str(packet.status),
            "title": packet.title,
            "summary": packet.summary,
            "created_by_kind": packet.created_by_kind.value if hasattr(packet.created_by_kind, "value") else str(packet.created_by_kind),
            "created_by_id": packet.created_by_id,
            "storage_ref": packet.storage_ref,
        },
    )


@router.post(
    "/runtime/service-preflight/inspect",
    response_model=RuntimeServicePreflightInspectResponse,
)
async def inspect_runtime_service_preflight(
    response: Response,
    request: RuntimeServicePreflightInspectRequest | None = None,
):
    """
    Inspect one narrow runtime service preflight result for live-proof discipline.

    This endpoint is operational and inspect-style only.
    It does not imply a broad service-management API.
    """
    result = await run_preflight(
        host=request.host if request and request.host else "127.0.0.1",
        port=request.port if request and request.port else 8000,
        strict_preferred_owner=request.strict_preferred_owner if request else False,
        expected_code_fingerprint=request.expected_code_fingerprint if request else None,
        strict_code_freshness=request.strict_code_freshness if request else False,
    )

    response.headers["X-IKE-Version"] = "v0-experimental"
    response.headers["Cache-Control"] = "no-store"

    return RuntimeServicePreflightInspectResponse(
        ref=ObjectRef(
            id=f"runtime_service_preflight:{result.timestamp}",
            kind="runtime_service_preflight",
            id_scope="provisional",
            stability="experimental",
            permalink=None,
        ),
        data={
            "status": result.status.value if hasattr(result.status, "value") else str(result.status),
            "timestamp": result.timestamp,
            "api_health": {
                "endpoint": result.api_health.endpoint,
                "is_healthy": result.api_health.is_healthy,
                "response_status": result.api_health.response_status,
                "response_body": result.api_health.response_body,
                "response_time_ms": result.api_health.response_time_ms,
                "error_message": result.api_health.error_message,
            },
            "port_ownership": {
                "port": result.port_ownership.port,
                "listening_processes": result.port_ownership.listening_processes,
                "unique_count": result.port_ownership.unique_count,
                "is_clear": result.port_ownership.is_clear,
                "inspection_method": result.port_ownership.inspection_method,
                "inspection_error": result.port_ownership.inspection_error,
            },
              "summary": result.summary,
              "details": result.details,
              "owner_chain": result.details.get("owner_chain"),
              "repo_launcher": result.details.get("repo_launcher"),
              "controller_acceptability": result.details.get("controller_acceptability"),
          },
      )
