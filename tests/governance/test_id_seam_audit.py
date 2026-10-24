"""``gz validate --id-seam``: the identity seam's ratchet and resolution check.

Drydock RO-2 tranche 1 (`docs/governance/harbor-ro2-identity-seam.md` § The
witness). The scan finds every id grammar and spelling-derived parent outside the
seam; the baseline holds today's sites, keyed by file and enclosing symbol, and
may only shrink; the resolution check resolves every ``@covers`` REQ, scenario
REQ tag, and brief frontmatter OBPI and ADR id through the seam's resolver.
"""

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from gzkit.core.id_resolver import IdentityContext
from gzkit.governance.trust_audits.id_seam import (
    BASELINE_RELPATH,
    SeamSite,
    audit_id_seam,
    check_id_resolution,
    check_seam_baseline,
    collect_cited_ids,
    scan_seam_sites,
    scan_source,
)

_REPO = Path(__file__).resolve().parents[2]


def _kinds(source: str) -> list[tuple[str, str]]:
    return sorted((site.symbol, site.kind) for site in scan_source(textwrap.dedent(source), "m.py"))


class TestTheScanFindsGrammarCopies(unittest.TestCase):
    def test_a_compiled_literal_is_a_site_of_its_kind(self) -> None:
        found = _kinds(
            r"""
            import re
            _OBPI = re.compile(r"OBPI-\d+\.\d+\.\d+-\d+")

            def f(text):
                return re.search(r"(?:ADR|REQ)-[\d.]+", text)
            """
        )
        self.assertEqual(found, [("<module>", "OBPI"), ("f", "ADR"), ("f", "REQ")])

    def test_a_named_constant_a_pattern_keyword_and_an_fstring_are_sites(self) -> None:
        found = _kinds(
            r"""
            import re
            from pydantic import Field
            TASK_RE = r"TASK-\d+"

            class M:
                id: str = Field(..., pattern=r"^ADR-\d+$")

                def g(self, text, n):
                    return re.match(TASK_RE, text) or re.match(rf"OBPI-{n}-\d{{2}}", text)
            """
        )
        self.assertEqual(found, [("M", "ADR"), ("M.g", "OBPI"), ("M.g", "TASK")])

    def test_a_split_slice_or_rewrite_of_an_id_is_a_parent_site(self) -> None:
        found = _kinds(
            """
            def h(obpi_id, adr_id, other):
                a = obpi_id.rsplit("-", 1)[0]
                b = adr_id[:9]
                c = obpi_id.replace("OBPI-", "ADR-")
                d = other.split("-")
                return a, b, c, d
            """
        )
        self.assertEqual(found, [("h", "parent"), ("h", "parent"), ("h", "parent")])

    def test_an_id_composed_from_parts_is_a_compose_site_counted_once(self) -> None:
        """Composition recovers a parent or scans for children by spelling (tranche 5)."""
        found = _kinds(
            r"""
            import re

            def c(task, semver, n, text):
                parent = f"OBPI-{task.semver}-{task.obpi_item}"
                children = [k for k in text if k.startswith(f"REQ-{semver}-")]
                return parent, children, re.match(rf"ADR-{n}-\d", text)
            """
        )
        self.assertEqual(found, [("c", "ADR"), ("c", "compose"), ("c", "compose")])

    def test_the_seam_bodies_and_prose_are_not_sites(self) -> None:
        found = _kinds(
            r"""
            import re
            from gzkit.core.models import REQ_ID_BODY_PLAIN
            _REQ = re.compile(rf"^{REQ_ID_BODY_PLAIN}$")

            def k(obpi_id):
                if not obpi_id.startswith("OBPI-"):
                    raise ValueError(f"OBPI-{obpi_id} is not an id")
                return re.sub(r"\s+", " ", obpi_id)
            """
        )
        self.assertEqual(found, [])

    def test_an_embedded_hook_script_is_scanned_as_the_python_it_is(self) -> None:
        found = _kinds(
            '''
            from textwrap import dedent

            def _gate_script():
                return dedent(
                    """\\
                    import re
                    PATTERN = re.compile(r"OBPI-[\\\\d.]+-\\\\d+")

                    def main():
                        return PATTERN
                    """
                )
            '''
        )
        self.assertEqual(found, [("_gate_script:<module>", "OBPI")])

    def test_the_seam_modules_are_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            core = root / "src" / "gzkit" / "core"
            core.mkdir(parents=True)
            body = 'import re\nX = re.compile(r"OBPI-\\d+")\n'
            for name in ("models.py", "id_resolver.py", "other.py"):
                (core / name).write_text(body, encoding="utf-8")
            sites = scan_seam_sites(root)
        self.assertEqual([site.file for site in sites], ["src/gzkit/core/other.py"])


def _site(file: str, symbol: str, kind: str) -> SeamSite:
    return SeamSite(file=file, symbol=symbol, kind=kind, line=1)


class TestTheBaselineOnlyShrinks(unittest.TestCase):
    rows = ({"file": "a.py", "symbol": "f", "kind": "OBPI", "sites": 2},)

    def test_the_seeded_sites_pass(self) -> None:
        sites = [_site("a.py", "f", "OBPI"), _site("a.py", "f", "OBPI")]
        self.assertEqual(check_seam_baseline(sites, list(self.rows)), [])

    def test_a_new_site_fails_and_names_the_seam(self) -> None:
        sites = [_site("a.py", "f", "OBPI")] * 2 + [_site("b.py", "g", "REQ")]
        errors = check_seam_baseline(sites, list(self.rows))
        self.assertEqual(len(errors), 1)
        self.assertIn("b.py", errors[0].artifact)
        self.assertIn("gzkit.core.models", errors[0].message)
        self.assertIn("harbor-ro2-identity-seam.md", errors[0].message)

    def test_a_grown_symbol_fails(self) -> None:
        sites = [_site("a.py", "f", "OBPI")] * 3
        self.assertEqual(len(check_seam_baseline(sites, list(self.rows))), 1)

    def test_a_gone_or_shrunk_row_must_be_removed_or_lowered(self) -> None:
        for sites in ([], [_site("a.py", "f", "OBPI")]):
            with self.subTest(remaining=len(sites)):
                errors = check_seam_baseline(sites, list(self.rows))
                self.assertEqual(len(errors), 1)
                self.assertIn(BASELINE_RELPATH, errors[0].message)


class TestEveryCitedIdResolves(unittest.TestCase):
    def _context(self) -> IdentityContext:
        return IdentityContext(
            graph={
                "OBPI-0.1.0-01-a": {"type": "obpi", "parent": "ADR-0.1.0-x"},
                "OBPI-0.1.0-02-b": {"type": "obpi", "parked": True},
                "ADR-0.1.0-x": {"type": "adr"},
            },
            req_owners={
                "REQ-0.1.0-01-01": ("OBPI-0.1.0-01-a",),
                "REQ-0.1.0-02-01": ("OBPI-0.1.0-02-b",),
            },
        )

    def test_resolvable_ids_pass_and_parked_ones_are_recorded_as_such(self) -> None:
        cited = [("t.py", "REQ-0.1.0-01-01"), ("t.py", "REQ-0.1.0-02-01"), ("b.md", "ADR-0.1.0")]
        self.assertEqual(check_id_resolution(cited, self._context()), [])

    def test_an_unresolvable_id_fails_at_its_source(self) -> None:
        errors = check_id_resolution([("x.feature", "REQ-0.1.0-01-99")], self._context())
        self.assertEqual([error.artifact for error in errors], ["x.feature"])
        self.assertIn("REQ-0.1.0-01-99", errors[0].message)


class TestCitedIdsAreCollectedFromTheirChannels(unittest.TestCase):
    def test_decorators_tags_and_frontmatter_are_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "test_a.py").write_text(
                textwrap.dedent(
                    """
                    from gzkit.traceability import covers

                    @covers("REQ-0.1.0-01-01")
                    def test_x():
                        with raises(ValueError):
                            covers("INVALID")

                    class TestY:
                        @covers("REQ-0.1.0-01-03")
                        def test_y(self):
                            with raises(ValueError):

                                @covers("REQ-9.9.9-99-99")
                                def nested():
                                    pass
                    """
                ),
                encoding="utf-8",
            )
            (root / "features").mkdir()
            (root / "features" / "a.feature").write_text(
                "Feature: f\n  @REQ-0.1.0-01-02 @slow\n  Scenario: s\n", encoding="utf-8"
            )
            obpis = root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.1.0-x" / "obpis"
            obpis.mkdir(parents=True)
            (obpis / "OBPI-0.1.0-01-a.md").write_text(
                "---\nid: OBPI-0.1.0-01-a\nparent: ADR-0.1.0-x\n---\n", encoding="utf-8"
            )
            cited = collect_cited_ids(root, "docs/design")
        self.assertEqual(
            sorted(ident for _, ident in cited),
            [
                "ADR-0.1.0-x",
                "OBPI-0.1.0-01-a",
                "REQ-0.1.0-01-01",
                "REQ-0.1.0-01-02",
                "REQ-0.1.0-01-03",
            ],
        )


class TestTheRealTree(unittest.TestCase):
    """The committed baseline matches today's sites and every cited id resolves."""

    def test_the_repository_passes_its_own_scope(self) -> None:
        self.assertEqual([error.message for error in audit_id_seam(_REPO)], [])

    def test_the_baseline_is_a_registered_shrink_ratchet_at_its_row_count(self) -> None:
        rows = json.loads((_REPO / BASELINE_RELPATH).read_text(encoding="utf-8"))["sites"]
        registry = json.loads(
            (_REPO / "data" / "waiver_ratchet_registry.json").read_text(encoding="utf-8")
        )
        (entry,) = [s for s in registry["surfaces"] if s["data_file"] == BASELINE_RELPATH]
        self.assertEqual(entry["mechanism"], "shrink-ratchet")
        self.assertEqual(entry["baseline_count"], len(rows))


class TestTheScanReadsEveryLiteralForm(unittest.TestCase):
    def test_an_annotated_constant_and_a_concatenation_are_read(self) -> None:
        found = _kinds(
            r"""
            import re
            X: str = r"ADR-\d+"

            def f(text):
                return re.match(X, text) or re.match(r"OBPI-" + r"\d+", text)
            """
        )
        self.assertEqual(found, [("f", "ADR"), ("f", "OBPI")])

    def test_an_embedded_string_that_is_not_python_is_one_hook_site(self) -> None:
        found = _kinds(
            """
            from textwrap import dedent

            def _doc():
                return dedent("OBPI-[0-9]+ ((")

            def _bytes():
                return dedent(b"OBPI-[0-9]+")
            """
        )
        self.assertEqual(found, [("_doc", "hook")])

    def test_slicing_prose_named_for_an_artifact_is_no_site_and_slicing_its_id_is(self) -> None:
        found = _kinds(
            """
            def statement_tail(req_text, req_id):
                return req_text[3:], req_id[3:]
            """
        )
        self.assertEqual(found, [("statement_tail", "parent")])

    def test_a_split_on_a_non_separator_or_a_rewrite_of_prose_is_no_site(self) -> None:
        found = _kinds(
            """
            def g(obpi_id, text):
                return obpi_id.split(","), text.replace("old", "new")
            """
        )
        self.assertEqual(found, [])


class TestTheBaselineIsExact(unittest.TestCase):
    def test_a_row_held_twice_fails(self) -> None:
        row = {"file": "a.py", "symbol": "f", "kind": "OBPI", "sites": 1}
        errors = check_seam_baseline([_site("a.py", "f", "OBPI")], [row, dict(row)])
        self.assertEqual(len(errors), 1)
        self.assertIn("twice", errors[0].message)

    def test_a_missing_baseline_fails_closed_naming_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            errors = audit_id_seam(Path(tmp))
        self.assertEqual([error.artifact for error in errors], [BASELINE_RELPATH])


class TestDispatch(unittest.TestCase):
    """The flag reaches the scope, and gz check runs it as its own bound step."""

    def _invoke(self, rows: list[dict]):
        from gzkit.cli import main
        from tests.commands.common import CliRunner, _quick_init

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            Path("data").mkdir(exist_ok=True)
            Path(BASELINE_RELPATH).write_text(
                json.dumps({"_doc": "fixture", "sites": rows}), encoding="utf-8"
            )
            return runner.invoke(main, ["validate", "--id-seam"])

    def test_a_dead_baseline_row_is_a_policy_breach_through_the_flag(self) -> None:
        result = self._invoke(
            [{"file": "src/gzkit/gone.py", "symbol": "f", "kind": "ADR", "sites": 1}]
        )
        self.assertEqual(result.exit_code, 3, result.output)
        self.assertIn("src/gzkit/gone.py", result.output)

    def test_an_exact_baseline_passes_through_the_flag(self) -> None:
        result = self._invoke([])
        self.assertEqual(result.exit_code, 0, result.output)

    def test_the_audit_is_part_of_the_packages_declared_surface(self) -> None:
        from gzkit.governance import trust_audits

        self.assertIn("audit_id_seam", trust_audits.__all__)
        self.assertIs(trust_audits.audit_id_seam, audit_id_seam)

    def test_gz_check_shells_the_scope_as_its_own_bound_step(self) -> None:
        from unittest.mock import patch

        from gzkit import quality
        from gzkit.commands.quality import _STEP_GUARD_META, _build_check_steps
        from gzkit.qc_binding import build_qc_registry

        runner = dict(_build_check_steps())["Identity seam"]
        with patch.object(quality, "run_command", return_value="ran") as shelled:
            self.assertEqual(runner(_REPO), "ran")
        self.assertEqual(shelled.call_args.args[0], "uv run gz validate --id-seam")
        self.assertEqual(_STEP_GUARD_META["Identity seam"][0], "id-seam")
        step = {s.name: s for s in build_qc_registry()}["Identity seam"]
        self.assertEqual((step.binding, step.subject), ("bound", "src/"))


class TestNegativeControls(unittest.TestCase):
    def _record(self, claim: str):
        from gzkit.enforcement import production_enforcement_registry

        return {r.claim_id: r for r in production_enforcement_registry()}[claim]

    def test_the_catch_control_catches_the_new_site_and_names_its_exemption(self) -> None:
        from gzkit.enforcement import _run_single_claim

        record = self._record("identity-seam")
        result = _run_single_claim(record)
        self.assertEqual(result.outcome, "PASS", result.message)
        self.assertEqual(record.exempts, "identity-seam-baselined")
        self.assertIsNotNone(record.population)

    def test_the_admit_control_admits_the_baselined_site(self) -> None:
        from gzkit.enforcement import EXEMPTS_NONE, _run_single_claim

        record = self._record("identity-seam-baselined")
        result = _run_single_claim(record)
        self.assertEqual(result.outcome, "PASS", result.message)
        self.assertEqual(record.exempts, EXEMPTS_NONE)
        self.assertIsNotNone(record.population)

    def test_the_entrypoints_report_nothing_when_the_decoy_fires(self) -> None:
        """With the baseline emptied, the held site fires too: no catch, and no admit."""
        from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            (root / ".gzkit" / "ledger.jsonl").write_text("", encoding="utf-8")
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            for name, kind in (("held", "OBPI"), ("fresh", "REQ")):
                (src / f"{name}.py").write_text(
                    f'import re\n\n\ndef {name}():\n    return re.compile(r"{kind}-\\d+")\n',
                    encoding="utf-8",
                )
            (root / "data").mkdir()
            (root / BASELINE_RELPATH).write_text(json.dumps({"sites": []}), encoding="utf-8")
            self.assertEqual(ep._ep_id_seam(root), [])
            self.assertEqual(ep._ep_id_seam_admits_baselined(root), 0)


if __name__ == "__main__":
    unittest.main()
