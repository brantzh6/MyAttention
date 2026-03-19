from dataclasses import dataclass


@dataclass
class ObjectRef:
    key: str
    size_bytes: int
    content_type: str | None = None
    content_encoding: str | None = None


@dataclass
class ObjectMeta:
    key: str
    size_bytes: int
    content_type: str | None = None
    content_encoding: str | None = None


class ObjectStore:
    async def put_bytes(
        self,
        key: str,
        data: bytes,
        content_type: str | None = None,
        content_encoding: str | None = None,
    ) -> ObjectRef:
        raise NotImplementedError

    async def get_bytes(self, key: str) -> bytes:
        raise NotImplementedError

    async def exists(self, key: str) -> bool:
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        raise NotImplementedError

    async def head(self, key: str) -> ObjectMeta:
        raise NotImplementedError
