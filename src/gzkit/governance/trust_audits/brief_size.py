"""OBPI brief size scope (GHI #1196).

`docs/governance/GovZero/obpi-decomposition-matrix.md` § Refining Overlay says a
unit that fails a granularity principle "MUST be decomposed further", and § Step 4
says the rule is "enforced as a mechanics contract". The mechanics held only a
count of briefs per ADR: `BriefStructure` set minimums, no `gz validate` scope
measured one brief, and a run could append to its brief without limit. Measured
when this landed, `OBPI-0.35.0-15` had been authored at 33 KB against an 8 KB
template and had grown past 160 KB across nine review rounds.

This scope measures every **live** brief on five dimensions and fails closed on
any that exceeds its declared bound:

* `reqs`, `requirements`, `allowed_paths` and `contract_bytes` describe the brief
  as authored, so a brief born too large is refused before its run starts.
* `total_bytes` includes `## Evidence`, so a run that only appends to its brief
  is stopped as well.

The bounds ship in the package (`brief_size_bounds.json`) so an adopter gets the
rule without carrying gzkit's `data/`. A project may hold ceilings for briefs
that were already over a bound at cutover, in `data/brief_size_grandfather.json`;
a ceiling admits its own brief on its own dimension up to the recorded value and
nothing else. Terminal briefs are sealed records and are not measured, for the
reason `--brief-structure` gives.
"""

import json
import re
from importlib.resources import files
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.brief_structure import is_terminal_brief_status
from gzkit.governance.trust_audits.brief_reconcile import _find_obpi_briefs
from gzkit.governance.trust_audits.brief_structure import _declared_status
from gzkit.hooks.obpi import extract_allowed_paths, section_body
from gzkit.registries import RegistryError, load_registry, registry_path
from gzkit.triangle import REQ_ID_BODY_PLAIN

DIMENSIONS = ("reqs", "requirements", "allowed_paths", "contract_bytes", "total_bytes")

_TYPE = "brief_size"
_GRANDFATHER = "brief_size_grandfather.json"
_REQ_ID_RE = re.compile(REQ_ID_BODY_PLAIN)
_NUMBERED_ITEM_RE = re.compile(r"^\d+\.\s", re.MULTILINE)
_EVIDENCE_RE = re.compile(r"^## Evidence\s*$", re.MULTILINE)
_REMEDY = (
    "A brief past its bound is not one unit of work: "
    "docs/governance/GovZero/obpi-decomposition-matrix.md (Refining Overlay) requires it "
    "to be decomposed further, and the gates can only fire between briefs (GHI #1196). "
    "Split the brief under its parent ADR, or cut it back, then re-run "
    "`uv run gz validate --brief-size`."
)


def measure_brief(text: str) -> dict[str, int]:
    """Measure one brief on every dimension in ``DIMENSIONS``."""
    evidence = _EVIDENCE_RE.search(text)
    contract = text[: evidence.start()] if evidence else text
    return {
        "reqs": len(set(_REQ_ID_RE.findall(section_body(text, "Acceptance Criteria") or ""))),
        "requirements": len(
            _NUMBERED_ITEM_RE.findall(section_body(text, "Requirements (FAIL-CLOSED)") or "")
        ),
        "allowed_paths": len(set(extract_allowed_paths(text))),
        "contract_bytes": len(contract.encode("utf-8")),
        "total_bytes": len(text.encode("utf-8")),
    }


def load_bounds() -> dict[str, int]:
    """Return the packaged bound for each dimension."""
    payload = json.loads(files("gzkit").joinpath("brief_size_bounds.json").read_text("utf-8"))
    return {dimension: entry["max"] for dimension, entry in payload["bounds"].items()}


def load_ceilings(
    project_root: Path,
) -> tuple[dict[str, dict[str, int]], list[ValidationError]]:
    """Return the project's ceilings, or none and a finding when the file is unusable.

    Absence means the project grandfathers nothing. An unusable file admits
    nothing either, and says so: a ceiling file that cannot be read must never
    widen what passes.
    """
    path = registry_path(project_root, _GRANDFATHER)
    if not path.is_file():
        return {}, []
    artifact = path.relative_to(project_root).as_posix()
    try:
        payload = load_registry(project_root, _GRANDFATHER)
    except RegistryError as exc:
        return {}, [ValidationError(type=_TYPE, artifact=artifact, message=str(exc))]
    ceilings = payload.get("ceilings") if isinstance(payload, dict) else None
    well_formed = isinstance(ceilings, dict) and all(
        isinstance(entry, dict)
        and all(
            dimension in DIMENSIONS and isinstance(value, int) for dimension, value in entry.items()
        )
        for entry in ceilings.values()
    )
    if not well_formed:
        message = (
            f"{artifact} must be an object whose `ceilings` maps a brief id to "
            f"{{dimension: integer}} over {', '.join(DIMENSIONS)}. It is not, so no "
            "ceiling is honoured. Repair the file, then re-run "
            "`uv run gz validate --brief-size`."
        )
        return {}, [ValidationError(type=_TYPE, artifact=artifact, message=message)]
    return ceilings, []


def audit_brief_size(project_root: Path) -> list[ValidationError]:
    """Fail closed on every live brief that exceeds a bound on any dimension."""
    bounds = load_bounds()
    ceilings, errors = load_ceilings(project_root)
    for brief_path in _find_obpi_briefs(project_root):
        status = _declared_status(brief_path)
        if status and is_terminal_brief_status(status):
            continue
        artifact = brief_path.relative_to(project_root).as_posix()
        try:
            size = measure_brief(brief_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as exc:
            message = (
                f"{brief_path.name} could not be read as UTF-8 text ({exc}), so it cannot be "
                "measured, and an unmeasured live brief does not pass (GHI #1196). Restore "
                "the file, then re-run `uv run gz validate --brief-size`."
            )
            errors.append(ValidationError(type=_TYPE, artifact=artifact, message=message))
            continue
        own_ceilings = ceilings.get(brief_path.stem, {})
        for dimension in DIMENSIONS:
            ceiling = own_ceilings.get(dimension)
            limit = bounds[dimension] if ceiling is None else ceiling
            if size[dimension] <= limit:
                continue
            held = (
                f"its recorded ceiling of {limit} (the bound is {bounds[dimension]})"
                if ceiling is not None
                else f"the bound of {limit}"
            )
            errors.append(
                ValidationError(
                    type=_TYPE,
                    artifact=artifact,
                    field=dimension,
                    message=(
                        f"{brief_path.stem} measures {size[dimension]} on `{dimension}`, "
                        f"over {held}. {_REMEDY}"
                    ),
                )
            )
    return errors
