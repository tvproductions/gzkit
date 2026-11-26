"""No live surface cites AGENTS.md numbering the 2026-09-17 rewrite dropped (GHI #1375).

The 2026-09-17 rewrite of root `AGENTS.md` (8ecb176f0, GHI #921) rendered § Behavior
Rules, § OPERATOR ECONOMY OF EFFORT and the anti-vibing claims as unnumbered bullets, and
kept only the 6c, 6g and 6h tags on DO IT RIGHT. Surfaces kept citing "Behavior Rule 9",
"§ Never #2", "Operator Economy #7", "operative claim 2" and "(6b)".
`.gzkit/rules/skill-authoring.md` § Parsimony 2: text attributed to `AGENTS.md` is
quoted from the current file, by section name, or not quoted. GHI #1035 repaired the
same class in runtime messages on a grep and left no standing witness.

This is a phrasing fence over prose in the form ruled for M9 (operator, 2026-11-26, "a"):
it claims only the shapes below, and its form is open under #1370. It splits text at
". ", "; ", "! ", "? ", blank lines and the start of a list item or table row, drops
backticks, collapses whitespace, and refuses a piece that holds:

- "Behavior Rule" or "Behavior Rules", then up to four non-word characters and an
  optional "Always" or "Never", then a number;
- "Always #N" or "Never #N", unless the piece names `behavior-rules.md`, which keeps its
  own numbered headings;
- "Operator Economy" followed within 30 characters by "#N";
- "operative claim N"; or
- "(6a)", "(6b)", "(6d)", "(6e)" or "(6f)" in a piece that names "DO IT RIGHT".

A piece holding a date (YYYY-MM or YYYY-MM-DD) is a dated record and is admitted.

It reads the `.md`, `.py`, `.json`, `.toml`, `.yaml` and `.yml` files under
`.gzkit/skills`, `.gzkit/rules`, `.gzkit/agents`, `.gzkit/personas`, `.gzkit/chores`,
`src/gzkit` and `docs/user`, and `AGENTS.md`, `CLAUDE.md`, `README.md` and
`.gitattributes`, skipping any path through a `proofs`, `archive` or `templates`
directory: the adopter
template carries its own numbered Behavior Rules. `src/gzkit/handoff_api.py` is skipped by
name: its parser comments name `Always #13` as a text form the handoff corpus still holds.
It does not read `docs/governance`,
which mixes live doctrine with dated records and lift anchors, so the consumers repaired
there are held by review only. `tests.md`'s own "invariant 6f" label is not a shape here.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOTS = tuple(
    REPO / part
    for part in (
        ".gzkit/skills",
        ".gzkit/rules",
        ".gzkit/agents",
        ".gzkit/personas",
        ".gzkit/chores",
        "src/gzkit",
        "docs/user",
    )
)
ROOT_FILES = (REPO / "AGENTS.md", REPO / "CLAUDE.md", REPO / "README.md", REPO / ".gitattributes")
SUFFIXES = {".md", ".py", ".json", ".toml", ".yaml", ".yml"}
SKIPPED_PARTS = {"proofs", "archive", "templates"}
SKIPPED_FILES = {REPO / "src/gzkit/handoff_api.py"}

_BEHAVIOR_RULE = re.compile(r"\bBehavior Rules?\W{0,4}(?:Always|Never)?\W{0,3}#?\d+")
_ALWAYS_NEVER = re.compile(r"\b(?:Always|Never) #\d+")
_ECONOMY = re.compile(r"Operator Economy.{0,30}#\d+")
_CLAIM = re.compile(r"\boperative claim \d+", re.IGNORECASE)
_DROPPED_TAG = re.compile(r"\(6[abdef]\)")
_DO_IT_RIGHT = re.compile(r"DO IT RIGHT")
_BEHAVIOR_DOC = re.compile(r"behavior-rules\.md")
_DATED = re.compile(r"\b\d{4}-\d{2}\b")
_SENTENCE = re.compile(r"[.;!?]\s|\n\s*\n|\n(?=\s*(?:[-*+|]|\d+\.)\s?)")


def _cites_dropped_number(flat: str) -> bool:
    """True when one collapsed piece holds a dropped-numbering shape."""
    shapes = (
        _BEHAVIOR_RULE.search(flat),
        _ALWAYS_NEVER.search(flat) and not _BEHAVIOR_DOC.search(flat),
        _ECONOMY.search(flat),
        _CLAIM.search(flat),
        _DROPPED_TAG.search(flat) and _DO_IT_RIGHT.search(flat),
    )
    return any(shapes)


def dropped_numbering(text: str) -> list[str]:
    """Return each piece of *text* that cites AGENTS.md numbering the rewrite dropped."""
    found: list[str] = []
    for piece in _SENTENCE.split(text):
        flat = re.sub(r"\s+", " ", piece.replace("`", "")).strip()
        if not _DATED.search(flat) and _cites_dropped_number(flat):
            found.append(flat)
    return found


def _live_files() -> list[Path]:
    paths = [path for root in ROOTS for path in sorted(root.rglob("*")) if path.is_file()]
    paths.extend(ROOT_FILES)
    return [
        path
        for path in paths
        if (path.suffix in SUFFIXES or path.name == ".gitattributes")
        and not SKIPPED_PARTS.intersection(path.relative_to(REPO).parts)
        and path not in SKIPPED_FILES
    ]


class TestAgentsMdNumberingNotCited(unittest.TestCase):
    def test_every_root_exists(self):
        missing = [p for p in (*ROOTS, *ROOT_FILES) if not p.exists()]
        self.assertEqual(missing, [], "a fence root moved; update the roots")

    def test_no_live_surface_cites_dropped_numbering(self):
        offenders = [
            f"{path.relative_to(REPO).as_posix()}: {hit}"
            for path in _live_files()
            for hit in dropped_numbering(path.read_text(encoding="utf-8", errors="replace"))
        ]
        self.assertEqual(
            offenders,
            [],
            "AGENTS.md § Behavior Rules, § OPERATOR ECONOMY and the anti-vibing claims are "
            "unnumbered since 2026-09-17 (GHI #1375): cite the section and quote the rule: "
            + "; ".join(offenders),
        )

    def test_the_fence_tells_a_dropped_number_from_a_live_citation(self):
        stale = (
            "not resolve it unilaterally (Behavior Rule 9).",
            "agent-writable only through gz verbs (`AGENTS.md` § Never #2).",
            "file it per `AGENTS.md` § Behavior Rules — Always #13.",
            "- **Never ask what canon already answers** (AGENTS.md § Operator Economy #7).",
            "The doctrine is explicit at `AGENTS.md` § Anti-vibing mantra operative claim 2:",
            "(see `AGENTS.md` § DO IT RIGHT, items 2 (6b) and 5 (6e)).",
            "`improvement` post-correction lessons (Behavior Rule #11), and",
            "(Behavior Rule Always #11) capturing the staleness and the adjustment.",
            "AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT operative claim 3",
        )
        live = (
            (
                "The binding rule is `AGENTS.md` § Behavior Rules (the GHI-authoring rule; "
                "rationale in `docs/governance/behavior-rules.md` § Always #13)."
            ),
            "(see `AGENTS.md` § DO IT RIGHT, items 2 and 5).",
            "per the DO IT RIGHT maxim (`AGENTS.md` § DO IT RIGHT, items 1 and 7 (6c)).",
            "**Tests assert semantics, not strings (invariant 6f).**",
            (
                "``AGENTS.md`` § Behavior Rules was numbered until 2026-09, and the handoff "
                "corpus still cites it as ``Always #13``"
            ),
            "§ PRIME DIRECTIVE 4 and § DO IT RIGHT #3 bind here.",
            "See `AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT (doctrine drift).",
        )
        for text in stale:
            with self.subTest(stale=text):
                self.assertTrue(dropped_numbering(text))
        for text in live:
            with self.subTest(live=text):
                self.assertFalse(dropped_numbering(text))


if __name__ == "__main__":
    unittest.main()
