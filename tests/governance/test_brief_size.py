"""Tests for the `gz validate --brief-size` scope (GHI #1196).

`docs/governance/GovZero/obpi-decomposition-matrix.md` says a unit that fails a
granularity principle "MUST be decomposed further", and nothing measured one
brief: `BriefStructure` set minimums only, and the decomposition scorecard set a
count of briefs per ADR. A live brief could therefore be authored oversized and
grow without bound during its run.

The fixtures are built from the declared bounds rather than from literals, so
these tests follow the bound when the operator re-rules it and fail only when
the scope stops enforcing it.
"""

import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from gzkit.governance.trust_audits.brief_size import (
    DIMENSIONS,
    audit_brief_size,
    load_bounds,
    load_ceilings,
    measure_brief,
)

_REPO = Path(__file__).resolve().parents[2]
_GRANDFATHER = "data/brief_size_grandfather.json"


def _brief(*, status: str = "Draft", reqs: int = 2, requirements: int = 2, paths: int = 2) -> str:
    """Render a brief with the given counts on the three counted dimensions."""
    req_lines = "\n".join(
        f"- [ ] REQ-0.1.0-01-{n:02d} [BEHAVIOR]: Given a, when b, then c"
        for n in range(1, reqs + 1)
    )
    requirement_lines = "\n".join(
        f"{n}. REQUIREMENT: constraint {n}" for n in range(1, requirements + 1)
    )
    path_lines = "\n".join(f"- `src/gzkit/mod_{n}.py`" for n in range(1, paths + 1))
    return (
        "---\n"
        "id: OBPI-0.1.0-01-sized\n"
        "parent: ADR-0.1.0-f\n"
        "lane: Lite\n"
        f"status: {status}\n"
        "---\n\n"
        "# OBPI-0.1.0-01-sized: Sized\n\n"
        f"## Allowed Paths\n\n{path_lines}\n\n"
        f"## Requirements (FAIL-CLOSED)\n\n{requirement_lines}\n\n"
        f"## Acceptance Criteria\n\n{req_lines}\n\n"
        "## Evidence\n\n### Change Log\n\n- none\n"
    )


class _Tree(unittest.TestCase):
    def _root(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "docs" / "design" / "adr" / "pkg" / "obpis").mkdir(parents=True)
        return root

    def _write(self, root: Path, text: str, name: str = "OBPI-0.1.0-01-sized.md") -> None:
        (root / "docs" / "design" / "adr" / "pkg" / "obpis" / name).write_text(
            text, encoding="utf-8"
        )

    def _grandfather(self, root: Path, payload: object) -> None:
        (root / "data").mkdir(exist_ok=True)
        (root / _GRANDFATHER).write_text(json.dumps(payload), encoding="utf-8")


class TestMeasure(unittest.TestCase):
    def test_counts_follow_the_sections_they_name(self):
        size = measure_brief(_brief(reqs=3, requirements=4, paths=5))
        self.assertEqual(
            (size["reqs"], size["requirements"], size["allowed_paths"]),
            (3, 4, 5),
        )

    def test_a_requirement_id_repeated_in_a_criterion_counts_once(self):
        text = _brief(reqs=1).replace("then c", "then c, as REQ-0.1.0-01-01 already says")
        self.assertEqual(measure_brief(text)["reqs"], 1)

    def test_evidence_grows_the_whole_brief_and_not_its_contract(self):
        base = _brief()
        grown = base + "- a logged correction\n" * 50
        before, after = measure_brief(base), measure_brief(grown)
        self.assertEqual(after["contract_bytes"], before["contract_bytes"])
        self.assertGreater(after["total_bytes"], before["total_bytes"])

    def test_bytes_are_utf8_bytes_and_not_characters(self):
        text = _brief().replace("constraint 1", "constraint — one")
        self.assertEqual(measure_brief(text)["total_bytes"], len(text.encode("utf-8")))

    def test_every_measured_dimension_has_a_declared_bound(self):
        self.assertEqual(set(load_bounds()), set(DIMENSIONS))
        self.assertEqual(set(measure_brief(_brief())), set(DIMENSIONS))


class TestBriefSizeScope(_Tree):
    def test_a_live_brief_inside_every_bound_passes(self):
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            self._write(root, _brief())
            self.assertEqual(audit_brief_size(root), [])

    def test_each_counted_dimension_fails_closed_one_past_its_bound(self):
        bounds = load_bounds()
        for dimension, keyword in (
            ("reqs", "reqs"),
            ("requirements", "requirements"),
            ("allowed_paths", "paths"),
        ):
            with self.subTest(dimension=dimension), TemporaryDirectory() as tmp:
                root = self._root(tmp)
                self._write(root, _brief(**{keyword: bounds[dimension] + 1}))
                errors = audit_brief_size(root)
                self.assertEqual([e.field for e in errors], [dimension])
                self.assertEqual(errors[0].type, "brief_size")
                self.assertIn("OBPI-0.1.0-01-sized.md", errors[0].artifact)
                self.assertIn(str(bounds[dimension] + 1), errors[0].message)

    def test_a_brief_exactly_at_a_bound_passes(self):
        bounds = load_bounds()
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            self._write(root, _brief(reqs=bounds["reqs"]))
            self.assertEqual(audit_brief_size(root), [])

    def test_a_run_that_only_appends_evidence_trips_the_whole_brief_bound(self):
        bounds = load_bounds()
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            self._write(root, _brief() + "x" * bounds["total_bytes"])
            self.assertEqual([e.field for e in audit_brief_size(root)], ["total_bytes"])

    def test_a_contract_past_its_bound_is_reported_apart_from_the_whole(self):
        bounds = load_bounds()
        padding = "\n## Open Design Questions\n\n" + "q" * bounds["contract_bytes"] + "\n"
        text = _brief().replace("\n## Evidence", padding + "\n## Evidence")
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            self._write(root, text)
            fields = {e.field for e in audit_brief_size(root)}
        self.assertIn("contract_bytes", fields)

    def test_a_terminal_brief_is_a_sealed_record_and_is_not_measured(self):
        bounds = load_bounds()
        for status in ("Completed", "attested_completed", "Withdrawn"):
            with self.subTest(status=status), TemporaryDirectory() as tmp:
                root = self._root(tmp)
                self._write(root, _brief(status=status, reqs=bounds["reqs"] + 5))
                self.assertEqual(audit_brief_size(root), [])

    def test_a_live_brief_that_cannot_be_read_is_a_finding_and_not_a_pass(self):
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            target = root / "docs" / "design" / "adr" / "pkg" / "obpis" / "OBPI-0.1.0-01-raw.md"
            target.write_bytes(b"\xff\xfe not utf-8")
            errors = audit_brief_size(root)
        self.assertEqual([e.artifact.rsplit("/", 1)[-1] for e in errors], ["OBPI-0.1.0-01-raw.md"])
        self.assertIsNone(errors[0].field)

    def test_a_tree_with_no_briefs_has_nothing_to_report(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(audit_brief_size(Path(tmp)), [])


class TestGrandfatherCeilings(_Tree):
    def test_a_ceiling_admits_the_brief_up_to_the_ceiling_and_no_further(self):
        over = load_bounds()["reqs"] + 3
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            self._grandfather(root, {"ceilings": {"OBPI-0.1.0-01-sized": {"reqs": over}}})
            self._write(root, _brief(reqs=over))
            self.assertEqual(audit_brief_size(root), [])
            self._write(root, _brief(reqs=over + 1))
            errors = audit_brief_size(root)
        self.assertEqual([e.field for e in errors], ["reqs"])
        self.assertIn(str(over), errors[0].message)

    def test_a_ceiling_on_one_dimension_admits_no_other(self):
        bounds = load_bounds()
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            self._grandfather(
                root, {"ceilings": {"OBPI-0.1.0-01-sized": {"reqs": bounds["reqs"] + 3}}}
            )
            self._write(root, _brief(requirements=bounds["requirements"] + 1))
            self.assertEqual([e.field for e in audit_brief_size(root)], ["requirements"])

    def test_a_ceiling_for_one_brief_admits_no_other_brief(self):
        over = load_bounds()["reqs"] + 3
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            self._grandfather(root, {"ceilings": {"OBPI-0.1.0-09-other": {"reqs": over}}})
            self._write(root, _brief(reqs=over))
            self.assertEqual([e.field for e in audit_brief_size(root)], ["reqs"])

    def test_an_unreadable_ceiling_file_is_a_finding_and_admits_nothing(self):
        over = load_bounds()["reqs"] + 3
        for payload in ("{not json", '["a list"]', '{"ceilings": {"OBPI-0.1.0-01-sized": 9}}'):
            with self.subTest(payload=payload), TemporaryDirectory() as tmp:
                root = self._root(tmp)
                (root / "data").mkdir()
                (root / _GRANDFATHER).write_text(payload, encoding="utf-8")
                self._write(root, _brief(reqs=over))
                errors = audit_brief_size(root)
                self.assertIn(_GRANDFATHER, [e.artifact for e in errors])
                self.assertIn("reqs", [e.field for e in errors])


class TestLiveTree(unittest.TestCase):
    def test_the_repository_passes_its_own_scope(self):
        self.assertEqual(audit_brief_size(_REPO), [])

    def test_ceilings_only_shrink_against_the_committed_baseline(self):
        """Pre-commit check: an edit cannot add a ceiling or raise one."""
        from tests.commands.common import _isolated_git_env

        previous = subprocess.run(
            ["git", "show", f"HEAD:{_GRANDFATHER}"],
            cwd=_REPO,
            env=_isolated_git_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if previous.returncode:
            self.skipTest("No committed ceiling baseline yet (or Git history unavailable).")
        old = json.loads(previous.stdout)["ceilings"]
        current, unreadable = load_ceilings(_REPO)
        self.assertEqual(unreadable, [])
        self.assertLessEqual(current.keys(), old.keys(), "Ceiling entries may only be removed.")
        for brief, ceilings in current.items():
            self.assertLessEqual(ceilings.keys(), old[brief].keys(), f"{brief}: no new dimension.")
            for dimension, ceiling in ceilings.items():
                self.assertLessEqual(
                    ceiling, old[brief][dimension], f"{brief} {dimension}: may only decrease."
                )


class TestDispatch(unittest.TestCase):
    """A scope only reachable behind a remembered flag, or exiting 1, is not a gate."""

    def _invoke(self, reqs: int):
        from gzkit.cli import main
        from tests.commands.common import CliRunner, _quick_init

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            obpis = Path("docs") / "design" / "adr" / "pkg" / "obpis"
            obpis.mkdir(parents=True, exist_ok=True)
            (obpis / "OBPI-0.1.0-01-sized.md").write_text(_brief(reqs=reqs), encoding="utf-8")
            return runner.invoke(main, ["validate", "--brief-size"])

    def test_the_flag_reaches_the_scope_and_a_breach_is_a_policy_breach(self):
        result = self._invoke(load_bounds()["reqs"] + 1)
        self.assertEqual(result.exit_code, 3, result.output)
        self.assertIn("OBPI-0.1.0-01-sized", result.output)

    def test_the_flag_passes_a_brief_inside_its_bounds(self):
        result = self._invoke(load_bounds()["reqs"])
        self.assertEqual(result.exit_code, 0, result.output)

    def test_the_audit_is_part_of_the_packages_declared_surface(self):
        from gzkit.governance import trust_audits

        self.assertIn("audit_brief_size", trust_audits.__all__)
        self.assertIs(trust_audits.audit_brief_size, audit_brief_size)

    def test_gz_check_shells_the_scope_as_its_own_bound_step(self):
        from gzkit import quality
        from gzkit.commands.quality import _STEP_GUARD_META, _build_check_steps
        from gzkit.qc_binding import build_qc_registry

        runner = dict(_build_check_steps())["Brief size"]
        with patch.object(quality, "run_command", return_value="ran") as shelled:
            self.assertEqual(runner(_REPO), "ran")
        self.assertEqual(shelled.call_args.args[0], "uv run gz validate --brief-size")
        self.assertEqual(_STEP_GUARD_META["Brief size"][0], "brief-size")
        step = {s.name: s for s in build_qc_registry()}["Brief size"]
        self.assertEqual((step.binding, step.subject), ("bound", "docs/"))


class TestNegativeControls(unittest.TestCase):
    """The refuse and admit halves are registered, declared and pass on their own fixtures."""

    def _record(self, claim_id: str):
        from gzkit.enforcement import production_enforcement_registry

        return {r.claim_id: r for r in production_enforcement_registry()}[claim_id]

    def test_the_refuse_control_catches_its_fixture_for_its_own_reason(self):
        from gzkit.enforcement import _run_single_claim

        record = self._record("brief-size")
        result = _run_single_claim(record)
        self.assertEqual(result.outcome, "PASS", result.message)
        self.assertEqual(record.exempts, "brief-size-grandfathered")
        self.assertIsNotNone(record.population)

    def test_the_refuse_entrypoint_reports_no_catch_when_a_decoy_fires(self):
        from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep

        over = _brief(reqs=load_bounds()["reqs"] + 1)
        with TemporaryDirectory() as tmp:
            obpis = Path(tmp) / "docs" / "design" / "adr" / "pkg" / "obpis"
            obpis.mkdir(parents=True)
            (obpis / "OBPI-0.0.99-01-over.md").write_text(over, encoding="utf-8")
            caught = ep._ep_brief_size(Path(tmp))
            (obpis / "OBPI-0.0.99-01-at.md").write_text(over, encoding="utf-8")
            with_decoy_firing = ep._ep_brief_size(Path(tmp))
        self.assertEqual([e.field for e in caught], ["reqs"])
        self.assertEqual(with_decoy_firing, [])

    def test_the_admit_control_passes_and_owes_no_further_exemption(self):
        from gzkit.enforcement import EXEMPTS_NONE, _run_single_claim

        record = self._record("brief-size-grandfathered")
        result = _run_single_claim(record)
        self.assertEqual(result.outcome, "PASS", result.message)
        self.assertEqual(record.exempts, EXEMPTS_NONE)
        self.assertIsNotNone(record.population)


if __name__ == "__main__":
    unittest.main()
