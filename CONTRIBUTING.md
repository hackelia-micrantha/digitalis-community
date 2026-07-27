# Contributing to Digitalis Community

Digitalis Community is the public publication, release, and community boundary for Digitalis. Contributions should improve public documentation, release evidence, deployment safety, accessibility, or community guidance without exposing private implementation material.

## Before opening a change

- Search existing issues and pull requests for overlap.
- Keep each change focused and explain the public outcome.
- Use issue #2 or a linked public issue for publication-boundary work.
- Do not copy material from private repositories unless it has been explicitly reviewed for publication.

## Prohibited content

Do not publish:

- credentials, tokens, keys, account identifiers, or internal endpoints;
- raw attestation evidence or customer data;
- private threat analysis or unreviewed exploit details;
- unpublished implementation code or private repository identifiers;
- third-party material without an appropriate license and attribution.

## Public technical claims

Describe maturity precisely. Prefer explicit terms such as:

- **design** for an architectural proposal;
- **prototype** for active validation work;
- **preview** for publicly consumable but unstable artifacts;
- **production** only when release, operational, compatibility, and security evidence support the claim.

Generated or synchronized public material should identify its publication version, review date, source release or opaque publication identifier, and generation method where practical.

## Pull requests

A pull request should include:

- what changed and why;
- the public user or maintainer impact;
- security and publication-boundary considerations;
- validation performed;
- remaining follow-up work.

Changes to `web/` should preserve:

- readable content without JavaScript;
- keyboard navigation and visible focus;
- reduced-motion behavior;
- valid internal links;
- the canonical `.well-known/security.txt` path;
- the security and cache policy in `web/_headers`.

## Validation

Run the repository site validator before requesting review:

```sh
python3 scripts/validate_site.py
```

The same validator runs in GitHub Actions.
