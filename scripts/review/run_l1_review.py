from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable


ROLE = "code-review-agent"
LEVELS = ("L1", "L2", "L3")
EXECUTE_MODES = ("none", "qoder", "openclaw")


def emit_text(text: str = "") -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((text + "\n").encode("utf-8"))


def safe_task_id(value: str) -> str:
    value = value.strip()
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    return safe.strip("._-") or "review_task"


def resolve_under_cwd(cwd: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = cwd / path
    return path.resolve()


def format_command(parts: Iterable[str]) -> str:
    return " ".join(f'"{part}"' if " " in part else part for part in parts)


def format_process_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def build_qoder_command(
    cwd: Path,
    task_id: str,
    brief_path: Path,
    context_path: Path,
    result_path: Path,
    done_path: Path,
) -> list[str]:
    return [
        sys.executable,
        str((cwd / "scripts" / "qoder" / "qoder_delegate.py").resolve()),
        "--cwd",
        str(cwd),
        "--task-id",
        task_id,
        "--brief",
        str(brief_path),
        "--context",
        str(context_path),
        "--result",
        str(result_path),
        "--done",
        str(done_path),
        "--lane",
        "review",
        "--reasoning-mode",
        "high",
        "--sandbox-identity",
        f"qoder_workspace:{task_id}",
        "--sandbox-kind",
        "qoder_workspace",
        "--capability-profile",
        "review_high_reasoning",
        "--network-policy",
        "disabled",
        "--role",
        ROLE,
        "--mode",
        "agent",
        "--reuse-window",
    ]


def build_openclaw_command(cwd: Path, task_id: str, brief_path: Path, delegate_timeout: int) -> list[str]:
    return [
        sys.executable,
        str((cwd / "scripts" / "acpx" / "openclaw_delegate.py").resolve()),
        "--mode",
        "prompt",
        "--agent-alias",
        "openclaw-reviewer",
        "--cwd",
        str(cwd),
        "--session",
        f"{safe_task_id(task_id).lower()}-review",
        "--file",
        str(brief_path),
        "--timeout",
        str(delegate_timeout),
        "--lane",
        "review",
        "--reasoning-mode",
        "high",
        "--sandbox-kind",
        "openclaw_workspace",
        "--capability-profile",
        "review_high_reasoning",
        "--network-policy",
        "disabled",
    ]


def build_brief(
    *,
    task_id: str,
    title: str,
    level: str,
    cwd: Path,
    target_brief: Path,
    target_result: Path,
    target_files: list[Path],
    validations: list[str],
) -> str:
    level_rules = {
        "L1": [
            "- This is delegated daily review.",
            "- Do not create a zip.",
            "- Do not create an external manual review packet.",
            "- Return findings, validation gaps, and a controller-facing recommendation.",
        ],
        "L2": [
            "- This is PR / Codex review preparation.",
            "- Do not create an external zip.",
            "- Use the GitHub PR as the review package when the branch is ready.",
            "- Resolve or explicitly accept Codex PR review findings before promotion.",
        ],
        "L3": [
            "- This is manual cross-model review preparation.",
            "- L3 must remain explicit and rare.",
            "- If a zip is later prepared, keep the external package to no more than 10 entries.",
            "- Do not treat this runner output as full L3 packaging.",
        ],
    }
    lines = [
        "# Review Brief",
        "",
        f"task_id: {task_id}",
        f"title: {title}",
        f"level: {level}",
        "lane: review",
        f"role: {ROLE}",
        "reasoning_mode: high",
        "network_policy: disabled",
        "",
        "## Goal",
        "- Review the bounded implementation against its packet, result evidence, and declared validation.",
        "",
        "## Review Level Rules",
        *level_rules[level],
        "",
        "## Required Inputs",
        f"- Project contract: {(cwd / 'AGENTS.md').resolve()}",
        f"- Review policy: {(cwd / 'docs' / 'IKE_REVIEW_CADENCE_AND_AUTOMATION_POLICY_2026-04-29.md').resolve()}",
        f"- Target brief: {target_brief}",
        f"- Target result: {target_result}",
        *[f"- Target file: {path}" for path in target_files],
        "",
        "## Reviewer Instructions",
        "- Check scope discipline first.",
        "- Check correctness against the target brief.",
        "- Check whether validation evidence is sufficient.",
        "- Do not edit project files.",
        "- Do not broaden into architecture redesign.",
        "- Do not make the final controller promotion decision.",
        "",
        "## Validation To Consider",
        *([f"- {item}" for item in validations] or ["- No validation command was declared. Treat this as a validation gap unless justified."]),
        "",
        "## Expected Output",
        "- summary",
        "- findings",
        "- validation_gaps",
        "- known_risks",
        "- recommendation: accept | accept_with_changes | reject",
        "",
    ]
    return "\n".join(lines)


def build_context(
    *,
    task_id: str,
    title: str,
    level: str,
    target_brief: Path,
    target_result: Path,
    target_files: list[Path],
    validations: list[str],
) -> str:
    def status(path: Path) -> str:
        return "exists" if path.exists() else "missing"

    lines = [
        f"# Review Context: {task_id}",
        "",
        "## Metadata",
        f"- title: {title}",
        f"- level: {level}",
        "- artifact_root: .runtime/reviews",
        "",
        "## Targets",
        f"- target_brief: {target_brief} ({status(target_brief)})",
        f"- target_result: {target_result} ({status(target_result)})",
        *[f"- target_file: {path} ({status(path)})" for path in target_files],
        "",
        "## Declared Validation",
        *([f"- {item}" for item in validations] or ["- Not declared."]),
        "",
        "## Artifact Contract",
        "- briefs/<task-id>.md is the canonical local review request.",
        "- contexts/<task-id>.md is the canonical context packet.",
        "- results/<task-id>.md is where reviewer output should be pasted or written.",
        "- done/<task-id>.json tracks the review artifact identity and level.",
        "",
    ]
    return "\n".join(lines)


def build_result_template(task_id: str, level: str) -> str:
    return "\n".join(
        [
            f"# {task_id}",
            "",
            f"level: {level}",
            "status: pending",
            "",
            "## Summary",
            "",
            "## Findings",
            "",
            "## Validation Gaps",
            "",
            "## Known Risks",
            "",
            "## Recommendation",
            "",
        ]
    )


def write_done_metadata(
    *,
    done_path: Path,
    task_id: str,
    requested_task_id: str,
    title: str,
    level: str,
    status: str,
    brief_path: Path,
    context_path: Path,
    result_path: Path,
    execute: str,
    delegate_attempted: bool,
    delegate_command: list[str] | None,
    delegate_exit_code: int | None,
) -> None:
    done_path.write_text(
        json.dumps(
            {
                "task_id": task_id,
                "requested_task_id": requested_task_id,
                "title": title,
                "level": level,
                "status": status,
                "execute": execute,
                "delegate_attempted": delegate_attempted,
                "delegate_command": delegate_command,
                "delegate_exit_code": delegate_exit_code,
                "brief": str(brief_path),
                "context": str(context_path),
                "result": str(result_path),
                "zip_created": False,
                "external_packet_created": False,
                "created_at": "",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def run_delegate(command: list[str], cwd: Path, timeout_seconds: int) -> int:
    emit_text("delegate_status: running")
    emit_text(f"delegate_timeout_seconds: {timeout_seconds}")
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        emit_text("delegate_status: timeout")
        emit_text(f"delegate_exit_code: {exit_code}")
        if exc.stdout:
            emit_text("delegate_stdout:")
            emit_text(format_process_output(exc.stdout).rstrip())
        emit_text("delegate_stderr:")
        stderr = format_process_output(exc.stderr).rstrip()
        if stderr:
            emit_text(stderr)
        emit_text(f"delegate wrapper timed out after {timeout_seconds} seconds; reviewer judgement was not parsed and promotion is blocked.")
        return exit_code
    emit_text(f"delegate_exit_code: {result.returncode}")
    if result.stdout:
        emit_text("delegate_stdout:")
        emit_text(result.stdout.rstrip())
    if result.stderr:
        emit_text("delegate_stderr:")
        emit_text(result.stderr.rstrip())
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare deterministic project review artifacts for L1 daily review, with explicit L2/L3 guidance."
    )
    parser.add_argument("--cwd", default=".", help="Workspace directory.")
    parser.add_argument("--level", choices=LEVELS, default="L1", help="Review level. Defaults to L1.")
    parser.add_argument("--task-id", required=True, help="Stable review task identifier.")
    parser.add_argument("--title", required=True, help="Short review title.")
    parser.add_argument("--target-brief", required=True, help="Implementation brief or policy file to review against.")
    parser.add_argument("--target-result", required=True, help="Implementation result file to review.")
    parser.add_argument("--target-file", action="append", default=[], help="Changed file to include in scope. Repeat as needed.")
    parser.add_argument("--target-files", nargs="*", default=[], help="Additional changed files to include in scope.")
    parser.add_argument("--validation", action="append", default=[], help="Validation command or evidence. Repeat as needed.")
    parser.add_argument(
        "--execute",
        choices=EXECUTE_MODES,
        default="none",
        help="Delegate execution mode. Defaults to prepare-only: none.",
    )
    parser.add_argument(
        "--delegate-timeout",
        type=int,
        default=1800,
        help="Seconds to wait for the delegate wrapper before failing. Defaults to 1800.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned artifacts and commands without writing files.")
    args = parser.parse_args()
    if args.delegate_timeout < 1:
        parser.error("--delegate-timeout must be at least 1 second.")

    cwd = Path(args.cwd).resolve()
    task_id = safe_task_id(args.task_id)
    target_brief = resolve_under_cwd(cwd, args.target_brief)
    target_result = resolve_under_cwd(cwd, args.target_result)
    target_files = [resolve_under_cwd(cwd, item) for item in [*args.target_file, *args.target_files]]
    validations = args.validation

    base = cwd / ".runtime" / "reviews"
    brief_path = base / "briefs" / f"{task_id}.md"
    context_path = base / "contexts" / f"{task_id}.md"
    result_path = base / "results" / f"{task_id}.md"
    done_path = base / "done" / f"{task_id}.json"

    qoder_command = build_qoder_command(cwd, task_id, brief_path, context_path, result_path, done_path)
    openclaw_command = build_openclaw_command(cwd, task_id, brief_path, args.delegate_timeout)
    selected_delegate_command = {
        "none": None,
        "qoder": qoder_command,
        "openclaw": openclaw_command,
    }[args.execute]

    emit_text(f"review_level: {args.level}")
    emit_text(f"dry_run: {str(args.dry_run).lower()}")
    emit_text(f"execute: {args.execute}")
    emit_text(f"delegate_timeout_seconds: {args.delegate_timeout}")
    emit_text("")
    emit_text("planned_artifacts:")
    for path in (brief_path, context_path, result_path, done_path):
        emit_text(f"- {path}")
    emit_text("")

    if args.level == "L1":
        emit_text("level_guidance: L1 creates no zip and no external manual packet.")
    elif args.level == "L2":
        emit_text("level_guidance: L2 uses GitHub PR / Codex review; no external zip is created.")
    else:
        emit_text("level_guidance: L3 was explicitly requested. Remember the external zip rule: no more than 10 entries.")
    emit_text("")

    emit_text("next_commands:")
    emit_text(f"- qoder: {format_command(qoder_command)}")
    emit_text(f"- openclaw: {format_command(openclaw_command)}")
    emit_text(f"- manual: paste reviewer output into {result_path}")
    if args.level == "L2":
        emit_text("- github/codex: push a scoped branch, open a draft PR, then use Codex PR review on GitHub.")
    if args.level == "L3":
        emit_text("- l3_manual: prepare a separate user-approved external packet only if still needed; keep zip entries <= 10.")
    emit_text("")
    if args.execute == "none":
        emit_text("execution_plan: prepare artifacts only; no delegate will run.")
    elif args.dry_run:
        emit_text(f"execution_plan: would execute {args.execute} after writing artifacts; dry-run prevents writes and delegate execution.")
        emit_text(f"selected_delegate_command: {format_command(selected_delegate_command or [])}")
    else:
        emit_text(f"execution_plan: write artifacts, then execute {args.execute}.")
        emit_text(f"selected_delegate_command: {format_command(selected_delegate_command or [])}")

    if args.dry_run:
        return 0

    for directory in (brief_path.parent, context_path.parent, result_path.parent, done_path.parent):
        directory.mkdir(parents=True, exist_ok=True)

    brief_path.write_text(
        build_brief(
            task_id=task_id,
            title=args.title,
            level=args.level,
            cwd=cwd,
            target_brief=target_brief,
            target_result=target_result,
            target_files=target_files,
            validations=validations,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    context_path.write_text(
        build_context(
            task_id=task_id,
            title=args.title,
            level=args.level,
            target_brief=target_brief,
            target_result=target_result,
            target_files=target_files,
            validations=validations,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not result_path.exists():
        result_path.write_text(build_result_template(task_id, args.level) + "\n", encoding="utf-8", newline="\n")
    write_done_metadata(
        done_path=done_path,
        task_id=task_id,
        requested_task_id=args.task_id,
        title=args.title,
        level=args.level,
        status="prepared",
        brief_path=brief_path,
        context_path=context_path,
        result_path=result_path,
        execute=args.execute,
        delegate_attempted=False,
        delegate_command=selected_delegate_command,
        delegate_exit_code=None,
    )

    if selected_delegate_command is None:
        emit_text("")
        emit_text("execution_status: prepared_only")
        return 0

    emit_text("")
    emit_text(f"execution_status: delegating_to_{args.execute}")
    delegate_exit_code = run_delegate(selected_delegate_command, cwd, args.delegate_timeout)
    write_done_metadata(
        done_path=done_path,
        task_id=task_id,
        requested_task_id=args.task_id,
        title=args.title,
        level=args.level,
        status="delegate_completed" if delegate_exit_code == 0 else "delegate_failed",
        brief_path=brief_path,
        context_path=context_path,
        result_path=result_path,
        execute=args.execute,
        delegate_attempted=True,
        delegate_command=selected_delegate_command,
        delegate_exit_code=delegate_exit_code,
    )
    if delegate_exit_code != 0:
        emit_text("execution_status: delegate_failed")
        return delegate_exit_code
    emit_text("execution_status: delegate_completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
