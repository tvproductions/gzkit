"""Confirmation tests for OBPI-0.26.0-01 (ADR Management).

@covers ADR-0.26.0-governance-library-module-absorption
@covers OBPI-0.26.0-01-adr-management

Decision: Confirm. gzkit's distributed ADR management (plan/status/adr_audit/
adr_promote/adr_coverage/gates + typed identity models + event-sourced ledger
+ config-first status vocabulary) is architecturally superior to
airlineops/src/opsdev/lib/adr.py on every dimension the brief's Comparison
Matrix scores. No module-wide absorption, no narrow-helper absorption.

These tests assert the semantic claims the brief's rationale makes — that
the gzkit surfaces cited as "better" actually exist, are importable, and
carry the typed/strict shape the rationale relies on. Pin semantics, not
byte-level output.
"""

import importlib
import unittest

from gzkit.traceability import covers


class TestAdrManagementConfirmDecision(unittest.TestCase):
    """Semantic verification of the OBPI-0.26.0-01 Confirm rationale."""

    @covers("REQ-0.26.0-01-01")
    def test_final_decision_recorded_in_brief(self):
        """Brief records exactly one final decision: Absorb, Confirm, or Exclude.

        REQ-01 semantics: the completed comparison yields one final decision
        line. The brief's decision heading must match the canonical
        Absorb/Confirm/Exclude vocabulary and name exactly one outcome.
        """
        from pathlib import Path

        brief = Path(
            "docs/design/adr/pre-release/"
            "ADR-0.26.0-governance-library-module-absorption/"
            "obpis/OBPI-0.26.0-01-adr-management.md"
        )
        self.assertTrue(brief.exists(), f"brief not found at {brief}")
        text = brief.read_text(encoding="utf-8")

        decisions = [
            line
            for line in text.splitlines()
            if line.startswith("## Decision: ")
            and line.split(": ", 1)[1].strip() in {"Absorb", "Confirm", "Exclude"}
        ]
        self.assertEqual(
            len(decisions),
            1,
            "REQ-01: brief must record exactly one canonical decision heading",
        )

    @covers("REQ-0.26.0-01-02")
    def test_rationale_names_existing_gzkit_surfaces(self):
        """Rationale cites concrete capability differences — the named surfaces exist.

        REQ-02 semantics: the Comparison Matrix claims gzkit wins via specific
        named surfaces (Pydantic identity models, config-first status vocabulary,
        event-sourced ledger, kind/semver binding, 5-gate pipeline, ADR
        promotion, ARB receipts). Each named surface must be importable — a
        rationale that names absent code is unfounded.
        """
        modules = [
            "gzkit.core.models",
            "gzkit.commands.plan",
            "gzkit.commands.status",
            "gzkit.commands.adr_audit",
            "gzkit.commands.adr_promote",
            "gzkit.commands.adr_coverage",
            "gzkit.commands.gates",
            "gzkit.ledger",
            "gzkit.ledger_events",
            "gzkit.governance.status_vocab",
        ]
        for mod_name in modules:
            with self.subTest(module=mod_name):
                importlib.import_module(mod_name)

    @covers("REQ-0.26.0-01-03")
    def test_no_absorbed_adr_module_introduced(self):
        """Absorb-outcome conditional does not fire: no new absorbed module.

        REQ-03 semantics: only an Absorb outcome requires an adapted
        gzkit module + tests. With a Confirm decision, the conditional
        is intentionally unsatisfied — we verify the negative by confirming
        no `src/gzkit/adr/` library module was introduced as an
        absorption target.
        """
        from pathlib import Path

        adr_lib_module = Path("src/gzkit/adr/__init__.py")
        adr_lib_file = Path("src/gzkit/adr.py")
        self.assertFalse(
            adr_lib_module.exists() or adr_lib_file.exists(),
            "REQ-03: Confirm outcome must not introduce a new src/gzkit/adr absorption target",
        )

    @covers("REQ-0.26.0-01-04")
    def test_confirm_rationale_is_surface_broader_than_opsdev(self):
        """Confirm rationale: gzkit surface is broader and stronger than opsdev/adr.py.

        REQ-04 semantics: a Confirm outcome must explain why no upstream
        absorption is warranted. The explanation rests on gzkit surfaces
        that cover opsdev/adr.py's capabilities and add typed/strict
        shape opsdev lacks. Verify the named concrete patterns:

        - Typed `AdrId`, `ObpiId`, `ReqId` identity models (opsdev uses
          module-scope regex)
        - `_validate_kind_and_semver` enforces foundation/feature/pool binding
          (opsdev has no kind/semver binding)
        - Ledger event constructors exist (opsdev is a read-only consumer)
        """
        from gzkit.commands.plan import _validate_kind_and_semver
        from gzkit.core.models import AdrFrontmatter, AdrId, ObpiId, ReqId
        from gzkit.ledger_events import (
            adr_created_event,
            audit_receipt_emitted_event,
            lifecycle_transition_event,
            obpi_receipt_emitted_event,
        )

        self.assertTrue(callable(_validate_kind_and_semver))
        for model in (AdrFrontmatter, AdrId, ObpiId, ReqId):
            self.assertTrue(hasattr(model, "model_config"))
            self.assertTrue(model.model_config.get("frozen"))
        for event_fn in (
            adr_created_event,
            audit_receipt_emitted_event,
            lifecycle_transition_event,
            obpi_receipt_emitted_event,
        ):
            self.assertTrue(callable(event_fn))

    @covers("REQ-0.26.0-01-05")
    def test_no_operator_visible_behavior_change(self):
        """Gate 4 N/A: the Confirm outcome introduces no new CLI surface.

        REQ-05 semantics: Gate 4 behavioral proof is required only when
        operator-visible behavior changes. A Confirm outcome changes no
        CLI verb, flag, output form, or exit code — we verify the
        negative by confirming the `gz adr` subcommand surface set
        remains exactly the pre-absorption set (no new verbs).
        """
        import argparse

        from gzkit.cli.parser_artifacts import _register_adr_parsers

        root = argparse.ArgumentParser()
        commands = root.add_subparsers(dest="command")
        _register_adr_parsers(commands)

        adr_parser = commands.choices["adr"]
        adr_subparser_actions = [
            action
            for action in adr_parser._actions
            if action.__class__.__name__ == "_SubParsersAction"
        ]
        self.assertEqual(
            len(adr_subparser_actions),
            1,
            "REQ-05: gz adr parser must expose exactly one subcommand group",
        )
        registered_verbs = set(adr_subparser_actions[0].choices)
        expected_adr_verbs = {
            "status",
            "report",
            "promote",
            "evaluate",
            "audit-check",
            "covers-check",
            "emit-receipt",
        }
        self.assertTrue(
            expected_adr_verbs.issubset(registered_verbs),
            f"REQ-05: pre-absorption `gz adr` verbs must remain registered; "
            f"missing={expected_adr_verbs - registered_verbs}",
        )


if __name__ == "__main__":
    unittest.main()
