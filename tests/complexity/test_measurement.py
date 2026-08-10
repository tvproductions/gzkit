"""Tests for the measurement orchestration entrypoint (OBPI-0.0.27-03).

Pins:

- :func:`measure_corpus` produces a structurally-valid baseline artifact
  when run under the stub harness.
- The path filter respects ``excluded_paths`` (REQ-02).
- A missing tool binary fails closed with
  :class:`MissingMeasurementToolError` (REQ-05).
- A corpus that cannot be loaded fails closed with
  :class:`CorpusLoaderError` (REQ-05).
- Every subprocess invocation is list-form with ``encoding="utf-8"``;
  ``shell=True`` is forbidden (REQ-07).
- No real network or git subprocess fires in the unit tier (REQ-09).
- ``pyproject.toml`` declares the three runtime deps with major-version
  pins (REQ-07).
"""

from __future__ import annotations

import ast
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.complexity.measurement import (
    CorpusLoaderError,
    MissingMeasurementToolError,
    WholeProjectMeasurementRejectedError,
    _apply_path_filter,
    measure_corpus,
)
from gzkit.models.exemplar import (
    ExcludedPath,
    ExemplarCorpus,
    ExemplarProject,
    load_corpus,
)
from gzkit.traceability import covers
from tests.complexity import (
    run_pipeline_into_dir,
    stub_corpus,
    stubbed_pipeline_environment,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MEASUREMENT_PATH = _REPO_ROOT / "src" / "gzkit" / "complexity" / "measurement.py"
_PYPROJECT_PATH = _REPO_ROOT / "pyproject.toml"


class TestMeasureCorpusSmoke(unittest.TestCase):
    """End-to-end shape: ``measure_corpus`` produces a valid baseline artifact."""

    @covers("REQ-0.0.27-03-01")
    def test_measure_corpus_smoke(self) -> None:
        """Stubbed pipeline yields per-project + cross-project distributions."""
        corpus = stub_corpus()
        with run_pipeline_into_dir(corpus) as out_dir:
            payload = json.loads((out_dir / "baseline.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["corpus_revision"], 1)
        self.assertEqual(payload["corpus_schema_version"], "1.0.0")
        self.assertEqual(len(payload["projects"]), 1)
        project = payload["projects"][0]
        self.assertEqual(project["name"], "fixture-alpha")
        metric_keys = [metric["metric_key"] for metric in project["metrics"]]
        self.assertIn("radon_cc", metric_keys)
        # The fixture canned radon_cc output -> 2 raw values per measured file.
        radon_cc = next(m for m in project["metrics"] if m["metric_key"] == "radon_cc")
        self.assertGreaterEqual(radon_cc["sample_count"], 1)
        # Cross-project block must list every canonical metric.
        cross_keys = [metric["metric_key"] for metric in payload["cross_project"]["metrics"]]
        self.assertIn("cohesion_lcom4", cross_keys)


class TestPathFilter(unittest.TestCase):
    """REQ-0.0.27-03-02: excluded paths are subtracted from measurement set."""

    @covers("REQ-0.0.27-03-02")
    def test_path_filter_excludes_excluded_glob(self) -> None:
        """``excluded.py`` is removed from the resolved-path tuple."""
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            (tree / "alpha.py").write_text("x = 1\n", encoding="utf-8")
            (tree / "excluded.py").write_text("y = 2\n", encoding="utf-8")
            project = ExemplarProject.model_validate(
                {
                    "name": "p",
                    "canonical_url": "https://example.invalid/p",
                    "commit_sha": "0" * 40,
                    "archetypal_cell": 1,
                    "cell_label": "x",
                    "included_paths": ("**/*.py",),
                    "excluded_paths_with_rationale": (
                        ExcludedPath(
                            glob="excluded.py",
                            exclusion_rationale="not relevant",
                        ),
                    ),
                    "path_filter_rationale": "fixture rationale",
                    "longevity_evidence": "fixture",
                    "maintenance_health_evidence": "fixture",
                    "practitioner_reputation_citation": "fixture",
                    "pure_python_loc_ratio": 1.0,
                    "craftsmanship_signal_narrative": "fixture",
                    "project_doctrine_fitness_narrative": "fixture",
                }
            )
            paths = _apply_path_filter(tree, project)
            names = {path.name for path in paths}
            self.assertIn("alpha.py", names)
            self.assertNotIn("excluded.py", names)


class TestFailClosedExitPaths(unittest.TestCase):
    """REQ-0.0.27-03-05: missing-binary + corpus-load failures fail closed."""

    @covers("REQ-0.0.27-03-05")
    def test_missing_binary_raises_named_error(self) -> None:
        """``shutil.which`` returning ``None`` raises ``MissingMeasurementToolError``."""
        with mock.patch(
            "gzkit.complexity.measurement.shutil.which",
            return_value=None,
        ):
            corpus = stub_corpus()
            with tempfile.TemporaryDirectory() as out:
                with self.assertRaises(MissingMeasurementToolError) as ctx:
                    measure_corpus(corpus, Path(out))
                # Tool name is preserved on the exception so the CLI can
                # surface a recovery hint without re-parsing the message.
                self.assertIn(ctx.exception.tool, {"radon", "lizard", "cohesion"})

    @covers("REQ-0.0.27-03-05")
    def test_corpus_loader_error_wraps_missing_path(self) -> None:
        """A non-existent corpus path surfaces as ``CorpusLoaderError``."""
        # The doctrine wraps OS / decode / Pydantic errors at the
        # corpus-loading boundary so callers can react to "the corpus
        # could not be loaded" without depending on which underlying
        # exception fired.  The wrapper lives in measurement.py because
        # measurement.py is the only consumer that owns the exit-3 path.
        with self.assertRaises(CorpusLoaderError):
            from gzkit.complexity.measurement import safe_load_corpus

            safe_load_corpus(Path("/nonexistent/path/that/does/not/exist.json"))

    def test_whole_project_measurement_is_rejected(self) -> None:
        """Empty ``included_paths`` raises ``WholeProjectMeasurementRejectedError``.

        Pydantic guards the include list at construction time
        (``min_length=1``); for the rejection-error branch we exercise the
        ``_apply_path_filter`` helper directly with a model bypass via
        ``model_construct`` so the corpus-authoring rejection contract is
        observable independent of the schema floor.
        """
        # model_construct skips validation so the include list can be
        # empty for the purposes of testing the rejection branch.
        project = ExemplarProject.model_construct(
            name="empty",
            canonical_url="https://example.invalid/empty",
            commit_sha="0" * 40,
            archetypal_cell=1,
            cell_label="x",
            included_paths=(),
            excluded_paths_with_rationale=(),
            path_filter_rationale="x",
            longevity_evidence="x",
            maintenance_health_evidence="x",
            practitioner_reputation_citation="x",
            pure_python_loc_ratio=1.0,
            craftsmanship_signal_narrative="x",
            project_doctrine_fitness_narrative="x",
        )
        with (
            tempfile.TemporaryDirectory() as tmp,
            self.assertRaises(WholeProjectMeasurementRejectedError),
        ):
            _apply_path_filter(Path(tmp), project)


class TestSubprocessInvocationDiscipline(unittest.TestCase):
    """REQ-0.0.27-03-07: subprocess calls are list-form, UTF-8, no shell."""

    @covers("REQ-0.0.27-03-07")
    def test_subprocess_invocation_is_list_form_and_utf8(self) -> None:
        """Captured ``subprocess.run`` calls all use list args + utf-8 encoding."""
        with (
            stubbed_pipeline_environment() as (_tree, spy),
            tempfile.TemporaryDirectory() as out,
        ):
            measure_corpus(
                stub_corpus(),
                Path(out),
                cache_root=Path(out) / "cache",
            )
        self.assertGreater(len(spy.calls), 0)
        for call in spy.calls:
            self.assertIsInstance(
                call["argv"],
                list,
                msg="subprocess.run must be invoked with list-form args",
            )
            kwargs = call["kwargs"]
            self.assertIs(kwargs.get("shell"), None)
            self.assertNotEqual(
                kwargs.get("shell"),
                True,
                msg="shell=True is forbidden by .claude/rules/cross-platform.md",
            )
            self.assertEqual(kwargs.get("encoding"), "utf-8")


class TestUnitTierIsolation(unittest.TestCase):
    """Brief Requirement 9: unit tier never clones a real repo.

    Discipline assertion — Requirement 9 is a process REQ in the brief's
    `## Requirements (FAIL-CLOSED)` section but is not an Acceptance Criterion,
    so no `@covers` decorator (the parity gate keys on Acceptance Criteria).
    """

    def test_no_real_clone_in_unit_tier(self) -> None:
        """Stub harness intercepts ``_resolve_tree`` so no ``git clone`` fires."""
        with (
            stubbed_pipeline_environment() as (_tree, spy),
            tempfile.TemporaryDirectory() as out,
        ):
            measure_corpus(
                stub_corpus(),
                Path(out),
                cache_root=Path(out) / "cache",
            )
        # No call's argv may begin with "git clone" — _resolve_tree is the
        # only site that would invoke git, and it is monkey-patched out.
        for call in spy.calls:
            argv = call["argv"]
            if argv and argv[0] == "git":
                self.fail(f"unit tier must not invoke git: argv={argv!r}")


class TestPyprojectDeclaresDeps(unittest.TestCase):
    """REQ-0.0.27-03-07: ``pyproject.toml`` declares the three pinned deps."""

    @covers("REQ-0.0.27-03-07")
    def test_pyproject_declares_three_deps_with_pins(self) -> None:
        """``radon``, ``lizard``, ``cohesion`` each appear with a major-version pin."""
        text = _PYPROJECT_PATH.read_text(encoding="utf-8")
        for dep in ("radon", "lizard", "cohesion"):
            pattern = rf'"{dep}>=\d+\.\d+,<\d+\.\d+"'
            self.assertRegex(
                text,
                pattern,
                msg=f"{dep} missing major-version pin in pyproject.toml dependencies",
            )

    def test_pyproject_cites_stdlib_first_named_departure(self) -> None:
        """The dep block carries the named-departure rationale comment."""
        text = _PYPROJECT_PATH.read_text(encoding="utf-8")
        self.assertIn("Stdlib-First", text)


class TestFunctionSizeDiscipline(unittest.TestCase):
    """REQ-0.0.27-03-10: every function in ``measurement.py`` <= 50 lines."""

    def test_function_size_discipline(self) -> None:
        """Parse the AST and assert no function exceeds the size limit."""
        source = _MEASUREMENT_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        oversized: list[tuple[str, int]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = node.end_lineno or node.lineno
                length = end - node.lineno + 1
                if length > 50:
                    oversized.append((node.name, length))
        self.assertEqual(
            oversized,
            [],
            msg=f"measurement.py functions over 50 lines: {oversized!r}",
        )

    def test_module_size_discipline(self) -> None:
        """The module respects the 600-line module ceiling."""
        line_count = len(_MEASUREMENT_PATH.read_text(encoding="utf-8").splitlines())
        self.assertLessEqual(line_count, 600)


class TestNoOperatorPiiInComplexityPackage(unittest.TestCase):
    """REQ-0.0.27-03-12: never include the operator's personal email."""

    def test_no_operator_pii_in_complexity_package(self) -> None:
        """No file under ``src/gzkit/complexity`` or ``tests/complexity`` carries the literal."""
        # The literal lives in agent context only; if it appears in any
        # repo-bound artifact under the OBPI's allow-listed paths, the
        # AGENTS.md § Local Agent Rules covenant has been violated.
        forbidden = "ahuimanu" + "@gmail.com"
        scan_roots = (
            _REPO_ROOT / "src" / "gzkit" / "complexity",
            _REPO_ROOT / "tests" / "complexity",
        )
        offenders: list[Path] = []
        for root in scan_roots:
            for path in root.rglob("*.py"):
                if forbidden in path.read_text(encoding="utf-8"):
                    offenders.append(path)
        self.assertEqual(offenders, [], msg=f"operator PII leaked to {offenders!r}")


class TestCorpusLoaderHelper(unittest.TestCase):
    """Defensive tests for the loader-error wrapper used by the CLI surface."""

    def test_safe_load_corpus_round_trips_a_real_corpus(self) -> None:
        """``safe_load_corpus`` returns the same payload as ``load_corpus``."""
        from gzkit.complexity.measurement import safe_load_corpus

        corpus_path = _REPO_ROOT / "data" / "exemplar_corpus.json"
        loaded = safe_load_corpus(corpus_path)
        self.assertIsInstance(loaded, ExemplarCorpus)
        self.assertEqual(loaded, load_corpus(corpus_path))

    def test_safe_load_corpus_wraps_invalid_json(self) -> None:
        """Invalid JSON in the corpus path surfaces as ``CorpusLoaderError``."""
        from gzkit.complexity.measurement import safe_load_corpus

        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "bad.json"
            broken.write_text("{not valid json", encoding="utf-8")
            with self.assertRaises(CorpusLoaderError):
                safe_load_corpus(broken)


class TestSubprocessHasNoShellTrue(unittest.TestCase):
    """Static guard: no source line inside measurement.py opts into shell=True."""

    def test_no_shell_true_in_measurement_source(self) -> None:
        """Defense in depth: REQ-07 is also a static-source guarantee."""
        source = _MEASUREMENT_PATH.read_text(encoding="utf-8")
        self.assertNotRegex(source, r"shell\s*=\s*True")

    def test_subprocess_calls_use_list_form_in_source(self) -> None:
        """Every ``subprocess.run`` call passes a list literal as its first arg."""
        source = _MEASUREMENT_PATH.read_text(encoding="utf-8")
        # All subprocess.run invocations should open with `[` for list form.
        # The regex tolerates whitespace + newline between `(` and `[`.
        for match in re.finditer(r"subprocess\.run\s*\(", source):
            tail = source[match.end() : match.end() + 80]
            self.assertTrue(
                tail.lstrip().startswith("["),
                msg=f"subprocess.run not list-form near: {tail!r}",
            )


class TestLizardCohesionParserArgvRegression(unittest.TestCase):
    """GHI #398: lizard CSV mode and cohesion ``-d``/file produced silent zeros.

    Lizard 1.22.1's default ``--csv`` layout does not include nesting depth;
    the ``-End`` extension flag is required to surface ND as the trailing
    column.  Cohesion's ``-d`` flag is the directory mode; passing a file
    to it returns empty stdout and the parser silently records sample_count
    of zero.  Both cases were structurally invisible at the OBPI-03 test
    tier because the canned subprocess outputs accidentally satisfied the
    parser shape.  These argv-level regressions pin the call shape so a
    flag regression is caught at unit test time.
    """

    @covers("REQ-0.0.27-03-04")
    def test_lizard_argv_carries_nd_extension(self) -> None:
        """Captured lizard argv contains ``-End`` so ND is emitted as the 12th column."""
        with (
            stubbed_pipeline_environment() as (_tree, spy),
            tempfile.TemporaryDirectory() as out,
        ):
            measure_corpus(stub_corpus(), Path(out), cache_root=Path(out) / "cache")
        lizard_calls = [c for c in spy.calls if c["argv"] and c["argv"][0] == "lizard"]
        self.assertGreater(len(lizard_calls), 0, msg="no lizard subprocess calls captured")
        for call in lizard_calls:
            self.assertIn(
                "-End",
                call["argv"],
                msg=f"lizard argv missing -End extension flag: {call['argv']!r}",
            )

    @covers("REQ-0.0.27-03-04")
    def test_cohesion_argv_uses_files_flag_not_directory(self) -> None:
        """Captured cohesion argv carries ``-f`` and never ``-d``."""
        with (
            stubbed_pipeline_environment() as (_tree, spy),
            tempfile.TemporaryDirectory() as out,
        ):
            measure_corpus(stub_corpus(), Path(out), cache_root=Path(out) / "cache")
        cohesion_calls = [c for c in spy.calls if c["argv"] and c["argv"][0] == "cohesion"]
        self.assertGreater(len(cohesion_calls), 0, msg="no cohesion subprocess calls captured")
        for call in cohesion_calls:
            self.assertIn(
                "-f",
                call["argv"],
                msg=f"cohesion argv missing -f files flag: {call['argv']!r}",
            )
            self.assertNotIn(
                "-d",
                call["argv"],
                msg=f"cohesion argv must not use -d directory flag on a file: {call['argv']!r}",
            )


class TestLizardCohesionRealParserOutput(unittest.TestCase):
    """GHI #398 remediation: parsers populate ND and LCOM4 against real tool output.

    These tests deliberately bypass the subprocess stub harness and invoke
    the real ``lizard`` and ``cohesion`` binaries against tempdir fixtures.
    The discipline carve-out is intentional: the original defect was
    structurally invisible at the unit tier precisely because every test
    mocked the subprocess seam.  Verifying the parser-tool contract
    requires running the actual tools.  Fast (<1s on a typical workstation)
    because each fixture is a single small file.
    """

    @covers("REQ-0.0.27-03-04")
    def test_lizard_parser_extracts_nesting_depth_from_real_output(self) -> None:
        """A deeply nested function yields ``nesting_depth`` samples > 0."""
        from gzkit.complexity.measurement import _run_lizard

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested.py"
            target.write_text(
                "def deeply_nested():\n"
                "    for a in range(10):\n"
                "        for b in range(10):\n"
                "            for c in range(10):\n"
                "                for d in range(10):\n"
                "                    if a == b == c == d:\n"
                "                        return a\n",
                encoding="utf-8",
            )
            result = _run_lizard(target)
        self.assertGreater(
            len(result["nesting_depth"]),
            0,
            msg="nesting_depth list must contain at least one sample for a real file",
        )
        self.assertGreater(
            max(result["nesting_depth"]),
            0,
            msg="deepest function's nesting depth must exceed zero (5 control levels in fixture)",
        )

    @covers("REQ-0.0.27-03-04")
    def test_cohesion_parser_extracts_lcom4_from_real_output(self) -> None:
        """A class fixture file yields at least one ``cohesion_lcom4`` sample."""
        from gzkit.complexity.measurement import _run_cohesion

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "klass.py"
            target.write_text(
                "class Sample:\n"
                "    def __init__(self):\n"
                "        self.x = 1\n"
                "    def use_x(self):\n"
                "        return self.x\n",
                encoding="utf-8",
            )
            result = _run_cohesion(target)
        self.assertGreater(
            len(result),
            0,
            msg="cohesion lcom4 list must contain at least one sample for a class file",
        )


if __name__ == "__main__":  # pragma: no cover - convenience runner
    unittest.main()


__all__: tuple[str, ...] = ()
