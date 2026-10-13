# Synthetic Digitalis trust lifecycle illustration

This standalone **teaching model** shows how untrusted submissions, backend-side
provider verification, server-selected project policy, and protected configuration
installation must be separated. It is based on public `digitalis.v1` contracts
([protocol](../README.md), [startup outcomes](../../rfcs/rfc_0006_startup_policy_outcome_model_and_failure_handling.md)).

From the repository root:

```sh
python3 -m unittest discover -s protocol/synthetic -p '*_example.py' -v
```

The tests demonstrate synthetic acceptance only after installation, replay/expiry
and revocation denial, bounded attempts, expiry while provider work runs, version/project/operation/provider and
request-hash binding, verified application identity, server-selected policy
matching, provider failure/rejection, single-winner reservation, and\nconfiguration-installation failure (including uncertain results).

**Not security qualification.** No genuine attestation evidence, provider token
verification, cryptographic canonicalization, signatures, authenticated backend
identity, durable transactional challenge state, interleaved concurrency,
KMS, or hardware-backed configuration installation is implemented. Fake
adapters are test injections controlled by this script, **not mobile-client
fields**. The `ALLOW` value is an illustrative RFC-0006 outcome, not a
`digitalis.v1` verification API result. The current public API leaves policy
decision and configuration reference null and its configuration endpoint is
a stub. Do not use this model as production verification or evidence of
provider/device readiness.

The sample checks state again before installation but has no concurrent clock
advance or atomic compare-and-consume; production systems must enforce both.
