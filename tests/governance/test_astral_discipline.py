"""``gz validate --astral-discipline``: the RO-9 witness (drydock, 2026-10-19).

`docs/governance/harbor-ro9-astral-toolchain.md` § The witness. Each fact is
declared once, in the place Astral's tools read it; a restatement, a lock that
is never checked, a tool run outside the lock, or a non-Astral tool with no
recorded reason is a violation. Today's violations seed a shrink-only baseline.
"""

from __future__ import annotations

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.astral_discipline import (
    BASELINE_RELPATH,
    EXCEPTIONS_RELPATH,
    Violation,
    audit_astral_discipline,
    check_discipline_baseline,
    find_violations,
    scaffold_violations,
)

_REPO = Path(__file__).resolve().parents[2]

_PYPROJECT = """\
[project]
name = "demo"
version = "0.1.0"
requires-python = ">=3.14"
classifiers = ["Programming Language :: Python :: 3.14"]
dependencies = []

[dependency-groups]
dev = ["ruff>=0.17", "ty>=0.0.89", "behave>=1.3"]

[build-system]
requires = ["uv_build>=0.13.1,<0.14"]
build-backend = "uv_build"
"""

_EXCEPTIONS = {
    "_doc": "fixture (docs/governance/harbor-ro9-astral-toolchain.md)",
    "tools": [{"name": "behave", "reason": "Astral ships no BDD runner."}],
    "restatements": [
        {
            "file": "pyproject.toml",
            "key": "project.classifiers",
            "agrees_with": "requires-python",
            "reason": "PyPI trove metadata, read by no Astral tool.",
        }
    ],
}

_CI = """\
name: CI
jobs:
  check:
    steps:
      - uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884 # v10.3.0
      - run: uv sync --locked --all-extras
      - run: uv run behave
      - run: uv run ruff check .
      - run: uv run ty check .
"""


class _Tree:
    """A compliant project, with each test changing one file."""

    def __init__(self, **files: str) -> None:
        self.files = {
            "pyproject.toml": _PYPROJECT,
            ".python-version": "3.14.8\n",
            ".github/workflows/ci.yml": _CI,
            "data/astral_exceptions.json": json.dumps(_EXCEPTIONS),
        }
        self.files.update(files)

    def violations(self) -> list[tuple[str, str, str]]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, text in self.files.items():
                if text is None:
                    continue
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(textwrap.dedent(text), encoding="utf-8")
            found = find_violations(root)
        return sorted((v.rule, v.file, v.subject) for v in found)


def _rules(**files: str) -> set[str]:
    return {rule for rule, _, _ in _Tree(**files).violations()}


class TestACompliantProjectIsClean(unittest.TestCase):
    def test_the_fixture_has_no_violation(self) -> None:
        self.assertEqual(_Tree().violations(), [])


class TestThePythonVersionIsDeclaredOnce(unittest.TestCase):
    def test_a_ruff_or_ty_target_is_a_restatement(self) -> None:
        ruff = _PYPROJECT + '\n[tool.ruff]\ntarget-version = "py314"\n'
        self.assertIn(
            ("version-restated", "pyproject.toml", "tool.ruff.target-version"),
            _Tree(**{"pyproject.toml": ruff}).violations(),
        )
        ty = '[environment]\npython-version = "3.14"\n'
        self.assertIn(
            ("version-restated", "ty.toml", "environment.python-version"),
            _Tree(**{"ty.toml": ty}).violations(),
        )

    def test_a_workflow_version_is_a_restatement_and_a_bare_install_is_not(self) -> None:
        pinned = _CI + "      - run: uv python install 3.14.8\n"
        self.assertIn("version-restated", _rules(**{".github/workflows/ci.yml": pinned}))
        bare = _CI + "      - run: uv python install\n"
        self.assertEqual(_Tree(**{".github/workflows/ci.yml": bare}).violations(), [])

    def test_setup_python_is_a_restatement_and_its_own_violation(self) -> None:
        setup = _CI + (
            "      - uses: actions/setup-python@v6\n"
            '        with:\n          python-version: "3.14.8"\n'
        )
        self.assertEqual(
            _rules(**{".github/workflows/ci.yml": setup}), {"setup-python", "version-restated"}
        )

    def test_a_registered_restatement_must_agree_with_its_home(self) -> None:
        wrong = _PYPROJECT.replace(":: 3.14", ":: 3.13")
        self.assertIn(
            ("version-disagrees", "pyproject.toml", "project.classifiers"),
            _Tree(**{"pyproject.toml": wrong}).violations(),
        )

    def test_a_missing_home_or_a_pin_below_the_floor_is_a_violation(self) -> None:
        self.assertIn("version-home-missing", _rules(**{".python-version": None}))
        self.assertIn("version-below-floor", _rules(**{".python-version": "3.13.16\n"}))

    def test_a_skill_that_hardcodes_a_version_is_a_restatement(self) -> None:
        skill = "Run `uv python install 3.13` then `uv python pin 3.13.16`.\n"
        self.assertIn("version-restated", _rules(**{".gzkit/skills/x/SKILL.md": skill}))


class TestTheLockIsChecked(unittest.TestCase):
    def test_a_frozen_or_bare_sync_in_automation_is_a_violation(self) -> None:
        for flags in ("--frozen --all-extras", ""):
            with self.subTest(flags=flags):
                ci = _CI.replace("uv sync --locked --all-extras", f"uv sync {flags}".rstrip())
                self.assertEqual(_rules(**{".github/workflows/ci.yml": ci}), {"lock-unchecked"})


class TestDependenciesLiveInTheProject(unittest.TestCase):
    def test_pip_and_requirements_files_are_violations(self) -> None:
        self.assertEqual(_rules(**{"requirements-docs.txt": "mkdocs==1.6.1\n"}), {"pip-in-project"})
        ci = _CI + "      - run: uv pip install -r requirements-docs.txt\n"
        self.assertEqual(_rules(**{".github/workflows/ci.yml": ci}), {"pip-in-project"})
        rtd = "build:\n  jobs:\n    install:\n      - pip install -r requirements-docs.txt\n"
        self.assertEqual(_rules(**{".readthedocs.yaml": rtd}), {"pip-in-project"})

    def test_dev_tooling_in_an_extra_is_a_violation(self) -> None:
        extra = _PYPROJECT.replace(
            "dependencies = []\n",
            'dependencies = []\n\n[project.optional-dependencies]\ndocs = ["behave>=1.3"]\n',
        )
        self.assertEqual(_rules(**{"pyproject.toml": extra}), {"dev-tool-in-extra"})
        dev = _PYPROJECT.replace(
            "dependencies = []\n",
            'dependencies = []\n\n[project.optional-dependencies]\ndev = ["httpx>=0.27"]\n',
        )
        self.assertIn("dev-tool-in-extra", _rules(**{"pyproject.toml": dev}))


class TestToolsRunFromTheLock(unittest.TestCase):
    def test_uvx_or_path_for_a_locked_tool_is_a_violation(self) -> None:
        source = textwrap.dedent(
            """
            def f():
                a = ["uvx", "ruff", "check", "."]
                b = ["ruff", "--version"]
                c = ["uv", "run", "ruff", "check"]
                d = ["uvx", "pre-commit", "install"]
                e = ["uvx", "ty", *argv]
                return a, b, c, d, e
            """
        )
        found = _Tree(**{"src/gzkit/m.py": source}).violations()
        self.assertEqual(
            [v for v in found if v[0] == "tool-outside-lock"],
            [
                ("tool-outside-lock", "src/gzkit/m.py", "ruff"),
                ("tool-outside-lock", "src/gzkit/m.py", "ruff"),
                ("tool-outside-lock", "src/gzkit/m.py", "ty"),
            ],
        )

    def test_a_chore_command_through_uvx_is_a_violation(self) -> None:
        acceptance = json.dumps({"criteria": [{"command": "uvx ty check ."}]})
        self.assertIn(
            "tool-outside-lock", _rules(**{"src/gzkit/chores/x/acceptance.json": acceptance})
        )

    def test_a_declared_tool_nothing_invokes_is_a_violation(self) -> None:
        unused = _PYPROJECT.replace('"behave>=1.3"]', '"behave>=1.3", "vulture>=2.16"]')
        found = _Tree(**{"pyproject.toml": unused}).violations()
        self.assertIn(("unused-dependency", "pyproject.toml", "vulture"), found)


class TestEveryNonAstralToolHasAReason(unittest.TestCase):
    def test_an_unregistered_tool_is_a_violation(self) -> None:
        extra = _PYPROJECT.replace('"behave>=1.3"]', '"behave>=1.3", "coverage>=7"]')
        ci = _CI + "      - run: uv run coverage report\n"
        found = _Tree(**{"pyproject.toml": extra, ".github/workflows/ci.yml": ci}).violations()
        self.assertEqual(found, [("non-astral-unregistered", "pyproject.toml", "coverage")])

    def test_a_reasonless_or_dead_register_entry_is_a_violation(self) -> None:
        reasonless = {**_EXCEPTIONS, "tools": [{"name": "behave", "reason": ""}]}
        self.assertIn(
            "exception-without-reason",
            _rules(**{"data/astral_exceptions.json": json.dumps(reasonless)}),
        )
        dead = {
            **_EXCEPTIONS,
            "tools": [*_EXCEPTIONS["tools"], {"name": "xenon", "reason": "gone"}],
        }
        self.assertIn(
            "exception-stale", _rules(**{"data/astral_exceptions.json": json.dumps(dead)})
        )


class TestBuildAndPublishThroughUv(unittest.TestCase):
    def test_a_non_uv_backend_is_a_violation(self) -> None:
        hatch = _PYPROJECT.replace(
            'requires = ["uv_build>=0.13.1,<0.14"]\nbuild-backend = "uv_build"',
            'requires = ["hatchling"]\nbuild-backend = "hatchling.build"',
        )
        self.assertEqual(_rules(**{"pyproject.toml": hatch}), {"build-backend-not-uv"})

    def test_publishing_outside_uv_is_a_violation(self) -> None:
        for step in (
            "      - uses: pypa/gh-action-pypi-publish@release/v1\n",
            "      - run: uv tool run twine check --strict dist/*\n",
        ):
            with self.subTest(step=step):
                self.assertEqual(
                    _rules(**{".github/workflows/ci.yml": _CI + step}), {"publish-not-uv"}
                )


class TestTheScaffoldIsWitnessed(unittest.TestCase):
    def test_gz_inits_project_is_checked_by_the_same_rules(self) -> None:
        found = scaffold_violations()
        self.assertTrue(all(v.file.startswith("gz init scaffold:") for v in found))
        self.assertTrue(
            {v.rule for v in found}
            <= {
                "version-restated",
                "dev-tool-in-extra",
                "build-backend-not-uv",
                "version-home-missing",
                "unused-dependency",
                "non-astral-unregistered",
            }
        )


def _violation(rule: str, file: str, subject: str) -> Violation:
    return Violation(rule=rule, file=file, subject=subject, detail="")


class TestTheBaselineOnlyShrinks(unittest.TestCase):
    rows = ({"rule": "lock-unchecked", "file": "ci.yml", "subject": "uv sync", "count": 2},)

    def test_the_seeded_violations_pass(self) -> None:
        found = [_violation("lock-unchecked", "ci.yml", "uv sync")] * 2
        self.assertEqual(check_discipline_baseline(found, list(self.rows)), [])

    def test_a_new_violation_fails_naming_the_spec(self) -> None:
        found = [_violation("lock-unchecked", "ci.yml", "uv sync")] * 2 + [
            _violation("setup-python", "d.yml", "actions/setup-python")
        ]
        errors = check_discipline_baseline(found, list(self.rows))
        self.assertEqual(
            [e.artifact for e in errors], ["setup-python::d.yml::actions/setup-python"]
        )
        self.assertIn("harbor-ro9-astral-toolchain.md", errors[0].message)

    def test_a_gone_shrunk_or_duplicated_row_fails(self) -> None:
        self.assertEqual(len(check_discipline_baseline([], list(self.rows))), 1)
        self.assertEqual(
            len(
                check_discipline_baseline(
                    [_violation("lock-unchecked", "ci.yml", "uv sync")], list(self.rows)
                )
            ),
            1,
        )
        twice = [dict(self.rows[0]), dict(self.rows[0])]
        self.assertIn(
            "twice",
            check_discipline_baseline(
                [_violation("lock-unchecked", "ci.yml", "uv sync")] * 2, twice
            )[0].message,
        )


class TestTheRealTree(unittest.TestCase):
    def test_the_repository_passes_its_own_scope(self) -> None:
        self.assertEqual([e.message for e in audit_astral_discipline(_REPO)], [])

    def test_the_baseline_is_a_registered_shrink_ratchet_at_its_row_count(self) -> None:
        rows = json.loads((_REPO / BASELINE_RELPATH).read_text(encoding="utf-8"))["violations"]
        registry = json.loads(
            (_REPO / "data" / "waiver_ratchet_registry.json").read_text(encoding="utf-8")
        )
        (entry,) = [s for s in registry["surfaces"] if s["data_file"] == BASELINE_RELPATH]
        self.assertEqual(
            (entry["mechanism"], entry["baseline_count"]), ("shrink-ratchet", len(rows))
        )

    def test_the_exception_register_is_declared(self) -> None:
        registries = json.loads(
            (_REPO / "data" / "config_registry.json").read_text(encoding="utf-8")
        )["registries"]
        self.assertIn(Path(EXCEPTIONS_RELPATH).name, registries)


if __name__ == "__main__":
    unittest.main()
