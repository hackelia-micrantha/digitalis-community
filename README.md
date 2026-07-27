# Digitalis Community

Digitalis Community is the public publication, release, and community boundary for the Digitalis mobile application trust project.

## Repository role

This repository contains reviewed public material, including:

- the public website and architecture whitepaper under `web/`;
- public release artifacts and provenance metadata when available;
- contribution, security, and community guidance;
- deployment configuration for the public static site.

The authoritative engineering implementation and private threat-analysis material are maintained outside this public repository. Content published here must be explicitly reviewed for public release and must not include secrets, raw attestation evidence, private exploit detail, or unpublished implementation material.

## Project status

Digitalis is currently an architecture and integration prototype. The public site distinguishes defined architecture, active implementation, evaluated integrations, and planned work. It does not claim production readiness, completed cross-provider parity, or stable public SDK compatibility.

See [`web/index.html`](web/index.html) for the current public status and [`web/whitepaper.html`](web/whitepaper.html) for the public architecture summary.

## Public-site deployment

The deployable site root is `web/`. Cloudflare Pages or equivalent static hosting must publish that directory rather than the repository root.

Security headers and cache policy are defined in [`web/_headers`](web/_headers). The canonical security contact is published at [`web/.well-known/security.txt`](web/.well-known/security.txt).

## Publication provenance

Public technical material should identify, where appropriate:

- publication or document version;
- review date;
- public tracking issue or decision record;
- source release or opaque publication identifier;
- generation method for generated material.

Private repository identifiers must not be disclosed unless they have been explicitly approved for publication.

## Contributing and security

- Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before proposing changes.
- Follow [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) in community spaces.
- Report vulnerabilities through [`SECURITY.md`](SECURITY.md), not public issues.

## License

Repository content is licensed under the terms in [`LICENSE`](LICENSE), except where a file or published artifact states otherwise.
