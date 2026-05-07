"""Auto-chain hook installer and runtime (OBPI-0.0.29-05).

Install mode replaces the ``xenon-complexity`` pre-commit entry with a
composite hook that runs xenon first and chains to the complexity advisor
on failure. Run mode wraps the advisor in OBPI-09's timeout primitive and
returns the appropriate exit code per REQ-0.0.29-05-06.

Install::

    python -m gzkit.hooks.install_complexity_advisor

Run (called by the shell hook)::

    python -m gzkit.hooks.install_complexity_advisor --run src/foo.py src/bar.py
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from radon.complexity import cc_visit
from radon.visitors import Function

from gzkit.complexity.advisor.diagnosis import AdvisorDiagnosis
from gzkit.complexity.advisor.engine import AstContext, DiagnosisEngine, EngineError
from gzkit.complexity.advisor.timeout import TimeoutOk, run_with_timeout
from gzkit.complexity.thresholds import load_threshold_table

_DEFAULT_RULE_PATH = Path(".gzkit/rules/complexity-thresholds.md")
_FAILURE_LOG_PATH = Path(".gzkit/insights/advisor-failures.jsonl")
_METRIC_KEY = "radon_cc"
_DEFAULT_TIMEOUT_S = 30.0

_HOOK_ID = "complexity-advisor-auto-chain"
_HOOK_NAME = "complexity advisor (xenon + advisor auto-chain)"
_HOOK_ENTRY = ".gzkit/hooks/pre-commit-complexity-advisor"

_NEW_HOOK_YAML = f"""\
      - id: {_HOOK_ID}
        name: {_HOOK_NAME}
        entry: {_HOOK_ENTRY}
        language: script
        pass_filenames: false
        types: [python]
        stages: [pre-commit]
"""


def run_auto_chain(file_paths: list[str], *, timeout_s: float = _DEFAULT_TIMEOUT_S) -> int:
    """Run the advisor on staged files with timeout. Returns hook exit code."""
    result = run_with_timeout(
        lambda: _diagnose_files(file_paths),
        timeout_s=timeout_s,
        log_path=_FAILURE_LOG_PATH,
        context_file_paths=file_paths,
        context_invocation="auto-chain",
    )
    if not isinstance(result, TimeoutOk):
        print(
            "warning: complexity advisor timed out; commit proceeding (fail-open)",
            file=sys.stderr,
        )
        return 0

    diagnoses: list[AdvisorDiagnosis] = result.value
    has_block = any(d.crossing_band == "block" for d in diagnoses)

    if has_block:
        _render_to_stderr(diagnoses)
        return 1

    if diagnoses:
        _render_to_stderr(diagnoses)

    return 0


def _diagnose_files(file_paths: list[str]) -> list[AdvisorDiagnosis]:
    """Run the diagnosis engine on the given files."""
    rule_path = _DEFAULT_RULE_PATH
    if not rule_path.exists():
        print(
            f"warning: threshold rule not found: {rule_path.as_posix()}; skipping advisor",
            file=sys.stderr,
        )
        return []

    table = load_threshold_table(rule_path)
    try:
        engine = DiagnosisEngine()
    except EngineError as exc:
        print(f"warning: engine init failed: {exc}; skipping advisor", file=sys.stderr)
        return []

    all_diagnoses: list[AdvisorDiagnosis] = []
    for file_path_str in file_paths:
        file_path = Path(file_path_str)
        if not file_path.exists() or file_path.suffix != ".py":
            continue
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=file_path_str)
        except (OSError, SyntaxError) as exc:
            print(f"warning: skipping {file_path_str}: {exc}", file=sys.stderr)
            continue

        radon_blocks = [b for b in cc_visit(source) if isinstance(b, Function)]
        func_nodes_by_line = _index_function_nodes(tree)

        for block in radon_blocks:
            if table.band_for(_METRIC_KEY, float(block.complexity)) is None:
                continue
            target_node = func_nodes_by_line.get(block.lineno)
            if target_node is None:
                continue
            ast_context = AstContext(
                file_path=file_path_str,
                source=source,
                tree=tree,
                target_node=target_node,
            )
            try:
                diagnosis = engine.diagnose(
                    ast_context, _METRIC_KEY, float(block.complexity), table
                )
            except EngineError as exc:
                print(f"warning: engine error on {file_path_str}: {exc}", file=sys.stderr)
                continue
            if diagnosis is not None:
                all_diagnoses.append(diagnosis)

    return all_diagnoses


def _index_function_nodes(tree: ast.Module) -> dict[int, ast.AST]:
    """Map lineno to the corresponding FunctionDef/AsyncFunctionDef node."""
    indexed: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            indexed[node.lineno] = node
    return indexed


def _render_to_stderr(diagnoses: list[AdvisorDiagnosis]) -> None:
    """Render diagnoses to stderr (REQ-0.0.29-05-06)."""
    for index, diag in enumerate(diagnoses, start=1):
        proof_first = diag.proof[0]
        proof_last = diag.proof[-1]
        print(
            f"[{index}] metric={diag.metric} value={diag.crossing_value} band={diag.crossing_band}",
            file=sys.stderr,
        )
        print(f"  Archetype: {diag.archetype.value}", file=sys.stderr)
        print(
            f"  Authority: {diag.doctrinal_frame.authority} ({diag.doctrinal_frame.citation})",
            file=sys.stderr,
        )
        print(
            f"  Proof: {Path(proof_first.file_path).as_posix()}"
            f":{proof_first.start_line}-{proof_last.end_line}",
            file=sys.stderr,
        )
        print(f"  Recommended move: {diag.recommended_move}", file=sys.stderr)


def install() -> int:
    """Replace xenon-complexity with the composite auto-chain hook in .pre-commit-config.yaml."""
    config_path = Path(".pre-commit-config.yaml")
    if not config_path.exists():
        print("error: .pre-commit-config.yaml not found", file=sys.stderr)
        return 1

    content = config_path.read_text(encoding="utf-8")
    if _HOOK_ID in content:
        print(f"Hook '{_HOOK_ID}' already present in .pre-commit-config.yaml")
        return 0

    marker = "      - id: xenon-complexity"
    if marker not in content:
        print(
            "warning: xenon-complexity entry not found; appending hook to first local repo",
            file=sys.stderr,
        )
        content = _append_hook_to_first_repo(content)
    else:
        content = _replace_xenon_entry(content)

    config_path.write_text(content, encoding="utf-8")
    print(f"Installed hook '{_HOOK_ID}' in .pre-commit-config.yaml")
    print(f"  Replaced: xenon-complexity -> {_HOOK_ID}")
    print(f"  Skip:     SKIP={_HOOK_ID} git commit")
    return 0


def _replace_xenon_entry(content: str) -> str:
    """Replace the xenon-complexity entry with the composite hook."""
    lines = content.splitlines(keepends=True)
    result: list[str] = []
    skip = False
    for line in lines:
        if "- id: xenon-complexity" in line:
            skip = True
            result.append(_NEW_HOOK_YAML)
            continue
        if skip:
            if line.strip().startswith("- id:") or (line.strip() and not line.startswith(" ")):
                skip = False
                result.append(line)
            continue
        result.append(line)
    return "".join(result)


def _append_hook_to_first_repo(content: str) -> str:
    """Fallback: append hook after the first ``hooks:`` key in a local repo."""
    lines = content.splitlines(keepends=True)
    result: list[str] = []
    inserted = False
    for i, line in enumerate(lines):
        result.append(line)
        if not inserted and "hooks:" in line and i > 0:
            result.append("\n")
            result.append(_NEW_HOOK_YAML)
            inserted = True
    return "".join(result)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Complexity advisor auto-chain hook installer and runtime."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--install",
        action="store_true",
        help="Install the hook in .pre-commit-config.yaml",
    )
    group.add_argument(
        "--run",
        nargs="+",
        metavar="FILE",
        help="Run the advisor on staged files (called by the shell hook)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=_DEFAULT_TIMEOUT_S,
        help=f"Advisor timeout in seconds (default: {_DEFAULT_TIMEOUT_S})",
    )
    return parser


def main() -> int:
    """Entry point for ``python -m gzkit.hooks.install_complexity_advisor``."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.install:
        return install()
    return run_auto_chain(args.run, timeout_s=args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
