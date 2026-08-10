"""The typecheck scope is one value, not four agreeing copies (GHI #199 class).

GHI #199 was an ARB receipt labelled ``typecheck`` that measured a different
scope than the governance gate of the same name. The repair aligned the two
strings. It did not remove the *ability* for them to disagree: the command was
still spelled out independently in ``CANONICAL_STEP_COMMANDS``, in
``quality.run_typecheck``, in ``commands.arb.arb_typecheck_cmd``, and in the
pre-commit hook — four hand-synced copies of one fact, with nothing asserting
they agreed. That is the shape ``ADR-pool.governance-document-structural-
validation`` catalogues as *"one grammar, derived, not re-spelled"*.

Three of the four now derive. This module pins that they derive rather than
merely match: each test MUTATES the canonical entry and asserts the consumer
follows. A test that only compared the two current values would pass equally
well against two independently-spelled copies that happen to agree today —
which is exactly the state that shipped GHI #199.

The pre-commit hook is the one copy that cannot derive (YAML read by another
tool before Python runs), so it is pinned by equality instead. That asymmetry
is deliberate and is the reason this module reads the config file at all.
"""

from __future__ import annotations

import shlex
import unittest
from pathlib import Path
from unittest import mock

import yaml

from gzkit.arb.validator import CANONICAL_STEP_COMMANDS
from gzkit.commands.arb import arb_typecheck_cmd
from gzkit.quality import run_typecheck

_SENTINEL_COMMAND = ["uv", "run", "ty", "check", "sentinel-scope"]


def _pre_commit_ty_entry(repo_root: Path) -> str:
    """Return the ``entry:`` string of the ``ty-check`` hook, or "" when absent."""
    config = yaml.safe_load((repo_root / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    for repo in config.get("repos", []):
        for hook in repo.get("hooks", []):
            if hook.get("id") == "ty-check":
                return str(hook.get("entry", ""))
    return ""


class TypecheckGateDerivesFromCanon(unittest.TestCase):
    """The gate and the receipt producer READ the canonical entry."""

    def test_quality_gate_follows_a_changed_canonical_command(self) -> None:
        """Move the canonical value; the gate's argv must move with it."""
        with (
            mock.patch.dict(CANONICAL_STEP_COMMANDS, {"typecheck": _SENTINEL_COMMAND}),
            mock.patch("gzkit.quality.run_command") as runner,
        ):
            run_typecheck(Path("."))

        self.assertEqual(
            list(runner.call_args.args[0]),
            _SENTINEL_COMMAND,
            msg=(
                "run_typecheck did not follow the canonical command. It is "
                "re-spelling the scope instead of reading it, which is the "
                "GHI #199 divergence made possible again."
            ),
        )

    def test_arb_receipt_producer_follows_a_changed_canonical_command(self) -> None:
        """An ARB `typecheck` receipt must measure whatever canon declares."""
        with (
            mock.patch.dict(CANONICAL_STEP_COMMANDS, {"typecheck": _SENTINEL_COMMAND}),
            mock.patch("gzkit.commands.arb.arb_step_cmd", return_value=0) as step,
        ):
            arb_typecheck_cmd()

        self.assertEqual(
            list(step.call_args.kwargs["argv"]),
            _SENTINEL_COMMAND,
            msg=(
                "arb_typecheck_cmd did not follow the canonical command. A "
                "receipt labelled 'typecheck' would attest a scope the gate "
                "never measured — GHI #199 verbatim."
            ),
        )

    def test_gate_and_receipt_producer_agree_on_the_live_value(self) -> None:
        """Both consumers land on the same argv for the command as shipped."""
        with mock.patch("gzkit.quality.run_command") as runner:
            run_typecheck(Path("."))
        with mock.patch("gzkit.commands.arb.arb_step_cmd", return_value=0) as step:
            arb_typecheck_cmd()

        self.assertEqual(list(runner.call_args.args[0]), list(step.call_args.kwargs["argv"]))


class PreCommitHookMatchesCanon(unittest.TestCase):
    """The one copy that cannot derive is pinned by equality instead."""

    def test_pre_commit_ty_entry_equals_the_canonical_command(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        entry = _pre_commit_ty_entry(repo_root)

        self.assertNotEqual(entry, "", msg="No `ty-check` hook found in .pre-commit-config.yaml")
        self.assertEqual(
            shlex.split(entry),
            CANONICAL_STEP_COMMANDS["typecheck"],
            msg=(
                "The pre-commit `ty` hook checks a different scope than the "
                "governance gate. Developers would see one verdict locally and "
                "another at attestation — the divergence GHI #199 named, "
                "relocated to the hook that runs most often."
            ),
        )


class TypecheckScopeCoversTheOrientationHook(unittest.TestCase):
    """The scope must reach `scripts/`, which is why it was widened.

    `scripts/session_orientation.py` runs on every SessionStart, before the
    agent's first response. Under the `src`-only scope it carried five live
    diagnostics that no gate could see, including a `call-non-callable`. This
    asserts the *reason* for the widening, so a future narrowing back to `src`
    fails here with the motivation attached rather than silently re-blinding
    the hook.
    """

    def test_canonical_scope_is_not_restricted_to_src(self) -> None:
        command = CANONICAL_STEP_COMMANDS["typecheck"]
        self.assertNotIn(
            "src",
            command,
            msg=(
                "The typecheck scope was narrowed back to `src`, which leaves "
                "scripts/session_orientation.py structurally unchecked."
            ),
        )
        self.assertIn(".", command)

    def test_features_stays_excluded(self) -> None:
        """`behave` step functions annotate `context` attributes; ty rejects that."""
        command = CANONICAL_STEP_COMMANDS["typecheck"]
        self.assertIn("--exclude", command)
        pattern = command[command.index("--exclude") + 1]
        self.assertIn("features", pattern)

    def test_the_exclude_is_spelled_so_it_fires_on_every_platform(self) -> None:
        """A `**` glob silently excludes nothing on Windows.

        `ty` reports paths with the platform separator (`features\\steps\\foo.py`),
        so a forward-slash glob never matches and every in-`features` diagnostic
        reaches the gate — `gz check` fails on a tree CI just passed. Measured
        2026-08-09: bare `features` exits 0 while `features/**`, `./features/**`,
        `**/features/**` and `features/**/*.py` all exit 1.

        Asserted as a property of the SPELLING rather than as the old literal,
        because the literal was the defect. `.gzkit/rules/cross-platform.md`
        holds Windows, macOS and Linux co-equal, so a gate that is green on one
        and red on another is broken, not merely unlucky.
        """
        command = CANONICAL_STEP_COMMANDS["typecheck"]
        pattern = command[command.index("--exclude") + 1]
        self.assertNotIn(
            "*",
            pattern,
            msg=(
                f"typecheck exclude {pattern!r} uses a glob; globs with a path "
                "separator do not match on Windows. Use the bare directory name."
            ),
        )


if __name__ == "__main__":
    unittest.main()
