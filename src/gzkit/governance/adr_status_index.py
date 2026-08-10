"""ADR Status Index regeneration — Layer 3 projection from Layer 1 canon.

`docs/governance/GovZero/adr-status.md` is a derived view per
`docs/governance/state-doctrine.md`. It must be regenerated from on-disk
ADR packages, never hand-maintained. This module owns the canonical
regeneration path and supplies the drift comparator for
`gz validate --adr-status-fresh`.

GHI #322 — drift across ~5 ADRs went undetected because no maintained
regenerator existed; this module closes the class.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple

ADR_SUBDIRS: tuple[str, ...] = ("foundation", "pre-release")
TABLE_HEADER = "| ID | Title | Kind | Lane | Status | Date | Path |"
TABLE_DIVIDER = "|---|---|---|---|---|---|---|"
SOURCE_OF_TRUTH_NOTE = (
    "Source-of-truth: filesystem under "
    "`docs/design/adr/{foundation,pre-release}/`; this table is a Layer 3 "
    "derived view per `docs/governance/state-doctrine.md`. Regenerate via "
    "`gz register-adrs` (which calls `regenerate_adr_status_md` after "
    "ledger reconciliation); drift is fail-closed by "
    "`gz validate --adr-status-fresh`."
)

# The H1 separator has two authored spellings in the corpus -- `# ADR-x: Title`
# and `# ADR-x — Title`. Matching only the colon sent every em-dash ADR to the
# stem fallback, so 11 of 86 rendered their own id in the Title column while the
# file carried a real authored title. The fallback itself stays correct: an H1
# with no separator genuinely has no title to extract.
_HEADER_TITLE_RE = re.compile(r"^#\s+(ADR-\S+)\s*[:—–]\s*(.+?)\s*$")
_TABLE_ROW_LINK_RE = re.compile(r"\[([^\]]+)\]")
_SEMVER_RE = re.compile(r"^ADR-(\d+)\.(\d+)\.(\d+)")


class AdrRow(NamedTuple):
    """One row of the ADR status table."""

    adr_id: str
    title: str
    kind: str
    lane: str
    status: str
    date: str
    rel_path: str

    def semver_key(self) -> tuple[int, int, int, int, str]:
        """Order foundation (0.0.x) ahead of feature (0.y.z), then by semver."""
        match = _SEMVER_RE.match(self.adr_id)
        if not match:
            return (9, 9, 9, 9, self.adr_id)
        major, minor, patch = (int(x) for x in match.groups())
        bucket = 0 if (major == 0 and minor == 0) else 1
        return (bucket, major, minor, patch, self.adr_id)

    def signature(self) -> tuple[str, ...]:
        """Return a comparable tuple for drift detection (excludes regen date)."""
        return (
            self.adr_id,
            self.title,
            self.kind,
            self.lane,
            self.status,
            self.date,
            self.rel_path,
        )


def _parse_adr_metadata(adr_file: Path, docs_root: Path) -> AdrRow | None:
    """Parse one ADR file's frontmatter + H1 title into an AdrRow."""
    try:
        content = adr_file.read_text(encoding="utf-8")
    except OSError:
        return None

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    frontmatter: dict[str, str] = {}
    body_start = 0
    for idx in range(1, len(lines)):
        raw = lines[idx]
        if raw.strip() == "---":
            body_start = idx + 1
            break
        if ":" not in raw:
            continue
        key, _, value = raw.partition(":")
        frontmatter[key.strip().lower()] = value.strip().strip("\"'")

    title = ""
    for raw in lines[body_start : body_start + 30]:
        match = _HEADER_TITLE_RE.match(raw.strip())
        if match:
            title = match.group(2)
            break

    try:
        rel_path = adr_file.relative_to(docs_root).as_posix()
    except ValueError:
        return None

    return AdrRow(
        adr_id=adr_file.stem,
        title=title or adr_file.stem,
        kind=frontmatter.get("kind", ""),
        lane=frontmatter.get("lane", ""),
        status=frontmatter.get("status", ""),
        date=frontmatter.get("date", ""),
        rel_path=rel_path,
    )


def collect_adr_rows(project_root: Path) -> list[AdrRow]:
    """Walk on-disk ADR packages and return rows in canonical order."""
    docs_root = project_root / "docs"
    adr_root = docs_root / "design" / "adr"
    rows: list[AdrRow] = []
    for subdir_name in ADR_SUBDIRS:
        subdir = adr_root / subdir_name
        if not subdir.is_dir():
            continue
        for adr_dir in sorted(subdir.iterdir()):
            if not adr_dir.is_dir() or not adr_dir.name.startswith("ADR-"):
                continue
            adr_file = adr_dir / f"{adr_dir.name}.md"
            if not adr_file.is_file():
                continue
            row = _parse_adr_metadata(adr_file, docs_root)
            if row is not None:
                rows.append(row)
    rows.sort(key=AdrRow.semver_key)
    return rows


def render_table(rows: list[AdrRow], regen_date: str) -> str:
    """Render the canonical adr-status.md content from rows."""
    out: list[str] = [
        "<!-- pyml disable-num-lines 100 md013 -->",
        "",
        "# ADR Status Table",
        "",
        "Status: Active",
        "",
        "",
        SOURCE_OF_TRUTH_NOTE,
        "",
        f"Last regenerated: {regen_date} (count: {len(rows)} ADRs).",
        "",
        TABLE_HEADER,
        TABLE_DIVIDER,
    ]
    for row in rows:
        link = f"[{row.adr_id}](../../{row.rel_path})"
        out.append(
            f"| {link} | {row.title} | {row.kind} | {row.lane} | "
            f"{row.status} | {row.date} | `{row.rel_path}` |"
        )
    return "\n".join(out) + "\n"


def _adr_status_path(project_root: Path) -> Path:
    return project_root / "docs" / "governance" / "GovZero" / "adr-status.md"


def regenerate_adr_status_md(
    project_root: Path,
    *,
    write: bool = True,
    regen_date: str | None = None,
) -> str:
    """Regenerate adr-status.md from on-disk truth and (optionally) write it."""
    rows = collect_adr_rows(project_root)
    date = regen_date or datetime.now(UTC).strftime("%Y-%m-%d")
    content = render_table(rows, date)
    if write:
        target = _adr_status_path(project_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
    return content


def parse_existing_rows(content: str) -> dict[str, tuple[str, ...]]:
    """Extract committed table rows keyed by adr_id."""
    rows: dict[str, tuple[str, ...]] = {}
    for raw in content.splitlines():
        if not raw.startswith("| ["):
            continue
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        if len(cells) != 7:
            continue
        link_match = _TABLE_ROW_LINK_RE.match(cells[0])
        if not link_match:
            continue
        adr_id = link_match.group(1)
        title, kind, lane, status, date, path_cell = cells[1:7]
        path = path_cell.strip("`")
        rows[adr_id] = (adr_id, title, kind, lane, status, date, path)
    return rows


class DriftEntry(NamedTuple):
    """One adr-status drift finding."""

    adr_id: str
    kind: str  # "missing" | "obsolete" | "field"
    detail: str


def compute_drift(project_root: Path) -> list[DriftEntry]:
    """Compare committed adr-status.md against on-disk truth."""
    target = _adr_status_path(project_root)
    if not target.is_file():
        rel = target.relative_to(project_root).as_posix()
        return [DriftEntry("(file)", "missing", f"{rel} missing")]

    fresh_rows = collect_adr_rows(project_root)
    fresh_by_id = {row.adr_id: row.signature() for row in fresh_rows}
    existing_by_id = parse_existing_rows(target.read_text(encoding="utf-8"))

    drift: list[DriftEntry] = []
    for adr_id in sorted(set(fresh_by_id) - set(existing_by_id)):
        drift.append(DriftEntry(adr_id, "missing", "on-disk ADR has no row in adr-status.md"))
    for adr_id in sorted(set(existing_by_id) - set(fresh_by_id)):
        drift.append(DriftEntry(adr_id, "obsolete", "table row references no on-disk ADR"))
    for adr_id in sorted(set(fresh_by_id) & set(existing_by_id)):
        if fresh_by_id[adr_id] != existing_by_id[adr_id]:
            fields = []
            labels = ("adr_id", "title", "kind", "lane", "status", "date", "rel_path")
            for label, fresh, existing in zip(
                labels, fresh_by_id[adr_id], existing_by_id[adr_id], strict=True
            ):
                if fresh != existing:
                    fields.append(f"{label}: committed={existing!r} on-disk={fresh!r}")
            drift.append(DriftEntry(adr_id, "field", "; ".join(fields)))
    return drift
