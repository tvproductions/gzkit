"""Commit authorship must be provable inside the repo it protects (GHI #725).

`AGENTS.md` § Local Agent Rules forbids the operator's personal email in any
repo-bound artifact, and names the recovery: a filter-repo rewrite plus a
force-push. Until now the only thing standing between that rule and a violation
was a hand-added `--local` git config override in one clone. A fresh clone, a
worktree, a second machine, or a CI checkout that commits reverts to global
config and the rule is broken silently — detectable only after the commit exists.

The guard detects rather than configures: writing to an operator's git config is
what `src/gzkit/commands/init_cmd.py:467` declines to do. It is also OFF by
default, because a gzkit-shaped identity policy imposed on every adopter is the
dogfooding-leak complaint open at GHI #607.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.config import GzkitConfig
from gzkit.governance.trust_audits.authorship import audit_authorship, evaluate_authorship
from tests.commands.common import _isolated_git_env

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class AuthorshipPolicyIsOptIn(unittest.TestCase):
    """An undeclared policy must not impose gzkit's identity rules on adopters."""

    def test_no_policy_declared_admits_any_address(self) -> None:
        self.assertEqual(evaluate_authorship("someone@example.com", None), [])

    def test_no_policy_declared_admits_a_missing_address(self) -> None:
        """An adopter with no git identity yet is not violating a rule they never set."""
        self.assertEqual(evaluate_authorship(None, None), [])


class AuthorshipPolicyFailsClosed(unittest.TestCase):
    """A declared policy binds, and says how to recover."""

    _SUFFIX = "@users.noreply.github.com"

    def test_matching_address_passes(self) -> None:
        self.assertEqual(evaluate_authorship("123456+handle" + self._SUFFIX, self._SUFFIX), [])

    def test_non_matching_address_fails(self) -> None:
        errors = evaluate_authorship("operator@personal-mail.example", self._SUFFIX)
        self.assertEqual(len(errors), 1, msg="one policy, one finding")

    def test_absent_address_fails_when_a_policy_is_declared(self) -> None:
        """Unset identity resolves to whatever global config holds at commit time."""
        errors = evaluate_authorship(None, self._SUFFIX)
        self.assertEqual(len(errors), 1)

    def test_the_violating_address_is_never_echoed(self) -> None:
        """The finding must not reproduce the PII it exists to keep out of the repo.

        A validator that prints the personal address writes it into CI logs and
        ARB receipts — reproducing the leak while reporting it.
        """
        secret = "operator@personal-mail.example"
        message = evaluate_authorship(secret, self._SUFFIX)[0].message
        self.assertNotIn(secret, message)
        self.assertNotIn("personal-mail", message)

    def test_finding_carries_three_part_recovery_prose(self) -> None:
        """`.gzkit/rules/guardrail-feedback-prose.md`: what failed, why, next step."""
        message = evaluate_authorship("operator@personal-mail.example", self._SUFFIX)[0].message
        self.assertIn(self._SUFFIX, message, msg="what failed: the expected shape")
        self.assertIn("AGENTS.md", message, msg="why: the cited binding rule")
        self.assertIn("git config --local user.email", message, msg="next step: runnable")


class DeclaredPolicyReachesTheAudit(unittest.TestCase):
    """The adapter must actually read the policy and the identity.

    Without these, `ThisRepositoryIsGuarded` alone is tautological: it returns
    `[]` both when the guard works and when the policy never loads. That is
    exactly how the first implementation shipped green — `GzkitConfig.load`
    selected keys from a hand-copied list that predated `authorship`, so the
    declared policy was silently discarded and the audit could never fire.
    """

    def _project(self, root: Path, config: dict) -> None:
        (root / ".gzkit.json").write_text(json.dumps(config), encoding="utf-8")

    def test_declared_suffix_survives_config_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._project(root, {"authorship": {"required_email_suffix": "@example.invalid"}})
            loaded = GzkitConfig.load(root / ".gzkit.json")
        self.assertEqual(loaded.authorship.required_email_suffix, "@example.invalid")

    def test_violating_identity_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._project(root, {"authorship": {"required_email_suffix": "@example.invalid"}})
            with mock.patch(
                "gzkit.governance.trust_audits.authorship._effective_email",
                return_value="someone@elsewhere.test",
            ):
                errors = audit_authorship(root)
        # Both stamped identities are judged, author and committer (GHI #1340).
        self.assertEqual([e.artifact for e in errors], ["commit author", "commit committer"])

    def test_compliant_identity_is_admitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._project(root, {"authorship": {"required_email_suffix": "@example.invalid"}})
            with mock.patch(
                "gzkit.governance.trust_audits.authorship._effective_email",
                return_value="someone@example.invalid",
            ):
                errors = audit_authorship(root)
        self.assertEqual(errors, [])

    def test_undeclared_policy_never_consults_git(self) -> None:
        """No policy means no identity lookup — an adopter pays nothing for the scope."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._project(root, {"project_name": "adopter"})
            with mock.patch("gzkit.governance.trust_audits.authorship._effective_email") as lookup:
                errors = audit_authorship(root)
        self.assertEqual(errors, [])
        lookup.assert_not_called()


_SUFFIX = "@users.noreply.github.com"


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(  # noqa: S603 — git argv this test builds
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_isolated_git_env(),
    )


def _compliant_repo(tmp: str) -> Path:
    """Return a repository whose CONFIG identity satisfies the declared policy."""
    root = Path(tmp)
    _git(["init", "-q", "-b", "main"], root)
    _git(["config", "user.email", f"g0{_SUFFIX}"], root)
    _git(["config", "user.name", "g0"], root)
    (root / ".gzkit.json").write_text(
        json.dumps({"authorship": {"required_email_suffix": _SUFFIX}}), encoding="utf-8"
    )
    return root


class TheIdentityACommitStampsIsTheOneJudged(unittest.TestCase):
    """The guard reads the identity git will stamp, not the configured one (GHI #1340).

    git takes a commit's author from `--author`, `GIT_AUTHOR_EMAIL` or the amended
    commit, and its committer from `GIT_COMMITTER_EMAIL`, before it reads config.
    These run real git: a stubbed lookup cannot show which address git resolves.
    """

    def _audit(self, root: Path, **env: str) -> list[str]:
        with mock.patch.dict(os.environ, env):
            return [error.artifact for error in audit_authorship(root)]

    def test_a_compliant_identity_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._audit(_compliant_repo(tmp)), [])

    def test_an_author_override_that_violates_the_policy_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifacts = self._audit(_compliant_repo(tmp), GIT_AUTHOR_EMAIL="a@example.com")
        self.assertEqual(artifacts, ["commit author"])

    def test_a_committer_override_that_violates_the_policy_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifacts = self._audit(_compliant_repo(tmp), GIT_COMMITTER_EMAIL="c@example.com")
        self.assertEqual(artifacts, ["commit committer"])

    def test_the_refusal_names_the_identity_and_the_override_to_drop(self) -> None:
        # output-contract: three-part recovery prose (guardrail-feedback-prose.md).
        with tempfile.TemporaryDirectory() as tmp:
            root = _compliant_repo(tmp)
            with mock.patch.dict(os.environ, {"GIT_AUTHOR_EMAIL": "a@example.com"}):
                (error,) = audit_authorship(root)
        self.assertIn("commit author address", error.message)
        self.assertIn("`--author`", error.message)
        self.assertIn("GIT_AUTHOR_EMAIL", error.message)
        self.assertNotIn("a@example.com", error.message)

    def test_a_commit_made_with_a_violating_author_flag_is_refused_at_the_hook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _compliant_repo(tmp)
            hook = root / ".git" / "hooks" / "pre-commit"
            hook.write_text(
                "#!/bin/sh\n"
                f'exec "{sys.executable}" -c "import sys; from pathlib import Path; '
                "from gzkit.governance.trust_audits.authorship import audit_authorship; "
                'sys.exit(1 if audit_authorship(Path.cwd()) else 0)"\n',
                encoding="utf-8",
            )
            hook.chmod(0o755)
            (root / "a.txt").write_text("a\n", encoding="utf-8")
            _git(["add", "a.txt"], root)
            refused = subprocess.run(
                ["git", "commit", "-q", "--author", "X <x@example.com>", "-m", "x"],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=_isolated_git_env(),
            )
        self.assertNotEqual(refused.returncode, 0)


class ThisRepositoryIsGuarded(unittest.TestCase):
    """gzkit itself declares the policy, so the guard is armed where it originated."""

    def test_live_repository_passes_its_own_authorship_audit(self) -> None:
        errors = audit_authorship(_PROJECT_ROOT)
        self.assertEqual(
            errors,
            [],
            msg=(
                "This clone's effective git identity violates the declared authorship "
                "policy. Commits from it would carry the address AGENTS.md forbids.\n"
                + "\n".join(f"  {e.artifact}: {e.message}" for e in errors)
            ),
        )


if __name__ == "__main__":
    unittest.main()
