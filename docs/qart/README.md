# Digitalis v1 QART Analysis

QART means **Questions, Alternatives, Recommendations, Tradeoffs**.

A QART slice is a bounded pre-implementation analysis artifact. It is used where the project has a clear problem but still needs explicit comparison before implementation is authorized.

## Slice lifecycle

```text
Open questions
  -> alternatives and evidence
  -> recommendation
  -> tradeoffs and rejected options
  -> accepted decision IDs
  -> ADRs
  -> implementation issues and pull requests
```

A QART recommendation is not authoritative by itself. Once accepted, the binding decision is recorded as an ADR and listed in the project decision register.

## v1 slices

| Slice | Scope | Primary decisions |
|---|---|---|
| [QART-01](01-repository-and-product-boundaries.md) | Repository, product, and Themis migration boundaries | Ownership, consolidation, publication |
| [QART-02](02-trust-bootstrap-protocol.md) | Challenge lifecycle, request binding, endpoint contract | Replay protection, identity binding, API split |
| [QART-03](03-provider-policy-and-outcomes.md) | Provider evidence, policy, outcomes, remediation | Normalization, tier handling, fail-closed behavior |
| [QART-04](04-configuration-and-key-lifecycle.md) | Configuration integrity, expiry, rollback, keys | Signed configuration, KMS, activation lifecycle |
| [QART-05](05-delivery-sdk-and-assurance.md) | Deployment, SDK order, CI, conformance, release | Android-first slice, Cloudflare adapter, assurance gates |
| [QART-06](06-durable-worker-authority.md) | Durable trust authority for the first-party Worker | Project/environment authority, SQLite-backed Durable Objects, transaction boundary |

## Review requirements

Each slice must:

- state the security invariant;
- identify existing implementation evidence;
- compare at least two credible alternatives;
- record rejected approaches;
- define implementation consequences;
- identify tests needed to validate the decision;
- assign stable decision IDs;
- point to the ADRs that bind accepted decisions.

## Traceability

Implementation work should include the relevant QART IDs in issue and pull request descriptions. Security-sensitive decisions must not be changed only in code; superseding analysis and ADRs are required.