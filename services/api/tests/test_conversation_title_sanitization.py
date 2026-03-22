import sys
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from routers.conversations import _build_conversation_title, _looks_corrupted_title


class ConversationTitleSanitizationTest(unittest.TestCase):
    def test_corrupted_title_detection(self) -> None:
        self.assertTrue(_looks_corrupted_title("????"))
        self.assertTrue(_looks_corrupted_title("??????????API????"))
        self.assertFalse(_looks_corrupted_title("新对话"))
        self.assertFalse(_looks_corrupted_title("美的公司希望推出一款智能中枢产品"))

    def test_build_conversation_title_normalizes_whitespace(self) -> None:
        title = _build_conversation_title("  第一行标题\n第二行内容  ")
        self.assertEqual(title, "第一行标题 第二行内容")

    def test_build_conversation_title_truncates_long_content(self) -> None:
        title = _build_conversation_title("a" * 80)
        self.assertEqual(title, ("a" * 50) + "...")

    def test_build_conversation_title_falls_back_for_empty_content(self) -> None:
        self.assertEqual(_build_conversation_title("   "), "新对话")
        self.assertEqual(_build_conversation_title(None), "新对话")

    def test_corrupted_generated_title_should_be_treated_as_invalid(self) -> None:
        title = _build_conversation_title("????????????")
        self.assertTrue(_looks_corrupted_title(title))


if __name__ == "__main__":
    unittest.main()
