"""One-shot backfill: write `kind:` frontmatter into existing non-pool ADRs.

Classifies by semver (`0.0.x` -> `foundation`, otherwise -> `feature`) and
emits a JSON receipt to artifacts/receipts/. Idempotent: files already
carrying `kind:` are skipped on re-runs. Pool ADRs (under
`docs/design/adr/pool/`) are excluded by path; files without parseable
semver frontmatter are recorded as errors and not mutated.

OBPI-0.0.17-05-backfill-and-roundtrip.

Usage:
    uv run python scripts/backfill_adr_taxonomy.py --dry-run
    uv run python scripts/backfill_adr_taxonomy.py --apply
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

_FOUNDATION_SEMVER_RE = re.compile(r"^0\.0\.\d+$")
_VALID_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_SEMVER_LINE_RE = re.compile(r"^semver:\s*(\S+)\s*$", re.MULTILINE)
_KIND_LINE_RE = re.compile(r"^kind:\s*\S+", re.MULTILINE)
_STATUS_LINE_RE = re.compile(r"^status:\s*\S+", re.MULTILINE)

_ADR_ROOTS = (
    Path("docs/design/adr/foundation"),
    Path("docs/design/adr/pre-release"),
)

_SKIP_PARTS = frozenset({"obpis", "briefs", "audit", "handoffs", "plans", "pool"})


def classify_kind(semver: str) -> Literal["foundation", "feature"]:
    """0.0.x -> foundation; everything else with valid semver shape -> feature."""
    if _FOUNDATION_SEMVER_RE.match(semver):
        return "foundation"
    return "feature"


def walk_adrs(project_root: Path) -> Iterator[Path]:
    """Yield top-level ADR files under foundation/ and pre-release/.

    Skips nested obpis/briefs/audit/handoffs/plans directories and the
    ADR-CLOSEOUT-FORM template.
    """
    for relroot in _ADR_ROOTS:
        absroot = project_root / relroot
        if not absroot.is_dir():
            continue
        for path in sorted(absroot.rglob("ADR-*.md")):
            if path.name == "ADR-CLOSEOUT-FORM.md":
                continue
            if any(part in _SKIP_PARTS for part in path.parts):
                continue
            yield path


def _extract_frontmatter(content: str) -> str | None:
    """Return the frontmatter block (between the first two `---` fences), or None."""
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1]


def insert_kind_after_status(content: str, kind: str) -> str:
    """Insert `kind: <kind>` immediately after the `status:` line in frontmatter.

    Operates only inside the leading frontmatter block; the body is
    untouched. Caller guarantees frontmatter exists and lacks a kind line.
    """
    parts = content.split("---", 2)
    head, fm, body = parts[0], parts[1], parts[2]
    lines = fm.splitlines(keepends=False)
    new_lines: list[str] = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if not inserted and line.startswith("status:"):
            new_lines.append(f"kind: {kind}")
            inserted = True
    new_fm = "\n".join(new_lines)
    if fm.endswith("\n"):
        new_fm += "\n"
    return f"{head}---{new_fm}---{body}"


def _process_one(
    path: Path, project_root: Path
) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
    """Return (modification, error). Exactly one is non-None unless skipped."""
    rel = path.relative_to(project_root).as_posix()
    text = path.read_text(encoding="utf-8")
    fm = _extract_frontmatter(text)
    if fm is None:
        return None, {"path": rel, "reason": "no parseable frontmatter block"}
    if _KIND_LINE_RE.search(fm):
        return None, None  # idempotent skip
    if not _STATUS_LINE_RE.search(fm):
        return None, {"path": rel, "reason": "missing `status:` field"}
    semver_match = _SEMVER_LINE_RE.search(fm)
    if semver_match is None:
        return None, {"path": rel, "reason": "missing `semver:` field"}
    semver = semver_match.group(1)
    if not _VALID_SEMVER_RE.match(semver):
        return None, {"path": rel, "reason": f"malformed semver `{semver}`"}
    kind = classify_kind(semver)
    new_text = insert_kind_after_status(text, kind)
    return (
        {"path": rel, "kind": kind, "semver": semver, "new_text": new_text},
        None,
    )


def run_backfill(
    *,
    project_root: Path,
    receipt_dir: Path,
    dry_run: bool,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Walk eligible ADRs, optionally mutate them, and emit a receipt.

    Returns the receipt dict (also written to disk). Pool ADRs are excluded
    by path. Files with `kind:` already present are silently skipped to
    keep the operation idempotent.
    """
    timestamp = (now or datetime.now(UTC)).strftime("%Y-%m-%dT%H-%M-%SZ")
    modifications: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    files_scanned = 0

    for adr in walk_adrs(project_root):
        files_scanned += 1
        mod, err = _process_one(adr, project_root)
        if err is not None:
            errors.append(err)
            continue
        if mod is None:
            continue
        if not dry_run:
            adr.write_text(mod["new_text"], encoding="utf-8")
        modifications.append({"path": mod["path"], "kind": mod["kind"], "semver": mod["semver"]})

    receipt: dict[str, Any] = {
        "timestamp": timestamp,
        "dry_run": dry_run,
        "files_scanned": files_scanned,
        "files_modified": len(modifications),
        "modifications": modifications,
        "errors": errors,
    }

    receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipt_dir / f"adr-taxonomy-backfill-{timestamp}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Backfill `kind:` frontmatter into existing non-pool ADRs.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Write changes to disk.")
    mode.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without writing (default).",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root (defaults to cwd).",
    )
    args = parser.parse_args(argv)

    dry_run = not args.apply
    project_root = args.project_root.resolve()
    receipt_dir = project_root / "artifacts" / "receipts"

    receipt = run_backfill(
        project_root=project_root,
        receipt_dir=receipt_dir,
        dry_run=dry_run,
    )

    print(
        f"Scanned {receipt['files_scanned']} ADR(s); "
        f"{'would modify' if dry_run else 'modified'} {receipt['files_modified']}; "
        f"errors: {len(receipt['errors'])}"
    )
    return 0 if not receipt["errors"] else 0  # errors are reported but not fatal


if __name__ == "__main__":
    sys.exit(main())
