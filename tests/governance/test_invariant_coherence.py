"""Tests for validate_invariant_coherence — rendition-playback semantics (OBPI-0.0.37-22).

After re-pointing (OBPI-0.0.37-22), --invariant-coherence diffs deterministic
playback of the committed rendition against the committed rendered surface.

Covers:
    REQ-0.0.37-22-04 — exits 3 when rendition playback differs from committed AGENTS.md
    REQ-0.0.37-03-01 — exits 0 (empty list) when rendition bytes match AGENTS.md
    REQ-0.0.37-03-02 — exits 3 (one ValidationError) on drift; message includes diff
    REQ-0.0.37-03-03 — read-only on a clean run (no ledger event on match); drift
                        emits composition_drift_detected. (The former per-run
                        composition_rendered emission was removed — no consumer; it
                        broke the pre-push gate. ADR-0.0.37 Draft, OBPI-03 repudiated.)
    REQ-0.0.37-03-04 — ledger.json schema registers both event definitions
    REQ-0.0.37-03-05 — invariant_coherence runs in gz check (validate registry + pipeline)

Bootstrap-safe: when no committed rendition exists, returns [] with no events.
All tests use tempfile.TemporaryDirectory for sandbox isolation.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.content.rendition_store import save_rendition
from gzkit.governance.trust_audits.invariant_coherence import validate_invariant_coherence
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MINIMAL_RENDITION = (
    b"# AGENTS.md\n\nA minimal test agent contract.\n\n## Behavior Rules\n\n"
    b"- Always read AGENTS.md before starting work.\n"
)


def _setup_project(root: Path, *, with_rendition: bool = True) -> None:
    """Scaffold minimal project structure under root."""
    gzkit_dir = root / ".gzkit"
    gzkit_dir.mkdir(parents=True, exist_ok=True)

    if with_rendition:
        save_rendition(root, "AGENTS.md", "root", _MINIMAL_RENDITION)


def _write_agents_md(root: Path, content: bytes) -> None:
    """Write AGENTS.md at the project root."""
    (root / "AGENTS.md").write_bytes(content)


def _rendition_bytes(root: Path) -> bytes:
    """Return the committed rendition bytes (what playback produces)."""
    from gzkit.content.rendition_store import load_rendition, rendition_exists

    if rendition_exists(root, "AGENTS.md", "root"):
        return load_rendition(root, "AGENTS.md", "root")
    return b""


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
    """AGENTS.md matches committed rendition bytes: validator returns empty list."""

    @covers("REQ-0.0.37-03-01")
    def test_matching_agents_md_returns_no_errors(self) -> None:
        _setup_project(self.root)
        _write_agents_md(self.root, _rendition_bytes(self.root))

        errors = validate_invariant_coherence(self.root)

        self.assertEqual(errors, [], f"Expected no errors, got: {errors}")

    @covers("REQ-0.0.37-03-01")
    def test_bootstrap_no_rendition_returns_no_errors(self) -> None:
        """Bootstrap: no committed rendition → validator returns [] without checking."""
        _setup_project(self.root, with_rendition=False)
        _write_agents_md(self.root, b"# AGENTS.md\n\nSome content.\n")

        errors = validate_invariant_coherence(self.root)

        self.assertEqual(errors, [], "Bootstrap: no rendition → no coherence check")


class TestMismatchDrift(_TempProjectMixin):
    """AGENTS.md differs from rendition: validator returns one ValidationError."""

    @covers("REQ-0.0.37-03-02")
    @covers("REQ-0.0.37-22-04")
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
        _write_agents_md(self.root, b"# AGENTS.md\n\nDifferent content.\n")

        errors = validate_invariant_coherence(self.root)

        self.assertEqual(len(errors), 1)
        # A unified diff hunk always starts with @@
        self.assertIn("@@", errors[0].message)


class TestCleanRunIsReadOnly(_TempProjectMixin):
    """The validator is read-only on a clean run — no ledger event on match.

    Re-derived from the former TestCompositionRenderedEmitted (ADR-0.0.37 Draft,
    OBPI-0.0.37-03 repudiated): the per-run ``composition_rendered`` emission was
    removed (no consumer; it broke the pre-push gate by dirtying the tree). A
    matching surface now emits NOTHING — the clean-run purity that makes the
    validator gate-safe, matching its rendition siblings.
    """

    @covers("REQ-0.0.37-03-03")
    def test_no_events_on_match(self) -> None:
        _setup_project(self.root)
        _write_agents_md(self.root, _rendition_bytes(self.root))

        validate_invariant_coherence(self.root)

        events = _read_ledger_events(self.root)
        self.assertEqual(events, [], f"Clean run must emit no ledger events, got: {events}")

    @covers("REQ-0.0.37-03-03")
    def test_no_composition_rendered_emitted_on_match(self) -> None:
        """Regression lock: the removed per-run telemetry must not return."""
        _setup_project(self.root)
        _write_agents_md(self.root, _rendition_bytes(self.root))

        validate_invariant_coherence(self.root)

        events = _read_ledger_events(self.root)
        rendered = [e for e in events if e.get("event") == "composition_rendered"]
        self.assertEqual(rendered, [], "composition_rendered must not be emitted (removed)")

    @covers("REQ-0.0.37-03-03")
    def test_bootstrap_no_rendition_emits_no_events(self) -> None:
        """Bootstrap: no committed rendition → validator returns early, emits nothing."""
        _setup_project(self.root, with_rendition=False)
        _write_agents_md(self.root, b"# AGENTS.md\n\nBootstrap content.\n")

        validate_invariant_coherence(self.root)

        events = _read_ledger_events(self.root)
        self.assertEqual(events, [], "Bootstrap: no rendition → no ledger events")


class TestCompositionDriftEmitted(_TempProjectMixin):
    """On drift: composition_drift_detected emitted, composition_rendered NOT."""

    @covers("REQ-0.0.37-03-03")
    def test_only_drift_event_emitted_on_drift(self) -> None:
        _setup_project(self.root)
        _write_agents_md(self.root, b"# AGENTS.md\n\nStale content.\n")

        validate_invariant_coherence(self.root)

        events = _read_ledger_events(self.root)
        rendered_events = [e for e in events if e.get("event") == "composition_rendered"]
        drift_events = [e for e in events if e.get("event") == "composition_drift_detected"]
        self.assertEqual(rendered_events, [], "composition_rendered must NOT be emitted (removed)")
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
    """Bootstrap (no committed rendition): validator is a no-op."""

    def test_no_rendition_returns_empty_list(self) -> None:
        """Without a committed rendition, validator skips coherence check (bootstrap-safe)."""
        _setup_project(self.root, with_rendition=False)

        result = validate_invariant_coherence(self.root)

        self.assertEqual(result, [], "Bootstrap: no rendition → empty list")

    def test_no_rendition_emits_no_ledger_events(self) -> None:
        """Bootstrap: no committed rendition → no ledger events emitted."""
        _setup_project(self.root, with_rendition=False)

        validate_invariant_coherence(self.root)

        events = _read_ledger_events(self.root)
        self.assertEqual(events, [], "Bootstrap: no rendition → no ledger events")


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
    def test_invariant_coherence_is_default_tier_in_registry(self) -> None:
        # `_collect_errors` derives its default_scopes from VALIDATOR_REGISTRY
        # (Sanity-Reduction #618). invariant_coherence must be a default-tier
        # entry to run on the no-flag `gz check` path — the semantic successor to
        # the former source-string assertion (asserts behavior, not source text).
        from gzkit.commands import validate_cmd

        default_stems = {e.stem for e in validate_cmd.VALIDATOR_REGISTRY if e.tier == "default"}
        self.assertIn(
            "invariant_coherence",
            default_stems,
            "invariant_coherence must be a default-tier scope (runs in gz check)",
        )

    @covers("REQ-0.0.37-03-05")
    def test_invariant_coherence_in_gz_check_pipeline(self) -> None:
        # The two assertions above cover the `gz validate` registry. `gz check`
        # does NOT run that registry's default tier — it runs the SEPARATE curated
        # pipeline in `_build_check_steps()`. invariant_coherence was absent there,
        # so committed AGENTS.md<->rendition drift sailed through the pre-push
        # `gz check` gate silently (governance-core declares the gate "in the gz
        # check default scope" — implementation had drifted from doctrine). This
        # closes the gap against the surface the pre-merge gate actually runs.
        from gzkit.commands.quality import _build_check_steps

        step_names = [name for name, _ in _build_check_steps()]
        self.assertIn(
            "Invariant coherence",
            step_names,
            "invariant_coherence must be a step in the gz check pipeline (_build_check_steps)",
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
