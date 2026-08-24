# ADR-0007: SQLite-backed Durable Objects are the v1 trust authority

**Status:** Proposed  
**Date:** 2026-08-21  
**Decision owners:** Digitalis maintainers  
**Related:** QART-06, #11, #15, #16, #20, #31, #51

## Context

Digitalis v1 already selects Cloudflare Workers as the first-party hosted runtime and uses issued, single-use challenges with canonical request binding. The current executable challenge repository is process-local and therefore cannot provide production replay protection or durable attempt accounting.

The repository has conflicting persistence directions: an implementation-ready PostgreSQL design on `main` and PR #31's node-local SQLite + Drizzle proposal. A service-node SQLite file does not exist as an authoritative filesystem primitive in the accepted Worker runtime, while introducing PostgreSQL before the first vertical slice adds an external operational dependency that has not been shown necessary.

Cloudflare Durable Objects provide per-object private, strongly consistent, transactional storage. New Durable Object namespaces use/recommend the SQLite storage backend, which exposes SQL and synchronous transaction APIs and persists across object eviction/restart.

## Decision

Digitalis v1 will use a **SQLite-backed Durable Object as the authoritative trust-state partition for each project/environment** in the first-party Cloudflare Worker runtime.

The authority object owns challenge lifecycle state and counted verification attempts required to determine whether a provider call may be made and whether a completed submission may succeed.

Each provider verification uses a two-phase authoritative attempt lifecycle:

1. **Reserve attempt:** before any provider network call, one SQLite transaction revalidates project/environment scope, challenge identity, request binding, provider, lifecycle state, expiry, and submission limit; allocates the next numbered attempt; increments the authoritative submission count; and inserts an attempt in `reserved` state.
2. **Verify provider:** perform provider network verification outside any storage transaction using the immutable reservation/binding snapshot.
3. **Finalize attempt:** re-enter the same authority object and use one SQLite transaction to revalidate challenge lifecycle/binding and reservation identity, record the provider result, finalize the attempt, and apply the required challenge transition including successful consumption when applicable.

A request that cannot reserve an attempt does not call the provider. A reserved attempt consumes submission budget even if the provider times out or the client disconnects; bounded recovery may finalize abandoned reservations as failures but must not silently refund them into an unbounded provider-call path.

D1, PostgreSQL, R2, analytics systems, or other stores may later contain derived read models, audit exports, or control-plane information, but they are not authoritative for the v1 challenge trust decision unless a later QART/ADR explicitly changes this decision.

Node-local SQLite may exist only in explicitly non-production/reference adapters and must pass the same repository/transaction contract tests. It must not be described as the production Digitalis v1 persistence baseline.

## Partitioning

The default authority key is a deterministic project/environment identity.

A single global authority is rejected because it creates unnecessary contention and blast radius. Per-device or per-installation authority is rejected for v1 because it fragments project-scoped challenge/policy/configuration authority before there is evidence that such sharding is required.

Any future sharding of a project/environment authority requires a superseding decision because it changes serialization and routing semantics.

## Consequences

### Positive

- persistence matches the accepted Worker deployment model;
- provider-call admission is bounded before external cost is incurred;
- exactly-once challenge consumption can be expressed inside one strongly consistent transactional authority;
- SQLite semantics are retained without relying on a node-local filesystem;
- project/environment authority is explicit and naturally isolated;
- no external database service is required for the first vertical slice;
- runtime-neutral provider, protocol, policy, and serialization packages remain portable.

### Negative

- the hosted adapter intentionally depends on a Cloudflare-specific coordination primitive;
- one project/environment object is a serialization partition and requires measured throughput validation;
- provider failures and abandoned requests consume submission budget once reserved;
- cross-project reporting needs a separate non-authoritative read/index model;
- cross-object transactions are unavailable, so one trust decision cannot be split across authority objects.

## Security consequences

- storage or object failure fails closed;
- inability to reserve an attempt prevents the provider call;
- concurrent callers cannot exceed `max_submissions` by racing before provider verification;
- no positive verification outcome may be emitted from a failed/unknown finalize transaction state;
- reservations and finalization are correlated by exact immutable identity and duplicate finalization is idempotent;
- raw provider tokens, protected operation arguments, reusable bearer credentials, private keys, and protected configuration are not persisted in the authority by default;
- unauthorized project access and unknown challenge identifiers remain non-enumerating at the public API boundary;
- stale derived/read-model data cannot participate in challenge authorization;
- migration/version mismatch blocks activation rather than silently weakening invariants.

## Required implementation changes

1. Update #11 and the persistence implementation slice to distinguish domain invariants from the Worker-specific authority adapter and model `reserved`/finalized attempts explicitly.
2. Implement a deterministic project/environment Durable Object routing boundary in the Digitalis Worker.
3. Implement SQLite schema/migrations for projects or authoritative project references, challenges, attempt reservations/results, and exact reservation identities as appropriate to the partition.
4. Add reservation, transaction, concurrency, restart/eviction, abandoned-attempt recovery, migration, privacy, and negative tests.
5. Revise or close PR #31 so node-local SQLite is not represented as production authority.
6. Keep PostgreSQL as a possible future deployment adapter, not a v1 prerequisite.

## Alternatives considered

### D1 primary authority

Rejected as the default because read replication is asynchronous and session semantics must be managed explicitly. D1 remains viable for non-authoritative relational/read workloads and could be reconsidered if future requirements justify it.

### PostgreSQL through Hyperdrive

Deferred. It has mature relational transactions but introduces a separate availability, credentials, backup, connectivity, and operational boundary before the first milestone.

### Node-local SQLite + Drizzle

Rejected for the first-party hosted runtime because the accepted runtime is Cloudflare Workers, not a persistent service node.

### Split authority

Rejected for v1 because challenge consumption and attempt/decision state must not depend on an uncoordinated cross-store commit.

## Validation

Acceptance requires evidence that:

- concurrent reservation attempts never admit more than `max_submissions` provider calls;
- attempt number allocation, submission-count increment, and reservation insertion are atomic;
- concurrent valid finalized submissions yield exactly one successful consumption;
- duplicate finalize/retry is idempotent by exact reservation identity;
- provider timeout/client disconnect cannot create an unbounded retry/refund path;
- provider latency cannot bypass expiry/revocation/consumption changes before finalize;
- object restart/eviction preserves challenge and reserved-attempt state;
- migration failure is fail closed;
- local and deployed Worker tests exercise the same contract;
- privacy tests prove forbidden raw inputs are absent from durable state;
- load testing defines the safe per-partition operating envelope.

## Supersession

A change to D1/PostgreSQL as primary authority, split authority, provider verification before authoritative reservation, or sharded project/environment authority requires a superseding ADR and corresponding QART analysis.
