"""Authoring-time hint engine wrapping the ADR-0.0.29-02 advisor (OBPI-0.0.30-03).

The engine reads a Python source file, runs ``radon.complexity.cc_visit`` for
per-function cyclomatic-complexity blocks, invokes the ADR-0.0.29-02
:class:`gzkit.complexity.advisor.engine.DiagnosisEngine` for each crossing,
and then projects only ``advise``-band diagnoses into
:class:`gzkit.complexity.authoring.hint.AuthoringHint` instances. ``warn`` and
``block``-band crossings are the trigger-time advisor's responsibility and
are filtered out at the authoring layer.

Per ADR-0.0.30 § Decision rationale #1 the projection is one-direction
(full -> light). The engine is consumed by OBPI-01 (CLI), OBPI-04 (protocol)
and OBPI-05 (justify integration); none of those surfaces is allowed to
fabricate a diagnosis or hint outside this engine.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Literal

from radon.complexity import cc_visit
from radon.visitors import Function

from gzkit.complexity.advisor.engine import AstContext, DiagnosisEngine
from gzkit.complexity.authoring.hint import AuthoringHint, project_diagnosis_to_hint
from gzkit.complexity.thresholds import ThresholdTable, load_threshold_table

__all__ = [
    "DEFAULT_RULE_PATH",
    "METRIC_KEY",
    "analyze",
]

METRIC_KEY = "radon_cc"
DEFAULT_RULE_PATH = Path(".gzkit/rules/complexity-thresholds.json")

_PrecedenceBand = Literal["approaching", "approaching_warn"]


def analyze(
    path: Path,
    table: ThresholdTable | None = None,
) -> tuple[AuthoringHint, ...]:
    """Return authoring hints for ``advise``-band crossings under ``path``.

    ``path`` may be a single ``.py`` file or a directory; in the directory
    case every ``.py`` file under the tree is analyzed. ``table`` defaults to
    the canonical threshold table at ``.gzkit/rules/complexity-thresholds.json``
    -- the caller can inject an alternative table for tests.

    Empty result (no advise-band crossings) returns ``()`` per REQ-0.0.30-03-05.
    """
    resolved = table if table is not None else load_threshold_table(DEFAULT_RULE_PATH)
    engine = DiagnosisEngine()
    hints: list[AuthoringHint] = []
    for source_file in _iter_python_files(path):
        hints.extend(_analyze_file(source_file, resolved, engine))
    return tuple(hints)


def _iter_python_files(target: Path) -> list[Path]:
    """Return ``.py`` files under ``target`` (file or directory)."""
    if target.is_file():
        return [target] if target.suffix == ".py" else []
    return sorted(target.rglob("*.py"))


def _analyze_file(
    source_file: Path,
    table: ThresholdTable,
    engine: DiagnosisEngine,
) -> list[AuthoringHint]:
    """Run radon + diagnosis-engine for each ``radon_cc`` crossing in one file."""
    source = source_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(source_file))
    radon_blocks = [b for b in cc_visit(source) if isinstance(b, Function)]
    func_nodes = _index_function_nodes(tree)
    hints: list[AuthoringHint] = []
    for block in radon_blocks:
        hint = _process_block(block, source_file, source, tree, func_nodes, table, engine)
        if hint is not None:
            hints.append(hint)
    return hints


def _process_block(
    block: Function,
    source_file: Path,
    source: str,
    tree: ast.Module,
    func_nodes: dict[int, ast.AST],
    table: ThresholdTable,
    engine: DiagnosisEngine,
) -> AuthoringHint | None:
    """Run the diagnosis engine for one radon block; project to hint when advise."""
    value = float(block.complexity)
    band = table.band_for(METRIC_KEY, value)
    if band is None or band.trigger_semantic != "advise":
        return None
    target_node = func_nodes.get(block.lineno)
    if target_node is None:
        return None
    ast_context = AstContext(
        file_path=str(source_file),
        source=source,
        tree=tree,
        target_node=target_node,
    )
    diagnosis = engine.diagnose(ast_context, METRIC_KEY, value, table)
    if diagnosis is None:
        return None
    precedence_band = _classify_precedence_band(table, METRIC_KEY, value)
    return project_diagnosis_to_hint(diagnosis, precedence_band=precedence_band)


def _classify_precedence_band(
    table: ThresholdTable,
    metric: str,
    value: float,
) -> _PrecedenceBand:
    """Classify ``value`` as upper (``approaching_warn``) or lower (``approaching``).

    Boundary is the midpoint between the advise band's ``absolute_number``
    and the warn band's ``absolute_number`` for ``metric``. When no warn
    band exists for the metric, classification falls back to ``approaching``
    (no upper edge to project against).
    """
    advise_abs = _band_absolute(table, metric, "advise")
    warn_abs = _band_absolute(table, metric, "warn")
    if advise_abs is None or warn_abs is None:
        return "approaching"
    midpoint = (advise_abs + warn_abs) / 2.0
    if value >= midpoint:
        return "approaching_warn"
    return "approaching"


def _band_absolute(
    table: ThresholdTable,
    metric: str,
    trigger: str,
) -> float | None:
    """Return ``absolute_number`` for the (metric, trigger) band, or ``None``."""
    for band in table.bands_for_metric(metric):
        if band.trigger_semantic == trigger:
            return band.absolute_number
    return None


def _index_function_nodes(tree: ast.Module) -> dict[int, ast.AST]:
    """Map ``lineno`` to the corresponding FunctionDef/AsyncFunctionDef node."""
    indexed: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            indexed[node.lineno] = node
    return indexed
