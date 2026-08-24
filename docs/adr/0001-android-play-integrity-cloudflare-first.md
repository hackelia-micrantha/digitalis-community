# ADR-0001: Android, Play Integrity, and Cloudflare First

**Status:** Accepted  
**Date:** 2026-07-26  
**QART decisions:** QART-0026 through QART-0032

## Context

Digitalis currently has broad documentation but no complete production-credible platform path. SDK directories are placeholders, the Express backend mixes concerns, and the strongest existing provider and deployment evidence is the Themis Cloudflare Worker for Google Play Integrity.

Themis is the predecessor product and code lineage for Digitalis, not merely an unrelated prototype. The intended evolution is to rebuild and rebrand that Worker-based service as Digitalis while correcting its protocol, provider, policy, tenancy, and assurance defects.

Attempting Android, Apple, multiple wrappers, multiple backends, encryption, native protection, and customer conformance simultaneously would multiply security implementations before the protocol is executable.

## Decision

The first implementation slice is:

```text
Android native SDK and reference app
  -> Google Play Integrity standard request
  -> Digitalis verification service on Cloudflare Workers
  -> runtime-neutral Google provider package
  -> runtime-neutral Digitalis policy package
  -> canonical outcome
  -> KMS-signed configuration
  -> verified Android activation
```

Cloudflare Workers is the primary hosted verification runtime for Digitalis v1 and the direct continuation of the Themis deployment model.

The Worker owns:

- public HTTP routing and contract enforcement;
- Cloudflare bindings and environment configuration;
- request limits, rate controls, deadlines, and correlation;
- composition of challenge, provider, policy, configuration, and audit services;
- deployment, preview, rollback, and operational behavior.

The Worker does not independently own or duplicate provider verdict interpretation, policy rules, canonical serialization, or cross-language protocol definitions. Those remain runtime-neutral packages so they are testable, reusable, and portable if another supported runtime is added later.

Native Android is implemented before Apple, Kotlin Multiplatform, and React Native surfaces.

The first milestone requires real provider integration and a real Android binary. Mock-only success does not satisfy the milestone.

CI, conformance fixtures, SBOM, provenance, and signed immutable releases are included in the milestone definition.

## Consequences

### Positive

- evolves the existing Themis product and deployment lineage rather than discarding it;
- produces one end-to-end security boundary early;
- keeps Cloudflare Workers as the primary operational model;
- validates protocol and SDK assumptions against a real provider;
- creates fixtures reusable by Apple and later deployment runtimes;
- avoids premature wrapper duplication.

### Negative

- Apple and cross-platform wrappers are deferred;
- the initial hosted product remains Cloudflare-centric;
- control-plane and Worker state coordination must be implemented;
- a real Play Integrity test environment is required;
- Themis naming, repository identity, and deployment continuity require an explicit rebrand and migration plan.

## Constraints

- protocol, policy, provider, and canonical serialization packages remain runtime-neutral;
- the Cloudflare Worker remains the supported first-party hosted service rather than a disposable example adapter;
- Worker-specific bindings do not appear in public protocol schemas;
- platform-specific numeric remediation codes remain inside the Android SDK;
- no second Google verifier or policy implementation is maintained for Express or another runtime;
- deferred capabilities require separate QART and ADR promotion.

## Validation

This decision is validated when a released Android reference binary completes the real challenge, Play Integrity, Digitalis Worker, policy, signed-configuration, and activation path, and every defined negative fixture prevents protected feature activation.
