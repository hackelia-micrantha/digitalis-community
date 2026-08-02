#!/usr/bin/env python3
"""Smoke-test the deployed Digitalis Community production site."""

from __future__ import annotations

import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "https://digitalis.micrantha.com"
CHECKS = {
    "/": "Mobile trust",
    "/whitepaper.html": "Digitalis",
    "/.well-known/security.txt": "Contact: mailto:security.digitalis@micrantha.com",
    "/robots.txt": "Sitemap: https://digitalis.micrantha.com/sitemap.xml",
    "/sitemap.xml": "https://digitalis.micrantha.com/whitepaper.html",
}
REQUIRED_HEADERS = {
    "content-security-policy": ("frame-ancestors 'none'", "object-src 'none'"),
    "strict-transport-security": ("max-age=",),
    "x-content-type-options": ("nosniff",),
    "referrer-policy": ("strict-origin-when-cross-origin",),
}
NESTED_404_PATH = "/docs/definitely-not-a-real-route"
NESTED_404_MARKERS = (
    'href="/styles.css"',
    'href="/"',
    'href="/whitepaper.html"',
    "404 · page not found",
)


def fetch(path: str) -> tuple[int, dict[str, str], str]:
    request = Request(
        f"{BASE_URL}{path}",
        headers={"User-Agent": "digitalis-production-smoke/1"},
    )
    try:
        response = urlopen(request, timeout=20)
    except HTTPError as exc:
        response = exc

    with response:
        body = response.read().decode("utf-8", errors="replace")
        headers = {key.lower(): value for key, value in response.headers.items()}
        return response.status, headers, body


def main() -> int:
    errors: list[str] = []
    for path, expected_text in CHECKS.items():
        try:
            status, headers, body = fetch(path)
        except URLError as exc:
            errors.append(f"{path}: connection failed: {exc.reason}")
            continue

        if status != 200:
            errors.append(f"{path}: expected HTTP 200, got {status}")
        if expected_text not in body:
            errors.append(f"{path}: expected content marker not found")

        if path == "/":
            for header, required_values in REQUIRED_HEADERS.items():
                actual = headers.get(header, "")
                if not actual:
                    errors.append(f"/: missing {header}")
                    continue
                for required in required_values:
                    if required.lower() not in actual.lower():
                        errors.append(f"/: {header} missing {required}")

    try:
        status, _, body = fetch(NESTED_404_PATH)
    except URLError as exc:
        errors.append(f"{NESTED_404_PATH}: connection failed: {exc.reason}")
    else:
        if status != 404:
            errors.append(f"{NESTED_404_PATH}: expected HTTP 404, got {status}")
        for marker in NESTED_404_MARKERS:
            if marker not in body:
                errors.append(f"{NESTED_404_PATH}: missing 404 marker {marker}")

    if errors:
        print("Digitalis production smoke test failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Digitalis production smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
