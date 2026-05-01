#!/usr/bin/env python3
"""ghi-triage: fetch open GHIs, score routing, render deterministic deliverable.

Self-contained to the skill directory. Uses Rich (already a gzkit project
dependency) for the optional terminal-only table view. Invoke via:

    uv run python .claude/skills/ghi-triage/scripts/triage.py [args]

Routing thresholds: AGENTS.md § Defect-fix routing.

Output formats:
  - markdown (default, chat-renderable) — the candidate-set table
  - json — structured records for the agent's judgment pass
  - rank — the deterministic rank-ordered deliverable (requires --rank-input)
  - rich — terminal-only Rich table; explicit opt-in for TTY operators
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
from pathlib import Path

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

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


# --- Precedent count cache ---------------------------------------------------


def _precedent_cache_path() -> Path:
    return Path.home() / ".cache" / "gzkit" / "triage-precedent.json"


def _git_head_sha() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return out.stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _load_precedent_cache(head: str) -> int | None:
    path = _precedent_cache_path()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    entry = payload.get(head)
    if isinstance(entry, int):
        return entry
    return None


def _store_precedent_cache(head: str, count: int) -> None:
    path = _precedent_cache_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                payload = {}
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            payload = {}
        payload[head] = count
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    except OSError:
        pass


def fix_precedent_count() -> int:
    _require("git")
    head = _git_head_sha()
    if head is not None:
        cached = _load_precedent_cache(head)
        if cached is not None:
            return cached
    out = subprocess.run(
        ["git", "log", "--since=60 days ago", "--oneline", "--grep=^fix("],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    count = sum(1 for line in out.stdout.splitlines() if line.strip())
    if head is not None:
        _store_precedent_cache(head, count)
    return count


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
    """Triage routing for an open GHI.

    GHIs are repair vessels for defects; the receipts left on the GHI itself
    are the audit trail. Triage never routes to OBPI — OBPI ceremony is
    reserved for new feature-shape work under an active ADR (operator-
    directed via gz plan / gz-design), not produced from the issue queue.
    Feature-shape signals on a GHI are surfaced through `rationale()` as
    escalation hints for operator judgment, not as a routing flip.
    """
    if issue.number in duplicates:
        return "close-dup"
    if not precedent_ok:
        return "ambiguous"
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
    "ambiguous": "ambiguous",
    "close-dup": "close",
}

# Color map for at-a-glance scanning.
URGENCY_STYLE = {"now": "bold red", "soon": "yellow", "later": "dim"}
ROUTE_STYLE = {
    "direct-fix": "green",
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


# --- Rank deliverable (the agent-fed deterministic output) -------------------


SEVERITY_VALUES = ("blocking", "degrading", "latent")
SEVERITY_RANK = {sev: idx for idx, sev in enumerate(SEVERITY_VALUES)}
WHY_MAX_CHARS = 120
ACTION_MAX_CHARS = 80
_FORBIDDEN_CHARS = set("*_`#|<>\n\r\t")


@dataclass(frozen=True)
class RankItem:
    number: int
    severity: str
    action: str
    why: str


class RankInputError(ValueError):
    """Raised when --rank-input fails the rendering-edge contract."""


def _validate_text_field(value: object, field: str, idx: int, max_chars: int) -> str:
    if not isinstance(value, str):
        raise RankInputError(f"rankings[{idx}].{field} must be a string")
    cleaned = value.strip()
    if not cleaned:
        raise RankInputError(f"rankings[{idx}].{field} required")
    if len(cleaned) > max_chars:
        raise RankInputError(
            f"rankings[{idx}].{field} exceeds {max_chars} chars (got {len(cleaned)})"
        )
    bad = sorted({c for c in cleaned if c in _FORBIDDEN_CHARS})
    if bad:
        raise RankInputError(f"rankings[{idx}].{field} contains forbidden characters: {bad!r}")
    return cleaned


def parse_rank_input(payload: object, known_numbers: set[int]) -> list[RankItem]:
    """Validate agent-supplied rank input.

    Constrains WHY/ACTION shape at the rendering edge so determinism does not
    leak through cognitive freedom on the input side (GHI #324, comment by
    voidborne-d). Cognitive freedom on the input; determinism on the render.
    """
    if not isinstance(payload, dict):
        raise RankInputError("--rank-input must be a JSON object")
    rankings = payload.get("rankings")  # ty: ignore[invalid-argument-type]
    if not isinstance(rankings, list) or not rankings:
        raise RankInputError("--rank-input requires non-empty 'rankings' list")
    items: list[RankItem] = []
    seen: set[int] = set()
    for idx, entry in enumerate(rankings):
        if not isinstance(entry, dict):
            raise RankInputError(f"rankings[{idx}] must be an object")
        number = entry.get("number")  # ty: ignore[invalid-argument-type]
        if not isinstance(number, int) or isinstance(number, bool):
            raise RankInputError(f"rankings[{idx}].number must be int")
        if number in seen:
            raise RankInputError(f"rankings[{idx}].number={number} duplicates earlier entry")
        if number not in known_numbers:
            raise RankInputError(
                f"rankings[{idx}].number={number} not present in fetched issue set"
            )
        seen.add(number)
        severity = entry.get("severity")  # ty: ignore[invalid-argument-type]
        if severity not in SEVERITY_VALUES:
            raise RankInputError(f"rankings[{idx}].severity must be one of {SEVERITY_VALUES}")
        raw_action = entry.get("action")  # ty: ignore[invalid-argument-type]
        raw_why = entry.get("why")  # ty: ignore[invalid-argument-type]
        action = _validate_text_field(raw_action, "action", idx, ACTION_MAX_CHARS)
        why = _validate_text_field(raw_why, "why", idx, WHY_MAX_CHARS)
        items.append(RankItem(number=number, severity=severity, action=action, why=why))
    return items


def render_rank(
    items: list[RankItem],
    issue_index: dict[int, Issue],
    routes: dict[int, str],
    precedent: int,
    total: int,
) -> str:
    """Render the rank-ordered deliverable.

    Deterministic by construction: items render in caller-provided order
    (the agent owns the ranking), every field is validated upstream by
    parse_rank_input, and no formatting branches on environment.
    """
    lines = [
        f"# GHI Triage Ranking — {len(items)} ranked of {total} open "
        f"| fix() precedent (60d): {precedent}",
        "",
    ]
    for rank, item in enumerate(items, start=1):
        title = issue_index[item.number].title
        route_label = routes.get(item.number, "—")
        lines.append(
            f"{rank}. #{item.number} [{item.severity}] {route_label} — {item.action} — {item.why}"
        )
        lines.append(f"   ↳ {title}")
    lines.append("")
    return "\n".join(lines)


# --- Rendering ---------------------------------------------------------------


def _detect_width() -> int:
    """Pick a render width by interrogating the runtime context.

    Resolution order:
      1. GHI_TRIAGE_WIDTH env var (explicit operator override)
      2. COLUMNS env var (parent shell or harness propagation)
      3. shutil.get_terminal_size() when stdout is a real TTY (no cap)
      4. 100 cols (agent-harness display column; no TTY detected)
    """
    env_explicit = os.environ.get("GHI_TRIAGE_WIDTH")
    if env_explicit and env_explicit.isdigit():
        return int(env_explicit)

    env_cols = os.environ.get("COLUMNS")
    if env_cols and env_cols.isdigit():
        return int(env_cols)

    if sys.stdout.isatty():
        return shutil.get_terminal_size((100, 20)).columns

    return 100


def _make_console(width: int | None) -> Console:
    """Force Rich to render a real table even under non-TTY capture.

    Rich downgrades box drawing, color, and column ratios when stdout isn't a
    TTY. We always want the full Rich table, so `force_terminal=True` keeps
    the glyphs and the explicit width defeats the 80-col fallback.
    """
    if width is None:
        width = _detect_width()
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


def render_json(issues: list[Issue], precedent: int, duplicates: dict[int, int]) -> str:
    """Emit triage records for agent consumption.

    The agent uses this to drive per-GHI judgment: full body included so the
    agent does not re-shell `gh issue view` once per issue.
    """
    precedent_ok = precedent >= 3
    records: list[dict] = []
    for issue in issues:
        r = route(issue, precedent_ok, duplicates)
        u = urgency(issue, r)
        records.append(
            {
                "number": issue.number,
                "title": issue.title,
                "labels": issue.labels,
                "klass": issue.klass,
                "body": issue.body,
                "files_mentioned": sorted(issue.unique_paths),
                "dup_of": duplicates.get(issue.number),
                "route": ROUTE_LABEL[r],
                "urgency": u,
                "rationale": rationale(issue, r, duplicates),
                "created_at": issue.created_at,
                "updated_at": issue.updated_at,
            }
        )
    records.sort(key=lambda x: (URGENCY_RANK[x["urgency"]], x["number"]))
    return json.dumps(
        {"precedent_60d": precedent, "count": len(issues), "issues": records},
        indent=2,
    )


def _read_rank_input(path: str | None) -> object:
    if path is None or path == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(path).read_text(encoding="utf-8")
    if not raw.strip():
        raise RankInputError("--rank-input is empty")
    return json.loads(raw)


def main() -> int:
    p = argparse.ArgumentParser(description="Triage open GHIs")
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--label", default=None, help="Filter by single label")
    p.add_argument(
        "--format",
        choices=("markdown", "json", "rank", "rich"),
        default="markdown",
        help="Output format. 'markdown' (default) — chat-renderable table for "
        "operator skim. 'json' — structured records the agent reads to compose "
        "rank input. 'rank' — the deterministic rank-ordered deliverable; "
        "requires --rank-input. 'rich' — terminal-only Rich table with ANSI "
        "color, opt-in for TTY operators.",
    )
    p.add_argument(
        "--rank-input",
        default=None,
        help="Path to a JSON file containing the agent's rank input "
        "({'rankings': [{number, severity, action, why}, ...]}); use '-' for "
        "stdin. Required with --format rank. Validation rules: severity is "
        f"one of {SEVERITY_VALUES}; action ≤{ACTION_MAX_CHARS} chars; "
        f"why ≤{WHY_MAX_CHARS} chars; neither field may contain newlines or "
        "markdown control characters.",
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
        if args.format == "json":
            print(json.dumps({"precedent_60d": 0, "count": 0, "issues": []}))
        elif args.format == "rank":
            sys.stderr.write("ghi-triage: no open issues — nothing to rank.\n")
            return 1
        else:
            print("No open issues.")
        return 0
    precedent = fix_precedent_count()
    duplicates = detect_duplicates(issues)

    if args.format == "rank":
        try:
            payload = _read_rank_input(args.rank_input)
            known = {issue.number for issue in issues}
            items = parse_rank_input(payload, known)
        except (RankInputError, json.JSONDecodeError, FileNotFoundError, OSError) as exc:
            sys.stderr.write(f"ghi-triage: --rank-input invalid: {exc}\n")
            return 1
        precedent_ok = precedent >= 3
        issue_index = {issue.number: issue for issue in issues}
        routes = {
            issue.number: ROUTE_LABEL[route(issue, precedent_ok, duplicates)] for issue in issues
        }
        sys.stdout.write(render_rank(items, issue_index, routes, precedent, len(issues)))
        return 0
    if args.format == "rich":
        render(issues, precedent, duplicates, width=args.width)
    elif args.format == "markdown":
        print(render_markdown(issues, precedent, duplicates))
    else:
        print(render_json(issues, precedent, duplicates))
    return 0


if __name__ == "__main__":
    sys.exit(main())
