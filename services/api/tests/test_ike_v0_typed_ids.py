"""
Minimal tests for IKE v0 typed ID helpers.

Tests verify:
- ID generation with prefixes
- ID validation
- ID parsing
- Error handling for invalid IDs
"""

import unittest
from ike_v0.types.ids import (
    IKEKind,
    IKE_ID_PREFIXES,
    generate_ike_id,
    validate_ike_id,
    parse_ike_id,
)


class TestIKEKind(unittest.TestCase):
    """Tests for IKEKind enum."""

    def test_all_kinds_defined(self):
        """All required v0 object kinds are defined."""
        expected_kinds = {
            "observation",
            "entity",
            "claim",
            "research_task",
            "experiment",
            "decision",
            "harness_case",
        }
        actual_kinds = {k.value for k in IKEKind}
        self.assertEqual(expected_kinds, actual_kinds)


class TestGenerateIKEId(unittest.TestCase):
    """Tests for generate_ike_id function."""

    def test_generate_with_enum(self):
        """Generate ID using IKEKind enum."""
        ike_id = generate_ike_id(IKEKind.OBSERVATION)
        self.assertTrue(ike_id.startswith("ike:observation:"))
        self.assertEqual(len(ike_id), len("ike:observation:") + 36)  # UUID is 36 chars

    def test_generate_with_string(self):
        """Generate ID using string kind."""
        ike_id = generate_ike_id("entity")
        self.assertTrue(ike_id.startswith("ike:entity:"))

    def test_generate_with_custom_uuid(self):
        """Generate ID with provided UUID."""
        custom_uuid = "12345678-1234-1234-1234-123456789012"
        ike_id = generate_ike_id(IKEKind.CLAIM, custom_uuid)
        self.assertEqual(ike_id, f"ike:claim:{custom_uuid}")

    def test_generate_all_kinds(self):
        """Generate IDs for all v0 object kinds."""
        for kind in IKEKind:
            with self.subTest(kind=kind):
                ike_id = generate_ike_id(kind)
                expected_prefix = IKE_ID_PREFIXES[kind]
                self.assertTrue(ike_id.startswith(expected_prefix))

    def test_generate_invalid_kind(self):
        """Generate ID with invalid kind raises error."""
        with self.assertRaises(ValueError):
            generate_ike_id("invalid_kind")


class TestValidateIKEId(unittest.TestCase):
    """Tests for validate_ike_id function."""

    def test_valid_ids(self):
        """Valid IKE IDs return True."""
        valid_ids = [
            "ike:observation:550e8400-e29b-41d4-a716-446655440000",
            "ike:entity:12345678-1234-1234-1234-123456789012",
            "ike:claim:ABCDEF00-ABCD-ABCD-ABCD-ABCDEF001234",
            "ike:research_task:00000000-0000-0000-0000-000000000000",
            "ike:experiment:ffffffff-ffff-ffff-ffff-ffffffffffff",
            "ike:decision:12345678-90ab-cdef-1234-567890abcdef",
            "ike:harness_case:87654321-dcba-4321-fedc-ba0987654321",
        ]
        for ike_id in valid_ids:
            with self.subTest(ike_id=ike_id):
                self.assertTrue(validate_ike_id(ike_id))

    def test_invalid_ids(self):
        """Invalid IKE IDs return False."""
        invalid_ids = [
            "",
            "not-an-ike-id",
            "ike:invalid_kind:550e8400-e29b-41d4-a716-446655440000",
            "ike:observation:not-a-uuid",
            "observation:550e8400-e29b-41d4-a716-446655440000",  # missing ike: prefix
            "IKE:OBSERVATION:550e8400-e29b-41d4-a716-446655440000",  # uppercase
        ]
        for ike_id in invalid_ids:
            with self.subTest(ike_id=ike_id):
                self.assertFalse(validate_ike_id(ike_id))


class TestParseIKEId(unittest.TestCase):
    """Tests for parse_ike_id function."""

    def test_parse_valid_id(self):
        """Parse valid IKE ID returns correct kind and UUID."""
        ike_id = "ike:observation:550e8400-e29b-41d4-a716-446655440000"
        kind, uuid_str = parse_ike_id(ike_id)
        self.assertEqual(kind, IKEKind.OBSERVATION)
        self.assertEqual(uuid_str, "550e8400-e29b-41d4-a716-446655440000")

    def test_parse_all_kinds(self):
        """Parse IDs for all v0 object kinds."""
        for kind in IKEKind:
            with self.subTest(kind=kind):
                test_uuid = "12345678-1234-1234-1234-123456789012"
                ike_id = f"ike:{kind.value}:{test_uuid}"
                parsed_kind, parsed_uuid = parse_ike_id(ike_id)
                self.assertEqual(parsed_kind, kind)
                self.assertEqual(parsed_uuid, test_uuid)

    def test_parse_invalid_id(self):
        """Parse invalid IKE ID raises ValueError."""
        invalid_ids = [
            "not-an-ike-id",
            "ike:observation:not-a-uuid",
            "ike:invalid_kind:550e8400-e29b-41d4-a716-446655440000",
        ]
        for ike_id in invalid_ids:
            with self.subTest(ike_id=ike_id):
                with self.assertRaises(ValueError):
                    parse_ike_id(ike_id)


if __name__ == "__main__":
    unittest.main()
