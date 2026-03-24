import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from brains.control_plane import build_execution_plan


class BrainExecutionPlanTest(unittest.IsolatedAsyncioTestCase):
    async def test_chat_voting_plan_combines_primary_and_supporting_models(self) -> None:
        primary = SimpleNamespace(brain_id="dialog-brain", default_models=["qwen3.5-plus"])
        review = SimpleNamespace(brain_id="chief-brain")
        fallback = SimpleNamespace(brain_id="brainstem-controller")
        route = SimpleNamespace(
            route_id="chat-general",
            problem_type="interactive_dialog",
            thinking_framework="dialog_orchestration",
            enabled=True,
            supporting_brains=["research-brain", "knowledge-brain"],
            review_brain=review,
            fallback_brain=fallback,
            primary_brain=primary,
            extra={"surface": "chat"},
        )
        profiles = [
            primary,
            SimpleNamespace(brain_id="research-brain", default_models=["deepseek-v3.2", "glm-5"]),
            SimpleNamespace(brain_id="knowledge-brain", default_models=["qwen3.5-plus", "MiniMax-M2.5"]),
        ]

        with patch("brains.control_plane.ensure_brain_control_plane", AsyncMock(return_value={})), \
            patch("brains.control_plane.list_brain_routes", AsyncMock(return_value=[route])), \
            patch("brains.control_plane.list_brain_profiles", AsyncMock(return_value=profiles)):
            plan = await build_execution_plan(
                AsyncMock(),
                problem_type="interactive_dialog",
                surface="chat",
                use_voting=True,
                enable_search=True,
                enable_thinking=True,
            )

        self.assertEqual(plan.route_id, "chat-general")
        self.assertEqual(plan.primary_brain, "dialog-brain")
        self.assertEqual(plan.supporting_brains, ["research-brain", "knowledge-brain"])
        self.assertEqual(
            plan.selected_models,
            ["qwen3.5-plus", "deepseek-v3.2", "glm-5", "MiniMax-M2.5"],
        )
        self.assertEqual(plan.execution_mode, "voting")

    async def test_requested_model_overrides_brain_defaults(self) -> None:
        primary = SimpleNamespace(brain_id="dialog-brain", default_models=["qwen3.5-plus"])
        route = SimpleNamespace(
            route_id="chat-general",
            problem_type="interactive_dialog",
            thinking_framework="dialog_orchestration",
            enabled=True,
            supporting_brains=[],
            review_brain=None,
            fallback_brain=None,
            primary_brain=primary,
            extra={"surface": "chat"},
        )

        with patch("brains.control_plane.ensure_brain_control_plane", AsyncMock(return_value={})), \
            patch("brains.control_plane.list_brain_routes", AsyncMock(return_value=[route])), \
            patch("brains.control_plane.list_brain_profiles", AsyncMock(return_value=[primary])):
            plan = await build_execution_plan(
                AsyncMock(),
                problem_type="interactive_dialog",
                surface="chat",
                requested_model="deepseek-v3.2",
            )

        self.assertEqual(plan.selected_models, ["deepseek-v3.2"])
        self.assertEqual(plan.execution_mode, "single")


if __name__ == "__main__":
    unittest.main()
