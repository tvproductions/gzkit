import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.ledger import Ledger
from gzkit.traceability import covers
from gzkit.validate_pkg.document import validate_document
from tests.commands.common import CliRunner, _quick_init


class TestPlanCommand(unittest.TestCase):
    """Tests for gz plan command.

    @covers REQ-0.0.17-02-01 (kind required)
    @covers REQ-0.0.17-02-02 (foundation semver gate)
    @covers REQ-0.0.17-02-03 (feature semver gate)
    @covers REQ-0.0.17-02-04 (pool routing + no kind field)
    @covers REQ-0.0.17-02-05 (kind after status in template)
    @covers REQ-0.0.17-02-06 (validate-before-write atomicity)
    @covers REQ-0.0.17-02-07 (foundation/feature directory routing)
    @covers REQ-0.0.17-02-08 (prior behavior preserved)
    """

    # --- REQ-0.0.17-02-01: --kind required ---

    def test_plan_create_requires_kind_flag(self) -> None:
        """@covers REQ-0.0.17-02-01 — omitting --kind exits 1 naming both foundation/feature."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["plan", "create", "scratch", "--semver", "0.1.0"])
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("foundation", result.output)
            self.assertIn("feature", result.output)

    # --- REQ-0.0.17-02-02: foundation requires 0.0.x semver ---

    def test_plan_create_foundation_rejects_non_0_0_x_semver(self) -> None:
        """@covers REQ-0.0.17-02-02 — foundation + non-0.0.x exits 1 with recovery."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "scratch",
                    "--kind",
                    "foundation",
                    "--semver",
                    "0.5.0",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("0.0.", result.output)
            foundation_root = Path("design/adr/foundation")
            self.assertFalse(
                foundation_root.exists() and any(foundation_root.rglob("*.md")),
                msg="foundation tree must remain untouched on rejection",
            )

    # --- REQ-0.0.17-02-03: feature rejects 0.0.x semver ---

    def test_plan_create_feature_rejects_0_0_x_semver(self) -> None:
        """@covers REQ-0.0.17-02-03 — feature + 0.0.x exits 1 with recovery."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "scratch",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.0.50",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("feature", result.output.lower())
            pre_release_root = Path("design/adr/pre-release")
            self.assertFalse(
                pre_release_root.exists() and any(pre_release_root.rglob("*.md")),
                msg="pre-release tree must remain untouched on rejection",
            )

    # --- REQ-0.0.17-02-04: pool routing + no kind field ---

    def test_plan_create_pool_routes_to_flat_pool_file_without_kind_field(self) -> None:
        """@covers REQ-0.0.17-02-04 — pool writes ADR-pool.<slug>.md flat, no kind: / no semver:."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                ["plan", "create", "experimental-thing", "--kind", "pool"],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_path = Path("design/adr/pool/ADR-pool.experimental-thing.md")
            self.assertTrue(adr_path.exists(), msg=f"expected {adr_path}")
            content = adr_path.read_text(encoding="utf-8")
            # Frontmatter block (between first two --- fences)
            frontmatter = content.split("---", 2)[1]
            self.assertNotIn("kind:", frontmatter, msg="pool ADRs must not carry kind:")
            self.assertNotIn("semver:", frontmatter, msg="pool ADRs must not carry semver:")
            self.assertIn("status: Pool", frontmatter)

    # --- REQ-0.0.17-02-05: template places kind after status ---

    def test_plan_create_foundation_template_places_kind_after_status(self) -> None:
        """@covers REQ-0.0.17-02-05 — rendered frontmatter: kind: immediately after status:."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "new-foundation",
                    "--kind",
                    "foundation",
                    "--semver",
                    "0.0.99",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_path = Path(
                "design/adr/foundation/ADR-0.0.99-new-foundation/ADR-0.0.99-new-foundation.md"
            )
            self.assertTrue(adr_path.exists(), msg=f"expected {adr_path}")
            content = adr_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            status_idx = next(i for i, line in enumerate(lines) if line.startswith("status:"))
            self.assertTrue(
                lines[status_idx + 1].startswith("kind:"),
                msg=f"expected kind: on line after status:, got: {lines[status_idx + 1]!r}",
            )
            self.assertIn("kind: foundation", lines[status_idx + 1])

    # --- REQ-0.0.17-02-06: validate-before-write atomicity ---

    def test_plan_create_rejection_writes_no_file_no_ledger_event(self) -> None:
        """@covers REQ-0.0.17-02-06 — rejection writes nothing anywhere (file nor ledger)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger_before = Ledger(Path(".gzkit/ledger.jsonl"))
            events_before = len(ledger_before.read_all())

            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "scratch",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.0.99",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)

            # No ADR markdown anywhere under design/adr
            adr_tree = list(Path("design/adr").rglob("*.md")) if Path("design/adr").exists() else []
            self.assertEqual(adr_tree, [], msg="no ADR files should have been written on rejection")

            # No new ledger events
            ledger_after = Ledger(Path(".gzkit/ledger.jsonl"))
            events_after = len(ledger_after.read_all())
            self.assertEqual(events_after, events_before, msg="no new ledger events on rejection")

    # --- REQ-0.0.17-02-07: foundation/feature per-ADR folder routing ---

    def test_plan_create_foundation_routes_to_foundation_dir_per_adr_folder(self) -> None:
        """@covers REQ-0.0.17-02-07 — foundation ADRs land at foundation/<id>/<id>.md."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "infra-thing",
                    "--kind",
                    "foundation",
                    "--semver",
                    "0.0.42",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_path = Path(
                "design/adr/foundation/ADR-0.0.42-infra-thing/ADR-0.0.42-infra-thing.md"
            )
            self.assertTrue(adr_path.exists(), msg=f"expected {adr_path}")

    def test_plan_create_feature_routes_to_pre_release_dir_per_adr_folder(self) -> None:
        """@covers REQ-0.0.17-02-07 — feature ADRs land at pre-release/<id>/<id>.md."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "new-feature",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.5.0",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_path = Path("design/adr/pre-release/ADR-0.5.0-new-feature/ADR-0.5.0-new-feature.md")
            self.assertTrue(adr_path.exists(), msg=f"expected {adr_path}")

    # --- REQ-0.0.17-02-08: prior behavior preserved (scorecard, ledger, canonicalization) ---

    def test_plan_creates_file_with_scorecard(self) -> None:
        """@covers REQ-0.0.17-02-08 — scorecard + checklist generation unchanged."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                ["plan", "create", "scorecard-feature", "--kind", "feature", "--semver", "0.1.0"],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_path = Path(
                "design/adr/pre-release/ADR-0.1.0-scorecard-feature/ADR-0.1.0-scorecard-feature.md"
            )
            self.assertTrue(adr_path.exists())
            content = adr_path.read_text(encoding="utf-8")
            self.assertIn("## Decomposition Scorecard", content)
            self.assertIn("- Final Target OBPI Count: 1", content)
            self.assertEqual(content.count("- [ ] OBPI-0.1.0-"), 1)

    def test_plan_registers_adr_in_ledger(self) -> None:
        """@covers REQ-0.0.17-02-08 — ledger registration path unchanged."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "my-feature",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.2.0",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            graph = ledger.get_artifact_graph()
            self.assertIn("ADR-0.2.0-my-feature", graph)
            self.assertEqual(graph["ADR-0.2.0-my-feature"]["type"], "adr")

    def test_plan_canonicalizes_short_form_adr_parent(self) -> None:
        """@covers REQ-0.0.17-02-08 (GHI #222) — parent canonicalization preserved."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            from gzkit.ledger import adr_created_event

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-0.3.0-parent-feature", "PRD-1", "lite"))

            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "child-feature",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.4.0",
                    "--obpi",
                    "ADR-0.3.0",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)

            fresh_ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            graph = fresh_ledger.get_artifact_graph()
            child = graph.get("ADR-0.4.0-child-feature")
            self.assertIsNotNone(child)
            self.assertEqual(child["parent"], "ADR-0.3.0-parent-feature")

            adr_path = Path(
                "design/adr/pre-release/ADR-0.4.0-child-feature/ADR-0.4.0-child-feature.md"
            )
            content = adr_path.read_text(encoding="utf-8")
            self.assertIn("parent: ADR-0.3.0-parent-feature", content)


class TestPlanCanonicalIdComposition(unittest.TestCase):
    """GHI #279 / #344 / #494 — gz plan create composes canonical slugged ADR ids.

    GHI #279 patched the instance for ADR-0.0.22; GHI #344 closes the class
    by rejecting bare-semver positional names at composition time so the
    bare ``adr_created`` event path no longer exists. GHI #494 closes the
    sibling hole: an ``ADR-`` prefixed bare-id positional name (``ADR-0.0.49``)
    bypassed the bare-semver gate and was returned verbatim, emitting a
    bare-id ``adr_created`` event. The scaffolder now rejects bare ``ADR-``
    ids at composition time and derives the emitted ``adr_created`` id from
    the on-disk directory slug-form rather than the intermediate id variable.
    The bridge in ``Ledger.has_adr_created`` remains for historical ledgers
    that already accumulated bare events before the path was closed.
    """

    def test_slug_name_produces_canonical_slugged_id(self) -> None:
        """A real slug in `name` produces ADR-<semver>-<slug> everywhere."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "agent-rule-placement-invariant",
                    "--kind",
                    "foundation",
                    "--semver",
                    "0.0.77",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)

            adr_id = "ADR-0.0.77-agent-rule-placement-invariant"
            adr_path = Path(f"design/adr/foundation/{adr_id}/{adr_id}.md")
            self.assertTrue(adr_path.exists(), msg=f"expected {adr_path}")

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            adr_events = [
                e for e in ledger.read_all() if e.event == "adr_created" and "0.0.77" in e.id
            ]
            self.assertEqual(len(adr_events), 1)
            self.assertEqual(adr_events[0].id, adr_id)

    def test_bare_semver_name_is_rejected(self) -> None:
        """GHI #344 — bare-semver positional name fails fast with no side effects.

        Closes the GHI #279 class of failure: prior contract accepted
        `gz plan create 0.0.22 --kind foundation --semver 0.0.22`, silently
        discarded the slug, and emitted a bare-ID `adr_created` event whose
        ledger row diverged from the slugged on-disk directory. The fix
        rejects bare-semver names at composition time. The CLI must:

        - Exit 1 (user/config error per `.claude/rules/cli.md`)
        - Name the operator-facing recovery in stderr/console output
        - Write no ADR file
        - Append no `adr_created` event to the ledger
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger_path = Path(".gzkit/ledger.jsonl")
            events_before = [e.id for e in Ledger(ledger_path).read_all()]

            result = runner.invoke(
                main,
                ["plan", "create", "0.0.22", "--kind", "foundation", "--semver", "0.0.22"],
            )

            self.assertEqual(result.exit_code, 1, msg=result.output)
            unwrapped = result.output.replace("\n", " ")
            self.assertIn("descriptive slug", unwrapped)
            self.assertIn("0.0.22", unwrapped)

            foundation_root = Path("design/adr/foundation")
            self.assertFalse(
                foundation_root.exists() and any(foundation_root.rglob("ADR-0.0.22*")),
                msg="no ADR directory may be scaffolded on rejection",
            )
            events_after = [e.id for e in Ledger(ledger_path).read_all()]
            self.assertEqual(
                events_after,
                events_before,
                msg="ledger must be untouched on bare-semver rejection",
            )

    def test_bare_adr_prefixed_name_is_rejected(self) -> None:
        """GHI #494 — bare ``ADR-X.Y.Z`` positional name fails fast, no side effects.

        Closes the regression-#4 sibling of the GHI #279 class: the prior
        contract returned an ``ADR-`` prefixed name verbatim, so
        ``gz plan create ADR-0.0.49 --kind foundation --semver 0.0.49``
        scaffolded ``foundation/ADR-0.0.49/`` and emitted a bare-id
        ``adr_created`` event that diverged from the canonical slug-form
        on-disk directory once renamed. A bare ``ADR-`` id carries no slug
        suffix and fails the schema ``id`` pattern (GHI #346). The CLI must:

        - Exit 1 (user/config error per ``.claude/rules/cli.md``)
        - Name the operator-facing recovery in console output
        - Write no ADR file
        - Append no ``adr_created`` event to the ledger
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger_path = Path(".gzkit/ledger.jsonl")
            events_before = [e.id for e in Ledger(ledger_path).read_all()]

            result = runner.invoke(
                main,
                ["plan", "create", "ADR-0.0.49", "--kind", "foundation", "--semver", "0.0.49"],
            )

            self.assertEqual(result.exit_code, 1, msg=result.output)
            unwrapped = result.output.replace("\n", " ")
            self.assertIn("slug", unwrapped)
            self.assertIn("ADR-0.0.49", unwrapped)

            foundation_root = Path("design/adr/foundation")
            self.assertFalse(
                foundation_root.exists() and any(foundation_root.rglob("ADR-0.0.49*")),
                msg="no ADR directory may be scaffolded on bare-ADR-id rejection",
            )
            events_after = [e.id for e in Ledger(ledger_path).read_all()]
            self.assertEqual(
                events_after,
                events_before,
                msg="ledger must be untouched on bare-ADR-id rejection",
            )

    def test_adr_created_id_derives_from_on_disk_directory(self) -> None:
        """GHI #494 — the emitted ``adr_created`` id equals the on-disk slug-form.

        The architectural class fix: the scaffolder derives the ledger event
        id (T2) from the canonical on-disk directory name (T1) rather than
        from a shared intermediate variable. This pins T1 == T2 structurally
        so a bare id can never reach the ledger while the directory is
        slug-form.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "emission-time-canonical-form",
                    "--kind",
                    "foundation",
                    "--semver",
                    "0.0.81",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)

            adr_id = "ADR-0.0.81-emission-time-canonical-form"
            adr_dir = Path(f"design/adr/foundation/{adr_id}")
            self.assertTrue(adr_dir.is_dir(), msg=f"expected directory {adr_dir}")

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            adr_events = [
                e for e in ledger.read_all() if e.event == "adr_created" and "0.0.81" in e.id
            ]
            self.assertEqual(len(adr_events), 1, msg=str([e.id for e in adr_events]))
            self.assertEqual(
                adr_events[0].id,
                adr_dir.name,
                msg="adr_created.id must equal the on-disk directory slug-form",
            )


class TestPlanIdempotentAdrCreated(unittest.TestCase):
    """GHI #279 — gz plan create emission is idempotent per canonical ADR id."""

    def test_duplicate_plan_create_emits_single_adr_created(self) -> None:
        """Re-running plan create for the same canonical id does not double-emit."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            args = [
                "plan",
                "create",
                "sample-feature",
                "--kind",
                "feature",
                "--semver",
                "0.6.0",
            ]
            first = runner.invoke(main, args)
            self.assertEqual(first.exit_code, 0, msg=first.output)

            second = runner.invoke(main, args)
            self.assertEqual(second.exit_code, 0, msg=second.output)
            self.assertIn("already has an adr_created event", second.output)

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            adr_events = [
                e for e in ledger.read_all() if e.event == "adr_created" and "0.6.0" in e.id
            ]
            observed_ids = [e.id for e in adr_events]
            self.assertEqual(
                len(adr_events),
                1,
                msg=f"expected one adr_created for the canonical id, got {observed_ids}",
            )


class TestPlanTaxonomyRoundtrip(unittest.TestCase):
    """OBPI-0.0.17-05 — scaffolder→validator round-trip for `gz plan create --kind`.

    Mirrors GHI #186 (PRD) and GHI #216 (constitution) precedents: invoke the
    scaffolder, assert it succeeds, then run the document validator with the
    `adr` schema (which loads the taxonomy audit) and assert zero errors.

    @covers REQ-0.0.17-05-05
    """

    def test_plan_create_foundation_kind_passes_taxonomy_validator(self) -> None:
        """@covers REQ-0.0.17-05-05 — foundation scaffolder output validates clean."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "round-trip-foundation",
                    "--kind",
                    "foundation",
                    "--semver",
                    "0.0.99",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            scaffolded = Path(
                "design/adr/foundation/ADR-0.0.99-round-trip-foundation/"
                "ADR-0.0.99-round-trip-foundation.md"
            )
            self.assertTrue(scaffolded.exists(), msg=f"missing {scaffolded}")
            errors = validate_document(scaffolded, "adr")
            self.assertEqual(
                [e.message for e in errors],
                [],
                msg="validator rejected freshly-scaffolded foundation ADR",
            )

    def test_plan_create_feature_kind_passes_taxonomy_validator(self) -> None:
        """@covers REQ-0.0.17-05-05 — feature scaffolder output validates clean."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "round-trip-feature",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.7.0",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            scaffolded = Path(
                "design/adr/pre-release/ADR-0.7.0-round-trip-feature/"
                "ADR-0.7.0-round-trip-feature.md"
            )
            self.assertTrue(scaffolded.exists(), msg=f"missing {scaffolded}")
            errors = validate_document(scaffolded, "adr")
            self.assertEqual(
                [e.message for e in errors],
                [],
                msg="validator rejected freshly-scaffolded feature ADR",
            )


class TestPlanCreateKindFoundation(unittest.TestCase):
    """OBPI-0.0.35-03 — `## Why foundation tier?` section convention.

    Foundation-kind ADRs scaffolded by `gz plan create --kind foundation`
    must carry the `## Why foundation tier?` heading between `## Persona`
    and `## Intent`, pre-populated with two author prompts (invariance-test
    answer + port-vs-plug framing). Feature-kind ADRs must not.

    @covers REQ-0.0.35-03-02 (foundation scaffolds the section)
    @covers REQ-0.0.35-03-03 (feature does NOT scaffold the section)
    @covers REQ-0.0.35-03-04 (two prompts present)
    @covers REQ-0.0.35-03-07 (RED-before / GREEN-after evidence)
    """

    @covers("REQ-0.0.35-03-01")
    @covers("REQ-0.0.35-03-02")
    @covers("REQ-0.0.35-03-04")
    @covers("REQ-0.0.35-03-07")
    def test_foundation_adr_scaffolds_why_foundation_tier_section(self) -> None:
        """Foundation scaffolding: exact heading, position, and two prompts."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "why-foundation-tier-scaffold",
                    "--kind",
                    "foundation",
                    "--semver",
                    "0.0.99",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_path = Path(
                "design/adr/foundation/"
                "ADR-0.0.99-why-foundation-tier-scaffold/"
                "ADR-0.0.99-why-foundation-tier-scaffold.md"
            )
            self.assertTrue(adr_path.exists(), msg=f"expected {adr_path}")
            content = adr_path.read_text(encoding="utf-8")

            # REQ-0.0.35-03-02 — section heading present, byte-identical
            self.assertIn(
                "## Why foundation tier?",
                content,
                msg="foundation ADR must scaffold `## Why foundation tier?` heading",
            )

            # REQ-0.0.35-03-09 (positioning) — heading sits between Persona and Intent
            persona_idx = content.index("## Persona")
            why_idx = content.index("## Why foundation tier?")
            intent_idx = content.index("## Intent")
            self.assertLess(
                persona_idx,
                why_idx,
                msg="`## Why foundation tier?` must appear after `## Persona`",
            )
            self.assertLess(
                why_idx,
                intent_idx,
                msg="`## Why foundation tier?` must appear before `## Intent`",
            )

            # REQ-0.0.35-03-04 — two prompts present (invariance-test + port-vs-plug)
            # Section body extracted between its heading and the next H2.
            section_body = content[why_idx:intent_idx]
            self.assertIn(
                "invariance test",
                section_body.lower(),
                msg="section must include invariance-test answer prompt",
            )
            self.assertIn(
                "port",
                section_body.lower(),
                msg="section must include port-vs-plug framing prompt",
            )
            self.assertIn(
                "plug",
                section_body.lower(),
                msg="section must include port-vs-plug framing prompt",
            )

    @covers("REQ-0.0.35-03-03")
    def test_feature_adr_does_not_scaffold_why_foundation_tier_section(self) -> None:
        """Feature-kind ADRs MUST NOT carry the section."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "no-foundation-tier-here",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.99.0",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_path = Path(
                "design/adr/pre-release/"
                "ADR-0.99.0-no-foundation-tier-here/"
                "ADR-0.99.0-no-foundation-tier-here.md"
            )
            self.assertTrue(adr_path.exists(), msg=f"expected {adr_path}")
            content = adr_path.read_text(encoding="utf-8")
            self.assertNotIn(
                "## Why foundation tier?",
                content,
                msg="feature ADR must NOT scaffold `## Why foundation tier?` heading",
            )

    @covers("REQ-0.0.35-03-05")
    def test_concept_page_documents_why_foundation_tier_convention(self) -> None:
        """Concept page must have a convention section."""
        from pathlib import Path as _Path

        concept_path = _Path("docs/user/concepts/foundation-feature-invariance-test.md")
        self.assertTrue(concept_path.exists(), msg=f"concept page missing: {concept_path}")
        content = concept_path.read_text(encoding="utf-8")
        self.assertIn(
            "## Why foundation tier? (the convention)",
            content,
            msg="concept page must contain the Why-foundation-tier convention section",
        )
        self.assertIn(
            "## Why foundation tier?",
            content,
            msg="concept page must name the exact heading within the convention section",
        )

    @covers("REQ-0.0.35-03-06")
    def test_runbook_cross_references_why_foundation_tier_convention(self) -> None:
        """Runbook must cross-reference the convention."""
        from pathlib import Path as _Path

        runbook_path = _Path("docs/user/runbook.md")
        self.assertTrue(runbook_path.exists(), msg=f"runbook missing: {runbook_path}")
        content = runbook_path.read_text(encoding="utf-8")
        self.assertIn(
            "Why foundation tier?",
            content,
            msg="runbook must cross-reference the `## Why foundation tier?` convention",
        )
