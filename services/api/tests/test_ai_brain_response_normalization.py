import sys
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from feeds.ai_brain import AIDecisionBrain, DecisionContext, DecisionType


class _ObjectResponse:
    def __init__(self, content: str):
        self.content = content


class _StringLLM:
    async def chat(self, messages):
        return '{"action":"continue","reasoning":"ok","confidence":0.8}'


class _ObjectLLM:
    async def chat(self, messages):
        return _ObjectResponse('{"action":"continue","reasoning":"ok","confidence":0.9}')


class AIBrainResponseNormalizationTest(unittest.IsolatedAsyncioTestCase):
    async def test_local_llm_accepts_plain_string_response(self):
        brain = AIDecisionBrain(llm_client=_StringLLM(), use_external_agent=False)
        decision = await brain.decide(
            DecisionContext(
                decision_type=DecisionType.ANALYZE,
                source_name="test",
                goal="verify decision parsing",
            )
        )
        self.assertEqual(decision.action, "continue")
        self.assertGreater(decision.confidence, 0.0)

    async def test_local_llm_accepts_content_object_response(self):
        brain = AIDecisionBrain(llm_client=_ObjectLLM(), use_external_agent=False)
        decision = await brain.decide(
            DecisionContext(
                decision_type=DecisionType.ANALYZE,
                source_name="test",
                goal="verify decision parsing",
            )
        )
        self.assertEqual(decision.action, "continue")
        self.assertGreater(decision.confidence, 0.0)


if __name__ == "__main__":
    unittest.main()
