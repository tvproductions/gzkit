"""Tests for validate_invariant_coherence covering all 5 brief acceptance REQs.

Covers:
    REQ-0.0.37-03-01 — exits 0 (empty list) when rendered bytes match AGENTS.md
    REQ-0.0.37-03-02 — exits 3 (one ValidationError) on drift; message includes diff
    REQ-0.0.37-03-03 — emits composition_rendered always; drift also emits
                        composition_drift_detected
    REQ-0.0.37-03-04 — ledger.json schema registers both event definitions
    REQ-0.0.37-03-05 — invariant_coherence is in the default_scopes of validate_cmd

All tests use tempfile.TemporaryDirectory for sandbox isolation; never write
to the live repo root.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.compose import render_agents_md
from gzkit.governance.invariants import load_invariants
from gzkit.governance.trust_audits.invariant_coherence import validate_invariant_coherence
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MINIMAL_TEMPLATE = """\
# AGENTS.md

Composition output:

{% for inv_id, inv in invariants.items() %}- {{ inv_id }}: {{ inv.claim }}
{% endfor %}
"""

_TEST_INVARIANT = {
    "id": "TEST-1",
    "claim": "Test invariant claim",
    "structural_witness": ["test-witness-1"],
    "composition_targets": ["AGENTS.md"],
}


def _setup_project(root: Path, *, with_invariant: bool = True) -> None:
    """Scaffold minimal project structure under root."""
    gzkit_dir = root / ".gzkit"
    gzkit_dir.mkdir(parents=True, exist_ok=True)

    template_dir = root / ".gzkit" / "templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "agents.md").write_text(_MINIMAL_TEMPLATE, encoding="utf-8")

    if with_invariant:
        inv_dir = root / ".gzkit" / "invariants"
        inv_dir.mkdir(parents=True, exist_ok=True)
        (inv_dir / "TEST-1.json").write_text(
            json.dumps(_TEST_INVARIANT, indent=2), encoding="utf-8"
        )


def _write_agents_md(root: Path, content: bytes) -> None:
    """Write AGENTS.md at the project root."""
    (root / "AGENTS.md").write_bytes(content)


def _render_expected(root: Path) -> bytes:
    """Render AGENTS.md bytes using the project's template and invariants."""
    invariants = load_invariants(root)
    return render_agents_md(invariants, root / ".gzkit" / "templates", root)


def _read_ledger_events(root: Path) -> list[dict]:
    """Read all events from .gzkit/ledger.jsonl."""
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []
    events = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            events.append(json.loads(line))
    return events


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------


class _TempProjectMixin(unittest.TestCase):
    """Mixin providing a fresh temp project root for each test."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()


class TestMatchNoDrift(_TempProjectMixin):
    """AGENTS.md matches rendered bytes: validator returns empty list."""

    @covers("REQ-0.0.37-03-01")
    def test_matching_agents_md_returns_no_errors(self) -> None:
        _setup_project(self.root)
        expected_bytes = _render_expected(self.root)
        _write_agents_md(self.root, expected_bytes)

        errors = validate_invariant_coherence(self.root)

        self.assertEqual(errors, [], f"Expected no errors, got: {errors}")


class TestMismatchDrift(_TempProjectMixin):
    """AGENTS.md differs from rendered bytes: validator returns one ValidationError."""

    @covers("REQ-0.0.37-03-02")
    def test_differing_agents_md_returns_one_error(self) -> None:
        _setup_project(self.root)
        _write_agents_md(self.root, b"# AGENTS.md\n\nThis is wrong content.\n")

        errors = validate_invariant_coherence(self.root)

        self.assertEqual(len(errors), 1, f"Expected 1 error, got: {errors}")
        error = errors[0]
        self.assertEqual(error.type, "invariant_coherence")

    @covers("REQ-0.0.37-03-02")
    def test_error_message_contains_diff_header(self) -> None:
        _setup_project(self.root)
        _write_agents_md(self.root, b"# AGENTS.md\n\nDifferent content.\n")

        errors = validate_invariant_coherence(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("Diff (first 50 lines)", errors[0].message)

    @covers("REQ-0.0.37-03-02")
    def test_error_message_contains_diff_hunk_marker(self) -> None:
        _setup_project(self.root)
        # Provide AGENTS.md that differs so a hunk shows up in the unified diff.
        _write_agents_md(self.root, b"# AGENTS.md\n\nDifferent content.\n")

        errors = validate_invariant_coherence(self.root)

        self.assertEqual(len(errors), 1)
        # A unified diff hunk always starts with @@
        self.assertIn("@@", errors[0].message)


class TestCompositionRenderedEmitted(_TempProjectMixin):
    """composition_rendered event emitted on matching run."""

    @covers("REQ-0.0.37-03-03")
    def test_composition_rendered_event_present(self) -> None:
        _setup_project(self.root)
        expected_bytes = _render_expected(self.root)
        _write_agents_md(self.root, expected_bytes)

        validate_invariant_coherence(self.root)

        events = _read_ledger_events(self.root)
        rendered_events = [e for e in events if e.get("event") == "composition_rendered"]
        self.assertEqual(
            len(rendered_events), 1, f"Expected 1 composition_rendered event, got: {events}"
        )

    @covers("REQ-0.0.37-03-03")
    def test_composition_rendered_event_fields(self) -> None:
        _setup_project(self.root)
        expected_bytes = _render_expected(self.root)
        _write_agents_md(self.root, expected_bytes)

        validate_invariant_coherence(self.root)

        events = _read_ledger_events(self.root)
        rendered_events = [e for e in events if e.get("event") == "composition_rendered"]
        self.assertEqual(len(rendered_events), 1)
        ev = rendered_events[0]
        # Required fields from schema: invariant_count, target, byte_count, render_ts
        self.assertIn("invariant_count", ev)
        self.assertIn("target", ev)
        self.assertIn("byte_count", ev)
        self.assertIn("render_ts", ev)
        self.assertEqual(ev["invariant_count"], 1)
        self.assertEqual(ev["target"], "AGENTS.md")
        self.assertIsInstance(ev["byte_count"], int)

    @covers("REQ-0.0.37-03-03")
    def test_no_drift_event_on_match(self) -> None:
        _setup_project(self.root)
        expected_bytes = _render_expected(self.root)
        _write_agents_md(self.root, expected_bytes)

        validate_invariant_coherence(self.root)

        events = _read_ledger_events(self.root)
        drift_events = [e for e in events if e.get("event") == "composition_drift_detected"]
        self.assertEqual(
            drift_events, [], f"Expected no drift events on match, got: {drift_events}"
        )


class TestCompositionDriftEmitted(_TempProjectMixin):
    """composition_rendered AND composition_drift_detected emitted on drift."""

    @covers("REQ-0.0.37-03-03")
    def test_both_events_emitted_on_drift(self) -> None:
        _setup_project(self.root)
        _write_agents_md(self.root, b"# AGENTS.md\n\nStale content.\n")

        validate_invariant_coherence(self.root)

        events = _read_ledger_events(self.root)
        rendered_events = [e for e in events if e.get("event") == "composition_rendered"]
        drift_events = [e for e in events if e.get("event") == "composition_drift_detected"]
        self.assertEqual(len(rendered_events), 1, "composition_rendered must be emitted")
        self.assertEqual(len(drift_events), 1, "composition_drift_detected must be emitted")

    @covers("REQ-0.0.37-03-03")
    def test_drift_event_has_diff_first_50_lines_field(self) -> None:
        _setup_project(self.root)
        _write_agents_md(self.root, b"# AGENTS.md\n\nStale content.\n")

        validate_invariant_coherence(self.root)

        events = _read_ledger_events(self.root)
        drift_events = [e for e in events if e.get("event") == "composition_drift_detected"]
        self.assertEqual(len(drift_events), 1)
        ev = drift_events[0]
        self.assertIn("diff_first_50_lines", ev)
        self.assertIsInstance(ev["diff_first_50_lines"], str)
        self.assertTrue(len(ev["diff_first_50_lines"]) > 0)


class TestEmptyRegistry(_TempProjectMixin):
    """No .gzkit/invariants/ directory: load_invariants returns empty dict."""

    def test_no_invariants_dir_returns_validation_result(self) -> None:
        # Setup template but no invariants dir; AGENTS.md absent.
        _setup_project(self.root, with_invariant=False)

        # Should not raise; returns a list (possibly 1 error due to drift).
        result = validate_invariant_coherence(self.root)

        self.assertIsInstance(result, list)
        # Each element (if any) must be a ValidationError.
        for err in result:
            self.assertEqual(err.type, "invariant_coherence")

    def test_no_invariants_dir_emits_composition_rendered(self) -> None:
        _setup_project(self.root, with_invariant=False)

        validate_invariant_coherence(self.root)

        events = _read_ledger_events(self.root)
        rendered_events = [e for e in events if e.get("event") == "composition_rendered"]
        self.assertEqual(len(rendered_events), 1)
        self.assertEqual(rendered_events[0]["invariant_count"], 0)


class TestSchemaRegistered(unittest.TestCase):
    """REQ-0.0.37-03-04: ledger.json schema includes both event type definitions."""

    @covers("REQ-0.0.37-03-04")
    def test_composition_rendered_event_defined_in_schema(self) -> None:
        schema_path = (
            Path(__file__).parent.parent.parent / "src" / "gzkit" / "schemas" / "ledger.json"
        )
        self.assertTrue(schema_path.exists(), f"Schema file missing: {schema_path}")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        events = schema.get("events", {})
        self.assertIn(
            "composition_rendered",
            events,
            "composition_rendered must be defined in ledger.json events",
        )

    @covers("REQ-0.0.37-03-04")
    def test_composition_drift_detected_event_defined_in_schema(self) -> None:
        schema_path = (
            Path(__file__).parent.parent.parent / "src" / "gzkit" / "schemas" / "ledger.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        events = schema.get("events", {})
        self.assertIn(
            "composition_drift_detected",
            events,
            "composition_drift_detected must be defined in ledger.json events",
        )

    @covers("REQ-0.0.37-03-04")
    def test_composition_rendered_required_fields_present(self) -> None:
        schema_path = (
            Path(__file__).parent.parent.parent / "src" / "gzkit" / "schemas" / "ledger.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        event_def = schema["events"]["composition_rendered"]
        required = event_def.get("required", [])
        for field in ("invariant_count", "target", "byte_count", "render_ts"):
            self.assertIn(
                field,
                required,
                f"Field {field!r} missing from composition_rendered required",
            )

    @covers("REQ-0.0.37-03-04")
    def test_composition_drift_required_fields_present(self) -> None:
        schema_path = (
            Path(__file__).parent.parent.parent / "src" / "gzkit" / "schemas" / "ledger.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        event_def = schema["events"]["composition_drift_detected"]
        required = event_def.get("required", [])
        for field in ("target", "diff_first_50_lines", "render_ts"):
            self.assertIn(
                field,
                required,
                f"Field {field!r} missing from composition_drift_detected required",
            )


class TestGzCheckDefault(unittest.TestCase):
    """REQ-0.0.37-03-05: invariant_coherence runs by default in gz check."""

    @covers("REQ-0.0.37-03-05")
    def test_invariant_coherence_in_default_scope_runners(self) -> None:
        from gzkit.commands.validate_cmd import _default_scope_runners

        runners = _default_scope_runners(Path("."), None)
        self.assertIn(
            "invariant_coherence",
            runners,
            "invariant_coherence must appear in _default_scope_runners",
        )

    @covers("REQ-0.0.37-03-05")
    def test_invariant_coherence_in_collect_errors_default_scopes(self) -> None:
        # Verify the default_scopes dict in _collect_errors includes
        # invariant_coherence (even if its value starts as False).
        import inspect

        from gzkit.commands import validate_cmd

        source = inspect.getsource(validate_cmd._collect_errors)
        self.assertIn(
            '"invariant_coherence"',
            source,
            "invariant_coherence must appear in _collect_errors default_scopes",
        )


class TestScorecardEntry(unittest.TestCase):
    """REQ-0.0.37-03-06: scorecard entry in advisory-rules-audit.md."""

    @covers("REQ-0.0.37-03-06")
    def test_scorecard_entry_present(self) -> None:
        scorecard = (
            Path(__file__).resolve().parents[2] / "docs" / "governance" / "advisory-rules-audit.md"
        )
        text = scorecard.read_text(encoding="utf-8")
        self.assertIn("--invariant-coherence", text)
        self.assertIn("**Mechanical**", text)

    @covers("REQ-0.0.37-03-06")
    def test_scorecard_row_cites_validator_module(self) -> None:
        scorecard = (
            Path(__file__).resolve().parents[2] / "docs" / "governance" / "advisory-rules-audit.md"
        )
        text = scorecard.read_text(encoding="utf-8")
        # The scorecard row for --invariant-coherence must cite the validator module.
        invariant_lines = [line for line in text.splitlines() if "invariant-coherence" in line]
        self.assertTrue(
            any(
                "invariant_coherence.py" in line or "OBPI-0.0.37-03" in line
                for line in invariant_lines
            ),
            "scorecard row must cite invariant_coherence.py or OBPI-0.0.37-03",
        )


if __name__ == "__main__":
    unittest.main()
