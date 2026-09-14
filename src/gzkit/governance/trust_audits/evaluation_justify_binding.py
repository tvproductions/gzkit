"""Fail-closed gate: require gz-justify reasoning when evaluation scores trigger.

Gate fires when the most recent ``adr-evaluation`` ledger event for the given
artifact has at least one dimension score below ``low_score_threshold`` OR at
least ``red_team_count_threshold`` red-team challenges fired, and no qualifying
``gz-justify`` walkthrough exists under ``artifacts/justify/``.

A qualifying walkthrough is completed reasoning about the evaluated subject (GHI
#996). Presence is not that: a file named for the subject answered "is something
there", never "did the required reasoning happen". A candidate qualifies only when

1. it parses as a walkthrough (the reader ``gz justify validate`` uses),
2. every section is filled — a structural check, never a quality judgment,
3. its own frontmatter names the evaluated subject (the filename is not
   evidence), and
4. it was generated at or after the evaluation it answers.

Thresholds are loaded from ``data/eval_feedback_thresholds.json`` — never
hardcoded (REQ-0.0.26-02-05).
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.justify.models import AnchorRef
from gzkit.justify.parser import WalkthroughParseError, parse_walkthrough

_ADR_ID_RE = re.compile(r"^ADR-(\d+\.\d+\.\d+)(?:-([a-z0-9][a-z0-9-]*))?$", re.IGNORECASE)
_OBPI_ID_RE = re.compile(r"^OBPI-(\d+\.\d+\.\d+-\d+)(?:-([a-z0-9][a-z0-9-]*))?$", re.IGNORECASE)
_ADR_SLUG_RE = re.compile(r"^adr-(\d+)-(\d+)-(\d+)(?:-([a-z0-9][a-z0-9-]*))?$")


def validate_evaluation_justify_binding(
    artifact_id: str,
    project_root: Path,
    *,
    ledger_path: Path | None = None,
) -> list[ValidationError]:
    """Return ValidationError if low evaluation scores have no qualifying gz-justify walkthrough.

    Returns:
        Empty list if gate passes (no trigger, or trigger + qualifying walkthrough).
        Non-empty list if gate fires (trigger + no qualifying walkthrough).

    """
    # Find most recent adr-evaluation event for this artifact
    lp = ledger_path or (project_root / ".gzkit" / "ledger.jsonl")
    event = _latest_evaluation_event(lp, artifact_id)
    if event is None:
        return []  # No evaluation has run — no gate requirement

    reasons = _trigger_reasons(event, _load_thresholds(project_root))
    if not reasons:
        return []  # No trigger

    evaluated_at = _parse_instant(event.get("timestamp") or event.get("ts"))
    qualified, refusals = _assess_walkthroughs(project_root, artifact_id, evaluated_at)
    if qualified:
        return []

    return [
        ValidationError(
            type="evaluation-justify-binding",
            artifact=artifact_id,
            message=_refusal_message(artifact_id, reasons, refusals, evaluated_at),
        )
    ]


def _trigger_reasons(event: dict, thresholds: dict) -> list[str]:
    """Return why ``event`` triggers the gate; empty when it does not."""
    low_score_threshold = thresholds.get("low_score_threshold", 3.0)
    red_team_count_threshold = thresholds.get("red_team_count_threshold", 3)
    dimensions: dict[str, float] = event.get("dimensions", {})
    red_team: list = event.get("red_team_challenges_fired", [])
    failing_dims = [dim for dim, score in dimensions.items() if score < low_score_threshold]
    reasons = []
    if failing_dims:
        reasons.append(f"dimension score(s) below threshold: {', '.join(failing_dims)}")
    if len(red_team) >= red_team_count_threshold:
        reasons.append(f"{len(red_team)} red-team challenge(s) fired")
    return reasons


def _load_thresholds(project_root: Path) -> dict:
    """Load eval feedback thresholds from ``data/eval_feedback_thresholds.json``."""
    config_path = project_root / "data" / "eval_feedback_thresholds.json"
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def _latest_evaluation_event(ledger_path: Path, artifact_id: str) -> dict | None:
    """Return the most recent ``adr-evaluation`` event for ``artifact_id``, or None."""
    if not ledger_path.exists():
        return None
    events = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("event") == "adr-evaluation" and ev.get("id") == artifact_id:
            events.append(ev)
    return events[-1] if events else None


def _assess_walkthroughs(
    project_root: Path, artifact_id: str, evaluated_at: datetime | None
) -> tuple[bool, list[str]]:
    """Return whether a walkthrough qualifies, plus why each candidate for this subject did not.

    A candidate is a file whose frontmatter names the subject, or whose name starts
    with the subject's dashed id — the latter only so an operator holding an
    old-convention file learns why it no longer counts. Names never admit.
    """
    justify_dir = project_root / "artifacts" / "justify"
    if evaluated_at is None or not justify_dir.is_dir():
        return False, []
    name_prefix = artifact_id.replace(".", "-").lower()
    refusals: list[str] = []
    for path in sorted(justify_dir.iterdir()):
        name = path.name.lower()
        named_for_subject = name.startswith((f"{name_prefix}-", f"{name_prefix}."))
        refusal = _refusal_reason(path, artifact_id, evaluated_at)
        if refusal is None:
            return True, []
        if named_for_subject or refusal[1]:
            refusals.append(f"{path.relative_to(project_root).as_posix()} ({refusal[0]})")
    return False, refusals


def _refusal_reason(
    path: Path, artifact_id: str, evaluated_at: datetime
) -> tuple[str, bool] | None:
    """Return ``None`` when ``path`` qualifies, else ``(reason, names_this_subject)``."""
    if not path.is_file():
        return "not a file", False
    try:
        walkthrough = parse_walkthrough(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        return f"unreadable: {exc}", False
    except WalkthroughParseError as exc:
        return f"not a parseable walkthrough: {exc}", False
    if not _names_subject(walkthrough.anchor, artifact_id):
        return f"names {_anchor_label(walkthrough.anchor)}, not {artifact_id}", False
    unfilled = [section.ordinal for section in walkthrough.sections if not section.is_filled]
    if unfilled:
        return f"section(s) {', '.join(map(str, unfilled))} unfilled", True
    generated_at = _parse_instant(walkthrough.generated_at)
    if generated_at is None:
        return f"generated_at {walkthrough.generated_at!r} is not an ISO-8601 instant", True
    if generated_at < evaluated_at:
        return (
            f"generated {generated_at.isoformat()}, before the evaluation at "
            f"{evaluated_at.isoformat()}",
            True,
        )
    return None


def _names_subject(anchor: AnchorRef, artifact_id: str) -> bool:
    """Return True when the walkthrough's own anchor identifies the evaluated subject.

    ``gz justify`` refuses ADR anchors, so an ADR is named by a ``draft`` anchor
    whose slug is the ADR id with dots as dashes, or by an ``obpi`` anchor under it
    — `gz-adr-evaluate` routes a low ADR score to one (operator ruling 2026-09-14). An
    OBPI is named by its own ``obpi`` anchor. A GHI anchor never names an evaluation:
    its link to an ADR lives on GitHub, which this gate does not consult.
    """
    subject = _subject_key(artifact_id)
    claimed = _claimed_subject(anchor)
    if claimed is None:
        return False
    kind, core, slug = claimed
    if subject[0] == "adr" and kind == "obpi":
        return core.rsplit("-", 1)[0] == subject[1]
    if (kind, core) != subject[:2]:
        return False
    return slug is None or subject[2] is None or slug == subject[2]


def _claimed_subject(anchor: AnchorRef) -> tuple[str, str, str | None] | None:
    """Return the subject key a walkthrough's anchor claims, or None for a GHI anchor."""
    if anchor.kind == "draft" and anchor.draft_slug:
        adr = _ADR_SLUG_RE.match(anchor.draft_slug)
        if adr:
            return ("adr", ".".join(adr.group(1, 2, 3)), adr.group(4))
        return ("id", anchor.draft_slug, None)
    if anchor.kind == "obpi" and anchor.identifier:
        claimed = _subject_key(anchor.identifier)
        return claimed if claimed[0] == "obpi" else None  # an obpi anchor must carry an OBPI id
    return None


def _subject_key(identifier: str) -> tuple[str, str, str | None]:
    """Return ``(kind, core, slug)``: short and full ids of one ADR/OBPI share kind and core.

    An id of neither shape is keyed by its dashed lowercase form and binds only exactly.
    """
    for kind, pattern in (("adr", _ADR_ID_RE), ("obpi", _OBPI_ID_RE)):
        match = pattern.match(identifier)
        if match:
            slug = match.group(2)
            return (kind, match.group(1), slug.lower() if slug else None)
    return ("id", identifier.replace(".", "-").lower(), None)


def _anchor_label(anchor: AnchorRef) -> str:
    if anchor.kind == "draft":
        return f"draft slug {anchor.draft_slug!r}"
    return f"{anchor.kind} anchor {anchor.identifier!r}"


def _producer_step(artifact_id: str) -> str:
    """Return the ``gz justify`` invocation whose walkthrough names ``artifact_id``."""
    kind, core, _slug = _subject_key(artifact_id)
    if kind == "obpi":
        return f"uv run gz justify OBPI-{core} --save"
    slug = artifact_id.replace(".", "-").lower()
    draft = f'uv run gz justify --draft "<what the evaluation found>" --draft-slug {slug} --save'
    if kind == "adr":
        return f"uv run gz justify OBPI-{core}-<NN> --save for an OBPI under it, or {draft}"
    return draft


def _refusal_message(
    artifact_id: str, reasons: list[str], refusals: list[str], evaluated_at: datetime | None
) -> str:
    """Compose three-part recovery prose: what failed, why, the governed next step."""
    if evaluated_at is None:
        found = "the evaluation records no timestamp, so no walkthrough can be shown to answer it"
        answered = "the evaluation"
    else:
        found = "no qualifying walkthrough under artifacts/justify/"
        if refusals:
            found += "; refused: " + "; ".join(refusals)
        answered = f"the evaluation at {evaluated_at.isoformat()}"
    return (
        f"gz-justify walkthrough required for {artifact_id}: {'; '.join(reasons)}, and {found}. "
        "ADR-0.0.26 Decision 2 requires completed reasoning before the lifecycle advances: "
        f"a walkthrough qualifies only when it parses, every section is filled, its frontmatter "
        f"names {artifact_id}, and it was generated at or after {answered}. "
        f"Next: {_producer_step(artifact_id)}, fill every section, then confirm with "
        "`uv run gz justify validate <file>`."
    )


def _parse_instant(value: object) -> datetime | None:
    """Parse an ISO-8601 instant; a naive value is read as UTC, an unparseable one as None."""
    if not isinstance(value, str):
        return None
    try:
        instant = datetime.fromisoformat(value)
    except ValueError:
        return None
    return instant if instant.tzinfo else instant.replace(tzinfo=UTC)
