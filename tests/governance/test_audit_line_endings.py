"""Fixture-level tests for ``audit_line_endings`` (GHI #570).

The cross-platform CRLF/LF hazard recurred as one-off fixes (GHIs #478, #161,
#384) for want of a gate. ``audit_line_endings`` mechanizes two surfaces: a
committed ``.gitattributes`` LF-normalization directive, and the absence of
CRLF in any *committed* (indexed) text surface — verified via
``git ls-files --eol``, NOT working-tree bytes. Checking the index lets
``.gitattributes`` do the work and stops the gate from policing volatile
working-tree state that git normalizes away on commit (a Windows ``write_text``
emits CRLF transiently, but the index stays LF). These tests gate the scan
semantics against synthetic temp git trees; ``gz check`` itself gates current
repo state by running the scope on the real tree.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_line_endings

_GITATTRIBUTES = "* text=auto eol=lf\n"


def _git(root: Path, *args: str) -> None:
    """Run a git command in ``root``, raising on failure."""
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def _init_repo(root: Path, *, autocrlf: str = "false") -> None:
    """Init a repo with pinned ``core.autocrlf`` so index EOL is deterministic."""
    _git(root, "init", "-q")
    _git(root, "config", "core.autocrlf", autocrlf)


class LineEndingAuditTests(unittest.TestCase):
    """``audit_line_endings`` flags committed CRLF and a missing/weak .gitattributes."""

    def _project(
        self,
        tmp: str,
        *,
        gitattributes: str | None = _GITATTRIBUTES,
        py_bytes: bytes = b"x = 1\n",
    ) -> Path:
        root = Path(tmp)
        if gitattributes is not None:
            (root / ".gitattributes").write_text(gitattributes, encoding="utf-8", newline="\n")
        src = root / "src"
        src.mkdir()
        (src / "mod.py").write_bytes(py_bytes)
        return root

    def test_crlf_committed_to_index_is_flagged(self) -> None:
        """A blob staged with CRLF (no eol=lf normalization) is flagged via the index.

        ``*.png binary`` carries no eol=lf for ``.py``; with ``core.autocrlf=false``
        git stores the CRLF blob verbatim, so ``git ls-files --eol`` reports
        ``i/crlf`` and the gate fails closed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, gitattributes="*.png binary\n", py_bytes=b"x = 1\r\n")
            _init_repo(root)
            _git(root, "add", "-A")
            errors = audit_line_endings(root)
            self.assertTrue(
                any(e.type == "line_endings" and e.artifact == "src/mod.py" for e in errors),
                msg=f"expected committed-CRLF flag on src/mod.py, got {errors}",
            )

    def test_eol_lf_normalizes_index_so_no_flag(self) -> None:
        """``* text=auto eol=lf`` makes git store an LF blob even from a CRLF file.

        The working file is CRLF on disk (``w/crlf``) but the index is ``i/lf`` —
        the gate must trust the index and NOT flag. This is the regression guard
        for "let .gitattributes do the work": the byte-level working-tree check
        this replaced would have falsely failed here on Windows.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, py_bytes=b"x = 1\r\n")
            _init_repo(root)
            _git(root, "add", "-A")
            line_ending_errors = [e for e in audit_line_endings(root) if e.type == "line_endings"]
            self.assertEqual(
                line_ending_errors,
                [],
                msg=f"eol=lf must normalize the index to LF — no flag; got {line_ending_errors}",
            )

    def test_missing_gitattributes_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, gitattributes=None)
            errors = audit_line_endings(root)
            self.assertTrue(
                any(e.artifact == ".gitattributes" for e in errors),
                msg=f"expected missing-.gitattributes flag, got {errors}",
            )

    def test_gitattributes_without_lf_directive_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, gitattributes="*.png binary\n")
            errors = audit_line_endings(root)
            self.assertTrue(
                any(e.artifact == ".gitattributes" for e in errors),
                msg=f"expected weak-.gitattributes flag, got {errors}",
            )

    def test_clean_lf_project_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp)
            _init_repo(root)
            _git(root, "add", "-A")
            self.assertEqual(
                [],
                audit_line_endings(root),
                msg="clean LF project with proper .gitattributes must pass",
            )


if __name__ == "__main__":
    unittest.main()
