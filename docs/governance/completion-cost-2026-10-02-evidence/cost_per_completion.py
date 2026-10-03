"""Cost per OBPI completion, by completion month (read-only analysis)."""

import bisect
import collections
import datetime as dt
import json
import re
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCR = Path(__file__).parent
CUTOFF = "2026-04-01"
SHORT = re.compile(r"OBPI-(\d+\.\d+\.\d+)-(\d+)(?!\d)")


def ts(s):
    """Parse an ISO timestamp (a trailing Z allowed) into an aware UTC datetime."""
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.UTC)


def short_of(full):
    """Return the short ``OBPI-X.Y.Z-NN`` form of a full OBPI slug."""
    m = SHORT.match(full)
    return f"OBPI-{m.group(1)}-{m.group(2)}" if m else full


ledger_lines = (REPO / ".gzkit/ledger.jsonl").read_text(encoding="utf-8").splitlines()
events = [json.loads(line) for line in ledger_lines if line.strip()]
for e in events:
    e["_t"] = ts(e["ts"])

# ---- index OBPI-bearing events by full id ---------------------------------
by_obpi = collections.defaultdict(list)
parent_of = {}
parked = set()
adr_gate = collections.defaultdict(list)  # adr full id -> gate_checked events
for e in events:
    keys = set()
    for k in ("id", "obpi_id", "parent", "brief_id"):
        v = e.get(k)
        if isinstance(v, str) and v.startswith("OBPI-"):
            keys.add(v)
    if e["event"] == "artifact_edited" and "OBPI-" in str(e.get("path", "")):
        m = re.search(r"(OBPI-[\w.-]+?)\.md", str(e.get("path")))
        if m:
            keys.add(m.group(1))
    for k in keys:
        by_obpi[k].append(e)
    if e["event"] == "obpi_created":
        parent_of[e["id"]] = e.get("parent")
    if e["event"] == "obpi_parked":
        parked.add(e["id"])
    if e["event"] == "obpi_receipt_emitted":
        parent_of.setdefault(e["id"], e.get("parent"))
    if e["event"] == "gate_checked":
        adr_gate[e["id"]].append(e)

all_full = set(parent_of) | set(by_obpi)
short_map = collections.defaultdict(set)
for f in all_full:
    if SHORT.match(f):
        short_map[short_of(f)].add(f)

# ---- completions ------------------------------------------------------------
receipts = collections.defaultdict(list)
repud = collections.defaultdict(list)
for e in events:
    if e["event"] == "obpi_receipt_emitted" and e.get("receipt_event") == "completed":
        receipts[e["id"]].append(e)
    if e["event"] == "obpi_completion_repudiated":
        repud[e["id"]].append(e)

# ---- git ---------------------------------------------------------------------
commits = []
raw = (SCR / "cost_gitlog.txt").read_text(errors="replace")
for rec in raw.split("\x1e")[1:]:
    h, d, s, b = (rec.split("\x1f") + ["", "", "", ""])[:4]
    if s.rstrip().endswith("(gz git-sync)"):
        continue  # git-sync bodies enumerate changed file paths -> inflate
    cited = {f"OBPI-{a}-{n}" for a, n in SHORT.findall(s + "\n" + b)}
    full = set(re.findall(r"OBPI-\d+\.\d+\.\d+-\d+-[a-z0-9-]*[a-z0-9]", s + "\n" + b))
    commits.append((ts(d), cited, full))
commits_by_short = collections.defaultdict(list)
commits_by_full = collections.defaultdict(list)
for t, cited, full in commits:
    for c in cited:
        commits_by_short[c].append(t)
    for f in full:
        commits_by_full[f].append(t)

# ---- handoffs ------------------------------------------------------------------
handoffs_by_short = collections.defaultdict(list)
for p in list((REPO / ".gzkit/handoffs").glob("*.md")) + list(
    (REPO / ".gzkit/handoffs/archive").glob("*.md")
):
    txt = p.read_text(errors="replace")
    m = re.search(r'^timestamp:\s*"?([0-9T:\-+.Z]+)', txt, re.M)
    t = None
    if m:
        try:
            t = ts(m.group(1))
        except ValueError:
            t = None
    if t is None:
        m2 = re.match(r"(\d{4})-?(\d{2})-?(\d{2})", p.name)
        if m2:
            t = dt.datetime(int(m2[1]), int(m2[2]), int(m2[3]), 12, tzinfo=dt.UTC)
    cited = {f"OBPI-{a}-{n}" for a, n in SHORT.findall(txt + " " + p.name)}
    for c in cited:
        handoffs_by_short[c].append((t, p.name))

# ---- issues ----------------------------------------------------------------------
issue_ts = sorted(
    ts(i["createdAt"]) for i in json.loads((SCR / "cost_issues.json").read_text(encoding="utf-8"))
)


def issues_between(a, b):
    """Count GitHub issues created between two instants, inclusive."""
    return bisect.bisect_right(issue_ts, b) - bisect.bisect_left(issue_ts, a)


FAIL_EVENTS = {
    "brief_reconcile_drift_detected",
    "task_blocked",
    "obpi_blocked_on_operator",
    "obpi_lock_ttl_warning",
    "brief_reconcile_drift_overridden",
    "security_floor_overridden",
}

rows = []
for oid, recs in receipts.items():
    recs.sort(key=lambda e: e["_t"])
    first = recs[0]
    if first["ts"] < CUTOFF:
        continue
    comp = first["_t"]
    evs = sorted(by_obpi[oid], key=lambda e: e["_t"])
    locks = [e for e in evs if e["event"] == "obpi_lock_claimed" and e["_t"] <= comp]
    pipe = [
        e
        for e in evs
        if e["event"]
        in ("pipeline_launched", "stage2_dispatch_recorded", "task_started", "red_receipt_emitted")
        and e["_t"] <= comp
    ]
    created = [e for e in evs if e["event"] == "obpi_created"]
    if locks:
        start, anchor = locks[0]["_t"], "lock"
    elif pipe:
        start, anchor = pipe[0]["_t"], "pipeline/task"
    elif created:
        start, anchor = created[0]["_t"], "created"
    else:
        start, anchor = None, "none"
    win = [e for e in evs if start and start <= e["_t"] <= comp and e is not first]
    types = collections.Counter(e["event"] for e in win)
    fails = collections.Counter()
    for e in win:
        if e["event"] in FAIL_EVENTS:
            fails[e["event"]] += 1
        if e["event"] == "adversarial_validation" and str(e.get("verdict", "")).startswith(
            "refuted"
        ):
            fails["adv_refuted"] += 1
    if types["pipeline_launched"] > 1:
        fails["pipeline_relaunch"] = types["pipeline_launched"] - 1
    if types["obpi_lock_claimed"] > 1:
        fails["lock_reclaim"] = types["obpi_lock_claimed"] - 1
    roles = collections.Counter(
        (e.get("role"), e.get("task_id")) for e in win if e["event"] == "stage2_dispatch_recorded"
    )
    rd = sum(v - 1 for v in roles.values() if v > 1)
    if rd:
        fails["stage2_redispatch"] = rd
    adr = parent_of.get(oid)
    if start and adr:
        gf = sum(
            1
            for g in adr_gate.get(adr, [])
            if start <= g["_t"] <= comp and g.get("status") == "fail"
        )
        if gf:
            fails["parent_adr_gate_fail"] = gf
    sid = short_of(oid)
    amb = sorted(short_map[sid] - {oid})
    call = sorted(commits_by_short.get(sid, []))
    cts = [t for t in call if start and start <= t <= comp + dt.timedelta(hours=1)]
    cfull = sorted(commits_by_full.get(oid, []))
    hos = handoffs_by_short.get(sid, [])
    ho_win = [
        n
        for t, n in hos
        if t and start and start - dt.timedelta(days=1) <= t <= comp + dt.timedelta(days=1)
    ]
    rows.append(
        {
            "id": oid,
            "month": comp.strftime("%Y-%m"),
            "comp": comp,
            "start": start,
            "anchor": anchor,
            "hours": (comp - start).total_seconds() / 3600 if start else None,
            "nevents": len(win),
            "types": types,
            "fails": fails,
            "nfail": sum(fails.values()),
            "ncommits": len(cts),
            "ncommits_all": len(call),
            "ncpost": len(
                [
                    t
                    for t in call
                    if created and created[0]["_t"] <= t <= comp + dt.timedelta(hours=1)
                ]
            ),
            "cspan_days": (
                (
                    comp
                    - min(
                        [
                            t
                            for t in call
                            if created and created[0]["_t"] <= t <= comp + dt.timedelta(hours=1)
                        ]
                    )
                ).total_seconds()
                / 86400
            )
            if [
                t for t in call if created and created[0]["_t"] <= t <= comp + dt.timedelta(hours=1)
            ]
            else None,
            "nfull": len(cfull),
            "fullspan": (cfull[0].date(), cfull[-1].date()) if cfull else None,
            "nev_noacc": sum(1 for e in win if e["event"] != "acceptance_recorded"),
            "late_lock": any(e["event"] == "obpi_lock_claimed" and e["_t"] > comp for e in evs),
            "span": (call[0].date(), call[-1].date()) if call else None,
            "nho": len(hos),
            "nho_win": len(ho_win),
            "issues": issues_between(start, comp) if start else None,
            "nreceipts": len(recs),
            "repudiated": bool(repud.get(oid)),
            "amb": list(amb),
            "amb_parked": [a for a in amb if a in parked],
            "backfill": (first.get("evidence") or {}).get("recorder_source") is None,
        }
    )


def q(vals, p):
    """Return the p-th percentile of the non-None values, or None when there are none."""
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return None
    if p == 50:
        return statistics.median(vals)
    k = max(0, min(len(vals) - 1, round(p / 100 * (len(vals) - 1))))
    return vals[k]


def fmt(v):
    """Render a metric value for the report; None prints as n/d."""
    return "n/d" if v is None else (f"{v:.1f}" if isinstance(v, float) else str(v))


by_m = collections.defaultdict(list)
for r in rows:
    by_m[r["month"]].append(r)
print(
    " | ".join(
        [
            "month n anchors",
            "hours",
            "events",
            "events-excl-acceptance",
            "fails",
            "commits(short,in-window)",
            "commits(short,all-time)",
            "commits(full-slug)",
            "handoffs(win)",
            "handoffs(all)",
            "issues  [each med/p90]",
            "nonlock-with-lock-after-receipt",
            "ambiguousShort",
        ]
    )
)
for m in sorted(by_m):
    R = by_m[m]
    anc = collections.Counter(r["anchor"] for r in R)
    out = [m, len(R), dict(anc)]
    for key in (
        "hours",
        "nevents",
        "nev_noacc",
        "nfail",
        "ncommits",
        "ncommits_all",
        "nfull",
        "nho_win",
        "nho",
        "issues",
        "ncpost",
        "cspan_days",
    ):
        vals = [r[key] for r in R]
        out.append(f"{fmt(q(vals, 50))}/{fmt(q(vals, 90))}")
    out.append(sum(r["late_lock"] for r in R if r["anchor"] != "lock"))
    out.append(f"cspan-derivable={sum(r['cspan_days'] is not None for r in R)}")
    out.append(sum(bool(r["amb"]) for r in R))
    print(*out, sep=" | ")
    # hours for lock-anchored only
    lh = [r["hours"] for r in R if r["anchor"] == "lock"]
    print("   lock-anchored hours med/p90:", fmt(q(lh, 50)), fmt(q(lh, 90)), "n=", len(lh))
    tot = collections.Counter()
    for r in R:
        tot.update(r["fails"])
    print("   fail totals:", dict(tot))
    ty = collections.Counter()
    for r in R:
        ty.update(r["types"])
    print("   event totals:", dict(ty.most_common(12)))

print("\n--- individual Jul-Oct ---")
for r in sorted(rows, key=lambda r: r["comp"]):
    if r["month"] >= (sys.argv[1] if len(sys.argv) > 1 else "2026-08"):
        print(
            r["id"],
            r["comp"].isoformat()[:16],
            "start",
            r["start"] and r["start"].isoformat()[:16],
            r["anchor"],
            "h",
            fmt(r["hours"]),
            "ev",
            r["nevents"],
            "fails",
            dict(r["fails"]),
            "cpost",
            r["ncpost"],
            "cspan_d",
            fmt(r["cspan_days"]),
            "commits win/all/full",
            r["ncommits"],
            r["ncommits_all"],
            r["nfull"],
            "allspan",
            r["span"],
            "fullspan",
            r["fullspan"],
            "ho",
            r["nho_win"],
            "/",
            r["nho"],
            "iss",
            r["issues"],
            "rec",
            r["nreceipts"],
            "repud",
            r["repudiated"],
            "amb",
            r["amb"],
            "parked",
            r["amb_parked"],
            "types",
            dict(r["types"]),
        )
