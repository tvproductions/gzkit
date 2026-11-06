"""Policy test: a guarded source read treats undecodable bytes as unreadable.

A scanner that reads a file with ``read_text(encoding="utf-8")`` and guards it with
``except (OSError, SyntaxError)`` means "skip or report a file I cannot read or
parse". ``UnicodeDecodeError`` is a ``ValueError``, not an ``OSError``, so bytes
that are not UTF-8 escape that guard and abort the whole scan (GHI #1307; the same
class as GHI #1180 on the registry read seam). This scan reads every such ``try``
in the package and requires its handlers to cover the decode failure as well, or
the read to pass ``errors=``, which cannot raise it.
"""

import ast
import unittest
from pathlib import Path

SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "gzkit"
_READ_GUARD = {"OSError", "SyntaxError"}
_DECODE_COVER = {"UnicodeDecodeError", "UnicodeError", "ValueError"}


def _handler_names(handler: ast.ExceptHandler) -> set[str]:
    """Return the exception class names one ``except`` clause names."""
    node = handler.type
    if node is None:
        return {"BaseException"}
    elts = node.elts if isinstance(node, ast.Tuple) else [node]
    return {e.id if isinstance(e, ast.Name) else ast.unparse(e) for e in elts}


def _reads_utf8_strictly(body: list[ast.stmt]) -> bool:
    """Return True when the block calls ``read_text`` with an encoding and no ``errors=``."""
    for stmt in body:
        for node in ast.walk(stmt):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                continue
            if node.func.attr != "read_text":
                continue
            keywords = {kw.arg for kw in node.keywords}
            if "errors" not in keywords and ("encoding" in keywords or node.args):
                return True
    return False


def _unguarded_reads() -> list[str]:
    """Return ``path:line`` for each read guard that lets a decode failure escape."""
    found: list[str] = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Try) or not _reads_utf8_strictly(node.body):
                continue
            names = set().union(*(_handler_names(h) for h in node.handlers))
            if names >= _READ_GUARD and not names & (_DECODE_COVER | {"Exception"}):
                found.append(f"{path.relative_to(SRC_ROOT.parent).as_posix()}:{node.lineno}")
    return found


class TestSourceReadDecodeGuard(unittest.TestCase):
    """Every OSError/SyntaxError read guard also covers undecodable bytes."""

    def test_no_read_guard_lets_a_decode_failure_escape(self) -> None:
        self.assertEqual(
            _unguarded_reads(),
            [],
            "these reads catch OSError and SyntaxError but not UnicodeDecodeError, so a "
            "non-UTF-8 file aborts the scan instead of being treated as unreadable "
            "(GHI #1307): add UnicodeDecodeError to the same except clause",
        )

    def test_the_scan_sees_an_unguarded_read(self) -> None:
        """Negative control: the detector flags the shape it exists to refuse."""
        tree = ast.parse(
            "try:\n"
            "    s = p.read_text(encoding='utf-8')\n"
            "except (OSError, SyntaxError):\n"
            "    pass\n"
        )
        guard = next(n for n in ast.walk(tree) if isinstance(n, ast.Try))
        self.assertTrue(_reads_utf8_strictly(guard.body))
        self.assertEqual(_handler_names(guard.handlers[0]), _READ_GUARD)


if __name__ == "__main__":
    unittest.main()
