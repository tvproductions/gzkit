"""Tests asserting _requires_human_obpi_attestation returns True unconditionally.

REQ-0.0.36-02-01..05: ADR-0.0.36 universal OBPI attestation.
"""

import ast
import inspect
import re
import subprocess
import textwrap
import unittest
from pathlib import Path

from gzkit.commands.adr_audit import (
    _is_foundation_adr,
    _requires_human_obpi_attestation,
)
from tests.commands.common import _isolated_git_env


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
        assert isinstance(func, ast.FunctionDef)
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
        assert isinstance(stmt, ast.Return)
        value = stmt.value
        self.assertIsInstance(value, ast.Constant)
        assert isinstance(value, ast.Constant)
        self.assertIs(value.value, True)

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


_GATE_PATH = "src/gzkit/commands/adr_audit.py"
_GATE_NAME = "_enforce_human_attestation_authenticity"
# OBPI-0.0.36-02's landing: the commit inside its lock window (2026-05-17T23:36Z
# to 2026-05-18T00:19Z on the ledger) that collapsed _requires_human_obpi_attestation.
_OBPI_LANDING = "e9ebd770f3a11c820443a2cc9bc1f63548be08d7"


def _gate_body_at(rev: str) -> str:
    """Return the authenticity gate's source as it stood at *rev*."""
    shown = subprocess.run(  # noqa: S603 -- fixed argv; rev and path are module constants
        ["git", "show", f"{rev}:{_GATE_PATH}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
        cwd=Path(__file__).resolve().parents[2],
        env=_isolated_git_env(),
    )
    for node in ast.walk(ast.parse(shown.stdout)):
        if isinstance(node, ast.FunctionDef) and node.name == _GATE_NAME:
            return ast.get_source_segment(shown.stdout, node) or ""
    return ""


@covers("OBPI-0.0.36-02")
class TestEnforceAuthenticityUnmodified(unittest.TestCase):
    """REQ-0.0.36-02-05: OBPI-0.0.36-02 left the authenticity gate's body byte-identical.

    The REQ asserts a property of that OBPI's own diff: "Given
    `_enforce_human_attestation_authenticity` after this OBPI, when compared to its
    pre-OBPI implementation, then the function body is byte-identical (this OBPI does
    not touch the authenticity gate)." It once read the live function, which made it
    look like a standing freeze. GHI #1308 removed the gate ADR-0.0.36's 2026-05-14
    addendum records as removed, and the operator ruled (2026-11-06, verbatim "A")
    that the REQ is a claim about the OBPI's diff, so it stays true of history and its
    proof re-points to that history (docs/governance/attested-req-subject-retirement.md,
    doctrine-neutral case). The proof compares the body on either side of the OBPI's
    landing commit, which CI's full-depth checkout carries.
    """

    @covers("REQ-0.0.36-02-05")
    def test_obpi_landing_left_the_gate_body_byte_identical(self):
        before = _gate_body_at(f"{_OBPI_LANDING}^")
        after = _gate_body_at(_OBPI_LANDING)
        self.assertTrue(before, "the gate must exist before the OBPI's landing")
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
