# QART-03: Provider Evidence, Policy, and Outcomes

**Status:** Recommended and recorded by ADR-0003  
**Scope:** provider adapters, normalized evidence, deterministic policy, canonical outcomes, and remediation

## Questions

1. What is the boundary between provider verification and Digitalis policy?
2. Should provider results be represented as a boolean, risk score, or structured evidence?
3. How should Google integrity tiers and optional signals affect outcomes?
4. Which component decides host actions such as retry, degrade, remediation, or feature denial?
5. What happens when a provider omits, cannot evaluate, or adds a verdict field?
6. How are reason codes kept stable across backend and SDK languages?

## Security invariant

Provider adapters authenticate evidence and return facts. A versioned deterministic policy evaluates those facts and produces the only canonical Digitalis outcome. Provider code must not directly authorize features or instruct the host application to terminate.

## Existing evidence

- The current Digitalis provider interface returns `verified`, confidence, and a device hash.
- The Digitalis Google provider can return verified after logging an invalid app-recognition verdict.
- Themis correctly rejects an unrecognized application but treats basic, device, and strong integrity as successful variants.
- Themis also produces host actions such as `stopApp`, refresh, and licensing dialog suggestions.
- RFC-0003 proposes a richer provider lifecycle and RFC-0006 defines canonical startup outcomes.

## Alternatives

### A. Boolean provider verification

Provider returns `true` or `false`; caller decides behavior.

**Advantages**

- simple API;
- easy to test superficially.

**Risks**

- destroys assurance detail;
- provider-specific policy becomes hidden inside adapters;
- missing and unevaluated claims are ambiguous;
- policy changes require provider-code changes;
- audit evidence cannot explain decisions.

### B. Provider-specific policy in each adapter

Each adapter returns a Digitalis outcome and remediation.

**Advantages**

- provider expertise remains near provider code;
- quick implementation for one platform.

**Risks**

- inconsistent outcomes across providers;
- duplicated policy;
- difficult conformance;
- new provider versions silently change application behavior;
- host actions leak into security-verification code.

### C. Structured normalized evidence plus a separate deterministic policy engine

Each provider verifies provider-specific cryptography and identities, then emits a normalized envelope preserving provider-native claims. The policy engine evaluates evidence against a versioned project policy and emits a canonical outcome, reason code, TTL, retry classification, remediation, and configuration authorization.

**Advantages**

- auditable decisions;
- explicit assurance tiers;
- provider and policy tests can be isolated;
- policy versions can be rolled out independently;
- supports multiple SDKs and customer policies;
- unknown fields can be preserved without granting access.

**Risks**

- larger schema;
- requires a stable reason registry;
- normalization must avoid false equivalence between providers.

## Recommendation

Select alternative C.

### Provider adapter responsibilities

A provider adapter may:

- prepare provider-specific instructions;
- decode and authenticate provider evidence;
- verify challenge and request binding;
- verify application identity against server configuration;
- classify provider errors;
- normalize known facts;
- preserve relevant provider-native claims;
- report provider and capability versions.

It must not:

- return final `ALLOW` or `DENY` decisions;
- choose configuration versions;
- decide host application exit behavior;
- collapse unevaluated claims into success;
- reinterpret project policy.

### Normalized evidence envelope

```text
contract_version
provider
provider_mode
provider_api_version
challenge_id
project_id
observed_at
request_binding
application_identity
installation_identity or key reference
device_assurance labels
account or licensing signals
environment and access-risk signals
provider errors and evaluation status
raw-claim digest
```

Provider-native fields may be retained in a namespaced extension object, subject to privacy and retention policy.

### Canonical outcomes

The v1 registry is:

- `ALLOW`;
- `ALLOW_DEGRADED`;
- `RETRYABLE_FAILURE`;
- `DENY_POLICY`;
- `DENY_INTEGRITY`;
- `UNSUPPORTED_ENVIRONMENT`.

Each decision includes:

- stable reason code;
- policy version;
- evidence digest;
- issued and expiry times;
- retry metadata;
- optional remediation identifier;
- optional authorized configuration reference.

### Google tier guidance

Provider facts:

- `MEETS_STRONG_INTEGRITY`;
- `MEETS_DEVICE_INTEGRITY`;
- `MEETS_BASIC_INTEGRITY`;
- no recognized device label;
- unevaluated or provider-error state.

Default v1 policy direction:

- strong: eligible for `ALLOW`;
- device: eligible for `ALLOW` according to project policy;
- basic only: `ALLOW_DEGRADED` or `DENY_POLICY`, never unconditional success;
- no label: `DENY_INTEGRITY`;
- provider transient error: `RETRYABLE_FAILURE`;
- unsupported platform or provider mode: `UNSUPPORTED_ENVIRONMENT`.

These defaults remain policy, not provider behavior.

### Remediation

The policy engine returns a named Digitalis remediation such as:

- refresh provider state;
- obtain Play license;
- update Play services;
- update application;
- retry later;
- contact support.

The Android SDK maps a named remediation to the applicable Play Integrity dialog constant. Numeric platform values do not cross the Digitalis public contract.

## Tradeoffs

- Preserving provider-native detail increases payload and schema complexity, but prevents normalization from erasing material evidence.
- A stable reason registry slows ad hoc changes, but makes telemetry and SDK behavior predictable.
- `ALLOW_DEGRADED` is useful but risky; v1 may support the outcome contract while enabling it only for explicitly configured low-risk features.

## Decisions

- **QART-0012:** Provider adapters return authenticated structured evidence, never final feature authorization.
- **QART-0013:** Policy evaluation is deterministic, versioned, and isolated from provider integrations.
- **QART-0014:** Canonical outcomes are shared across providers and SDKs.
- **QART-0015:** Google basic integrity is not unconditional verification.
- **QART-0016:** Missing or unevaluated provider claims never become positive evidence.
- **QART-0017:** Remediation is represented by named Digitalis identifiers and mapped to native constants in platform SDKs.
- **QART-0018:** Reason codes are defined in one executable registry with cross-language fixtures.

## Required tests

- every Google tier and tier combination;
- `PLAY_RECOGNIZED` and non-recognized applications;
- certificate and version mismatches;
- omitted and unknown claims;
- provider transient and permanent errors;
- deterministic replay of policy fixtures;
- policy-version differences;
- reason-code compatibility across TypeScript and Kotlin;
- remediation mapping;
- evidence digest stability;
- fail-closed behavior for malformed normalized evidence.