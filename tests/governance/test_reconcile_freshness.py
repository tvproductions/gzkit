"""Tests for is_receipt_fresh (OBPI-0.0.37-07).

REQ-0.0.37-07-01 — pure function semantics; covered via @covers decorators below.
"""

from __future__ import annotations

import os
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.traceability import covers


def _ts(offset_seconds: float = 0.0) -> datetime:
    """Return a UTC datetime offset from now."""
    return datetime.fromtimestamp(time.time() + offset_seconds, tz=UTC)


class TestIsReceiptFresh(unittest.TestCase):
    """Tests for ``is_receipt_fresh`` (REQ-0.0.37-07-01)."""

    @covers("REQ-0.0.37-07-01")
    def test_receipt_fresh_when_ts_newer_than_all_files(self) -> None:
        """receipt_ts > max mtime → True."""
        from gzkit.governance.reconcile_freshness import is_receipt_fresh

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "src" / "foo.py"
            f.parent.mkdir(parents=True)
            f.write_text("x", encoding="utf-8")
            old_mtime = time.time() - 100
            os.utime(f, (old_mtime, old_mtime))

            fresh_ts = _ts(0)
            self.assertTrue(is_receipt_fresh(fresh_ts, ["src/foo.py"], root))

    @covers("REQ-0.0.37-07-01")
    def test_receipt_stale_when_ts_older_than_file(self) -> None:
        """receipt_ts < mtime of a file → False."""
        from gzkit.governance.reconcile_freshness import is_receipt_fresh

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "src" / "foo.py"
            f.parent.mkdir(parents=True)
            f.write_text("x", encoding="utf-8")

            stale_ts = _ts(-200)
            self.assertFalse(is_receipt_fresh(stale_ts, ["src/foo.py"], root))

    @covers("REQ-0.0.37-07-01")
    def test_missing_path_returns_false(self) -> None:
        """A path that does not exist → False (forces re-reconcile)."""
        from gzkit.governance.reconcile_freshness import is_receipt_fresh

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fresh_ts = _ts(0)
            self.assertFalse(is_receipt_fresh(fresh_ts, ["src/nonexistent.py"], root))

    @covers("REQ-0.0.37-07-01")
    def test_empty_allowed_paths_returns_false(self) -> None:
        """No paths → False (no domain to be fresh against)."""
        from gzkit.governance.reconcile_freshness import is_receipt_fresh

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fresh_ts = _ts(0)
            self.assertFalse(is_receipt_fresh(fresh_ts, [], root))

    @covers("REQ-0.0.37-07-01")
    def test_glob_pattern_expands_correctly(self) -> None:
        """Glob pattern is expanded; receipt fresh only when newer than all matches."""
        from gzkit.governance.reconcile_freshness import is_receipt_fresh

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = root / "src" / "mypkg"
            pkg.mkdir(parents=True)
            f1 = pkg / "a.py"
            f2 = pkg / "b.py"
            f1.write_text("a", encoding="utf-8")
            f2.write_text("b", encoding="utf-8")
            old = time.time() - 100
            os.utime(f1, (old, old))
            os.utime(f2, (old, old))

            fresh_ts = _ts(0)
            self.assertTrue(is_receipt_fresh(fresh_ts, ["src/mypkg/*.py"], root))

    @covers("REQ-0.0.37-07-01")
    def test_glob_with_one_newer_file_returns_false(self) -> None:
        """If any file under a glob is newer than receipt_ts → False."""
        from gzkit.governance.reconcile_freshness import is_receipt_fresh

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = root / "src" / "mypkg"
            pkg.mkdir(parents=True)
            f1 = pkg / "a.py"
            f2 = pkg / "b.py"
            f1.write_text("a", encoding="utf-8")
            f2.write_text("b", encoding="utf-8")

            stale_ts = _ts(-200)
            self.assertFalse(is_receipt_fresh(stale_ts, ["src/mypkg/*.py"], root))


if __name__ == "__main__":
    unittest.main()
