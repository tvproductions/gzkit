"""Tests for vendor-manifest expansion (OBPI-0.0.34-08).

Covers:
  REQ-0.0.34-08-01 — data/vendor-manifest.json validates against schema; --vendor-manifest exits 0
  REQ-0.0.34-08-02 — render pipeline reads content_type_routes; no hard-coded branches
  REQ-0.0.34-08-03 — missing content_type_routes entry fails closed naming the missing entry
  REQ-0.0.34-08-04 — (content_type, vendor) routes equal manifest's declared routes
  REQ-0.0.34-08-05 — schema-clean, manifest-drift fail-closed, route round-trip coverage
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.content import vendors
from gzkit.content.models import Rule
from gzkit.content.render import TemplateNotFound, render
from gzkit.governance.trust_audits.vendor_manifest import validate_vendor_manifest
from gzkit.schemas import load_schema
from gzkit.traceability import covers

_DEFAULT_ROUTES: dict[str, list[str]] = {
    "AgentContract": ["claude"],
    "Bullet": ["claude"],
    "Chore": ["claude"],
    "Handoff": ["claude"],
    "Persona": ["claude"],
    "Rule": ["claude"],
    "Scenario": ["claude"],
    "Skill": ["claude"],
}


def _write_manifest(root: Path, payload: dict[str, object]) -> Path:
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    manifest = data_dir / "vendor-manifest.json"
    manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return manifest


class TestVendorManifestSchema(unittest.TestCase):
    """REQ-0.0.34-08-01 / -05: schema-clean validation."""

    @covers("REQ-0.0.34-08-01")
    @covers("REQ-0.0.34-08-05")  # audit-exempt: regression-invariant-overlay REQ-05 structural
    def test_canonical_manifest_validates_clean(self) -> None:
        """data/vendor-manifest.json must validate against the bundled schema."""
        project_root = Path(__file__).resolve().parents[2]
        errors = validate_vendor_manifest(project_root)
        self.assertEqual(errors, [], f"Vendor manifest should validate clean, got: {errors}")

    @covers("REQ-0.0.34-08-01")
    def test_schema_loads_and_declares_required_key(self) -> None:
        """Vendor-manifest schema must require content_type_routes."""
        schema = load_schema("vendor_manifest")
        self.assertIn("content_type_routes", schema.get("required", []))
        self.assertEqual(schema.get("additionalProperties"), False)


class TestVendorManifestDrift(unittest.TestCase):
    """REQ-0.0.34-08-03 / -05: manifest-drift fail-closed."""

    @covers("REQ-0.0.34-08-03")
    def test_missing_manifest_file_fails_closed(self) -> None:
        """Missing data/vendor-manifest.json must produce a fail-closed error."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            errors = validate_vendor_manifest(root)
            self.assertTrue(errors, "Missing manifest should produce errors")
            self.assertTrue(
                any("vendor-manifest.json" in e.message for e in errors),
                f"Error message should reference the manifest file: {errors}",
            )

    @covers("REQ-0.0.34-08-03")
    def test_missing_content_type_routes_key_fails_closed(self) -> None:
        """A manifest missing content_type_routes must name the missing entry."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(root, {})
            errors = validate_vendor_manifest(root)
            self.assertTrue(errors, "Missing content_type_routes should produce errors")
            self.assertTrue(
                any("content_type_routes" in e.message for e in errors),
                f"Error should name the missing key: {errors}",
            )

    @covers("REQ-0.0.34-08-03")
    def test_manifest_with_additional_properties_fails_closed(self) -> None:
        """Schema rejects unknown top-level keys (additionalProperties: false)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["claude"]},
                    "unexpected_key": "rejected",
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertTrue(errors, "Unknown top-level key should produce schema errors")


class TestVendorRoutingRoundTrip(unittest.TestCase):
    """REQ-0.0.34-08-04 / -05: route enumeration round-trip."""

    @covers("REQ-0.0.34-08-04")
    def test_all_routes_round_trip_with_project_root(self) -> None:
        """vendors.all_routes(project_root=...) returns manifest's declared map."""
        project_root = Path(__file__).resolve().parents[2]
        loaded = vendors.all_routes(project_root=project_root)
        self.assertEqual(loaded, _DEFAULT_ROUTES)

    @covers("REQ-0.0.34-08-04")
    def test_routes_for_returns_vendors(self) -> None:
        """vendors.routes_for(content_type) returns the registered mirrors."""
        project_root = Path(__file__).resolve().parents[2]
        for ct, expected in _DEFAULT_ROUTES.items():
            with self.subTest(content_type=ct):
                self.assertEqual(vendors.routes_for(ct, project_root=project_root), expected)

    @covers("REQ-0.0.34-08-04")
    def test_routes_for_unknown_content_type_returns_empty(self) -> None:
        """Unknown content type returns an empty list (fail-closed at caller)."""
        project_root = Path(__file__).resolve().parents[2]
        self.assertEqual(vendors.routes_for("__nonexistent_ct__", project_root=project_root), [])

    @covers("REQ-0.0.34-08-04")
    def test_fallback_routes_match_canonical_manifest(self) -> None:
        """In-code fallback (no project_root) mirrors the canonical manifest."""
        # No project_root → uses _FALLBACK_ROUTES; must equal canonical manifest.
        for ct, expected in _DEFAULT_ROUTES.items():
            with self.subTest(content_type=ct):
                self.assertEqual(vendors.routes_for(ct), expected)


class TestRenderPipelineManifestIntegration(unittest.TestCase):
    """REQ-0.0.34-08-02: render pipeline reads manifest, no hard-coded branches."""

    @covers("REQ-0.0.34-08-02")
    def test_render_rejects_unknown_vendor_via_manifest(self) -> None:
        """render() must raise TemplateNotFound when vendor not in manifest routes."""
        rule = Rule(title="Test Rule", version="1.0.0", paths=[], body=[])
        with self.assertRaises(TemplateNotFound):
            render(rule, vendor="__nonexistent_vendor__")

    @covers("REQ-0.0.34-08-02")
    def test_render_accepts_manifest_declared_vendor(self) -> None:
        """render() succeeds for (content_type, vendor) pairs in the manifest."""
        rule = Rule(title="Manifest Routing Test", version="1.0.0", paths=[], body=[])
        result = render(rule, vendor="claude")
        self.assertIsInstance(result, bytes)
        self.assertIn(b"Manifest Routing Test", result)


if __name__ == "__main__":
    unittest.main()
