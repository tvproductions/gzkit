"""The harness's identity and session variables are read in one place (GHI #1360).

GHI #484 corrected Claude Code's session variable in ``lock_manager`` while three
hooks kept their own copy of the read and kept the wrong variable, so every row
they wrote under Claude Code carried no session. A second copy of the read is the
failure mechanism, so this scope refuses one: outside ``lock_manager.py`` no file
under the scanned roots may hold a quoted literal of any of these names. Any read
spelled with a literal is caught that way, whatever its form (``getenv``, a wrapped
``environ.get``, ``in``, ``setdefault``, ``pop``, an alias), and so is a hook script
gzkit renders from a template string. A name assembled at run time is not caught.

The names are spelled here, so this module is the one other file allowed to hold
them, as the threshold table names its own numbers. The subject is gzkit's own
source, so the scope reads nothing in an adopter project, whose code may read the
harness variables however it likes; the copies gzkit delivers there are byte copies
of canon this scope already read on gzkit's tree.

It began as the unit test `tests/policy/test_harness_session_single_source.py`, which
the tautology audit classed as a content echo; under the operator's ruling on #1370
("A") it is this scope, with its roots, file patterns and literal pattern unchanged.
"""

import re
from typing import TYPE_CHECKING

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.prose_fence import missing_roots
from gzkit.rules import is_framework_tree

if TYPE_CHECKING:
    from pathlib import Path

_TYPE = "harness_session_single_source"
_PREFIX = "[harness-session-single-source]"
_SCOPE = "harness-session-single-source"

#: Each root and the files under it that can carry a read: Python modules, the
#: Jinja templates gzkit renders, the generated Claude hooks (a hand edit there
#: would otherwise go unseen until the next sync) and the extensionless git hooks.
ROOTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("src/gzkit", ("*.py", "*.j2")),
    ("scripts", ("*.py",)),
    (".gzkit/skills", ("*.py",)),
    (".gzkit/chores", ("*.py",)),
    (".gzkit/hooks", ("*",)),
    (".claude/hooks", ("*.py",)),
)
HOMES = (
    "src/gzkit/lock_manager.py",
    "src/gzkit/governance/trust_audits/harness_session_single_source.py",
)
HARNESS_VARIABLES = (
    "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_SESSION_ID",
    "COPILOT_SESSION_ID",
    "CLAUDECODE",
    "CLAUDE_CODE",
    "CODEX_SANDBOX",
)
# The closing quote may be escaped, as inside a template that writes a quoted name.
_LITERAL = re.compile(rf"""["'](?:{"|".join(HARNESS_VARIABLES)})\\?["']""")


_RECOVERY = (
    "holds a quoted harness identity or session variable outside gzkit.lock_manager, "
    "which is the one place they are read (GHI #1360; GHI #484 fixed one copy and left "
    "three). Read them through gzkit.lock_manager (resolve_agent, harness_session_id), "
    "then re-run `uv run gz validate --{scope}`."
)


def _scanned(project_root: Path) -> list[Path]:
    homes = {project_root / rel for rel in HOMES}
    found: set[Path] = set()
    for rel, patterns in ROOTS:
        root = project_root / rel
        if root.is_dir():
            found.update(p for pattern in patterns for p in root.rglob(pattern) if p.is_file())
    return sorted(
        path
        for path in found
        if path not in homes and path.suffix != ".md" and "__pycache__" not in path.parts
    )


def audit_harness_session_single_source(project_root: Path) -> list[ValidationError]:
    """Fail closed on a quoted harness variable outside its home module.

    Returns:
        One finding per offending line, plus one per declared root or home absent
        from gzkit's tree; nothing in an adopter project.

    """
    if not is_framework_tree(project_root):
        return []
    errors = missing_roots(
        project_root,
        (*(rel for rel, _ in ROOTS), *HOMES),
        error_type=_TYPE,
        prefix=_PREFIX,
        scope=_SCOPE,
    )
    for path in _scanned(project_root):
        rel = path.relative_to(project_root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        errors.extend(
            ValidationError(
                type=_TYPE,
                artifact=f"{rel}:{number}",
                message=f"{_PREFIX} {rel}:{number} {_RECOVERY.format(scope=_SCOPE)}",
            )
            for number, line in enumerate(text.splitlines(), 1)
            if _LITERAL.search(line)
        )
    return errors
