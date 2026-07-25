"""Brief allowed-path validity primitives shared across plan-audit and obpi-validate.

Lifted from ``gzkit.commands.plan_audit_cmd`` under GHI #419 so that brief
authoring-time pre-flight (``gz obpi validate``, ``gz adr promote``) can run
the same path-existence + vendor-mirror checks as ``gz plan audit``, without
waiting for plan authoring to surface the drift.

GHI #419 cost evidence: every OBPI implementation that started from a
brief with drifted ``## Allowed Paths`` paid ~10 minutes correcting the
drift mid-flight at Stage 4. Brief-authoring pre-flight closes that gap
at zero cost.

Invariants preserved from the GHI #393 / GHI #403 origins:

* Vendor-mirror surfaces (``.claude/rules/``, ``.claude/skills/``,
  ``.github/skills/``, ``.github/instructions/``, ``.agents/skills/``) fail
  fail-closed regardless of existence — editing a generated mirror is
  silently overwritten by the next ``gz agent sync control-surfaces``.
* Glob-shaped paths (``src/gzkit/**/*.py``) resolve through their longest
  literal-prefix root.
* Net-new paths the brief or sibling plan declares it creates are exempt
  from the existence gap (GHI #403 carryover; brief-level analogue
  authored under GHI #419).
"""

import re
from pathlib import Path

_ALLOWED_HEADING_RE = re.compile(r"^##\s+ALLOWED\s+PATHS(\s*\(.*?\))?\s*$", re.IGNORECASE)
_BULLET_PATH_RE = re.compile(r"^\s*-\s*`([^`]+)`")

_VENDOR_MIRROR_TO_CANONICAL: tuple[tuple[str, str], ...] = (
    (".claude/rules/", ".gzkit/rules/"),
    (".claude/skills/", ".gzkit/skills/"),
    (".github/skills/", ".gzkit/skills/"),
    (".github/instructions/", ".gzkit/rules/"),
    (".agents/skills/", ".gzkit/skills/"),
)

_GLOB_MARKER_CHARS = "*?[<"

_CREATES_PATH_PREFIXES: tuple[str, ...] = (
    "src/",
    "tests/",
    "docs/",
    ".gzkit/",
    ".claude/",
    ".agents/",
    ".github/",
    "data/",
    "features/",
)


def _normalize_for_creates(token: str) -> str:
    """Normalize a token for creates-set comparison.

    Strips at most one literal ``./`` prefix and trailing ``/``. Distinct
    from ``str.lstrip("./")`` which would also eat the leading dot of
    dotfile-rooted paths like ``.gzkit/`` or ``.claude/``, breaking the
    prefix check at the call site (GHI #433).
    """
    return token.removeprefix("./").rstrip("/")


def has_glob_chars(token: str) -> bool:
    """Return True when the token contains a glob marker character."""
    return any(ch in token for ch in _GLOB_MARKER_CHARS)


def glob_root(path: str) -> str:
    """Return the longest leading literal-component prefix of a glob path.

    ``src/gzkit/**/*.py`` -> ``src/gzkit``;
    ``.gzkit/skills/<slug>/SKILL.md`` -> ``.gzkit/skills``;
    ``*.md`` -> ``""`` (caller treats as project root).
    """
    literal: list[str] = []
    for part in path.split("/"):
        if has_glob_chars(part):
            break
        literal.append(part)
    return "/".join(literal)


def vendor_mirror_canonical(path: str) -> str | None:
    """Return the canonical edit surface for a vendor-mirror path, else None."""
    normalized = path.rstrip("/") + "/"
    for prefix, canonical in _VENDOR_MIRROR_TO_CANONICAL:
        if normalized.startswith(prefix):
            tail = path[len(prefix) :].rstrip("/")
            return canonical + tail if tail else canonical.rstrip("/")
    return None


def allowed_path_resolves(project_root: Path, path: str) -> bool:
    """Return True when an allowed path resolves to a real file/dir or its glob root exists."""
    if path.startswith("-"):
        return True
    candidate = path.rstrip("/")
    if not candidate:
        return False
    if has_glob_chars(candidate):
        root = glob_root(candidate)
        if not root:
            return True
        return (project_root / root).exists()
    return (project_root / candidate).exists()


def extract_allowed_paths(brief_path: Path) -> list[str] | None:
    """Extract allowed paths from an OBPI brief.

    Accepts ``## Allowed Paths`` and ``## ALLOWED PATHS`` (and parenthesized
    lane suffixes like ``## ALLOWED PATHS (Foundational)``). Path bullets are
    read from the first backtick-delimited token on each bullet line, so
    trailing ``-- commentary`` is ignored.
    """
    content = brief_path.read_text(encoding="utf-8")
    in_allowed = False
    paths: list[str] = []
    for line in content.splitlines():
        if _ALLOWED_HEADING_RE.match(line):
            in_allowed = True
            continue
        if in_allowed and line.startswith("## "):
            break
        if in_allowed:
            match = _BULLET_PATH_RE.match(line)
            if match:
                path = match.group(1).strip()
                if path:
                    paths.append(path)
    return paths if paths else None


# `gz specify` scaffolds every Discovery Checklist row as "Required path exists
# **or is intentionally created in this OBPI**" (`specify_cmd.py:419`) — a line
# that declares its own path may be net-new. The creates-extractor only knew
# `**CREATE**` and "creates these files", so the producer and the consumer
# disagreed about a marker the producer emits on every scaffolded brief, and 53
# Draft briefs reported Discovery drift for files their own OBPI exists to
# create. Same one-document-many-parsers class as GHI #615 itself; the two
# surfaces are matched here rather than the phrasing being changed, because the
# corpus already carries it.
_SCAFFOLDED_CREATES_HINT = "intentionally created in this OBPI"


def _extract_creates_paths_from_text(content: str) -> set[str]:
    """Mine path-shaped tokens from CREATE markers and Creates-these-files sections.

    Returned paths are normalized: leading ``./`` stripped, trailing ``/``
    stripped. The same normalization runs on the ``allowed`` side in
    :func:`check_brief_path_validity` so directory-shaped allowed paths
    (``src/gzkit/ports/``) match directory-shaped creates declarations.
    """
    paths: set[str] = set()
    in_creates_section = False
    for line in content.splitlines():
        if line.lstrip().startswith("#"):
            in_creates_section = "creates these files" in line.lower()
        if not (in_creates_section or "**CREATE**" in line or _SCAFFOLDED_CREATES_HINT in line):
            continue
        for token in line.split():
            cleaned = _normalize_for_creates(token.strip("`*,()[]<>"))
            if any(cleaned.startswith(prefix) for prefix in _CREATES_PATH_PREFIXES):
                paths.add(cleaned)
    return paths


def extract_brief_creates_paths(brief_path: Path) -> set[str]:
    """Return paths the brief declares it creates (GHI #419 brief-level analogue).

    Brief authors declare net-new paths via either: lines containing the
    literal token ``**CREATE**``, or any line under a heading whose text
    contains ``creates these files`` (case-insensitive). This mirrors the
    plan-level GHI #403 marker so authoring-time ``gz obpi validate`` can
    suppress the existence gap on net-new files the brief is creating
    without waiting for the plan to land.
    """
    return _extract_creates_paths_from_text(brief_path.read_text(encoding="utf-8"))


def extract_plan_creates_paths(plan_file: Path) -> set[str]:
    """Return paths the plan declares it creates (GHI #403)."""
    return _extract_creates_paths_from_text(plan_file.read_text(encoding="utf-8"))


def check_brief_path_validity(
    project_root: Path,
    allowed: list[str],
    creates_paths: set[str] | None = None,
) -> list[str]:
    """Return gap messages for non-existent or vendor-mirror allowed paths (GHI #393).

    Net-new paths declared as created (plan-level GHI #403 or brief-level
    GHI #419) are exempt from the non-existence check — they exist in
    contract before they exist on disk.
    """
    creates = creates_paths or set()
    gaps: list[str] = []
    for path in allowed:
        canonical = vendor_mirror_canonical(path)
        if canonical is not None:
            gaps.append(
                "Allowed path is a generated vendor mirror; edit canonical "
                f"surface instead: {path} -> {canonical}"
            )
            continue
        if not allowed_path_resolves(project_root, path):
            if _normalize_for_creates(path) in creates:
                continue
            gaps.append(f"Allowed path does not exist in repository: {path}")
    return gaps


def check_brief_path_validity_for_brief(
    project_root: Path,
    brief_path: Path,
) -> list[str]:
    """Extract allowed + brief-level creates and run the validity check.

    Returns an empty list when the brief has no ``## Allowed Paths`` section
    (newly scaffolded briefs surface no signal until paths are authored).
    """
    allowed = extract_allowed_paths(brief_path)
    if not allowed:
        return []
    creates = extract_brief_creates_paths(brief_path)
    return check_brief_path_validity(project_root, allowed, creates)
