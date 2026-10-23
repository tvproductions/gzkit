"""``gz validate --complexity-ceiling``: the Lizard C/C/C gate (RO-9 tranche 4, GHI #1183).

`docs/governance/harbor-ro9-astral-toolchain.md` § Ruled for tranche 4. Xenon's
C/C/C contract is re-derived over Lizard's native function scores: the largest
function, each module's mean and the function-weighted overall mean are each
held at the cyclomatic ceiling Ruff reads (``[tool.ruff.lint.mccabe]
max-complexity``). A function Lizard does not measure is a refused partial
measurement, never a silent pass.
"""

from __future__ import annotations

import contextlib
import io
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from gzkit.cli.main import main
from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.complexity_ceiling import (
    audit_complexity_ceiling,
    cyclomatic_ceiling,
    measure_ceiling,
    measure_cognitive,
)


def _branches(name: str, count: int) -> str:
    """Return a function whose cyclomatic complexity is ``count + 1``."""
    body = "".join(f"    if x == {i}:\n        return {i}\n" for i in range(count))
    return f"def {name}(x):\n{body}    return -1\n"


_PYPROJECT = """\
[project]
name = "demo"
version = "0.1.0"

[build-system]
requires = ["uv_build>=0.13.1,<0.14"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-name = "demo"
module-root = "src"

[tool.ruff.lint.mccabe]
max-complexity = 5
"""


class MeasureCeilingTest(unittest.TestCase):
    def test_function_at_the_ceiling_passes(self) -> None:
        self.assertEqual(measure_ceiling({"m.py": _branches("f", 4)}, 5.0), [])

    def test_function_over_the_ceiling_fails_with_its_score(self) -> None:
        findings = measure_ceiling({"m.py": _branches("f", 5)}, 5.0)
        self.assertEqual(len([f for f in findings if f.kind == "function"]), 1)
        self.assertIn("f", findings[0].message)
        self.assertIn("6", findings[0].message)

    def test_module_mean_over_the_ceiling_fails_without_a_function_breach(self) -> None:
        # Every function sits at 5 and the ceiling is 4.5: each function breaches
        # too, so isolate the mean by asserting it is reported as its own kind.
        source = _branches("a", 4) + _branches("b", 4)
        kinds = {f.kind for f in measure_ceiling({"m.py": source}, 4.5)}
        self.assertIn("module-mean", kinds)
        self.assertIn("overall-mean", kinds)

    def test_overall_mean_is_weighted_by_function_count(self) -> None:
        # Module one: a single function at 5. Module two: three at 1. The mean of
        # the module means would be 3.0; the function-weighted mean is 2.0.
        files = {
            "one.py": _branches("a", 4),
            "two.py": "".join(f"def b{i}():\n    return 1\n" for i in range(3)),
        }
        self.assertNotIn("overall-mean", {f.kind for f in measure_ceiling(files, 2.0)})
        self.assertIn("overall-mean", {f.kind for f in measure_ceiling(files, 1.9)})

    def test_an_unmeasured_function_is_a_refused_partial_measurement(self) -> None:
        findings = measure_ceiling({"m.py": "def f(x): return x\n"}, 5.0)
        self.assertEqual([f.kind for f in findings], ["unmeasured"])

    def test_an_ellipsis_stub_carries_no_decision_and_is_not_refused(self) -> None:
        source = "class P:\n    def f(self) -> None: ...\n"
        self.assertEqual(measure_ceiling({"m.py": source}, 5.0), [])

    def test_a_documented_ellipsis_stub_is_not_refused(self) -> None:
        source = 'class P:\n    def f(self) -> None: """Say what f does."""; ...\n'
        self.assertEqual(measure_ceiling({"m.py": source}, 5.0), [])

    def test_an_inline_body_that_is_not_a_stub_is_refused(self) -> None:
        source = 'class P:\n    def f(self) -> int: """Doc."""; return 1\n'
        self.assertEqual([f.kind for f in measure_ceiling({"m.py": source}, 5.0)], ["unmeasured"])

    def test_unparseable_source_is_refused(self) -> None:
        findings = measure_ceiling({"m.py": "def f(:\n"}, 5.0)
        self.assertEqual([f.kind for f in findings], ["unparseable"])

    def test_a_module_with_no_functions_adds_no_denominator(self) -> None:
        files = {"empty.py": "X = 1\n", "m.py": _branches("f", 4)}
        self.assertEqual(measure_ceiling(files, 5.0), [])


class CyclomaticCeilingTest(unittest.TestCase):
    def test_reads_ruffs_max_complexity(self) -> None:
        pyproject = {"tool": {"ruff": {"lint": {"mccabe": {"max-complexity": 20}}}}}
        self.assertEqual(cyclomatic_ceiling(pyproject), 20.0)

    def test_an_undeclared_ceiling_is_none(self) -> None:
        self.assertIsNone(cyclomatic_ceiling({}))


class AuditComplexityCeilingTest(unittest.TestCase):
    def _tmp(self) -> Path:
        handle = tempfile.TemporaryDirectory()
        self.addCleanup(handle.cleanup)
        return Path(handle.name)

    def _project(self, module_source: str) -> Path:
        tmp = self._tmp()
        (tmp / "pyproject.toml").write_text(_PYPROJECT, encoding="utf-8")
        package = tmp / "src" / "demo"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "core.py").write_text(textwrap.dedent(module_source), encoding="utf-8")
        return tmp

    def test_clean_package_passes(self) -> None:
        self.assertEqual(audit_complexity_ceiling(self._project(_branches("f", 4))), [])

    def test_breach_in_a_shipped_module_is_an_error_naming_the_file(self) -> None:
        errors = audit_complexity_ceiling(self._project(_branches("f", 5)))
        function_errors = [e for e in errors if e.artifact == "src/demo/core.py"]
        self.assertEqual(len(function_errors), 2)  # the function, and its one-function module
        self.assertTrue(all(e.type == "complexity_ceiling" for e in errors))

    def test_each_error_names_the_rule_and_a_runnable_next_step(self) -> None:
        # .gzkit/rules/guardrail-feedback-prose.md: what failed, why, what to run.
        for error in audit_complexity_ceiling(self._project(_branches("f", 5))):
            self.assertIn("GHI #1183", error.message)
            self.assertIn("uv run gz validate --complexity-ceiling", error.message)

    def test_an_undeclared_ceiling_is_refused_naming_where_to_declare_it(self) -> None:
        root = self._project(_branches("f", 1))
        pyproject = root / "pyproject.toml"
        text = pyproject.read_text(encoding="utf-8")
        pyproject.write_text(text.split("[tool.ruff.lint.mccabe]")[0], encoding="utf-8")
        errors = audit_complexity_ceiling(root)
        self.assertEqual([e.artifact for e in errors], ["pyproject.toml"])
        self.assertIn("[tool.ruff.lint.mccabe] max-complexity", errors[0].message)

    def test_a_project_that_ships_no_wheel_is_clean(self) -> None:
        self.assertEqual(audit_complexity_ceiling(self._tmp()), [])


class GzValidateRunsTheScopeTest(unittest.TestCase):
    """`gz validate --complexity-ceiling` reaches the audit and treats a finding as a breach."""

    def _validate(self, findings: list[ValidationError]) -> tuple[int, str]:
        out = io.StringIO()
        with (
            mock.patch(
                "gzkit.governance.trust_audits.audit_complexity_ceiling", return_value=findings
            ) as audit,
            # An open MX hangar demotes ERROR-level scopes to advisory; grade the
            # scope as it stands outside one, where its findings block.
            mock.patch("gzkit.mx.checkpoint.blocks", return_value=True),
            contextlib.redirect_stdout(out),
            contextlib.redirect_stderr(out),
        ):
            try:
                code = main(["validate", "--complexity-ceiling"])
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
        self.assertEqual(audit.call_count, 1, out.getvalue())
        return code, out.getvalue()

    def test_a_clean_tree_passes_the_scope(self) -> None:
        code, output = self._validate([])
        self.assertEqual(code, 0, output)
        self.assertIn("complexity_ceiling", output)

    def test_a_finding_is_a_policy_breach(self) -> None:
        """Exit 3, the CLI doctrine's policy-breach code (`.gzkit/rules/cli.md`)."""
        finding = ValidationError(type="complexity_ceiling", artifact="m.py", message="m")
        code, output = self._validate([finding])
        self.assertEqual(code, 3, output)


class TheScopeIsWiredIntoGzCheckTest(unittest.TestCase):
    def test_gz_check_runs_the_complexity_ceiling_audit(self) -> None:
        from gzkit.commands.quality import _build_check_steps  # noqa: PLC0415
        from gzkit.quality import run_complexity_ceiling_audit  # noqa: PLC0415

        self.assertIn(("Complexity ceiling", run_complexity_ceiling_audit), _build_check_steps())

    def test_the_step_runs_the_validate_scope(self) -> None:
        from gzkit import quality  # noqa: PLC0415

        sentinel = object()
        with mock.patch.object(quality, "run_command", return_value=sentinel) as run:
            result = quality.run_complexity_ceiling_audit(Path("."))
        self.assertIs(result, sentinel)
        self.assertEqual(run.call_args.args[0], "uv run gz validate --complexity-ceiling")

    def test_the_step_is_bound_at_error_severity(self) -> None:
        from gzkit.commands.quality import _STEP_GUARD_META  # noqa: PLC0415
        from gzkit.mx import levels  # noqa: PLC0415

        self.assertEqual(
            _STEP_GUARD_META["Complexity ceiling"], ("complexity-ceiling", levels.ERROR)
        )

    def test_the_qc_binding_audit_accepts_the_step(self) -> None:
        from gzkit.governance.trust_audits.qc_binding import audit_qc_binding  # noqa: PLC0415

        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            errors = audit_qc_binding(Path("."))
        findings = [f"{e.artifact} {e.message}" for e in errors]
        self.assertFalse([f for f in findings if "Complexity ceiling" in f], findings)


class TheNegativeControlDiscriminatesTest(unittest.TestCase):
    """The registered control reports the planted breach and stays silent on the decoy."""

    def setUp(self) -> None:
        from gzkit.governance.trust_audits import _qc_negative_controls as nc  # noqa: PLC0415

        def mkroot(slug: str) -> Path:
            tmp = tempfile.TemporaryDirectory(prefix=f"gzkit-qc-nc-{slug}-")
            self.addCleanup(tmp.cleanup)
            return Path(tmp.name)

        patcher = mock.patch.object(nc, "_mkroot", side_effect=mkroot)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_the_control_catches_only_the_function_over_the_ceiling(self) -> None:
        from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep  # noqa: PLC0415
        from gzkit.governance.trust_audits import _qc_negative_controls as nc  # noqa: PLC0415

        caught = ep._ep_complexity_ceiling(nc._build_complexity_ceiling())
        self.assertTrue(caught)
        self.assertTrue(all(e.artifact == "src/nc/over.py" for e in caught), caught)
        self.assertTrue(any("over: cyclomatic 4 > 3" in e.message for e in caught), caught)

    def test_the_control_reports_nothing_when_the_decoy_fires(self) -> None:
        from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep  # noqa: PLC0415
        from gzkit.governance.trust_audits import _qc_negative_controls as nc  # noqa: PLC0415

        root = nc._build_complexity_ceiling()
        pyproject = root / "pyproject.toml"
        text = pyproject.read_text(encoding="utf-8")
        pyproject.write_text(text.replace("max-complexity = 3", "max-complexity = 2"), "utf-8")
        self.assertEqual(ep._ep_complexity_ceiling(root), [])

    def test_the_claim_is_registered_with_its_judgments(self) -> None:
        from gzkit.enforcement import POPULATION_NONE  # noqa: PLC0415
        from gzkit.governance.trust_audits._qc_claim_exemptions import (  # noqa: PLC0415
            EXEMPTS_NONE,
            QC_CLAIM_EXEMPTS,
        )
        from gzkit.governance.trust_audits._qc_claim_populations import (  # noqa: PLC0415
            QC_CLAIM_POPULATIONS,
        )
        from gzkit.governance.trust_audits._qc_negative_controls import (  # noqa: PLC0415
            _build_complexity_ceiling,
        )

        self.assertEqual(QC_CLAIM_EXEMPTS["complexity-ceiling"], EXEMPTS_NONE)
        self.assertEqual(QC_CLAIM_POPULATIONS["complexity-ceiling"], POPULATION_NONE)
        self.assertTrue(callable(_build_complexity_ceiling))


def _flat_ifs(name: str, count: int, indent: str = "") -> str:
    """Return a function whose cognitive complexity is ``count`` (one flat ``if`` each)."""
    body = "".join(f"{indent}    if x == {i}:\n{indent}        x += 1\n" for i in range(count))
    return f"{indent}def {name}(x):\n{body}{indent}    return x\n"


class MeasureCognitiveTest(unittest.TestCase):
    """The cognitive leg: a ceiling, less an exact shrink-only baseline (RO-9 tranche 4)."""

    def _kinds(self, files: dict[str, str], baseline: dict[tuple[str, str], int]) -> list[str]:
        return [f.kind for f in measure_cognitive(files, 2, baseline)]

    def test_a_function_at_the_ceiling_passes(self) -> None:
        self.assertEqual(self._kinds({"m.py": _flat_ifs("f", 2)}, {}), [])

    def test_a_function_over_the_ceiling_fails_with_its_score(self) -> None:
        findings = measure_cognitive({"m.py": _flat_ifs("f", 3)}, 2, {})
        self.assertEqual([f.kind for f in findings], ["cognitive"])
        self.assertIn("m.py:1 f: cognitive 3 > 2", findings[0].message)

    def test_a_held_function_at_its_baseline_score_passes(self) -> None:
        self.assertEqual(self._kinds({"m.py": _flat_ifs("f", 3)}, {("m.py", "f"): 3}), [])

    def test_a_held_function_that_worsens_fails_against_its_row(self) -> None:
        findings = measure_cognitive({"m.py": _flat_ifs("f", 4)}, 2, {("m.py", "f"): 3})
        self.assertEqual([f.kind for f in findings], ["cognitive"])
        self.assertIn("cognitive 4 > 3, its baseline row", findings[0].message)

    def test_a_row_above_its_function_must_be_lowered(self) -> None:
        findings = measure_cognitive({"m.py": _flat_ifs("f", 3)}, 2, {("m.py", "f"): 5})
        self.assertEqual([f.kind for f in findings], ["cognitive-held"])
        self.assertIn("at 5 and it now scores 3", findings[0].message)

    def test_a_row_whose_function_is_gone_is_dead(self) -> None:
        findings = measure_cognitive({"m.py": _flat_ifs("f", 1)}, 2, {("m.py", "g"): 3})
        self.assertEqual([f.kind for f in findings], ["cognitive-held"])
        self.assertIn("m.py g at 3 and it is gone", findings[0].message)

    def test_a_row_at_the_ceiling_holds_nothing_and_is_dead(self) -> None:
        self.assertEqual(
            self._kinds({"m.py": _flat_ifs("f", 2)}, {("m.py", "f"): 2}), ["cognitive-held"]
        )

    def test_a_method_is_keyed_by_its_qualified_name(self) -> None:
        source = "class C:\n" + _flat_ifs("m", 3, indent="    ")
        self.assertEqual(self._kinds({"m.py": source}, {("m.py", "C.m"): 3}), [])

    def test_a_name_defined_twice_is_held_at_its_higher_score(self) -> None:
        source = f"if X:\n{_flat_ifs('f', 3, '    ')}else:\n{_flat_ifs('f', 4, '    ')}"
        self.assertEqual(self._kinds({"m.py": source}, {("m.py", "f"): 4}), [])

    def test_a_module_that_does_not_parse_is_left_to_the_cyclomatic_leg(self) -> None:
        self.assertEqual(self._kinds({"m.py": "def f(:\n"}, {}), [])


class AuditCognitiveLegTest(unittest.TestCase):
    """The audit runs the cognitive leg only when `.gzkit.json` declares its ceiling."""

    def _project(self, module_source: str, gzkit_json: str | None) -> Path:
        handle = tempfile.TemporaryDirectory()
        self.addCleanup(handle.cleanup)
        root = Path(handle.name)
        (root / "pyproject.toml").write_text(_PYPROJECT, encoding="utf-8")
        package = root / "src" / "demo"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "core.py").write_text(module_source, encoding="utf-8")
        if gzkit_json is not None:
            (root / ".gzkit.json").write_text(gzkit_json, encoding="utf-8")
        return root

    def _baseline(self, root: Path, rows: str) -> None:
        (root / "data").mkdir()
        (root / "data" / "cognitive_complexity_baseline.json").write_text(
            f'{{"functions": [{rows}]}}', encoding="utf-8"
        )

    _DECLARED = '{"complexity": {"cognitive_ceiling": 2}}'
    _ROW = '{"file": "src/demo/core.py", "function": "f", "score": 3}'

    def test_an_undeclared_ceiling_leaves_cognitive_complexity_unchecked(self) -> None:
        self.assertEqual(audit_complexity_ceiling(self._project(_flat_ifs("f", 3), None)), [])

    def test_a_declared_ceiling_fails_a_function_over_it_with_recovery_prose(self) -> None:
        errors = audit_complexity_ceiling(self._project(_flat_ifs("f", 3), self._DECLARED))
        self.assertEqual([e.artifact for e in errors], ["src/demo/core.py"])
        # .gzkit/rules/guardrail-feedback-prose.md: what failed, why, what to run.
        self.assertIn("cognitive 3 > 2", errors[0].message)
        self.assertIn("RO-9 tranche 4", errors[0].message)
        self.assertIn("uv run gz validate --complexity-ceiling", errors[0].message)

    def test_the_baseline_file_holds_a_grandfathered_function(self) -> None:
        root = self._project(_flat_ifs("f", 3), self._DECLARED)
        self._baseline(root, self._ROW)
        self.assertEqual(audit_complexity_ceiling(root), [])

    def test_a_baseline_without_its_functions_list_is_malformed(self) -> None:
        root = self._project(_flat_ifs("f", 1), self._DECLARED)
        (root / "data").mkdir()
        (root / "data" / "cognitive_complexity_baseline.json").write_text("{}", encoding="utf-8")
        errors = audit_complexity_ceiling(root)
        self.assertEqual([e.artifact for e in errors], ["data/cognitive_complexity_baseline.json"])
        self.assertIn("malformed", errors[0].message)

    def test_a_row_held_twice_is_a_defect_in_the_baseline(self) -> None:
        root = self._project(_flat_ifs("f", 3), self._DECLARED)
        self._baseline(root, f"{self._ROW}, {self._ROW}")
        errors = audit_complexity_ceiling(root)
        self.assertEqual([e.artifact for e in errors], ["data/cognitive_complexity_baseline.json"])
        self.assertIn("twice", errors[0].message)


if __name__ == "__main__":
    unittest.main()
