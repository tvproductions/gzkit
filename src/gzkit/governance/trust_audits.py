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

_FORBIDDEN_TYPE_IGNORE = re.compile(r"#\s*type:\s*ignore\[")
_BACKTICKED_INVOCATION = re.compile(r"`gz\s+([a-z][a-z0-9-]*)[^`]*`")
_QUOTED_INVOCATION = re.compile(r'"gz\s+([a-z][a-z0-9-]*)[^"]*"')
_STEP_DEF_FIXTURE = re.compile(r'the gz command\s+"([a-z][a-z0-9-]*)')
_EVENT_TYPE_HEURISTIC = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*")


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


__all__ = [
    "audit_cli_alignment",
    "audit_event_handlers",
    "audit_type_ignores",
    "audit_validator_fields",
]
