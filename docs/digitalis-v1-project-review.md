# Digitalis v1 Project Review

**Status:** Baseline implementation review  
**Reviewed:** 2026-07-26  
**Repositories:**

- `hackelia-micrantha/digitalis`
- `hackelia-micrantha/digitalis-community`
- `ryjen/cloudflare-play-integrity`

## Executive summary

Digitalis has a coherent security-product direction but remains a prototype rather than a production-ready trust-bootstrap system.

The product lineage is:

```text
Themis Cloudflare Worker
  -> corrected provider, protocol, policy, tenancy, and configuration boundaries
  -> Digitalis branding and contracts
  -> supported Digitalis Cloudflare Worker service
```

Themis is therefore not merely disposable prior art. It is the predecessor implementation and deployment lineage that should be rebuilt and rebranded as Digitalis. Cloudflare Workers remains the preferred first-party hosted verification runtime for v1.

The strongest assets are:

- a backend-authoritative trust model;
- a detailed RFC suite covering providers, configuration, policy, outcomes, and native protection;
- a useful state and outcome vocabulary;
- a working Google OAuth and Play Integrity decode path in the Themis Worker;
- existing Cloudflare deployment knowledge;
- a public community repository that can serve as the publication and documentation boundary.

The largest gaps are:

- incomplete and unsafe provider verification;
- no issued-challenge lifecycle or correct transaction binding;
- provider verdicts flattened into booleans;
- no authoritative tenant/project authorization boundary;
- raw signing and encryption key material stored in PostgreSQL;
- no credible mobile SDK implementation;
- implementation drift from the documented control contract;
- duplicated site and schema sources;
- no meaningful required CI, release assurance, or conformance suite;
- no explicit Themis-to-Digitalis repository, endpoint, and release migration plan.

The recommended first vertical slice is:

> Android + Google Play Integrity standard requests + the Digitalis Cloudflare Worker + deterministic Digitalis policy + signed configuration + one Android reference application.

Digitalis should not independently maintain the unsafe Express Google verifier and the Themis-derived Worker verifier. The useful Themis verification core should be corrected or rewritten into one provider package, and the Worker should be rebuilt and rebranded as the supported Digitalis service.

## Intended product

Digitalis is a mobile trust-bootstrap and protected-configuration system.

The intended flow is:

```text
Host application
  -> Digitalis mobile SDK
  -> platform attestation provider
  -> Digitalis Cloudflare Worker
  -> normalized evidence
  -> deterministic policy evaluation
  -> canonical startup outcome
  -> signed configuration reference
  -> verified local installation
  -> protected feature activation
```

The service, not the device, is authoritative for interpreting evidence and deciding whether protected behavior is allowed.

## Repository and service roles

### `hackelia-micrantha/digitalis`

Authoritative engineering and product repository.

It should own:

- Digitalis product identity and architecture;
- protocol and executable schemas;
- provider and policy packages;
- the supported Cloudflare Worker service or its authoritative source relationship;
- control-plane interfaces and records;
- mobile SDKs and reference applications;
- conformance fixtures and golden vectors;
- security tests and release tooling;
- private implementation documentation.

### `hackelia-micrantha/digitalis-community`

Public publication boundary.

It should own:

- public website;
- public product documentation;
- public security contact and disclosure policy;
- selected generated protocol summaries or schemas;
- public release metadata and community artifacts.

It must not independently maintain copied private implementation source. Publication should be one-way, reproducible, and provenance-bearing.

### `ryjen/cloudflare-play-integrity` / Themis

Predecessor Digitalis service and source lineage.

The repository demonstrates:

- Google service-account OAuth from a Worker;
- Play Integrity server-side token decoding;
- package, freshness, app-recognition, device-integrity, licensing, and activity checks;
- a Cloudflare Worker deployment boundary;
- operational knowledge that should carry into Digitalis.

It also contains material defects and must not remain a separate competing verifier after cutover.

Repository transition may use either:

1. a history-preserving rename/move that leaves it as the active Digitalis Worker repository; or
2. a documented migration into `hackelia-micrantha/digitalis`, with the predecessor repository retained as a redirect and provenance record.

Archival is optional and only appropriate after active service continuity, discoverability, attribution, and source/release provenance are preserved.

## Documentation assessment

### Strengths

The RFC suite captures the correct architectural concerns:

1. trust bootstrap and attestation architecture;
2. backend abstraction and conformance;
3. provider normalization;
4. protected configuration lifecycle;
5. native protection as defense in depth;
6. startup policy and canonical outcomes.

The control contract also recognizes the need for:

- versioned requests and responses;
- normalized capabilities;
- explicit outcomes and reason codes;
- configuration references;
- TTL and retry metadata;
- policy modes.

### Gaps and drift

- RFCs remain Draft or targeted for In Review despite a normalization plan saying they are ready for coordinated promotion.
- The implementation does not implement the documented endpoint split or response contract.
- Provider interfaces in code are much simpler than the provider lifecycle described in the RFCs.
- The trust-bootstrap path requires an `account_id`, although user identity should not be required for device trust bootstrap.
- State names differ slightly between documents.
- Public claims exceed implemented controls.
- The threat model overstates guarantees delivered by current provider code.
- Existing docs previously described Themis mainly as an extraction/archive source rather than the predecessor Digitalis Worker lineage.

## Backend and Worker assessment

### Current Express surface

The Express backend exposes:

- `POST /api/v1/config`;
- `POST /api/v1/admin/seed`.

The configuration controller combines provider verification, persistence, identity lookup, configuration and key selection, nonce generation, encryption, signing, logging, and response construction. This makes it difficult to test policy independently or reason about transaction boundaries.

The Express prototype should not become a second first-party Google verification service. It may supply temporary control-plane code or migration evidence, but the primary hosted runtime is the Digitalis Cloudflare Worker.

### Apple provider

The Apple implementation accepts a magic success token and otherwise performs shallow CBOR and format checks. It does not verify the certificate chain, signature, authenticator data, application identity, challenge, nonce, or replay state. It can report success without authentic evidence.

### Google provider in Digitalis

The current Digitalis Google provider accepts a magic token, uses a hard-coded package, and can return verified state after observing that the application is not `PLAY_RECOGNIZED`. Device integrity is not meaningfully enforced, and a request nonce is reused as a device identifier.

### Google provider in Themis

Themis is the stronger implementation seed because it performs the real OAuth and decode flow and rejects unrecognized applications and missing device verdicts.

It must be corrected during the Digitalis rebuild:

- compare `requestHash` to an independently reconstructed canonical request digest, not the encrypted integrity token;
- resolve package, certificate digest, version, and Google project from trusted project configuration;
- do not accept `MEETS_BASIC_INTEGRITY` as unconditional allow;
- separate provider evidence from final app actions such as `stopApp`;
- correct remediation constant and string-interpolation defects;
- separate runtime and OpenAPI types;
- enable strict TypeScript and comprehensive tests;
- add tenant, project, quota, rate, privacy, and abuse boundaries;
- cache service-account access tokens safely;
- integrate issued challenges, deterministic policy, and signed configuration.

## Security findings

### Critical

1. Apple authentication bypass through incomplete verification.
2. Google application-recognition bypass in the current Digitalis provider.
3. Magic success tokens in production code paths.
4. Unauthenticated administrative seed endpoint.
5. No issued, expiring, single-use challenge lifecycle.
6. Raw private signing keys and reusable symmetric keys stored in PostgreSQL.
7. No authoritative tenant/project request authorization.

### High

8. No deterministic policy engine or canonical outcome implementation.
9. No configuration expiry, revocation, rollback prevention, or atomic activation.
10. Noncanonical JSON serialization is signed across language boundaries.
11. Provider identity is hard-coded or client-controlled.
12. No rate limiting, quota enforcement, request body limits, or provider deadlines.
13. No explicit privacy, retention, or minimization model for provider payloads.
14. Public claims and threat-model statements exceed current implementation.
15. No documented repository, endpoint, domain, secret, and release cutover from Themis to Digitalis.

### Moderate

16. Broad default CORS and development logging.
17. Duplicate schema and site sources.
18. Weak type checking and minimal negative testing.
19. No required CI, dependency review, SBOM, provenance, or release signing.
20. Missing project governance files and repository ownership controls.

## Data and key management

The current schema and services allow raw key material in PostgreSQL even though comments imply encrypted-at-rest handling.

The v1 key model should store only:

- KMS resource identifier;
- public verification key;
- key ID;
- algorithm;
- lifecycle status and timestamps;
- rotation and audit metadata.

Digitalis should use signed configuration for v1 and defer application-layer encryption. TLS protects transport. A project-wide AES key distributed to all clients does not provide a credible additional confidentiality boundary. Per-install hardware-backed key agreement can be introduced later if a concrete secret-provisioning threat requires it.

## SDK assessment

The SDK directories contain generated placeholders rather than working SDKs.

Recommended order:

1. normative protocol schemas and golden vectors;
2. Android native implementation and reference app;
3. Apple native implementation;
4. Kotlin Multiplatform and React Native facades over stabilized native implementations.

## Overlap and duplication

### Exact duplication

- the private site and community site were copied from the same source;
- documentation schema and runtime schema are exact duplicates.

### Conceptual duplication

- overview and workflow documentation repeat the same architecture flow;
- Digitalis Express and Themis separately implement Google verification;
- provider code and policy code both decide host behavior;
- multiple documents define nearby but not identical state vocabularies.

### Required resolution

- community owns the public site;
- migrations or executable schemas own data/contract definitions and documentation is generated;
- one Google provider package is shared by the Digitalis Worker and any later supported runtime;
- the Digitalis Worker is the single supported first-party hosted verification service;
- provider adapters return normalized evidence only;
- policy returns canonical outcomes and remediation;
- one executable state and reason registry is authoritative;
- Themis-to-Digitalis repository and release provenance is explicit.

## Target v1 architecture

```text
packages/
  protocol/
  policy/
  provider-google-play-integrity/
  provider-apple-app-attest/
services/
  control-plane/
  digitalis-worker-cloudflare/
apps/
  android-reference/
conformance/
  fixtures/
  golden-vectors/
```

### API direction

```text
POST /v1/challenges
POST /v1/attestations:verify
GET  /v1/configurations/{configRef}
POST /v1/telemetry
GET  /v1/capabilities
```

### Core records

- tenants;
- projects;
- project provider configurations;
- installations;
- attestation challenges;
- attestation attempts;
- policy versions;
- configuration versions;
- signing key references;
- configuration issuances;
- security events.

User accounts are not required in the critical trust-bootstrap path.

## First credible milestone

The first production-credible milestone is complete when:

- the supported service is branded Digitalis and deployed on Cloudflare Workers;
- Themis-to-Digitalis source and release provenance is verifiable;
- no production success bypass exists;
- invalid provider signatures, identities, hashes, or verdicts fail closed;
- Google non-recognized applications fail;
- device-tier policy is explicit;
- challenges are expiring and single-use;
- replay is covered by tests;
- project identity is server-authoritative;
- cross-project access fails;
- only an authorized outcome activates protected features;
- expiry, revocation, and rollback are enforced;
- exactly one configuration and signing key can be active;
- TypeScript, Kotlin, and later Swift verify the same signed golden envelope;
- signing keys remain in KMS;
- no production seed or debug routes exist;
- required CI and security gates pass;
- release artifacts include SBOM and provenance;
- no parallel independent Themis and Digitalis verifier remains in production.

## Analysis and decisions

The analysis is divided into five QART slices under [`qart/`](qart/README.md). Accepted decisions are recorded in [`adr/`](adr/README.md) and indexed in the [QART decision register](qart-decision-register.md).

Implementation sequence and issue mapping are maintained in the [Digitalis v1 implementation roadmap](digitalis-v1-implementation-roadmap.md).
