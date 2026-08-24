# QART-04: Configuration and Key Lifecycle

**Status:** Recommended and recorded by ADR-0005  
**Scope:** configuration signing, confidentiality, activation, expiry, rollback, revocation, and key custody

## Questions

1. Does v1 require application-layer configuration encryption in addition to TLS?
2. Where should signing keys and encryption keys be stored?
3. How are configuration versions activated, expired, revoked, and rolled back safely?
4. What does the SDK verify before activating protected features?
5. How are key and configuration rotations made atomic?
6. What evidence is retained for issued configurations?

## Security invariant

A client activates protected features only after verifying a canonical, signed, authorized, unexpired, non-revoked configuration envelope whose project, policy, and issuance context match the accepted startup decision. Private signing keys never leave managed key custody.

## Existing evidence

- Digitalis currently encrypts configuration with a project-wide AES key and signs a JSON payload.
- Raw RSA private keys and symmetric keys are stored in PostgreSQL.
- Rotation creates additional active keys without deactivating prior keys.
- Configuration selection does not consistently enforce expiry, revocation, rollback, or one-active-version invariants.
- JSON serialization is not canonical across languages.
- No credible mechanism securely provisions a reusable project-wide AES key to every client.

## Alternatives

### A. Sign and encrypt every configuration with project-wide keys stored in PostgreSQL

**Advantages**

- resembles the current implementation;
- provides a second encrypted layer in addition to TLS;
- straightforward server code.

**Risks**

- database compromise exposes private signing and decryption keys;
- the shared client decryption key must be embedded or broadly distributed;
- encryption may create a false confidentiality claim;
- rotation and revocation are difficult;
- cross-language envelope verification is underspecified.

### B. Signed canonical configuration for v1, with keys held in KMS

The server signs canonical bytes through a managed key service. The client embeds or retrieves trusted public keys and verifies signatures. TLS provides transport confidentiality. Application-layer encryption is deferred.

**Advantages**

- solves the core integrity and authenticity requirement;
- no reusable client decryption secret;
- signing key cannot be read from the database;
- simpler SDK and golden-vector conformance;
- supports key IDs and rotation.

**Risks**

- configuration contents are visible to a compromised client after delivery;
- requires honest product language about confidentiality;
- KMS integration adds cloud-provider operational dependency.

### C. Per-install hardware-backed key agreement and encrypted configuration

Each installation creates a hardware-backed asymmetric key. The backend encrypts or wraps configuration material for that installation after successful attestation.

**Advantages**

- strongest configuration confidentiality option;
- supports installation-specific revocation and secret provisioning;
- no project-wide decryption key.

**Risks**

- substantially more protocol and recovery complexity;
- platform asymmetry;
- key replacement and device migration concerns;
- not necessary for non-secret configuration.

## Recommendation

Select alternative B for v1. Preserve alternative C as a future capability gated by a concrete secret-provisioning threat model.

### Canonical envelope

The signed envelope should contain:

```text
contract_version
project_id
config_id
config_version
policy_version
issued_at
not_before
expires_at
configuration payload or payload digest
required capabilities
minimum SDK version
key_id
algorithm
```

The canonical serialization must be specified and tested. Acceptable choices include RFC 8785 JSON Canonicalization Scheme or deterministic CBOR. The project must select one and publish golden vectors.

### Client activation

The SDK verifies:

1. supported contract and algorithm;
2. trusted key ID and signature;
3. project binding;
4. configuration ID and version;
5. issuance and expiry times with bounded skew;
6. non-revocation state when online policy requires it;
7. minimum SDK and capability requirements;
8. linkage to the accepted startup decision or configuration reference;
9. rollback floor stored in protected local metadata.

Only after all checks pass may the SDK atomically activate the configuration.

### Key records

PostgreSQL stores:

- KMS resource ID;
- public key;
- key ID;
- algorithm;
- status: pending, active, retiring, revoked;
- activation and retirement timestamps;
- creator and approval metadata;
- audit references.

It does not store private signing key bytes.

### Rotation

- create and validate the next KMS key;
- publish its public key through the trusted-key set;
- transition the next key to active in one transaction;
- transition the prior key to retiring;
- permit a bounded verification overlap;
- stop issuing new envelopes with the retiring key;
- revoke only after configured client compatibility and incident requirements are satisfied.

### Configuration lifecycle

- drafts are immutable once submitted for approval;
- activation creates one authoritative active version per project/environment;
- activation and deactivation occur atomically;
- expired or revoked versions cannot be issued;
- rollback requires an explicit authorized rollback operation and a monotonic rollback floor;
- each issuance records policy version, evidence digest, config version, key ID, timestamps, and decision reference.

## Tradeoffs

- Signed-only configuration does not hide data from the endpoint, but a client that consumes the data cannot be assumed to keep a shared symmetric key secret either.
- KMS adds cost and provider integration, but removes the highest-risk key-custody defect.
- Online revocation checks increase availability dependency; policy may permit bounded offline use using signed expiry and a locally stored rollback floor.

## Decisions

- **QART-0019:** Digitalis v1 uses signed canonical configuration without project-wide application-layer encryption.
- **QART-0020:** Private signing keys remain in KMS or equivalent managed key custody.
- **QART-0021:** PostgreSQL stores key references and public metadata, not private key material.
- **QART-0022:** Exactly one configuration version and one issuing key are active per project/environment at a time.
- **QART-0023:** Configuration expiry, revocation, and rollback rules are enforced before issuance and activation.
- **QART-0024:** SDK activation is atomic and stores a protected monotonic rollback floor.
- **QART-0025:** Per-install encrypted secret provisioning is deferred until justified by a separate threat model and ADR.

## Required tests

- cross-language signature golden vectors;
- noncanonical payload rejection;
- unknown and revoked key IDs;
- expired and not-yet-valid envelopes;
- wrong project or configuration reference;
- concurrent key rotation;
- concurrent configuration activation;
- one-active database constraints;
- attempted rollback below stored floor;
- explicit authorized rollback;
- offline expiry and clock-skew behavior;
- KMS denial and timeout behavior;
- issuance audit completeness.