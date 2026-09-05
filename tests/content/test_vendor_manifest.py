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
    "AgentContract": ["root"],
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
                    "content_type_routes": {"AgentContract": ["root"], "Rule": ["claude"]},
                    "content_type_temperatures": {
                        "AgentContract": {"root": "lite"},
                        "Rule": {"claude": "heavy"},
                    },
                },
            )
            # The resolver is generic. Exercised across TWO content types so the
            # mechanism is proven without asserting AgentContract is per-vendor --
            # the root-contract ruling (2026-08-17) forbids a second AgentContract
            # route, and gz validate --vendor-manifest fail-closes on one.
            self.assertEqual(vendors.temperature_for("Rule", "claude", project_root=root), "heavy")
            self.assertEqual(
                vendors.temperature_for("AgentContract", "root", project_root=root), "lite"
            )

    @covers("REQ-0.0.37-15-02")
    def test_codex_resolves_to_lite(self) -> None:
        """temperature_for resolves codex to 'lite' per manifest declaration."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["root"]},
                    "content_type_temperatures": {"AgentContract": {"root": "lite"}},
                },
            )
            result = vendors.temperature_for("AgentContract", "root", project_root=root)
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
        """Codex lite render includes Judgment bullets. The density-projection filter was
        retired (OBPI-0.0.37-27); all bullets now render at every temperature, so the
        Judgment bullet appears regardless of routing temperature."""
        model = AgentContract(
            name="Test",
            purpose="Test contract",
            rules=[
                Bullet(text="judgment-bullet", classification="Judgment"),
                Bullet(text="plain-bullet"),
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["root"]},
                    "content_type_temperatures": {"AgentContract": {"root": "lite"}},
                },
            )
            result = render(model, "root", temperature="lite", project_root=root)
            self.assertIn(b"judgment-bullet", result)
            self.assertIn(b"plain-bullet", result)

    @covers("REQ-0.0.37-15-04")
    def test_temperature_no_longer_differentiates_a_vendor_render(self) -> None:
        """OBPI-15's per-vendor render selection-via-temperature RETIRES (ADR-0.0.37
        § Decision Re-Alignment: "15's per-vendor selection retires — per-vendor emission
        ruled out by the Codex-loader finding"). The differentiation was delivered solely by
        the temperature-projection filter; OBPI-0.0.37-27 proved it inert and removed it.

        This test pins ONLY what the retirement changed: for the routed consumer, the routed
        temperature no longer alters the bytes (lite render == heavy render).

        AMENDED 2026-08-17 (OBPI-0.35.0-09). This docstring previously reserved space for
        "the intended future where codex and claude are tuned to diverge." That future is
        FORECLOSED: `AgentContract` is the root contract, routed to exactly one consumer, and
        `gz validate --vendor-manifest` fail-closes on a second. The per-vendor `.j2` routing
        this note cited as leaving the door open turned out to be two BYTE-IDENTICAL 530 B
        templates, collapsed to `root.md.j2`. The assertion is unchanged and still correct;
        only the reason for its scope moved."""
        model = AgentContract(
            name="Test",
            purpose="Test contract",
            rules=[
                Bullet(text="judgment-bullet", classification="Judgment"),
                Bullet(text="plain-bullet"),
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["root"]},
                    "content_type_temperatures": {"AgentContract": {"root": "lite"}},
                },
            )
            root_lite = render(model, "root", temperature="lite", project_root=root)
            root_heavy = render(model, "root", temperature="heavy", project_root=root)
            self.assertEqual(
                root_lite,
                root_heavy,
                "Temperature-projection retired (OBPI-0.0.37-27): for a single vendor, the "
                "routed temperature must no longer alter the rendered bytes",
            )

    # REQ-0.0.37-15-05 is [SUPPORT] (OBPI-15 abandoned): its proof channel is
    # `gz validate --vendor-manifest` + an artifact_edited ledger event, NOT a
    # @covers test. This structural regression check stays but is not decorated —
    # decorating a SUPPORT REQ inflates the @covers census (GHI #703).
    def test_manifest_declares_temperatures(self) -> None:
        """Canonical data/vendor-manifest.json contains content_type_temperatures key."""
        project_root = Path(__file__).resolve().parents[2]
        manifest_path = project_root / "data" / "vendor-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertIn("content_type_temperatures", manifest)
        errors = validate_vendor_manifest(project_root)
        self.assertEqual(errors, [], f"Canonical manifest should validate clean, got: {errors}")

    # REQ-0.0.37-15-06 is [SUPPORT] (OBPI-15 abandoned): proven by
    # `gz validate --vendor-manifest` + a schema-file artifact_edited event, not
    # @covers. The schema admit/reject tests below exercise validate_vendor_manifest
    # (behavioral), undecorated (GHI #703). The former test_content_type_routes_shape
    # _unchanged was decommissioned — its assertIsInstance-on-static-data assertions
    # were a tautological echo of the JSON schema (enforced by the validator), adding
    # no behavioral proof.
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
                    "content_type_routes": {"AgentContract": ["root"]},
                    "content_type_temperatures": {"AgentContract": {"root": "lite"}},
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertEqual(
                errors,
                [],
                f"Valid per-vendor temperatures should validate clean, got: {errors}",
            )

    def test_schema_rejects_out_of_enum_temperature(self) -> None:
        """Schema rejects a manifest with an out-of-enum temperature value."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["root"]},
                    "content_type_temperatures": {"AgentContract": {"codex": "extra-hot"}},
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertTrue(
                errors,
                "Schema must reject an out-of-enum temperature value (REQ-0.0.37-15-06).",
            )


class TestAgentContractRootFence(unittest.TestCase):
    """REQ-0.35.0-09-08 / -09: AgentContract is the ROOT contract, routed to ``root``.

    ``AGENTS.md`` is the agent-harness default and the one root contract; the single
    rendition serves every harness. The doctrine is stated at
    ``docs/governance/agent-control-surface-rendering-substrate.md:211`` as
    ``gz content render agent_contract --vendor=root`` and carried an
    ``invariant``-tier corpus entry from 2026-08-17. It had no mechanical witness,
    which is how a per-consumer shape reached three surfaces and then a Heavy-lane
    brief. This class is that witness.
    """

    @covers("REQ-0.35.0-09-08")
    def test_multi_vendor_agent_contract_route_fails_closed(self) -> None:
        """More than one route for AgentContract must fail closed."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["root", "codex"], "Rule": ["claude"]},
                    "content_type_temperatures": {"AgentContract": {"root": "heavy"}},
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertTrue(
                any("root contract" in e.message for e in errors),
                f"A second AgentContract route must fail closed naming the doctrine: {errors}",
            )

    @covers("REQ-0.35.0-09-08")
    def test_multi_vendor_agent_contract_temperature_fails_closed(self) -> None:
        """More than one temperature for AgentContract must fail closed."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["root"]},
                    "content_type_temperatures": {
                        "AgentContract": {"root": "heavy", "codex": "lite"}
                    },
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertTrue(
                any("root contract" in e.message for e in errors),
                f"A second AgentContract temperature must fail closed: {errors}",
            )

    @covers("REQ-0.35.0-09-08")
    def test_single_vendor_specific_agent_contract_route_fails_closed(self) -> None:
        """ONE route is not the invariant — one route NAMED ``root`` is.

        REQ-0.35.0-09-08 ends "a second per-vendor ``AgentContract`` rendition
        cannot be declared, in JSON or in code". Declaring ``["codex"]`` declares
        exactly that, and a cardinality check cannot see it: it counts one route
        and passes. The two sibling tests above both mutate to TWO routes, so
        neither can separate "exactly one" from "exactly root" — the fence read
        green against a manifest that had re-vendored the root contract.

        Surfaced 2026-08-21 by the tier-1 Codex adversary (receipt
        ``arb-step-codexadversary-0bd5c04ee75c45a992052d9bfa9ad9f2``), which
        changed the manifest and ``_FALLBACK_ROUTES`` together to ``["codex"]``
        and observed all five fence tests stay green under a mutant that refutes
        the OBPI's whole objective.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["codex"], "Rule": ["claude"]},
                    "content_type_temperatures": {"AgentContract": {"codex": "lite"}},
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertTrue(
                any("root contract" in e.message for e in errors),
                "a single VENDOR-SPECIFIC AgentContract route re-vendors the root "
                f"contract and must fail closed naming the doctrine: {errors}",
            )

    @covers("REQ-0.35.0-09-08")
    def test_single_vendor_specific_agent_contract_temperature_fails_closed(self) -> None:
        """The temperature arm carries the same identity obligation as the route arm.

        A temperature keyed to a vendor names a compression setpoint chosen FOR
        that vendor, which is the per-vendor AgentContract the doctrine forbids —
        the count being one changes nothing about that.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["root"]},
                    "content_type_temperatures": {"AgentContract": {"codex": "lite"}},
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertTrue(
                any("root contract" in e.message for e in errors),
                "a vendor-keyed AgentContract temperature must fail closed even "
                f"when only one is declared: {errors}",
            )

    @covers("REQ-0.35.0-09-08")
    def test_routing_the_root_contract_obliges_declaring_its_setpoint(self) -> None:
        """Routing `AgentContract` without a temperature must fail closed.

        The two identity checks above are guards on OPTIONAL structures: each runs
        only once its key resolves to the expected type, so DELETING the key skips
        the guard entirely and the invariant degrades to "exactly root, if
        declared". Surfaced 2026-08-21 by the tier-1 Codex adversary (receipt
        ``arb-step-codexadversary-3da844475ab041a69f62249c42eb0113``).

        The route arm survives that omission because `_FALLBACK_ROUTES` is a second
        copy and the agreement check notices the absence. The temperature arm has no
        second copy — deliberately, by the operator directive noted in
        ``vendors.py`` — so omission is invisible there and ONLY there. That
        asymmetry is why this test binds the temperature to the route rather than
        demanding both unconditionally: a partial fixture that routes no root
        contract owes no setpoint, exactly as it owes no fallback agreement.

        An absent setpoint is not a cosmetic gap. This brief's requirement 7 makes
        the `lite` setpoint FALSIFIABLE; a rendition graded against no declared
        setpoint cannot be wrong, which is the unfalsifiable state the OBPI exists
        to end.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["root"], "Rule": ["claude"]},
                    "content_type_temperatures": {"Rule": {"claude": "heavy"}},
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertTrue(
                any("root contract" in e.message for e in errors),
                "routing the root contract with no declared temperature leaves the "
                f"setpoint unfalsifiable and must fail closed: {errors}",
            )

    @covers("REQ-0.35.0-09-08")
    def test_per_vendor_delivery_caps_remain_legal(self) -> None:
        """Caps stay per-vendor — a cap is an observed fact about someone else's product.

        The asymmetry is the point: a route and a temperature are controls gzkit
        chooses per content type, so a second one is a doctrine breach. A cap is
        the vendor's own knob — Codex's ``project_doc_max_bytes`` — and belongs
        to the vendor even where gzkit sets its value, which for Codex it does,
        in the ``.codex/config.toml`` it generates (GHI #962). The manifest
        records the value; the vendor owns the mechanism.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["root"]},
                    "content_type_temperatures": {"AgentContract": {"root": "heavy"}},
                    "content_type_delivery_caps": {
                        "AgentContract": {"codex": 32768, "claude": 200000}
                    },
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertEqual(errors, [], f"Multiple delivery caps must stay legal, got: {errors}")

    @covers("REQ-0.35.0-09-09")
    def test_fallback_table_must_agree_with_manifest(self) -> None:
        """The in-code fallback table is a second copy; divergence must fail closed.

        ``_FALLBACK_ROUTES`` is maintained by a comment ("Update both surfaces
        together"). That is the same two-copies-one-binds shape that let the root
        doctrine drift, one layer down — so it is witnessed rather than trusted.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # The check only binds a root that SHIPS the second copy. Materialize the
            # marker so this fixture is a source tree rather than a bare data dir.
            vendors_py = root / "src" / "gzkit" / "content" / "vendors.py"
            vendors_py.parent.mkdir(parents=True, exist_ok=True)
            vendors_py.write_text("# fixture marker\n", encoding="utf-8")
            diverged = {ct: list(vs) for ct, vs in vendors._FALLBACK_ROUTES.items()}
            diverged["Rule"] = ["copilot"]
            _write_manifest(
                root,
                {
                    "content_type_routes": diverged,
                    "content_type_temperatures": {"AgentContract": {"root": "heavy"}},
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertTrue(
                any("_FALLBACK_ROUTES" in e.message for e in errors),
                f"Fallback/manifest divergence must fail closed: {errors}",
            )

    @covers("REQ-0.35.0-09-09")
    def test_surface_content_types_must_agree_with_its_fallback(self) -> None:
        """The surface->content-type map is a SECOND COPY and must be witnessed too.

        ``surface_content_types`` was added 2026-08-21 to close GHI #840, and it
        arrived in exactly the shape REQ-0.35.0-09-09 exists to forbid: a manifest
        map plus an in-code mirror kept in agreement by a comment. The tier-1 Codex
        adversary named it the weakest point of the whole repair (receipt
        ``arb-step-codexadversary-76971da7d2c04b09a65f1b2eaacfc038``) — *"recreates
        the exact two-copies, comment-says-synchronize, nothing-binds failure class
        this OBPI is meant to eliminate."*

        The consequence is not cosmetic: a wrong map makes the floor gate grade
        ``claude`` and EXCLUDE ``root``, i.e. it grades the rendition nothing
        delivers and skips the one every harness reads.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vendors_py = root / "src" / "gzkit" / "content" / "vendors.py"
            vendors_py.parent.mkdir(parents=True, exist_ok=True)
            vendors_py.write_text("# fixture marker\n", encoding="utf-8")
            agreeing = {ct: list(v) for ct, v in vendors._FALLBACK_ROUTES.items()}
            _write_manifest(
                root,
                {
                    "content_type_routes": agreeing,
                    "content_type_temperatures": {"AgentContract": {"root": "heavy"}},
                    "surface_content_types": {"AGENTS.md": "Rule"},
                },
            )
            errors = validate_vendor_manifest(root)
            self.assertTrue(
                any("surface_content_types" in e.message for e in errors),
                f"a divergent surface_content_types map must fail closed: {errors}",
            )

    @covers("REQ-0.35.0-09-09")
    def test_blanking_the_route_map_entirely_fails_closed(self) -> None:
        """An EMPTY ``content_type_routes`` in a source tree is divergence, not absence.

        The agreement guard read ``routes and dict(routes) != ...``, so ``{}`` was
        falsy and skipped the comparison — blanking every route validated cleanly
        while ``_FALLBACK_ROUTES`` still declared eight. Found by the same adversary
        pass. A source tree that ships the second copy always has something to
        disagree with; only a fixture that ships no ``vendors.py`` is exempt, and
        that exemption is carried by ``owns_fallback``, not by emptiness.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vendors_py = root / "src" / "gzkit" / "content" / "vendors.py"
            vendors_py.parent.mkdir(parents=True, exist_ok=True)
            vendors_py.write_text("# fixture marker\n", encoding="utf-8")
            _write_manifest(root, {"content_type_routes": {}})
            errors = validate_vendor_manifest(root)
            self.assertTrue(
                any("_FALLBACK_ROUTES" in e.message for e in errors),
                f"blanking every route must fail closed in a source tree: {errors}",
            )

    @covers("REQ-0.35.0-09-09")
    def test_shipped_manifest_and_fallback_agree(self) -> None:
        """The real repo's two copies must agree — the regression this fence exists for."""
        project_root = Path(__file__).resolve().parents[2]
        self.assertEqual(
            vendors.all_routes(project_root=project_root),
            dict(vendors._FALLBACK_ROUTES),
            "data/vendor-manifest.json and _FALLBACK_ROUTES have diverged.",
        )


class TestBindingDeliveryCap(unittest.TestCase):
    """REQ-0.35.0-09-10 — one delivered surface is measured against the SMALLEST cap."""

    @covers("REQ-0.35.0-09-10")
    def test_the_smallest_declared_cap_binds_and_names_its_vendor(self) -> None:
        """The strictest declared cap binds, and the witness names who set it.

        `AgentContract` routes to a single `root` consumer, and no vendor named
        `root` publishes a `project_doc_max_bytes`. A per-route cap lookup
        therefore finds nothing and falls SILENT — losing the truncation witness
        at exactly the moment one shared surface makes it matter most. One file
        cannot be short for Codex and long for everyone else, so the smallest cap
        any harness declares is the one that binds.

        Naming the vendor is half the REQ and is asserted separately: a bare
        "over cap" warning does not tell an operator whose limit they crossed,
        and the caps are per-vendor precisely because they are observed facts
        about someone else's product rather than a control gzkit chooses.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["root"]},
                    "content_type_delivery_caps": {
                        "AgentContract": {"codex": 32768, "spacious": 1000000}
                    },
                },
            )

            binding = vendors.binding_delivery_cap("AgentContract", project_root=root)

            self.assertIsNotNone(binding, "a declared cap must be found for the routed surface")
            assert binding is not None
            cap, vendor = binding
            self.assertEqual(
                cap,
                32768,
                "the SMALLEST declared cap binds — a surface fitting the roomiest "
                "harness still truncates in the strictest one",
            )
            self.assertEqual(
                vendor,
                "codex",
                "the witness must name the vendor whose cap bound, so an operator "
                "knows which harness truncates rather than only that some cap exists",
            )

    @covers("REQ-0.35.0-09-10")
    def test_no_declared_cap_fails_open_rather_than_inventing_one(self) -> None:
        """An undeclared cap yields None — gzkit never invents a byte limit.

        Fail-open is deliberate and stated: an undeclared cap means gzkit knows of
        no limit, and fail-closing would force an agent to make up a number, which
        is the fabrication the delivery witness exists to prevent.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(root, {"content_type_routes": {"AgentContract": ["root"]}})

            self.assertIsNone(vendors.binding_delivery_cap("AgentContract", project_root=root))


if __name__ == "__main__":
    unittest.main()
