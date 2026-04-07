"""
Tests for IKE v0 Preview API endpoints.

Tests verify:
- Decision preview endpoint creates valid Decision objects
- HarnessCase preview endpoint creates valid HarnessCase objects
- Response envelope includes correct provisional/experimental metadata
- Response headers are set correctly
- Endpoints use existing mappers correctly

Note: Tests use isolated FastAPI app and import router module directly
to avoid heavy dependency imports from other routers.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for direct imports
api_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(api_dir))

from fastapi import FastAPI
from fastapi.testclient import TestClient


# Import router directly from module file to avoid routers/__init__.py chain
# This bypasses the heavy imports from other routers
def load_ike_v0_router():
    """Load ike_v0 router module directly."""
    import importlib.util
    router_path = api_dir / "routers" / "ike_v0.py"
    spec = importlib.util.spec_from_file_location("ike_v0_router", router_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.router


ike_v0_router = load_ike_v0_router()

# Create isolated test app with only the IKE v0 router
test_app = FastAPI(title="IKE v0 Test API")
test_app.include_router(ike_v0_router, prefix="/api")


class TestIKERouter(unittest.TestCase):
    """Tests for IKE v0 router endpoints."""

    def setUp(self):
        """Set up test client."""
        self.client = TestClient(test_app)

    def test_decision_preview_basic(self):
        """Decision preview endpoint creates valid response."""
        payload = {
            "task_ref": "ike:research_task:12345678-1234-1234-1234-123456789012",
            "experiment_refs": [
                "ike:experiment:12345678-1234-1234-1234-123456789012"
            ],
            "decision_outcome": "adopt",
            "rationale": "The experiment results support the hypothesis",
        }

        response = self.client.post("/api/ike/v0/decisions/preview", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify envelope structure
        self.assertIn("ref", data)
        self.assertIn("data", data)

        # Verify ref metadata
        ref = data["ref"]
        self.assertTrue(ref["id"].startswith("ike:decision:"))
        self.assertEqual(ref["kind"], "decision")
        self.assertEqual(ref["id_scope"], "provisional")
        self.assertEqual(ref["stability"], "experimental")
        self.assertIsNone(ref["permalink"])

        # Verify data contains decision fields
        decision_data = data["data"]
        self.assertEqual(decision_data["kind"], "decision")
        self.assertEqual(decision_data["task_ref"], payload["task_ref"])
        self.assertEqual(decision_data["decision_outcome"], payload["decision_outcome"])
        self.assertEqual(decision_data["decision_type"], "experiment_evaluation")

    def test_decision_preview_headers(self):
        """Decision preview endpoint sets correct headers."""
        payload = {
            "task_ref": "ike:research_task:12345678-1234-1234-1234-123456789012",
            "experiment_refs": [],
            "decision_outcome": "adopt",
            "rationale": "Test",
        }

        response = self.client.post("/api/ike/v0/decisions/preview", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-IKE-Version"), "v0-experimental")
        self.assertEqual(response.headers.get("Cache-Control"), "no-store")

    def test_decision_preview_with_optional_fields(self):
        """Decision preview handles optional fields."""
        payload = {
            "task_ref": "ike:research_task:12345678-1234-1234-1234-123456789012",
            "experiment_refs": [
                "ike:experiment:12345678-1234-1234-1234-123456789012",
                "ike:experiment:12345678-1234-1234-1234-123456789013",
            ],
            "decision_outcome": "reject",
            "rationale": "The experiment results do not support the hypothesis",
            "review_required": True,
            "evidence_refs": ["ike:observation:12345678-1234-1234-1234-123456789012"],
        }

        response = self.client.post("/api/ike/v0/decisions/preview", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        decision_data = data["data"]

        self.assertEqual(decision_data["review_required"], True)
        self.assertEqual(decision_data["evidence_refs"], payload["evidence_refs"])
        self.assertEqual(len(decision_data["experiment_refs"]), 2)

    def test_decision_preview_all_outcomes(self):
        """Decision preview accepts all valid IKE v0 outcomes."""
        valid_outcomes = ["adopt", "reject", "defer", "escalate"]

        for outcome in valid_outcomes:
            with self.subTest(outcome=outcome):
                payload = {
                    "task_ref": "ike:research_task:12345678-1234-1234-1234-123456789012",
                    "experiment_refs": [],
                    "decision_outcome": outcome,
                    "rationale": "Test",
                }

                response = self.client.post("/api/ike/v0/decisions/preview", json=payload)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["data"]["decision_outcome"], outcome)

    def test_harness_case_preview_basic(self):
        """HarnessCase preview endpoint creates valid response."""
        payload = {
            "subject_refs": [
                "ike:research_task:12345678-1234-1234-1234-123456789012",
                "ike:experiment:12345678-1234-1234-1234-123456789012",
                "ike:decision:12345678-1234-1234-1234-123456789012",
            ],
            "expected_behavior": {
                "has_task": True,
                "has_experiment": True,
                "has_decision": True,
            },
            "actual_behavior": {
                "has_task": True,
                "has_experiment": True,
                "has_decision": True,
            },
            "pass_fail": True,
        }

        response = self.client.post("/api/ike/v0/harness-cases/preview", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify envelope structure
        self.assertIn("ref", data)
        self.assertIn("data", data)

        # Verify ref metadata
        ref = data["ref"]
        self.assertTrue(ref["id"].startswith("ike:harness_case:"))
        self.assertEqual(ref["kind"], "harness_case")
        self.assertEqual(ref["id_scope"], "provisional")
        self.assertEqual(ref["stability"], "experimental")
        self.assertIsNone(ref["permalink"])

        # Verify data contains harness case fields
        hc_data = data["data"]
        self.assertEqual(hc_data["kind"], "harness_case")
        self.assertEqual(hc_data["case_type"], "loop_completeness")
        self.assertEqual(hc_data["pass_fail"], True)
        self.assertEqual(len(hc_data["subject_refs"]), 3)

    def test_harness_case_preview_headers(self):
        """HarnessCase preview endpoint sets correct headers."""
        payload = {
            "subject_refs": [],
            "expected_behavior": {},
            "actual_behavior": {},
            "pass_fail": True,
        }

        response = self.client.post("/api/ike/v0/harness-cases/preview", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-IKE-Version"), "v0-experimental")
        self.assertEqual(response.headers.get("Cache-Control"), "no-store")

    def test_harness_case_preview_fail_case(self):
        """HarnessCase preview handles failing case."""
        payload = {
            "subject_refs": [],
            "expected_behavior": {"has_task": True},
            "actual_behavior": {"has_task": False},
            "pass_fail": False,
            "notes": "Loop incomplete - missing task",
        }

        response = self.client.post("/api/ike/v0/harness-cases/preview", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        hc_data = data["data"]

        self.assertEqual(hc_data["pass_fail"], False)
        self.assertEqual(hc_data["notes"], "Loop incomplete - missing task")
        self.assertEqual(hc_data["status"], "open")  # Fail case -> open status

    def test_harness_case_preview_with_evidence(self):
        """HarnessCase preview handles evidence refs."""
        payload = {
            "subject_refs": [],
            "expected_behavior": {},
            "actual_behavior": {},
            "pass_fail": True,
            "evidence_refs": [
                "ike:observation:12345678-1234-1234-1234-123456789012",
                "ike:observation:12345678-1234-1234-1234-123456789013",
            ],
        }

        response = self.client.post("/api/ike/v0/harness-cases/preview", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        hc_data = data["data"]

        self.assertEqual(hc_data["evidence_refs"], payload["evidence_refs"])

    def test_harness_case_preview_provenance(self):
        """HarnessCase preview includes correct provenance."""
        payload = {
            "subject_refs": ["ike:research_task:12345678-1234-1234-1234-123456789012"],
            "expected_behavior": {},
            "actual_behavior": {},
            "pass_fail": True,
        }

        response = self.client.post("/api/ike/v0/harness-cases/preview", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        hc_data = data["data"]

        provenance = hc_data.get("provenance", {})
        self.assertEqual(provenance.get("case_type"), "loop_completeness")
        self.assertEqual(provenance.get("subject_count"), 1)
        self.assertEqual(provenance.get("mapper"), "create_loop_completeness_harness_case")

    def test_decision_preview_provenance(self):
        """Decision preview includes correct provenance."""
        payload = {
            "task_ref": "ike:research_task:12345678-1234-1234-1234-123456789012",
            "experiment_refs": [
                "ike:experiment:12345678-1234-1234-1234-123456789012",
                "ike:experiment:12345678-1234-1234-1234-123456789013",
            ],
            "decision_outcome": "adopt",
            "rationale": "Test",
        }

        response = self.client.post("/api/ike/v0/decisions/preview", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        decision_data = data["data"]

        provenance = decision_data.get("provenance", {})
        self.assertEqual(provenance.get("decision_type"), "experiment_evaluation")
        self.assertEqual(provenance.get("experiment_count"), 2)
        self.assertEqual(provenance.get("mapper"), "create_experiment_evaluation_decision")

    def test_decision_preview_invalid_outcome_returns_422(self):
        """Decision preview returns 422 for invalid decision_outcome values."""
        invalid_outcomes = ["approved", "rejected", "needs_revision", "invalid", ""]

        for invalid_outcome in invalid_outcomes:
            with self.subTest(invalid_outcome=invalid_outcome):
                payload = {
                    "task_ref": "ike:research_task:12345678-1234-1234-1234-123456789012",
                    "experiment_refs": [],
                    "decision_outcome": invalid_outcome,
                    "rationale": "Test",
                }

                response = self.client.post("/api/ike/v0/decisions/preview", json=payload)

                self.assertEqual(response.status_code, 422)

    def test_observation_inspect_basic(self):
        """Observation inspect endpoint creates valid response."""
        payload = {
            "feed_item": {
                "id": "feed-123",
                "source_id": "source-abc",
                "title": "Test Feed Item",
                "summary": "Test summary",
                "url": "https://example.com/article",
                "fetched_at": "2024-01-01T00:00:00Z",
            }
        }

        response = self.client.post("/api/ike/v0/observations/inspect", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify envelope structure
        self.assertIn("ref", data)
        self.assertIn("data", data)

        # Verify ref metadata
        ref = data["ref"]
        self.assertTrue(ref["id"].startswith("ike:observation:"))
        self.assertEqual(ref["kind"], "observation")
        self.assertEqual(ref["id_scope"], "provisional")
        self.assertEqual(ref["stability"], "experimental")
        self.assertIsNone(ref["permalink"])

        # Verify data contains observation fields
        obs_data = data["data"]
        self.assertEqual(obs_data["kind"], "observation")
        self.assertEqual(obs_data["title"], "Test Feed Item")
        self.assertEqual(obs_data["summary"], "Test summary")
        self.assertEqual(obs_data["source_ref"], "source-abc")

    def test_observation_inspect_headers(self):
        """Observation inspect endpoint sets correct headers."""
        payload = {
            "feed_item": {
                "source_id": "source-abc",
                "title": "Test",
                "fetched_at": "2024-01-01T00:00:00Z",
            }
        }

        response = self.client.post("/api/ike/v0/observations/inspect", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-IKE-Version"), "v0-experimental")
        self.assertEqual(response.headers.get("Cache-Control"), "no-store")

    def test_observation_inspect_with_raw_ingest(self):
        """Observation inspect handles optional raw_ingest."""
        payload = {
            "feed_item": {
                "source_id": "source-abc",
                "title": "Test",
                "fetched_at": "2024-01-01T00:00:00Z",
            },
            "raw_ingest": {"object_key": "s3://bucket/object-123"},
        }

        response = self.client.post("/api/ike/v0/observations/inspect", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        obs_data = data["data"]

        self.assertEqual(obs_data["raw_ref"], "s3://bucket/object-123")
        self.assertIn("s3://bucket/object-123", obs_data["references"])

    def test_observation_inspect_with_signal_type(self):
        """Observation inspect handles custom signal_type."""
        payload = {
            "feed_item": {
                "source_id": "source-abc",
                "title": "Test",
                "fetched_at": "2024-01-01T00:00:00Z",
            },
            "signal_type": "custom_signal",
        }

        response = self.client.post("/api/ike/v0/observations/inspect", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        obs_data = data["data"]

        self.assertEqual(obs_data["signal_type"], "custom_signal")

    def test_observation_inspect_provenance(self):
        """Observation inspect includes correct provenance."""
        payload = {
            "feed_item": {
                "source_id": "source-abc",
                "title": "Test",
                "fetched_at": "2024-01-01T00:00:00Z",
            }
        }

        response = self.client.post("/api/ike/v0/observations/inspect", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        obs_data = data["data"]

        provenance = obs_data.get("provenance", {})
        self.assertEqual(provenance.get("mapper"), "map_feed_item_to_observation")
        self.assertEqual(provenance.get("source_type"), "feed_item")

    def test_observation_inspect_confidence_from_importance(self):
        """Observation inspect derives confidence from importance."""
        payload = {
            "feed_item": {
                "source_id": "source-abc",
                "title": "Test",
                "fetched_at": "2024-01-01T00:00:00Z",
                "importance": 0.8,
            }
        }

        response = self.client.post("/api/ike/v0/observations/inspect", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        obs_data = data["data"]

        self.assertEqual(obs_data["confidence"], 0.8)

    def test_chain_inspect_returns_404_for_missing_artifact(self):
        """Chain inspect returns 404 with helpful message for missing artifact."""
        # Import get_db inside test to avoid heavy import chain at module level
        from db import get_db
        
        # Override DB dependency to return None (artifact not found)
        async def mock_get_db():
            # Create a mock async session that returns None for any query
            class MockResult:
                def scalar_one_or_none(self):
                    return None
            class MockDB:
                async def execute(self, query):
                    return MockResult()
            return MockDB()
        
        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            payload = {
                "artifact_id": "00000000-0000-0000-0000-000000000000",
            }

            response = self.client.post("/api/ike/v0/chains/inspect", json=payload)

            self.assertEqual(response.status_code, 404)
            detail = response.json()["detail"]
            self.assertIn("not found", detail.lower())
            self.assertIn("TaskArtifact", detail)
        finally:
            test_app.dependency_overrides.clear()


if __name__ == "__main__":
    unittest.main()
