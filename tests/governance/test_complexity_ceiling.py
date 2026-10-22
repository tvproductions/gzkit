"""``gz validate --complexity-ceiling``: the Lizard C/C/C gate (RO-9 tranche 4, GHI #1183).

`docs/governance/harbor-ro9-astral-toolchain.md` § Ruled for tranche 4. Xenon's
C/C/C contract is re-derived over Lizard's native function scores: the largest
function, each module's mean and the function-weighted overall mean are each
held at the cyclomatic ceiling Ruff reads (``[tool.ruff.lint.mccabe]
max-complexity``). A function Lizard does not measure is a refused partial
measurement, never a silent pass.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.complexity_ceiling import (
    audit_complexity_ceiling,
    cyclomatic_ceiling,
    measure_ceiling,
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


if __name__ == "__main__":
    unittest.main()
