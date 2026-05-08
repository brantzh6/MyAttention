import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


API_DIR = Path(__file__).resolve().parent.parent
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))


def load_system_router_module():
    router_path = API_DIR / "routers" / "system.py"
    spec = importlib.util.spec_from_file_location("system_router_test_module", router_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


system_module = load_system_router_module()
system_router = system_module.router

test_app = FastAPI(title="System Health Route Test API")
test_app.include_router(system_router, prefix="/api")


class SystemHealthRouterTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(test_app)

    def test_code_health_is_code_truth_only(self):
        response = self.client.get("/api/system/code-health")
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload["truth_plane"], "code_truth")
        self.assertEqual(payload["overall_status"], "healthy")
        self.assertTrue(payload["checks"][0]["running"])
        self.assertIn("/health", payload["checks"][0]["details"]["routes"])

    def test_runtime_health_returns_structured_error_instead_of_500(self):
        with (
            patch.object(system_module, "check_docker_container", return_value={"name": "IKE PostgreSQL", "status": "healthy", "running": True}),
            patch.object(system_module, "check_database_postgres", side_effect=RuntimeError("db down")),
            patch.object(system_module, "check_database_redis", return_value={"name": "Redis", "status": "healthy", "running": True}),
            patch.object(system_module, "check_database_qdrant", return_value={"name": "Qdrant", "status": "healthy", "running": True}),
            patch.object(system_module, "check_api_service", return_value={"name": "IKE API", "status": "healthy", "running": True}),
            patch.object(system_module, "check_llm_service", return_value={"name": "Tongyi Qwen (LLM)", "status": "healthy", "running": True}),
        ):
            response = self.client.get("/api/system/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["truth_plane"], "runtime_truth")
        self.assertEqual(payload["overall_status"], "error")
        self.assertIn("db down", payload["error"])


if __name__ == "__main__":
    unittest.main()
