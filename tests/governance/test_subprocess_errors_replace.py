"""Recurrence guard for text-mode subprocess reads missing ``errors=`` (GHI #582).

A text-mode subprocess capture (``text=True`` / ``encoding=`` / ``capture_output``)
decodes sub-process bytes to ``str``; without ``errors=`` an undecodable byte
(cp1252/latin-1 tool or git output) raises ``UnicodeDecodeError`` — a
``ValueError`` that ``except OSError`` misses — and aborts the command mid-run.

``audit_subprocess_errors`` scans ``src/gzkit`` for the class. This test runs it
against the real tree so a re-introduced site fails closed in the ``gz check``
test tier, mirroring ``test_path_separator_portability.py``'s enforcement of the
``.as_posix()`` rule. The teeth/false-positive tests prove the audit actually
discriminates rather than trivially returning ``[]``.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.cross_platform import audit_subprocess_errors

REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_src(project_root: Path, body: str) -> None:
    """Write ``body`` into a src/gzkit module inside a fake project root."""
    src = project_root / "src" / "gzkit"
    src.mkdir(parents=True, exist_ok=True)
    (src / "fixture_mod.py").write_text("import subprocess\n\n" + body, encoding="utf-8")


class SubprocessErrorsRecurrenceTests(unittest.TestCase):
    def test_real_tree_has_no_missing_errors(self) -> None:
        """Fail-close guard: the shipped src/gzkit tree has zero unguarded sites."""
        findings = audit_subprocess_errors(REPO_ROOT)
        self.assertEqual(
            findings,
            [],
            "text-mode subprocess captures under src/gzkit must pass errors= "
            f"(GHI #582); offenders: {[e.artifact for e in findings]}",
        )

    def test_audit_flags_text_mode_capture_without_errors(self) -> None:
        """Teeth: a text=True capture missing errors= is flagged."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_src(
                root,
                "def f():\n"
                "    return subprocess.run(['git', 'log'], capture_output=True, text=True)\n",
            )
            findings = audit_subprocess_errors(root)

        self.assertEqual(len(findings), 1, "a text-mode capture without errors= must flag")
        self.assertEqual(findings[0].type, "subprocess_errors")
        self.assertIn("fixture_mod.py", findings[0].artifact)

    def test_audit_flags_encoding_without_errors(self) -> None:
        """Teeth: encoding= (which also enables text mode) without errors= flags."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_src(
                root,
                "def f():\n    return subprocess.check_output(['git', 'log'], encoding='utf-8')\n",
            )
            findings = audit_subprocess_errors(root)

        self.assertEqual(len(findings), 1, "check_output with encoding= but no errors= must flag")

    def test_audit_accepts_text_mode_with_errors(self) -> None:
        """A text-mode capture WITH errors= is the fixed shape — not flagged."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_src(
                root,
                "def f():\n"
                "    return subprocess.run(\n"
                "        ['git', 'log'], capture_output=True, text=True, errors='replace'\n"
                "    )\n",
            )
            findings = audit_subprocess_errors(root)

        self.assertEqual(findings, [], "errors= present must satisfy the audit")

    def test_audit_ignores_bytes_mode_capture(self) -> None:
        """No false positive: bytes-mode capture (no text/encoding) does not decode.

        Adding errors= there would silently ENABLE text mode and flip the return
        type from bytes to str — so the audit must NOT demand it.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_src(
                root,
                "def f():\n    return subprocess.run(['git', 'log'], capture_output=True)\n",
            )
            findings = audit_subprocess_errors(root)

        self.assertEqual(findings, [], "bytes-mode capture must not be flagged")

    def test_audit_ignores_text_mode_without_capture(self) -> None:
        """No false positive: text mode with no capture inherits streams (no decode)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_src(
                root,
                "def f():\n    return subprocess.run(['git', 'log'], text=True)\n",
            )
            findings = audit_subprocess_errors(root)

        self.assertEqual(findings, [], "text mode without capture has nothing to decode")

    def test_message_is_actionable(self) -> None:
        """Finding prose names the fix and cites the rule (guardrail-feedback-prose)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_src(
                root,
                "def f():\n"
                "    return subprocess.run(['git', 'log'], capture_output=True, text=True)\n",
            )
            findings = audit_subprocess_errors(root)

        self.assertEqual(len(findings), 1)
        message = findings[0].message
        self.assertIn('errors="replace"', message, "must name the concrete fix")
        self.assertIn("cross-platform.md", message, "must cite the governing rule")


if __name__ == "__main__":
    unittest.main()
