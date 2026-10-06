"""BDD steps for classification ownership in gz validate --bullet-retention — OBPI-0.35.0-10.

Fixture shape mirrors `tests/governance/test_bullet_retention.py`: a two-section
control surface (one section the ownership declaration marks corpus-owned, one it
marks unowned), an ownership declaration backed by a real ledger genesis event,
one corpus entry for the owned section, a scorecard whose rows name their
source in the Notes column, and the pinned row identities of that scorecard.

@covers REQ-0.35.0-10-01
@covers REQ-0.35.0-10-02
@covers REQ-0.35.0-10-03
@covers REQ-0.35.0-10-04
@covers REQ-0.35.0-10-08
@covers REQ-0.35.0-10-09
"""

from __future__ import annotations

import json
from pathlib import Path

from behave import given

from gzkit.content.corpus_store import append_entry
from gzkit.content.models import CorpusEntry
from gzkit.content.ownership import declaration_path, sections_digest
from gzkit.governance.events import emit_section_ownership_genesis

_SURFACE = "AGENTS.md"
_OWNED_RULE = "owned rule alpha must hold"
_SKILL_RULE = "skill rule zeta must hold"
_SKILL_SOURCE = ".gzkit/skills/demo/SKILL.md"
#: The owned section's body deliberately omits the owned rule, so an enforced
#: classification is a retention violation and an unenforced one is clean.
_OWNED_CHUNK = "## Owned Section\n\n"
_UNOWNED_CHUNK = "## Unowned Section\nHand-authored prose nobody claims.\n"
_SECTIONS = {"owned-section": "corpus-owned", "unowned-section": "unowned"}
_SCORECARD_HEAD = (
    "### Fixture Contract\n\n| # | Rule | Score | Notes |\n|---|------|-------|-------|\n"
)
_SCORECARD_SECTION = "fixture-contract"

#: The "I run \"{command}\"" @when and the "the command exits 0" / "the command
#: exits non-zero" / "the output includes" @then steps are deliberately NOT
#: redefined here — `obpi_lock_steps.py`, `content_compose_steps.py` and
#: `gz_steps.py` already register those step texts, and behave's registry is
#: global across all loaded step modules.


def _scorecard_path(context) -> Path:
    return context.root / "docs" / "governance" / "advisory-rules-audit.md"


def _pin(context, *numbers: str) -> None:
    """Commit the identities of scorecard rows *numbers* as the project's pinned set."""
    path = context.root / "data" / "advisory_scorecard_identities.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    identities = [f"{_SCORECARD_SECTION} #{number}" for number in numbers]
    path.write_text(json.dumps({"identities": identities}), encoding="utf-8")


@given("a project whose control surface has one corpus-owned section")
def step_enrolled_project(context) -> None:
    root = Path.cwd()
    (root / ".gzkit").mkdir(exist_ok=True)
    (root / _SURFACE).write_text(_OWNED_CHUNK + _UNOWNED_CHUNK, encoding="utf-8")
    (root / "CLAUDE.md").write_text("", encoding="utf-8")
    floor = len(_UNOWNED_CHUNK.encode("utf-8"))
    digest = sections_digest(_SECTIONS)
    event_id = f"section-ownership-genesis-{_SURFACE}-{digest[:12]}"
    emit_section_ownership_genesis(root, event_id, _SURFACE, digest, floor)
    declaration_path(root, _SURFACE).parent.mkdir(parents=True, exist_ok=True)
    declaration_path(root, _SURFACE).write_text(
        json.dumps(
            {
                "surface": _SURFACE,
                "sections": _SECTIONS,
                "unowned_byte_floor": floor,
                "measured_at": "2026-10-03T00:00:00Z",
                "floor_event_id": event_id,
            }
        ),
        encoding="utf-8",
    )
    context.root = root
    context.exit_code = None
    context.output = ""


@given('the owned corpus entry is classified "{classification}"')
def step_owned_entry(context, classification: str) -> None:
    append_entry(
        context.root,
        _SURFACE,
        CorpusEntry(
            id="e-owned",
            surface=_SURFACE,
            section="owned-section",
            tier="invariant",
            classification=classification,
            text=_OWNED_RULE,
            origin="bdd-test",
            ts="2026-10-03T00:00:00+00:00",
        ),
    )


@given('the scorecard scores the owned bullet "{score}"')
def step_scorecard_owned_row(context, score: str) -> None:
    path = _scorecard_path(context)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"{_SCORECARD_HEAD}| 1 | {_OWNED_RULE} | **{score}** | "
        f"`source={_SURFACE}#owned-section entry=e-owned` |\n",
        encoding="utf-8",
    )
    _pin(context, "1")


def _add_skill_row(context, skill_text: str) -> None:
    path = _scorecard_path(context)
    row = f"| 2 | {_SKILL_RULE} | **Mechanical** | `source={_SKILL_SOURCE}` |\n"
    path.write_text(path.read_text(encoding="utf-8") + row, encoding="utf-8")
    _pin(context, "1", "2")
    skill = context.root / _SKILL_SOURCE
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text(skill_text, encoding="utf-8")


@given("a Mechanical scorecard row attributed to a skill file that carries its text")
def step_skill_row_retained(context) -> None:
    _add_skill_row(context, f"- {_SKILL_RULE}\n")


@given("a Mechanical scorecard row attributed to a skill file that lacks its text")
def step_skill_row_absent(context) -> None:
    _add_skill_row(context, "The skill says something else.\n")


@given("the pinned identities list a row the scorecard no longer carries")
def step_pinned_row_gone(context) -> None:
    _pin(context, "1", "2")


@given("the scorecard file is removed")
def step_scorecard_removed(context) -> None:
    _scorecard_path(context).unlink()
