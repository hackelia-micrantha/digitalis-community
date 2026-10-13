# Synthetic Digitalis lifecycle illustration

This is a **standalone educational model** of the public `digitalis.v1` request-binding and challenge lifecycle constraints described by [the public protocol](../README.md) and [startup-outcome RFC](../../rfcs/rfc_0006_startup_policy_outcome_model_and_failure_handling.md). Run with:

```sh
python3 -m unittest discover -s protocol/synthetic -p '*_example.py' -v
```

It covers an invented successful case, replay, expiry, changed project, operation, provider, request binding, incompatible version, simulated provider rejection, policy denial and simulated signed-configuration failure. In every negative case protected configuration stays disabled.

**Not a working attestation implementation:** there is no provider token, signature verification, real request canonicalization, backend authorization, durable challenge storage, atomic multi-instance consumption, attested app identity, key management, or actual configuration activation. The fixed request hash and boolean inputs are intentionally artificial. In the actual public protocol the configuration endpoint is a stub and verification does not yet return a policy decision or configuration reference. No result from this example is an attestation, security or integration qualification.
