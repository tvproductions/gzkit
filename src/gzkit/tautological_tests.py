"""AST scanner, disposition engine, baseline/waivers manager, and drift gate validator.

Implements the decommission-tautological-tests chore infrastructure (OBPI-0.0.59-04).
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from gzkit.commands.validate_cmd import ValidationError
from gzkit.models.tautological_tests import (
    Baseline,
    ProposedDisposition,
    TautologicalTestOperation,
)

# Hardcoded self-exemption: this file path is never counted in the operation scan.
# Rationale: the file that lists exemptions cannot itself be subject to the gate it governs.
# (2am-operator circular-dependency analysis)
_WAIVERS_SELF_EXCLUSION = "data/tautological_test_waivers.json"

_FILESYSTEM_CALL_NAMES: frozenset[str] = frozenset(
    {"open", "read_text", "read_bytes", "exists", "is_file", "is_dir", "stat"}
)

_OS_PATH_ATTRS: frozenset[str] = frozenset(
    {"exists", "isfile", "isdir", "join", "abspath", "realpath"}
)

_FIXTURE_FUNCTION_NAMES: frozenset[str] = frozenset(
    {"setUp", "setUpClass", "tearDown", "tearDownClass", "setUpModule", "tearDownModule"}
)

_LEDGER_HINTS: frozenset[str] = frozenset({"ledger", "receipt", ".jsonl", "ledger.jsonl"})
_SCHEMA_HINTS: frozenset[str] = frozenset({"schema", "config", ".json", "manifest"})


def _extract_context_hint(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """Extract a rough context hint from a function's source via string constant walk."""
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            return child.value
    return None


def _has_filesystem_op(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[bool, str, int]:
    """Return (found, operation_kind, line_number) for the first filesystem op."""
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            # open(...) or Path(...).read_text() etc.
            if isinstance(child.func, ast.Name) and child.func.id in _FILESYSTEM_CALL_NAMES:
                return True, child.func.id, child.lineno
            if isinstance(child.func, ast.Attribute):
                attr = child.func.attr
                if attr in _FILESYSTEM_CALL_NAMES:
                    return True, attr, child.lineno
                # os.path.* access
                if (
                    isinstance(child.func.value, ast.Attribute)
                    and child.func.value.attr == "path"
                    and attr in _OS_PATH_ATTRS
                ):
                    return True, f"os.path.{attr}", child.lineno
    return False, "", 0


def _has_assertion(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[bool, str]:
    """Return (found, assertion_kind) for the first assertion in a function."""
    for child in ast.walk(node):
        if isinstance(child, ast.Assert):
            return True, "assert"
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr.startswith("assert")
        ):
            return True, child.func.attr
    return False, ""


_CLI_INVOKE_ATTR = "invoke"
_SUBPROCESS_LAUNCH_ATTRS: frozenset[str] = frozenset({"run", "check_output", "check_call", "Popen"})
_CLI_ENTRY_TOKENS: frozenset[str] = frozenset({"gz", "uv"})


def _gzkit_imported_names(tree: ast.Module) -> frozenset[str]:
    """Collect the local names bound to gzkit production imports in a module."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("gzkit"):
            names.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            names.update(
                (alias.asname or alias.name).split(".")[0]
                for alias in node.names
                if alias.name.startswith("gzkit")
            )
    return frozenset(names)


def _attr_root_name(node: ast.expr) -> str | None:
    """Return the root ``Name`` id of an attribute chain (``a.b.c`` -> ``a``)."""
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _calls_production_code(
    node: ast.FunctionDef | ast.AsyncFunctionDef, gzkit_names: frozenset[str]
) -> bool:
    """Return True if the function exercises project computation.

    A test that calls a gzkit production symbol or invokes the CLI (CliRunner
    ``.invoke`` / ``subprocess`` on ``gz``/``uv``) runs project code: its
    assertion can fail when behavior changes, so it is a behavioral/contract
    test, not a tautological content echo. A unit test exists to verify the
    project's computation; one that exercises none is the superfluous case this
    audit targets. This discriminator stops the scan from flagging the ~88% of
    filesystem-touching tests that are in fact behavioral.
    """
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if isinstance(func, ast.Name) and func.id in gzkit_names:
            return True
        if isinstance(func, ast.Attribute):
            if func.attr == _CLI_INVOKE_ATTR:
                return True
            if _attr_root_name(func) in gzkit_names:
                return True
            if func.attr in _SUBPROCESS_LAUNCH_ATTRS and any(
                isinstance(arg, ast.List)
                and any(
                    isinstance(el, ast.Constant) and el.value in _CLI_ENTRY_TOKENS
                    for el in arg.elts
                )
                for arg in child.args
            ):
                return True
    return False


def _class_setup_map(
    tree: ast.Module,
) -> dict[int, ast.FunctionDef | ast.AsyncFunctionDef]:
    """Map each class-method node id to its class's setUp/setUpClass node.

    A test whose production-code call lives in the class fixture (not the method
    body) is still behavioral, so the exemption must see the setUp too.
    """
    out: dict[int, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for cls in ast.walk(tree):
        if not isinstance(cls, ast.ClassDef):
            continue
        setup = next(
            (
                b
                for b in cls.body
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef))
                and b.name in ("setUp", "setUpClass")
            ),
            None,
        )
        if setup is None:
            continue
        for b in cls.body:
            if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out[id(b)] = setup
    return out


def scan_test_tree(tests_path: Path) -> list[TautologicalTestOperation]:
    """Scan all .py files under tests_path for tautological test operations.

    A tautological test operation is a co-occurrence of a filesystem-shaped
    operation and an assertion statement within the same function body.

    The waivers file path (_WAIVERS_SELF_EXCLUSION) is unconditionally excluded.
    """
    results: list[TautologicalTestOperation] = []
    if not tests_path.exists():
        return results

    for py_file in sorted(tests_path.rglob("*.py")):
        # Derive posix relative path (relative to tests_path's parent = project root)
        try:
            rel = py_file.relative_to(tests_path.parent).as_posix()
        except ValueError:
            rel = py_file.as_posix()

        # Self-exemption: skip the waivers file (it's JSON, but guard is symbolic)
        if rel == _WAIVERS_SELF_EXCLUSION:
            continue

        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, OSError):
            continue

        gzkit_names = _gzkit_imported_names(tree)
        setup_map = _class_setup_map(tree)

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            has_fs, op_kind, op_line = _has_filesystem_op(node)
            if not has_fs:
                continue
            has_assert, assert_kind = _has_assertion(node)
            if not has_assert:
                continue
            # A test that exercises project computation (calls gzkit code or the
            # CLI) is behavioral/contract, not a tautological echo — exempt it.
            setup = setup_map.get(id(node))
            if _calls_production_code(node, gzkit_names) or (
                setup is not None and _calls_production_code(setup, gzkit_names)
            ):
                continue
            context = _extract_context_hint(node)
            results.append(
                TautologicalTestOperation(
                    file_path=rel,
                    line_number=op_line,
                    operation_kind=op_kind,
                    function_name=node.name,
                    assertion_kind=assert_kind,
                    context_hint=context,
                )
            )
    return results


def propose_disposition(op: TautologicalTestOperation) -> ProposedDisposition:
    """Propose exactly one of four dispositions for a tautological test operation.

    Heuristics:
    - setUp/setUpClass/tearDown functions → keep_as_fixture
    - ledger/receipt paths referenced → replace_with_ledger
    - schema/config/manifest paths referenced → fold_to_validator
    - default → convert
    """
    if op.function_name in _FIXTURE_FUNCTION_NAMES:
        return ProposedDisposition.keep_as_fixture

    hint = (op.context_hint or "").lower()
    if any(h in hint for h in _LEDGER_HINTS):
        return ProposedDisposition.replace_with_ledger
    if any(h in hint for h in _SCHEMA_HINTS):
        # Exclude .json that is also a receipt/ledger hint to avoid conflict
        if any(h in hint for h in _LEDGER_HINTS):
            return ProposedDisposition.replace_with_ledger
        return ProposedDisposition.fold_to_validator

    return ProposedDisposition.convert


def load_baseline(data_dir: Path) -> Baseline:
    """Load the baseline from data/tautological_test_baseline.json."""
    baseline_path = data_dir / "tautological_test_baseline.json"
    if not baseline_path.exists():
        return Baseline(operations=[], generated_at="1970-01-01T00:00:00+00:00")
    raw = json.loads(baseline_path.read_text(encoding="utf-8"))
    return Baseline.model_validate(raw)


def load_waivers(data_dir: Path) -> dict[str, list[str]]:
    """Load file-level waivers from data/tautological_test_waivers.json.

    Returns a dict mapping file_path (posix) to list of rationale_key strings.
    Each entry in the list represents one waived operation for that file.
    """
    waivers_path = data_dir / "tautological_test_waivers.json"
    if not waivers_path.exists():
        return {}
    raw = json.loads(waivers_path.read_text(encoding="utf-8"))
    return raw.get("file_waivers", {})


def count_waived(waivers: dict[str, list[str]], file_path: str) -> int:
    """Count waived operations for a given file path."""
    return len(waivers.get(file_path, []))


def _total_waived(waivers: dict[str, list[str]]) -> int:
    return sum(len(v) for v in waivers.values())


def audit_drift(project_root: Path) -> list[ValidationError]:
    """Compare current scan count to baseline + waivers; return errors on excess.

    Exits:
    - 0 → current ≤ baseline + waivers (clean)
    - 3 (via ValidationError type="tautological_test_audit") → drift detected
    """
    tests_path = project_root / "tests"
    data_dir = project_root / "data"

    ops = scan_test_tree(tests_path)
    baseline = load_baseline(data_dir)
    waivers = load_waivers(data_dir)

    current_count = len(ops)
    baseline_count = len(baseline.operations)
    waived_count = _total_waived(waivers)
    allowed = baseline_count + waived_count

    if current_count <= allowed:
        return []

    new_ops = ops[allowed:]
    errors: list[ValidationError] = []
    for op in new_ops:
        disposition = propose_disposition(op)
        errors.append(
            ValidationError(
                type="tautological_test_audit",
                artifact=op.file_path,
                message=(
                    f"Line {op.line_number}: {op.operation_kind!r} in "
                    f"{op.function_name!r} co-occurs with assertion "
                    f"{op.assertion_kind!r}. Suggested disposition: {disposition.value}"
                ),
            )
        )
    return errors
