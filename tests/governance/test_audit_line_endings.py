"""Fixture-level tests for ``audit_line_endings`` (GHI #570).

The cross-platform CRLF/LF hazard recurred as one-off fixes (GHIs #478,
#161, #384) for want of a gate. ``audit_line_endings`` mechanizes two
surfaces: a committed ``.gitattributes`` LF-normalization directive, and
the absence of CRLF bytes in any tracked text surface. These tests gate
the scan semantics against synthetic temp trees; ``gz check`` itself gates
current repo state by running the scope on the real tree.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_line_endings

_GITATTRIBUTES = "* text=auto eol=lf\n"


class LineEndingAuditTests(unittest.TestCase):
    """``audit_line_endings`` flags CRLF surfaces and a missing/weak .gitattributes."""

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

    def test_crlf_text_surface_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, py_bytes=b"x = 1\r\n")
            errors = audit_line_endings(root)
            self.assertTrue(
                any(e.type == "line_endings" and e.artifact == "src/mod.py" for e in errors),
                msg=f"expected CRLF flag on src/mod.py, got {errors}",
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
            self.assertEqual(
                [],
                audit_line_endings(root),
                msg="clean LF project with proper .gitattributes must pass",
            )


if __name__ == "__main__":
    unittest.main()
