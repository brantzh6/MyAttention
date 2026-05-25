from typing import Any

from feeds.source_contracts import SourceDiscoveryCandidate, SourceDiscoveryFocus


def _compress_generic_domain_candidates(
    candidates: list[dict[str, Any]],
    focus: SourceDiscoveryFocus,
) -> list[dict[str, Any]]:
    if focus not in {
        SourceDiscoveryFocus.METHOD,
        SourceDiscoveryFocus.FRONTIER,
        SourceDiscoveryFocus.LATEST,
    }:
        return candidates

    specific_best_by_domain: dict[str, float] = {}
    for candidate in candidates:
        item_type = str(candidate.get("item_type", "")).lower()
        domain = str(candidate.get("domain", "")).lower()
        if not domain or item_type == "domain":
            continue
        specific_best_by_domain[domain] = max(
            specific_best_by_domain.get(domain, 0.0),
            float(candidate.get("authority_score", 0.0) or 0.0),
        )

    compressed: list[dict[str, Any]] = []
    for candidate in candidates:
        item_type = str(candidate.get("item_type", "")).lower()
        domain = str(candidate.get("domain", "")).lower()
        score = float(candidate.get("authority_score", 0.0) or 0.0)
        best_specific = specific_best_by_domain.get(domain, 0.0)
        if item_type == "domain" and best_specific >= max(score - 0.02, 0.38):
            continue
        compressed.append(candidate)
    return compressed


def _repository_base_object_key(object_key: str, item_type: str) -> str:
    key = str(object_key or "").lower()
    item_type = str(item_type or "").lower()
    if item_type == "repository":
        return key
    if item_type == "release" and "/release/" in key:
        return key.split("/release/", 1)[0]
    return ""


def _compress_release_repository_overlap(
    candidates: list[dict[str, Any]],
    focus: SourceDiscoveryFocus,
) -> list[dict[str, Any]]:
    if focus not in {SourceDiscoveryFocus.LATEST, SourceDiscoveryFocus.FRONTIER}:
        return candidates

    release_best_by_repo: dict[str, float] = {}
    for candidate in candidates:
        item_type = str(candidate.get("item_type", "")).lower()
        if item_type != "release":
            continue
        repo_key = _repository_base_object_key(candidate.get("object_key", ""), item_type)
        if not repo_key:
            continue
        release_best_by_repo[repo_key] = max(
            release_best_by_repo.get(repo_key, 0.0),
            float(candidate.get("authority_score", 0.0) or 0.0),
        )

    compressed: list[dict[str, Any]] = []
    for candidate in candidates:
        item_type = str(candidate.get("item_type", "")).lower()
        object_key = str(candidate.get("object_key", "")).lower()
        score = float(candidate.get("authority_score", 0.0) or 0.0)
        best_release = release_best_by_repo.get(object_key, 0.0)
        if item_type == "repository" and best_release >= max(score - 0.02, 0.38):
            continue
        compressed.append(candidate)
    return compressed


def compress_source_candidates(
    candidates: list[SourceDiscoveryCandidate],
    focus: SourceDiscoveryFocus,
) -> list[SourceDiscoveryCandidate]:
    """Apply regularized source-discovery compression after extraction."""
    payloads = [candidate.model_dump() for candidate in candidates]
    payloads = _compress_generic_domain_candidates(payloads, focus)
    payloads = _compress_release_repository_overlap(payloads, focus)
    allowed_keys = [str(payload.get("object_key", "")) for payload in payloads]
    allowed = set(allowed_keys)
    compressed = [candidate for candidate in candidates if candidate.object_key in allowed]
    compressed.sort(
        key=lambda candidate: allowed_keys.index(candidate.object_key)
        if candidate.object_key in allowed
        else len(allowed_keys)
    )
    return compressed
