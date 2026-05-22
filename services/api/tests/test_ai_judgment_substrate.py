import unittest

from feeds.ai_judgment import (
    SourceCandidateJudgment,
    compare_judgment_verdict_overlap,
    default_model_for_provider,
    derive_selective_absorption_advice,
    derive_panel_insights,
    normalize_ai_judgments,
    parse_ai_judgment_payload,
)


class AIJudgmentSubstrateTests(unittest.TestCase):
    def test_parse_ai_judgment_payload_strips_fences(self):
        payload, status = parse_ai_judgment_payload(
            """```json
            {"summary":"ok","judgments":[]}
            ```"""
        )
        self.assertEqual(status, "valid_json")
        self.assertEqual(payload["summary"], "ok")

    def test_parse_ai_judgment_payload_falls_back_on_invalid_json(self):
        payload, status = parse_ai_judgment_payload("```json\n{\"summary\": [}\n```")
        self.assertEqual(status, "invalid_json_fallback")
        self.assertEqual(payload, {"summary": "", "judgments": []})

    def test_normalize_ai_judgments_filters_invalid_entries(self):
        judgments, summary, discarded = normalize_ai_judgments(
            {"a", "b"},
            {
                "summary": "test",
                "judgments": [
                    {"object_key": "a", "verdict": "follow", "rationale": "good", "confidence": 0.8},
                    {"object_key": "z", "verdict": "follow", "rationale": "bad key", "confidence": 0.8},
                    {"object_key": "b", "verdict": "weird", "rationale": "bad verdict", "confidence": 0.8},
                ],
            },
        )
        self.assertEqual(summary, "test")
        self.assertEqual(len(judgments), 1)
        self.assertEqual(judgments[0]["object_key"], "a")
        self.assertEqual(discarded, 2)

    def test_compare_judgment_verdict_overlap_requires_full_overlap_for_stable(self):
        primary = [
            SourceCandidateJudgment(
                object_key="a",
                item_type="domain",
                verdict="follow",
                rationale="good",
                confidence=0.9,
                review_priority="high",
            )
        ]
        secondary: list[SourceCandidateJudgment] = []
        summary = compare_judgment_verdict_overlap(primary, secondary)
        self.assertEqual(summary["panel_signal"], "mixed")
        self.assertEqual(summary["primary_only_count"], 1)

    def test_derive_panel_insights_review_review_is_not_consensus_worthy(self):
        primary = [
            SourceCandidateJudgment(
                object_key="paper-1",
                item_type="paper",
                verdict="review",
                rationale="interesting",
                confidence=0.85,
                review_priority="normal",
            )
        ]
        secondary = [
            SourceCandidateJudgment(
                object_key="paper-1",
                item_type="paper",
                verdict="review",
                rationale="needs checking",
                confidence=0.82,
                review_priority="normal",
            )
        ]
        insights = derive_panel_insights(primary, secondary)
        self.assertEqual(len(insights.consensus_worthy), 0)
        self.assertEqual(len(insights.disagreement_worthy), 0)
        self.assertEqual(len(insights.follow_up_hints), 1)

    def test_default_model_for_provider_is_provider_aware(self):
        self.assertEqual(default_model_for_provider("anthropic"), "claude-3-5-sonnet-20241022")
        self.assertEqual(default_model_for_provider("openai"), "gpt-4o")
        self.assertEqual(default_model_for_provider("ollama"), "qwen2:7b")

    def test_derive_selective_absorption_advice_promotes_high_confidence_follow_consensus(self):
        primary = [
            SourceCandidateJudgment(
                object_key="repo-1",
                item_type="repository",
                verdict="follow",
                rationale="core repo",
                confidence=0.91,
                review_priority="high",
            )
        ]
        secondary = [
            SourceCandidateJudgment(
                object_key="repo-1",
                item_type="repository",
                verdict="follow",
                rationale="same conclusion",
                confidence=0.84,
                review_priority="high",
            )
        ]
        advice = derive_selective_absorption_advice(primary, secondary)
        self.assertEqual(len(advice.ready_to_follow), 1)
        self.assertEqual(advice.ready_to_follow[0].object_key, "repo-1")
        self.assertEqual(advice.ready_to_follow[0].proposed_action, "follow")
        self.assertEqual(len(advice.needs_manual_review), 0)

    def test_derive_selective_absorption_advice_routes_conviction_gap_to_watch(self):
        primary = [
            SourceCandidateJudgment(
                object_key="thread-1",
                item_type="signal",
                verdict="follow",
                rationale="emerging signal",
                confidence=0.82,
                review_priority="high",
            )
        ]
        secondary = [
            SourceCandidateJudgment(
                object_key="thread-1",
                item_type="signal",
                verdict="review",
                rationale="promising but not enough yet",
                confidence=0.78,
                review_priority="normal",
            )
        ]
        advice = derive_selective_absorption_advice(primary, secondary)
        self.assertEqual(len(advice.watch_candidates), 1)
        self.assertEqual(advice.watch_candidates[0].basis, "conviction-gap")
        self.assertEqual(len(advice.needs_manual_review), 0)

    def test_derive_selective_absorption_advice_routes_polarized_to_manual_review(self):
        primary = [
            SourceCandidateJudgment(
                object_key="candidate-1",
                item_type="signal",
                verdict="follow",
                rationale="strong opportunity",
                confidence=0.88,
                review_priority="high",
            )
        ]
        secondary = [
            SourceCandidateJudgment(
                object_key="candidate-1",
                item_type="signal",
                verdict="ignore",
                rationale="looks like noise",
                confidence=0.81,
                review_priority="low",
            )
        ]
        advice = derive_selective_absorption_advice(primary, secondary)
        self.assertEqual(len(advice.needs_manual_review), 1)
        self.assertEqual(advice.needs_manual_review[0].basis, "polarized")
        self.assertEqual(len(advice.watch_candidates), 0)


if __name__ == "__main__":
    unittest.main()
