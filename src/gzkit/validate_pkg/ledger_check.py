"""Ledger validation for append-only JSONL governance ledger."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from gzkit.core.validation_rules import ValidationError
from gzkit.event_evidence import ObpiReceiptEvidence, pydantic_loc_to_field_path
from gzkit.ledger_corrections import (
    CORRECTION_EVENT,
    SubjectKey,
    corrected_subject,
    identity_key,
    is_correction,
    is_well_formed,
    parse_ledger_ts,
)
from gzkit.schemas import load_schema

#: Re-exported so ``gzkit.ledger_merge`` keeps its existing import. The
#: definition moved to :mod:`gzkit.ledger_corrections` — a stdlib-only leaf both
#: the validator and the replay netting import — because the two paths judge the
#: same rows and were judging them by different timestamp contracts: a
#: correction whose ``ts`` this file refused went on voiding its subject at
#: replay, which read no timestamp at all.
__all__ = ["parse_ledger_ts", "validate_ledger"]


def _append_ledger_error(
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
    message: str,
    field: str | None = None,
) -> None:
    artifact = f"{ledger_path}:{line_no}"
    errors.append(
        ValidationError(
            type="ledger",
            artifact=artifact,
            message=message,
            field=field,
        )
    )


#: JSON-Schema type name -> the Python types that satisfy it. `number` admits
#: both because JSON draws no int/float line; `integer` keeps accepting `bool`
#: exactly as it did before this map existed, since `bool` subclasses `int` and
#: narrowing that is a separate decision from the three holes GHI #883 named.
_JSON_TYPE_PYTHON: dict[str, tuple[type, ...]] = {
    "string": (str,),
    "integer": (int,),
    "number": (int, float),
    "object": (dict,),
    "array": (list,),
    "boolean": (bool,),
    "null": (type(None),),
}

#: Phrasing for a single declared type, preserved verbatim from before the union
#: form existed so operator-facing messages (and the assertions reading them) do
#: not churn for a change that is not about them.
_SINGLE_TYPE_PHRASE: dict[str, str] = {
    "string": "must be a string.",
    "integer": "must be an integer.",
    "number": "must be a number.",
    "object": "must be an object.",
    "array": "must be an array.",
    "boolean": "must be a boolean.",
    "null": "must be null.",
}


def _declared_types(rule: dict[str, Any]) -> tuple[str, ...]:
    """Return the type names a field rule permits, for either declaration form.

    `type` is a string or a LIST of strings. Before GHI #883 the check compared
    ``rule.get("type") == "string"``, and a list never equals a string, so every
    branch fell through and a union-declared field was checked for nothing at
    all -- 14 fields across 12 event types accepted any value whatsoever. The
    silence is what made it survive: an unchecked field looks exactly like a
    field that passed.
    """
    declared = rule.get("type")
    if isinstance(declared, str):
        return (declared,)
    if isinstance(declared, list):
        return tuple(name for name in declared if isinstance(name, str))
    return ()


def _validate_ledger_field(
    value: Any,
    field: str,
    rule: dict[str, Any],
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    """Validate one field against its schema rule, recursing into array items.

    Kept in agreement with `gzkit.events.parse_typed_event` by
    `tests/governance/test_ledger_reader_parity.py`: a row this accepts must be
    replayable by the typed reader and vice versa, which is a property neither
    reader can check alone (GHI #883).
    """
    declared = _declared_types(rule)
    permitted = tuple(
        python_type for name in declared for python_type in _JSON_TYPE_PYTHON.get(name, ())
    )
    if permitted and not isinstance(value, permitted):
        phrase = (
            _SINGLE_TYPE_PHRASE[declared[0]]
            if len(declared) == 1 and declared[0] in _SINGLE_TYPE_PHRASE
            else f"must be one of the declared types {list(declared)}."
        )
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Field '{field}' {phrase}",
            field=field,
        )
        return

    if isinstance(value, str):
        min_length = rule.get("min_length")
        # Measure the STRIPPED length. A raw character count is satisfied by
        # whitespace, so `"   "` passed every `min_length` guard in the schema
        # while carrying no content — measured on `foundation_grandfathered`'s
        # `attestor`, where it meant a witnessless event satisfied the gate that
        # exists to require a witness (ADR-0.34.0 OBPI-04). This is a class fix:
        # 54 event types carry min_length-guarded string fields and all of them
        # had the same hole. Blast radius measured before landing — zero live
        # ledger rows pass today and fail under the stripped check.
        if isinstance(min_length, int) and len(value.strip()) < min_length:
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"Field '{field}' must be at least {min_length} non-whitespace characters.",
                field=field,
            )

    if isinstance(value, int):
        min_value = rule.get("min")
        if isinstance(min_value, int) and value < min_value:
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"Field '{field}' must be >= {min_value}.",
                field=field,
            )

    # Descend into declared item types. The outer `isinstance(value, list)` check
    # alone let `floor_moved_ids: [7]` pass the schema and then fail typed replay
    # (GHI #883) — the failure surfacing far from the write that caused it. Every
    # array field declaring `items` had the same hole.
    items_rule = rule.get("items")
    if isinstance(value, list) and isinstance(items_rule, dict):
        for index, item in enumerate(value):
            _validate_ledger_field(
                item,
                f"{field}[{index}]",
                items_rule,
                errors,
                ledger_path,
                line_no,
            )

    allowed = rule.get("enum")
    # An explicit null on a nullable field carries no value to enum-check. The
    # enum constrains what the field says when it says anything; `null` is the
    # field declining to say, which the type check above has already permitted.
    if value is None and "null" in declared:
        return
    if isinstance(allowed, list) and value not in allowed:
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Field '{field}' must be one of {allowed}, got '{value}'.",
            field=field,
        )


def _conditional_predicate(when: Any) -> tuple[str, list[Any]] | None:
    """Return ``(field, allowed)`` when *when* is a supported predicate, else None.

    The only supported form is ``{"field": <name>, "in": [<values>]}`` -- a
    discriminator matched against a closed value set. That is deliberately
    narrow: every conditional invariant observed on this schema has that shape,
    and a richer predicate language grows a surface for a rule to be authored
    that reads as a guard while selecting nothing.

    Readability is answered separately from selection so an unreadable rule can
    be REPORTED rather than skipped. A guard the validator quietly ignores is
    indistinguishable from a passing one -- the presence-check family AGENTS.md
    names, where the only witness is that a rule was authored.
    """
    if not isinstance(when, dict):
        return None
    field = when.get("field")
    allowed = when.get("in")
    if not isinstance(field, str) or not field or not isinstance(allowed, list):
        return None
    return field, allowed


def _validate_ledger_conditionals(
    entry: dict[str, Any],
    event_name: str,
    conditionals: Any,
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    """Apply cross-field rules: constraints keyed on another field's value.

    Every other check in this module reads one field in isolation -- an
    unconditional `required` list, and per-field type/enum/min/min_length. An
    invariant spanning two fields was therefore inexpressible, so wherever a
    runtime gate's condition is recorded in the payload the ledger held enough
    to DETECT a violation by inspection but not enough to REJECT one (GHI #882).

    The class is any event carrying both a discriminator and a field required
    only for some of its values. `corpus_entry_retired` is the instance that
    surfaced it: `gz content retire` refuses a retirement moving invariant-tier
    liveness without a named `--attestor`, records which way the floor moved in
    `floor_direction`, and a hand-authored row pairing a moved floor with an
    empty attestor validated clean. `attestor` cannot simply join `required`
    with a `min_length` -- it is legitimately empty on a routine compressible
    retirement, and that asymmetry is the whole reason a conditional form is
    needed rather than a bespoke check for this one event.

    Each rule carries its own `because` prose. `gz validate --ledger` is a
    fail-closed surface, so `.claude/rules/guardrail-feedback-prose.md`
    § Invariant binds it to three parts -- what failed, why it is forbidden,
    the governed next step -- and the "why" is specific to the rule, not to
    the mechanism. A rule with no `because` cannot compose that message and is
    refused as unsupported, which makes the prose bar mechanical here rather
    than aspirational.
    """
    if not isinstance(conditionals, list):
        return

    for rule in conditionals:
        when = rule.get("when") if isinstance(rule, dict) else None
        then = rule.get("then") if isinstance(rule, dict) else None
        because = rule.get("because") if isinstance(rule, dict) else None
        predicate = _conditional_predicate(when)
        if (
            predicate is None
            or not isinstance(then, dict)
            or not isinstance(because, str)
            or not because.strip()
        ):
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"Event '{event_name}' declares an unsupported conditional rule: "
                f"{json.dumps(rule, sort_keys=True, default=str)}. A conditional needs "
                'a `when` of the form {"field": <name>, "in": [<values>]}, a `then` '
                "object, and non-empty `because` recovery prose "
                "(.claude/rules/guardrail-feedback-prose.md § Invariant); an "
                "unevaluated rule would go inert and read exactly like a passing "
                "check. Repair the rule in `src/gzkit/schemas/ledger.json`, then "
                "re-run `uv run gz validate --ledger`.",
                field="event",
            )
            continue

        when_field, allowed = predicate
        # An entry that does not CARRY the discriminator never fires. The ledger
        # is append-only, so a field introduced today is absent from every row
        # already committed; reading absence as "matches any value" would reject
        # history that no edit is permitted to repair (GHI #877).
        if when_field not in entry or entry[when_field] not in allowed:
            continue

        observed = entry[when_field]
        condition = f"{when_field} is {observed!r}"

        for field in then.get("required", []):
            if field in entry:
                continue
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"Event '{event_name}' is missing field '{field}', required when "
                f"{condition}. {because}",
                field=field,
            )

        properties = then.get("properties", {})
        if not isinstance(properties, dict):
            continue
        for field, field_rule in properties.items():
            if field not in entry or not isinstance(field_rule, dict):
                continue
            # Reuse the per-field checks so the conditional arm and the
            # unconditional one cannot drift -- notably `min_length`, which
            # measures the STRIPPED length. Re-message rather than mutate:
            # ValidationError is frozen, and the finding is only actionable
            # once it names the condition that made the field required.
            scratch: list[ValidationError] = []
            _validate_ledger_field(entry[field], field, field_rule, scratch, ledger_path, line_no)
            errors.extend(
                error.model_copy(
                    update={
                        "message": f"{error.message.rstrip('.')}, required when "
                        f"{condition}. {because}"
                    }
                )
                for error in scratch
            )


def _validate_obpi_receipt_evidence(
    entry: dict[str, Any],
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    """Validate obpi_receipt_emitted evidence via Pydantic discriminated model.

    Replaces manual dispatch with ObpiReceiptEvidence model validation.
    Pydantic errors are converted to gzkit ValidationError format with
    matching field paths for backward-compatible error detection.
    """
    evidence = entry.get("evidence")
    if not isinstance(evidence, dict):
        return
    try:
        ObpiReceiptEvidence.model_validate(evidence)
    except PydanticValidationError as exc:
        for err in exc.errors():
            field_path = pydantic_loc_to_field_path("evidence", err["loc"])
            msg = err.get("msg", "")
            # Strip Pydantic's "Value error, " prefix for clean messages
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, ") :]
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"{field_path} {msg}.",
                field=field_path,
            )


def _validate_ledger_required_fields(
    entry: dict[str, Any],
    required_fields: list[str],
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    for field in required_fields:
        if field in entry:
            continue
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Missing required field: {field}",
            field=field,
        )


def _validate_ledger_event_name(
    entry: dict[str, Any],
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> str | None:
    event_value = entry.get("event")
    if isinstance(event_value, str) and event_value.strip():
        return event_value
    _append_ledger_error(
        errors,
        ledger_path,
        line_no,
        "Field 'event' must be a non-empty string.",
        field="event",
    )
    return None


def _validate_ledger_metadata(
    entry: dict[str, Any],
    expected_schema: str,
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    schema_value = entry.get("schema")
    if schema_value != expected_schema:
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Invalid schema value '{schema_value}', expected '{expected_schema}'.",
            field="schema",
        )

    artifact_id = entry.get("id")
    if not isinstance(artifact_id, str) or not artifact_id.strip():
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            "Field 'id' must be a non-empty string.",
            field="id",
        )

    ts_value = entry.get("ts")
    if not isinstance(ts_value, str) or not ts_value.strip():
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            "Field 'ts' must be a non-empty ISO8601 string.",
            field="ts",
        )
    else:
        normalized_ts = ts_value.replace("Z", "+00:00")
        try:
            datetime.fromisoformat(normalized_ts)
        except ValueError:
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"Field 'ts' is not valid ISO8601: {ts_value}",
                field="ts",
            )

    parent_value = entry.get("parent")
    if "parent" in entry and parent_value is not None and not isinstance(parent_value, str):
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            "Field 'parent' must be a string when present.",
            field="parent",
        )


def _validate_ledger_event_fields(
    entry: dict[str, Any],
    event_name: str,
    event_rule: dict[str, Any],
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    event_required = event_rule.get("required", [])
    for field in event_required:
        if field in entry:
            continue
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Event '{event_name}' missing required field: {field}",
            field=field,
        )

    properties = event_rule.get("properties", {})
    if isinstance(properties, dict):
        for field, rule in properties.items():
            if field not in entry or not isinstance(rule, dict):
                continue
            _validate_ledger_field(
                entry[field],
                field,
                rule,
                errors,
                ledger_path,
                line_no,
            )

    # Guarded rather than returned early on a malformed `properties`: the
    # conditional and evidence arms are independent of it, and a schema defect
    # in one arm silently disarming the others is the inertness this rule form
    # exists to refuse.
    _validate_ledger_conditionals(
        entry=entry,
        event_name=event_name,
        conditionals=event_rule.get("conditional", []),
        errors=errors,
        ledger_path=ledger_path,
        line_no=line_no,
    )

    if event_name == "obpi_receipt_emitted":
        _validate_obpi_receipt_evidence(entry, errors, ledger_path, line_no)


def _validate_ledger_entry(
    entry: dict[str, Any],
    required_fields: list[str],
    expected_schema: str,
    event_rules: dict[str, Any],
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    _validate_ledger_required_fields(entry, required_fields, errors, ledger_path, line_no)
    _validate_ledger_metadata(entry, expected_schema, errors, ledger_path, line_no)

    event_name = _validate_ledger_event_name(entry, errors, ledger_path, line_no)
    if event_name is None:
        return

    event_rule = event_rules.get(event_name)
    if not isinstance(event_rule, dict):
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Unknown event type: {event_name}",
            field="event",
        )
        return

    _validate_ledger_event_fields(entry, event_name, event_rule, errors, ledger_path, line_no)


def _validate_ledger_corrections(
    entries: list[tuple[int, dict[str, Any]]],
    errors: list[ValidationError],
    ledger_path: Path,
) -> None:
    """Enforce the three cross-row properties `gz ledger correct` refuses (GHI #611).

    The command holds the whole ledger when it writes, so it can check that a
    correction's subject exists, is not itself a correction, and was written
    first. Nothing else could: every check above this one reads a single row, and
    a contract-violating correction is individually well-formed. But a row
    reaching the file did not necessarily pass the command — the exported factory
    is callable directly, a merge can carry a correction in, and a row can be
    hand-written — and `gz validate --ledger` is the gate that reads what actually
    landed. Its silence meant such a row sat in the ledger reading as valid.

    **The contract is imported, never restated.** `is_well_formed`,
    `corrected_subject`, `identity_key` and `parse_ledger_ts` all come from
    `gzkit.ledger_corrections`, which is where the netting rule lives. A
    validator that re-derived "is this correction well formed" would be a
    second, drifting implementation of the primitive — the per-consumer
    hand-patching GHI #611 exists to end — and the two copies would disagree at
    the first amendment to either. They already had: envelope validity and
    ordering were checked HERE and nowhere else, so a correction this function
    rejected still voided its subject at replay.

    **Order is POSITION in the file, never the timestamp.** The file IS the
    append order. Comparing timestamps accepted a correction standing ahead of
    its subject whenever the two shared a `ts` — which the ledger already
    contains a pair of — and said nothing at all when either failed to parse.
    Line numbers are exactly the sequence positions `correction_state` counts,
    so the two paths now agree by construction rather than by coincidence.
    """
    #: First appearance wins: a subject repeated later is still, at its earliest
    #: line, ahead of a correction naming it. `identity_key` skips rows whose
    #: `(event, id, ts)` triple is not all strings — such a row has no identity
    #: under this ledger's rule, no well-formed correction can name it, and
    #: hashing it raised `TypeError` and aborted the whole validation run.
    subjects: dict[SubjectKey, int] = {}
    for line_no, entry in entries:
        if is_correction(entry):
            continue
        if (key := identity_key(entry)) is not None:
            subjects.setdefault(key, line_no)

    for line_no, entry in entries:
        if not is_correction(entry):
            continue
        subject = corrected_subject(entry)
        if subject[0] == CORRECTION_EVENT:
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                "This correction names another correction as its subject. Correcting a "
                "correction would make the netting resolve itself recursively, so 'what "
                "is live' would depend on evaluation order; 'reinstated' against the "
                "ORIGINAL row is the in-family reversal.",
                field="subject_event",
            )
            continue
        # A correction failing its own declared contract is already reported
        # field-by-field above, and is inert at replay. Re-reporting it here
        # would say the same defect twice in different words.
        if not is_well_formed(entry):
            continue
        subject_line = subjects.get(subject)
        if subject_line is None:
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"This correction names no ledger row: (event={subject[0]}, "
                f"id={subject[1]}, ts={subject[2]}). A dangling reference sits in the "
                "ledger asserting a correction no reader can apply.",
                field="subject_ts",
            )
            continue
        if subject_line > line_no:
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"This correction precedes its subject: the correction is at line "
                f"{line_no} and the row it corrects is at line {subject_line} "
                f"(stamped {subject[2]}). A corrective action is appended AFTER the "
                "fact it corrects, so a row standing ahead of its subject cannot have "
                "been written by `gz ledger correct` — and it is inert at replay, "
                "which counts the same positions. Re-append the correction at the end "
                "of the ledger rather than editing either row in place.",
                field="ts",
            )


def validate_ledger(ledger_path: Path) -> list[ValidationError]:
    """Validate append-only ledger JSONL entries against ledger schema."""
    errors: list[ValidationError] = []

    if not ledger_path.exists():
        return [
            ValidationError(
                type="ledger",
                artifact=str(ledger_path),
                message="Ledger file does not exist",
            )
        ]

    try:
        schema = load_schema("ledger")
    except FileNotFoundError:
        return [
            ValidationError(
                type="ledger",
                artifact=str(ledger_path),
                message="Ledger schema not found",
            )
        ]

    required_fields = schema.get("required", ["schema", "event", "id", "ts"])
    expected_schema = schema.get("ledger_schema", "gzkit.ledger.v1")
    event_rules = schema.get("events", {})

    # Cross-row state. Every check above this point reads one row in isolation,
    # so an ordering defect was structurally invisible to the validator: the
    # rows either side of an inversion are each individually well-formed
    # (GHI #812).
    previous_ts: datetime | None = None
    previous_line = 0
    #: Every well-shaped row, for the cross-row correction pass below. A
    #: correction's subject may sit anywhere in the file, so the property is not
    #: decidable while streaming.
    entries: list[tuple[int, dict[str, Any]]] = []

    with ledger_path.open(encoding="utf-8") as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                _append_ledger_error(
                    errors,
                    ledger_path,
                    line_no,
                    f"Invalid JSON: {exc}",
                )
                continue

            if not isinstance(entry, dict):
                _append_ledger_error(
                    errors,
                    ledger_path,
                    line_no,
                    "Ledger entry must be a JSON object.",
                )
                continue

            entries.append((line_no, entry))
            _validate_ledger_entry(
                entry=entry,
                required_fields=required_fields,
                expected_schema=expected_schema,
                event_rules=event_rules,
                errors=errors,
                ledger_path=ledger_path,
                line_no=line_no,
            )

            current_ts = parse_ledger_ts(entry.get("ts"))
            if current_ts is None:
                continue
            if previous_ts is not None and current_ts < previous_ts:
                _append_ledger_error(
                    errors,
                    ledger_path,
                    line_no,
                    f"Field 'ts' runs backwards: {current_ts.isoformat()} precedes "
                    f"line {previous_line}'s {previous_ts.isoformat()}. The ledger is "
                    "append-only, so rows must be ordered by ts. A conflicted "
                    "concurrent-session merge is the usual cause; resolve it as a "
                    "ts-ordered union rather than appending one side to the other.",
                    field="ts",
                )
            # Advance even across an inversion, so each boundary is reported once
            # rather than every subsequent row failing against a high-water mark.
            previous_ts = current_ts
            previous_line = line_no

    _validate_ledger_corrections(entries, errors, ledger_path)
    return errors
