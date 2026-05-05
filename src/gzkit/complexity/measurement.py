"""Measurement orchestration for the complexity baseline pipeline.

Public entrypoint :func:`measure_corpus` consumes an
:class:`gzkit.models.exemplar.ExemplarCorpus` and produces a
:class:`gzkit.complexity.baseline.BaselineArtifact` written to
``output_dir/baseline.json`` + ``output_dir/baseline.summary.md``.

Determinism: the only non-static inputs are the corpus revision, the pinned
SHAs (under operator control), and the installed tool versions (read via
:mod:`importlib.metadata`).  No clock reads, no set iteration, no
floating-point sorted-by-string.  See :mod:`gzkit.complexity.baseline` for
the canonical-shape JSON contract.

Subprocess discipline: every tool invocation uses list-form
:func:`subprocess.run` with ``encoding="utf-8"``; the shell-pass-through flag
is forbidden per ``.claude/rules/cross-platform.md``.  Missing tool binaries
fail closed with :class:`MissingMeasurementToolError` (REQ-0.0.27-03-05).

Path filter discipline: every project must declare at least one
``included_paths`` glob.  Whole-project measurement (empty includes) is
rejected with :class:`WholeProjectMeasurementRejectedError`
(REQ-0.0.27-03-03).
"""

from __future__ import annotations

import csv
import importlib.metadata
import io
import json
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path

from gzkit.complexity.aggregator import aggregate_cross_project, aggregate_project
from gzkit.complexity.baseline import (
    BaselineArtifact,
    ProjectBaseline,
    render_summary,
    serialize_baseline,
)
from gzkit.models.exemplar import ExemplarCorpus, ExemplarProject, load_corpus

# Canonical 12-metric keys.  Order is load-bearing — every per-project and
# cross-project block iterates this tuple, so a baseline.json's metric order
# is byte-deterministic across runs.
CANONICAL_METRICS: tuple[str, ...] = (
    "radon_cc",
    "radon_mi",
    "radon_hal_volume",
    "radon_hal_difficulty",
    "radon_hal_effort",
    "radon_raw_nloc",
    "radon_raw_lloc",
    "lizard_nloc",
    "lizard_param_count",
    "lizard_nesting_depth",
    "lizard_ccn",
    "cohesion_lcom4",
)

# Required external binaries.  Order is alphabetical for deterministic
# error messages when more than one is missing.
_REQUIRED_TOOLS: tuple[str, ...] = ("cohesion", "lizard", "radon")


class MissingMeasurementToolError(RuntimeError):
    """Raised when a required measurement tool binary is not on ``PATH``.

    Carries the tool name so callers can surface the recovery hint without
    re-parsing the message.
    """

    def __init__(self, tool: str) -> None:
        self.tool = tool
        super().__init__(f"Missing measurement tool binary: {tool!r}")


class CorpusLoaderError(RuntimeError):
    """Raised when the corpus file cannot be loaded or parsed."""


class WholeProjectMeasurementRejectedError(RuntimeError):
    """Raised when a project declares no ``included_paths`` filter.

    The doctrine forbids whole-project measurement: the corpus is curated
    at the project + module-subset level, not at the project level.  A
    project with empty includes is a corpus authoring defect, not a
    measurement edge case.
    """


def safe_load_corpus(path: Path) -> ExemplarCorpus:
    """Load *path* as an :class:`ExemplarCorpus`, wrapping all I/O failures.

    The doctrine wraps OS errors (file not found, permission denied),
    decode errors (invalid UTF-8), JSON parse errors, and Pydantic
    validation errors at the corpus-loading boundary so the CLI exit-3
    path can react to "the corpus could not be loaded" without depending
    on which underlying exception fired (REQ-0.0.27-03-05).
    """
    try:
        return load_corpus(path)
    except (OSError, ValueError) as exc:
        raise CorpusLoaderError(f"Failed to load corpus from {path!s}: {exc}") from exc


def measure_corpus(
    corpus: ExemplarCorpus,
    output_dir: Path,
    *,
    cache_root: Path | None = None,
) -> BaselineArtifact:
    """Run the full measurement pipeline against *corpus*.

    Workflow:

    1. Assert all required tool binaries are present (fail closed).
    2. Resolve every project's tree (clone-if-absent at SHA, under
       *cache_root*; in unit tests, :func:`_resolve_tree` is patched).
    3. Apply the project's ``included_paths`` / ``excluded_paths`` filter.
    4. Run :func:`_measure_project` for each filtered set.
    5. Aggregate per-project + cross-project distributions.
    6. Serialize to ``output_dir/baseline.json`` +
       ``output_dir/baseline.summary.md``.

    Returns the :class:`BaselineArtifact` constructed from the run.
    """
    _assert_tool_binaries_present()
    cache = _default_cache_root(cache_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    project_baselines, pooled_raw = _measure_all_projects(corpus, cache)
    cross = aggregate_cross_project(
        projects=project_baselines,
        pooled_raw=pooled_raw,
        metric_keys=CANONICAL_METRICS,
    )
    artifact = BaselineArtifact(
        corpus_revision=corpus.corpus_revision,
        corpus_schema_version=corpus.schema_version,
        tool_versions=_collect_tool_versions(),
        projects=tuple(project_baselines),
        cross_project=cross,
    )
    _write_baseline_outputs(artifact, output_dir)
    return artifact


def _measure_all_projects(
    corpus: ExemplarCorpus,
    cache_root: Path,
) -> tuple[list[ProjectBaseline], dict[str, list[float]]]:
    """Walk every corpus project and return (per-project baselines, pooled raw values)."""
    pooled_raw: dict[str, list[float]] = {key: [] for key in CANONICAL_METRICS}
    project_baselines: list[ProjectBaseline] = []
    for project in corpus.projects:
        tree = _resolve_tree(project, cache_root)
        paths = _apply_path_filter(tree, project)
        raw = _measure_project(tree, paths)
        project_baselines.append(
            aggregate_project(
                name=project.name,
                commit_sha=project.commit_sha,
                archetypal_cell=project.archetypal_cell,
                raw_metrics=raw,
                metric_keys=CANONICAL_METRICS,
            )
        )
        for metric_key, values in raw.items():
            pooled_raw[metric_key].extend(float(value) for value in values)
    return project_baselines, pooled_raw


def _assert_tool_binaries_present() -> None:
    """Raise :class:`MissingMeasurementToolError` if any tool is missing."""
    for tool in _REQUIRED_TOOLS:
        if shutil.which(tool) is None:
            raise MissingMeasurementToolError(tool)


def _default_cache_root(cache_root: Path | None) -> Path:
    """Resolve *cache_root*, defaulting to ``~/.cache/gzkit/exemplar-corpus``."""
    if cache_root is not None:
        return cache_root
    return Path.home() / ".cache" / "gzkit" / "exemplar-corpus"


def _collect_tool_versions() -> dict[str, str]:
    """Return a sorted-key dict of installed tool versions.

    Uses :mod:`importlib.metadata` so determinism does not depend on
    subprocess output formatting.  A missing distribution surfaces as the
    sentinel string ``"unknown"`` — the situation only arises when a tool
    binary is on ``PATH`` but its Python distribution is absent (e.g. a
    shim install), which is itself a degraded-environment signal.
    """
    versions: dict[str, str] = {}
    for tool in _REQUIRED_TOOLS:
        try:
            versions[tool] = importlib.metadata.version(tool)
        except importlib.metadata.PackageNotFoundError:
            versions[tool] = "unknown"
    return dict(sorted(versions.items()))


def _resolve_tree(project: ExemplarProject, cache_root: Path) -> Path:
    """Return the local path of *project*'s working tree at its pinned SHA.

    Clone-if-absent semantics: the tree lives at
    ``cache_root/<name>-<sha[:12]>``.  In unit tests this function is
    monkey-patched so no network or git subprocess fires.

    Recovery: if the cached tree exists but is corrupt, the operator
    deletes it and re-runs; this function does not attempt automatic
    recovery to avoid hiding upstream-cache corruption.
    """
    target = cache_root / f"{project.name}-{project.commit_sha[:12]}"
    if target.is_dir():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", str(project.canonical_url), str(target)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(target), "checkout", project.commit_sha],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return target


def _apply_path_filter(tree: Path, project: ExemplarProject) -> tuple[Path, ...]:
    """Resolve *project*'s ``included_paths`` minus ``excluded_paths``.

    Globs are expanded relative to *tree*.  An empty include list raises
    :class:`WholeProjectMeasurementRejectedError` per REQ-0.0.27-03-03.
    """
    if not project.included_paths:
        raise WholeProjectMeasurementRejectedError(
            f"Project {project.name!r} has no included_paths; "
            "whole-project measurement is rejected."
        )
    included: set[Path] = set()
    for pattern in project.included_paths:
        for match in tree.glob(pattern):
            if match.is_file():
                included.add(match.resolve())
    for excluded in project.excluded_paths_with_rationale:
        for match in tree.glob(excluded.glob):
            if match.is_file():
                included.discard(match.resolve())
    return tuple(sorted(included))


def _measure_project(tree: Path, paths: Sequence[Path]) -> Mapping[str, list[float]]:
    """Run every tool wrapper against *paths* and pool the per-metric values."""
    if not paths:
        return {key: [] for key in CANONICAL_METRICS}
    results: dict[str, list[float]] = {key: [] for key in CANONICAL_METRICS}
    for path in paths:
        results["radon_cc"].extend(_run_radon_cc(path))
        results["radon_mi"].extend(_run_radon_mi(path))
        hal = _run_radon_hal(path)
        results["radon_hal_volume"].extend(hal["volume"])
        results["radon_hal_difficulty"].extend(hal["difficulty"])
        results["radon_hal_effort"].extend(hal["effort"])
        raw = _run_radon_raw(path)
        results["radon_raw_nloc"].extend(raw["nloc"])
        results["radon_raw_lloc"].extend(raw["lloc"])
        liz = _run_lizard(path)
        results["lizard_nloc"].extend(liz["nloc"])
        results["lizard_param_count"].extend(liz["param_count"])
        results["lizard_nesting_depth"].extend(liz["nesting_depth"])
        results["lizard_ccn"].extend(liz["ccn"])
        results["cohesion_lcom4"].extend(_run_cohesion(path))
    return results


def _run_radon_cc(path: Path) -> list[float]:
    """Run ``radon cc --json`` and return per-function complexity values.

    ``radon cc --json`` emits ``{filepath: [{"complexity": int, ...}, ...]}``.
    Empty arrays (file with no functions) are valid; non-zero exit is
    treated as "no values" rather than raising — measurement of one file
    must not abort the whole pipeline.
    """
    completed = subprocess.run(
        ["radon", "cc", "--json", "--no-assert", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        return []
    payload = json.loads(completed.stdout)
    values: list[float] = []
    for entries in payload.values():
        if isinstance(entries, list):
            for entry in entries:
                if isinstance(entry, dict) and "complexity" in entry:
                    values.append(float(entry["complexity"]))
    return values


def _run_radon_mi(path: Path) -> list[float]:
    """Run ``radon mi --json`` and return the per-file MI values.

    ``radon mi --json`` emits ``{filepath: {"mi": float, ...}}``.  A file
    with no measurable MI returns an empty list.
    """
    completed = subprocess.run(
        ["radon", "mi", "--json", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        return []
    payload = json.loads(completed.stdout)
    values: list[float] = []
    for entry in payload.values():
        if isinstance(entry, dict) and "mi" in entry:
            values.append(float(entry["mi"]))
    return values


def _run_radon_hal(path: Path) -> dict[str, list[float]]:
    """Run ``radon hal --json`` and split into volume/difficulty/effort lists.

    ``radon hal --json`` emits per-file aggregate Halstead metrics
    ``{filepath: {"total": {"volume": ..., "difficulty": ..., "effort": ...}}}``.
    """
    completed = subprocess.run(
        ["radon", "hal", "--json", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    out: dict[str, list[float]] = {"volume": [], "difficulty": [], "effort": []}
    if completed.returncode != 0 or not completed.stdout.strip():
        return out
    payload = json.loads(completed.stdout)
    for entry in payload.values():
        block = entry.get("total") if isinstance(entry, dict) else None
        if isinstance(block, dict):
            _append_if_number(out["volume"], block.get("volume"))
            _append_if_number(out["difficulty"], block.get("difficulty"))
            _append_if_number(out["effort"], block.get("effort"))
    return out


def _run_radon_raw(path: Path) -> dict[str, list[float]]:
    """Run ``radon raw --json`` and split into nloc/lloc lists.

    ``radon raw --json`` emits per-file SLOC counts; we record NLOC and
    LLOC since they are the doctrine-cited size signals.
    """
    completed = subprocess.run(
        ["radon", "raw", "--json", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    out: dict[str, list[float]] = {"nloc": [], "lloc": []}
    if completed.returncode != 0 or not completed.stdout.strip():
        return out
    payload = json.loads(completed.stdout)
    for entry in payload.values():
        if isinstance(entry, dict):
            _append_if_number(out["nloc"], entry.get("sloc"))
            _append_if_number(out["lloc"], entry.get("lloc"))
    return out


def _run_lizard(path: Path) -> dict[str, list[float]]:
    """Run ``lizard -End --csv`` and split into nloc/param/nesting/ccn lists.

    The ``-End`` extension flag activates lizard's nesting-depth analyzer
    (``lizard_ext.lizardnd``), which appends ``ND`` as a trailing column.
    Without it, lizard 1.22.1's CSV layout has 11 columns and exposes no
    nesting-depth signal at all — column 6 is the file path string, not
    nesting depth (GHI #398).  The resulting layout is 12 columns:
    NLOC, CCN, token_count, PARAM, length, location, file, name,
    signature, start_line, end_line, ND.
    """
    completed = subprocess.run(
        ["lizard", "-End", "--csv", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    out: dict[str, list[float]] = {
        "nloc": [],
        "ccn": [],
        "param_count": [],
        "nesting_depth": [],
    }
    if not completed.stdout.strip():
        return out
    reader = csv.reader(io.StringIO(completed.stdout))
    for row in reader:
        _absorb_lizard_row(row, out)
    return out


def _absorb_lizard_row(row: list[str], out: dict[str, list[float]]) -> None:
    """Parse one lizard ``-End --csv`` row; ND is the trailing 12th column."""
    if len(row) < 12:
        return
    _append_if_numeric_str(out["nloc"], row[0])
    _append_if_numeric_str(out["ccn"], row[1])
    _append_if_numeric_str(out["param_count"], row[3])
    _append_if_numeric_str(out["nesting_depth"], row[11])


def _run_cohesion(path: Path) -> list[float]:
    """Run ``cohesion -f <path>`` and return per-class LCOM4 values.

    The ``-f``/``--files`` flag is cohesion's file-input mode.  The
    earlier ``-d`` invocation invoked the directory mode, which rejects a
    file path with a usage error and produces empty stdout, silently
    yielding zero samples for every project (GHI #398).  Cohesion has no
    JSON mode; output is text of shape ``Class: <name> ... Total: <pct>%``.
    """
    completed = subprocess.run(
        ["cohesion", "-f", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if not completed.stdout:
        return []
    values: list[float] = []
    for line in completed.stdout.splitlines():
        token = line.strip()
        if "Total:" not in token:
            continue
        tail = token.split("Total:", 1)[1].strip().rstrip("%").strip()
        try:
            values.append(float(tail))
        except ValueError:
            continue
    return values


def _append_if_number(target: list[float], value: object) -> None:
    """Append *value* to *target* if it is a real ``int``/``float``."""
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)):
        target.append(float(value))


def _append_if_numeric_str(target: list[float], value: str) -> None:
    """Append *value* parsed as ``float`` to *target* if it is a number."""
    token = value.strip()
    if not token:
        return
    try:
        target.append(float(token))
    except ValueError:
        return


def _write_baseline_outputs(artifact: BaselineArtifact, output_dir: Path) -> None:
    """Serialize *artifact* to ``baseline.json`` + ``baseline.summary.md``."""
    json_path = output_dir / "baseline.json"
    summary_path = output_dir / "baseline.summary.md"
    json_path.write_text(serialize_baseline(artifact), encoding="utf-8")
    summary_path.write_text(render_summary(artifact), encoding="utf-8")


__all__ = [
    "CANONICAL_METRICS",
    "CorpusLoaderError",
    "MissingMeasurementToolError",
    "WholeProjectMeasurementRejectedError",
    "measure_corpus",
    "safe_load_corpus",
]
