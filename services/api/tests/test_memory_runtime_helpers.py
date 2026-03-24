import asyncio
import unittest
from types import SimpleNamespace
from uuid import uuid4

from memory.runtime import record_task_memory


class _FakeDb:
    def __init__(self):
        self.items = []
        self.flushed = False

    def add(self, item):
        self.items.append(item)

    async def flush(self):
        self.flushed = True


class MemoryRuntimeHelperTests(unittest.TestCase):
    def test_record_task_memory_adds_memory(self):
        async def _run():
            db = _FakeDb()
            context = SimpleNamespace(id=uuid4())
            task = SimpleNamespace(id=uuid4())
            memory = await record_task_memory(
                db,
                context=context,
                task=task,
                memory_kind="checkpoint",
                title="Self-test checkpoint",
                summary="healthy",
                content='{"healthy": true}',
                payload={"problem_type": "system_evolution"},
            )
            self.assertTrue(db.flushed)
            self.assertEqual(len(db.items), 1)
            self.assertEqual(memory.memory_kind, "checkpoint")
            self.assertEqual(memory.title, "Self-test checkpoint")

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
