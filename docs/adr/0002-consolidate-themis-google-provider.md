# ADR-0002: Rebuild and Rebrand Themis as the Digitalis Cloudflare Service

**Status:** Accepted  
**Date:** 2026-07-26  
**QART decisions:** QART-0003, QART-0004

## Context

Digitalis and `ryjen/cloudflare-play-integrity` currently contain separate Google Play Integrity verification prototypes.

The Digitalis implementation is structurally newer but contains unsafe mock success and incorrect verdict enforcement. The Themis implementation contains a real Google OAuth and token-decode path and stricter app/device checks, but it also has incorrect request-hash validation, client-controlled package identity, policy leakage, type defects, and no tenant boundary.

Themis is the predecessor implementation and product identity that will evolve into Digitalis. Its Cloudflare Worker deployment model is expected to continue as the primary Digitalis hosted verification service.

Maintaining two security-critical implementations or treating the Worker as disposable would create permanent drift and lose useful operational continuity.

## Decision

Digitalis will evolve the Themis lineage into one supported Cloudflare Worker service branded as Digitalis.

The implementation will contain one runtime-neutral `provider-google-play-integrity` package and one runtime-neutral Digitalis policy/protocol core, composed by the first-party Cloudflare Worker service.

Useful Themis behavior, deployment knowledge, repository history, and attribution will be preserved, but defective code will be corrected or rewritten before becoming authoritative.

The provider package owns:

- service-account authentication and token caching;
- Google token decoding;
- verification of request details against stored challenge context;
- application identity validation against server-side project configuration;
- provider-specific claim parsing and normalization;
- provider error classification;
- provider capability reporting.

The Digitalis Cloudflare Worker owns:

- the public service endpoints;
- Cloudflare bindings and secret configuration;
- request validation, limits, rate controls, deadlines, and correlation;
- composition of protocol, provider, policy, configuration, and audit services;
- deployment, preview, rollback, and operational runbooks.

Neither the provider package nor the Worker independently owns duplicate final policy rules, host application actions, or cross-language protocol definitions.

## Repository transition

The product transition may be implemented by either:

1. renaming or moving the existing Themis repository while preserving its Git history; or
2. migrating the implementation and relevant history into `hackelia-micrantha/digitalis`, then retaining the old repository as a redirect and provenance record.

The exact Git repository mechanics are an implementation decision, but these outcomes are required:

- the supported service is branded Digitalis;
- the supported hosted runtime remains Cloudflare Workers;
- source and release provenance trace back to the Themis lineage;
- only one production Google verifier and one first-party Worker service remain;
- the old repository is archived only if its active role has been replaced or renamed without losing discoverability or history.

## Consequences

### Positive

- preserves the intended product lineage from Themis to Digitalis;
- retains the proven Cloudflare Worker deployment direction;
- one implementation receives security fixes;
- historical work and attribution are preserved;
- provider and policy tests become reusable;
- Digitalis can remove its unsafe Express prototype provider.

### Negative

- the change is a redesign and rebrand rather than a direct rename-only migration;
- historical OpenArchive/Themis naming and licensing must be reconciled;
- repository and deployment continuity must be planned explicitly;
- runtime-neutral package boundaries add some structure inside a Worker-first product.

## Required corrections during the rebuild

- reconstruct and compare the expected canonical `requestHash`;
- resolve package, certificate digest, version, and Google project from trusted project configuration;
- preserve integrity tiers rather than returning one success boolean;
- remove `stopApp` and native dialog codes from provider output;
- separate HTTP schemas from runtime types;
- enable strict TypeScript;
- add deterministic provider fixtures and negative tests;
- add deadlines, quotas, rate limits, secure secret bindings, and OAuth token caching;
- integrate issued challenges, deterministic policy, signed configuration, tenancy, privacy, and audit controls.

## Validation

This decision is complete when the supported Digitalis Cloudflare Worker is demonstrably descended from and replaces the Themis service, only one package interprets Google Play Integrity claims, the unsafe Digitalis Express provider is removed, real-provider tests pass, and repository/release provenance documents the rebrand and migration.
