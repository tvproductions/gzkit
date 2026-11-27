"""Tests closing the two foundation-kind authoring doors (ADR-0.34.0).

@covers REQ-0.34.0-02-01 (gz plan create --kind foundation rejected)
@covers REQ-0.34.0-02-02 (gz adr promote --kind foundation rejected)
@covers REQ-0.34.0-02-03 (grandfathered on-disk kind: foundation ADR still validates)
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.cli import main
from gzkit.commands.register import is_ungrandfathered_foundation
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event
from gzkit.traceability import covers
from gzkit.validate_pkg.document import validate_document
from tests.commands.common import CliRunner, _quick_init


class TestFoundationKindClosedAtAuthoringTime(unittest.TestCase):
    """Both `gz plan create --kind foundation` and `gz adr promote --kind
    foundation` are rejected at the command handler with three-part
    guardrail-feedback prose, while the schema enum / argparse choices keep
    `foundation` so grandfathered on-disk ADRs still validate.
    """

    @staticmethod
    def _seed_pool_adr(config: GzkitConfig, adr_id: str = "ADR-pool.sample-work") -> Path:
        pool_dir = Path(config.paths.adrs) / "pool"
        pool_dir.mkdir(parents=True, exist_ok=True)
        pool_file = pool_dir / f"{adr_id}.md"
        pool_file.write_text(
            "---\n"
            f"id: {adr_id}\n"
            "status: Pool\n"
            "parent: PRD-GZKIT-1.0.0\n"
            "lane: heavy\n"
            "---\n\n"
            f"# {adr_id}: Sample Work\n\n"
            "## Status\n\n"
            "Pool\n\n"
            "## Intent\n\n"
            "Turn sample pool work into executable tracked delivery.\n\n"
            "## Target Scope\n\n"
            "- Define runtime command contract\n\n"
            "## Non-Goals\n\n"
            "- No external orchestrator\n",
            encoding="utf-8",
        )
        return pool_file

    # --- REQ-0.34.0-02-01 ---

    @covers("REQ-0.34.0-02-01")
    def test_plan_create_foundation_kind_rejected_with_three_part_prose(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger_path = Path(".gzkit/ledger.jsonl")
            ledger_bytes_before = ledger_path.read_bytes()

            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "sunset-demo",
                    "--kind",
                    "foundation",
                    "--semver",
                    "0.0.99",
                ],
            )
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            # (a) what failed
            self.assertIn("--kind foundation", result.output)
            # (b) why forbidden
            self.assertIn("ADR-0.34.0", result.output)
            # (c) governed next step
            self.assertIn("--kind feature", result.output)
            self.assertIn("--kind pool", result.output)
            foundation_root = Path("design/adr/foundation")
            self.assertFalse(
                foundation_root.exists() and any(foundation_root.rglob("*.md")),
                msg="rejected --kind foundation must write no ADR file",
            )
            self.assertEqual(
                ledger_path.read_bytes(),
                ledger_bytes_before,
                msg="rejection must append no ledger event",
            )

    @covers("REQ-0.34.0-02-01")
    def test_plan_create_foundation_kind_rejected_before_semver_binding_check(self) -> None:
        """Closed-kind rejection fires even when --semver would also fail the
        foundation semver-binding check — ordering must not route the
        operator to the wrong error (brief's Critical guard-ordering clause).
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "sunset-demo",
                    "--kind",
                    "foundation",
                    "--semver",
                    "0.5.0",
                ],
            )
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("ADR-0.34.0", result.output)
            self.assertNotIn("requires --semver matching 0.0.x", result.output)

    # --- REQ-0.34.0-02-02 ---

    @covers("REQ-0.34.0-02-02")
    def test_adr_promote_foundation_kind_rejected_with_three_part_prose(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool_file = self._seed_pool_adr(config)
            ledger_path = Path(".gzkit/ledger.jsonl")
            ledger = Ledger(ledger_path)
            ledger.append(adr_created_event("ADR-pool.sample-work", "", "heavy"))

            # Byte-level pre-state: a rejection must mutate NOTHING. Asserting
            # only that the pool file still *exists* would pass even if the
            # command rewrote its contents or appended a ledger event first.
            pool_bytes_before = pool_file.read_bytes()
            ledger_bytes_before = ledger_path.read_bytes()

            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.0.99",
                    "--kind",
                    "foundation",
                ],
            )
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("--kind foundation", result.output)
            self.assertIn("ADR-0.34.0", result.output)
            self.assertIn("--kind feature", result.output)
            self.assertIn("--kind pool", result.output)
            self.assertEqual(
                pool_file.read_bytes(),
                pool_bytes_before,
                msg="rejection must leave the pool ADR byte-identical",
            )
            self.assertEqual(
                ledger_path.read_bytes(),
                ledger_bytes_before,
                msg="rejection must append no ledger event",
            )
            foundation_root = Path(config.paths.adrs) / "foundation"
            self.assertFalse(
                foundation_root.exists() and any(foundation_root.rglob("*.md")),
                msg="rejected --kind foundation must perform no promotion I/O",
            )

    @covers("REQ-0.34.0-02-02")
    def test_adr_promote_foundation_kind_rejected_before_semver_binding_check(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            self._seed_pool_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.sample-work", "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.5.0",
                    "--kind",
                    "foundation",
                ],
            )
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("ADR-0.34.0", result.output)
            self.assertNotIn("requires --semver matching 0.0.x", result.output)

    # --- REQ-0.34.0-02-03 ---

    # --- REQ-0.34.0-02-05: programmatic choke points ---

    @covers("REQ-0.34.0-02-05")
    def test_render_adr_by_kind_refuses_foundation(self) -> None:
        """The shared render/write path refuses the closed kind.

        Guarding only the command handlers is a per-instance fix that the next
        new caller reopens — `gz interview adr` was exactly that (REQ-04). The
        write path is the choke point, so it re-validates rather than trusting
        its callers.
        """
        from gzkit.commands.plan import _build_scorecard_and_checklist, _render_adr_by_kind

        with TemporaryDirectory() as tmp:
            scorecard, checklist_seed = _build_scorecard_and_checklist(
                lane="lite",
                semver="0.0.99",
                score_data_state=None,
                score_logic_engine=None,
                score_interface=None,
                score_observability=None,
                score_lineage=None,
                split_single_narrative=False,
                split_surface_boundary=False,
                split_state_anchor=False,
                split_testability_ceiling=False,
                baseline_selected=None,
            )
            with self.assertRaises(ValueError) as ctx:
                _render_adr_by_kind(
                    kind="foundation",
                    name="programmatic-door",
                    adr_title="Programmatic Door",
                    semver="0.0.99",
                    lane="lite",
                    canonical_parent="",
                    scorecard=scorecard,
                    checklist_seed=checklist_seed,
                    adrs_root=Path(tmp),
                )
            self.assertIn("ADR-0.34.0", str(ctx.exception))
            self.assertFalse(
                any(Path(tmp).rglob("*.md")),
                msg="refused render must write no ADR file",
            )

    @covers("REQ-0.34.0-02-05")
    def test_render_adr_by_kind_still_renders_feature(self) -> None:
        """Closure must not widen — the render path still serves feature kind."""
        from gzkit.commands.plan import _build_scorecard_and_checklist, _render_adr_by_kind

        with TemporaryDirectory() as tmp:
            scorecard, checklist_seed = _build_scorecard_and_checklist(
                lane="lite",
                semver="0.35.0",
                score_data_state=None,
                score_logic_engine=None,
                score_interface=None,
                score_observability=None,
                score_lineage=None,
                split_single_narrative=False,
                split_surface_boundary=False,
                split_state_anchor=False,
                split_testability_ceiling=False,
                baseline_selected=None,
            )
            _, adr_file = _render_adr_by_kind(
                kind="feature",
                name="feature-door",
                adr_title="Feature Door",
                semver="0.35.0",
                lane="lite",
                canonical_parent="",
                scorecard=scorecard,
                checklist_seed=checklist_seed,
                adrs_root=Path(tmp),
            )
            self.assertTrue(adr_file.is_file())
            self.assertIn("kind: feature", adr_file.read_text(encoding="utf-8"))

    @covers("REQ-0.34.0-02-05")
    def test_build_adr_promotion_plan_refuses_foundation(self) -> None:
        """The promotion-plan builder re-validates instead of trusting its caller.

        `_build_adr_promotion_plan` -> `_apply_adr_promotion` schedules the ADR,
        OBPI, pool and ledger writes. Validation living only in the CLI caller
        left this path able to construct a foundation package (found by Step-4b
        adversarial re-validation).
        """
        from gzkit.commands.adr_promote import _build_adr_promotion_plan
        from gzkit.commands.common import GzCliError

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool_file = self._seed_pool_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))

            with self.assertRaises(GzCliError) as ctx:
                _build_adr_promotion_plan(
                    Path(),
                    config,
                    ledger,
                    pool_file,
                    "ADR-pool.sample-work",
                    pool_metadata={},
                    pool_content=pool_file.read_text(encoding="utf-8"),
                    semver="0.0.99",
                    slug=None,
                    title=None,
                    parent=None,
                    lane="heavy",
                    kind="foundation",
                    target_status="proposed",
                )
            self.assertIn("ADR-0.34.0", str(ctx.exception))

    # --- REQ-0.34.0-02-04 ---

    @covers("REQ-0.34.0-02-04")
    def test_interview_adr_foundation_semver_rejected_with_three_part_prose(self) -> None:
        """`gz interview adr` is the third authoring door and must be closed too.

        `interview_cmd._resolve_adr_doc` derives `kind: foundation` from a
        `0.0.x` semver embedded in the canonical id, with its own routing that
        never reaches `plan.py`. Guarding `plan create` / `adr promote` alone
        leaves this door open (found by Step-4b adversarial validation).
        """
        import json as _json

        from gzkit.ledger import Ledger

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger_path = Path(".gzkit/ledger.jsonl")
            events_before = [e.id for e in Ledger(ledger_path).read_all()]

            answers = {
                "id": "ADR-0.0.999-interview-foundation-door",
                "semver": "0.0.999",
                "title": "Interview Foundation Door",
                "lane": "lite",
                "parent": "PRD-GZKIT-1.0.0",
                "intent": "Prove the interview door is closed.",
                "decision": "Reject foundation authoring.",
                "positive_consequences": "1. Closure has no bypass",
                "negative_consequences": "1. None",
                "checklist": "1. Close the door",
                "alternatives": "Leave it open: rejected.",
            }
            Path("answers.json").write_text(_json.dumps(answers), encoding="utf-8")

            result = runner.invoke(main, ["interview", "adr", "--from", "answers.json"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            unwrapped = result.output.replace("\n", " ")
            # (a) what failed / (b) why forbidden / (c) governed next step
            self.assertIn("foundation", unwrapped)
            self.assertIn("ADR-0.34.0", unwrapped)
            self.assertIn("--kind feature", unwrapped)
            self.assertIn("--kind pool", unwrapped)

            adrs_root = Path("design/adr")
            self.assertFalse(
                adrs_root.exists() and any(adrs_root.rglob("*.md")),
                msg="rejected interview authoring must write no ADR file",
            )
            self.assertEqual(
                [e.id for e in Ledger(ledger_path).read_all()],
                events_before,
                msg="ledger must be untouched on closed-kind rejection",
            )

    @covers("REQ-0.34.0-02-04")
    def test_interview_adr_feature_semver_still_passes_unchanged(self) -> None:
        """Closure must not widen — a feature-semver interview still succeeds."""
        import json as _json

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            answers = {
                "id": "ADR-0.36.0-interview-feature-door",
                "semver": "0.36.0",
                "title": "Interview Feature Door",
                "lane": "lite",
                "parent": "PRD-GZKIT-1.0.0",
                "intent": "Feature authoring is unaffected.",
                "decision": "Keep the feature door open.",
                "positive_consequences": "1. Feature work proceeds",
                "negative_consequences": "1. None",
                "checklist": "1. Ship it",
                "alternatives": "Close everything: rejected.",
            }
            Path("answers.json").write_text(_json.dumps(answers), encoding="utf-8")

            result = runner.invoke(main, ["interview", "adr", "--from", "answers.json"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

    # --- REQ-0.34.0-02-03 ---

    @covers("REQ-0.34.0-02-03")
    def test_existing_grandfathered_foundation_adr_still_validates(self) -> None:
        """Every grandfathered foundation still validates with the kind closed.

        The roster is READ FROM THE MANIFEST rather than hardcoded. A pinned
        example rots the moment the sunset migration moves it: this test named
        ``ADR-0.0.1-canonical-govzero-parity`` until OBPI-0.34.0-04 demoted it to
        pool, at which point the assertion failed over a missing fixture rather
        than over the behavior it guards. Reading the manifest also widens the
        check from one ADR to all 51.
        """
        manifest = json.loads(Path("data/foundation_grandfather.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest, msg="the grandfather manifest must not be empty")
        for entry in manifest:
            adr_path = Path("docs/design/adr/foundation") / entry["id"] / f"{entry['id']}.md"
            with self.subTest(adr=entry["id"]):
                self.assertTrue(adr_path.exists(), msg=f"manifest entry not on disk: {adr_path}")
                self.assertEqual(
                    validate_document(adr_path, "adr"),
                    [],
                    msg="closing the authoring doors must not invalidate the grandfathered set",
                )

    @covers("REQ-0.34.0-02-03")
    def test_kind_enum_still_lists_foundation_seal_not_delete(self) -> None:
        """The validator still admits ``kind: foundation``: sealed, not deleted."""

        def kind_errors(kind: str) -> list[str]:
            with TemporaryDirectory() as tmp:
                adr_path = Path(tmp) / "ADR-0.0.99-demo.md"
                adr_path.write_text(
                    "---\nid: ADR-0.0.99-demo\nstatus: Proposed\nsemver: 0.0.99\nlane: lite\n"
                    f"kind: {kind}\nparent: PRD-GZKIT-1.0.0\ndate: 2026-11-23\n---\n\n"
                    "# ADR-0.0.99: Demo\n",
                    encoding="utf-8",
                )
                errors = validate_document(adr_path, "adr")
            return [error.message for error in errors if error.field == "kind"]

        self.assertEqual(kind_errors("foundation"), [])
        self.assertTrue(kind_errors("bogus"), "the kind field must still be a closed set")

    # --- REQ-0.34.0-02-04 (fence): closure did not widen to feature/pool ---

    def test_plan_create_feature_kind_still_passes_unchanged(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "sunset-demo",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.35.0",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_plan_create_pool_kind_still_passes_unchanged(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                ["plan", "create", "some-backlog-item", "--kind", "pool"],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_adr_promote_feature_kind_still_passes_unchanged(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            self._seed_pool_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.sample-work", "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)


class TestFoundationClosureIsFrameworkWide(unittest.TestCase):
    """The foundation kind is closed in EVERY project, adopters included (GHI #1402).

    Operator rulings: *"foundations are retired"* (2026-09-27,
    `docs/rnd/design-amendment.md`), and on 2026-11-27 *"we WERE using foundation
    ADRs but have stopped doing so. They must not persist and we must not permit
    adopters to use them."* That retires the project-local carve-out GHI #740
    built, which read an absent `data/foundation_grandfather.json` as "this
    project never closed the kind".

    Every test here runs in a bare project with NO manifest, which is what an
    adopter has: the doors must refuse there exactly as they do in gzkit.
    """

    _ADOPTER_ID = "ADR-0.0.1-adopter-identity"

    def _adopter_package(self, root: Path) -> Path:
        adr = root / f"{self._ADOPTER_ID}.md"
        adr.write_text(
            f"---\nid: {self._ADOPTER_ID}\nkind: foundation\nstatus: Draft\n---\n\n# x\n",
            encoding="utf-8",
        )
        return adr

    def test_adopter_plan_create_foundation_is_refused(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            # given an adopter project with no grandfather manifest
            _quick_init()
            # when it asks for a foundation ADR
            result = runner.invoke(
                main,
                ["plan", "create", "adopter-identity", "--kind", "foundation", "--semver", "0.0.1"],
            )
            authored = list(Path("design/adr/foundation").rglob("*.md"))
            # then the door refuses, citing the closure, and writes nothing
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("ADR-0.34.0", result.output)
            self.assertEqual(authored, [], "no foundation ADR may be written in an adopter")

    def test_adopter_registration_membrane_refuses_foundation_packages(self) -> None:
        with TemporaryDirectory() as tmp:
            # given an adopter's foundation package and the empty roster an adopter has
            adr = self._adopter_package(Path(tmp))
            # when the registration membrane judges it
            refused = is_ungrandfathered_foundation(adr, self._ADOPTER_ID, frozenset())
            # then it never reaches the adr_created ingress
            self.assertTrue(refused, "an adopter's foundation package must be refused")

    def test_grandfathered_foundation_package_is_still_admitted(self) -> None:
        with TemporaryDirectory() as tmp:
            # given a foundation package on the frozen roster
            adr = self._adopter_package(Path(tmp))
            # when the membrane judges it against that roster
            refused = is_ungrandfathered_foundation(
                adr, self._ADOPTER_ID, frozenset({self._ADOPTER_ID})
            )
            # then the frozen legacy record still registers (REQ-0.34.0-02-03)
            self.assertFalse(refused, "a grandfathered foundation ADR stays readable")

    def test_fresh_gz_init_adopter_cannot_author_a_foundation_adr(self) -> None:
        """Runs the REAL `gz init`, so the claim is about what an adopter receives."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # given a project scaffolded by gz init
            init = runner.invoke(main, ["init"])
            self.assertEqual(init.exit_code, 0, msg=init.output)
            # when it asks for a foundation ADR
            result = runner.invoke(
                main,
                ["plan", "create", "adopter-identity", "--kind", "foundation", "--semver", "0.0.1"],
            )
            # then the kind is closed there too
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("ADR-0.34.0", result.output)


if __name__ == "__main__":
    unittest.main()
