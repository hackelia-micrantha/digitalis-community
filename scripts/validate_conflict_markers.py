#!/usr/bin/env python3
"""Reject unresolved Git merge conflict markers in tracked files."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Git's default conflict marker size is seven characters, but marker size can
# be increased via attributes. The opening/closing/base markers are specific
# enough to avoid treating ordinary separators such as "=======" as errors.
CONFLICT_MARKER = re.compile(
    rb"^(?:<{7,}|>{7,}|\|{7,})(?: .*)?$",
    flags=re.MULTILINE,
)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [ROOT / Path(raw.decode("utf-8")) for raw in result.stdout.split(b"\0") if raw]


def find_conflict_markers(path: Path) -> list[int]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"cannot read {path.relative_to(ROOT)}: {exc}") from exc

    if b"\0" in data:
        return []

    lines: list[int] = []
    for match in CONFLICT_MARKER.finditer(data):
        lines.append(data.count(b"\n", 0, match.start()) + 1)
    return lines


def main() -> int:
    failures: list[str] = []

    try:
        files = tracked_files()
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError) as exc:
        print(f"Unable to enumerate tracked files: {exc}", file=sys.stderr)
        return 2

    for path in files:
        if not path.is_file():
            continue
        try:
            lines = find_conflict_markers(path)
        except RuntimeError as exc:
            failures.append(str(exc))
            continue
        for line in lines:
            failures.append(f"{path.relative_to(ROOT)}:{line}: unresolved merge conflict marker")

    if failures:
        print("Unresolved merge conflict validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Unresolved merge conflict validation passed ({len(files)} tracked files checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
