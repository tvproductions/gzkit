"""gz-how catalog coverage audit (GHI #1106).

`gz validate --how-coverage` holds the `gz-how` flow guide to the catalog it
describes. The skill it replaced, `gz-skill-router`, carried a "must be updated
when skills are added" duty and no gate, and fell 36 skills behind a 73-skill
catalog. Four properties, each a policy breach:

1. every active skill appears in the hub's catalog under a flow, or in its
   "Not in the catalog" list with a reason;
2. every skill the hub or a flow file names exists and is not retired;
3. every `references/*.md` link in the hub resolves;
4. every flow file under `references/` is linked from the hub.

The catalog's shape is parsed, not searched: a row or exclusion that does not
parse is itself a finding, so the format cannot drift out from under the check.
A project whose catalog has no `gz-how` is skipped.
"""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.validate import ValidationError

_SKILLS_DIR = Path(".gzkit") / "skills"
_HOW_SLUG = "gz-how"
_CATALOG_HEADING = "## What can I do? (catalog)"
_EXCLUDED_HEADING = "### Not in the catalog"

_ROW = re.compile(r"^\|\s*([^|`]+?)\s*\|\s*`([a-z0-9][a-z0-9-]*)`\s*\|\s*$")
_TABLE_FRAME = re.compile(r"^\|\s*(Intent\s*\|\s*Skill|-+\s*\|\s*-+)\s*\|\s*$")
_EXCLUDED = re.compile(r"^- `([a-z0-9][a-z0-9-]*)` — (\S.*)$")
_SKILL_TOKEN = re.compile(r"`((?:gz|ghi)-[a-z0-9-]+|git-sync|airlineops-[a-z0-9-]+)`")
_FLOW_LINK = re.compile(r"\]\((references/[^)#\s]+\.md)\)")
_LIFECYCLE = re.compile(r"^lifecycle_state:\s*(\S+)", re.MULTILINE)


class HowCatalogEntry(BaseModel):
    """One skill's place in the gz-how catalog."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    skill: str = Field(..., min_length=1, description="Skill slug the row names")
    flow: str = Field(..., min_length=1, description="Flow heading the row sits under")
    excluded_reason: str | None = Field(None, description="Why the skill has no catalog row")


def _live_skills(project_root: Path) -> set[str]:
    """Return slugs with a canonical SKILL.md whose lifecycle is not retired."""
    root = project_root / _SKILLS_DIR
    live: set[str] = set()
    for skill_md in root.glob("*/SKILL.md"):
        state = _LIFECYCLE.search(skill_md.read_text(encoding="utf-8"))
        if state is None or state.group(1).strip("\"'") != "retired":
            live.add(skill_md.parent.name)
    return live


def _catalog_section(hub: str) -> list[str]:
    """Return the lines of the catalog section, up to the next H2."""
    start = hub.find(_CATALOG_HEADING)
    if start == -1:
        return []
    body = hub[start + len(_CATALOG_HEADING) :]
    end = re.search(r"^## ", body, re.MULTILINE)
    return (body[: end.start()] if end else body).splitlines()


def _error(artifact: str, field: str, message: str) -> ValidationError:
    return ValidationError(type="how_coverage", artifact=artifact, field=field, message=message)


def _parse_catalog(hub: str, artifact: str) -> tuple[list[HowCatalogEntry], list[ValidationError]]:
    """Parse the catalog's rows and exclusions; an unparseable line is a finding."""
    entries: list[HowCatalogEntry] = []
    errors: list[ValidationError] = []
    flow = ""
    for line in _catalog_section(hub):
        stripped = line.strip()
        if stripped.startswith("### "):
            flow = stripped.removeprefix("### ").strip()
        elif stripped.startswith("|") and not _TABLE_FRAME.match(stripped):
            row = _ROW.match(stripped)
            if row is None or not flow:
                errors.append(_error(artifact, "unparseable_row", _unparseable(stripped)))
            else:
                entries.append(HowCatalogEntry(skill=row.group(2), flow=flow))
        elif stripped.startswith("- ") and flow == _EXCLUDED_HEADING.removeprefix("### "):
            excluded = _EXCLUDED.match(stripped)
            if excluded is None:
                errors.append(_error(artifact, "unparseable_row", _unparseable(stripped)))
            else:
                entries.append(
                    HowCatalogEntry(
                        skill=excluded.group(1), flow=flow, excluded_reason=excluded.group(2)
                    )
                )
    return entries, errors


def _unparseable(line: str) -> str:
    return (
        f"gz-how catalog line does not parse: {line!r}. A row reads "
        "`| <intent> | `<skill>` |` under a `### <flow>` heading; an exclusion reads "
        "`- `<skill>` — <reason>` under `### Not in the catalog`."
    )


def _named_skill_errors(how_dir: Path, project_root: Path, live: set[str]) -> list[ValidationError]:
    """Flag every skill the hub or a flow file names that does not exist or is retired."""
    errors: list[ValidationError] = []
    for path in [how_dir / "SKILL.md", *sorted((how_dir / "references").glob("*.md"))]:
        artifact = path.relative_to(project_root).as_posix()
        for slug in sorted(set(_SKILL_TOKEN.findall(path.read_text(encoding="utf-8")))):
            if slug not in live:
                errors.append(
                    _error(
                        artifact,
                        "unknown_skill",
                        f"{artifact} names `{slug}`, which has no live skill under "
                        f".gzkit/skills/. Repoint it to the skill that does the job, or "
                        f"remove it.",
                    )
                )
    return errors


def _flow_link_errors(how_dir: Path, hub: str, project_root: Path) -> list[ValidationError]:
    """Flag hub links to missing flow files, and flow files the hub never links."""
    errors: list[ValidationError] = []
    linked = set(_FLOW_LINK.findall(hub))
    hub_artifact = (how_dir / "SKILL.md").relative_to(project_root).as_posix()
    for target in sorted(linked):
        if not (how_dir / target).is_file():
            errors.append(
                _error(
                    hub_artifact,
                    "dead_link",
                    f"{hub_artifact} links {target}, which does not exist.",
                )
            )
    for flow_file in sorted((how_dir / "references").glob("*.md")):
        rel = flow_file.relative_to(how_dir).as_posix()
        if rel not in linked:
            errors.append(
                _error(
                    flow_file.relative_to(project_root).as_posix(),
                    "orphan_flow",
                    f"{rel} is not linked from {hub_artifact}; link it from the question "
                    "index or delete it.",
                )
            )
    return errors


def audit_how_coverage(project_root: Path) -> list[ValidationError]:
    """Hold the gz-how guide to the live skill catalog; see the module docstring."""
    how_dir = project_root / _SKILLS_DIR / _HOW_SLUG
    hub_path = how_dir / "SKILL.md"
    if not hub_path.is_file():
        return []
    hub = hub_path.read_text(encoding="utf-8")
    hub_artifact = hub_path.relative_to(project_root).as_posix()
    live = _live_skills(project_root)

    entries, errors = _parse_catalog(hub, hub_artifact)
    catalogued = {entry.skill for entry in entries}
    for slug in sorted(live - catalogued):
        errors.append(
            _error(
                hub_artifact,
                "uncatalogued",
                f"skill `{slug}` is active but absent from the gz-how catalog. Add a row "
                f"under the flow it belongs to, or list it under "
                f"'{_EXCLUDED_HEADING.removeprefix('### ')}' with a reason.",
            )
        )
    errors.extend(_named_skill_errors(how_dir, project_root, live))
    errors.extend(_flow_link_errors(how_dir, hub, project_root))
    return errors
