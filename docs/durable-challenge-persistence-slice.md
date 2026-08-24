# Durable challenge persistence slice

Status: implementation-ready  
Parent: #11  
Constraints: #15, #20

## Objective

Replace the process-local challenge lifecycle with a PostgreSQL-backed boundary that preserves the existing `digitalis.v1` protocol semantics across process restarts and multiple service instances.

This slice stops at durable challenge and attempt state. It does not implement Google Play Integrity decoding, deterministic policy, KMS-backed configuration signing, the Cloudflare Worker adapter, or the Android SDK.

## Security invariants

1. Public `project_id` values are selectors, not authorization credentials.
2. Challenge scope is resolved from an authenticated server-side project context before persistence.
3. Challenge identifiers are globally unique and unguessable.
4. A challenge can transition from `issued` to `consumed`, `expired`, or `revoked` only once.
5. Exactly one concurrent successful submission may consume an issued challenge.
6. Provider work never holds a database transaction open.
7. Successful consumption and the corresponding successful attempt record are committed atomically.
8. Every counted submission and its attempt record are committed atomically.
9. Failed, duplicate, expired, revoked, and transient submissions are auditable without retaining raw provider evidence or protected operation arguments by default.
10. Repository methods never accept client-controlled tenant or project authority independently of the authenticated project context.
11. Database errors fail closed and cannot manufacture a verified outcome.
12. Project/challenge consistency is enforced by database constraints, not application convention alone.

## Minimal schema

### `digitalis_projects`

Stores authoritative routing and lifecycle configuration required by the challenge slice.

- `id uuid primary key`
- `public_project_id text unique not null`
- `tenant_id uuid not null`
- `status text not null check (status in ('active', 'suspended', 'retired'))`
- `policy_version text not null`
- `allowed_providers text[] not null`
- `allowed_operations text[] not null`
- `challenge_ttl_seconds integer not null`
- `max_submissions integer not null`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

The API-facing project identifier is mapped to this record only after the deployment adapter establishes the caller's authorized project context. A later multi-tenant routing decision may replace global `public_project_id` uniqueness with tenant-scoped uniqueness, but this slice must not infer tenant authority from the public identifier.

### `attestation_challenges`

- `id uuid primary key`
- `project_id uuid not null references digitalis_projects(id)`
- `contract_version text not null`
- `operation text not null`
- `provider text not null`
- `policy_version text not null`
- `request_hash text not null`
- `status text not null check (status in ('issued', 'consumed', 'revoked', 'expired'))`
- `issued_at timestamptz not null`
- `expires_at timestamptz not null`
- `consumed_at timestamptz null`
- `submission_count integer not null default 0`
- `max_submissions integer not null`
- `version bigint not null default 0`

Protected operation arguments are not persisted in this slice. The canonical `request_hash`, operation name, project, provider, contract version, and policy version are sufficient to revalidate immutable request binding when the client resubmits the operation arguments.

Required constraints:

- `expires_at > issued_at`
- `submission_count >= 0`
- `max_submissions > 0`
- `submission_count <= max_submissions`
- `consumed_at is not null` exactly when `status = 'consumed'`
- unique `(id, project_id)` for composite attempt references
- unique `(project_id, id)` for explicit project-scoped lookups

### `attestation_attempts`

- `id uuid primary key`
- `challenge_id uuid not null`
- `project_id uuid not null`
- `attempt_number integer not null`
- `provider text not null`
- `outcome text not null`
- `reason_code text not null`
- `evidence_reference text null`
- `evidence_digest text null`
- `request_hash text not null`
- `started_at timestamptz not null`
- `completed_at timestamptz not null`
- `created_at timestamptz not null`

Required constraints:

- foreign key `(challenge_id, project_id)` references `attestation_challenges(id, project_id)`
- unique `(challenge_id, attempt_number)`
- `attempt_number > 0`
- `completed_at >= started_at`
- no raw provider token, decoded evidence payload, protected operation arguments, credential, configuration, or key-material column
- outcome vocabulary is bounded to provider verification and lifecycle results owned by this slice

The composite foreign key prevents an attempt from naming one challenge and a different project even if application code is defective.

### `security_events`

This slice may write minimized lifecycle events through an interface, but a broad event model is not required before #20 defines the field inventory. No raw evidence, credential, configuration, provider token, or protected operation argument may be written.

## Repository boundary

Replace the current mutation-oriented interface with explicit transaction results rather than nullable records whose failure reason is ambiguous.

```ts
interface DurableChallengeRepository {
  create(input: CreateChallengeRecord): Promise<ChallengeRecord>;
  findForAuthorizedProject(
    projectInternalId: string,
    challengeId: string,
  ): Promise<ChallengeRecord | null>;
  recordRejectedAttempt(input: RejectedAttempt): Promise<AttemptResult>;
  recordTransientAttempt(input: TransientAttempt): Promise<AttemptResult>;
  consumeVerifiedChallenge(input: VerifiedAttempt): Promise<ConsumeResult>;
  expireIfIssued(input: LifecycleTransition): Promise<TransitionResult>;
  revokeIfIssued(input: LifecycleTransition): Promise<TransitionResult>;
}
```

All mutating attempt methods must execute a transaction that:

1. conditionally updates the authorized challenge row while project, challenge ID, status, expiry, request hash, provider, and submission limit still match;
2. increments `submission_count` and returns the resulting value as `attempt_number`;
3. applies the required terminal or non-terminal lifecycle transition;
4. inserts the corresponding attempt using the returned attempt number;
5. commits both changes together;
6. returns a typed result.

`consumeVerifiedChallenge` additionally transitions the challenge to `consumed` and sets `consumed_at`. A rejected or transient attempt either leaves the challenge `issued` or revokes it when the submission limit is reached.

A conditional update is preferred over a long-lived `SELECT ... FOR UPDATE` transaction because provider verification occurs before this transaction. The update must affect exactly one row. Zero affected rows are resolved to a typed lifecycle conflict by a follow-up read in the same transaction.

Attempt numbers must never be allocated with `max(attempt_number) + 1`; they are derived from the challenge row's atomically incremented `submission_count`.

## Verification flow

```text
resolve authorized project context
  -> load issued challenge snapshot
  -> recompute and validate immutable request binding
  -> perform bounded provider verification outside a DB transaction
  -> begin transaction
  -> re-check project, status, expiry, provider, request hash, and submission limit
  -> atomically increment submission count, record attempt, and apply transition
  -> commit
```

The second validation prevents time-of-check/time-of-use races while avoiding database locks during an external provider call.

## Failure semantics

Repository methods return typed internal outcomes including:

- `consumed`
- `already_consumed`
- `expired`
- `revoked`
- `submission_limit_reached`
- `project_mismatch`
- `binding_mismatch`
- `not_found`
- `transient_storage_failure`

Only `consumed` can contribute to a later positive policy decision. Storage errors and unknown states fail closed.

`project_mismatch` is an internal audit distinction only. Public API behavior must collapse unauthorized project access and unknown challenge IDs to the same non-enumerating response.

## Migration strategy

1. Add ordered, immutable versioned migrations and a migration-history table.
2. Create the project, challenge, and attempt tables without importing obsolete prototype rows.
3. Add indexes for project-scoped challenge lookup, expiry processing, and attempt history.
4. Introduce the PostgreSQL repository behind the existing interface.
5. Keep the in-memory repository test-only and inaccessible from production composition.
6. Switch production composition only after migration, concurrency, rollback, restart, and redaction tests pass.
7. Roll back the application independently of schema rollback when the new schema remains backward-compatible.
8. Use a forward corrective migration for any deployed destructive schema defect; do not silently edit an applied migration.
9. Never re-enable the removed legacy schema or endpoint as a rollback mechanism.

## Required tests

### Migration

- clean database migration;
- a migration already recorded in migration history is not reapplied;
- migration checksum or immutability drift is detected;
- partial migration failure rolls back;
- constraints reject invalid lifecycle and cross-project attempt states;
- obsolete bootstrap schema is not recreated.

### Repository integration

- create and project-scoped lookup;
- concurrent successful consumption produces exactly one `consumed` result;
- losing submissions receive a stable terminal result;
- concurrent rejected/transient submissions receive unique monotonic attempt numbers;
- expired challenge cannot be consumed;
- revoked challenge cannot be consumed;
- wrong-project access does not reveal challenge existence;
- request/provider/binding mismatch cannot consume;
- submission-limit transition is durable and atomic with the final attempt;
- failed transaction leaves neither a lifecycle mutation nor a partial attempt;
- state survives process restart and a second repository instance.

### Privacy and logging

- operation arguments, raw evidence, and provider tokens are absent from persisted rows;
- database and application errors redact connection strings and payloads;
- evidence references and digests remain traceable after raw evidence disposal;
- unauthorized project lookups are indistinguishable from unknown challenge IDs at the API boundary.

## Acceptance criteria

- Versioned PostgreSQL migrations create the minimal project, challenge, and attempt model.
- Production project routing resolves an authenticated internal project identity before repository access.
- Production composition uses the PostgreSQL repository; the in-memory implementation is test-only.
- Composite constraints prevent cross-project challenge/attempt records.
- Every counted submission atomically updates the challenge and records its attempt.
- One transaction atomically records a successful attempt and consumes the challenge.
- Multi-instance concurrent verification produces exactly one durable success.
- Restart, rollback, expiry, revocation, duplicate, submission-limit, and cross-project tests pass.
- No protected operation arguments, raw evidence, provider token, credential, private key, or protected configuration is persisted or logged.
- CI runs migration and PostgreSQL integration tests before merge.

## Non-goals

- Google OAuth or Play Integrity verdict interpretation;
- policy outcome evaluation;
- configuration issuance or KMS integration;
- generalized administrative APIs;
- broad telemetry or case management;
- retention periods beyond the minimum constraints required by #20;
- Cloudflare-specific persistence selection.
