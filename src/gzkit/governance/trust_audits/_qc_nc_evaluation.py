"""Negative controls for the evaluation-justify-binding gate (GHI #996).

Two claims, on the exemption-half precedent (GHI #797). The gate refuses a
triggered evaluation that nothing answers, and ADMITS one that a qualifying
walkthrough answers — a project-controllable file that makes the gate pass an item
it would otherwise fail, which is an exemption by `_qc_claim_exemptions`' bar.

The refuse control is the present-but-false shape the gate once failed: evidence
EXISTS for the subject in every form except the one that counts. A presence check
passes it; only a gate that reads what the evidence says refuses it. The admit
control plants a walkthrough built by the real producer, so a qualifier tightened
past what `gz justify` can produce fails there.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from gzkit.enforcement import create_fixture_tempdir
from gzkit.justify.models import AnchorRef, EvidenceBundle
from gzkit.justify.walkthrough import render_markdown, render_scaffold

#: The evaluated subject every fixture plants; the entrypoints check this id.
SUBJECT = "ADR-0.0.88"

_EVALUATED_AT = datetime(2026, 1, 2, tzinfo=UTC)


def _walkthrough(
    slug: str, *, generated_at: datetime, filled: bool = True, anchor: AnchorRef | None = None
) -> str:
    anchor = anchor or AnchorRef(
        kind="draft", draft_slug=slug, draft_text="fixture", body="fixture"
    )
    evidence = EvidenceBundle(
        anchor=anchor, taxonomy_reference="docs/governance/model-regression-taxonomy.md"
    )
    walkthrough = render_scaffold(anchor, evidence, now=generated_at)
    if filled:
        sections = [
            section.model_copy(update={"reasoning": f"Reasoning for section {section.ordinal}."})
            for section in walkthrough.sections
        ]
        walkthrough = walkthrough.model_copy(update={"sections": sections})
    return render_markdown(walkthrough)


def _triggered_root(slug: str) -> Path:
    """Build a project whose latest evaluation of :data:`SUBJECT` trips the low-score trigger."""
    root = create_fixture_tempdir(prefix=f"gzkit-qc-nc-{slug}-")
    (root / "data").mkdir()
    (root / "data" / "eval_feedback_thresholds.json").write_text(
        json.dumps({"low_score_threshold": 3.0, "red_team_count_threshold": 3}), encoding="utf-8"
    )
    (root / ".gzkit").mkdir()
    event = {
        "event": "adr-evaluation",
        "id": SUBJECT,
        "dimensions": {"clarity": 1.0},
        "red_team_challenges_fired": [],
        "timestamp": _EVALUATED_AT.isoformat(),
        "ts": _EVALUATED_AT.isoformat(),
    }
    (root / ".gzkit" / "ledger.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")
    (root / "artifacts" / "justify").mkdir(parents=True)
    return root


def build_present_but_false_evidence() -> Path:
    """Plant every present-but-false form of evidence for :data:`SUBJECT`, and nothing real."""
    root = _triggered_root("evaluation-justify-binding")
    justify = root / "artifacts" / "justify"
    after = datetime(2026, 1, 3, tzinfo=UTC)
    before = datetime(2026, 1, 1, tzinfo=UTC)
    (justify / "adr-0-0-88-empty.md").write_text("", encoding="utf-8")
    (justify / "adr-0-0-88-malformed.md").write_text("# Justify\n\nRationale.", encoding="utf-8")
    (justify / "adr-0-0-88-unfilled.md").write_text(
        _walkthrough("adr-0-0-88", generated_at=after, filled=False), encoding="utf-8"
    )
    (justify / "adr-0-0-88-other-subject.md").write_text(
        _walkthrough("adr-0-0-89", generated_at=after), encoding="utf-8"
    )
    (justify / "adr-0-0-88-predates.md").write_text(
        _walkthrough("adr-0-0-88", generated_at=before), encoding="utf-8"
    )
    (justify / "adr-0-0-88-directory.md").mkdir()
    # Complete and after the evaluation, each naming something other than the ADR:
    # a GHI, an OBPI under a different ADR, and an obpi anchor carrying the ADR's id.
    for name, anchor in (
        ("ghi", AnchorRef(kind="ghi", identifier="GHI-996", body=SUBJECT)),
        ("other-adr-obpi", AnchorRef(kind="obpi", identifier="OBPI-0.0.89-01", body="b")),
        ("cross-kind", AnchorRef(kind="obpi", identifier=SUBJECT, body="b")),
    ):
        (justify / f"adr-0-0-88-{name}.md").write_text(
            _walkthrough("", generated_at=after, anchor=anchor), encoding="utf-8"
        )
    return root


def build_qualifying_walkthrough() -> Path:
    """Plant one walkthrough the producer can write that answers the evaluation."""
    root = _triggered_root("evaluation-justify-binding-qualified")
    (root / "artifacts" / "justify" / "answer.md").write_text(
        _walkthrough("adr-0-0-88", generated_at=datetime(2026, 1, 3, tzinfo=UTC)),
        encoding="utf-8",
    )
    return root
