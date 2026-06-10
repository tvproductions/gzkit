"""Regression test for the fail-open seam in audit_skill_alignment (REQ-0.0.69-03-04).

The bare ``except Exception: return []`` at
``src/gzkit/governance/trust_audits/cli.py:222-225`` silently swallows any
exception from ``_known_cli_verb_paths``, making the audit appear clean when
verb-path resolution is actually broken (fail-open).

This test FAILS until the seam is fixed:

    Before fix:  ``audit_skill_alignment`` returns ``[]`` (exception swallowed).
    After  fix:  the exception propagates — ``audit_skill_alignment`` raises,
                 or surfaces the failure as a non-empty ValidationError list.

The test patches ``_known_cli_verb_paths`` to raise ``ValueError`` and asserts
that ``audit_skill_alignment`` does NOT silently return ``[]``.

Covers:
    REQ-0.0.69-03-04 — ValidationError inside audit_skill_alignment must
        surface; not swallowed by bare except returning [].
"""

from __future__ import annotations

import tempfile
import unittest
import unittest.mock
from pathlib import Path

from gzkit.governance.trust_audits.cli import audit_skill_alignment
from gzkit.traceability import covers


class TestAuditSkillAlignmentSeam(unittest.TestCase):
    """REQ-0.0.69-03-04 — fail-open seam regression for audit_skill_alignment."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        # Create .gzkit/skills so the early-exit guard (line 219-221) does not
        # fire, ensuring execution reaches the _known_cli_verb_paths() call.
        (self.root / ".gzkit" / "skills").mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.69-03-04")
    def test_audit_skill_alignment_propagates_internal_error(self) -> None:
        """Bare ``except Exception: return []`` at cli.py:222-225 masks errors.

        Patching ``_known_cli_verb_paths`` to raise ``ValueError`` simulates
        any exception that verb-path resolution might produce (import failure,
        argparse internal error, etc.).

        Failure mode before fix: ``audit_skill_alignment`` returns ``[]``,
        masking the broken resolution as a clean audit result.

        Expected behavior after fix: the exception is NOT swallowed — it either
        propagates to the caller or is returned as a ValidationError in the
        list, making the failure visible.
        """
        from gzkit.governance.trust_audits import cli as cli_module

        raised_in_test: list[bool] = []

        with unittest.mock.patch.object(
            cli_module,
            "_known_cli_verb_paths",
            side_effect=ValueError("simulated verb-path resolution failure"),
        ):
            try:
                errors = audit_skill_alignment(self.root)
            except ValueError:
                # Exception propagated — fix strategy A (re-raise). Test passes.
                raised_in_test.append(True)
                return

        # Fix strategy B: exception surfaced as ValidationError in returned list.
        # If we reach here, no exception was raised — errors must be non-empty.
        self.assertGreater(
            len(errors),
            0,
            "Internal error from _known_cli_verb_paths must surface — "
            "not be swallowed by bare `except Exception: return []`. "
            f"Got: errors={errors!r}, raised={raised_in_test!r}",
        )


if __name__ == "__main__":
    unittest.main()
