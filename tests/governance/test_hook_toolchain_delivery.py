"""The project delivers every tool its hooks need; the machine supplies none (GHI #1330).

A clone reset on 2026-11-19 had no hook files, no ``pre-commit`` and no ``gitleaks``.
The delivery check's recovery, ``uv run pre-commit install``, could not run, because
pre-commit was in no dependency group, and the secrets hook needed a system binary
nothing installs. Operator, 2026-11-19, verbatim: "these are troubling because if
they live at the machine level then we have a failing of gzkit's installation".
Rulings the same day, by selection: pre-commit becomes a dev dependency, and
gitleaks moves to the upstream gitleaks pre-commit hook.

Canonical: https://pre-commit.com/#golang ("pre-commit will bootstrap `go` if it is
not present", new in 3.0.0); https://github.com/gitleaks/gitleaks
``.pre-commit-hooks.yaml`` (hook ``gitleaks``, ``language: golang``).
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands import init_cmd
from gzkit.governance.trust_audits.session_green_gate import (
    audit_session_green_gate,
    declared_hook_entries,
    declared_hook_types,
    install_recovery,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

#: A local hook's executable is the project's when it runs through ``uv`` (the
#: project environment `uv sync` builds) or is a script the repository carries.
_PROJECT_RUNNERS = frozenset({"uv"})

#: Executables a local hook may take from the machine, each with its reason.
_MACHINE_EXECUTABLES = {
    "bash": "the TODO/FIXME scan's shell; informational, `|| true`, never gates",
}

_GATE_CONFIG = """\
repos:
  - repo: local
    hooks:
      - id: gz-check-pre-push
        name: gz check
        entry: uv run gz check
        language: unsupported
        pass_filenames: false
        stages: [pre-push]
"""


def _own_entry_executables() -> dict[str, str]:
    """Return each hook's executable, as the gate reads the hooks.

    A hook a remote repo defines carries no entry of its own (``declared_hook_entries``
    reads it as empty): pre-commit installs what it runs, so it needs nothing here.

    Returns:
        The first word of each hook's own entry, by hook id; remote hooks omitted.

    """
    return {
        hook_id: entry.split()[0]
        for hook_id, entry in declared_hook_entries(REPO_ROOT).items()
        if entry.strip()
    }


class TestNoHookNeedsAMachineBinary(unittest.TestCase):
    def test_every_hook_runs_a_project_delivered_executable(self):
        for hook_id, executable in _own_entry_executables().items():
            with self.subTest(hook=hook_id):
                delivered = executable in _PROJECT_RUNNERS or (REPO_ROOT / executable).is_file()
                self.assertTrue(
                    delivered or executable in _MACHINE_EXECUTABLES,
                    f"{hook_id} runs `{executable}`, which neither `uv sync` nor the "
                    "repository delivers; route it through a pre-commit repo or `uv run`",
                )

    def test_the_secrets_scanner_comes_from_its_hook_repo(self):
        entries = declared_hook_entries(REPO_ROOT)
        self.assertIn("gitleaks", entries)
        self.assertEqual(entries["gitleaks"], "", "gitleaks names its own executable")

    def test_the_machine_exceptions_name_only_live_hooks(self):
        used = set(_own_entry_executables().values())
        self.assertEqual(sorted(set(_MACHINE_EXECUTABLES) - used), [])


class TestTheRecoveryCanRunOnAFreshMachine(unittest.TestCase):
    """The printed recovery names how to obtain pre-commit, not only how to run it."""

    def _unhooked_worktree(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / ".git" / "hooks").mkdir(parents=True)
        (root / ".pre-commit-config.yaml").write_text(_GATE_CONFIG, encoding="utf-8")
        return root

    def test_the_recovery_obtains_pre_commit_before_installing(self):
        recovery = install_recovery(["pre-commit", "pre-push"])
        self.assertIn("uv sync", recovery)
        self.assertIn("uv tool install pre-commit", recovery)
        self.assertIn("pre-commit install --hook-type pre-commit --hook-type pre-push", recovery)

    def test_the_delivery_finding_carries_that_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._unhooked_worktree(tmp)
            findings = audit_session_green_gate(root, check_delivery=True)
            expected = install_recovery(declared_hook_types(root))
        self.assertTrue(findings)
        for finding in findings:
            self.assertIn(expected, finding.message)

    def test_gz_init_names_the_same_recovery_when_no_installer_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._unhooked_worktree(tmp)
            with mock.patch.object(init_cmd.subprocess, "run", side_effect=OSError("absent")):
                status = init_cmd._install_pre_commit_hooks(root)
            expected = install_recovery(declared_hook_types(root))
        self.assertIsNotNone(status)
        self.assertIn(expected, status or "")

    def test_a_hooks_path_redirect_names_the_same_recovery(self):
        """pre-commit refuses while `core.hooksPath` is set; the message still says how to recover.

        Driven by the `gz arb red --commit 6f35e85ac` run, whose revert of this branch's
        recovery left every test passing (receipt
        arb-red-commit-6f35e85acca9-c29ec0590e0044b09a6ff718ca03b91a).
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = self._unhooked_worktree(tmp)
            (root / ".git" / "config").write_text(
                "[core]\n\thooksPath = elsewhere\n", encoding="utf-8"
            )
            status = init_cmd._install_pre_commit_hooks(root)
            expected = install_recovery(declared_hook_types(root))
        self.assertIn("core.hooksPath", status or "")
        self.assertIn(expected, status or "")

    def test_gz_init_never_installs_hooks_from_an_ephemeral_environment(self):
        """Hooks installed by `uvx pre-commit` point into uv's cache, which a prune deletes.

        That is a machine-level dependency the hooks cannot survive, the class GHI #1330
        names, and a locked tool run outside the lock (`gz validate --astral-discipline`).
        """
        tried: list[list[str]] = []

        def refuse(argv: list[str], **_kwargs: object) -> None:
            tried.append(argv)
            message = "absent"
            raise OSError(message)

        with tempfile.TemporaryDirectory() as tmp:
            root = self._unhooked_worktree(tmp)
            with mock.patch.object(init_cmd.subprocess, "run", side_effect=refuse):
                init_cmd._install_pre_commit_hooks(root)
        self.assertTrue(tried)
        self.assertFalse([argv for argv in tried if Path(argv[0]).name.startswith("uvx")])

    def test_the_project_environment_carries_the_installer(self):
        """The control: `uv sync` put pre-commit in this environment, not the machine's PATH.

        Searched in the running interpreter's own scripts directory only, so a
        machine-wide install (``uv tool install pre-commit``) cannot satisfy it.
        """
        scripts = Path(sys.executable).parent
        self.assertIsNotNone(shutil.which("pre-commit", path=str(scripts)), scripts.as_posix())
