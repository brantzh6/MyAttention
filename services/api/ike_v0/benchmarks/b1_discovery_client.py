"""
IKE B1 Discovery Client

Small HTTP client helper for calling source-discovery endpoint
and returning results suitable for B1-S1 benchmark.

This is a bounded helper - not a generic discovery service.
"""

import httpx
from typing import Any, Dict, List, Optional

from .b1_harness import HarnessTrendBundle, detect_harness_trend_bundle


# Default API base URL - can be overridden via environment or config
DEFAULT_API_BASE = "http://localhost:8000"

# B1-S1 benchmark-specific topic expansion for "harness"
# This scopes discovery to the intended technical neighborhood
B1_HARNESS_CONTEXT_TOPICS = [
    "openclaw",
    "AI agent",
    "evaluation",
    "testing",
    "runtime",
    "skill",
    "agent verification",
    "benchmark",
]


class DiscoveryClientError(Exception):
    """Raised when discovery HTTP call fails."""
    pass


class DiscoveryResponseError(Exception):
    """Raised when discovery response is malformed or missing expected data."""
    pass


def call_source_discovery(
    topic: str,
    focus: str = "authoritative",
    limit: int = 12,
    api_base: str = DEFAULT_API_BASE,
) -> List[Dict[str, Any]]:
    """
    Call the source-discovery HTTP endpoint and return candidates.

    This helper makes a POST request to /api/sources/discover and
    converts the response into a list of candidate dicts suitable
    for detect_harness_trend_bundle().

    Args:
        topic: The discovery topic (e.g., "harness")
        focus: Discovery focus - one of: latest, authoritative, frontier, method
        limit: Number of candidates to request (3-30)
        api_base: Base URL for the API (default: http://localhost:8000)

    Returns:
        List of candidate dicts with fields:
            - name: str
            - type: str (mapped from object_bucket/item_type)
            - description: str (from recommendation_reason)
            - source_ref: str (from object_key)
            - domain: str
            - url: str
            - authority_tier: str
            - authority_score: float

    Raises:
        DiscoveryClientError: If HTTP call fails
        DiscoveryResponseError: If response is malformed or missing candidates
    """
    url = f"{api_base}/api/sources/discover"

    request_body = {
        "topic": topic,
        "focus": focus,
        "limit": limit,
    }

    try:
        with httpx.Client() as client:
            response = client.post(url, json=request_body, timeout=30.0)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as e:
        raise DiscoveryClientError(f"Discovery HTTP call failed: {e}")
    except httpx.TimeoutException as e:
        raise DiscoveryClientError(f"Discovery call timed out: {e}")
    except Exception as e:
        raise DiscoveryClientError(f"Discovery call failed: {e}")

    # Validate response structure
    if not isinstance(data, dict):
        raise DiscoveryResponseError("Discovery response must be a JSON object")

    if "candidates" not in data:
        raise DiscoveryResponseError("Discovery response missing 'candidates' field")

    candidates_raw = data.get("candidates", [])
    if not isinstance(candidates_raw, list):
        raise DiscoveryResponseError("Discovery 'candidates' must be a list")

    # Convert candidates to benchmark-friendly format
    converted_candidates: List[Dict[str, Any]] = []
    for c in candidates_raw:
        if not isinstance(c, dict):
            continue

        # Map object_bucket/item_type to benchmark entity types
        object_bucket = c.get("object_bucket", "domain")
        item_type = c.get("item_type", "domain")
        url = c.get("url", "")
        domain = c.get("domain", "")

        # Try to infer entity type from object_bucket, item_type, related_entities, and URL/domain
        entity_type = _infer_entity_type(
            object_bucket,
            item_type,
            c.get("related_entities", []),
            url=url,
            domain=domain,
        )

        # Build description from recommendation_reason and other fields
        description_parts = []
        if c.get("recommendation_reason"):
            description_parts.append(c["recommendation_reason"])
        if c.get("inferred_roles"):
            description_parts.append(f"Roles: {', '.join(c['inferred_roles'][:2])}")

        converted = {
            "name": c.get("name", c.get("domain", "Unknown")),
            "type": entity_type,
            "description": " ".join(description_parts) if description_parts else f"Discovered {item_type} for {topic}",
            "source_ref": c.get("object_key", ""),
            "domain": c.get("domain", ""),
            "url": c.get("url", ""),
            "authority_tier": c.get("authority_tier", "C"),
            "authority_score": c.get("authority_score", 0.0),
        }

        # Only include candidates with a name
        if converted["name"]:
            converted_candidates.append(converted)

    return converted_candidates


def _build_b1_discovery_topic(topic: str) -> str:
    """
    Build expanded discovery topic for B1-S1 benchmark.

    For the "harness" topic, this expands to include relevant context
    about openclaw, AI agents, evaluation, testing, etc. to avoid
    generic unrelated harness mentions.

    For other topics, returns the topic unchanged.

    Args:
        topic: The base topic (e.g., "harness")

    Returns:
        Expanded topic string for discovery API
    """
    if topic.lower() == "harness":
        # Expand harness to include B1-S1 relevant context
        # This scopes discovery to the intended technical neighborhood
        context = " ".join(B1_HARNESS_CONTEXT_TOPICS)
        return f"{topic} {context}"
    return topic


def _infer_entity_type(
    object_bucket: str,
    item_type: str,
    related_entities: List[Dict[str, str]],
    url: str = "",
    domain: str = "",
) -> str:
    """
    Infer benchmark entity type from discovery response fields.

    Priority order:
    1. Explicit object_bucket hints (person, repo, org)
    2. GitHub URL pattern analysis (user vs org vs repo) - overrides generic community bucket
    3. Generic community bucket fallback
    4. item_type hints
    5. related_entities hints
    6. Default to domain

    Args:
        object_bucket: The object bucket (authority, person, repo, etc.)
        item_type: The item type (domain, github, twitter, etc.)
        related_entities: List of related entity dicts with type/name
        url: The URL of the candidate (optional, for GitHub pattern matching)
        domain: The domain of the candidate (optional, for GitHub pattern matching)

    Returns:
        Entity type string suitable for B1 benchmark ranking
    """
    # Check explicit object_bucket hints first (person, repo, org)
    bucket_lower = object_bucket.lower()
    if "person" in bucket_lower:
        return "person"
    if "repo" in bucket_lower or "repository" in bucket_lower:
        return "repository"
    if "org" in bucket_lower or "organization" in bucket_lower:
        return "organization"

    # Check GitHub URL patterns BEFORE generic community bucket
    # This ensures github.com/user/... is classified as person, not community
    check_url = url.lower() if url else domain.lower()
    if "github.com" in check_url:
        # Parse GitHub URL pattern: github.com/{owner}/{repo} or github.com/user/{username}
        # Remove protocol and www if present
        clean_url = check_url.replace("https://", "").replace("http://", "").replace("www.", "")
        if clean_url.startswith("github.com/"):
            path_parts = clean_url.replace("github.com/", "").split("/")
            if len(path_parts) >= 1:
                # Check for explicit user/org patterns
                if path_parts[0] == "user":
                    # github.com/user/username -> person
                    return "person"
                elif path_parts[0] == "org" or path_parts[0] == "orgs":
                    # github.com/org/orgname or github.com/orgs/orgname -> organization
                    return "organization"
                elif len(path_parts) >= 2:
                    # github.com/owner/repo -> repository
                    return "repository"
                elif len(path_parts) == 1:
                    # github.com/username (could be user or org, default to person for single-segment)
                    # Check if it looks like a personal username (no hyphens, short)
                    username = path_parts[0]
                    if "-" not in username and len(username) < 20:
                        return "person"
                    else:
                        return "organization"

    # Generic community bucket fallback (after GitHub URL patterns)
    if "community" in bucket_lower:
        return "community"

    # Check item_type
    item_lower = item_type.lower()
    if "github" in item_lower:
        return "repository"
    if "twitter" in item_lower or "x.com" in item_lower:
        return "person"
    # Don't return domain yet - check related_entities first

    # Check related_entities for person/repo/org hints
    for entity in related_entities:
        entity_type = entity.get("type", "").lower()
        if "person" in entity_type:
            return "person"
        if "repo" in entity_type or "repository" in entity_type:
            return "repository"
        if "org" in entity_type or "organization" in entity_type:
            return "organization"
        if "community" in entity_type:
            return "community"

    # Default to domain (will be de-emphasized in ranking)
    return "domain"


def run_harness_benchmark(
    topic: str = "harness",
    focus: str = "authoritative",
    limit: int = 12,
    api_base: str = DEFAULT_API_BASE,
) -> HarnessTrendBundle:
    """
    Run the full B1-S1 harness benchmark.

    This helper:
    1. Calls source discovery with topic expansion for "harness"
    2. Passes results to detect_harness_trend_bundle()
    3. Returns the resulting HarnessTrendBundle

    For the "harness" topic, the discovery query is automatically expanded
    to include relevant context (openclaw, AI agent, evaluation, testing, etc.)
    to avoid generic unrelated harness mentions.

    Args:
        topic: The benchmark topic (default: "harness")
        focus: Discovery focus (default: "authoritative")
        limit: Number of candidates to request (default: 12)
        api_base: API base URL (default: http://localhost:8000)

    Returns:
        HarnessTrendBundle with ranked entities and analysis

    Raises:
        DiscoveryClientError: If discovery HTTP call fails
        DiscoveryResponseError: If discovery response is malformed
    """
    # Build expanded topic for B1-S1 benchmark
    # This scopes "harness" to the intended technical neighborhood
    expanded_topic = _build_b1_discovery_topic(topic)

    # Call discovery with expanded topic
    candidates = call_source_discovery(
        topic=expanded_topic,
        focus=focus,
        limit=limit,
        api_base=api_base,
    )

    # Wrap in discovery_results format expected by detect_harness_trend_bundle
    # Use original topic for benchmark analysis (not the expanded query)
    discovery_results = [
        {
            "query": expanded_topic,
            "focus": focus,
            "candidates": candidates,
        }
    ]

    # Run benchmark analysis
    bundle = detect_harness_trend_bundle(
        discovery_results=discovery_results,
        topic=topic,
    )

    return bundle
