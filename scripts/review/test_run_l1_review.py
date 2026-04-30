from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("run_l1_review.py")
SPEC = importlib.util.spec_from_file_location("run_l1_review", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
RUN_L1_REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUN_L1_REVIEW)


class RunL1ReviewStatusTests(unittest.TestCase):
    def test_classifies_wrapper_launch_as_launched_when_result_is_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result_path = Path(temp_dir) / "result.md"
            result_path.write_text("# review\n\nstatus: pending\n", encoding="utf-8", newline="\n")

            status = RUN_L1_REVIEW.classify_delegate_status(0, result_path)

            self.assertEqual(status, "delegate_launched")

    def test_classifies_complete_result_as_completed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result_path = Path(temp_dir) / "result.md"
            result_path.write_text(
                "\n".join(
                    [
                        "# Task",
                        "",
                        "## Task ID",
                        "",
                        "## Summary",
                        "Done",
                        "",
                        "## Files Changed",
                        "- `scripts/review/run_l1_review.py`",
                        "",
                        "## Commit Hash",
                        "abc123",
                        "",
                        "## Validation Run",
                        "pytest scripts/review/test_run_l1_review.py",
                        "",
                        "## Known Risks",
                        "None",
                        "",
                        "## Recommendation",
                        "accept",
                        "",
                    ]
                ),
                encoding="utf-8",
                newline="\n",
            )

            status = RUN_L1_REVIEW.classify_delegate_status(0, result_path)

            self.assertEqual(status, "delegate_completed")

    def test_classifies_nonzero_exit_as_failed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result_path = Path(temp_dir) / "result.md"

            status = RUN_L1_REVIEW.classify_delegate_status(1, result_path)

            self.assertEqual(status, "delegate_failed")


if __name__ == "__main__":
    unittest.main()
