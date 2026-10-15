"""Render the served set from the attested control inventory (OBPI-0.35.0-20).

The cutover brief rules that the skill body holds the invocation text only and
that each stage's procedure reaches the agent from the runtime at stage entry,
with every control in the attested inventory still delivered at every position
in its ``applies_at`` and nothing reworded (§ Decision item 13: "a change of
delivery, never a shortening"). This module is what makes that cutover a
function of the inventory rather than a hand edit: given the inventory it
renders the invocation body, one procedure per stage and the rationale record.

What leaves a block at a position:

- every passage the inventory classes ``rationale`` — it moves, verbatim, to
  the rationale record under the id of the control it explains (operator ruling
  Q2 "A", 2026-10-05), and the control it explains carries a pointer there;
- the span of every control that does not apply at that position, so that no
  stage control sits in the invocation text and no control sits in the
  procedure of a stage outside its ``applies_at`` (REQ-0.35.0-20-01).

What stays is verbatim. A block left without an applicable control, and the
headings, rules and table scaffolding left without content, are omitted. The
stage files are derived views of the inventory and are held to this render by
``tests/governance/test_pipeline_procedure_render.py``; the body is canon and is
held to the controls by the inventory checker.
"""

from __future__ import annotations

import itertools
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.governance.pipeline_control_inventory import (
    Block,
    ControlInventory,
    Violation,
    effective_span,
)
from gzkit.pipeline_procedure import STAGE_PROCEDURES, StageProcedure

RECORD_PATH = "docs/governance/obpi-pipeline-control-rationale.md"
INVOCATION = "invocation"
RENDER_TEST = "tests/governance/test_pipeline_procedure_render.py"

_STAGE_HEADING = re.compile(r"^### Stage (\d):")
_TABLE_SEPARATOR = re.compile(r"^\|?\s*:?-{3,}")

#: The one sentence of new text the cutover adds to the body (REQ-0.35.0-20-05).
SERVED_STATEMENT = (
    "**Each stage's procedure is served by the runtime at stage entry.** "
    "`uv run gz obpi pipeline <OBPI-ID>` prints `Stage N procedure: <path> (sha256 "
    "<digest>)` for Stage 1 and again for every stage it enters; read that file before "
    "acting in the stage. The five files live in `references/` beside this skill, "
    "`stage-1-load-context.md` through `stage-5-sync-and-account.md`, rendered from the "
    "attested control inventory (`data/obpi_pipeline_control_inventory.json`) with nothing "
    "reworded; this body keeps the controls that apply at invocation or at every stage. A "
    "stage file that is missing, empty or altered refuses the launch before any marker is "
    "written (OBPI-0.35.0-17, Requirement 7; cut over in OBPI-0.35.0-20)."
)


class RenderedSet(BaseModel):
    """The invocation body, one served text per stage key, and the rationale record."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    body: str = Field(..., description="Skill body after the frontmatter")
    stages: dict[str, str] = Field(..., description="Served procedure text per stage key")
    record: str = Field(..., description="The rationale record, keyed by control id")


def stage_ranges(inventory: ControlInventory) -> dict[str, range]:
    """Return each stage's own block range: its ``### Stage N:`` heading to the next section."""
    heads = [
        (index, f"stage{match.group(1)}")
        for index, block in enumerate(inventory.blocks)
        if (match := _STAGE_HEADING.match(block.text))
    ]
    if not heads:
        return {}
    blocks = inventory.blocks
    end = next(
        (i for i in range(heads[-1][0] + 1, len(blocks)) if blocks[i].text.startswith("## ")),
        len(blocks),
    )
    bounds = [index for index, _ in heads] + [end]
    return {key: range(bounds[n], bounds[n + 1]) for n, (_, key) in enumerate(heads)}


def _remove(text: str, quote: str) -> str:
    """Cut *quote* out of *text*, closing the gap with one newline or one space.

    No line is left with trailing whitespace: the pre-commit hook strips it,
    and a served file must be the bytes the runtime pins.
    """
    if quote not in text:
        msg = f"quote is not in the block: {quote[:60]!r}"
        raise ValueError(msg)
    before, after = text.split(quote, 1)
    before, after = before.rstrip(" "), after.lstrip(" ")
    if not before or not after:
        joined = (before + after).strip("\n")
    elif before.endswith("\n") and after.startswith("\n"):
        joined = before.rstrip("\n") + "\n" + after.lstrip("\n")
    elif before.endswith("\n") or after.startswith("\n"):
        joined = before + after
    else:
        joined = before + " " + after
    return "\n".join(line.rstrip() for line in joined.split("\n"))


def _is_scaffold(block: Block) -> bool:
    """Return True for a heading, a rule, or a table header or separator row classed structure."""
    text = block.text
    if block.controls:
        return False
    return (
        text.startswith("#")
        or text.strip() == "---"
        or (text.startswith("|") and all(n.class_ == "structure" for n in block.non_control))
    )


def _renders_at(block: Block, position: str) -> bool:
    """Return True when *block* holds text at *position*: an applicable control or structure."""
    if block.controls:
        return any(position in control.applies_at for control in block.controls)
    return any(non.class_ == "structure" for non in block.non_control)


def _delivered_text(block: Block, position: str) -> str:
    """Return *block* as delivered at *position*; only call it when the block renders there."""
    text = block.text
    for non in block.non_control:
        if non.class_ == "rationale":
            text = _remove(text, non.quote)
    for control in block.controls:
        if position not in control.applies_at:
            text = _remove(text, control.quote)
        elif control.reworded is not None:
            text = text.replace(control.quote, effective_span(control), 1)
    for control in block.controls:
        if position in control.applies_at and effective_span(control) not in text:
            msg = f"{control.id}: removing other text from its block loses its span at {position}"
            raise ValueError(msg)
    return text


def _rationale_ids(inventory: ControlInventory) -> dict[int, list[str]]:
    """Map each block index to the ids of its controls that a rationale passage explains."""
    holder = {
        control.id: index
        for index, block in enumerate(inventory.blocks)
        for control in block.controls
    }
    explained = {
        non.explains
        for block in inventory.blocks
        for non in block.non_control
        if non.class_ == "rationale" and non.explains
    }
    out: dict[int, list[str]] = {}
    for control_id, index in holder.items():
        if control_id in explained:
            out.setdefault(index, []).append(control_id)
    return out


def _pointer(ids: list[str]) -> str:
    return f"> Rationale: {RECORD_PATH} " + ", ".join(f"§ {control_id}" for control_id in ids)


class _Item(BaseModel):
    """One rendered block in a position's sequence, with what the pruner needs to know."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    index: int
    text: str
    scaffold: bool
    pointer_ids: list[str] = Field(default_factory=list)


def _render_block(
    inventory: ControlInventory, index: int, position: str, pointers: dict[int, list[str]]
) -> _Item:
    block = inventory.blocks[index]
    if _is_scaffold(block):
        return _Item(index=index, text=block.text, scaffold=True)
    ids = [
        control.id
        for control in block.controls
        if position in control.applies_at and control.id in pointers.get(index, [])
    ]
    return _Item(
        index=index, text=_delivered_text(block, position), scaffold=False, pointer_ids=ids
    )


def _heading_level(text: str) -> int:
    return len(text) - len(text.lstrip("#"))


def _is_heading_item(item: _Item) -> bool:
    return item.scaffold and item.text.startswith("#")


def _heading_introduces_content(items: list[_Item], n: int) -> bool:
    """Return True when the heading at *n* is followed by content before its next peer."""
    level = _heading_level(items[n].text)
    section = itertools.takewhile(
        lambda later: not (_is_heading_item(later) and _heading_level(later.text) <= level),
        items[n + 1 :],
    )
    return any(not later.scaffold for later in section)


def _table_scaffold_introduces_rows(items: list[_Item], n: int) -> bool:
    """Return True when the header or separator row at *n* is followed by a delivered row."""
    following = next(
        (later for later in items[n + 1 :] if not (later.scaffold and later.text.startswith("|"))),
        None,
    )
    return following is not None and not following.scaffold and following.text.startswith("|")


def _without_dangling_rules(kept: list[_Item]) -> list[_Item]:
    """Drop a horizontal rule that no longer sits between two other items."""
    out: list[_Item] = []
    for n, item in enumerate(kept):
        if item.scaffold and item.text.strip() == "---":
            has_before = bool(out) and out[-1].text.strip() != "---"
            has_after = any(later.text.strip() != "---" for later in kept[n + 1 :])
            if not (has_before and has_after):
                continue
        out.append(item)
    return out


def _prune(items: list[_Item]) -> list[_Item]:
    """Drop headings, table scaffolding and rules that introduce no content."""
    kept: list[_Item] = []
    for n, item in enumerate(items):
        if _is_heading_item(item) and not _heading_introduces_content(items, n):
            continue
        if (
            item.scaffold
            and item.text.startswith("|")
            and not _table_scaffold_introduces_rows(items, n)
        ):
            continue
        kept.append(item)
    return _without_dangling_rules(kept)


_LIST_MARKER = re.compile(r"^(?:[-*+]|\d+\.)\s")


def _tight(previous: str, current: str) -> bool:
    """Table rows and list items that follow one another sit on consecutive lines."""
    if previous.startswith("|") and current.startswith("|"):
        return True
    return bool(_LIST_MARKER.match(previous)) and bool(_LIST_MARKER.match(current))


def _emit(items: list[_Item]) -> list[str]:
    """Join rendered items into paragraphs, placing a table row's pointer after its table."""
    paragraphs: list[str] = []
    deferred: list[str] = []
    for item in items:
        is_row = item.text.startswith("|")
        if deferred and not is_row:
            paragraphs.append(_pointer(deferred))
            deferred = []
        if paragraphs and _tight(paragraphs[-1].splitlines()[-1], item.text):
            paragraphs[-1] = paragraphs[-1] + "\n" + item.text
        else:
            paragraphs.append(item.text)
        if item.pointer_ids and is_row:
            deferred.extend(item.pointer_ids)
        elif item.pointer_ids:
            paragraphs.append(_pointer(item.pointer_ids))
    if deferred:
        paragraphs.append(_pointer(deferred))
    return paragraphs


def _own_items(
    inventory: ControlInventory, indices: range | list[int], position: str, pointers
) -> list[_Item]:
    return [
        _render_block(inventory, index, position, pointers)
        for index in indices
        if _renders_at(inventory.blocks[index], position)
    ]


def _table_header_before(inventory: ControlInventory, index: int) -> list[_Item]:
    """Return the structure rows (header and separator) immediately above a table row."""
    header: list[_Item] = []
    back = index - 1
    while (
        back >= 0
        and _is_scaffold(inventory.blocks[back])
        and inventory.blocks[back].text.startswith("|")
    ):
        header.insert(0, _Item(index=back, text=inventory.blocks[back].text, scaffold=True))
        back -= 1
    return header


def _carried_items(inventory: ControlInventory, own: range, position: str, pointers) -> list[_Item]:
    """Blocks outside *own* with a control at *position*; a table row brings its header once."""
    items: list[_Item] = []
    previous_index = -2
    for index, block in enumerate(inventory.blocks):
        if index in own or not block.controls or not _renders_at(block, position):
            continue
        if block.text.startswith("|") and previous_index != index - 1:
            items.extend(_table_header_before(inventory, index))
        items.append(_render_block(inventory, index, position, pointers))
        previous_index = index
    return items


def render_body(inventory: ControlInventory) -> str:
    """Render the invocation text: blocks outside every stage section, invocation controls only."""
    ranges = stage_ranges(inventory)
    in_stage = {index for stage in ranges.values() for index in stage}
    pointers = _rationale_ids(inventory)
    indices = [index for index in range(len(inventory.blocks)) if index not in in_stage]
    items = _prune(_own_items(inventory, indices, INVOCATION, pointers))
    first_section = next(
        (n for n, item in enumerate(items) if item.scaffold and item.text.startswith("## ")),
        len(items),
    )
    statement = _Item(index=-1, text=SERVED_STATEMENT, scaffold=False)
    items = [*items[:first_section], statement, *items[first_section:]]
    return "\n\n".join(_emit(items)) + "\n"


def _stage_header(inventory: ControlInventory, procedure: StageProcedure) -> str:
    baseline = inventory.baseline
    return (
        f"<!-- Stage {procedure.number} procedure, served by the runtime at stage entry "
        "(OBPI-0.35.0-17; cut over in OBPI-0.35.0-20). Rendered from "
        "data/obpi_pipeline_control_inventory.json by gzkit.governance.pipeline_procedure_render: "
        "the stage's own section first, then every block from another section holding a control "
        f"whose applies_at names this stage. Every control is verbatim from the attested baseline "
        f"of {baseline.path} ({baseline.commit}, body sha256 {baseline.body_sha256}); passages the "
        f"inventory classes as rationale are in {RECORD_PATH} under the control they explain, and "
        "a control that applies elsewhere is left out of its block here. Nothing is reworded. Do "
        f"not edit by hand: {RENDER_TEST} holds this file to the render. -->"
    )


def render_stage(inventory: ControlInventory, procedure: StageProcedure) -> str:
    """Render one stage's served procedure: its own section, then the controls carried in."""
    own = stage_ranges(inventory)[procedure.key]
    pointers = _rationale_ids(inventory)
    parts = [
        _stage_header(inventory, procedure),
        f"# Stage {procedure.number}: {procedure.label} — served procedure",
        *_emit(_prune(_own_items(inventory, own, procedure.key, pointers))),
    ]
    carried = _carried_items(inventory, own, procedure.key, pointers)
    if carried:
        parts.append(f"## Controls carried into Stage {procedure.number} from other sections")
        parts.extend(_emit(carried))
    return "\n\n".join(parts) + "\n"


def _blockquote(text: str) -> str:
    """Quote *text* line by line, so a line of it that starts with # is not a heading."""
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())


def render_record(inventory: ControlInventory) -> str:
    """Render the rationale record: every rationale passage under the control it explains."""
    baseline = inventory.baseline
    quotes: dict[str, list[str]] = {}
    for block in inventory.blocks:
        for non in block.non_control:
            if non.class_ == "rationale" and non.explains:
                quotes.setdefault(non.explains, []).append(non.quote)
    parts = [
        "# OBPI pipeline control rationale",
        (
            '> Record, not rule (OBPI-0.35.0-20; operator ruling Q2 "A", 2026-10-05). Each '
            "section is keyed by the id of a control in "
            "`data/obpi_pipeline_control_inventory.json` "
            "and holds, verbatim, every passage of the attested baseline "
            f"(`{baseline.path}` at `{baseline.commit}`, skill {baseline.skill_version}, body "
            f"sha256 `{baseline.body_sha256}`) that the inventory classes as `rationale` "
            "explaining "
            "that control. The control binds where it is delivered: the skill body for a control "
            "that applies at invocation, the served stage procedure otherwise; each such control "
            "carries a pointer here. Nothing here binds and nothing here is reworded. "
            "`check_rationale_record` in `src/gzkit/governance/pipeline_control_inventory.py` "
            "holds this record to the inventory."
        ),
    ]
    for block in inventory.blocks:
        for control in block.controls:
            if control.id not in quotes:
                continue
            parts.append(f"## {control.id}")
            parts.append(f"**Control** (applies at: {', '.join(control.applies_at)}):")
            parts.append(_blockquote(control.quote))
            parts.append("**Rationale:**")
            parts.extend(quotes[control.id])
    return "\n\n".join(parts) + "\n"


def read_rationale_record(project_root: Path) -> str:
    """Return the rationale record's text, as the checker consumes it."""
    return (project_root / RECORD_PATH).read_text(encoding="utf-8")


def render_served_set(inventory: ControlInventory) -> RenderedSet:
    """Render the body, every stage procedure and the record from one inventory."""
    return RenderedSet(
        body=render_body(inventory),
        stages={
            p.key: render_stage(inventory, p)
            for p in STAGE_PROCEDURES
            if p.key in stage_ranges(inventory)
        },
        record=render_record(inventory),
    )


def check_stage_placement(inventory: ControlInventory, served: dict[str, str]) -> list[Violation]:
    """Return every control whose span sits in a served stage outside its ``applies_at``.

    A span that is part of a control delivered at that stage is not misplaced: two
    sections may state the same command, and each statement is its own control.
    The invocation text is ``check_placement``'s subject and is skipped here.
    """
    controls = [control for block in inventory.blocks for control in block.controls]
    out: list[Violation] = []
    for position, text in served.items():
        if position == INVOCATION:
            continue
        delivered = [effective_span(c) for c in controls if position in c.applies_at]
        foreign = [c for c in controls if position not in c.applies_at]
        for control in foreign:
            span = effective_span(control)
            if span in text and not any(span in home for home in delivered):
                out.append(
                    Violation(kind="misplaced", where=f"{control.id}@{position}", detail=span[:120])
                )
    return out
