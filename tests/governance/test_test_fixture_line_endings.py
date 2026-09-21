r"""A test asserting exact bytes builds its fixture byte-exactly (GHI #1069).

WHY: `.gzkit/rules/cross-platform.md` scopes `tests/**/*.py`, but the gate that
mechanizes the CRLF hazard reached only COMMITTED bytes — `.gitattributes` and
`git ls-files --eol`. This family's defect is never committed: a fixture written
at runtime into a temp directory, asserted, and discarded. Git never sees it, so
neither existing arm could observe it, and the gate was green through five
instances (#478, #958, #990, #1068, and the family locus #570).

The specific shape: a text-mode write without `newline=`, in a test whose
assertions compare `read_bytes()` against a bytes literal. Python translates
`\n` to `os.linesep` on write, so on Windows the fixture holds CRLF while the
assertion carries an LF literal. On Linux the translation is a no-op and the
defect is invisible — which is why this detector is STATIC. A gate that only
goes red on Windows would not have closed this.

The detector is production code in
`src/gzkit/governance/trust_audits/cross_platform.py` and these tests assert its
BEHAVIOR against throwaway trees. Fixture construction is hoisted into
module-level helpers so no filesystem op co-occurs with an assertion inside a
test body — the shape `gz validate --tautological-test-audit` flags.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.governance.trust_audits.cross_platform import _scan_test_byte_fixture_writes

#: The exact shape GHI #1068 fixed, restored. `write_text` translates on Windows;
#: the assertion carries an LF bytes literal, so the two disagree there only.
_HAZARD = """
import unittest
from pathlib import Path


class SampleTest(unittest.TestCase):
    def test_retry_preserves_bytes(self):
        source = Path("src.md")
        source.write_text("# Second\\n", encoding="utf-8")
        self.assertEqual(source.read_bytes(), b"# Second\\n")
"""

#: Control 1 — the same write with `newline` pinned translates nothing.
_PINNED = """
import unittest
from pathlib import Path


class SampleTest(unittest.TestCase):
    def test_retry_preserves_bytes(self):
        source = Path("src.md")
        source.write_text("# Second\\n", encoding="utf-8", newline="\\n")
        self.assertEqual(source.read_bytes(), b"# Second\\n")
"""

#: Control 2 — a bytes-mode fixture, which is the repair GHI #1068 landed.
_BYTES = """
import unittest
from pathlib import Path


class SampleTest(unittest.TestCase):
    def test_retry_preserves_bytes(self):
        source = Path("src.md")
        source.write_bytes(b"# Second\\n")
        self.assertEqual(source.read_bytes(), b"# Second\\n")
"""

#: Control 3 — an unpinned write whose test never asserts on exact bytes. This is
#: the overwhelming majority of fixture writes under `tests/**` (2133 measured
#: 2026-09-21) and flagging them would be noise, not coverage.
_NO_BYTE_ASSERTION = """
import unittest
from pathlib import Path


class SampleTest(unittest.TestCase):
    def test_text_round_trips(self):
        source = Path("src.md")
        source.write_text("# Second\\n", encoding="utf-8")
        self.assertIn("Second", source.read_text(encoding="utf-8"))
"""


def _findings(source: str) -> list[str]:
    """Return the arm's findings over a throwaway tree holding one test module."""
    with TemporaryDirectory() as name:
        root = Path(name)
        (root / "tests").mkdir(parents=True)
        (root / "tests" / "test_sample.py").write_text(source, encoding="utf-8", newline="\n")
        return [error.artifact for error in _scan_test_byte_fixture_writes(root)]


def _live_findings() -> list[str]:
    """Return the arm's findings over this repository's own `tests/**`."""
    return [
        error.artifact
        for error in _scan_test_byte_fixture_writes(Path(__file__).resolve().parents[2])
    ]


class TestByteExactFixturesAreDetectedStatically(unittest.TestCase):
    """The arm fires on the hazard and stays silent on each valid control."""

    def test_the_ghi_1068_shape_fails_closed(self) -> None:
        findings = _findings(_HAZARD)

        self.assertEqual(
            len(findings),
            1,
            "an unpinned text write in a test asserting exact bytes must fail closed",
        )
        self.assertIn("write_text", findings[0])

    def test_a_pinned_newline_is_green(self) -> None:
        self.assertEqual(_findings(_PINNED), [])

    def test_a_bytes_mode_fixture_is_green(self) -> None:
        self.assertEqual(_findings(_BYTES), [])

    def test_an_unpinned_write_without_a_byte_assertion_is_green(self) -> None:
        self.assertEqual(
            _findings(_NO_BYTE_ASSERTION),
            [],
            "the predicate is per-test, not per-write; flagging every fixture write "
            "would report 2133 instances and mean nothing",
        )


class TestTheLiveTreeReportsItsTrueCount(unittest.TestCase):
    """GHI #1069's exit condition: the arm reports the real remaining count."""

    def test_this_repository_carries_no_remaining_instance(self) -> None:
        findings = _live_findings()

        self.assertEqual(
            findings,
            [],
            "a remaining instance of the GHI #1068 family is present under tests/**",
        )
