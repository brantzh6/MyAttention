import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from feeds.raw_ingest import build_raw_object_key


class RawIngestKeyTest(unittest.TestCase):
    def test_build_raw_object_key_is_stable_and_windows_safe(self) -> None:
        fetched_at = datetime(2026, 3, 19, 10, 30, tzinfo=timezone.utc)
        external_id = "https://example.com/news?id=1&lang=zh-CN"

        key = build_raw_object_key("news/world", fetched_at, external_id)

        self.assertTrue(key.startswith("raw/news_world/2026/03/19/"))
        self.assertTrue(key.endswith(".json.gz"))
        self.assertNotIn("https://", key)
        self.assertNotIn("?", key)
        self.assertNotIn(":", key)
        self.assertNotIn("&", key)

    def test_build_raw_object_key_same_input_same_key(self) -> None:
        fetched_at = datetime(2026, 3, 19, 10, 30, tzinfo=timezone.utc)
        external_id = "item-42"

        key1 = build_raw_object_key("source/a", fetched_at, external_id)
        key2 = build_raw_object_key("source/a", fetched_at, external_id)

        self.assertEqual(key1, key2)


if __name__ == "__main__":
    unittest.main()
