#!/usr/bin/env python3
"""Validate the Digitalis Community publication manifest."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "web"
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
    "sha256",
}
PRIVATE_IDENTIFIER_PATTERNS = (
    re.compile(r"hackelia-micrantha/digitalis(?!-community)(?:\b|/)", re.IGNORECASE),
    re.compile(
        r"github\.com/hackelia-micrantha/digitalis(?!-community)(?:\b|/)",
        re.IGNORECASE,
    ),
)
PUBLICATION_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,127}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


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


def parse_iso_date(value: object, field: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        fail(errors, f"{field} must be an ISO date")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        fail(errors, f"{field} must be an ISO date")
        return None


def validate_top_level(manifest: dict[str, object], errors: list[str]) -> date | None:
    if manifest.get("schema_version") != 1:
        fail(errors, "schema_version must be 1")

    publication_id = manifest.get("publication_id")
    if not isinstance(publication_id, str) or not PUBLICATION_ID_PATTERN.fullmatch(
        publication_id
    ):
        fail(errors, "publication_id must be a stable lowercase identifier")

    reviewed_at = parse_iso_date(manifest.get("reviewed_at"), "reviewed_at", errors)
    if reviewed_at is not None:
        if reviewed_at > date.today():
            fail(errors, "reviewed_at cannot be in the future")
        if isinstance(publication_id, str) and not publication_id.endswith(
            reviewed_at.isoformat()
        ):
            fail(errors, "publication_id must end with reviewed_at")

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
        if source.get("visibility") == "private":
            if source.get("repository_identifier") != "withheld":
                fail(errors, "private source.repository_identifier must be withheld")
            if source.get("reference_type") != "opaque-publication-id":
                fail(errors, "private source.reference_type must be opaque-publication-id")

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

    return reviewed_at


def normalize_artifact_path(path_value: str) -> str | None:
    pure = PurePosixPath(path_value)
    if pure.is_absolute() or ".." in pure.parts or path_value != pure.as_posix():
        return None
    return pure.as_posix()


def validate_artifacts(
    manifest: dict[str, object], reviewed_at: date | None, errors: list[str]
) -> set[str]:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        fail(errors, "artifacts must be a non-empty array")
        return set()

    seen: set[str] = set()
    for index, artifact in enumerate(artifacts):
        prefix = f"artifacts[{index}]"
        if not isinstance(artifact, dict):
            fail(errors, f"{prefix} must be an object")
            continue

        missing = REQUIRED_ARTIFACT_FIELDS - artifact.keys()
        if missing:
            fail(errors, f"{prefix} missing fields: {', '.join(sorted(missing))}")

        for field in REQUIRED_ARTIFACT_FIELDS - {"sha256"}:
            if not isinstance(artifact.get(field), str) or not str(artifact[field]).strip():
                fail(errors, f"{prefix}.{field} must be a non-empty string")

        path_value = artifact.get("path")
        if not isinstance(path_value, str) or not path_value:
            continue
        normalized = normalize_artifact_path(path_value)
        if normalized is None:
            fail(errors, f"{prefix}.path must be a normalized repository-relative path")
            continue
        if normalized in seen:
            fail(errors, f"duplicate artifact path: {normalized}")
            continue
        seen.add(normalized)

        target = (ROOT / normalized).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            fail(errors, f"artifact path escapes repository: {normalized}")
            continue
        if not target.is_file():
            fail(errors, f"artifact path does not exist: {normalized}")
            continue

        actual_sha256 = hashlib.sha256(target.read_bytes()).hexdigest()
        declared_sha256 = artifact.get("sha256")
        if not isinstance(declared_sha256, str) or not SHA256_PATTERN.fullmatch(
            declared_sha256
        ):
            fail(errors, f"{prefix}.sha256 must be {actual_sha256}")
        elif declared_sha256 != actual_sha256:
            fail(
                errors,
                f"{prefix}.sha256 mismatch for {normalized}: expected {actual_sha256}",
            )

        artifact_date = parse_iso_date(artifact.get("version"), f"{prefix}.version", errors)
        if artifact_date is not None and reviewed_at is not None and artifact_date > reviewed_at:
            fail(errors, f"{prefix}.version cannot be newer than reviewed_at")

        ownership = artifact.get("ownership")
        if ownership not in ALLOWED_OWNERSHIP:
            fail(errors, f"{prefix}.ownership is not recognized: {ownership}")

        if ownership == "publication-owned" and artifact.get(
            "generation_method"
        ) != "reviewed-public-maintenance":
            fail(
                errors,
                f"{prefix}.generation_method must be reviewed-public-maintenance "
                "for publication-owned artifacts",
            )

        artifact_text = target.read_bytes().decode("utf-8", errors="ignore")
        if any(pattern.search(artifact_text) for pattern in PRIVATE_IDENTIFIER_PATTERNS):
            fail(errors, f"governed artifact exposes a prohibited private repository identifier: {normalized}")

    return seen


def validate_site_coverage(artifact_paths: set[str], errors: list[str]) -> None:
    if not SITE.is_dir():
        return
    published_files = {
        path.relative_to(ROOT).as_posix()
        for path in SITE.rglob("*")
        if path.is_file()
    }
    missing = sorted(published_files - artifact_paths)
    extra = sorted(
        path
        for path in artifact_paths
        if path.startswith("web/") and path not in published_files
    )
    for path in missing:
        fail(errors, f"published file is missing from publication manifest: {path}")
    for path in extra:
        fail(errors, f"manifest references a missing published file: {path}")


def validate_manifest_safety(errors: list[str]) -> None:
    text = MANIFEST.read_text(encoding="utf-8") if MANIFEST.is_file() else ""
    if any(pattern.search(text) for pattern in PRIVATE_IDENTIFIER_PATTERNS):
        fail(errors, "publication manifest exposes a prohibited private repository identifier")


def main() -> int:
    errors: list[str] = []
    manifest = load_manifest(errors)
    if manifest is not None:
        reviewed_at = validate_top_level(manifest, errors)
        artifact_paths = validate_artifacts(manifest, reviewed_at, errors)
        validate_site_coverage(artifact_paths, errors)
        validate_manifest_safety(errors)

    if errors:
        print("Digitalis publication validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Digitalis publication validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
