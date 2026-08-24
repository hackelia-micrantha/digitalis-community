# Digitalis Status, Gap, and Priority Review

**Review date:** 2026-07-27  
**Repositories:** `hackelia-micrantha/digitalis`, `hackelia-micrantha/digitalis-community`  
**Assessment:** Requires focused completion work  
**Current maturity:** Architecture and executable protocol prototype; pre-alpha

## 1. Executive summary

Digitalis is intended to provide backend-authoritative mobile trust bootstrap:

1. a mobile application obtains a short-lived server challenge;
2. provider evidence is bound to a canonical protected operation;
3. the Digitalis service verifies that evidence using server-owned application identity;
4. a deterministic policy maps normalized evidence to a canonical outcome;
5. an authorized client receives KMS-signed configuration;
6. a native SDK verifies, installs, and activates that configuration locally.

The accepted first delivery slice is:

```text
Android reference application
  -> Digitalis Android SDK
  -> Google Play Integrity standard request
  -> Digitalis Cloudflare Worker
  -> normalized provider evidence
  -> deterministic Digitalis policy
  -> canonical startup outcome
  -> KMS-signed configuration
  -> verified local activation
```

The project direction is coherent and unusually well documented. QART analyses and ADRs have resolved the major product, repository, protocol, policy, key-custody, and first-milestone questions. The implementation is nevertheless not yet a usable trust-bootstrap product.

The current executable boundary provides strict `digitalis.v1` request validation, canonical request hashing, server-owned project profiles, a process-local challenge lifecycle, replay and substitution protection, and cross-language TypeScript/Kotlin vectors. Incomplete provider paths fail closed.

The first milestone remains incomplete because Digitalis does not yet have:

- a positive Google Play Integrity verifier;
- durable multi-instance challenge state;
- deterministic policy evaluation;
- KMS-backed signed configuration;
- the supported Digitalis Cloudflare Worker;
- a native Android SDK or reference binary;
- required private-repository CI and release evidence.

The immediate direction is to finish one Android/Google/Cloudflare vertical slice and remove competing legacy mechanisms before expanding to Apple, KMP, React Native, customer-managed backends, risk scoring, or alternate hosted runtimes.

## 2. Project and repository model

### `digitalis`

Authoritative for:

- product architecture and security decisions;
- QART and ADR records;
- executable protocols and conformance fixtures;
- provider, policy, configuration, SDK, and service implementation;
- private threat analysis;
- generated release and publication inputs.

### `digitalis-community`

Authoritative for:

- reviewed public website and whitepaper content;
- public release artifacts and publication-safe provenance;
- contribution and security-reporting guidance;
- public static-site deployment.

### Themis lineage

Themis is the predecessor Digitalis service and Cloudflare Worker lineage. It is not intended to remain an independent competing verifier. Useful OAuth, Google decode, operational, and deployment behavior should be migrated or rewritten into one Digitalis provider package and one supported Digitalis Worker service with preserved provenance.

### Current boundary concern

The private repository still declares both `web` and `external/community` as submodules pointing to `digitalis-community`. This conflicts with the accepted one-way publication model unless a concrete private build requirement is documented. The preferred boundary is reviewed publication metadata rather than private source dependency on the public repository.

## 3. Current executable capability

The implemented protocol slice includes:

- `POST /api/v1/challenges`;
- `POST /api/v1/attestations:verify`;
- `GET /api/v1/configurations/{configRef}` as an explicit `501` contract stub;
- strict rejection of unsupported versions and unknown critical fields;
- server-owned policy, provider, and operation scope;
- canonical JSON serialization and SHA-256 base64url request hashing;
- shared TypeScript/Kotlin golden vectors;
- random expiring challenge identifiers;
- provider-to-request binding requirements;
- process-local replay, expiry, revocation, substitution, retry, submission-limit, and concurrent-consumption behavior;
- one-way evidence references rather than returned raw evidence;
- production rejection of mock-attestation, development-seed, and process-local project-profile configuration.

This is a useful executable state-machine prototype. It is not evidence of production correctness because state remains process-local and no production provider can currently return verified bound evidence.

## 4. Capability status matrix

| Capability | Intended outcome | Status | Missing work | Risk |
| --- | --- | --- | --- | --- |
| Product and repository boundaries | One engineering authority and one public publication boundary | Decision complete; incompletely enforced | Remove duplicate submodule/site/schema ownership | Medium |
| Fail-closed provider behavior | No prototype request value can manufacture trusted state | Implemented; missing continuous CI evidence | Required private-repository checks | Medium |
| `digitalis.v1` contract | Strict provider-neutral challenge, verification, and configuration-reference API | Partially implemented | Complete remaining contract and generated types | Medium |
| Canonical request binding | Identical operation digest across SDK and service languages | Implemented in prototype | CI enforcement and Android integration | Medium |
| Challenge lifecycle | Expiring, single-use, replay-safe durable challenge | Partially implemented | PostgreSQL transaction, restart, multi-instance semantics | High |
| Google Play Integrity provider | Authenticate provider evidence and return normalized claims | Not implemented | Themis migration/rewrite and real-provider tests | High |
| Deterministic policy | Map normalized evidence to versioned canonical decisions | Not implemented | Registries and side-effect-free evaluator | High |
| Signed configuration | KMS-signed, expiring, revocable, rollback-safe configuration | Blocked | Canonical envelope, KMS signer, lifecycle and vectors | High |
| Digitalis Cloudflare Worker | Supported hosted verification service | Not implemented | Worker, bindings, environments, operations, cutover | High |
| Android SDK and reference app | Real binary completing the trust-bootstrap flow | Not implemented | SDK, Play request, local signature/storage/rollback handling | High |
| Tenant/project authorization | Prevent cross-project access and provider abuse | Undefined | QART/ADR and implementation | High |
| Privacy and retention | Minimize provider evidence and audit data | Undefined | Field inventory, retention/deletion/redaction policy | High |
| Private repository CI | Required build, test, conformance, security and release gates | Not implemented | GitHub Actions and branch protection | High |
| Public website boundary | Accurate and hardened static publication | Repository controls implemented | Repair deployment and verify live behavior | Medium |
| Publication provenance | One-way reviewed publication with traceability | Partially implemented | Bind records to artifact digests and scan governed content | Medium |
| Apple App Attest | Second provider/platform implementation | Deferred | Separate post-v1 milestone | Low for v1 |

## 5. Verified completed work

### Architecture baseline

The project has:

- five QART slices;
- a QART decision register;
- six accepted ADRs;
- a phased implementation roadmap;
- an explicit Android/Google/Cloudflare first milestone;
- a definition of done requiring threat, test, migration, privacy, rollback, documentation, and provenance considerations.

### Fail-closed prototype cleanup

The completed cleanup removed or disabled:

- synthetic Apple and Google success tokens;
- shallow Apple CBOR acceptance as verified evidence;
- Google acceptance without recognized application evidence;
- default administrative seed routing;
- production mock and seed configuration.

### Executable request-binding slice

The first #11 slice establishes a real protocol and state-machine boundary. Negative behavior is tested for replay, expiry, revocation, wrong project, wrong operation, changed operation data, provider substitution, provider-binding mismatch, bounded retry, submission limits, and process-local concurrent consumption.

### Public repository hardening

`digitalis-community` now has:

- a clear public publication role;
- deployment configuration targeting `web/`;
- static-site security and cache headers;
- canonical `security.txt`;
- contribution, conduct, license, and security guidance;
- site link, anchor, accessibility, and no-JavaScript validation;
- one-way publication workflow and manifest validation.

## 6. Critical gaps and inconsistencies

### 6.1 Competing legacy runtime remains mounted

The backend still exposes deprecated `POST /api/v1/config` alongside the new challenge protocol. The legacy controller combines client-supplied identity, provider verification, configuration selection, signing, optional encryption, delivery logging, and response construction.

It currently fails closed only because provider implementations reject all evidence. A future provider implementation could accidentally reactivate the superseded path.

Tracked by #24.

### 6.2 Legacy schema contradicts accepted v1 architecture

The same bootstrap schema exists in both `backend/src/db/schema.sql` and `docs/schema.sql`. It includes:

- raw `key_material` in PostgreSQL;
- shared signing and encryption keys;
- raw provider payload retention;
- account-coupled trust bootstrap;
- independently active keys/configurations;
- confidence and risk scoring;
- alert and case-management tables outside the first milestone.

The `migrate` command executes this complete schema rather than applying versioned migrations. The replacement v1 schema should be designed from accepted requirements rather than incrementally generalizing the prototype.

### 6.3 Challenge authority is process-local

The in-memory repository demonstrates correct local state transitions but cannot prove:

- restart durability;
- multi-instance exclusion;
- transactional attempt and lifecycle records;
- database rollback behavior;
- persistent audit evidence.

The next #11 slice should make challenge consumption, attempt recording, lifecycle transitions, and minimized audit records durable and transactional. The later integrated transaction that combines positive provider verification, deterministic policy evaluation, challenge consumption, and configuration-issuance authorization belongs after the #12, #13, and #14 interfaces exist.

### 6.4 Authorization and abuse boundaries are undefined

A public project identifier is routing data, not authorization. Before durable challenge issuance and paid provider calls, Digitalis must define:

- project and application identity resolution;
- tenant consistency;
- mobile versus administrative credentials;
- cross-project access controls;
- body and field limits;
- per-project, installation, network, and global rate limits;
- provider quotas and deadlines;
- production CORS and proxy behavior.

Issue #15 should begin with a focused QART/ADR slice rather than immediately implementing middleware.

### 6.5 Privacy requirements must precede persistence

The retained normalized evidence, digest, decision, identifier, audit, and telemetry fields must be decided before migrations are written. Raw provider tokens, credentials, private keys, unnecessary device/account identifiers, and raw configuration must not become default logs or durable records.

Issue #20 is therefore a dependency of the durable #11 schema slice, not later cleanup.

### 6.6 Private repository lacks required GitHub CI

The tests are stronger than the automation around them. No GitHub workflow evidence protects the merged protocol slice. The repository also contains a `pnpm-lock.yaml` while README commands instruct `npm install`.

The immediate #18 slice should establish:

- pinned pnpm/Corepack installation;
- TypeScript build;
- Jest unit and integration tests;
- Kotlin golden-vector execution;
- dependency audit;
- static analysis and secret scanning;
- migration and generated-artifact drift checks.

The outstanding Morgan security update is specifically `1.10.1` to `1.11.0`; the current `1.10.1` dependency is not the completed target.

### 6.7 Public deployment is not verified healthy

The final `digitalis-community` publication-provenance PR merged and repository validation passed, but Cloudflare reported a failed deployment for the merged head. Public issue #2 should remain open until:

- a preview deployment succeeds;
- the custom domain is verified;
- canonical `security.txt` is reachable;
- CSP, HSTS, cache, and other response headers are observed live;
- rollback is exercised.

### 6.8 Publication provenance is metadata-only

The current manifest validates paths, ownership classes, and source references but does not cryptographically bind those records to artifact contents. A governed file can change while retaining an old version and review record.

Recommended follow-up:

- add SHA-256 for each governed artifact;
- verify digests in CI;
- scan governed public text and metadata for prohibited private identifiers;
- maintain an immutable private mapping from opaque publication IDs to source commits and reviews.

### 6.9 Public roadmap exceeds the accepted first milestone

Public language still mentions optional configuration encryption, customer-managed deployment, and Apple demonstration near the first milestone. The accepted v1 scope is signed configuration without shared application-layer encryption and Android/Google/Cloudflare first.

Public documentation should distinguish:

- current milestone;
- post-v1 planned expansion;
- architectural possibility that has not been committed to a milestone.

## 7. Priority model

The repository currently labels several implementation workstreams P0. Under the project review priority definition, no active P0 incident is verified because production provider paths fail closed and no release-capable service exists.

Recommended interpretation:

- **P0:** active exploit, data loss, broken production service, or blocker for all work;
- **P1:** required for the first release or material security/correctness risk reduction;
- **P2:** important consistency, maintainability, usability, or operational improvement;
- **P3:** deferred expansion.

Most existing P0 implementation issues are release-blocking P1 work unless evidence shows the legacy service is actively deployed or relied upon.

## 8. Recommended execution order

### Phase 1: immediate stabilization

1. Remove deprecated config-delivery runtime and quarantine the legacy schema (#24).
2. Establish minimal required GitHub CI as the first #18 slice.
3. Update Morgan from `1.10.1` to `1.11.0` and normalize pnpm/Corepack usage.
4. Repair and verify the Digitalis Community deployment.
5. Bind publication records to artifact digests.
6. Remove stale private/public submodule coupling.

**Exit criteria**

- no legacy configuration-delivery route is mounted;
- private `main` requires build, test, and vector checks;
- dependency installation is reproducible;
- Morgan `1.11.0` is installed through the canonical lockfile;
- the public preview deployment succeeds;
- live headers and `security.txt` are verified.

### Phase 2: required decisions

1. Define project authorization and provider-abuse controls (#15).
2. Define evidence minimization, retention, deletion, and audit policy (#20).
3. Clarify Worker-to-KMS signing topology (#14).
4. Clarify opaque public provenance to private source mapping (#19 / ADR-0006).

**Exit criteria**

- no unresolved decision blocks schema design;
- retained fields and redaction rules are explicit;
- signer failure and availability behavior are defined.

### Phase 3: foundational state and contracts

1. Replace the bootstrap SQL with versioned v1 migrations.
2. Implement durable project, challenge, attempt, installation-reference, policy-reference, and security-event repositories.
3. Make challenge consumption, attempt recording, lifecycle transitions, and minimized audit records transactional.
4. Add restart, multi-instance, idempotency, retry, and rollback tests.

**Exit criteria**

- exactly one durable challenge consumption under concurrent instances;
- database rollback cannot leave a consumed challenge without its attempt and lifecycle records;
- no raw private signing key or raw provider token is persisted.

### Phase 4: first complete product slice

1. Implement one shared Google Play Integrity provider package (#12).
2. Implement deterministic policy and executable registries (#13).
3. Implement KMS-backed signed configuration lifecycle (#14).
4. Integrate positive provider verification, deterministic policy evaluation, challenge consumption, and configuration-issuance authorization into one durable transaction.
5. Build and deploy the Digitalis Cloudflare Worker (#16).
6. Implement the Android SDK and reference app (#17).

**Exit criteria**

A real Android binary completes:

```text
challenge
  -> Play Integrity
  -> Digitalis Worker
  -> normalized evidence
  -> deterministic policy
  -> signed configuration
  -> local verification
  -> protected activation
```

Every negative fixture leaves protected behavior disabled, and a successful flow records one atomic decision and issuance chain.

### Phase 5: validation and release assurance

1. Add controlled real-provider integration testing.
2. Produce SBOMs, checksums, provenance, and signed immutable release artifacts.
3. Add deployment, rollback, quota, credential-rotation, and incident runbooks.
4. Protect the default branch with required checks and ownership rules.
5. Refresh public status from demonstrated release evidence.

**Exit criteria**

- release evidence is independently verifiable;
- required checks protect `main`;
- production logs contain no credentials or raw evidence;
- public claims match demonstrated controls.

### Deferred expansion

Do not begin until the first milestone is complete:

- Apple App Attest and Swift SDK;
- customer-managed backend packaging;
- Kotlin Multiplatform and React Native facades;
- native binary protection and obfuscation requirements;
- risk scoring and SIEM/case-management integration;
- alternate first-party hosted runtimes.

## 9. Issue and pull-request actions

### New issue

- #24 — remove deprecated config-delivery runtime and quarantine legacy schema.

### Existing issues to retain and refine

- #11 — durable v1 challenge state, attempt recording, authenticated routing, and transactional lifecycle;
- #12 — single corrected Themis-derived Google provider;
- #13 — deterministic policy and registries;
- #14 — KMS-backed signed configuration and integrated issuance transaction;
- #15 — authorization and abuse controls;
- #16 — Digitalis Cloudflare Worker rebuild and cutover;
- #17 — Android SDK and reference application;
- #18 — CI, conformance, SBOM, and release provenance;
- #19 — publication boundary, duplicated sources, and provenance;
- #20 — evidence privacy and retention;
- #21 — RFC and control-contract normalization.

### Decision issues

QART issues #5, #7, #8, and #9 should be closed once their decision-specific checklists and implementation links are updated. They should not remain open solely because linked implementation is unfinished. Issue #6 provides the preferred pattern: completed decision issue with separate implementation tracking.

### Pull requests

- close obsolete Cloudflare autoconfiguration PRs in both repositories as superseded;
- replace or rebase the stale Morgan dependency PR with the explicit `1.11.0` target using the canonical package manager and lockfile;
- keep `digitalis-community` issue #2 open until the failed deployment and live verification are resolved.

## 10. Final assessment

**Conclusion: Requires focused completion work.**

Digitalis has a credible architecture and a useful executable protocol foundation, but it is not ready to release. The project should now optimize for completion and simplification:

- delete the competing legacy path;
- establish continuous evidence;
- resolve authorization and privacy before persistence;
- complete one provider, one policy engine, one signed-configuration path, one Worker service, and one native SDK;
- expand only after that slice is demonstrated and releasable.
