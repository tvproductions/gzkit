"""GHI #1155 — `gz validate --gate-enrollment` reaches its audit and reports its verdict.

Routed through the real parser so a dropped flag, dispatch entry or handler fails here,
not only in the unit tests of the audit it calls.
"""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest import mock

from gzkit.cli.main import main
from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.gate_enrollment import (
    claimed_functions,
    enrolled_claims,
    scope_population,
)
from gzkit.governance.trust_audits.gate_population import population_members

_AUDIT = "gzkit.governance.trust_audits.gate_enrollment.audit_gate_enrollment"
_POPULATION_AUDIT = "gzkit.governance.trust_audits.gate_population.audit_gate_population_enrollment"


def _run(
    argv: list[str],
    findings: list[ValidationError],
    population_findings: list[ValidationError] | None = None,
) -> tuple[int, str]:
    out = io.StringIO()
    with (
        mock.patch(_AUDIT, return_value=findings) as audit,
        mock.patch(_POPULATION_AUDIT, return_value=population_findings or []) as other,
        contextlib.redirect_stdout(out),
    ):
        code = main(argv)
    audit.assert_called_once()
    other.assert_called_once()
    return code, out.getvalue()


class TestGateEnrollmentCli(unittest.TestCase):
    def test_clean_audit_exits_zero_and_reports_counts_derived_from_the_registries(self):
        code, out = _run(["validate", "--gate-enrollment"], [])
        population = scope_population()
        claimed = claimed_functions()
        enrolled = sum(1 for fns in population.values() if enrolled_claims(fns, claimed))
        self.assertEqual(code, 0)
        self.assertIn(f"{len(population)} validate scopes inventoried", out)
        self.assertIn(f"{enrolled} named by an enforcement claim", out)
        # Rich wraps the line, so compare on collapsed whitespace.
        collapsed = " ".join(out.split())
        self.assertIn(f"{len(population) - enrolled} disclosed as unenrolled", collapsed)

    def test_clean_audit_also_reports_the_other_gate_populations(self):
        code, out = _run(["validate", "--gate-enrollment"], [])
        members = population_members()
        enrolled = sum(1 for fns in members.values() if enrolled_claims(fns, claimed_functions()))
        collapsed = " ".join(out.split())
        self.assertEqual(code, 0)
        self.assertIn(f"{len(members)} other gates inventoried", collapsed)
        self.assertIn(f"{len(members) - enrolled} disclosed as unenrolled", collapsed)

    def test_a_population_finding_alone_exits_three_and_names_the_gate(self):
        finding = ValidationError(
            type="gate-enrollment", artifact="complete-refusal:_new_gate", message="no claim"
        )
        code, out = _run(["validate", "--gate-enrollment"], [], [finding])
        self.assertEqual(code, 3)
        self.assertIn("complete-refusal:_new_gate", out)

    def test_a_finding_exits_three_and_names_the_scope(self):
        finding = ValidationError(type="gate-enrollment", artifact="some_scope", message="no claim")
        code, out = _run(["validate", "--gate-enrollment"], [finding])
        self.assertEqual(code, 3)
        self.assertIn("some_scope", out)

    def test_json_mode_emits_the_findings_and_exits_three(self):
        finding = ValidationError(type="gate-enrollment", artifact="some_scope", message="no claim")
        code, out = _run(["validate", "--gate-enrollment", "--json"], [finding])
        self.assertEqual(code, 3)
        self.assertEqual([f["artifact"] for f in json.loads(out)], ["some_scope"])


if __name__ == "__main__":
    unittest.main()
