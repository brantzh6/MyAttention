import unittest
import sys
from types import SimpleNamespace
from pathlib import Path

# Add parent directory to path for direct imports
api_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(api_dir))

from config import get_effective_qwen_default_model


class ConfigRuntimeIdentityTest(unittest.TestCase):
    def test_coding_base_defaults_to_qwen36_plus(self):
        settings = SimpleNamespace(
            qwen_base_url="https://coding.dashscope.aliyuncs.com/v1",
            qwen_api_key="",
        )
        self.assertEqual(get_effective_qwen_default_model(settings), "qwen3.6-plus")

    def test_non_coding_base_keeps_qwen_max(self):
        settings = SimpleNamespace(
            qwen_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            qwen_api_key="",
        )
        self.assertEqual(get_effective_qwen_default_model(settings), "qwen-max")
