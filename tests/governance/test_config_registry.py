"""Config-registry declaration gate (GHI #929).

The gate exists because `data/` accumulated 41 registries with no owner, no
loader, and no coherence gate, while the waiver/grandfather family already had
all three via `data/waiver_ratchet_registry.json`. These tests pin the four
arms that make the new registry a STATE check rather than a presence check —
the distinction AGENTS.md § DO IT RIGHT draws, and the one GHI #932 was filed
against elsewhere in this same audit package.
"""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.config_registry import audit_config_registry


def _root(registries: dict, data_files: list[str], modules: dict | None = None) -> Path:
    root = Path(tempfile.mkdtemp())
    (root / "data").mkdir()
    (root / "data" / "config_registry.json").write_text(
        json.dumps({"registries": registries}), encoding="utf-8"
    )
    for name in data_files:
        if name == "config_registry.json":
            continue  # already written above; do not clobber the registry itself
        (root / "data" / name).write_text("{}", encoding="utf-8")
    for rel, text in (modules or {}).items():
        p = root / "src" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


class ConfigRegistryExhaustiveness(unittest.TestCase):
    """Arm 1 — a registry on disk that is not declared is a silent bypass."""

    def test_undeclared_registry_fails_closed(self) -> None:
        root = _root(
            {"config_registry.json": {"owner": "m.py", "kind": "code"}},
            ["config_registry.json", "sneaky_thresholds.json"],
            {"m.py": "config_registry.json"},
        )
        errors = audit_config_registry(root)
        self.assertTrue(
            any("sneaky_thresholds.json" in e.message for e in errors),
            "an undeclared data registry must fail closed",
        )

    def test_waiver_family_is_not_claimed_by_this_gate(self) -> None:
        """The waiver globs belong to waiver_ratchet; double-owning them is drift."""
        root = _root(
            {"config_registry.json": {"owner": "m.py", "kind": "code"}},
            ["config_registry.json", "historical_self_close_waivers.json"],
            {"m.py": "config_registry.json"},
        )
        errors = audit_config_registry(root)
        self.assertEqual(
            [],
            [e for e in errors if "waivers.json" in e.message],
            "waiver-family files are owned by waiver_ratchet_registry, not this gate",
        )


class ConfigRegistryOwnerVerification(unittest.TestCase):
    """Arm 2/3 — the declared owner must actually consume the file."""

    def test_owner_that_does_not_reference_the_file_fails(self) -> None:
        root = _root(
            {
                "config_registry.json": {"owner": "m.py", "kind": "code"},
                "thing.json": {"owner": "liar.py", "kind": "code"},
            },
            ["config_registry.json", "thing.json"],
            {"m.py": "config_registry.json", "liar.py": "# reads nothing"},
        )
        errors = audit_config_registry(root)
        self.assertTrue(
            any("thing.json" in e.message and "liar.py" in e.message for e in errors),
            "an owner that never references its registry is an asserted, not verified, owner",
        )

    def test_declared_file_that_does_not_exist_fails(self) -> None:
        root = _root(
            {
                "config_registry.json": {"owner": "m.py", "kind": "code"},
                "phantom.json": {"owner": "m.py", "kind": "code"},
            },
            ["config_registry.json"],
            {"m.py": "config_registry.json phantom.json"},
        )
        errors = audit_config_registry(root)
        self.assertTrue(
            any("phantom.json" in e.message for e in errors),
            "a declared registry with no file on disk is a phantom declaration",
        )

    def test_missing_owner_module_fails(self) -> None:
        root = _root(
            {
                "config_registry.json": {"owner": "m.py", "kind": "code"},
                "thing.json": {"owner": "gone.py", "kind": "code"},
            },
            ["config_registry.json", "thing.json"],
            {"m.py": "config_registry.json"},
        )
        errors = audit_config_registry(root)
        self.assertTrue(
            any("gone.py" in e.message for e in errors),
            "an owner module that does not exist cannot be a verified consumer",
        )


class ConfigRegistryRelationSymmetry(unittest.TestCase):
    """Arm 4 — two registries encoding one concept must relate mechanically."""

    def test_asymmetric_relation_fails(self) -> None:
        root = _root(
            {
                "config_registry.json": {"owner": "m.py", "kind": "code"},
                "a.json": {"owner": "m.py", "kind": "code", "relates_to": ["b.json"]},
                "b.json": {"owner": "m.py", "kind": "code"},
            },
            ["config_registry.json", "a.json", "b.json"],
            {"m.py": "config_registry.json a.json b.json"},
        )
        errors = audit_config_registry(root)
        self.assertTrue(
            any("a.json" in e.message and "b.json" in e.message for e in errors),
            "a one-way relates_to leaves the sibling unaware; symmetry is the point",
        )

    def test_symmetric_relation_passes(self) -> None:
        root = _root(
            {
                "config_registry.json": {"owner": "m.py", "kind": "code"},
                "a.json": {"owner": "m.py", "kind": "code", "relates_to": ["b.json"]},
                "b.json": {"owner": "m.py", "kind": "code", "relates_to": ["a.json"]},
            },
            ["config_registry.json", "a.json", "b.json"],
            {"m.py": "config_registry.json a.json b.json"},
        )
        self.assertEqual([], audit_config_registry(root))


class ConfigRegistryAgainstLiveTree(unittest.TestCase):
    """The committed registry must actually hold against the real repository."""

    def test_live_repository_passes(self) -> None:
        root = Path(__file__).resolve().parents[2]
        errors = audit_config_registry(root)
        self.assertEqual([], errors, "committed config_registry.json must describe the live tree")


if __name__ == "__main__":
    unittest.main()
