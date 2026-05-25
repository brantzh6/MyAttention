import sys
import unittest
from unittest.mock import patch
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from llm.router import TaskRouter, TaskType, ModelConfig, ROUTING_CONFIG, EFFECTIVE_QWEN_DEFAULT_MODEL


class LLMRouterTest(unittest.TestCase):
    """Tests for LLM router model selection."""

    def test_simple_qa_does_not_use_legacy_qwen_turbo(self) -> None:
        """SIMPLE_QA should not return qwen-turbo (legacy unsupported model)."""
        router = TaskRouter()

        with patch(
            "llm.router.get_effective_qwen_default_model", return_value="qwen3.6-plus"
        ):
            config = router.get_model_config(TaskType.SIMPLE_QA)

        self.assertNotEqual(config.model, "qwen-turbo")
        self.assertNotEqual(config.fallback_model, "qwen-turbo")
        self.assertEqual(config.model, "qwen3.6-plus")
        self.assertEqual(config.fallback_model, "qwen3.6-plus")

    def test_simple_qa_routes_to_effective_default_model(self) -> None:
        """SIMPLE_QA should route to the current effective default model."""
        router = TaskRouter()

        with patch(
            "llm.router.get_effective_qwen_default_model", return_value="qwen-max"
        ):
            config = router.get_model_config(TaskType.SIMPLE_QA)

        self.assertEqual(config.model, "qwen-max")
        self.assertEqual(config.provider, "qwen")

    def test_simple_qa_coding_endpoint_routes_to_qwen36_plus(self) -> None:
        """SIMPLE_QA with coding endpoint should route to qwen3.6-plus."""
        router = TaskRouter()

        with patch(
            "llm.router.get_effective_qwen_default_model", return_value="qwen3.6-plus"
        ):
            config = router.get_model_config(TaskType.SIMPLE_QA)

        self.assertEqual(config.model, "qwen3.6-plus")
        self.assertEqual(config.provider, "qwen")

    def test_summarization_fallback_uses_effective_default(self) -> None:
        """SUMMARIZATION fallback_model should resolve to effective default."""
        router = TaskRouter()

        with patch(
            "llm.router.get_effective_qwen_default_model", return_value="qwen-max"
        ):
            config = router.get_model_config(TaskType.SUMMARIZATION)

        self.assertEqual(config.model, "qwen-plus")
        self.assertEqual(config.fallback_model, "qwen-max")

    def test_deep_analysis_unchanged(self) -> None:
        """DEEP_ANALYSIS should use explicit model names, not legacy defaults."""
        router = TaskRouter()

        config = router.get_model_config(TaskType.DEEP_ANALYSIS)

        self.assertEqual(config.model, "qwen-max")
        self.assertEqual(config.fallback_model, "qwen-plus")

    def test_code_generation_unchanged(self) -> None:
        """CODE_GENERATION should use explicit model names."""
        router = TaskRouter()

        config = router.get_model_config(TaskType.CODE_GENERATION)

        self.assertEqual(config.model, "qwen-max")
        self.assertEqual(config.fallback_model, "qwen-plus")

    def test_critical_decision_remains_voting(self) -> None:
        """CRITICAL_DECISION should remain voting with no fallback mutation."""
        router = TaskRouter()

        config = router.get_model_config(TaskType.CRITICAL_DECISION)

        self.assertEqual(config.provider, "voting")
        self.assertEqual(config.model, "voting")
        self.assertIsNone(config.fallback_provider)
        self.assertIsNone(config.fallback_model)

    def test_fact_check_remains_voting(self) -> None:
        """FACT_CHECK should remain voting with no fallback mutation."""
        router = TaskRouter()

        config = router.get_model_config(TaskType.FACT_CHECK)

        self.assertEqual(config.provider, "voting")
        self.assertEqual(config.model, "voting")
        self.assertIsNone(config.fallback_provider)
        self.assertIsNone(config.fallback_model)

    def test_route_simple_message_returns_supported_model(self) -> None:
        """Routing a simple message should return a supported current model."""
        router = TaskRouter()

        with patch(
            "llm.router.get_effective_qwen_default_model", return_value="qwen3.6-plus"
        ):
            config = router.route("Hello, how are you?")

        self.assertNotEqual(config.model, "qwen-turbo")
        self.assertIn(config.model, ["qwen3.6-plus", "qwen-max"])

    def test_route_fact_check_keywords_triggers_voting(self) -> None:
        """Messages with fact-check keywords should trigger voting."""
        router = TaskRouter()

        config = router.route("please fact check this claim")

        self.assertEqual(config.provider, "voting")
        self.assertEqual(config.model, "voting")

    def test_routing_config_simple_qa_model_is_sentinel(self) -> None:
        """ROUTING_CONFIG should have sentinel for SIMPLE_QA model (resolved at runtime)."""
        self.assertEqual(ROUTING_CONFIG[TaskType.SIMPLE_QA].model, EFFECTIVE_QWEN_DEFAULT_MODEL)

    def test_custom_routing_overrides_default(self) -> None:
        """Custom routing config should override defaults."""
        custom_config = ModelConfig(
            provider="custom",
            model="custom-model",
            temperature=0.1,
        )
        router = TaskRouter(custom_routing={TaskType.SIMPLE_QA: custom_config})

        config = router.get_model_config(TaskType.SIMPLE_QA)

        self.assertEqual(config.provider, "custom")
        self.assertEqual(config.model, "custom-model")

    def test_custom_routing_preserves_none_fallback_for_non_qwen(self) -> None:
        """Custom routing with non-qwen fallback_provider should preserve None fallback."""
        custom_config = ModelConfig(
            provider="qwen",
            model="qwen-max",
            fallback_provider="custom",
            fallback_model=None,
            temperature=0.5,
        )
        router = TaskRouter(custom_routing={TaskType.SIMPLE_QA: custom_config})

        with patch(
            "llm.router.get_effective_qwen_default_model", return_value="qwen3.6-plus"
        ):
            config = router.get_model_config(TaskType.SIMPLE_QA)

        self.assertEqual(config.provider, "qwen")
        self.assertEqual(config.model, "qwen-max")
        self.assertEqual(config.fallback_provider, "custom")
        self.assertIsNone(config.fallback_model)

    def test_custom_routing_resolves_sentinel_fallback_for_qwen_fallback_provider(self) -> None:
        """Custom routing with qwen fallback_provider should resolve sentinel fallback_model."""
        custom_config = ModelConfig(
            provider="qwen",
            model="qwen-max",
            fallback_provider="qwen",
            fallback_model=EFFECTIVE_QWEN_DEFAULT_MODEL,
            temperature=0.5,
        )
        router = TaskRouter(custom_routing={TaskType.SIMPLE_QA: custom_config})

        with patch(
            "llm.router.get_effective_qwen_default_model", return_value="qwen3.6-plus"
        ):
            config = router.get_model_config(TaskType.SIMPLE_QA)

        self.assertEqual(config.provider, "qwen")
        self.assertEqual(config.model, "qwen-max")
        self.assertEqual(config.fallback_provider, "qwen")
        self.assertEqual(config.fallback_model, "qwen3.6-plus")

    def test_custom_routing_preserves_none_fallback_for_qwen_fallback_provider(self) -> None:
        """Custom routing with qwen fallback_provider and fallback_model=None preserves None."""
        custom_config = ModelConfig(
            provider="qwen",
            model="qwen-max",
            fallback_provider="qwen",
            fallback_model=None,  # Explicit None, should NOT be resolved
            temperature=0.5,
        )
        router = TaskRouter(custom_routing={TaskType.SIMPLE_QA: custom_config})

        with patch(
            "llm.router.get_effective_qwen_default_model", return_value="qwen3.6-plus"
        ):
            config = router.get_model_config(TaskType.SIMPLE_QA)

        self.assertEqual(config.provider, "qwen")
        self.assertEqual(config.model, "qwen-max")
        self.assertEqual(config.fallback_provider, "qwen")
        self.assertIsNone(config.fallback_model)  # None preserved, not resolved


if __name__ == "__main__":
    unittest.main()
