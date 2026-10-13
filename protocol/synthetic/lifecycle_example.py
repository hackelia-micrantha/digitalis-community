#!/usr/bin/env python3
"""Synthetic Digitalis challenge lifecycle *teaching model*, not a verifier.

All evidence here is invented. This code does not implement an attestation
provider, cryptographic request canonicalization, policy authority, or KMS.
"""
from dataclasses import dataclass
import unittest

VERSION = "digitalis.v1"
PROJECT = "11111111-1111-4111-8111-111111111111"
OPERATION = "configuration.bootstrap"
PROVIDER = "google_play_integrity"
HASH = "A" * 43  # synthetic fixed binding, NOT a digest
NOW = 1000


@dataclass
class Challenge:
    version: str = VERSION
    project: str = PROJECT
    operation: str = OPERATION
    provider: str = PROVIDER
    bound_hash: str = HASH
    expires_at: int = NOW + 120
    consumed: bool = False


@dataclass(frozen=True)
class Submission:
    version: str = VERSION
    project: str = PROJECT
    operation: str = OPERATION
    provider: str = PROVIDER
    reconstructed_hash: str = HASH
    synthetic_provider_accepts: bool = True
    synthetic_policy_allows: bool = True
    synthetic_config_signature_valid: bool = True


def evaluate(challenge: Challenge, submission: Submission, now: int) -> tuple[str, bool]:
    """Return a public RFC-style outcome and whether protected config may activate.

    Simulated provider/policy/config flags are NOT authoritative proof. The
    educational state machine is deliberately fail-closed and side-effect free.
    """
    if challenge.consumed or now >= challenge.expires_at:
        return "DENY_INTEGRITY", False
    if submission.provider not in ("google_play_integrity", "apple_app_attest"):
        return "UNSUPPORTED_ENVIRONMENT", False
    if (submission.version, submission.project, submission.operation, submission.provider,
        submission.reconstructed_hash) != (
        challenge.version, challenge.project, challenge.operation, challenge.provider,
        challenge.bound_hash
    ):
        return "DENY_INTEGRITY", False
    if not submission.synthetic_provider_accepts:
        return "DENY_INTEGRITY", False
    if not submission.synthetic_policy_allows:
        return "DENY_POLICY", False
    if not submission.synthetic_config_signature_valid:
        return "DENY_INTEGRITY", False
    challenge.consumed = True
    return "ALLOW", True


class SyntheticLifecycleExamples(unittest.TestCase):
    def assert_denied(self, submission: Submission, *, now: int = NOW, challenge=None):
        c = challenge or Challenge()
        outcome, enabled = evaluate(c, submission, now)
        self.assertNotEqual(outcome, "ALLOW")
        self.assertFalse(enabled)
        self.assertFalse(c.consumed)

    def test_synthetic_happy_path_and_replay(self):
        c = Challenge()
        self.assertEqual(evaluate(c, Submission(), NOW), ("ALLOW", True))
        self.assertEqual(evaluate(c, Submission(), NOW), ("DENY_INTEGRITY", False))

    def test_expiry_boundary(self):
        self.assert_denied(Submission(), now=NOW + 120)

    def test_project_binding(self):
        self.assert_denied(Submission(project="22222222-2222-4222-8222-222222222222"))

    def test_operation_binding(self):
        self.assert_denied(Submission(operation="configuration.other"))

    def test_provider_binding(self):
        self.assert_denied(Submission(provider="apple_app_attest"))

    def test_request_hash_binding(self):
        self.assert_denied(Submission(reconstructed_hash="B" * 43))

    def test_contract_version(self):
        self.assert_denied(Submission(version="digitalis.v2"))

    def test_unsupported_provider(self):
        c = Challenge()
        self.assertEqual(evaluate(c, Submission(provider="unsupported"), NOW), ("UNSUPPORTED_ENVIRONMENT", False))
        self.assertFalse(c.consumed)

    def test_provider_rejection(self):
        self.assert_denied(Submission(synthetic_provider_accepts=False))

    def test_policy_denial(self):
        self.assert_denied(Submission(synthetic_policy_allows=False))

    def test_configuration_integrity_denial(self):
        self.assert_denied(Submission(synthetic_config_signature_valid=False))


if __name__ == "__main__":
    unittest.main()
