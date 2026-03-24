from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from brains.control_plane import ensure_brain_control_plane, list_brain_profiles, list_brain_routes
from db import BrainProfile, BrainRoute, get_db

router = APIRouter()


class BrainProfileResponse(BaseModel):
    brain_id: str
    role: str
    description: str | None
    capabilities: list[str]
    default_models: list[str]
    fallback_models: list[str]
    tool_policy: dict[str, Any]
    cost_policy: dict[str, Any]
    latency_policy: dict[str, Any]
    risk_policy: dict[str, Any]
    status: str
    version: int


class BrainRouteResponse(BaseModel):
    route_id: str
    problem_type: str
    thinking_framework: str
    primary_brain: str
    supporting_brains: list[str]
    review_brain: str | None
    fallback_brain: str | None
    enabled: bool
    version: int
    extra: dict[str, Any]


class BrainControlPlaneResponse(BaseModel):
    bootstrap: dict[str, int]
    profiles: list[BrainProfileResponse]
    routes: list[BrainRouteResponse]


def _profile_to_response(profile: BrainProfile) -> BrainProfileResponse:
    return BrainProfileResponse(
        brain_id=profile.brain_id,
        role=profile.role,
        description=profile.description,
        capabilities=list(profile.capabilities or []),
        default_models=list(profile.default_models or []),
        fallback_models=list(profile.fallback_models or []),
        tool_policy=dict(profile.tool_policy or {}),
        cost_policy=dict(profile.cost_policy or {}),
        latency_policy=dict(profile.latency_policy or {}),
        risk_policy=dict(profile.risk_policy or {}),
        status=profile.status,
        version=profile.version,
    )


def _route_to_response(route: BrainRoute) -> BrainRouteResponse:
    return BrainRouteResponse(
        route_id=route.route_id,
        problem_type=route.problem_type,
        thinking_framework=route.thinking_framework,
        primary_brain=route.primary_brain.brain_id,
        supporting_brains=list(route.supporting_brains or []),
        review_brain=route.review_brain.brain_id if route.review_brain else None,
        fallback_brain=route.fallback_brain.brain_id if route.fallback_brain else None,
        enabled=route.enabled,
        version=route.version,
        extra=dict(route.extra or {}),
    )


@router.get("/control-plane", response_model=BrainControlPlaneResponse)
async def get_brain_control_plane(
    db: AsyncSession = Depends(get_db),
):
    bootstrap = await ensure_brain_control_plane(db)
    profiles = await list_brain_profiles(db)
    routes = await list_brain_routes(db)
    return BrainControlPlaneResponse(
        bootstrap=bootstrap,
        profiles=[_profile_to_response(item) for item in profiles],
        routes=[_route_to_response(item) for item in routes],
    )
