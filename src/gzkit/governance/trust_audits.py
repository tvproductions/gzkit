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

_FORBIDDEN_TYPE_IGNORE = re.compile(r"#\s*type:\s*ignore\[")
_BACKTICKED_INVOCATION = re.compile(r"`gz\s+([a-z][a-z0-9-]*)[^`]*`")
_QUOTED_INVOCATION = re.compile(r'"gz\s+([a-z][a-z0-9-]*)[^"]*"')
_STEP_DEF_FIXTURE = re.compile(r'the gz command\s+"([a-z][a-z0-9-]*)')
_EVENT_TYPE_HEURISTIC = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*")
_PYTHONUTF8_PREFIX = re.compile(r"PYTHONUTF8=1\s+uv\s+run\s+(?:gz|-m\s+gzkit)")
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
    """Fail on unresolvable ``gz <verb>`` strings in features and operator docs (GHI #198)."""
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
    """Fail on ``PYTHONUTF8=1 uv run gz ...`` anti-pattern in docs/skills/features.

    The CLI entrypoint configures UTF-8 at runtime; the env-var prefix is
    redundant and (per CLAUDE.md local rule 9) must never appear in
    operator-facing docs or skill examples.
    """
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
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for lineno, line in enumerate(content.splitlines(), 1):
                if not _PYTHONUTF8_PREFIX.search(line):
                    continue
                rel = path.relative_to(project_root)
                if path.name == "advisory-rules-audit.md":
                    continue
                errors.append(
                    ValidationError(
                        type="utf8_prefix",
                        artifact=f"{rel}:{lineno}",
                        message=(
                            "`PYTHONUTF8=1` prefix on `uv run gz` is forbidden — "
                            "the CLI entrypoint configures UTF-8 at runtime "
                            "(CLAUDE.md local rule 9)."
                        ),
                    )
                )
    return errors


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
    """
    import subprocess  # noqa: PLC0415

    pyproject = project_root / "pyproject.toml"
    if not pyproject.is_file():
        return []
    version = _read_pyproject_version(pyproject)
    if version is None:
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
    expected = f"v{version}"
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
# Audit: behave REQ scenario-tag coverage (GHI #211 / rule 39)
# ---------------------------------------------------------------------------


_FEATURE_COVERS_REQ = re.compile(r"#\s*@covers\s+(REQ-\d+\.\d+\.\d+-\d+-\d+)")


def audit_behave_req_tags(project_root: Path) -> list[ValidationError]:
    """Fail on feature files declaring ``# @covers REQ-*`` without matching scenario tags.

    Rule 39 (``.gzkit/rules/tests.md``): scenarios that cover a REQ carry
    ``@REQ-X.Y.Z-NN-MM`` as a scenario-level tag. Feature-level
    ``# @covers REQ-...`` comments remain supported for narrative authorship
    but are too coarse for OBPI-scoped filtering — every REQ cited in a
    feature-level covers comment must have a corresponding
    scenario-level tag somewhere in the same file.
    """
    features_root = project_root / "features"
    if not features_root.is_dir():
        return []

    errors: list[ValidationError] = []
    for feat in sorted(features_root.rglob("*.feature")):
        try:
            text = feat.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        declared = set(_FEATURE_COVERS_REQ.findall(text))
        if not declared:
            continue
        tagged = {m.group(1) for m in _SCENARIO_REQ_TAG.finditer(text)}
        missing = sorted(declared - tagged)
        if not missing:
            continue
        rel = feat.relative_to(project_root).as_posix()
        errors.append(
            ValidationError(
                type="behave_req_tags",
                artifact=rel,
                message=(
                    "Feature-level `# @covers REQ-*` comments require matching "
                    "scenario-level `@REQ-X.Y.Z-NN-MM` tags. Missing: "
                    + ", ".join(missing[:5])
                    + (f" (+{len(missing) - 5} more)" if len(missing) > 5 else "")
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


__all__ = [
    "audit_advisory_scorecard",
    "audit_behave_req_tags",
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
