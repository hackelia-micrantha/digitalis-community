#!/usr/bin/env python3
"""Synthetic trust-boundary demonstration; never verifies real attestation."""
from dataclasses import dataclass
from typing import Protocol
import unittest

VERSION = "digitalis.v1"
PROJECT = "11111111-1111-4111-8111-111111111111"
OPERATION = "configuration.bootstrap"
PROVIDER = "google_play_integrity"
APP = "com.example.synthetic"
HASH = "A" * 43  # invented placeholder, NOT a request digest
NOW = 1000


@dataclass(frozen=True)
class Submission:
    version: str = VERSION
    project: str = PROJECT
    operation: str = OPERATION
    provider: str = PROVIDER
    claimed_app: str = APP
    request_hash: str = HASH


@dataclass(frozen=True)
class VerifiedEvidence:
    """Result produced only by a backend-side provider verifier adapter."""
    reconstructed_hash: str
    verified_app: str


@dataclass(frozen=True)
class ProjectPolicy:
    """Configuration resolved on the backend, never supplied by the client."""
    version: str = "policy-1"
    project: str = PROJECT
    operation: str = OPERATION
    provider: str = PROVIDER
    app: str = APP


@dataclass
class Challenge:
    project: str = PROJECT
    operation: str = OPERATION
    provider: str = PROVIDER
    policy_version: str = "policy-1"
    bound_hash: str = HASH
    expires_at: int = NOW + 120
    submissions: int = 0
    max_submissions: int = 3
    consumed: bool = False
    revoked: bool = False


class ProviderVerifier(Protocol):
    def verify(self, submission: Submission) -> VerifiedEvidence | None: ...


class PolicyAuthority(Protocol):
    def resolve(self, project: str) -> ProjectPolicy | None: ...


class ConfigInstaller(Protocol):
    def install(self, policy: ProjectPolicy) -> bool: ...


class FakeProvider:
    """Injectable synthetic backend adapter, not client supplied evidence."""
    def __init__(self, result=VerifiedEvidence(HASH, APP)):
        self.result = result

    def verify(self, submission):
        return self.result


class FakePolicy:
    def __init__(self, result=ProjectPolicy()):
        self.result = result

    def resolve(self, project):
        return self.result


class FakeInstaller:
    def __init__(self, succeeds=True):
        self.succeeds = succeeds
        self.calls = 0

    def install(self, policy):
        self.calls += 1
        return self.succeeds


def evaluate(challenge: Challenge, submission: Submission, now: int,
             provider: ProviderVerifier, policy: PolicyAuthority,
             installer: ConfigInstaller) -> tuple[str, bool]:
    """Return illustrative RFC-0006 startup outcome and protected-feature gate.

    All adapters are trusted *simulation seams*. Actual systems must authenticate
    backend authority, atomically consume durable challenges, and verify configs.
    """
    if challenge.consumed or challenge.revoked or now >= challenge.expires_at:
        return "DENY_INTEGRITY", False
    if challenge.submissions >= challenge.max_submissions:
        return "DENY_INTEGRITY", False
    if submission.provider not in ("google_play_integrity", "apple_app_attest"):
        return "UNSUPPORTED_ENVIRONMENT", False
    if (submission.version, submission.project, submission.operation,
        submission.provider, submission.request_hash) != (
        VERSION, challenge.project, challenge.operation,
        challenge.provider, challenge.bound_hash):
        return "DENY_INTEGRITY", False

    # No client-provided booleans control verification, policy, or installation.
    challenge.submissions += 1
    try:
        verified = provider.verify(submission)
    except Exception:
        return "RETRYABLE_FAILURE", False
    if verified is None or verified.reconstructed_hash != challenge.bound_hash:
        return "DENY_INTEGRITY", False
    if verified.verified_app != submission.claimed_app:
        return "DENY_INTEGRITY", False

    try:
        resolved = policy.resolve(challenge.project)
    except Exception:
        return "DENY_POLICY", False
    if resolved is None or (
        resolved.version, resolved.project, resolved.operation,
        resolved.provider, resolved.app
    ) != (
        challenge.policy_version, challenge.project, challenge.operation,
        challenge.provider, verified.verified_app
    ):
        return "DENY_POLICY", False

    # A real implementation rechecks state under a transaction after async work.
    if challenge.revoked or challenge.consumed or now >= challenge.expires_at:
        return "DENY_INTEGRITY", False

    try:
        installed = installer.install(resolved)
    except Exception:
        return "DENY_INTEGRITY", False
    if not installed:
        return "DENY_INTEGRITY", False
    challenge.consumed = True
    return "ALLOW", True


class SyntheticLifecycleExamples(unittest.TestCase):
    def setUp(self):
        self.challenge = Challenge()
        self.installer = FakeInstaller()

    def run_case(self, submission=None, provider=None, policy=None, now=NOW):
        return evaluate(self.challenge, submission or Submission(), now,
                        provider or FakeProvider(), policy or FakePolicy(),
                        self.installer)

    def assert_blocked(self, expected, submission=None, provider=None, policy=None, now=NOW):
        self.assertEqual(self.run_case(submission, provider, policy, now), (expected, False))
        self.assertEqual(self.installer.calls, 0)
        self.assertFalse(self.challenge.consumed)

    def test_success_requires_install_then_replay_denied(self):
        self.assertEqual(self.run_case(), ("ALLOW", True))
        self.assertEqual(self.installer.calls, 1)
        self.assertEqual(self.run_case(), ("DENY_INTEGRITY", False))
        self.assertEqual(self.installer.calls, 1)

    def test_expiry_boundary(self):
        self.assert_blocked("DENY_INTEGRITY", now=NOW + 120)

    def test_revoked(self):
        self.challenge.revoked = True
        self.assert_blocked("DENY_INTEGRITY")

    def test_submission_limit(self):
        self.challenge.submissions = self.challenge.max_submissions
        self.assert_blocked("DENY_INTEGRITY")

    def test_project_binding(self):
        self.assert_blocked("DENY_INTEGRITY", Submission(project="other"))

    def test_operation_binding(self):
        self.assert_blocked("DENY_INTEGRITY", Submission(operation="configuration.other"))

    def test_provider_binding(self):
        self.assert_blocked("DENY_INTEGRITY", Submission(provider="apple_app_attest"))

    def test_unsupported_provider(self):
        self.assert_blocked("UNSUPPORTED_ENVIRONMENT", Submission(provider="unsupported"))

    def test_request_binding(self):
        self.assert_blocked("DENY_INTEGRITY", Submission(request_hash="B" * 43))

    def test_version_binding(self):
        self.assert_blocked("DENY_INTEGRITY", Submission(version="digitalis.v2"))

    def test_missing_provider_evidence(self):
        self.assert_blocked("DENY_INTEGRITY", provider=FakeProvider(None))

    def test_provider_hash_mismatch(self):
        self.assert_blocked("DENY_INTEGRITY", provider=FakeProvider(VerifiedEvidence("B" * 43, APP)))

    def test_app_identity_mismatch(self):
        self.assert_blocked("DENY_INTEGRITY", provider=FakeProvider(VerifiedEvidence(HASH, "bad.app")))

    def test_policy_adapter_exception_denies(self):
        class BrokenPolicy:
            def resolve(self, project):
                raise RuntimeError("synthetic policy outage")
        self.assert_blocked("DENY_POLICY", policy=BrokenPolicy())

    def test_policy_denial(self):
        self.assert_blocked("DENY_POLICY", policy=FakePolicy(None))

    def test_stale_policy_version(self):
        self.assert_blocked("DENY_POLICY", policy=FakePolicy(ProjectPolicy(version="old")))

    def test_install_failure(self):
        self.installer.succeeds = False
        self.assertEqual(self.run_case(), ("DENY_INTEGRITY", False))
        self.assertFalse(self.challenge.consumed)

    def test_provider_exception_bounded_attempts(self):
        class FailingProvider:
            def verify(self, submission):
                raise TimeoutError("synthetic outage")
        failing = FailingProvider()
        for _ in range(3):
            self.assert_blocked("RETRYABLE_FAILURE", provider=failing)
        self.assertEqual(self.challenge.submissions, 3)
        self.assert_blocked("DENY_INTEGRITY", provider=failing)


if __name__ == "__main__":
    unittest.main()
