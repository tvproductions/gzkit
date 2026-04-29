"""Ledger event / validator-field trust audits (GHI #193 class).

* ``audit_event_handlers`` — every ledger event emitted has a graph handler
  claiming it, or an explicit ``_NO_GRAPH_IMPACT`` waiver with rationale.
* ``audit_validator_fields`` — every validator ``info.get('<field>')`` read
  has a corresponding graph or creation-entry write.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from gzkit.validate import ValidationError

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

_EVENT_TYPE_HEURISTIC = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*")
_GRAPH_WRITE_PATTERN = re.compile(r'graph\[[^\]]+\]\["([^"]+)"\]')
_ENTRY_KEY_PATTERN = re.compile(r'\bentry\["([^"]+)"\]')


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
