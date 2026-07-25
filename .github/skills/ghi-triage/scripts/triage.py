#!/usr/bin/env python3
"""ghi-triage: fetch open GHIs, score routing, render deterministic deliverable.

Self-contained to the skill directory. Stdlib + `gh` CLI are the only
hard runtime requirements; `rich` is imported lazily inside the
`--format rich` path so consumers without it can still use the
markdown / json / rank formats. Invoke via:

    uv run python .claude/skills/ghi-triage/scripts/triage.py [args]

Routing thresholds: AGENTS.md § Defect-fix routing.

Output formats:
  - markdown (default, chat-renderable) — the candidate-set table
  - json — structured records for the agent's judgment pass
  - rank — the deterministic rank-ordered deliverable (requires --rank-input)
  - rich — terminal-only Rich table; explicit opt-in for TTY operators
                (this is the only path that requires `rich`)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # ty: ignore[call-non-callable]
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")  # ty: ignore[call-non-callable]
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")  # ty: ignore[call-non-callable]

# --- Markdown renderer (default) ---------------------------------------------


def _md_escape(s: str) -> str:
    """Escape pipes and collapse newlines so a cell stays one markdown row."""
    return s.replace("|", "\\|").replace("\n", " ").strip()


def render_markdown(
    issues: list[Issue],
    precedent: int,
    duplicates: dict[int, int],
    *,
    blocker_resolver=None,
) -> str:
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
            _md_escape(rationale(issue, r, duplicates, blocker_resolver=blocker_resolver)),
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
class Comment:
    body: str
    created_at: str


@dataclass
class Issue:
    number: int
    title: str
    labels: list[str]
    body: str
    created_at: str
    updated_at: str
    comments: list[Comment] = field(default_factory=list)

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


# --- Blocker freshness -------------------------------------------------------
#
# `ghi-close/SKILL.md` § Phase 1 step 1a: a blocker comment is "a claim about
# the tree as it stood on the day it was written" and must be re-derived before
# it is honored. The obligation was prose-only, so the decay went uncaught until
# someone checked by hand. These functions supply the instrument.

_BLOCKER_MARKERS = (
    re.compile(r"\bblocker\b", re.I),
    re.compile(r"\bblocked\s+on\b", re.I),
    re.compile(r"\bsequence\s+(?:this\s+)?after\b", re.I),
    re.compile(r"\bwaiting\s+on\b", re.I),
)

# OBPI before ADR: an OBPI id embeds its parent's semver, so matching ADR first
# would strand the suffix and invent a second, bogus reference.
_REFERENCE_PATTERNS = (
    ("OBPI", re.compile(r"\bOBPI-\d+\.\d+\.\d+-\d+")),
    ("ADR", re.compile(r"\bADR-(?:pool\.[a-z0-9-]+|\d+\.\d+\.\d+)")),
    ("GHI", re.compile(r"(?:\bGHI\s*)?#(\d+)\b")),
)

# `#N` is also how gzkit prose numbers a rule, a list item, or a section of some
# *other* document -- "`skill-surface-sync.md` #6", "Behavior Rules item #13".
# Those resolve against the issue tracker by coincidence, and a low number
# almost always hits a long-closed issue, so an unguarded match manufactures a
# confident false gate. Observed on the first live run against GHI #691.
_ORDINAL_CONTEXT = re.compile(
    r"(?:rules?|items?|steps?|sections?|invariants?|criteri(?:on|a)|questions?|rows?"
    r"|points?|lines?|phases?|notes?|tables?|clauses?|defects?|\.md`?|§)\s*$",
    re.I,
)


@dataclass
class BlockerRef:
    kind: str
    identifier: str
    state: str = "unknown"


@dataclass
class Blocker:
    created_at: str
    references: list[BlockerRef]

    @property
    def cites_settled(self) -> bool:
        """True when a cited precondition has already closed.

        Only `settled` counts. `unknown` does not: an unresolvable reference is
        missing evidence, not evidence of a closed precondition. Collapsing the
        two would let the flag manufacture a verdict it never earned.
        """
        return any(ref.state == "settled" for ref in self.references)


def is_blocker_comment(body: str) -> bool:
    """True when a comment records a precondition on the tree.

    Deliberately narrow. Every comment cross-links issues, so mining all of them
    would turn ordinary discussion into false gates -- the noise that gets a
    freshness signal ignored, which is indistinguishable from not having one.
    """
    return any(p.search(body or "") for p in _BLOCKER_MARKERS)


def extract_references(text: str) -> list[BlockerRef]:
    """Return every governance identifier a precondition cites.

    Pure -- no network, no `gh`. Deduplicated on (kind, identifier) with
    first-seen order preserved, so a blocker naming the same GHI twice yields
    one reference to adjudicate rather than two.
    """
    seen: set[tuple[str, str]] = set()
    found: list[BlockerRef] = []
    remaining = text or ""
    for kind, pattern in _REFERENCE_PATTERNS:
        for match in pattern.finditer(remaining):
            identifier = match.group(1) if kind == "GHI" else match.group(0)
            if kind == "GHI" and _ORDINAL_CONTEXT.search(remaining[: match.start()]):
                continue
            if (kind, identifier) in seen:
                continue
            seen.add((kind, identifier))
            found.append(BlockerRef(kind=kind, identifier=identifier))
        # Consume what this kind claimed so a looser later pattern cannot
        # re-read the same span (`ADR-0.0.65` inside `OBPI-0.0.65-02`).
        remaining = pattern.sub(" ", remaining)
    return found


def blockers(issue: Issue, resolver=None) -> list[Blocker]:
    """Pair each of an issue's preconditions with the live state of what it cites.

    `resolver` is a parameter, never a named technology (hexagonal § Operative
    rule 4): it maps a GHI number to `live` / `settled` / `unknown`. With none
    injected every reference stays `unknown`, so the core is exercisable without
    `gh` and an unreachable live state never renders as verified.

    ADR and OBPI references always resolve `unknown` -- their only repo-local
    index is a Layer-3 derived view, which `state-doctrine.md` forbids as a
    source of truth. Reporting them as unverified is the honest outcome.
    """
    found: list[Blocker] = []
    for comment in issue.comments:
        if not is_blocker_comment(comment.body):
            continue
        refs = extract_references(comment.body)
        if resolver is not None:
            for ref in refs:
                if ref.kind == "GHI":
                    ref.state = resolver(int(ref.identifier))
        found.append(Blocker(created_at=comment.created_at, references=refs))
    return found


def _stale_blocker_note(issue: Issue, resolver) -> str | None:
    """Render the settled citations of an issue's preconditions, if any."""
    settled = [
        f"#{ref.identifier}"
        for blocker in blockers(issue, resolver)
        for ref in blocker.references
        if ref.state == "settled"
    ]
    if not settled:
        return None
    return f"stale blocker: cites settled {', '.join(dict.fromkeys(settled))}"


# --- Data acquisition --------------------------------------------------------

ISSUE_JSON_FIELDS = "number,title,labels,createdAt,updatedAt,body,comments"


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
        ISSUE_JSON_FIELDS,
    ]
    if label:
        cmd += ["--label", label]
    raw = subprocess.run(
        cmd, capture_output=True, text=True, check=True, encoding="utf-8", errors="replace"
    )
    data = json.loads(raw.stdout)
    return [
        Issue(
            number=i["number"],
            title=i["title"],
            labels=[lbl["name"] for lbl in i["labels"]],
            body=i.get("body") or "",
            created_at=i["createdAt"],
            updated_at=i["updatedAt"],
            comments=[
                Comment(body=c.get("body") or "", created_at=c.get("createdAt") or "")
                for c in (i.get("comments") or [])
            ],
        )
        for i in data
    ]


def gh_reference_resolver(open_numbers: set[int]):
    """Adapter: resolve a GHI number against GitHub, closing over the open set.

    The open set is already in hand from `fetch()`, so a reference to an open
    issue costs nothing. Anything else needs one `gh` call to distinguish
    *closed* from *never existed* -- a distinction that matters, because a
    blocker citing a typo'd number is not a discharged precondition.
    """
    cache: dict[int, str] = {}

    def resolve(number: int) -> str:
        if number in open_numbers:
            return "live"
        if number in cache:
            return cache[number]
        try:
            raw = subprocess.run(
                ["gh", "issue", "view", str(number), "--json", "state"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace",
            )
            state = json.loads(raw.stdout).get("state", "")
            cache[number] = "settled" if state == "CLOSED" else "live"
        except (OSError, ValueError, subprocess.SubprocessError):
            # Unreachable state is `unknown`, never `settled`: a network failure
            # must not be readable as "the precondition cleared".
            cache[number] = "unknown"
        return cache[number]

    return resolve


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


def rationale(
    issue: Issue,
    route_label: str,
    duplicates: dict[int, int],
    *,
    blocker_resolver=None,
) -> str:
    if route_label == "close-dup":
        return f"Duplicate of #{duplicates[issue.number]}"
    paths = issue.unique_paths
    body = issue.body or ""
    parts: list[str] = []
    stale = _stale_blocker_note(issue, blocker_resolver)
    if stale:
        # First, not appended: a precondition that no longer holds changes
        # whether the rest of the rationale is worth reading at all.
        parts.append(stale)
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
_ALLOWED_RANKING_KEYS = frozenset({"number", "severity"})


@dataclass(frozen=True)
class RankItem:
    number: int
    severity: str


class RankInputError(ValueError):
    """Raised when --rank-input fails the rendering-edge contract."""


def parse_rank_input(payload: object, known_numbers: set[int]) -> list[RankItem]:
    """Validate agent-supplied rank input.

    Schema is structural-only: number + severity per entry. No prose fields
    (no `action`, no `why`) — those duplicated the renderer's title output
    and produced the recurring chat-surface duplication GHI #424 closed
    structurally. Cognitive freedom lives in selection + ordering + severity;
    the renderer owns all prose.
    """
    if not isinstance(payload, dict):
        raise RankInputError("--rank-input must be a JSON object")
    rankings = payload.get("rankings")
    if not isinstance(rankings, list) or not rankings:
        raise RankInputError("--rank-input requires non-empty 'rankings' list")
    items: list[RankItem] = []
    seen: set[int] = set()
    for idx, entry in enumerate(rankings):
        if not isinstance(entry, dict):
            raise RankInputError(f"rankings[{idx}] must be an object")
        extra = sorted(set(entry.keys()) - _ALLOWED_RANKING_KEYS)
        if extra:
            raise RankInputError(
                f"rankings[{idx}] has forbidden field(s) {extra!r}; "
                "schema accepts only 'number' and 'severity' (GHI #424)"
            )
        number = entry.get("number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise RankInputError(f"rankings[{idx}].number must be int")
        if number in seen:
            raise RankInputError(f"rankings[{idx}].number={number} duplicates earlier entry")
        if number not in known_numbers:
            raise RankInputError(
                f"rankings[{idx}].number={number} not present in fetched issue set"
            )
        seen.add(number)
        severity = entry.get("severity")
        if not isinstance(severity, str) or severity not in SEVERITY_VALUES:
            raise RankInputError(f"rankings[{idx}].severity must be one of {SEVERITY_VALUES}")
        items.append(RankItem(number=number, severity=severity))
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
    parse_rank_input, and no formatting branches on environment. The line
    shape is a strict superset of the agent's input — the agent contributes
    {number, severity, ordering}; the renderer adds {route, title} from the
    fetched issue set. No prose field appears in both surfaces.
    """
    lines = [
        f"# GHI Triage Ranking — {len(items)} ranked of {total} open "
        f"| fix() precedent (60d): {precedent}",
        "",
    ]
    for rank, item in enumerate(items, start=1):
        title = issue_index[item.number].title
        route_label = routes.get(item.number, "—")
        lines.append(f"{rank}. #{item.number} [{item.severity}] {route_label} — {title}")
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


def _make_console(width: int | None):
    """Force Rich to render a real table even under non-TTY capture.

    Rich downgrades box drawing, color, and column ratios when stdout isn't a
    TTY. We always want the full Rich table, so `force_terminal=True` keeps
    the glyphs and the explicit width defeats the 80-col fallback.

    Rich is imported lazily here so consumers that ship the skill without
    `rich` installed can still use the markdown / json / rank paths
    (`--format rich` is the only consumer of this helper).
    """
    from rich.console import Console  # noqa: PLC0415 — lazy: see docstring

    if width is None:
        width = _detect_width()
    return Console(force_terminal=True, color_system="truecolor", width=width)


def render(
    issues: list[Issue],
    precedent: int,
    duplicates: dict[int, int],
    width: int | None = None,
    *,
    blocker_resolver=None,
) -> None:
    # Lazy imports: rich is only needed for the --format rich path; keeping
    # the skill script importable on consumers that don't ship rich.
    from rich import box  # noqa: PLC0415
    from rich.table import Table  # noqa: PLC0415
    from rich.text import Text  # noqa: PLC0415

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
            rationale(issue, r, duplicates, blocker_resolver=blocker_resolver),
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


def render_json(
    issues: list[Issue],
    precedent: int,
    duplicates: dict[int, int],
    *,
    blocker_resolver=None,
) -> str:
    """Emit triage records for agent consumption.

    The agent uses this to drive per-GHI judgment: full body included so the
    agent does not re-shell `gh issue view` once per issue. `blockers` carries
    each recorded precondition with the live state of what it cites, so the
    judgment pass re-derives them (`ghi-close` § Phase 1 step 1a) instead of
    inheriting them as standing fact.
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
                "rationale": rationale(issue, r, duplicates, blocker_resolver=blocker_resolver),
                "blockers": [
                    {
                        "created_at": b.created_at,
                        "cites_settled": b.cites_settled,
                        "references": [
                            {"kind": ref.kind, "identifier": ref.identifier, "state": ref.state}
                            for ref in b.references
                        ],
                    }
                    for b in blockers(issue, blocker_resolver)
                ],
                "created_at": issue.created_at,
                "updated_at": issue.updated_at,
            }
        )
    records.sort(key=lambda x: (URGENCY_RANK[x["urgency"]], x["number"]))
    return json.dumps(
        {"precedent_60d": precedent, "count": len(issues), "issues": records},
        indent=2,
    )


RANK_INPUT_CACHE_DIR = Path(".gzkit/cache/triage")


def _ensure_rank_input_cache_dir() -> Path:
    """Create `.gzkit/cache/triage/` on demand and return its resolved path.

    Auto-creation keeps the skill portable to fresh checkouts: the agent's
    `Write .gzkit/cache/triage/<name>.json` step would otherwise fail with
    a parent-directory error on first use. The directory is the supported
    Write target, so the script owns its lifecycle.
    """
    RANK_INPUT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return RANK_INPUT_CACHE_DIR.resolve()


def _read_rank_input(path: str | None) -> object:
    """Load rank input from a path under .gzkit/cache/triage/.

    Stdin (`-`) is rejected and inline-pipe shapes (`echo '<json>' | …`) are
    structurally impossible: the agent must Write the JSON to a file under
    the cache directory and pass the path. The path constraint kills the
    duplicate-render shape on the bash command-line surface (GHI #424
    round 4) — a `Write` tool call surfaces only the file path in chat,
    while `echo '<json>' | …` surfaces the whole rank payload as the
    command line itself.
    """
    if path is None:
        raise RankInputError(
            "--format rank requires --rank-input <path>; stdin is not accepted (GHI #424)"
        )
    if path == "-":
        raise RankInputError(
            "--rank-input does not accept stdin ('-'); "
            "Write the JSON to .gzkit/cache/triage/<name>.json and pass the path "
            "(GHI #424)"
        )
    cache_root = _ensure_rank_input_cache_dir()
    resolved = Path(path).resolve()
    try:
        resolved.relative_to(cache_root)
    except ValueError as exc:
        raise RankInputError(
            f"--rank-input path must live under {RANK_INPUT_CACHE_DIR.as_posix()}/ "
            f"(got {path!r}); the cache-path requirement structurally prevents "
            "inline-pipe duplicate-render shapes (GHI #424)"
        ) from exc
    raw = resolved.read_text(encoding="utf-8")
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
        "({'rankings': [{number, severity}, ...]}). Path MUST live under "
        f"{RANK_INPUT_CACHE_DIR.as_posix()}/ (stdin rejected — Write the "
        "JSON to a cache file and pass the path). Required with --format "
        f"rank. Schema is structural-only: severity is one of "
        f"{SEVERITY_VALUES}. No prose fields are accepted (extras are "
        "rejected, GHI #424).",
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
    resolver = gh_reference_resolver({issue.number for issue in issues})
    if args.format == "rich":
        render(issues, precedent, duplicates, width=args.width, blocker_resolver=resolver)
    elif args.format == "markdown":
        print(render_markdown(issues, precedent, duplicates, blocker_resolver=resolver))
    else:
        print(render_json(issues, precedent, duplicates, blocker_resolver=resolver))
    return 0


if __name__ == "__main__":
    sys.exit(main())
