"""Resolve the procedure the runtime serves at each pipeline stage entry (OBPI-0.35.0-17).

Brief 17's rulings: the per-stage procedures are Markdown files inside the skill
package (Q1, operator: "A"), and stage entry prints a path and a digest rather
than the text (Q3, operator: "A"), because the harness truncates long hook
output; the agent reads the file. Delivery fails closed when a procedure is
missing, unreadable, empty or not the bytes the runtime expects (Requirement 7).

The expected bytes are pinned here, in code, so the runtime carries its own
expectation and a project that lacks the files refuses stage entry instead of
entering a stage on no text. The files are canon under
``.gzkit/skills/gz-obpi-pipeline/references/``; the wheel copy under
``gzkit.skills`` is what ``gz init`` and :func:`seed_stage_procedures` deliver.
"""

from __future__ import annotations

import hashlib
from importlib.resources import files
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.core.exceptions import GzkitError

SKILL_SLUG = "gz-obpi-pipeline"
REFERENCES_DIR = Path(".gzkit") / "skills" / SKILL_SLUG / "references"


class StageProcedure(BaseModel):
    """One stage's served procedure: its file in the skill package and the bytes expected."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str = Field(..., description="Position key, e.g. stage3")
    number: int = Field(..., description="Stage number")
    label: str = Field(..., description="Stage label")
    filename: str = Field(..., description="File under the skill's references directory")
    sha256: str = Field(..., description="Digest of the file bytes the runtime expects")


class ProcedurePointer(BaseModel):
    """What stage entry prints: the path to read and the digest it carries."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str
    number: int
    label: str
    path: str = Field(..., description="Project-relative posix path")
    sha256: str


class ProcedureUnavailable(GzkitError):
    """A stage's procedure is missing, unreadable, empty or not the expected bytes."""


#: The served procedures and the bytes the runtime expects for each. Regenerated
#: from ``data/obpi_pipeline_control_inventory.json`` whenever the attested
#: baseline changes; ``tests/test_pipeline_procedure.py`` holds the pins to the files.
STAGE_PROCEDURES: tuple[StageProcedure, ...] = (
    StageProcedure(
        key="stage1",
        number=1,
        label="Load Context",
        filename="stage-1-load-context.md",
        sha256="196aac77cf76efbfbff2d96430414cd20c0ef33523fd8c7a7a592703421012b9",
    ),
    StageProcedure(
        key="stage2",
        number=2,
        label="Implement",
        filename="stage-2-implement.md",
        sha256="4c1d52df1115df8bec346124d7bf5a9c8e37cbd06865926b800d2f6eaab652bc",
    ),
    StageProcedure(
        key="stage3",
        number=3,
        label="Verify",
        filename="stage-3-verify.md",
        sha256="d10035a5e84525724026c59bea5f9f7ee3928e6fd36b22fccb1ee22d558714c5",
    ),
    StageProcedure(
        key="stage4",
        number=4,
        label="Present Evidence",
        filename="stage-4-present-evidence.md",
        sha256="be95b14d99a3a04305c8309531e39354df6e00073d9c5ee9999882cf56aa907f",
    ),
    StageProcedure(
        key="stage5",
        number=5,
        label="Sync And Account",
        filename="stage-5-sync-and-account.md",
        sha256="9a8e18ad4b917d0c53db67b9d4f1e709161638977345b9953d931aca69302edb",
    ),
)

_LAUNCH_STAGES: dict[str | None, tuple[int, ...]] = {
    None: (1, 2, 3, 4, 5),
    "verify": (1, 3, 4, 5),
    "ceremony": (1, 4, 5),
    "sync": (1, 5),
}


def stages_for_launch(start_from: str | None) -> list[str]:
    """Return the position keys a launch visits, Stage 1 first (Stage 1 always runs)."""
    return [f"stage{number}" for number in _LAUNCH_STAGES.get(start_from, (1, 2, 3, 4, 5))]


def _procedure_for(key: str) -> StageProcedure | None:
    return next((procedure for procedure in STAGE_PROCEDURES if procedure.key == key), None)


def _unavailable(label: str, what_failed: str, rel: str) -> ProcedureUnavailable:
    return ProcedureUnavailable(
        f"{label} procedure unavailable: {what_failed}.\n"
        "WHY: the runtime serves each stage's procedure at stage entry and refuses the "
        "stage when it cannot (OBPI-0.35.0-17, Requirement 7); a stage entered without "
        "its procedure would run on no text or on the wrong text.\n"
        f"NEXT STEP: restore {rel} from the skill package with "
        "`uv run gz agent sync control-surfaces` (or `uv run gz init` in a fresh "
        "project), then re-run `uv run gz obpi pipeline <OBPI-ID> [--from=<stage>]`."
    )


def resolve_stage_procedure(project_root: Path, key: str) -> ProcedurePointer:
    """Return the pointer for a stage, or raise ProcedureUnavailable with recovery prose."""
    procedure = _procedure_for(key)
    if procedure is None:
        known = ", ".join(p.key for p in STAGE_PROCEDURES)
        raise _unavailable("Stage", f"no served procedure is keyed {key!r} (known: {known})", "it")
    rel = (REFERENCES_DIR / procedure.filename).as_posix()
    label = f"Stage {procedure.number}"
    path = project_root / REFERENCES_DIR / procedure.filename
    if not path.is_file():
        raise _unavailable(label, f"{rel} is missing", rel)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise _unavailable(label, f"{rel} is unreadable ({exc})", rel) from exc
    if not data.strip():
        raise _unavailable(label, f"{rel} is empty", rel)
    digest = hashlib.sha256(data).hexdigest()
    if digest != procedure.sha256:
        raise _unavailable(
            label,
            f"{rel} carries sha256 {digest}, not the expected {procedure.sha256}",
            rel,
        )
    return ProcedurePointer(
        key=procedure.key,
        number=procedure.number,
        label=procedure.label,
        path=rel,
        sha256=digest,
    )


def resolve_launch_procedures(
    project_root: Path, start_from: str | None
) -> dict[str, ProcedurePointer]:
    """Resolve every stage a launch visits, Stage 1 first, before anything is written.

    A launch whose later stage lacks its procedure is refused here, at the start,
    rather than after markers and ledger rows exist (OBPI-0.35.0-17, Requirement 7).
    """
    return {
        key: resolve_stage_procedure(project_root, key) for key in stages_for_launch(start_from)
    }


def render_pointer(pointer: ProcedurePointer) -> str:
    """Render the line stage entry prints: the path to read and the digest it carries."""
    return (
        f"Stage {pointer.number} procedure: {pointer.path} (sha256 {pointer.sha256}) "
        "— read it before acting in this stage."
    )


def served_texts(project_root: Path) -> dict[str, str]:
    """Return the served text per stage key, as the inventory checker consumes it."""
    return {
        procedure.key: (project_root / REFERENCES_DIR / procedure.filename).read_text(
            encoding="utf-8"
        )
        for procedure in STAGE_PROCEDURES
    }


def seed_stage_procedures(project_root: Path) -> list[Path]:
    """Copy the stage files from the installed skill package into ``project_root``.

    This is what ``gz init`` delivers for a real project; the test scaffold calls
    it so a seeded project carries the procedures the runtime refuses to run
    without.
    """
    package = files("gzkit.skills") / SKILL_SLUG / "references"
    target = project_root / REFERENCES_DIR
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for procedure in STAGE_PROCEDURES:
        destination = target / procedure.filename
        destination.write_bytes((package / procedure.filename).read_bytes())
        written.append(destination)
    return written
