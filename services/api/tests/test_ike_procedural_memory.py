"""
Tests for IKE v0 Procedural Memory Prototype.

Tests verify:
- ProceduralMemory schema validates correctly
- ProceduralMemoryStore persists to human-inspectable JSON files
- Task closure pathway works end-to-end
- No regressions to existing behavior
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from ike_v0.schemas.procedural_memory import ProceduralMemory
from ike_v0.runtime.procedural_memory import (
    ProceduralMemoryStore,
    capture_procedure,
    get_default_store,
    validate_closure_payload,
    capture_procedure_from_payload,
    TaskClosurePayload,
    create_benchmark_closure_payload,
)
from ike_v0.types.ids import generate_ike_id, IKEKind, validate_ike_id


class TestProceduralMemorySchema(unittest.TestCase):
    """Tests for ProceduralMemory schema."""

    def test_create_procedural_memory(self):
        """Create a procedural memory with all required fields."""
        memory = ProceduralMemory(
            id="proc_test_001",
            kind="procedure",
            memory_type="procedure",
            title="Test Procedure",
            lesson="Always validate inputs before processing",
            why_it_mattered="Prevented data corruption in edge cases",
            how_to_apply="Add input validation at the start of each task handler",
            confidence=0.85,
            source_artifact_ref="task_closure_123",
            created_from="task_closure",
            created_at=datetime.now(timezone.utc),
        )

        self.assertEqual(memory.kind, "procedure")
        self.assertEqual(memory.memory_type, "procedure")
        self.assertEqual(memory.title, "Test Procedure")
        self.assertEqual(memory.confidence, 0.85)
        self.assertEqual(memory.created_from, "task_closure")

    def test_procedural_memory_kind_is_literal(self):
        """Kind field is restricted to 'procedure' literal."""
        # Should work with "procedure"
        memory = ProceduralMemory(
            id="proc_test_002",
            kind="procedure",
            memory_type="procedure",
            title="Test",
            lesson="Test lesson",
            why_it_mattered="Test reason",
            how_to_apply="Test application",
            confidence=0.7,
            source_artifact_ref="test_ref",
            created_from="task_closure",
            created_at=datetime.now(timezone.utc),
        )
        self.assertEqual(memory.kind, "procedure")

    def test_procedural_memory_confidence_range(self):
        """Confidence must be between 0.0 and 1.0."""
        # Valid confidence values
        for conf in [0.0, 0.5, 1.0]:
            memory = ProceduralMemory(
                id=f"proc_test_{conf}",
                kind="procedure",
                memory_type="procedure",
                title="Test",
                lesson="Test lesson",
                why_it_mattered="Test reason",
                how_to_apply="Test application",
                confidence=conf,
                source_artifact_ref="test_ref",
                created_at=datetime.now(timezone.utc),
                created_from="task_closure",
            )
            self.assertEqual(memory.confidence, conf)

    def test_procedural_memory_to_dict(self):
        """ProceduralMemory serializes to dictionary correctly."""
        created_at = datetime.now(timezone.utc)
        memory = ProceduralMemory(
            id="proc_test_003",
            kind="procedure",
            memory_type="procedure",
            title="Test Procedure",
            lesson="Test lesson",
            why_it_mattered="Test reason",
            how_to_apply="Test application",
            confidence=0.75,
            source_artifact_ref="task_closure_456",
            created_from="task_closure",
            created_at=created_at,
        )

        data = memory.model_dump(mode="json")

        self.assertEqual(data["id"], "proc_test_003")
        self.assertEqual(data["kind"], "procedure")
        self.assertEqual(data["memory_type"], "procedure")
        self.assertEqual(data["title"], "Test Procedure")
        self.assertEqual(data["confidence"], 0.75)
        self.assertEqual(data["created_from"], "task_closure")
        self.assertIn("created_at", data)

    def test_procedural_memory_created_from_is_literal(self):
        """created_from field is restricted to 'task_closure' in v1."""
        # Should work with "task_closure"
        memory = ProceduralMemory(
            id="proc_test_004",
            kind="procedure",
            memory_type="procedure",
            title="Test",
            lesson="Test lesson",
            why_it_mattered="Test reason",
            how_to_apply="Test application",
            confidence=0.7,
            source_artifact_ref="test_ref",
            created_from="task_closure",
            created_at=datetime.now(timezone.utc),
        )
        self.assertEqual(memory.created_from, "task_closure")


class TestProceduralMemoryStore(unittest.TestCase):
    """Tests for ProceduralMemoryStore."""

    def setUp(self):
        """Set up test fixtures with temporary storage directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.store = ProceduralMemoryStore(storage_dir=Path(self.temp_dir))

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_procedure(self):
        """Create a procedure record."""
        memory = self.store.create_procedure(
            title="Test Procedure",
            lesson="Always validate inputs",
            why_it_mattered="Prevents errors",
            how_to_apply="Validate at entry point",
            confidence=0.8,
            source_artifact_ref="task_001",
        )

        self.assertIsInstance(memory, ProceduralMemory)
        self.assertEqual(memory.kind, "procedure")
        self.assertEqual(memory.memory_type, "procedure")
        self.assertEqual(memory.created_from, "task_closure")
        # ID should use IKE typed format: ike:procedure:{uuid}
        self.assertTrue(memory.id.startswith("ike:procedure:"))
        self.assertTrue(validate_ike_id(memory.id))

    def test_create_procedure_with_custom_id(self):
        """Create a procedure with custom memory ID."""
        memory = self.store.create_procedure(
            title="Test",
            lesson="Lesson",
            why_it_mattered="Reason",
            how_to_apply="Application",
            confidence=0.7,
            source_artifact_ref="task_002",
            memory_id="custom_id_123",
        )

        self.assertEqual(memory.id, "custom_id_123")

    def test_create_procedure_validates_confidence(self):
        """Procedure creation validates confidence range."""
        # Valid confidence
        self.store.create_procedure(
            title="Test",
            lesson="Lesson",
            why_it_mattered="Reason",
            how_to_apply="Application",
            confidence=0.5,
            source_artifact_ref="task_003",
        )

        # Invalid confidence (too high)
        with self.assertRaises(ValueError):
            self.store.create_procedure(
                title="Test",
                lesson="Lesson",
                why_it_mattered="Reason",
                how_to_apply="Application",
                confidence=1.5,
                source_artifact_ref="task_004",
            )

        # Invalid confidence (negative)
        with self.assertRaises(ValueError):
            self.store.create_procedure(
                title="Test",
                lesson="Lesson",
                why_it_mattered="Reason",
                how_to_apply="Application",
                confidence=-0.1,
                source_artifact_ref="task_005",
            )

    def test_persist_writes_json_file(self):
        """Persist writes human-inspectable JSON file."""
        memory = self.store.create_procedure(
            title="Persisted Procedure",
            lesson="Test lesson",
            why_it_mattered="Test reason",
            how_to_apply="Test application",
            confidence=0.75,
            source_artifact_ref="task_006",
        )

        filepath = self.store.persist(memory)

        # File should exist
        self.assertTrue(filepath.exists())
        self.assertEqual(filepath.suffix, ".json")
        # Filename should have colons replaced with underscores
        expected_filename = memory.id.replace(":", "_") + ".json"
        self.assertEqual(filepath.name, expected_filename)

        # File should be valid JSON
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["id"], memory.id)
        self.assertEqual(data["title"], "Persisted Procedure")
        self.assertEqual(data["kind"], "procedure")

    def test_persist_is_human_inspectable(self):
        """Persisted JSON is pretty-printed for human inspection."""
        memory = self.store.create_procedure(
            title="Readable Procedure",
            lesson="Test lesson",
            why_it_mattered="Test reason",
            how_to_apply="Test application",
            confidence=0.8,
            source_artifact_ref="task_007",
        )

        filepath = self.store.persist(memory)

        # Read raw file content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Should be pretty-printed (has newlines and indentation)
        self.assertIn("\n", content)
        self.assertIn("  ", content)  # Indentation

    def test_capture_from_task_closure(self):
        """Capture creates and persists in one call."""
        filepath = self.store.capture_from_task_closure(
            title="Captured Procedure",
            lesson="Test lesson",
            why_it_mattered="Test reason",
            how_to_apply="Test application",
            confidence=0.85,
            source_artifact_ref="task_closure_008",
        )

        # Should return path to persisted file
        self.assertTrue(filepath.exists())

        # Load and verify
        memory = self.store.load(filepath.stem)
        self.assertIsNotNone(memory)
        self.assertEqual(memory.title, "Captured Procedure")
        self.assertEqual(memory.source_artifact_ref, "task_closure_008")

    def test_load_memory(self):
        """Load a persisted memory by ID."""
        # Create and persist
        memory = self.store.create_procedure(
            title="Loadable Procedure",
            lesson="Test lesson",
            why_it_mattered="Test reason",
            how_to_apply="Test application",
            confidence=0.7,
            source_artifact_ref="task_009",
        )
        self.store.persist(memory)

        # Load by ID
        loaded = self.store.load(memory.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, memory.id)
        self.assertEqual(loaded.title, "Loadable Procedure")

    def test_load_nonexistent_memory(self):
        """Load returns None for nonexistent memory."""
        loaded = self.store.load("nonexistent_id")
        self.assertIsNone(loaded)

    def test_list_all_memories(self):
        """List all persisted memories."""
        # Create multiple memories
        for i in range(3):
            self.store.capture_from_task_closure(
                title=f"Procedure {i}",
                lesson=f"Lesson {i}",
                why_it_mattered=f"Reason {i}",
                how_to_apply=f"Application {i}",
                confidence=0.7 + i * 0.1,
                source_artifact_ref=f"task_{i}",
            )

        memories = self.store.list_all()

        self.assertEqual(len(memories), 3)
        titles = [m.title for m in memories]
        self.assertIn("Procedure 0", titles)
        self.assertIn("Procedure 1", titles)
        self.assertIn("Procedure 2", titles)

    def test_list_all_empty_store(self):
        """List returns empty list when store is empty."""
        memories = self.store.list_all()
        self.assertEqual(len(memories), 0)

    def test_count_memories(self):
        """Count returns number of persisted memories."""
        self.assertEqual(self.store.count(), 0)

        self.store.capture_from_task_closure(
            title="Count Test 1",
            lesson="Lesson",
            why_it_mattered="Reason",
            how_to_apply="Application",
            confidence=0.7,
            source_artifact_ref="task_10",
        )
        self.assertEqual(self.store.count(), 1)

        self.store.capture_from_task_closure(
            title="Count Test 2",
            lesson="Lesson",
            why_it_mattered="Reason",
            how_to_apply="Application",
            confidence=0.8,
            source_artifact_ref="task_11",
        )
        self.assertEqual(self.store.count(), 2)

    def test_delete_memory(self):
        """Delete removes a memory from disk."""
        # Create and persist
        memory = self.store.create_procedure(
            title="Deletable Procedure",
            lesson="Test lesson",
            why_it_mattered="Test reason",
            how_to_apply="Test application",
            confidence=0.75,
            source_artifact_ref="task_012",
        )
        filepath = self.store.persist(memory)

        # Verify exists
        self.assertTrue(filepath.exists())

        # Delete
        result = self.store.delete(memory.id)
        self.assertTrue(result)

        # Verify deleted
        self.assertFalse(filepath.exists())
        self.assertIsNone(self.store.load(memory.id))

    def test_delete_nonexistent_memory(self):
        """Delete returns False for nonexistent memory."""
        result = self.store.delete("nonexistent_id")
        self.assertFalse(result)

    def test_storage_dir_created_if_missing(self):
        """Storage directory is created automatically."""
        with tempfile.TemporaryDirectory() as temp_base:
            nested_dir = Path(temp_base) / "nested" / "procedural_memories"
            store = ProceduralMemoryStore(storage_dir=nested_dir)

            # Directory should be created
            self.assertTrue(nested_dir.exists())

            # Should be able to persist
            memory = store.create_procedure(
                title="Test",
                lesson="Lesson",
                why_it_mattered="Reason",
                how_to_apply="Application",
                confidence=0.7,
                source_artifact_ref="task_013",
            )
            filepath = store.persist(memory)
            self.assertTrue(filepath.exists())


class TestConvenienceFunctions(unittest.TestCase):
    """Tests for convenience functions."""

    def test_get_default_store(self):
        """Get default store returns singleton."""
        store1 = get_default_store()
        store2 = get_default_store()

        # Should be same instance (singleton)
        self.assertIs(store1, store2)

    def test_capture_procedure(self):
        """Capture procedure using default store."""
        # Note: This uses the real default store, not a temp directory
        # We just verify it doesn't crash and returns a Path
        filepath = capture_procedure(
            title="Convenience Test",
            lesson="Test lesson",
            why_it_mattered="Test reason",
            how_to_apply="Test application",
            confidence=0.8,
            source_artifact_ref="convenience_task_001",
        )

        self.assertIsInstance(filepath, Path)
        self.assertTrue(filepath.exists())

        # Clean up
        filepath.unlink()


class TestProceduralMemoryV1Prototype(unittest.TestCase):
    """Integration tests for v1 prototype requirements."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.store = ProceduralMemoryStore(storage_dir=Path(self.temp_dir))

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_v1_only_procedure_type(self):
        """V1 prototype supports only 'procedure' memory type."""
        memory = self.store.create_procedure(
            title="V1 Procedure",
            lesson="Test",
            why_it_mattered="Test",
            how_to_apply="Test",
            confidence=0.7,
            source_artifact_ref="task_v1",
        )

        # Only 'procedure' is supported
        self.assertEqual(memory.memory_type, "procedure")
        self.assertEqual(memory.kind, "procedure")

    def test_v1_only_task_closure_trigger(self):
        """V1 prototype triggers only at 'task_closure'."""
        memory = self.store.create_procedure(
            title="V1 Task Closure",
            lesson="Test",
            why_it_mattered="Test",
            how_to_apply="Test",
            confidence=0.7,
            source_artifact_ref="task_v1",
        )

        # Only 'task_closure' trigger in v1
        self.assertEqual(memory.created_from, "task_closure")

    def test_v1_file_based_storage(self):
        """V1 uses file-based local storage."""
        filepath = self.store.capture_from_task_closure(
            title="File-Based Test",
            lesson="Test lesson",
            why_it_mattered="Test reason",
            how_to_apply="Test application",
            confidence=0.75,
            source_artifact_ref="task_v1_file",
        )

        # Verify file exists and is readable
        self.assertTrue(filepath.exists())
        self.assertTrue(filepath.is_file())

        # Verify human-inspectable JSON
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)

        self.assertIn("title", data)
        self.assertIn("lesson", data)
        self.assertIn("how_to_apply", data)

    def test_v1_minimal_record_shape(self):
        """V1 uses minimal structured record per B3 decision."""
        memory = self.store.create_procedure(
            title="Minimal Record",
            lesson="Core lesson",
            why_it_mattered="Why it mattered",
            how_to_apply="How to apply",
            confidence=0.8,
            source_artifact_ref="task_v1_minimal",
        )

        # Verify all required fields from B3 decision
        self.assertTrue(hasattr(memory, "memory_type"))
        self.assertTrue(hasattr(memory, "title"))
        self.assertTrue(hasattr(memory, "lesson"))
        self.assertTrue(hasattr(memory, "why_it_mattered"))
        self.assertTrue(hasattr(memory, "how_to_apply"))
        self.assertTrue(hasattr(memory, "confidence"))
        self.assertTrue(hasattr(memory, "source_artifact_ref"))
        self.assertTrue(hasattr(memory, "created_from"))
        self.assertTrue(hasattr(memory, "created_at"))

    def test_v1_narrow_testable_pathway(self):
        """V1 provides narrow pathway from task_closure to persisted record."""
        # Simulate task closure capture
        filepath = self.store.capture_from_task_closure(
            title="Task Closure Lesson",
            lesson="Always test edge cases early",
            why_it_mattered="Caught bugs before production",
            how_to_apply="Add edge case tests in test plan template",
            confidence=0.9,
            source_artifact_ref="task_closure_benchmark_001",
        )

        # Verify the complete pathway
        self.assertTrue(filepath.exists())

        # Load and verify content
        memory = self.store.load(filepath.stem)
        self.assertIsNotNone(memory)
        self.assertEqual(memory.title, "Task Closure Lesson")
        self.assertEqual(memory.created_from, "task_closure")
        self.assertEqual(memory.source_artifact_ref, "task_closure_benchmark_001")


class TestClosureAdapter(unittest.TestCase):
    """Tests for closure adapter functions - payload validation and pass-through."""

    def test_validate_closure_payload_basic(self):
        """Validate a complete closure payload."""
        payload = {
            "title": "Test Procedure",
            "lesson": "Always validate inputs before processing",
            "why_it_mattered": "Prevented data corruption in edge cases",
            "how_to_apply": "Add input validation at the start of each task handler",
            "confidence": 0.85,
            "source_artifact_ref": "task_closure_123",
        }

        result = validate_closure_payload(payload)

        self.assertIsInstance(result, TaskClosurePayload)
        self.assertEqual(result.title, "Test Procedure")
        self.assertEqual(result.lesson, "Always validate inputs before processing")
        self.assertEqual(result.confidence, 0.85)

    def test_validate_closure_payload_required_fields(self):
        """Validate raises error for missing required fields."""
        required_fields = ["title", "lesson", "why_it_mattered", "how_to_apply", "confidence", "source_artifact_ref"]

        for field in required_fields:
            payload = {
                "title": "Test",
                "lesson": "Lesson",
                "why_it_mattered": "Reason",
                "how_to_apply": "Application",
                "confidence": 0.7,
                "source_artifact_ref": "ref",
            }
            del payload[field]

            with self.assertRaises(ValueError) as context:
                validate_closure_payload(payload)
            self.assertIn(field, str(context.exception))

    def test_validate_closure_payload_confidence_range(self):
        """Validate confidence must be between 0.0 and 1.0."""
        # Valid confidence
        payload = {
            "title": "Test",
            "lesson": "Lesson",
            "why_it_mattered": "Reason",
            "how_to_apply": "Application",
            "confidence": 0.5,
            "source_artifact_ref": "ref",
        }
        result = validate_closure_payload(payload)
        self.assertEqual(result.confidence, 0.5)

        # Too high
        payload["confidence"] = 1.5
        with self.assertRaises(ValueError):
            validate_closure_payload(payload)

        # Negative
        payload["confidence"] = -0.1
        with self.assertRaises(ValueError):
            validate_closure_payload(payload)

    def test_validate_closure_payload_confidence_type(self):
        """Validate confidence must be a number."""
        payload = {
            "title": "Test",
            "lesson": "Lesson",
            "why_it_mattered": "Reason",
            "how_to_apply": "Application",
            "confidence": "not_a_number",
            "source_artifact_ref": "ref",
        }
        with self.assertRaises(ValueError):
            validate_closure_payload(payload)

    def test_validate_closure_payload_string_fields_type(self):
        """Validate string fields must be strings."""
        for field in ["title", "lesson", "why_it_mattered", "how_to_apply", "source_artifact_ref"]:
            payload = {
                "title": "Test",
                "lesson": "Lesson",
                "why_it_mattered": "Reason",
                "how_to_apply": "Application",
                "confidence": 0.7,
                "source_artifact_ref": "ref",
            }
            payload[field] = 123  # Wrong type

            with self.assertRaises(ValueError):
                validate_closure_payload(payload)

    def test_validate_closure_payload_string_fields_not_empty(self):
        """Validate string fields cannot be empty."""
        for field in ["title", "lesson", "why_it_mattered", "how_to_apply", "source_artifact_ref"]:
            payload = {
                "title": "Test",
                "lesson": "Lesson",
                "why_it_mattered": "Reason",
                "how_to_apply": "Application",
                "confidence": 0.7,
                "source_artifact_ref": "ref",
            }
            payload[field] = ""  # Empty string

            with self.assertRaises(ValueError):
                validate_closure_payload(payload)

            payload[field] = "   "  # Whitespace only
            with self.assertRaises(ValueError):
                validate_closure_payload(payload)

    def test_validate_closure_payload_normalizes_confidence(self):
        """Validate converts confidence to float."""
        payload = {
            "title": "Test",
            "lesson": "Lesson",
            "why_it_mattered": "Reason",
            "how_to_apply": "Application",
            "confidence": 1,  # Integer
            "source_artifact_ref": "ref",
        }
        result = validate_closure_payload(payload)
        self.assertIsInstance(result.confidence, float)
        self.assertEqual(result.confidence, 1.0)

    def test_capture_procedure_from_payload(self):
        """Capture procedure from payload end-to-end."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProceduralMemoryStore(storage_dir=Path(temp_dir))
            import ike_v0.runtime.procedural_memory as pm
            original_store = pm._default_store
            pm._default_store = store

            try:
                payload = {
                    "title": "Payload Test Procedure",
                    "lesson": "Explicit lesson from closure",
                    "why_it_mattered": "Explicit reason",
                    "how_to_apply": "Explicit guidance",
                    "confidence": 0.9,
                    "source_artifact_ref": "ike_chain:explicit_001",
                }

                filepath = capture_procedure_from_payload(payload)

                self.assertTrue(filepath.exists())

                # Load and verify content matches payload exactly
                filename = filepath.name
                memory_id = filename.replace("_", ":", 2)[:-5]
                memory = store.load(memory_id)
                self.assertIsNotNone(memory)
                self.assertEqual(memory.title, "Payload Test Procedure")
                self.assertEqual(memory.lesson, "Explicit lesson from closure")
                self.assertEqual(memory.why_it_mattered, "Explicit reason")
                self.assertEqual(memory.how_to_apply, "Explicit guidance")
                self.assertEqual(memory.confidence, 0.9)
            finally:
                pm._default_store = original_store

    def test_capture_procedure_from_payload_with_custom_id(self):
        """Capture procedure from payload with custom memory ID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProceduralMemoryStore(storage_dir=Path(temp_dir))
            import ike_v0.runtime.procedural_memory as pm
            original_store = pm._default_store
            pm._default_store = store

            try:
                payload = {
                    "title": "Test",
                    "lesson": "Lesson",
                    "why_it_mattered": "Reason",
                    "how_to_apply": "Application",
                    "confidence": 0.7,
                    "source_artifact_ref": "ref",
                }

                custom_id = "ike:procedure:12345678-1234-1234-1234-123456789012"
                filepath = capture_procedure_from_payload(payload, memory_id=custom_id)

                # Verify custom ID was used
                self.assertTrue(filepath.name.startswith("ike_procedure_12345678"))
            finally:
                pm._default_store = original_store

    def test_capture_procedure_from_payload_preserves_exact_content(self):
        """Adapter does not modify or derive content - exact pass-through."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProceduralMemoryStore(storage_dir=Path(temp_dir))
            import ike_v0.runtime.procedural_memory as pm
            original_store = pm._default_store
            pm._default_store = store

            try:
                # Specific content that should not be modified
                payload = {
                    "title": "My Exact Title",
                    "lesson": "My Exact Lesson Text",
                    "why_it_mattered": "My Exact Reason",
                    "how_to_apply": "My Exact Guidance",
                    "confidence": 0.73,
                    "source_artifact_ref": "my_ref",
                }

                filepath = capture_procedure_from_payload(payload)

                # Load and verify exact content preserved
                filename = filepath.name
                memory_id = filename.replace("_", ":", 2)[:-5]
                memory = store.load(memory_id)

                self.assertEqual(memory.title, payload["title"])
                self.assertEqual(memory.lesson, payload["lesson"])
                self.assertEqual(memory.why_it_mattered, payload["why_it_mattered"])
                self.assertEqual(memory.how_to_apply, payload["how_to_apply"])
                self.assertEqual(memory.confidence, payload["confidence"])
            finally:
                pm._default_store = original_store


class TestBenchmarkClosurePayload(unittest.TestCase):
    """Tests for benchmark closure memory payload helper."""

    def test_create_benchmark_closure_payload_basic(self):
        """Create benchmark closure payload with explicit fields."""
        payload = create_benchmark_closure_payload(
            title="Three-tier audit structure",
            lesson="Pre/in/post-action tiers provide concrete evaluation workflow",
            why_it_mattered="Enables structured visibility into agent operations",
            how_to_apply="Apply three-tier structure to evolution-layer evaluations",
            confidence=0.75,
            source_artifact_ref="SR-HARNESS-B4S4-8098e069",
        )

        self.assertEqual(payload["title"], "Three-tier audit structure")
        self.assertEqual(payload["lesson"], "Pre/in/post-action tiers provide concrete evaluation workflow")
        self.assertEqual(payload["why_it_mattered"], "Enables structured visibility into agent operations")
        self.assertEqual(payload["how_to_apply"], "Apply three-tier structure to evolution-layer evaluations")
        self.assertEqual(payload["confidence"], 0.75)
        self.assertEqual(payload["source_artifact_ref"], "SR-HARNESS-B4S4-8098e069")

    def test_create_benchmark_closure_payload_returns_dict(self):
        """Create returns a dict suitable for capture_procedure_from_payload."""
        payload = create_benchmark_closure_payload(
            title="Test",
            lesson="Test lesson",
            why_it_mattered="Test reason",
            how_to_apply="Test guidance",
            confidence=0.8,
            source_artifact_ref="test_ref",
        )

        self.assertIsInstance(payload, dict)
        self.assertIn("title", payload)
        self.assertIn("lesson", payload)
        self.assertIn("why_it_mattered", payload)
        self.assertIn("how_to_apply", payload)
        self.assertIn("confidence", payload)
        self.assertIn("source_artifact_ref", payload)

    def test_create_benchmark_closure_payload_with_real_example(self):
        """Create payload with realistic benchmark closure example."""
        payload = create_benchmark_closure_payload(
            title="Nightly explicit audits with metrics",
            lesson="13 core metrics with no-silent-pass reporting provides reusable evaluation pattern",
            why_it_mattered="Demonstrates concrete approach for evaluation visibility and accountability",
            how_to_apply="Adopt explicit metrics reporting pattern for IKE evolution evaluations",
            confidence=0.7,
            source_artifact_ref="SR-HARNESS-B4S4-8098e069",
        )

        # Verify payload is valid for capture
        validated = validate_closure_payload(payload)
        self.assertIsInstance(validated, TaskClosurePayload)

    def test_create_benchmark_closure_payload_compatible_with_capture(self):
        """Payload can be passed directly to capture_procedure_from_payload."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProceduralMemoryStore(storage_dir=Path(temp_dir))
            import ike_v0.runtime.procedural_memory as pm
            original_store = pm._default_store
            pm._default_store = store

            try:
                payload = create_benchmark_closure_payload(
                    title="Benchmark Test",
                    lesson="Test lesson from benchmark",
                    why_it_mattered="Test reason",
                    how_to_apply="Test guidance",
                    confidence=0.8,
                    source_artifact_ref="SR-TEST-001",
                )

                filepath = capture_procedure_from_payload(payload)

                self.assertTrue(filepath.exists())

                # Verify content
                filename = filepath.name
                memory_id = filename.replace("_", ":", 2)[:-5]
                memory = store.load(memory_id)
                self.assertEqual(memory.title, "Benchmark Test")
                self.assertEqual(memory.source_artifact_ref, "SR-TEST-001")
            finally:
                pm._default_store = original_store


if __name__ == "__main__":
    unittest.main()
