"""``gz validate --astral-discipline``: the RO-9 witness (drydock, 2026-10-19).

`docs/governance/harbor-ro9-astral-toolchain.md` § The witness. Each fact is
declared once, in the place Astral's tools read it; a restatement, a lock that
is never checked, a tool run outside the lock, or a non-Astral tool with no
recorded reason is a violation. Today's violations seed a shrink-only baseline.
"""

import contextlib
import io
import json
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from gzkit.cli.main import main
from gzkit.core.validation_rules import ValidationError
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

_UNBANNED = """\
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

_BAN = """
[tool.ruff.lint.flake8-tidy-imports.banned-api]
"__future__.annotations".msg = "annotations are deferred in Python 3.14"
"""

_PYPROJECT = _UNBANNED + _BAN

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
env:
  UV_MALWARE_CHECK: "1"
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

    def __init__(self, **files: str | None) -> None:
        self.files: dict[str, str | None] = {
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


def _rules(**files: str | None) -> set[str]:
    return {rule for rule, _, _ in _Tree(**files).violations()}


class TestACompliantProjectIsClean(unittest.TestCase):
    def test_the_fixture_has_no_violation(self) -> None:
        self.assertEqual(_Tree().violations(), [])


class TestTheFloorsAnnotationIdiomIsLinted(unittest.TestCase):
    """At a 3.14 floor, Ruff refuses PEP 563's import (`.gzkit/rules/pythonic.md` § Imports)."""

    _KEY = ("deferred-annotations-unbanned", "pyproject.toml", "__future__.annotations")

    def test_a_314_floor_whose_ruff_config_does_not_ban_the_import_is_a_violation(self) -> None:
        self.assertIn(self._KEY, _Tree(**{"pyproject.toml": _UNBANNED}).violations())

    def test_a_ban_in_ruff_toml_satisfies_it(self) -> None:
        for name in ("ruff.toml", ".ruff.toml"):
            with self.subTest(config=name):
                tree = _Tree(**{"pyproject.toml": _UNBANNED, name: _BAN.replace("tool.ruff.", "")})
                self.assertNotIn(self._KEY, tree.violations())

    def test_a_313_floor_needs_no_ban_because_313_has_no_deferred_annotations(self) -> None:
        floor = _UNBANNED.replace('">=3.14"', '">=3.13"').replace("3 :: 3.14", "3 :: 3.13")
        tree = _Tree(**{"pyproject.toml": floor, ".python-version": "3.13.9\n"})
        self.assertNotIn("deferred-annotations-unbanned", {r for r, _, _ in tree.violations()})


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


class TestAutomationChecksForMalwareBeforeInstalling(unittest.TestCase):
    """Where a new version enters, uv's malware check runs (operator ruling 2026-10-28)."""

    def test_a_workflow_that_runs_uv_without_the_malware_check_is_a_violation(self) -> None:
        for env in ('  UV_MALWARE_CHECK: "1"\n', '  UV_MALWARE_CHECK: "0"\n', ""):
            with self.subTest(env=env):
                ci = _CI.replace('  UV_MALWARE_CHECK: "1"\n', env)
                expected = set() if env.endswith('"1"\n') else {"malware-check-off"}
                self.assertEqual(_rules(**{".github/workflows/ci.yml": ci}), expected)

    def test_a_workflow_that_never_runs_uv_needs_no_malware_check(self) -> None:
        notes = "name: Notes\njobs:\n  n:\n    steps:\n      - run: gh release view\n"
        self.assertEqual(_rules(**{".github/workflows/notes.yml": notes}), set())


class TestDependenciesLiveInTheProject(unittest.TestCase):
    def test_pip_and_requirements_files_are_violations(self) -> None:
        self.assertEqual(_rules(**{"requirements-docs.txt": "mkdocs==1.6.1\n"}), {"pip-in-project"})
        ci = _CI + "      - run: uv pip install -r requirements-docs.txt\n"
        self.assertEqual(_rules(**{".github/workflows/ci.yml": ci}), {"pip-in-project"})
        rtd = "build:\n  jobs:\n    install:\n      - pip install -r requirements-docs.txt\n"
        self.assertEqual(_rules(**{".readthedocs.yaml": rtd}), {"pip-in-project"})

    def test_a_requirements_file_anywhere_in_the_tree_is_a_violation(self) -> None:
        """Strict uv project discipline admits no requirements file at any depth (operator)."""
        for name in ("docs/requirements.txt", "tools/ci/requirements-dev.txt"):
            with self.subTest(file=name):
                found = _Tree(**{name: "mkdocs==1.6.1\n"}).violations()
                self.assertIn(("pip-in-project", name, Path(name).name), found)

    def test_an_environment_or_build_output_is_not_the_tree(self) -> None:
        for name in (".venv/lib/pkg/requirements.txt", "site/requirements.txt"):
            with self.subTest(file=name):
                self.assertNotIn("pip-in-project", _rules(**{name: "x==1\n"}))

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

    def test_a_registered_dated_record_is_not_an_invocation(self) -> None:
        """A history table of argv that ran is a record; only its own symbol is exempt."""
        source = textwrap.dedent(
            """
            RETIRED = {"coverage": [("2026-09-18T10:57:40Z", ["ruff", "check", "."])]}

            def f():
                return ["ruff", "--version"]
            """
        )
        record = {"file": "src/gzkit/m.py", "symbol": "RETIRED", "reason": "dated receipts"}
        registered = json.dumps({**_EXCEPTIONS, "records": [record]})
        found = _Tree(
            **{"src/gzkit/m.py": source, "data/astral_exceptions.json": registered}
        ).violations()
        self.assertEqual(
            [v for v in found if v[0].startswith(("tool-outside-lock", "exception"))],
            [("tool-outside-lock", "src/gzkit/m.py", "ruff")],
        )

    def test_a_reasonless_or_dead_record_is_a_violation(self) -> None:
        source = 'RETIRED = [["ruff", "check"]]\n'
        for record, rule in (
            (
                {"file": "src/gzkit/m.py", "symbol": "RETIRED", "reason": ""},
                "exception-without-reason",
            ),
            ({"file": "src/gzkit/m.py", "symbol": "GONE", "reason": "r"}, "exception-stale"),
        ):
            registered = json.dumps({**_EXCEPTIONS, "records": [record]})
            with self.subTest(rule=rule):
                self.assertIn(
                    rule,
                    _rules(**{"src/gzkit/m.py": source, "data/astral_exceptions.json": registered}),
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

    def test_a_comment_naming_a_retired_tool_is_not_a_use(self) -> None:
        """A full-line comment documents; only workflow code runs a tool (RO-9 tranche 3)."""
        comments = (
            "      # In place of `twine check` and pypa/gh-action-pypi-publish,\n"
            "      # never actions/setup-python, and no `pip install` here.\n"
        )
        self.assertEqual(_rules(**{".github/workflows/ci.yml": _CI + comments}), set())

    def test_a_commented_pip_in_the_other_project_yaml_is_not_a_use(self) -> None:
        """The Read the Docs and pre-commit configs are read the same way."""
        for name in (".readthedocs.yaml", ".pre-commit-config.yaml"):
            with self.subTest(name=name):
                self.assertEqual(_rules(**{name: "# was: pip install -r docs.txt\n"}), set())
                self.assertIn("pip-in-project", _rules(**{name: "    - pip install -r docs.txt\n"}))


class TestTheScaffoldIsWitnessed(unittest.TestCase):
    """RO-9 tranche 7's done condition: the project `gz init` builds carries no violation."""

    def test_gz_inits_project_carries_no_violation(self) -> None:
        self.assertEqual(scaffold_violations(), [])

    def test_a_scaffold_violation_is_labelled_as_the_scaffolds(self) -> None:
        planted = Violation(rule="setup-python", file="ci.yml", subject="actions/setup-python")
        with mock.patch(
            "gzkit.governance.trust_audits.astral_discipline.find_violations",
            return_value=[planted],
        ):
            found = scaffold_violations()
        self.assertEqual([v.file for v in found], ["gz init scaffold:ci.yml"])


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

    def test_the_package_exports_the_audit(self) -> None:
        from gzkit.governance import trust_audits  # noqa: PLC0415

        self.assertIn("audit_astral_discipline", trust_audits.__all__)
        self.assertIs(trust_audits.audit_astral_discipline, audit_astral_discipline)

    def test_the_exception_register_is_declared(self) -> None:
        registries = json.loads(
            (_REPO / "data" / "config_registry.json").read_text(encoding="utf-8")
        )["registries"]
        self.assertIn(Path(EXCEPTIONS_RELPATH).name, registries)


_RTD = 'version: 2\nbuild:\n  os: ubuntu-24.04\n  tools:\n    python: "3.13"\n'


class TestEveryVersionHomeIsRead(unittest.TestCase):
    """Branches RO-9 tranche 1's red witness left undriven (receipt arb-red-commit-fea4697ac6fb)."""

    def test_a_missing_floor_is_a_missing_home(self) -> None:
        pyproject = _PYPROJECT.replace('requires-python = ">=3.14"\n', "")
        self.assertIn(
            ("version-home-missing", "pyproject.toml", "requires-python"),
            _Tree(**{"pyproject.toml": pyproject}).violations(),
        )

    def test_a_ty_environment_version_is_a_restatement(self) -> None:
        pyproject = _PYPROJECT + '\n[tool.ty.environment]\npython-version = "3.14"\n'
        self.assertIn(
            ("version-restated", "pyproject.toml", "tool.ty.environment.python-version"),
            _Tree(**{"pyproject.toml": pyproject}).violations(),
        )

    def test_read_the_docs_python_is_a_restatement_unless_registered_and_agreeing(self) -> None:
        key = (".readthedocs.yaml", "build.tools.python")
        unregistered = _Tree(**{".readthedocs.yaml": _RTD}).violations()
        self.assertIn(("version-restated", *key), unregistered)
        exceptions = json.loads(json.dumps(_EXCEPTIONS))
        exceptions["restatements"].append(
            {"file": key[0], "key": key[1], "agrees_with": ".python-version", "reason": "RTD."}
        )
        registered = _Tree(
            **{".readthedocs.yaml": _RTD, "data/astral_exceptions.json": json.dumps(exceptions)}
        ).violations()
        self.assertIn(("version-disagrees", *key), registered)
        self.assertNotIn(("version-restated", *key), registered)


class TestToolsRunFromTheLockEverywhere(unittest.TestCase):
    def test_a_pre_commit_entry_through_uvx_is_a_violation(self) -> None:
        config = (
            "repos:\n  - repo: local\n    hooks:\n      - id: lint\n        entry: uvx ruff check\n"
        )
        self.assertIn(
            ("tool-outside-lock", ".pre-commit-config.yaml", "ruff"),
            _Tree(**{".pre-commit-config.yaml": config}).violations(),
        )

    def test_bytecode_caches_are_not_sources(self) -> None:
        argv = 'import subprocess\nsubprocess.run(["uvx", "ruff", "check"])\n'
        found = _Tree(**{"src/demo/__pycache__/cached.py": argv}).violations()
        self.assertEqual([v for v in found if v[0] == "tool-outside-lock"], [])
        found = _Tree(**{"src/demo/live.py": argv}).violations()
        self.assertIn(("tool-outside-lock", "src/demo/live.py", "ruff"), found)

    def test_unreadable_distribution_metadata_maps_no_modules(self) -> None:
        from gzkit.governance.trust_audits import astral_discipline as ad  # noqa: PLC0415

        ad._distribution_modules.cache_clear()
        self.addCleanup(ad._distribution_modules.cache_clear)
        with mock.patch.object(
            ad.importlib.metadata, "packages_distributions", side_effect=OSError
        ):
            self.assertEqual(ad._distribution_modules(), {})


class TestTheAuditReadsItsBaseline(unittest.TestCase):
    def _audit(self, baseline: str | None) -> list:
        files = {".github/workflows/ci.yml": _CI.replace("--locked ", "")}
        if baseline is not None:
            files[BASELINE_RELPATH] = baseline
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, text in {**_Tree(**files).files}.items():
                if text is None:
                    continue
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text(textwrap.dedent(text), encoding="utf-8")
            return audit_astral_discipline(root)

    def test_no_baseline_announces_and_does_not_fail(self) -> None:
        with mock.patch(
            "gzkit.governance.trust_audits.astral_discipline.emit_advisory"
        ) as advisory:
            self.assertEqual(self._audit(None), [])
        self.assertTrue(advisory.called)

    def test_a_malformed_baseline_is_an_error(self) -> None:
        (error,) = self._audit(json.dumps({"_doc": "x", "rows": []}))
        self.assertIn("malformed", error.message)

    def test_a_baseline_holding_the_violation_admits_it(self) -> None:
        row = {"rule": "lock-unchecked", "file": ".github/workflows/ci.yml", "subject": "uv sync"}
        self.assertEqual(
            self._audit(json.dumps({"_doc": "x", "violations": [{**row, "count": 1}]})), []
        )


class TestTheNegativeControlsDiscriminate(unittest.TestCase):
    """RO-9's two canaries' controls: each reports only the violation it planted."""

    def setUp(self) -> None:
        from gzkit.governance.trust_audits import _qc_negative_controls as nc  # noqa: PLC0415

        def mkroot(slug: str) -> Path:
            tmp = tempfile.TemporaryDirectory(prefix=f"gzkit-qc-nc-{slug}-")
            self.addCleanup(tmp.cleanup)
            return Path(tmp.name)

        # The builders take their directory from the enforcement runner; a unit test
        # owns its own, so the fixture is the same tree in a directory it cleans up.
        patcher = mock.patch.object(nc, "_mkroot", side_effect=mkroot)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_the_new_violation_control_catches_only_the_setup_python_step(self) -> None:
        from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep  # noqa: PLC0415
        from gzkit.governance.trust_audits import _qc_negative_controls as nc  # noqa: PLC0415

        caught = ep._ep_astral_discipline(nc._build_astral_discipline())
        self.assertTrue(caught)
        self.assertTrue(all("setup-python" in e.artifact for e in caught), caught)
        decoy = nc._build_astral_discipline()
        (decoy / BASELINE_RELPATH).write_text(
            json.dumps({"_doc": "x", "violations": []}), encoding="utf-8"
        )
        self.assertEqual(ep._ep_astral_discipline(decoy), [])

    def test_the_deferred_annotations_control_catches_only_the_unbanned_import(self) -> None:
        from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep  # noqa: PLC0415
        from gzkit.governance.trust_audits import _qc_negative_controls as nc  # noqa: PLC0415

        caught = ep._ep_astral_discipline_deferred_annotations(
            nc._build_astral_discipline_deferred_annotations()
        )
        self.assertTrue(caught)
        self.assertTrue(all("deferred-annotations-unbanned" in e.artifact for e in caught), caught)
        decoy = nc._build_astral_discipline_deferred_annotations()
        (decoy / BASELINE_RELPATH).write_text(
            json.dumps({"_doc": "x", "violations": []}), encoding="utf-8"
        )
        self.assertEqual(ep._ep_astral_discipline_deferred_annotations(decoy), [])

    def test_the_admit_control_is_truthy_only_when_the_baseline_admits(self) -> None:
        from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep  # noqa: PLC0415
        from gzkit.governance.trust_audits import _qc_negative_controls as nc  # noqa: PLC0415

        self.assertEqual(
            ep._ep_astral_discipline_admits_baselined(nc._build_astral_discipline_baselined()), 1
        )
        self.assertEqual(
            ep._ep_astral_discipline_admits_baselined(nc._build_astral_discipline()), 0
        )


class TestTheClaimsDeclareTheirPopulation(unittest.TestCase):
    def test_neither_astral_claim_is_an_undeclared_population(self) -> None:
        from gzkit.governance.trust_audits.population_controls import (  # noqa: PLC0415
            audit_population_controls,
        )

        flagged = [e.message for e in audit_population_controls(_REPO)]
        self.assertFalse([m for m in flagged if "'astral-discipline" in m], flagged)


class TestTheDeferredAnnotationsControlIsRegistered(unittest.TestCase):
    """Scorecard row 23b cites `NC:astral-discipline-deferred-annotations`; it must resolve."""

    _CLAIM = "astral-discipline-deferred-annotations"

    def test_the_control_is_a_registered_claim(self) -> None:
        from gzkit.enforcement import (  # noqa: PLC0415
            _ensure_production_claims_registered,
            registered_claims,
        )

        _ensure_production_claims_registered()
        self.assertIn(self._CLAIM, registered_claims())

    def test_the_claim_declares_the_baseline_that_admits_its_violations(self) -> None:
        from gzkit.governance.trust_audits.exemption_controls import (  # noqa: PLC0415
            audit_exemption_controls,
        )

        flagged = [e.message for e in audit_exemption_controls(_REPO)]
        self.assertFalse([m for m in flagged if self._CLAIM in m], flagged)


class TestTheRo9LiteralsAreDeclaredAuditSubjects(unittest.TestCase):
    """The RO-9 controls name paths they audit, which `gz check-config-paths` must not flag."""

    def test_neither_literal_reads_as_an_ungoverned_path(self) -> None:
        from gzkit.commands.config_paths import (  # noqa: PLC0415
            _collect_source_path_literal_issues,
        )
        from gzkit.config import GzkitConfig  # noqa: PLC0415

        manifest = json.loads((_REPO / ".gzkit" / "manifest.json").read_text(encoding="utf-8"))
        config = GzkitConfig.load(_REPO / ".gzkit.json")
        issues = [
            " ".join(str(v) for v in issue.values())
            for issue in _collect_source_path_literal_issues(_REPO, manifest, config)
        ]
        for module, literal in (
            ("_qc_negative_controls.py", ".github/workflows/ci.yml"),
            ("qc_binding.py", "pyproject.toml"),
        ):
            with self.subTest(module=module):
                self.assertFalse([i for i in issues if module in i and literal in i], issues)


class TestTheGzCheckStepIsQcBound(unittest.TestCase):
    def test_the_qc_binding_audit_accepts_the_astral_step(self) -> None:
        from gzkit.governance.trust_audits.qc_binding import audit_qc_binding  # noqa: PLC0415

        # The audit prints advisories; captured so the verbose run reads this test's result.
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            errors = audit_qc_binding(_REPO)
        findings = [f"{e.artifact} {e.message}" for e in errors]
        self.assertFalse([f for f in findings if "Astral discipline" in f], findings)


class TestTheScopeIsWiredIntoGzCheck(unittest.TestCase):
    def test_gz_check_runs_the_astral_discipline_audit(self) -> None:
        from gzkit.commands.quality import _build_check_steps  # noqa: PLC0415
        from gzkit.quality import run_astral_discipline_audit  # noqa: PLC0415

        self.assertIn(("Astral discipline", run_astral_discipline_audit), _build_check_steps())

    def test_the_step_runs_the_validate_scope(self) -> None:
        from gzkit import quality  # noqa: PLC0415

        sentinel = object()
        with mock.patch.object(quality, "run_command", return_value=sentinel) as run:
            result = quality.run_astral_discipline_audit(_REPO)
        self.assertIs(result, sentinel)
        self.assertEqual(run.call_args.args[0], "uv run gz validate --astral-discipline")


class TestTheScaffoldIsPlannedOnADryRun(unittest.TestCase):
    """`gz init --dry-run` lists the project skeleton the witness checks (RO-9 tranche 1)."""

    def test_the_dry_run_lists_the_skeleton(self) -> None:
        from gzkit.commands.init_cmd import _normalize_package_name  # noqa: PLC0415
        from tests.commands.common import CliRunner  # noqa: PLC0415

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--dry-run"])
            name = _normalize_package_name(Path.cwd().name)
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Would build the project with uv init --lib", result.output)
        self.assertIn("Would seed data/astral_discipline_baseline.json", result.output)
        self.assertIn("Would create tests/__init__.py", result.output)
        self.assertFalse(Path(name).exists())


class TestGzValidateRunsTheScope(unittest.TestCase):
    """`gz validate --astral-discipline` reaches the audit and treats a finding as a breach."""

    def _validate(self, findings: list) -> tuple[int, str]:
        out = io.StringIO()
        with (
            mock.patch(
                "gzkit.governance.trust_audits.audit_astral_discipline", return_value=findings
            ) as audit,
            # An open MX hangar demotes ERROR-level scopes to advisory; grade the
            # scope as it stands outside one, where its findings block.
            mock.patch("gzkit.mx.checkpoint.blocks", return_value=True),
            contextlib.redirect_stdout(out),
            contextlib.redirect_stderr(out),
        ):
            try:
                code = main(["validate", "--astral-discipline"])
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
        self.assertEqual(audit.call_count, 1, out.getvalue())
        return code, out.getvalue()

    def test_a_clean_tree_passes_the_scope(self) -> None:
        code, output = self._validate([])
        self.assertEqual(code, 0, output)
        self.assertIn("astral_discipline", output)

    def test_a_finding_is_a_policy_breach(self) -> None:
        """Exit 3, the CLI doctrine's policy-breach code (`.gzkit/rules/cli.md`)."""
        finding = ValidationError(type="astral_discipline", artifact="pyproject.toml", message="m")
        code, output = self._validate([finding])
        self.assertEqual(code, 3, output)


if __name__ == "__main__":
    unittest.main()
