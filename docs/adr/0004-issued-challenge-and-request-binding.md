# ADR-0004: Issued Challenges and Canonical Request Binding

**Status:** Accepted  
**Date:** 2026-07-26  
**QART decisions:** QART-0006 through QART-0011

## Context

The current backend accepts provider evidence directly during configuration delivery. It has no persisted challenge lifecycle, no atomic replay state, and no provider-neutral transaction binding. Themis checks freshness but incorrectly compares Google `requestHash` with the encrypted integrity token and trusts a client-provided package.

Provider evidence must be bound to one Digitalis project, operation, and short-lived server issuance.

## Decision

Digitalis uses a provider-neutral challenge lifecycle with separate operations for challenge issuance, evidence verification, and configuration retrieval.

```text
POST /v1/challenges
POST /v1/attestations:verify
GET  /v1/configurations/{configRef}
```

The server creates a short-lived challenge record containing project, operation, provider mode, policy version, issuance state, expiry, submission limit, and random or provider-specific preparation material.

A canonical protected-operation representation includes:

- project ID;
- contract version;
- challenge ID;
- operation name;
- normalized operation arguments.

The operation is serialized canonically and hashed. For Google standard requests, the resulting digest is used as `requestHash`. The backend independently reconstructs and compares the digest after decoding the token.

Expected package, certificate digest, version, provider environment, and other application identity values are resolved from server-side project configuration. Client values are diagnostic only.

Successful verification atomically consumes the challenge. Expired, revoked, consumed, mismatched, or over-submitted challenges fail closed. Transient-provider retry behavior is explicit and audited.

User identity is not required for the trust-bootstrap decision.

## Consequences

### Positive

- replay and cross-operation substitution are testable;
- provider differences share one lifecycle;
- configuration delivery is authorized by a recorded decision;
- project identity cannot be redefined by the client;
- retries and duplicate submissions have explicit semantics.

### Negative

- adds persistence and an additional network exchange;
- canonicalization must be identical across SDK and backend languages;
- challenge-state availability becomes part of the verification path;
- clock-skew and idempotency rules require careful testing.

## Constraints

- challenge IDs are unguessable and not authorization by themselves;
- challenge consumption and successful decision issuance occur atomically;
- returned configuration references are scoped and expiring;
- raw provider evidence is minimized and never used as a reusable bearer credential;
- canonicalization is covered by golden vectors.

## Validation

This decision is complete when replay, double submission, wrong project, wrong operation, wrong package, wrong hash, expiration, revocation, provider retry, and cross-provider substitution tests all fail or behave according to the versioned contract.