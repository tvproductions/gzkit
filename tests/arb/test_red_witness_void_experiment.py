"""The RED witness must not report a verdict when its experiment never ran (GHI #839).

``gz arb red`` reconstructs the base tree, copies in ONLY the test files, and runs
the covering test there. The premise is that the implementation under test is
ABSENT from that tree -- that asymmetry IS the experiment. The premise is not a
given: ``resolve_base_commit`` returns HEAD, so the moment the production code
lands, the base tree already contains it, nothing is withheld, every covering test
passes, and ``classify_failure(0, ...)`` returns ``none`` -- the code for "your test
is hollow".

So the witness reported a confident accusation against tests that are fine, and the
remedy it named ("rewrite the test") would have damaged them. A ``none`` that means
"I could not run the experiment" must not share a name with a ``none`` that means
"your test cannot fail".

The premise fails in THREE ways, only one of which the filing issue named:

1. Work fully landed -- no production diff, no test diff.
2. Production landed, tests still uncommitted -- the case a fix keyed on
   ``changed_test_files`` would still get wrong, because that list is NON-empty
   while the production code is present anyway.
3. A caller passing an explicit ``base_commit`` that already carries the code.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from gzkit.red_witness import (
    RedWitness,
    resolve_base_commit,
    run_red_witness,
    withheld_production_files,
)

_IMPL = "VALUE = 1\n"
_TEST = (
    "import unittest\n\n\n"
    "class T(unittest.TestCase):\n"
    "    def test_v(self) -> None:\n"
    "        self.assertEqual(1, 1)\n"
)


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _repo() -> Path:
    """A one-commit repo carrying a production module and its test."""
    root = Path(tempfile.mkdtemp(prefix="gzkit-red839-"))
    _git(["init", "-q", "-b", "main"], root)
    _git(["config", "user.email", "g0@users.noreply.github.com"], root)
    _git(["config", "user.name", "g0"], root)
    (root / "src").mkdir()
    (root / "tests").mkdir()
    (root / "src" / "impl.py").write_text(_IMPL, encoding="utf-8")
    (root / "tests" / "test_impl.py").write_text(_TEST, encoding="utf-8")
    _git(["add", "-A"], root)
    _git(["commit", "-qm", "base"], root)
    return root


class TestWithheldProductionFiles(unittest.TestCase):
    """The premise check answers 'was anything actually withheld', not 'did tests change'."""

    def test_landed_work_withholds_nothing(self) -> None:
        root = _repo()
        self.assertEqual(
            withheld_production_files(root, resolve_base_commit(root)),
            [],
            "with the work committed, the base tree IS the implemented tree",
        )

    def test_uncommitted_tests_alone_still_withhold_nothing(self) -> None:
        root = _repo()
        (root / "tests" / "test_extra.py").write_text(_TEST, encoding="utf-8")
        self.assertEqual(
            withheld_production_files(root, resolve_base_commit(root)),
            [],
            "a changed TEST file does not put the production code back in the base "
            "tree -- keying the check on changed tests would miss this case",
        )

    def test_modified_production_is_withheld(self) -> None:
        root = _repo()
        (root / "src" / "impl.py").write_text("VALUE = 2\n", encoding="utf-8")
        self.assertEqual(
            withheld_production_files(root, resolve_base_commit(root)),
            [Path("src/impl.py")],
            "an in-flight production change is exactly what the experiment withholds",
        )

    def test_untracked_production_is_withheld(self) -> None:
        root = _repo()
        (root / "src" / "new_impl.py").write_text(_IMPL, encoding="utf-8")
        self.assertEqual(
            withheld_production_files(root, resolve_base_commit(root)),
            [Path("src/new_impl.py")],
            "a brand-new production module appears only in ls-files --others",
        )


class TestVoidExperimentIsNotAVerdict(unittest.TestCase):
    """A run that withheld nothing reports that, and never runs the test at all."""

    def test_landed_work_reports_not_applicable(self) -> None:
        root = _repo()
        witness = run_red_witness(
            project_root=root,
            req_id="REQ-0.35.0-09-01",
            test_names=["tests.test_impl"],
            # A runner that would CRASH if invoked: the void path must short-circuit
            # before any test runs, so reaching it at all is the failure.
            test_runner=["definitely-not-a-real-binary-839"],
        )
        self.assertEqual(
            witness.failure_class,
            "not-applicable",
            "nothing was withheld, so the run witnesses nothing -- reporting 'none' "
            "here accuses a test that was never actually tested",
        )
        self.assertIn("withheld", witness.output_tail)

    def test_not_applicable_is_neither_red_nor_hollow(self) -> None:
        witness = RedWitness(
            req_id="REQ-0.35.0-09-01",
            base_commit="558e80996df7",
            test_names=["tests.test_impl"],
            exit_status=0,
            failure_class="not-applicable",
            output_tail="",
        )
        self.assertFalse(
            witness.is_red,
            "a void experiment did not demonstrate falsifiability",
        )
        self.assertNotEqual(
            witness.failure_class,
            "none",
            "'I could not run the experiment' and 'your test cannot fail' are "
            "different findings and may not share a class",
        )


if __name__ == "__main__":
    unittest.main()
