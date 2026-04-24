"""Wheel packaging contract tests for OBPI-0.0.21-03.

Verifies that ``uv build`` ships canonical chore data files in the wheel,
excludes runtime evidence (``proofs/``, ``__pycache__``), and that
``pyproject.toml`` uses Hatchling-native syntax (no MANIFEST.in, no
``[tool.setuptools.*]``).

@covers OBPI-0.0.21-03
"""

import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
import zipfile
from pathlib import Path

from gzkit.traceability import covers

REPO_ROOT = Path(__file__).resolve().parent.parent


def _build_wheel_into(tmpdir: Path) -> Path:
    """Build a wheel into tmpdir and return its path.

    Uses ``uv build --wheel --out-dir`` to keep build hermetic and avoid
    polluting the repo's ``dist/``.
    """
    result = subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmpdir)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"uv build failed (exit {result.returncode})\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    wheels = sorted(tmpdir.glob("py_gzkit-*.whl"))
    if not wheels:
        raise RuntimeError(f"no wheel produced in {tmpdir}; stdout: {result.stdout}")
    return wheels[-1]


class TestWheelChoresShipping(unittest.TestCase):
    """REQ-0.0.21-03-01..03 + 07: wheel contents contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls._tmp_path = Path(cls._tmp.name)
        cls._wheel = _build_wheel_into(cls._tmp_path)
        with zipfile.ZipFile(cls._wheel) as z:
            cls._namelist = list(z.namelist())

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    @covers("REQ-0.0.21-03-01")
    def test_wheel_ships_chores_registry(self) -> None:
        """REQ-01: gzkit/chores/registry.json is present in the built wheel."""
        self.assertIn(
            "gzkit/chores/registry.json",
            self._namelist,
            msg=(
                "registry.json must ship in the wheel so downstream "
                "pip install py-gzkit can resolve the canonical chore set"
            ),
        )

    @covers("REQ-0.0.21-03-02")
    def test_wheel_ships_representative_chore_data(self) -> None:
        """REQ-02: at least 30 chore slug dirs with both CHORE.md and acceptance.json."""
        slug_to_files: dict[str, set[str]] = {}
        slug_pattern = re.compile(r"^gzkit/chores/([a-z0-9-]+)/(CHORE\.md|acceptance\.json)$")
        for name in self._namelist:
            match = slug_pattern.match(name)
            if match:
                slug, fname = match.group(1), match.group(2)
                slug_to_files.setdefault(slug, set()).add(fname)

        complete_slugs = {
            slug
            for slug, files in slug_to_files.items()
            if {"CHORE.md", "acceptance.json"}.issubset(files)
        }
        self.assertGreaterEqual(
            len(complete_slugs),
            30,
            msg=(
                f"Expected >=30 complete chore slugs in wheel; got "
                f"{len(complete_slugs)}: {sorted(complete_slugs)}"
            ),
        )

    @covers("REQ-0.0.21-03-03")
    def test_wheel_excludes_proofs_and_pycache(self) -> None:
        """REQ-03 + 07: no proofs/ or __pycache__ paths under gzkit/chores/."""

        def _is_excluded(name: str) -> bool:
            return (
                "/proofs/" in name
                or name.endswith("/proofs")
                or "__pycache__" in name
                or name.endswith(".pyc")
            )

        violations = [
            n for n in self._namelist if n.startswith("gzkit/chores/") and _is_excluded(n)
        ]
        self.assertEqual(
            violations,
            [],
            msg=(
                "Wheel must not contain runtime proofs evidence or bytecode "
                f"under gzkit/chores/; found: {violations[:10]}"
            ),
        )


class TestPyprojectHatchlingNative(unittest.TestCase):
    """REQ-0.0.21-03-06: Hatchling-native syntax; no setuptools/MANIFEST.in."""

    @covers("REQ-0.0.21-03-06")
    def test_pyproject_uses_hatchling_native_syntax(self) -> None:
        """REQ-06: include/force-include declared; no MANIFEST.in; no [tool.setuptools]."""
        pyproject_path = REPO_ROOT / "pyproject.toml"
        with pyproject_path.open("rb") as fh:
            data = tomllib.load(fh)

        wheel_target = (
            data.get("tool", {})
            .get("hatch", {})
            .get("build", {})
            .get("targets", {})
            .get("wheel", {})
        )
        has_force_include = "force-include" in wheel_target
        has_include = bool(wheel_target.get("include"))
        self.assertTrue(
            has_force_include or has_include,
            msg=(
                "pyproject.toml must declare a Hatchling-native data-shipping "
                "mechanism: [tool.hatch.build.targets.wheel.force-include] OR "
                "[tool.hatch.build.targets.wheel].include"
            ),
        )

        self.assertNotIn(
            "setuptools",
            data.get("tool", {}),
            msg="pyproject.toml must not contain a [tool.setuptools.*] block",
        )

        manifest_in = REPO_ROOT / "MANIFEST.in"
        self.assertFalse(
            manifest_in.exists(),
            msg=(
                f"{manifest_in} must not exist (setuptools vestige; Hatchling is the build backend)"
            ),
        )

    @covers("REQ-0.0.21-03-06")
    def test_pyproject_preserves_packages_declaration(self) -> None:
        """REQ-03 (preserve): packages = ['src/gzkit'] declaration MUST remain intact."""
        pyproject_path = REPO_ROOT / "pyproject.toml"
        with pyproject_path.open("rb") as fh:
            data = tomllib.load(fh)
        wheel_target = data["tool"]["hatch"]["build"]["targets"]["wheel"]
        self.assertEqual(
            wheel_target.get("packages"),
            ["src/gzkit"],
            msg="packages = ['src/gzkit'] must remain (data shipping ADDS to it)",
        )


class TestEditableInstallResolvesChores(unittest.TestCase):
    """REQ-0.0.21-03-04: editable install exposes chores via importlib.resources."""

    @covers("REQ-0.0.21-03-04")
    def test_importlib_resources_lists_chore_slugs(self) -> None:
        """REQ-04: importlib.resources.files('gzkit.chores').iterdir() yields slug dirs."""
        import importlib.resources

        files = importlib.resources.files("gzkit.chores")
        slug_dirs = [p.name for p in files.iterdir() if p.is_dir() and not p.name.startswith("__")]
        self.assertGreaterEqual(
            len(slug_dirs),
            30,
            msg=(
                f"importlib.resources must expose >=30 chore slugs in editable "
                f"install (REQ-04); got {len(slug_dirs)}: {slug_dirs[:5]}..."
            ),
        )

    @covers("REQ-0.0.21-03-04")
    def test_importlib_resources_resolves_registry_json(self) -> None:
        """REQ-04: registry.json is readable via importlib.resources."""
        import importlib.resources
        import json

        registry_text = (
            importlib.resources.files("gzkit.chores")
            .joinpath("registry.json")
            .read_text(encoding="utf-8")
        )
        registry = json.loads(registry_text)
        self.assertTrue(
            isinstance(registry, dict | list),
            msg="registry.json must parse as JSON via importlib.resources",
        )


class TestPyInstallerBinaryDataBundling(unittest.TestCase):
    """REQ-0.0.21-03-05: gz.spec bundles chore data for the pyinstaller binary path."""

    @covers("REQ-0.0.21-03-05")
    def test_gz_spec_extends_datas_with_chores(self) -> None:
        """REQ-05: gz.spec MUST collect chore .md/.json files into the datas list."""
        spec_path = REPO_ROOT / "gz.spec"
        spec_text = spec_path.read_text(encoding="utf-8")
        # Spec must reference a chores collection AND include it in datas
        self.assertIn(
            "CHORES",
            spec_text,
            msg="gz.spec must define a CHORES datas list (REQ-05)",
        )
        self.assertRegex(
            spec_text,
            r"datas\s*=\s*[A-Z_+\s]*CHORES",
            msg="gz.spec datas list must include CHORES so the binary bundles chore data",
        )
        # Spec must restrict to .md/.json so proofs/ and pycache stay out
        self.assertIn(
            '{".md", ".json"}',
            spec_text,
            msg=(
                "gz.spec CHORES collection must restrict to .md/.json files "
                "(matches the wheel exclude contract for proofs/pycache)"
            ),
        )

    @covers("REQ-0.0.21-03-05")
    def test_pyinstaller_dependency_remains_declared(self) -> None:
        """REQ-05: pyinstaller dev-group dependency MUST stay declared so binary build works."""
        pyproject_path = REPO_ROOT / "pyproject.toml"
        with pyproject_path.open("rb") as fh:
            data = tomllib.load(fh)
        dev_deps = data.get("dependency-groups", {}).get("dev", [])
        self.assertTrue(
            any(d.startswith("pyinstaller") for d in dev_deps),
            msg=(
                "pyinstaller MUST remain in dependency-groups.dev so the binary "
                "build path (gz.spec) keeps working (REQ-05)"
            ),
        )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(unittest.main())
