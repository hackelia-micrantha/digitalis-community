# RFC-0004 — Secure Configuration Provisioning and Hardware-Backed Storage

## Status
In Review

## Summary
Define how the SDK validates, installs, activates, rotates, and revokes protected configuration using hardware-backed storage facilities such as Android Keystore and Apple secure enclave/keychain-backed mechanisms.

## Problem
Configuration is part of the trusted state established after attestation. Improper local storage or activation rules can undermine the entire trust bootstrap.

## Goals
- Ensure protected configuration is installed only after successful attestation and backend authorization
- Use hardware-backed primitives where available
- Define versioning, rotation, rollback resistance, and revocation expectations

## Normative Requirements
1. Protected configuration MUST be versioned.
2. Protected configuration MUST be integrity-validated before installation.
3. Sensitive key material MUST be stored in hardware-backed facilities where supported.
4. The SDK MUST record installation state atomically where feasible.
5. The SDK MUST prevent unauthorized rollback to older protected configuration versions.
6. The SDK MUST support backend-driven revocation or invalidation.
7. The SDK MUST zeroize or minimize plaintext secret residency in memory to the extent practical.

## Data Classes
- public operational configuration
- integrity-protected protected configuration
- secrets / keys / derived credentials
- installation metadata
- active version / policy binding metadata

## Activation Rules
- Public config MAY be available pre-attestation if explicitly allowed
- Protected config MUST NOT activate before successful attestation and verification
- Revoked config MUST be removed or marked unusable as soon as feasible

### Config Validity vs. Startup Outcome
Config validity (integrity, version, expiry) is a necessary but not sufficient condition for startup success. The final startup outcome is determined by RFC-0006 startup policy, which maps both config validity and other trust signals into canonical outcomes. A valid config can still result in a non-`ALLOW` outcome if other policy conditions fail.

### Containment Behavior
After config expiry, revocation, rollback rejection, or integrity failure, the SDK MUST follow containment behavior defined in RFC-0006. Specifically:
- TTL expiry with backend unreachable → `RETRYABLE_FAILURE` (RFC-0006)
- Revocation of active config → `DENY_INTEGRITY` (RFC-0006)
- Rollback rejection → `DENY_INTEGRITY` (RFC-0006)
- Integrity validation failure → `DENY_INTEGRITY` (RFC-0006)

## Security Considerations
- Hardware-backed storage is not universal; fallback behavior must be explicit and policy-gated
- Secure enclave / keystore availability differs by device and OS version
- Backup/restore semantics can create subtle rollback or cloning issues

## Binding Model Note
Weak binding is the v1 default for config installation. Strong binding (where config is cryptographically tied to a specific device or install identity beyond standard hardware-backed storage) is deferred intentionally and may be introduced in a future revision if required by policy.

## Consequences
This RFC makes configuration a governed security asset rather than generic app settings, at the cost of higher lifecycle complexity.

