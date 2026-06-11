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


class TestRetireLnConsumerChain(unittest.TestCase):
    """Consumer-side retirement of the ln: surface (GHI #601, direct repair).

    ADR-0.0.69-04 retired the ln: producer/schema/flag but left the read+render
    consumer chain alive as dead code (0 briefs carry ln:, so the render branch
    never fires). GHI #601 deletes it. These assert the consumer surface is
    absent — RED before the repair, GREEN after. No @covers: a GHI-tracked
    direct repair has no parent REQ.
    """

    def test_parse_ln_entries_helper_absent(self) -> None:
        """ceremony_data._parse_ln_entries must be deleted."""
        from gzkit.commands import ceremony_data

        self.assertFalse(
            hasattr(ceremony_data, "_parse_ln_entries"),
            "_parse_ln_entries still exists — the ln: parser was not deleted (GHI #601)",
        )

    def test_extract_brief_metadata_has_no_ln_entries_key(self) -> None:
        """extract_brief_metadata must no longer emit an ln_entries key."""
        import tempfile
        from pathlib import Path

        from gzkit.commands.ceremony_data import extract_brief_metadata

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", encoding="utf-8", delete=False
        ) as f:
            tmp = Path(f.name)
        try:
            tmp.write_text(
                "---\nid: OBPI-0.0.99-01-test\nstatus: Draft\nlane: Lite\n---\n\n"
                "# OBPI-0.0.99-01-test\n\n## Acceptance Criteria\n\n"
                "- [ ] REQ-0.0.99-01-01 [behavior]: does X\n",
                encoding="utf-8",
            )
            meta = extract_brief_metadata(tmp)
            self.assertNotIn(
                "ln_entries",
                meta,
                "extract_brief_metadata still emits ln_entries — consumer not retired (GHI #601)",
            )
        finally:
            tmp.unlink(missing_ok=True)

    def test_render_step_6_rejects_ln_entries_argument(self) -> None:
        """render_step_6_attestation must no longer accept an ln_entries argument."""
        from gzkit.commands.ceremony_steps import render_step_6_attestation

        with self.assertRaises(
            TypeError,
            msg="render_step_6_attestation still accepts ln_entries — not retired (GHI #601)",
        ):
            render_step_6_attestation("ADR-0.0.99-test", ln_entries=[])  # type: ignore[call-arg]


if __name__ == "__main__":
    unittest.main()
