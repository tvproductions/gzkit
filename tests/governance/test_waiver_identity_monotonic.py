"""GHI #1154 item 4 — a shrink-ratchet surface is monotonic in identity, not only in count.

A count ratchet cannot see a swap: drop one entry, add another, and nothing moved. Operator
ruling (GHI #1154, defaults taken 2026-10-01): a renamed or moved operation is new and fails
unless a reviewed authorization record names it. These tests derive from that ruling, drive the
real audit over planted trees, and weaken it the ways the swap could return.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

from gzkit.enforcement import production_enforcement_registry, run_meta_validator
from gzkit.governance.trust_audits import waiver_identity_claims as claims
from gzkit.governance.trust_audits import waiver_ratchet as gate
from gzkit.governance.trust_audits.waiver_identity_claims import (
    ADMIT_CLAIM_ID,
    REFUSE_CLAIM_ID,
    _record,
    new_identity_shape_population,
)
from gzkit.governance.trust_audits.waiver_ratchet import audit_waiver_ratchet
from gzkit.registries import load_registry, registry_path

_GATE = "gzkit.governance.trust_audits.waiver_ratchet:audit_waiver_ratchet"
_ROOT = Path(__file__).resolve().parents[2]
_REAL_IDENTITIES = gate._identities


def _outcomes() -> dict[str, str]:
    wanted = {REFUSE_CLAIM_ID, ADMIT_CLAIM_ID}
    records = [r for r in production_enforcement_registry() if r.claim_id in wanted]
    result = run_meta_validator(registry=records)
    return {r.claim_id: r.outcome for r in result.claim_results}


class TestTheLiveRegistryDeclaresIdentity(unittest.TestCase):
    def test_every_shrink_ratchet_surface_declares_how_an_entry_is_identified(self):
        registry = load_registry(_ROOT, "waiver_ratchet_registry.json")
        self.assertTrue(registry.get("identity_baseline"))
        for surface in registry["surfaces"]:
            if surface["mechanism"] == "shrink-ratchet":
                with self.subTest(surface["data_file"]):
                    self.assertIn(surface.get("identity", {}).get("kind"), gate._IDENTITY_KINDS)

    def test_the_live_surfaces_are_clean_so_the_baseline_holds_every_identity_they_carry(self):
        self.assertEqual(audit_waiver_ratchet(_ROOT), [])


class TestAnUnacceptedIdentityIsRefused(unittest.TestCase):
    def _audit(self, shape):
        with tempfile.TemporaryDirectory() as tmp:
            return claims._audit(audit_waiver_ratchet, Path(tmp), shape)

    def test_every_planted_shape_is_refused_for_identity_and_never_for_the_count(self):
        for name in new_identity_shape_population():
            with self.subTest(name):
                errors = self._audit(claims._REFUSED_SHAPES[name])
                self.assertTrue(any("never accepted" in e.message for e in errors), name)
                # The count ratchet is satisfied, so identity is the only thing that refused.
                self.assertFalse(any("grew to" in e.message for e in errors), name)

    def test_a_complete_record_authorizes_exactly_the_identity_it_names(self):
        spec, _, baseline_ids, _ = claims._REFUSED_SHAPES["string-swapped"]
        named = self._audit((spec, ["a", "c"], baseline_ids, [_record(identity="c")]))
        unnamed = self._audit((spec, ["a", "d"], baseline_ids, [_record(identity="c")]))
        self.assertEqual(named, [])
        self.assertTrue(any("never accepted" in e.message for e in unnamed))

    def test_an_authorization_is_not_a_license_for_growth(self):
        # The count ratchet still bounds the surface: a record cannot raise it.
        spec, _, baseline_ids, _ = claims._REFUSED_SHAPES["string-swapped"]
        grown = (spec, ["a", "b", "c"], baseline_ids, [_record(identity="c")])
        with tempfile.TemporaryDirectory() as tmp:
            errors = claims._audit(
                audit_waiver_ratchet, Path(tmp), grown, baseline_count=len(baseline_ids)
            )
        self.assertTrue(any("grew to" in e.message for e in errors))
        self.assertFalse(any("never accepted" in e.message for e in errors))


class TestIdentityIsReadPerKind(unittest.TestCase):
    """How each declared kind reads an entry, and when a kind cannot read its collection."""

    def test_keys_reads_the_object_keys(self):
        found = gate._identities({"a": 1, "b": 2}, {"kind": "keys"})
        self.assertEqual(found, Counter({"a": 1, "b": 1}))

    def test_strings_reads_each_string_and_counts_a_repeat(self):
        found = gate._identities(["a", "b", "b"], {"kind": "strings"})
        self.assertEqual(found, Counter({"a": 1, "b": 2}))

    def test_fields_joins_the_named_fields_and_ignores_the_rest(self):
        spec = {"kind": "fields", "fields": ["file", "name"]}
        moved_line = [{"file": "t.py", "name": "x", "line": 9}]
        same_op = [{"file": "t.py", "name": "x", "line": 1}]
        self.assertEqual(gate._identities(moved_line, spec), gate._identities(same_op, spec))
        self.assertEqual(gate._identities(same_op, spec), Counter({"t.py::x": 1}))

    def test_a_kind_that_cannot_read_its_collection_reads_nothing(self):
        unreadable = [
            ({"kind": "keys"}, ["not", "an", "object"]),
            ({"kind": "strings"}, {"an": "object"}),
            ({"kind": "strings"}, ["a", 1]),
            ({"kind": "fields", "fields": ["f"]}, {"an": "object"}),
            ({"kind": "fields", "fields": ["f"]}, ["not an object"]),
            ({"kind": "fields", "fields": ["f"]}, [{"other": 1}]),
            ({"kind": "fields"}, [{"f": 1}]),
            ({"kind": "fields", "fields": []}, [{"f": 1}]),
            ({"kind": "bogus"}, ["a"]),
        ]
        for spec, collection in unreadable:
            with self.subTest(spec=spec, collection=collection):
                self.assertIsNone(gate._identities(collection, spec))


class TestIdentityDeclarationIsHeldToAccount(unittest.TestCase):
    """A registry that opts in cannot be satisfied by an absent or unreadable declaration."""

    def _errors(self, spec, collection=("a",), baseline=None, authorizations=()):
        shape = (
            spec,
            list(collection),
            ["a"] if baseline is None else baseline,
            list(authorizations),
        )
        with tempfile.TemporaryDirectory() as tmp:
            return claims._audit(audit_waiver_ratchet, Path(tmp), shape)

    def test_a_surface_with_no_identity_declaration_is_refused(self):
        errors = self._errors(None)
        self.assertTrue(any("is not one of" in e.message for e in errors))

    def test_an_unknown_identity_kind_is_refused(self):
        errors = self._errors({"kind": "bogus"})
        self.assertTrue(any("is not one of" in e.message for e in errors))

    def test_count_only_with_a_reason_is_a_disclosure_and_passes(self):
        self.assertEqual(self._errors({"kind": "count-only", "reason": "no stable name"}), [])

    def test_count_only_without_a_reason_is_silence_and_is_refused(self):
        for spec in ({"kind": "count-only"}, {"kind": "count-only", "reason": "  "}):
            with self.subTest(spec=spec):
                errors = self._errors(spec)
                self.assertTrue(any("no 'reason'" in e.message for e in errors))

    def test_a_declaration_the_entries_do_not_fit_is_refused(self):
        errors = self._errors({"kind": "keys"})
        self.assertTrue(any("do not have that shape" in e.message for e in errors))

    def test_a_surface_the_baseline_never_recorded_is_refused(self):
        shape = ({"kind": "strings"}, ["a"], ["a"], [])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims._audit(audit_waiver_ratchet, root, shape)
            baseline_path = registry_path(root, "waiver_identity_baseline.json")
            baseline_path.write_text(
                json.dumps({"surfaces": {}, "authorizations": []}), encoding="utf-8"
            )
            errors = audit_waiver_ratchet(root)
        self.assertTrue(any("no identity baseline" in e.message for e in errors))

    def test_a_missing_identity_baseline_file_is_refused(self):
        shape = ({"kind": "strings"}, ["a"], ["a"], [])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims._audit(audit_waiver_ratchet, root, shape)
            registry_path(root, "waiver_identity_baseline.json").unlink()
            errors = audit_waiver_ratchet(root)
        self.assertTrue(any("missing or unparseable" in e.message for e in errors))

    def test_an_incomplete_record_is_named_as_not_reviewed_and_lacks_what_it_lacks(self):
        errors = self._errors({"kind": "strings"}, ["a", "c"], ["a", "b"], [claims._incomplete()])
        reviewed = [e.message for e in errors if "not reviewed" in e.message]
        self.assertEqual(len(reviewed), 1)
        self.assertIn("lacks reason", reviewed[0])

    def test_a_registry_that_does_not_opt_in_is_judged_on_count_alone(self):
        shape = ({"kind": "strings"}, ["a", "c"], ["a", "b"], [])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims._audit(audit_waiver_ratchet, root, shape)
            path = registry_path(root, "waiver_ratchet_registry.json")
            registry = json.loads(path.read_text(encoding="utf-8"))
            del registry["identity_baseline"]
            path.write_text(json.dumps(registry), encoding="utf-8")
            self.assertEqual(audit_waiver_ratchet(root), [])


class TestIdentityClaims(unittest.TestCase):
    def test_both_claims_name_the_audit_and_pass(self):
        records = {r.claim_id: r for r in production_enforcement_registry()}
        for claim_id in (REFUSE_CLAIM_ID, ADMIT_CLAIM_ID):
            self.assertIn(_GATE, records[claim_id].gate_targets)
        self.assertEqual(_outcomes(), {REFUSE_CLAIM_ID: "PASS", ADMIT_CLAIM_ID: "PASS"})


def _count_only(*_args, **_kwargs):
    """The pre-#1154 audit: identity is never read."""
    return []


def _ignores_the_surface_a_record_names(baseline, data_file):
    """An authorization lookup that honors any record, whichever surface it names."""
    records = baseline.get("authorizations", [])
    return Counter(str(r["identity"]) for r in records), []


def _accepts_incomplete_records(baseline, data_file):
    records = baseline.get("authorizations", [])
    return Counter(str(r["identity"]) for r in records if r.get("data_file") == data_file), []


def _set_not_multiset(collection, spec):
    found = _REAL_IDENTITIES(collection, spec)
    return None if found is None else Counter(set(found))


class TestControlsFailWhenTheAuditIsWeakened(unittest.TestCase):
    def test_a_count_only_audit_fails_the_refuse_control(self):
        with mock.patch.object(gate, "_check_identity", _count_only):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_honoring_a_record_for_another_surface_fails_the_refuse_control(self):
        with mock.patch.object(gate, "_authorized", _ignores_the_surface_a_record_names):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_accepting_an_incomplete_record_fails_the_refuse_control(self):
        with mock.patch.object(gate, "_authorized", _accepts_incomplete_records):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_reading_identity_as_a_set_fails_the_refuse_control(self):
        with mock.patch.object(gate, "_identities", _set_not_multiset):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_a_refuse_everything_audit_fails_the_admit_control(self):
        def refuses(*_args, **_kwargs):
            return [gate._err("x", "baseline never accepted")]

        with mock.patch.object(gate, "_check_identity", refuses):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")


if __name__ == "__main__":
    unittest.main()
