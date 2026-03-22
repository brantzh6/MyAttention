import sys
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from db.models import Conversation, Message


class ModelColumnMappingsTest(unittest.TestCase):
    def test_conversation_extra_maps_to_metadata_column(self) -> None:
        self.assertEqual(Conversation.extra.property.columns[0].name, "metadata")

    def test_message_extra_maps_to_metadata_column(self) -> None:
        self.assertEqual(Message.extra.property.columns[0].name, "metadata")


if __name__ == "__main__":
    unittest.main()
