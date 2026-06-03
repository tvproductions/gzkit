"""Tests for vendor-manifest expansion (OBPI-0.0.34-08).

Covers:
  REQ-0.0.34-08-01 — data/vendor-manifest.json validates against schema; --vendor-manifest exits 0
  REQ-0.0.34-08-02 — render pipeline reads content_type_routes; no hard-coded branches
  REQ-0.0.34-08-03 — missing content_type_routes entry fails closed naming the missing entry
  REQ-0.0.34-08-04 — (content_type, vendor) routes equal manifest's declared routes
  REQ-0.0.34-08-05 — schema-clean, manifest-drift fail-closed, route round-trip coverage

Also covers:
  REQ-0.0.37-15-01..06 — per-vendor temperature routing (TestPerVendorTemperatureRouting)
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.content import vendors
from gzkit.content.models import AgentContract, Bullet, Rule
from gzkit.content.render import TemplateNotFound, render
from gzkit.governance.trust_audits.vendor_manifest import validate_vendor_manifest
from gzkit.schemas import load_schema
from gzkit.traceability import covers

_DEFAULT_ROUTES: dict[str, list[str]] = {
    "AgentContract": ["claude", "codex"],
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


class TestPerVendorTemperatureRouting(unittest.TestCase):
    """Per-vendor temperature routing via manifest (OBPI-0.0.37-15).

    Covers:
      REQ-0.0.37-15-01 — vendors.py resolves per-vendor temperature from manifest
      REQ-0.0.37-15-02 — Codex resolves to lite; missing vendor fails closed
      REQ-0.0.37-15-03 — Codex lite mirror still contains every Judgment bullet
      REQ-0.0.37-15-04 — Codex and Claude AgentContract renders differ
      REQ-0.0.37-15-05 — per-vendor temperatures declared in data/vendor-manifest.json
      REQ-0.0.37-15-06 — additive content_type_temperatures sibling; schema constrains enum
    """

    @covers("REQ-0.0.37-15-01")
    def test_temperature_for_resolves_from_manifest(self) -> None:
        """temperature_for returns the temperature declared in manifest for the given vendor."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["claude", "codex"]},
                    "content_type_temperatures": {
                        "AgentContract": {"claude": "heavy", "codex": "lite"}
                    },
                },
            )
            result = vendors.temperature_for("AgentContract", "claude", project_root=root)
            self.assertEqual(result, "heavy")

    @covers("REQ-0.0.37-15-02")
    def test_codex_resolves_to_lite(self) -> None:
        """temperature_for resolves codex to 'lite' per manifest declaration."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["claude", "codex"]},
                    "content_type_temperatures": {
                        "AgentContract": {"claude": "heavy", "codex": "lite"}
                    },
                },
            )
            result = vendors.temperature_for("AgentContract", "codex", project_root=root)
            self.assertEqual(result, "lite")

    @covers("REQ-0.0.37-15-02")
    def test_missing_vendor_temperature_fails_closed(self) -> None:
        """temperature_for raises ValueError for a vendor not declared in manifest temperatures."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["claude"]},
                    "content_type_temperatures": {"AgentContract": {"claude": "heavy"}},
                },
            )
            with self.assertRaises(ValueError):
                vendors.temperature_for("AgentContract", "unknown_vendor", project_root=root)

    @covers("REQ-0.0.37-15-02")
    def test_temperature_for_no_manifest_fails_closed(self) -> None:
        """temperature_for fails closed with no in-code default when no manifest is present.

        Operator directive 2026-06-03: temperature is a general control, not a
        vendor-locked rule — there is no in-code (content_type, vendor) default,
        so resolution without a declaring manifest raises rather than returning
        a baked-in tier.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)  # no manifest written
            with self.assertRaises(ValueError):
                vendors.temperature_for("AgentContract", "codex", project_root=root)
        # And with no project_root at all (no manifest readable) — still fails closed.
        with self.assertRaises(ValueError):
            vendors.temperature_for("AgentContract", "codex")

    @covers("REQ-0.0.37-15-03")
    def test_codex_lite_contains_all_judgment_bullets(self) -> None:
        """Codex lite render includes Judgment bullets (0-Kelvin floor invariant)."""
        model = AgentContract(
            name="Test",
            purpose="Test contract",
            rules=[
                Bullet(text="judgment-bullet", classification="Judgment", density_min="lite"),
                Bullet(text="heavy-only-bullet", density_min="heavy"),
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["claude", "codex"]},
                    "content_type_temperatures": {
                        "AgentContract": {"codex": "lite", "claude": "heavy"}
                    },
                },
            )
            result = render(model, "codex", temperature="lite", project_root=root)
            self.assertIn(b"judgment-bullet", result)
            self.assertNotIn(b"heavy-only-bullet", result)

    @covers("REQ-0.0.37-15-04")
    def test_codex_and_claude_renders_differ(self) -> None:
        """Codex and Claude renders of the same AgentContract produce different bytes."""
        model = AgentContract(
            name="Test",
            purpose="Test contract",
            rules=[
                Bullet(text="judgment-bullet", classification="Judgment", density_min="lite"),
                Bullet(text="heavy-only-bullet", density_min="heavy"),
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["claude", "codex"]},
                    "content_type_temperatures": {
                        "AgentContract": {"codex": "lite", "claude": "heavy"}
                    },
                },
            )
            codex_result = render(model, "codex", temperature="lite", project_root=root)
            claude_result = render(model, "claude", temperature="heavy", project_root=root)
            self.assertNotEqual(codex_result, claude_result)

    @covers("REQ-0.0.37-15-05")
    def test_manifest_declares_temperatures(self) -> None:
        """Canonical data/vendor-manifest.json contains content_type_temperatures key."""
        project_root = Path(__file__).resolve().parents[2]
        manifest_path = project_root / "data" / "vendor-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertIn("content_type_temperatures", manifest)
        errors = validate_vendor_manifest(project_root)
        self.assertEqual(errors, [], f"Canonical manifest should validate clean, got: {errors}")

    @covers("REQ-0.0.37-15-06")
    def test_content_type_routes_shape_unchanged(self) -> None:
        """content_type_routes shape is preserved; content_type_temperatures is a sibling key."""
        project_root = Path(__file__).resolve().parents[2]
        manifest_path = project_root / "data" / "vendor-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        routes = manifest["content_type_routes"]
        self.assertIsInstance(routes, dict)
        for key, val in routes.items():
            with self.subTest(content_type=key):
                self.assertIsInstance(val, list)
                for item in val:
                    self.assertIsInstance(item, str)
        self.assertIn("content_type_temperatures", manifest)

    @covers("REQ-0.0.37-15-06")
    def test_schema_admits_valid_content_type_temperatures(self) -> None:
        """Manifest with content_type_temperatures using valid enum values validates clean.

        This test documents the RED→GREEN transition for schema expansion:
        today it fails because the schema rejects content_type_temperatures as an
        unknown top-level key (additionalProperties: false). After implementation,
        the schema admits the block and constrains temperature to {lite, medium, heavy}.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["claude", "codex"]},
                    "content_type_temperatures": {
                        "AgentContract": {"codex": "lite", "claude": "heavy"}
                    },
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertEqual(
                errors,
                [],
                f"Valid per-vendor temperatures should validate clean, got: {errors}",
            )

    @covers("REQ-0.0.37-15-06")
    def test_schema_rejects_out_of_enum_temperature(self) -> None:
        """Schema rejects a manifest with an out-of-enum temperature value."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["claude", "codex"]},
                    "content_type_temperatures": {"AgentContract": {"codex": "extra-hot"}},
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertTrue(
                errors,
                "Schema must reject an out-of-enum temperature value (REQ-0.0.37-15-06).",
            )


if __name__ == "__main__":
    unittest.main()
