"""Time-bomb test: fail CI if any flag is past its remove_by date.

This is a standalone test file per ADR-0.0.8 Section 6.6 so that CI
failure messages are unambiguous.  It loads the actual ``data/flags.json``
registry and fails if any flag has outlived its ``remove_by`` deadline.

@covers OBPI-0.0.8-04-diagnostics-and-staleness
"""

import unittest
from datetime import date

from gzkit.flags.registry import load_registry
from gzkit.traceability import covers


class TestNoExpiredFlags(unittest.TestCase):
    """Standalone CI guard: no flag may be past its remove_by date."""

    @covers("REQ-0.0.8-04-02")
    @covers("REQ-0.0.8-04-03")
    def test_no_expired_flags(self) -> None:
        """Load data/flags.json and fail if any flag is past remove_by."""
        registry = load_registry()
        today = date.today()

        expired: list[str] = []
        for spec in registry.values():
            if spec.remove_by is not None and spec.remove_by < today:
                expired.append(
                    f"  {spec.key} (remove_by={spec.remove_by}, category={spec.category.value})"
                )

        if expired:
            msg = (
                f"{len(expired)} expired flag(s) found — "
                "remove these flags and their code paths:\n" + "\n".join(expired)
            )
            self.fail(msg)


if __name__ == "__main__":
    unittest.main()
