# ADR-0005: Signed Canonical Configuration with KMS Key Custody

**Status:** Accepted  
**Date:** 2026-07-26  
**QART decisions:** QART-0019 through QART-0025

## Context

The prototype stores raw private signing keys and project-wide AES keys in PostgreSQL, signs noncanonical JSON, and does not define a credible mechanism to provision a shared decryption key to clients. Configuration expiry, revocation, rotation, activation, and rollback are incomplete.

The v1 requirement is trustworthy configuration integrity and authorization. Endpoint confidentiality against the endpoint itself is not achievable with a broadly distributed project-wide symmetric key.

## Decision

Digitalis v1 distributes signed canonical configuration without project-wide application-layer encryption.

TLS provides transport confidentiality. Private signing keys remain in KMS or equivalent managed key custody and are referenced, not stored, by Digitalis.

The signed envelope includes contract, project, configuration, policy, validity, capability, SDK, key, algorithm, and payload information. Digitalis selects one canonical serialization and publishes cross-language golden vectors.

PostgreSQL stores:

- KMS resource ID;
- public key;
- key ID and algorithm;
- lifecycle status and timestamps;
- rotation and audit metadata.

Exactly one configuration version and one issuing key are active per project/environment. Activation and retirement are transactional. Expired or revoked configurations cannot be issued. SDKs store a protected monotonic rollback floor and atomically activate verified configuration.

Per-install hardware-backed encrypted secret provisioning is deferred until a separate threat model and ADR justify it.

## Consequences

### Positive

- database compromise does not reveal private signing keys;
- SDKs do not contain a reusable shared decryption secret;
- cross-language signature behavior is testable;
- key rotation and revocation become explicit;
- product claims match the actual security boundary.

### Negative

- configuration contents are visible after delivery to the client;
- KMS availability and cost enter the issuance path;
- public-key distribution and overlap rotation require lifecycle controls;
- protected offline rollback state differs across platforms.

## Constraints

- private key bytes never enter application memory or database storage;
- signature input is canonical and versioned;
- configuration references are scoped to the accepted decision;
- activation checks project, validity, key, capabilities, minimum SDK, and rollback floor;
- issuance records retain only the evidence necessary for audit and incident response.

## Validation

This decision is complete when TypeScript and Kotlin verify the same golden envelopes, unknown/revoked keys fail, expiry and rollback tests pass, concurrent activation preserves one-active invariants, and database inspection confirms that no private signing key material is present.