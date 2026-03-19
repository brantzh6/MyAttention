import sys
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from db.models import SourceType as SourceTypeEnum
from feeds.persistence import (
    build_import_feed_extra,
    build_import_source_url,
    map_import_source_type,
    normalize_import_source_key,
)


class FeedPersistenceHelpersTest(unittest.TestCase):
    def test_normalize_import_source_key_is_windows_safe(self) -> None:
        self.assertEqual(normalize_import_source_key("phase1/smoke"), "phase1_smoke")
        self.assertEqual(normalize_import_source_key("  ?? "), "imported")

    def test_build_import_source_url_uses_normalized_key(self) -> None:
        self.assertEqual(
            build_import_source_url("phase1/smoke"),
            "import://phase1_smoke",
        )

    def test_map_import_source_type_defaults_to_rss(self) -> None:
        self.assertEqual(map_import_source_type("api"), SourceTypeEnum.API)
        self.assertEqual(map_import_source_type("web"), SourceTypeEnum.WEB)
        self.assertEqual(map_import_source_type("unknown"), SourceTypeEnum.RSS)

    def test_build_import_feed_extra_contains_traceability_fields(self) -> None:
        extra = build_import_feed_extra(
            raw_ingest_id="raw-1",
            source_key="phase1/smoke",
            source_name="Phase1 Smoke",
            source_type="rss",
            category="tech",
            category_name="科技",
            metadata={"rank": 1},
            urgency_factors={"score": 0.8},
            secondary_tags=["ai"],
            language="zh",
        )
        self.assertEqual(extra["raw_ingest_id"], "raw-1")
        self.assertEqual(extra["source_key"], "phase1/smoke")
        self.assertEqual(extra["metadata"]["rank"], 1)
        self.assertEqual(extra["secondary_tags"], ["ai"])


if __name__ == "__main__":
    unittest.main()
