"""The pipeline skill's control inventory: its model and the pure, total checker.

OBPI-0.35.0-17 § Control Inventory Contract. The inventory is a complete partition
of the skill body into blocks; every meaningful character of every block lies inside
a control quote or a non-control quote. The checker is pure and total: given the
inventory, the baseline body, the text served per position and the rationale record,
it returns every violation, never only the first.

Block and coverage primitives are those OBPI-0.35.0-14 landed in
``gzkit.content.retention`` (brief 17, Allowed Paths, READ-ONLY import), so an
inventory and a retention map agree on what a block is and which characters count.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.content.retention import meaningful_positions, split_blocks
from gzkit.governance.trust_audits.config_derivation import PROVENANCE_KEYS
from gzkit.registries import load_registry

POSITIONS: tuple[str, ...] = ("invocation", "stage1", "stage2", "stage3", "stage4", "stage5")
REGISTRY_NAME = "obpi_pipeline_control_inventory.json"


class Reworded(BaseModel):
    """A declared rewording of a control's delivered span, with its reason."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str = Field(..., description="The delivered text in place of the baseline quote")
    reason: str = Field(..., description="Why the span differs from the quote")


class Control(BaseModel):
    """One statement that binds what the agent does."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="Row id, e.g. S4-017")
    quote: str = Field(..., description="Verbatim substring of the block text")
    applies_at: list[str] = Field(..., description="Positions the control applies at")
    cause: str | None = Field(None, description="GHI or ruling the skill cites")
    delivered_span: str = Field(..., description="Text delivered at every applies_at position")
    reworded: Reworded | None = Field(None, description="Declared rewording, else null")


class NonControl(BaseModel):
    """Text that binds nothing: rationale or structure."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    quote: str = Field(..., description="Verbatim substring of the block text")
    class_: Literal["rationale", "structure"] = Field(..., alias="class")
    explains: str | None = Field(None, description="Control id a rationale explains")
    reason: str = Field(..., description="Why it binds nothing")


class Block(BaseModel):
    """One baseline block with its controls and non-control quotes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str = Field(..., description="The block, verbatim")
    controls: list[Control] = Field(default_factory=list)
    non_control: list[NonControl] = Field(default_factory=list)


class Baseline(BaseModel):
    """The pinned baseline the inventory partitions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str = Field(..., description="Skill file path")
    commit: str = Field(..., description="Commit the baseline was read from")
    skill_version: str = Field(..., description="metadata.skill-version at that commit")
    body_sha256: str = Field(..., description="Digest of the body, frontmatter excluded")


class ControlInventory(BaseModel):
    """The complete inventory."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    baseline: Baseline
    extracted_by: str = Field(..., description="Reviewer agent identity")
    mapped_by: str = Field(..., description="Author agent identity")
    blocks: list[Block] = Field(default_factory=list)


class Violation(BaseModel):
    """One violation of the contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: str = Field(..., description="Violation kind")
    where: str = Field(..., description="Block index, control id or id@position")
    detail: str = Field(..., description="What was found")


def body_digest(body: str) -> str:
    """Return the SHA-256 of the body text."""
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def effective_span(control: Control) -> str:
    """Return the text a control delivers: its rewording when declared, else its span."""
    return control.reworded.text if control.reworded else control.delivered_span


def _coverage_violations(index: int, block: Block) -> list[Violation]:
    """Return the quote and coverage violations of one block."""
    text = block.text
    covered = bytearray(len(text))
    out: list[Violation] = []
    quotes = [c.quote for c in block.controls] + [n.quote for n in block.non_control]
    for quote in quotes:
        at = text.find(quote)
        if at < 0:
            out.append(
                Violation(kind="quote-not-substring", where=f"block {index}", detail=quote[:120])
            )
        else:
            covered[at : at + len(quote)] = b"\x01" * len(quote)
    uncovered = [pos for pos in meaningful_positions(text) if not covered[pos]]
    if uncovered:
        first, last = uncovered[0], uncovered[-1]
        out.append(
            Violation(kind="uncovered", where=f"block {index}", detail=text[first : last + 1][:120])
        )
    return out


def _row_violations(index: int, block: Block, seen: set[str], known: set[str]) -> list[Violation]:
    """Return the row-shape violations of one block's controls and non-controls."""
    out: list[Violation] = []
    for control in block.controls:
        if control.id in seen:
            out.append(
                Violation(kind="duplicate-control-id", where=control.id, detail=f"block {index}")
            )
        seen.add(control.id)
        if not control.applies_at:
            out.append(
                Violation(kind="empty-applies-at", where=control.id, detail=f"block {index}")
            )
        for position in control.applies_at:
            if position not in POSITIONS:
                out.append(
                    Violation(
                        kind="unknown-position",
                        where=f"{control.id}@{position}",
                        detail=f"block {index}",
                    )
                )
        expected = control.reworded.text if control.reworded else control.quote
        if control.delivered_span != expected:
            out.append(
                Violation(
                    kind="span-mismatch", where=control.id, detail=control.delivered_span[:120]
                )
            )
    for non in block.non_control:
        if non.class_ == "rationale" and non.explains not in known:
            out.append(
                Violation(kind="explains-unknown", where=f"block {index}", detail=str(non.explains))
            )
    return out


def check_before_state(inventory: ControlInventory, body: str) -> list[Violation]:
    """Return every before-state violation: digest, partition, coverage, row shape."""
    out: list[Violation] = []
    if body_digest(body) != inventory.baseline.body_sha256:
        out.append(
            Violation(
                kind="digest-mismatch", where="baseline", detail=inventory.baseline.body_sha256
            )
        )
    expected = split_blocks(body)
    actual = [block.text for block in inventory.blocks]
    if actual != expected:
        first = next(
            (i for i, (a, b) in enumerate(zip(actual, expected, strict=False)) if a != b),
            min(len(actual), len(expected)),
        )
        out.append(
            Violation(
                kind="blocks-differ",
                where=f"block {first}",
                detail=f"{len(actual)} blocks against {len(expected)} in the body",
            )
        )
    known = {control.id for block in inventory.blocks for control in block.controls}
    seen: set[str] = set()
    for index, block in enumerate(inventory.blocks):
        out.extend(_coverage_violations(index, block))
        out.extend(_row_violations(index, block, seen, known))
    return out


def check_delivery(inventory: ControlInventory, served: dict[str, str]) -> list[Violation]:
    """Return every control whose span is not delivered at a position it applies at."""
    out: list[Violation] = []
    for block in inventory.blocks:
        for control in block.controls:
            span = effective_span(control)
            for position in control.applies_at:
                if position not in served:
                    out.append(
                        Violation(
                            kind="position-not-served",
                            where=f"{control.id}@{position}",
                            detail=span[:120],
                        )
                    )
                elif span not in served[position]:
                    out.append(
                        Violation(
                            kind="not-delivered",
                            where=f"{control.id}@{position}",
                            detail=span[:120],
                        )
                    )
    return out


def check_placement(inventory: ControlInventory, invocation_text: str) -> list[Violation]:
    """Return every stage control whose span sits in the invocation text."""
    out: list[Violation] = []
    for block in inventory.blocks:
        for control in block.controls:
            if (
                "invocation" not in control.applies_at
                and effective_span(control) in invocation_text
            ):
                out.append(
                    Violation(
                        kind="misplaced",
                        where=f"{control.id}@invocation",
                        detail=effective_span(control)[:120],
                    )
                )
    return out


def _record_sections(record_text: str) -> dict[str, str]:
    """Split a rationale record into sections keyed by the control id its heading names."""
    sections: dict[str, str] = {}
    current: str | None = None
    for line in record_text.splitlines():
        if line.startswith("#"):
            current = line.lstrip("#").strip()
            sections.setdefault(current, "")
        elif current is not None:
            sections[current] += line + "\n"
    return sections


def check_rationale_record(inventory: ControlInventory, record_text: str) -> list[Violation]:
    """Return every rationale quote absent from the record under its control id."""
    sections = _record_sections(record_text)
    out: list[Violation] = []
    for block in inventory.blocks:
        for non in block.non_control:
            if non.class_ != "rationale":
                continue
            home = next(
                (body for key, body in sections.items() if non.explains and non.explains in key),
                None,
            )
            if home is None or non.quote not in home:
                out.append(
                    Violation(
                        kind="rationale-missing", where=str(non.explains), detail=non.quote[:120]
                    )
                )
    return out


def read_skill_body(project_root: Path, inventory: ControlInventory) -> str:
    """Return the pinned skill's body, frontmatter excluded, as the digest is taken."""
    text = (project_root / inventory.baseline.path).read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    return text if end is None else "".join(lines[end + 1 :])


def load_inventory(project_root: Path) -> ControlInventory:
    """Load the committed inventory through the registry seam."""
    payload = load_registry(project_root, REGISTRY_NAME)
    data = {key: value for key, value in payload.items() if key not in PROVENANCE_KEYS}
    return ControlInventory.model_validate(data)
