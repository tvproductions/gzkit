"""Tests for gz validate --fidelity-presence (OBPI-0.0.73-08).

Mechanizes Boundary Invariant #4: every non-pool ADR Decision must carry a
parseable ``## Fidelity Assertions`` block. These tests assert the behavioral
contract from the brief's Acceptance Criteria:

  REQ-0.0.73-08-01  block-less non-pool ADR → finding (CLI exit 3)
  REQ-0.0.73-08-02  compliant corpus → no findings AND step wired into gz check
  REQ-0.0.73-08-03  grandfathered block-less passes; a NEW one fails closed
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.fidelity_presence import (
    _load_grandfather,
    audit_fidelity_presence,
)
from gzkit.traceability import covers

_BLOCK = (
    "\n## Fidelity Assertions\n\n"
    "| Claim | Command | Expected exit |\n"
    "|-------|---------|---------------|\n"
    "| The thing works against the real system. | uv run gz --version | 0 |\n"
)


def _make_adr(root: Path, adr_id: str, *, with_block: bool, tier: str = "foundation") -> Path:
    """Write a minimal ADR Decision package; return the Decision file path."""
    pkg = root / "docs" / "design" / "adr" / tier / adr_id
    pkg.mkdir(parents=True, exist_ok=True)
    body = (
        f"---\nid: {adr_id}\nkind: foundation\nlane: Lite\n---\n# {adr_id}\n\n## Decision\n\nX.\n"
    )
    if with_block:
        body += _BLOCK
    decision = pkg / f"{adr_id}.md"
    decision.write_text(body, encoding="utf-8")
    return decision


class TestBlockLessFlagged(unittest.TestCase):
    """A block-less non-pool ADR Decision is flagged (REQ-0.0.73-08-01)."""

    @covers("REQ-0.0.73-08-01")
    def test_block_less_adr_produces_one_finding_naming_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_adr(root, "ADR-0.0.1-blockless", with_block=False)
            errors = audit_fidelity_presence(root, grandfather=frozenset())
        self.assertEqual(len(errors), 1, [e.message for e in errors])
        self.assertEqual(errors[0].type, "fidelity-presence")
        self.assertEqual(errors[0].artifact, "ADR-0.0.1-blockless")
        self.assertIn("ADR-0.0.1-blockless", errors[0].message)

    @covers("REQ-0.0.73-08-01")
    def test_recovery_prose_names_block_and_next_step(self) -> None:
        # Three-part recovery prose (guardrail-feedback-prose.md): what failed,
        # the cited invariant, and a runnable next step.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_adr(root, "ADR-0.0.2-blockless", with_block=False)
            errors = audit_fidelity_presence(root, grandfather=frozenset())
        message = errors[0].message
        self.assertIn("Fidelity Assertions", message)
        self.assertIn("Boundary Invariant #4", message)
        self.assertIn("gz validate --fidelity-presence", message)

    @covers("REQ-0.0.73-08-01")
    def test_empty_block_is_treated_as_missing(self) -> None:
        # A heading with no data rows is not a parseable block (parser raises).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decision = _make_adr(root, "ADR-0.0.3-emptyblock", with_block=False)
            decision.write_text(
                decision.read_text(encoding="utf-8") + "\n## Fidelity Assertions\n\n(none yet)\n",
                encoding="utf-8",
            )
            errors = audit_fidelity_presence(root, grandfather=frozenset())
        self.assertEqual(len(errors), 1, [e.message for e in errors])


class TestCompliantCorpusAndWiring(unittest.TestCase):
    """Compliant corpus passes; the step is wired into gz check (REQ-0.0.73-08-02)."""

    @covers("REQ-0.0.73-08-02")
    def test_compliant_adr_produces_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_adr(root, "ADR-0.0.1-compliant", with_block=True)
            errors = audit_fidelity_presence(root, grandfather=frozenset())
        self.assertEqual(errors, [], [e.message for e in errors])

    @covers("REQ-0.0.73-08-02")
    def test_step_is_in_gz_check_step_list(self) -> None:
        from gzkit.commands.quality import _build_check_steps

        names = [name for name, _ in _build_check_steps()]
        self.assertIn("Fidelity presence", names)

    @covers("REQ-0.0.73-08-02")
    def test_step_is_classified_and_builds_into_registry(self) -> None:
        from gzkit.qc_binding import _STEP_CLASSIFICATION, build_qc_registry

        self.assertIn("Fidelity presence", _STEP_CLASSIFICATION)
        registry = build_qc_registry()
        match = [s for s in registry if s.id == "fidelity-presence"]
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0].binding, "bound")

    @covers("REQ-0.0.73-08-02")
    def test_negative_control_is_registered_and_genuine(self) -> None:
        # The bound step must carry a GENUINE negative control: registered via the
        # single @enforces primitive and PASSing its un-forced run against the
        # block-less fixture. (ADR-0.0.74 OBPI-0.0.74-16 lifted the engine; there is
        # no _NEGATIVE_CONTROL_DEBT escape to be excluded from.)
        from gzkit.enforcement import (
            _ensure_production_claims_registered,
            _run_single_claim,
            get_enforcement_registry,
        )

        _ensure_production_claims_registered()
        records = {r.claim_id: r for r in get_enforcement_registry()}
        self.assertIn("fidelity-presence", records)
        result = _run_single_claim(records["fidelity-presence"])
        self.assertEqual(result.outcome, "PASS")

    @covers("REQ-0.0.73-08-02")
    def test_pool_and_closeout_decisions_are_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # A block-less pool ADR must NOT be flagged (BI #7 scopes to non-pool).
            _make_adr(root, "ADR-pool.demo", with_block=False, tier="pool")
            # A closeout-form sidecar matches ADR-*.md but is not a Decision.
            closeout = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.9-x"
            closeout.mkdir(parents=True, exist_ok=True)
            (closeout / "ADR-0.0.9-x.md").write_text(f"# ADR-0.0.9-x\n{_BLOCK}", encoding="utf-8")
            (closeout / "ADR-CLOSEOUT-FORM.md").write_text("# closeout\n", encoding="utf-8")
            errors = audit_fidelity_presence(root, grandfather=frozenset())
        self.assertEqual(errors, [], [e.message for e in errors])


class TestGrandfatherCutover(unittest.TestCase):
    """Grandfathered block-less ADRs pass; a NEW one fails closed (REQ-0.0.73-08-03)."""

    @covers("REQ-0.0.73-08-03")
    def test_grandfathered_block_less_adr_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_adr(root, "ADR-0.0.1-legacy", with_block=False)
            errors = audit_fidelity_presence(root, grandfather=frozenset({"ADR-0.0.1-legacy"}))
        self.assertEqual(errors, [], [e.message for e in errors])

    @covers("REQ-0.0.73-08-03")
    def test_new_block_less_adr_not_in_grandfather_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_adr(root, "ADR-0.0.1-legacy", with_block=False)
            _make_adr(root, "ADR-0.9.0-fresh", with_block=False, tier="pre-release")
            errors = audit_fidelity_presence(root, grandfather=frozenset({"ADR-0.0.1-legacy"}))
        self.assertEqual(len(errors), 1, [e.message for e in errors])
        self.assertEqual(errors[0].artifact, "ADR-0.9.0-fresh")

    @covers("REQ-0.0.73-08-03")
    def test_grandfather_loader_missing_file_grandfathers_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(_load_grandfather(Path(tmp)), frozenset())

    @covers("REQ-0.0.73-08-03")
    def test_grandfather_loader_reads_declared_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gf = root / "data" / "fidelity_presence_grandfather.json"
            gf.parent.mkdir(parents=True, exist_ok=True)
            gf.write_text(
                json.dumps({"grandfathered_adrs": ["ADR-0.0.1-legacy", "ADR-0.0.2-legacy"]}),
                encoding="utf-8",
            )
            loaded = _load_grandfather(root)
        self.assertEqual(loaded, frozenset({"ADR-0.0.1-legacy", "ADR-0.0.2-legacy"}))


class TestRealCorpusGreen(unittest.TestCase):
    """The live project corpus passes under the committed grandfather (REQ-0.0.73-08-03)."""

    @covers("REQ-0.0.73-08-03")
    def test_live_corpus_is_green(self) -> None:
        # Loads the committed grandfather file; the gate must be green today.
        errors = audit_fidelity_presence(Path("."))
        self.assertEqual(errors, [], [e.artifact for e in errors])


if __name__ == "__main__":
    unittest.main()
