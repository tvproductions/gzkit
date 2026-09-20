"""Detect transcribed sibling-state annotations that have decayed (row 3, R&D 2026-09-20).

An issue body that writes ``#889 (open)`` transcribes a Layer-2 fact -- GitHub's issue
state -- into prose that never reconciles. The annotation was TRUE when authored and
silently becomes false the moment the sibling closes. Measured 2026-09-20: five of the
ten such annotations in the open queue were already false.

**The remedy this chore recommends is subtractive, and the body is never rewritten.**
``#889 (open)`` is a dated record of what its author observed; editing it to ``(closed)``
falsifies the record, which is the move ``AGENTS.md`` forbids for every other archive.
GitHub already renders issue state live, so the durable form is a bare ``#889`` and the
correct fix is to stop writing the second copy -- the same subtraction GHI #768 ruled for
transcribed ADR counts, and the same clause the advisory scorecard scores at row ``17h``.

**Scope is the ANNOTATED form only, and that bound is real.** The detector binds an
annotation to the reference immediately preceding it. Prose that merely *reasons* as if a
sibling were open -- GHI #969's argument rests on #889 being open without ever writing
``(open)`` -- is invisible here and needs a reader. The R&D record's larger count included
those; this gate does not claim them.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

#: Shrink-only disclosure of annotations already decayed when this chore landed.
BASELINE_PATH = Path("data") / "ghi_cross_reference_baseline.json"

#: Upper bound for the issue census; a full result at this size means truncation.
CENSUS_LIMIT = 2000

#: ``#889 (open)`` / ``**#929** (open)`` / ``#533 (still open)`` -- the annotation must
#: follow the reference it annotates. A window-based match reads ``(open)`` from a
#: neighbouring clause: the first draft of this detector did exactly that and returned
#: nine hits for five real ones, a 44% false-positive rate.
ANNOTATION_RE = re.compile(r"#(\d+)\*{0,2}\s*\((open|still open)\)", re.IGNORECASE)


def fetch_issues():
    """Return every issue with number, state and body, refusing a truncated census."""
    proc = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--state",
            "all",
            "--limit",
            str(CENSUS_LIMIT),
            "--json",
            "number,state,body,title",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gh issue list failed: {proc.stderr.strip()}")
    issues = json.loads(proc.stdout)
    if len(issues) >= CENSUS_LIMIT:
        raise RuntimeError(
            f"census returned {len(issues)} at limit {CENSUS_LIMIT}: page may be truncated"
        )
    return issues


def scan(issues):
    """Return (decayed, total) annotations across open bodies.

    An annotation is decayed when an OPEN body asserts a sibling is open and that
    sibling is CLOSED.
    """
    state = {i["number"]: i["state"] for i in issues}
    decayed, total = [], 0
    for issue in sorted((i for i in issues if i["state"] == "OPEN"), key=lambda i: i["number"]):
        for match in ANNOTATION_RE.finditer(issue["body"] or ""):
            sibling = int(match.group(1))
            if sibling not in state:
                continue
            total += 1
            if state[sibling] == "CLOSED":
                decayed.append({"issue": issue["number"], "cites": sibling})
    return decayed, total


def load_baseline():
    """Return the disclosed (issue, cites) pairs; a malformed file reads as empty."""
    if not BASELINE_PATH.exists():
        return set()
    try:
        data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        return {(e["issue"], e["cites"]) for e in data.get("disclosed", [])}
    except (json.JSONDecodeError, KeyError, TypeError):
        return set()


def self_test():
    """Assert detector semantics with no network and no repo state."""
    issues = [
        {"number": 1, "state": "OPEN", "body": "see #2 (open) and #3 (open)", "title": ""},
        {"number": 2, "state": "CLOSED", "body": "", "title": ""},
        {"number": 3, "state": "OPEN", "body": "", "title": ""},
        # The window trap: a correct "(closed)" list must not lend "(open)" to its neighbours.
        {"number": 4, "state": "OPEN", "body": "#3 (open) -- #2, #5 (closed) -- done", "title": ""},
        {"number": 5, "state": "CLOSED", "body": "", "title": ""},
        # Bold form, and an unknown sibling that must not be counted at all.
        {"number": 6, "state": "OPEN", "body": "**#2** (open) plus #9999 (open)", "title": ""},
    ]
    decayed, total = scan(issues)
    pairs = {(d["issue"], d["cites"]) for d in decayed}
    assert pairs == {(1, 2), (6, 2)}, pairs
    assert total == 4, total  # #2,#3 from 1; #3 from 4; #2 from 6; #9999 unknown, uncounted
    assert not scan([])[0], "empty census must yield no findings"
    assert load_baseline() is not None
    print("self-test: OK")
    return 0


def main(argv=None):
    """Scan, report, and fail closed on decay the baseline does not disclose."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--report", action="store_true", help="print the scan, always exit 0")
    parser.add_argument("--self-test", action="store_true", help="deterministic, no network")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    decayed, total = scan(fetch_issues())
    rate = f"{len(decayed) / total:.0%}" if total else "n/a"
    print(f"transcribed sibling-state annotations: {total}")
    print(f"decayed (body asserts OPEN, sibling CLOSED): {len(decayed)}  -> rate {rate}")
    for entry in decayed:
        print(f"  #{entry['issue']} asserts #{entry['cites']} is open; it is closed")

    if args.report:
        return 0

    undisclosed = [d for d in decayed if (d["issue"], d["cites"]) not in load_baseline()]
    if undisclosed:
        print(f"\nUNDISCLOSED decay: {len(undisclosed)}")
        for entry in undisclosed:
            print(f"  #{entry['issue']} -> #{entry['cites']}")
        print(
            "\nThe debt may not grow silently. Do NOT rewrite the body -- the annotation was\n"
            "true when authored. Route: stop transcribing sibling state at authoring time\n"
            "(ghi-author), or disclose the instance in data/ghi_cross_reference_baseline.json\n"
            "with a reason. Shrink-only: an entry records an absence, it does not justify one."
        )
        return 1
    print("\nAll decay is disclosed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
