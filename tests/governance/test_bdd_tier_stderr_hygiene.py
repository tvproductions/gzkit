"""A passing BDD run must not emit failure-shaped prose (GHI #726).

The behave tier writes its captured stderr into ADR audit proofs via
``_print_command_output`` in ``gzkit.commands.gates``, unconditionally — pass or
fail. So any warning a scenario provokes becomes durable Gate-5 evidence, where
an exercised negative control and an ignored real warning read identically.

Two distinct causes produced the same symptom, and they need opposite fixes:

* A fixture brief whose acceptance-criteria line predates the four-tier REQ id
  shape. ``triangle`` warns correctly; the fixture is what drifted. Covered by
  ``FixtureBriefParses``.
* Negative controls whose observable IS a warning (``--receipt-shape``
  warn-only). Suppressing those at the source would delete the behavior under
  test, so the harness captures and asserts them instead. Covered by
  ``ExpectedWarningCapture``.
"""

from __future__ import annotations

import importlib.util
import logging
import sys
import types
import unittest
from pathlib import Path

from gzkit.triangle import extract_reqs_from_brief

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path) -> types.ModuleType:
    """Import a behave-tier module that lives outside any package."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - import plumbing
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FixtureBriefParses(unittest.TestCase):
    """The BDD fixture brief must satisfy the same REQ shape production briefs do."""

    def test_fixture_brief_yields_its_req_and_warns_nothing(self) -> None:
        steps = _load(
            "_bdd_attestation_receipt_binding_steps",
            _PROJECT_ROOT / "features" / "steps" / "attestation_receipt_binding_steps.py",
        )
        obpi_id = "OBPI-0.99.0-01-fixture"
        content = steps._BRIEF_TEMPLATE.format(
            obpi_id=obpi_id,
            adr_id="ADR-0.99.0-fixture",
            lane="Lite",
            req_id=steps._fixture_req_id(obpi_id),
        )

        with self.assertNoLogs("gzkit.triangle", level=logging.WARNING):
            reqs = extract_reqs_from_brief(content, obpi_id)

        self.assertEqual(
            [str(r.id) for r in reqs],
            ["REQ-0.99.0-01-01"],
            msg=(
                "The fixture brief's acceptance criteria must parse through the same "
                "extractor production briefs use. An unparseable line yields zero REQs "
                "AND a drift warning that lands in committed audit proofs (GHI #726)."
            ),
        )
        self.assertEqual(
            reqs[0].taxonomy_kind,
            "SUPPORT",
            msg=(
                "The fixture REQ must stay SUPPORT. BEHAVIOR is the one kind whose only "
                "proof channel is a @covers test, so tagging it BEHAVIOR would make the "
                "completion scenarios fail the REQ-coverage gate on an uncovered REQ — "
                "changing what these scenarios test, not just how the fixture parses."
            ),
        )

    def test_req_id_is_derived_from_the_obpi_it_belongs_to(self) -> None:
        """A hard-coded id would silently outlive a rename of the OBPI fixture."""
        steps = _load(
            "_bdd_attestation_receipt_binding_steps",
            _PROJECT_ROOT / "features" / "steps" / "attestation_receipt_binding_steps.py",
        )
        self.assertEqual(steps._fixture_req_id("OBPI-0.0.99-04-fixture"), "REQ-0.0.99-04-01")


class ExpectedWarningCapture(unittest.TestCase):
    """Scenarios whose observable is a warning capture it rather than leaking it."""

    def setUp(self) -> None:
        self.env = _load("_bdd_environment", _PROJECT_ROOT / "features" / "environment.py")
        self.context = types.SimpleNamespace()

    def _scenario(self, *tags: str) -> types.SimpleNamespace:
        return types.SimpleNamespace(tags=list(tags))

    def test_tagged_scenario_keeps_the_warning_off_the_root_logger(self) -> None:
        scenario = self._scenario(self.env.EXPECTED_WARNING_TAG)
        self.env.arm_expected_warnings(self.context, scenario)
        try:
            with self.assertNoLogs(level=logging.WARNING):
                logging.getLogger("gzkit.governance.trust_audits.receipt_shape").warning(
                    "pre-cutoff receipt drift"
                )
        finally:
            self.env.disarm_expected_warnings(self.context, scenario)

    def test_tagged_scenario_fails_when_its_expected_warning_never_fires(self) -> None:
        """The capture must not become a blanket mute — silence is a broken control."""
        scenario = self._scenario(self.env.EXPECTED_WARNING_TAG)
        self.env.arm_expected_warnings(self.context, scenario)
        with self.assertRaises(AssertionError):
            self.env.disarm_expected_warnings(self.context, scenario)

    def test_untagged_scenario_is_left_alone(self) -> None:
        """An untagged scenario must keep propagating, or real warnings vanish."""
        scenario = self._scenario("@REQ-0.0.24-01-01")
        self.env.arm_expected_warnings(self.context, scenario)
        try:
            with self.assertLogs(
                "gzkit.governance.trust_audits.receipt_shape", level=logging.WARNING
            ):
                logging.getLogger("gzkit.governance.trust_audits.receipt_shape").warning(
                    "a real warning nobody armed for"
                )
        finally:
            self.env.disarm_expected_warnings(self.context, scenario)


if __name__ == "__main__":
    unittest.main()
