"""Unit tests for audit_distribution (OBPI-0.0.32-07, REQ-0.0.32-07-*).

Tests exercise each drift class in isolation using synthetic temp trees,
confirming that the validator is static-only (no wheel build) and correctly
exits 0 on clean state, exits 3 on policy drift, and exits 2 on system errors.
"""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from gzkit.traceability import covers


def _write_pyproject(root: Path, wheel_exclude: list[str] | None = None) -> None:
    """Write a minimal uv_build pyproject.toml; the wheel ships ``src/gzkit`` minus excludes.

    The fixtures modelled hatchling's include globs until RO-9 tranche 3 moved
    the build to uv_build (2026-10-22), which has no wheel includes: a file is
    left out of the wheel only by an exclude or by sitting outside the module.
    """
    excludes = ", ".join(f'"{pattern}"' for pattern in wheel_exclude or [])
    (root / "pyproject.toml").write_text(
        '[project]\nname = "py-gzkit"\n\n'
        '[build-system]\nbuild-backend = "uv_build"\n\n'
        '[tool.uv.build-backend]\nmodule-name = "gzkit"\nmodule-root = "src"\n'
        f"wheel-exclude = [{excludes}]\n",
        encoding="utf-8",
    )


def _write_manifest(root: Path, surfaces: dict[str, list[str]]) -> None:
    """Write a minimal distribution_baseline_manifest.json."""
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "distribution_baseline_manifest.json").write_text(
        json.dumps({"schema_version": "1.0", "surfaces": surfaces}),
        encoding="utf-8",
    )


class TestCleanStateExitsZero(unittest.TestCase):
    """Clean state: on-disk, included, and baseline all agree — empty error list."""

    @covers("REQ-0.0.32-07-05")
    def test_clean_state_returns_empty_error_list(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Create a skill file on disk
            skill = root / "src" / "gzkit" / "skills" / "test-skill" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# Test skill\n", encoding="utf-8")

            _write_pyproject(root)
            _write_manifest(root, {"skills": ["test-skill/SKILL.md"]})

            errors = audit_distribution(root)

            self.assertEqual(errors, [], msg=f"Expected no errors; got: {errors}")


class TestOnDiskNotIncluded(unittest.TestCase):
    """ON_DISK_NOT_INCLUDED: file under surface root, not covered by any include glob."""

    @covers("REQ-0.0.32-07-02")
    @covers("REQ-0.0.32-07-03")
    def test_file_not_covered_by_include_is_flagged(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Create a skill file on disk
            skill = root / "src" / "gzkit" / "skills" / "orphan-skill" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# Orphan\n", encoding="utf-8")

            # An exclude that removes this file from the wheel
            _write_pyproject(root, ["orphan-skill"])
            # Baseline matches what's included (nothing for skills)
            _write_manifest(root, {"skills": []})

            errors = audit_distribution(root)

            self.assertTrue(
                any(
                    "ON_DISK_NOT_INCLUDED" in e.message and "orphan-skill/SKILL.md" in e.artifact
                    for e in errors
                ),
                msg=f"Expected ON_DISK_NOT_INCLUDED for orphan-skill/SKILL.md; got: {errors}",
            )

    @covers("REQ-0.0.32-07-05")
    def test_on_disk_not_included_error_type_is_distribution(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "src" / "gzkit" / "skills" / "unincluded" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# unincluded\n", encoding="utf-8")

            _write_pyproject(root, ["unincluded"])
            _write_manifest(root, {"skills": []})

            errors = audit_distribution(root)

            self.assertTrue(
                any(e.type == "distribution" for e in errors),
                msg=f"Expected type='distribution'; got: {[e.type for e in errors]}",
            )

    @covers("REQ-0.0.32-07-05")
    def test_resolution_hint_present_for_on_disk_not_included(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "src" / "gzkit" / "skills" / "hint-check" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# hint\n", encoding="utf-8")

            _write_pyproject(root, ["hint-check"])
            _write_manifest(root, {"skills": []})

            errors = audit_distribution(root)

            self.assertTrue(
                any("pyproject.toml" in e.message for e in errors),
                msg="Expected resolution hint referencing pyproject.toml",
            )


class TestBaselineNotOnDisk(unittest.TestCase):
    """BASELINE_NOT_ON_DISK: baseline manifest entry does not exist on disk."""

    @covers("REQ-0.0.32-07-02")
    @covers("REQ-0.0.32-07-03")
    def test_phantom_baseline_entry_is_flagged(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # No on-disk file
            _write_pyproject(root)
            # Baseline claims a file that doesn't exist
            _write_manifest(root, {"skills": ["phantom-skill/SKILL.md"]})

            errors = audit_distribution(root)

            self.assertTrue(
                any(
                    "BASELINE_NOT_ON_DISK" in e.message and "phantom-skill/SKILL.md" in e.artifact
                    for e in errors
                ),
                msg=f"Expected BASELINE_NOT_ON_DISK for phantom-skill/SKILL.md; got: {errors}",
            )

    @covers("REQ-0.0.32-07-05")
    def test_baseline_not_on_disk_resolution_hint_present(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_pyproject(root)
            _write_manifest(root, {"skills": ["missing/SKILL.md"]})

            errors = audit_distribution(root)

            baseline_errors = [e for e in errors if "BASELINE_NOT_ON_DISK" in e.message]
            self.assertTrue(
                len(baseline_errors) > 0
                and any("baseline manifest" in e.message for e in baseline_errors),
                msg="Expected resolution hint referencing baseline manifest",
            )


class TestOnDiskNotBaseline(unittest.TestCase):
    """ON_DISK_NOT_BASELINE: file on disk + covered by include, absent from baseline."""

    @covers("REQ-0.0.32-07-02")
    @covers("REQ-0.0.32-07-03")
    def test_untracked_included_file_is_flagged(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            new_skill = root / "src" / "gzkit" / "skills" / "new-skill" / "SKILL.md"
            new_skill.parent.mkdir(parents=True)
            new_skill.write_text("# new\n", encoding="utf-8")

            _write_pyproject(root)
            # Baseline is empty — file exists on disk and is covered but not in baseline
            _write_manifest(root, {"skills": []})

            errors = audit_distribution(root)

            self.assertTrue(
                any(
                    "ON_DISK_NOT_BASELINE" in e.message and "new-skill/SKILL.md" in e.artifact
                    for e in errors
                ),
                msg=f"Expected ON_DISK_NOT_BASELINE for new-skill/SKILL.md; got: {errors}",
            )

    @covers("REQ-0.0.32-07-05")
    def test_on_disk_not_baseline_resolution_hint_present(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "src" / "gzkit" / "skills" / "hint-skill" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# hint\n", encoding="utf-8")

            _write_pyproject(root)
            _write_manifest(root, {"skills": []})

            errors = audit_distribution(root)

            self.assertTrue(
                any(
                    "ON_DISK_NOT_BASELINE" in e.message
                    and "distribution_baseline_manifest.json" in e.message
                    for e in errors
                ),
                msg="Expected resolution hint referencing distribution_baseline_manifest.json",
            )


class TestMalformedToml(unittest.TestCase):
    """Malformed pyproject.toml must exit 2 (system error), not 3 (policy breach)."""

    @covers("REQ-0.0.32-07-06")
    def test_malformed_toml_raises_system_exit_2(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("this is not valid toml {{{{", encoding="utf-8")
            _write_manifest(root, {})

            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
                audit_distribution(root)

            self.assertEqual(
                ctx.exception.code,
                2,
                msg=f"Expected SystemExit(2) for malformed TOML; got code={ctx.exception.code}",
            )

    @covers("REQ-0.0.32-07-06")
    def test_missing_pyproject_raises_system_exit_2(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(root, {})
            # No pyproject.toml

            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
                audit_distribution(root)

            self.assertEqual(ctx.exception.code, 2)

    @covers("REQ-0.0.32-07-06")
    def test_missing_manifest_raises_system_exit_2(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_pyproject(root)
            # No data/distribution_baseline_manifest.json

            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
                audit_distribution(root)

            self.assertEqual(ctx.exception.code, 2)


class TestWalkFilter(unittest.TestCase):
    """Files under excluded segments (__pycache__, etc.) are ignored."""

    @covers("REQ-0.0.32-07-02")
    def test_pycache_files_not_flagged(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Create a legit skill on disk
            skill = root / "src" / "gzkit" / "skills" / "cache-test" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# Cache test\n", encoding="utf-8")

            # Create __pycache__ files inside surface root
            pycache = root / "src" / "gzkit" / "skills" / "__pycache__" / "something.pyc"
            pycache.parent.mkdir(parents=True)
            pycache.write_bytes(b"fake pyc")

            _write_pyproject(root)
            _write_manifest(root, {"skills": ["cache-test/SKILL.md"]})

            errors = audit_distribution(root)

            # The .pyc file should NOT trigger ON_DISK_NOT_INCLUDED errors
            self.assertFalse(
                any("__pycache__" in e.artifact for e in errors),
                msg=f"__pycache__ files should be excluded; got: {errors}",
            )
            # And the clean .md file should not trigger errors either
            self.assertFalse(
                any("cache-test" in e.artifact for e in errors),
                msg=f"Legit skill should not be flagged; got: {errors}",
            )

    @covers("REQ-0.0.32-07-07")
    def test_audit_does_not_invoke_uv_build(self) -> None:
        """Confirm static-only invariant: no uv build subprocess during audit."""
        import subprocess as _subprocess

        from gzkit.governance.trust_audits import audit_distribution

        original_run = _subprocess.run
        build_calls: list[str] = []

        def _spy_run(args: object, **kwargs: object) -> object:
            if isinstance(args, (list, tuple)) and any(
                "uv" in str(a) or "hatch" in str(a) for a in args
            ):
                build_calls.append(str(args))
            return original_run(args, **kwargs)  # type: ignore

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_pyproject(root)
            _write_manifest(root, {})

            import unittest.mock as mock

            with (
                mock.patch("subprocess.run", side_effect=_spy_run),
                contextlib.suppress(SystemExit),
            ):
                audit_distribution(root)

        self.assertEqual(build_calls, [], msg=f"must not invoke subprocess; got: {build_calls}")


class TestStaticOnlyInvariant(unittest.TestCase):
    """REQ-0.0.32-07-04: no uv build or hatch build subprocess calls."""

    @covers("REQ-0.0.32-07-04")
    def test_audit_does_not_call_uv_build_subprocess(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_pyproject(root)
            _write_manifest(root, {"skills": []})

            import unittest.mock as mock

            with mock.patch("subprocess.run") as mock_run:
                audit_distribution(root)
                mock_run.assert_not_called()


class TestDocumentationAndScorecard(unittest.TestCase):
    """REQ-0.0.32-07-10: CLI flag registration (BEHAVIOR — exercises parser)."""

    @covers("REQ-0.0.32-07-10")
    def test_distribution_flag_registered_in_cli(self) -> None:
        import io
        from contextlib import redirect_stderr, redirect_stdout

        from gzkit.cli import main

        output = io.StringIO()
        try:
            with redirect_stdout(output), redirect_stderr(output):
                main(["validate", "--help"])
        except SystemExit:
            pass
        help_text = output.getvalue()
        self.assertIn(
            "--distribution", help_text, "gz validate --distribution must be registered in CLI"
        )


class TestRegenerateDistributionBaseline(unittest.TestCase):
    """Tests for the regenerate_distribution_baseline function (OBPI-0.0.32-15)."""

    @covers("REQ-0.0.32-15-01")
    def test_regenerator_is_callable(self) -> None:
        """regenerate_distribution_baseline is importable and callable."""
        from gzkit.governance.trust_audits.distribution import regenerate_distribution_baseline

        self.assertTrue(callable(regenerate_distribution_baseline))

    @staticmethod
    def _seed_surface_root(root: Path) -> None:
        """Populate a temp project root with one canonical skill surface file.

        Test-isolation contract: the regenerator writes the baseline manifest
        and appends a ledger event. Both MUST land in the temp root, never the
        live repo (see .gzkit/rules/tests.md — never use production databases).
        """
        skill = root / "src" / "gzkit" / "skills" / "test-skill" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("# Test skill\n", encoding="utf-8")
        _write_pyproject(root)
        _write_manifest(root, {"skills": []})

    @covers("REQ-0.0.32-15-03")
    def test_regenerate_then_audit_exits_zero(self) -> None:
        """After regenerating against a project root, audit returns no errors."""
        from gzkit.governance.trust_audits.distribution import (
            audit_distribution,
            regenerate_distribution_baseline,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._seed_surface_root(root)
            regenerate_distribution_baseline(root)
            errors = audit_distribution(root)
            self.assertEqual(
                [],
                errors,
                f"audit returned errors after regeneration: {[e.message for e in errors]}",
            )

    @covers("REQ-0.0.32-15-03")
    def test_regenerate_is_idempotent(self) -> None:
        """Running the regenerator twice produces no manifest diff."""
        from gzkit.governance.trust_audits.distribution import regenerate_distribution_baseline

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._seed_surface_root(root)
            manifest_path = root / "data" / "distribution_baseline_manifest.json"

            regenerate_distribution_baseline(root)
            content_after_first = json.loads(manifest_path.read_text(encoding="utf-8"))

            regenerate_distribution_baseline(root)
            content_after_second = json.loads(manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(
                content_after_first["surfaces"],
                content_after_second["surfaces"],
                "Regenerating twice must produce the same manifest",
            )

    @covers("REQ-0.0.32-15-02")
    def test_regenerator_emits_ledger_event(self) -> None:
        """Successful regeneration appends a distribution_baseline_regenerated ledger event."""
        from gzkit.governance.trust_audits.distribution import regenerate_distribution_baseline

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._seed_surface_root(root)
            ledger_path = root / ".gzkit" / "ledger.jsonl"

            regenerate_distribution_baseline(root)

            lines_after = ledger_path.read_text(encoding="utf-8").splitlines()
            self.assertGreater(len(lines_after), 0, "No ledger event appended")
            last_event = json.loads(lines_after[-1])
            self.assertEqual(
                "distribution_baseline_regenerated",
                last_event.get("event"),
                f"Expected distribution_baseline_regenerated event, got: {last_event.get('event')}",
            )


class TestPackageOnlyExemption(unittest.TestCase):
    """Classifier-based exemption for package_only files in ON_DISK_NOT_INCLUDED (REQ-06)."""

    @covers("REQ-0.0.32-15-06")
    def test_package_only_init_py_not_flagged(self) -> None:
        """__init__.py under a canonical surface is exempt from ON_DISK_NOT_INCLUDED."""
        from gzkit.governance.trust_audits.distribution import _collect_errors

        project_root = Path(__file__).resolve().parents[2]
        on_disk = {"src/gzkit/rules/__init__.py", "src/gzkit/rules/agents.md"}
        included = {"src/gzkit/rules/agents.md"}
        baseline = {"src/gzkit/rules/agents.md"}

        errors = _collect_errors(on_disk, included, baseline, project_root)
        flagged = [e.artifact for e in errors]
        self.assertNotIn(
            "src/gzkit/rules/__init__.py",
            flagged,
            "__init__.py must not be flagged as ON_DISK_NOT_INCLUDED",
        )

    @covers("REQ-0.0.32-15-06")
    def test_scaffolder_py_not_flagged(self) -> None:
        """_scaffolder.py (package_only) under rules surface is exempt from ON_DISK_NOT_INCLUDED."""
        from gzkit.governance.trust_audits.distribution import _collect_errors

        project_root = Path(__file__).resolve().parents[2]
        on_disk = {"src/gzkit/rules/_scaffolder.py", "src/gzkit/rules/agents.md"}
        included = {"src/gzkit/rules/agents.md"}
        baseline = {"src/gzkit/rules/agents.md"}

        errors = _collect_errors(on_disk, included, baseline, project_root)
        flagged = [e.artifact for e in errors]
        self.assertNotIn(
            "src/gzkit/rules/_scaffolder.py",
            flagged,
            "_scaffolder.py (package_only) must not be flagged as ON_DISK_NOT_INCLUDED",
        )


class TestSurfaceDomainIsNotSelfSupplied(unittest.TestCase):
    """The audit's domain is the canonical surface set, never the manifest's own keys.

    A checker whose scope comes from an artifact it also validates can report that
    a listed member is wrong but never that a member is missing.  ``surface_roots``
    was derived from ``manifest["surfaces"]``, so a canonical surface absent from the
    manifest was outside the audit's domain entirely — ``src/gzkit/chores`` was never
    walked, and the ``chores`` branch of ``_get_surface_classifier`` was unreachable.
    Residual disclosed on GHI #783; the class named in the 2026-08-09 handoff.
    """

    def test_canonical_surface_absent_from_manifest_is_still_audited(self) -> None:
        """A chores file on disk and wheel-included is reported, not silently skipped."""
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            skill = root / "src" / "gzkit" / "skills" / "test-skill" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# Test skill\n", encoding="utf-8")

            chore = root / "src" / "gzkit" / "chores" / "demo-slug" / "CHORE.md"
            chore.parent.mkdir(parents=True)
            chore.write_text("# Demo chore\n", encoding="utf-8")

            _write_pyproject(root)
            # The manifest declares only `skills`.  The chores surface is real,
            # on disk, and shipped by the include glob — but unlisted.
            _write_manifest(root, {"skills": ["test-skill/SKILL.md"]})

            errors = audit_distribution(root)

            flagged = [e.artifact for e in errors]
            self.assertIn(
                "src/gzkit/chores/demo-slug/CHORE.md",
                flagged,
                "A canonical surface missing from the baseline manifest must be "
                "reported; deriving surface_roots from the manifest's own keys makes "
                "its absence unobservable.",
            )

    def test_authored_chore_gate_script_is_not_exempted_as_package_only(self) -> None:
        """The exemption check must classify on the path form the classifier expects.

        ``_classify_chore_file`` resolves a ``.py`` file's class by locating its
        ``.gzkit/`` counterpart via ``relative_to(project_root / 'src' / 'gzkit' /
        'chores')``, which raises on a relative path and falls through to
        ``package_only``.  An authored chore gate script silently exempted from
        drift reporting is the blindness this audit exists to close.
        """
        from gzkit.governance.trust_audits.distribution import _is_package_only

        project_root = Path(__file__).resolve().parents[2]
        gate_script = "src/gzkit/chores/module-sloc-cap-radon/check_module_size.py"

        self.assertFalse(
            _is_package_only(gate_script, project_root),
            f"{gate_script} is an authored canonical gate script; exempting it "
            "would hide its absence from the wheel.",
        )

    def test_module_root_py_file_is_modelled_as_shipped(self) -> None:
        """A .py file under the module root ships with no include declared.

        uv_build ships the module tree whole; modelling a glob list instead
        reported shipped files as not-shipped, the defect this replaced the
        hatchling `packages` test for (RO-9 tranche 3).
        """
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            chore_dir = root / "src" / "gzkit" / "chores" / "demo-slug"
            chore_dir.mkdir(parents=True)
            (chore_dir / "CHORE.md").write_text("# Demo\n", encoding="utf-8")
            (chore_dir / "check_thing.py").write_text("x = 1\n", encoding="utf-8")

            # The authored counterpart is what makes the script `canonical` rather
            # than `package_only` — without it the exemption fires first and the
            # shipping model this test targets is never reached.
            canonical_dir = root / ".gzkit" / "chores" / "demo-slug"
            canonical_dir.mkdir(parents=True)
            (canonical_dir / "check_thing.py").write_text("x = 1\n", encoding="utf-8")

            _write_pyproject(root)
            _write_manifest(
                root,
                {"chores": ["demo-slug/CHORE.md", "demo-slug/check_thing.py"]},
            )

            errors = audit_distribution(root)

            self.assertEqual([e.artifact for e in errors], [])

    def test_regenerator_recovers_a_surface_the_manifest_omits(self) -> None:
        """Regeneration is from on-disk truth, so it adds a surface the manifest lacks."""
        from gzkit.governance.trust_audits.distribution import (
            regenerate_distribution_baseline,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            chore = root / "src" / "gzkit" / "chores" / "demo-slug" / "CHORE.md"
            chore.parent.mkdir(parents=True)
            chore.write_text("# Demo chore\n", encoding="utf-8")

            _write_pyproject(root)
            _write_manifest(root, {})

            regenerate_distribution_baseline(root)

            rewritten = json.loads(
                (root / "data" / "distribution_baseline_manifest.json").read_text(encoding="utf-8")
            )
            self.assertIn(
                "chores",
                rewritten["surfaces"],
                "regenerate_distribution_baseline documents on-disk truth as its sole "
                "input; a surface it cannot discover makes that claim false.",
            )


class TestUvBuildWheelPrediction(unittest.TestCase):
    """`wheel_shipped_files` predicts a uv_build wheel without building one.

    Each case is a uv_build rule read from its documentation and probed on uv
    0.13.1 on 2026-10-22, where the prediction matched a real wheel's 877 files.
    """

    def _tree(self, root: Path, *rel_paths: str) -> None:
        for rel in rel_paths:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x\n", encoding="utf-8")

    def test_the_module_tree_ships_whole(self) -> None:
        from gzkit.governance.trust_audits.distribution import wheel_shipped_files

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root, "src/gzkit/__init__.py", "src/gzkit/data/x.json", "docs/a.md")
            _write_pyproject(root)
            self.assertEqual(
                wheel_shipped_files(root), {"src/gzkit/__init__.py", "src/gzkit/data/x.json"}
            )

    def test_an_unanchored_exclude_removes_a_directory_and_its_children_at_depth(self) -> None:
        from gzkit.governance.trust_audits.distribution import wheel_shipped_files

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(
                root,
                "src/gzkit/chores/a/CHORE.md",
                "src/gzkit/chores/a/proofs/log.md",
                "src/gzkit/chores/a/proofs/deep/run.json",
            )
            _write_pyproject(root, ["gzkit/chores/*/proofs"])
            self.assertEqual(wheel_shipped_files(root), {"src/gzkit/chores/a/CHORE.md"})

    def test_uv_default_excludes_apply_with_none_declared(self) -> None:
        from gzkit.governance.trust_audits.distribution import wheel_shipped_files

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(
                root,
                "src/gzkit/a.py",
                "src/gzkit/__pycache__/a.cpython-314.pyc",
                "src/gzkit/b.pyo",
            )
            _write_pyproject(root)
            self.assertEqual(wheel_shipped_files(root), {"src/gzkit/a.py"})

    def test_the_module_name_defaults_to_the_normalized_project_name(self) -> None:
        from gzkit.governance.trust_audits.distribution import wheel_shipped_files

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root, "src/my_tool/__init__.py", "src/gzkit/__init__.py")
            (root / "pyproject.toml").write_text(
                '[project]\nname = "My-Tool"\n[build-system]\nbuild-backend = "uv_build"\n',
                encoding="utf-8",
            )
            self.assertEqual(wheel_shipped_files(root), {"src/my_tool/__init__.py"})

    def test_a_project_not_built_by_uv_build_predicts_no_wheel(self) -> None:
        from gzkit.governance.trust_audits.distribution import wheel_shipped_files

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root, "src/gzkit/__init__.py")
            (root / "pyproject.toml").write_text(
                '[build-system]\nbuild-backend = "hatchling.build"\n', encoding="utf-8"
            )
            self.assertEqual(wheel_shipped_files(root), set())

    def test_an_anchored_exclude_is_refused_as_a_system_error(self) -> None:
        from gzkit.governance.trust_audits.distribution import wheel_shipped_files

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root, "src/gzkit/__init__.py")
            _write_pyproject(root, ["/gzkit/chores/*/proofs"])
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as ctx:
                wheel_shipped_files(root)
            self.assertEqual(ctx.exception.code, 2)
            self.assertIn("unanchored", stderr.getvalue())

    @covers("REQ-0.0.32-07-02")
    def test_a_not_included_finding_names_the_exclude_that_removed_it(self) -> None:
        """REQ-02's glob context: under uv_build it is the exclude pattern."""
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root, "src/gzkit/skills/kept/SKILL.md", "src/gzkit/skills/gone/SKILL.md")
            _write_pyproject(root, ["skills/gone"])
            _write_manifest(root, {"skills": ["kept/SKILL.md"]})

            errors = audit_distribution(root)

            self.assertEqual([e.artifact for e in errors], ["src/gzkit/skills/gone/SKILL.md"])
            self.assertIn("'skills/gone'", errors[0].message)

    def test_a_double_star_exclude_spans_any_depth(self) -> None:
        from gzkit.governance.trust_audits.distribution import wheel_shipped_files

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(
                root,
                "src/gzkit/skills/a/SKILL.md",
                "src/gzkit/skills/a/drafts/x.md",
                "src/gzkit/skills/a/b/c/drafts/y.md",
            )
            _write_pyproject(root, ["gzkit/**/drafts"])
            self.assertEqual(wheel_shipped_files(root), {"src/gzkit/skills/a/SKILL.md"})


class TestUnshippedReason(unittest.TestCase):
    """Each not-included finding says why the wheel leaves the file out (REQ-0.0.32-07-02)."""

    def test_a_default_exclude_is_named_as_uv_builds_own(self) -> None:
        from gzkit.governance.trust_audits.distribution import unshipped_reason

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_pyproject(root)
            self.assertEqual(
                unshipped_reason(root, "src/gzkit/skills/a/x.pyc"),
                "uv_build's default exclude '*.pyc' removes it",
            )

    def test_a_file_outside_the_module_root_is_named_by_location(self) -> None:
        from gzkit.governance.trust_audits.distribution import unshipped_reason

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                '[build-system]\nbuild-backend = "uv_build"\n'
                '[tool.uv.build-backend]\nmodule-name = "other"\n',
                encoding="utf-8",
            )
            self.assertEqual(
                unshipped_reason(root, "src/gzkit/skills/a/SKILL.md"),
                "it sits outside the module root 'src/other'",
            )

    def test_a_project_without_a_uv_build_wheel_is_named_as_such(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "src" / "gzkit" / "skills" / "a" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# a\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                '[build-system]\nbuild-backend = "hatchling.build"\n', encoding="utf-8"
            )
            _write_manifest(root, {"skills": ["a/SKILL.md"]})

            errors = audit_distribution(root)

            self.assertEqual([e.artifact for e in errors], ["src/gzkit/skills/a/SKILL.md"])
            self.assertIn("declares no uv_build wheel", errors[0].message)

    def test_a_shipped_file_missing_from_the_baseline_is_named_as_shipped(self) -> None:
        from gzkit.governance.trust_audits import audit_distribution

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "src" / "gzkit" / "skills" / "a" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# a\n", encoding="utf-8")
            _write_pyproject(root)
            _write_manifest(root, {"skills": []})

            errors = audit_distribution(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("ON_DISK_NOT_BASELINE", errors[0].message)
            self.assertIn("covered by the wheel", errors[0].message)


if __name__ == "__main__":
    unittest.main()
