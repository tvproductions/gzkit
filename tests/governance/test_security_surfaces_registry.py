"""Registry-level tests for the security-surface registry (ADR-0.0.22, OBPI-0.0.22-02).

Covers REQ-0.0.22-02-01 (registry validates against schema), REQ-0.0.22-02-02
(all nine canonical categories present, each with at least one glob),
REQ-0.0.22-02-05 (match_globs returns category labels for intersecting globs),
REQ-0.0.22-02-06 (governance contract documented in sibling README citing
parent ADR), REQ-0.0.22-02-07 (bootstrap exception narrative present in README),
REQ-0.0.22-02-08 (scope discipline — no out-of-scope artifacts authored).

@covers REQ-0.0.22-02-01
@covers REQ-0.0.22-02-02
@covers REQ-0.0.22-02-05
@covers REQ-0.0.22-02-06
@covers REQ-0.0.22-02-07
@covers REQ-0.0.22-02-08
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema

from gzkit.models.security_surfaces import (
    CANONICAL_CATEGORIES,
    SecuritySurfaceEntry,
    load_registry,
    match_globs,
)
from gzkit.schemas import load_schema
from gzkit.traceability import covers  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "data" / "security_surfaces.json"
README_PATH = REPO_ROOT / "data" / "README-security-surfaces.md"


class TestSchemaIntegrity(unittest.TestCase):
    """REQ-0.0.22-02-01 (schema half): minimal fixture validates."""

    def test_schema_loads(self) -> None:
        schema = load_schema("security_surfaces")
        self.assertIn("$schema", schema)
        self.assertEqual(schema.get("type"), "array")

    def test_schema_accepts_valid_entry(self) -> None:
        schema = load_schema("security_surfaces")
        fixture = [
            {
                "category": "credential_handling",
                "globs": ["src/example/credentials.py"],
                "rationale": "credential helper",
            }
        ]
        jsonschema.validate(fixture, schema)

    def test_schema_rejects_unknown_category(self) -> None:
        schema = load_schema("security_surfaces")
        fixture = [
            {
                "category": "cosmic_radiation",
                "globs": ["src/x.py"],
                "rationale": "x",
            }
        ]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(fixture, schema)

    def test_schema_rejects_extra_key(self) -> None:
        schema = load_schema("security_surfaces")
        fixture = [
            {
                "category": "credential_handling",
                "globs": ["src/x.py"],
                "rationale": "x",
                "severity": "high",
            }
        ]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(fixture, schema)

    def test_schema_rejects_empty_globs(self) -> None:
        schema = load_schema("security_surfaces")
        fixture = [
            {
                "category": "credential_handling",
                "globs": [],
                "rationale": "x",
            }
        ]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(fixture, schema)


class TestRegistryContents(unittest.TestCase):
    """REQ-0.0.22-02-01 (file half), REQ-0.0.22-02-02, REQ-0.0.22-02-06, REQ-0.0.22-02-07."""

    def test_registry_file_exists(self) -> None:
        self.assertTrue(REGISTRY_PATH.is_file(), f"missing {REGISTRY_PATH}")

    def test_registry_validates_against_schema(self) -> None:
        schema = load_schema("security_surfaces")
        raw = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        jsonschema.validate(raw, schema)

    def test_registry_loads_into_pydantic_model(self) -> None:
        entries = load_registry(REGISTRY_PATH)
        self.assertGreater(len(entries), 0)
        for entry in entries:
            self.assertIsInstance(entry, SecuritySurfaceEntry)

    def test_all_nine_canonical_categories_present(self) -> None:
        entries = load_registry(REGISTRY_PATH)
        present = {entry.category for entry in entries}
        self.assertEqual(present, set(CANONICAL_CATEGORIES))

    def test_each_category_has_at_least_one_glob(self) -> None:
        entries = load_registry(REGISTRY_PATH)
        by_category: dict[str, list[str]] = {}
        for entry in entries:
            by_category.setdefault(entry.category, []).extend(entry.globs)
        for category in CANONICAL_CATEGORIES:
            self.assertIn(category, by_category)
            self.assertGreaterEqual(len(by_category[category]), 1)

    def test_governance_readme_exists(self) -> None:
        self.assertTrue(README_PATH.is_file(), f"missing {README_PATH}")

    def test_governance_readme_documents_contract(self) -> None:
        body = README_PATH.read_text(encoding="utf-8")
        self.assertIn("ADR-0.0.22", body)
        self.assertIn("sensitivity: security", body)

    def test_governance_readme_records_bootstrap_exception(self) -> None:
        body = README_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("bootstrap", body)


class TestMatchGlobs(unittest.TestCase):
    """REQ-0.0.22-02-05: match_globs returns category labels for intersecting globs."""

    def test_no_intersection_returns_empty(self) -> None:
        registry = (
            SecuritySurfaceEntry(
                category="credential_handling",
                globs=("src/gzkit/auth/**/*.py",),
                rationale="r",
            ),
        )
        self.assertEqual(match_globs(("docs/**/*.md",), registry), ())

    def test_direct_match_returns_category(self) -> None:
        registry = (
            SecuritySurfaceEntry(
                category="arb_receipt_chain",
                globs=("src/gzkit/arb/**/*.py",),
                rationale="r",
            ),
        )
        self.assertEqual(
            match_globs(("src/gzkit/arb/validator.py",), registry),
            ("arb_receipt_chain",),
        )

    def test_glob_to_glob_intersection(self) -> None:
        registry = (
            SecuritySurfaceEntry(
                category="ledger_integrity",
                globs=("src/gzkit/ledger/**/*.py",),
                rationale="r",
            ),
        )
        self.assertEqual(
            match_globs(("src/gzkit/ledger/**/*.py",), registry),
            ("ledger_integrity",),
        )

    def test_two_categories_returned(self) -> None:
        registry = (
            SecuritySurfaceEntry(
                category="arb_receipt_chain",
                globs=("src/gzkit/arb/**/*.py",),
                rationale="r",
            ),
            SecuritySurfaceEntry(
                category="ledger_integrity",
                globs=("src/gzkit/ledger/**/*.py",),
                rationale="r",
            ),
        )
        result = match_globs(
            ("src/gzkit/arb/validator.py", "src/gzkit/ledger/store.py"),
            registry,
        )
        self.assertEqual(set(result), {"arb_receipt_chain", "ledger_integrity"})

    def test_real_registry_match(self) -> None:
        registry = load_registry(REGISTRY_PATH)
        result = match_globs(("src/gzkit/arb/validator.py",), registry)
        self.assertIn("arb_receipt_chain", result)


class TestScopeDiscipline(unittest.TestCase):
    """REQ-0.0.22-02-08: this OBPI does NOT author cross-OBPI surfaces."""

    def test_validate_sensitivity_scope_not_authored(self) -> None:
        # OBPI-03's responsibility, not this OBPI's.
        trust_audits = REPO_ROOT / "src" / "gzkit" / "governance" / "trust_audits.py"
        if trust_audits.is_file():
            self.assertNotIn(
                "validate_sensitivity_binding", trust_audits.read_text(encoding="utf-8")
            )

    def test_security_review_attestation_authored_at_named_path(self) -> None:
        # Forward-looking absence-guard converted to backward-looking
        # presence-witness when OBPI-0.0.22-04 landed: the function
        # exists at the path OBPI-04 was scoped to author at.
        adr_audit = REPO_ROOT / "src" / "gzkit" / "commands" / "adr_audit.py"
        self.assertTrue(adr_audit.is_file(), "adr_audit.py must exist")
        self.assertIn(
            "_requires_security_review_attestation",
            adr_audit.read_text(encoding="utf-8"),
        )

    def test_security_sensitivity_rule_authored_at_named_path(self) -> None:
        # Forward-looking absence-guard converted to backward-looking
        # presence-witness when OBPI-0.0.22-06 landed: the rule file
        # exists at the path OBPI-06 was scoped to author at.
        rule = REPO_ROOT / ".gzkit" / "rules" / "security-sensitivity.md"
        self.assertTrue(rule.is_file(), "OBPI-06 must author the rule file")
        body = rule.read_text(encoding="utf-8")
        self.assertIn(
            "data/security_surfaces.json",
            body,
            "rule file must cite the security-surface registry",
        )
        self.assertIn(
            "gz validate --sensitivity",
            body,
            "rule file must cite the validator scope",
        )


if __name__ == "__main__":
    unittest.main()
