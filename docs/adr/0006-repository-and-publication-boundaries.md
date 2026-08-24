# ADR-0006: Engineering and Public Publication Boundaries

**Status:** Accepted  
**Date:** 2026-07-26  
**QART decisions:** QART-0001, QART-0002, QART-0005

## Context

The private Digitalis repository and public `digitalis-community` repository contain copied website source. Runtime and documentation schema sources are also duplicated. Without explicit ownership, public claims, schemas, and implementation can drift independently.

Digitalis needs a private engineering boundary and a public product/community boundary without maintaining duplicate authoritative sources.

## Decision

`hackelia-micrantha/digitalis` is the authoritative engineering repository.

It owns protocol, providers, policy, control plane, deployment adapters, SDKs, reference applications, conformance, release tooling, and private implementation documentation.

`hackelia-micrantha/digitalis-community` is the public publication boundary.

It owns the public website, public security and disclosure material, selected generated documentation, public release metadata, and future community artifacts.

Publication from Digitalis to Digitalis Community is one-way and reproducible. Published artifacts record the source repository, source commit, contract or document version, and generation method.

The public repository does not independently modify copied private implementation, protocol, or schema source.

Database migrations or executable protocol schemas are authoritative. Human-readable schema documentation is generated.

## Consequences

### Positive

- private engineering and public communication responsibilities are clear;
- public content can be audited back to a source commit;
- implementation and schema drift are reduced;
- security claims can be gated on demonstrated controls;
- public repository access does not expose private implementation.

### Negative

- publication automation and provenance metadata are required;
- contributors cannot directly edit generated public technical artifacts;
- website changes must identify their authoritative source;
- repository naming may require clarification if community capabilities expand.

## Constraints

- public status language must distinguish design, prototype, preview, and production controls;
- no private secrets, internal threat details, or unreviewed exploit instructions are published;
- generated files contain clear generated-source headers where appropriate;
- publication drift is checked in CI;
- the public security contact and disclosure policy remain independently accessible.

## Validation

This decision is complete when duplicate private site and schema sources are removed or generated, the community deployment uses the correct public directory, publication records source provenance, and CI detects public artifact drift.