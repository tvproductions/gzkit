"""Forbid mypy-style ``# type: ignore[<code>]`` comments (GHI #197).

``ty`` does not honor bracketed codes on ``# type: ignore``. When this project
migrated from mypy to ty, legacy comments like ``# type: ignore[override]``
kept their codes but stopped suppressing the underlying diagnostic — silently.
12 such diagnostics surfaced during ADR-0.0.16 closeout after weeks of being
invisible to the gate.

Policy going forward: suppressions must be one of

* ``# type: ignore`` — bare, honored by both mypy-style and ty tooling
* ``# ty: ignore[<ty-code>]`` — ty's native form

This scan fails fast on any legacy bracketed form under ``src/``.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _PROJECT_ROOT / "src"

# Match `# type: ignore[...]` where something sits inside the brackets.
# Bare `# type: ignore` (no brackets) is allowed and not matched here.
_FORBIDDEN_PATTERN = re.compile(r"#\s*type:\s*ignore\[")


class TypeIgnoreSyntaxPolicy(unittest.TestCase):
    """Every ``# type: ignore[...]`` under src/ must be rewritten to ``# ty: ignore[...]``."""

    def test_no_bracketed_type_ignore_under_src(self) -> None:
        offenders: list[str] = []
        for py_file in _SRC_ROOT.rglob("*.py"):
            for lineno, line in enumerate(py_file.read_text(encoding="utf-8").splitlines(), 1):
                if _FORBIDDEN_PATTERN.search(line):
                    rel = py_file.relative_to(_PROJECT_ROOT)
                    offenders.append(f"{rel}:{lineno}: {line.strip()}")
        self.assertFalse(
            offenders,
            msg=(
                "Found `# type: ignore[<code>]` comments — ty does not honor bracketed "
                "mypy-style codes. Use bare `# type: ignore` or `# ty: ignore[<ty-code>]`.\n"
                + "\n".join(offenders)
            ),
        )


if __name__ == "__main__":
    unittest.main()
