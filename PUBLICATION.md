# Digitalis Public Publication Workflow

This repository is the authoritative public publication boundary for Digitalis. It is not a mirror of a private engineering repository.

## Direction

Publication is **one-way inbound**:

1. Private or internal work is selected for public release.
2. The material is reduced to the minimum publication-safe package.
3. Secrets, raw attestation evidence, private identifiers, exploit detail, and unpublished implementation material are removed.
4. A reviewer approves the public claims, maturity language, and provenance record.
5. The package is committed through a pull request in `digitalis-community`.
6. After merge, the public repository owns the published files. Later public edits happen here unless another explicitly reviewed publication package replaces them.

There is no automatic reverse synchronization from this repository into private engineering sources. There is no implicit full-repository mirroring in either direction.

## Publication manifest

[`publication/manifest.json`](publication/manifest.json) records:

- the publication identifier and review date;
- the direction and destination boundary;
- a publication-safe source reference;
- policy constraints preventing reverse sync and private identifier disclosure;
- each governed artifact, its version, ownership, generation method, and source reference.

A private repository name or commit may be recorded only when explicitly approved for public disclosure. Otherwise use an opaque publication identifier that can be resolved by authorized maintainers outside this repository.

## Required package fields

Each imported or generated public artifact must have:

- a repository-relative path;
- a public version;
- an ownership classification;
- a generation or maintenance method;
- a publication-safe source reference.

All paths must remain within this repository and must exist at validation time. Manifest entries must be unique.

## Ownership classes

- `publication-owned`: maintained directly in this repository after initial review.
- `generated-publication`: generated from a reviewed source package and replaced only through a new publication run.
- `external-artifact`: third-party or separately released material with explicit license and provenance.

The current website is `publication-owned`. This resolves duplicate ownership: the public copy is maintained here rather than synchronized continuously from a private site tree.

## Validation

Run:

```sh
python3 scripts/validate_publication.py
python3 scripts/validate_site.py
```

CI runs both validators whenever publication metadata, governed files, deployment configuration, or validation code changes.
