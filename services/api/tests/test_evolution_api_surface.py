import importlib.util
import sys
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


api_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(api_dir))


def load_evolution_router_module():
    router_path = api_dir / "routers" / "evolution.py"
    spec = importlib.util.spec_from_file_location(
        "evolution_router_test_module_api_surface", router_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evolution_module = load_evolution_router_module()
evolution_router = evolution_module.router

test_app = FastAPI(title="Evolution API Surface Test API")
test_app.include_router(evolution_router, prefix="/api/evolution")


class EvolutionApiSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(test_app)

    def test_list_evolution_contexts_returns_empty_list(self):
        """GET /contexts returns empty list when no durable context source exists."""
        response = self.client.get("/api/evolution/contexts")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["contexts"], [])
        self.assertIn("runtime dashboard support surface", data["advisory_note"])
        self.assertIn("non-canonical", data["advisory_note"])

    def test_get_evolution_context_by_id_returns_404(self):
        """GET /contexts/{context_id} returns 404 when context not found."""
        response = self.client.get("/api/evolution/contexts/test-context-id")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["detail"]["error"], "Context not found")
        self.assertEqual(data["detail"]["context_id"], "test-context-id")
        self.assertIn("runtime dashboard support surface", data["detail"]["advisory_note"])

    def test_get_evolution_context_with_special_chars_returns_404(self):
        """GET /contexts with special characters in ID returns 404."""
        response = self.client.get("/api/evolution/contexts/context-with-special-chars-123")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["detail"]["error"], "Context not found")

    def test_list_task_memories_returns_empty_list(self):
        """GET /memories/task returns empty list when no durable task-memory source exists."""
        response = self.client.get("/api/evolution/memories/task")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["memories"], [])
        self.assertIn("runtime dashboard support surface", data["advisory_note"])
        self.assertIn("non-canonical", data["advisory_note"])

    def test_list_procedural_memories_returns_empty_list(self):
        """GET /memories/procedural returns empty list when no durable procedural-memory source exists."""
        response = self.client.get("/api/evolution/memories/procedural")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["memories"], [])
        self.assertIn("runtime dashboard support surface", data["advisory_note"])
        self.assertIn("non-canonical", data["advisory_note"])

    def test_all_new_endpoints_return_valid_json(self):
        """All four new endpoints return valid JSON without 404 for list endpoints."""
        endpoints = [
            "/api/evolution/contexts",
            "/api/evolution/memories/task",
            "/api/evolution/memories/procedural",
        ]
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, dict)

    def test_contexts_response_schema_matches_frontend_expectations(self):
        """Contexts response schema matches frontend TypeScript interface."""
        response = self.client.get("/api/evolution/contexts")
        data = response.json()
        # Verify response has expected structure
        self.assertIn("contexts", data)
        self.assertIn("advisory_note", data)
        # Empty contexts list
        self.assertEqual(len(data["contexts"]), 0)

    def test_task_memories_response_schema_matches_frontend_expectations(self):
        """Task memories response schema matches frontend TypeScript interface."""
        response = self.client.get("/api/evolution/memories/task")
        data = response.json()
        # Verify response has expected structure
        self.assertIn("memories", data)
        self.assertIn("advisory_note", data)
        # Empty memories list
        self.assertEqual(len(data["memories"]), 0)

    def test_procedural_memories_response_schema_matches_frontend_expectations(self):
        """Procedural memories response schema matches frontend TypeScript interface."""
        response = self.client.get("/api/evolution/memories/procedural")
        data = response.json()
        # Verify response has expected structure
        self.assertIn("memories", data)
        self.assertIn("advisory_note", data)
        # Empty memories list
        self.assertEqual(len(data["memories"]), 0)

    def test_all_new_endpoints_are_registered(self):
        """All four new endpoints are properly registered and respond."""
        # Verify new endpoints exist by checking they don't 404
        new_endpoints = [
            "/api/evolution/contexts",
            "/api/evolution/memories/task",
            "/api/evolution/memories/procedural",
        ]
        for endpoint in new_endpoints:
            response = self.client.get(endpoint)
            # All list endpoints should return 200
            self.assertEqual(response.status_code, 200)

        # Detail endpoint should return 404 (deterministic for any ID)
        detail_response = self.client.get("/api/evolution/contexts/test-id")
        self.assertEqual(detail_response.status_code, 404)

    def test_advisory_notes_are_explicit_about_runtime_surface(self):
        """Advisory notes explicitly state these are runtime dashboard surfaces."""
        endpoints = [
            "/api/evolution/contexts",
            "/api/evolution/memories/task",
            "/api/evolution/memories/procedural",
        ]
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            data = response.json()
            advisory = data["advisory_note"]
            # Check explicit wording
            self.assertIn("runtime dashboard support surface", advisory)
            self.assertIn("non-canonical", advisory)
            # Each endpoint mentions it's not a durable source
            self.assertIn("Not a durable", advisory)

    def test_detail_endpoint_404_is_deterministic(self):
        """Detail endpoint behavior is deterministic - always 404 for any ID."""
        # Test multiple IDs to verify deterministic 404 behavior
        test_ids = [
            "simple-id",
            "uuid-like-123e4567-e89b-12d3-a456-426614174000",
            "evolution-context-1",
            "source_intelligence_context",
        ]
        for test_id in test_ids:
            response = self.client.get(f"/api/evolution/contexts/{test_id}")
            self.assertEqual(response.status_code, 404)
            data = response.json()
            self.assertEqual(data["detail"]["error"], "Context not found")
            self.assertEqual(data["detail"]["context_id"], test_id)


if __name__ == "__main__":
    unittest.main()