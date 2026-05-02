from typing import TYPE_CHECKING, TypeAlias
from urllib.parse import urlparse

if TYPE_CHECKING:
    from feeds.source_contracts import SourceDiscoveryFocus

CandidateIdentity: TypeAlias = tuple[str, str, str, str, str]


_CONTEXTUAL_TECH_MEDIA_DOMAINS = {
    "36kr.com",
    "huxiu.com",
    "ithome.com",
    "jiqizhixin.com",
    "techcrunch.com",
    "theverge.com",
    "wired.com",
}

_RESERVED_GITHUB_SINGLE_SEGMENT_PATHS = {
    "orgs",
    "topics",
    "collections",
    "features",
    "enterprise",
    "pricing",
    "marketplace",
    "sponsors",
    "settings",
    "search",
    "notifications",
    "explore",
    "login",
    "join",
}

_RESERVED_GITLAB_SINGLE_SEGMENT_PATHS = {
    "explore",
    "groups",
    "projects",
}

_RESERVED_SOCIAL_SINGLE_SEGMENT_PATHS = {
    "about",
    "download",
    "explore",
    "hashtag",
    "home",
    "i",
    "intent",
    "login",
    "logout",
    "messages",
    "privacy",
    "search",
    "settings",
    "share",
    "signup",
    "tos",
}


def is_reserved_social_namespace(handle: str) -> bool:
    return handle.strip().lower() in _RESERVED_SOCIAL_SINGLE_SEGMENT_PATHS


def is_reserved_repository_namespace(domain: str, owner: str) -> bool:
    normalized_domain = normalize_domain(domain)
    normalized_owner = owner.strip().lower()
    if normalized_domain == "github.com":
        return normalized_owner in _RESERVED_GITHUB_SINGLE_SEGMENT_PATHS
    if normalized_domain == "gitlab.com":
        return normalized_owner in _RESERVED_GITLAB_SINGLE_SEGMENT_PATHS
    return False


def _focus_value(focus) -> str:
    return str(getattr(focus, "value", focus) or "").strip().lower()


def normalize_domain(value: str) -> str:
    parsed = urlparse(value if "://" in value else f"https://{value}")
    domain = parsed.netloc or parsed.path
    normalized = domain.lower().removeprefix("www.")
    parts = normalized.split(".")
    if len(parts) >= 3 and parts[0] in {"m", "mobile", "eu"}:
        normalized = ".".join(parts[1:])
    return normalized


def is_contextual_media_article_candidate(domain: str, path_segments: list[str]) -> bool:
    if domain not in _CONTEXTUAL_TECH_MEDIA_DOMAINS:
        return False
    if not path_segments:
        return False
    first = path_segments[0].lower()
    if first in {
        "tag",
        "tags",
        "topic",
        "topics",
        "category",
        "categories",
        "author",
        "authors",
        "about",
        "team",
        "search",
        "newsletters",
        "podcasts",
        "events",
    }:
        return False
    return True


def _github_repo_signal_identity(
    domain: str,
    path_segments: list[str],
    url: str,
    focus,
) -> CandidateIdentity | None:
    if domain != "github.com":
        return None
    if len(path_segments) < 4:
        return None

    owner, repo = path_segments[0], path_segments[1]
    section = path_segments[2].lower()
    item_id = path_segments[3]
    if is_reserved_repository_namespace(domain, owner):
        return None

    if section == "issues":
        object_key = f"{domain}/{owner}/{repo}/issue/{item_id}".lower()
        canonical_url = url if url.startswith("http") else f"https://{domain}/{owner}/{repo}/issues/{item_id}"
        display_name = f"{owner}/{repo} issue {item_id}"
        return "signal", object_key, display_name, canonical_url, domain

    if section in {"pull", "pulls"}:
        object_key = f"{domain}/{owner}/{repo}/pull/{item_id}".lower()
        canonical_url = url if url.startswith("http") else f"https://{domain}/{owner}/{repo}/pull/{item_id}"
        display_name = f"{owner}/{repo} pull {item_id}"
        return "signal", object_key, display_name, canonical_url, domain

    if section == "discussions":
        object_key = f"{domain}/{owner}/{repo}/discussion/{item_id}".lower()
        canonical_url = url if url.startswith("http") else f"https://{domain}/{owner}/{repo}/discussions/{item_id}"
        display_name = f"{owner}/{repo} discussion {item_id}"
        return "signal", object_key, display_name, canonical_url, domain

    return None


def candidate_identity(url: str, focus: "SourceDiscoveryFocus") -> CandidateIdentity:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    domain = normalize_domain(parsed.netloc or parsed.path)
    path_segments = [segment for segment in (parsed.path or "").split("/") if segment]
    focus_value = _focus_value(focus)

    if focus_value in {"latest", "frontier"} and is_contextual_media_article_candidate(
        domain,
        path_segments,
    ):
        slug = "-".join(path_segments).lower()
        object_key = f"{domain}/article/{slug}"
        canonical_url = url if url.startswith("http") else f"https://{domain}/{'/'.join(path_segments)}"
        display_name = f"{domain} article"
        return "signal", object_key, display_name, canonical_url, domain

    github_repo_signal = _github_repo_signal_identity(domain, path_segments, url, focus)
    if github_repo_signal is not None:
        return github_repo_signal

    if domain in {"github.com", "gitlab.com"} and len(path_segments) >= 4 and path_segments[2].lower() == "releases":
        owner, repo = path_segments[0], path_segments[1]
        if is_reserved_repository_namespace(domain, owner):
            return "domain", domain, domain, f"https://{domain}", domain
        is_tag_release = len(path_segments) >= 5 and path_segments[3].lower() == "tag"
        release_id = path_segments[4] if is_tag_release else path_segments[3]
        object_key = f"{domain}/{owner}/{repo}/release/{release_id}".lower()
        release_path = f"releases/tag/{release_id}" if is_tag_release else f"releases/{release_id}"
        canonical_url = url if url.startswith("http") else f"https://{domain}/{owner}/{repo}/{release_path}"
        display_name = f"{owner}/{repo} release {release_id}"
        return "release", object_key, display_name, canonical_url, domain

    if domain in {"github.com", "gitlab.com"} and len(path_segments) >= 3 and path_segments[2].lower() == "releases":
        owner, repo = path_segments[0], path_segments[1]
        if is_reserved_repository_namespace(domain, owner):
            return "domain", domain, domain, f"https://{domain}", domain
        object_key = f"{domain}/{owner}/{repo}/release/latest".lower()
        canonical_url = f"https://{domain}/{owner}/{repo}/releases"
        display_name = f"{owner}/{repo} releases"
        return "release", object_key, display_name, canonical_url, domain

    if domain in {"github.com", "gitlab.com"} and path_segments and path_segments[0].lower() == "orgs" and len(path_segments) >= 2:
        org = path_segments[1]
        object_key = f"{domain}/org/{org}".lower()
        canonical_url = f"https://{domain}/orgs/{org}"
        return "organization", object_key, org, canonical_url, domain

    if domain in {"github.com", "gitlab.com"} and len(path_segments) == 1:
        handle = path_segments[0]
        if domain == "github.com" and handle.lower() in _RESERVED_GITHUB_SINGLE_SEGMENT_PATHS:
            return "domain", domain, domain, f"https://{domain}", domain
        if domain == "gitlab.com" and handle.lower() in _RESERVED_GITLAB_SINGLE_SEGMENT_PATHS:
            return "domain", domain, domain, f"https://{domain}", domain
        object_key = f"{domain}/org/{handle}".lower()
        canonical_url = f"https://{domain}/{handle}"
        return "organization", object_key, handle, canonical_url, domain

    if domain in {"github.com", "gitlab.com"} and len(path_segments) >= 2:
        owner, repo = path_segments[0], path_segments[1]
        if is_reserved_repository_namespace(domain, owner):
            return "domain", domain, domain, f"https://{domain}", domain
        object_key = f"{domain}/{owner}/{repo}".lower()
        canonical_url = f"https://{domain}/{owner}/{repo}"
        display_name = f"{owner}/{repo}"
        return "repository", object_key, display_name, canonical_url, domain

    if domain == "huggingface.co" and len(path_segments) >= 2:
        owner, repo = path_segments[0], path_segments[1]
        object_key = f"{domain}/{owner}/{repo}".lower()
        canonical_url = f"https://{domain}/{owner}/{repo}"
        display_name = f"{owner}/{repo}"
        return "repository", object_key, display_name, canonical_url, domain

    if domain == "reddit.com" and len(path_segments) >= 2 and path_segments[0].lower() == "r":
        if len(path_segments) >= 4 and path_segments[2].lower() in {"comments", "s"}:
            if focus_value == "method":
                community = path_segments[1]
                object_key = f"{domain}/r/{community}".lower()
                canonical_url = f"https://{domain}/r/{community}"
                display_name = f"r/{community}"
                return "community", object_key, display_name, canonical_url, domain
            thread_id = path_segments[3]
            object_key = f"{domain}/thread/{thread_id}".lower()
            canonical_url = url if url.startswith("http") else f"https://{domain}/{'/'.join(path_segments[:4])}"
            display_name = f"r/{path_segments[1]} thread {thread_id}"
            return "signal", object_key, display_name, canonical_url, domain
        community = path_segments[1]
        object_key = f"{domain}/r/{community}".lower()
        canonical_url = f"https://{domain}/r/{community}"
        display_name = f"r/{community}"
        return "community", object_key, display_name, canonical_url, domain

    if domain == "linkedin.com" and len(path_segments) >= 2 and path_segments[0].lower() == "company":
        company = path_segments[1]
        object_key = f"{domain}/company/{company}".lower()
        canonical_url = f"https://{domain}/company/{company}"
        return "organization", object_key, company, canonical_url, domain

    if domain == "linkedin.com" and len(path_segments) >= 2 and path_segments[0].lower() == "in":
        handle = path_segments[1]
        object_key = f"{domain}/in/{handle}".lower()
        canonical_url = f"https://{domain}/in/{handle}"
        return "person", object_key, handle, canonical_url, domain

    if domain in {"x.com", "twitter.com"} and path_segments:
        if len(path_segments) >= 3 and path_segments[1].lower() == "status":
            handle = path_segments[0]
            if is_reserved_social_namespace(handle):
                return "domain", domain, domain, f"https://{domain}", domain
            status_id = path_segments[2]
            object_key = f"{domain}/{handle}/status/{status_id}".lower()
            canonical_url = url if url.startswith("http") else f"https://{domain}/{handle}/status/{status_id}"
            display_name = f"@{handle} status {status_id}"
            return "signal", object_key, display_name, canonical_url, domain
        handle = path_segments[0]
        if not is_reserved_social_namespace(handle):
            object_key = f"{domain}/{handle}".lower()
            canonical_url = f"https://{domain}/{handle}"
            display_name = f"@{handle}"
            return "person", object_key, display_name, canonical_url, domain

    if domain == "news.ycombinator.com" and parsed.query:
        query = parsed.query.lower()
        if "id=" in query:
            item_id = query.split("id=", 1)[1].split("&", 1)[0]
            object_key = f"{domain}/item/{item_id}".lower()
            canonical_url = url if url.startswith("http") else f"https://{domain}{parsed.path}?id={item_id}"
            display_name = f"HN item {item_id}"
            return "signal", object_key, display_name, canonical_url, domain

    event_segments = {
        "events",
        "event",
        "summit",
        "conference",
        "meetup",
        "workshop",
        "webinar",
        "talk",
        "talks",
    }
    if any(segment.lower() in event_segments for segment in path_segments):
        object_key = f"{domain}:event"
        canonical_url = url if url.startswith("http") else f"https://{domain}/{'/'.join(path_segments)}"
        display_name = f"{domain} events"
        return "event", object_key, display_name, canonical_url, domain

    if any(
        segment.lower() in {"changelog", "release", "releases", "release-notes", "announcements"}
        or segment.lower().startswith("release-")
        or segment.lower().startswith("announcement-")
        for segment in path_segments
    ):
        object_key = f"{domain}:release"
        canonical_url = url if url.startswith("http") else f"https://{domain}/{'/'.join(path_segments)}"
        display_name = f"{domain} release stream"
        return "release", object_key, display_name, canonical_url, domain

    object_key = domain
    canonical_url = f"https://{domain}" if domain else url
    display_name = domain
    return "domain", object_key, display_name, canonical_url, domain


def focus_category(focus) -> str:
    focus_value = _focus_value(focus)
    if focus_value == "method":
        return "开发者"
    if focus_value == "frontier":
        return "AI研究"
    if focus_value == "latest":
        return "科技"
    return "AI研究"


def ai_judgment_truth_boundary() -> list[str]:
    return [
        "AI judgment inspect output is advisory, not canonical source truth",
        "AI judgment does not auto-subscribe, auto-promote, or write source plans",
        "model verdicts must remain reviewable and may be wrong or incomplete",
        "model summary is advisory condensation, not the canonical decision set",
    ]
