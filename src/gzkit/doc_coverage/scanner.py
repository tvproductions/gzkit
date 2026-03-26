"""AST-driven CLI documentation coverage scanner."""

import ast
import importlib
from pathlib import Path
from typing import NamedTuple

from gzkit.commands.common import COMMAND_DOCS, get_project_root
from gzkit.doc_coverage.models import CommandCoverage, CoverageReport, OrphanedDoc, SurfaceResult

_SURFACE_NAMES = (
    "manpage",
    "index_entry",
    "operator_runbook",
    "governance_runbook",
    "docstring",
    "command_docs_mapping",
)


class DiscoveredCommand(NamedTuple):
    """A CLI command discovered by AST scanning of _build_parser."""

    name: str
    handler_name: str | None
    line: int


def _extract_string_arg(call: ast.Call, index: int = 0) -> str | None:
    """Return the string value of a positional argument at *index* in *call*."""
    if len(call.args) <= index:
        return None
    arg = call.args[index]
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return arg.value
    return None


def _extract_handler_name(set_defaults_call: ast.Call) -> str | None:
    """Extract function name from set_defaults(func=lambda a: HANDLER(...))."""
    for kw in set_defaults_call.keywords:
        if kw.arg != "func":
            continue
        if not isinstance(kw.value, ast.Lambda):
            continue
        body = kw.value.body
        if not isinstance(body, ast.Call):
            continue
        func = body.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
    return None


def _find_build_parser_body(tree: ast.Module) -> list[ast.stmt] | None:
    """Return the statement list of _build_parser() from a parsed AST module."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_build_parser":
            return node.body
    return None


def _find_root_parser_name(body: list[ast.stmt]) -> str | None:
    """Identify the root StableArgumentParser variable name in _build_parser."""
    for stmt in body:
        if not isinstance(stmt, ast.Assign):
            continue
        if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
            continue
        rhs = stmt.value
        if not isinstance(rhs, ast.Call):
            continue
        func = rhs.func
        is_stable = (isinstance(func, ast.Name) and func.id == "StableArgumentParser") or (
            isinstance(func, ast.Attribute) and func.attr == "StableArgumentParser"
        )
        if is_stable:
            return stmt.targets[0].id
    return None


class _ParserState:
    """Mutable accumulator for the two-pass AST discovery algorithm."""

    def __init__(self, root_parser_name: str | None) -> None:
        self.root_parser_name = root_parser_name
        self.parser_vars: dict[str, str] = {}
        self.subparser_vars: dict[str, str] = {}
        self.group_vars: set[str] = set()
        self.leaf_commands: list[DiscoveredCommand] = []

    def get_prefix(self, var_name: str) -> str | None:
        """Return the command prefix for a subparser group variable."""
        return self.subparser_vars.get(var_name)


def _handle_assignment(stmt: ast.Assign, state: _ParserState) -> None:
    """Process an assignment statement for add_subparsers or add_parser calls."""
    if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
        return
    if not isinstance(stmt.value, ast.Call) or not isinstance(stmt.value.func, ast.Attribute):
        return

    target_name = stmt.targets[0].id
    call = stmt.value
    attr = call.func.attr  # type: ignore[union-attr]
    obj = call.func.value  # type: ignore[union-attr]
    if not isinstance(obj, ast.Name):
        return
    obj_name = obj.id

    if attr == "add_subparsers":
        if obj_name == state.root_parser_name:
            state.subparser_vars[target_name] = ""
            state.group_vars.add(obj_name)
        elif obj_name in state.parser_vars:
            state.subparser_vars[target_name] = state.parser_vars[obj_name]
            state.group_vars.add(obj_name)
    elif attr == "add_parser":
        cmd_name = _extract_string_arg(call, 0)
        if cmd_name is None:
            return
        prefix = state.get_prefix(obj_name)
        if prefix is None:
            return
        state.parser_vars[target_name] = f"{prefix} {cmd_name}".strip()


def _handle_set_defaults(stmt: ast.Expr, state: _ParserState) -> None:
    """Process a standalone p_foo.set_defaults(func=...) expression."""
    call = stmt.value
    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
        return
    if call.func.attr != "set_defaults" or not isinstance(call.func.value, ast.Name):
        return
    obj_name = call.func.value.id
    if obj_name in state.parser_vars and obj_name not in state.group_vars:
        handler = _extract_handler_name(call)
        state.leaf_commands.append(
            DiscoveredCommand(state.parser_vars[obj_name], handler, stmt.lineno)
        )


def _handle_chained_add_parser(stmt: ast.Expr, state: _ParserState) -> None:
    """Process an inline bar.add_parser(...).set_defaults(func=...) chain."""
    call = stmt.value
    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
        return
    if call.func.attr != "set_defaults":
        return
    inner = call.func.value
    if not isinstance(inner, ast.Call) or not isinstance(inner.func, ast.Attribute):
        return
    if inner.func.attr != "add_parser" or not isinstance(inner.func.value, ast.Name):
        return
    obj_name = inner.func.value.id
    cmd_name = _extract_string_arg(inner, 0)
    if cmd_name is None:
        return
    prefix = state.get_prefix(obj_name)
    if prefix is None:
        return
    full_path = f"{prefix} {cmd_name}".strip()
    handler = _extract_handler_name(call)
    state.leaf_commands.append(DiscoveredCommand(full_path, handler, stmt.lineno))


def discover_commands(source: str) -> list[DiscoveredCommand]:
    """Discover all CLI leaf commands by AST-scanning _build_parser() source.

    Parses the argparse tree from cli/main.py without importing the module.
    Returns a list of DiscoveredCommand named tuples, one per leaf subcommand.
    """
    tree = ast.parse(source)
    body = _find_build_parser_body(tree)
    if body is None:
        return []

    state = _ParserState(_find_root_parser_name(body))

    for stmt in body:
        if isinstance(stmt, ast.Assign):
            _handle_assignment(stmt, state)
        elif isinstance(stmt, ast.Expr):
            # Try standalone set_defaults first (more specific match)
            if (
                isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Attribute)
                and stmt.value.func.attr == "set_defaults"
                and isinstance(stmt.value.func.value, ast.Name)
            ):
                _handle_set_defaults(stmt, state)
            else:
                _handle_chained_add_parser(stmt, state)

    return state.leaf_commands


def _build_import_map(source: str) -> dict[str, str]:
    """Parse top-level from-imports and return function_name -> module_path mapping."""
    tree = ast.parse(source)
    import_map: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                func_name = alias.asname if alias.asname else alias.name
                import_map[func_name] = node.module
    return import_map


def _resolve_handler_docstring(handler_name: str, main_source: str) -> str | None:
    """Resolve the docstring for a handler function by importing its module.

    Parses the import statements from main_source to locate the module, then
    imports it and retrieves the function's __doc__.
    """
    import_map = _build_import_map(main_source)
    module_path = import_map.get(handler_name)
    if module_path is None:
        return None
    try:
        mod = importlib.import_module(module_path)
        fn = getattr(mod, handler_name, None)
        if fn is None:
            return None
        return fn.__doc__
    except (ImportError, AttributeError):
        return None


def _check_runbook(path: Path, command_name: str) -> tuple[bool, str]:
    """Return (passed, detail) for a runbook reference to *command_name*."""
    if not path.exists():
        return False, f"Runbook not found: {path}"
    content = path.read_text(encoding="utf-8")
    search_str = f"gz {command_name}"
    if search_str in content:
        return True, f"Found '{search_str}' in {path.name}"
    return False, f"'{search_str}' not found in {path.name}"


def check_surfaces(
    project_root: Path,
    commands: list[DiscoveredCommand],
    main_source: str,
) -> list[CommandCoverage]:
    """Check all six documentation surfaces for each discovered command.

    Returns a list of CommandCoverage objects, one per command.
    """
    commands_dir = project_root / "docs" / "user" / "commands"
    index_path = commands_dir / "index.md"
    operator_runbook = project_root / "docs" / "user" / "runbook.md"
    governance_runbook = project_root / "docs" / "governance" / "governance_runbook.md"

    index_content = index_path.read_text(encoding="utf-8") if index_path.exists() else ""

    results: list[CommandCoverage] = []
    for cmd in commands:
        slug = cmd.name.replace(" ", "-")
        surfaces: list[SurfaceResult] = []

        # 1. Manpage
        manpage_path = commands_dir / f"{slug}.md"
        if manpage_path.exists():
            surfaces.append(
                SurfaceResult(surface="manpage", passed=True, detail=f"Found {manpage_path.name}")
            )
        else:
            surfaces.append(
                SurfaceResult(
                    surface="manpage", passed=False, detail=f"Missing {manpage_path.name}"
                )
            )

        # 2. Index entry
        if f"{slug}.md" in index_content:
            surfaces.append(
                SurfaceResult(
                    surface="index_entry", passed=True, detail=f"'{slug}.md' found in index"
                )
            )
        else:
            surfaces.append(
                SurfaceResult(
                    surface="index_entry", passed=False, detail=f"'{slug}.md' not in index"
                )
            )

        # 3. Operator runbook
        op_passed, op_detail = _check_runbook(operator_runbook, cmd.name)
        surfaces.append(
            SurfaceResult(surface="operator_runbook", passed=op_passed, detail=op_detail)
        )

        # 4. Governance runbook
        gov_passed, gov_detail = _check_runbook(governance_runbook, cmd.name)
        surfaces.append(
            SurfaceResult(surface="governance_runbook", passed=gov_passed, detail=gov_detail)
        )

        # 5. Docstring
        if cmd.handler_name:
            doc = _resolve_handler_docstring(cmd.handler_name, main_source)
            if doc and doc.strip():
                surfaces.append(
                    SurfaceResult(
                        surface="docstring",
                        passed=True,
                        detail=f"{cmd.handler_name}() has docstring",
                    )
                )
            else:
                surfaces.append(
                    SurfaceResult(
                        surface="docstring",
                        passed=False,
                        detail=f"{cmd.handler_name}() has no docstring",
                    )
                )
        else:
            surfaces.append(
                SurfaceResult(surface="docstring", passed=False, detail="No handler name resolved")
            )

        # 6. COMMAND_DOCS mapping
        if cmd.name in COMMAND_DOCS:
            surfaces.append(
                SurfaceResult(
                    surface="command_docs_mapping",
                    passed=True,
                    detail=f"'{cmd.name}' in COMMAND_DOCS",
                )
            )
        else:
            surfaces.append(
                SurfaceResult(
                    surface="command_docs_mapping",
                    passed=False,
                    detail=f"'{cmd.name}' not in COMMAND_DOCS",
                )
            )

        results.append(
            CommandCoverage(
                command=cmd.name,
                surfaces=surfaces,
                all_passed=all(s.passed for s in surfaces),
            )
        )

    return results


def find_orphaned_docs(
    project_root: Path,
    discovered_names: set[str],
) -> list[OrphanedDoc]:
    """Find documentation referencing commands that no longer exist.

    Checks COMMAND_DOCS keys and manpage files in docs/user/commands/.
    """
    orphans: list[OrphanedDoc] = []

    # Check COMMAND_DOCS keys not in discovered commands
    for key in COMMAND_DOCS:
        if key not in discovered_names:
            orphans.append(
                OrphanedDoc(
                    surface="command_docs_mapping",
                    reference=key,
                    detail=f"COMMAND_DOCS key '{key}' has no matching discovered command",
                )
            )

    # Check manpage files whose slug doesn't map to a discovered command
    commands_dir = project_root / "docs" / "user" / "commands"
    if commands_dir.exists():
        for md_file in sorted(commands_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue
            slug = md_file.stem  # filename without .md
            cmd_name = slug.replace("-", " ")
            if cmd_name not in discovered_names:
                orphans.append(
                    OrphanedDoc(
                        surface="manpage",
                        reference=str(md_file.relative_to(project_root)),
                        detail=f"Manpage '{md_file.name}' has no matching command '{cmd_name}'",
                    )
                )

    return orphans


def scan_cli_commands(project_root: Path | None = None) -> list[DiscoveredCommand]:
    """Discover all CLI commands by AST-scanning cli/main.py.

    Returns a list of DiscoveredCommand named tuples, one per leaf subcommand.
    """
    if project_root is None:
        project_root = get_project_root()
    main_path = project_root / "src" / "gzkit" / "cli" / "main.py"
    source = main_path.read_text(encoding="utf-8")
    return discover_commands(source)


def check_surfaces_report(project_root: Path | None = None) -> CoverageReport:
    """Run a full documentation coverage scan and return a CoverageReport.

    Discovers commands via AST, checks all six surfaces per command, and
    identifies any orphaned documentation referencing removed commands.
    """
    if project_root is None:
        project_root = get_project_root()
    main_path = project_root / "src" / "gzkit" / "cli" / "main.py"
    source = main_path.read_text(encoding="utf-8")
    commands = discover_commands(source)
    coverage_list = check_surfaces(project_root, commands, source)
    discovered_names = {c.name for c in commands}
    orphaned = find_orphaned_docs(project_root, discovered_names)

    fully_covered = sum(1 for c in coverage_list if c.all_passed)
    with_gaps = len(coverage_list) - fully_covered

    return CoverageReport(
        commands_discovered=len(commands),
        commands_fully_covered=fully_covered,
        commands_with_gaps=with_gaps,
        coverage=coverage_list,
        orphaned=orphaned,
        passed=with_gaps == 0 and len(orphaned) == 0,
    )
