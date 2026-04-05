"""Tests for persona drift detection engine.

@covers ADR-0.0.13-portable-persona-control-surface
@covers OBPI-0.0.13-05-persona-drift-monitoring
"""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.personas import (
    TRAIT_PROXY_REGISTRY,
    _check_trait,
    _completion_quality_proxy,
    _evidence_quality_proxy,
    _governance_activity_proxy,
    _plan_discipline_proxy,
    _test_evidence_proxy,
    evaluate_persona_drift,
)
from gzkit.traceability import covers

_PERSONA_TEMPLATE = """\
---
name: {name}
traits:
{traits}
anti-traits:
{anti_traits}
grounding: Test persona.
---

# {name} Persona
"""


def _write_persona(
    personas_dir: Path, name: str, traits: list[str], anti_traits: list[str]
) -> None:
    traits_yaml = "\n".join(f"  - {t}" for t in traits)
    anti_yaml = "\n".join(f"  - {t}" for t in anti_traits)
    content = _PERSONA_TEMPLATE.format(name=name, traits=traits_yaml, anti_traits=anti_yaml)
    (personas_dir / f"{name}.md").write_text(content, encoding="utf-8")


def _write_ledger(root: Path, events: list[dict]) -> None:
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(e) for e in events]
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_audit_log(root: Path, records: list[dict]) -> None:
    log_dir = root / "docs" / "design" / "adr" / "test-adr" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(r) for r in records]
    (log_dir / "obpi-audit.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")


class TestTraitProxyRegistry(unittest.TestCase):
    """Verify proxy registry maps known traits to functions."""

    GOVERNANCE_TRAITS = ["governance-aware", "governance-fidelity", "evidence-anchoring"]
    TEST_TRAITS = ["test-first", "thorough", "architectural-rigor"]
    EVIDENCE_TRAITS = ["evidence-driven", "evidence-based-assessment", "precision"]
    COMPLETION_TRAITS = ["complete-units", "atomic-edits", "ceremony-completion"]
    PLAN_TRAITS = ["methodical", "plan-then-write", "stage-discipline", "sequential-flow"]

    @covers("REQ-0.0.13-05-01")
    def test_governance_traits_mapped(self) -> None:
        for trait in self.GOVERNANCE_TRAITS:
            with self.subTest(trait=trait):
                self.assertIn(trait, TRAIT_PROXY_REGISTRY)
                name, _fn = TRAIT_PROXY_REGISTRY[trait]
                self.assertEqual(name, "governance_activity")

    @covers("REQ-0.0.13-05-01")
    def test_test_traits_mapped(self) -> None:
        for trait in self.TEST_TRAITS:
            with self.subTest(trait=trait):
                self.assertIn(trait, TRAIT_PROXY_REGISTRY)
                name, _fn = TRAIT_PROXY_REGISTRY[trait]
                self.assertEqual(name, "test_evidence")

    @covers("REQ-0.0.13-05-01")
    def test_evidence_traits_mapped(self) -> None:
        for trait in self.EVIDENCE_TRAITS:
            with self.subTest(trait=trait):
                self.assertIn(trait, TRAIT_PROXY_REGISTRY)

    @covers("REQ-0.0.13-05-01")
    def test_completion_traits_mapped(self) -> None:
        for trait in self.COMPLETION_TRAITS:
            with self.subTest(trait=trait):
                self.assertIn(trait, TRAIT_PROXY_REGISTRY)

    @covers("REQ-0.0.13-05-01")
    def test_plan_traits_mapped(self) -> None:
        for trait in self.PLAN_TRAITS:
            with self.subTest(trait=trait):
                self.assertIn(trait, TRAIT_PROXY_REGISTRY)

    @covers("REQ-0.0.13-05-01")
    def test_unmapped_trait_returns_no_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _check_trait("some-unknown-trait", Path(tmp), [], [])
            self.assertEqual(result.status, "no_evidence")
            self.assertEqual(result.proxy, "unmapped")


class TestGovernanceActivityProxy(unittest.TestCase):
    """Test governance activity proxy with synthetic events."""

    @covers("REQ-0.0.13-05-01")
    def test_pass_when_gate_events_present(self) -> None:
        events: list[dict[str, object]] = [
            {"event": "gate_checked", "ts": "2026-01-01T00:00:00Z"},
            {"event": "attested", "ts": "2026-01-02T00:00:00Z"},
        ]
        status, detail = _governance_activity_proxy(Path("."), events, [])
        self.assertEqual(status, "pass")
        self.assertIn("2", detail)

    @covers("REQ-0.0.13-05-01")
    def test_fail_when_no_events(self) -> None:
        status, _detail = _governance_activity_proxy(Path("."), [], [])
        self.assertEqual(status, "fail")

    @covers("REQ-0.0.13-05-01")
    def test_ignores_non_governance_events(self) -> None:
        events: list[dict[str, object]] = [{"event": "adr_created", "ts": "2026-01-01T00:00:00Z"}]
        status, _detail = _governance_activity_proxy(Path("."), events, [])
        self.assertEqual(status, "fail")


class TestTestEvidenceProxy(unittest.TestCase):
    """Test evidence proxy with synthetic audit records."""

    @covers("REQ-0.0.13-05-02")
    def test_pass_with_passing_tests(self) -> None:
        audits: list[dict[str, object]] = [
            {"evidence": {"test_count": 10, "tests_passed": True}},
        ]
        status, detail = _test_evidence_proxy(Path("."), [], audits)
        self.assertEqual(status, "pass")
        self.assertIn("10", detail)

    @covers("REQ-0.0.13-05-02")
    def test_fail_with_zero_tests(self) -> None:
        audits: list[dict[str, object]] = [
            {"evidence": {"test_count": 0, "tests_passed": True}},
        ]
        status, _detail = _test_evidence_proxy(Path("."), [], audits)
        self.assertEqual(status, "fail")

    @covers("REQ-0.0.13-05-02")
    def test_fail_with_no_audits(self) -> None:
        status, _detail = _test_evidence_proxy(Path("."), [], [])
        self.assertEqual(status, "fail")


class TestEvidenceQualityProxy(unittest.TestCase):
    """Test evidence quality proxy."""

    @covers("REQ-0.0.13-05-02")
    def test_pass_with_criteria(self) -> None:
        audits: list[dict[str, object]] = [
            {
                "evidence": {
                    "criteria_evaluated": [
                        {"criterion": "REQ-1", "result": "PASS", "evidence": "test passes"},
                    ],
                },
            },
        ]
        status, _detail = _evidence_quality_proxy(Path("."), [], audits)
        self.assertEqual(status, "pass")

    @covers("REQ-0.0.13-05-02")
    def test_fail_without_criteria(self) -> None:
        audits: list[dict[str, object]] = [{"evidence": {}}]
        status, _detail = _evidence_quality_proxy(Path("."), [], audits)
        self.assertEqual(status, "fail")


class TestCompletionQualityProxy(unittest.TestCase):
    """Test completion quality proxy."""

    @covers("REQ-0.0.13-05-02")
    def test_pass_with_completed_brief(self) -> None:
        audits: list[dict[str, object]] = [{"brief_status_after": "Completed"}]
        status, _detail = _completion_quality_proxy(Path("."), [], audits)
        self.assertEqual(status, "pass")

    @covers("REQ-0.0.13-05-02")
    def test_pass_with_attestation(self) -> None:
        audits: list[dict[str, object]] = [{"action_taken": "attestation_recorded"}]
        status, _detail = _completion_quality_proxy(Path("."), [], audits)
        self.assertEqual(status, "pass")


class TestPlanDisciplineProxy(unittest.TestCase):
    """Test plan discipline proxy."""

    @covers("REQ-0.0.13-05-02")
    def test_pass_when_adr_precedes_gate(self) -> None:
        events: list[dict[str, object]] = [
            {"event": "adr_created", "ts": "2026-01-01T00:00:00Z"},
            {"event": "gate_checked", "ts": "2026-01-02T00:00:00Z"},
        ]
        status, _detail = _plan_discipline_proxy(Path("."), events, [])
        self.assertEqual(status, "pass")

    @covers("REQ-0.0.13-05-02")
    def test_fail_when_no_adr_created(self) -> None:
        events: list[dict[str, object]] = [
            {"event": "gate_checked", "ts": "2026-01-02T00:00:00Z"},
        ]
        status, _detail = _plan_discipline_proxy(Path("."), events, [])
        self.assertEqual(status, "fail")


class TestAntiTraitInversion(unittest.TestCase):
    """Verify anti-traits are checked with inverse semantics."""

    @covers("REQ-0.0.13-05-01")
    def test_anti_trait_marked_in_result(self) -> None:
        events: list[dict[str, object]] = [
            {"event": "gate_checked", "ts": "2026-01-01T00:00:00Z"},
        ]
        result = _check_trait("governance-aware", Path("."), events, [], is_anti_trait=True)
        self.assertTrue(result.is_anti_trait)
        self.assertEqual(result.status, "pass")
        self.assertIn("inverse", result.detail)


class TestEvaluatePersonaDrift(unittest.TestCase):
    """Integration tests for the drift evaluation engine."""

    @covers("REQ-0.0.13-05-01")
    def test_all_personas_evaluated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            _write_persona(personas_dir, "alpha", ["methodical"], ["scope-creep"])
            _write_persona(personas_dir, "beta", ["thorough"], ["rubber-stamping"])
            _write_ledger(root, [{"event": "adr_created", "ts": "2026-01-01T00:00:00Z"}])
            report = evaluate_persona_drift(root)
            self.assertEqual(report.total_personas, 2)
            names = [p.persona for p in report.personas]
            self.assertIn("alpha", names)
            self.assertIn("beta", names)

    @covers("REQ-0.0.13-05-03")
    def test_single_persona_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            _write_persona(personas_dir, "alpha", ["methodical"], ["scope-creep"])
            _write_persona(personas_dir, "beta", ["thorough"], ["rubber-stamping"])
            _write_ledger(root, [])
            report = evaluate_persona_drift(root, persona_name="alpha")
            self.assertEqual(report.total_personas, 1)
            self.assertEqual(report.personas[0].persona, "alpha")

    @covers("REQ-0.0.13-05-04")
    def test_no_drift_when_all_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            _write_persona(personas_dir, "tester", ["governance-aware"], ["scope-creep"])
            _write_ledger(root, [{"event": "gate_checked", "ts": "2026-01-01T00:00:00Z"}])
            report = evaluate_persona_drift(root)
            self.assertEqual(report.drift_count, 0)

    @covers("REQ-0.0.13-05-05")
    def test_drift_when_proxy_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            _write_persona(personas_dir, "tester", ["governance-aware"], ["scope-creep"])
            _write_ledger(root, [])  # No governance events -> fail
            report = evaluate_persona_drift(root)
            self.assertGreater(report.drift_count, 0)

    @covers("REQ-0.0.13-05-01")
    def test_report_model_serializable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            _write_persona(personas_dir, "tester", ["methodical"], ["scope-creep"])
            _write_ledger(root, [])
            report = evaluate_persona_drift(root)
            data = json.loads(report.model_dump_json())
            self.assertIn("personas", data)
            self.assertIn("total_checks", data)
            self.assertIn("drift_count", data)
            self.assertIn("scan_timestamp", data)
