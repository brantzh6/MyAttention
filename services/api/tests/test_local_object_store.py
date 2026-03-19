import sys
import tempfile
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from storage.local import LocalObjectStore


class LocalObjectStoreTest(unittest.IsolatedAsyncioTestCase):
    async def test_put_head_get_delete_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalObjectStore(tmpdir)
            data = b'{"hello":"world"}'
            key = "raw/test-source/2026/03/19/item-123.json.gz"

            ref = await store.put_bytes(
                key,
                data,
                content_type="application/json",
                content_encoding="gzip",
            )
            self.assertEqual(ref.key, key)
            self.assertEqual(ref.size_bytes, len(data))

            head = await store.head(key)
            self.assertEqual(head.key, key)
            self.assertEqual(head.size_bytes, len(data))
            self.assertEqual(head.content_type, "application/json")
            self.assertEqual(head.content_encoding, "gzip")

            payload = await store.get_bytes(key)
            self.assertEqual(payload, data)
            self.assertTrue(await store.exists(key))

            await store.delete(key)
            self.assertFalse(await store.exists(key))

    async def test_escape_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalObjectStore(tmpdir)
            with self.assertRaises(ValueError):
                await store.put_bytes("../escape.txt", b"bad")


if __name__ == "__main__":
    unittest.main()
