"""Policy tests: Ruff never calls an import Pydantic reads at runtime typing-only.

Pydantic resolves a model's field annotations when the class is built, so a name
used only in an annotation of a ``BaseModel`` subclass is still a runtime import.
Ruff's TC001-TC003 report it as typing-only unless
``[tool.ruff.lint.flake8-type-checking] runtime-evaluated-base-classes`` names the
base, and the fix Ruff offers then moves it under ``TYPE_CHECKING`` and leaves the
model undefined (GHI #1270: ``EnforcementClaimRecord`` lost ``Callable`` and 833
tests failed). Each probe runs Ruff with the project's own configuration.
"""

import importlib
import inspect
import json
import pkgutil
import subprocess
import sys
import textwrap
import tomllib
import unittest
from pathlib import Path

from pydantic import BaseModel

import gzkit

REPO_ROOT = Path(__file__).parent.parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"


def _typing_only_findings(source: str) -> list[str]:
    """Return the TC001-TC003 findings Ruff reports for *source* under the project config.

    Returns:
        Each finding's message.
    """
    result = subprocess.run(  # noqa: S603 — the running interpreter, a fixed argv
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--config",
            str(PYPROJECT),
            "--select",
            "TC001,TC002,TC003",
            "--output-format",
            "json",
            "--no-cache",
            "--stdin-filename",
            "src/gzkit/runtime_annotation_probe.py",
            "-",
        ],
        input=textwrap.dedent(source),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        cwd=REPO_ROOT,
    )
    return [finding["message"] for finding in json.loads(result.stdout or "[]")]


class TestPydanticAnnotationsAreRuntime(unittest.TestCase):
    def test_a_model_field_annotation_is_not_typing_only(self) -> None:
        source = """
            from collections.abc import Callable

            from pydantic import BaseModel


            class Record(BaseModel):
                fixture: Callable[[], object]
            """
        self.assertEqual(_typing_only_findings(source), [])

    def test_a_subclass_of_a_project_model_base_is_runtime_too(self) -> None:
        source = """
            from collections.abc import Callable

            from gzkit.content.models.base import BaseContentModel


            class Section(BaseContentModel):
                render: Callable[[], str]
            """
        self.assertEqual(_typing_only_findings(source), [])


def _configured_bases() -> set[str]:
    with PYPROJECT.open("rb") as handle:
        config = tomllib.load(handle)
    type_checking = config["tool"]["ruff"]["lint"]["flake8-type-checking"]
    return set(type_checking["runtime-evaluated-base-classes"])


def _project_model_bases() -> set[str]:
    """Return every gzkit class a gzkit Pydantic model inherits from directly.

    Returns:
        Qualified names, as Ruff matches them.
    """
    bases: set[str] = set()
    for info in pkgutil.walk_packages(gzkit.__path__, "gzkit."):
        if info.name.rpartition(".")[2] == "__main__":
            continue  # an entry point runs the CLI when imported
        module = importlib.import_module(info.name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module.__name__ or not issubclass(cls, BaseModel):
                continue
            bases.update(
                f"{base.__module__}.{base.__qualname__}"
                for base in cls.__bases__
                if issubclass(base, BaseModel) and base.__module__.startswith("gzkit.")
            )
    return bases


class TestEveryProjectModelBaseIsConfigured(unittest.TestCase):
    def test_no_project_model_base_is_missing(self) -> None:
        self.assertEqual(_project_model_bases() - _configured_bases(), set())


class TestTheProbeStillSeesTypingOnlyImports(unittest.TestCase):
    """The control: a name used only in a plain function's signature is still flagged."""

    def test_a_function_annotation_is_typing_only(self) -> None:
        source = """
            from collections.abc import Callable


            def call(fn: Callable[[], object]) -> object:
                return fn()
            """
        self.assertEqual(len(_typing_only_findings(source)), 1)


if __name__ == "__main__":
    unittest.main()
