"""The catalog's edges, coverage report and BDD alignment: RO-3 tranche 3.

`docs/governance/harbor-ro3-requirements-store.md` § Tranches row 3 and § The
witness: `depends_on` resolving and acyclic, `governed_by` resolving through the
RO-2 seam, `member_of` resolving, `derives_from` naming a live PRD FR or § 7
attribute, the coverage report, and BDD alignment. Rulings of 2026-10-22: a § 7
attribute is `NFR-<slug>` derived from its heading; `depends_on` names a gate as
`gate:<n>` and a boundary as `external:<slug>` from a declared roster; a catalog
REQ's BDD binding is its scenario tag and its `@covers` test. The freeze lock
moved to RO-5.
"""

import json
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from gzkit.governance.trust_audits.catalog import audit_catalog
from gzkit.governance.trust_audits.catalog_edges import (
    bdd_findings,
    coverage_gaps,
    edge_findings,
    prd_needs,
)
from gzkit.models.catalog import Catalog, Criterion, External, Outcome, Req
from gzkit.traceability import CatalogBindings

_PRD = textwrap.dedent(
    """
    # PRD

    ## 6. Functional Requirements

    ### FR-001: Project Initialization

    Initialize a project.

    ### FR-004: Brief Creation

    **Retired 2026-10-18** (§ 19). No standalone brief exists.

    ### FR-005a: OBPI Brief Creation

    Create a brief.

    ## 7. Non-Functional Requirements

    ### Performance

    - fast

    ### Explainability

    - traced

    ## 8. Dependencies

    ### Runtime

    - Python
    """
)

_NEEDS = frozenset({"FR-001", "FR-005a", "NFR-performance", "NFR-explainability"})
_GATES = frozenset({1, 2, 3, 4, 5})


def _outcome(code: str, **fields: object) -> Outcome:
    base: dict[str, object] = {
        "code": code,
        "statement": "The operator can resume a session.",
        "owner": "g0",
        "user_facing": False,
        "governed_by": [],
        "depends_on": [],
        "feature": None,
        "retired": False,
    }
    return Outcome.model_validate(base | fields)


def _req(req_id: str, member_of: str = "H1", **fields: object) -> Req:
    base: dict[str, object] = {
        "id": req_id,
        "member_of": member_of,
        "statement": "Effect, because rationale.",
        "criteria": [Criterion(state_or_input="s", required_outcome="o", evidence="e")],
        "kind": "BEHAVIOR",
        "revision": 1,
        "derives_from": ["FR-001"],
        "applies_to": [],
    }
    return Req.model_validate(base | fields)


def _catalog(
    outcomes: tuple[Outcome, ...] = (),
    reqs: tuple[Req, ...] = (),
    externals: tuple[External, ...] = (),
) -> Catalog:
    return Catalog(families=(), outcomes=outcomes, reqs=reqs, externals=externals)


def _edges(catalog: Catalog, governed: frozenset[str] = frozenset()) -> list[str | None]:
    errors = edge_findings(catalog, needs=_NEEDS, gates=_GATES, governs=lambda adr: adr in governed)
    return [error.field for error in errors]


class TestPrdNeeds(unittest.TestCase):
    """The live needs are the PRD's unretired FRs and its § 7 attributes."""

    def test_live_frs_and_section_seven_attributes_are_read_from_the_prd(self):
        self.assertEqual(
            prd_needs(_PRD),
            ("FR-001", "FR-005a", "NFR-performance", "NFR-explainability"),
        )

    def test_an_fr_with_no_prose_before_the_next_heading_is_live(self):
        """Only a `**Retired` line retires an FR; an empty body is not one."""
        text = "## 6. FRs\n\n### FR-001: A\n### FR-002: B\n\n## 7. NFRs\n\n### FR-003: C\n"
        self.assertEqual(prd_needs(text), ("FR-001", "FR-002", "FR-003"))

    def test_a_retired_fr_and_a_heading_outside_section_seven_are_not_needs(self):
        needs = prd_needs(_PRD)
        self.assertNotIn("FR-004", needs)
        self.assertNotIn("NFR-runtime", needs)


class TestDependsOn(unittest.TestCase):
    """An outcome's `depends_on` resolves, by declared prefix, and is acyclic."""

    def test_an_outcome_a_gate_and_a_rostered_boundary_resolve(self):
        external = External(slug="github", name="GitHub", scope="Issues and releases.")
        catalog = _catalog(
            (_outcome("H1"), _outcome("H2", depends_on=["H1", "gate:5", "external:github"])),
            externals=(external,),
        )
        self.assertEqual(_edges(catalog), [])

    def test_an_unknown_outcome_gate_or_boundary_fails(self):
        for target in ("H9", "gate:6", "gate:x", "external:gitlab", "ADR-0.1.0"):
            with self.subTest(target=target):
                catalog = _catalog((_outcome("H1", depends_on=[target]),))
                self.assertEqual(_edges(catalog), ["depends_on"])

    def test_a_cycle_through_outcomes_fails(self):
        catalog = _catalog(
            (
                _outcome("H1", depends_on=["H2"]),
                _outcome("H2", depends_on=["H3"]),
                _outcome("H3", depends_on=["H1"]),
            )
        )
        self.assertEqual(_edges(catalog), ["depends_on"])

    def test_a_self_dependency_is_a_cycle(self):
        self.assertEqual(_edges(_catalog((_outcome("H1", depends_on=["H1"]),))), ["depends_on"])


class TestGovernedBy(unittest.TestCase):
    """`governed_by` resolves through the RO-2 seam."""

    def test_a_resolving_adr_passes_and_an_unknown_one_fails(self):
        catalog = _catalog((_outcome("H1", governed_by=["ADR-0.1.0"]),))
        self.assertEqual(_edges(catalog, frozenset({"ADR-0.1.0"})), [])
        self.assertEqual(_edges(catalog), ["governed_by"])


class TestMemberOf(unittest.TestCase):
    def test_a_req_in_an_outcome_the_catalog_lacks_fails(self):
        catalog = _catalog((_outcome("H1"),), (_req("REQ-1", member_of="H2"),))
        self.assertEqual(_edges(catalog), ["member_of"])


class TestDerivesFrom(unittest.TestCase):
    def test_a_live_fr_and_a_section_seven_attribute_resolve(self):
        req = _req("REQ-1", derives_from=["FR-005a", "NFR-performance"])
        self.assertEqual(_edges(_catalog((_outcome("H1"),), (req,))), [])

    def test_a_retired_or_unknown_need_fails(self):
        for need in ("FR-004", "FR-099", "NFR-runtime"):
            with self.subTest(need=need):
                req = _req("REQ-1", derives_from=[need])
                self.assertEqual(_edges(_catalog((_outcome("H1"),), (req,))), ["derives_from"])


class TestCoverageReport(unittest.TestCase):
    """A need no REQ derives from is listed, in the PRD's order."""

    def test_an_empty_catalog_leaves_every_need_uncovered(self):
        needs = prd_needs(_PRD)
        self.assertEqual(coverage_gaps(_catalog(), needs), list(needs))

    def test_a_derived_need_drops_out_of_the_report(self):
        req = _req("REQ-1", derives_from=["FR-001", "NFR-performance"])
        gaps = coverage_gaps(_catalog((_outcome("H1"),), (req,)), prd_needs(_PRD))
        self.assertEqual(gaps, ["FR-005a", "NFR-explainability"])


def _bindings(
    *,
    tags: frozenset[str] = frozenset({"H1"}),
    scenarios: frozenset[str] = frozenset({"REQ-1"}),
    covered: frozenset[str] = frozenset({"REQ-1"}),
) -> CatalogBindings:
    path = "features/resume.feature"
    return CatalogBindings(
        feature_tags={path: tags}, scenario_reqs={path: scenarios}, covered_reqs=covered
    )


class TestBddAlignment(unittest.TestCase):
    """A user-facing outcome's feature carries its code; each BEHAVIOR REQ has both bindings."""

    def _catalog(self, **outcome_fields: object) -> Catalog:
        fields: dict[str, object] = {"user_facing": True, "feature": "features/resume.feature"}
        return _catalog(
            (_outcome("H1", **(fields | outcome_fields)),),
            (_req("REQ-1"), _req("REQ-2", kind="SUPPORT")),
        )

    def _fields(self, catalog: Catalog, bindings: CatalogBindings) -> list[str | None]:
        return [error.field for error in bdd_findings(catalog, bindings)]

    def test_an_aligned_outcome_passes(self):
        self.assertEqual(self._fields(self._catalog(), _bindings()), [])

    def test_a_user_facing_outcome_without_a_feature_fails(self):
        self.assertEqual(self._fields(self._catalog(feature=None), _bindings()), ["feature"])

    def test_a_feature_file_that_does_not_exist_or_lacks_the_code_tag_fails(self):
        missing = self._catalog(feature="features/other.feature")
        self.assertEqual(self._fields(missing, _bindings()), ["feature"])
        self.assertEqual(self._fields(self._catalog(), _bindings(tags=frozenset())), ["feature"])

    def test_a_behavior_req_without_its_scenario_tag_or_covers_test_fails(self):
        catalog = self._catalog()
        self.assertEqual(self._fields(catalog, _bindings(scenarios=frozenset())), ["scenario"])
        self.assertEqual(self._fields(catalog, _bindings(covered=frozenset())), ["covers"])

    def test_an_outcome_that_is_not_user_facing_needs_no_feature(self):
        catalog = self._catalog(user_facing=False, feature=None)
        self.assertEqual(self._fields(catalog, _bindings(scenarios=frozenset())), [])


class TestAuditOverAProject(unittest.TestCase):
    """`audit_catalog` reads the PRD, the manifest, the ledger, features and tests itself."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "design" / "prd").mkdir(parents=True)
        (self.root / "design" / "prd" / "PRD-TEST-1.0.0.md").write_text(_PRD, encoding="utf-8")
        (self.root / ".gzkit").mkdir()
        manifest = {"gates": {"lite": [1, 2], "heavy": [1, 2, 3, 4, 5]}}
        (self.root / ".gzkit" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        self.write("families", [{"code": "H", "band": "product", "name": "H", "scope": "S."}])
        self.write("externals", [])
        self.write("work_packages", [])
        self.write("outcomes", [_outcome("H1", depends_on=["gate:5"]).model_dump(mode="json")])
        self.write("reqs", [_req("REQ-1", kind="SUPPORT").model_dump(mode="json")])

    def write(self, kind: str, entries: list[object]) -> None:
        path = self.root / "data" / "catalog" / f"{kind}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"_doc": "Fixture.", kind: entries}), encoding="utf-8")

    def test_a_project_whose_edges_resolve_passes(self):
        self.assertEqual(audit_catalog(self.root), [])

    def test_the_audit_reads_the_live_prd_and_the_manifest_gates(self):
        bad = _req("REQ-1", kind="SUPPORT", derives_from=["FR-004"]).model_dump(mode="json")
        self.write("reqs", [bad])
        self.write("outcomes", [_outcome("H1", depends_on=["gate:9"]).model_dump(mode="json")])
        fields = sorted(str(error.field) for error in audit_catalog(self.root))
        self.assertEqual(fields, ["depends_on", "derives_from"])

    def test_an_adr_the_ledger_does_not_record_fails_governed_by(self):
        outcome = _outcome("H1", governed_by=["ADR-0.1.0"]).model_dump(mode="json")
        self.write("outcomes", [outcome])
        self.assertEqual([e.field for e in audit_catalog(self.root)], ["governed_by"])

    def test_governed_by_resolves_an_adr_the_ledger_records_and_refuses_an_obpi(self):
        from gzkit.ledger import Ledger
        from gzkit.ledger_events import adr_created_event, obpi_created_event

        ledger = Ledger(self.root / ".gzkit" / "ledger.jsonl")
        ledger.append(adr_created_event("ADR-0.1.0-probe", "PRD-TEST-1.0.0", "lite"))
        ledger.append(obpi_created_event("OBPI-0.1.0-01-probe", "ADR-0.1.0-probe"))
        for adr, expected in (("ADR-0.1.0-probe", []), ("OBPI-0.1.0-01-probe", ["governed_by"])):
            with self.subTest(adr=adr):
                outcome = _outcome("H1", governed_by=[adr]).model_dump(mode="json")
                self.write("outcomes", [outcome])
                self.assertEqual([e.field for e in audit_catalog(self.root)], expected)

    def test_depends_on_reads_the_roster_from_the_externals_file(self):
        outcome = _outcome("H1", depends_on=["external:github"]).model_dump(mode="json")
        self.write("outcomes", [outcome])
        self.assertEqual([e.field for e in audit_catalog(self.root)], ["depends_on"])
        self.write("externals", [{"slug": "github", "name": "GitHub", "scope": "Issues."}])
        self.assertEqual(audit_catalog(self.root), [])

    def test_bdd_alignment_reads_the_projects_features_and_tests(self):
        outcome = _outcome("H1", user_facing=True, feature="features/resume.feature")
        self.write("outcomes", [outcome.model_dump(mode="json")])
        self.write("reqs", [_req("REQ-1").model_dump(mode="json")])
        (self.root / "features").mkdir()
        (self.root / "features" / "resume.feature").write_text(
            "@H1\nFeature: Resume\n\n  @REQ-1\n  Scenario: resumes\n    Given a handoff\n",
            encoding="utf-8",
        )
        self.assertEqual([e.field for e in audit_catalog(self.root)], ["covers"])
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_resume.py").write_text(
            '@covers("REQ-1")\ndef test_resumes():\n    pass\n', encoding="utf-8"
        )
        self.assertEqual(audit_catalog(self.root), [])


class TestNegativeControls(unittest.TestCase):
    """Each check family's control catches every case it plants, for its own reason."""

    _CLAIMS = (
        "requirements-catalog-edges",
        "requirements-catalog-coverage",
        "requirements-catalog-bdd",
    )

    def _builders(self):
        """Return the control builders, writing under a temp dir this test owns."""
        from gzkit.governance.trust_audits import _qc_negative_controls as nc

        tmp = Path(self.enterContext(TemporaryDirectory()))
        self.enterContext(patch.object(nc, "_mkroot", lambda slug: tmp / slug))
        return nc

    def test_each_control_catches_its_fixture(self):
        from gzkit.enforcement import (
            EXEMPTS_NONE,
            _run_single_claim,
            production_enforcement_registry,
        )

        records = {r.claim_id: r for r in production_enforcement_registry()}
        for claim in self._CLAIMS:
            with self.subTest(claim=claim):
                result = _run_single_claim(records[claim])
                self.assertEqual(result.outcome, "PASS", result.message)
                self.assertEqual(records[claim].exempts, EXEMPTS_NONE)
                self.assertIsNotNone(records[claim].population)

    def test_a_control_missing_one_planted_case_reports_no_catch(self):
        """The edges and BDD controls need every case they plant, or nothing is caught."""
        from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep

        nc = self._builders()
        root = nc._build_catalog_edges()
        reqs = root / "data" / "catalog" / "reqs.json"
        payload = json.loads(reqs.read_text(encoding="utf-8"))
        payload["reqs"] = [r for r in payload["reqs"] if r["member_of"] != "H7"]
        reqs.write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual(ep._ep_catalog_edges(root), [])

        root = nc._build_catalog_bdd()
        (root / "features" / "h2.feature").write_text(
            "@H2\nFeature: H2\n\n  @REQ-1\n  Scenario: s\n    Given g\n", encoding="utf-8"
        )
        self.assertEqual(ep._ep_catalog_bdd(root), [])

    def test_the_coverage_control_reports_no_catch_when_a_finding_fires(self):
        from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep

        nc = self._builders()
        root = nc._build_catalog_coverage()
        outcomes = root / "data" / "catalog" / "outcomes.json"
        payload = json.loads(outcomes.read_text(encoding="utf-8"))
        payload["outcomes"][0]["depends_on"] = ["H9"]
        outcomes.write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual(ep._ep_catalog_coverage(root), [])


if __name__ == "__main__":
    unittest.main()
