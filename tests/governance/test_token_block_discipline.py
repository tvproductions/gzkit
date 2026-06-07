"""Token-block discipline coverage (ADR-0.0.41).

Tests assert the binding sub-invariants of `.gzkit/rules/token-block-discipline.md`:
- Sub-Invariant 1 (abandon category enum)
- Sub-Invariant 2 (register-entry minimum-information)
- Sub-Invariant 3 (reaping register-entry rule)
- Sub-Invariant 4 (TTL canon and reaping discipline)
- Sub-Invariant 5 (release fail-closed precondition)

Authored progressively across OBPI-0.0.41-02, -03, -04 per parent ADR § Evidence.
"""

from __future__ import annotations

import unittest


class TokenBlockDisciplineCoverage(unittest.TestCase):
    """Placeholder — REQ-derived `@covers`-decorated tests land per OBPI."""

    def test_token_block_rule_file_present(self) -> None:
        """Sanity: the canonical rule file authored by OBPI-01 is on disk."""
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[2]
        rule_path = repo_root / ".gzkit" / "rules" / "token-block-discipline.md"
        self.assertTrue(rule_path.is_file(), f"Missing rule file: {rule_path}")


if __name__ == "__main__":
    unittest.main()
