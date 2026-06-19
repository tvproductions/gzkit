"""Substance channel for `gz adr evaluate` (ADR-0.0.73 / OBPI-07, GHI #624).

The deterministic evaluator (`adr_eval_scoring.py`) grades **structural
completeness** only — section presence, depth, counts, references. It makes NO
claim about decision SUBSTANCE (whether the problem is genuinely understood or
the decision genuinely justified). Substance is a semantic judgment that no
deterministic regex/word-count can make; the prior `gz adr evaluate` faked it
with keyword heuristics and presented the fake as an authoritative quality
verdict (the facade ADR-0.0.73 exists to kill, GHI #624).

This module is the honest substance channel. Substance scores come ONLY from a
recorded, explanation-first judge verdict (the gzkit record-and-validate judge
flow — ADR-0.0.39/40 — which makes NO live LLM call; an agent/LLM judge produces
the verdict, it is recorded as a ledger event, and read back here). Absent a
recorded verdict, substance is reported **UNGRADED** — never fabricated from
shape. The structural channel and this substance channel carry distinct labels
and are never composited into one number.

Forced downstream (named, not assumed): the full judge-governance apparatus
(JudgeInvocation model, leakage / output-discipline / meta-eval validators) is
ADR-0.0.40's unbuilt scope. This module reuses the existing record-and-validate
seam and the explanation-first discipline only.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

# The two decision-SUBSTANCE dimensions the prior evaluator faked with keyword
# heuristics. These are the only dimensions whose honest grading requires
# semantic judgment; the remaining structural-completeness dimensions are
# deterministic and stay in adr_eval_scoring.py.
SUBSTANCE_DIMENSIONS: tuple[str, ...] = (
    "Problem Substance",
    "Decision Substance",
)

# Minimum explanation length for a disciplined judge verdict (explanation-first
# discipline, mirrors the advisor-QC record half: a verdict with no substantive
# rationale is not a judgment).
_MIN_EXPLANATION_CHARS = 50

# Ledger event recorded by the judge record-half for an ADR substance verdict.
_SUBSTANCE_VERDICT_EVENT = "adr_substance_verdict"


class SubstanceGrade(StrEnum):
    """Substance grade for one ADR decision dimension.

    UNGRADED is the honest default: it means no disciplined judge verdict has
    been recorded for this dimension. It is NEVER produced by deterministic
    shape analysis — the whole point is that shape cannot grade substance.
    """

    STRONG = "STRONG"
    ADEQUATE = "ADEQUATE"
    WEAK = "WEAK"
    UNGRADED = "UNGRADED"


class SubstanceVerdict(BaseModel):
    """A substance judgment for one ADR decision dimension.

    A graded verdict (grade != UNGRADED) MUST carry a non-empty, explanation-first
    rationale and a judge-receipt id — it is the recorded output of a judge, not a
    deterministic score. An UNGRADED verdict carries neither and asserts only the
    absence of a judgment.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    dimension: str = Field(..., description="Substance dimension name")
    grade: SubstanceGrade = Field(..., description="Substance grade or UNGRADED")
    rationale: str = Field("", description="Explanation-first judge rationale (graded only)")
    receipt_id: str = Field("", description="arb-step-judge-* receipt id (graded only)")

    @property
    def is_graded(self) -> bool:
        return self.grade is not SubstanceGrade.UNGRADED


def ungraded(dimension: str) -> SubstanceVerdict:
    """The honest default: no judge verdict recorded for this dimension."""
    return SubstanceVerdict(dimension=dimension, grade=SubstanceGrade.UNGRADED)


def get_substance_verdict_for_adr(
    project_root: Path,
    adr_id: str,
    dimension: str,
) -> SubstanceVerdict:
    """Read the latest recorded judge substance verdict for an ADR dimension.

    Returns the recorded verdict when a disciplined one exists (non-empty
    explanation >= _MIN_EXPLANATION_CHARS and a judge receipt id); otherwise
    returns an UNGRADED verdict. NEVER computes a grade from the ADR prose —
    substance is judged, not pattern-matched.
    """
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return ungraded(dimension)

    latest: SubstanceVerdict | None = None
    for raw in ledger_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or _SUBSTANCE_VERDICT_EVENT not in line:
            continue
        record = _parse_substance_event(line, adr_id, dimension)
        if record is not None:
            latest = record  # later lines win; ledger is append-only chronological
    return latest if latest is not None else ungraded(dimension)


def _parse_substance_event(line: str, adr_id: str, dimension: str) -> SubstanceVerdict | None:
    """Parse one ledger line into a disciplined SubstanceVerdict, or None."""
    import json

    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        return None
    if event.get("event") != _SUBSTANCE_VERDICT_EVENT:
        return None
    if event.get("adr_id") != adr_id or event.get("dimension") != dimension:
        return None
    rationale = str(event.get("rationale", ""))
    receipt_id = str(event.get("receipt_id", ""))
    grade_raw = str(event.get("grade", ""))
    # Discipline gate: a graded verdict needs an explanation-first rationale and a
    # judge receipt. A malformed/undisciplined record does NOT silently grade.
    valid_grades = {g.value for g in SubstanceGrade}
    if grade_raw not in valid_grades or grade_raw == SubstanceGrade.UNGRADED.value:
        return None
    if len(rationale) < _MIN_EXPLANATION_CHARS or not receipt_id.startswith("arb-step-judge-"):
        return None
    return SubstanceVerdict(
        dimension=dimension,
        grade=SubstanceGrade(grade_raw),
        rationale=rationale,
        receipt_id=receipt_id,
    )


def substance_channel_for_adr(project_root: Path, adr_id: str) -> list[SubstanceVerdict]:
    """The full substance channel: one verdict per substance dimension."""
    return [
        get_substance_verdict_for_adr(project_root, adr_id, dim) for dim in SUBSTANCE_DIMENSIONS
    ]
