"""Tests asserting _requires_human_obpi_attestation returns True unconditionally.

REQ-0.0.36-02-01..05: ADR-0.0.36 universal OBPI attestation.
"""

from __future__ import annotations

import ast
import inspect
import re
import textwrap
import unittest

from gzkit.commands.adr_audit import (
    _enforce_human_attestation_authenticity,
    _is_foundation_adr,
    _requires_human_obpi_attestation,
)


def covers(target: str):
    def _identity(obj):
        return obj

    return _identity


@covers("OBPI-0.0.36-02")
class TestAttestationUniversality(unittest.TestCase):
    """REQ-0.0.36-02-01: gate returns True for all kind x lane inputs."""

    @covers("REQ-0.0.36-02-01")
    def test_gate_returns_true_for_foundation_lite(self):
        self.assertTrue(_requires_human_obpi_attestation("ADR-0.0.99-some-foundation", "lite"))

    @covers("REQ-0.0.36-02-01")
    def test_gate_returns_true_for_foundation_heavy(self):
        self.assertTrue(_requires_human_obpi_attestation("ADR-0.0.99-some-foundation", "heavy"))

    @covers("REQ-0.0.36-02-01")
    def test_gate_returns_true_for_feature_lite(self):
        # Previously returned False (self-closeable cell in the matrix).
        # ADR-0.0.36 collapses this cell: universal attestation required.
        self.assertTrue(_requires_human_obpi_attestation("ADR-0.1.0-some-feature", "lite"))

    @covers("REQ-0.0.36-02-01")
    def test_gate_returns_true_for_feature_heavy(self):
        self.assertTrue(_requires_human_obpi_attestation("ADR-0.1.0-some-feature", "heavy"))

    @covers("REQ-0.0.36-02-01")
    def test_gate_returns_true_for_parent_adr_none(self):
        # Previously returned False for None parent_adr. Collapse removes the guard.
        self.assertTrue(_requires_human_obpi_attestation(None, "lite"))


@covers("OBPI-0.0.36-02")
class TestGateBodyShape(unittest.TestCase):
    """REQ-0.0.36-02-02: function body collapses to a single return True.

    Asserts the structural REQ — the body has no conditional branching, returns
    True unconditionally — by inspecting the function source. The signature is
    preserved so call-sites compile unchanged.
    """

    @covers("REQ-0.0.36-02-02")
    def test_function_body_is_unconditional_return_true(self):
        source = textwrap.dedent(inspect.getsource(_requires_human_obpi_attestation))
        tree = ast.parse(source)
        func = tree.body[0]
        self.assertIsInstance(func, ast.FunctionDef)
        body = func.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body = body[1:]
        self.assertEqual(len(body), 1, "function body must contain a single statement")
        stmt = body[0]
        self.assertIsInstance(stmt, ast.Return)
        self.assertIsInstance(stmt.value, ast.Constant)
        self.assertIs(stmt.value.value, True)

    @covers("REQ-0.0.36-02-02")
    def test_function_signature_preserved(self):
        sig = inspect.signature(_requires_human_obpi_attestation)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ["parent_adr", "parent_lane", "brief_frontmatter"])
        self.assertIs(sig.parameters["brief_frontmatter"].default, None)


@covers("OBPI-0.0.36-02")
class TestIsFoundationAdrRetainedForTaxonomy(unittest.TestCase):
    """REQ-0.0.36-02-03: helper retained with docstring citing ADR-0.0.36 / OBPI-0.0.36-02."""

    @covers("REQ-0.0.36-02-03")
    def test_helper_still_exists_and_returns_classification(self):
        # Helper retained for taxonomy classification (not attestation routing).
        self.assertTrue(_is_foundation_adr("ADR-0.0.99-some-foundation"))
        self.assertFalse(_is_foundation_adr("ADR-0.1.0-some-feature"))

    @covers("REQ-0.0.36-02-03")
    def test_helper_docstring_cites_obpi_and_adr_and_disclaims_routing(self):
        doc = inspect.getdoc(_is_foundation_adr) or ""
        self.assertIn("ADR-0.0.36", doc)
        self.assertIn("OBPI-0.0.36-02", doc)
        # The docstring must explicitly disclaim attestation-routing load-bearing.
        self.assertTrue(
            re.search(r"no longer.*load.bearing.*attestation", doc, re.IGNORECASE),
            f"docstring must disclaim attestation-routing role; got: {doc!r}",
        )


@covers("OBPI-0.0.36-02")
class TestEnforceAuthenticityUnmodified(unittest.TestCase):
    """REQ-0.0.36-02-05 (acceptance) / -06 (req): authenticity gate must remain intact."""

    @covers("REQ-0.0.36-02-05")
    def test_authenticity_gate_three_branches_present(self):
        # Regression-invariant overlay: structural assertion that the three
        # branches (TTY, agent-relayed, fail-closed) preserved across the
        # ADR-0.0.36 collapse. Brief REQ-06 / Acceptance REQ-05 forbid
        # touching this function's body.
        source = inspect.getsource(_enforce_human_attestation_authenticity)
        self.assertIn("ATTESTATION_TYPE_HUMAN", source)
        self.assertIn("ATTESTATION_TYPE_AGENT_RELAYED", source)
        self.assertIn("GHI #290", source)


if __name__ == "__main__":
    unittest.main()
