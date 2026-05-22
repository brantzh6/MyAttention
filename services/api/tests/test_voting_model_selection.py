import sys
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from llm.voting import MultiModelVoting


class VotingModelSelectionTest(unittest.TestCase):
    def test_accepts_string_model_list(self) -> None:
        voting = MultiModelVoting(models=["qwen3.5-plus", "MiniMax-M2.5"])
        self.assertEqual(
            voting.models,
            [
                {"provider": "qwen", "model": "qwen3.5-plus", "name": "qwen3.5-plus"},
                {"provider": "qwen", "model": "MiniMax-M2.5", "name": "MiniMax-M2.5"},
            ],
        )

    def test_rejects_unknown_string_model(self) -> None:
        with self.assertRaises(ValueError):
            MultiModelVoting(models=["unknown-model"])

    def test_search_only_uses_search_capable_models(self) -> None:
        voting = MultiModelVoting(enable_search=True)
        self.assertEqual(
            [model["name"] for model in voting.models],
            ["qwen3.5-plus", "MiniMax-M2.5", "deepseek-v3.2"],
        )

    def test_thinking_only_uses_thinking_capable_models(self) -> None:
        voting = MultiModelVoting(enable_thinking=True)
        self.assertEqual(
            [model["name"] for model in voting.models],
            ["qwen3.5-plus", "deepseek-v3.2", "glm-5"],
        )

    def test_search_and_thinking_uses_union_with_primary_and_support_models(self) -> None:
        voting = MultiModelVoting(enable_search=True, enable_thinking=True)
        self.assertEqual(
            [model["name"] for model in voting.models],
            ["qwen3.5-plus", "MiniMax-M2.5", "deepseek-v3.2", "glm-5"],
        )
        self.assertEqual(voting._model_capability_summary("qwen3.5-plus")["role"], "primary")
        self.assertEqual(voting._model_capability_summary("MiniMax-M2.5")["role"], "support")
        self.assertEqual(voting._model_capability_summary("glm-5")["contribution"], "thinking")


if __name__ == "__main__":
    unittest.main()
