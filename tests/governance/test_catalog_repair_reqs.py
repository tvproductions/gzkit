"""The repair requirement beside the catalog requirement: RP-12 O2 task 2.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings and
`docs/governance/ieee/requirements-model.md` § 12: one base requirement carries
statement, criteria, kind, revision and `supersedes`; the catalog requirement
keeps `member_of`, `derives_from` and `applies_to`; the repair requirement names
its package in `held_on`, its problem report, and may name a design REQ it aligns
to (ruling 45). Both live in `data/catalog/reqs.json`, one `REQ-<n>` sequence.
"""

import unittest

from pydantic import TypeAdapter
from pydantic import ValidationError as PydanticValidationError

from gzkit.governance.trust_audits.catalog import audit_catalog
from gzkit.models.catalog import CatalogReq, RepairReq, Req, load_catalog
from tests.governance.test_catalog import _req, _Tree, _wp

_REQ = TypeAdapter(Req)


def _repair_req(req_id: str, held_on: str = "WP-01-x", **fields: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": req_id,
        "specialization": "repair",
        "held_on": held_on,
        "problem_report": 1183,
        "aligns_to": None,
        "supersedes": None,
        "statement": "The stamp generator is importable by its public name.",
        "criteria": [
            {
                "state_or_input": "the hook module is generated",
                "required_outcome": "it imports a public name",
                "evidence": "the import ratchet test",
            }
        ],
        "kind": "BEHAVIOR",
        "revision": 1,
    }
    return {**base, **fields}


class TestSpecializations(unittest.TestCase):
    """Ruling 45: each REQ is marked as one specialization, and carries only its fields."""

    def test_the_mark_selects_the_specialization(self):
        self.assertIsInstance(_REQ.validate_python(_req("REQ-1")), CatalogReq)
        self.assertIsInstance(_REQ.validate_python(_repair_req("REQ-2")), RepairReq)

    def test_a_req_without_its_mark_is_refused(self):
        unmarked = {key: value for key, value in _req("REQ-1").items() if key != "specialization"}
        with self.assertRaises(PydanticValidationError):
            _REQ.validate_python(unmarked)

    def test_a_repair_req_carries_no_catalog_field(self):
        for field, value in (("member_of", "H1"), ("derives_from", []), ("applies_to", [])):
            with self.subTest(field=field), self.assertRaises(PydanticValidationError):
                _REQ.validate_python({**_repair_req("REQ-2"), field: value})

    def test_a_catalog_req_carries_no_repair_field(self):
        for field, value in (("held_on", "WP-01-x"), ("problem_report", 1183)):
            with self.subTest(field=field), self.assertRaises(PydanticValidationError):
                _REQ.validate_python({**_req("REQ-1"), field: value})

    def test_either_kind_of_proof_channel_serves_a_repair(self):
        """A docs issue gains an honest SUPPORT kind (the R&D run's decision)."""
        for kind in ("BEHAVIOR", "SUPPORT", "STRUCTURAL-FENCE"):
            with self.subTest(kind=kind):
                self.assertEqual(_REQ.validate_python(_repair_req("REQ-2", kind=kind)).kind, kind)

    def test_supersedes_names_a_req_by_its_id(self):
        with self.assertRaises(PydanticValidationError):
            _REQ.validate_python(_repair_req("REQ-2", supersedes="OBPI-0.1.0-01"))


class TestRepairReqStore(_Tree):
    """`gz validate --catalog` over the repair requirements in `data/catalog/reqs.json`."""

    def setUp(self) -> None:
        super().setUp()
        packages: list[object] = [
            _wp("WP-01-x"),
            _wp("WP-02-d", "delivery"),
            _wp("WP-03-y", issues=[7]),
        ]
        self.write("work_packages", packages)

    def test_a_repair_req_held_on_its_repair_package_passes(self):
        self.write("reqs", [_req("REQ-1"), _repair_req("REQ-2", aligns_to="REQ-1")])
        self.assertEqual(audit_catalog(self.root), [])
        catalog = load_catalog(self.root)
        self.assertEqual([req.id for req in catalog.catalog_reqs()], ["REQ-1"])

    def test_held_on_names_a_repair_package_the_catalog_holds(self):
        for held_on in ("WP-09-gone", "WP-02-d"):
            with self.subTest(held_on=held_on):
                self.write("reqs", [_req("REQ-1"), _repair_req("REQ-2", held_on)])
                self.assertEqual(self.fields(), ["reqs"])

    def test_the_problem_report_is_an_issue_its_package_carries(self):
        self.write("reqs", [_req("REQ-1"), _repair_req("REQ-2", problem_report=7)])
        errors = audit_catalog(self.root)
        self.assertEqual([e.field for e in errors], ["reqs"])
        self.assertIn("#7", errors[0].message)

    def test_aligns_to_names_a_catalog_req_the_store_holds(self):
        for aligns_to in ("REQ-9", "REQ-3"):
            with self.subTest(aligns_to=aligns_to):
                reqs: list[object] = [_req("REQ-1"), _repair_req("REQ-2", aligns_to=aligns_to)]
                reqs.append(_repair_req("REQ-3"))
                self.write("reqs", reqs)
                self.assertEqual(self.fields(), ["reqs"])

    def test_supersedes_names_another_req_the_store_holds(self):
        for supersedes in ("REQ-9", "REQ-2"):
            with self.subTest(supersedes=supersedes):
                self.write("reqs", [_req("REQ-1"), _repair_req("REQ-2", supersedes=supersedes)])
                self.assertEqual(self.fields(), ["reqs"])
        self.write("reqs", [_req("REQ-1"), _repair_req("REQ-2", supersedes="REQ-1")])
        self.assertEqual(audit_catalog(self.root), [])

    def test_one_sequence_across_both_specializations(self):
        self.write("reqs", [_req("REQ-1"), _repair_req("REQ-1")])
        self.assertEqual(self.fields(), ["reqs"])

    def test_the_catalog_edge_checks_read_catalog_reqs_only(self):
        """A repair REQ has no outcome, so `member_of` and `derives_from` never read it."""
        self.write("reqs", [_req("REQ-1"), _repair_req("REQ-2")])
        self.assertEqual(audit_catalog(self.root), [])


if __name__ == "__main__":
    unittest.main()
