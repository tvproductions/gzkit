"""Handler for ``gz complexity advise`` (OBPI-0.0.29-03).

Wraps the ADR-0.0.29 trigger-time response surface. Reads the canonical
threshold table at ``.gzkit/rules/complexity-thresholds.md`` (ADR-0.0.28),
measures the target file or directory via ``radon.complexity.cc_visit``,
and runs the OBPI-0.0.29-02 :class:`DiagnosisEngine` for each per-function
``radon_cc`` crossing.

Output Contract: default human prose names archetype, doctrinal authority,
proof line range, and recommended-move excerpt for each diagnosis.
``--json`` mode emits the canonical Pydantic serialization as a JSON array.

Exit codes (binding, REQ-0.0.29-03-02):

* ``0`` — clean run (no crossings) or all crossings stayed at warn/advise band.
* ``1`` — user/config error (bad path, malformed flags).
* ``2`` — system/IO error (missing threshold table, AST parse error).
* ``3`` — policy breach (one or more block-band crossings).
"""

from __future__ import annotations

import ast
import json
import sys
from collections.abc import Iterator
from pathlib import Path

from radon.complexity import cc_visit
from radon.visitors import Function

from gzkit.complexity.advisor.diagnosis import AdvisorDiagnosis
from gzkit.complexity.advisor.engine import (
    AstContext,
    DiagnosisEngine,
    EngineError,
)
from gzkit.complexity.advisor.presentation import AdHocPresenter, AutoChainPresenter
from gzkit.complexity.thresholds import ThresholdTable, load_threshold_table

DEFAULT_RULE_PATH = Path(".gzkit/rules/complexity-thresholds.md")
METRIC_KEY = "radon_cc"


def complexity_advise_cmd(
    *,
    path: str,
    json_output: bool = False,
    quiet: bool = False,  # noqa: ARG001 — accepted, surfaced via parser
    verbose: bool = False,  # noqa: ARG001
    dry_run: bool = False,  # noqa: ARG001
    auto_chain: bool = False,
    rule_path: str | None = None,
) -> int:
    """Run advisor against ``path``; return exit code per the contract."""
    target = Path(path)
    if not target.exists():
        print(f"error: path does not exist: {path}", file=sys.stderr)
        raise SystemExit(1)

    table = _load_table_or_exit(rule_path)
    engine = _build_engine_or_exit()

    diagnoses: list[AdvisorDiagnosis] = []
    functions_checked = 0
    for source_file in _iter_python_files(target):
        try:
            file_diagnoses, file_func_count = _analyze_file(source_file, table, engine)
            functions_checked += file_func_count
            diagnoses.extend(file_diagnoses)
        except SyntaxError as exc:
            print(f"error: failed to parse {source_file}: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        except EngineError as exc:
            print(f"error: engine: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc

    if json_output:
        print(_render_json(diagnoses))
    else:
        metrics_checked = 1  # currently only radon_cc
        presenter = AutoChainPresenter() if auto_chain else AdHocPresenter()
        output = presenter.render(
            diagnoses, metrics_checked=metrics_checked, functions_checked=functions_checked
        )
        if output:
            print(output)

    exit_code = _resolve_exit_code(diagnoses)
    if exit_code != 0:
        raise SystemExit(exit_code)
    return 0


def _load_table_or_exit(rule_path: str | None) -> ThresholdTable:
    target = Path(rule_path) if rule_path else DEFAULT_RULE_PATH
    if not target.exists():
        print(
            f"error: threshold rule not found: {target.as_posix()}",
            file=sys.stderr,
        )
        raise SystemExit(2)
    try:
        return load_threshold_table(target)
    except (ValueError, OSError) as exc:
        print(f"error: failed to load threshold table: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def _build_engine_or_exit() -> DiagnosisEngine:
    try:
        return DiagnosisEngine()
    except EngineError as exc:
        print(f"error: engine init: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def _iter_python_files(target: Path) -> Iterator[Path]:
    """Yield Python source files under ``target`` (file or directory)."""
    if target.is_file():
        if target.suffix == ".py":
            yield target
        return
    yield from sorted(target.rglob("*.py"))


def _analyze_file(
    source_file: Path,
    table: ThresholdTable,
    engine: DiagnosisEngine,
) -> tuple[list[AdvisorDiagnosis], int]:
    """Run the engine for each ``radon_cc`` crossing in ``source_file``.

    Returns:
        A tuple of (diagnoses list, count of function blocks analyzed).
    """
    source = source_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(source_file))
    radon_blocks = [b for b in cc_visit(source) if isinstance(b, Function)]
    func_nodes_by_line = _index_function_nodes(tree)
    diagnoses: list[AdvisorDiagnosis] = []
    for block in radon_blocks:
        if table.band_for(METRIC_KEY, float(block.complexity)) is None:
            continue
        target_node = func_nodes_by_line.get(block.lineno)
        if target_node is None:
            continue
        ast_context = AstContext(
            file_path=str(source_file),
            source=source,
            tree=tree,
            target_node=target_node,
        )
        diagnosis = engine.diagnose(ast_context, METRIC_KEY, float(block.complexity), table)
        if diagnosis is not None:
            diagnoses.append(diagnosis)
    return diagnoses, len(radon_blocks)


def _index_function_nodes(tree: ast.Module) -> dict[int, ast.AST]:
    """Map ``lineno`` to the corresponding FunctionDef/AsyncFunctionDef node."""
    indexed: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            indexed[node.lineno] = node
    return indexed


def _render_json(diagnoses: list[AdvisorDiagnosis]) -> str:
    """Emit AdvisorDiagnosis list as a JSON array (REQ-0.0.29-03-08)."""
    payload = [d.model_dump(mode="json") for d in diagnoses]
    return json.dumps(payload, indent=2, sort_keys=True)


def _resolve_exit_code(diagnoses: list[AdvisorDiagnosis]) -> int:
    """Return 3 if any block-band crossing, else 0 (REQ-0.0.29-03-02)."""
    return 3 if any(d.crossing_band == "block" for d in diagnoses) else 0


__all__ = [
    "DEFAULT_RULE_PATH",
    "METRIC_KEY",
    "complexity_advise_cmd",
]
