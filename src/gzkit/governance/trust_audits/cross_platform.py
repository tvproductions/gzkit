r"""Cross-platform UTF-8 trust audit (cross-platform.md rule 9).

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
    r"""Join trailing-backslash shell continuations into logical lines.

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
    * No tracked text surface may be COMMITTED with CRLF — verified against the
      git index (``git ls-files --eol``), never the working tree. A correct
      ``.gitattributes`` already makes committed CRLF impossible; this index
      check is the defense-in-depth that confirms git did the work, without
      policing volatile working-tree bytes that git normalizes away on commit.
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


def _scan_crlf_surfaces(project_root: Path) -> list[ValidationError]:
    """Fail closed on any tracked text surface COMMITTED with CRLF.

    The line-ending contract lives at the git layer: ``.gitattributes``
    (``* text=auto eol=lf``) normalizes every text blob to LF in the index on
    commit. This scan verifies that contract is honored by inspecting the index
    EOL via ``git ls-files --eol`` — not the working-tree bytes, which a Windows
    checkout or a Python ``write_text`` may transiently render as CRLF and which
    git normalizes away on commit. Trusting the index lets ``.gitattributes`` do
    the work instead of the gate re-deriving it at every write site.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), "ls-files", "--eol"],
            capture_output=True,
            check=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        # Outside a git work tree (fixture temp dirs): no index to inspect; the
        # .gitattributes-presence check still gates the contract.
        return []
    errors: list[ValidationError] = []
    for entry in result.stdout.decode("utf-8", "surrogateescape").splitlines():
        meta, tab, rel_posix = entry.partition("\t")
        if not tab:
            continue
        fields = meta.split()
        if not fields or not fields[0].startswith("i/"):
            continue
        if fields[0][2:] not in ("crlf", "mixed"):
            continue
        if Path(rel_posix).suffix.lower() not in _LINE_ENDING_TEXT_SUFFIXES:
            continue
        errors.append(
            ValidationError(
                type="line_endings",
                artifact=rel_posix,
                message=_CRLF_SURFACE_MESSAGE,
            )
        )
    return errors


# ---------------------------------------------------------------------------
# Subprocess text-read decode robustness (cross-platform.md; GHI #582)
# ---------------------------------------------------------------------------

_SUBPROCESS_CAPTURE_FUNCS: frozenset[str] = frozenset({"run", "Popen", "check_output"})

_SUBPROCESS_ERRORS_MESSAGE = (
    "text-mode subprocess capture decodes sub-process output but passes no "
    "`errors=` — non-UTF-8 tool/git output (cp1252/latin-1) raises "
    "UnicodeDecodeError (a ValueError, so `except OSError` misses it) and "
    'aborts the command mid-run. Add `errors="replace"` (mirror '
    "`src/gzkit/quality.py::run_command`). `.claude/rules/cross-platform.md` "
    "§ Subprocess reads."
)


def _subprocess_func_name(node: ast.Call) -> str | None:
    """Return the subprocess capture func name (`run`/`Popen`/`check_output`)."""
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr in _SUBPROCESS_CAPTURE_FUNCS:
        value = func.value
        if isinstance(value, ast.Name) and value.id == "subprocess":
            return func.attr
    return None


def _call_kwargs(node: ast.Call) -> dict[str, ast.expr]:
    return {kw.arg: kw.value for kw in node.keywords if kw.arg}


def _is_truthy_constant(value: ast.expr) -> bool:
    return isinstance(value, ast.Constant) and bool(value.value)


def _decodes_text(kwargs: dict[str, ast.expr]) -> bool:
    """Return True when the call decodes bytes→str (text mode).

    Only text-mode calls decode; passing ``errors=`` to a bytes-mode call would
    silently *enable* text mode (subprocess docs), flipping the return type — so
    bytes-mode calls are never flagged.
    """
    if _is_truthy_constant(kwargs.get("text", ast.Constant(value=False))):
        return True
    if _is_truthy_constant(kwargs.get("universal_newlines", ast.Constant(value=False))):
        return True
    encoding = kwargs.get("encoding")
    return encoding is not None and not (
        isinstance(encoding, ast.Constant) and encoding.value is None
    )


def _captures_output(func_name: str, kwargs: dict[str, ast.expr]) -> bool:
    """Return True when the call captures sub-process stdout/stderr (something to decode)."""
    if func_name == "check_output":
        return True
    if _is_truthy_constant(kwargs.get("capture_output", ast.Constant(value=False))):
        return True
    for stream in ("stdout", "stderr"):
        value = kwargs.get(stream)
        if isinstance(value, ast.Attribute) and value.attr == "PIPE":
            return True
    return False


def audit_subprocess_errors(project_root: Path) -> list[ValidationError]:
    """Flag text-mode subprocess captures under ``src/gzkit`` missing ``errors=``.

    A text-mode capture (``text=True`` / ``encoding=`` / ``universal_newlines=``
    combined with ``check_output``, ``capture_output=True``, or ``stdout=PIPE``)
    decodes sub-process bytes to ``str``. Without ``errors=``, undecodable bytes
    raise ``UnicodeDecodeError`` and abort the command — the whole-family
    cross-platform crash GHI #582 remediates. Bytes-mode calls are not flagged:
    adding ``errors=`` there would silently enable text mode.

    This is the recurrence defense for the GHI #582 sweep — invoked by
    ``tests/governance/test_subprocess_errors_replace.py`` against the real tree
    so a re-introduced site fails closed in the ``gz check`` test tier, mirroring
    the ``.as_posix()`` rule's ``test_path_separator_portability.py`` enforcement.
    """
    errors: list[ValidationError] = []
    src_root = project_root / "src" / "gzkit"
    if not src_root.is_dir():
        return errors
    for py_path in sorted(src_root.rglob("*.py")):
        try:
            tree = ast.parse(py_path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func_name = _subprocess_func_name(node)
            if func_name is None:
                continue
            kwargs = _call_kwargs(node)
            if (
                _decodes_text(kwargs)
                and _captures_output(func_name, kwargs)
                and "errors" not in kwargs
            ):
                rel = py_path.relative_to(project_root).as_posix()
                errors.append(
                    ValidationError(
                        type="subprocess_errors",
                        artifact=f"{rel}:{node.lineno}",
                        message=_SUBPROCESS_ERRORS_MESSAGE,
                    )
                )
    return errors
