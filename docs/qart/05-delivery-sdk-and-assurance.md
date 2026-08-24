# QART-05: Delivery, SDK, and Assurance

**Status:** Recommended and recorded by ADR-0001  
**Scope:** first platform, primary hosted runtime, SDK sequence, conformance, CI, and release assurance

## Questions

1. Which platform and provider should be implemented first?
2. Should v1 begin with the generic Express backend or the existing Themis Cloudflare Worker lineage?
3. Is Cloudflare Workers merely an adapter or the primary hosted Digitalis service?
4. How many SDKs should be built before the protocol stabilizes?
5. Which assurance gates define a credible milestone?
6. How should provider and deployment conformance be tested?
7. Which capabilities are explicitly deferred?

## Security invariant

The first release must prove one complete trust-bootstrap path with real provider evidence, deterministic policy, signed configuration, a native SDK, and executable negative tests. Breadth must not substitute for a verified end-to-end boundary, and the Themis-to-Digitalis rebrand must not create a second verifier or service.

## Existing evidence

- The SDK directories are generated placeholders.
- The Express backend mixes control-plane, provider, policy, and configuration delivery concerns.
- Themis already demonstrates Google service-account OAuth and token decoding in Cloudflare Workers.
- Themis is intended to be rebuilt and rebranded as Digitalis while retaining the Worker deployment model.
- Digitalis documentation attempts to cover Android, Apple, multiple SDK surfaces, custom backends, native protection, encrypted configuration, and rich degraded modes simultaneously.
- Current CI and release assurance are minimal.

## Alternatives

### A. Implement all platforms and deployment modes in parallel

Android, Apple, Kotlin Multiplatform, React Native, Express, Cloudflare, and customer-managed backends progress together.

**Advantages**

- broad product story;
- early API pressure from multiple platforms.

**Risks**

- multiplies security implementations before the contract stabilizes;
- slow feedback;
- inconsistent behavior;
- no single complete path;
- high test and release complexity.

### B. Generic Express backend first, SDKs later

Complete the Express service and database model before integrating a mobile client, and treat Themis as prior art only.

**Advantages**

- centralized implementation;
- familiar service architecture;
- easier local database development.

**Risks**

- protocol decisions remain untested by a real provider and SDK;
- provider and policy mixing may become entrenched;
- current Express code is not a safe foundation without substantial restructuring;
- loses the existing Worker-based product and deployment lineage.

### C. Rebuild Themis as the Digitalis Cloudflare Worker and deliver Android first

Build runtime-neutral protocol, provider, and policy packages inside a first-party Digitalis Cloudflare Worker service descended from Themis. Add signed configuration and one Android reference SDK/application. Add control-plane state only where required for project, challenge, policy, configuration, key, and audit records.

**Advantages**

- preserves the intended Themis-to-Digitalis product lineage;
- reuses the strongest implementation and deployment evidence;
- validates a real provider quickly;
- keeps Cloudflare Workers as the primary hosted product runtime;
- keeps core security logic testable and portable;
- delivers an executable demonstration;
- creates fixtures reusable by Apple and later runtimes.

**Risks**

- Android and Cloudflare are intentionally privileged in v1 delivery;
- control-plane and Worker state coordination must be designed;
- rebrand and repository migration require explicit provenance work;
- Apple support is deferred.

## Recommendation

Select alternative C.

### First slice

```text
Android reference app
  -> Digitalis Android SDK
  -> Google Play Integrity standard request
  -> Digitalis Cloudflare Worker service
  -> Google provider package
  -> normalized evidence
  -> Digitalis policy package
  -> canonical outcome
  -> signed config reference
  -> verified configuration activation
```

### Package and service boundaries

```text
packages/
  protocol/
  policy/
  provider-google-play-integrity/
services/
  control-plane/
  digitalis-worker-cloudflare/
apps/
  android-reference/
conformance/
  fixtures/
  golden-vectors/
```

The Cloudflare Worker is the primary first-party hosted Digitalis service. It is not a second provider or policy implementation: it composes shared packages and owns HTTP, bindings, deployment, limits, observability, and operational behavior.

### Themis transition

- preserve source and release provenance;
- correct or rewrite unsafe implementation before promotion;
- rebrand the supported service as Digitalis;
- use a history-preserving repository rename/move or a documented migration into the Digitalis repository;
- retain the old repository as a redirect/provenance record only if it no longer hosts the active service;
- archive it only after discoverability and continuity are preserved.

### SDK sequence

1. executable protocol schemas and TypeScript reference implementation;
2. native Android SDK and reference app;
3. native Apple SDK and reference app;
4. Kotlin Multiplatform facade where it can reuse native security operations;
5. React Native facade over native modules.

### Required CI

Pull requests require:

- build;
- unit tests;
- integration and replay tests;
- lint and strict type checking;
- formatting checks;
- CodeQL or equivalent static analysis;
- dependency review and package audit;
- secret scanning;
- schema and generated-artifact drift checks;
- conformance fixtures and golden vectors.

Release workflows require:

- reproducible or controlled builds;
- SBOM;
- artifact checksums;
- provenance attestation;
- signed immutable release tags or artifacts;
- release contract and migration notes;
- traceability from Digitalis releases to the Themis predecessor source where applicable.

### First milestone acceptance

- real Google decode path in the Digitalis Cloudflare Worker;
- no test bypass in production;
- server-authoritative package, certificate, and version checks;
- correct request-hash reconstruction;
- single-use challenge;
- deterministic outcomes and reasons;
- signed config verified by Android;
- replay, mismatch, expiry, rollback, and malformed-input tests;
- KMS-backed signing;
- required CI;
- public material marked accurately as prototype until these controls are demonstrated;
- service identity, repository, deployment, and provenance reflect the Themis-to-Digitalis transition.

### Deferred from v1

- customer-managed backend certification;
- production Apple implementation;
- KMP and React Native facades;
- native obfuscation and binary hardening;
- mandatory process termination;
- SIEM and case-management integrations;
- generalized risk scoring;
- per-install encrypted secret provisioning;
- complex degraded-mode orchestration;
- replacing Cloudflare Workers as the primary hosted runtime without a new QART and ADR.

## Tradeoffs

- Android-first reduces initial market breadth, but produces a credible complete path.
- Cloudflare-first creates a deliberate platform dependency for the hosted service, but preserves the existing product direction and operational knowledge.
- Runtime-neutral core packages prevent lock-in at the security-logic layer without pretending every runtime is equally supported.
- Deferring wrappers avoids duplicate cryptographic behavior, but application teams cannot use KMP or React Native until native contracts stabilize.
- Strong CI adds early work, but provider-verification defects are too consequential for optional assurance.

## Decisions

- **QART-0026:** The first implementation slice is Android plus Google Play Integrity.
- **QART-0027:** Cloudflare Workers is the primary first-party hosted verification runtime for Digitalis v1 and the continuation of the Themis service lineage.
- **QART-0028:** Provider, protocol, policy, and canonical serialization packages remain runtime-neutral and are composed by the Worker rather than duplicated inside handlers.
- **QART-0029:** Native Android precedes Apple, KMP, and React Native implementations.
- **QART-0030:** The first credible milestone requires real-binary and real-provider integration, not mock-only tests.
- **QART-0031:** CI, conformance, SBOM, and provenance are release requirements, not later hardening.
- **QART-0032:** Deferred capabilities or a change of primary hosted runtime require separate QART and ADR promotion before entering v1 scope.

## Required tests and evidence

- deployed Digitalis Worker decodes a real test-provider token;
- Android reference app produces the bound request hash;
- golden request, evidence, decision, and configuration envelopes;
- provider fake for deterministic negative tests;
- emulator or unsupported-environment behavior;
- rate-limit and Google-quota behavior;
- OAuth credential rotation and cache expiry;
- Worker/control-plane timeout and partial-failure behavior;
- artifact provenance verification;
- Themis-to-Digitalis repository and release provenance verification;
- installation and upgrade test for the Android SDK.
