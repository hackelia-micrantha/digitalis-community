# Digitalis v1 Implementation Roadmap

**Status:** Proposed execution order  
**Basis:** Digitalis project review, QART-01 through QART-05, ADR-0001 through ADR-0006

## Objective

Deliver one production-credible Android trust-bootstrap path using Google Play Integrity, the first-party Digitalis Cloudflare Worker service descended from Themis, deterministic Digitalis policy, KMS-backed signed configuration, and a native Android SDK/reference application.

## Product and runtime direction

- Themis is the predecessor Digitalis service and implementation lineage.
- The supported v1 service is rebuilt and rebranded as Digitalis.
- Cloudflare Workers remains the primary first-party hosted verification runtime.
- Protocol, provider, policy, and canonical serialization packages remain runtime-neutral so the Worker composes rather than duplicates security logic.
- Repository transition may use a history-preserving rename/move or a documented migration into `hackelia-micrantha/digitalis`.
- A predecessor repository is archived only after active service continuity, discoverability, attribution, and source/release provenance are preserved.
- Commercialization is a post-milestone P2 validation track under #32 and `docs/product/commercialization-strategy.md`; commercial requirements must not weaken or reorder the P0/P1 trust and assurance gates.

## Program structure

### Phase 0: remove unsafe prototype behavior

1. Remove magic success tokens from production provider paths.
2. Disable or remove the unauthenticated administrative seed endpoint outside controlled development fixtures.
3. Make incomplete Apple verification fail closed and explicitly unsupported until implemented.
4. Make the current unsafe Digitalis Google provider fail closed until replaced.
5. Correct public documentation so prototype status and unimplemented guarantees are explicit.

**Exit criteria**

- no unauthenticated path can manufacture trusted state;
- no incomplete provider reports verified evidence;
- production configuration cannot enable seed or mock bypasses.

### Phase 1: executable protocol and state model

1. Define OpenAPI and executable schemas for challenge, verification, decision, configuration reference, capabilities, telemetry, and signed configuration envelope.
2. Establish canonical serialization and hashing.
3. Create the canonical outcome, reason, remediation, provider-error, and capability registries.
4. Add golden vectors consumed by TypeScript and Kotlin.
5. Create challenge, attempt, policy-version, configuration-version, issuance, installation, and security-event migrations.

**Exit criteria**

- schemas generate or validate runtime types;
- golden vectors pass in TypeScript and Kotlin;
- state and reason names have one authoritative registry.

### Phase 2: rebuild the Themis verification core

1. Inventory Themis code, behavior, deployment knowledge, provenance, and known defects.
2. Migrate or rewrite the useful Google OAuth and decode flow.
3. Build `provider-google-play-integrity` as the single runtime-neutral verdict package.
4. Validate package, certificate digest, version, request details, provider environment, and project identity from server configuration.
5. Correct standard-request `requestHash` reconstruction.
6. Return structured evidence rather than boolean success or host actions.
7. Cache OAuth access tokens with safe expiry handling.
8. Add provider deadlines, error classification, quota handling, and redacted audit metadata.
9. Preserve Themis attribution and behavioral compatibility notes.

**Exit criteria**

- non-recognized apps fail;
- wrong package, certificate, version, project, hash, and stale requests fail;
- all provider verdict tiers have deterministic fixtures;
- provider package contains no Digitalis allow/deny policy;
- no second independent Google verdict implementation remains.

### Phase 3: challenge and policy boundary

1. Implement provider-neutral challenge issuance.
2. Atomically consume successful challenges.
3. Add replay, duplicate, expiry, revocation, and retry semantics.
4. Implement deterministic policy evaluation.
5. Map normalized evidence to canonical outcomes and reason codes.
6. Add named remediation output.
7. Remove user-account dependency from the trust-bootstrap path.

**Exit criteria**

- replay and concurrent double-submission tests pass;
- policy fixtures reproduce exactly;
- only a policy decision can authorize a configuration reference.

### Phase 4: signed configuration and key custody

1. Select and document canonical configuration serialization.
2. Replace database private-key storage with KMS references.
3. Implement trusted public-key distribution and key IDs.
4. Add one-active key and configuration constraints.
5. Enforce expiry, revocation, activation, retirement, and rollback state.
6. Record configuration issuance evidence.
7. Remove project-wide application-layer encryption from v1 code and claims.

**Exit criteria**

- database contains no private signing key bytes;
- TypeScript and Kotlin verify identical signed envelopes;
- activation, expiry, revocation, rotation, and rollback tests pass.

### Phase 5: rebuild and rebrand the Digitalis Cloudflare Worker

1. Rebuild the Themis Worker as the supported Digitalis service over shared protocol, provider, policy, configuration, and audit packages.
2. Rename service identity, API documentation, package metadata, domains, and operational material from Themis to Digitalis.
3. Declare required Worker secrets and bindings.
4. Add request validation, body limits, rate limiting, project quotas, correlation IDs, provider deadlines, and structured security events.
5. Integrate Worker requests with authoritative challenge, policy, configuration, and audit records.
6. Add preview, staging, production, deployment, and rollback configuration.
7. Select and document repository rename/move or migration mechanics.
8. Add endpoint and consumer cutover guidance and redirects where required.
9. Add operational runbooks for credential rotation, Google quota, incident response, migration, and rollback.

**Exit criteria**

- the supported service is branded Digitalis and runs on Cloudflare Workers;
- Worker handlers contain no duplicate provider or policy implementation;
- deployment fails when required secrets are absent;
- abuse and quota tests pass;
- production logs do not expose evidence or credentials;
- Themis-to-Digitalis source and release provenance is verifiable;
- no production deployment depends on parallel independent Themis and Digitalis services.

### Phase 6: Android SDK and reference application

1. Implement challenge retrieval and capability negotiation.
2. Prepare Google standard integrity requests.
3. Construct canonical operation data and request hash.
4. Submit provider evidence to the Digitalis Worker and process canonical decisions.
5. Retrieve and verify signed configuration.
6. Store protected configuration metadata and rollback floor.
7. Activate protected features only after an authorized outcome.
8. Map named remediation to supported Android behavior.
9. Build a reference app demonstrating allow, deny, retry, unsupported, expiry, revocation, and rollback paths.

**Exit criteria**

- a real Android binary completes the end-to-end Digitalis Worker flow;
- protected features remain unavailable for every negative fixture;
- upgrade and reinstall behavior is documented and tested.

### Phase 7: assurance and publication

1. Require build, test, strict type checking, lint, format, dependency review, static analysis, secret scanning, and conformance checks.
2. Add real-provider integration testing in a controlled environment.
3. Produce SBOM, checksums, provenance, and signed immutable release artifacts.
4. Establish CODEOWNERS, security policy, contribution guidance, issue templates, and branch protection.
5. Verify Themis-to-Digitalis repository and release provenance.
6. Replace copied website and schema sources with one-way generated publication.
7. Update `digitalis-community` with accurate public architecture and status.

**Exit criteria**

- required checks protect the default branch;
- release evidence is independently verifiable;
- public claims match demonstrated implementation;
- the active Digitalis Worker and predecessor lineage are discoverable and documented.

## Priorities

### P0 — active implementation boundary

- unsafe bypass removal;
- protocol schemas and challenge lifecycle;
- corrected Themis-derived Google provider core;
- deterministic policy and canonical outcomes;
- KMS-backed signed configuration;
- tenant/project authorization;
- required CI and security gates.

### P1 — first complete product slice

- Digitalis Cloudflare Worker rebuild and rebrand;
- Android SDK and reference app;
- configuration lifecycle and rollback;
- replay and cross-project test suite;
- repository and endpoint cutover from Themis to Digitalis;
- public/private repository publication boundary;
- privacy and retention rules.

### P2 — expansion and commercial validation after milestone

- commercialization/product validation track (#32; `docs/product/commercialization-strategy.md`);
- privacy-preserving metering semantics and measured unit economics before billing implementation;
- design-partner discovery and bounded paid integration path;
- public/private/commercial artifact and licensing decisions before broad SDK/source publication;
- Apple App Attest provider and native Apple SDK;
- cross-language Swift golden vectors;
- customer-managed backend packaging and conformance only if supported by validated enterprise demand;
- Kotlin Multiplatform and React Native facades.

### P3 — later assurance and product expansion

- per-install encrypted secret provisioning;
- native protection and binary validation;
- pinning;
- risk and anomaly scoring;
- SIEM and case-management integrations;
- alternate first-party hosted runtimes, requiring new QART and ADR approval.

## Non-goals for the first milestone

- generic multi-provider scoring;
- shared project AES keys;
- mandatory application termination;
- production Apple verification;
- all mobile wrappers;
- customer-managed backend certification;
- billing/payment integration or plan-dependent trust semantics;
- broad commercial control-plane implementation before its threat model and customer evidence exist;
- maintaining separate Themis and Digitalis hosted verifiers;
- replacing Cloudflare Workers as the primary hosted runtime;
- opaque security claims not backed by tests.

## Definition of done for implementation issues

Every implementation issue must include:

- linked QART and ADR decisions;
- threat or failure mode addressed;
- explicit in-scope and out-of-scope boundaries;
- testable acceptance criteria;
- negative tests;
- migration or compatibility notes;
- logging and privacy considerations;
- rollback plan where state, repository, endpoint, or deployment changes;
- documentation and provenance updates.
