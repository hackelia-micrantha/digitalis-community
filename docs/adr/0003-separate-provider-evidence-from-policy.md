# ADR-0003: Separate Provider Evidence from Policy and Outcomes

**Status:** Accepted  
**Date:** 2026-07-26  
**QART decisions:** QART-0012 through QART-0018

## Context

Current implementations flatten provider results into booleans or combine provider verification with host actions. This hides assurance differences, duplicates policy, makes missing claims ambiguous, and prevents deterministic cross-provider behavior.

Google Play Integrity alone can return materially different application, device, account, environment, and activity claims. Apple providers expose different but similarly non-equivalent evidence. Treating all of this as `verified: true` is unsafe.

## Decision

Provider adapters authenticate provider evidence and return structured normalized evidence plus namespaced provider claims.

A separate deterministic, versioned Digitalis policy engine evaluates that evidence and returns the canonical outcome:

- `ALLOW`;
- `ALLOW_DEGRADED`;
- `RETRYABLE_FAILURE`;
- `DENY_POLICY`;
- `DENY_INTEGRITY`;
- `UNSUPPORTED_ENVIRONMENT`.

Every outcome includes a stable reason code, policy version, evidence digest, expiry, retry metadata, optional remediation identifier, and optional authorized configuration reference.

Missing or unevaluated provider claims never become positive evidence.

Google `MEETS_BASIC_INTEGRITY` is not unconditional success. Its treatment is explicitly selected by project policy.

Remediation uses Digitalis names. Native SDKs translate those names to supported platform dialogs or user experiences.

## Consequences

### Positive

- decisions are explainable and replayable;
- policy changes do not require provider rewrites;
- provider-native assurance differences are preserved;
- cross-language SDK behavior can be tested from shared fixtures;
- unknown provider fields do not silently grant access.

### Negative

- schemas and fixtures are larger;
- reason and remediation registries require lifecycle governance;
- normalization must avoid implying equivalence where none exists;
- policy-version migration becomes an explicit operational concern.

## Constraints

- provider packages cannot import host application behavior;
- the policy engine is side-effect free for a given input and version;
- policy fixtures include all positive and negative result classes;
- provider-native claims retained for audit are minimized and subject to retention policy;
- changing an existing reason code's meaning requires a contract version change.

## Validation

This decision is complete when provider tests can run without the policy engine, policy fixtures can run without live provider calls, TypeScript and Kotlin produce identical outcomes and reasons, and no provider code directly authorizes configuration or protected features.