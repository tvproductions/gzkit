"""Retirement assertions for the ln: closeout-proof-binding surface (OBPI-0.0.69-04).

These tests are intentionally RED before OBPI-0.0.69-04 lands and GREEN after.
Each test asserts the ABSENCE of a surface that must be deleted.

Covers:
    REQ-0.0.69-04-01 — closeout_proof_binding module, ReqEvidence class, and
        BriefStructure.ln field must not exist.
    REQ-0.0.69-04-02 — --closeout-proof-binding flag must be rejected as
        unknown (exit 2, argparse error).
    REQ-0.0.69-04-03 — _inject_ln_block / _render_ln_block / _strip_existing_ln
        must not exist as attributes on the obpi_complete module.
    REQ-0.0.69-04-04 — BriefStructure must reject ln: via extra="forbid" after
        the ln field is removed.
"""

from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
import unittest

from gzkit.traceability import covers


class TestRetireLnSurface(unittest.TestCase):
    @covers("REQ-0.0.69-04-01")
    def test_closeout_proof_binding_module_absent(self) -> None:
        """closeout_proof_binding must not be importable after retirement."""
        spec = importlib.util.find_spec("gzkit.governance.trust_audits.closeout_proof_binding")
        self.assertIsNone(
            spec,
            "gzkit.governance.trust_audits.closeout_proof_binding is still importable "
            "— the module was not deleted (OBPI-0.0.69-04 REQ-01)",
        )

    @covers("REQ-0.0.69-04-01")
    def test_req_evidence_and_ln_field_absent(self) -> None:
        """ReqEvidence class and BriefStructure.ln field must not exist."""
        import gzkit.governance.brief_structure as bs_mod

        self.assertFalse(
            hasattr(bs_mod, "ReqEvidence"),
            "ReqEvidence class still exists on gzkit.governance.brief_structure "
            "— it was not deleted (OBPI-0.0.69-04 REQ-01)",
        )

        from gzkit.governance.brief_structure import BriefStructure

        self.assertNotIn(
            "ln",
            BriefStructure.model_fields,
            "BriefStructure.ln field still exists — it was not deleted (OBPI-0.0.69-04 REQ-01)",
        )

    @covers("REQ-0.0.69-04-02")
    def test_closeout_proof_binding_flag_unknown(self) -> None:
        """gz validate --closeout-proof-binding must exit 2 (unrecognized argument)."""
        result = subprocess.run(
            [sys.executable, "-m", "gzkit", "validate", "--closeout-proof-binding"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode,
            2,
            f"Expected exit 2 (argparse unrecognized argument) but got "
            f"{result.returncode}. stderr={result.stderr!r}. "
            "The --closeout-proof-binding flag still exists "
            "(OBPI-0.0.69-04 REQ-02)",
        )

    @covers("REQ-0.0.69-04-03")
    def test_inject_ln_functions_absent(self) -> None:
        """_inject_ln_block, _render_ln_block, _strip_existing_ln must not exist."""
        import gzkit.commands.obpi_complete as oc_mod

        for fn_name in ("_inject_ln_block", "_render_ln_block", "_strip_existing_ln"):
            self.assertFalse(
                hasattr(oc_mod, fn_name),
                f"{fn_name} still exists on gzkit.commands.obpi_complete "
                f"— the #599 producer was not deleted (OBPI-0.0.69-04 REQ-03)",
            )

    @covers("REQ-0.0.69-04-04")
    def test_ln_field_forbidden_on_brief_structure(self) -> None:
        """BriefStructure must reject ln= via extra='forbid' after field removal."""
        from pydantic import ValidationError

        from gzkit.governance.brief_structure import BriefStructure

        with self.assertRaises(
            ValidationError,
            msg="BriefStructure accepted ln= without raising ValidationError — "
            "the ln field still exists and extra='forbid' is not blocking it "
            "(OBPI-0.0.69-04 REQ-04)",
        ):
            BriefStructure(
                id="OBPI-0.0.99-01-test",
                parent="ADR-0.0.99-test",
                lane="Lite",
                status="Draft",
                allowlist=["tests/"],
                reqs=["REQ-0.0.99-01-01"],
                verification=["uv run gz lint"],
                ln=[],
            )


if __name__ == "__main__":
    unittest.main()
