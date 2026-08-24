# RFC-0006 — Startup Policy, Outcome Model, and Failure Handling

## Status
In Review

## Summary
Define the canonical startup outcome model for the Attest SDK, including verdict semantics, retry behavior, degraded mode rules, blocking behavior, timed hard exit policy, and cross-RFC mapping of failures into deterministic client actions.

---

## Mental Model (authoritative)
Startup policy is the **decision layer** that converts trust/bootstrap results into application behavior.

- RFC-0001 defines the state machine.
- RFC-0002 defines backend authority.
- RFC-0003 defines attestation collection/error classes.
- RFC-0004 defines config validity and activation rules.
- This RFC defines what the SDK must **do** when those components succeed or fail.

The goal is deterministic, testable behavior under success, denial, expiry, partial failure, and degraded conditions.

---

## Scope
This RFC defines:
- canonical startup outcomes
- outcome-to-behavior mapping
- retry policy
- degraded mode policy
- blocking screen policy
- timed hard exit policy
- telemetry requirements for outcome decisions
- mapping rules from upstream failure classes

This RFC does not define:
- attestation provider internals
- backend verification logic
- config package cryptographic details

---

## Core Invariants (MUST hold)
1. **Protected Features Default Off**
   - Protected capabilities MUST remain disabled unless the SDK reaches an allowed trusted state.

2. **Deterministic Outcome Mapping**
   - Equivalent upstream conditions MUST produce equivalent startup outcomes.

3. **No Silent Degradation**
   - Degraded mode MUST be explicit, policy-controlled, and observable.

4. **Failure Is a Security State**
   - Startup failure MUST be treated as a trust decision outcome, not merely a UX problem.

5. **Hard Exit Must Be Deliberate**
   - Timed exit behavior MUST be policy-driven and auditable.

---

## Canonical Outcomes
The SDK MUST normalize all startup results into one of the following canonical outcomes.

### 1. `ALLOW`
Meaning:
- Trust bootstrap succeeded
- Backend authorized operation
- Valid config active (if required)

Behavior:
- Protected features enabled
- App continues normally

`ALLOW` is the **only** outcome that enables protected features. No other outcome, including `ALLOW_DEGRADED`, permits protected-feature access.

### 2. `ALLOW_DEGRADED`
Meaning:
- Trust bootstrap partially succeeded or policy intentionally limits capabilities
- Only explicitly permitted non-sensitive behavior may continue

Behavior:
- Protected features remain disabled
- Only policy-approved degraded features may run
- User-facing blocking/notice MAY be shown depending on product policy

`ALLOW_DEGRADED` is currently a pure outcome in this RFC. It may later correspond to a formal distinct state in RFC-0001 if the architecture evolves to model degraded operation as an explicit state rather than only an outcome. Until such promotion occurs, it remains an outcome only.

### 3. `RETRYABLE_FAILURE`
Meaning:
- A temporary failure occurred and retry may reasonably succeed

Examples:
- transient backend unavailability
- timeout during attestation collection
- network interruption before config fetch

Behavior:
- Protected features disabled
- Retry permitted according to policy
- Blocking state entered unless local product policy explicitly allows a holding pattern

### 4. `DENY_POLICY`
Meaning:
- Backend policy denied trust/bootstrap

Examples:
- attestation valid but disallowed by policy
- environment risk level too high
- unsupported capability profile for project rules

Behavior:
- Protected features disabled
- Blocking state entered
- Timed hard exit SHOULD be available in strict mode

### 5. `DENY_INTEGRITY`
Meaning:
- Integrity-related failure makes continued trusted operation unsafe

Examples:
- malformed evidence after collection
- invalid config signature
- rollback rejection
- revocation of active config

Behavior:
- Protected features disabled
- Blocking state entered immediately
- Timed hard exit SHOULD be enabled by default in strict mode

### 6. `UNSUPPORTED_ENVIRONMENT`
Meaning:
- Current platform/runtime/provider conditions do not support required operation

Examples:
- provider unavailable on target environment
- required secure storage unavailable when policy forbids fallback
- unsupported SDK/backend contract version

Behavior:
- Protected features disabled
- Blocking state entered
- Retry MAY be suppressed if retry cannot change result

---

## Default Policy Recommendations
These are normative recommendations and SHOULD be the default unless backend policy overrides them.

### Baseline Defaults
- Default blocking behavior: **enabled**
- Default timed hard exit: **enabled for deny/integrity outcomes**
- Default exit delay: **short, user-visible timeout**
- Default retry policy: **limited exponential backoff for retryable failures**
- Default degraded mode: **disabled unless explicitly authorized**

### Rationale
This aligns with the project’s security posture that a running app remains part of the attack surface.

---

## Behavior Matrix

| Outcome | Protected Features | Blocking UI | Retry | Timed Hard Exit | Degraded Operation |
|---|---|---:|---:|---:|---:|
| `ALLOW` | Enabled | No | No | No | No |
| `ALLOW_DEGRADED` | Disabled | Optional / Policy | Optional | Optional | Yes |
| `RETRYABLE_FAILURE` | Disabled | Yes | Yes | Optional | No by default |
| `DENY_POLICY` | Disabled | Yes | No by default | Yes (recommended) | No by default |
| `DENY_INTEGRITY` | Disabled | Yes | No by default | Yes (recommended) | No |
| `UNSUPPORTED_ENVIRONMENT` | Disabled | Yes | Usually No | Optional | No by default |

---

## Blocking State Policy
Blocking state is the default containment behavior when trusted startup cannot complete.

### Requirements
- Blocking state MUST prevent access to protected features.
- Blocking state MUST communicate that startup could not complete.
- Blocking state MUST be compatible with timed exit policy where configured.
- Blocking state MUST remain observable to telemetry and app logic.

### UX Guidance
The exact UI belongs to the host app/product, but the SDK SHOULD be able to signal:
- blocking reason code
- retry allowed or not
- exit countdown if enabled

---

## Timed Hard Exit Policy

### Purpose
Hard exit exists to reduce residual attack surface when the app cannot enter a trusted operating state.

### Requirements
- Timed hard exit MUST be policy-controlled.
- Timed hard exit SHOULD be enabled by default for `DENY_INTEGRITY`.
- Timed hard exit SHOULD be enabled by default for `DENY_POLICY` in strict deployments.
- Exit behavior MUST be telemetry-visible and auditable.

### Constraints
- Exit MUST NOT be triggered silently without an outcome record.
- Exit countdown SHOULD be user-visible where feasible.
- Exit path MUST avoid leaving protected state active.

---

## Retry Policy

### Retryable Classes
Only temporary, plausibly recoverable failures SHOULD map to `RETRYABLE_FAILURE`.

Examples:
- network interruption
- transient timeout
- backend 5xx / temporary unavailability

### Non-Retryable by Default
The following SHOULD NOT automatically retry by default:
- policy denials
- integrity failures
- unsupported environment results
- rollback rejection
- revocation-triggered invalidation

### Backoff Guidance
The SDK SHOULD support:
- bounded retries
- exponential backoff
- jitter
- user-visible retry state if blocking UI is present

### Default Retry Budget Guidance
The default retry budget SHOULD be:
- Maximum retry attempts: **3** for `RETRYABLE_FAILURE`
- Initial backoff: **1 second**
- Maximum backoff: **30 seconds**
- Jitter: **±25%** of computed backoff

These defaults are guidance only. Final values remain backend-configurable and may be overridden by backend policy. Implementations MUST document any deviation from these defaults.

---

## Degraded Mode Policy

### Default
Degraded mode is **disabled by default**.

### Enablement Rule
Degraded mode MAY be entered only when backend policy explicitly allows it.

### Constraints
- Only explicitly approved non-sensitive features may run.
- Protected storage, secrets, and protected network flows MUST remain disabled.
- Degraded mode MUST be observable in SDK state and telemetry.
- Degraded mode MUST NOT silently become normal operation.

### Examples of Acceptable Degraded Behavior
- limited informational UI
- onboarding/holding screen
- low-risk local-only features

### Examples of Unacceptable Degraded Behavior
- access to protected endpoints
- unlocking protected config-driven functionality
- continued use after TTL expiry without policy support

---

## Mapping Rules from Upstream Failures

### From RFC-0003 (attestation/provider)
- `UNSUPPORTED_PROVIDER` -> `UNSUPPORTED_ENVIRONMENT`
- `PROVIDER_UNAVAILABLE` -> `RETRYABLE_FAILURE` or `UNSUPPORTED_ENVIRONMENT` based on policy/context
- `CHALLENGE_REJECTED` -> `DENY_POLICY` or `DENY_INTEGRITY` depending on root cause classification
- `EVIDENCE_COLLECTION_FAILED` -> `RETRYABLE_FAILURE`
- `EVIDENCE_MALFORMED` -> `DENY_INTEGRITY`
- `LOCAL_NORMALIZATION_FAILED` -> `DENY_INTEGRITY` or `RETRYABLE_FAILURE` depending on determinism
- `TIMEOUT` -> `RETRYABLE_FAILURE`

### From RFC-0002 (backend)
- backend policy deny -> `DENY_POLICY`
- backend contract/version incompatibility -> `UNSUPPORTED_ENVIRONMENT`
- backend unavailable -> `RETRYABLE_FAILURE`
- no-silent-downgrade capability mismatch -> `UNSUPPORTED_ENVIRONMENT` or `DENY_POLICY`

### From RFC-0004 (config/storage)
- integrity validation failure -> `DENY_INTEGRITY`
- rollback rejection -> `DENY_INTEGRITY`
- secure storage unavailable with fallback forbidden -> `UNSUPPORTED_ENVIRONMENT`
- TTL expiry requiring revalidation with backend unreachable -> `RETRYABLE_FAILURE`
- revocation of active config -> `DENY_INTEGRITY`

---

## State Integration (RFC-0001 alignment)
Canonical outcomes MUST map to trust/bootstrap states consistently.

### Example State Implications
- `ALLOW` -> `TRUSTED_ACTIVE`
- `ALLOW_DEGRADED` -> degraded operational state (logical, even if not formalized as a distinct state in RFC-0001 yet)
- `RETRYABLE_FAILURE` -> non-trusted blocking/retry state
- `DENY_*` -> denied terminal state
- `UNSUPPORTED_ENVIRONMENT` -> terminal unsupported state

This RFC assumes the SDK may expose outcome separately from internal detailed state.

---

## Minimal API Expectations
The SDK SHOULD expose startup decision information such that the host application can render correct containment UX.

Example logical types:

```ts
type StartupOutcome =
  | "ALLOW"
  | "ALLOW_DEGRADED"
  | "RETRYABLE_FAILURE"
  | "DENY_POLICY"
  | "DENY_INTEGRITY"
  | "UNSUPPORTED_ENVIRONMENT"

interface StartupResult {
  outcome: StartupOutcome
  reasonCode: string
  retryAllowed: boolean
  exitScheduled: boolean
  exitAfterMs?: number
}
```

---

## Runtime Invariants (Code-Level)

```ts
assert(startupOutcome != null)
assert(startupOutcome == "ALLOW" -> protected_features_enabled == true)
assert(startupOutcome != "ALLOW" -> protected_features_enabled == false)
assert(startupOutcome == "ALLOW_DEGRADED" -> protected_features_enabled == false)
assert(exitScheduled == true -> startupOutcome != "ALLOW")
assert(degradedMode == true -> startupOutcome == "ALLOW_DEGRADED")
```

---

## Telemetry & Audit Events (Required)
The SDK MUST emit structured events for:
- outcome determination
- blocking state entry
- retry scheduling and retry exhaustion
- degraded mode entry/exit
- hard exit scheduling
- hard exit execution
- reason code mapping from upstream failures

Recommended fields:
- timestamp
- startup_outcome
- reason_code
- retry_allowed
- exit_scheduled
- exit_after_ms
- sdk_version
- config_version if present
- provider_id if present
- backend_id if present

---

## Testing Expectations
A conforming implementation SHOULD test:
- all canonical outcomes
- outcome mapping determinism
- retry backoff boundaries
- degraded mode gating
- hard exit scheduling behavior
- TTL expiry transitions
- no-protected-feature access in non-allow states

---

## Security Considerations
- Overusing `RETRYABLE_FAILURE` can accidentally create indefinite insecure holding states.
- Degraded mode is a policy exception and should remain narrow and visible.
- Hard exit improves containment but complicates product UX and testability.
- Reason-code ambiguity creates operational confusion; reason mapping must be explicit.
- Unsupported environment handling should avoid accidental loops or user-hostile retry storms.

---

## Open Questions
- Whether degraded operation should become an explicit formal state in RFC-0001 rather than only an outcome
- Whether exit-delay defaults should be standardized numerically in this RFC or left to backend policy entirely
- Whether retry budgets should be global or per-failure-class

---

## Consequences
Pros:
- deterministic and testable behavior across all startup paths
- centralized decision model for product and security teams
- consistent containment posture across platforms and deployments
- clear integration contract for host app UX

Cons:
- stricter policy behavior may feel harsher to product teams
- degraded mode requires careful scoping to avoid abuse
- hard exit requires deliberate implementation and QA coverage

---

## Dependencies
- RFC-0001 defines trust bootstrap states and invariants
- RFC-0002 defines backend verdict authority and contract errors
- RFC-0003 defines provider-side failure classes
- RFC-0004 defines config/storage validation failures and TTL rules

