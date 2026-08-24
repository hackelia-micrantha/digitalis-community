# RFC-0005 — Native Protection, Obfuscation, and Binary Validation

## Status
In Review

## Summary
Define the role, limits, and governance of obfuscated native binaries within the Attest SDK. Native protection is a defense-in-depth layer used to raise reverse-engineering cost around selected sensitive client-side operations, while preserving backend authority, release traceability, and operational supportability.

---

## Mental Model (authoritative)
Native protection is a **friction layer**, not a **trust anchor**.

It can:
- increase attacker cost
- reduce trivial patching or static inspection
- narrow some classes of SDK abuse

It cannot:
- replace backend verification
- make client trust decisions authoritative
- prevent a determined attacker from analyzing or patching code indefinitely

Accordingly, protected native components MUST remain subordinate to the system architecture defined in RFC-0001 through RFC-0004 and RFC-0006.

---

## Scope
This RFC defines:
- which responsibilities may be placed in protected native code
- which responsibilities must remain outside it
- binary identity and integrity validation expectations
- release/provenance requirements
- debugging, incident response, and supportability constraints
- policy boundaries to keep native protection disciplined

This RFC does not define:
- a specific obfuscation vendor or toolchain
- exact binary packing or anti-tamper implementation details
- app-store-specific legal interpretation

---

## Core Invariants (MUST hold)
1. **No Native Trust Authority**
   - Native protected code MUST NOT become the authoritative source of trust decisions.

2. **Backend Authority Preserved**
   - Allow/deny/degrade decisions MUST remain backend-authoritative.

3. **Defense in Depth Only**
   - Native obfuscation MUST be treated as an additional cost-imposition control, not a primary protection boundary.

4. **Validation Before Activation**
   - Protected native components SHOULD be identity/integrity validated before use.

5. **Release Traceability**
   - Every protected native binary MUST map to a known SDK release and build provenance record.

6. **Operational Recoverability**
   - Native protection choices MUST NOT make support, crash analysis, or incident response infeasible.

---

## Allowed Responsibility Boundaries
The following MAY be implemented in protected native code when justified:

### 1. Attestation Orchestration Helpers
Examples:
- challenge handling helpers
- provider interaction wrappers
- evidence packaging helpers

Constraint:
- raw evidence and policy semantics must still flow through the standardized SDK abstractions

### 2. Sensitive Local Crypto Helpers
Examples:
- signature verification helpers
- local package integrity checks
- key derivation helpers tied to platform secure storage usage

Constraint:
- crypto placement in native code does not remove the need for backend verification or config lifecycle controls

### 3. Config Validation Helpers
Examples:
- config package integrity verification
- version floor checks
- rollback guard helpers

Constraint:
- validation results MUST still map into the canonical outcome model from RFC-0006

### 4. Narrow Anti-Tamper Signals
Examples:
- binary self-checks
- bridge integrity checks
- environment heuristics

Constraint:
- native anti-tamper signals are advisory unless backend policy explicitly interprets them; they MUST NOT be treated as authoritative trust decisions

---

## Forbidden or Strongly Discouraged Uses
The following MUST NOT be delegated solely to protected native code:

### 1. Final Trust Decisions
Disallowed:
- authoritative allow/deny verdicts
- policy mode selection
- degraded mode authorization

### 2. Permanent Secret Reliance on Obfuscation Alone
Disallowed:
- shipping secrets whose only protection is binary concealment
- embedding long-lived trust anchors only behind obfuscation

### 3. Unbounded Self-Modifying or Review-Hostile Behavior
Disallowed / strongly discouraged:
- behavior likely to break maintainability, platform review, or debugging to an unacceptable degree

### 4. Hidden Compatibility Downgrades
Disallowed:
- silently bypassing normal SDK validation or telemetry because logic moved into native code
- native helpers MUST NOT bypass RFC-0004 validation lifecycle or RFC-0002 telemetry expectations

---

## Native Scope Recommendation
Recommended minimum scope:
- attestation helper logic
- local config/package integrity checks
- narrow crypto support functions

Recommended maximum scope:
- do not move all business logic or SDK control flow into protected native binaries

Reason:
- the more code moved into opaque native layers, the more the system accumulates support, portability, and governance debt

---

## Binary Validation Model
Protected native components SHOULD support identity/integrity validation before activation.

### Acceptable Validation Inputs
- expected binary measurement/hash
- code-signing identity
- signed manifest describing expected component set
- backend-approved protection profile

### Validation Timing
Validation MAY occur:
- at SDK initialization
- before native bridge activation
- before config validation/decryption helpers are invoked

### Requirements
- Validation failure MUST produce an explicit failure path
- Validation failure MUST map to a canonical startup outcome
- Validation status SHOULD be included in telemetry

---

## Release Provenance and Mapping
Every protected native binary MUST have traceable provenance.

### Required Associations
- SDK version
- native component version
- build identifier
- platform/ABI target
- protection profile identifier (if applicable)

### Provenance Expectations
The project SHOULD maintain:
- reproducible or as-reproducible-as-practical builds
- signed release artifacts
- artifact manifests
- symbol handling plan for crash analysis

### Reason
A protected binary without provenance becomes a supply-chain blind spot.

---

## Build and CI/CD Constraints
Native protection increases build complexity and therefore requires governance.

### Requirements
- protected binary builds MUST be auditable
- release packaging MUST verify expected native artifacts are present
- version mismatch between SDK wrapper and native component MUST fail build or release validation
- CI/CD SHOULD record artifact measurements and manifests

### Strong Recommendation
A protected native release should never be “special manual magic” that bypasses normal release controls.

---

## Native Bridge Boundary
The interface between managed/runtime code and native protected code MUST be deliberately narrow.

### Requirements
- inputs and outputs SHOULD be typed and minimal
- secrets SHOULD NOT traverse the bridge unless necessary
- bridge failures MUST be explicit and telemetry-visible
- native helper functions SHOULD avoid broad ambient access to app state

### Reason
The bridge is a practical attack and maintenance boundary.

---

## Failure Handling
Native protection failures MUST not create undefined behavior. Native-path failure outcome mapping is owned by RFC-0006.

### Example Failure Classes
- native component missing
- native component validation failure
- bridge invocation failure
- unsupported ABI/platform
- integrity helper failure
- anti-tamper signal triggered

### Behavior
These MUST map into RFC-0006 canonical outcomes, typically:
- `DENY_INTEGRITY`
- `UNSUPPORTED_ENVIRONMENT`
- `RETRYABLE_FAILURE` only when failure is plausibly transient

---

## Telemetry & Audit Events (Required)
The SDK MUST emit structured events for:
- native component loaded / not loaded
- native validation success/failure
- bridge invocation failures
- protection profile identifier
- component version and measurement where safe to report
- fallback from native helper path to non-native path if policy permits

Recommended fields:
- timestamp
- sdk_version
- native_component_version
- platform
- abi
- protection_profile
- validation_status
- outcome_code

---

## Debugging and Incident Response
Native protection reduces observability unless explicitly planned for.

### Requirements
- the project MUST maintain symbolication/support procedures appropriate to the build strategy
- crash reporting MUST preserve enough context to distinguish native validation vs runtime faults
- incident response MUST be able to identify which protected binary version was deployed

### Strong Recommendation
Do not choose protection techniques that make your own responders less capable than your attackers.

---

## Platform and Distribution Constraints
Because the SDK targets app-store distributed mobile applications:
- techniques that materially threaten review acceptance, stability, or maintainability SHOULD be avoided
- protection measures SHOULD remain compatible with standard platform signing, packaging, and update flows
- native protection strategy SHOULD assume normal store release/update cycles, even if backend-delivered config evolves faster

---

## Runtime Invariants (Code-Level)

```ts
assert(backend_is_authoritative == true)
assert(native_allow_decision == undefined)
assert(native_validation_failed == true -> protected_features_enabled == false)
assert(native_component_version != null -> sdk_release_mapping_exists == true)
assert(native_bridge_failure == true -> failure_outcome != "ALLOW")
```

---

## Testing Expectations
A conforming implementation SHOULD test:
- expected native component present/absent paths
- validation success/failure paths
- ABI/platform mismatch handling
- bridge error propagation
- release manifest verification
- telemetry generation for native-specific failures
- symbolication and operational support workflows

---

## Security Considerations
- Obfuscation is useful primarily as attacker-cost amplification, not as a standalone control.
- Binary validation is valuable, but if the validation logic itself is weakly governed, it can create false confidence.
- Native code can reduce obvious static exposure while increasing memory corruption, portability, and QA risk.
- Embedded secrets protected only by binary opacity should be assumed recoverable by a capable adversary.
- Anti-tamper signals are most valuable when combined with backend policy and telemetry, not when used as isolated client-side verdicts.

---

## Open Questions
- Whether native validation should be mandatory in strict policy mode or merely recommended
- Whether protection profiles should be standardized across projects/backends
- Which functions are sufficiently security-sensitive to justify native placement versus remaining in managed code

---

## Consequences
Pros:
- raises reverse-engineering and patching cost
- narrows exposure of selected sensitive helper logic
- adds optional binary identity checks and release discipline
- complements attestation/config validation without replacing them

Cons:
- higher CI/CD and release complexity
- harder debugging and incident response if not planned carefully
- increased platform-specific maintenance burden
- risk of over-trusting a defense-in-depth layer

---

## Dependencies
- RFC-0001 defines backend-authoritative trust bootstrap and activation invariants
- RFC-0003 constrains how attestation provider logic may be wrapped natively
- RFC-0004 constrains config validation, rollback, and secret-handling behavior
- RFC-0006 defines canonical failure outcomes for native-path failures

