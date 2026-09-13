"""Chores-layout drift trust audit (ADR-0.0.21 Decision #9)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from gzkit.validate import ValidationError

_CHORES_LAYOUT_FILES: frozenset[str] = frozenset({"CHORE.md", "acceptance.json"})

_CHORES_LAYOUT_EXCLUDED_SEGMENTS: frozenset[str] = frozenset(
    {"__pycache__", ".venv", "dist", "build", "node_modules"}
)


def _is_excluded_chore_path(rel_parts: tuple[str, ...]) -> bool:
    """Skip dotfile-hidden ancestors and excluded build/venv segments."""
    if any(seg.startswith(".") for seg in rel_parts[:-1]):
        return True
    return any(seg in _CHORES_LAYOUT_EXCLUDED_SEGMENTS for seg in rel_parts)


def _is_canonical_chore_path(rel_posix: str, canonical_roots: tuple[str, ...]) -> bool:
    return any(rel_posix.startswith(f"{root}/") for root in canonical_roots)


def audit_chores_layout(project_root: Path) -> list[ValidationError]:
    """Flag ``CHORE.md`` / ``acceptance.json`` outside canonical chores roots.

    ADR-0.0.21 Decision #9: chores live under exactly two roots —
    ``src/gzkit/chores/`` (canonical, shipped in the wheel) and the
    project-scoped ``paths.chores`` (default ``.gzkit/chores/``). Two vectors
    fail closed: (1) any ``CHORE.md`` or ``acceptance.json`` discovered
    outside both roots is layout drift; (2) ANY file under the forbidden
    legacy ``ops/chores/`` root is drift regardless of filename — bare proof
    debris (no ``CHORE.md`` beside it) re-creates the tree the migration
    erased and slipped past the filename-only check for a month (GHI #605).

    Walking semantics mirror the ``audit_utf8_prefix`` pattern: skip
    dotfile-hidden segments, ``__pycache__``/``.venv``/``dist``/``build``/
    ``node_modules``. Waiver entries in
    ``data/chores_layout_waivers.json`` (a JSON list of POSIX path strings)
    exempt explicitly-listed paths per trust-doctrine T2.
    """
    from gzkit.config import GzkitConfig  # noqa: PLC0415

    config = GzkitConfig.load(project_root / ".gzkit.json")
    project_chores_root = config.paths.chores.strip("/")
    canonical_roots = ("src/gzkit/chores", project_chores_root)

    waivers = _load_chores_layout_waivers(project_root)

    errors: list[ValidationError] = []
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(project_root):
        # Prune excluded directories in place so traversal never descends
        # into dotfile-hidden or build/venv trees. A directory whose name
        # starts with "." or is in the excluded segment set would have every
        # file beneath it rejected by ``_is_excluded_chore_path`` (a dir name
        # is always an ancestor segment for files below it), so pruning here
        # cannot change which files reach the per-file filter — only how many
        # are walked.
        dirnames[:] = [
            name
            for name in dirnames
            if not name.startswith(".") and name not in _CHORES_LAYOUT_EXCLUDED_SEGMENTS
        ]
        base = Path(dirpath)
        files.extend(base / name for name in filenames)
    for path in sorted(files):
        if not path.is_file():
            continue
        rel = path.relative_to(project_root)
        if _is_excluded_chore_path(rel.parts):
            continue
        rel_posix = rel.as_posix()
        if rel_posix in waivers or _is_canonical_chore_path(rel_posix, canonical_roots):
            continue
        if rel_posix.startswith("ops/chores/"):
            errors.append(
                ValidationError(
                    type="chores_layout",
                    artifact=rel_posix,
                    message=(
                        f"file under forbidden legacy `ops/chores/` root: {rel_posix}. "
                        "ADR-0.0.21 Decision #9 forbids the `ops/chores/` layout "
                        "entirely (the migration vector this audit closes), regardless "
                        "of filename — bare proof debris re-creates the tree (GHI #605). "
                        "Recovery: delete the file and rewrite the chore's proof-write "
                        f"path to `{project_chores_root}/<slug>/proofs/`."
                    ),
                )
            )
            continue
        if path.name not in _CHORES_LAYOUT_FILES:
            continue
        errors.append(
            ValidationError(
                type="chores_layout",
                artifact=rel_posix,
                message=(
                    f"stray {path.name} outside canonical chores roots "
                    f"(`src/gzkit/chores/`, `{project_chores_root}/`). "
                    "ADR-0.0.21 Decision #9 forbids ad-hoc chore layouts."
                ),
            )
        )
    return errors


_CRITERIA_HEADING_RE = re.compile(r"^##\s+Acceptance(?:\s+Criteria)?\s*$", re.MULTILINE)
_NEXT_HEADING_RE = re.compile(r"^##\s+", re.MULTILINE)
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_FENCE_RE = re.compile(r"^```[^\n]*\n(.*?)^```", re.MULTILINE | re.DOTALL)
_VERSION_FIELD_RE = re.compile(r"\*\*Version:\*\*")
#: A change-history note, `> **Version 2.0.0 (...)**` or `> **3.2.0 (...)**`.
_HISTORY_VERSION_RE = re.compile(r"\*\*(?:Version\s+)?(\d+)\.(\d+)\.(\d+)\s*\(")
_TABLE_ROW_RE = re.compile(r"^\s*\|", re.MULTILINE)
_HEADER_FIELD_RE = re.compile(r"\*\*(Lane|Slug|Vendor|Timeout):\*\*\s*`?([A-Za-z0-9_.-]+)")
#: First tokens that make a span a runnable command rather than a name in prose.
_COMMAND_RUNNERS: frozenset[str] = frozenset({"uv", "uvx", "python", "python3", "gz", "test"})


def _criteria_section(chore_md: str) -> str | None:
    """Return the body of the ``## Acceptance Criteria`` (or ``## Acceptance``) section."""
    heading = _CRITERIA_HEADING_RE.search(chore_md)
    if heading is None:
        return None
    following = _NEXT_HEADING_RE.search(chore_md, heading.end())
    return chore_md[heading.end() : following.start() if following else len(chore_md)]


def _stated_commands(section: str) -> list[str]:
    """Return every command-shaped span a criteria section states.

    A span is command-shaped when it has at least two tokens and its first token
    is a runner in :data:`_COMMAND_RUNNERS`. A lone tool name (`grep`) or a
    pattern (`Path(__file__).parents`) is prose, not a criterion. Commands under
    any other runner are not recognized — a stated limit, not a guarantee.
    """
    fenced = [line for block in _FENCE_RE.findall(section) for line in block.splitlines()]
    unfenced = _FENCE_RE.sub("", section)
    spans = [*_INLINE_CODE_RE.findall(unfenced), *fenced]
    commands: list[str] = []
    for span in spans:
        tokens = span.split()
        if len(tokens) >= 2 and tokens[0] in _COMMAND_RUNNERS:
            commands.append(" ".join(tokens))
    return commands


def _runs(command: str, json_commands: frozenset[str]) -> bool:
    """Return True when ``command`` is carried by acceptance.json or reads it.

    A bare ``gz`` form of a JSON command counts as the same command. ``gz chores
    <verb>`` renders or executes the JSON itself, so pointing at it is the
    citation, never a restatement.
    """
    bare = command.removeprefix("uv run ")
    return (
        command in json_commands
        or f"uv run {command}" in json_commands
        or bare.startswith("gz chores ")
    )


def _history_mismatch(chore_md: str, entry: dict[str, object]) -> list[str]:
    """Return a message when the newest change note names a version the registry lacks.

    Older notes are the record of how the chore got here and stay; only the
    newest must be the version the registry carries.
    """
    noted = [tuple(int(part) for part in match) for match in _HISTORY_VERSION_RE.findall(chore_md)]
    if not noted:
        return []
    newest = ".".join(str(part) for part in max(noted))
    if newest == str(entry.get("version")):
        return []
    return [
        f"newest change note names version {newest} but registry.json carries "
        f"`{entry.get('version')}`; bump the registry with the note."
    ]


def _header_mismatches(chore_md: str, entry: dict[str, object]) -> list[str]:
    """Return a message per Lane/Slug/Vendor/Timeout value the registry disagrees with."""
    registry_values = {
        "Lane": entry.get("lane"),
        "Slug": entry.get("slug"),
        "Vendor": entry.get("vendor"),
        "Timeout": entry.get("timeoutSeconds"),
    }
    mismatches: list[str] = []
    for field, stated in _HEADER_FIELD_RE.findall(chore_md):
        expected = registry_values[field]
        normalized = stated.lower().removesuffix("s") if field == "Timeout" else stated.lower()
        if normalized != str(expected).lower():
            mismatches.append(
                f"**{field}:** states `{stated}` but registry.json carries `{expected}`; "
                "the registry is the authority, so the copy must agree with it."
            )
    return mismatches


def audit_chore_metadata_authority(project_root: Path) -> list[ValidationError]:
    """Flag chore metadata a ``CHORE.md`` states that its JSON authority does not carry.

    ``gz chores`` executes ``acceptance.json`` and reads ``registry.json``; a
    ``CHORE.md`` is the procedure an agent reads. Authored twice with nothing
    holding them equal, 17 of 40 chores' criteria and 7 versions drifted
    (GHI #1002). ``.gzkit/rules/governance-core.md``: *"Cite the authority, not
    the value."* Arms, per registered chore on the project surface:

    1. No ``**Version:**`` field, and the newest change note (``**X.Y.Z (``)
       names the registry's version — a version is written only in the registry.
    2. Every ``**Lane:**`` / ``**Slug:**`` / ``**Vendor:**`` / ``**Timeout:**``
       value agrees with the registry. These carry rationale beside the value
       and had not drifted, so they are held equal rather than removed.
    3. The criteria section exists, cites ``acceptance.json``, carries no table,
       and every command it states is one the JSON runs. Commands elsewhere
       (workflow, evidence) write proofs and are not criteria.

    Stated limits: a command under a runner outside :data:`_COMMAND_RUNNERS`, a
    required file named only in prose, and restatements under other headings
    (``## Checklist``, ``## Manual completion checks``) are not detected.

    Sync holds each slug's ``CHORE.md`` and ``acceptance.json`` byte-equal at
    ``src/gzkit/chores/``, ``README.md`` likewise, and ships ``registry.json``
    filtered (GHI #728, #1005), so the package copies are not re-read here.
    """
    from gzkit.config import GzkitConfig  # noqa: PLC0415

    config = GzkitConfig.load(project_root / ".gzkit.json")
    chores_root = project_root / config.paths.chores
    registry_path = chores_root / "registry.json"
    try:
        entries = json.loads(registry_path.read_text(encoding="utf-8")).get("chores", [])
    except (OSError, json.JSONDecodeError, AttributeError):
        return []
    errors: list[ValidationError] = []
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("path"):
            continue
        slug_dir = project_root / str(entry["path"])
        chore_md_path = slug_dir / "CHORE.md"
        try:
            chore_md = chore_md_path.read_text(encoding="utf-8")
            criteria = json.loads((slug_dir / "acceptance.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        artifact = chore_md_path.relative_to(project_root).as_posix()
        messages: list[str] = []
        if _VERSION_FIELD_RE.search(chore_md):
            messages.append(
                "states a **Version:** field; a chore's version is written only in "
                "registry.json, which `gz chores` reads."
            )
        messages.extend(_history_mismatch(chore_md, entry))
        messages.extend(_header_mismatches(chore_md, entry))
        section = _criteria_section(chore_md)
        if section is None or "acceptance.json" not in section:
            messages.append(
                "criteria section missing or does not cite acceptance.json; it must point "
                "at the JSON `gz chores run` executes rather than stand alone."
            )
        else:
            json_commands = frozenset(
                " ".join(str(c.get("command", "")).split()) for c in criteria.get("criteria", [])
            )
            if _TABLE_ROW_RE.search(section):
                messages.append(
                    "criteria section carries a table; it cites acceptance.json, so a "
                    "table there can only be a second copy of the criteria."
                )
            messages.extend(
                f"criteria section states `{command}`, which acceptance.json does not run."
                for command in _stated_commands(section)
                if not _runs(command, json_commands)
            )
        errors.extend(
            ValidationError(type="chore_metadata_authority", artifact=artifact, message=message)
            for message in messages
        )
    return errors


def _load_chores_layout_waivers(project_root: Path) -> frozenset[str]:
    """Load waiver paths from ``data/chores_layout_waivers.json``.

    Returns an empty frozenset if the file is absent, empty, or
    malformed — the audit fails open on waiver IO so a missing file does
    not silently become a strict-mode escape hatch in either direction.
    """
    waiver_file = project_root / "data" / "chores_layout_waivers.json"
    if not waiver_file.is_file():
        return frozenset()
    try:
        payload = json.loads(waiver_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return frozenset()
    if not isinstance(payload, list):
        return frozenset()
    return frozenset(str(entry) for entry in payload if isinstance(entry, str))
