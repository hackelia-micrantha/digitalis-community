# QART-02: Trust-Bootstrap Protocol

**Status:** Recommended and recorded by ADR-0004  
**Scope:** challenge issuance, request binding, replay resistance, project identity, and API contract

## Questions

1. How does Digitalis bind attestation evidence to a specific project and operation?
2. Should challenge issuance and evidence verification be one endpoint or separate operations?
3. Which values are server-authoritative?
4. How are replays, stale responses, retries, and duplicate submissions handled?
5. Is user identity required during trust bootstrap?
6. How should Google `requestHash` and Apple challenge material map to one provider-neutral protocol?

## Security invariant

An accepted attestation must prove that fresh provider evidence was generated for one Digitalis-issued, unexpired, unconsumed challenge, for an authorized project and operation. Client-provided identity values cannot redefine the expected application.

## Existing evidence

- Digitalis currently verifies a token directly during configuration delivery.
- No challenge record is issued, consumed, or expired.
- A response nonce is generated after verification and therefore does not bind the evidence.
- The implementation requires an `account_id` despite the RFC position that trust bootstrap should not require user identity.
- Themis performs freshness and request-detail checks, but incorrectly compares the decoded `requestHash` to the encrypted token and trusts a package supplied by the client.
- Google standard requests provide platform-managed replay protection, but Digitalis still needs operation and project binding and its own issuance/audit lifecycle.

## Alternatives

### A. One `POST /config` call containing provider token and client identities

**Advantages**

- minimal API;
- resembles the current implementation.

**Risks**

- no issued challenge or operation binding;
- configuration delivery and verification are inseparable;
- replay and retry semantics are ambiguous;
- project and application identity can become client-controlled;
- provider differences leak into the public API.

### B. Provider-specific challenge and verification endpoints

Examples: `/google/challenge`, `/google/verify`, `/apple/challenge`, `/apple/verify`.

**Advantages**

- provider behavior is explicit;
- easier initial implementation.

**Risks**

- duplicates protocol semantics;
- SDK callers must encode provider behavior;
- future provider additions expand the public surface;
- conformance becomes provider-specific.

### C. Provider-neutral Digitalis challenge and verification envelope

Digitalis issues one challenge object containing provider instructions. The SDK collects evidence and submits a versioned provider-neutral envelope. Provider adapters verify evidence against server-resolved project configuration and the stored challenge.

**Advantages**

- clear lifecycle and audit boundary;
- shared replay and retry semantics;
- server-authoritative project identity;
- provider adapters remain internal;
- supports future providers and capability negotiation.

**Risks**

- more records and endpoints;
- requires canonical operation hashing;
- mobile SDK must retain challenge context safely.

## Recommendation

Select alternative C.

### Endpoint direction

```text
POST /v1/challenges
POST /v1/attestations:verify
GET  /v1/configurations/{configRef}
```

Configuration is delivered only after a successful verification decision authorizes a specific configuration reference.

### Challenge record

A challenge should include:

- `challenge_id`;
- `contract_version`;
- `project_id` resolved by an authenticated or otherwise authorized project route;
- `operation`;
- provider and provider mode;
- random challenge bytes or provider preparation material;
- issue and expiry timestamps;
- maximum submissions;
- status: issued, consumed, expired, revoked;
- optional installation identifier or public-key reference;
- policy version expected for evaluation.

### Canonical operation binding

The protected request should be serialized canonically and hashed:

```text
project_id
contract_version
challenge_id
operation
normalized operation arguments
```

For Google standard requests, the digest becomes `requestHash`. The backend independently reconstructs the digest and compares it to decoded request details.

For Apple, the challenge and canonical request digest are incorporated into the client-data hash or assertion verification process according to the selected App Attest operation.

### Server-authoritative identity

The server resolves from project configuration:

- Android package name;
- allowed signing-certificate digests;
- minimum or allowed version codes;
- Google Cloud project and credentials;
- Apple team, bundle, environment, and key configuration;
- policy version;
- allowed provider mode.

The client may echo identity for diagnostics, but echoed identity never defines the expected value.

### Replay and retry behavior

- challenges are short-lived;
- successful verification atomically consumes the challenge;
- duplicate successful submissions return an idempotent result or a stable replay denial according to contract policy;
- expired, revoked, or mismatched challenges fail closed;
- provider-transient failures do not automatically consume a challenge unless policy requires it;
- submission counts and timestamps are audited;
- raw evidence retention is minimized and policy-controlled.

### User identity

User identity is not required for the device trust-bootstrap decision. Account association may occur later or be supplied as optional policy context after installation trust is established.

## Tradeoffs

- A challenge table and two-step flow add latency and persistence, but make the security boundary auditable.
- Google already provides replay protection for standard requests, but Digitalis challenges remain necessary for project, operation, and cross-provider semantics.
- Idempotent replay responses improve reliability but must not let an attacker use a response as a reusable authorization token; returned configuration references therefore remain scoped and expiring.

## Decisions

- **QART-0006:** Digitalis uses a provider-neutral issued-challenge lifecycle.
- **QART-0007:** Challenge and verification are separate operations from configuration retrieval.
- **QART-0008:** Project and application identity are resolved from server-side project configuration.
- **QART-0009:** Google `requestHash` is an independently reconstructed canonical operation digest, never the integrity token.
- **QART-0010:** Successful verification atomically consumes a short-lived challenge.
- **QART-0011:** User identity is not required in the critical trust-bootstrap path.

## Required tests

- challenge expiry;
- challenge revocation;
- replay after successful consumption;
- concurrent double submission;
- wrong project;
- wrong operation;
- wrong package, certificate, or version;
- incorrect request hash;
- malformed canonical input;
- provider transient retry;
- cross-provider challenge substitution;
- idempotency behavior;
- clock-skew boundaries.