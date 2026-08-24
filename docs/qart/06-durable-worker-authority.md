# QART-06: Durable Worker Authority

**Status:** Recommended; binding decision proposed by ADR-0007  
**Scope:** durable trust authority for the Digitalis v1 Cloudflare Worker

## Questions

1. What storage primitive should be authoritative for challenge lifecycle, attempt accounting, replay protection, and later configuration/capability authorization?
2. How should the design preserve the accepted Cloudflare Workers first-party runtime without duplicating security-critical persistence semantics?
3. Which consistency and transaction guarantees are required for exactly one successful challenge consumption under concurrent submissions?
4. How should local/reference persistence relate to the hosted production authority?

## Security invariant

One trust decision must have one authoritative durable state transition. Concurrent verification must not produce more than one successful challenge consumption, and provider-call admission must itself be bounded by authoritative state so concurrent requests cannot bypass submission limits before network verification begins. Storage ambiguity, stale authority reads, restart, eviction, or backend failure must never manufacture trusted state.

## Existing evidence

- ADR-0001 and QART-05 make Cloudflare Workers the first-party hosted runtime for v1.
- The current executable challenge repository is process-local and therefore not production-capable.
- `docs/architecture/durable-challenge-persistence-slice.md` currently specifies PostgreSQL and multi-instance semantics.
- PR #31 proposes SQLite + Drizzle as a node-local production baseline, which is not directly usable by the accepted Worker runtime.
- The repository and unit-of-work invariants in #11 remain useful independently of the concrete storage adapter.
- Cloudflare Durable Objects provide per-object private, strongly consistent, transactional storage; Cloudflare recommends SQLite-backed Durable Object namespaces for new Durable Objects.
- SQLite-backed Durable Objects expose SQL and explicit synchronous transaction APIs, and persisted state survives object eviction/restart.
- D1 read replication is asynchronous; D1 Sessions provide sequential consistency for a logical session, so authorization-critical code must reason explicitly about stale replicas if D1 is used as authority.

## Alternatives

### A. SQLite-backed Durable Object per project/environment

Use a deterministic Durable Object identity for each authoritative project/environment partition. The object owns challenge rows, attempt reservations/results, lifecycle transitions, and later trust-decision references in its attached SQLite storage.

**Advantages**

- native to the accepted Worker runtime;
- strong consistency and serialized object execution align with single-use challenge semantics;
- SQLite-backed transactional SQL without a service-node filesystem;
- project/environment partition is a natural authority and blast-radius boundary;
- no separate database service is required for the first vertical slice;
- local Worker testing can use the same runtime/storage model.

**Risks**

- one project/environment object is a serialization partition and may become a throughput hotspot;
- cross-project reporting requires a separate non-authoritative index/read model;
- object naming, migrations, retention, and deletion must be explicit and auditable;
- cross-object transactions are not available, so a single trust decision must not span multiple authority objects.

### B. D1 as primary authority

Store all project/challenge/attempt state in one or more D1 databases.

**Advantages**

- Worker-native relational database;
- straightforward global relational querying and migrations;
- simpler cross-project operational views.

**Risks**

- read replicas are asynchronously replicated;
- Sessions provide sequential consistency, not an implicit substitute for a single serialized authority partition;
- stale-read mistakes in authorization paths have direct security consequences;
- concurrency semantics for exactly-once challenge consumption and pre-provider attempt reservation must be proven independently.

### C. External PostgreSQL through Hyperdrive

Retain PostgreSQL as the production authority and connect from Workers through Hyperdrive.

**Advantages**

- mature relational transaction semantics;
- existing persistence design can be retained with less conceptual change;
- strong fit if later administrative or multi-service workloads require a shared relational database.

**Risks**

- additional infrastructure, credentials, backup, latency, incident, and availability dependencies before the first milestone;
- increases operational scope without evidence that v1 needs shared cross-project relational authority;
- runtime-neutral repository abstractions can hide materially different failure behavior.

### D. Node-local SQLite as production authority

Use a local SQLite file with Drizzle behind the existing Express/backend composition.

**Advantages**

- simple local development;
- small operational footprint outside Workers;
- familiar SQL and migration tooling.

**Risks**

- incompatible with the accepted Cloudflare Worker deployment model as the first-party hosted authority;
- requires a second security-critical persistence implementation before the supported service exists;
- creates duplicated trust semantics and divergent failure behavior.

### E. Split trust authority across Durable Objects and another database

Use Durable Objects for coordination and D1/PostgreSQL for authoritative attempt or decision records.

**Advantages**

- separates coordination from analytics/storage concerns.

**Risks**

- creates a cross-store commit problem for one trust decision;
- can leave challenge consumption and attempt/decision state divergent;
- materially increases recovery and audit complexity.

## Recommendation

Select alternative A for Digitalis v1.

Use one SQLite-backed Durable Object as the authoritative trust-state partition for each project/environment. The authoritative object owns all state required to decide whether a challenge is still valid, whether another provider verification may be attempted, and whether a completed verification may transition the challenge.

Each provider verification is admitted through a two-phase authoritative attempt lifecycle:

1. **Reserve:** in one synchronous SQLite transaction, revalidate project/environment scope, challenge identity, request binding, provider, lifecycle state, expiry, and `max_submissions`; allocate the next monotonically numbered attempt; increment the authoritative submission count; insert the attempt as `reserved`; commit before any provider network call.
2. **Verify:** perform provider network verification outside any storage transaction using the immutable reservation/binding snapshot.
3. **Finalize:** re-enter the same authority object and, in one synchronous transaction, revalidate challenge lifecycle/binding and the reservation identity, record the provider result, mark the reservation finalized, and apply the required challenge transition including successful consumption when applicable.

A request that cannot reserve an attempt never reaches the provider. A reserved attempt consumes submission budget even if the provider call times out or the client disconnects; recovery policy may finalize abandoned reservations as bounded failures but must never silently refund them in a way that permits unbounded provider calls.

D1 or another store may later hold derived operational/reporting data, but it must not participate in the authorization decision unless a later QART explicitly changes the authority model.

PostgreSQL remains a valid future adapter for a different deployment topology, but it is not a prerequisite for the first-party Worker milestone. Node-local SQLite may remain useful for local/reference adapters only if repository contract tests prove semantic equivalence and documentation clearly marks it non-authoritative for the hosted service.

## Authority model

```text
request -> Worker routing/authentication
        -> deterministic project/environment DO id
        -> Durable Object
             -> SQLite authoritative state
             -> reserve transaction:
                  re-check lifecycle/binding/max_submissions
                  allocate attempt number
                  increment submission count
                  insert reserved attempt
             -> provider verification outside transaction
             -> finalize transaction:
                  re-check lifecycle/binding/reservation
                  record provider result
                  finalize attempt
                  consume/revoke/retain challenge
             -> typed outcome
        -> policy/config pipeline
```

Provider network work must not be performed while a storage transaction is open. The pre-provider reservation prevents concurrent callers from exceeding the authoritative submission budget, while final revalidation prevents provider latency from authorizing expired, revoked, consumed, or otherwise changed challenge state.

## Partitioning

The v1 default partition key is project/environment, not device or installation.

Reasons:

- challenge issuance and policy/configuration authority are project-scoped;
- a deterministic project/environment authority prevents cross-project confusion;
- per-device objects would fragment project-level lifecycle/configuration authority prematurely;
- one global object would create unnecessary blast radius and contention.

If production evidence shows one project/environment object cannot satisfy throughput, sharding requires a new QART because sharding changes the single-authority invariant and routing semantics.

## Failure semantics

- object/storage unavailability -> fail closed;
- reservation transaction failure -> no provider call and no successful verification outcome;
- provider timeout/client disconnect after reservation -> reservation remains consumed submission budget until deterministically finalized/expired as failure;
- finalize transaction failure -> no successful verification outcome; reservation remains recoverable by exact identity;
- duplicate/concurrent success -> exactly one finalize transaction may consume the issued challenge;
- concurrent submissions beyond `max_submissions` -> fail before provider verification because attempt reservation is authoritative;
- unknown or unauthorized project/challenge -> non-enumerating public response;
- stale derived/read-model data -> never authoritative;
- Worker/object restart -> durable SQLite state and reservations remain authoritative;
- migration failure -> block activation rather than silently using incompatible schema.

## Privacy and retention

Persist only the minimum state required by #20. Raw provider tokens, protected operation arguments, reusable bearer credentials, private keys, and protected configuration are not stored in the challenge authority by default. Attempt reservations store only the minimum immutable binding/evidence references required to correlate and finalize the attempt. Evidence references/digests may be retained only under explicit policy.

## Tradeoffs

- Durable Objects intentionally introduce Cloudflare-specific state orchestration in the hosted adapter; runtime-neutral protocol/provider/policy packages remain portable.
- Project/environment serialization simplifies correctness but may cap per-partition write throughput; measure before sharding.
- Reserving before provider work means provider failures and abandoned requests consume submission budget; this is intentional to preserve abuse bounds and requires explicit UX/retry policy.
- A separate read model may eventually be necessary for fleet-wide reporting; keeping it non-authoritative avoids cross-store trust ambiguity.
- PostgreSQL portability is preserved at repository-contract level rather than by forcing PostgreSQL into the first Worker milestone.

## Decisions

- **QART-0033:** Digitalis v1 uses one authoritative durable trust-state partition per project/environment.
- **QART-0034:** The first-party Cloudflare Worker implements that authority with a SQLite-backed Durable Object.
- **QART-0035:** Each provider verification must first reserve a numbered attempt atomically, incrementing authoritative submission count before any provider network call.
- **QART-0036:** Provider network verification occurs outside storage transactions; the reserved attempt is then finalized atomically with lifecycle revalidation and any successful challenge consumption.
- **QART-0037:** D1/PostgreSQL/read models may store derived operational data but are non-authoritative for the v1 trust decision unless superseded by a later QART/ADR.
- **QART-0038:** Node-local SQLite is permitted only for explicitly non-production/reference adapters and must satisfy shared repository contract tests.
- **QART-0039:** Sharding a project/environment authority requires a new decision because it changes trust routing and serialization semantics.

## Required tests and evidence

- concurrent reservation attempts never admit more than `max_submissions` provider calls;
- attempt numbers are unique/monotonic within a challenge and reservation + submission-count increment are atomic;
- concurrent successful finalized submissions produce exactly one consumed result;
- reservation/finalize rollback leaves no partial authoritative mutation;
- provider timeout, client disconnect, and abandoned reservations cannot refund submission budget into an unbounded retry path;
- expiry/revocation/consumption changes during provider latency are observed before finalize mutation;
- duplicate finalize/retry is idempotent by exact reservation identity;
- Durable Object restart/eviction preserves lifecycle and reserved-attempt state;
- wrong-project and unknown challenge paths are publicly indistinguishable;
- migration/version mismatch fails closed;
- no raw provider token or protected operation arguments are persisted;
- local Worker test and deployed test Worker exercise the same authority contract;
- load test establishes the project/environment partition's safe operating envelope before any sharding proposal.

## Rejected directions

- Do not make PR #31's node-local SQLite file the production v1 authority.
- Do not perform provider verification before authoritative attempt reservation.
- Do not make a read replica or derived event/reporting store authoritative for challenge consumption.
- Do not split one trust decision across two stores without an explicit atomicity model and new decision record.

## Implementation consequences

1. Revise #11 to separate runtime-neutral repository/transaction invariants from the Worker adapter and model reserved/finalized attempts explicitly.
2. Supersede the PostgreSQL-specific implementation-ready slice with a Durable Object implementation slice while retaining its domain invariants.
3. Revise or close PR #31; keep Drizzle/local SQLite only if explicitly scoped to a reference adapter.
4. Implement the Worker Durable Object adapter and pre-provider reservation boundary before positive Google provider authorization is allowed to reach configuration issuance.
5. Add Worker/DO reservation, concurrency, restart, negative, privacy, and abandoned-attempt recovery tests to CI.

## Binding ADR

- ADR-0007 — SQLite-backed Durable Objects are the Digitalis v1 trust authority.

Refs #11, #15, #16, #20, #31, #51.
