# Digitalis Architecture Decision Records

ADRs are the authoritative record of accepted Digitalis architecture decisions.

| ADR | Decision | Status |
|---|---|---|
| [ADR-0001](0001-android-play-integrity-cloudflare-first.md) | Android, Play Integrity, and the Digitalis Cloudflare Worker form the first vertical slice | Accepted |
| [ADR-0002](0002-consolidate-themis-google-provider.md) | Rebuild and rebrand Themis as the Digitalis Cloudflare service | Accepted |
| [ADR-0003](0003-separate-provider-evidence-from-policy.md) | Separate provider evidence from deterministic policy and outcomes | Accepted |
| [ADR-0004](0004-issued-challenge-and-request-binding.md) | Use issued challenges and canonical request binding | Accepted |
| [ADR-0005](0005-signed-configuration-and-kms.md) | Use signed canonical configuration with KMS-backed key custody | Accepted |
| [ADR-0006](0006-repository-and-publication-boundaries.md) | Separate engineering and public publication repository ownership | Accepted |
| [ADR-0007](0007-sqlite-durable-object-trust-authority.md) | Use SQLite-backed Durable Objects as the v1 trust authority | Proposed |

## Status values

- **Proposed:** under review and not authoritative;
- **Accepted:** binding for implementation;
- **Superseded:** replaced by a later ADR;
- **Deprecated:** retained for history but must not be used for new work.

A superseding ADR must identify the replaced ADR and affected QART decision IDs.