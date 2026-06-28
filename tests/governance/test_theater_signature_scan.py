"""Tests for the static theater-signature analyzer (ADR-0.0.73 channel 1, GHI #657).

The analyzer detects three structurally-decidable theater signatures in QC-step
validator source: copy-vs-self, mtime-where-name-says-content, and skip-if-PASS.
The four semantic signatures (prose-graded-by-nothing, shape-graded-not-substance,
empty-input-passes, fixture-only) are deliberately NOT statically detected — a
static detector for them would itself grade by shape (the GHI #624 facade) and is
owned by channel 2 (behavioral negative-control execution).

Each detect test cites the real facade the pattern is calibrated on; each guard
test pins a legitimate-looking shape that must NOT be flagged.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.theater_signature_scan import (
    scan_source_for_signatures,
    scan_validator_tree,
)


def _scan(source: str) -> list:
    """Write source to a temp .py file and scan it; return findings."""
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "probe.py"
        path.write_text(source, encoding="utf-8")
        return scan_source_for_signatures(path, rel="src/probe.py")


class TestCopyVsSelf(unittest.TestCase):
    """copy-vs-self: tautological self-equality (calibrated on the ADR-0.0.37
    fixture==fixture facade — an assertion that can never fail)."""

    def test_self_compare_eq_flagged(self) -> None:
        findings = _scan("def check(a):\n    return a == a\n")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].signature, "copy-vs-self")
        self.assertEqual(findings[0].function_name, "check")

    def test_assert_equal_x_x_flagged(self) -> None:
        src = (
            "import unittest\n"
            "class T(unittest.TestCase):\n"
            "    def test_it(self):\n"
            "        x = compute()\n"
            "        self.assertEqual(x, x)\n"
        )
        findings = _scan(src)
        self.assertEqual([f.signature for f in findings], ["copy-vs-self"])

    def test_not_equal_self_not_flagged(self) -> None:
        # a != a is the legitimate NaN-detection idiom — must NOT flag.
        findings = _scan("def is_nan(a):\n    return a != a\n")
        self.assertEqual(findings, [])

    def test_call_operands_not_flagged(self) -> None:
        # f() == f() may be non-deterministic; flagging it is unsafe (purity guard).
        findings = _scan("def check():\n    return now() == now()\n")
        self.assertEqual(findings, [])

    def test_distinct_operands_not_flagged(self) -> None:
        findings = _scan("def check(a, b):\n    return a == b\n")
        self.assertEqual(findings, [])


class TestMtimeWhereNameSaysContent(unittest.TestCase):
    """mtime-where-name-says-content: a content/freshness-named function whose
    body reads st_mtime instead of content (calibrated on the repudiated
    rendition_freshness mtime tautology)."""

    def test_mtime_in_content_named_fn_flagged(self) -> None:
        src = "def verify_content_freshness(p):\n    return p.stat().st_mtime\n"
        findings = _scan(src)
        self.assertEqual([f.signature for f in findings], ["mtime-where-name-says-content"])

    def test_getmtime_call_flagged(self) -> None:
        src = "import os\ndef check_content_hash(p):\n    return os.path.getmtime(p)\n"
        findings = _scan(src)
        self.assertEqual([f.signature for f in findings], ["mtime-where-name-says-content"])

    def test_mtime_in_docstring_not_flagged(self) -> None:
        # Models rendition_freshness.py:8 — a docstring that MENTIONS st_mtime but
        # uses no mtime in code. The detector inspects Attribute/Call nodes only,
        # so docstring Constants are invisible. This is the load-bearing FP guard.
        src = (
            "def verify_content_freshness(p):\n"
            '    """Checks content, NOT st_mtime / getmtime (the repudiated tautology)."""\n'
            "    return p.read_text()\n"
        )
        findings = _scan(src)
        self.assertEqual(findings, [])

    def test_mtime_without_content_name_not_flagged(self) -> None:
        # A function reading mtime for a non-content purpose (log rotation) — the
        # name carries no content/freshness semantics, so it must NOT flag.
        src = "def rotate_logs(p):\n    return p.stat().st_mtime\n"
        findings = _scan(src)
        self.assertEqual(findings, [])


class TestSkipIfPass(unittest.TestCase):
    """skip-if-PASS: short-circuit clean-return gated on persisted PASS state
    (the check never runs the second time)."""

    def test_skip_on_persisted_pass_flagged(self) -> None:
        src = (
            "def audit(record):\n"
            "    if record.status == 'PASS':\n"
            "        return []\n"
            "    return run_real_audit(record)\n"
        )
        findings = _scan(src)
        self.assertEqual([f.signature for f in findings], ["skip-if-PASS"])

    def test_locally_computed_status_not_flagged(self) -> None:
        # status computed in-function from a real check is legitimate early-return.
        src = (
            "def audit(record):\n"
            "    status = run_real_audit(record)\n"
            "    if status == 'PASS':\n"
            "        return []\n"
            "    return ['failed']\n"
        )
        findings = _scan(src)
        self.assertEqual(findings, [])


class TestRealTreeZeroFalsePositives(unittest.TestCase):
    """The load-bearing regression: the current (known-clean post-Movement-I)
    trust_audits validator tree must yield ZERO findings. If this can never go
    red, the detectors are noise; when a real facade lands it flips red."""

    def test_trust_audits_tree_is_clean(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        audits_dir = project_root / "src" / "gzkit" / "governance" / "trust_audits"
        files = sorted(audits_dir.rglob("*.py"))
        self.assertGreater(len(files), 5, "expected a populated trust_audits tree")
        findings = scan_validator_tree(project_root, files)
        self.assertEqual(
            findings,
            [],
            f"static theater-signature analyzer reported false positives on the "
            f"known-clean tree: {[(f.file_path, f.line_number, f.signature) for f in findings]}",
        )


if __name__ == "__main__":
    unittest.main()
