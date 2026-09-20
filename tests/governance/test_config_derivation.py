"""The two axes `--config-registry` declares exhaustive but does not reach (GHI #1066).

Ownership is complete and is not retested here. These assert the fences added
beside it: a registry that records no authority for its values, and a policy
threshold hardcoded in a module body where `data/config_registry.json`'s
`data/*.json` scope cannot see it.

Both fences are SHRINK-ONLY ratchets that freeze a population without repairing
it. The tests assert the freezing semantics — what may enter, what may not, and
that a stale baseline entry is itself a finding — never that the frozen rows are
good.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.config_derivation import (
    audit_derivation,
    audit_direct_data_reach,
    audit_module_constants,
    policy_constants,
    records_derivation,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


class DerivationIsRecordedOrGrandfathered(unittest.TestCase):
    """A registry records its authority, or the shrink-only baseline names it."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "data").mkdir()
        self.addCleanup(self._tmp.cleanup)

    def _baseline(self, names: list[str]) -> None:
        # The baseline lives in data/ and is scanned like any other registry, so
        # it records its own authority. The committed one does the same; a fence
        # that exempted itself would be the first thing to drift.
        (self.root / "data" / "config_derivation_grandfather.json").write_text(
            json.dumps({"_doc": "Shrink-only baseline, GHI #1066.", "grandfathered": names}),
            encoding="utf-8",
        )

    def _registry(self, name: str, payload: dict) -> None:
        (self.root / "data" / name).write_text(json.dumps(payload), encoding="utf-8")

    def test_registry_citing_an_authority_passes(self) -> None:
        self._baseline([])
        self._registry("t.json", {"_doc": "Per ADR-0.0.22, the merge order.", "x": 1})
        self.assertEqual(audit_derivation(self.root, {}, self.root / "data"), [])

    def test_registry_with_no_provenance_is_refused(self) -> None:
        self._baseline([])
        self._registry("t.json", {"x": 1})
        errors = audit_derivation(self.root, {}, self.root / "data")
        self.assertEqual([e.artifact for e in errors], ["t.json"])

    def test_prose_that_cites_nothing_is_refused(self) -> None:
        """Documentation is not derivation — the distinction the fence exists to draw."""
        self._baseline([])
        self._registry("t.json", {"_doc": "Thresholds for the widget subsystem.", "x": 1})
        self.assertEqual(len(audit_derivation(self.root, {}, self.root / "data")), 1)

    def test_grandfathered_registry_is_permitted(self) -> None:
        self._baseline(["t.json"])
        self._registry("t.json", {"x": 1})
        self.assertEqual(audit_derivation(self.root, {}, self.root / "data"), [])

    def test_bare_array_is_satisfied_by_its_declaration(self) -> None:
        """Five registries are bare arrays and cannot carry a field at all.

        Refusing the declaration side would make them permanently unfixable, so
        either side satisfies the fence.
        """
        self._baseline([])
        (self.root / "data" / "t.json").write_text(json.dumps(["a", "b"]), encoding="utf-8")
        entries = {"t.json": {"derivation": "Set by operator ruling 2026-09-20."}}
        self.assertEqual(audit_derivation(self.root, entries, self.root / "data"), [])

    def test_bare_array_without_a_declared_derivation_is_refused(self) -> None:
        self._baseline([])
        (self.root / "data" / "t.json").write_text(json.dumps(["a"]), encoding="utf-8")
        self.assertEqual(len(audit_derivation(self.root, {}, self.root / "data")), 1)

    def test_baseline_naming_a_phantom_is_a_finding(self) -> None:
        """A stale entry inflates the count and hides a later addition under it."""
        self._baseline(["gone.json"])
        errors = audit_derivation(self.root, {}, self.root / "data")
        self.assertEqual([e.artifact for e in errors], ["gone.json"])

    def test_missing_baseline_fails_closed(self) -> None:
        """Without the baseline every unsourced registry would pass unobserved."""
        self._registry("t.json", {"x": 1})
        errors = audit_derivation(self.root, {}, self.root / "data")
        self.assertEqual(len(errors), 1)
        self.assertIn("missing or unparseable", errors[0].message)


class DerivationRecognition(unittest.TestCase):
    """What counts as recording an authority."""

    def test_a_docs_path_counts(self) -> None:
        self.assertTrue(records_derivation({"_doc": "See docs/governance/x.md"}, None))

    def test_an_adr_counts(self) -> None:
        self.assertTrue(records_derivation({"citation": "ADR-0.0.27 bands"}, None))

    def test_a_ghi_counts(self) -> None:
        self.assertTrue(records_derivation({"rationale": "Set under GHI #768"}, None))

    def test_an_operator_ruling_counts(self) -> None:
        self.assertTrue(records_derivation({"note": "operator ruling 2026-08-17"}, None))

    def test_a_schema_declaration_does_not_count(self) -> None:
        """`$schema` declares shape, never origin."""
        self.assertFalse(records_derivation({"$schema": "docs/x.md"}, None))


class ModuleConstantsAreRostered(unittest.TestCase):
    """A policy threshold in a module body is unreachable by the data/*.json gate."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "src" / "gzkit").mkdir(parents=True)
        (self.root / "data").mkdir()
        self.addCleanup(self._tmp.cleanup)

    def _module(self, body: str) -> None:
        (self.root / "src" / "gzkit" / "m.py").write_text(body, encoding="utf-8")

    def _roster(self, names: list[str]) -> None:
        (self.root / "data" / "module_constant_grandfather.json").write_text(
            json.dumps({"constants": names}), encoding="utf-8"
        )

    def test_new_policy_constant_is_refused(self) -> None:
        self._roster([])
        self._module("MAX_RETRIES = 5\n")
        errors = audit_module_constants(self.root)
        self.assertEqual([e.artifact for e in errors], ["src/gzkit/m.py::MAX_RETRIES"])

    def test_rostered_constant_is_permitted(self) -> None:
        self._roster(["src/gzkit/m.py::MAX_RETRIES"])
        self._module("MAX_RETRIES = 5\n")
        self.assertEqual(audit_module_constants(self.root), [])

    def test_non_policy_names_are_not_swept_in(self) -> None:
        """The name pattern bounds the population; an unrelated constant is not config."""
        self._roster([])
        self._module("GREETING = 3\nVERSION = 2\n")
        self.assertEqual(audit_module_constants(self.root), [])

    def test_booleans_are_not_thresholds(self) -> None:
        self._roster([])
        self._module("MAX_ENABLED = True\n")
        self.assertEqual(audit_module_constants(self.root), [])

    def test_non_module_level_constant_is_out_of_scope(self) -> None:
        """A threshold inside a function is not a declared setting."""
        self._roster([])
        self._module("def f():\n    MAX_RETRIES = 5\n    return MAX_RETRIES\n")
        self.assertEqual(audit_module_constants(self.root), [])

    def test_missing_roster_fails_closed(self) -> None:
        self._module("MAX_RETRIES = 5\n")
        errors = audit_module_constants(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing or unparseable", errors[0].message)


class LiveTreeIsFenced(unittest.TestCase):
    """The committed baselines match the tree they were cut from."""

    def test_the_live_tree_passes_both_fences(self) -> None:
        registry = json.loads(
            (REPO_ROOT / "data" / "config_registry.json").read_text(encoding="utf-8")
        )["registries"]
        entries = {k: v for k, v in registry.items() if isinstance(v, dict)}
        self.assertEqual(audit_derivation(REPO_ROOT, entries, REPO_ROOT / "data"), [])
        self.assertEqual(audit_module_constants(REPO_ROOT), [])

    def test_the_roster_has_no_stale_entries(self) -> None:
        """A roster entry for a constant that is gone lets a new one hide under it."""
        rostered = set(
            json.loads(
                (REPO_ROOT / "data" / "module_constant_grandfather.json").read_text(
                    encoding="utf-8"
                )
            )["constants"]
        )
        self.assertEqual(sorted(rostered - set(policy_constants(REPO_ROOT))), [])


class DirectDataReachIsRostered(unittest.TestCase):
    """A single read seam is single only while nothing routes around it (GHI #1067)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "data").mkdir()
        (self.root / "src" / "gzkit").mkdir(parents=True)
        self.addCleanup(self._tmp.cleanup)

    def _roster(self, modules: list[str]) -> None:
        (self.root / "data" / "direct_data_reach_grandfather.json").write_text(
            json.dumps({"_doc": "Fixture roster, GHI #1067.", "modules": modules}),
            encoding="utf-8",
        )

    def _module(self, name: str, body: str) -> str:
        (self.root / "src" / "gzkit" / name).write_text(body, encoding="utf-8")
        return f"src/gzkit/{name}"

    def test_new_direct_reach_is_refused(self) -> None:
        self._roster([])
        rel = self._module("m.py", 'P = "data/x.json"\n')
        self.assertEqual([e.artifact for e in audit_direct_data_reach(self.root)], [rel])

    def test_path_data_form_is_caught(self) -> None:
        """The first cut of the detector missed this form and under-rostered by 40%."""
        self._roster([])
        rel = self._module("m.py", 'from pathlib import Path\nP = Path("data") / "x.json"\n')
        self.assertEqual([e.artifact for e in audit_direct_data_reach(self.root)], [rel])

    def test_root_slash_data_form_is_caught(self) -> None:
        self._roster([])
        rel = self._module("m.py", 'def f(root):\n    return root / "data" / "x.json"\n')
        self.assertEqual([e.artifact for e in audit_direct_data_reach(self.root)], [rel])

    def test_rostered_module_is_permitted(self) -> None:
        rel = self._module("m.py", 'P = "data/x.json"\n')
        self._roster([rel])
        self.assertEqual(audit_direct_data_reach(self.root), [])

    def test_module_using_the_seam_is_not_flagged(self) -> None:
        self._roster([])
        self._module("m.py", "from gzkit.registries import load_registry\n")
        self.assertEqual(audit_direct_data_reach(self.root), [])

    def test_stale_roster_entry_is_a_finding(self) -> None:
        """A migrated module left on the roster lets a regression hide under it."""
        self._roster(["src/gzkit/gone.py"])
        self.assertEqual(
            [e.artifact for e in audit_direct_data_reach(self.root)], ["src/gzkit/gone.py"]
        )

    def test_missing_roster_fails_closed(self) -> None:
        self._module("m.py", 'P = "data/x.json"\n')
        errors = audit_direct_data_reach(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing or unparseable", errors[0].message)


if __name__ == "__main__":
    unittest.main()
