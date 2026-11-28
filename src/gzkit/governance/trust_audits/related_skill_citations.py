"""Every skill a `## Related Skills` section names is a live canonical skill (GHI #1381).

The `lint`, `test` and `format` skills were retired into `gz-check` on 2026-04-03 and
their tombstones deleted under GHI #464, yet `git-sync` kept listing all three as
related skills, in canon and in the packaged template `gz init` delivers. Nothing
resolved a related-skill name, so a retirement left every consumer pointing at nothing.

The scope reads the `## Related Skills` section of every canonical skill
(`.gzkit/skills/*/SKILL.md`) and every packaged template skill
(`src/gzkit/templates/skills/*/SKILL.md`), matching the heading in any letter case, from
the heading to the next `## ` heading. The entries it reads are the skill-shaped names
(lowercase letters, digits and hyphens, an optional leading `/`, backticked or bare,
bold or not) that open a `-` or `*` list item, and the names in a table row's first cell,
where `/` may join several. A list item's description and a table's later cells are not
read, since they name other things too (a debt class, a command). Every other non-blank
line in the section, except a table's header row and separator, is refused as unread, so
an entry shape the reader does not know (an ordered item, a link) fails rather than
passing unchecked. Each name must be a live skill as `gzkit.skills.list_skills` reads
them: a directory under the configured skills path holding a `SKILL.md` whose
`lifecycle_state` is not `retired`. A skill named outside that
section, and any other `## Related …` heading, is not read. The vendor mirrors and
`src/gzkit/skills/` copy canon and are not read again.

It began as the unit test `tests/policy/test_related_skills_resolve.py`, which the
tautology audit classed as a content echo; under the operator's ruling on #1370 ("A") it
is this scope, with its section and entry patterns unchanged.
"""

import re
from typing import TYPE_CHECKING

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.prose_fence import missing_roots
from gzkit.skills import list_skills

if TYPE_CHECKING:
    from pathlib import Path

_TYPE = "related_skill_citations"
_PREFIX = "[related-skill-citations]"
_SCOPE = "related-skill-citations"

ROOTS = (".gzkit/skills", "src/gzkit/templates/skills")

_SECTION = re.compile(r"^## (?i:related skills)[ \t]*\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
_NAME = r"(?:\*\*)?`?/?([a-z][a-z0-9-]*)`?(?:\*\*)?"
_LIST_ENTRY = re.compile(rf"^\s*[-*]\s+{_NAME}(?=[\s,;:.]|$)")
_TABLE_NAME = re.compile(rf"^\s*{_NAME}\s*$")
_TABLE_SEPARATOR = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")


def _line_names(line: str) -> list[str]:
    if line.lstrip().startswith("|"):
        first_cell = line.strip().strip("|").split("|", 1)[0].replace("`/", "`")
        return [m.group(1) for part in first_cell.split("/") if (m := _TABLE_NAME.match(part))]
    match = _LIST_ENTRY.match(line)
    return [match.group(1)] if match else []


def _read_section(section: str) -> tuple[list[str], list[str]]:
    """Return the section's entry names and each non-blank line that yields none."""
    names: list[str] = []
    unread: list[str] = []
    lines = section.splitlines()
    for index, line in enumerate(lines):
        following = lines[index + 1] if index + 1 < len(lines) else ""
        if not line.strip() or _TABLE_SEPARATOR.match(line):
            continue
        if line.lstrip().startswith("|") and _TABLE_SEPARATOR.match(following):
            continue
        found = _line_names(line)
        names.extend(found)
        if not found:
            unread.append(line.strip())
    return names, unread


def _entry_names(section: str) -> list[str]:
    return _read_section(section)[0]


def unread_related_skills_lines(text: str) -> list[str]:
    """Return each line of *text*'s Related Skills section that yields no entry name."""
    match = _SECTION.search(text)
    return _read_section(match.group(1))[1] if match else []


def unresolved_related_skills(text: str, live: set[str]) -> list[str]:
    """Return each skill name in *text*'s Related Skills section that is not in *live*."""
    match = _SECTION.search(text)
    if match is None:
        return []
    return [name for name in _entry_names(match.group(1)) if name not in live]


_UNRESOLVED = (
    "names {name!r} under Related Skills, which is not a live skill: a retired skill's "
    "consumers move to its successor (GHI #1381). Name the live skill, then re-run "
    "`uv run gz validate --{scope}`."
)
_UNREAD = (
    "holds a Related Skills line the scope cannot read: {line!r}. A line opens with a "
    "skill name, as a `-` or `*` list item or a table row's first cell, so the name "
    "can be resolved (GHI #1381). Reshape it, then re-run `uv run gz validate --{scope}`."
)


def audit_related_skill_citations(project_root: Path) -> list[ValidationError]:
    """Fail closed on a Related Skills entry that names no live skill, or cannot be read.

    Returns:
        One finding per unresolved name and per unread line, plus one per declared
        root absent from gzkit's own tree.

    """
    errors = missing_roots(project_root, ROOTS, error_type=_TYPE, prefix=_PREFIX, scope=_SCOPE)
    live = {skill.name for skill in list_skills(project_root)}
    for rel in ROOTS:
        root = project_root / rel
        if not root.is_dir():
            continue
        for skill_file in sorted(root.glob("*/SKILL.md")):
            artifact = skill_file.relative_to(project_root).as_posix()
            text = skill_file.read_text(encoding="utf-8")
            messages = [
                _UNRESOLVED.format(name=name, scope=_SCOPE)
                for name in unresolved_related_skills(text, live)
            ]
            messages += [
                _UNREAD.format(line=line, scope=_SCOPE)
                for line in unread_related_skills_lines(text)
            ]
            errors.extend(
                ValidationError(type=_TYPE, artifact=artifact, message=f"{_PREFIX} {artifact} {m}")
                for m in messages
            )
    return errors
