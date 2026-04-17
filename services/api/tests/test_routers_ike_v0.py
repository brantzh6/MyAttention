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
from unittest.mock import AsyncMock, patch

# Add parent directory to path for direct imports
api_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(api_dir))

REPO_ROOT = api_dir.parents[1]
PREFERRED_VENV_HINT = str(REPO_ROOT / ".venv" / "Scripts" / "python.exe").replace("/", "\\").lower()
REPO_UVICORN_HINT = str(REPO_ROOT / ".venv" / "Scripts" / "uvicorn.exe").replace("/", "\\").lower()

from fastapi import FastAPI
from fastapi.testclient import TestClient
from runtime.project_surface import ProjectRuntimeReadSurface
from runtime.service_preflight import (
    ApiHealthInfo,
    PortOwnershipInfo,
    PreflightResult,
    PreflightStatus,
)
from runtime.leases import LeaseRecord
from runtime.state_machine import TaskStatus
from runtime.task_lifecycle import LifecycleProofResult
from runtime.db_backed_lifecycle_proof import DBBackedLifecycleProofResult


# Import router directly from module file to avoid routers/__init__.py chain
# This bypasses the heavy imports from other routers
def load_ike_v0_router():
    """Load ike_v0 router module directly."""
    import importlib.util
    router_path = api_dir / "routers" / "ike_v0.py"
    spec = importlib.util.spec_from_file_location("ike_v0_router", router_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ike_v0_module = load_ike_v0_router()
ike_v0_router = ike_v0_module.router

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

    def test_runtime_project_surface_inspect_basic(self):
        """Runtime project surface inspect returns provisional runtime surface."""
        from db import get_db

        surface = ProjectRuntimeReadSurface(
            project_id="11111111-1111-1111-1111-111111111111",
            project_key="runtime-mainline",
            title="Runtime Mainline",
            status="active",
            current_phase="R2-C",
            priority=1,
            current_work_context_id=None,
            current_focus="Bridge runtime truth into visible surface",
            blockers_summary=None,
            next_steps_summary="Expose a narrow runtime card",
            active_tasks=[],
            waiting_tasks=[],
            latest_decision=None,
            trusted_packets=[],
            metadata={
                "source": "runtime_truth_only",
                "has_current_context": False,
            },
        )

        class MockDB:
            async def run_sync(self, fn):
                return surface

        async def mock_get_db():
            return MockDB()

        original_builder = ike_v0_module.build_latest_project_runtime_read_surface
        ike_v0_module.build_latest_project_runtime_read_surface = (
            lambda sync_session, project_key=None: surface
        )
        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.post("/api/ike/v0/runtime/project-surface/inspect", json={})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(response.headers.get("X-IKE-Version"), "v0-experimental")
            self.assertEqual(data["ref"]["kind"], "runtime_project_surface")
            self.assertEqual(data["data"]["project_key"], "runtime-mainline")
            self.assertEqual(data["data"]["metadata"]["source"], "runtime_truth_only")
        finally:
            ike_v0_module.build_latest_project_runtime_read_surface = original_builder
            test_app.dependency_overrides.clear()

    def test_runtime_project_surface_inspect_returns_404_when_unavailable(self):
        """Runtime project surface inspect returns bounded 404 when no project exists."""
        from db import get_db

        class MockDB:
            async def run_sync(self, fn):
                return None

        async def mock_get_db():
            return MockDB()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.post("/api/ike/v0/runtime/project-surface/inspect", json={})
            self.assertEqual(response.status_code, 404)
            self.assertIn("Runtime project surface not available", response.json()["detail"])
        finally:
            test_app.dependency_overrides.clear()

    def test_runtime_project_surface_bootstrap_basic(self):
        """Runtime project surface bootstrap returns provisional runtime surface."""
        from db import get_db

        surface = ProjectRuntimeReadSurface(
            project_id="22222222-2222-2222-2222-222222222222",
            project_key="runtime-bootstrap",
            title="Runtime Bootstrap",
            status="active",
            current_phase="R2-D",
            priority=1,
            current_work_context_id=None,
            current_focus=None,
            blockers_summary=None,
            next_steps_summary=None,
            active_tasks=[],
            waiting_tasks=[],
            latest_decision=None,
            trusted_packets=[],
            metadata={
                "source": "runtime_truth_only",
                "bootstrap_created": True,
                "bootstrap_source": "explicit_request",
            },
        )

        class MockDB:
            async def run_sync(self, fn):
                return surface

        async def mock_get_db():
            return MockDB()

        original_builder = ike_v0_module.bootstrap_runtime_project_surface
        ike_v0_module.bootstrap_runtime_project_surface = (
            lambda sync_session, project_key, title, current_phase=None, priority=1: surface
        )
        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.post(
                "/api/ike/v0/runtime/project-surface/bootstrap",
                json={
                    "project_key": "runtime-bootstrap",
                    "title": "Runtime Bootstrap",
                    "current_phase": "R2-D",
                },
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["data"]["project_key"], "runtime-bootstrap")
            self.assertEqual(data["data"]["metadata"]["bootstrap_created"], True)
            self.assertEqual(response.headers.get("X-IKE-Version"), "v0-experimental")
        finally:
            ike_v0_module.bootstrap_runtime_project_surface = original_builder
            test_app.dependency_overrides.clear()

    def test_runtime_benchmark_candidate_import_basic(self):
        """Benchmark candidate import returns a provisional runtime packet."""
        from db import get_db

        class MockStatus:
            value = "pending_review"

        class MockCreatedByKind:
            value = "runtime"

        class MockPacket:
            memory_packet_id = "33333333-3333-3333-3333-333333333333"
            project_id = "22222222-2222-2222-2222-222222222222"
            packet_type = "benchmark_procedural_candidate"
            status = MockStatus()
            title = "Candidate packet"
            summary = "Candidate summary"
            created_by_kind = MockCreatedByKind()
            created_by_id = "benchmark_bridge"
            storage_ref = None

        class MockDB:
            async def run_sync(self, fn):
                return MockPacket()

        async def mock_get_db():
            return MockDB()

        original_importer = ike_v0_module.import_benchmark_candidate_into_runtime_project
        ike_v0_module.import_benchmark_candidate_into_runtime_project = (
            lambda sync_session, project_key, payload: MockPacket()
        )
        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.post(
                "/api/ike/v0/runtime/benchmark-candidate/import",
                json={
            "project_key": "ike-runtime-mainline",
                    "candidate_payload": {
                        "title": "Candidate packet",
                        "lesson": "Lesson",
                        "why_it_mattered": "Why it mattered",
                        "how_to_apply": "How to apply",
                        "confidence": 0.7,
                        "source_artifact_ref": "artifact-ref",
                        "status": "candidate",
                        "derived_from": {"study_result_ref": "SR-1"},
                        "notes": [],
                    },
                },
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(response.headers.get("X-IKE-Version"), "v0-experimental")
            self.assertEqual(data["ref"]["kind"], "runtime_memory_packet")
            self.assertEqual(data["data"]["packet_type"], "benchmark_procedural_candidate")
            self.assertEqual(data["data"]["status"], "pending_review")
        finally:
            ike_v0_module.import_benchmark_candidate_into_runtime_project = original_importer
            test_app.dependency_overrides.clear()

    def test_runtime_benchmark_candidate_import_returns_400_for_bridge_error(self):
        """Benchmark candidate import returns bounded 400 for invalid payloads."""
        from db import get_db
        from runtime.benchmark_bridge import BenchmarkBridgeError

        class MockDB:
            async def run_sync(self, fn):
                raise BenchmarkBridgeError("Benchmark bridge requires valid reviewed payload.")

        async def mock_get_db():
            return MockDB()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.post(
                "/api/ike/v0/runtime/benchmark-candidate/import",
                json={
            "project_key": "ike-runtime-mainline",
                    "candidate_payload": {},
                },
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn("Benchmark bridge", response.json()["detail"])
        finally:
            test_app.dependency_overrides.clear()

    def test_runtime_service_preflight_inspect_basic(self):
        """Runtime service preflight inspect returns provisional operational result."""
        result = PreflightResult(
            status=PreflightStatus.AMBIGUOUS,
            timestamp="2026-04-08T15:51:11+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8000/health",
                is_healthy=True,
                response_status=200,
                response_body={"status": "healthy"},
                response_time_ms=123.4,
            ),
            port_ownership=PortOwnershipInfo(
                port=8000,
                listening_processes=[
                    {"pid": 1, "name": "python.exe"},
                    {"pid": 2, "name": "python.exe"},
                ],
                unique_count=2,
                is_clear=False,
                inspection_method="windows_powershell",
            ),
            summary="Ambiguous: 2 processes claim port 8000",
            details={"listening_process_count": 2},
        )

        with patch.object(ike_v0_module, "run_preflight", AsyncMock(return_value=result)):
            response = self.client.post("/api/ike/v0/runtime/service-preflight/inspect")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get("X-IKE-Version"), "v0-experimental")
            data = response.json()
            self.assertEqual(data["ref"]["kind"], "runtime_service_preflight")
            self.assertEqual(data["data"]["status"], "ambiguous")
            self.assertEqual(data["data"]["port_ownership"]["unique_count"], 2)
            self.assertEqual(data["data"]["summary"], "Ambiguous: 2 processes claim port 8000")

    def test_runtime_service_preflight_inspect_strict_preferred_owner(self):
        """Runtime service preflight inspect forwards strict preferred-owner mode."""
        result = PreflightResult(
            status=PreflightStatus.AMBIGUOUS,
            timestamp="2026-04-09T03:20:00+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8000/health",
                is_healthy=True,
                response_status=200,
                response_body={"status": "healthy"},
                response_time_ms=21.0,
            ),
            port_ownership=PortOwnershipInfo(
                port=8000,
                listening_processes=[{"pid": 1, "name": "python.exe"}],
                unique_count=1,
                is_clear=True,
                inspection_method="windows_powershell",
            ),
            summary="Ambiguous: preferred owner mismatch on port 8000",
              details={
                  "preferred_owner": {
                      "status": "preferred_mismatch",
                      "matched": False,
                      "matched_hint": None,
                  },
                  "owner_chain": {
                      "status": "parent_preferred_child_mismatch",
                      "parent_matches_preferred": True,
                      "matched_hint": PREFERRED_VENV_HINT,
                  },
                  "strict_preferred_owner": True,
              },
          )

        with patch.object(ike_v0_module, "run_preflight", AsyncMock(return_value=result)) as mock_run_preflight:
            response = self.client.post(
                "/api/ike/v0/runtime/service-preflight/inspect",
                json={"strict_preferred_owner": True},
            )
            self.assertEqual(response.status_code, 200)
            mock_run_preflight.assert_awaited_once_with(
                host="127.0.0.1",
                port=8000,
                strict_preferred_owner=True,
                expected_code_fingerprint=None,
                strict_code_freshness=False,
                self_check_current_code=False,
            )
            data = response.json()
            self.assertEqual(data["data"]["details"]["strict_preferred_owner"], True)
            self.assertEqual(data["data"]["details"]["preferred_owner"]["status"], "preferred_mismatch")
            self.assertEqual(data["data"]["owner_chain"]["status"], "parent_preferred_child_mismatch")
            self.assertEqual(data["data"]["repo_launcher"], None)

    def test_runtime_service_preflight_inspect_strict_code_freshness(self):
        """Runtime service preflight inspect forwards strict code-freshness mode."""
        result = PreflightResult(
            status=PreflightStatus.AMBIGUOUS,
            timestamp="2026-04-09T03:45:00+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8000/health",
                is_healthy=True,
                response_status=200,
                response_body={"status": "healthy"},
                response_time_ms=18.0,
            ),
            port_ownership=PortOwnershipInfo(
                port=8000,
                listening_processes=[{"pid": 1, "name": "python.exe"}],
                unique_count=1,
                is_clear=True,
                inspection_method="windows_powershell",
            ),
            summary="Ambiguous: live service code fingerprint mismatch",
            details={
                "code_fingerprint": {
                    "status": "available",
                    "scope": "runtime_service_preflight_surface_v1",
                    "fingerprint": "actual-1234",
                    "sources": ["service_preflight.py", "ike_v0.py"],
                    "source_count": 2,
                },
                "code_freshness": {
                    "status": "mismatch",
                    "expected_fingerprint": "expected-9999",
                    "actual_fingerprint": "actual-1234",
                },
                "strict_code_freshness": True,
            },
        )

        with patch.object(ike_v0_module, "run_preflight", AsyncMock(return_value=result)) as mock_run_preflight:
            response = self.client.post(
                "/api/ike/v0/runtime/service-preflight/inspect",
                json={
                    "strict_code_freshness": True,
                    "expected_code_fingerprint": "expected-9999",
                },
            )
            self.assertEqual(response.status_code, 200)
            mock_run_preflight.assert_awaited_once_with(
                host="127.0.0.1",
                port=8000,
                strict_preferred_owner=False,
                expected_code_fingerprint="expected-9999",
                strict_code_freshness=True,
                self_check_current_code=False,
            )
            data = response.json()
            self.assertEqual(data["data"]["details"]["strict_code_freshness"], True)
            self.assertEqual(data["data"]["details"]["code_freshness"]["status"], "mismatch")

    def test_runtime_service_preflight_inspect_accepts_explicit_host_port(self):
        """Runtime service preflight inspect can target a non-default live-proof port."""
        result = PreflightResult(
            status=PreflightStatus.READY,
            timestamp="2026-04-09T04:00:00+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8011/health",
                is_healthy=True,
                response_status=200,
                response_body={"status": "healthy"},
                response_time_ms=15.0,
            ),
            port_ownership=PortOwnershipInfo(
                port=8011,
                listening_processes=[{"pid": 10, "name": "python.exe"}],
                unique_count=1,
                is_clear=True,
                inspection_method="windows_powershell",
            ),
            summary="Ready: API healthy at http://127.0.0.1:8011/health (15.0ms), single process owns port 8011",
            details={},
        )

        with patch.object(ike_v0_module, "run_preflight", AsyncMock(return_value=result)) as mock_run_preflight:
            response = self.client.post(
                "/api/ike/v0/runtime/service-preflight/inspect",
                json={"host": "127.0.0.1", "port": 8011},
            )
            self.assertEqual(response.status_code, 200)
            mock_run_preflight.assert_awaited_once_with(
                host="127.0.0.1",
                port=8011,
                strict_preferred_owner=False,
                expected_code_fingerprint=None,
                strict_code_freshness=False,
                self_check_current_code=False,
            )
            data = response.json()
            self.assertEqual(data["data"]["port_ownership"]["port"], 8011)

    def test_runtime_service_preflight_inspect_self_check_current_code(self):
        """Runtime service preflight inspect can request a local current-code self-check."""
        result = PreflightResult(
            status=PreflightStatus.READY,
            timestamp="2026-04-10T07:25:00+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8000/health",
                is_healthy=True,
                response_status=200,
                response_body={"status": "healthy"},
                response_time_ms=20.0,
            ),
            port_ownership=PortOwnershipInfo(
                port=8000,
                listening_processes=[{"pid": 1, "name": "python.exe"}],
                unique_count=1,
                is_clear=True,
                inspection_method="windows_powershell",
            ),
            summary="Ready: API healthy at http://127.0.0.1:8000/health (20.0ms), single process owns port 8000",
            details={},
        )

        with patch.object(ike_v0_module, "run_preflight", AsyncMock(return_value=result)) as mock_run_preflight:
            response = self.client.post(
                "/api/ike/v0/runtime/service-preflight/inspect",
                json={"self_check_current_code": True, "strict_code_freshness": True},
            )
            self.assertEqual(response.status_code, 200)
            mock_run_preflight.assert_awaited_once_with(
                host="127.0.0.1",
                port=8000,
                strict_preferred_owner=False,
                expected_code_fingerprint=None,
                strict_code_freshness=True,
                self_check_current_code=True,
            )

    def test_runtime_service_preflight_inspect_exposes_repo_launcher(self):
        """Runtime service preflight inspect exposes repo-launcher evidence."""
        result = PreflightResult(
            status=PreflightStatus.AMBIGUOUS,
            timestamp="2026-04-09T04:40:00+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8013/health",
                is_healthy=True,
                response_status=200,
                response_body={"status": "healthy"},
                response_time_ms=12.0,
            ),
            port_ownership=PortOwnershipInfo(
                port=8013,
                listening_processes=[{"pid": 10, "name": "python.exe"}],
                unique_count=1,
                is_clear=True,
                inspection_method="windows_powershell",
            ),
            summary="Ambiguous: port ownership unclear",
            details={
                "repo_launcher": {
                    "status": "parent_and_child_repo_launcher_match",
                    "child_matches": True,
                    "parent_matches": True,
                    "matched_hint": REPO_UVICORN_HINT,
                }
            },
        )

        with patch.object(ike_v0_module, "run_preflight", AsyncMock(return_value=result)):
            response = self.client.post("/api/ike/v0/runtime/service-preflight/inspect")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(
                data["data"]["repo_launcher"]["status"],
                "parent_and_child_repo_launcher_match",
            )

    def test_runtime_service_preflight_inspect_exposes_controller_acceptability(self):
        """Runtime service preflight inspect exposes controller acceptability."""
        result = PreflightResult(
            status=PreflightStatus.AMBIGUOUS,
            timestamp="2026-04-09T04:50:00+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8013/health",
                is_healthy=True,
                response_status=200,
                response_body={"status": "healthy"},
                response_time_ms=14.0,
            ),
            port_ownership=PortOwnershipInfo(
                port=8013,
                listening_processes=[{"pid": 10, "name": "python.exe"}],
                unique_count=1,
                is_clear=True,
                inspection_method="windows_powershell",
            ),
            summary="Ambiguous: port ownership unclear",
            details={
                "controller_acceptability": {
                    "status": "acceptable_windows_venv_redirector",
                    "acceptable": True,
                    "controller_confirmation_required": True,
                    "rule": "windows_venv_redirector_v1",
                    "promotion_path": "controller_confirmation_required",
                },
                "controller_promotion": {
                    "status": "controller_confirmation_required",
                    "eligible": True,
                    "target_status": "canonical_accepted",
                    "controller_confirmation_required": True,
                    "basis": "windows_venv_redirector_v1",
                }
            },
        )

        with patch.object(ike_v0_module, "run_preflight", AsyncMock(return_value=result)):
            response = self.client.post("/api/ike/v0/runtime/service-preflight/inspect")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(
                data["data"]["controller_acceptability"]["status"],
                "acceptable_windows_venv_redirector",
            )
            self.assertTrue(
                data["data"]["controller_acceptability"]["controller_confirmation_required"]
            )
            self.assertEqual(
                data["data"]["controller_acceptability"]["rule"],
                "windows_venv_redirector_v1",
            )
            self.assertEqual(
                data["data"]["controller_promotion"]["status"],
                "controller_confirmation_required",
            )
            self.assertTrue(data["data"]["controller_promotion"]["eligible"])

    def test_runtime_service_preflight_controller_decision_inspect_forwards_self_check(self):
        """Controller decision inspect forwards the same preflight request shape."""
        result = PreflightResult(
            status=PreflightStatus.READY,
            timestamp="2026-04-10T07:40:00+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8000/health",
                is_healthy=True,
                response_status=200,
                response_body={"status": "healthy"},
                response_time_ms=20.0,
            ),
            port_ownership=PortOwnershipInfo(
                port=8000,
                listening_processes=[{"pid": 1, "name": "python.exe"}],
                unique_count=1,
                is_clear=True,
                inspection_method="windows_powershell",
            ),
            summary="Ready",
            details={
                "controller_acceptability": {
                    "status": "acceptable_windows_venv_redirector",
                    "acceptable": True,
                    "controller_confirmation_required": True,
                },
                "controller_promotion": {
                    "status": "controller_confirmation_required",
                    "eligible": True,
                    "target_status": "canonical_accepted",
                    "controller_confirmation_required": True,
                    "basis": "windows_venv_redirector_v1",
                },
            },
        )

        with patch.object(ike_v0_module, "run_preflight", AsyncMock(return_value=result)) as mock_run_preflight:
            response = self.client.post(
                "/api/ike/v0/runtime/service-preflight/controller-decision/inspect",
                json={"self_check_current_code": True, "strict_code_freshness": True},
            )
            self.assertEqual(response.status_code, 200)
            mock_run_preflight.assert_awaited_once_with(
                host="127.0.0.1",
                port=8000,
                strict_preferred_owner=False,
                expected_code_fingerprint=None,
                strict_code_freshness=True,
                self_check_current_code=True,
            )

    def test_runtime_service_preflight_controller_decision_inspect_is_confirmation_gated(self):
        """Controller decision inspect exposes recommendation without mutating acceptance."""
        result = PreflightResult(
            status=PreflightStatus.READY,
            timestamp="2026-04-10T07:41:00+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8000/health",
                is_healthy=True,
                response_status=200,
                response_body={"status": "healthy"},
                response_time_ms=18.0,
            ),
            port_ownership=PortOwnershipInfo(
                port=8000,
                listening_processes=[{"pid": 1, "name": "python.exe"}],
                unique_count=1,
                is_clear=True,
                inspection_method="windows_powershell",
            ),
            summary="Ready",
            details={
                "controller_acceptability": {
                    "status": "acceptable_windows_venv_redirector",
                    "acceptable": True,
                    "controller_confirmation_required": True,
                    "rule": "windows_venv_redirector_v1",
                },
                "controller_promotion": {
                    "status": "controller_confirmation_required",
                    "eligible": True,
                    "target_status": "canonical_accepted",
                    "controller_confirmation_required": True,
                    "basis": "windows_venv_redirector_v1",
                },
            },
        )

        with patch.object(ike_v0_module, "run_preflight", AsyncMock(return_value=result)):
            response = self.client.post("/api/ike/v0/runtime/service-preflight/controller-decision/inspect")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(
                data["data"]["decision"]["recommended_action"],
                "controller_confirmation_required",
            )
            self.assertEqual(
                data["data"]["decision"]["target_status"],
                "canonical_accepted",
            )
            self.assertTrue(data["data"]["decision"]["eligible"])
            self.assertTrue(data["data"]["truth_boundary"]["inspect_only"])
            self.assertFalse(data["data"]["truth_boundary"]["mutates_acceptance"])
            self.assertFalse(data["data"]["truth_boundary"]["records_controller_decision"])
            self.assertFalse(data["data"]["truth_boundary"]["implies_canonical_accepted"])

    def test_runtime_service_preflight_controller_acceptance_record_inspect_forwards_project_key(self):
        """Controller acceptance record inspect forwards preflight shape and project_key."""
        from db import get_db

        result = PreflightResult(
            status=PreflightStatus.READY,
            timestamp="2026-04-11T02:10:00+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8000/health",
                is_healthy=True,
                response_status=200,
                response_body={"status": "healthy"},
                response_time_ms=12.0,
            ),
            port_ownership=PortOwnershipInfo(
                port=8000,
                listening_processes=[{"pid": 1, "name": "python.exe"}],
                unique_count=1,
                is_clear=True,
                inspection_method="windows_powershell",
            ),
            summary="Ready",
            details={
                "host": "127.0.0.1",
                "port": 8000,
                "controller_promotion": {
                    "status": "controller_confirmation_required",
                    "eligible": True,
                    "target_status": "canonical_accepted",
                    "basis": "windows_venv_redirector_v1",
                },
                "canonical_launch": {
                    "launch_mode": "repo_uvicorn_entry",
                    "launcher_path": "D:\\code\\MyAttention\\.venv\\Scripts\\uvicorn.exe",
                },
            },
        )

        class MockDB:
            async def run_sync(self, fn):
                return fn(object())

        async def mock_get_db():
            return MockDB()

        payload = {
            "status": "ready",
            "project": {
                "project_id": "proj-123",
                "project_key": "ike-runtime-mainline",
                "title": "Runtime Mainline",
            },
            "current_preflight": {"status": "ready"},
            "decision_record": {
                "exists": False,
                "decision_id": None,
                "decision_scope": "canonical_service_acceptance",
            },
            "truth_boundary": {
                "inspect_only": True,
                "mutates_acceptance": False,
                "records_controller_decision": False,
                "implies_canonical_accepted": False,
            },
        }

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(ike_v0_module, "run_preflight", AsyncMock(return_value=result)):
                with patch.object(
                    ike_v0_module,
                    "inspect_controller_acceptance_record",
                    return_value=payload,
                ) as mock_inspect:
                    response = self.client.post(
                        "/api/ike/v0/runtime/service-preflight/controller-decision/record/inspect",
                        json={
                            "project_key": "ike-runtime-mainline",
                            "self_check_current_code": True,
                        },
                    )
                    self.assertEqual(response.status_code, 200)
                    data = response.json()
                    self.assertEqual(
                        data["ref"]["kind"],
                        "runtime_controller_acceptance_record_inspect",
                    )
                    self.assertEqual(
                        data["data"]["project"]["project_key"],
                        "ike-runtime-mainline",
                    )
                    self.assertTrue(data["data"]["truth_boundary"]["inspect_only"])
                    mock_inspect.assert_called_once()
                    self.assertEqual(
                        mock_inspect.call_args.kwargs["project_key"],
                        "ike-runtime-mainline",
                    )
        finally:
            test_app.dependency_overrides.clear()

    def test_runtime_service_preflight_controller_acceptance_record_writes_bounded_result(self):
        """Controller acceptance record route exposes explicit bounded write semantics."""
        from db import get_db

        result = PreflightResult(
            status=PreflightStatus.READY,
            timestamp="2026-04-11T02:11:00+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8000/health",
                is_healthy=True,
                response_status=200,
                response_body={"status": "healthy"},
                response_time_ms=12.0,
            ),
            port_ownership=PortOwnershipInfo(
                port=8000,
                listening_processes=[{"pid": 1, "name": "python.exe"}],
                unique_count=1,
                is_clear=True,
                inspection_method="windows_powershell",
            ),
            summary="Ready",
            details={
                "host": "127.0.0.1",
                "port": 8000,
                "controller_promotion": {
                    "status": "controller_confirmation_required",
                    "eligible": True,
                    "target_status": "canonical_accepted",
                    "basis": "windows_venv_redirector_v1",
                },
                "canonical_launch": {
                    "launch_mode": "repo_uvicorn_entry",
                    "launcher_path": "D:\\code\\MyAttention\\.venv\\Scripts\\uvicorn.exe",
                },
            },
        )

        class MockDB:
            async def run_sync(self, fn):
                return fn(object())

        async def mock_get_db():
            return MockDB()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(ike_v0_module, "run_preflight", AsyncMock(return_value=result)):
                with patch.object(
                    ike_v0_module,
                    "record_controller_acceptance",
                    return_value={
                        "recorded": True,
                        "idempotent_reuse": False,
                        "rejected": False,
                        "decision_id": "dec-123",
                        "decision_scope": "canonical_service_acceptance",
                        "outcome": "adopt",
                        "status": "final",
                        "target_status": "canonical_accepted",
                        "basis": "windows_venv_redirector_v1",
                        "superseded": False,
                        "supersedes_decision_id": None,
                        "event_recorded": True,
                        "work_context_updated": True,
                        "project_id": "proj-123",
                        "project_key": "ike-runtime-mainline",
                        "task_anchor_id": "task-123",
                        "truth_boundary": {
                            "inspect_only": False,
                            "mutates_acceptance": True,
                            "records_controller_decision": True,
                            "implies_canonical_accepted": False,
                        },
                    },
                ) as mock_record:
                    response = self.client.post(
                        "/api/ike/v0/runtime/service-preflight/controller-decision/record",
                        json={
                            "project_key": "ike-runtime-mainline",
                            "controller_id": "controller-001",
                            "summary": "Accept runtime proof",
                        },
                    )
                    self.assertEqual(response.status_code, 200)
                    data = response.json()
                    self.assertEqual(
                        data["ref"]["kind"],
                        "runtime_controller_acceptance_record",
                    )
                    self.assertTrue(data["data"]["recorded"])
                    self.assertTrue(data["data"]["truth_boundary"]["mutates_acceptance"])
                    self.assertTrue(
                        data["data"]["truth_boundary"]["records_controller_decision"]
                    )
                    mock_record.assert_called_once()
                    self.assertEqual(
                        mock_record.call_args.kwargs["controller_id"],
                        "controller-001",
                    )
        finally:
            test_app.dependency_overrides.clear()

    def test_runtime_service_preflight_controller_acceptance_record_returns_400_for_bounded_error(self):
        """Controller acceptance record rejects bounded write errors clearly."""
        from db import get_db

        result = PreflightResult(
            status=PreflightStatus.READY,
            timestamp="2026-04-11T02:12:00+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8000/health",
                is_healthy=True,
                response_status=200,
                response_body={"status": "healthy"},
                response_time_ms=12.0,
            ),
            port_ownership=PortOwnershipInfo(
                port=8000,
                listening_processes=[{"pid": 1, "name": "python.exe"}],
                unique_count=1,
                is_clear=True,
                inspection_method="windows_powershell",
            ),
            summary="Ready",
            details={
                "host": "127.0.0.1",
                "port": 8000,
                "controller_promotion": {
                    "status": "controller_confirmation_required",
                    "eligible": True,
                    "target_status": "canonical_accepted",
                    "basis": "windows_venv_redirector_v1",
                },
            },
        )

        class MockDB:
            async def run_sync(self, fn):
                return fn(object())

        async def mock_get_db():
            return MockDB()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(ike_v0_module, "run_preflight", AsyncMock(return_value=result)):
                with patch.object(
                    ike_v0_module,
                    "record_controller_acceptance",
                    side_effect=ike_v0_module.ControllerAcceptanceError(
                        "Runtime project has no task anchor for controller acceptance event recording."
                    ),
                ):
                    response = self.client.post(
                        "/api/ike/v0/runtime/service-preflight/controller-decision/record",
                        json={"controller_id": "controller-001"},
                    )
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("no task anchor", response.json()["detail"])
        finally:
            test_app.dependency_overrides.clear()

    def test_runtime_task_lifecycle_proof_inspect_runs_narrow_proof(self):
        """Runtime task lifecycle proof inspect returns one provisional audit-shaped proof."""
        proof = LifecycleProofResult(
            success=True,
            task_id="task-123",
            project_id="proj-123",
            final_status=TaskStatus.DONE,
            transitions=[],
            events=[{"event_type": "state_transition"}],
            lease=LeaseRecord(
                lease_id="lease-123",
                task_id="task-123",
                owner_kind="delegate",
                owner_id="delegate-x",
                lease_status="released",
                heartbeat_at=None,
                expires_at="2026-04-10T00:00:00+00:00",
                created_at="2026-04-10T00:00:00+00:00",
                metadata={"source": "test"},
            ),
            memory_packet=None,
            error=None,
        )

        with patch.object(
            ike_v0_module,
            "execute_lifecycle_proof",
            return_value=proof,
        ) as mock_execute, patch.object(
            ike_v0_module,
            "validate_lifecycle_proof_integrity",
            return_value=(True, "Lifecycle proof has full integrity"),
        ), patch.object(
            ike_v0_module,
            "is_proof_auditable",
            return_value=True,
        ), patch.object(
            ike_v0_module,
            "derive_work_context_from_proof",
            return_value=None,
        ):
            response = self.client.post(
                "/api/ike/v0/runtime/task-lifecycle/proof/inspect",
                json={
                    "project_id": "proj-123",
                    "task_id": "task-123",
                    "task_type": "implementation",
                    "task_title": "Lifecycle proof task",
                    "delegate_id": "delegate-x",
                    "controller_id": "controller-y",
                },
            )

        self.assertEqual(response.status_code, 200)
        mock_execute.assert_called_once_with(
            task_id="task-123",
            project_id="proj-123",
            task_type="implementation",
            delegate_id="delegate-x",
            controller_id="controller-y",
            task_title="Lifecycle proof task",
        )
        data = response.json()
        self.assertEqual(data["ref"]["kind"], "runtime_task_lifecycle_proof")
        self.assertEqual(data["data"]["task_id"], "task-123")
        self.assertEqual(data["data"]["project_id"], "proj-123")
        self.assertEqual(data["data"]["final_status"], "done")
        self.assertTrue(data["data"]["integrity"]["valid"])
        self.assertTrue(data["data"]["integrity"]["auditable"])
        self.assertEqual(data["data"]["lease"]["lease_id"], "lease-123")
        self.assertEqual(data["data"]["lease"]["lease_status"], "released")
        self.assertTrue(data["data"]["truth_boundary"]["inspect_only"])
        self.assertFalse(data["data"]["truth_boundary"]["persists_runtime_state"])

    def test_runtime_task_lifecycle_proof_inspect_generates_ids_by_default(self):
        """Runtime task lifecycle proof inspect can generate provisional ids when omitted."""
        proof = LifecycleProofResult(
            success=True,
            task_id="generated-task",
            project_id="generated-project",
            final_status=TaskStatus.DONE,
            transitions=[],
            events=[],
            lease=None,
            memory_packet=None,
            error=None,
        )

        with patch.object(
            ike_v0_module,
            "execute_lifecycle_proof",
            return_value=proof,
        ) as mock_execute, patch.object(
            ike_v0_module,
            "validate_lifecycle_proof_integrity",
            return_value=(True, "ok"),
        ), patch.object(
            ike_v0_module,
            "is_proof_auditable",
            return_value=True,
        ), patch.object(
            ike_v0_module,
            "derive_work_context_from_proof",
            return_value=None,
        ):
            response = self.client.post(
                "/api/ike/v0/runtime/task-lifecycle/proof/inspect",
            )

        self.assertEqual(response.status_code, 200)
        call = mock_execute.call_args.kwargs
        self.assertEqual(call["task_type"], "implementation")
        self.assertEqual(call["task_title"], "Runtime lifecycle proof task")
        self.assertEqual(call["delegate_id"], "delegate-001")
        self.assertEqual(call["controller_id"], "controller-001")
        self.assertTrue(call["task_id"])
        self.assertTrue(call["project_id"])
        data = response.json()
        self.assertEqual(data["data"]["summary"]["final_status"], "done")

    def test_runtime_db_backed_lifecycle_proof_inspect_basic(self):
        """Runtime DB-backed lifecycle proof inspect returns one bounded audit shape."""
        from db import get_db

        proof = DBBackedLifecycleProofResult(
            success=True,
            project_id="proj-db-123",
            task_id="task-db-123",
            final_status="done",
            lease_id="lease-db-123",
            event_ids=["evt-1", "evt-2", "evt-3", "evt-4", "evt-5", "evt-6"],
            persisted_event_count=6,
            error=None,
        )

        class MockDB:
            async def run_sync(self, fn):
                return proof

        async def mock_get_db():
            return MockDB()

        original_execute = ike_v0_module.execute_db_backed_lifecycle_proof
        ike_v0_module.execute_db_backed_lifecycle_proof = (
            lambda sync_session, project_key=None, title="DB-backed lifecycle proof task",
            delegate_id="delegate-001", controller_id="controller-001": proof
        )
        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.post(
                "/api/ike/v0/runtime/task-lifecycle/db-proof/inspect",
                json={
                    "project_key": "db-proof-mainline",
                    "task_title": "DB proof task",
                    "delegate_id": "delegate-x",
                    "controller_id": "controller-y",
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get("X-IKE-Version"), "v0-experimental")
            data = response.json()
            self.assertEqual(data["ref"]["kind"], "runtime_db_backed_lifecycle_proof")
            self.assertEqual(data["data"]["project_id"], "proj-db-123")
            self.assertEqual(data["data"]["task_id"], "task-db-123")
            self.assertTrue(data["data"]["summary"]["success"])
            self.assertEqual(data["data"]["summary"]["final_status"], "done")
            self.assertEqual(data["data"]["summary"]["persisted_event_count"], 6)
            self.assertTrue(data["data"]["truth_boundary"]["inspect_only"])
            self.assertTrue(data["data"]["truth_boundary"]["bounded_db_proof"])
            self.assertTrue(data["data"]["truth_boundary"]["persists_runtime_state"])
            self.assertFalse(data["data"]["truth_boundary"]["implies_general_task_runner"])
            self.assertFalse(data["data"]["truth_boundary"]["detached_execution"])
        finally:
            ike_v0_module.execute_db_backed_lifecycle_proof = original_execute
            test_app.dependency_overrides.clear()

    def test_runtime_db_backed_lifecycle_proof_inspect_uses_defaults(self):
        """Runtime DB-backed lifecycle proof inspect forwards default bounded inputs."""
        from db import get_db

        proof = DBBackedLifecycleProofResult(
            success=False,
            project_id="proj-db-default",
            task_id="task-db-default",
            final_status="inbox",
            lease_id=None,
            event_ids=[],
            persisted_event_count=0,
            error="proof failed",
        )

        class MockDB:
            async def run_sync(self, fn):
                return fn(object())

        async def mock_get_db():
            return MockDB()

        captured = {}

        def fake_execute(sync_session, project_key=None, title="DB-backed lifecycle proof task",
                         delegate_id="delegate-001", controller_id="controller-001"):
            captured["project_key"] = project_key
            captured["title"] = title
            captured["delegate_id"] = delegate_id
            captured["controller_id"] = controller_id
            return proof

        original_execute = ike_v0_module.execute_db_backed_lifecycle_proof
        ike_v0_module.execute_db_backed_lifecycle_proof = fake_execute
        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.post("/api/ike/v0/runtime/task-lifecycle/db-proof/inspect")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(captured["project_key"], None)
            self.assertEqual(captured["title"], "DB-backed lifecycle proof task")
            self.assertEqual(captured["delegate_id"], "delegate-001")
            self.assertEqual(captured["controller_id"], "controller-001")
            data = response.json()
            self.assertFalse(data["data"]["summary"]["success"])
            self.assertEqual(data["data"]["summary"]["error"], "proof failed")
            self.assertTrue(data["data"]["truth_boundary"]["persists_runtime_state"])
        finally:
            ike_v0_module.execute_db_backed_lifecycle_proof = original_execute
            test_app.dependency_overrides.clear()

    def test_runtime_db_backed_lifecycle_proof_inspect_preserves_failure_honesty(self):
        """Runtime DB-backed lifecycle proof inspect exposes durable partial failure truth."""
        from db import get_db

        proof = DBBackedLifecycleProofResult(
            success=False,
            project_id="proj-db-failure",
            task_id="task-db-failure",
            final_status="ready",
            lease_id="lease-db-failure",
            event_ids=["evt-1", "evt-2"],
            persisted_event_count=2,
            error="synthetic ready->active failure",
        )

        class MockDB:
            async def run_sync(self, fn):
                return proof

        async def mock_get_db():
            return MockDB()

        original_execute = ike_v0_module.execute_db_backed_lifecycle_proof
        ike_v0_module.execute_db_backed_lifecycle_proof = (
            lambda sync_session, project_key=None, title="DB-backed lifecycle proof task",
            delegate_id="delegate-001", controller_id="controller-001": proof
        )
        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.post("/api/ike/v0/runtime/task-lifecycle/db-proof/inspect")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertFalse(data["data"]["summary"]["success"])
            self.assertEqual(data["data"]["summary"]["final_status"], "ready")
            self.assertEqual(data["data"]["summary"]["persisted_event_count"], 2)
            self.assertEqual(
                data["data"]["summary"]["error"],
                "synthetic ready->active failure",
            )
            self.assertEqual(data["data"]["audit"]["final_status"], "ready")
            self.assertEqual(data["data"]["audit"]["persisted_event_count"], 2)
            self.assertTrue(data["data"]["truth_boundary"]["inspect_only"])
            self.assertTrue(data["data"]["truth_boundary"]["persists_runtime_state"])
            self.assertFalse(data["data"]["truth_boundary"]["implies_general_task_runner"])
        finally:
            ike_v0_module.execute_db_backed_lifecycle_proof = original_execute
            test_app.dependency_overrides.clear()


if __name__ == "__main__":
    unittest.main()
