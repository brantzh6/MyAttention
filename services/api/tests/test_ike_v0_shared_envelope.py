"""
Minimal tests for IKE v0 SharedEnvelope schema.

Tests verify:
- Import works
- Instantiation with required fields
- Timestamps are timezone-aware UTC
- JSON serialization includes expected fields
- Confidence validation works
"""

import unittest
from datetime import datetime, timezone

from ike_v0.schemas.envelope import SharedEnvelope


class TestSharedEnvelope(unittest.TestCase):
    """Basic tests for SharedEnvelope schema."""

    def test_import(self):
        """SharedEnvelope can be imported."""
        self.assertIsNotNone(SharedEnvelope)

    def test_instantiation_required_fields(self):
        """SharedEnvelope can be instantiated with required fields."""
        envelope = SharedEnvelope(
            id="test-id-123",
            kind="observation"
        )
        self.assertEqual(envelope.id, "test-id-123")
        self.assertEqual(envelope.kind, "observation")
        self.assertEqual(envelope.version, "v0.1.0")
        self.assertEqual(envelope.status, "draft")
        self.assertEqual(envelope.confidence, 0.5)
        self.assertEqual(envelope.provenance, {})
        self.assertEqual(envelope.references, [])

    def test_timestamps_are_timezone_aware(self):
        """created_at and updated_at are timezone-aware UTC datetimes."""
        envelope = SharedEnvelope(
            id="test-id-456",
            kind="entity"
        )
        self.assertIsNotNone(envelope.created_at)
        self.assertIsNotNone(envelope.updated_at)
        self.assertIsNotNone(envelope.created_at.tzinfo)
        self.assertIsNotNone(envelope.updated_at.tzinfo)
        self.assertEqual(envelope.created_at.tzinfo, timezone.utc)
        self.assertEqual(envelope.updated_at.tzinfo, timezone.utc)

    def test_json_serialization(self):
        """JSON serialization includes expected envelope fields."""
        envelope = SharedEnvelope(
            id="test-id-789",
            kind="claim"
        )
        data = envelope.model_dump()
        required_fields = [
            "id", "kind", "version", "status",
            "created_at", "updated_at", "provenance",
            "confidence", "references"
        ]
        for field in required_fields:
            self.assertIn(field, data)

    def test_confidence_validation(self):
        """Confidence field validation works for valid values."""
        envelope = SharedEnvelope(
            id="test-id-valid",
            kind="decision",
            confidence=0.85
        )
        self.assertEqual(envelope.confidence, 0.85)

        envelope_zero = SharedEnvelope(
            id="test-id-zero",
            kind="experiment",
            confidence=0.0
        )
        self.assertEqual(envelope_zero.confidence, 0.0)

        envelope_one = SharedEnvelope(
            id="test-id-one",
            kind="research_task",
            confidence=1.0
        )
        self.assertEqual(envelope_one.confidence, 1.0)


if __name__ == "__main__":
    unittest.main()
