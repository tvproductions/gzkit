"""Cross-platform UTF-8 trust audit (cross-platform.md rule 9).

The CLI entrypoint reconfigures stdio at runtime; the env-var prefix is
redundant. The runtime guard does NOT cover fresh-interpreter helpers,
so doc/skill/feature surfaces must either reconfigure their own stdio or
use the file-handoff pattern for non-Python tools (jq/awk/sed). GHI #275
extends the original GHI #206 check to those classes. GHI #486 extends
the doc scan to ``\\``-continued shell pipelines, which the line-scoped
regexes would otherwise silently miss.
"""

from __future__ import annotations

import ast
import re
import subprocess
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
        "/obpis/OBPI-0.25.0-32-handoff-validation-pattern.md:245"
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
    (
        "docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate"
        "/obpis/OBPI-0.0.34-04-authoring-cli.md:255"
    ): (
        "Key-proof verification command showing how to inspect coverage output — "
        "the pipe is a usage example in an OBPI brief, not production code that runs "
        "in gzkit's runtime. The evidence block illustrates the operator action; "
        "no reconfigure() guard is needed at the documentation layer."
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


def _coalesce_continuations(content: str) -> list[tuple[int, str]]:
    """Join trailing-backslash shell continuations into logical lines.

    A ``gz ... | tool`` pipeline may be split across physical lines with a
    trailing ``\\``. The pipe regexes are line-scoped, so a continuation
    silently evades the scan (GHI #486). Each logical line is reported at
    the physical line where it begins, so waivers keyed to a start line and
    the standalone single-line case both keep their original line numbers.
    """
    physical = content.splitlines()
    logical: list[tuple[int, str]] = []
    index = 0
    while index < len(physical):
        start = index + 1
        buffer = physical[index]
        while buffer.rstrip().endswith("\\") and index + 1 < len(physical):
            buffer = f"{buffer.rstrip()[:-1]} {physical[index + 1]}"
            index += 1
        logical.append((start, buffer))
        index += 1
    return logical


def _scan_one_doc_pipe_file(path: Path, project_root: Path) -> list[ValidationError]:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    rel_path = path.relative_to(project_root).as_posix()
    errors: list[ValidationError] = []
    for lineno, line in _coalesce_continuations(content):
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


# GHI #570: mechanize the CRLF/LF cross-platform hazard that recurred as one-off
# fixes (GHIs #478, #161, #384) for want of a gate. The git layer (.gitattributes)
# normalizes line endings to LF regardless of a clone's local core.autocrlf; the
# outcome scan fails closed on any committed text surface that still carries CRLF.
_GITATTRIBUTES_LF_DIRECTIVE = re.compile(r"^\s*\*\s+text=auto\s+eol=lf\b", re.MULTILINE)
_LINE_ENDING_TEXT_SUFFIXES: frozenset[str] = frozenset(
    {
        ".py",
        ".md",
        ".json",
        ".jsonl",
        ".toml",
        ".yaml",
        ".yml",
        ".txt",
        ".cfg",
        ".ini",
        ".feature",
    }
)
_LINE_ENDING_SCAN_ROOTS = (
    "src",
    "tests",
    ".gzkit",
    ".claude",
    ".agents",
    ".github",
    "docs",
    "features",
)
_LINE_ENDING_SKIP_DIRS: frozenset[str] = frozenset(
    {".git", ".venv", "__pycache__", "node_modules", ".mypy_cache", ".ruff_cache"}
)
_GITATTRIBUTES_MISSING_MESSAGE = (
    "Missing `.gitattributes` — add `* text=auto eol=lf` so git normalizes line "
    "endings to LF on every platform regardless of a clone's local `core.autocrlf` "
    "(`.gzkit/rules/cross-platform.md`; ADR-0.0.1)."
)
_GITATTRIBUTES_WEAK_MESSAGE = (
    "`.gitattributes` lacks the `* text=auto eol=lf` LF-normalization directive "
    "(`.gzkit/rules/cross-platform.md`; ADR-0.0.1)."
)
_CRLF_SURFACE_MESSAGE = (
    "CRLF line endings in a text surface — normalize to LF. A `write_text`/`open` "
    'write without `newline="\\n"` emits CRLF on Windows '
    "(`.gzkit/rules/cross-platform.md`; ADR-0.0.1)."
)


def audit_line_endings(project_root: Path) -> list[ValidationError]:
    """Enforce cross-platform LF line endings (``cross-platform.md``; GHI #570).

    Two failure surfaces mechanize the CRLF/LF hazard:

    * ``.gitattributes`` MUST exist and carry ``* text=auto eol=lf`` so git
      normalizes line endings to LF on every platform regardless of a clone's
      local ``core.autocrlf``.
    * No tracked text surface may contain a CRLF byte sequence — the outcome a
      stray ``write_text``/``open`` without ``newline=`` produces on Windows,
      which then surfaces as whole-file byte drift in parity comparisons.
    """
    errors: list[ValidationError] = []
    errors.extend(_check_gitattributes_lf(project_root))
    errors.extend(_scan_crlf_surfaces(project_root))
    return errors


def _check_gitattributes_lf(project_root: Path) -> list[ValidationError]:
    """Fail closed when ``.gitattributes`` is missing or omits the LF directive."""
    path = project_root / ".gitattributes"
    if not path.is_file():
        return [
            ValidationError(
                type="line_endings",
                artifact=".gitattributes",
                message=_GITATTRIBUTES_MISSING_MESSAGE,
            )
        ]
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = ""
    if not _GITATTRIBUTES_LF_DIRECTIVE.search(content):
        return [
            ValidationError(
                type="line_endings",
                artifact=".gitattributes",
                message=_GITATTRIBUTES_WEAK_MESSAGE,
            )
        ]
    return []


def _git_tracked_relposix(project_root: Path) -> frozenset[str] | None:
    """Return git-tracked paths as project-relative posix strings.

    Returns ``None`` outside a git work tree (e.g. fixture temp dirs), where the
    caller falls back to scanning every text file. Inside a repo, untracked and
    gitignored files — runtime state such as ``.instruction-state.json`` — are
    exempt, matching the ``runtime_state`` class doctrine (skill-surface-sync.md).
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), "ls-files", "-z"],
            capture_output=True,
            check=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    rels = result.stdout.decode("utf-8", "surrogateescape").split("\0")
    return frozenset(rel for rel in rels if rel)


def _scan_crlf_surfaces(project_root: Path) -> list[ValidationError]:
    """Fail closed on any tracked text surface that still carries a CRLF byte."""
    tracked = _git_tracked_relposix(project_root)
    errors: list[ValidationError] = []
    for rel in _LINE_ENDING_SCAN_ROOTS:
        root = project_root / rel
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in _LINE_ENDING_TEXT_SUFFIXES:
                continue
            if _LINE_ENDING_SKIP_DIRS.intersection(path.parts):
                continue
            rel_posix = path.relative_to(project_root).as_posix()
            if tracked is not None and rel_posix not in tracked:
                continue
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if b"\r\n" in data:
                errors.append(
                    ValidationError(
                        type="line_endings",
                        artifact=rel_posix,
                        message=_CRLF_SURFACE_MESSAGE,
                    )
                )
    return errors
