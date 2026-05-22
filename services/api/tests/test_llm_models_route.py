import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


API_DIR = Path(__file__).resolve().parent.parent
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))


def load_models_router_module():
    router_path = API_DIR / "routers" / "models.py"
    spec = importlib.util.spec_from_file_location("llm_models_router_test_module", router_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


models_module = load_models_router_module()
models_router = models_module.router

test_app = FastAPI(title="LLM Models Route Test API")
test_app.include_router(models_router, prefix="/api/llm")


class LLMModelsRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(test_app)

    def test_build_providers_includes_bailian_families(self):
        def fake_get_settings():
            return SimpleNamespace(
                qwen_api_key="",
                qwen_base_url="",
                bailian_coding_plan_api_key="",
                bailian_api_key="",
                anthropic_api_key="",
                openai_api_key="",
                ollama_base_url="http://localhost:11434",
            )

        fake_get_settings.cache_clear = lambda: None

        with patch.object(models_module, "get_settings", fake_get_settings):
            providers = models_module._build_providers()

        by_provider = {}
        for provider in providers:
            by_provider.setdefault(provider.provider, []).append(provider)

        self.assertIn("bailian-coding-plan", by_provider)
        self.assertIn("bailian", by_provider)
        self.assertEqual(len(by_provider["bailian-coding-plan"]), 9)
        self.assertEqual(len(by_provider["bailian"]), 1)
        self.assertEqual(by_provider["bailian-coding-plan"][0].key_env, "BAILIAN_CODING_PLAN_API_KEY")
        self.assertTrue(by_provider["ollama"][0].api_key_set)

    def test_update_api_key_routes_bailian_family_to_new_secret_name(self):
        def fake_get_settings():
            return SimpleNamespace(
                qwen_api_key="",
                qwen_base_url="",
                bailian_coding_plan_api_key="",
                bailian_api_key="",
                anthropic_api_key="",
                openai_api_key="",
                ollama_base_url="http://localhost:11434",
            )

        fake_get_settings.cache_clear = lambda: None

        with patch.object(models_module, "get_settings", fake_get_settings), patch.object(
            models_module, "write_local_secret"
        ) as write_local_secret:
            response = self.client.put(
                "/api/llm/providers/bailian/api-key",
                json={"api_key": "sk-test-bailian"},
            )

        self.assertEqual(response.status_code, 200)
        write_local_secret.assert_called_once_with("BAILIAN_API_KEY", "sk-test-bailian")


if __name__ == "__main__":
    unittest.main()
