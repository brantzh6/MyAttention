from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db import BrainFallback, BrainPolicy, BrainProfile, BrainRole, BrainRoute
from llm.voting import MultiModelVoting


@dataclass(frozen=True)
class BrainProfileSpec:
    brain_id: str
    role: str
    description: str
    capabilities: list[str]
    default_models: list[str]
    fallback_models: list[str]
    tool_policy: dict[str, Any]
    cost_policy: dict[str, Any]
    latency_policy: dict[str, Any]
    risk_policy: dict[str, Any]
    status: str = "active"
    version: int = 1


@dataclass(frozen=True)
class BrainRouteSpec:
    route_id: str
    problem_type: str
    thinking_framework: str
    primary_brain: str
    supporting_brains: list[str]
    review_brain: str | None
    fallback_brain: str | None
    version: int = 1
    enabled: bool = True
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class BrainExecutionPlan:
    route_id: str
    problem_type: str
    thinking_framework: str
    primary_brain: str
    supporting_brains: list[str]
    review_brain: str | None
    fallback_brain: str | None
    primary_models: list[str]
    supporting_models: list[str]
    selected_models: list[str]
    execution_mode: str
    surface: str | None


DEFAULT_BRAIN_PROFILES: tuple[BrainProfileSpec, ...] = (
    BrainProfileSpec(
        brain_id="brainstem-controller",
        role=BrainRole.SYSTEM.value,
        description="Keeps the system alive through guardrails, health checks, and safe degradation.",
        capabilities=["health-check", "fallback", "service-recovery"],
        default_models=[],
        fallback_models=[],
        tool_policy={"network": "limited", "write": "safe-only"},
        cost_policy={"budget": "minimal"},
        latency_policy={"target_ms": 2000},
        risk_policy={"auto_execute": True, "require_review_for_write": True},
    ),
    BrainProfileSpec(
        brain_id="chief-brain",
        role=BrainRole.CHIEF.value,
        description="Frames problems, selects methods, delegates to specialist brains, and arbitrates results.",
        capabilities=["problem-framing", "method-selection", "delegation", "arbitration"],
        default_models=["qwen3.5-plus", "deepseek-v3.2"],
        fallback_models=["MiniMax-M2.5"],
        tool_policy={"network": "allowed", "write": "planning-only"},
        cost_policy={"budget": "balanced"},
        latency_policy={"target_ms": 8000},
        risk_policy={"auto_execute": False, "review_required_for_high_risk": True},
    ),
    BrainProfileSpec(
        brain_id="dialog-brain",
        role=BrainRole.DIALOG.value,
        description="Owns user-facing responses and coordinates specialist consultation for chat tasks.",
        capabilities=["conversation", "response-synthesis", "multi-model-voting"],
        default_models=["qwen3.5-plus"],
        fallback_models=["MiniMax-M2.5"],
        tool_policy={"network": "allowed", "write": "none"},
        cost_policy={"budget": "balanced"},
        latency_policy={"target_ms": 6000},
        risk_policy={"auto_execute": False},
    ),
    BrainProfileSpec(
        brain_id="source-intelligence-brain",
        role=BrainRole.SOURCE_INTELLIGENCE.value,
        description="Discovers, evaluates, promotes, demotes, and retires sources for ongoing collection.",
        capabilities=["source-discovery", "authority-mapping", "source-review"],
        default_models=["qwen3.5-plus", "deepseek-v3.2"],
        fallback_models=["MiniMax-M2.5"],
        tool_policy={"network": "allowed", "write": "source-plan-only"},
        cost_policy={"budget": "balanced"},
        latency_policy={"target_ms": 12000},
        risk_policy={"auto_execute": False, "require_review_for_subscription": True},
    ),
    BrainProfileSpec(
        brain_id="research-brain",
        role=BrainRole.RESEARCH.value,
        description="Runs structured research workflows, evidence collection, and comparative analysis.",
        capabilities=["deep-research", "comparative-analysis", "evidence-log"],
        default_models=["deepseek-v3.2", "qwen3.5-plus"],
        fallback_models=["MiniMax-M2.5"],
        tool_policy={"network": "allowed", "write": "research-artifacts"},
        cost_policy={"budget": "high"},
        latency_policy={"target_ms": 20000},
        risk_policy={"auto_execute": False},
    ),
    BrainProfileSpec(
        brain_id="knowledge-brain",
        role=BrainRole.KNOWLEDGE.value,
        description="Transforms information into structured knowledge across subject, time, and fact dimensions.",
        capabilities=["knowledge-extraction", "knowledge-structuring", "cross-domain-linking"],
        default_models=["qwen3.5-plus"],
        fallback_models=["deepseek-v3.2"],
        tool_policy={"network": "allowed", "write": "knowledge-artifacts"},
        cost_policy={"budget": "balanced"},
        latency_policy={"target_ms": 15000},
        risk_policy={"auto_execute": False},
    ),
    BrainProfileSpec(
        brain_id="evolution-chief-brain",
        role=BrainRole.EVOLUTION.value,
        description="Supervises self-test, diagnosis, recovery planning, and method improvement loops.",
        capabilities=["self-test", "diagnosis", "recovery-planning", "method-review"],
        default_models=["qwen3.5-plus", "deepseek-v3.2"],
        fallback_models=["MiniMax-M2.5"],
        tool_policy={"network": "allowed", "write": "issue-artifacts"},
        cost_policy={"budget": "balanced"},
        latency_policy={"target_ms": 10000},
        risk_policy={"auto_execute": True, "require_review_for_destructive_actions": True},
    ),
    BrainProfileSpec(
        brain_id="coding-brain",
        role=BrainRole.CODING.value,
        description="Handles code-focused diagnosis, patch planning, and implementation support.",
        capabilities=["code-analysis", "patch-planning", "test-driven-fix"],
        default_models=["deepseek-v3.2"],
        fallback_models=["qwen3.5-plus"],
        tool_policy={"network": "allowed", "write": "code-and-tests"},
        cost_policy={"budget": "high"},
        latency_policy={"target_ms": 15000},
        risk_policy={"auto_execute": False, "review_required_for_schema_changes": True},
    ),
)


DEFAULT_BRAIN_ROUTES: tuple[BrainRouteSpec, ...] = (
    BrainRouteSpec(
        route_id="chat-general",
        problem_type="interactive_dialog",
        thinking_framework="dialog_orchestration",
        primary_brain="dialog-brain",
        supporting_brains=["chief-brain", "research-brain", "knowledge-brain"],
        review_brain="chief-brain",
        fallback_brain="brainstem-controller",
        extra={"surface": "chat"},
    ),
    BrainRouteSpec(
        route_id="source-intelligence",
        problem_type="source_intelligence",
        thinking_framework="source_intelligence",
        primary_brain="source-intelligence-brain",
        supporting_brains=["research-brain", "knowledge-brain"],
        review_brain="chief-brain",
        fallback_brain="brainstem-controller",
        extra={"surface": "feeds"},
    ),
    BrainRouteSpec(
        route_id="self-evolution",
        problem_type="system_evolution",
        thinking_framework="systems_diagnosis",
        primary_brain="evolution-chief-brain",
        supporting_brains=["coding-brain", "research-brain"],
        review_brain="chief-brain",
        fallback_brain="brainstem-controller",
        extra={"surface": "evolution"},
    ),
    BrainRouteSpec(
        route_id="deep-research",
        problem_type="topic_research",
        thinking_framework="deep_research",
        primary_brain="research-brain",
        supporting_brains=["knowledge-brain", "source-intelligence-brain"],
        review_brain="chief-brain",
        fallback_brain="dialog-brain",
        extra={"surface": "research"},
    ),
)


def get_default_brain_profile_specs() -> tuple[BrainProfileSpec, ...]:
    return DEFAULT_BRAIN_PROFILES


def get_default_brain_route_specs() -> tuple[BrainRouteSpec, ...]:
    return DEFAULT_BRAIN_ROUTES


async def ensure_brain_control_plane(db: AsyncSession) -> dict[str, int]:
    existing_profiles = await db.execute(select(BrainProfile))
    profiles_by_brain_id = {item.brain_id: item for item in existing_profiles.scalars().all()}

    created_profiles = 0
    updated_profiles = 0
    for spec in DEFAULT_BRAIN_PROFILES:
        existing = profiles_by_brain_id.get(spec.brain_id)
        if existing is None:
            profile = BrainProfile(
                brain_id=spec.brain_id,
                role=spec.role,
                description=spec.description,
                capabilities=spec.capabilities,
                default_models=spec.default_models,
                fallback_models=spec.fallback_models,
                tool_policy=spec.tool_policy,
                cost_policy=spec.cost_policy,
                latency_policy=spec.latency_policy,
                risk_policy=spec.risk_policy,
                status=spec.status,
                version=spec.version,
            )
            db.add(profile)
            created_profiles += 1
            continue

        profile_changed = any(
            (
                existing.role != spec.role,
                (existing.description or "") != spec.description,
                list(existing.capabilities or []) != list(spec.capabilities),
                list(existing.default_models or []) != list(spec.default_models),
                list(existing.fallback_models or []) != list(spec.fallback_models),
                dict(existing.tool_policy or {}) != dict(spec.tool_policy),
                dict(existing.cost_policy or {}) != dict(spec.cost_policy),
                dict(existing.latency_policy or {}) != dict(spec.latency_policy),
                dict(existing.risk_policy or {}) != dict(spec.risk_policy),
                existing.status != spec.status,
                int(existing.version or 1) != int(spec.version or 1),
            )
        )
        if profile_changed:
            existing.role = spec.role
            existing.description = spec.description
            existing.capabilities = list(spec.capabilities)
            existing.default_models = list(spec.default_models)
            existing.fallback_models = list(spec.fallback_models)
            existing.tool_policy = dict(spec.tool_policy)
            existing.cost_policy = dict(spec.cost_policy)
            existing.latency_policy = dict(spec.latency_policy)
            existing.risk_policy = dict(spec.risk_policy)
            existing.status = spec.status
            existing.version = spec.version
            updated_profiles += 1

    if created_profiles or updated_profiles:
        await db.flush()
        existing_profiles = await db.execute(select(BrainProfile))
        profiles_by_brain_id = {item.brain_id: item for item in existing_profiles.scalars().all()}

    existing_routes = await db.execute(select(BrainRoute))
    routes_by_route_id = {item.route_id: item for item in existing_routes.scalars().all()}

    created_routes = 0
    for spec in DEFAULT_BRAIN_ROUTES:
        if spec.route_id in routes_by_route_id:
            continue
        route = BrainRoute(
            route_id=spec.route_id,
            problem_type=spec.problem_type,
            thinking_framework=spec.thinking_framework,
            primary_brain_id=profiles_by_brain_id[spec.primary_brain].id,
            supporting_brains=spec.supporting_brains,
            review_brain_id=profiles_by_brain_id[spec.review_brain].id if spec.review_brain else None,
            fallback_brain_id=profiles_by_brain_id[spec.fallback_brain].id if spec.fallback_brain else None,
            version=spec.version,
            enabled=spec.enabled,
            extra=spec.extra or {},
        )
        db.add(route)
        created_routes += 1

    fallback_specs = (
        {
            "fallback_id": "evolution-chief-brain:provider_failure",
            "brain_id": "evolution-chief-brain",
            "failure_mode": "provider_failure",
            "fallback_brain": "brainstem-controller",
            "fallback_mode": "degrade",
            "fallback_policy": {"action": "keep-monitoring", "disable_llm_reasoning": True},
        },
        {
            "fallback_id": "dialog-brain:provider_failure",
            "brain_id": "dialog-brain",
            "failure_mode": "provider_failure",
            "fallback_brain": "chief-brain",
            "fallback_mode": "review",
            "fallback_policy": {"action": "fallback-to-primary-summary"},
        },
    )

    existing_fallbacks = await db.execute(select(BrainFallback))
    fallback_ids = {item.fallback_id for item in existing_fallbacks.scalars().all()}
    created_fallbacks = 0
    for spec in fallback_specs:
        if spec["fallback_id"] in fallback_ids:
            continue
        db.add(BrainFallback(**spec, enabled=True, version=1))
        created_fallbacks += 1

    policy_specs = (
        {
            "policy_id": "route:self-evolution",
            "brain_id": "evolution-chief-brain",
            "route_id": "self-evolution",
            "cost_policy": {"budget": "balanced"},
            "latency_policy": {"target_ms": 10000},
            "execution_policy": {"mode": "auto-daemon"},
            "network_policy": {"search": True, "external_fetch": True},
            "timeout_policy": {"seconds": 30},
            "degrade_policy": {"fallback": "brainstem-controller"},
        },
        {
            "policy_id": "route:source-intelligence",
            "brain_id": "source-intelligence-brain",
            "route_id": "source-intelligence",
            "cost_policy": {"budget": "balanced"},
            "latency_policy": {"target_ms": 15000},
            "execution_policy": {"mode": "review-before-subscribe"},
            "network_policy": {"search": True, "external_fetch": True},
            "timeout_policy": {"seconds": 45},
            "degrade_policy": {"fallback": "research-brain"},
        },
    )

    existing_policies = await db.execute(select(BrainPolicy))
    policy_ids = {item.policy_id for item in existing_policies.scalars().all()}
    created_policies = 0
    for spec in policy_specs:
        if spec["policy_id"] in policy_ids:
            continue
        db.add(BrainPolicy(**spec, enabled=True, version=1))
        created_policies += 1

    if created_profiles or created_routes or created_fallbacks or created_policies:
        await db.commit()

    return {
        "created_profiles": created_profiles,
        "updated_profiles": updated_profiles,
        "created_routes": created_routes,
        "created_fallbacks": created_fallbacks,
        "created_policies": created_policies,
    }


async def list_brain_profiles(db: AsyncSession) -> list[BrainProfile]:
    result = await db.execute(select(BrainProfile).order_by(BrainProfile.role.asc(), BrainProfile.brain_id.asc()))
    return list(result.scalars().all())


async def list_brain_routes(db: AsyncSession) -> list[BrainRoute]:
    result = await db.execute(
        select(BrainRoute)
        .options(
            selectinload(BrainRoute.primary_brain),
            selectinload(BrainRoute.review_brain),
            selectinload(BrainRoute.fallback_brain),
        )
        .order_by(BrainRoute.problem_type.asc(), BrainRoute.route_id.asc())
    )
    return list(result.scalars().all())


def _ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _filter_models_for_capabilities(
    models: list[str],
    *,
    enable_search: bool,
    enable_thinking: bool,
) -> list[str]:
    filtered: list[str] = []
    for model in models:
        info = MultiModelVoting.BAILIAN_MODELS.get(model)
        if not info:
            filtered.append(model)
            continue

        supports_search = info.get("supports_search", False)
        supports_thinking = info.get("supports_thinking", False)

        if enable_search and enable_thinking:
            if not (supports_search or supports_thinking):
                continue
        elif enable_search and not supports_search:
            continue
        elif enable_thinking and not supports_thinking:
            continue

        filtered.append(model)

    return filtered


async def build_execution_plan(
    db: AsyncSession,
    *,
    problem_type: str,
    surface: str | None = None,
    use_voting: bool = False,
    enable_search: bool = False,
    enable_thinking: bool = False,
    requested_model: str | None = None,
) -> BrainExecutionPlan:
    await ensure_brain_control_plane(db)

    routes = await list_brain_routes(db)
    profiles = await list_brain_profiles(db)
    profile_by_brain_id = {item.brain_id: item for item in profiles}

    matching_routes = [route for route in routes if route.problem_type == problem_type and route.enabled]
    if surface:
        surface_specific = [route for route in matching_routes if (route.extra or {}).get("surface") == surface]
        if surface_specific:
            matching_routes = surface_specific

    if not matching_routes:
        raise ValueError(f"No brain route enabled for problem_type={problem_type}")

    route = matching_routes[0]
    primary_profile = route.primary_brain
    supporting_profiles = [
        profile_by_brain_id[brain_id]
        for brain_id in (route.supporting_brains or [])
        if brain_id in profile_by_brain_id
    ]

    primary_models = _ordered_unique(list(primary_profile.default_models or []))
    supporting_models = _ordered_unique(
        [model for profile in supporting_profiles for model in list(profile.default_models or [])]
    )

    if requested_model:
        selected_models = [requested_model]
    elif use_voting:
        selected_models = _ordered_unique(primary_models + supporting_models)
        selected_models = _filter_models_for_capabilities(
            selected_models,
            enable_search=enable_search,
            enable_thinking=enable_thinking,
        ) or selected_models
    else:
        selected_models = primary_models[:1] or supporting_models[:1]

    execution_mode = "voting" if use_voting else "single"

    return BrainExecutionPlan(
        route_id=route.route_id,
        problem_type=route.problem_type,
        thinking_framework=route.thinking_framework,
        primary_brain=primary_profile.brain_id,
        supporting_brains=[profile.brain_id for profile in supporting_profiles],
        review_brain=route.review_brain.brain_id if route.review_brain else None,
        fallback_brain=route.fallback_brain.brain_id if route.fallback_brain else None,
        primary_models=primary_models,
        supporting_models=supporting_models,
        selected_models=selected_models,
        execution_mode=execution_mode,
        surface=(route.extra or {}).get("surface"),
    )
