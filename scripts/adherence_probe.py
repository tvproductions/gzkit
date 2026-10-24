#!/usr/bin/env python3
"""Measure whether a rendered per-turn contract surface is actually RECALLABLE.

`gz validate --instructions-files-budget` answers *"were the bytes delivered"*.
This answers the question underneath it: *"can the agent still produce the rule"* —
section by section, against each section's byte offset in the rendered surface.

WHY THIS EXISTS. Published long-context work measures RETRIEVAL (needle-in-a-
haystack, multi-document QA) because retrieval is easy to score. Instruction
ADHERENCE is not measured anywhere, because scoring it needs rules whose recall
is mechanically checkable. gzkit has hundreds of those, ranked for truncation
survival in ``data/agents_md_survival_declaration.json``, so it can measure on
its own corpus what the literature does not publish: Chroma's "Context Rot"
(2025) puts clear degradation for 1M-context models around 300-400K tokens, and
the lost-in-the-middle result puts a >30% penalty on mid-context material — but
neither says what a 47KB instruction contract costs in obeyed rules. This
produces that curve for THIS surface on THIS model, which is the only form of
the answer that can inform a trim.

TWO PROPERTIES DECIDE WHETHER A RUN IS TRUSTWORTHY, and both are enforced here
rather than left to the reader:

1. **The question never carries its answer.** Each probe addresses a section by
   its HEADING and asks the model to produce the body. A probe that quotes the
   body cannot fail — the hollow-test family ``.gzkit/rules/tests.md`` names,
   and the one that survived deliberately broken production behaviour five
   times over under GHI-tracked review. Scoring therefore runs on
   :func:`answer_tokens` — anchor tokens MINUS heading tokens — because a word
   handed to the model in the question is not evidence that it recalled
   anything.

2. **A negative control probes a section that does not exist.** A model that
   "recalls" it is confabulating, and that invalidates the entire run rather
   than costing one row. Same discipline ``_qc_negative_controls`` applies to
   enforcement claims: a control asserting a property that no longer holds is
   worse than no control.

Byte offsets are measured from the rendered surface on every run, never read
from a stored constant — a frozen measurement in a declaration is a derived
view masquerading as source-of-truth (Architectural Boundary 6).

Usage::

    uv run python scripts/adherence_probe.py                    # probe AGENTS.md via codex
    uv run python scripts/adherence_probe.py --surface CLAUDE.md
    uv run python scripts/adherence_probe.py --json out.json
    uv run python scripts/adherence_probe.py --dry-run          # print probes, call nothing
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

MISSING_TOKEN = "MISSING"

RECALLED = "recalled"
ABSENT = "absent"
CONFABULATED = "confabulated"

#: A token must clear this share of a section's answer tokens to count as
#: recall. Half is deliberate: a model that reproduces the substance in its own
#: words is recalling, while one that shares a word or two with the topic is
#: not. Tuned against the fixtures in tests/scripts/test_adherence_probe.py.
_RECALL_THRESHOLD = 0.5

_MIN_TOKEN_LEN = 4

#: Closed-class words carry no evidence of recall — a fluent model emits them
#: whether or not it ever saw the rule.
_STOPWORDS = frozenset(
    [
        # fmt: off
        "that",
        "this",
        "then",
        "than",
        "they",
        "them",
        "their",
        "there",
        "these",
        "those",
        "with",
        "without",
        "within",
        "from",
        "into",
        "onto",
        "upon",
        "your",
        "yours",
        "will",
        "shall",
        "must",
        "never",
        "always",
        "about",
        "above",
        "below",
        "over",
        "under",
        "when",
        "where",
        "which",
        "while",
        "whose",
        "what",
        "have",
        "has",
        "had",
        "been",
        "being",
        "does",
        "done",
        "each",
        "every",
        "both",
        "some",
        "none",
        "only",
        "just",
        "also",
        "more",
        "most",
        "much",
        "many",
        "such",
        "very",
        "like",
        "unless",
        "until",
        "because",
        "before",
        "after",
        "during",
        "against",
        "between",
        "through",
        "here",
        "not",
        "and",
        "the",
        "for",
        "are",
        "but",
        "its",
        "you",
        "was",
        "were",
        "can",
        "may",
        "might",
        # fmt: on
    ]
)

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[a-z][a-z'-]*")
# Smart quotes, dashes and the like: a model re-punctuates freely, and scoring
# must not read that as a miss.
_PUNCT_FOLD = str.maketrans(
    {
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "…": "...",
    }
)


@dataclass(frozen=True)
class Section:
    """One ``## `` section of a rendered surface, with its measured position."""

    section_id: str
    title: str
    offset: int
    anchor: str


@dataclass(frozen=True)
class Result:
    """One probe's outcome."""

    section: Section
    verdict: str
    answer: str


def _slug(title: str) -> str:
    """Section id in the vocabulary ``gzkit.content.parse.section_id`` mints.

    Reimplemented rather than imported so the probe runs against ANY rendered
    markdown — including a candidate rendition that is not yet installed, which
    is exactly the artifact a trim needs measured before it lands.
    """
    lowered = title.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")


#: A block opening with one of these is structure, not prose. ``*`` and ``-``
#: are matched WITH a trailing space so a bold lead (``**Pattern:** ...``) is
#: read as the sentence it is — the first cut matched a bare ``*`` and skipped
#: ``## Attestation``'s real opening line, anchoring on a sentence further down
#: and scoring the model's correct quote as a confabulation.
_STRUCTURAL_LEADS = ("#", ">", "- ", "* ", "|", "```", "<!--", "1. ")


def _first_sentence(body: str) -> str:
    """First prose sentence of a section body, or ``""`` if it does not lead with prose.

    Returns empty for a body that OPENS with a table, list or fence rather than
    searching past it. The probe asks for a section's first sentence, so an
    anchor taken from below a leading table asks one question and scores a
    different one — marking a correct answer wrong. Such a section carries no
    fair probe and is excluded by :func:`is_probeable`; a missing row is honest,
    an unfair row produces a number that looks like evidence.
    """
    for block in body.split("\n\n"):
        stripped = block.strip()
        if not stripped:
            continue
        if stripped.startswith(_STRUCTURAL_LEADS):
            return ""
        collapsed = " ".join(stripped.split())
        return _SENTENCE_END.split(collapsed)[0].strip()
    return ""


def is_probeable(section: Section) -> bool:
    """Whether ``section`` can be asked a question it can be fairly scored on."""
    return bool(section.anchor) and bool(answer_tokens(section))


def parse_sections(text: str) -> list[Section]:
    """Return every ``## `` section with the BYTE offset of its heading.

    Byte offsets, not character offsets: a vendor delivery cap is expressed in
    bytes, so a surface carrying any non-ASCII would otherwise report a
    position that no cap comparison can use.
    """
    lines = text.splitlines(keepends=True)
    heads: list[tuple[str, int, int]] = []
    offset = 0
    for index, line in enumerate(lines):
        if line.startswith("## "):
            heads.append((line[3:].strip(), offset, index))
        offset += len(line.encode("utf-8"))

    sections: list[Section] = []
    for position, (title, byte_offset, line_index) in enumerate(heads):
        end = heads[position + 1][2] if position + 1 < len(heads) else len(lines)
        body = "".join(lines[line_index + 1 : end])
        sections.append(
            Section(
                section_id=_slug(title),
                title=title,
                offset=byte_offset,
                anchor=_first_sentence(body),
            )
        )
    return sections


def distinctive_tokens(text: str) -> set[str]:
    """Content words of ``text`` — the ones whose presence is evidence."""
    folded = text.translate(_PUNCT_FOLD).lower()
    return {
        word
        for word in _WORD.findall(folded)
        if len(word) >= _MIN_TOKEN_LEN and word not in _STOPWORDS
    }


#: The question, with the only per-section variable being the heading it
#: addresses. Held as a template so :func:`answer_tokens` can subtract its
#: wording automatically — edit the prose here and scoring re-derives.
_PROBE_TEMPLATE = (
    "Answer ONLY from the instructions already in your context. "
    "Do NOT read, open, search, or list any files.\n\n"
    'Your context may contain a section headed "## {title}". '
    "If it does, quote its first sentence verbatim. "
    "If it does not, reply with exactly {missing} and nothing else."
)

#: Every content word the probe itself supplies. A model can echo any of these
#: without having seen the surface, so they are never evidence of recall.
#: Derived from the template rather than hand-listed: the first cut of this
#: module wrote "verbatim" into the question while one section's anchor read
#: "...the operator's verbatim words unchanged", which would have scored a
#: partial hit for parroting the prompt back.
_SCAFFOLD_TOKENS = distinctive_tokens(
    _PROBE_TEMPLATE.replace("{title}", "").replace("{missing}", MISSING_TOKEN)
)


def answer_tokens(section: Section) -> set[str]:
    """Tokens the model must SUPPLY — anchor tokens minus everything given.

    Subtracts BOTH the heading (the probe must name it to address the section)
    and the probe's own wording. The rule is one rule: a word the question
    hands over is not evidence that anything was recalled. Counting it would
    let a model score by echoing the question back — the hollow-test shape this
    module exists to measure, not to reproduce.
    """
    given = distinctive_tokens(section.title) | _SCAFFOLD_TOKENS
    return distinctive_tokens(section.anchor) - given


def build_probe(section: Section) -> str:
    """The question asked about ``section`` — by identity, never by content."""
    return _PROBE_TEMPLATE.format(title=section.title, missing=MISSING_TOKEN)


def score(section: Section, answer: str) -> str:
    """Classify one answer as recalled, absent, or confabulated."""
    cleaned = answer.translate(_PUNCT_FOLD).strip()
    if cleaned.strip("\"'. \t\n").upper() == MISSING_TOKEN:
        return ABSENT

    expected = answer_tokens(section)
    if not expected:
        # No scoreable anchor (an empty or purely structural section body).
        # Reporting recall here would credit the probe for asking nothing.
        return CONFABULATED

    hit = expected & distinctive_tokens(cleaned)
    return RECALLED if len(hit) / len(expected) >= _RECALL_THRESHOLD else CONFABULATED


def negative_control(text: str) -> Section:
    """A plausible-sounding section that is NOT in ``text``.

    Deterministic for a given surface so runs stay comparable, and verified
    absent rather than assumed absent — a control that accidentally names a
    real section would invert the whole test.
    """
    candidates = (
        "Deprecation Ledger Protocol",
        "Quorum Escalation Policy",
        "Telemetry Retention Covenant",
        "Provisional Rollback Charter",
    )
    lowered = text.lower()
    for title in candidates:
        if title.lower() not in lowered:
            return Section(section_id=_slug(title), title=title, offset=-1, anchor="")
    raise RuntimeError("no negative control available: every candidate title is present")


def control_passed(verdict: str) -> bool:
    """A control is only clean when the model declined to recall it."""
    return verdict == ABSENT


def build_report(results: list[Result], *, cap: int | None = None, control_ok: bool = True) -> dict:
    """Assemble the deliverable: recall against byte position."""
    ordered = sorted(results, key=lambda r: r.section.offset)
    rows = [
        {
            "section_id": r.section.section_id,
            "title": r.section.title,
            "offset": r.section.offset,
            "past_cap": cap is not None and r.section.offset >= cap,
            "verdict": r.verdict,
            "recalled": r.verdict == RECALLED,
        }
        for r in ordered
    ]

    def _rate(subset: list[dict]) -> float | None:
        if not subset:
            return None
        return sum(1 for row in subset if row["recalled"]) / len(subset)

    within = [row for row in rows if not row["past_cap"]]
    beyond = [row for row in rows if row["past_cap"]]
    return {
        "valid": bool(control_ok),
        "control_passed": bool(control_ok),
        "cap": cap,
        "probed": len(rows),
        "recall_rate": _rate(rows) or 0.0,
        "recall_rate_within_cap": _rate(within),
        "recall_rate_past_cap": _rate(beyond),
        "rows": rows,
    }


def run_codex(question: str, cwd: Path) -> str:
    """Ask a FRESH Codex session, so the surface loads the way a session sees it."""
    completed = subprocess.run(
        ["codex", "exec", "--skip-git-repo-check", question],
        cwd=cwd,
        capture_output=True,
        text=True,
        # Codex output is not guaranteed UTF-8; a strict decode raises
        # UnicodeDecodeError -- a ValueError, so an `except OSError` around the
        # call would miss it and abort the probe mid-run (GHI #582,
        # `.claude/rules/cross-platform.md` § Subprocess reads).
        errors="replace",
        check=False,
        timeout=300,
    )
    return completed.stdout


RUNNERS = {"codex": run_codex}


def _render(report: dict) -> str:
    lines: list[str] = []
    if not report["valid"]:
        lines.append(
            "RUN INVALID — the negative control was 'recalled'. The model is "
            "confabulating, so every row below is unreliable.\n"
        )
    cap = report["cap"]
    lines.append(f"probed {report['probed']} sections   cap={cap}")
    lines.append(f"overall recall   {report['recall_rate']:.0%}")
    for label, key in (
        ("within cap", "recall_rate_within_cap"),
        ("past cap  ", "recall_rate_past_cap"),
    ):
        if report[key] is not None:
            lines.append(f"  {label}     {report[key]:.0%}")
    lines.append("")
    lines.append(f"{'offset':>8}  {'':1}  {'verdict':<13} section")
    for row in report["rows"]:
        mark = "!" if row["past_cap"] else " "
        lines.append(f"{row['offset']:>8}  {mark}  {row['verdict']:<13} {row['section_id']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--surface", default="AGENTS.md")
    parser.add_argument("--runner", choices=sorted(RUNNERS), default="codex")
    parser.add_argument("--cap", type=int, default=32768)
    parser.add_argument("--json", dest="json_out")
    parser.add_argument("--limit", type=int, default=0, help="probe only the first N")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    root = Path.cwd()
    surface = root / args.surface
    if not surface.is_file():
        print(f"no such surface: {surface}", file=sys.stderr)
        return 2

    text = surface.read_text(encoding="utf-8")
    parsed = parse_sections(text)
    sections = [s for s in parsed if is_probeable(s)]
    skipped = len(parsed) - len(sections)
    if args.limit:
        sections = sections[: args.limit]
    control = negative_control(text)

    if args.dry_run:
        for section in [control, *sections]:
            print(f"--- {section.section_id} @ {section.offset}")
            print(build_probe(section))
            print()
        return 0

    runner = RUNNERS[args.runner]

    print(f"negative control: {control.title} ...", file=sys.stderr, flush=True)
    control_verdict = score(control, runner(build_probe(control), root))
    control_ok = control_passed(control_verdict)

    results: list[Result] = []
    for index, section in enumerate(sections, start=1):
        print(
            f"[{index}/{len(sections)}] {section.section_id} @ {section.offset}",
            file=sys.stderr,
            flush=True,
        )
        answer = runner(build_probe(section), root)
        results.append(Result(section, score(section, answer), answer))

    report = build_report(results, cap=args.cap, control_ok=control_ok)
    # Never a silent cap: a run that quietly drops a third of the surface reads
    # as full coverage. Say what was excluded and why, in the report itself.
    report["skipped_unprobeable"] = skipped
    print(_render(report))
    if skipped:
        print(
            f"\n{skipped} of {len(parsed)} sections excluded: no prose lead sentence "
            "to score fairly (body opens with a table, list, or fence)."
        )
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nwrote {args.json_out}", file=sys.stderr)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
