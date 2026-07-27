#!/usr/bin/env python3
"""Validate the Digitalis Community static publication boundary."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "web"


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.references: list[tuple[str, str]] = []
        self.visible_text: list[str] = []
        self._hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.add(element_id)
        for attribute in ("href", "src"):
            value = values.get(attribute)
            if value:
                self.references.append((attribute, value))
        if tag in {"script", "style", "template"}:
            self._hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "template"} and self._hidden_depth:
            self._hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._hidden_depth and data.strip():
            self.visible_text.append(data.strip())


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_jsonc(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"(^|\s)//.*$", r"\1", text, flags=re.MULTILINE)
    return json.loads(text)


def validate_configuration(errors: list[str]) -> None:
    config_path = ROOT / "wrangler.jsonc"
    if not config_path.is_file():
        fail(errors, "missing wrangler.jsonc")
        return
    try:
        config = parse_jsonc(config_path)
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"invalid wrangler.jsonc: {exc}")
        return
    if config.get("pages_build_output_dir") != "./web":
        fail(errors, "wrangler.jsonc must publish ./web")
    if not config.get("compatibility_date"):
        fail(errors, "wrangler.jsonc must define compatibility_date")


def validate_required_files(errors: list[str]) -> None:
    required = [
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "CONTRIBUTING.md",
        ROOT / "CODE_OF_CONDUCT.md",
        ROOT / "SECURITY.md",
        SITE / "index.html",
        SITE / "whitepaper.html",
        SITE / "styles.css",
        SITE / "main.js",
        SITE / "_headers",
        SITE / ".well-known" / "security.txt",
    ]
    for path in required:
        if not path.is_file():
            fail(errors, f"missing required file: {path.relative_to(ROOT)}")


def validate_headers(errors: list[str]) -> None:
    path = SITE / "_headers"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "Content-Security-Policy:",
        "Strict-Transport-Security:",
        "X-Content-Type-Options: nosniff",
        "X-Frame-Options: DENY",
        "Referrer-Policy:",
        "Permissions-Policy:",
        "Cache-Control:",
    ]
    for header in required:
        if header not in text:
            fail(errors, f"web/_headers missing {header}")
    if "script-src 'self'" not in text or "style-src 'self'" not in text:
        fail(errors, "CSP must keep scripts and styles same-origin")


def validate_security_txt(errors: list[str]) -> None:
    path = SITE / ".well-known" / "security.txt"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    required = {
        "Contact:": "mailto:security.digitalis@micrantha.com",
        "Canonical:": "https://digitalis.micrantha.com/.well-known/security.txt",
        "Expires:": None,
        "Preferred-Languages:": "en",
    }
    for key, expected in required.items():
        matching = [line for line in text.splitlines() if line.startswith(key)]
        if not matching:
            fail(errors, f"security.txt missing {key}")
        elif expected and expected not in matching[0]:
            fail(errors, f"security.txt has unexpected {key} value")


def local_target(document: Path, reference: str) -> tuple[Path, str] | None:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or reference.startswith(("mailto:", "tel:")):
        return None
    raw_path = unquote(parsed.path)
    if not raw_path:
        target = document
    elif raw_path.startswith("/"):
        target = SITE / raw_path.lstrip("/")
    else:
        target = document.parent / raw_path
    return target.resolve(), unquote(parsed.fragment)


def validate_documents(errors: list[str]) -> None:
    documents: dict[Path, DocumentParser] = {}
    for document in sorted(SITE.rglob("*.html")):
        parser = DocumentParser()
        parser.feed(document.read_text(encoding="utf-8"))
        documents[document.resolve()] = parser
        if not parser.visible_text:
            fail(errors, f"{document.relative_to(ROOT)} has no static visible text")
        if "skip-link" not in document.read_text(encoding="utf-8"):
            fail(errors, f"{document.relative_to(ROOT)} lacks skip navigation")

    for document, parser in documents.items():
        for attribute, reference in parser.references:
            target_info = local_target(document, reference)
            if target_info is None:
                continue
            target, fragment = target_info
            try:
                target.relative_to(SITE.resolve())
            except ValueError:
                fail(errors, f"{document.relative_to(ROOT)} {attribute} escapes web/: {reference}")
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                fail(errors, f"{document.relative_to(ROOT)} has missing local target: {reference}")
                continue
            if fragment and target.suffix == ".html":
                target_parser = documents.get(target.resolve())
                if target_parser is None:
                    target_parser = DocumentParser()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    documents[target.resolve()] = target_parser
                if fragment not in target_parser.ids:
                    fail(errors, f"{document.relative_to(ROOT)} has missing anchor: {reference}")


def main() -> int:
    errors: list[str] = []
    validate_configuration(errors)
    validate_required_files(errors)
    validate_headers(errors)
    validate_security_txt(errors)
    validate_documents(errors)

    if errors:
        print("Digitalis Community site validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Digitalis Community site validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
