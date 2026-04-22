"""Trust-boundary audits promoted from ``tests/governance/`` to first-class ``gz validate`` scopes.

Each audit here enforces one of the three invariants from
``docs/governance/trust-doctrine.md``:

* **T1 — Every produced value has a read-path assertion** (covered by regression
  tests elsewhere, not this module)
* **T2 — Every consumed value has a write-path audit** — ``audit_validator_fields``
* **T3 — Canonical claims bind canonical provenance** — covered by ``gz arb validate``

Plus two supporting audits that catch the same trust-chain poisoning shape at
adjacent layers:

* ``audit_event_handlers`` — every ledger event emitted must be claimed by a
  graph handler or explicitly waived
* ``audit_type_ignores`` — every ``# type: ignore[...]`` under ``src/`` must use
  ty-honored syntax
* ``audit_cli_alignment`` — every ``gz <verb>`` string in features and operator
  docs must resolve through the CLI parser

Each audit returns a list of ``ValidationError`` objects so it composes with
``gz validate`` alongside manifest/ledger/document validation.
"""

from __future__ import annotations

import ast
import json
import re
import tokenize
from pathlib import Path

from gzkit.validate import ValidationError

# ---------------------------------------------------------------------------
# Shared waivers (must stay in sync with tests/governance/ counterparts)
# ---------------------------------------------------------------------------


_NO_GRAPH_IMPACT: dict[str, str] = {
    "project_init": "Bootstrap sentinel; no artifact nodes emit from it.",
    "artifact_edited": "Session activity log; consumed by anchor analysis, not graph.",
    "obpi_lock_claimed": "L3 ephemeral lock file; consumed by gz obpi lock, not graph.",
    "obpi_lock_released": "L3 ephemeral lock file; consumed by gz obpi lock, not graph.",
    "patch-release": (
        "Release-line metadata (hyphenated per patch_release_event at "
        "src/gzkit/ledger_events.py:300). Consumed by gz patch release, "
        "not artifact graph."
    ),
    "audit_generated": "Heavy-lane audit trail; consumed by gz adr audit tooling, not graph.",
    "adr_eval_completed": "Evaluation scorecard; consumed by gz adr evaluate, not graph.",
    "lifecycle_transition": (
        "Transition log for state-doctrine audits; consumed by gz state, not graph directly."
    ),
    "artifact_renamed": (
        "Consumed by _build_rename_map during graph construction, not by a per-event handler."
    ),
    "gate_checked": (
        "Consumed by _build_latest_gate_states during graph construction, "
        "not by a per-event handler."
    ),
}

_VALIDATOR_FIELD_WAIVERS: dict[str, str] = {}

_DOC_PROSE_VERBS: frozenset[str] = frozenset()

# Classes over 300 lines that are explicitly waived from the size limit.
# Each waiver must cite the reason and carry a tracking ticket or rationale
# (trust-doctrine T2 — explicit waivers over silent pass-lists).
_CLASS_SIZE_WAIVERS: dict[str, str] = {
    "src/gzkit/ledger.py::Ledger": (
        "Ledger aggregate root — rewrite tracked separately; splitting by "
        "event-type partition is an ADR-scope refactor."
    ),
    "src/gzkit/hooks/obpi.py::ObpiValidator": (
        "Precondition-chain validator; split by precondition category tracked "
        "as follow-up maintenance."
    ),
}

# ``@dataclass`` sites explicitly waived from the BaseModel discipline.
# Non-governance internal value objects may use stdlib dataclass where no
# serialization/validation is required.
_DATACLASS_WAIVERS: dict[str, str] = {
    "src/gzkit/commands/obpi_precomplete.py::CheckResult": (
        "Internal check-result record consumed only by obpi_precomplete CLI; "
        "no persistence, no cross-surface contract."
    ),
}

# GHI #275: gz-to-helper pipe lines that predate the extended scan.
# Keys are ``<relative-path>:<lineno>``; values carry the rationale.
# New doc additions must either reconfigure (Python) or use --output file
# handoff (non-Python); existing evidence in closed OBPIs is waived rather
# than rewritten because those files live under completed audit artifacts.
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
}

_FORBIDDEN_TYPE_IGNORE = re.compile(r"#\s*type:\s*ignore\[")
_BACKTICKED_INVOCATION = re.compile(r"`gz\s+([a-z][a-z0-9-]*)[^`]*`")
_QUOTED_INVOCATION = re.compile(r'"gz\s+([a-z][a-z0-9-]*)[^"]*"')
_STEP_DEF_FIXTURE = re.compile(r'the gz command\s+"([a-z][a-z0-9-]*)')
_EVENT_TYPE_HEURISTIC = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*")
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
_REQ_ID_IN_BRIEF = re.compile(r"\bREQ-\d+\.\d+\.\d+-\d+-\d+\b")
_SCENARIO_REQ_TAG = re.compile(r"^\s*@(REQ-\d+\.\d+\.\d+-\d+-\d+)\b", re.MULTILINE)
_RULE_HEADING = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_SCORECARD_RULE_ROW = re.compile(
    r"^\|\s*(\d+|meta)\s*\|\s*([^|]+?)\s*\|\s*\*\*([A-Za-z]+)(?:\*\*)?"
)


# ---------------------------------------------------------------------------
# Audit: type-ignore syntax (ty migration)
# ---------------------------------------------------------------------------


def audit_type_ignores(project_root: Path) -> list[ValidationError]:
    """Fail on any ``# type: ignore[<code>]`` under ``src/`` (GHI #197).

    ``ty`` does not honor bracketed mypy-style codes — the markers look valid
    but suppress nothing. Use bare ``# type: ignore`` or ``# ty: ignore[<ty-code>]``.

    Uses ``tokenize`` so only real Python comments match — docstrings and
    string literals that happen to contain the literal pattern are ignored.
    """
    src_root = project_root / "src"
    if not src_root.is_dir():
        return []
    errors: list[ValidationError] = []
    for py_file in src_root.rglob("*.py"):
        try:
            with py_file.open("rb") as fp:
                tokens = list(tokenize.tokenize(fp.readline))
        except (SyntaxError, tokenize.TokenError):
            continue
        for tok in tokens:
            if tok.type != tokenize.COMMENT:
                continue
            if _FORBIDDEN_TYPE_IGNORE.search(tok.string):
                errors.append(
                    ValidationError(
                        type="type_ignores",
                        artifact=f"{py_file.relative_to(project_root)}:{tok.start[0]}",
                        message=(
                            "`# type: ignore[<code>]` is not honored by ty. Use "
                            "bare `# type: ignore` or `# ty: ignore[<ty-code>]`."
                        ),
                    )
                )
    return errors


# ---------------------------------------------------------------------------
# Audit: BDD / operator-doc CLI-verb alignment
# ---------------------------------------------------------------------------


def audit_cli_alignment(project_root: Path) -> list[ValidationError]:
    """Enforce `.gzkit/rules/governance-core.md` § Operator-doc verb resolution (GHI #198)."""
    sources: list[Path] = []
    features_root = project_root / "features"
    if features_root.is_dir():
        sources.extend(sorted(features_root.rglob("*.feature")))
    runbook = project_root / "docs" / "user" / "runbook.md"
    if runbook.is_file():
        sources.append(runbook)
    commands_root = project_root / "docs" / "user" / "commands"
    if commands_root.is_dir():
        sources.extend(sorted(commands_root.rglob("*.md")))
    manpages_root = project_root / "docs" / "user" / "manpages"
    if manpages_root.is_dir():
        sources.extend(sorted(manpages_root.rglob("*.md")))

    verbs_seen: dict[str, list[str]] = {}
    for source in sources:
        for lineno, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            rel = f"{source.relative_to(project_root)}:{lineno}"
            for pattern in (_BACKTICKED_INVOCATION, _QUOTED_INVOCATION, _STEP_DEF_FIXTURE):
                for match in pattern.finditer(line):
                    verbs_seen.setdefault(match.group(1), []).append(rel)

    known_verbs = _known_cli_verbs()
    errors: list[ValidationError] = []
    for verb, locations in sorted(verbs_seen.items()):
        if verb in _DOC_PROSE_VERBS:
            continue
        if verb in known_verbs:
            continue
        errors.append(
            ValidationError(
                type="cli_alignment",
                artifact=locations[0],
                message=(
                    f"`gz {verb}` is not a registered CLI verb; "
                    f"seen at {len(locations)} location(s). Rename the reference "
                    "or register the verb."
                ),
            )
        )
    return errors


def _known_cli_verbs() -> frozenset[str]:
    """Return the top-level subcommand names registered on the gz CLI."""
    import argparse  # noqa: PLC0415

    from gzkit.cli.main import _build_parser  # noqa: PLC0415

    parser = _build_parser()
    verbs: set[str] = set()
    for action in parser._actions:  # noqa: SLF001 — argparse provides no public API
        if isinstance(action, argparse._SubParsersAction):
            verbs.update(action.choices.keys())
    return frozenset(verbs)


# ---------------------------------------------------------------------------
# Audit: ledger event → graph handler coverage
# ---------------------------------------------------------------------------


def audit_event_handlers(project_root: Path) -> list[ValidationError]:
    """Fail on ledger event types that no graph handler claims (GHI #193 class)."""
    ledger_events = project_root / "src" / "gzkit" / "ledger_events.py"
    ledger = project_root / "src" / "gzkit" / "ledger.py"
    if not ledger_events.is_file() or not ledger.is_file():
        return []

    emitted = _collect_emitted_event_types(ledger_events)
    claimed = _collect_claimed_event_types(ledger)

    errors: list[ValidationError] = []
    for unclaimed in sorted(emitted - claimed - _NO_GRAPH_IMPACT.keys()):
        errors.append(
            ValidationError(
                type="event_handlers",
                artifact=f"src/gzkit/ledger_events.py::{unclaimed}",
                message=(
                    f"Ledger event `{unclaimed}` is emitted but no graph handler "
                    "claims it and no waiver exists. Add a handler in "
                    "src/gzkit/ledger.py or add a rationale to "
                    "tests/governance/test_ledger_event_handler_coverage.py::NO_GRAPH_IMPACT."
                ),
            )
        )
    for stale in sorted(_NO_GRAPH_IMPACT.keys() - emitted):
        errors.append(
            ValidationError(
                type="event_handlers",
                artifact=f"NO_GRAPH_IMPACT::{stale}",
                message=(
                    f"Waiver `{stale}` references an event type that no longer "
                    "appears in ledger_events.py. Remove the stale waiver."
                ),
            )
        )
    return errors


def _collect_emitted_event_types(source: Path) -> set[str]:
    tree = ast.parse(source.read_text(encoding="utf-8"))
    emitted: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg != "event":
                continue
            value = keyword.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                emitted.add(value.value)
    return emitted


def _collect_claimed_event_types(source: Path) -> set[str]:
    tree = ast.parse(source.read_text(encoding="utf-8"))
    claimed: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Compare)
            and isinstance(node.left, ast.Attribute)
            and node.left.attr == "event"
            and isinstance(node.left.value, ast.Name)
            and node.left.value.id == "event"
        ):
            for comparator in node.comparators:
                if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                    claimed.add(comparator.value)
        if isinstance(node, (ast.Set, ast.List, ast.Tuple)):
            for elt in node.elts:
                if (
                    isinstance(elt, ast.Constant)
                    and isinstance(elt.value, str)
                    and _EVENT_TYPE_HEURISTIC.fullmatch(elt.value)
                ):
                    claimed.add(elt.value)
    return claimed


# ---------------------------------------------------------------------------
# Audit: validator reads → graph writes coverage
# ---------------------------------------------------------------------------


def audit_validator_fields(project_root: Path) -> list[ValidationError]:
    """Fail on validator ``info.get('<field>')`` reads with no graph writer (GHI #193 class)."""
    validator_src = project_root / "src" / "gzkit" / "commands" / "validate_frontmatter.py"
    ledger_src = project_root / "src" / "gzkit" / "ledger.py"
    if not validator_src.is_file() or not ledger_src.is_file():
        return []

    read_fields = _collect_info_get_fields(validator_src)
    written_fields = _collect_ledger_written_fields(ledger_src)

    errors: list[ValidationError] = []
    for unpopulated in sorted(read_fields - written_fields - _VALIDATOR_FIELD_WAIVERS.keys()):
        errors.append(
            ValidationError(
                type="validator_fields",
                artifact=f"src/gzkit/commands/validate_frontmatter.py::{unpopulated}",
                message=(
                    f"Validator reads graph field `{unpopulated}` but no "
                    "_apply_*_metadata handler or creation-entry initializer "
                    "writes it. Either add population in src/gzkit/ledger.py "
                    "or remove the read. This is GHI #193 class."
                ),
            )
        )
    return errors


def _collect_info_get_fields(source: Path) -> set[str]:
    tree = ast.parse(source.read_text(encoding="utf-8"))
    fields: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "get":
            continue
        caller = func.value
        if not isinstance(caller, ast.Name) or caller.id != "info":
            continue
        if not node.args:
            continue
        key = node.args[0]
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            fields.add(key.value)
    return fields


_GRAPH_WRITE_PATTERN = re.compile(r'graph\[[^\]]+\]\["([^"]+)"\]')
_ENTRY_KEY_PATTERN = re.compile(r'\bentry\["([^"]+)"\]')


def _collect_ledger_written_fields(source: Path) -> set[str]:
    text = source.read_text(encoding="utf-8")
    written: set[str] = set()
    written.update(_GRAPH_WRITE_PATTERN.findall(text))
    written.update(_ENTRY_KEY_PATTERN.findall(text))
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != "_artifact_creation_entry":
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Dict):
                for key in sub.keys:
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        written.add(key.value)
    return written


# ---------------------------------------------------------------------------
# Audit: PYTHONUTF8=1 prefix antipattern on uv run gz (GHI #206 / rule 9)
# ---------------------------------------------------------------------------


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


def _scan_doc_pipe_patterns(project_root: Path) -> list[ValidationError]:
    """Scan docs/skills/features for gz-pipe anti-patterns."""
    roots: list[Path] = []
    for rel in ("docs", ".gzkit/skills", ".claude/skills", "features"):
        candidate = project_root / rel
        if candidate.is_dir():
            roots.append(candidate)
    errors: list[ValidationError] = []
    for root in roots:
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".md", ".feature", ".txt"}:
                continue
            # advisory-rules-audit.md documents the anti-pattern by name;
            # skip lines that cite it as prose rather than prescribe it.
            if path.name == "advisory-rules-audit.md":
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            rel_path = path.relative_to(project_root)
            for lineno, line in enumerate(content.splitlines(), 1):
                artifact = f"{rel_path}:{lineno}"
                if artifact in _UTF8_PIPE_WAIVERS:
                    continue
                if _PYTHONUTF8_PREFIX.search(line):
                    errors.append(
                        ValidationError(
                            type="utf8_prefix",
                            artifact=artifact,
                            message=(
                                "`PYTHONUTF8=1` prefix on `uv run gz` is forbidden — "
                                "the CLI entrypoint configures UTF-8 at runtime "
                                "(CLAUDE.md local rule 9)."
                            ),
                        )
                    )
                    continue
                if _GZ_PIPE_PYTHON.search(line) and not _STDOUT_RECONFIGURE.search(line):
                    errors.append(
                        ValidationError(
                            type="utf8_prefix",
                            artifact=artifact,
                            message=(
                                "`gz ... | python ...` is a fresh-interpreter pipe "
                                "(no runtime UTF-8 guard). Add "
                                "`sys.stdout.reconfigure(encoding='utf-8')` inside "
                                "the helper, or waive in `_UTF8_PIPE_WAIVERS` "
                                "(`.gzkit/rules/cross-platform.md`)."
                            ),
                        )
                    )
                    continue
                if _GZ_PIPE_NON_PYTHON.search(line):
                    errors.append(
                        ValidationError(
                            type="utf8_prefix",
                            artifact=artifact,
                            message=(
                                "`gz ... | jq|awk|sed` pipes gz UTF-8 output through a "
                                "non-Python tool that crashes on cp1252. Use the "
                                "`--output path.json` handoff pattern "
                                "(`.gzkit/rules/cross-platform.md` § Windows-safe "
                                "helper patterns)."
                            ),
                        )
                    )
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
                artifact=str(path.relative_to(project_root)),
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


def _is_entry_point_script(tree: ast.Module) -> bool:
    """True if the module has ``if __name__ == '__main__':`` and calls ``print``."""
    has_main_guard = False
    has_print = False
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            if (
                isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
            ):
                has_main_guard = True
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
        ):
            has_print = True
    return has_main_guard and has_print


# ---------------------------------------------------------------------------
# Audit: no third test tier under unittest (GHI #209 / rule 37)
# ---------------------------------------------------------------------------


def audit_test_tiers(project_root: Path) -> list[ValidationError]:
    """Fail if a third test tier re-appears under ``tests/`` or CLI flags.

    GHI #182 removed ``tests/integration/`` and the ``--integration`` /
    ``--e2e`` / ``--slow`` flags on ``gz test``. The two runners —
    ``unittest`` over ``tests/`` and ``behave`` over ``features/`` — are the
    only test tiers. Any re-introduction is drift.
    """
    errors: list[ValidationError] = []
    forbidden_dirs = ("integration", "e2e", "slow", "bdd")
    tests_root = project_root / "tests"
    if tests_root.is_dir():
        for name in forbidden_dirs:
            path = tests_root / name
            if path.exists():
                errors.append(
                    ValidationError(
                        type="test_tiers",
                        artifact=str(path.relative_to(project_root)),
                        message=(
                            f"Forbidden third test tier `tests/{name}/` — the "
                            "two runners are unittest and behave. See GHI #182."
                        ),
                    )
                )
    # CLI flag recurrence on gz test
    cli_root = project_root / "src" / "gzkit" / "cli"
    if cli_root.is_dir():
        forbidden_flags = ("--integration", "--e2e", "--slow", "--bdd-only")
        for py_file in sorted(cli_root.rglob("parser*.py")):
            try:
                text = py_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for flag in forbidden_flags:
                if flag in text:
                    errors.append(
                        ValidationError(
                            type="test_tiers",
                            artifact=str(py_file.relative_to(project_root)),
                            message=(
                                f"Forbidden test-tier flag `{flag}` registered "
                                "on a parser — third test tier anti-pattern."
                            ),
                        )
                    )
    return errors


# ---------------------------------------------------------------------------
# Audit: Pydantic BaseModel + ConfigDict discipline (GHI #203 / rules 25, 26)
# ---------------------------------------------------------------------------


def audit_pydantic_models(project_root: Path) -> list[ValidationError]:
    """Fail on stdlib ``@dataclass`` in governance code and BaseModels missing ConfigDict.

    Rule 25: no stdlib ``dataclass`` for governance data models.
    Rule 26: every ``BaseModel`` subclass declares ``model_config = ConfigDict(...)``.
    """
    src_root = project_root / "src" / "gzkit"
    if not src_root.is_dir():
        return []
    errors: list[ValidationError] = []
    for py_file in sorted(src_root.rglob("*.py")):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        rel = py_file.relative_to(project_root).as_posix()
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            artifact_key = f"{rel}::{node.name}"
            if _has_dataclass_decorator(node) and artifact_key not in _DATACLASS_WAIVERS:
                errors.append(
                    ValidationError(
                        type="pydantic_models",
                        artifact=f"{rel}:{node.lineno}",
                        message=(
                            f"Class `{node.name}` uses stdlib `@dataclass`. "
                            "Governance data must use Pydantic `BaseModel` "
                            "(`.gzkit/rules/models.md`)."
                        ),
                    )
                )
            if _extends_basemodel(node) and not _has_model_config(node):
                errors.append(
                    ValidationError(
                        type="pydantic_models",
                        artifact=f"{rel}:{node.lineno}",
                        message=(
                            f"BaseModel subclass `{node.name}` is missing "
                            "`model_config = ConfigDict(...)` (rule 26)."
                        ),
                    )
                )
    for stale in sorted(_DATACLASS_WAIVERS.keys() - _extant_class_keys(src_root, project_root)):
        errors.append(
            ValidationError(
                type="pydantic_models",
                artifact=f"DATACLASS_WAIVERS::{stale}",
                message=(
                    f"Waiver `{stale}` references a class that no longer exists. "
                    "Remove the stale waiver."
                ),
            )
        )
    return errors


def _has_dataclass_decorator(node: ast.ClassDef) -> bool:
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == "dataclass":
            return True
        if (
            isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Name)
            and dec.func.id == "dataclass"
        ):
            return True
        if isinstance(dec, ast.Attribute) and dec.attr == "dataclass":
            return True
    return False


def _extends_basemodel(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id == "BaseModel":
            return True
        if isinstance(base, ast.Attribute) and base.attr == "BaseModel":
            return True
    return False


def _has_model_config(node: ast.ClassDef) -> bool:
    for stmt in node.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == "model_config":
                    return True
        if (
            isinstance(stmt, ast.AnnAssign)
            and isinstance(stmt.target, ast.Name)
            and stmt.target.id == "model_config"
        ):
            return True
    return False


def _extant_class_keys(src_root: Path, project_root: Path) -> set[str]:
    keys: set[str] = set()
    for py_file in src_root.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        rel = py_file.relative_to(project_root).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                keys.add(f"{rel}::{node.name}")
    return keys


# ---------------------------------------------------------------------------
# Audit: class size limit (300 lines) (GHI #204 / rule 21)
# ---------------------------------------------------------------------------


def audit_class_size(project_root: Path) -> list[ValidationError]:
    """Fail on classes whose body exceeds 300 lines (rule 21).

    Waivers are explicit in ``_CLASS_SIZE_WAIVERS`` and carry a rationale.
    """
    src_root = project_root / "src" / "gzkit"
    if not src_root.is_dir():
        return []
    limit = 300
    errors: list[ValidationError] = []
    extant: set[str] = set()
    for py_file in sorted(src_root.rglob("*.py")):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        rel = py_file.relative_to(project_root).as_posix()
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            end = getattr(node, "end_lineno", node.lineno)
            span = end - node.lineno + 1
            key = f"{rel}::{node.name}"
            extant.add(key)
            if span <= limit:
                continue
            if key in _CLASS_SIZE_WAIVERS:
                continue
            errors.append(
                ValidationError(
                    type="class_size",
                    artifact=f"{rel}:{node.lineno}",
                    message=(
                        f"Class `{node.name}` spans {span} lines (>{limit}). "
                        "Split or add an explicit waiver with rationale in "
                        "`_CLASS_SIZE_WAIVERS` (`.gzkit/rules/pythonic.md`)."
                    ),
                )
            )
    for stale in sorted(_CLASS_SIZE_WAIVERS.keys() - extant):
        errors.append(
            ValidationError(
                type="class_size",
                artifact=f"CLASS_SIZE_WAIVERS::{stale}",
                message=(
                    f"Waiver `{stale}` references a class that no longer exists. "
                    "Remove the stale waiver."
                ),
            )
        )
    return errors


# ---------------------------------------------------------------------------
# Audit: version bump → git tag alignment (GHI #205 / rule 11)
# ---------------------------------------------------------------------------


def audit_version_release(project_root: Path) -> list[ValidationError]:
    """Fail if ``pyproject.toml`` version has no matching ``vX.Y.Z`` git tag.

    Every version bump is a release (CLAUDE.md local rule 11). This audit
    compares the declared pyproject version against the local git-tag set;
    if the bump landed without a tag, the release step was skipped.

    Per GHI #217, the audit also accepts an in-flight release manifest at
    ``docs/releases/PATCH-v{version}.md`` as equivalent evidence. The
    manifest is written by ``gz patch release`` before the bump commit is
    attempted, so it satisfies the audit during the brief window between
    the commit and ``gh release create`` (which creates the tag).
    """
    import subprocess  # noqa: PLC0415

    pyproject = project_root / "pyproject.toml"
    if not pyproject.is_file():
        return []
    version = _read_pyproject_version(pyproject)
    if version is None:
        return []
    expected = f"v{version}"
    manifest = project_root / "docs" / "releases" / f"PATCH-{expected}.md"
    if manifest.is_file():
        return []
    try:
        result = subprocess.run(
            ["git", "tag", "--list", "v*"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    tags = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    if expected in tags:
        return []
    return [
        ValidationError(
            type="version_release",
            artifact=f"pyproject.toml::version={version}",
            message=(
                f"Declared version `{version}` has no matching git tag `{expected}`. "
                "Every version bump is a release (CLAUDE.md local rule 11) — "
                f"create one via `gh release create {expected} --target main "
                f'--title "{expected}" --latest --notes "..."`.'
            ),
        )
    ]


def _read_pyproject_version(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("version"):
            continue
        match = re.match(r'version\s*=\s*"([^"]+)"', stripped)
        if match:
            return match.group(1)
    return None


# ---------------------------------------------------------------------------
# Audit: pool ADR runtime-track isolation (GHI #208 / rules 1, 2)
# ---------------------------------------------------------------------------


def audit_pool_adr_isolation(project_root: Path) -> list[ValidationError]:
    """Fail on pool ADRs receiving runtime-track lifecycle or gate events.

    Pool ADRs (under ``docs/design/adr/pool/`` or id-prefixed ``ADR-pool.*``)
    are architectural backlog. Per architectural-boundaries rules 1–2 they
    must not receive Gate 1+ events; doing so means they were promoted
    without the formal ``gz-adr-promote`` ceremony.
    """
    import json  # noqa: PLC0415

    ledger = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger.is_file():
        return []

    forbidden_events = {
        "gate_checked",
        "attestation",
        "obpi_completed",
        "adr_attested",
        "adr_audit",
        "adr_closeout",
        "lifecycle_transition",
    }
    errors: list[ValidationError] = []
    seen: set[tuple[str, str]] = set()
    for lineno, raw in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        event_type = event.get("event")
        artifact_id = event.get("id") or event.get("adr_id") or ""
        if not isinstance(artifact_id, str) or not artifact_id.startswith("ADR-pool."):
            continue
        if event_type not in forbidden_events:
            continue
        key = (artifact_id, event_type)
        if key in seen:
            continue
        seen.add(key)
        errors.append(
            ValidationError(
                type="pool_adr_isolation",
                artifact=f".gzkit/ledger.jsonl:{lineno}",
                message=(
                    f"Pool ADR `{artifact_id}` received runtime-track event "
                    f"`{event_type}`. Pool ADRs must not advance through "
                    "gates without promotion via `gz adr promote` "
                    "(CLAUDE.md architectural boundaries 1–2)."
                ),
            )
        )
    return errors


# ---------------------------------------------------------------------------
# Audit: behave REQ scenario-tag coverage (GHI #211; reversed per GHI #276)
# ---------------------------------------------------------------------------
#
# Direction: OBPI → feature. Rule 39 and the scorecard assert "Heavy-lane
# and foundation-kind OBPIs have ``@REQ-X.Y.Z-NN-MM`` scenario coverage."
# The original (GHI #211) feature → feature scan could flag a feature file
# that forgot to tag a scenario but could not flag a heavy OBPI that never
# wrote a feature at all. The reversed direction enumerates heavy OBPI
# briefs, extracts REQs from the Acceptance Criteria section, and asserts
# each REQ has a matching scenario-level ``@REQ-*`` tag somewhere under
# ``features/``. Pool ADRs are excluded (cross-ref ``--pool-adr-isolation``).
#
# Waivers live in ``data/behave_coverage_waivers.json`` keyed by OBPI ID.
# The initial seed captures every heavy OBPI that predates the reversal
# (GHI #276 closed-OBPI carve-out, same pattern as ``_UTF8_PIPE_WAIVERS``).

_OBPI_ID_IN_FRONTMATTER = re.compile(
    r"^id:\s*(OBPI-[0-9]+\.[0-9]+\.[0-9]+-[0-9]+[A-Za-z0-9\-.]*)\s*$",
    re.MULTILINE,
)
_LANE_IN_FRONTMATTER = re.compile(r"^lane:\s*([A-Za-z]+)\s*$", re.MULTILINE)
_ACCEPTANCE_SECTION = re.compile(
    r"^##\s+Acceptance Criteria\s*$(.*?)(?=^##\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)


def _load_behave_coverage_waivers(project_root: Path) -> dict[str, str]:
    """Return ``{OBPI-id: rationale}`` from the sidecar waiver file.

    The sidecar stores rationale codes keyed to a ``default_rationale`` map
    so the 370+ historical entries compress to one-liners plus one shared
    message. Keys without a resolvable rationale code still load as waived
    (rationale falls through to the raw code string) so the audit never
    blocks on a malformed entry.
    """
    waiver_path = project_root / "data" / "behave_coverage_waivers.json"
    if not waiver_path.is_file():
        return {}
    try:
        payload = json.loads(waiver_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return {}
    default_rationale = payload.get("default_rationale", {}) or {}
    waivers = payload.get("waivers", {}) or {}
    out: dict[str, str] = {}
    for obpi_id, entry in waivers.items():
        if not isinstance(obpi_id, str) or not obpi_id.startswith("OBPI-"):
            continue
        rationale_code = ""
        if isinstance(entry, dict):
            rationale_code = str(entry.get("rationale", ""))
        elif isinstance(entry, str):
            rationale_code = entry
        out[obpi_id] = default_rationale.get(rationale_code, rationale_code)
    return out


def _extract_heavy_obpi_briefs(project_root: Path) -> list[tuple[Path, str, list[str]]]:
    """Enumerate heavy-lane OBPI briefs under ``docs/design/adr/``.

    Returns tuples of ``(brief_path, obpi_id, req_ids)``. Pool-ADR briefs
    (``docs/design/adr/pool/**``) are excluded per the ``--pool-adr-isolation``
    contract. REQ-IDs are extracted from the ``## Acceptance Criteria``
    section only — the REQ Coverage and Requirements sections restate the
    same IDs, and anchoring on Acceptance Criteria matches the brief template
    and the ``gz adr audit-check`` derivation.
    """
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    briefs: list[tuple[Path, str, list[str]]] = []
    for brief in sorted(adr_root.rglob("OBPI-*.md")):
        if "pool" in brief.parts:
            continue
        try:
            text = brief.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        lane_match = _LANE_IN_FRONTMATTER.search(text)
        if not lane_match or lane_match.group(1).lower() != "heavy":
            continue
        id_match = _OBPI_ID_IN_FRONTMATTER.search(text)
        if not id_match:
            continue
        obpi_id = id_match.group(1)
        accept_match = _ACCEPTANCE_SECTION.search(text)
        if not accept_match:
            continue
        req_ids = sorted(set(_REQ_ID_IN_BRIEF.findall(accept_match.group(1))))
        if not req_ids:
            continue
        briefs.append((brief, obpi_id, req_ids))
    return briefs


def _collect_scenario_req_tags(project_root: Path) -> set[str]:
    """Return the set of REQ-IDs carried by scenario-level ``@REQ-*`` tags."""
    features_root = project_root / "features"
    if not features_root.is_dir():
        return set()
    tagged: set[str] = set()
    for feat in features_root.rglob("*.feature"):
        try:
            text = feat.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        tagged.update(m.group(1) for m in _SCENARIO_REQ_TAG.finditer(text))
    return tagged


def audit_behave_req_tags(project_root: Path) -> list[ValidationError]:
    """Fail on heavy-lane OBPIs whose REQs lack ``@REQ-*`` scenario tags.

    Rule 39 (``.gzkit/rules/tests.md`` § Behave scenario tagging) and the
    advisory scorecard row 39 both assert that heavy-lane and foundation-kind
    OBPIs carry scenario-level ``@REQ-X.Y.Z-NN-MM`` tags for every REQ in
    their Acceptance Criteria. The enforcement direction is OBPI → feature:
    enumerate heavy OBPI briefs, assert each REQ is tagged somewhere under
    ``features/**``. Missing coverage → policy breach (exit 3) unless the
    OBPI ID is present in ``data/behave_coverage_waivers.json``.

    Pool-ADR briefs are excluded per the ``--pool-adr-isolation`` contract;
    pool ADRs do not carry gate obligations and cannot fire Gate 4.
    """
    briefs = _extract_heavy_obpi_briefs(project_root)
    if not briefs:
        return []
    tagged_reqs = _collect_scenario_req_tags(project_root)
    waivers = _load_behave_coverage_waivers(project_root)
    errors: list[ValidationError] = []
    for brief_path, obpi_id, req_ids in briefs:
        if obpi_id in waivers:
            continue
        missing = [r for r in req_ids if r not in tagged_reqs]
        if not missing:
            continue
        rel = brief_path.relative_to(project_root).as_posix()
        errors.append(
            ValidationError(
                type="behave_req_tags",
                artifact=rel,
                message=(
                    f"Heavy-lane OBPI `{obpi_id}` has REQ-IDs without "
                    "matching scenario-level `@REQ-X.Y.Z-NN-MM` tags under "
                    "`features/**`. Missing: "
                    + ", ".join(missing[:5])
                    + (f" (+{len(missing) - 5} more)" if len(missing) > 5 else "")
                    + ". Add scenario tags or waive in "
                    "`data/behave_coverage_waivers.json` with rationale."
                ),
            )
        )
    return errors


# ---------------------------------------------------------------------------
# Audit: Skill ↔ CLI ↔ runbook alignment Invariant 1 (GHI #202 / rule 28)
# ---------------------------------------------------------------------------


# CLI verbs that legitimately have no wielding skill (e.g. bootstrap and
# internal commands). Each entry must cite a reason.
_NO_SKILL_VERBS: dict[str, str] = {
    "init": "Bootstrap command — scaffolds a new repo; no skill mediates initialization.",
    "register-adrs": "One-shot historical registrar; not a recurring operator action.",
    "migrate-semver": "One-shot migration command; no skill mediates historical renames.",
    "personas": "Internal persona listing; consumed by other skills, not directly.",
    "roles": "Internal role listing; consumed by other skills, not directly.",
    "interview": "Subcommand invoked inside gz-adr-create; no standalone skill needed.",
    "drift": "Subcommand consumed by other skills.",
    "preflight": "Subcommand consumed by other skills.",
    "readiness": "Subcommand consumed by other skills.",
    "covers": "Coverage inspection; consumed by tests, not a skill.",
    "specify": "Subcommand invoked by gz-obpi-specify; skill-version gating covers it.",
    "flag": "Feature-flag inspection; internal developer affordance.",
    "flags": "Feature-flag inspection; internal developer affordance.",
    "parity": "Cross-repo parity inspector; consumed by airlineops-parity-scan skill.",
    "format": "Alias invocation — the `format` skill wraps it.",
    "lint": "Direct lint verb; wrapped by ARB workflow.",
    "typecheck": "Direct typecheck verb; wrapped by ARB workflow.",
    "test": "Direct test verb; wrapped by ARB workflow.",
    "task": (
        "Subcommand group (`gz task start/complete`); consumed by "
        "TASK-trailer discipline in TDD workflow."
    ),
    "frontmatter": (
        "Subcommand group (`gz frontmatter reconcile/check`); consumed "
        "inside gz-adr-recon and state-doctrine skills."
    ),
    "justify": (
        "CLI surface landed in ADR-0.0.19 OBPI-02 ahead of its wielding skill; "
        "the `gz-justify` skill ships in OBPI-0.0.19-04 per the ADR's "
        "decomposition plan (skill definition + upstream integrations OBPI)."
    ),
}


def audit_skill_alignment(project_root: Path) -> list[ValidationError]:
    """Invariant 1: every CLI verb is referenced by at least one skill.

    Scans ``.gzkit/skills/**/SKILL.md`` frontmatter (``gz_command:``) and body
    prose for each registered top-level CLI verb. A verb with no wielding
    skill and no explicit waiver is a defect signal per
    ``.gzkit/rules/tool-skill-runbook-alignment.md``.
    """
    skills_root = project_root / ".gzkit" / "skills"
    if not skills_root.is_dir():
        return []
    try:
        known_verbs = _known_cli_verbs()
    except Exception:
        return []

    verb_refs: dict[str, set[str]] = {verb: set() for verb in known_verbs}
    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        try:
            content = skill_md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = skill_md.relative_to(project_root).as_posix()
        for verb in known_verbs:
            if re.search(rf"\bgz\s+{re.escape(verb)}\b", content) or re.search(
                rf"gz_command:\s*{re.escape(verb)}\b", content
            ):
                verb_refs[verb].add(rel)

    errors: list[ValidationError] = []
    for verb in sorted(known_verbs):
        if verb in _NO_SKILL_VERBS:
            continue
        if verb_refs[verb]:
            continue
        errors.append(
            ValidationError(
                type="skill_alignment",
                artifact=f"gz {verb}",
                message=(
                    f"CLI verb `gz {verb}` has no wielding skill under "
                    ".gzkit/skills/**. Author a skill or add an entry to "
                    "`_NO_SKILL_VERBS` with rationale (tool-skill-runbook Invariant 1)."
                ),
            )
        )
    for stale in sorted(_NO_SKILL_VERBS.keys() - known_verbs):
        errors.append(
            ValidationError(
                type="skill_alignment",
                artifact=f"_NO_SKILL_VERBS::{stale}",
                message=(
                    f"Waiver `{stale}` references a verb that is no longer registered. "
                    "Remove the stale waiver."
                ),
            )
        )
    return errors


# ---------------------------------------------------------------------------
# Audit: advisory-rules scorecard self-test (GHI #212)
# ---------------------------------------------------------------------------


def audit_advisory_scorecard(project_root: Path) -> list[ValidationError]:
    """Every rule file under ``.gzkit/rules/`` must appear in the scorecard.

    The scorecard at ``docs/governance/advisory-rules-audit.md`` catalogues
    rules and scores their enforceability. When a new rule file lands
    without a scorecard entry, this audit flags the drift so the scorecard
    stays a complete index (trust-doctrine §3 — doctrine that survives agent
    rotation is doctrine that's mechanical).
    """
    scorecard = project_root / "docs" / "governance" / "advisory-rules-audit.md"
    rules_root = project_root / ".gzkit" / "rules"
    if not scorecard.is_file() or not rules_root.is_dir():
        return []
    scorecard_text = scorecard.read_text(encoding="utf-8").lower()
    errors: list[ValidationError] = []
    for rule_md in sorted(rules_root.glob("*.md")):
        stem = rule_md.stem.lower()
        if stem in scorecard_text:
            continue
        errors.append(
            ValidationError(
                type="advisory_scorecard",
                artifact=str(rule_md.relative_to(project_root)),
                message=(
                    f"Rule file `{rule_md.name}` is not referenced by the advisory "
                    "scorecard. Add a row to `docs/governance/advisory-rules-audit.md` "
                    "with a score (Mechanical / Promotable / Judgment / Ambiguous)."
                ),
            )
        )
    return errors


# ---------------------------------------------------------------------------
# Audit: reconcile freshness (GHI #213 / rule 4)
# ---------------------------------------------------------------------------


def audit_reconcile_freshness(project_root: Path) -> list[ValidationError]:
    """Flag when reconciliation has not run since HEAD or within a recency window.

    Reconciliation is a core architectural operation, not a maintenance
    chore (CLAUDE.md architectural-boundary 4). If the latest
    ``frontmatter_reconciled`` / ``reconcile_*`` ledger event is older than
    HEAD's commit timestamp, derived state is potentially stale.
    """
    import json  # noqa: PLC0415
    import subprocess  # noqa: PLC0415
    from datetime import UTC, datetime  # noqa: PLC0415

    ledger = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger.is_file():
        return []

    latest: datetime | None = None
    reconcile_events = {
        "frontmatter_reconciled",
        "reconcile_run",
        "reconcile_completed",
        "state_reconciled",
        "obpi_reconciled",
    }
    for raw in ledger.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if event.get("event") not in reconcile_events:
            continue
        ts = event.get("ts")
        if not isinstance(ts, str):
            continue
        try:
            parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if latest is None or parsed > latest:
            latest = parsed

    try:
        head_ts_text = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "HEAD"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    try:
        head_ts = datetime.fromisoformat(head_ts_text.replace("Z", "+00:00"))
    except ValueError:
        return []

    if latest is None:
        # Ledger has no reconcile events yet — the reconciliation pathway is
        # still being mechanized. Skip rather than fail until the event types
        # above are emitted by ``gz frontmatter reconcile`` / ``gz state``.
        return []
    # Allow a 24-hour grace window so in-flight commits don't fail pre-commit
    # on a strictly monotonic comparison.
    delta = (head_ts - latest).total_seconds()
    if delta > 86400:
        now = datetime.now(UTC).isoformat()
        return [
            ValidationError(
                type="reconcile_freshness",
                artifact=f".gzkit/ledger.jsonl::latest={latest.isoformat()}",
                message=(
                    f"Latest reconcile event is older than HEAD by {int(delta)}s "
                    f"(HEAD={head_ts.isoformat()}, now={now}). Run "
                    "`uv run gz frontmatter reconcile` before the next release."
                ),
            )
        ]
    return []


# ---------------------------------------------------------------------------
# Audit: ADR taxonomy — kind / semver / id-prefix coherence (ADR-0.0.17)
# ---------------------------------------------------------------------------


_FOUNDATION_SEMVER_RE = re.compile(r"^0\.0\.\d+$")
_POOL_ID_PREFIX = "ADR-pool."


def audit_adr_taxonomy(project_root: Path) -> list[ValidationError]:
    """Fail on ADRs that violate the pool/foundation/feature taxonomy.

    Enforces ADR-0.0.17 § Decision: pool kind is derived from the
    ``ADR-pool.*`` id prefix; non-pool ADRs carry ``kind: foundation`` or
    ``kind: feature`` in frontmatter; ``foundation`` requires semver
    ``0.0.x``; ``feature`` requires any other semver. Never mutates files.
    """
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    errors: list[ValidationError] = []
    for adr_md in sorted(adr_root.rglob("ADR-*.md")):
        # Skip nested obpi / brief / audit artefacts — same convention as
        # _validate_decomposition in validate_cmd.py.
        if "obpis" in adr_md.parts or "briefs" in adr_md.parts or "audit" in adr_md.parts:
            continue
        frontmatter = _parse_adr_frontmatter(adr_md)
        if frontmatter is None:
            continue
        rel = adr_md.relative_to(project_root).as_posix()
        adr_id = frontmatter.get("id", "")
        kind = frontmatter.get("kind")
        semver = frontmatter.get("semver")
        is_pool = isinstance(adr_id, str) and adr_id.startswith(_POOL_ID_PREFIX)

        if is_pool:
            if kind is not None:
                errors.append(
                    ValidationError(
                        type="taxonomy",
                        artifact=rel,
                        message=(
                            "Pool ADRs derive kind from the `ADR-pool.*` id "
                            "prefix; remove the `kind:` frontmatter field."
                        ),
                    )
                )
            continue

        if kind is None:
            errors.append(
                ValidationError(
                    type="taxonomy",
                    artifact=rel,
                    message=(
                        "Non-pool ADR is missing `kind:` frontmatter. Add "
                        "`kind: foundation` for an app/system invariant ADR "
                        "(semver `0.0.x`) or `kind: feature` for a capability "
                        "ADR (semver `0.y.z` and up). See ADR-0.0.17 / ADR-0.0.18."
                    ),
                )
            )
            continue

        if kind not in ("foundation", "feature"):
            errors.append(
                ValidationError(
                    type="taxonomy",
                    artifact=rel,
                    message=(
                        f"Unknown `kind: {kind}`. Expected `foundation` or "
                        "`feature` (pool kind is id-derived, not frontmatter)."
                    ),
                )
            )
            continue

        if kind == "foundation" and not (
            isinstance(semver, str) and _FOUNDATION_SEMVER_RE.match(semver)
        ):
            errors.append(
                ValidationError(
                    type="taxonomy",
                    artifact=rel,
                    message=(
                        f"`kind: foundation` requires semver `0.0.x`; got "
                        f"`{semver}`. Foundation ADRs are app/system invariants "
                        "and never impact release versioning."
                    ),
                )
            )
        elif kind == "feature" and isinstance(semver, str) and _FOUNDATION_SEMVER_RE.match(semver):
            errors.append(
                ValidationError(
                    type="taxonomy",
                    artifact=rel,
                    message=(
                        f"`kind: feature` forbids semver `0.0.x`; got `{semver}`. "
                        "Feature ADRs carry release-impacting semver (`0.y.z` and up)."
                    ),
                )
            )
    return errors


def _parse_adr_frontmatter(path: Path) -> dict[str, str] | None:
    """Read a flat YAML frontmatter block as a ``str -> str`` mapping.

    Stdlib-only to match every sibling audit in this module (no PyYAML
    import widens the trust surface for a flat key/value block).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None
    fields: dict[str, str] = {}
    for raw in lines[1:end]:
        if ":" not in raw:
            continue
        key, _, value = raw.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            value = value[1:-1]
        fields[key] = value
    return fields


_BRIEF_EVIDENCE_H3_HEADINGS = (
    "Implementation Summary",
    "Key Proof",
    "Closing Argument",
)


def audit_brief_headings(project_root: Path) -> list[ValidationError]:
    """Brief evidence sections must use H3, not H2 (GHI #238).

    OBPI briefs standardise per-completion evidence headings at H3 level.
    ``gz obpi complete`` and the completion hooks extract
    ``### Implementation Summary`` and ``### Key Proof`` by exact H3 match;
    the defense-brief renderer extracts ``### Closing Argument``. A brief
    that drifts one of these to ``##`` passes schema validation (the section
    exists) but the extractor stops at the next H2 boundary and yields an
    empty body — triggering mid-ceremony failures.

    The audit flags any ``## Heading`` whose heading text equals one of the
    canonical names exactly (after stripping a trailing ``(Lite)`` / ``(Heavy)``
    parenthetical). Exact match is deliberate: ``## Acceptance Criteria`` is
    a legitimate top-level H2 brief section and must not be conflated with
    the per-pass evidence ``### ACCEPTANCE``.
    """
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    errors: list[ValidationError] = []
    canonical_forms = {h.casefold() for h in _BRIEF_EVIDENCE_H3_HEADINGS}
    for brief in sorted(adr_root.rglob("OBPI-*.md")):
        try:
            lines = brief.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        rel = brief.relative_to(project_root).as_posix()
        for lineno, raw in enumerate(lines, start=1):
            if not raw.startswith("## "):
                continue
            heading = raw[3:].split("(")[0].strip().casefold()
            if heading not in canonical_forms:
                continue
            canonical = next(h for h in _BRIEF_EVIDENCE_H3_HEADINGS if h.casefold() == heading)
            errors.append(
                ValidationError(
                    type="brief_headings",
                    artifact=f"{rel}:{lineno}",
                    message=(
                        f"Evidence section `{canonical}` must use H3 "
                        f"(`### {canonical}`), not H2. Ceremony renderers "
                        "and completion hooks look for H3 level."
                    ),
                )
            )
    return errors


__all__ = [
    "audit_adr_taxonomy",
    "audit_advisory_scorecard",
    "audit_behave_req_tags",
    "audit_brief_headings",
    "audit_class_size",
    "audit_cli_alignment",
    "audit_event_handlers",
    "audit_pool_adr_isolation",
    "audit_pydantic_models",
    "audit_reconcile_freshness",
    "audit_skill_alignment",
    "audit_test_tiers",
    "audit_type_ignores",
    "audit_utf8_prefix",
    "audit_validator_fields",
    "audit_version_release",
]
