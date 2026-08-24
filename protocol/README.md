# Digitalis Protocol v1

This directory is the authoritative executable contract boundary for the Digitalis v1 trust-bootstrap protocol.

## Version

The only supported contract version in this slice is:

```text
digitalis.v1
```

Unknown versions and unknown critical request fields are rejected. User account identity and policy selection are intentionally absent from the client challenge contract.

## Operations

The first protocol operations are:

```text
POST /api/v1/challenges
POST /api/v1/attestations:verify
GET  /api/v1/configurations/{configRef}
```

The configuration-reference endpoint remains a documented contract stub until the KMS-backed signed-configuration slice is implemented.

## Server-authoritative project scope

`project_id` is a selector for server-owned configuration, not permission for the client to define project identity. Before issuing a challenge, the server resolves a configured project profile containing:

- the active policy version;
- allowed provider modes;
- allowed protected operations.

The request cannot provide `policy_version`. Unknown projects, disallowed providers, and disallowed operations fail closed.

This executable slice loads explicit profiles from `DIGITALIS_CHALLENGE_PROFILES_JSON`. An absent profile list allows no challenge issuance. The process-local profile source is refused when `NODE_ENV=production`; durable authenticated project configuration moves to PostgreSQL in the next #11 slice.

Example test or development profile:

```json
[
  {
    "project_id": "11111111-1111-4111-8111-111111111111",
    "policy_version": "policy-1",
    "allowed_providers": ["google_play_integrity"],
    "allowed_operations": ["configuration.bootstrap"]
  }
]
```

## Canonical request binding

The protected operation contains exactly:

- `project_id`;
- `contract_version`;
- `challenge_id`;
- `operation`;
- `operation_arguments`.

`operation_arguments` accepts JSON values with these restrictions:

- numbers must be JavaScript-safe integers;
- object keys are ordered by Unicode code point;
- strings and keys must be Unicode scalar sequences;
- unpaired UTF-16 surrogates are rejected;
- no `undefined`, floating-point, NaN, or infinity values;
- arrays preserve input order;
- strings use JSON escaping and UTF-8 encoding.

The canonical UTF-8 bytes are hashed with SHA-256 and encoded as exactly 43 unpadded base64url characters. Decode-equivalent non-canonical aliases are rejected. For Google Play Integrity standard requests, this value is the `requestHash`.

Shared vectors are in `golden/canonical-request-vectors.json`. The TypeScript backend implementation and the standalone Kotlin verifier must produce the same bytes and hashes. The vectors include nested values, supplementary Unicode key ordering, and JSON escaping.

### Conformance verification

Run the TypeScript suite from `backend/`:

```bash
pnpm exec jest --runInBand
```

Run the standalone Kotlin verifier from the repository root:

```bash
kotlinc -script protocol/v1/kotlin/CanonicalRequestVectors.main.kts
```

Both implementations must pass before canonical serialization, vector, or request-hash changes can merge.

## Provider evidence binding

A provider adapter cannot return only a boolean trust result. A successful adapter result must also return the request hash decoded or reconstructed from the provider evidence. The challenge service compares that value with the stored canonical request hash before consuming the challenge.

The production adapter in this slice always returns `BOUND_PROVIDER_VERIFICATION_NOT_IMPLEMENTED`. Positive bound verification belongs to the corrected provider work in #12.

## Lifecycle semantics in slice 1

- challenge IDs are random UUIDv4 values;
- default lifetime is 120 seconds with at most five seconds of server-side clock skew;
- default submission limit is three;
- server-configured project, policy, operation, and provider scope are bound;
- challenge state is rechecked after provider work so an expired or concurrently consumed challenge cannot be authorized;
- successful bound provider verification consumes the challenge atomically within the repository implementation;
- rejected, thrown-transient, and explicit transient provider submissions increment the bounded submission count;
- consumed, expired, revoked, mismatched, and over-submitted challenges fail closed;
- raw provider evidence is never returned as a reusable credential; responses contain only a one-way evidence reference.

The first repository implementation is process-local and exists to make the contract and state machine executable. PostgreSQL persistence, transaction rollback tests, durable audit records, authenticated project routing, and multi-instance atomicity are the next #11 slice.
