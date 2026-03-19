"""Feeds module."""

__all__ = [
    "FeedFetcher",
    "get_feed_fetcher",
    "FeedSource",
    "FeedEntry",
    "AuthorityClassifier",
    "get_authority_classifier",
    "DepthFetcher",
    "get_depth_fetcher",
    "TaskClassifier",
    "get_task_classifier",
    "TaskProcessor",
    "get_task_processor",
]


def __getattr__(name: str):
    if name in {"FeedFetcher", "get_feed_fetcher", "FeedSource", "FeedEntry"}:
        from . import fetcher as module

        return getattr(module, name)
    if name in {"AuthorityClassifier", "get_authority_classifier"}:
        from . import authority as module

        return getattr(module, name)
    if name in {"DepthFetcher", "get_depth_fetcher"}:
        from . import depth_fetcher as module

        return getattr(module, name)
    if name in {"TaskClassifier", "get_task_classifier"}:
        from . import task_classifier as module

        return getattr(module, name)
    if name in {"TaskProcessor", "get_task_processor"}:
        from . import task_processor as module

        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
