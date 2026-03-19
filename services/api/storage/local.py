import asyncio
import json
from pathlib import Path

from .base import ObjectMeta, ObjectRef, ObjectStore


class LocalObjectStore(ObjectStore):
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path).expanduser().resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, key: str) -> Path:
        normalized = key.strip("/").replace("\\", "/")
        path = (self.base_path / normalized).resolve()
        if self.base_path not in path.parents and path != self.base_path:
            raise ValueError(f"Object key escapes base path: {key}")
        return path

    def _meta_path(self, path: Path) -> Path:
        return path.with_name(f"{path.name}.meta.json")

    async def put_bytes(
        self,
        key: str,
        data: bytes,
        content_type: str | None = None,
        content_encoding: str | None = None,
    ) -> ObjectRef:
        path = self._resolve_path(key)
        meta_path = self._meta_path(path)

        def _write() -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            meta_path.write_text(
                json.dumps(
                    {
                        "content_type": content_type,
                        "content_encoding": content_encoding,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

        await asyncio.to_thread(_write)
        return ObjectRef(
            key=key,
            size_bytes=len(data),
            content_type=content_type,
            content_encoding=content_encoding,
        )

    async def get_bytes(self, key: str) -> bytes:
        path = self._resolve_path(key)
        return await asyncio.to_thread(path.read_bytes)

    async def exists(self, key: str) -> bool:
        path = self._resolve_path(key)
        return await asyncio.to_thread(path.exists)

    async def delete(self, key: str) -> None:
        path = self._resolve_path(key)
        meta_path = self._meta_path(path)

        def _delete() -> None:
            if path.exists():
                path.unlink()
            if meta_path.exists():
                meta_path.unlink()

        await asyncio.to_thread(_delete)

    async def head(self, key: str) -> ObjectMeta:
        path = self._resolve_path(key)
        meta_path = self._meta_path(path)

        def _stat():
            content_type = None
            content_encoding = None
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    content_type = meta.get("content_type")
                    content_encoding = meta.get("content_encoding")
                except (OSError, json.JSONDecodeError, TypeError, ValueError):
                    content_type = None
                    content_encoding = None
            return path.stat(), content_type, content_encoding

        stat, content_type, content_encoding = await asyncio.to_thread(_stat)
        return ObjectMeta(
            key=key,
            size_bytes=stat.st_size,
            content_type=content_type,
            content_encoding=content_encoding,
        )
