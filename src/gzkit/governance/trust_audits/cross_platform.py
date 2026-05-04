"""Cross-platform UTF-8 trust audit (cross-platform.md rule 9).

The CLI entrypoint reconfigures stdio at runtime; the env-var prefix is
redundant. The runtime guard does NOT cover fresh-interpreter helpers,
so doc/skill/feature surfaces must either reconfigure their own stdio or
use the file-handoff pattern for non-Python tools (jq/awk/sed). GHI #275
extends the original GHI #206 check to those classes.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from gzkit.validate import ValidationError

_CLOSED_OBPI_WAIVER_RATIONALE = (
    "Closed-OBPI verification block — rewriting attested evidence is itself "
    "doctrine drift. New doc additions must reconfigure."
)
_UTF8_PIPE_WAIVERS: dict[str, str] = {
    (
        "docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical"
        "/obpis/OBPI-0.0.17-02-plan-create-kind.md:165"
    ): _CLOSED_OBPI_WAIVER_RATIONALE,
    (
        "docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine"
        "/obpis/OBPI-0.0.18-02-runbook-prd-to-adr.md:135"
    ): _CLOSED_OBPI_WAIVER_RATIONALE,
    (
        "docs/design/adr/foundation/ADR-0.0.8-feature-toggle-system"
        "/obpis/OBPI-0.0.8-05-cli-surface.md:107"
    ): _CLOSED_OBPI_WAIVER_RATIONALE,
    (
        "docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution"
        "/obpis/OBPI-0.18.0-05-pipeline-runtime-integration.md:141"
    ): _CLOSED_OBPI_WAIVER_RATIONALE,
    (
        "docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption"
        "/obpis/OBPI-0.25.0-32-handoff-validation-pattern.md:244"
    ): _CLOSED_OBPI_WAIVER_RATIONALE,
    "docs/governance/pipeline-marker-migration-path.md:178": (
        "Migration-path doc describing historical marker semantics; target "
        "audience is governance maintainers on POSIX shells."
    ),
    (
        "docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant"
        "/audit/proofs/validate-help.txt:53"
    ): (
        "Audit-proof captures the --utf8-prefix validator's own help text, "
        "which describes the anti-pattern it forbids. GHI #299."
    ),
    (
        "docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/audit/AUDIT.md:229"
    ): (
        "ADR-0.0.26 audit document describes the anti-pattern in the context of "
        "a remediated Gate 2 shortfall (R2) — meta-documentation, not actual usage."
    ),
    (
        "docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/audit/AUDIT.md:323"
    ): (
        "ADR-0.0.26 audit document explains why the anti-pattern appeared in audit "
        "proof text — meta-documentation of the rule, not actual usage."
    ),
}

_PYTHONUTF8_PREFIX = re.compile(r"PYTHONUTF8=1\s+uv\s+run\s+(?:gz|-m\s+gzkit)")
# GHI #275: extend utf8_prefix to fresh-interpreter helpers and non-Python tools.
# A gz pipeline into python -c / python <script> is a fresh interpreter that
# defaults to cp1252 on Windows legacy consoles. Require explicit reconfigure.
_GZ_PIPE_PYTHON = re.compile(r"(?:uv\s+run\s+)?gz\s+[^\n|`]*\|\s*(?:uv\s+run\s+)?python\b")
# A gz pipeline into jq / awk / sed is the file-handoff class: no runtime-level
# recourse exists (they're non-Python tools), the rule prescribes `--output`
# handoff instead.
_GZ_PIPE_NON_PYTHON = re.compile(r"(?:uv\s+run\s+)?gz\s+[^\n|`]*\|\s*(jq|awk|sed)\b")
_STDOUT_RECONFIGURE = re.compile(r"sys\.stdout\.reconfigure\s*\(\s*encoding\s*=\s*['\"]utf-?8['\"]")


def audit_utf8_prefix(project_root: Path) -> list[ValidationError]:
    """Enforce ``cross-platform.md`` rule 9 + scope-boundary subsection.

    The original check (GHI #206) flagged the ``PYTHONUTF8=1 uv run gz`` env
    prefix. GHI #275 extends coverage to the full rule text:

    * ``gz ... | python[-c] ...`` pipelines that skip ``sys.stdout.reconfigure``
    * ``gz ... | jq|awk|sed`` pipelines (non-Python tools — file handoff only)
    * ``tools/**/*.py`` entry points that ``print`` without reconfigure

    The CLI entrypoint configures UTF-8 at runtime; the env-var prefix is
    redundant, but the runtime guard does not cover fresh-interpreter
    helpers — those must reconfigure their own stdio.
    """
    errors: list[ValidationError] = []
    errors.extend(_scan_doc_pipe_patterns(project_root))
    errors.extend(_scan_tools_scripts(project_root))
    return errors


_DOC_PIPE_SCAN_ROOTS = ("docs", ".gzkit/skills", ".claude/skills", "features")
_DOC_PIPE_SUFFIXES: frozenset[str] = frozenset({".md", ".feature", ".txt"})

_PYTHONUTF8_MESSAGE = (
    "`PYTHONUTF8=1` prefix on `uv run gz` is forbidden — "
    "the CLI entrypoint configures UTF-8 at runtime "
    "(CLAUDE.md local rule 9)."
)
_GZ_PIPE_PYTHON_MESSAGE = (
    "`gz ... | python ...` is a fresh-interpreter pipe "
    "(no runtime UTF-8 guard). Add "
    "`sys.stdout.reconfigure(encoding='utf-8')` inside "
    "the helper, or waive in `_UTF8_PIPE_WAIVERS` "
    "(`.gzkit/rules/cross-platform.md`)."
)
_GZ_PIPE_NON_PYTHON_MESSAGE = (
    "`gz ... | jq|awk|sed` pipes gz UTF-8 output through a "
    "non-Python tool that crashes on cp1252. Use the "
    "`--output path.json` handoff pattern "
    "(`.gzkit/rules/cross-platform.md` § Windows-safe "
    "helper patterns)."
)


def _doc_pipe_message(line: str) -> str | None:
    """Return the violation message for a single doc line, or ``None`` if clean."""
    if _PYTHONUTF8_PREFIX.search(line):
        return _PYTHONUTF8_MESSAGE
    if _GZ_PIPE_PYTHON.search(line) and not _STDOUT_RECONFIGURE.search(line):
        return _GZ_PIPE_PYTHON_MESSAGE
    if _GZ_PIPE_NON_PYTHON.search(line):
        return _GZ_PIPE_NON_PYTHON_MESSAGE
    return None


def _iter_doc_pipe_paths(project_root: Path) -> list[Path]:
    """Enumerate scannable doc/skill/feature files (excluding the prose carve-out)."""
    paths: list[Path] = []
    for rel in _DOC_PIPE_SCAN_ROOTS:
        candidate = project_root / rel
        if not candidate.is_dir():
            continue
        for path in sorted(candidate.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in _DOC_PIPE_SUFFIXES:
                continue
            # advisory-rules-audit.md documents the anti-pattern by name;
            # skip lines that cite it as prose rather than prescribe it.
            if path.name == "advisory-rules-audit.md":
                continue
            paths.append(path)
    return paths


def _scan_one_doc_pipe_file(path: Path, project_root: Path) -> list[ValidationError]:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    rel_path = path.relative_to(project_root).as_posix()
    errors: list[ValidationError] = []
    for lineno, line in enumerate(content.splitlines(), 1):
        artifact = f"{rel_path}:{lineno}"
        if artifact in _UTF8_PIPE_WAIVERS:
            continue
        message = _doc_pipe_message(line)
        if message is None:
            continue
        errors.append(ValidationError(type="utf8_prefix", artifact=artifact, message=message))
    return errors


def _scan_doc_pipe_patterns(project_root: Path) -> list[ValidationError]:
    """Scan docs/skills/features for gz-pipe anti-patterns."""
    errors: list[ValidationError] = []
    for path in _iter_doc_pipe_paths(project_root):
        errors.extend(_scan_one_doc_pipe_file(path, project_root))
    return errors


def _scan_tools_scripts(project_root: Path) -> list[ValidationError]:
    """Scan ``tools/**/*.py`` entry points for missing UTF-8 reconfigure."""
    tools_root = project_root / "tools"
    if not tools_root.is_dir():
        return []
    errors: list[ValidationError] = []
    for path in sorted(tools_root.rglob("*.py")):
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        if not _is_entry_point_script(tree):
            continue
        if _STDOUT_RECONFIGURE.search(source):
            continue
        errors.append(
            ValidationError(
                type="utf8_prefix",
                artifact=path.relative_to(project_root).as_posix(),
                message=(
                    "`tools/` entry-point script prints without "
                    "`sys.stdout.reconfigure(encoding='utf-8')`. Fresh "
                    "interpreters default to cp1252 on Windows legacy consoles "
                    "(`.gzkit/rules/cross-platform.md` § Scope boundary of "
                    "the runtime guard)."
                ),
            )
        )
    return errors


def _is_main_guard(node: ast.AST) -> bool:
    """Return True for ``if __name__ == ...:`` nodes."""
    if not isinstance(node, ast.If):
        return False
    test = node.test
    return (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and test.left.id == "__name__"
    )


def _is_print_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print"
    )


def _is_entry_point_script(tree: ast.Module) -> bool:
    """Return ``True`` if the module has ``if __name__ == '__main__':`` and calls ``print``."""
    has_main_guard = False
    has_print = False
    for node in ast.walk(tree):
        if _is_main_guard(node):
            has_main_guard = True
        if _is_print_call(node):
            has_print = True
    return has_main_guard and has_print
