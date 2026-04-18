"""Every validator-read graph field must have a graph-writer (GHI #193 class).

Unit-test entry to the audit; the canonical logic lives in
``gzkit.governance.trust_audits.audit_validator_fields`` and is also exposed as
``gz validate --validator-fields``.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_validator_fields

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ValidatorGraphFieldCoverage(unittest.TestCase):
    """Every ``info.get(...)`` field the validator reads must be written by the graph builder."""

    def test_every_field_is_populated(self) -> None:
        errors = audit_validator_fields(_PROJECT_ROOT)
        self.assertFalse(
            errors,
            msg=(
                "Validator reads artifact-graph fields that are never written by "
                "src/gzkit/ledger.py. Either add population in a "
                "_apply_*_metadata handler (or the creation entry), or remove "
                "the read.\n" + "\n".join(f"  {e.artifact}: {e.message}" for e in errors)
            ),
        )


if __name__ == "__main__":
    unittest.main()
