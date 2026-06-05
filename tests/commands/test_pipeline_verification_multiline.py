"""Verify-stage extractor joins multi-line Verification commands (GHI #569, BI-1).

ADR-0.0.63 § Boundary Invariants BI-1: multi-line quoted constructs (e.g.
``python -c "…"`` spanning physical lines) are joined into one logical command,
never split per physical line. The verify-stage extractor must reuse
``extract_fenced_commands`` so it shares the joiner with the demo path — not
just the ``is_shell_less_executable`` classifier.
"""

from __future__ import annotations

import unittest

from gzkit.commands.obpi_stages import _pipeline_verification_commands

_BRIEF = """# OBPI test brief

## Verification

```bash
python -c "import sys
print('ok')"
```
"""


class TestPipelineVerificationMultiline(unittest.TestCase):
    def test_multiline_python_c_is_joined_not_split(self) -> None:
        # Pre-#569 the block was split per physical line; the first fragment
        # `python -c "import sys` has an unterminated quote, fails
        # is_shell_less_executable, and the extractor raises SystemExit(1).
        # The shared joiner keeps it as one logical command that passes.
        try:
            commands = _pipeline_verification_commands(_BRIEF, "lite")
        except SystemExit:  # pragma: no cover - the pre-fix failure path
            self.fail(
                "multi-line python -c was split per physical line and rejected "
                "(BI-1 violation); extractor must join via extract_fenced_commands"
            )

        joined = [c for c in commands if "import sys" in c and "print('ok')" in c]
        self.assertEqual(
            len(joined),
            1,
            f"multi-line python -c must be one joined command, got: {commands!r}",
        )
        self.assertFalse(
            any(c.strip() == 'python -c "import sys' for c in commands),
            f"command was shredded per physical line: {commands!r}",
        )


if __name__ == "__main__":
    unittest.main()
