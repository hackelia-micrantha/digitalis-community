#!/usr/bin/env python3
"""Require publication metadata updates when a pull request changes deployed assets."""

from __future__ import annotations

import os
import re
import subprocess
import sys

SAFE_REF = re.compile(r"^[A-Za-z0-9._/-]+$")


def main() -> int:
    base_ref = os.environ.get("GITHUB_BASE_REF", "").strip()
    if not base_ref:
        print("Publication change validation skipped outside pull requests")
        return 0
    if not SAFE_REF.fullmatch(base_ref) or base_ref.startswith(("/", "-")) or ".." in base_ref:
        print("Unsafe GITHUB_BASE_REF", file=sys.stderr)
        return 1

    base = f"origin/{base_ref}"
    try:
        completed = subprocess.run(
            ["git", "diff", "--name-only", f"{base}...HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print(exc.stderr or "Unable to inspect pull request changes", file=sys.stderr)
        return 1

    changed = {line.strip() for line in completed.stdout.splitlines() if line.strip()}
    deployed_changed = any(path.startswith("web/") for path in changed)
    manifest_changed = "publication/manifest.json" in changed

    if deployed_changed and not manifest_changed:
        print(
            "publication/manifest.json must change whenever deployed web/ assets change",
            file=sys.stderr,
        )
        return 1

    print("Publication change validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
