"""Negative controls must discriminate the claim they name (GHI #699).

The enforcement-floor audit reported 47/47 verified while 32 of those negative
controls could not distinguish "the enforcement caught the violation" from
"something unrelated went wrong". These tests pin the discrimination contract
itself, so a future coarsening of the signal fails here rather than shipping as
a green floor.

Semantics under test (derived from the campaign plan
``docs/governance/build-to-1.0-campaign-2026-06-30.md`` §5, clauses (b) and (c)):
a negative control must run the real path in its **production** configuration
and assert it fails **for the reason the claim names**.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


class TestCommandFailsDiscriminatesExitCode(unittest.TestCase):
    """A subprocess NC must not score a launch failure as a caught violation.

    §5 clause (c): the control asserts the production path *fails* — but a tool
    that never ran did not fail, it was absent. Scoring both as "caught" makes
    the control unable to detect that the enforcement was removed entirely.
    """

    def test_missing_binary_is_not_a_caught_violation(self) -> None:
        """A command that cannot launch (returncode -1) must score as NOT caught."""
        from gzkit.governance.trust_audits._qc_nc_entrypoints import _command_fails

        root = Path(tempfile.mkdtemp(prefix="gzkit-nc-discrim-"))
        signal = _command_fails("gzkit-no-such-binary-deadbeef", root, expected_exit=1)

        self.assertEqual(
            signal,
            0,
            "A tool that failed to launch (returncode -1) must NOT be scored as "
            "having caught the violation. Scoring any non-zero exit as 'caught' "
            "means deleting the enforcement entirely leaves the NC green "
            "(GHI #699 generator #1).",
        )

    def test_expected_exit_code_is_a_caught_violation(self) -> None:
        """The documented violation exit code must score as caught."""
        from gzkit.governance.trust_audits._qc_nc_entrypoints import _command_fails

        root = Path(tempfile.mkdtemp(prefix="gzkit-nc-discrim-"))
        (root / "pyproject.toml").write_text(
            "[project]\nname = 'x'\nversion = '0.0.0'\n", encoding="utf-8"
        )
        (root / "bad.py").write_text("import sys\n", encoding="utf-8")

        signal = _command_fails("uv run ruff check .", root, expected_exit=1)

        self.assertEqual(
            signal,
            1,
            "ruff exits 1 on a lint violation; that is the claim's documented "
            "catch signal and must score as caught.",
        )

    def test_clean_tree_is_not_a_caught_violation(self) -> None:
        """The second pole: a clean project must NOT trip the control."""
        from gzkit.governance.trust_audits._qc_nc_entrypoints import _command_fails

        root = Path(tempfile.mkdtemp(prefix="gzkit-nc-discrim-clean-"))
        (root / "pyproject.toml").write_text(
            "[project]\nname = 'x'\nversion = '0.0.0'\n", encoding="utf-8"
        )
        (root / "good.py").write_text('"""Doc."""\n', encoding="utf-8")

        signal = _command_fails("uv run ruff check .", root, expected_exit=1)

        self.assertEqual(
            signal,
            0,
            "A guard that fires on a clean tree is as broken as one that never "
            "fires; only this pole catches it.",
        )


class TestSubprocessEntrypointsExerciseTheWorkingTree(unittest.TestCase):
    """§5 clause (b): the control must run the path in its production configuration.

    A ``uv run gz ...`` subprocess launched from a scratch directory resolves
    ``gz`` from whatever is on PATH — under a bare (non-``uv run``) invocation
    that is the installed wheel at ``~/.local/bin/gz``, not ``src/gzkit/``.
    Gutting the working tree then leaves the control green.

    The fix is not to pin PATH but to stop shelling out: a gz-owned check is a
    Python callable and must be invoked as one, which makes the working tree
    definitionally the code under test.
    """

    #: Claims whose enforcement lives in gzkit's own Python, not an external tool.
    GZ_OWNED_CLAIMS = (
        "skill-audit",
        "readiness-audit",
        "cli-audit",
        "preflight",
        "parity-check",
    )

    def test_gz_owned_claims_do_not_shell_out(self) -> None:
        """gz-owned NC entrypoints must call production Python, not `uv run gz`."""
        import inspect

        from gzkit.governance.trust_audits import _qc_negative_controls as ncs

        table = {claim: ep for claim, _fx, ep in ncs._QC_NEGATIVE_CONTROL_TABLE}

        offenders: list[str] = []
        for claim in self.GZ_OWNED_CLAIMS:
            entrypoint = table[claim]
            source = inspect.getsource(entrypoint)
            if "uv run gz" in source:
                offenders.append(claim)

        self.assertEqual(
            offenders,
            [],
            "These NC entrypoints shell out to `uv run gz`, which resolves to the "
            "installed wheel rather than src/gzkit/ — gutting the working tree "
            "leaves them green (GHI #699 generator #5). Invoke the production "
            f"Python callable directly instead. Offenders: {offenders}",
        )


if __name__ == "__main__":
    unittest.main()
