"""Unit tests for the complexity measurement pipeline (OBPI-0.0.27-03).

This package's ``__init__`` doubles as the shared-fixture module — every
helper that more than one ``tests/complexity/test_*.py`` consumes lives
here so each test module imports from a stable, allow-listed path.

The fixture surface is deliberately small:

- :func:`stub_corpus` -> a single-project :class:`ExemplarCorpus` whose
  pinned SHA, included paths, and excluded paths are wired to the canned
  tool outputs in :func:`stubbed_subprocess`.
- :func:`stubbed_subprocess` -> a :class:`unittest.mock.MagicMock` that
  returns deterministic canned ``radon`` / ``lizard`` / ``cohesion``
  output keyed off the first two argv tokens.
- :func:`run_pipeline_with_stubs` -> serialized ``baseline.json`` text
  produced by :func:`gzkit.complexity.measurement.measure_corpus` under
  the stub harness.
- :func:`run_pipeline_into_dir` -> context manager yielding the written
  output directory for end-to-end shape assertions.
"""

from __future__ import annotations

import contextlib
import json
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path
from unittest import mock

from gzkit.complexity.measurement import measure_corpus
from gzkit.models.exemplar import (
    ExcludedPath,
    ExemplarCorpus,
    ExemplarProject,
)

# A pinned 40-char hex SHA used by the fixture project.
_FIXTURE_SHA = "abcdef0123456789abcdef0123456789abcdef01"


def stub_corpus() -> ExemplarCorpus:
    """Return a one-project :class:`ExemplarCorpus` for unit-tier tests.

    The included path glob matches a single ``alpha.py`` under the stubbed
    tree; the excluded path glob matches an ``excluded.py`` so path-filter
    behavior is observable.
    """
    project = ExemplarProject.model_validate(
        {
            "name": "fixture-alpha",
            "canonical_url": "https://example.invalid/fixture-alpha",
            "commit_sha": _FIXTURE_SHA,
            "archetypal_cell": 1,
            "cell_label": "Fixture cell",
            "included_paths": ("**/*.py",),
            "excluded_paths_with_rationale": (
                ExcludedPath(
                    glob="excluded.py",
                    exclusion_rationale="Pinned-out fixture file used by path-filter tests.",
                ),
            ),
            "path_filter_rationale": "Fixture for unit-tier tests of the measurement pipeline.",
            "longevity_evidence": "Synthetic fixture; not a real project.",
            "maintenance_health_evidence": "Synthetic fixture; not a real project.",
            "practitioner_reputation_citation": "Synthetic fixture (no real citation).",
            "pure_python_loc_ratio": 1.0,
            "craftsmanship_signal_narrative": "Synthetic fixture for unit-tier coverage.",
            "project_doctrine_fitness_narrative": "Synthetic fixture; doctrine-neutral.",
        }
    )
    return ExemplarCorpus(
        schema_version="1.0.0",
        corpus_revision=1,
        projects=(project,),
        vacant_cells=(),
    )


def _canned_outputs() -> dict[tuple[str, str], str]:
    """Return the canned stdout for each (tool, subcommand) pair."""
    return {
        ("radon", "cc"): json.dumps({"alpha.py": [{"complexity": 4}, {"complexity": 9}]}),
        ("radon", "mi"): json.dumps({"alpha.py": {"mi": 71.5}}),
        ("radon", "hal"): json.dumps(
            {
                "alpha.py": {
                    "total": {"volume": 100.0, "difficulty": 5.0, "effort": 500.0},
                }
            }
        ),
        ("radon", "raw"): json.dumps({"alpha.py": {"sloc": 80, "lloc": 60}}),
        ("lizard", "alpha.py"): "10,3,40,2,12,alpha.py:do_thing,1,1,2\n",
        ("cohesion", "alpha.py"): "Class: A\n  Total: 75.0%\n",
    }


def _stub_completed(stdout: str, returncode: int = 0) -> mock.Mock:
    """Return a fake :class:`subprocess.CompletedProcess` for *stdout*."""
    completed = mock.Mock(spec=subprocess.CompletedProcess)
    completed.stdout = stdout
    completed.stderr = ""
    completed.returncode = returncode
    return completed


def _route_subprocess(args: list[str]) -> mock.Mock:
    """Pick the canned output appropriate for *args* (list-form invocation)."""
    canned = _canned_outputs()
    if not args:
        return _stub_completed("", returncode=2)
    head = args[0]
    if head == "radon" and len(args) >= 2:
        return _stub_completed(canned.get(("radon", args[1]), ""))
    if head == "lizard":
        return _stub_completed(canned.get(("lizard", "alpha.py"), ""))
    if head == "cohesion":
        return _stub_completed(canned.get(("cohesion", "alpha.py"), ""))
    return _stub_completed("", returncode=0)


class _SubprocessSpy:
    """Capture every call to ``subprocess.run`` for shape assertions."""

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def __call__(self, *args: object, **kwargs: object) -> mock.Mock:
        argv = list(args[0]) if args and isinstance(args[0], (list, tuple)) else []
        self.calls.append({"argv": argv, "kwargs": dict(kwargs)})
        return _route_subprocess(argv)


@contextlib.contextmanager
def stubbed_pipeline_environment() -> Iterator[tuple[Path, _SubprocessSpy]]:
    """Yield a (tree, subprocess-spy) pair with all external surfaces stubbed.

    The yielded tree contains an ``alpha.py`` file matching the fixture
    project's include glob.  ``subprocess.run`` inside
    :mod:`gzkit.complexity.measurement` is replaced with a capturing spy
    that returns canned tool output.  ``shutil.which`` returns a synthetic
    binary path for every required tool so the binary-presence assertion
    passes.
    """
    spy = _SubprocessSpy()
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp) / "tree"
        tree.mkdir()
        (tree / "alpha.py").write_text("def do_thing():\n    return 1\n", encoding="utf-8")
        # Excluded.py exists so the exclusion glob has a target to subtract.
        (tree / "excluded.py").write_text("def excluded():\n    return 0\n", encoding="utf-8")
        with (
            mock.patch(
                "gzkit.complexity.measurement.subprocess.run",
                side_effect=spy,
            ),
            mock.patch(
                "gzkit.complexity.measurement.shutil.which",
                lambda name: f"/usr/local/bin/{name}",
            ),
            mock.patch(
                "gzkit.complexity.measurement._resolve_tree",
                lambda project, cache_root: tree,
            ),
        ):
            yield tree, spy


def run_pipeline_with_stubs(corpus: ExemplarCorpus) -> str:
    """Run :func:`measure_corpus` under the stub harness; return baseline JSON text."""
    with (
        stubbed_pipeline_environment() as (_tree, _spy),
        tempfile.TemporaryDirectory() as out,
    ):
        out_dir = Path(out)
        measure_corpus(corpus, out_dir, cache_root=Path(out) / "cache")
        return (out_dir / "baseline.json").read_text(encoding="utf-8")


@contextlib.contextmanager
def run_pipeline_into_dir(corpus: ExemplarCorpus) -> Iterator[Path]:
    """Run :func:`measure_corpus` and yield the output directory for assertions."""
    with stubbed_pipeline_environment() as (_tree, _spy), tempfile.TemporaryDirectory() as out:
        out_dir = Path(out)
        measure_corpus(corpus, out_dir, cache_root=Path(out) / "cache")
        yield out_dir


# Defensive import-time touch so an unused-import lint cannot strip these
# helpers when the type-checker visits this module before the test files
# are discovered.
_ = shutil


__all__ = [
    "run_pipeline_into_dir",
    "run_pipeline_with_stubs",
    "stub_corpus",
    "stubbed_pipeline_environment",
]
