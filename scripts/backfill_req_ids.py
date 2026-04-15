"""Backfill REQ-ID acceptance criteria into legacy OBPI briefs.

Phase 3 of GHI #160 governance graph rot remediation.

For each OBPI brief that has a `## REQUIREMENTS (...)` section but no
`## Acceptance Criteria` section, parse the numbered REQUIREMENTS items
and insert a canonical Acceptance Criteria section with deterministic
`REQ-<semver>-<obpi_item>-<criterion>` identifiers (1:1 mapping).

Coarse-requirement splitting is a refinement pass left for after every
ADR is at least visible to `gz covers` (DO IT RIGHT #3).

Usage:
    uv run python scripts/backfill_req_ids.py --dry-run [<adr_id> ...]
    uv run python scripts/backfill_req_ids.py [<adr_id> ...]

If no ADR ids are passed, every ADR under docs/design/adr is processed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADR_ROOT = ROOT / "docs" / "design" / "adr"

REQ_ID_PATTERN = re.compile(r"REQ-\d+\.\d+\.\d+-\d+-\d+")
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
HEADING_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.M)
REQUIREMENTS_HEADING = re.compile(r"^##\s+REQUIREMENTS\b", re.M | re.I)
ACCEPTANCE_HEADING = re.compile(r"^##\s+Acceptance Criteria\b", re.M)
NUMBERED_ITEM_PATTERN = re.compile(r"^\s*(\d+)\.\s+(.+)$")


def parse_frontmatter(content: str) -> dict[str, str]:
    """Extract YAML-ish key:value pairs from frontmatter."""
    m = FRONTMATTER_PATTERN.match(content)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def derive_semver(parent: str) -> str | None:
    """Extract X.Y.Z from `ADR-X.Y.Z-name` parent string."""
    m = re.match(r"ADR-(\d+\.\d+\.\d+)", parent or "")
    return m.group(1) if m else None


def find_requirements_section(content: str) -> tuple[int, int] | None:
    """Return (start, end) char offsets of the first REQUIREMENTS section body.

    The body is everything between the heading line and the next ``## `` heading
    (or end of file). Start offset is the first character after the heading line's
    trailing newline; end offset is the start of the next heading line (or EOF).
    """
    m = REQUIREMENTS_HEADING.search(content)
    if not m:
        return None
    body_start = content.find("\n", m.end()) + 1
    next_heading = HEADING_PATTERN.search(content, body_start)
    body_end = next_heading.start() if next_heading else len(content)
    return body_start, body_end


def extract_numbered_items(section_body: str) -> list[str]:
    """Return the prose text of every numbered item in a REQUIREMENTS section.

    Markdown allows either `1. 2. 3.` or `1. 1. 1.` numbering — both styles
    are accepted. Multi-line item continuation (indented continuation lines)
    is folded into the preceding item's text.
    """
    items: list[str] = []
    current: list[str] = []
    for raw in section_body.splitlines():
        stripped = raw.strip()
        if not stripped:
            if current:
                items.append(" ".join(current).strip())
                current = []
            continue
        m = NUMBERED_ITEM_PATTERN.match(raw)
        if m:
            if current:
                items.append(" ".join(current).strip())
            current = [m.group(2).strip()]
        elif current and (raw.startswith("   ") or raw.startswith("\t")):
            current.append(stripped)
    if current:
        items.append(" ".join(current).strip())
    return [i for i in items if i]


def build_acceptance_section(semver: str, item: str, requirements: list[str]) -> str:
    """Build the canonical Acceptance Criteria section text."""
    nn = item.zfill(2)
    lines = [
        "## Acceptance Criteria",
        "",
        "<!--",
        "Specific, testable criteria for completion.",
        "Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.",
        "Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.",
        "-->",
        "",
    ]
    for idx, text in enumerate(requirements, start=1):
        mm = str(idx).zfill(2)
        lines.append(f"- [x] REQ-{semver}-{nn}-{mm}: {text}")
    lines.append("")
    return "\n".join(lines) + "\n"


def find_acceptance_section(content: str) -> tuple[int, int] | None:
    """Return (start, end) char offsets of the existing Acceptance Criteria body."""
    m = ACCEPTANCE_HEADING.search(content)
    if not m:
        return None
    body_start = content.find("\n", m.end()) + 1
    next_heading = HEADING_PATTERN.search(content, body_start)
    body_end = next_heading.start() if next_heading else len(content)
    return body_start, body_end


CHECKLIST_LINE_PATTERN = re.compile(r"^(\s*-\s+\[)([ xX])(\]\s+)(.+?)\s*$")


def rewrite_acceptance_section(body: str, semver: str, item: str) -> tuple[str, int]:
    """Inject REQ IDs into an existing Acceptance Criteria body's `- [ ]` lines.

    Returns (rewritten_body, n_reqs_assigned).
    """
    nn = item.zfill(2)
    out_lines: list[str] = []
    counter = 0
    for raw in body.splitlines():
        m = CHECKLIST_LINE_PATTERN.match(raw)
        if m and "REQ-" not in raw:
            counter += 1
            mm = str(counter).zfill(2)
            req_id = f"REQ-{semver}-{nn}-{mm}"
            out_lines.append(f"{m.group(1)}x{m.group(3)}{req_id}: {m.group(4)}")
        else:
            out_lines.append(raw)
    return "\n".join(out_lines) + ("\n" if body.endswith("\n") else ""), counter


def derive_semver_and_item(path: Path, fm: dict[str, str]) -> tuple[str | None, str | None]:
    """Resolve semver + obpi item from frontmatter with filename fallback."""
    semver = derive_semver(fm.get("parent", ""))
    item = fm.get("item") or fm.get("sequence")
    if not semver or not item:
        fm_match = re.match(r"OBPI-(\d+\.\d+\.\d+)-(\d+)", path.name)
        if fm_match:
            semver = semver or fm_match.group(1)
            item = item or fm_match.group(2)
    return semver, item


def process_obpi_file(path: Path, dry_run: bool) -> tuple[str, int]:
    """Process one OBPI brief. Returns (status, n_reqs_added)."""
    content = path.read_text(encoding="utf-8")

    if REQ_ID_PATTERN.search(content):
        return ("has-req-ids", 0)

    fm = parse_frontmatter(content)
    semver, item = derive_semver_and_item(path, fm)
    if not semver or not item:
        return ("missing-frontmatter", 0)

    # Mode D: existing Acceptance Criteria section with bare `- [ ]` lines
    accept_section = find_acceptance_section(content)
    if accept_section is not None:
        body = content[accept_section[0] : accept_section[1]]
        rewritten, n = rewrite_acceptance_section(body, semver, item)
        if n == 0:
            return ("acceptance-section-no-checklist-items", 0)
        new_content = content[: accept_section[0]] + rewritten + content[accept_section[1] :]
        if not dry_run:
            path.write_text(new_content, encoding="utf-8")
        return ("backfilled-mode-d", n)

    # Mode E: REQUIREMENTS section but no Acceptance Criteria — synthesize one
    section = find_requirements_section(content)
    if not section:
        return ("no-requirements-section", 0)
    body = content[section[0] : section[1]]
    requirements = extract_numbered_items(body)
    if not requirements:
        return ("requirements-section-empty", 0)

    acceptance = build_acceptance_section(semver, item, requirements)
    insert_at = section[1]
    new_content = content[:insert_at] + acceptance + "\n" + content[insert_at:]

    if not dry_run:
        path.write_text(new_content, encoding="utf-8")
    return ("backfilled-mode-e", len(requirements))


def find_obpi_files(adr_filter: set[str]) -> list[Path]:
    """Walk every ADR directory and return its OBPI brief paths.

    Looks under both ``obpis/`` and ``briefs/`` to handle the ADR-0.40.0 pattern.
    Filters by ADR identifier when ``adr_filter`` is non-empty.
    """
    paths: list[Path] = []
    for adr_dir in sorted(ADR_ROOT.glob("*/ADR-*")):
        m = re.match(r"ADR-(\d+\.\d+\.\d+)-", adr_dir.name)
        if not m:
            continue
        adr_id = f"ADR-{m.group(1)}"
        if adr_filter and adr_id not in adr_filter:
            continue
        for sub in ("obpis", "briefs"):
            for f in sorted((adr_dir / sub).glob("OBPI-*.md")):
                if f.name.startswith("REVIEW-"):
                    continue
                paths.append(f)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("adr_ids", nargs="*", help="Target ADR identifiers (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = parser.parse_args()

    adr_filter = set(args.adr_ids)
    paths = find_obpi_files(adr_filter)

    by_status: dict[str, int] = {}
    by_adr: dict[str, int] = {}
    for path in paths:
        status, n_reqs = process_obpi_file(path, args.dry_run)
        by_status[status] = by_status.get(status, 0) + 1
        if status.startswith("backfilled"):
            adr_id = re.match(r"OBPI-(\d+\.\d+\.\d+)", path.name).group(1)
            by_adr[adr_id] = by_adr.get(adr_id, 0) + n_reqs
            tag = status.removeprefix("backfilled-")
            prefix = "[dry-run] " if args.dry_run else ""
            rel = path.relative_to(ROOT)
            print(f"  {prefix}[{tag}] {rel} +{n_reqs} REQs")

    print()
    print("=== status summary ===")
    for s, n in sorted(by_status.items()):
        print(f"  {s}: {n}")
    print()
    print("=== REQs added per ADR ===")
    for adr, n in sorted(by_adr.items(), key=lambda kv: tuple(int(p) for p in kv[0].split("."))):
        print(f"  ADR-{adr}: +{n}")
    total_reqs = sum(by_adr.values())
    print(f"\nTotal REQs added: {total_reqs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
