"""The requirements store, landed empty: RO-3 tranche 1.

`docs/governance/harbor-ro3-requirements-store.md` § Tranches row 1: the three
catalog files with their schemas and models, the family legend seeded, and
`gz validate --catalog` with the structure checks. Done when the files validate,
the scope runs in `gz check`, the legend's eleven families pass and a malformed
entry fails.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from pydantic import ValidationError as PydanticValidationError

from gzkit.governance.trust_audits.catalog import audit_catalog
from gzkit.models.catalog import (
    CATALOG_FILES,
    Family,
    Outcome,
    Req,
    catalog_json_schemas,
    load_catalog,
)
from gzkit.schemas import load_schema

_REPO = Path(__file__).resolve().parents[2]

#: Decision 8.3 of docs/governance/ieee/requirements-model.md, ruled 2026-10-18.
_RULED_BANDS = {
    "product": {"X", "H", "C", "M", "P", "D"},
    "common": {"R", "G", "A", "L", "Q"},
}


def _family(code: str, band: str = "product") -> dict[str, str]:
    return {"code": code, "band": band, "name": f"family {code}", "scope": "One sentence."}


def _outcome(code: str) -> dict[str, object]:
    return {
        "code": code,
        "statement": "The operator can resume a session.",
        "owner": "g0",
        "user_facing": False,
        "governed_by": [],
        "depends_on": [],
        "feature": None,
        "retired": False,
    }


def _req(req_id: str, member_of: str = "H1") -> dict[str, object]:
    return {
        "id": req_id,
        "member_of": member_of,
        "statement": "Effect, because rationale.",
        "criteria": [
            {
                "state_or_input": "a fresh handoff",
                "required_outcome": "its steps are presented",
                "evidence": "a test id",
            }
        ],
        "kind": "BEHAVIOR",
        "revision": 1,
        "derives_from": ["FR-001"],
        "applies_to": [],
    }


class _Tree(unittest.TestCase):
    """A temp project with a valid catalog; each test breaks one thing."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "data" / "catalog").mkdir(parents=True)
        self.write("families", [_family("H"), _family("G", "common")])
        self.write("outcomes", [_outcome("H1")])
        self.write("reqs", [_req("REQ-1")])
        self.write("externals", [])
        # The REQ derives from FR-001, which tranche 3's derives_from check reads
        # from the live PRD under the configured PRD directory.
        prd = self.root / "design" / "prd" / "PRD-FIXTURE-1.0.0.md"
        prd.parent.mkdir(parents=True)
        prd.write_text("## 6. Requirements\n\n### FR-001: Init\n\nInit.\n", encoding="utf-8")

    def write(self, kind: str, entries: list[object]) -> None:
        payload = {"_doc": "Fixture catalog.", kind: entries}
        self.write_raw(kind, json.dumps(payload))

    def write_raw(self, kind: str, text: str) -> None:
        (self.root / "data" / "catalog" / f"{kind}.json").write_text(text, encoding="utf-8")

    def fields(self) -> list[str | None]:
        return [error.field for error in audit_catalog(self.root)]


class TestModels(unittest.TestCase):
    """Each entry is a frozen model that refuses a shape the spec does not allow."""

    def test_a_family_code_is_one_capital_letter(self):
        for code in ("HH", "h", "", "1"):
            with self.subTest(code=code), self.assertRaises(PydanticValidationError):
                Family.model_validate(_family(code))

    def test_a_family_band_is_product_or_common(self):
        with self.assertRaises(PydanticValidationError):
            Family.model_validate(_family("H", "other"))

    def test_an_outcome_code_is_a_family_letter_and_a_dotted_number(self):
        for code in ("H1", "H1.4", "R3.12.2"):
            with self.subTest(code=code):
                self.assertEqual(Outcome.model_validate(_outcome(code)).code, code)
        for code in ("H", "1.4", "H1.", "h1", "H01"):
            with self.subTest(code=code), self.assertRaises(PydanticValidationError):
                Outcome.model_validate(_outcome(code))

    def test_a_req_id_is_the_area_free_sequential_grammar(self):
        self.assertEqual(Req.model_validate(_req("REQ-12")).id, "REQ-12")
        for req_id in ("REQ-0", "REQ-01", "REQ-0.35.0-01-01", "REQ-H1-1", "req-1"):
            with self.subTest(req_id=req_id), self.assertRaises(PydanticValidationError):
                Req.model_validate(_req(req_id))

    def test_a_req_carries_one_kind_of_three(self):
        with self.assertRaises(PydanticValidationError):
            Req.model_validate({**_req("REQ-1"), "kind": "PROSE"})

    def test_a_req_has_at_least_one_criterion_and_a_positive_revision(self):
        with self.assertRaises(PydanticValidationError):
            Req.model_validate({**_req("REQ-1"), "criteria": []})
        with self.assertRaises(PydanticValidationError):
            Req.model_validate({**_req("REQ-1"), "revision": 0})

    def test_a_req_carries_no_proof_and_an_outcome_no_lifecycle_state(self):
        """Proof and delivery status live only in the ledger (decisions 3 and 4)."""
        with self.assertRaises(PydanticValidationError):
            Req.model_validate({**_req("REQ-1"), "verdict": "SATISFIED"})
        with self.assertRaises(PydanticValidationError):
            Outcome.model_validate({**_outcome("H1"), "state": "validated"})

    def test_entries_are_frozen(self):
        family = Family.model_validate(_family("H"))
        with self.assertRaises(PydanticValidationError):
            family.code = "G"  # ty: ignore[invalid-assignment]


class TestSchemas(unittest.TestCase):
    """The committed schemas are the models' projection, so neither drifts alone."""

    def test_each_committed_schema_equals_its_model(self):
        for kind, schema in catalog_json_schemas().items():
            with self.subTest(kind=kind):
                self.assertEqual(load_schema(f"catalog_{kind}"), schema)

    def test_each_kind_is_one_file(self):
        self.assertEqual(set(catalog_json_schemas()), set(CATALOG_FILES))


class TestStructure(_Tree):
    """`audit_catalog`'s tranche-1 structure checks; the edges are tranche 3's tests."""

    def test_a_valid_catalog_passes(self):
        self.assertEqual(audit_catalog(self.root), [])

    def test_the_catalog_loads_as_models(self):
        catalog = load_catalog(self.root)
        self.assertEqual([f.code for f in catalog.families], ["H", "G"])
        self.assertEqual([o.code for o in catalog.outcomes], ["H1"])
        self.assertEqual([r.id for r in catalog.reqs], ["REQ-1"])

    def test_a_missing_file_is_a_finding(self):
        (self.root / "data" / "catalog" / "reqs.json").unlink()
        self.assertEqual(self.fields(), ["reqs"])

    def test_malformed_json_is_a_finding(self):
        self.write_raw("outcomes", "{nope")
        self.assertEqual(self.fields(), ["outcomes"])

    def test_a_malformed_entry_fails_against_the_schema(self):
        self.write("families", [_family("H", "other")])
        errors = audit_catalog(self.root)
        self.assertEqual([e.field for e in errors], ["families"])
        self.assertIn("band", errors[0].message)

    def test_a_finding_names_the_file_the_ruling_and_the_recovery(self):
        """Three-part recovery prose (.gzkit/rules/guardrail-feedback-prose.md)."""
        self.write("families", [_family("H", "other")])
        (error,) = audit_catalog(self.root)
        self.assertEqual(error.artifact, "data/catalog/families.json")
        self.assertIn("harbor-ro3-requirements-store.md", error.message)
        self.assertIn("uv run gz validate --catalog", error.message)

    def test_a_file_without_its_doc_header_fails(self):
        self.write_raw("reqs", json.dumps({"reqs": []}))
        self.assertEqual(self.fields(), ["reqs"])

    def test_a_duplicate_family_code_fails(self):
        self.write("families", [_family("H"), _family("H", "common")])
        self.assertEqual(self.fields(), ["families"])

    def test_a_duplicate_outcome_code_fails(self):
        self.write("outcomes", [_outcome("H1"), _outcome("H1")])
        self.assertEqual(self.fields(), ["outcomes"])

    def test_a_duplicate_req_id_fails(self):
        self.write("reqs", [_req("REQ-1"), _req("REQ-1")])
        self.assertEqual(self.fields(), ["reqs"])

    def test_an_outcome_in_a_family_the_legend_lacks_fails(self):
        self.write("outcomes", [_outcome("H1"), _outcome("Z2")])
        errors = audit_catalog(self.root)
        self.assertEqual([e.field for e in errors], ["outcomes"])
        self.assertIn("Z2", errors[0].message)

    def test_a_retired_outcome_still_holds_its_code(self):
        """A retired code stays in the file so it is never reused."""
        self.write("outcomes", [_outcome("H1"), {**_outcome("H1"), "retired": True}])
        self.assertEqual(self.fields(), ["outcomes"])


class TestLiveTree(unittest.TestCase):
    """The repository's own catalog: the legend seeded, outcomes and REQs empty."""

    def test_the_repository_passes_its_own_scope(self):
        self.assertEqual(audit_catalog(_REPO), [])

    def test_the_legend_is_decision_8_3s_eleven_families_in_their_bands(self):
        families = load_catalog(_REPO).families
        self.assertEqual(len(families), 11)
        by_band: dict[str, set[str]] = {"product": set(), "common": set()}
        for family in families:
            by_band[family.band].add(family.code)
        self.assertEqual(by_band, _RULED_BANDS)

    def test_no_outcome_or_req_is_authored(self):
        catalog = load_catalog(_REPO)
        self.assertEqual((catalog.outcomes, catalog.reqs), ((), ()))

    def test_each_file_is_a_declared_config_registry(self):
        from gzkit.governance.trust_audits.config_registry import audit_config_registry

        declared = json.loads((_REPO / "data" / "config_registry.json").read_text("utf-8"))
        for kind in CATALOG_FILES:
            with self.subTest(kind=kind):
                self.assertIn(f"catalog/{kind}.json", declared["registries"])
        findings = [e for e in audit_config_registry(_REPO) if "catalog" in e.artifact]
        self.assertEqual(findings, [])


class TestDispatch(unittest.TestCase):
    """A scope reachable only behind a remembered flag, or exiting 1, is not a gate."""

    def _invoke(self, band: str):
        from gzkit.cli import main
        from tests.commands.common import CliRunner, _quick_init

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            catalog = Path("data") / "catalog"
            catalog.mkdir(parents=True, exist_ok=True)
            for kind, entries in (
                ("families", [_family("H", band)]),
                ("outcomes", []),
                ("reqs", []),
                ("externals", []),
            ):
                text = json.dumps({"_doc": "Fixture catalog.", kind: entries})
                (catalog / f"{kind}.json").write_text(text, encoding="utf-8")
            return runner.invoke(main, ["validate", "--catalog"])

    def test_the_flag_reaches_the_scope_and_a_breach_is_a_policy_breach(self):
        result = self._invoke("other")
        self.assertEqual(result.exit_code, 3, result.output)
        self.assertIn("families", result.output)

    def test_the_flag_passes_a_valid_catalog(self):
        result = self._invoke("product")
        self.assertEqual(result.exit_code, 0, result.output)

    def test_the_audit_is_part_of_the_packages_declared_surface(self):
        from gzkit.governance import trust_audits

        self.assertIn("audit_catalog", trust_audits.__all__)
        self.assertIs(trust_audits.audit_catalog, audit_catalog)

    def test_gz_check_shells_the_scope_as_its_own_bound_step(self):
        from gzkit import quality
        from gzkit.commands.quality import _STEP_GUARD_META, _build_check_steps
        from gzkit.qc_binding import build_qc_registry

        runner = dict(_build_check_steps())["Requirements catalog"]
        with patch.object(quality, "run_command", return_value="ran") as shelled:
            self.assertEqual(runner(_REPO), "ran")
        self.assertEqual(shelled.call_args.args[0], "uv run gz validate --catalog")
        self.assertEqual(_STEP_GUARD_META["Requirements catalog"][0], "requirements-catalog")
        step = {s.name: s for s in build_qc_registry()}["Requirements catalog"]
        self.assertEqual((step.binding, step.subject), ("bound", "data/"))


class TestNegativeControl(unittest.TestCase):
    """The refuse control is registered and catches its fixture for its own reason."""

    def test_the_refuse_control_catches_its_fixture(self):
        from gzkit.enforcement import (
            EXEMPTS_NONE,
            _run_single_claim,
            production_enforcement_registry,
        )

        record = {r.claim_id: r for r in production_enforcement_registry()}["requirements-catalog"]
        result = _run_single_claim(record)
        self.assertEqual(result.outcome, "PASS", result.message)
        self.assertEqual(record.exempts, EXEMPTS_NONE)
        self.assertIsNotNone(record.population)

    def test_the_refuse_entrypoint_reports_no_catch_when_a_decoy_fires(self):
        """A finding against anything but the planted duplicate is a decoy firing."""
        from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep

        with TemporaryDirectory() as tmp:
            catalog = Path(tmp) / "data" / "catalog"
            catalog.mkdir(parents=True)
            for kind, entries in (
                ("families", [_family("H"), _family("H")]),
                ("outcomes", []),
                ("reqs", []),
                ("externals", []),
            ):
                text = json.dumps({"_doc": "Fixture catalog.", kind: entries})
                (catalog / f"{kind}.json").write_text(text, encoding="utf-8")
            caught = ep._ep_catalog(Path(tmp))
            (catalog / "reqs.json").write_text("{nope", encoding="utf-8")
            with_decoy_firing = ep._ep_catalog(Path(tmp))
        self.assertEqual([e.field for e in caught], ["families"])
        self.assertEqual(with_decoy_firing, [])


if __name__ == "__main__":
    unittest.main()
