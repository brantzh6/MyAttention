from __future__ import annotations

import argparse
from pathlib import Path


def read_excerpt(path: Path, max_lines: int) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    excerpt = lines[:max_lines]
    numbered = [f"{idx + 1:04d}: {line}" for idx, line in enumerate(excerpt)]
    return "\n".join(numbered)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a UTF-8 delegation context packet from a bounded task brief and selected file excerpts."
    )
    parser.add_argument("--title", required=True, help="Short task title.")
    parser.add_argument("--goal", required=True, help="One-sentence task goal.")
    parser.add_argument("--instructions", required=True, help="Execution instructions for the delegated agent.")
    parser.add_argument("--output", required=True, help="Output file path.")
    parser.add_argument(
        "--file",
        action="append",
        default=[],
        help="File to include. Repeat for multiple files.",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=220,
        help="Max lines to include from each file.",
    )
    args = parser.parse_args()

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    parts: list[str] = []
    parts.append("Complete this task in one turn.")
    parts.append("Do not ask follow-up questions.")
    parts.append("Do not scan the workspace.")
    parts.append("Use only the supplied context packet.")
    parts.append("")
    parts.append(f"Title: {args.title}")
    parts.append(f"Goal: {args.goal}")
    parts.append("")
    parts.append("Execution Instructions:")
    parts.append(args.instructions)
    parts.append("")
    parts.append("Context Packet:")

    for file_arg in args.file:
        path = Path(file_arg).resolve()
        parts.append("")
        parts.append(f"FILE: {path}")
        parts.append("```text")
        parts.append(read_excerpt(path, args.max_lines))
        parts.append("```")

    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
