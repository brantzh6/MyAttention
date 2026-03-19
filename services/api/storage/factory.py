from functools import lru_cache

from config import get_settings

from .base import ObjectStore
from .local import LocalObjectStore


@lru_cache()
def get_object_store() -> ObjectStore:
    settings = get_settings()
    backend = (settings.object_store_backend or "local").strip().lower()

    if backend != "local":
        raise ValueError(f"Unsupported object store backend: {backend}")

    return LocalObjectStore(settings.object_store_local_path)
