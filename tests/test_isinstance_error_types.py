"""Type-mismatch errors are catchable as both TypeError and ValueError.

Each class below is raised only when an ``isinstance`` check fails. It is a
``TypeError`` for what it reports (Ruff TRY004) and a ``ValueError`` for the
handlers and Pydantic validators that caught it before the TRY003 repair
(operator ruling 2026-11-06, verbatim: "A").
"""

import unittest

from gzkit import acceptance_errors, codex_roles, ledger_producer_probe_errors, quality_errors
from gzkit.hooks import codex

TYPE_MISMATCH_ERRORS = (
    quality_errors.MkdocsConfigNotMappingError,
    quality_errors.MkdocsValidationNotMappingError,
    codex_roles.NonStringDeveloperInstructionsError,
    codex_roles.InvalidRoleMetadataError,
    codex_roles.MissingRolesMappingError,
    acceptance_errors.ReviewReceiptCommandError,
    ledger_producer_probe_errors.AcceptanceEventTypeError,
    ledger_producer_probe_errors.ReportEventTypeError,
    ledger_producer_probe_errors.LeaseExpiryEventTypeError,
    ledger_producer_probe_errors.RenewalEventTypeError,
    ledger_producer_probe_errors.WriterEventTypeError,
    codex.InvalidCodexHookConfigError,
)


class TestTypeMismatchErrorsCatchableBothWays(unittest.TestCase):
    def test_each_is_a_type_error_and_a_value_error(self):
        for error in TYPE_MISMATCH_ERRORS:
            with self.subTest(error=error.__name__):
                self.assertTrue(issubclass(error, TypeError))
                self.assertTrue(issubclass(error, ValueError))


if __name__ == "__main__":
    unittest.main()
