import sys
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from feeds.ai_tester import evaluate_voting_quality, extract_voting_sections


class VotingQualityEvaluationTest(unittest.TestCase):
    def test_extract_voting_sections(self) -> None:
        consensus = (
            "【一句话判断】\n优先本地语音。\n"
            "【关键分歧】\n成本和体验存在冲突。\n"
            "【建议动作】\n先做语音 MVP。"
        )
        sections = extract_voting_sections(consensus)
        self.assertEqual(sections["一句话判断"], "优先本地语音。")
        self.assertIn("成本和体验", sections["关键分歧"])
        self.assertIn("MVP", sections["建议动作"])

    def test_high_quality_consensus_scores_high(self) -> None:
        consensus = (
            "【一句话判断】\n首版应优先本地语音控制，而不是视觉多模态。\n\n"
            "【共识】\n- 隐私与预算约束都更支持语音方案\n  来源：qwen3.5-plus, deepseek-v3.2\n\n"
            "【关键分歧】\n- 是否保留摄像头扩展接口\n  支持模型：MiniMax-M2.5\n\n"
            "【建议动作】\n- 先做本地语音 MVP，并验证唤醒率与误触发。\n"
        )
        quality = evaluate_voting_quality(consensus, successful_models=3)
        self.assertGreaterEqual(quality["score"], 80)
        self.assertEqual(quality["level"], "high")

    def test_weak_consensus_scores_low(self) -> None:
        consensus = (
            "【一句话判断】\n综合来看，需要进一步分析。\n\n"
            "【建议动作】\n建议结合实际情况继续观察。"
        )
        quality = evaluate_voting_quality(consensus, successful_models=2)
        self.assertLess(quality["score"], 65)
        self.assertEqual(quality["level"], "low")


if __name__ == "__main__":
    unittest.main()
