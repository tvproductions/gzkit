"""The readers RO-2 tranche 5 moved onto the identity seam, each driven by its own test.

`gz arb red --commit 94edfb495` graded tranche 5 `undriven`: 55 hunks survived,
each a reader whose new seam call its commit's tests never reached (receipt
`arb-red-commit-94edfb4955b4-8edc326655854abaa7bdfab3a49925e8`). Each test below
calls the reader the hunk changed and asserts what the id grammar says it must
return, so reverting the hunk (dropping the seam import, or restoring the
spelled-out parse) fails here. Expected values come from the grammar in
`gzkit.core.models`, never from a run of the code.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit import exchange_records, traceability
from gzkit.adr_eval import (
    AdrEvalResult,
    EvalVerdict,
    ObpiDimensionScores,
    render_scorecard_markdown,
)
from gzkit.airlock import enter as airlock_enter
from gzkit.commands import (
    adr_audit,
    adr_audit_covers_backfill,
    adr_coverage,
    adr_promote_utils,
    closeout_form,
    context_cmd,
    covers,
    obpi_lock,
    plan,
    plan_audit_cmd,
    specify_cmd,
    status,
    status_obpi,
    validate_decomposition,
    validate_task_envelope,
)
from gzkit.commands import quality as quality_cmd
from gzkit.commands.common import console as cli_console
from gzkit.foundation import sunset_migrate
from gzkit.governance.trust_audits import taxonomy
from gzkit.hooks.scripts import validation as hook_validation
from gzkit.ledger import Ledger, _extract_bare_adr_semver
from gzkit.lock_manager import adr_id_from_obpi
from gzkit.quality import _extract_obpi_slug
from gzkit.req_kind import compute_three_channel_coverage
from gzkit.req_kind_fence import _fence_obpi_anchored, _find_parent_adr_file
from gzkit.tasks import TaskId, derive_req_task_id, next_seq_for_req
from gzkit.traceability import CoverageEntry, CoverageReport, CoverageRollup


class TestParentsReadFromTheSeam(unittest.TestCase):
    """An id's parent: OBPI-<semver>-<NN> → ADR-<semver>; REQ → OBPI; TASK → REQ."""

    def test_an_obpi_names_its_adr(self) -> None:
        for reader in (
            obpi_lock._adr_id_from_obpi,
            adr_id_from_obpi,
            plan_audit_cmd._derive_adr_id,
        ):
            with self.subTest(reader=reader.__qualname__):
                self.assertEqual(reader("OBPI-0.1.0-02-some-slug"), "ADR-0.1.0")
                self.assertEqual(reader("OBPI-0.0.16-05"), "ADR-0.0.16")

    def test_a_req_names_its_obpi(self) -> None:
        self.assertEqual(
            adr_audit_covers_backfill._parent_obpi_id("REQ-0.1.0-02-03"), "OBPI-0.1.0-02"
        )
        self.assertEqual(adr_coverage._req_prefix_for_obpi("OBPI-0.1.0-02-slug"), "REQ-0.1.0-02-")
        self.assertTrue(covers._req_belongs_to_obpi("REQ-0.1.0-02-01", "OBPI-0.1.0-02-slug"))
        self.assertFalse(covers._req_belongs_to_obpi("REQ-0.1.0-03-01", "OBPI-0.1.0-02-slug"))

    def test_a_task_names_its_req_and_obpi(self) -> None:
        self.assertEqual(status._req_prefix_from_task_id("TASK-0.1.0-02-03-04"), "REQ-0.1.0-02-03")
        self.assertEqual(
            validate_task_envelope._obpi_id_for_task("TASK-0.1.0-02-03-04"), "OBPI-0.1.0-02"
        )
        self.assertTrue(
            validate_task_envelope._task_matches_obpi("TASK-0.1.0-02-03-04", "OBPI-0.1.0-02")
        )
        self.assertFalse(
            validate_task_envelope._task_matches_obpi("TASK-0.1.0-03-03-04", "OBPI-0.1.0-02")
        )

    def test_an_uncovered_accept_is_attributed_through_its_req_tasks(self) -> None:
        event = {
            "event": "obpi_completion_uncovered_accept",
            "obpi_id": "O",
            "req_id": "REQ-0.1.0-02-03",
        }
        self.assertTrue(
            validate_task_envelope._is_req_attributed_uncovered_accept_event(
                event, {"O": {"TASK-0.1.0-02-03-01"}}
            )
        )
        self.assertFalse(
            validate_task_envelope._is_req_attributed_uncovered_accept_event(
                event, {"O": {"TASK-0.1.0-02-04-01"}}
            )
        )


class TestSemversAndSlugsReadFromTheSeam(unittest.TestCase):
    def test_an_adr_semver(self) -> None:
        self.assertEqual(closeout_form._adr_semver_term("ADR-0.1.0-some-feature"), "0.1.0")
        self.assertEqual(specify_cmd._extract_semver("ADR-0.14.0-x"), "0.14.0")
        self.assertEqual(adr_coverage._extract_adr_semver("ADR-0.14.0-x"), "0.14.0")
        self.assertEqual(_extract_bare_adr_semver("ADR-0.0.22-security-x"), "ADR-0.0.22")

    def test_an_obpi_slug(self) -> None:
        self.assertEqual(
            _extract_obpi_slug("OBPI-0.23.0-02-product-proof-gate"), "product-proof-gate"
        )

    def test_a_canonical_adr_id_is_composed(self) -> None:
        self.assertEqual(plan._compose_canonical_adr_id("my-slug", "0.2.0"), "ADR-0.2.0-my-slug")
        self.assertEqual(adr_promote_utils._resolve_promotion_parent("0.1.0", {}), "ADR-0.1.0")

    def test_a_pool_id_yields_its_slug(self) -> None:
        self.assertEqual(
            adr_promote_utils._derive_slug_from_pool_id("ADR-pool.some-idea"), "some-idea"
        )
        # The epic is the first hyphen-delimited token of the pool slug.
        self.assertEqual(status._filename_derived_epic("ADR-pool.alpha-beta"), "alpha")

    def test_an_obpi_acceptance_seed_names_the_first_req(self) -> None:
        seed = specify_cmd._render_obpi_acceptance_seed("0.1.0", 2, "")
        self.assertIn("REQ-0.1.0-02-01", seed)

    def test_sort_keys_order_by_semver_not_by_spelling(self) -> None:
        self.assertEqual(
            sorted(["ADR-0.10.0", "ADR-0.9.0"], key=traceability.adr_sort_key),
            ["ADR-0.9.0", "ADR-0.10.0"],
        )
        self.assertEqual(traceability._obpi_sort_key("OBPI-0.15.0-03"), ((0, 15, 0), 3))


class TestTaxonomyReadsThePoolSlug(unittest.TestCase):
    def test_a_pool_slug_must_match_its_file(self) -> None:
        payload = {"id": "ADR-pool.a", "semver": "pool"}
        self.assertEqual(taxonomy._pool_identity_problems(payload, "a", frozenset()), [])
        self.assertEqual(len(taxonomy._pool_identity_problems(payload, "b", frozenset())), 1)


class TestFenceReadsTheSeam(unittest.TestCase):
    def test_a_section_naming_the_obpi_by_stem_anchors_its_req(self) -> None:
        self.assertTrue(_fence_obpi_anchored("per REQ-0.32.0-04-02", "REQ-0.32.0-04-01"))
        self.assertFalse(_fence_obpi_anchored("per REQ-0.32.0-05-02", "REQ-0.32.0-04-01"))

    def test_the_parent_adr_file_is_found_by_semver(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr = (
                root
                / "docs"
                / "design"
                / "adr"
                / "pre-release"
                / "ADR-0.1.0-foo"
                / "ADR-0.1.0-foo.md"
            )
            adr.parent.mkdir(parents=True)
            adr.write_text("---\nid: ADR-0.1.0-foo\n---\n", encoding="utf-8")
            found = _find_parent_adr_file("0.1.0", root)
        self.assertIsNotNone(found)
        self.assertEqual(found.name if found else None, "ADR-0.1.0-foo.md")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class TestCoversReadersScopeByTheAdrsReqPrefix(unittest.TestCase):
    """`@covers` scans keep the REQs under one ADR's semver, and only its active OBPIs."""

    def _tree(self, root: Path) -> None:
        _write(
            root / "tests" / "test_x.py",
            "from gzkit.traceability import covers\n\n\n"
            '@covers("REQ-0.1.0-01-01")\ndef test_a():\n    pass\n\n\n'
            '@covers("REQ-0.1.0-02-01")\ndef test_b():\n    pass\n\n\n'
            '@covers("REQ-0.1.10-01-01")\ndef test_c():\n    pass\n',
        )

    def test_the_audit_keeps_only_active_obpis_under_the_adr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root)
            every = adr_audit._collect_covers_locations_for_adr(root, "ADR-0.1.0-f")
            active = adr_audit._collect_covers_locations_for_adr(
                root, "ADR-0.1.0-f", ["OBPI-0.1.0-02-thing"]
            )
        self.assertEqual({req for req, _, _ in every}, {"REQ-0.1.0-01-01", "REQ-0.1.0-02-01"})
        self.assertEqual([req for req, _, _ in active], ["REQ-0.1.0-02-01"])

    def test_the_context_lists_covering_tests_under_the_adr_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root)
            rendered = context_cmd._render_covering_tests("ADR-0.1.0-f", root)
        self.assertIn("REQ-0.1.0-01-01", rendered)
        self.assertNotIn("REQ-0.1.10-01-01", rendered)


class TestAnObpisReqsAreReadFromItsBriefs(unittest.TestCase):
    def test_reqs_of_one_obpi_by_semver_and_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpis = root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.1.0-f" / "obpis"
            for item in ("01", "02"):
                _write(
                    obpis / f"OBPI-0.1.0-{item}-x.md",
                    f"---\nid: OBPI-0.1.0-{item}-x\nparent: ADR-0.1.0-f\n---\n\n"
                    f"## Acceptance Criteria\n\n- [ ] REQ-0.1.0-{item}-01: does a thing\n",
                )
            reqs = quality_cmd._resolve_obpi_req_ids(root, "obpi-0.1.0-02-x")
        self.assertEqual(reqs, {"REQ-0.1.0-02-01"})

    def test_an_id_that_is_not_an_obpi_is_refused(self) -> None:
        # Caught broadly so a missing guard (a TypeError further on) fails the assertion.
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(Exception) as raised:
            quality_cmd._resolve_obpi_req_ids(Path(tmp), "ADR-0.1.0-f")
        self.assertIsInstance(raised.exception, ValueError)


class TestTheObpiSectionCountsOpenRows(unittest.TestCase):
    def test_open_rows_are_counted_and_previewed(self) -> None:
        rows = [
            {"id": f"OBPI-0.1.0-0{n}", "completed": False, "found_file": True} for n in range(5)
        ]
        summary = {"total": 5, "completed": 0, "unit_status": "in_progress"}
        with cli_console.capture() as cap:
            status_obpi._print_status_obpi_section(rows, summary)
            status_obpi._print_status_obpi_section(rows, summary, full=True)
        text = cap.get()
        self.assertEqual(text.count("OBPI Open:       5 remaining"), 2)
        self.assertIn("... and 2 more", text)

    def test_no_open_rows_reports_all_complete(self) -> None:
        rows = [{"id": "OBPI-0.1.0-01", "ledger_completed": True, "found_file": True}]
        summary = {"total": 1, "completed": 1, "unit_status": "completed"}
        with cli_console.capture() as cap:
            status_obpi._print_status_obpi_section(rows, summary)
        text = cap.get()
        self.assertIn("all linked OBPIs completed with evidence", text)
        self.assertNotIn("OBPI Open", text)


class TestTheScorecardNamesEachObpiBySlug(unittest.TestCase):
    def test_an_obpi_row_shows_its_slug(self) -> None:
        score = ObpiDimensionScores(
            obpi_id="OBPI-0.1.0-02-some-slug",
            independence=3,
            testability=3,
            value=3,
            size=3,
            clarity=3,
            average=3.0,
        )
        result = AdrEvalResult(
            adr_id="ADR-0.1.0-f",
            adr_dimensions=[],
            adr_weighted_total=3.0,
            obpi_scores=[score],
            verdict=EvalVerdict.GO,
            action_items=[],
            timestamp="2026-10-19T00:00:00+00:00",
        )
        self.assertIn("| some-slug | 3 |", render_scorecard_markdown(result))


class TestTheAirlockProbeNamesNoArtifact(unittest.TestCase):
    def test_the_unaccounted_seam_control_holds_then_proceeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "brief.md", "# brief\n")
            _write(root / "accounted.md", f"accounts for DEP-UNACCOUNTED-{root.name}\n")
            self.assertEqual(airlock_enter._ep_airlock_unaccounted_seam(root), 1)


class TestDecompositionFindsBriefsByObpiPrefix(unittest.TestCase):
    def test_an_adr_with_its_briefs_reports_no_missing_brief(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_dir = root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.1.0-f"
            _write(
                adr_dir / "ADR-0.1.0-f.md",
                "---\nid: ADR-0.1.0-f\n---\n\n# ADR-0.1.0-f\n\n"
                "## Decomposition Scorecard\n\n"
                "- Data/State: 1\n- Logic/Engine: 1\n- Interface: 1\n"
                "- Observability: 1\n- Lineage: 1\n- Dimension Total: 5\n"
                "- Baseline Range: 3\n- Baseline Selected: 3\n- Split Single-Narrative: 0\n"
                "- Split Surface Boundary: 0\n- Split State Anchor: 0\n"
                "- Split Testability Ceiling: 0\n- Split Total: 0\n"
                "- Final Target OBPI Count: 3\n\n"
                "## Feature Checklist\n\n- [ ] OBPI-0.1.0-01: one\n- [ ] OBPI-0.1.0-02: two\n"
                "- [ ] OBPI-0.1.0-03: three\n",
            )
            without = validate_decomposition.validate_decomposition(root)
            _write(adr_dir / "obpis" / "OBPI-0.1.0-01-one.md", "# OBPI-0.1.0-01-one\n")
            with_brief = validate_decomposition.validate_decomposition(root)
        self.assertTrue(any("brief" in e.message.lower() for e in without), without)
        self.assertEqual(with_brief, [])


class TestTheCompletionExchangeNamesTheParentAdr(unittest.TestCase):
    def test_the_exchange_frontmatter_carries_the_obpis_adr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = exchange_records.write_completion_exchange(
                Path(tmp),
                obpi_id="OBPI-0.1.0-02-some-slug",
                agent="a",
                attestor="g0",
                attestation_text="ok",
                implementation_summary="s",
                key_proof="p",
                last_lock_event_timestamp=None,
                commit_sha="abc",
                branch="main",
                brief_rel_path="docs/design/adr/OBPI-0.1.0-02-some-slug.md",
            )
            text = Path(path).read_text(encoding="utf-8")
        self.assertIn("adr_id: ADR-0.1.0", text)


class TestTheGeneratedCompletionHookDerivesTheAdr(unittest.TestCase):
    def test_the_script_maps_an_obpi_to_its_adr(self) -> None:
        namespace: dict[str, object] = {"__name__": "generated_hook"}
        exec(
            compile(hook_validation._obpi_completion_validator_script(), "hook", "exec"), namespace
        )  # noqa: S102
        extract = namespace["extract_adr_id"]
        self.assertEqual(extract("OBPI-0.14.0-04"), "ADR-0.14.0")  # ty: ignore[call-non-callable]


class TestCoverageRollsUpAdrsInSemverOrder(unittest.TestCase):
    def test_by_adr_orders_0_9_before_0_10(self) -> None:
        entries = [
            CoverageEntry(req_id=rid, covered=True, covering_tests=["t"])
            for rid in ("REQ-0.10.0-01-01", "REQ-0.9.0-01-01")
        ]
        rollup = CoverageRollup(
            identifier="all", total_reqs=2, covered_reqs=2, uncovered_reqs=0, coverage_percent=100.0
        )
        report = CoverageReport(by_adr=[], by_obpi=[], entries=entries, summary=rollup)
        enriched = compute_three_channel_coverage(report, [])
        self.assertEqual([r.identifier for r in enriched.by_adr], ["ADR-0.9.0", "ADR-0.10.0"])


class TestTheTaskModelComposesItsLineage(unittest.TestCase):
    def test_a_task_names_its_req_obpi_and_adr(self) -> None:
        task = TaskId.parse("TASK-0.1.0-02-03-04")
        self.assertEqual(str(task), "TASK-0.1.0-02-03-04")
        self.assertEqual(task.req_id, "REQ-0.1.0-02-03")
        self.assertEqual(task.obpi_id, "OBPI-0.1.0-02")
        self.assertEqual(task.adr_id, "ADR-0.1.0")

    def test_the_next_seq_counts_only_the_reqs_own_tasks(self) -> None:
        existing = ["TASK-0.1.0-02-03-01", "TASK-0.1.0-02-03-02", "TASK-0.1.0-02-04-07"]
        self.assertEqual(next_seq_for_req("REQ-0.1.0-02-03", existing_task_ids=existing), 3)
        self.assertEqual(derive_req_task_id("REQ-0.1.0-02-03", seq=5), "TASK-0.1.0-02-03-05")


class TestTheSunsetMigrationReadsIdsThroughTheSeam(unittest.TestCase):
    def _init(self, root: Path) -> Ledger:
        _write(root / ".gzkit.json", json.dumps({"paths": {"adrs": "design/adr"}}))
        return Ledger(root / "ledger.jsonl")

    def test_a_foundation_id_that_disagrees_with_its_semver_is_a_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = self._init(root)
            pkg = root / "design" / "adr" / "foundation" / "ADR-0.0.5-x"
            _write(pkg / "ADR-0.0.5-x.md", "---\nid: ADR-0.0.5-x\nsemver: 0.0.6\n---\n# X\n")
            with self.assertRaises(RuntimeError) as raised:
                sunset_migrate.foundation_rows(root, ledger)
        self.assertIn("inconsistent with semver `0.0.6`", str(raised.exception))

    def test_a_torn_demotion_names_the_leftover_pool_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = self._init(root)
            _write(
                root / "artifacts" / "receipts" / "foundation-sunset-journal.json",
                json.dumps({"demotions": [{"source_id": "ADR-0.0.67-lost"}]}),
            )
            _write(root / "design" / "adr" / "pool" / "ADR-pool.lost.md", "x\n")
            stranded = sunset_migrate.interrupted_demotions(root, ledger)
        self.assertTrue(any("rm design/adr/pool/ADR-pool.lost.md" in s for s in stranded), stranded)


if __name__ == "__main__":
    unittest.main()
