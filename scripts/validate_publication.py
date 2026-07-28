#!/usr/bin/env python3
"""Validate the Digitalis Community publication manifest."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "publication" / "manifest.json"
ALLOWED_OWNERSHIP = {
    "publication-owned",
    "generated-publication",
    "external-artifact",
}
REQUIRED_ARTIFACT_FIELDS = {
    "path",
    "version",
    "ownership",
    "generation_method",
    "source_reference",
}
PRIVATE_IDENTIFIER_PATTERNS = (
    re.compile(r"hackelia-micrantha/digitalis(?:\b|/)", re.IGNORECASE),
    re.compile(r"github\.com/hackelia-micrantha/digitalis(?:\b|/)", re.IGNORECASE),
)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_manifest(errors: list[str]) -> dict[str, object] | None:
    if not MANIFEST.is_file():
        fail(errors, "missing publication/manifest.json")
        return None
    try:
        value = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"invalid publication manifest: {exc}")
        return None
    if not isinstance(value, dict):
        fail(errors, "publication manifest must be a JSON object")
        return None
    return value


def validate_top_level(manifest: dict[str, object], errors: list[str]) -> None:
    if manifest.get("schema_version") != 1:
        fail(errors, "schema_version must be 1")
    publication_id = manifest.get("publication_id")
    if not isinstance(publication_id, str) or not publication_id.strip():
        fail(errors, "publication_id must be a non-empty string")
    reviewed_at = manifest.get("reviewed_at")
    if not isinstance(reviewed_at, str):
        fail(errors, "reviewed_at must be an ISO date")
    else:
        try:
            parsed = date.fromisoformat(reviewed_at)
            if parsed > date.today():
                fail(errors, "reviewed_at cannot be in the future")
        except ValueError:
            fail(errors, "reviewed_at must be an ISO date")
    if manifest.get("direction") != "one-way-inbound":
        fail(errors, "direction must be one-way-inbound")

    destination = manifest.get("destination")
    if not isinstance(destination, dict):
        fail(errors, "destination must be an object")
    else:
        if destination.get("repository") != "hackelia-micrantha/digitalis-community":
            fail(errors, "destination.repository must identify digitalis-community")
        if destination.get("role") != "authoritative-publication-boundary":
            fail(errors, "destination.role must be authoritative-publication-boundary")

    source = manifest.get("source")
    if not isinstance(source, dict):
        fail(errors, "source must be an object")
    else:
        for field in ("visibility", "repository_identifier", "reference", "reference_type"):
            if not isinstance(source.get(field), str) or not str(source[field]).strip():
                fail(errors, f"source.{field} must be a non-empty string")

    policy = manifest.get("policy")
    if not isinstance(policy, dict):
        fail(errors, "policy must be an object")
    else:
        expected = {
            "public_files_authoritative_after_import": True,
            "reverse_sync_allowed": False,
            "implicit_mirroring_allowed": False,
            "private_identifiers_allowed": False,
        }
        for key, value in expected.items():
            if policy.get(key) is not value:
                fail(errors, f"policy.{key} must be {str(value).lower()}")


def validate_artifacts(manifest: dict[str, object], errors: list[str]) -> None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        fail(errors, "artifacts must be a non-empty array")
        return

    seen: set[str] = set()
    for index, artifact in enumerate(artifacts):
        prefix = f"artifacts[{index}]"
        if not isinstance(artifact, dict):
            fail(errors, f"{prefix} must be an object")
            continue
        missing = REQUIRED_ARTIFACT_FIELDS - artifact.keys()
        if missing:
            fail(errors, f"{prefix} missing fields: {', '.join(sorted(missing))}")
            continue
        for field in REQUIRED_ARTIFACT_FIELDS:
            if not isinstance(artifact.get(field), str) or not str(artifact[field]).strip():
                fail(errors, f"{prefix}.{field} must be a non-empty string")

        path_value = artifact.get("path")
        if not isinstance(path_value, str) or not path_value:
            continue
        if path_value in seen:
            fail(errors, f"duplicate artifact path: {path_value}")
            continue
        seen.add(path_value)

        target = (ROOT / path_value).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            fail(errors, f"artifact path escapes repository: {path_value}")
            continue
        if not target.is_file():
            fail(errors, f"artifact path does not exist: {path_value}")

        ownership = artifact.get("ownership")
        if ownership not in ALLOWED_OWNERSHIP:
            fail(errors, f"{prefix}.ownership is not recognized: {ownership}")


def validate_publication_safety(errors: list[str]) -> None:
    text = MANIFEST.read_text(encoding="utf-8") if MANIFEST.is_file() else ""
    for pattern in PRIVATE_IDENTIFIER_PATTERNS:
        if pattern.search(text):
            fail(errors, "publication manifest exposes a prohibited private repository identifier")


def main() -> int:
    errors: list[str] = []
    manifest = load_manifest(errors)
    if manifest is not None:
        validate_top_level(manifest, errors)
        validate_artifacts(manifest, errors)
        validate_publication_safety(errors)

    if errors:
        print("Digitalis publication validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Digitalis publication validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
