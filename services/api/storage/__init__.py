from .base import ObjectMeta, ObjectRef, ObjectStore

__all__ = ["ObjectMeta", "ObjectRef", "ObjectStore", "get_object_store"]


def get_object_store():
    from .factory import get_object_store as _get_object_store

    return _get_object_store()
