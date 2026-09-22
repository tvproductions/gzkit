#!/usr/bin/env python3
"""Measure the requirements/release-management seam in this repository.

Carries no literals from the date it was authored: every figure is derived from
the tree it is run against, so a later run reports that tree rather than
confirming a transcribed number (``AGENTS.md`` § Governance doctrine surfaces --
"A value written in a Markdown doc is ILLUSTRATIVE, never authoritative").

Usage::

    uv run python docs/governance/ieee/02-requirements-vs-release-evidence/measure.py
    uv run python .../measure.py --json

Exit status is 0 whenever the measurement completes; this is a census, not a
gate. Stdlib only, per the STDLIB-FIRST doctrine.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import TypedDict

REPO = Path(__file__).resolve().parents[4]

SEMVER_TAG = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
ADR_FEATURE = re.compile(r"^ADR-(\d+)\.(\d+)\.(\d+)-")
REQ_ID = re.compile(r"\bREQ-\d+\.\d+\.\d+-\d{2}-\d{2}\b")
REQ_PARENT = re.compile(r"^REQ-(\d+\.\d+\.\d+)-")
COVERS_CALL = re.compile(r"@covers\(([^)]*)\)", re.S)
BASELINE_WORD = re.compile(r"\b[A-Za-z_-]*baseline[A-Za-z_-]*\b", re.IGNORECASE)


class RenameCensus(TypedDict):
    """Identifier-rename totals, grouped by the reason the emitter declared."""

    total: int
    by_reason: dict[str, int]


class ReqCensus(TypedDict):
    """REQ-identifier population, citation count, and orphaned citations."""

    distinct_on_disk: int
    distinct_cited: int
    orphan_citations: int
    orphans_synthetic_fixture: int
    traceability_casualties: int
    casualty_sites: dict[str, list[str]]
    casualty_cause: dict[str, str]


def git(*args: str) -> str:
    """Run a git command in the repo and return stdout, or "" when it fails."""
    try:
        out = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=False)
    except OSError:
        return ""
    return out.stdout if out.returncode == 0 else ""


def version_lines() -> dict[str, object]:
    """Compare the shipped-release line against the ADR-identifier line.

    Both are written in semver. They are different sequences, and the size of
    the divergence is the measurement.
    """
    tags: list[tuple[int, ...]] = []
    for line in git("tag").splitlines():
        m = SEMVER_TAG.match(line.strip())
        if m:
            tags.append(tuple(int(p) for p in m.groups()))
    tags.sort()

    adrs: set[tuple[int, ...]] = set()
    for base in (REPO / "docs" / "design" / "adr").rglob("ADR-*"):
        m = ADR_FEATURE.match(base.name)
        if m:
            adrs.add(tuple(int(p) for p in m.groups()))
    feature_adrs = sorted(a for a in adrs if a[0] == 0 and a[1] > 0)

    tag_minors = {t[1] for t in tags if t[0] == 0}
    adr_minors = {a[1] for a in feature_adrs}
    return {
        "tag_count": len(tags),
        "highest_tag": ".".join(map(str, tags[-1])) if tags else None,
        "feature_adr_count": len(feature_adrs),
        "highest_feature_adr": (".".join(map(str, feature_adrs[-1])) if feature_adrs else None),
        "adr_minors_without_release": sorted(adr_minors - tag_minors),
        "released_minors_without_adr": sorted(tag_minors - adr_minors),
        "adr_minor_gaps": sorted(set(range(1, max(adr_minors) + 1)) - adr_minors)
        if adr_minors
        else [],
    }


def rename_events(ledger: Path) -> RenameCensus:
    """Count identifier renames in the ledger, grouped by declared reason."""
    reasons: Counter[str] = Counter()
    if not ledger.exists():
        return RenameCensus(total=0, by_reason={})
    with ledger.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("event") != "artifact_renamed":
                continue
            reason = event.get("reason") or event.get("extra", {}).get("reason") or "?"
            reasons[str(reason).split(" (")[0]] += 1
    return RenameCensus(total=sum(reasons.values()), by_reason=dict(reasons.most_common()))


def _ledger_adr_semvers(ledger: Path) -> set[str]:
    """Collect every ADR semver the ledger records as having really existed.

    Read from the ``id`` fields of ``adr_created`` and ``artifact_renamed``
    events only, never from a raw line scan: tests write their own fixture
    payloads into this file, so a substring match over the text reports ids like
    ``ADR-9.9.9`` that no ADR ever bore. Including ids that are gone from disk is
    the point -- a demoted ADR left its citations behind.
    """
    seen: set[str] = set()
    if not ledger.exists():
        return seen
    head = re.compile(r"^ADR-(\d+\.\d+\.\d+)")
    with ledger.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            name = event.get("event")
            if name == "adr_created":
                candidates = [event.get("id")]
            elif name == "artifact_renamed":
                extra = event.get("extra") or {}
                candidates = [
                    event.get("old_id") or extra.get("old_id"),
                    event.get("new_id") or extra.get("new_id"),
                ]
            else:
                continue
            for value in candidates:
                if (m := head.match(str(value or ""))) is not None:
                    seen.add(m.group(1))
    return seen


def req_population() -> ReqCensus:
    """REQ identifiers on disk, the surfaces citing them, and orphaned citations.

    An orphan is a cited REQ id with no brief on disk. Orphans split three ways
    and only two are defects. Judging "fixture" by absence from disk alone is
    wrong, and wrong in the direction that hides the interesting case: an ADR
    demoted to pool is ALSO absent from disk, and its briefs were destroyed with
    it, so its surviving citations are the sharpest casualties there are. The
    ledger is therefore consulted for ADR ids that once existed.

    - parent ADR on disk  -> casualty, the brief or index moved beneath it
    - parent ADR in ledger only -> casualty, the parent was demoted and its
      briefs deleted
    - parent ADR unknown to both -> synthetic test fixture, not a defect

    Only ids inside a ``@covers(...)`` call or an ``@REQ-`` scenario tag count as
    citations; a bare id in a test body is a literal under test, not a claim.
    """
    adr_root = REPO / "docs" / "design" / "adr"
    on_disk_semvers = {
        m.group(1)
        for d in adr_root.rglob("ADR-*")
        if (m := re.match(r"^ADR-(\d+\.\d+\.\d+)-", d.name))
    }
    ever_known = set(on_disk_semvers) | _ledger_adr_semvers(REPO / ".gzkit" / "ledger.jsonl")

    on_disk: set[str] = set()
    for brief in adr_root.rglob("OBPI-*.md"):
        on_disk.update(REQ_ID.findall(brief.read_text(encoding="utf-8", errors="ignore")))

    citations: dict[str, list[str]] = {}
    for test in (REPO / "tests").rglob("*.py"):
        text = test.read_text(encoding="utf-8", errors="ignore")
        for call in COVERS_CALL.finditer(text):
            line = text[: call.start()].count("\n") + 1
            rel = test.relative_to(REPO)
            for rid in REQ_ID.findall(call.group(1)):
                citations.setdefault(rid, []).append(f"{rel}:{line}")
    features = REPO / "features"
    if features.exists():
        for feat in features.rglob("*.feature"):
            rel = feat.relative_to(REPO)
            for rid in REQ_ID.findall(feat.read_text(encoding="utf-8", errors="ignore")):
                citations.setdefault(rid, []).append(str(rel))

    orphans = {rid: sites for rid, sites in citations.items() if rid not in on_disk}
    cause: dict[str, str] = {}
    for rid in orphans:
        m = REQ_PARENT.match(rid)
        parent = m.group(1) if m else ""
        if parent in on_disk_semvers:
            cause[rid] = "parent-on-disk"
        elif parent in ever_known:
            cause[rid] = "parent-demoted"
    casualties = {rid: sites for rid, sites in orphans.items() if rid in cause}
    return ReqCensus(
        distinct_on_disk=len(on_disk),
        distinct_cited=len(citations),
        orphan_citations=len(orphans),
        orphans_synthetic_fixture=len(orphans) - len(casualties),
        traceability_casualties=len(casualties),
        casualty_sites=dict(sorted(casualties.items())),
        casualty_cause=dict(sorted(cause.items())),
    )


def baseline_vocabulary() -> dict[str, object]:
    """Where the word "baseline" is used, and for what.

    12207:2026 § 3.1.12 reserves it for an approved, fixed version of a
    configuration item. This counts uses without judging them; the analysis
    reads the sites.
    """
    hits: Counter[str] = Counter()
    for src in (REPO / "src" / "gzkit").rglob("*.py"):
        for word in BASELINE_WORD.findall(src.read_text(encoding="utf-8", errors="ignore")):
            hits[word] += 1
    data = REPO / "data"
    artifacts = sorted(p.name for p in data.glob("*baseline*")) if data.exists() else []
    return {
        "occurrences_in_src": sum(hits.values()),
        "distinct_spellings": len(hits),
        "top_spellings": dict(hits.most_common(8)),
        "baseline_named_data_files": artifacts,
    }


def release_surfaces() -> dict[str, object]:
    """Size of the release-facing prose surfaces, against the ledger."""
    out: dict[str, object] = {}
    for name in ("RELEASE_NOTES.md", "CHANGELOG.md"):
        path = REPO / name
        out[name] = (
            {"bytes": path.stat().st_size, "lines": len(path.read_bytes().splitlines())}
            if path.exists()
            else None
        )
    ledger = REPO / ".gzkit" / "ledger.jsonl"
    out["ledger.jsonl"] = (
        {"bytes": ledger.stat().st_size, "rows": sum(1 for _ in ledger.open("rb"))}
        if ledger.exists()
        else None
    )
    return out


def main() -> int:
    """Run the census and print it as prose or JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of prose")
    args = parser.parse_args()

    rename = rename_events(REPO / ".gzkit" / "ledger.jsonl")
    reqs = req_population()
    report = {
        "head": git("rev-parse", "HEAD").strip() or None,
        "version_lines": version_lines(),
        "rename_events": rename,
        "req_population": reqs,
        "baseline_vocabulary": baseline_vocabulary(),
        "release_surfaces": release_surfaces(),
    }

    if args.json:
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    vl = report["version_lines"]
    print(f"HEAD {report['head']}")
    print("\n-- the two version lines --")
    print(f"  shipped tags        : {vl['tag_count']} (highest {vl['highest_tag']})")
    print(f"  feature ADR ids     : {vl['feature_adr_count']}")
    print(f"  highest feature ADR : {vl['highest_feature_adr']}")
    print(f"  ADR minors w/o rel. : {vl['adr_minors_without_release']}")
    print(f"  released w/o ADR    : {vl['released_minors_without_adr']}")
    print(f"  ADR minor gaps      : {vl['adr_minor_gaps']}")
    re_ = rename
    print(f"\n-- identifier renames ({re_['total']}) --")
    for reason, count in re_["by_reason"].items():
        print(f"  {count:5d}  {reason}")
    rp = reqs
    print("\n-- REQ identifiers --")
    print(f"  distinct on disk      : {rp['distinct_on_disk']}")
    print(f"  distinct cited        : {rp['distinct_cited']}")
    print(f"  orphan citations      : {rp['orphan_citations']}")
    print(f"    synthetic fixtures  : {rp['orphans_synthetic_fixture']}")
    print(f"    REAL casualties     : {rp['traceability_casualties']}")
    for rid, sites in rp["casualty_sites"].items():
        print(f"      {rid}  [{rp['casualty_cause'][rid]}]  <- {sites[0]}")
    bv = report["baseline_vocabulary"]
    print("\n-- 'baseline' vocabulary --")
    print(f"  occurrences in src  : {bv['occurrences_in_src']}")
    print(f"  distinct spellings  : {bv['distinct_spellings']}")
    print(f"  baseline data files : {bv['baseline_named_data_files']}")
    print("\n-- release surfaces --")
    for name, stat in report["release_surfaces"].items():
        print(f"  {name:20s} {stat}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
