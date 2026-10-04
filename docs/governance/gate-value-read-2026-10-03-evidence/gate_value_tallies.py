"""Tallies behind the gate-by-gate value read of 2026-10-03.

Read-only. Counts, from the ledger and the ARB receipts, how often each gate ran
and how often it returned something other than a pass. Run from the repository
root:

    uv run python docs/governance/gate-value-read-2026-10-03-evidence/gate_value_tallies.py

It counts verdicts. It does not judge what a non-pass caught: that reading is in
the README beside this script and was made by reading the records themselves.
A reviewer receipt's verdict and finding count are taken from its `stdout_tail`
by pattern, so a receipt whose output was truncated can be undercounted.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

LEDGER = Path(".gzkit/ledger.jsonl")
RECEIPTS = Path("artifacts/receipts")

# Ledger event -> the fields whose values are its verdict.
VERDICT_FIELDS = {
    "gate_checked": ("gate", "status"),
    "brief_reconciled": ("has_drift", "applied"),
    "adr_eval_completed": ("verdict",),
    "adversarial_validation": ("verdict",),
    "airlock_in": ("decision",),
    "airlock_out": ("verdict",),
    "acceptance_recorded": ("record_type",),
    "audit_generated": ("passed",),
    "enforcement_claim_verified": ("outcome",),
    "red_receipt_emitted": ("failure_class",),
    "red_commit_receipt_emitted": ("verdict",),
    "obpi_completion_repudiated": ("cause",),
}
PLAIN_CHECKS = (
    "arb-ruff",
    "arb-step-unittest",
    "arb-step-typecheck",
    "arb-step-mkdocs",
    "arb-step-behave",
)
REVIEWERS = ("specreview", "qualityreview", "codexadversary")
RECEIPT_KIND = re.compile(r"(arb-(?:step-)?[a-z\-]+?)-[0-9a-f]{12,}")
VERDICT = re.compile(r'"verdict"\s*:\s*"([^"]+)"')
FINDING = re.compile(r'"description"\s*:')


def ledger_rows() -> list[dict]:
    """Return every ledger row."""
    with LEDGER.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def ledger_tallies(rows: list[dict]) -> dict[str, object]:
    """Count rows per event and the verdict values of the verdict-carrying events."""
    by_event: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_event[row["event"]].append(row)
    verdicts = {
        event: dict(
            Counter(
                "/".join(str(row.get(f)) for f in fields) for row in by_event[event]
            ).most_common()
        )
        for event, fields in VERDICT_FIELDS.items()
    }
    proofs = [
        r["payload"].get("valid")
        for r in by_event["acceptance_recorded"]
        if r.get("record_type") == "proof"
    ]
    return {
        "rows": len(rows),
        "last_ts": rows[-1]["ts"],
        "rows_per_event": dict(Counter(row["event"] for row in rows).most_common()),
        "verdicts": verdicts,
        "acceptance_proof_valid": dict(Counter(str(v) for v in proofs)),
    }


def receipt_tallies() -> dict[str, object]:
    """Count ARB receipts by kind and exit status, and reviewer verdicts and findings."""
    exits: dict[str, Counter] = defaultdict(Counter)
    reviewers: dict[str, dict[str, object]] = {}
    for path in sorted(RECEIPTS.glob("*.json")):
        match = RECEIPT_KIND.match(path.name)
        kind = match.group(1) if match else path.name
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            exits[kind]["unparseable"] += 1
            continue
        exits[kind][str(receipt.get("exit_status"))] += 1
    for name in REVIEWERS:
        verdicts: Counter = Counter()
        findings = with_findings = truncated = 0
        for path in RECEIPTS.glob(f"arb-step-{name}-*.json"):
            receipt = json.loads(path.read_text(encoding="utf-8"))
            out = receipt.get("stdout_tail") or ""
            found = VERDICT.findall(out)
            verdicts[found[-1] if found else "no-verdict-field"] += 1
            count = len(FINDING.findall(out))
            findings += count
            with_findings += count > 0
            truncated += bool(receipt.get("stdout_truncated"))
        reviewers[name] = {
            "receipts": sum(verdicts.values()),
            "verdicts": dict(verdicts.most_common()),
            "with_findings": with_findings,
            "findings": findings,
            "stdout_truncated": truncated,
        }
    plain = {kind: dict(exits[kind]) for kind in PLAIN_CHECKS}
    plain_total = sum(sum(c.values()) for c in plain.values())
    plain_nonzero = plain_total - sum(c.get("0", 0) for c in plain.values())
    return {
        "receipts": sum(sum(c.values()) for c in exits.values()),
        "plain_checks": plain,
        "plain_checks_total": plain_total,
        "plain_checks_nonzero": plain_nonzero,
        "reviewers": reviewers,
    }


def main() -> None:
    """Print the tallies as JSON."""
    report = {"ledger": ledger_tallies(ledger_rows()), "receipts": receipt_tallies()}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
