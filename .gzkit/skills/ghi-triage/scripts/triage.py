#!/usr/bin/env python3
"""ghi-triage: fetch open GHIs, score routing, render table + short list.

Self-contained to the skill directory. Uses Rich (already a gzkit project
dependency) for table rendering. Invoke via:

    uv run python .claude/skills/ghi-triage/scripts/triage.py [args]

Routing thresholds: AGENTS.md § Defect-fix routing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

# --- Markdown renderer (default) ---------------------------------------------


def _md_escape(s: str) -> str:
    """Escape pipes and collapse newlines so a cell stays one markdown row."""
    return s.replace("|", "\\|").replace("\n", " ").strip()


def render_markdown(issues: list[Issue], precedent: int, duplicates: dict[int, int]) -> str:
    precedent_ok = precedent >= 3
    triaged: list[tuple[Issue, str, str]] = []
    for issue in issues:
        r = route(issue, precedent_ok, duplicates)
        u = urgency(issue, r)
        triaged.append((issue, r, u))
    triaged.sort(key=lambda x: (URGENCY_RANK[x[2]], x[0].number))

    lines: list[str] = []
    lines.append(
        f"**GHI Triage** — {len(issues)} open issues | `fix()` precedent (60d): **{precedent}**\n"
    )
    lines.append("| # | Class | Route | Urgency | Title | Rationale |")
    lines.append("|---:|---|---|---|---|---|")
    for issue, r, u in triaged:
        cells = [
            str(issue.number),
            _md_escape(issue.klass),
            _md_escape(ROUTE_LABEL[r]),
            _md_escape(u),
            _md_escape(issue.title),
            _md_escape(rationale(issue, r, duplicates)),
        ]
        lines.append("| " + " | ".join(cells) + " |")

    lines.append("")
    lines.append("**Short list (copy/paste):**")
    lines.append("")
    lines.append("```text")
    last_urgency: str | None = None
    for issue, r, u in triaged:
        if last_urgency is not None and u != last_urgency:
            lines.append("")
        last_urgency = u
        lines.append(f"#{issue.number} — {ROUTE_LABEL[r]:<10} — {issue.title}")
    lines.append("```")
    return "\n".join(lines)


# --- Heuristic signals --------------------------------------------------------

_OBPI_SIGNALS = (
    re.compile(r"\bADR amendment\b", re.I),
    re.compile(r"\bcrosses\s+(brief|ADR)\b", re.I),
    re.compile(r"\bscope\s+expansion\b", re.I),
    re.compile(r"\bschema\s+change\b", re.I),
    re.compile(r"\bcontract\s+change\b", re.I),
    re.compile(r"\bnew\s+CLI\s+(verb|subcommand|flag)\b", re.I),
    re.compile(r"\bre[-\s]?open(s|ed)?\s+an?\s+attested\b", re.I),
    re.compile(r"\bpartial\s+Absorb\b", re.I),
    re.compile(r"\bbrief\s+boundary\b", re.I),
    re.compile(r"\bplan[-\s]?mode\s+gate\b", re.I),
)

_NOW_SIGNALS = (
    re.compile(r"\bblocks?\b", re.I),
    re.compile(r"\bdeadlocks?\b", re.I),
    re.compile(r"\bbroken\b", re.I),
    re.compile(r"\bcurrently\s+(fails|failing)\b", re.I),
    re.compile(r"\bfails?\s+for\b", re.I),
    re.compile(r"\bfalse[-\s]?positive\b", re.I),
)

_PATH_RE = re.compile(r"`([\w./\-]+\.(?:py|md|json|yml|yaml|feature|toml))`")
_FENCE_RE = re.compile(r"```.*?```", re.S)


@dataclass
class Issue:
    number: int
    title: str
    labels: list[str]
    body: str
    created_at: str
    updated_at: str

    @property
    def klass(self) -> str:
        for label in ("defect", "enhancement", "investigation", "chore"):
            if label in self.labels:
                return label
        return "unlabeled"

    @property
    def unique_paths(self) -> set[str]:
        body = _FENCE_RE.sub("", self.body or "")
        return {m.group(1) for m in _PATH_RE.finditer(body)}


# --- Data acquisition --------------------------------------------------------


def _require(binary: str) -> None:
    if shutil.which(binary) is None:
        sys.stderr.write(f"ghi-triage: required binary not found on PATH: {binary}\n")
        sys.exit(2)


def fetch(limit: int, label: str | None) -> list[Issue]:
    _require("gh")
    cmd = [
        "gh",
        "issue",
        "list",
        "--state",
        "open",
        "--limit",
        str(limit),
        "--json",
        "number,title,labels,createdAt,updatedAt,body",
    ]
    if label:
        cmd += ["--label", label]
    raw = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding="utf-8")
    data = json.loads(raw.stdout)
    return [
        Issue(
            number=i["number"],
            title=i["title"],
            labels=[lbl["name"] for lbl in i["labels"]],
            body=i.get("body") or "",
            created_at=i["createdAt"],
            updated_at=i["updatedAt"],
        )
        for i in data
    ]


def fix_precedent_count() -> int:
    _require("git")
    out = subprocess.run(
        ["git", "log", "--since=60 days ago", "--oneline", "--grep=^fix("],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    return sum(1 for line in out.stdout.splitlines() if line.strip())


def detect_duplicates(issues: list[Issue]) -> dict[int, int]:
    by_title: dict[str, list[Issue]] = {}
    for i in issues:
        by_title.setdefault(i.title.strip().lower(), []).append(i)
    duplicates: dict[int, int] = {}
    for group in by_title.values():
        if len(group) > 1:
            canonical = min(group, key=lambda x: x.number)
            for dup in group:
                if dup.number != canonical.number:
                    duplicates[dup.number] = canonical.number
    return duplicates


# --- Routing logic -----------------------------------------------------------


def route(issue: Issue, precedent_ok: bool, duplicates: dict[int, int]) -> str:
    if issue.number in duplicates:
        return "close-dup"
    if not precedent_ok:
        return "ambiguous"
    body = issue.body or ""
    if any(p.search(body) or p.search(issue.title) for p in _OBPI_SIGNALS):
        return "OBPI-ceremony"
    paths = issue.unique_paths
    if len(paths) > 3:
        return "OBPI-ceremony"
    if re.search(r"\bOBPI-\d+\.\d+\.\d+-\d+\b", issue.title) and "premise broken" in body.lower():
        return "OBPI-ceremony"
    return "direct-fix"


def urgency(issue: Issue, route_label: str) -> str:
    if route_label == "close-dup":
        return "later"
    body = issue.body or ""
    if any(p.search(body) for p in _NOW_SIGNALS):
        return "now"
    if issue.klass == "chore":
        return "later"
    return "soon"


def rationale(issue: Issue, route_label: str, duplicates: dict[int, int]) -> str:
    if route_label == "close-dup":
        return f"Duplicate of #{duplicates[issue.number]}"
    paths = issue.unique_paths
    body = issue.body or ""
    parts: list[str] = []
    if paths:
        parts.append(f"{len(paths)} file{'s' if len(paths) != 1 else ''}")
    for p in _OBPI_SIGNALS:
        m = p.search(body) or p.search(issue.title)
        if m:
            parts.append(f"signal: {m.group(0)!r}")
            break
    for p in _NOW_SIGNALS:
        m = p.search(body)
        if m:
            parts.append(f"blocking: {m.group(0)!r}")
            break
    if not parts:
        parts.append("thin body — manual review")
    return "; ".join(parts)


URGENCY_RANK = {"now": 0, "soon": 1, "later": 2}
ROUTE_LABEL = {
    "direct-fix": "direct-fix",
    "OBPI-ceremony": "OBPI",
    "ambiguous": "ambiguous",
    "close-dup": "close",
}

# Color map for at-a-glance scanning.
URGENCY_STYLE = {"now": "bold red", "soon": "yellow", "later": "dim"}
ROUTE_STYLE = {
    "direct-fix": "green",
    "OBPI": "magenta",
    "ambiguous": "yellow",
    "close": "dim",
}
CLASS_STYLE = {
    "defect": "red",
    "enhancement": "cyan",
    "investigation": "blue",
    "chore": "dim",
    "unlabeled": "dim italic",
}


# --- Rendering ---------------------------------------------------------------


def _make_console(width: int | None) -> Console:
    """Force Rich to render a real table even under non-TTY capture.

    Rich detects whether stdout is a TTY and silently downgrades box drawing,
    color, and column ratios when it isn't (e.g. captured by a tool harness).
    For triage we always want the full Rich table, so:

    - `force_terminal=True` keeps box characters and ANSI color
    - explicit `width` defeats the 80-col fallback (env GHI_TRIAGE_WIDTH or --width)
    """
    if width is None:
        env = os.environ.get("GHI_TRIAGE_WIDTH")
        if env and env.isdigit():
            width = int(env)
        else:
            width = shutil.get_terminal_size((140, 20)).columns
            width = max(width, 140)
    return Console(force_terminal=True, color_system="truecolor", width=width)


def render(
    issues: list[Issue],
    precedent: int,
    duplicates: dict[int, int],
    width: int | None = None,
) -> None:
    console = _make_console(width)
    precedent_ok = precedent >= 3

    triaged: list[tuple[Issue, str, str]] = []
    for issue in issues:
        r = route(issue, precedent_ok, duplicates)
        u = urgency(issue, r)
        triaged.append((issue, r, u))
    triaged.sort(key=lambda x: (URGENCY_RANK[x[2]], x[0].number))

    console.print(
        f"\n[bold]GHI Triage[/bold] — {len(issues)} open issues | "
        f"fix() precedent (60d): [bold]{precedent}[/bold]\n"
    )

    table = Table(
        box=box.ROUNDED,
        show_lines=True,
        header_style="bold",
        expand=True,
        pad_edge=False,
    )
    table.add_column("#", justify="right", style="bold", no_wrap=True)
    table.add_column("Class", no_wrap=True)
    table.add_column("Route", no_wrap=True)
    table.add_column("Urgency", no_wrap=True)
    table.add_column("Title", overflow="fold", ratio=3)
    table.add_column("Rationale", overflow="fold", ratio=2)

    for issue, r, u in triaged:
        route_label = ROUTE_LABEL[r]
        table.add_row(
            str(issue.number),
            Text(issue.klass, style=CLASS_STYLE.get(issue.klass, "")),
            Text(route_label, style=ROUTE_STYLE.get(route_label, "")),
            Text(u, style=URGENCY_STYLE.get(u, "")),
            issue.title,
            rationale(issue, r, duplicates),
        )
    console.print(table)

    console.print("\n[bold]Short list (copy/paste):[/bold]\n")
    last_urgency: str | None = None
    for issue, r, u in triaged:
        if last_urgency is not None and u != last_urgency:
            console.print("")
        last_urgency = u
        console.print(
            f"#{issue.number} — {ROUTE_LABEL[r]:<10} — {issue.title}",
            highlight=False,
            markup=False,
        )
    console.print("")


def main() -> int:
    p = argparse.ArgumentParser(description="Triage open GHIs")
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--label", default=None, help="Filter by single label")
    p.add_argument(
        "--format",
        choices=("markdown", "rich"),
        default="markdown",
        help="Output format (default: markdown — renders cleanly through "
        "any markdown consumer; use 'rich' for direct-terminal use).",
    )
    p.add_argument(
        "--width",
        type=int,
        default=None,
        help="Rich render width override (only with --format rich)",
    )
    args = p.parse_args()

    issues = fetch(args.limit, args.label)
    if not issues:
        print("No open issues.")
        return 0
    precedent = fix_precedent_count()
    duplicates = detect_duplicates(issues)
    if args.format == "rich":
        render(issues, precedent, duplicates, width=args.width)
    else:
        print(render_markdown(issues, precedent, duplicates))
    return 0


if __name__ == "__main__":
    sys.exit(main())
