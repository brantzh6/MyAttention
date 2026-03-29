"""
Minimal tests for IKE v0 Observation schema and mapper.

Tests verify:
- Observation schema can be imported and instantiated
- Mapper can create observations from mock feed items
- Timestamps are timezone-aware
- Field mapping is correct
"""

import unittest
from datetime import datetime, timezone
from uuid import uuid4

from ike_v0.schemas.observation import Observation
from ike_v0.mappers.observation import map_feed_item_to_observation
from ike_v0.types.ids import IKEKind


class TestObservationSchema(unittest.TestCase):
    """Tests for Observation schema."""

    def test_import(self):
        """Observation can be imported."""
        self.assertIsNotNone(Observation)

    def test_instantiation_required_fields(self):
        """Observation can be instantiated with required fields."""
        now = datetime.now(timezone.utc)
        obs = Observation(
            id="ike:observation:12345678-1234-1234-1234-123456789012",
            kind="observation",
            created_at=now,
            updated_at=now,
            source_ref="source-123",
            observed_at=now,
            captured_at=now,
            title="Test Observation",
            summary="Test summary",
        )
        self.assertEqual(obs.kind, "observation")
        self.assertEqual(obs.source_ref, "source-123")
        self.assertEqual(obs.title, "Test Observation")
        self.assertEqual(obs.summary, "Test summary")
        self.assertEqual(obs.signal_type, "feed_item")

    def test_timestamps_timezone_aware(self):
        """Observation timestamps are timezone-aware."""
        now = datetime.now(timezone.utc)
        obs = Observation(
            id="ike:observation:12345678-1234-1234-1234-123456789012",
            kind="observation",
            created_at=now,
            updated_at=now,
            source_ref="source-123",
            observed_at=now,
            captured_at=now,
            title="Test",
            summary="Test",
        )
        self.assertIsNotNone(obs.observed_at.tzinfo)
        self.assertIsNotNone(obs.captured_at.tzinfo)
        self.assertEqual(obs.observed_at.tzinfo, timezone.utc)


class TestMapFeedItemToObservation(unittest.TestCase):
    """Tests for map_feed_item_to_observation function."""

    def test_map_from_dict(self):
        """Map a dict-like feed item to Observation."""
        feed_item = {
            "id": str(uuid4()),
            "source_id": str(uuid4()),
            "title": "Test Feed Item",
            "summary": "Test summary from feed",
            "url": "https://example.com/article",
            "importance": 0.75,
            "published_at": datetime.now(timezone.utc),
            "fetched_at": datetime.now(timezone.utc),
            "extra": {"key": "value"},
        }
        obs = map_feed_item_to_observation(feed_item)
        self.assertEqual(obs.kind, "observation")
        self.assertEqual(obs.title, "Test Feed Item")
        self.assertEqual(obs.summary, "Test summary from feed")
        self.assertEqual(obs.content_ref, "https://example.com/article")
        self.assertEqual(obs.confidence, 0.75)
        self.assertIn("mapper", obs.provenance)

    def test_map_with_raw_ingest(self):
        """Map with optional raw_ingest reference."""
        feed_item = {
            "source_id": str(uuid4()),
            "title": "Test",
            "summary": "Summary",
            "fetched_at": datetime.now(timezone.utc),
        }
        raw_ingest = {"object_key": "s3://bucket/key123"}
        obs = map_feed_item_to_observation(feed_item, raw_ingest=raw_ingest)
        self.assertEqual(obs.raw_ref, "s3://bucket/key123")
        self.assertIn("s3://bucket/key123", obs.references)

    def test_map_default_confidence(self):
        """Map uses default confidence when importance not provided."""
        feed_item = {
            "source_id": str(uuid4()),
            "title": "Test",
            "summary": "Summary",
            "fetched_at": datetime.now(timezone.utc),
        }
        obs = map_feed_item_to_observation(feed_item)
        self.assertEqual(obs.confidence, 0.5)

    def test_map_clamped_confidence(self):
        """Map clamps confidence to [0, 1] range."""
        feed_item_high = {
            "source_id": str(uuid4()),
            "title": "Test",
            "summary": "Summary",
            "importance": 1.5,  # Out of range
            "fetched_at": datetime.now(timezone.utc),
        }
        obs_high = map_feed_item_to_observation(feed_item_high)
        self.assertEqual(obs_high.confidence, 1.0)

        feed_item_low = {
            "source_id": str(uuid4()),
            "title": "Test",
            "summary": "Summary",
            "importance": -0.5,  # Out of range
            "fetched_at": datetime.now(timezone.utc),
        }
        obs_low = map_feed_item_to_observation(feed_item_low)
        self.assertEqual(obs_low.confidence, 0.0)

    def test_map_generated_id_format(self):
        """Map generates properly formatted IKE ID."""
        feed_item = {
            "source_id": str(uuid4()),
            "title": "Test",
            "summary": "Summary",
            "fetched_at": datetime.now(timezone.utc),
        }
        obs = map_feed_item_to_observation(feed_item)
        self.assertTrue(obs.id.startswith("ike:observation:"))
        self.assertEqual(len(obs.id), len("ike:observation:") + 36)


if __name__ == "__main__":
    unittest.main()
