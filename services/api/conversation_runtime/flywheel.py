"""Compatibility facade for flywheel routes.

This module re-exports route functions from decomposed modules
to preserve backward compatibility for router imports.

Route functions:
- run_flywheel_inspect -> flywheel_inspect.py
- run_task_packet_preview -> task_packet_preview.py
- run_execution_feedback_inspect -> execution_feedback.py
"""

# Import LLMAdapter for test mock path compatibility
# Tests patch "conversation_runtime.flywheel.LLMAdapter"
from llm.adapter import LLMAdapter

# Re-export route functions from decomposed modules
from conversation_runtime.flywheel_inspect import (
    run_flywheel_inspect,
    flywheel_truth_boundary,
)

from conversation_runtime.task_packet_preview import (
    run_task_packet_preview,
)

from conversation_runtime.execution_feedback import (
    run_execution_feedback_inspect,
)


__all__ = [
    "run_flywheel_inspect",
    "run_task_packet_preview",
    "run_execution_feedback_inspect",
    "flywheel_truth_boundary",
    "LLMAdapter",
]
