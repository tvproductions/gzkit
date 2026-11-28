"""Every relative link in a canonical skill, rule, chore, persona or agent file resolves.

GHI #1379. Three skill links were written one level short (`../../docs/…` from
`.gzkit/skills/<name>/SKILL.md`, which lands in `.gzkit/`), and nothing resolved skill
links: the pointer-integrity validator reads `> See [...]` blockquotes in the root
contracts and `.claude/rules/**` only (REQ-0.0.33-03-04), and the docs build does not
build skills.

The scope reads every `.md` file under `.gzkit/skills`, `.gzkit/rules`, `.gzkit/chores`,
`.gzkit/personas` and `.gzkit/agents`, skipping any path through a `proofs` or `archive`
directory (dated evidence, often copies written for another path) and every `AGENTS.md`,
which is generated; its links are tracked under #1380. It drops fenced code blocks and, per
line, single-backtick inline code spans, then resolves each inline `[text](target)` whose
target holds no whitespace or parenthesis, has no URL scheme and does not start with `#` or
`<`. The part before any `#` is resolved against the linking file's directory, as a
Markdown viewer would, and a target that does not exist on disk is refused. It does not
check anchors, titled links (`[x](path "t")`), angle-bracket targets, reference-style links
(`[x]: path`) or HTML links. A link that resolves here may still break from the package
copy under `src/gzkit/skills/<name>/`, one level deeper; that copy is a byte-identical
payload, not a place a reader opens.

The links name gzkit's own tree, so the scope reads nothing in an adopter project: the
canon gzkit delivers there links to `docs/` paths an adopter never has, which is #1138's
defect, not this scope's.

It began as the unit test `tests/policy/test_canon_relative_links_resolve.py`, which the
tautology audit classed as a content echo; under the operator's ruling on #1370 ("A") it
is this scope, with its link reading unchanged.
"""

import re
from typing import TYPE_CHECKING

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.prose_fence import live_files, missing_roots
from gzkit.rules import is_framework_tree

if TYPE_CHECKING:
    from pathlib import Path

_TYPE = "canon_relative_links"
_PREFIX = "[canon-relative-links]"
_SCOPE = "canon-relative-links"

ROOTS = (".gzkit/skills", ".gzkit/rules", ".gzkit/chores", ".gzkit/personas", ".gzkit/agents")
SKIPPED_PARTS = ("proofs", "archive")

_FENCE = re.compile(r"^\s*(```|~~~)")
_INLINE_CODE = re.compile(r"`[^`]*`")
_LINK = re.compile(r"\]\(([^()\s]+)\)")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def unresolved_links(path: Path, text: str) -> list[str]:
    """Return each relative link target in *text* that does not resolve from *path*'s directory."""
    found: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in _LINK.finditer(_INLINE_CODE.sub("", line)):
            target = match.group(1)
            if _SCHEME.match(target) or target.startswith(("#", "<")):
                continue
            relative = target.split("#", 1)[0]
            if relative and not (path.parent / relative).exists():
                found.append(target)
    return found


_RECOVERY = (
    "links to {target!r}, which does not resolve from the linking file's directory; from "
    ".gzkit/skills/<name>/ the repo root is ../../../ (GHI #1379). Correct the path, then "
    "re-run `uv run gz validate --{scope}`."
)


def audit_canon_relative_links(project_root: Path) -> list[ValidationError]:
    """Fail closed on a relative link in canon that does not resolve.

    Returns:
        One finding per unresolved link, plus one per declared root absent from
        gzkit's tree; nothing in an adopter project.

    """
    if not is_framework_tree(project_root):
        return []
    errors = missing_roots(project_root, ROOTS, error_type=_TYPE, prefix=_PREFIX, scope=_SCOPE)
    paths = [
        path
        for path in live_files(project_root, ROOTS, suffixes=(".md",), skip_parts=SKIPPED_PARTS)
        if path.name != "AGENTS.md"
    ]
    for path in paths:
        rel = path.relative_to(project_root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        errors.extend(
            ValidationError(
                type=_TYPE,
                artifact=rel,
                message=f"{_PREFIX} {rel} {_RECOVERY.format(target=target, scope=_SCOPE)}",
            )
            for target in unresolved_links(path, text)
        )
    return errors
