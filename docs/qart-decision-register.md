# Digitalis QART Decision Register

This register maps accepted QART recommendations to binding Architecture Decision Records and implementation work.

| ID | Decision | Source | ADR | Status |
|---|---|---|---|---|
| QART-0001 | `digitalis` is the authoritative engineering and product repository | QART-01 | ADR-0006 | Accepted |
| QART-0002 | `digitalis-community` is the public publication boundary | QART-01 | ADR-0006 | Accepted |
| QART-0003 | Themis is the predecessor Digitalis Cloudflare service and will be rebuilt and rebranded | QART-01 | ADR-0002 | Accepted |
| QART-0004 | Google verification is implemented once as a shared provider package | QART-01 | ADR-0002 | Accepted |
| QART-0005 | Public publication is one-way and provenance-bearing | QART-01 | ADR-0006 | Accepted |
| QART-0006 | Use a provider-neutral issued-challenge lifecycle | QART-02 | ADR-0004 | Accepted |
| QART-0007 | Separate challenge, verification, and configuration retrieval | QART-02 | ADR-0004 | Accepted |
| QART-0008 | Resolve application identity from server-side project configuration | QART-02 | ADR-0004 | Accepted |
| QART-0009 | Google `requestHash` is a canonical operation digest | QART-02 | ADR-0004 | Accepted |
| QART-0010 | Successful verification atomically consumes the challenge | QART-02 | ADR-0004 | Accepted |
| QART-0011 | User identity is not required for trust bootstrap | QART-02 | ADR-0004 | Accepted |
| QART-0012 | Provider adapters return structured authenticated evidence | QART-03 | ADR-0003 | Accepted |
| QART-0013 | Policy is deterministic, versioned, and provider-independent | QART-03 | ADR-0003 | Accepted |
| QART-0014 | Canonical outcomes are shared across providers and SDKs | QART-03 | ADR-0003 | Accepted |
| QART-0015 | Google basic integrity is not unconditional verification | QART-03 | ADR-0003 | Accepted |
| QART-0016 | Missing or unevaluated claims never become positive evidence | QART-03 | ADR-0003 | Accepted |
| QART-0017 | Remediation uses Digitalis identifiers mapped by native SDKs | QART-03 | ADR-0003 | Accepted |
| QART-0018 | Reason codes live in one executable cross-language registry | QART-03 | ADR-0003 | Accepted |
| QART-0019 | v1 uses signed canonical configuration without shared app-layer encryption | QART-04 | ADR-0005 | Accepted |
| QART-0020 | Private signing keys remain in managed key custody | QART-04 | ADR-0005 | Accepted |
| QART-0021 | PostgreSQL stores key references and public metadata only | QART-04 | ADR-0005 | Accepted |
| QART-0022 | One configuration and one issuing key are active per project/environment | QART-04 | ADR-0005 | Accepted |
| QART-0023 | Expiry, revocation, and rollback are enforced before issuance and activation | QART-04 | ADR-0005 | Accepted |
| QART-0024 | SDK configuration activation is atomic with a protected rollback floor | QART-04 | ADR-0005 | Accepted |
| QART-0025 | Per-install encrypted secret provisioning is deferred | QART-04 | ADR-0005 | Accepted |
| QART-0026 | First platform slice is Android plus Google Play Integrity | QART-05 | ADR-0001 | Accepted |
| QART-0027 | Cloudflare Workers is the primary first-party hosted Digitalis runtime and continues the Themis lineage | QART-05 | ADR-0001 | Accepted |
| QART-0028 | Protocol, provider, policy, and canonical serialization packages remain runtime-neutral | QART-05 | ADR-0001 | Accepted |
| QART-0029 | Native Android precedes Apple, KMP, and React Native | QART-05 | ADR-0001 | Accepted |
| QART-0030 | First milestone requires real-provider and real-binary integration | QART-05 | ADR-0001 | Accepted |
| QART-0031 | CI, conformance, SBOM, and provenance are release requirements | QART-05 | ADR-0001 | Accepted |
| QART-0032 | Deferred capabilities or a change of primary hosted runtime require separate QART and ADR promotion | QART-05 | ADR-0001 | Accepted |

## Change rules

- An accepted decision may be changed only by a superseding ADR.
- The superseding ADR must cite the affected QART IDs and explain which evidence changed.
- Implementation issues and pull requests should cite all applicable IDs.
- A decision cannot be marked implemented until its negative tests and required evidence are merged.
