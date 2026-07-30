"""Recurrence guard for text-mode subprocess reads missing ``errors=`` (GHI #582).

A text-mode subprocess capture (``text=True`` / ``encoding=`` / ``capture_output``)
decodes sub-process bytes to ``str``; without ``errors=`` an undecodable byte
(cp1252/latin-1 tool or git output) raises ``UnicodeDecodeError`` — a
``ValueError`` that ``except OSError`` misses — and aborts the command mid-run.

``audit_subprocess_errors`` scans every tree in ``_SUBPROCESS_AUDIT_ROOTS`` —
``src/gzkit``, ``scripts``, and ``.claude/hooks``. This test runs it against the
real tree so a re-introduced site fails closed in the ``gz check`` test tier,
mirroring ``test_path_separator_portability.py``'s enforcement of the
``.as_posix()`` rule. The teeth/false-positive tests prove the audit actually
discriminates rather than trivially returning ``[]``, and
``SubprocessAuditScopeTests`` proves each declared root is genuinely walked —
a guard scoped away from the surface it should cover reads as covered.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.cross_platform import (
    _SUBPROCESS_AUDIT_ROOTS,
    audit_subprocess_errors,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


_UNGUARDED = "def f():\n    return subprocess.run(['git', 'log'], capture_output=True, text=True)\n"


def _write_src(project_root: Path, body: str) -> None:
    """Write ``body`` into a src/gzkit module inside a fake project root."""
    _write_at(project_root, ("src", "gzkit"), body)


def _write_at(project_root: Path, parts: tuple[str, ...], body: str) -> Path:
    """Write a subprocess-using fixture module into an arbitrary tree."""
    target = project_root.joinpath(*parts)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "fixture_mod.py"
    path.write_text("import subprocess\n\n" + body, encoding="utf-8")
    return path


class SubprocessErrorsRecurrenceTests(unittest.TestCase):
    def test_real_tree_has_no_missing_errors(self) -> None:
        """Fail-close guard: every scanned tree has zero unguarded sites."""
        findings = audit_subprocess_errors(REPO_ROOT)
        self.assertEqual(
            findings,
            [],
            "text-mode subprocess captures in scanned trees must pass errors= "
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


class SubprocessAuditScopeTests(unittest.TestCase):
    """The audit must cover the trees where a decode crash costs the most.

    Scanning ``src/gzkit`` alone was the defect, not merely a limitation: the two
    worst-consequence sites in the repo sat outside it — the SessionStart boot
    hook (``scripts/session_orientation.py``) and the blocking hooks under
    ``.claude/hooks`` — where an undecodable byte kills session boot or refuses
    every tool call instead of failing one command. GHI #688 had already patched
    the boot hook's *file*-read side of this class; the *subprocess* side was
    invisible to the guard, so the recurrence defense did not defend the surface
    whose recurrence mattered most.
    """

    def test_every_declared_root_is_actually_scanned(self) -> None:
        """Each root in the declared tuple must really be walked, not just listed.

        Table-driven over ``_SUBPROCESS_AUDIT_ROOTS`` so adding a root without
        wiring it — or dropping one — fails here. Asserts scanning BEHAVIOR (an
        unguarded site planted in the root is found, and named by relative path)
        rather than that the directory exists on disk: an existence assertion
        proves content, not behavior, and is the shape
        ``gz validate --tautological-test-audit`` correctly refuses.

        Residual gap, recorded rather than silently dropped: if a tree is RENAMED
        in the repo without updating this tuple, the stale root scans nothing and
        the real-tree guard passes vacuously for it. Catching that needs the audit
        to report files-visited, which it does not, so it is not covered here.
        """
        for parts in _SUBPROCESS_AUDIT_ROOTS:
            rendered = "/".join(parts)
            with self.subTest(root=rendered), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _write_at(root, parts, _UNGUARDED)
                findings = audit_subprocess_errors(root)
                self.assertEqual(len(findings), 1, f"declared root {rendered} is not scanned")
                self.assertIn(f"{rendered}/fixture_mod.py", findings[0].artifact)

    def test_tests_tree_is_deliberately_not_scanned(self) -> None:
        """Pins the exclusion so it stays a decision, not an accident.

        A decode crash under ``tests/`` fails a test loudly — self-reporting, not
        a silent session kill — and 35 real sites carry the shape. Widening here
        means doing that sweep; it must not happen as a side effect of someone
        assuming the omission was an oversight.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_at(root, ("tests",), _UNGUARDED)
            findings = audit_subprocess_errors(root)
        self.assertEqual(findings, [], "tests/ is excluded by design; widening requires the sweep")


if __name__ == "__main__":
    unittest.main()
