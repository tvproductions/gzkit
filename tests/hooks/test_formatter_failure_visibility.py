"""A formatter that could not run must not read as one that ran (GHI #914).

``_ruff_format_dir`` discarded every signal that formatting failed. Two
suppression layers composed into silence: ``suppress(...)`` swallowed a
formatter that could not be LAUNCHED, and ``check=False`` with the
``CompletedProcess`` never bound swallowed one that launched, ran, and exited
non-zero -- along with the ``stderr`` explaining why. The function returned
``None`` on every path, so no caller could distinguish "formatted" from "did
not format", and none tried.

GHI #909 bound the subprocess to the synced root, which made the OUTCOME
deterministic per root. It did not make the FAILURE visible, and its own
docstring said so. This is the residual that repair disclosed and deferred.

THE CONSEQUENCE IS A MISDIRECTED DIAGNOSIS, not a crash. That docstring states
the formatting step is what *"keeps sync_all output byte-stable against the
pre-commit formatter, which is what the sync-parity validator compares
against."* When the step silently no-ops, the parity validator reports drift
with no indication that normalization never happened -- and the reader debugs
the renderer instead of the environment.

The fixture is GHI #910's instrument: a project ``uv`` can never build, because
the backend does not exist and nothing needs resolving. That is precisely the
tree in which this formatter fails, and it fails locally and offline in
milliseconds rather than on a network timeout.
"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from gzkit.hooks.core import _ruff_format_dir

GZKIT_REPO = Path(__file__).resolve().parents[2]

UNBUILDABLE_PYPROJECT = """\
[project]
name = "probe-tree"
version = "0.1.0"

[build-system]
requires = []
build-backend = "gzkit_no_such_backend"

[tool.ruff]
line-length = 100
"""

#: Deliberately not ruff-clean, so a formatter that DID run leaves a visible mark.
UNFORMATTED_SOURCE = "x   =    1\nif x==1:\n    pass\n"


class TestFormatterFailureIsObservable(unittest.TestCase):
    """The reportable question is 'did the procedure run', never 'is it armed'."""

    def _staged(self, root: Path) -> Path:
        """Write an unformatted module into a staging dir under ``root``."""
        staging = root / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        (staging / "hook.py").write_text(UNFORMATTED_SOURCE, encoding="utf-8")
        return staging

    def test_an_unrunnable_formatter_reports_why(self) -> None:
        """A tree uv cannot build yields a REASON, not a silent None.

        The return value is the channel the sync-parity path needs: it lets a
        drift report say the formatter did not run, instead of presenting an
        unexplained byte difference for a human to misattribute.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(UNBUILDABLE_PYPROJECT, encoding="utf-8")
            staging = self._staged(root)
            with redirect_stderr(io.StringIO()):
                failure = _ruff_format_dir(staging, root)
            self.assertIsNotNone(failure, "an unrunnable formatter reported success")
            self.assertIn("format", str(failure).lower())

    def test_the_failure_reaches_stderr(self) -> None:
        """Visible to an operator reading output, not only to a branching caller.

        Both channels are load-bearing and neither substitutes: a return value
        no caller inspects is as silent as the suppression it replaced, and a
        log line cannot be branched on.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(UNBUILDABLE_PYPROJECT, encoding="utf-8")
            staging = self._staged(root)
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                _ruff_format_dir(staging, root)
            self.assertIn("ruff format", stderr.getvalue())

    def test_the_diagnostic_is_not_reduced_to_a_line(self) -> None:
        """The reported cause must be the cause, not whichever line came first.

        `uv` frames its real error: a benign VIRTUAL_ENV or requires-python
        warning leads, remediation hints trail, and the actual failure sits in
        between. Reporting the first line names an irrelevant warning and
        reporting the last names a hint -- either one sends the reader
        somewhere wrong, which is the very outcome this issue is about.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(UNBUILDABLE_PYPROJECT, encoding="utf-8")
            staging = self._staged(root)
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                failure = _ruff_format_dir(staging, root)
            self.assertIn("gzkit_no_such_backend", stderr.getvalue())
            self.assertIn("gzkit_no_such_backend", str(failure))

    def test_a_working_formatter_stays_silent_and_reports_success(self) -> None:
        """Success must remain indistinguishable from today, or this is a new gate.

        Run against the gzkit repo itself, where ``uv run ruff format`` genuinely
        works -- so the test proves the failure channel is a channel and not a
        change of outcome.
        """
        with tempfile.TemporaryDirectory() as tmp:
            staging = self._staged(Path(tmp))
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                failure = _ruff_format_dir(staging, GZKIT_REPO)
            self.assertIsNone(failure, f"a working formatter reported failure: {failure}")
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(
                (staging / "hook.py").read_text(encoding="utf-8"),
                "x = 1\nif x == 1:\n    pass\n",
                "the formatter did not actually format, so this fixture proves nothing",
            )

    def test_an_absent_directory_is_not_a_failure(self) -> None:
        """Nothing to format is not the same event as failing to format."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                failure = _ruff_format_dir(root / "absent", root)
            self.assertIsNone(failure)
            self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
