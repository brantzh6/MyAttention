"""Check structural controller gates for IKE operations state.

This is intentionally small. It does not replace controller judgment, but it
prevents a pending or unreviewed operations state from being treated as accepted
project truth by mistake.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "ops" / "state" / "current_state.json"


def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def load_state() -> dict:
    with STATE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_accepted_project_truth(state: dict) -> int:
    review_state = state.get("review_state", {})
    governance_state = state.get("governance_state", {})
    dirty_tree_state = state.get("dirty_tree_state", {})

    truth_status = state.get("truth_status")
    review_status = review_state.get("status")
    absorption_required = review_state.get("controller_absorption_required")
    open_findings = review_state.get("open_findings_to_absorb") or []

    if truth_status != "accepted_project_truth":
        return fail(
            "truth_status is not accepted_project_truth "
            f"(actual: {truth_status!r})"
        )

    if review_status not in {"accepted", "accepted_with_changes_absorbed"}:
        return fail(
            "review_state.status is not accepted or accepted_with_changes_absorbed "
            f"(actual: {review_status!r})"
        )

    if absorption_required:
        return fail("controller_absorption_required is still true")

    if open_findings:
        return fail(f"open review findings remain: {open_findings}")

    kernel_status = (
        governance_state.get("current_operations_kernel_package", {}).get("status")
    )
    if kernel_status not in {"accepted", "accepted_with_changes_absorbed"}:
        return fail(
            "current_operations_kernel_package.status is not accepted "
            f"(actual: {kernel_status!r})"
        )

    if dirty_tree_state.get("status") == "degraded" and dirty_tree_state.get(
        "new_feature_coding_allowed"
    ):
        return fail("dirty tree is degraded but new feature coding is allowed")

    print("PASS: accepted_project_truth controller gate")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--claim",
        required=True,
        choices=["accepted_project_truth", "reviewed_pending_absorption"],
    )
    args = parser.parse_args()

    state = load_state()

    if args.claim == "accepted_project_truth":
        return check_accepted_project_truth(state)

    review_state = state.get("review_state", {})
    if review_state.get("status") == "reviewed_accept_with_changes":
        print("PASS: reviewed_pending_absorption controller gate")
        return 0
    return fail(
        "review_state.status is not reviewed_accept_with_changes "
        f"(actual: {review_state.get('status')!r})"
    )


if __name__ == "__main__":
    sys.exit(main())
