"""Tests for SUPPORT channel ledger query + validator dispatch (OBPI-0.0.69-01).

Derives assertions from brief acceptance-criteria REQs, not from implementation.

REQ-0.0.69-01-01 [behavior]: cited event found + validator exits 0 → proof_status "pass"
REQ-0.0.69-01-02 [behavior]: cited event absent OR citation unparseable → unproven/fail-close
REQ-0.0.69-01-03 [behavior]: cited validator scope non-zero → unproven/fail-close
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.traceability import covers


def _make_ledger(project_root: Path, event_type: str) -> None:
    """Write a minimal ledger.jsonl with one event of the given type."""
    gzkit_dir = project_root / ".gzkit"
    gzkit_dir.mkdir(exist_ok=True)
    event = {
        "schema": "1.0",
        "event": event_type,
        "id": "fixture-id",
        "ts": "2026-01-01T00:00:00+00:00",
    }
    (gzkit_dir / "ledger.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")


class TestResolveSupportProofPass(unittest.TestCase):
    """REQ-0.0.69-01-01: cited event present + validator exits 0 → proof_status "pass"."""

    @covers("REQ-0.0.69-01-01")
    def test_pass_when_event_found_and_scope_exits_zero(self) -> None:
        """Cited event in ledger AND scope exits 0 → "pass"; never "advisory-support"."""
        from gzkit.req_kind import resolve_support_proof

        req_text = (
            "manpage updated — artifact_edited ledger event "
            "+ gz validate --documents (doc-tree structural validator)"
        )

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _make_ledger(project_root, "artifact_edited")
            with patch(
                "gzkit.req_kind._dispatch_validator_scope", return_value=True
            ) as mock_dispatch:
                result = resolve_support_proof(req_text, project_root)
                mock_dispatch.assert_called_once_with("documents", project_root)

        self.assertEqual(result, "pass")
        self.assertNotEqual(result, "advisory-support")

    @covers("REQ-0.0.69-01-01")
    def test_compute_coverage_with_project_root_uses_real_resolver(self) -> None:
        """compute_three_channel_coverage with project_root resolves real proof_status."""
        from gzkit.req_kind import compute_three_channel_coverage
        from gzkit.traceability import CoverageEntry, CoverageReport, CoverageRollup
        from gzkit.triangle import DiscoveredReq, ReqEntity, ReqId, ReqStatus
        from gzkit.triangle import ReqKind as TriReqKind

        rid = ReqId.parse("REQ-0.0.59-99-01")
        entity = ReqEntity(
            id=rid,
            description=("rule updated — artifact_edited ledger event + gz validate --documents"),
            status=ReqStatus.UNCHECKED,
            parent_obpi="OBPI-0.0.59-99",
            kind=TriReqKind.CODE,
            taxonomy_kind="SUPPORT",
        )
        dreq = DiscoveredReq(entity=entity, source_path="test.md")
        entry = CoverageEntry(req_id="REQ-0.0.59-99-01", covered=False, covering_tests=[])
        rollup = CoverageRollup(
            identifier="all",
            total_reqs=1,
            covered_reqs=0,
            uncovered_reqs=1,
            coverage_percent=0.0,
        )
        report = CoverageReport(by_adr=[], by_obpi=[], entries=[entry], summary=rollup)

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _make_ledger(project_root, "artifact_edited")
            with patch(
                "gzkit.req_kind._dispatch_validator_scope", return_value=True
            ) as mock_dispatch:
                enriched = compute_three_channel_coverage(report, [dreq], project_root=project_root)
                mock_dispatch.assert_called_once_with("documents", project_root)

        # Resolver with patched dispatch should return "pass", not the legacy "advisory-support"
        self.assertNotEqual(enriched.entries[0].proof_status, "advisory-support")
        self.assertEqual(enriched.entries[0].proof_status, "pass")


class TestResolveSupportProofFailClose(unittest.TestCase):
    """REQ-0.0.69-01-02 and REQ-0.0.69-01-03: fail-close on missing event or failing scope."""

    @covers("REQ-0.0.69-01-02")
    def test_unproven_when_cited_event_absent(self) -> None:
        """Cited event NOT in ledger → unproven; never "advisory-support"."""
        from gzkit.req_kind import resolve_support_proof

        req_text = "manpage updated — artifact_edited ledger event + gz validate --documents"

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            # Ledger contains a DIFFERENT event type — not artifact_edited
            _make_ledger(project_root, "obpi_created")
            result = resolve_support_proof(req_text, project_root)

        self.assertNotEqual(result, "pass", "Absent event must not resolve to pass")
        self.assertNotEqual(result, "advisory-support", "Must not fall back to advisory-support")

    @covers("REQ-0.0.69-01-02")
    def test_unproven_when_ledger_missing(self) -> None:
        """No ledger at all → unproven; never "advisory-support"."""
        from gzkit.req_kind import resolve_support_proof

        req_text = "manpage updated — artifact_edited ledger event + gz validate --documents"

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            # No .gzkit/ledger.jsonl at all
            result = resolve_support_proof(req_text, project_root)

        self.assertNotEqual(result, "pass")
        self.assertNotEqual(result, "advisory-support")

    @covers("REQ-0.0.69-01-02")
    def test_validation_error_for_missing_citation_on_support_req(self) -> None:
        """Missing citation on SUPPORT REQ → ValidationError from _check_support_req."""
        from gzkit.commands.validate_req_kind import _check_support_req

        req_id = "REQ-0.0.69-test-01"
        # REQ line with no gz validate scope or event type cited
        ac_section = f"- [ ] {req_id} [SUPPORT]: rule file exists and is correct\n"

        errors = _check_support_req(req_id, ac_section, "tests/test_brief.md")

        self.assertGreater(len(errors), 0, "Missing citation must produce at least one error")

    @covers("REQ-0.0.69-01-02")
    def test_legacy_keyword_citation_stays_green_at_authoring_time(self) -> None:
        """Pre-parser keyword citations (generic 'ledger event' + scope) stay green.

        Authoring-time strictness must not exceed the pre-ADR-0.0.69 contract:
        briefs whose SUPPORT citations name no recognized event type passed the
        keyword check and must keep passing _check_support_req. Their proof
        resolves unproven at closeout until the citation names a concrete type.
        """
        from gzkit.commands.validate_req_kind import _check_support_req

        req_id = "REQ-0.0.69-test-03"
        # Generic 'ledger event' keyword + scope, but no recognized event type
        ac_section = (
            f"- [ ] {req_id} [SUPPORT]: doctrine doc updated. "
            "Proof: ledger event + gz validate --doctrine-shape green\n"
        )

        errors = _check_support_req(req_id, ac_section, "tests/test_brief.md")

        self.assertEqual(errors, [], "Legacy keyword citation must not regress to an error")

    @covers("REQ-0.0.69-01-02")
    def test_validation_error_for_citation_missing_scope(self) -> None:
        """SUPPORT REQ with event type but no gz validate scope → ValidationError."""
        from gzkit.commands.validate_req_kind import _check_support_req

        req_id = "REQ-0.0.69-test-02"
        # Has ledger event type but no gz validate --<scope>
        ac_section = f"- [ ] {req_id} [SUPPORT]: artifact_edited event confirms this\n"

        errors = _check_support_req(req_id, ac_section, "tests/test_brief.md")

        self.assertGreater(len(errors), 0, "Citation without scope must produce an error")

    @covers("REQ-0.0.69-01-02")
    def test_unproven_when_citation_unparseable(self) -> None:
        """Unparseable citation in resolve_support_proof → unproven; never pass."""
        from gzkit.req_kind import resolve_support_proof

        # No gz validate scope and no recognized event type
        req_text = "rule file exists and is correct"

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _make_ledger(project_root, "artifact_edited")
            result = resolve_support_proof(req_text, project_root)

        self.assertNotEqual(result, "pass")
        self.assertNotEqual(result, "advisory-support")

    @covers("REQ-0.0.69-01-03")
    def test_unproven_when_validator_exits_nonzero(self) -> None:
        """Cited validator dispatch non-zero → unproven; never "advisory-support"."""
        from gzkit.req_kind import resolve_support_proof

        req_text = "manpage updated — artifact_edited ledger event + gz validate --documents"

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _make_ledger(project_root, "artifact_edited")

            # Patch the in-process dispatch to simulate a failing scope
            with patch("gzkit.req_kind._dispatch_validator_scope", return_value=False):
                result = resolve_support_proof(req_text, project_root)

        self.assertNotEqual(result, "pass", "Non-zero exit must not resolve to pass")
        self.assertNotEqual(result, "advisory-support", "Must not fall back to advisory-support")


class TestSupportChannelLegacyRegression(unittest.TestCase):
    """Regression pin: legacy path (no project_root) still yields advisory-support."""

    @covers("REQ-0.0.69-01-01")
    def test_legacy_path_yields_advisory_support(self) -> None:
        """compute_three_channel_coverage without project_root → advisory-support for SUPPORT."""
        from gzkit.req_kind import compute_three_channel_coverage
        from gzkit.traceability import CoverageEntry, CoverageReport, CoverageRollup
        from gzkit.triangle import DiscoveredReq, ReqEntity, ReqId, ReqStatus
        from gzkit.triangle import ReqKind as TriReqKind

        rid = ReqId.parse("REQ-0.0.59-99-01")
        entity = ReqEntity(
            id=rid,
            description="rule updated — artifact_edited gz validate --documents",
            status=ReqStatus.UNCHECKED,
            parent_obpi="OBPI-0.0.59-99",
            kind=TriReqKind.CODE,
            taxonomy_kind="SUPPORT",
        )
        dreq = DiscoveredReq(entity=entity, source_path="test.md")
        entry = CoverageEntry(req_id="REQ-0.0.59-99-01", covered=False, covering_tests=[])
        rollup = CoverageRollup(
            identifier="all",
            total_reqs=1,
            covered_reqs=0,
            uncovered_reqs=1,
            coverage_percent=0.0,
        )
        report = CoverageReport(by_adr=[], by_obpi=[], entries=[entry], summary=rollup)

        # No project_root → legacy "advisory-support" path unchanged
        enriched = compute_three_channel_coverage(report, [dreq])
        self.assertEqual(
            enriched.entries[0].proof_status,
            "advisory-support",
            "Legacy path (no project_root) must still yield advisory-support",
        )


class TestRecursionFence(unittest.TestCase):
    """Recursion fence: scopes that re-enter req-kind/closeout-proof resolution resolve unproven."""

    @covers("REQ-0.0.69-01-01")
    def test_recursion_fence_for_req_kind_discipline_scope(self) -> None:
        """Citing gz validate --req-kind-discipline resolves unproven (not dispatched)."""
        from gzkit.req_kind import resolve_support_proof

        req_text = (
            "discipline enforced — artifact_edited ledger event + gz validate --req-kind-discipline"
        )

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _make_ledger(project_root, "artifact_edited")
            result = resolve_support_proof(req_text, project_root)

        self.assertNotEqual(result, "pass", "Recursion-fenced scope must not resolve to pass")
        self.assertNotEqual(result, "advisory-support", "Must not fall back to advisory-support")

    @covers("REQ-0.0.69-01-01")
    def test_recursion_fence_for_closeout_proof_scope(self) -> None:
        """Citing gz validate --closeout-proof resolves unproven (not dispatched)."""
        from gzkit.req_kind import resolve_support_proof

        req_text = "proof computed — artifact_edited ledger event + gz validate --closeout-proof"

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _make_ledger(project_root, "artifact_edited")
            result = resolve_support_proof(req_text, project_root)

        self.assertNotEqual(result, "pass")
        self.assertNotEqual(result, "advisory-support")


class TestKnownLedgerEventTypesCoherence(unittest.TestCase):
    """MF-1: _KNOWN_LEDGER_EVENT_TYPES must be derived from TypedLedgerEvent, not hand-maintained.

    Coherence pin: introspection works, the set is non-empty, ghosts are absent,
    and extras stay outside the union.
    """

    def _derive_union_types(self) -> frozenset[str]:
        """Introspect TypedLedgerEvent to produce the canonical set of typed event strings."""
        import typing

        from gzkit.events import TypedLedgerEvent

        result: set[str] = set()
        annotated_args = typing.get_args(TypedLedgerEvent)
        if not annotated_args:
            return frozenset()
        union_type = annotated_args[0]
        for model_cls in typing.get_args(union_type):
            event_field = getattr(model_cls, "model_fields", {}).get("event")
            if event_field is None:
                continue
            literal_values = typing.get_args(event_field.annotation)
            if literal_values:
                result.add(str(literal_values[0]))
        return frozenset(result)

    def test_derived_set_is_nonempty_and_contains_known_type(self) -> None:
        """Introspection works: the set is non-empty and contains artifact_edited."""
        from gzkit.req_kind import _KNOWN_LEDGER_EVENT_TYPES

        self.assertGreater(len(_KNOWN_LEDGER_EVENT_TYPES), 0, "Set must be non-empty")
        self.assertIn("artifact_edited", _KNOWN_LEDGER_EVENT_TYPES)

    def test_ghost_types_absent(self) -> None:
        """Ghost event types (not in TypedLedgerEvent union and not observed) must be absent."""
        from gzkit.req_kind import _KNOWN_LEDGER_EVENT_TYPES

        # obpi_completed was hand-maintained and is not in the TypedLedgerEvent union
        self.assertNotIn(
            "obpi_completed",
            _KNOWN_LEDGER_EVENT_TYPES,
            "obpi_completed is a ghost: not in TypedLedgerEvent union, must be removed",
        )

    def test_all_typed_events_present(self) -> None:
        """Every event type from TypedLedgerEvent union must be in _KNOWN_LEDGER_EVENT_TYPES."""
        from gzkit.req_kind import _KNOWN_LEDGER_EVENT_TYPES

        derived = self._derive_union_types()
        self.assertGreater(len(derived), 0, "Introspection must find at least one typed event")
        for event_type in derived:
            self.assertIn(
                event_type,
                _KNOWN_LEDGER_EVENT_TYPES,
                f"Typed event '{event_type}' from union is absent from _KNOWN_LEDGER_EVENT_TYPES",
            )

    def test_extras_not_in_union(self) -> None:
        """Every extra in _UNTYPED_LEDGER_EVENT_EXTRAS must NOT be in the TypedLedgerEvent union."""
        from gzkit.req_kind import _UNTYPED_LEDGER_EVENT_EXTRAS

        derived = self._derive_union_types()
        for extra in _UNTYPED_LEDGER_EVENT_EXTRAS:
            self.assertNotIn(
                extra,
                derived,
                f"Extra '{extra}' is now typed in the union; remove it from "
                "_UNTYPED_LEDGER_EVENT_EXTRAS",
            )


if __name__ == "__main__":
    unittest.main()
