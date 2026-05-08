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
from datetime import date
from pathlib import Path

from radon.complexity import cc_visit
from radon.visitors import Function

from gzkit.complexity.advisor.diagnosis import AdvisorDiagnosis
from gzkit.complexity.advisor.engine import (
    AstContext,
    DiagnosisEngine,
    EngineError,
)
from gzkit.complexity.advisor.intrinsic import get_attestation
from gzkit.complexity.advisor.presentation import AdHocPresenter, AutoChainPresenter
from gzkit.complexity.thresholds import ThresholdTable, load_threshold_table
from gzkit.ledger import Ledger
from gzkit.ledger_events import intrinsic_complexity_attestation_event

DEFAULT_RULE_PATH = Path(".gzkit/rules/complexity-thresholds.md")
METRIC_KEY = "radon_cc"

_ATTEST_CONFIRMATION = "ATTEST"

# Attested info: (qualname, reason, attestor, date_val)
_AttestedInfo = tuple[str, str, str, str]


def _is_attest_tty_available() -> bool:
    """Return True when stdin and stdout are both attached to a real TTY."""
    try:
        return bool(sys.stdin.isatty()) and bool(sys.stdout.isatty())
    except (ValueError, OSError):
        return False


def _prompt_attest_confirmation() -> str:
    """Read the operator confirmation word from stdin."""
    return input("> ").strip()


def _resolve_ledger_path() -> Path:
    """Return the canonical ledger path relative to CWD."""
    return Path.cwd() / ".gzkit" / "ledger.jsonl"


def complexity_advise_cmd(
    *,
    path: str,
    json_output: bool = False,
    quiet: bool = False,  # noqa: ARG001 — accepted, surfaced via parser
    verbose: bool = False,  # noqa: ARG001
    dry_run: bool = False,  # noqa: ARG001
    auto_chain: bool = False,
    rule_path: str | None = None,
    attest_intrinsic: bool = False,
    reason: str | None = None,
    attestor: str | None = None,
) -> int:
    """Run advisor against ``path``; return exit code per the contract."""
    if attest_intrinsic:
        result = _run_attest_intrinsic(
            path=path, reason=reason, attestor=attestor, rule_path=rule_path
        )
        if result != 0:
            raise SystemExit(result)
        return 0

    target = Path(path)
    if not target.exists():
        print(f"error: path does not exist: {path}", file=sys.stderr)
        raise SystemExit(1)

    table = _load_table_or_exit(rule_path)
    engine = _build_engine_or_exit()

    diagnoses: list[AdvisorDiagnosis] = []
    attested_all: list[_AttestedInfo] = []
    functions_checked = 0
    for source_file in _iter_python_files(target):
        try:
            file_diagnoses, file_attested, file_func_count = _analyze_file(
                source_file, table, engine
            )
            functions_checked += file_func_count
            diagnoses.extend(file_diagnoses)
            attested_all.extend(file_attested)
        except SyntaxError as exc:
            print(f"error: failed to parse {source_file}: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        except EngineError as exc:
            print(f"error: engine: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc

    if json_output:
        print(_render_json(diagnoses))
    else:
        for _qualname, reason_val, attestor_val, date_val in attested_all:
            print(f"intrinsic complexity attested by {attestor_val!r} on {date_val}: {reason_val}")
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
) -> tuple[list[AdvisorDiagnosis], list[_AttestedInfo], int]:
    """Run attestation check and engine for each ``radon_cc`` crossing.

    Attested functions are short-circuited before the engine call — this
    avoids EngineError for functions whose practitioner-eye content is
    pending operator authoring.

    Returns:
        (diagnoses, attested_infos, func_block_count)
    """
    source = source_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(source_file))
    radon_blocks = [b for b in cc_visit(source) if isinstance(b, Function)]
    func_nodes_by_line = _index_function_nodes(tree)
    diagnoses: list[AdvisorDiagnosis] = []
    attested: list[_AttestedInfo] = []

    for block in radon_blocks:
        if table.band_for(METRIC_KEY, float(block.complexity)) is None:
            continue
        target_node = func_nodes_by_line.get(block.lineno)
        if target_node is None:
            continue

        qualname = (
            f"{block.classname}.{block.name}" if getattr(block, "classname", None) else block.name
        )
        attestation = get_attestation(str(source_file.absolute()), qualname)
        if attestation is not None:
            reason_val, attestor_val, date_val = attestation
            attested.append((qualname, reason_val, attestor_val, date_val))
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

    return diagnoses, attested, len(radon_blocks)


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


def _run_attest_intrinsic(
    *,
    path: str,
    reason: str | None,
    attestor: str | None,
    rule_path: str | None,
) -> int:
    """Commit-time path: measure + gate + emit intrinsic attestation event.

    Expects ``path`` as ``<file_path>:<qualname>``. Fails closed on parse
    error, missing reason/attestor, non-crossing function, and headless
    invocation — no ledger event is emitted in any failure branch.
    """
    parts = path.rsplit(":", 1)
    if len(parts) != 2:
        print(
            f"error: --attest-intrinsic requires <file_path>:<qualname>; got {path!r}",
            file=sys.stderr,
        )
        return 1

    file_path_str, qualname = parts

    if not reason:
        print("error: --reason is required for --attest-intrinsic", file=sys.stderr)
        return 1
    if not attestor:
        print("error: --attestor is required for --attest-intrinsic", file=sys.stderr)
        return 1

    source_file = Path(file_path_str)
    if not source_file.exists():
        print(f"error: path does not exist: {file_path_str}", file=sys.stderr)
        return 1

    table = _load_table_or_exit(rule_path)

    try:
        source = source_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {file_path_str}: {exc}", file=sys.stderr)
        return 2

    radon_blocks = [b for b in cc_visit(source) if isinstance(b, Function)]
    target_block = None
    for block in radon_blocks:
        block_qualname = (
            f"{block.classname}.{block.name}" if getattr(block, "classname", None) else block.name
        )
        if block_qualname == qualname:
            target_block = block
            break

    if target_block is None:
        print(
            f"error: function {qualname!r} not found in {file_path_str}",
            file=sys.stderr,
        )
        return 1

    band = table.band_for(METRIC_KEY, float(target_block.complexity))
    if band is None:
        print(
            f"error: {qualname!r} does not cross any threshold band"
            f" (cc={target_block.complexity}); attestation refused",
            file=sys.stderr,
        )
        return 1

    if not _is_attest_tty_available():
        print(
            "error: --attest-intrinsic requires an interactive TTY; headless invocation refused",
            file=sys.stderr,
        )
        return 1

    print("\n=== Intrinsic Complexity Attestation ===")
    print(f"  Function: {qualname}")
    print(f"  File:     {file_path_str}")
    print(f"  Metric:   {METRIC_KEY} = {target_block.complexity}")
    print(f"  Band:     {band.trigger_semantic}")
    print(f"  Reason:   {reason}")
    print(f"  Attestor: {attestor}")
    print(
        f"\nType the word {_ATTEST_CONFIRMATION!r} (uppercase, no quotes) to confirm,"
        " or anything else to abort:"
    )

    response = _prompt_attest_confirmation()
    if response != _ATTEST_CONFIRMATION:
        print(f"error: attestation declined (got {response!r})", file=sys.stderr)
        return 1

    ledger_path = _resolve_ledger_path()
    ledger = Ledger(ledger_path)
    attestation_date = date.today().isoformat()
    event = intrinsic_complexity_attestation_event(
        file_path=file_path_str,
        qualname=qualname,
        reason=reason,
        attestor=attestor,
        attestation_date=attestation_date,
        metric=METRIC_KEY,
        crossing_band=band.trigger_semantic,
        crossing_value=float(target_block.complexity),
    )
    ledger.append(event)

    receipt_id = event.id
    print(f"Intrinsic complexity attested: {receipt_id}")
    return 0


__all__ = [
    "DEFAULT_RULE_PATH",
    "METRIC_KEY",
    "complexity_advise_cmd",
]
