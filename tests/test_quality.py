"""Tests for gzkit quality module."""

import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit import quality
from gzkit.commands.quality import _test_name_from_record
from gzkit.quality import (
    QualityResult,
    run_adr_path_contract_lint,
    run_command,
    run_skill_audit,
    run_tests,
)
from gzkit.triangle import EdgeType, LinkageRecord, VertexRef, VertexType


class TestObpiTestNameResolution(unittest.TestCase):
    """`gz test --obpi` must hand unittest dotted names, not file paths (GHI #302)."""

    def test_decorator_form_returns_module_dot_qualname(self) -> None:
        """Decorator-form @covers yields ``<module>.<TestClass>.<method>``."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            test_file = root / "tests" / "commands" / "test_foo.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("# placeholder\n", encoding="utf-8")

            record = LinkageRecord(
                source=VertexRef(
                    vertex_type=VertexType.TEST,
                    identifier="TestFoo.test_bar",
                    location=str(test_file),
                    line=10,
                ),
                target=VertexRef(vertex_type=VertexType.SPEC, identifier="REQ-0.0.21-02-01"),
                edge_type=EdgeType.COVERS,
                evidence_path=str(test_file),
                evidence_line=9,
            )
            self.assertEqual(
                _test_name_from_record(record, root),
                "tests.commands.test_foo.TestFoo.test_bar",
            )

    def test_comment_form_returns_dotted_module_only(self) -> None:
        """Docstring/comment-form @covers (identifier == file path) yields module only."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            test_file = root / "tests" / "test_config.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("# placeholder\n", encoding="utf-8")

            record = LinkageRecord(
                source=VertexRef(
                    vertex_type=VertexType.TEST,
                    identifier=str(test_file),
                    location=str(test_file),
                    line=39,
                ),
                target=VertexRef(vertex_type=VertexType.SPEC, identifier="REQ-0.0.21-02-01"),
                edge_type=EdgeType.COVERS,
                evidence_path=str(test_file),
                evidence_line=39,
            )
            self.assertEqual(_test_name_from_record(record, root), "tests.test_config")

    def test_missing_location_returns_none(self) -> None:
        """A record without a source location cannot anchor a unittest name."""
        record = LinkageRecord(
            source=VertexRef(vertex_type=VertexType.TEST, identifier="x", location=None, line=None),
            target=VertexRef(vertex_type=VertexType.SPEC, identifier="REQ-0.0.21-02-01"),
            edge_type=EdgeType.COVERS,
            evidence_path=None,
            evidence_line=None,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertIsNone(_test_name_from_record(record, Path(tmpdir)))


class TestQualityResult(unittest.TestCase):
    """Tests for QualityResult dataclass."""

    def test_to_dict(self) -> None:
        """Result converts to dictionary."""
        result = QualityResult(
            success=True,
            command="test command",
            stdout="output",
            stderr="",
            returncode=0,
        )
        d = result.to_dict()
        self.assertEqual(d["success"], True)
        self.assertEqual(d["command"], "test command")
        self.assertEqual(d["returncode"], 0)


class TestRunCommand(unittest.TestCase):
    """Tests for command execution."""

    def test_successful_command(self) -> None:
        """Successful command returns success=True."""
        result = run_command([sys.executable, "-c", "print('hello')"])
        self.assertTrue(result.success)
        self.assertIn("hello", result.stdout)
        self.assertEqual(result.returncode, 0)

    def test_failed_command(self) -> None:
        """Failed command returns success=False."""
        result = run_command([sys.executable, "-c", "import sys; sys.exit(1)"])
        self.assertFalse(result.success)
        self.assertEqual(result.returncode, 1)

    def test_command_with_cwd(self) -> None:
        """Command runs in specified directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_command(
                [sys.executable, "-c", "import os; print(os.getcwd())"],
                cwd=Path(tmpdir),
            )
            self.assertTrue(result.success)
            self.assertEqual(Path(result.stdout.strip()).resolve(), Path(tmpdir).resolve())

    def test_string_command_is_shlex_split(self) -> None:
        """String commands are tokenized via shlex, not handed to a shell (GHI #415)."""
        import shlex as _shlex

        result = run_command(f"{_shlex.quote(sys.executable)} --version")
        self.assertTrue(result.success)
        # Python --version emits "Python X.Y.Z" to stdout (3.4+) or stderr (<3.4).
        combined = result.stdout + result.stderr
        self.assertIn("Python", combined)

    def test_no_shell_metacharacter_interpretation(self) -> None:
        """Shell metacharacters in argv tokens are passed literal (GHI #415).

        Under ``shell=True``, ``;`` and ``$VAR`` would be parsed by the shell
        and could chain commands or expand environment variables outside the
        program's control. The governance gate runner must not expose that
        attack surface — argv tokens are forwarded literally to the program.
        """
        sentinel = "$HOME;injected_marker"
        result = run_command(
            [
                sys.executable,
                "-c",
                "import sys; sys.stdout.write(sys.argv[1])",
                sentinel,
            ]
        )
        self.assertTrue(result.success)
        # The full sentinel echoes verbatim — no env-var expansion, no chain.
        self.assertEqual(result.stdout, sentinel)

    def test_child_environment_forces_utf8_io(self) -> None:
        """The child receives PYTHONIOENCODING=utf-8 so its own stdout is UTF-8.

        Write-side companion of the GHI #582 read-side fix (GHI #661): a spawned
        Python child (behave's pretty formatter, unittest, mkdocs) picks a
        locale-dependent stdout encoding when its output is piped. On a
        non-UTF-8 console (Windows cp1252) it then crashes with
        UnicodeEncodeError writing a non-ASCII glyph — before run_command's
        errors="replace" capture ever sees the bytes. Forcing PYTHONIOENCODING
        in the child env makes the child's sys.stdout UTF-8 regardless of locale.
        """
        result = run_command(
            [sys.executable, "-c", "import os; print(os.environ.get('PYTHONIOENCODING'))"]
        )
        self.assertTrue(result.success)
        self.assertEqual(result.stdout.strip().lower(), "utf-8")

    def test_child_can_emit_non_ascii_glyph(self) -> None:
        """A child emitting U+2713 (behave's check-mark) round-trips intact.

        This is the concrete crash shape from GHI #661 — behave's pretty
        formatter writes U+2713. With UTF-8 child stdio the glyph is written and
        captured cleanly rather than raising UnicodeEncodeError in the child.
        """
        result = run_command([sys.executable, "-c", "print('\\u2713 done')"])
        self.assertTrue(result.success)
        self.assertIn("✓", result.stdout)


class TestQualityHasNoShellTrue(unittest.TestCase):
    """Static guard: src/gzkit/quality.py never opts into shell=True (GHI #415).

    Mirrors the defense-in-depth pattern from
    ``tests/complexity/test_measurement.py::TestSubprocessHasNoShellTrue`` —
    the runtime test asserts the semantic, this test asserts the surface.
    Closes the class of failure named in GHI #415 across the whole module,
    not just the single ``run_command`` site that surfaced it.
    """

    def test_no_shell_true_in_quality_source(self) -> None:
        """No source line in quality.py opts into shell=True."""
        source = Path(quality.__file__).read_text(encoding="utf-8")
        self.assertNotRegex(source, r"shell\s*=\s*True")

    def test_subprocess_run_uses_non_shell_form(self) -> None:
        """Every ``subprocess.run`` call in quality.py is shell=False (default)."""
        source = Path(quality.__file__).read_text(encoding="utf-8")
        for match in re.finditer(r"subprocess\.run\s*\(", source):
            tail = source[match.end() : match.end() + 400]
            # Default is shell=False; explicit shell=True would surface above.
            self.assertNotRegex(
                tail,
                r"shell\s*=\s*True",
                msg=f"subprocess.run with shell=True near: {tail[:120]!r}",
            )


class TestSkillAuditQualityIntegration(unittest.TestCase):
    """Tests for quality integration command wiring."""

    def test_run_skill_audit_uses_non_strict_default_command(self) -> None:
        """run_skill_audit should call CLI without --strict for default check behavior."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_command") as mock_run_command,
        ):
            mock_run_command.return_value = QualityResult(
                success=True,
                command="uv run gz skill audit",
                stdout="ok",
                stderr="",
                returncode=0,
            )
            run_skill_audit(Path(tmpdir))
            mock_run_command.assert_called_once_with(
                "uv run gz skill audit",
                cwd=Path(tmpdir),
            )


class TestTestRunnerBuffersPassingOutput(unittest.TestCase):
    """The test tier must not replay passing tests' fail-closed prose (GHI #723).

    Negative-path tests deliberately trigger fail-closed surfaces, and
    `.gzkit/rules/guardrail-feedback-prose.md` requires those surfaces to emit
    rich, alarming, actionable prose. When such a test PASSES, that prose still
    landed in the console, so a CI log for a run with one real failure carried 26
    error-shaped lines. Triage then targets the loudest line, which is a fixture:
    twice in two sessions the proposed remedy would have disabled a negative
    control rather than fixed a defect.

    `--buffer` is the stdlib-shaped answer (`unittest-parallel` exposes the same
    flag as `unittest`): output is captured per test and replayed ONLY for tests
    that fail or error. The assertion is on the runner's command contract because
    that is where the property lives — a passing suite has, by construction, no
    observable output to assert on.
    """

    def _captured_command(self) -> str:
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_command") as mock_run_command,
        ):
            mock_run_command.return_value = QualityResult(
                success=True, command="x", stdout="", stderr="", returncode=0
            )
            run_tests(Path(tmpdir))
            mock_run_command.assert_called_once()
            return str(mock_run_command.call_args.args[0])

    def test_runner_buffers_test_output(self) -> None:
        self.assertIn(
            "--buffer",
            self._captured_command(),
            msg="the test tier replays passing tests' fail-closed prose into CI logs",
        )

    def test_runner_still_uses_the_parallel_accelerator(self) -> None:
        """Negative control: buffering must not cost the parallel runner (GHI #512)."""
        command = self._captured_command()
        self.assertIn("unittest-parallel", command)
        self.assertIn("-t . -s tests", command)


class TestCanonicalQualityPath(unittest.TestCase):
    """run_all_checks must include cli audit and preflight (#133, #139)."""

    @staticmethod
    def _ok(command: str) -> QualityResult:
        return QualityResult(success=True, command=command, stdout="ok", stderr="", returncode=0)

    def test_run_all_checks_invokes_cli_audit_and_preflight(self) -> None:
        """The canonical path must wire both workflow-integrity checks."""
        from gzkit.quality import run_all_checks

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_lint", return_value=self._ok("lint")),
            patch("gzkit.quality.run_format_check", return_value=self._ok("format")),
            patch("gzkit.quality.run_typecheck", return_value=self._ok("typecheck")),
            patch("gzkit.quality.run_tests", return_value=self._ok("test")),
            patch("gzkit.quality.run_behave", return_value=self._ok("behave")),
            patch("gzkit.quality.run_skill_audit", return_value=self._ok("skill audit")),
            patch("gzkit.quality.run_parity_check", return_value=self._ok("parity")),
            patch("gzkit.quality.run_readiness_audit", return_value=self._ok("readiness")),
            patch("gzkit.quality.run_cli_audit", return_value=self._ok("cli audit")) as cli_audit,
            patch("gzkit.quality.run_preflight", return_value=self._ok("preflight")) as preflight,
            patch("gzkit.quality.run_drift_advisory") as drift,
        ):
            drift.return_value = None
            result = run_all_checks(Path(tmpdir))

            cli_audit.assert_called_once_with(Path(tmpdir))
            preflight.assert_called_once_with(Path(tmpdir))
            self.assertTrue(result.success)
            self.assertEqual(result.cli_audit.command, "cli audit")
            self.assertEqual(result.preflight.command, "preflight")

    def test_run_all_checks_fails_when_cli_audit_fails(self) -> None:
        """A failing CLI audit must flip overall success to False."""
        from gzkit.quality import run_all_checks

        failing = QualityResult(
            success=False,
            command="uv run gz cli audit",
            stdout="",
            stderr="gap",
            returncode=1,
        )
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_lint", return_value=self._ok("lint")),
            patch("gzkit.quality.run_format_check", return_value=self._ok("format")),
            patch("gzkit.quality.run_typecheck", return_value=self._ok("typecheck")),
            patch("gzkit.quality.run_tests", return_value=self._ok("test")),
            patch("gzkit.quality.run_behave", return_value=self._ok("behave")),
            patch("gzkit.quality.run_skill_audit", return_value=self._ok("skill audit")),
            patch("gzkit.quality.run_parity_check", return_value=self._ok("parity")),
            patch("gzkit.quality.run_readiness_audit", return_value=self._ok("readiness")),
            patch("gzkit.quality.run_cli_audit", return_value=failing),
            patch("gzkit.quality.run_preflight", return_value=self._ok("preflight")),
            patch("gzkit.quality.run_drift_advisory") as drift,
        ):
            drift.return_value = None
            result = run_all_checks(Path(tmpdir))
            self.assertFalse(result.success)

    def test_run_all_checks_fails_when_preflight_fails(self) -> None:
        """A failing preflight scan must flip overall success to False."""
        from gzkit.quality import run_all_checks

        failing = QualityResult(
            success=False,
            command="uv run gz preflight",
            stdout="",
            stderr="stale markers",
            returncode=1,
        )
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_lint", return_value=self._ok("lint")),
            patch("gzkit.quality.run_format_check", return_value=self._ok("format")),
            patch("gzkit.quality.run_typecheck", return_value=self._ok("typecheck")),
            patch("gzkit.quality.run_tests", return_value=self._ok("test")),
            patch("gzkit.quality.run_behave", return_value=self._ok("behave")),
            patch("gzkit.quality.run_skill_audit", return_value=self._ok("skill audit")),
            patch("gzkit.quality.run_parity_check", return_value=self._ok("parity")),
            patch("gzkit.quality.run_readiness_audit", return_value=self._ok("readiness")),
            patch("gzkit.quality.run_cli_audit", return_value=self._ok("cli audit")),
            patch("gzkit.quality.run_preflight", return_value=failing),
            patch("gzkit.quality.run_drift_advisory") as drift,
        ):
            drift.return_value = None
            result = run_all_checks(Path(tmpdir))
            self.assertFalse(result.success)

    def test_run_cli_audit_command_shape(self) -> None:
        """run_cli_audit calls the CLI directly."""
        from gzkit.quality import run_cli_audit

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_command") as mock_run_command,
        ):
            mock_run_command.return_value = self._ok("cli audit")
            run_cli_audit(Path(tmpdir))
            mock_run_command.assert_called_once_with(
                "uv run gz cli audit",
                cwd=Path(tmpdir),
            )

    def test_run_preflight_command_shape(self) -> None:
        """run_preflight calls the CLI without --apply (detection only)."""
        from gzkit.quality import run_preflight

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_command") as mock_run_command,
        ):
            mock_run_command.return_value = self._ok("preflight")
            run_preflight(Path(tmpdir))
            mock_run_command.assert_called_once_with(
                "uv run gz preflight",
                cwd=Path(tmpdir),
            )


class TestAdrPathContractLint(unittest.TestCase):
    """Tests for ADR path contract linting."""

    def test_passes_for_current_path_style(self) -> None:
        """Current ADR package paths pass lint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc = root / "docs/design/roadmap/ROADMAP.md"
            doc.parent.mkdir(parents=True, exist_ok=True)
            doc.write_text(
                "[ADR-0.2.0](../adr/pre-release/ADR-0.2.0-gate-verification/"
                "ADR-0.2.0-gate-verification.md)\n",
                encoding="utf-8",
            )

            result = run_adr_path_contract_lint(root)
            self.assertTrue(result.success)
            self.assertEqual(result.returncode, 0)

    def test_fails_for_legacy_series_folder_paths(self) -> None:
        """Legacy adr-0.x.x path references fail lint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc = root / "docs/design/roadmap/ROADMAP.md"
            doc.parent.mkdir(parents=True, exist_ok=True)
            doc.write_text(
                "[ADR-0.2.0](../adr/adr-0.2.x/ADR-0.2.0-gate-verification/"
                "ADR-0.2.0-gate-verification.md)\n",
                encoding="utf-8",
            )

            result = run_adr_path_contract_lint(root)
            self.assertFalse(result.success)
            self.assertEqual(result.returncode, 1)
            self.assertIn("docs/design/roadmap/ROADMAP.md:1:", result.stdout)

    def test_allows_airlineops_historical_reference(self) -> None:
        """Historical airlineops reference is allowed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc = root / "docs/design/lodestar/example.md"
            doc.parent.mkdir(parents=True, exist_ok=True)
            doc.write_text(
                "The canonical example is "
                "`airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.0-reset-organizing-doctrine.md`.\n",
                encoding="utf-8",
            )

            result = run_adr_path_contract_lint(root)
            self.assertTrue(result.success)


class TestKindInvarianceInCheckPipeline(unittest.TestCase):
    """REQ-0.0.35-04-06: kind-invariance audit must be in gz check."""

    def test_kind_invariance_in_check_steps(self) -> None:
        """REQ-0.0.35-04-06: gz check pipeline includes kind_invariance scope."""
        from gzkit.commands.quality import _build_check_steps

        steps = _build_check_steps()
        step_names = [name for name, _ in steps]
        self.assertIn(
            "Kind invariance",
            step_names,
            "gz check aggregator must include the Kind invariance step",
        )


class TestInterviewTranscriptsInCheckPipeline(unittest.TestCase):
    """GHI #515 (Finding 3): the interview-transcript audit must run in gz check."""

    def test_interview_transcripts_in_check_steps(self) -> None:
        """gz check pipeline includes the interview-transcript scope.

        A validator outside ``gz check`` is never exercised, so its
        divergence from reality goes unnoticed — the structural root cause
        GHI #511 named. Re-gating ``--interviews`` into the aggregator
        closes that class of dead enforcement (GHI #515).
        """
        from gzkit.commands.quality import _build_check_steps

        steps = _build_check_steps()
        step_names = [name for name, _ in steps]
        self.assertIn(
            "Interview transcripts",
            step_names,
            "gz check aggregator must include the Interview transcripts step",
        )


class TestDecisionDocProof(unittest.TestCase):
    """Tests for decision_doc proof type in product proof gate.

    @covers('REQ-GHI-163-01')
    GHI #163: Product proof gate missing decision_doc proof type.
    """

    def test_confirm_decision_satisfies_proof(self) -> None:
        """An OBPI brief with a Confirm decision has decision_doc proof."""
        from gzkit.quality import ObpiProofStatus

        status = ObpiProofStatus(
            obpi_id="OBPI-0.25.0-01-attestation-pattern",
            decision_doc_found=True,
        )
        self.assertTrue(status.has_proof)
        self.assertEqual(status.proof_type, "decision_doc")

    def test_exclude_decision_satisfies_proof(self) -> None:
        """An OBPI brief with an Exclude decision has decision_doc proof."""
        from gzkit.quality import ObpiProofStatus

        status = ObpiProofStatus(
            obpi_id="OBPI-0.25.0-03-signature-pattern",
            decision_doc_found=True,
        )
        self.assertTrue(status.has_proof)
        self.assertEqual(status.proof_type, "decision_doc")

    def test_no_decision_no_proof(self) -> None:
        """An OBPI brief with no decision and no other proof is MISSING."""
        from gzkit.quality import ObpiProofStatus

        status = ObpiProofStatus(
            obpi_id="OBPI-0.99.0-01-fake",
        )
        self.assertFalse(status.has_proof)
        self.assertEqual(status.proof_type, "MISSING")

    def test_check_decision_doc_detects_confirm(self) -> None:
        """_check_decision_doc_proof finds 'Decision: Confirm' in brief text."""
        from gzkit.quality import _check_decision_doc_proof

        brief_text = (
            "## Decision\n\n**Decision: Confirm** — gzkit's implementation is sufficient.\n"
        )
        self.assertTrue(_check_decision_doc_proof(brief_text))

    def test_check_decision_doc_detects_exclude(self) -> None:
        """_check_decision_doc_proof finds 'Decision: Exclude' in brief text."""
        from gzkit.quality import _check_decision_doc_proof

        brief_text = "**Decision: Exclude** — domain-specific, not warranted.\n"
        self.assertTrue(_check_decision_doc_proof(brief_text))

    def test_check_decision_doc_detects_absorb(self) -> None:
        """_check_decision_doc_proof finds 'Decision: Absorb' in brief text."""
        from gzkit.quality import _check_decision_doc_proof

        brief_text = "Decision: **Absorb** — the module adds governance value.\n"
        self.assertTrue(_check_decision_doc_proof(brief_text))

    def test_check_decision_doc_detects_heading_then_bold_value(self) -> None:
        """_check_decision_doc_proof finds '## Decision' heading + '**Absorb**' value."""
        from gzkit.quality import _check_decision_doc_proof

        brief_text = "## Decision\n\n**Absorb** — the airlineops module has been ported.\n"
        self.assertTrue(_check_decision_doc_proof(brief_text))

    def test_check_decision_doc_rejects_no_decision(self) -> None:
        """_check_decision_doc_proof returns False when no decision is present."""
        from gzkit.quality import _check_decision_doc_proof

        brief_text = "## Objective\n\nJust an objective, no decision.\n"
        self.assertFalse(_check_decision_doc_proof(brief_text))


class TestLintScopeMatchesPreCommit(unittest.TestCase):
    """The lint gate must lint the whole repo, not just ``src tests``.

    Regression guard for the gate-divergence defect (2026-06-01): ``gz check``
    linted only ``src tests`` while the pre-commit ruff-check hook lints the
    whole tree (minus ``site/``). Python under ``scripts/`` or ``features/``
    therefore passed ``gz check`` but was blocked at commit time — "green in
    check, red at commit". The lint gate must be a superset of the pre-commit
    hook so a green ``gz check`` implies a clean commit. ruff honors its own
    excludes + ``.gitignore``, so widening to ``.`` does not pull in vendored
    or generated trees.
    """

    def test_run_lint_targets_whole_repo_not_src_tests(self) -> None:
        ok = QualityResult(success=True, command="ruff", stdout="", stderr="", returncode=0)
        with (
            patch.object(quality, "run_command", return_value=ok) as run_cmd,
            patch.object(quality, "run_adr_path_contract_lint", return_value=ok),
            patch.object(quality, "run_parents_pattern_lint", return_value=ok),
        ):
            quality.run_lint(Path("/repo"))

        invoked = [call.args[0] for call in run_cmd.call_args_list]
        self.assertIn("uv run ruff check .", invoked)
        self.assertNotIn("uv run ruff check src tests", invoked)

    def test_run_format_autofix_targets_whole_repo(self) -> None:
        ok = QualityResult(success=True, command="ruff", stdout="", stderr="", returncode=0)
        with patch.object(quality, "run_command", return_value=ok) as run_cmd:
            quality.run_format(Path("/repo"))

        invoked = [call.args[0] for call in run_cmd.call_args_list]
        self.assertIn("uv run ruff check --fix .", invoked)
        self.assertNotIn("uv run ruff check --fix src tests", invoked)


if __name__ == "__main__":
    unittest.main()


class TestDocsBuildInCheckPipeline(unittest.TestCase):
    """`mkdocs build --strict` must run inside `gz check` (operator directive 2026-07-26).

    The strict docs build was a canonical ARB step and a Gate-3 command, but it
    was never in the `gz check` aggregator. That gap let a stale `mkdocs.yml`
    nav entry — pointing at a manpage renamed in an earlier pass — sit broken
    under a fully green `gz check` until a rename sweep happened to run the
    build by hand. Dead enforcement of exactly the class GHI #515 named.
    """

    def test_docs_build_in_check_steps(self) -> None:
        from gzkit.commands.quality import _build_check_steps

        step_names = [name for name, _ in _build_check_steps()]
        self.assertIn(
            "Docs build",
            step_names,
            "gz check aggregator must include the Docs build step",
        )

    def test_docs_build_is_skipped_when_the_project_has_no_docs_site(self) -> None:
        """Adopter safety: no `mkdocs.yml` means no docs site, not a failure.

        `gz check` runs in adopter repos that may ship no documentation site at
        all. Failing them for the absence of a file they never authored would
        make the gate unadoptable.
        """
        from gzkit.quality import run_mkdocs

        with tempfile.TemporaryDirectory() as tmp:
            result = run_mkdocs(Path(tmp))

        self.assertTrue(result.success, "A project with no mkdocs.yml must pass, not fail")
        self.assertEqual(result.returncode, 0)

    def test_docs_build_runs_strict_when_a_docs_site_exists(self) -> None:
        """The strict flag is the contract — a non-strict build tolerates broken nav."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "mkdocs.yml").write_text("site_name: probe\n", encoding="utf-8")
            with patch.object(quality, "run_command") as run_command:
                run_command.return_value = QualityResult(
                    success=True, command="", stdout="", stderr="", returncode=0
                )
                quality.run_mkdocs(root)

        invoked = run_command.call_args.args[0]
        self.assertIn("mkdocs build", invoked)
        self.assertIn("--strict", invoked, f"Docs build must be strict; got {invoked!r}")


class TestModuleSizeInCheckPipeline(unittest.TestCase):
    """The shrink-only module-size ratchet must run inside `gz check`.

    Same class as the Docs build gap above: the ratchet had teeth from its
    2026-08-01 cutover and no automatic caller, so it spoke only when a human
    ran `gz chores advise module-sloc-cap-radon`. A 297-SLOC breach shipped in
    v0.34.2 with every gate green — the gate was not wrong, it was never asked.
    """

    def test_module_size_gate_in_check_steps(self) -> None:
        from gzkit.commands.quality import _build_check_steps

        step_names = [name for name, _ in _build_check_steps()]
        self.assertIn(
            "Module size",
            step_names,
            "gz check aggregator must include the Module size step",
        )

    def test_self_test_failure_short_circuits_before_the_band_run(self) -> None:
        """A gate whose teeth are unverified is the same failure class as an uncalled gate.

        The `--self-test` arm drives all four breach directions over synthetic
        data. If it fails, `compute_breaches` is broken and the band run's
        verdict is worthless — so the band run must not be reached, and its
        green must never be what the caller sees.
        """
        from gzkit.quality import run_module_size_audit

        failed = QualityResult(
            success=False, command="self-test", stdout="", stderr="", returncode=3
        )
        with patch.object(quality, "run_command", return_value=failed) as run_command:
            result = run_module_size_audit(Path("."))

        self.assertFalse(result.success, "A toothless gate must not report success")
        self.assertEqual(
            run_command.call_count,
            1,
            "The band run must not execute once the self-test has failed",
        )

    def test_gate_delegates_to_the_chore_script_rather_than_reimplementing(self) -> None:
        """One threshold authority only.

        `.gzkit/rules/complexity-thresholds.md` § Invariant calls a second
        threshold authority "doctrine drift by another name". This step must
        therefore invoke the chore's own script; a re-implementation here would
        be the drift the script was written to remove.
        """
        from gzkit.quality import run_module_size_audit

        passed = QualityResult(success=True, command="", stdout="", stderr="", returncode=0)
        with patch.object(quality, "run_command", return_value=passed) as run_command:
            run_module_size_audit(Path("."))

        invoked = run_command.call_args.args[0]
        self.assertIn(
            "check_module_size.py",
            " ".join(invoked),
            f"Module size step must run the chore's own gate script; got {invoked!r}",
        )
