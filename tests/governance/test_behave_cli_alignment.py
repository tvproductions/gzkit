"""Every ``gz <verb>`` in features and operator docs must resolve (GHI #198).

Unit-test entry to the audit; the canonical logic lives in
``gzkit.governance.trust_audits.audit_cli_alignment`` and is also exposed as
``gz validate --cli-alignment``.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_cli_alignment

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class BehaveCliAlignmentPolicy(unittest.TestCase):
    """No stale ``gz <verb>`` invocations may appear in behave features or operator docs."""

    def test_every_gz_verb_resolves(self) -> None:
        errors = audit_cli_alignment(_PROJECT_ROOT)
        self.assertFalse(
            errors,
            msg=(
                "Features or operator docs cite `gz <verb>` strings that do not "
                "resolve through the CLI parser. Fix the assertion or add the verb "
                "to the CLI before landing.\n"
                + "\n".join(f"  {e.artifact}: {e.message}" for e in errors)
            ),
        )


if __name__ == "__main__":
    unittest.main()
