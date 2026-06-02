"""Round-trip fidelity tests for AgentContract — OBPI-0.0.34-03."""

from __future__ import annotations

import unittest

from gzkit.content.models import AgentContract, Bullet
from gzkit.content.parse import parse
from gzkit.content.render import render
from gzkit.governance.invariants import ConstitutionalInvariant, reconcile_invariant
from gzkit.traceability import covers


class TestRoundTripAgentContract(unittest.TestCase):
    """Round-trip fidelity: parse(render(model)) == model and render is idempotent."""

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_minimal(self) -> None:
        """parse(render(model)) == model for minimal AgentContract."""
        model = AgentContract(name="Test", purpose="A purpose", tech_stack=[], rules=[])
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "AgentContract")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_with_data(self) -> None:
        """parse(render(model)) == model for AgentContract with all fields populated."""
        model = AgentContract(
            name="My Agent",
            purpose="Does useful things",
            tech_stack=["Python 3.13+", "uv"],
            rules=[
                Bullet(text="Rule one", indent=0),
                Bullet(text="Sub rule", indent=1),
            ],
        )
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "AgentContract")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_render_idempotency(self) -> None:
        """render(parse(render(model))) == render(model) — byte-stable."""
        model = AgentContract(
            name="My Agent",
            purpose="Does useful things",
            tech_stack=["Python 3.13+", "uv"],
            rules=[Bullet(text="Rule one", indent=0)],
        )
        once = render(model, "claude")
        parsed = parse(once.decode("utf-8"), "AgentContract")
        twice = render(parsed, "claude")
        self.assertEqual(once, twice)


class TestReconcileInvariant(unittest.TestCase):
    """REQ-0.0.37-11-04: reconcile_invariant maps ConstitutionalInvariant -> Bullet."""

    @covers("REQ-0.0.37-11-04")
    def test_reconcile_maps_claim_to_text(self) -> None:
        inv = ConstitutionalInvariant(
            id="CIC-1",
            claim="Every claim originates from the registry.",
            structural_witness=["gz validate --invariant-coherence"],
            composition_targets=["AGENTS.md"],
        )
        bullet = reconcile_invariant(inv)
        self.assertEqual(bullet.text, "Every claim originates from the registry.")

    @covers("REQ-0.0.37-11-04")
    def test_reconcile_maps_first_structural_witness_to_witness(self) -> None:
        inv = ConstitutionalInvariant(
            id="CIC-1",
            claim="x",
            structural_witness=["gz validate --first", "gz validate --second"],
            composition_targets=[],
        )
        bullet = reconcile_invariant(inv)
        self.assertEqual(bullet.witness, "gz validate --first")

    @covers("REQ-0.0.37-11-04")
    def test_reconcile_assigns_mechanical_classification(self) -> None:
        inv = ConstitutionalInvariant(
            id="CIC-1",
            claim="x",
            structural_witness=["gz validate --foo"],
            composition_targets=[],
        )
        bullet = reconcile_invariant(inv)
        self.assertEqual(bullet.classification, "Mechanical")

    @covers("REQ-0.0.37-11-04")
    def test_reconcile_assigns_lite_density_min(self) -> None:
        inv = ConstitutionalInvariant(
            id="CIC-1",
            claim="x",
            structural_witness=["gz validate --foo"],
            composition_targets=[],
        )
        bullet = reconcile_invariant(inv)
        self.assertEqual(bullet.density_min, "lite")

    @covers("REQ-0.0.37-11-04")
    def test_reconcile_bullet_round_trips_via_model_dump(self) -> None:
        inv = ConstitutionalInvariant(
            id="CIC-2",
            claim="Every OBPI brief reconciles against project shape.",
            structural_witness=["gz brief reconcile"],
            composition_targets=["AGENTS.md"],
        )
        bullet = reconcile_invariant(inv)
        rebuilt = Bullet(**bullet.model_dump())
        self.assertEqual(bullet, rebuilt)


class TestReverseParseRoundTrip(unittest.TestCase):
    """OBPI-0.0.37-13 REQ-04: model<->JSON is lossless; the prose render is a lossy human
    view that structurally round-trips (sections/bullets/text/order), NOT classification."""

    def _import_agents_md(self) -> AgentContract:
        from pathlib import Path  # noqa: PLC0415

        agents = Path(__file__).resolve().parents[2] / "AGENTS.md"
        return parse(agents.read_text(encoding="utf-8"), "AgentContract", file_path=str(agents))

    @covers("REQ-0.0.37-13-04")
    def test_model_json_round_trip_is_lossless(self) -> None:
        """The lossless source-of-truth round-trip is model <-> canonical JSON — every field,
        classification included, survives exactly."""
        model = self._import_agents_md()
        rebuilt = AgentContract.model_validate_json(model.model_dump_json())
        self.assertEqual(rebuilt, model)

    @covers("REQ-0.0.37-13-04")
    def test_prose_render_recovers_structure_not_classification(self) -> None:
        """parse(render(model)) recovers sections/bullets/text/order. The prose render is an
        explicitly lossy human view, so classification metadata is NOT asserted to survive it,
        and blank-line normalization is permitted."""
        model = self._import_agents_md()
        reparsed = parse(render(model, "claude").decode("utf-8"), "AgentContract")
        # Sections and order recovered.
        self.assertEqual([p.title for p in reparsed.pillars], [p.title for p in model.pillars])
        # Bullet text recovered, in order.
        self.assertEqual(
            [[b.text for b in p.bullets] for p in reparsed.pillars],
            [[b.text for b in p.bullets] for p in model.pillars],
        )

        # Section content (non-blank body lines) recovered, in order.
        def nonblank(pillar: object) -> list[str]:
            return [line for line in pillar.lines if line.strip()]

        self.assertEqual(
            [nonblank(p) for p in reparsed.pillars],
            [nonblank(p) for p in model.pillars],
        )


if __name__ == "__main__":
    unittest.main()
