import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


api_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(api_dir))


def load_conversation_runtime_router_module():
    router_path = api_dir / "routers" / "conversation_runtime.py"
    spec = importlib.util.spec_from_file_location(
        "conversation_runtime_router_test_module", router_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


conversation_runtime_module = load_conversation_runtime_router_module()
conversation_runtime_router = conversation_runtime_module.router

test_app = FastAPI(title="Conversation Runtime Test API")
test_app.include_router(conversation_runtime_router, prefix="/api")


class _DummyClassifier:
    def classify(self, *args, **kwargs):
        return type("Authority", (), {"tier": "A", "score": 0.81})()


class ConversationRuntimeRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(test_app)

    def test_conversation_segment_inspect_extracts_source_candidate_and_judgment(self):
        class _DummyAdapter:
            def __init__(self):
                self._calls = 0

            async def chat(self, *args, **kwargs):
                self._calls += 1
                if self._calls == 1:
                    return """
                    {
                      "intent": "source_hint",
                      "summary": "user hinted at a repository source",
                      "source_candidates": [
                        {
                          "url": "https://github.com/openclaw/openclaw",
                          "context_note": "core repo for operator patterns"
                        }
                      ],
                      "correction_events": []
                    }
                    """
                return """
                {
                  "summary": "repository is worth following",
                  "judgments": [
                    {
                      "object_key": "github.com/openclaw/openclaw",
                      "verdict": "follow",
                      "rationale": "core implementation surface",
                      "confidence": 0.9,
                      "review_priority": "high"
                    }
                  ]
                }
                """

        with patch.object(
            conversation_runtime_module,
            "run_conversation_segment_inspect",
            wraps=conversation_runtime_module.run_conversation_segment_inspect,
        ), patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/inspect",
                json={
                    "conversation_text": "We should track https://github.com/openclaw/openclaw for operator patterns.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "find worth-following sources",
                    "focus": "method",
                    "interest_bias": "method",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["segment_intent"], "source_hint")
        self.assertEqual(len(data["source_candidates"]), 1)
        self.assertEqual(data["source_candidates"][0]["object_key"], "github.com/openclaw/openclaw")
        self.assertEqual(len(data["source_judgments"]), 1)
        self.assertEqual(data["source_judgments"][0]["verdict"], "follow")
        self.assertEqual(data["promotion_state"], "inspect_only")
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "review_source_candidates")
        self.assertEqual(data["controller_packet"]["review_mode"], "review_source_candidates")
        self.assertEqual(data["controller_packet"]["actionable_source_object_keys"], ["github.com/openclaw/openclaw"])
        self.assertIn("source_follow", data["controller_packet"]["reason_tags"])
        self.assertIn("raw conversation is not truth", " ".join(data["truth_boundary"]).lower())

    def test_conversation_segment_inspect_extracts_bounded_source_correction(self):
        class _DummyAdapter:
            def __init__(self):
                self._calls = 0

            async def chat(self, *args, **kwargs):
                self._calls += 1
                if self._calls == 1:
                    return """
                    {
                      "intent": "correction",
                      "summary": "user corrected source status",
                      "source_candidates": [],
                      "correction_events": [
                        {
                          "target_scope": "source_status",
                          "target_ref": "github.com/openclaw/openclaw",
                          "correction_content": "treat this as an active maintained source"
                        }
                      ]
                    }
                    """
                return """
                {
                  "summary": "this correction is worth review",
                  "judgments": [
                    {
                      "target_scope": "source_status",
                      "target_ref": "github.com/openclaw/openclaw",
                      "correction_content": "treat this as an active maintained source",
                      "verdict": "review",
                      "rationale": "clear bounded source-status correction",
                      "confidence": 0.84
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/inspect",
                json={
                    "conversation_text": "Correction: github.com/openclaw/openclaw is still active and should not be marked stale.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "capture source corrections",
                    "focus": "method",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["segment_intent"], "correction")
        self.assertEqual(len(data["correction_events"]), 1)
        self.assertEqual(len(data["correction_judgments"]), 1)
        self.assertEqual(data["correction_judgments"][0]["verdict"], "review")
        self.assertEqual(data["correction_summary"], "this correction is worth review")
        self.assertEqual(data["correction_events"][0]["target_scope"], "source_status")
        self.assertEqual(data["correction_events"][0]["proposal_state"], "proposed")
        self.assertEqual(data["correction_events"][0]["review_gate"], "controller_review_required")
        self.assertEqual(data["correction_events"][0]["absorption_state"], "not_absorbed")
        self.assertEqual(data["source_judgments"], [])
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "review_corrections")
        self.assertEqual(data["controller_packet"]["review_mode"], "review_corrections")
        self.assertEqual(data["controller_packet"]["advisory_scope"], "inspect_compression_only")
        self.assertEqual(data["controller_packet"]["truth_status"], "non_canonical")
        self.assertEqual(data["controller_packet"]["actionable_correction_targets"], ["source_status:github.com/openclaw/openclaw"])
        self.assertIn("correction_judgment_parse_status=valid_json", data["notes"])
        self.assertIn("discarded_corrections=0", data["notes"])
        self.assertIn("controller packet is advisory compression", " ".join(data["truth_boundary"]).lower())

    def test_conversation_segment_inspect_discards_out_of_scope_correction_and_stays_non_canonical(self):
        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "intent": "correction",
                  "summary": "entity correction should be ignored in phase 0",
                  "source_candidates": [],
                  "correction_events": [
                    {
                      "target_scope": "entity",
                      "target_ref": "OpenClaw",
                      "correction_content": "this is a framework not a repo"
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/inspect",
                json={
                    "conversation_text": "OpenClaw is a framework, not a repo.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "capture corrections",
                    "focus": "method",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["segment_intent"], "correction")
        self.assertEqual(data["correction_events"], [])
        self.assertEqual(data["promotion_state"], "inspect_only")
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "manual_review")
        self.assertIn("discarded_corrections=1", data["notes"])
        self.assertIn("not accepted state", " ".join(data["truth_boundary"]).lower())

    def test_conversation_segment_inspect_keeps_ignored_correction_manual(self):
        class _DummyAdapter:
            def __init__(self):
                self._calls = 0

            async def chat(self, *args, **kwargs):
                self._calls += 1
                if self._calls == 1:
                    return """
                    {
                      "intent": "correction",
                      "summary": "weak status correction",
                      "source_candidates": [],
                      "correction_events": [
                        {
                          "target_scope": "source_status",
                          "target_ref": "github.com/openclaw/openclaw",
                          "correction_content": "maybe stale, not sure"
                        }
                      ]
                    }
                    """
                return """
                {
                  "summary": "too vague to act on",
                  "judgments": [
                    {
                      "target_scope": "source_status",
                      "target_ref": "github.com/openclaw/openclaw",
                      "correction_content": "maybe stale, not sure",
                      "verdict": "ignore",
                      "rationale": "too weak and uncertain",
                      "confidence": 0.66
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/inspect",
                json={
                    "conversation_text": "Maybe github.com/openclaw/openclaw is stale, not sure.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "capture source corrections",
                    "focus": "method",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["correction_events"]), 1)
        self.assertEqual(len(data["correction_judgments"]), 1)
        self.assertEqual(data["correction_judgments"][0]["verdict"], "ignore")
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "manual_review")
        self.assertEqual(data["controller_packet"]["review_mode"], "manual_review")
        self.assertIn("manual_review_required", data["controller_packet"]["reason_tags"])
        self.assertIn("none are strong enough", " ".join(data["operational_advice"]["controller_notes"]).lower())

    def test_conversation_segment_inspect_other_segment_stays_no_action(self):
        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "intent": "other",
                  "summary": "general chatter with no bounded source or correction",
                  "source_candidates": [],
                  "correction_events": []
                }
                """

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/inspect",
                json={
                    "conversation_text": "Interesting direction overall, let's think more about it later.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "general reflection",
                    "focus": "method",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["segment_intent"], "other")
        self.assertEqual(data["source_candidates"], [])
        self.assertEqual(data["correction_events"], [])
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "no_action")
        self.assertEqual(data["controller_packet"]["review_mode"], "no_action")
        self.assertEqual(data["controller_packet"]["advisory_scope"], "inspect_compression_only")
        self.assertEqual(data["controller_packet"]["truth_status"], "non_canonical")
        self.assertIn("no_action", data["controller_packet"]["reason_tags"])

    def test_conversation_segment_panel_inspect_exposes_agreement_shape(self):
        class _DummyAdapter:
            def __init__(self):
                self._calls = 0

            async def chat(self, *args, **kwargs):
                self._calls += 1
                if self._calls == 1:
                    return """
                    {
                      "intent": "source_hint",
                      "summary": "conversation contains one repo hint",
                      "source_candidates": [
                        {
                          "url": "https://github.com/openclaw/openclaw",
                          "context_note": "core repo"
                        }
                      ],
                      "correction_events": []
                    }
                    """
                if self._calls == 2:
                    return """
                    {
                      "intent": "source_hint",
                      "summary": "secondary extraction sees the same repo",
                      "source_candidates": [
                        {
                          "url": "https://github.com/openclaw/openclaw",
                          "context_note": "same repo"
                        }
                      ],
                      "correction_events": []
                    }
                    """
                if self._calls == 3:
                    return """
                    {
                      "summary": "primary says follow",
                      "judgments": [
                        {
                          "object_key": "github.com/openclaw/openclaw",
                          "verdict": "follow",
                          "rationale": "primary sees core implementation value",
                          "confidence": 0.91,
                          "review_priority": "high"
                        }
                      ]
                    }
                    """
                return """
                {
                  "summary": "secondary says review",
                  "judgments": [
                    {
                      "object_key": "github.com/openclaw/openclaw",
                      "verdict": "review",
                      "rationale": "secondary wants more evidence first",
                      "confidence": 0.72,
                      "review_priority": "normal"
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/panel/inspect",
                json={
                    "conversation_text": "We should track https://github.com/openclaw/openclaw for operator patterns.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "compare source judgments",
                    "focus": "method",
                    "interest_bias": "method",
                    "primary_provider": "qwen",
                    "secondary_provider": "anthropic",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["segment_intent"], "source_hint")
        self.assertEqual(len(data["source_candidates"]), 1)
        self.assertEqual(len(data["primary_judgments"]), 1)
        self.assertEqual(len(data["secondary_judgments"]), 1)
        self.assertEqual(data["extraction_summary"]["source_candidate_signal"], "stable")
        self.assertEqual(data["panel_summary"]["panel_signal"], "mixed")
        self.assertEqual(data["panel_summary"]["disagreement_count"], 1)
        self.assertEqual(data["promotion_state"], "inspect_only")
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "manual_review")
        self.assertIn("selective_absorption", response.text)

    def test_conversation_segment_panel_inspect_handles_invalid_secondary_without_false_stable(self):
        class _DummyAdapter:
            def __init__(self):
                self._calls = 0

            async def chat(self, *args, **kwargs):
                self._calls += 1
                if self._calls == 1:
                    return """
                    {
                      "intent": "source_hint",
                      "summary": "conversation contains one repo hint",
                      "source_candidates": [
                        {
                          "url": "https://github.com/openclaw/openclaw",
                          "context_note": "core repo"
                        }
                      ],
                      "correction_events": []
                    }
                    """
                if self._calls == 2:
                    return "```json\n{bad json}\n```"
                if self._calls == 3:
                    return """
                    {
                      "summary": "primary says follow",
                      "judgments": [
                        {
                          "object_key": "github.com/openclaw/openclaw",
                          "verdict": "follow",
                          "rationale": "core implementation surface",
                          "confidence": 0.88,
                          "review_priority": "high"
                        }
                      ]
                    }
                    """
                return "```json\n{bad json}\n```"

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/panel/inspect",
                json={
                    "conversation_text": "We should track https://github.com/openclaw/openclaw for operator patterns.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "compare source judgments",
                    "focus": "method",
                    "primary_provider": "qwen",
                    "secondary_provider": "anthropic",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["extraction_summary"]["source_candidate_signal"], "mixed")
        self.assertEqual(data["panel_summary"]["panel_signal"], "mixed")
        self.assertEqual(data["panel_summary"]["secondary_only_count"], 0)
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "manual_review")
        self.assertIn("secondary_extraction_parse_status=invalid_json_fallback", data["notes"])

    def test_conversation_segment_panel_inspect_merges_secondary_only_extraction(self):
        class _DummyAdapter:
            def __init__(self):
                self._calls = 0

            async def chat(self, *args, **kwargs):
                self._calls += 1
                if self._calls == 1:
                    return """
                    {
                      "intent": "source_hint",
                      "summary": "primary extraction sees one repo",
                      "source_candidates": [
                        {
                          "url": "https://github.com/openclaw/openclaw",
                          "context_note": "primary repo"
                        }
                      ],
                      "correction_events": []
                    }
                    """
                if self._calls == 2:
                    return """
                    {
                      "intent": "source_hint",
                      "summary": "secondary extraction sees an extra issue thread",
                      "source_candidates": [
                        {
                          "url": "https://github.com/openclaw/openclaw",
                          "context_note": "same repo"
                        },
                        {
                          "url": "https://github.com/openclaw/openclaw/issues/42",
                          "context_note": "secondary-only thread"
                        }
                      ],
                      "correction_events": []
                    }
                    """
                if self._calls == 3:
                    return """
                    {
                      "summary": "primary judgments",
                      "judgments": [
                        {
                          "object_key": "github.com/openclaw/openclaw",
                          "verdict": "follow",
                          "rationale": "core repo",
                          "confidence": 0.88,
                          "review_priority": "high"
                        },
                        {
                          "object_key": "github.com/openclaw/openclaw/issues/42",
                          "verdict": "review",
                          "rationale": "interesting issue thread",
                          "confidence": 0.74,
                          "review_priority": "normal"
                        }
                      ]
                    }
                    """
                return """
                {
                  "summary": "secondary judgments",
                  "judgments": [
                    {
                      "object_key": "github.com/openclaw/openclaw",
                      "verdict": "follow",
                      "rationale": "same repo",
                      "confidence": 0.82,
                      "review_priority": "high"
                    },
                    {
                      "object_key": "github.com/openclaw/openclaw/issues/42",
                      "verdict": "follow",
                      "rationale": "issue thread looks action-worthy",
                      "confidence": 0.8,
                      "review_priority": "high"
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/panel/inspect",
                json={
                    "conversation_text": "We should track the main repo and the issue thread at github.com/openclaw/openclaw/issues/42.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "compare extracted source judgments",
                    "focus": "frontier",
                    "primary_provider": "qwen",
                    "secondary_provider": "anthropic",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["source_candidates"]), 2)
        self.assertEqual(data["extraction_summary"]["primary_only_source_candidate_count"], 0)
        self.assertEqual(data["extraction_summary"]["secondary_only_source_candidate_count"], 1)
        self.assertEqual(data["extraction_summary"]["merged_source_candidate_count"], 2)
        self.assertEqual(data["panel_summary"]["agreement_count"], 1)
        self.assertEqual(data["panel_summary"]["disagreement_count"], 0)
        self.assertEqual(data["panel_summary"]["panel_signal"], "stable")
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "manual_review")
        self.assertIn(
            "extraction divergence should be treated as an opportunity for controller review",
            " ".join(data["operational_advice"]["controller_notes"]).lower(),
        )

    def test_conversation_segment_panel_inspect_other_segment_stays_no_action(self):
        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "intent": "other",
                  "summary": "this is general discussion only",
                  "source_candidates": [],
                  "correction_events": []
                }
                """

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/panel/inspect",
                json={
                    "conversation_text": "This is interesting but not a concrete source or correction yet.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "understand general direction",
                    "focus": "method",
                    "primary_provider": "qwen",
                    "secondary_provider": "anthropic",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["segment_intent"], "other")
        self.assertEqual(data["source_candidates"], [])
        self.assertEqual(data["correction_events"], [])
        self.assertEqual(data["panel_summary"], {})
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "no_action")

    def test_conversation_segment_panel_inspect_mixed_intent_stays_manual_review(self):
        class _DummyAdapter:
            def __init__(self):
                self._calls = 0

            async def chat(self, *args, **kwargs):
                self._calls += 1
                if self._calls == 1:
                    return """
                    {
                      "intent": "source_hint",
                      "summary": "primary sees a repo source",
                      "source_candidates": [
                        {
                          "url": "https://github.com/openclaw/openclaw",
                          "context_note": "core repo"
                        }
                      ],
                      "correction_events": []
                    }
                    """
                if self._calls == 2:
                    return """
                    {
                      "intent": "correction",
                      "summary": "secondary sees a status correction",
                      "source_candidates": [],
                      "correction_events": [
                        {
                          "target_scope": "source_status",
                          "target_ref": "github.com/openclaw/openclaw",
                          "correction_content": "treat this as active"
                        }
                      ]
                    }
                    """
                if self._calls == 3:
                    return """
                    {
                      "summary": "primary says follow",
                      "judgments": [
                        {
                          "object_key": "github.com/openclaw/openclaw",
                          "verdict": "follow",
                          "rationale": "core repo",
                          "confidence": 0.9,
                          "review_priority": "high"
                        }
                      ]
                    }
                    """
                return """
                {
                  "summary": "secondary says review",
                  "judgments": [
                    {
                      "target_scope": "source_status",
                      "target_ref": "github.com/openclaw/openclaw",
                      "correction_content": "treat this as active",
                      "verdict": "review",
                      "rationale": "bounded correction",
                      "confidence": 0.8
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/panel/inspect",
                json={
                    "conversation_text": "Track github.com/openclaw/openclaw. Correction: treat it as active.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "mixed source and correction",
                    "focus": "method",
                    "primary_provider": "qwen",
                    "secondary_provider": "anthropic",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["extraction_summary"]["intent_signal"], "mixed")
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "manual_review")
        self.assertEqual(data["controller_packet"]["review_mode"], "manual_review")
        self.assertIn("models disagreed on segment intent classification", " ".join(data["operational_advice"]["controller_notes"]).lower())

    def test_conversation_segment_inspect_marks_truncated_conversation_window(self):
        filler = "noise " * 260
        tail = "Please track https://github.com/openclaw/openclaw for operator patterns."

        class _DummyAdapter:
            def __init__(self):
                self.messages = []
                self._calls = 0

            async def chat(self, *args, **kwargs):
                self._calls += 1
                self.messages.append(kwargs["message"])
                if self._calls == 1:
                    return """
                    {
                      "intent": "source_hint",
                      "summary": "tail contains one repo source",
                      "source_candidates": [
                        {
                          "url": "https://github.com/openclaw/openclaw",
                          "context_note": "tail repo"
                        }
                      ],
                      "correction_events": []
                    }
                    """
                return """
                {
                  "summary": "worth review",
                  "judgments": [
                    {
                      "object_key": "github.com/openclaw/openclaw",
                      "verdict": "review",
                      "rationale": "bounded source candidate",
                      "confidence": 0.72,
                      "review_priority": "normal"
                    }
                  ]
                }
                """

        adapter = _DummyAdapter()
        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=adapter,
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/inspect",
                json={
                    "conversation_text": filler + tail,
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "find source in long noisy text",
                    "focus": "method",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("conversation_window_truncated=true", data["notes"])
        self.assertIn("[conversation window truncated for bounded inspect]", adapter.messages[0])
        self.assertIn("https://github.com/openclaw/openclaw", adapter.messages[0])
        self.assertIn("https://github.com/openclaw/openclaw", data["source_candidates"][0]["sample_snippets"][0])

    def test_conversation_segment_panel_inspect_reviews_corrections(self):
        class _DummyAdapter:
            def __init__(self):
                self._calls = 0

            async def chat(self, *args, **kwargs):
                self._calls += 1
                if self._calls == 1:
                    return """
                    {
                      "intent": "correction",
                      "summary": "primary extracted a source status correction",
                      "source_candidates": [],
                      "correction_events": [
                        {
                          "target_scope": "source_status",
                          "target_ref": "github.com/openclaw/openclaw",
                          "correction_content": "treat this as active rather than stale"
                        }
                      ]
                    }
                    """
                if self._calls == 2:
                    return """
                    {
                      "intent": "correction",
                      "summary": "secondary extracted the same correction",
                      "source_candidates": [],
                      "correction_events": [
                        {
                          "target_scope": "source_status",
                          "target_ref": "github.com/openclaw/openclaw",
                          "correction_content": "treat this as active rather than stale"
                        }
                      ]
                    }
                    """
                if self._calls == 3:
                    return """
                    {
                      "summary": "primary says review",
                      "judgments": [
                        {
                          "target_scope": "source_status",
                          "target_ref": "github.com/openclaw/openclaw",
                          "correction_content": "treat this as active rather than stale",
                          "verdict": "review",
                          "rationale": "clear status correction",
                          "confidence": 0.86
                        }
                      ]
                    }
                    """
                return """
                {
                  "summary": "secondary also says review",
                  "judgments": [
                    {
                      "target_scope": "source_status",
                      "target_ref": "github.com/openclaw/openclaw",
                      "correction_content": "treat this as active rather than stale",
                      "verdict": "review",
                      "rationale": "same bounded correction",
                      "confidence": 0.79
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/panel/inspect",
                json={
                    "conversation_text": "Correction: github.com/openclaw/openclaw is active, not stale.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "compare correction review",
                    "focus": "method",
                    "primary_provider": "qwen",
                    "secondary_provider": "anthropic",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["correction_events"]), 1)
        self.assertEqual(len(data["primary_correction_judgments"]), 1)
        self.assertEqual(len(data["secondary_correction_judgments"]), 1)
        self.assertEqual(data["correction_panel_summary"]["panel_signal"], "stable")
        self.assertEqual(data["correction_panel_summary"]["agreement_count"], 1)
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "review_corrections")
        self.assertEqual(data["controller_packet"]["review_mode"], "review_corrections")
        self.assertEqual(data["controller_packet"]["actionable_correction_targets"], ["source_status:github.com/openclaw/openclaw"])
        self.assertIn("stable_correction_panel", data["controller_packet"]["reason_tags"])
        self.assertIn("correction panel signal is stable", " ".join(data["operational_advice"]["controller_notes"]).lower())

    def test_conversation_segment_panel_inspect_handles_invalid_secondary_correction_review(self):
        class _DummyAdapter:
            def __init__(self):
                self._calls = 0

            async def chat(self, *args, **kwargs):
                self._calls += 1
                if self._calls == 1:
                    return """
                    {
                      "intent": "correction",
                      "summary": "primary extracted correction",
                      "source_candidates": [],
                      "correction_events": [
                        {
                          "target_scope": "source_status",
                          "target_ref": "github.com/openclaw/openclaw",
                          "correction_content": "treat this as active rather than stale"
                        }
                      ]
                    }
                    """
                if self._calls == 2:
                    return """
                    {
                      "intent": "correction",
                      "summary": "secondary extracted the same correction",
                      "source_candidates": [],
                      "correction_events": [
                        {
                          "target_scope": "source_status",
                          "target_ref": "github.com/openclaw/openclaw",
                          "correction_content": "treat this as active rather than stale"
                        }
                      ]
                    }
                    """
                if self._calls == 3:
                    return """
                    {
                      "summary": "primary says review",
                      "judgments": [
                        {
                          "target_scope": "source_status",
                          "target_ref": "github.com/openclaw/openclaw",
                          "correction_content": "treat this as active rather than stale",
                          "verdict": "review",
                          "rationale": "clear status correction",
                          "confidence": 0.86
                        }
                      ]
                    }
                    """
                return "```json\n{bad json}\n```"

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/panel/inspect",
                json={
                    "conversation_text": "Correction: github.com/openclaw/openclaw is active, not stale.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "compare correction review",
                    "focus": "method",
                    "primary_provider": "qwen",
                    "secondary_provider": "anthropic",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["correction_panel_summary"]["panel_signal"], "mixed")
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "manual_review")
        self.assertEqual(data["controller_packet"]["review_mode"], "manual_review")
        self.assertIn("secondary_correction_parse_status=invalid_json_fallback", data["notes"])

    def test_conversation_segment_inspect_compresses_generic_domain_when_specific_source_exists(self):
        class _DummyAdapter:
            def __init__(self):
                self._calls = 0

            async def chat(self, *args, **kwargs):
                self._calls += 1
                if self._calls == 1:
                    return """
                    {
                      "intent": "source_hint",
                      "summary": "conversation contains a generic domain and a specific repo",
                      "source_candidates": [
                        {
                          "url": "https://github.com",
                          "context_note": "generic github mention"
                        },
                        {
                          "url": "https://github.com/openclaw/openclaw",
                          "context_note": "main implementation repo"
                        }
                      ],
                      "correction_events": []
                    }
                    """
                return """
                {
                  "summary": "repo is the real candidate worth review",
                  "judgments": [
                    {
                      "object_key": "github.com/openclaw/openclaw",
                      "verdict": "review",
                      "rationale": "specific repo is stronger than generic domain",
                      "confidence": 0.82,
                      "review_priority": "normal"
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/inspect",
                json={
                    "conversation_text": "We may use github broadly, but the real source is https://github.com/openclaw/openclaw.",
                    "speaker_role": "user",
                    "topic": "operator patterns",
                    "task_intent": "find the concrete implementation source",
                    "focus": "method",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        object_keys = [candidate["object_key"] for candidate in data["source_candidates"]]
        self.assertIn("github.com/openclaw/openclaw", object_keys)
        self.assertNotIn("github.com", object_keys)
        self.assertEqual(len(data["source_judgments"]), 1)
        self.assertEqual(data["source_judgments"][0]["object_key"], "github.com/openclaw/openclaw")
        self.assertEqual(data["intent_trace"]["source_candidates_before_compression"], 2)
        self.assertEqual(data["intent_trace"]["source_candidates_after_compression"], 1)
        self.assertIn("github.com", data["intent_trace"]["dropped_source_object_keys"])
        self.assertEqual(data["intent_trace"]["raw_segment_intent"], "source_hint")

    def test_conversation_segment_panel_inspect_prefers_release_over_duplicate_repository_in_latest_focus(self):
        class _DummyAdapter:
            def __init__(self):
                self._calls = 0

            async def chat(self, *args, **kwargs):
                self._calls += 1
                if self._calls == 1:
                    return """
                    {
                      "intent": "source_hint",
                      "summary": "primary extracted repo and release",
                      "source_candidates": [
                        {
                          "url": "https://github.com/openclaw/openclaw",
                          "context_note": "base repository"
                        },
                        {
                          "url": "https://github.com/openclaw/openclaw/releases",
                          "context_note": "latest release stream"
                        }
                      ],
                      "correction_events": []
                    }
                    """
                if self._calls == 2:
                    return """
                    {
                      "intent": "source_hint",
                      "summary": "secondary extracted the same repo and release",
                      "source_candidates": [
                        {
                          "url": "https://github.com/openclaw/openclaw",
                          "context_note": "base repository"
                        },
                        {
                          "url": "https://github.com/openclaw/openclaw/releases",
                          "context_note": "latest release stream"
                        }
                      ],
                      "correction_events": []
                    }
                    """
                if self._calls == 3:
                    return """
                    {
                      "summary": "release is the timely object worth review",
                      "judgments": [
                        {
                          "object_key": "github.com/openclaw/openclaw/release/latest",
                          "verdict": "follow",
                          "rationale": "latest focus should prioritize release surface",
                          "confidence": 0.88,
                          "review_priority": "high"
                        }
                      ]
                    }
                    """
                return """
                {
                  "summary": "secondary also prefers the release",
                  "judgments": [
                    {
                      "object_key": "github.com/openclaw/openclaw/release/latest",
                      "verdict": "follow",
                      "rationale": "same timely release preference",
                      "confidence": 0.81,
                      "review_priority": "high"
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.p0.LLMAdapter",
            return_value=_DummyAdapter(),
        ), patch(
            "conversation_runtime.p0.get_authority_classifier",
            return_value=_DummyClassifier(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/segments/panel/inspect",
                json={
                    "conversation_text": "Track the OpenClaw repo, but for latest updates the release stream matters more.",
                    "speaker_role": "user",
                    "topic": "openclaw latest releases",
                    "task_intent": "prefer timely release surface over duplicate repository",
                    "focus": "latest",
                    "primary_provider": "qwen",
                    "secondary_provider": "anthropic",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        object_keys = [candidate["object_key"] for candidate in data["source_candidates"]]
        self.assertIn("github.com/openclaw/openclaw/release/latest", object_keys)
        self.assertNotIn("github.com/openclaw/openclaw", object_keys)
        self.assertEqual(len(data["primary_judgments"]), 1)
        self.assertEqual(data["primary_judgments"][0]["object_key"], "github.com/openclaw/openclaw/release/latest")
        self.assertEqual(data["panel_summary"]["panel_signal"], "stable")
        self.assertEqual(data["intent_trace"]["source_candidates_before_compression"], 2)
        self.assertEqual(data["intent_trace"]["source_candidates_after_compression"], 1)
        self.assertIn(
            "github.com/openclaw/openclaw",
            data["intent_trace"]["dropped_source_object_keys"],
        )
        self.assertEqual(data["intent_trace"]["primary_raw_intent"], "source_hint")
        self.assertEqual(data["intent_trace"]["secondary_raw_intent"], "source_hint")
