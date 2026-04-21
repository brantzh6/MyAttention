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
        "conversation_runtime_router_test_module_flywheel", router_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


conversation_runtime_module = load_conversation_runtime_router_module()
conversation_runtime_router = conversation_runtime_module.router

test_app = FastAPI(title="Flywheel Inspect Test API")
test_app.include_router(conversation_runtime_router, prefix="/api")


class _DummyClassifier:
    def classify(self, *args, **kwargs):
        return type("Authority", (), {"tier": "A", "score": 0.81})()


class FlywheelInspectRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(test_app)

    def test_flywheel_inspect_extracts_knowledge_and_evolution_candidates(self):
        """Happy path: conversation yields both knowledge deltas and evolution triggers."""

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "intent": "flywheel_signal",
                  "summary": "conversation contains knowledge claims and evolution opportunities",
                  "source_candidates": [],
                  "correction_events": [],
                  "knowledge_delta_candidates": [
                    {
                      "delta_type": "claim",
                      "label": "OpenClaw uses operator pattern",
                      "content": "The OpenClaw framework implements the operator pattern for composable AI workflows"
                    },
                    {
                      "delta_type": "boundary",
                      "label": "operator scope limit",
                      "content": "Operators should not manage state outside their own scope"
                    }
                  ],
                  "evolution_trigger_candidates": [
                    {
                      "trigger_type": "study",
                      "label": "Study operator composition",
                      "rationale": "Understanding operator composition would improve source evaluation"
                    },
                    {
                      "trigger_type": "prototype",
                      "label": "Prototype operator evaluator",
                      "rationale": "A small prototype could validate whether operator patterns apply to source ranking"
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.flywheel.LLMAdapter",
            return_value=_DummyAdapter(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/flywheel/inspect",
                json={
                    "conversation_text": "OpenClaw uses the operator pattern for composable AI workflows. We should study this and maybe prototype an evaluator.",
                    "speaker_role": "user",
                    "topic": "operator patterns in AI frameworks",
                    "task_intent": "identify knowledge and evolution opportunities",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["segment_intent"], "flywheel_signal")
        self.assertEqual(len(data["knowledge_delta_candidates"]), 2)
        self.assertEqual(len(data["evolution_trigger_candidates"]), 2)
        self.assertEqual(data["knowledge_delta_candidates"][0]["delta_type"], "claim")
        self.assertEqual(data["knowledge_delta_candidates"][0]["label"], "OpenClaw uses operator pattern")
        self.assertEqual(data["knowledge_delta_candidates"][0]["trust_state"], "candidate")
        self.assertEqual(data["knowledge_delta_candidates"][0]["proposal_state"], "proposed")
        self.assertEqual(data["knowledge_delta_candidates"][0]["review_gate"], "controller_review_required")
        self.assertEqual(data["knowledge_delta_candidates"][0]["absorption_state"], "not_absorbed")
        self.assertEqual(data["evolution_trigger_candidates"][0]["trigger_type"], "study")
        self.assertEqual(data["evolution_trigger_candidates"][1]["trigger_type"], "prototype")
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "review_flywheel_candidates")
        self.assertEqual(data["controller_packet"]["review_mode"], "review_flywheel_candidates")
        self.assertIn("knowledge_delta_review", data["controller_packet"]["reason_tags"])
        self.assertIn("evolution_trigger_review", data["controller_packet"]["reason_tags"])
        self.assertEqual(data["promotion_state"], "inspect_only")
        self.assertEqual(data["controller_packet"]["truth_status"], "non_canonical")
        self.assertEqual(data["controller_packet"]["advisory_scope"], "flywheel_inspect_only")

    def test_flywheel_inspect_noisy_input_yields_no_candidates(self):
        """Noisy input with no actionable content falls back to no_action."""

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "intent": "other",
                  "summary": "general chatter with no actionable content",
                  "source_candidates": [],
                  "correction_events": [],
                  "knowledge_delta_candidates": [],
                  "evolution_trigger_candidates": []
                }
                """

        with patch(
            "conversation_runtime.flywheel.LLMAdapter",
            return_value=_DummyAdapter(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/flywheel/inspect",
                json={
                    "conversation_text": "This is interesting but I have nothing concrete to add right now.",
                    "speaker_role": "user",
                    "topic": "general discussion",
                    "task_intent": "general reflection",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["segment_intent"], "other")
        self.assertEqual(data["knowledge_delta_candidates"], [])
        self.assertEqual(data["evolution_trigger_candidates"], [])
        self.assertEqual(data["source_candidates"], [])
        self.assertEqual(data["correction_events"], [])
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "no_action")
        self.assertEqual(data["controller_packet"]["review_mode"], "no_action")
        self.assertIn("no_action", data["controller_packet"]["reason_tags"])
        self.assertEqual(data["promotion_state"], "inspect_only")

    def test_flywheel_inspect_explicit_non_canonical_boundary(self):
        """Verify truth boundary and inspect-only markers are always present."""

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "intent": "flywheel_signal",
                  "summary": "one concept extracted",
                  "source_candidates": [],
                  "correction_events": [],
                  "knowledge_delta_candidates": [
                    {
                      "delta_type": "concept",
                      "label": "bounded inspect",
                      "content": "flywheel inspect is strictly non-canonical"
                    }
                  ],
                  "evolution_trigger_candidates": []
                }
                """

        with patch(
            "conversation_runtime.flywheel.LLMAdapter",
            return_value=_DummyAdapter(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/flywheel/inspect",
                json={
                    "conversation_text": "The flywheel inspect should remain strictly non-canonical.",
                    "speaker_role": "user",
                    "topic": "flywheel design",
                    "task_intent": "verify boundary enforcement",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["promotion_state"], "inspect_only")
        self.assertEqual(data["controller_packet"]["truth_status"], "non_canonical")
        truth_text = " ".join(data["truth_boundary"]).lower()
        self.assertIn("not canonical knowledge", truth_text)
        self.assertIn("not accepted knowledge state", truth_text)
        self.assertIn("not scheduled actions", truth_text)
        self.assertIn("does not auto-promote", truth_text)
        self.assertIn("not a workflow contract", truth_text)
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "review_knowledge_deltas")
        self.assertEqual(len(data["knowledge_delta_candidates"]), 1)
        self.assertEqual(data["knowledge_delta_candidates"][0]["delta_type"], "concept")

    def test_flywheel_inspect_filters_invalid_delta_types(self):
        """Invalid delta_type values are filtered out, valid ones are kept."""

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "intent": "flywheel_signal",
                  "summary": "mixed valid and invalid candidates",
                  "source_candidates": [],
                  "correction_events": [],
                  "knowledge_delta_candidates": [
                    {
                      "delta_type": "claim",
                      "label": "valid claim",
                      "content": "a real claim"
                    },
                    {
                      "delta_type": "invalid_type",
                      "label": "invalid delta",
                      "content": "should be filtered"
                    },
                    {
                      "delta_type": "concept",
                      "label": "",
                      "content": "missing label should be filtered"
                    },
                    {
                      "delta_type": "relation",
                      "label": "valid relation",
                      "content": "a real relation"
                    }
                  ],
                  "evolution_trigger_candidates": [
                    {
                      "trigger_type": "study",
                      "label": "valid study trigger",
                      "rationale": "worth investigating"
                    },
                    {
                      "trigger_type": "bad_trigger",
                      "label": "invalid trigger",
                      "rationale": "should be filtered"
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.flywheel.LLMAdapter",
            return_value=_DummyAdapter(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/flywheel/inspect",
                json={
                    "conversation_text": "Some valid and invalid candidates here.",
                    "speaker_role": "user",
                    "topic": "filtering test",
                    "task_intent": "test filtering",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["knowledge_delta_candidates"]), 2)
        delta_types = [d["delta_type"] for d in data["knowledge_delta_candidates"]]
        self.assertIn("claim", delta_types)
        self.assertIn("relation", delta_types)
        self.assertNotIn("invalid_type", delta_types)
        self.assertEqual(len(data["evolution_trigger_candidates"]), 1)
        self.assertEqual(data["evolution_trigger_candidates"][0]["trigger_type"], "study")

    def test_flywheel_inspect_with_source_candidate_and_correction(self):
        """Flywheel route also yields source candidates and corrections via P0 normalization."""

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "intent": "source_hint",
                  "summary": "conversation has a source hint and a correction",
                  "source_candidates": [
                    {
                      "url": "https://github.com/openclaw/openclaw",
                      "context_note": "core repo"
                    }
                  ],
                  "correction_events": [
                    {
                      "target_scope": "source_status",
                      "target_ref": "github.com/openclaw/openclaw",
                      "correction_content": "treat as active"
                    }
                  ],
                  "knowledge_delta_candidates": [],
                  "evolution_trigger_candidates": []
                }
                """

        with patch(
            "conversation_runtime.flywheel.LLMAdapter",
            return_value=_DummyAdapter(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/flywheel/inspect",
                json={
                    "conversation_text": "Track https://github.com/openclaw/openclaw and treat it as active.",
                    "speaker_role": "user",
                    "topic": "source tracking",
                    "task_intent": "identify sources",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["segment_intent"], "source_hint")
        self.assertEqual(len(data["source_candidates"]), 1)
        self.assertEqual(data["source_candidates"][0]["object_key"], "github.com/openclaw/openclaw")
        self.assertEqual(len(data["correction_events"]), 1)
        self.assertEqual(data["correction_events"][0]["target_scope"], "source_status")
        self.assertEqual(data["correction_events"][0]["proposal_state"], "proposed")
        self.assertEqual(data["correction_events"][0]["review_gate"], "controller_review_required")
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "review_source_candidates")
        self.assertIn("source-level candidates only", " ".join(data["operational_advice"]["controller_notes"]).lower())

    def test_flywheel_inspect_discards_out_of_scope_correction(self):
        """Out-of-scope corrections (e.g. entity) are discarded by P0 normalization."""

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "intent": "correction",
                  "summary": "entity correction should be discarded",
                  "source_candidates": [],
                  "correction_events": [
                    {
                      "target_scope": "entity",
                      "target_ref": "OpenClaw",
                      "correction_content": "this is a framework not a repo"
                    }
                  ],
                  "knowledge_delta_candidates": [],
                  "evolution_trigger_candidates": []
                }
                """

        with patch(
            "conversation_runtime.flywheel.LLMAdapter",
            return_value=_DummyAdapter(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/flywheel/inspect",
                json={
                    "conversation_text": "OpenClaw is a framework, not a repo.",
                    "speaker_role": "user",
                    "topic": "classification",
                    "task_intent": "correction",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["correction_events"], [])
        self.assertIn("discarded_corrections=1", data["notes"])
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "manual_review")

    def test_flywheel_inspect_handles_invalid_json_gracefully(self):
        """Invalid LLM JSON response falls back to empty candidates."""

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return "```json\n{bad json}\n```"

        with patch(
            "conversation_runtime.flywheel.LLMAdapter",
            return_value=_DummyAdapter(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/flywheel/inspect",
                json={
                    "conversation_text": "Some text that will hit invalid JSON.",
                    "speaker_role": "user",
                    "topic": "fallback test",
                    "task_intent": "test error handling",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["segment_intent"], "other")
        self.assertEqual(data["knowledge_delta_candidates"], [])
        self.assertEqual(data["evolution_trigger_candidates"], [])
        self.assertEqual(data["source_candidates"], [])
        self.assertEqual(data["correction_events"], [])
        self.assertIn("conversation_parse_status=invalid_json_fallback", data["notes"])
        self.assertEqual(data["promotion_state"], "inspect_only")
        self.assertEqual(data["controller_packet"]["truth_status"], "non_canonical")

    def test_flywheel_inspect_evolution_only_triggers_review(self):
        """When only evolution triggers exist (no knowledge deltas), advice targets them."""

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "intent": "flywheel_signal",
                  "summary": "only evolution triggers found",
                  "source_candidates": [],
                  "correction_events": [],
                  "knowledge_delta_candidates": [],
                  "evolution_trigger_candidates": [
                    {
                      "trigger_type": "review",
                      "label": "Review source strategy",
                      "rationale": "Current strategy may not cover operator-pattern sources"
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.flywheel.LLMAdapter",
            return_value=_DummyAdapter(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/flywheel/inspect",
                json={
                    "conversation_text": "We should review our source strategy for operator patterns.",
                    "speaker_role": "user",
                    "topic": "source strategy",
                    "task_intent": "evolution opportunity",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["evolution_trigger_candidates"]), 1)
        self.assertEqual(data["evolution_trigger_candidates"][0]["trigger_type"], "review")
        self.assertEqual(data["evolution_trigger_candidates"][0]["trust_state"], "candidate")
        self.assertEqual(data["evolution_trigger_candidates"][0]["proposal_state"], "proposed")
        self.assertEqual(data["evolution_trigger_candidates"][0]["review_gate"], "controller_review_required")
        self.assertEqual(data["evolution_trigger_candidates"][0]["absorption_state"], "not_absorbed")
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "review_evolution_triggers")
        self.assertEqual(data["controller_packet"]["review_mode"], "review_evolution_triggers")
        self.assertIn("evolution_trigger_review", data["controller_packet"]["reason_tags"])
        self.assertNotIn("knowledge_delta_review", data["controller_packet"]["reason_tags"])

    # ---------------------------------------------------------------------------
    # Task-packet preview route tests
    # ---------------------------------------------------------------------------

    def test_task_packet_preview_knowledge_evolution_driven(self):
        """Task-packet with both knowledge and evolution labels -> mixed intent."""
        response = self.client.post(
            "/api/conversation-runtime/flywheel/task-packet/preview",
            json={
                "topic": "IKE architecture",
                "task_intent": "review knowledge candidates",
                "selected_knowledge_labels": ["claim:source-value", "concept:flywheel"],
                "selected_evolution_labels": ["study:multi-brain-runtime"],
                "selected_source_labels": [],
                "reviewer_note": "Needs priority sequencing",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["packet_intent"], "mixed")
        self.assertEqual(data["suggested_lane"], "mixed_review")
        self.assertEqual(data["suggested_next_step"], "prioritize_and_sequence")
        self.assertEqual(len(data["selected_label_groups"]), 2)

        knowledge_group = next(
            (g for g in data["selected_label_groups"] if g["label_type"] == "knowledge"), None
        )
        self.assertIsNotNone(knowledge_group)
        self.assertEqual(knowledge_group["count"], 2)
        self.assertIn("claim:source-value", knowledge_group["labels"])

        evolution_group = next(
            (g for g in data["selected_label_groups"] if g["label_type"] == "evolution"), None
        )
        self.assertIsNotNone(evolution_group)
        self.assertEqual(evolution_group["count"], 1)

        self.assertEqual(data["promotion_state"], "inspect_only")
        self.assertTrue(len(data["truth_boundary"]) > 0)
        self.assertEqual(data["controller_packet"]["truth_status"], "non_canonical")
        self.assertIn("mixed", data["controller_packet"]["reason_tags"])

    def test_task_packet_preview_source_only(self):
        """Task-packet with only source labels -> source_driven intent."""
        response = self.client.post(
            "/api/conversation-runtime/flywheel/task-packet/preview",
            json={
                "topic": "Source discovery",
                "task_intent": "review source candidates",
                "selected_knowledge_labels": [],
                "selected_evolution_labels": [],
                "selected_source_labels": ["36kr", "github.com/project"],
                "reviewer_note": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["packet_intent"], "source_driven")
        self.assertEqual(data["suggested_lane"], "source_review")
        self.assertEqual(data["suggested_next_step"], "review_source_candidates")
        self.assertEqual(len(data["selected_label_groups"]), 1)

        source_group = data["selected_label_groups"][0]
        self.assertEqual(source_group["label_type"], "source")
        self.assertEqual(source_group["count"], 2)
        self.assertIn("36kr", source_group["labels"])

        self.assertEqual(data["promotion_state"], "inspect_only")
        self.assertTrue(len(data["truth_boundary"]) > 0)
        self.assertEqual(data["controller_packet"]["truth_status"], "non_canonical")
        self.assertEqual(data["controller_packet"]["advisory_scope"], "task_packet_preview")
        self.assertIn("source_driven", data["controller_packet"]["reason_tags"])

    def test_task_packet_preview_empty_no_action_fallback(self):
        """Empty task-packet -> no_action fallback."""
        response = self.client.post(
            "/api/conversation-runtime/flywheel/task-packet/preview",
            json={
                "topic": "Empty test",
                "task_intent": "no actionable content",
                "selected_knowledge_labels": [],
                "selected_evolution_labels": [],
                "selected_source_labels": [],
                "reviewer_note": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["packet_intent"], "no_action")
        self.assertEqual(data["suggested_lane"], "no_action")
        self.assertEqual(data["suggested_next_step"], "no_action")
        self.assertEqual(len(data["selected_label_groups"]), 0)

        self.assertEqual(data["promotion_state"], "inspect_only")
        self.assertTrue(len(data["truth_boundary"]) > 0)
        self.assertIn("no_action", data["controller_packet"]["reason_tags"])

    def test_task_packet_preview_empty_with_reviewer_note(self):
        """Empty task-packet with reviewer note -> manual_review_with_note."""
        response = self.client.post(
            "/api/conversation-runtime/flywheel/task-packet/preview",
            json={
                "topic": "Ambiguous case",
                "task_intent": "needs human review",
                "selected_knowledge_labels": [],
                "selected_evolution_labels": [],
                "selected_source_labels": [],
                "reviewer_note": "Controller flagged for manual discussion",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["packet_intent"], "no_action")
        self.assertEqual(data["suggested_lane"], "no_action")
        self.assertEqual(data["suggested_next_step"], "manual_review_with_note")
        self.assertEqual(len(data["selected_label_groups"]), 0)

        self.assertEqual(data["promotion_state"], "inspect_only")
        self.assertIn("reviewer_note_present=true", data["notes"])

    def test_task_packet_preview_explicit_non_canonical_boundary(self):
        """Explicit non-canonical boundary flag is reflected in controller packet."""
        response = self.client.post(
            "/api/conversation-runtime/flywheel/task-packet/preview",
            json={
                "topic": "Non-canonical test",
                "task_intent": "explicit boundary test",
                "selected_knowledge_labels": ["claim:test"],
                "selected_evolution_labels": ["study:boundary-test"],
                "selected_source_labels": ["test-source"],
                "explicit_non_canonical": True,
                "reviewer_note": "Explicitly marking as non-canonical",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["packet_intent"], "mixed")
        self.assertEqual(data["suggested_lane"], "mixed_review")
        self.assertEqual(len(data["selected_label_groups"]), 3)

        self.assertEqual(data["promotion_state"], "inspect_only")
        self.assertEqual(data["controller_packet"]["truth_status"], "explicit_non_canonical")
        self.assertIn("explicit_non_canonical_boundary", data["controller_packet"]["reason_tags"])
        self.assertIn("explicit_non_canonical=True", data["notes"])

    def test_task_packet_preview_knowledge_only(self):
        """Task-packet with only knowledge labels -> knowledge_driven intent."""
        response = self.client.post(
            "/api/conversation-runtime/flywheel/task-packet/preview",
            json={
                "topic": "Knowledge focus",
                "task_intent": "knowledge review only",
                "selected_knowledge_labels": ["claim:data-quality", "concept:source-trust"],
                "selected_evolution_labels": [],
                "selected_source_labels": [],
                "reviewer_note": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["packet_intent"], "knowledge_driven")
        self.assertEqual(data["suggested_lane"], "knowledge_review")
        self.assertEqual(data["suggested_next_step"], "review_knowledge_candidates")
        self.assertEqual(len(data["selected_label_groups"]), 1)

        knowledge_group = data["selected_label_groups"][0]
        self.assertEqual(knowledge_group["label_type"], "knowledge")
        self.assertEqual(knowledge_group["count"], 2)

    def test_task_packet_preview_evolution_only(self):
        """Task-packet with only evolution labels -> evolution_driven intent."""
        response = self.client.post(
            "/api/conversation-runtime/flywheel/task-packet/preview",
            json={
                "topic": "Evolution focus",
                "task_intent": "evolution review only",
                "selected_knowledge_labels": [],
                "selected_evolution_labels": ["prototype:new-feature", "review:existing-code"],
                "selected_source_labels": [],
                "reviewer_note": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["packet_intent"], "evolution_driven")
        self.assertEqual(data["suggested_lane"], "evolution_review")
        self.assertEqual(data["suggested_next_step"], "review_evolution_candidates")
        self.assertEqual(len(data["selected_label_groups"]), 1)

        evolution_group = data["selected_label_groups"][0]
        self.assertEqual(evolution_group["label_type"], "evolution")
        self.assertEqual(evolution_group["count"], 2)

    def test_task_packet_preview_label_normalization(self):
        """Labels are normalized (whitespace stripped, empty filtered)."""
        response = self.client.post(
            "/api/conversation-runtime/flywheel/task-packet/preview",
            json={
                "topic": "Normalization test",
                "task_intent": "test whitespace handling",
                "selected_knowledge_labels": ["  claim:spaced  ", "", "concept:clean"],
                "selected_evolution_labels": ["  study:whitespace-test  "],
                "selected_source_labels": ["  source:with-spaces  ", "   "],
                "reviewer_note": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["packet_intent"], "mixed")
        self.assertEqual(len(data["selected_label_groups"]), 3)

        knowledge_group = next(
            (g for g in data["selected_label_groups"] if g["label_type"] == "knowledge"), None
        )
        self.assertIsNotNone(knowledge_group)
        self.assertEqual(knowledge_group["count"], 2)
        self.assertIn("claim:spaced", knowledge_group["labels"])
        self.assertIn("concept:clean", knowledge_group["labels"])

        evolution_group = next(
            (g for g in data["selected_label_groups"] if g["label_type"] == "evolution"), None
        )
        self.assertIsNotNone(evolution_group)
        self.assertEqual(evolution_group["count"], 1)
        self.assertIn("study:whitespace-test", evolution_group["labels"])

        source_group = next(
            (g for g in data["selected_label_groups"] if g["label_type"] == "source"), None
        )
        self.assertIsNotNone(source_group)
        self.assertEqual(source_group["count"], 1)
        self.assertIn("source:with-spaces", source_group["labels"])

    def test_task_packet_preview_whitespace_only_labels_fall_back_to_no_action(self):
        """Whitespace-only labels are discarded before intent derivation."""
        response = self.client.post(
            "/api/conversation-runtime/flywheel/task-packet/preview",
            json={
                "topic": "Whitespace only",
                "task_intent": "test empty normalized labels",
                "selected_knowledge_labels": ["   ", ""],
                "selected_evolution_labels": ["  "],
                "selected_source_labels": ["    "],
                "reviewer_note": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["packet_intent"], "no_action")
        self.assertEqual(data["suggested_lane"], "no_action")
        self.assertEqual(data["selected_label_groups"], [])
        self.assertIn("no_action", data["controller_packet"]["reason_tags"])

    def test_execution_feedback_inspect_extracts_reflection_candidates(self):
        """Worker execution feedback yields bounded knowledge and evolution reflection."""

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "intent": "execution_feedback",
                  "summary": "test failures show a boundary gap and a follow-up review need",
                  "knowledge_delta_candidates": [
                    {
                      "delta_type": "boundary",
                      "label": "preview route still inspect-only",
                      "content": "The worker result confirms the preview route should remain non-canonical and inspect-only"
                    }
                  ],
                  "evolution_trigger_candidates": [
                    {
                      "trigger_type": "review",
                      "label": "Review worker packet bridge debt",
                      "rationale": "The execution result suggests follow-up review on panel size and packet shaping"
                    }
                  ]
                }
                """

        with patch(
            "conversation_runtime.flywheel.LLMAdapter",
            return_value=_DummyAdapter(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/flywheel/execution-feedback/inspect",
                json={
                    "topic": "flywheel delegation",
                    "task_intent": "reflect worker result",
                    "worker_lane": "review",
                    "task_packet_summary": "Review the flywheel worker packet bridge",
                    "execution_feedback_text": "Review says the slice is acceptable but panel debt should be tracked.",
                    "execution_status_hint": "accept_with_changes",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["feedback_intent"], "execution_feedback")
        self.assertEqual(data["worker_lane"], "review")
        self.assertEqual(data["execution_status_hint"], "accept_with_changes")
        self.assertEqual(len(data["knowledge_delta_candidates"]), 1)
        self.assertEqual(len(data["evolution_trigger_candidates"]), 1)
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "review_execution_feedback")
        self.assertEqual(data["controller_packet"]["advisory_scope"], "execution_feedback_inspect_only")
        self.assertEqual(data["controller_packet"]["truth_status"], "non_canonical")
        truth_text = " ".join(data["truth_boundary"]).lower()
        self.assertIn("execution feedback inspect is candidate reflection only", truth_text)
        self.assertEqual(data["promotion_state"], "inspect_only")

    def test_execution_feedback_inspect_no_action_fallback(self):
        """Non-actionable worker feedback falls back to no_action."""

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "intent": "other",
                  "summary": "nothing actionable",
                  "knowledge_delta_candidates": [],
                  "evolution_trigger_candidates": []
                }
                """

        with patch(
            "conversation_runtime.flywheel.LLMAdapter",
            return_value=_DummyAdapter(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/flywheel/execution-feedback/inspect",
                json={
                    "topic": "flywheel delegation",
                    "task_intent": "reflect worker result",
                    "worker_lane": "test",
                    "task_packet_summary": "Run bounded validation",
                    "execution_feedback_text": "Build passed and there is nothing more to add.",
                    "execution_status_hint": "accept",
                    "provider": "qwen",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["feedback_intent"], "other")
        self.assertEqual(data["knowledge_delta_candidates"], [])
        self.assertEqual(data["evolution_trigger_candidates"], [])
        self.assertEqual(data["operational_advice"]["suggested_next_step"], "no_action")
        self.assertIn("no_action", data["controller_packet"]["reason_tags"])
        self.assertEqual(data["promotion_state"], "inspect_only")

    def test_execution_feedback_inspect_with_provenance_echoed_unverified(self):
        """Caller-provided provenance is echoed and marked as unverified/caller-provided."""

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                # Check that prompt includes provenance context
                prompt = args[1] if len(args) > 1 else kwargs.get("message", "")
                assert "worker_run_id: run-abc123" in prompt
                assert "worker_provider: claude-worker" in prompt
                assert "worker_model: claude-opus-4.6" in prompt
                assert "worker_artifact_ref: artifact-ref-xyz" in prompt
                return """
                {
                  "intent": "execution_feedback",
                  "summary": "worker result with provenance context",
                  "knowledge_delta_candidates": [
                    {
                      "delta_type": "claim",
                      "label": "provenance is inspect-only",
                      "content": "The provenance fields are caller-provided and not verified"
                    }
                  ],
                  "evolution_trigger_candidates": []
                }
                """

        with patch(
            "conversation_runtime.flywheel.LLMAdapter",
            return_value=_DummyAdapter(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/flywheel/execution-feedback/inspect",
                json={
                    "topic": "provenance test",
                    "task_intent": "verify provenance handling",
                    "worker_lane": "review",
                    "task_packet_summary": "Review with provenance",
                    "execution_feedback_text": "Worker completed with provenance tracking.",
                    "execution_status_hint": "accept",
                    "provider": "qwen",
                    "worker_run_id": "run-abc123",
                    "worker_provider": "claude-worker",
                    "worker_model": "claude-opus-4.6",
                    "worker_artifact_ref": "artifact-ref-xyz",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["feedback_intent"], "execution_feedback")
        self.assertEqual(len(data["knowledge_delta_candidates"]), 1)

        # Verify provenance is echoed correctly
        self.assertEqual(data["provenance"]["worker_run_id"], "run-abc123")
        self.assertEqual(data["provenance"]["worker_provider"], "claude-worker")
        self.assertEqual(data["provenance"]["worker_model"], "claude-opus-4.6")
        self.assertEqual(data["provenance"]["worker_artifact_ref"], "artifact-ref-xyz")
        self.assertEqual(data["provenance"]["provenance_source"], "caller_provided")
        self.assertEqual(data["provenance"]["verified"], False)

        # Verify notes indicate unverified provenance
        self.assertIn("provenance_source=caller_provided", data["notes"])
        self.assertIn("provenance_verified=false", data["notes"])

        # Verify truth boundary includes provenance disclaimer
        truth_text = " ".join(data["truth_boundary"]).lower()
        self.assertIn("caller-provided", truth_text)
        self.assertIn("not verified by this endpoint", truth_text)

        self.assertEqual(data["promotion_state"], "inspect_only")

    def test_execution_feedback_inspect_missing_provenance_valid(self):
        """Missing provenance fields remain valid and do not block inspect."""

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                # Verify prompt does NOT include provenance section when all fields are empty
                prompt = args[1] if len(args) > 1 else kwargs.get("message", "")
                assert "Worker Provenance Context" not in prompt
                return """
                {
                  "intent": "execution_feedback",
                  "summary": "feedback without provenance",
                  "knowledge_delta_candidates": [],
                  "evolution_trigger_candidates": []
                }
                """

        with patch(
            "conversation_runtime.flywheel.LLMAdapter",
            return_value=_DummyAdapter(),
        ):
            response = self.client.post(
                "/api/conversation-runtime/flywheel/execution-feedback/inspect",
                json={
                    "topic": "no provenance test",
                    "task_intent": "verify missing provenance",
                    "worker_lane": "coding",
                    "task_packet_summary": "Basic feedback",
                    "execution_feedback_text": "Worker completed without provenance.",
                    "execution_status_hint": "neutral",
                    "provider": "qwen",
                    # No provenance fields provided (all default to empty)
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["feedback_intent"], "execution_feedback")

        # Verify provenance defaults to empty values
        self.assertEqual(data["provenance"]["worker_run_id"], "")
        self.assertEqual(data["provenance"]["worker_provider"], "")
        self.assertEqual(data["provenance"]["worker_model"], "")
        self.assertEqual(data["provenance"]["worker_artifact_ref"], "")
        self.assertEqual(data["provenance"]["provenance_source"], "caller_provided")
        self.assertEqual(data["provenance"]["verified"], False)

        # Notes still indicate provenance source
        self.assertIn("provenance_source=caller_provided", data["notes"])
        self.assertIn("provenance_verified=false", data["notes"])

        self.assertEqual(data["promotion_state"], "inspect_only")


if __name__ == "__main__":
    unittest.main()
