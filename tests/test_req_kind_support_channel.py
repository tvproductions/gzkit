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
        from gzkit.req_kind_support import resolve_support_proof

        req_text = (
            "manpage updated. Witnessed by `artifact_edited` "
            "+ `gz validate --documents` (doc-tree structural validator)"
        )

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _make_ledger(project_root, "artifact_edited")
            with patch(
                "gzkit.req_kind_support._dispatch_validator_scope", return_value=True
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
        from gzkit.triangle import DiscoveredReq, ReqEntity, ReqId, ReqStatus, ReqTestability

        rid = ReqId.parse("REQ-0.0.59-99-01")
        entity = ReqEntity(
            id=rid,
            description=(
                "rule updated. Witnessed by `artifact_edited` + `gz validate --documents`"
            ),
            status=ReqStatus.UNCHECKED,
            parent_obpi="OBPI-0.0.59-99",
            kind=ReqTestability.CODE,
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
                "gzkit.req_kind_support._dispatch_validator_scope", return_value=True
            ) as mock_dispatch:
                enriched = compute_three_channel_coverage(report, [dreq], project_root=project_root)
                mock_dispatch.assert_called_once_with("documents", project_root)

        # Resolver with patched dispatch should return "pass", not the legacy "advisory-support"
        self.assertNotEqual(enriched.entries[0].proof_status, "advisory-support")
        self.assertEqual(enriched.entries[0].proof_status, "pass")


def _make_ledger_with_events(project_root: Path, events: list[dict]) -> None:
    """Write a ledger.jsonl with the given raw event dicts."""
    gzkit_dir = project_root / ".gzkit"
    gzkit_dir.mkdir(exist_ok=True)
    with (gzkit_dir / "ledger.jsonl").open("w", encoding="utf-8") as fh:
        for ev in events:
            fh.write(json.dumps(ev) + "\n")


def _ev(event: str, path: str | None) -> dict:
    """A minimal raw ledger event, optionally citing a path."""
    rec = {"schema": "1.0", "event": event, "id": path or "x", "ts": "t"}
    if path is not None:
        rec["path"] = path
    return rec


_PATCH_SCOPE = "gzkit.req_kind_support._dispatch_validator_scope"


class TestSupportProofPathAware(unittest.TestCase):
    """GHI #647: the ledger arm must verify an event CITING THE CITED PATH, not
    merely that an event of the type exists somewhere (the hollow-gate facade)."""

    # A REQ citing artifact_edited FOR a specific source path + a validator scope.
    _REQ = (
        "events.py registered. Witnessed by `artifact_edited` citing "
        "`src/gzkit/events.py` + `gz validate --ledger`"
    )

    def test_path_cited_but_no_event_cites_path_is_unproven(self) -> None:
        """Facade regression: artifact_edited exists for a DIFFERENT path → must NOT pass."""
        from gzkit.req_kind_support import resolve_support_proof

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_ledger_with_events(root, [_ev("artifact_edited", "docs/x.md")])
            with patch(_PATCH_SCOPE, return_value=True):
                result = resolve_support_proof(self._REQ, root, req_id="REQ-0.0.74-06-04")
            self.assertEqual(result, "unproven-support")

    def test_path_cited_and_event_cites_path_passes(self) -> None:
        from gzkit.req_kind_support import resolve_support_proof

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_ledger_with_events(root, [_ev("artifact_edited", "src/gzkit/events.py")])
            with patch(_PATCH_SCOPE, return_value=True):
                result = resolve_support_proof(self._REQ, root, req_id="REQ-0.0.74-06-04")
            self.assertEqual(result, "pass")

    def test_grandfathered_req_with_no_event_is_tolerated(self) -> None:
        """A pre-cutover hollow proof named in the grandfather file resolves to a
        distinct 'grandfathered-support' (tolerated, not laundered as 'pass')."""
        from gzkit.req_kind_support import resolve_support_proof

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_ledger_with_events(root, [_ev("artifact_edited", "docs/x.md")])
            (root / "data").mkdir()
            (root / "data" / "support_proof_grandfather.json").write_text(
                json.dumps({"grandfathered_reqs": ["REQ-0.0.74-06-04"]}), encoding="utf-8"
            )
            with patch(_PATCH_SCOPE, return_value=True):
                result = resolve_support_proof(self._REQ, root, req_id="REQ-0.0.74-06-04")
            self.assertEqual(result, "grandfathered-support")

    def test_live_nc_never_emitted_event_with_path_fails(self) -> None:
        """Live negative control (closes the #642/#647 'no NC' class): a SUPPORT
        proof citing an event TYPE that was never emitted at all MUST fail. A
        stub gate that auto-passes would pass this; the real gate refuses."""
        from gzkit.req_kind_support import resolve_support_proof

        req = (
            "rule shipped. Witnessed by `corpus_entry_appended` citing "
            "`.gzkit/rules/x.md` + `gz validate --ledger`"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Ledger has events, but NONE of type corpus_entry_appended.
            _make_ledger_with_events(root, [_ev("artifact_edited", "a/b.md")])
            with patch(_PATCH_SCOPE, return_value=True):
                result = resolve_support_proof(req, root, req_id="REQ-9.9.9-99-99")
            self.assertEqual(result, "unproven-support")

    def test_artifact_edited_cited_file_exists_passes_without_ledger_event(self) -> None:
        """GHI #647 drain: artifact_edited is content-authorship — the genuine proof
        is the cited artifact EXISTING on disk (+ structural validator), not a
        historical edit-event that is never emitted for most artifacts. A cited
        file that exists, with NO ledger event citing it, proves."""
        from gzkit.req_kind_support import resolve_support_proof

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_ledger_with_events(root, [_ev("obpi_created", None)])  # no artifact_edited
            (root / "src" / "gzkit").mkdir(parents=True)
            (root / "src" / "gzkit" / "events.py").write_text("x", encoding="utf-8")
            with patch(_PATCH_SCOPE, return_value=True):
                result = resolve_support_proof(self._REQ, root, req_id="REQ-X")
            self.assertEqual(result, "pass")

    def test_operation_event_requires_its_event_not_a_bare_file(self) -> None:
        """An operation-event citation (composition_candidate_emitted) is NOT
        satisfied by an unrelated artifact_edited event or a bare file — the
        operation's OWN event type must be present (it is specific, not the
        generic artifact_edited facade)."""
        from gzkit.req_kind_support import resolve_support_proof

        req = (
            "composer staged. Witnessed by `composition_candidate_emitted` citing "
            "`src/gzkit/schemas/ledger.json` + `gz validate --ledger`"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_ledger_with_events(root, [_ev("artifact_edited", "x.md")])  # not the op event
            (root / "src" / "gzkit" / "schemas").mkdir(parents=True)
            (root / "src" / "gzkit" / "schemas" / "ledger.json").write_text("{}", encoding="utf-8")
            with patch(_PATCH_SCOPE, return_value=True):
                result = resolve_support_proof(req, root, req_id="REQ-X")
            self.assertEqual(result, "unproven-support")

    def test_operation_event_present_proves(self) -> None:
        """A specific operation event existing in the ledger proves its citation —
        the event IS the record that the operation ran. Unlike generic
        artifact_edited (4295 events), operation events are specific, so
        type-presence is genuine proof, not the closed facade."""
        from gzkit.req_kind_support import resolve_support_proof

        req = (
            "composer staged. Witnessed by `composition_candidate_emitted` citing "
            "`src/gzkit/schemas/ledger.json` + `gz validate --ledger`"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_ledger_with_events(root, [_ev("composition_candidate_emitted", "whatever")])
            with patch(_PATCH_SCOPE, return_value=True):
                result = resolve_support_proof(req, root, req_id="REQ-X")
            self.assertEqual(result, "pass")

    def test_a_fence_scope_named_in_the_body_does_not_bind_the_proof(self) -> None:
        """GHI #647's case, now decided by declaration rather than by preference.

        A REQ may DOCUMENT `gz validate --req-kind-discipline` while being PROVEN
        by `--documents`. The old parser scanned the whole body, found both, and
        picked the non-fence one by a `_RECURSION_FENCE_SCOPES` preference — a
        workaround GHI #888 names as treating one symptom of the substring class.
        Reading only the clause decides it outright: the body's fence scope is
        commentary, and the declared scope is the proof. Same outcome, no heuristic.
        """
        from gzkit.req_kind_support import parse_support_citation

        req = (
            "`docs/governance/x.md` documents `gz validate --req-kind-discipline`. "
            "Witnessed by `artifact_edited` citing `docs/governance/x.md` + "
            "`gz validate --documents`."
        )
        cit = parse_support_citation(req)
        assert cit is not None
        self.assertEqual(cit.scope, "documents")
        self.assertEqual(cit.artifact_path, "docs/governance/x.md")

    def test_no_path_citation_falls_back_to_type_only(self) -> None:
        """A SUPPORT REQ that cites NO path keeps the type-only ledger check —
        path-aware enforcement only fires when a path is actually cited."""
        from gzkit.req_kind_support import resolve_support_proof

        req = "manpage updated. Witnessed by `artifact_edited` + `gz validate --documents`"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_ledger_with_events(root, [_ev("artifact_edited", None)])
            with patch(_PATCH_SCOPE, return_value=True):
                result = resolve_support_proof(req, root, req_id="REQ-0.0.69-01-04")
            self.assertEqual(result, "pass")


class TestResolveSupportProofFailClose(unittest.TestCase):
    """REQ-0.0.69-01-02 and REQ-0.0.69-01-03: fail-close on missing event or failing scope."""

    @covers("REQ-0.0.69-01-02")
    def test_unproven_when_cited_event_absent(self) -> None:
        """Cited event NOT in ledger → unproven; never "advisory-support"."""
        from gzkit.req_kind_support import resolve_support_proof

        req_text = "manpage updated. Witnessed by `artifact_edited` + `gz validate --documents`"

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
        from gzkit.req_kind_support import resolve_support_proof

        req_text = "manpage updated. Witnessed by `artifact_edited` + `gz validate --documents`"

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
        from gzkit.req_kind_support import resolve_support_proof

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
        from gzkit.req_kind_support import resolve_support_proof

        req_text = "manpage updated. Witnessed by `artifact_edited` + `gz validate --documents`"

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _make_ledger(project_root, "artifact_edited")

            # Patch the in-process dispatch to simulate a failing scope
            with patch("gzkit.req_kind_support._dispatch_validator_scope", return_value=False):
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
        from gzkit.triangle import DiscoveredReq, ReqEntity, ReqId, ReqStatus, ReqTestability

        rid = ReqId.parse("REQ-0.0.59-99-01")
        entity = ReqEntity(
            id=rid,
            description="rule updated — artifact_edited gz validate --documents",
            status=ReqStatus.UNCHECKED,
            parent_obpi="OBPI-0.0.59-99",
            kind=ReqTestability.CODE,
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
        from gzkit.req_kind_support import resolve_support_proof

        req_text = (
            "discipline enforced. Witnessed by `artifact_edited` "
            "+ `gz validate --req-kind-discipline`"
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
        from gzkit.req_kind_support import resolve_support_proof

        req_text = "proof computed. Witnessed by `artifact_edited` + `gz validate --closeout-proof`"

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _make_ledger(project_root, "artifact_edited")
            result = resolve_support_proof(req_text, project_root)

        self.assertNotEqual(result, "pass")
        self.assertNotEqual(result, "advisory-support")


class TestEarlyReturnScopeDispatch(unittest.TestCase):
    """REQ-0.0.69-01-01 extended (GHI #630): SUPPORT proofs citing early-return
    validator scopes (qc-binding, fidelity-presence, waiver-ratchet) — which own
    their full 0/2/3 lifecycle in validate_cmd — must dispatch via their
    trust-audit fn instead of fail-closing as unproven regardless of truth.

    GHI #630 met this by hand-wiring a `_early_return_scope_audit` map, because
    the three were absent from VALIDATOR_REGISTRY and so from the aggregate
    runner maps. They are now registered, so dispatch resolves them through
    `_explicit_scope_runners` like every other scope and that map is retired.
    The behavior these tests pin is unchanged; the patch target follows the
    dispatch path, which now reads the `trust_audits` package export.
    """

    _QC_BINDING_REQ = (
        "the --qc-binding scope is wired as a bound QC step. "
        "Witnessed by `artifact_edited` + `gz validate --qc-binding`"
    )

    @covers("REQ-0.0.69-01-01")
    def test_qc_binding_support_proof_passes_when_scope_clean(self) -> None:
        """Cited event present + qc-binding audit clean → "pass" (not unproven)."""
        from gzkit.req_kind_support import resolve_support_proof

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _make_ledger(project_root, "artifact_edited")
            with patch(
                "gzkit.governance.trust_audits.audit_qc_binding",
                return_value=[],
            ):
                result = resolve_support_proof(self._QC_BINDING_REQ, project_root)

        self.assertEqual(result, "pass")

    @covers("REQ-0.0.69-01-03")
    def test_qc_binding_support_proof_unproven_when_scope_errors(self) -> None:
        """The fix can still fail for the right reason: a qc-binding audit that
        returns errors resolves unproven, never pass (ADR-0.0.73 thesis)."""
        from gzkit.req_kind_support import resolve_support_proof

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _make_ledger(project_root, "artifact_edited")
            with patch(
                "gzkit.governance.trust_audits.audit_qc_binding",
                return_value=[object()],  # one error → scope not clean
            ):
                result = resolve_support_proof(self._QC_BINDING_REQ, project_root)

        self.assertNotEqual(result, "pass")


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
        from gzkit.req_kind_support import _KNOWN_LEDGER_EVENT_TYPES

        self.assertGreater(len(_KNOWN_LEDGER_EVENT_TYPES), 0, "Set must be non-empty")
        self.assertIn("artifact_edited", _KNOWN_LEDGER_EVENT_TYPES)

    def test_ghost_types_absent(self) -> None:
        """Ghost event types (not in TypedLedgerEvent union and not observed) must be absent."""
        from gzkit.req_kind_support import _KNOWN_LEDGER_EVENT_TYPES

        # obpi_completed was hand-maintained and is not in the TypedLedgerEvent union
        self.assertNotIn(
            "obpi_completed",
            _KNOWN_LEDGER_EVENT_TYPES,
            "obpi_completed is a ghost: not in TypedLedgerEvent union, must be removed",
        )

    def test_all_typed_events_present(self) -> None:
        """Every event type from TypedLedgerEvent union must be in _KNOWN_LEDGER_EVENT_TYPES."""
        from gzkit.req_kind_support import _KNOWN_LEDGER_EVENT_TYPES

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
        from gzkit.req_kind_support import _UNTYPED_LEDGER_EVENT_EXTRAS

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


class TestWitnessClauseGrammar(unittest.TestCase):
    """GHI #888: a SUPPORT REQ declares its proof; the parser never infers it.

    `parse_support_citation` scanned the whole REQ body for known event names with
    `in`, a substring test over free text. It could not tell a REQ that CITES an
    event from one that DENIES the event exists, and the failure was directional:
    it could only ever ADD event types, so a REQ could only look more proven than
    it was. These tests pin the replacement — an explicit, delimited witness
    clause that is READ, never a body that is GUESSED at.
    """

    _EV = "artifact_edited"

    def test_the_declaration_is_read_from_the_clause_not_the_body(self) -> None:
        from gzkit.req_kind_support import parse_support_citation

        req = (
            "the retirement is recorded. Witnessed by `artifact_edited` citing "
            "`docs/user/runbook.md` + `gz validate --documents`."
        )
        cit = parse_support_citation(req)
        assert cit is not None
        self.assertEqual(cit.event_types, [self._EV])
        self.assertEqual(cit.scope, "documents")
        self.assertEqual(cit.artifact_path, "docs/user/runbook.md")

    def test_a_denial_in_the_body_is_not_a_citation(self) -> None:
        # THE DEFECT, verbatim from GHI #888's reproduction. The sentence states
        # the event does NOT exist. Under the substring parser it was returned as
        # the REQ's proof channel and resolved green for the very reason the REQ
        # was amended. The clause is the only thing read, so the body cannot reach
        # the proof channel however it phrases itself.
        from gzkit.req_kind_support import parse_support_citation

        req = (
            "The ledger carries NO corpus_entry_retired event for these ids — measured "
            "0 of 8. Proven instead by the corpus row; gz validate "
            "--rendition-floor-coherence passes."
        )
        self.assertIsNone(parse_support_citation(req))

    def test_an_unrelated_mention_in_the_body_is_not_a_citation(self) -> None:
        # The same class in its quieter form: a REQ that QUOTES another REQ, or
        # documents a rejected alternative, acquired that event as proof. Nothing
        # about this text declares a witness, so nothing is parsed from it.
        from gzkit.req_kind_support import parse_support_citation

        req = (
            "the writer rejects an `artifact_edited` payload lacking a path, per the "
            "alternative considered in REQ-02 — `gz validate --documents` passes."
        )
        self.assertIsNone(parse_support_citation(req))

    def test_a_missing_declaration_is_refused_never_inferred(self) -> None:
        from gzkit.req_kind_support import parse_support_citation

        req = "manpage updated — artifact_edited ledger event + gz validate --documents"
        self.assertIsNone(parse_support_citation(req))

    def test_two_clauses_are_ambiguous_and_refused(self) -> None:
        # Ambiguity is refused, not resolved by preference. Picking one would put
        # the parser back in the business of guessing which claim is the proof.
        from gzkit.req_kind_support import parse_support_citation

        # The two clauses name the SAME event and the SAME scope deliberately. An
        # earlier version of this test used different ones and passed for the wrong
        # reason — the event/scope ambiguity guards rejected it, so the marker-count
        # rule was never exercised and a mutation relaxing it survived. Identical
        # clauses leave marker-count as the only rule that can refuse this input.
        req = (
            "Witnessed by `artifact_edited` + `gz validate --documents`. "
            "Witnessed by `artifact_edited` + `gz validate --documents`."
        )
        self.assertIsNone(parse_support_citation(req))

    def test_two_event_types_in_one_clause_are_ambiguous_and_refused(self) -> None:
        from gzkit.req_kind_support import parse_support_citation

        req = "Witnessed by `artifact_edited` and `obpi_created` + `gz validate --documents`."
        self.assertIsNone(parse_support_citation(req))

    def test_two_validator_scopes_in_one_clause_are_ambiguous_and_refused(self) -> None:
        # A clause naming two scopes names neither as THE structural arm. Refused
        # rather than resolved by preference — the old parser's fence-scope
        # preference is exactly the inference this grammar retires.
        from gzkit.req_kind_support import parse_support_citation

        req = (
            "Witnessed by `artifact_edited` + `gz validate --documents` and "
            "`gz validate --surfaces`."
        )
        self.assertIsNone(parse_support_citation(req))

    def test_a_clause_naming_no_recognized_event_is_refused(self) -> None:
        from gzkit.req_kind_support import parse_support_citation

        req = "Witnessed by `totally_made_up_event` + `gz validate --documents`."
        self.assertIsNone(parse_support_citation(req))

    def test_a_clause_with_no_validator_scope_is_refused(self) -> None:
        from gzkit.req_kind_support import parse_support_citation

        self.assertIsNone(parse_support_citation("Witnessed by `artifact_edited`."))

    def test_a_body_scope_does_not_complete_a_clause_that_lacks_one(self) -> None:
        # The clause is the whole declaration. Borrowing the scope from the body
        # would reopen the same seam one field over.
        from gzkit.req_kind_support import parse_support_citation

        req = "`gz validate --documents` passes. Witnessed by `artifact_edited`."
        self.assertIsNone(parse_support_citation(req))

    def test_an_undeclared_req_resolves_undeclared_never_pass(self) -> None:
        from gzkit.req_kind_support import resolve_support_proof

        req = "manpage updated — artifact_edited ledger event + gz validate --documents"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_ledger_with_events(root, [_ev("artifact_edited", None)])
            with patch(_PATCH_SCOPE, return_value=True):
                result = resolve_support_proof(req, root, req_id="REQ-X")
        self.assertEqual(result, "undeclared-support")
        self.assertNotEqual(result, "pass")
