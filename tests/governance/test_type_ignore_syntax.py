"""Forbid mypy-style ``# type: ignore[<code>]`` comments (GHI #197).

Unit-test entry to the audit; the canonical logic lives in
``gzkit.governance.trust_audits.audit_type_ignores`` and is also exposed as
``gz validate --type-ignores``.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_type_ignores

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class TypeIgnoreSyntaxPolicy(unittest.TestCase):
    """Every ``# type: ignore[...]`` under src/ must be rewritten to ``# ty: ignore[...]``."""

    def test_no_bracketed_type_ignore_under_src(self) -> None:
        errors = audit_type_ignores(_PROJECT_ROOT)
        self.assertFalse(
            errors,
            msg=(
                "Found `# type: ignore[<code>]` comments — ty does not honor bracketed "
                "mypy-style codes. Use bare `# type: ignore` or `# ty: ignore[<ty-code>]`.\n"
                + "\n".join(f"  {e.artifact}: {e.message}" for e in errors)
            ),
        )


if __name__ == "__main__":
    unittest.main()
