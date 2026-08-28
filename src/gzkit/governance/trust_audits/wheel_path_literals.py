r"""Resolvability witness for wheel-shipped instruction text (GHI #900).

``gz validate --distribution`` proves the canonical surfaces *arrive* in the
wheel byte-for-byte.  It says nothing about whether the instruction those
bytes carry can **resolve** for the party it was delivered to.  Four shipped
files told a reader to open a path that existed on one laptop; the delivery
gate read green throughout, because the bytes were intact.

Scope: every ``.md`` covered by ``[tool.hatch.build.targets.wheel] include``,
read from :func:`gzkit.governance.trust_audits.distribution.wheel_build_config`
— the same declaration the delivery gate reads.  A transcribed glob list would
cover the trees that existed the day it was written and miss the next one
added to the wheel.

Executable modules under ``hooks/scripts/**`` are deliberately out of scope.
They are code, not steps a reader resolves, and one of them names
``C:/Users/RUNNER~1/...`` in a docstring describing the Windows 8.3
short-name bug it defends against — an illustration.  Excluding code on
principle beats waiving that line by number.

**What fails closed** — path literals rooted where only the authoring
environment can resolve them:

* a named user's home (``/Users/<name>/…``, ``/home/<name>/…``)
* a Windows drive (``C:\…``, ``C:/…``)
* machine-provisioning roots (``/opt/…``, ``/srv/…``, ``/mnt/…``)

**What does not, and why it is a boundary rather than an oversight.**
``~/…`` and ``$HOME/…`` expand per reader by construction — they are the
*remedy* this rule steers authors toward, so flagging them would push authors
back to the literal they just left.  ``/tmp``, ``/usr``, ``/var`` and
``/private`` resolve on every POSIX machine; ``/tmp`` alone had 23 legitimate
uses in wheel ``.md`` when this was authored (scratch-file targets in skill
and chore recipes), and their Windows behaviour is the separate concern
``cross-platform.md`` § Console / UTF-8 and § Render relative paths already
own.  A machine-specific path under one of those roots is therefore NOT
caught here; that limit is stated rather than implied.

The placeholder form is safe by construction: ``/Users/<name>/`` does not
match, because a match requires a real path character after the separator.
Doctrine can name the shape it forbids without tripping its own witness.
"""

from __future__ import annotations

import re
from pathlib import Path

from gzkit.governance.trust_audits.distribution import wheel_build_config
from gzkit.validate import ValidationError

_TYPE = "wheel_path_literals"
_PREFIX = "[wheel-path-literals]"

#: Path characters that can legitimately follow a root separator.  A match
#: requires at least one, which is what makes ``<name>`` placeholders inert.
_SEG = r"[A-Za-z0-9._-]+"

#: Left fence: reject a hit whose separator is already inside a longer token —
#: a URL path (``example.com/Users/…``), ``$HOME/…``, ``~/…``, or a relative
#: fragment.  Each of those resolves per reader, or is not a filesystem root.
_NOT_ROOTED = r"(?<![\w.$~{-])"

_ENVIRONMENT_ROOTED: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("a named user's home directory", re.compile(rf"{_NOT_ROOTED}/(?:Users|home)/{_SEG}")),
    ("a Windows drive letter", re.compile(r"(?<![\w:])[A-Za-z]:[\\/](?!/)")),
    ("a machine-provisioning root", re.compile(rf"{_NOT_ROOTED}/(?:opt|srv|mnt)/{_SEG}")),
)

_REMEDIATION = (
    "A path literal rooted at %s resolves only where it was authored, but this "
    "file ships in the wheel and is read on someone else's machine. Replace it "
    "with an explicit override the reader supplies (an env var carrying NO "
    "default), a repo-relative path, or a $HOME/~ form that expands per reader. "
    "If no portable form exists, say plainly that the step is skipped when the "
    "input is absent -- a recorded limitation, never a silent skip. "
    "Rule: .gzkit/rules/cross-platform.md (§ Delivered path literals). GHI #900."
)


def wheel_instruction_files(project_root: Path) -> list[Path]:
    """Return every Markdown file the wheel delivers, per its own include block."""
    # missing_ok: this audit is default-tier, so it runs against project roots
    # that ship no wheel. No build config means no delivered instruction text.
    include_globs, _packages = wheel_build_config(project_root, missing_ok=True)
    found: set[Path] = set()
    for pattern in include_globs:
        for match in project_root.glob(pattern):
            if match.is_file() and match.suffix == ".md" and "__pycache__" not in match.parts:
                found.add(match)
    return sorted(found)


def _scan(path: Path, project_root: Path) -> list[ValidationError]:
    rel = path.relative_to(project_root).as_posix()
    errors: list[ValidationError] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for description, pattern in _ENVIRONMENT_ROOTED:
            found = pattern.search(line)
            if found is None:
                continue
            errors.append(
                ValidationError(
                    type=_TYPE,
                    artifact=rel,
                    message=(
                        f"{_PREFIX} {rel}:{number} ships an instruction naming "
                        f"{found.group(0).strip()!r}, rooted at {description}. "
                        f"{_REMEDIATION % description}"
                    ),
                )
            )
            break
    return errors


def audit_wheel_path_literals(project_root: Path) -> list[ValidationError]:
    """Fail closed on environment-rooted path literals in wheel-shipped Markdown."""
    errors: list[ValidationError] = []
    for path in wheel_instruction_files(project_root):
        errors.extend(_scan(path, project_root))
    return errors
