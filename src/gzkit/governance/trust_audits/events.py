"""Ledger event / validator-field trust audits (GHI #193 class).

* ``audit_event_handlers`` — every ledger event emitted has a graph handler
  claiming it, or an explicit ``_NO_GRAPH_IMPACT`` waiver with rationale.
* ``audit_event_schemas`` — every ledger event emitted has a paired
  ``schemas/ledger.json`` entry so ``gz validate --ledger`` does not
  fail-close with ``Unknown event type`` (GHI #374 class).
* ``audit_validator_fields`` — every validator ``info.get('<field>')`` read
  has a corresponding graph or creation-entry write.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from gzkit.validate import ValidationError

_NO_GRAPH_IMPACT: dict[str, str] = {
    "ledger_event_corrected": (
        "The append-only corrective action (GHI #611). It has no `_apply_*` graph "
        "handler BY DESIGN, and adding one would undo the fix: the correction is "
        "netted at the READER boundary — `get_artifact_graph` builds from "
        "`live_events(...)` — so every existing handler became correction-aware "
        "without a branch of its own. A per-event handler here would be a second, "
        "partial implementation of the netting, which is the per-verb hand-patching "
        "this GHI exists to end. Its subject is another ledger ROW, named by the "
        "`(event, id, ts)` triple, not a governance artifact, so there is no node to "
        "add and no edge to draw."
    ),
    "surface_weight_recalibrated": (
        "Witness that the surface-weight bands and/or floor moved (GHI #791), required "
        "by ADR-0.0.33 § Anti-Patterns item 3 — 'Band changes are ledger events, not "
        "config tweaks'. It records a THRESHOLD change, not an artifact relationship: "
        "the subject is a pair of integers in `surface_weight.py` and a snapshot in "
        "`data/surface_weight_floor.json`, neither of which is a graph node, so there "
        "is nothing to link. Its consumer is `_check_floor_drift`, which reads only the "
        "event's timestamp to decide whether the floor was re-snapshotted alongside it. "
        "Drawing an edge would model a doctrine calibration as artifact lineage."
    ),
    "session_exit_bookmark_skipped": (
        "The exit beat fired and deliberately booked nothing, because an authored "
        "handoff already covers the session and provably nothing has happened since "
        "(operator ruling 2026-08-05). It records a NON-event: no artifact was "
        "created, so there is no node to add and no edge to draw — the handoff it "
        "names is already a graph node via its own frontmatter. It exists so a "
        "deliberate skip is distinguishable from a crashed hook, which is the "
        "'does it fire?' ambiguity GHI #756 was filed to close; that is an audit "
        "property, not a lineage one."
    ),
    "handoff_resume_authorized": (
        "Operator ruling on a resumed handoff (GHI #574). It once lifted the Operator "
        "Authorization Gate for one harness session; that gate was retired 2026-08-15 "
        "and nothing reads this to permit anything now — it is the Layer-2 record of "
        "what the operator said. Waived unchanged: session-scoped, not artifact "
        "lineage. It attaches to a session id, and the handoff it names is already a "
        "graph node via its own frontmatter."
    ),
    "handoff_resume_decided": (
        "Operator transit decision on a resumed handoff (GHI #757), the successor to "
        "`handoff_resume_authorized` and still written by `gz handoff decide`. Waived "
        "for the same reason: session-scoped provenance, not artifact lineage. It "
        "attaches to a session id, and the handoff it names is already a graph node "
        "via its own frontmatter. The `decision` and `set_aside` fields sharpen WHAT "
        "was ruled and which counsel was declined — they do not make the ruling a "
        "durable relationship between artifacts, and since the gate's retirement they "
        "gate nothing at all."
    ),
    "stage2_dispatch_recorded": (
        "One mandated Stage-2 role produced receipted independent input (GHI #886). "
        "Process evidence about HOW an OBPI's Stage 2 was executed, not a relationship "
        "between artifacts: the OBPI is already a graph node via `obpi_created`, and "
        "this adds no second artifact to link it to. Its sole consumer is "
        "`_check_stage2_dispatch`, which counts roles at Stage 5. Same disposition and "
        "same reasoning as `red_receipt_emitted` one entry down — evidence attaching to "
        "a governance act, not lineage. Contrast `obpi_blocked_on_operator`, which DOES "
        "carry a handler: that one is a reversible STATE of the node itself, so `gz "
        "state` must show it; a dispatch record is an accumulating log, and there is no "
        "flag on the node it would set."
    ),
    "stage2_single_driver_declared": (
        "A knowingly-undispatched Stage 2, declared with its reason (GHI #886). Waived "
        "on identical grounds to `stage2_dispatch_recorded` above, and deliberately "
        "given the same disposition: the two are the two halves of one Stage-5 verdict, "
        "and splitting their treatment would be the instance-not-class shape this pair "
        "was fixed together to avoid."
    ),
    "red_receipt_emitted": (
        "Base-tree RED falsifiability witness for one BEHAVIOR REQ (GHI #642). Evidence "
        "that the REQ's covering test fails without its implementation; read by "
        "`gz validate --red-parity`. Attaches to a REQ, not to an artifact graph node."
    ),
    "corpus_entry_retired": (
        "Append-only corpus retirement receipt (GHI #635) — a retraction row superseded "
        "an earlier entry, shrinking the surface's invariant floor. Consumed by "
        "`gzkit.content.tier_policy` when resolving which entries still bind, and by "
        "corpus audits. It records which canon is *current*, not a relationship between "
        "artifacts: the corpus is a per-surface content store, not an artifact graph node."
    ),
    "corpus_retirement_reconciled": (
        "After-the-fact accounting for a retraction row that reached the corpus outside "
        "`gz content retire` — hand-appended (GHI #885) or orphaned by a crash between "
        "the corpus write and the ledger appends (GHI #878). Read by "
        "`gz validate --corpus-retirement-witness` as a witness that Layer 2 accounts "
        "for the canon change. Same disposition as `corpus_entry_retired` above and for "
        "the same reason: it records which canon is current inside a per-surface content "
        "store, never a relationship between artifact-graph nodes."
    ),
    "brief_reconciled": (
        "Brief reconciliation summary record (ADR-0.0.37, OBPI-06). Consumed by "
        "`gz obpi brief-drift` operators and reconciliation audits; does not add or "
        "modify artifact graph nodes."
    ),
    "brief_reconcile_drift_detected": (
        "Per-dimension brief drift payload (ADR-0.0.37, OBPI-06). Diagnostic record "
        "for `gz obpi brief-drift`; informs amendment decisions, not the artifact graph."
    ),
    "brief_reconcile_drift_overridden": (
        "Override receipt for --accept-stale-reconciliation (OBPI-0.0.37-08). "
        "Audit-trail event recording the operator's reason; not an artifact graph node."
    ),
    "security_floor_overridden": (
        "Override receipt for --accept-security-floor (ADR-0.0.72-04). Audit-trail "
        "event recording the overridden security surfaces, operator reason, and "
        "attestor so the override is census-visible; not an artifact graph node."
    ),
    "project_init": "Bootstrap sentinel; no artifact nodes emit from it.",
    "artifact_edited": "Session activity log; consumed by anchor analysis, not graph.",
    "obpi_lock_claimed": "L3 ephemeral lock file; consumed by gz obpi lock, not graph.",
    "obpi_lock_released": "L3 ephemeral lock file; consumed by gz obpi lock, not graph.",
    "obpi_lock_ttl_warning": (
        "SessionStart escalation record (token-block-discipline.md § Sub-Invariant 4, "
        "GHI #603) — a held lock crossed 50% TTL. Consumed by session orientation and "
        "lock-hygiene audits, not the artifact graph."
    ),
    "patch-release": (
        "Release-line metadata (hyphenated per patch_release_event at "
        "src/gzkit/ledger_events.py:300). Consumed by gz patch release, "
        "not artifact graph."
    ),
    "audit_generated": "Heavy-lane audit trail; consumed by gz adr audit tooling, not graph.",
    "adr_eval_completed": "Evaluation scorecard; consumed by gz adr evaluate, not graph.",
    "adr-evaluation": (
        "Full per-dimension evaluation scores (ADR-0.0.26-01). "
        "Consumed by eval-feedback-cluster chore and gz validate --evaluation-justify-binding; "
        "not a direct artifact graph node."
    ),
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
    "agent_sync_completed": (
        "Mechanical witness for `gz agent sync control-surfaces` runs (GHI #369). "
        "Records that canonical rules + mirrors regenerated; consumed by sync "
        "audits and brief-level REQ proofs, not the artifact graph."
    ),
    "obpi_completion_uncovered_accept": (
        "REQ-coverage waiver record (ADR-0.0.25-02). Consumed by "
        "_check_adr_obpi_coverage_gaps for ADR closeout gap subtraction; "
        "does not add or modify artifact graph nodes."
    ),
    "pipeline_marker_purged": (
        "Runtime cleanup record (GHI #399) — emitted when the pipeline launcher "
        "auto-purges a stale .pipeline-active-* marker whose OBPI is already "
        "attested_completed in the ledger. Audits the cleanup itself; does not "
        "modify the artifact graph (the OBPI's attested_completed state is "
        "already established by the upstream obpi_receipt_emitted event)."
    ),
    "pipeline_launched": (
        "Pipeline-launch authenticity record (GHI #412) — emitted at Stage 1 with "
        "the nonce embedded in the active pipeline marker. Cross-referenced by "
        "the agent-relayed attestation gate to verify the marker was produced "
        "by an operator-initiated 'gz obpi pipeline' run rather than a forged "
        "file. Does not modify the artifact graph."
    ),
    "intrinsic-complexity-attestation": (
        "Attestation record for functions with irreducibly intrinsic cyclomatic "
        "complexity (OBPI-0.0.29-07). Consumed by gz complexity advise advisor "
        "path and gz validate --documents trust audit; does not add artifact graph "
        "nodes (complexity attestations are a quality-governance record, not an "
        "artifact lifecycle event)."
    ),
    "distribution_baseline_regenerated": (
        "Records that `gz validate --distribution --regenerate` rewrote the "
        "baseline manifest (OBPI-0.0.32-15). Layer-2 witness for regeneration runs "
        "symmetric to agent_sync_completed; consumed by distribution drift audits, "
        "not the artifact graph."
    ),
    "composition_rendered": (
        "Constitutional invariant composition render record (ADR-0.0.37, OBPI-0.0.37-03). "
        "Layer-2 witness for successful registry renders; consumed by drift validator "
        "and governance audit tooling, not the artifact graph."
    ),
    "composition_drift_detected": (
        "Constitutional invariant composition drift record (ADR-0.0.37, OBPI-0.0.37-03). "
        "Layer-2 witness for detected drift between rendered registry and committed target; "
        "consumed by drift validator and governance audit tooling, not the artifact graph."
    ),
    "chore_decommission_processed": (
        "Operator-paced chore-processing record (OBPI-0.0.59-04). "
        "Layer-2 witness for each file processed by the decommission-tautological-tests chore; "
        "consumed by chore audit tooling, not the artifact graph."
    ),
    "corpus_entry_appended": (
        "Append-only corpus capture record (ADR-0.0.37, OBPI-0.0.37-19). "
        "Layer-2 witness for a `gz content remember` append to the per-surface corpus store; "
        "consumed by corpus/compose tooling for provenance audit, not the artifact graph."
    ),
    "composition_candidate_emitted": (
        "Authoring-time compression candidate record (ADR-0.0.37, OBPI-0.0.37-21). "
        "Layer-2 witness that `gz content compose` validated and staged a candidate rendition; "
        "consumed by compose/advisor tooling for audit, not the artifact graph."
    ),
    "rendition_committed": (
        "Operator-attested candidate→committed promotion record (ADR-0.0.37, OBPI-0.0.37-22). "
        "Layer-2 witness that `gz content commit` promoted a candidate to the durable committed "
        "rendition under the operator's corpus attestation, freezing the corpus "
        "content-fingerprint; consumed by the "
        "freshness gate and provenance audit, not the artifact graph."
    ),
    "rendition_advisor_verdict": (
        "Advisor-QC verdict record (ADR-0.0.37, OBPI-0.0.37-24). Layer-2 witness that "
        "`gz content advise-rendition` recorded an information-retained-per-byte verdict as an "
        "ARB receipt the operator cites at Gate 5. Advisory, never gating; consumed by the "
        "advisor-QC audit trail and operator attestation, not the artifact graph."
    ),
    "foundation_grandfathered": (
        "Terminality witness for one closed-manifest `kind: foundation` entry (ADR-0.34.0 "
        "Foundation Sunset, OBPI-04), emitted once per `data/foundation_grandfather.json` "
        "entry at populate time. Consumed by "
        "`gzkit.governance.trust_audits.taxonomy._grandfathered_event_ids` for the "
        "terminal-partition gate via a raw-JSONL replay, not by graph construction: it "
        "records a lifecycle fact ABOUT an existing ADR node, not a relationship BETWEEN "
        "artifacts, so `get_artifact_graph` materializes no node or edge from it (mirrors "
        "the `_ACKNOWLEDGED_NON_CORPUS_EVENT_TYPES` disposition in `gzkit.ontology.corpus`)."
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


def _collect_typed_model_event_types(source: Path) -> set[str]:
    """Collect event-name literals from ``event: Literal["<name>"]`` annotations.

    TASK ledger events (and similar Pydantic-direct emitters) declare their
    event name on the model class, not via a factory call — they need to be
    counted as emitted shapes for schema-coverage purposes.
    """
    tree = ast.parse(source.read_text(encoding="utf-8"))
    typed: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not isinstance(item, ast.AnnAssign):
                continue
            target = item.target
            if not (isinstance(target, ast.Name) and target.id == "event"):
                continue
            annotation = item.annotation
            if not (
                isinstance(annotation, ast.Subscript)
                and isinstance(annotation.value, ast.Name)
                and annotation.value.id == "Literal"
            ):
                continue
            literal_arg = annotation.slice
            if isinstance(literal_arg, ast.Constant) and isinstance(literal_arg.value, str):
                typed.add(literal_arg.value)
    return typed


def audit_event_schemas(project_root: Path) -> list[ValidationError]:
    """Fail on emitted ledger event types missing from ``schemas/ledger.json`` (GHI #374 class).

    Walks ``src/gzkit/ledger_events.py`` for factory-call ``event="<name>"`` constants
    and ``src/gzkit/events.py`` for typed-model ``event: Literal["<name>"]``
    annotations. Compares the union against the events declared in
    ``src/gzkit/schemas/ledger.json``. A factory or typed model without a paired
    schema entry causes ``gz validate --ledger`` to emit ``Unknown event type``
    once the event lands on the ledger — the same coupled-surface failure the
    handler audit closes on the graph side.
    """
    ledger_events = project_root / "src" / "gzkit" / "ledger_events.py"
    typed_events = project_root / "src" / "gzkit" / "events.py"
    schema_file = project_root / "src" / "gzkit" / "schemas" / "ledger.json"
    if not ledger_events.is_file() or not typed_events.is_file() or not schema_file.is_file():
        return []

    emitted = _collect_emitted_event_types(ledger_events)
    emitted |= _collect_typed_model_event_types(typed_events)

    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    declared = set(schema.get("events", {}).keys())

    errors: list[ValidationError] = []
    for missing in sorted(emitted - declared):
        errors.append(
            ValidationError(
                type="event_schemas",
                artifact=f"src/gzkit/schemas/ledger.json::{missing}",
                message=(
                    f"Ledger event `{missing}` is emitted but has no entry in "
                    "src/gzkit/schemas/ledger.json. Add a schema entry naming "
                    "required fields and property types so `gz validate --ledger` "
                    "does not fail-close with `Unknown event type`."
                ),
            )
        )
    for stale in sorted(declared - emitted):
        errors.append(
            ValidationError(
                type="event_schemas",
                artifact=f"src/gzkit/schemas/ledger.json::{stale}",
                message=(
                    f"Schema declares event `{stale}` but no factory in "
                    "src/gzkit/ledger_events.py and no typed model in "
                    "src/gzkit/events.py emits it. Remove the stale schema entry."
                ),
            )
        )
    return errors


def _string_constant(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _claimed_from_event_compare(node: ast.AST) -> set[str]:
    """Pick string-literal RHS from ``event.event == "<literal>"`` comparisons."""
    if not (
        isinstance(node, ast.Compare)
        and isinstance(node.left, ast.Attribute)
        and node.left.attr == "event"
        and isinstance(node.left.value, ast.Name)
        and node.left.value.id == "event"
    ):
        return set()
    return {v for c in node.comparators if (v := _string_constant(c)) is not None}


def _claimed_from_collection(node: ast.AST) -> set[str]:
    if not isinstance(node, (ast.Set, ast.List, ast.Tuple)):
        return set()
    return {
        v
        for elt in node.elts
        if (v := _string_constant(elt)) is not None and _EVENT_TYPE_HEURISTIC.fullmatch(v)
    }


def _collect_claimed_event_types(source: Path) -> set[str]:
    tree = ast.parse(source.read_text(encoding="utf-8"))
    claimed: set[str] = set()
    for node in ast.walk(tree):
        claimed.update(_claimed_from_event_compare(node))
        claimed.update(_claimed_from_collection(node))
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


def _info_get_field(node: ast.AST) -> str | None:
    """Return the literal field name in ``info.get("<field>")`` calls, else None."""
    if not isinstance(node, ast.Call) or not node.args:
        return None
    func = node.func
    if not isinstance(func, ast.Attribute) or func.attr != "get":
        return None
    caller = func.value
    if not isinstance(caller, ast.Name) or caller.id != "info":
        return None
    return _string_constant(node.args[0])


def _collect_info_get_fields(source: Path) -> set[str]:
    tree = ast.parse(source.read_text(encoding="utf-8"))
    fields: set[str] = set()
    for node in ast.walk(tree):
        field = _info_get_field(node)
        if field is not None:
            fields.add(field)
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


# ---------------------------------------------------------------------------
# Producer-side contract parity (GHI #877, reopened)
# ---------------------------------------------------------------------------

_PRODUCER_ROOT = Path("src") / "gzkit"
_ENVELOPE_FIELDS = frozenset({"schema", "schema_", "event", "id", "ts", "parent"})


def _typed_model_fields() -> dict[str, set[str]]:
    """Map each discriminator to the payload fields its typed model declares."""
    from typing import get_args

    from gzkit.events import TypedLedgerEvent

    union, _discriminator = get_args(TypedLedgerEvent)
    declared: dict[str, set[str]] = {}
    for member in get_args(union):
        tag = get_args(member.model_fields["event"].annotation)[0]
        declared[tag] = set(member.model_fields) - _ENVELOPE_FIELDS
    return declared


def _literal_dict_keys(node: ast.Dict) -> set[str]:
    return {
        key.value
        for key in node.keys
        if isinstance(key, ast.Constant) and isinstance(key.value, str)
    }


def _payload_keys(
    scope: ast.FunctionDef | ast.AsyncFunctionDef, extra: ast.expr | None
) -> set[str]:
    """Return the literal payload keys a ``LedgerEvent(...)`` call writes.

    Two shapes are read, because both occur: an inline ``extra={...}`` literal,
    and a named dict the function mutates before passing it (the
    ``extra["handoff_path"] = ...`` shape GHI #877 recorded). Keys computed at
    runtime are invisible to any static reader; that limit is stated in the
    audit's docstring rather than implied.
    """
    if isinstance(extra, ast.Dict):
        return _literal_dict_keys(extra)
    if not isinstance(extra, ast.Name):
        return set()
    keys: set[str] = set()
    for node in ast.walk(scope):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == extra.id
            and isinstance(node.value, ast.Dict)
        ):
            keys |= _literal_dict_keys(node.value)
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == extra.id
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            keys.add(node.slice.value)
    return keys


def audit_producer_fields(project_root: Path) -> list[ValidationError]:
    """Every field a producer writes must be declared by BOTH ledger contracts.

    GHI #877 closed this over the ledger's **committed rows** — a repo-wide fence
    asserting the typed union parses every row on disk. That fence is green while
    a producer that has never fired writes undeclared keys, and this audit exists
    because exactly that happened: ``_book_aborted_exit`` (``gzkit.airlock.exit``)
    writes ``aborted`` and ``error`` on ``airlock_out``, neither contract declared
    them, and the path had never raised in this repository. Zero rows, so nothing
    to parse, so nothing to catch. The first real aborted exit would have written
    a row that replay then refused — ``_EventBase`` is ``extra="forbid"``.

    So the committed-row fence tests HISTORY and this one tests PRODUCERS; they
    fail on different days by construction and neither subsumes the other.

    **Scope, stated rather than implied.** Static analysis reads the two shapes
    that occur in this codebase: an inline ``extra={...}`` literal and a named
    dict mutated by literal-key subscript before it is passed. A key computed at
    runtime, spread from ``**kwargs``, or assembled in a helper is invisible here.
    That residual is why this audit ACCOMPANIES the committed-row fence rather
    than replacing it.
    """
    schema_file = project_root / "src" / "gzkit" / "schemas" / "ledger.json"
    if not schema_file.is_file():
        return []
    schema_events = json.loads(schema_file.read_text(encoding="utf-8")).get("events", {})
    model_fields = _typed_model_fields()
    errors: list[ValidationError] = []

    for source in sorted((project_root / _PRODUCER_ROOT).rglob("*.py")):
        try:
            tree = ast.parse(source.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError):
            continue
        for scope in [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        ]:
            for call in [node for node in ast.walk(scope) if isinstance(node, ast.Call)]:
                func = call.func
                name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
                if name != "LedgerEvent":
                    continue
                keywords = {kw.arg: kw.value for kw in call.keywords}
                event = keywords.get("event")
                if not (isinstance(event, ast.Constant) and isinstance(event.value, str)):
                    continue
                declared_schema = set(schema_events.get(event.value, {}).get("properties", {}))
                declared_model = model_fields.get(event.value, set())
                rel = source.relative_to(project_root).as_posix()
                for key in sorted(_payload_keys(scope, keywords.get("extra"))):
                    missing = [
                        contract
                        for contract, declared in (
                            ("schemas/ledger.json", declared_schema),
                            ("the typed union", declared_model),
                        )
                        if key not in declared
                    ]
                    if not missing:
                        continue
                    errors.append(
                        ValidationError(
                            type="producer_fields",
                            artifact=f"{rel}::{event.value}.{key}",
                            message=(
                                f"Producer writes `{key}` on `{event.value}` but "
                                f"{' and '.join(missing)} does not declare it. The typed "
                                'union is extra="forbid", so the first row this producer '
                                "writes would fail replay. Declare the field in BOTH "
                                "contracts (GHI #877)."
                            ),
                        )
                    )
    return errors
