"""No live surface restates two facts the 2026-09-17 rewrite moved or dropped (GHI #1374).

The 2026-09-17 rewrite of root `AGENTS.md` (8ecb176f0, GHI #921) moved the canonical
receipt invocations from § Attestation to the `gz-arb` skill and carried the em-dash
pattern nowhere (compression sweep S23), and dropped the "≥3 `fix(` commits in 60 days"
precedent criterion from defect-fix routing by operator ruling (S14,
`docs/governance/defect-fix-routing.md`). Consumers kept restating both, `ghi-triage`'s
routing among them; that behavior is witnessed by `tests/skills/test_ghi_triage_routing.py`.

This is a phrasing fence over prose in the form ruled for M9 (operator, 2026-11-26, "a"):
it claims only the shapes below, and its form is open under #1370. It splits text at ". ",
"; ", "! ", "? ", blank lines and the start of a list item or table row, drops backticks, collapses
whitespace, and judges each piece. A table row is judged whole unless a cell holds one of
those sentence ends. It refuses a piece that:

- holds "precedent" and either "≥3", "≥ 3", ">=3", ">= 3" or "60 days"; or
- holds "§ Attestation" and either "em-dash", "em dash", "canonical invocation" or
  "canonical-invocation", and does not name "gz-arb", the invocations' current home.

A sentence holding an ISO date (YYYY-MM-DD) is a dated record and is admitted, so a
lineage line such as "On 2026-04-23 … moved to `AGENTS.md` § Attestation" stays true as
written.

It reads the `.md`, `.py`, `.json`, `.toml`, `.yaml` and `.yml` files under
`.gzkit/skills`, `.gzkit/rules`, `.gzkit/templates`, `.gzkit/agents`, `.gzkit/personas`,
`src/gzkit` and `docs/user`, and the root contracts, skipping any path through a `proofs`
or `archive` directory; other suffixes (the `.j2` templates among them) are not read. It
does not read
`docs/governance`, which mixes live doctrine with dated records (the routing doc keeps the
replaced criterion as a record), so the consumers repaired there are held by review only.
Nor does it judge a restatement in other words, or one split across sentences.
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
        ".gzkit/templates",
        ".gzkit/agents",
        ".gzkit/personas",
        "src/gzkit",
        "docs/user",
    )
)
ROOT_FILES = (REPO / "AGENTS.md", REPO / "CLAUDE.md", REPO / "README.md")
SUFFIXES = {".md", ".py", ".json", ".toml", ".yaml", ".yml"}
SKIPPED_PARTS = {"proofs", "archive"}

_PRECEDENT = re.compile(r"\bprecedent", re.IGNORECASE)
_THRESHOLD = re.compile(r"(?:≥|>=)\s?3\b|\b60 days\b", re.IGNORECASE)
_ATTESTATION = re.compile(r"§ ?Attestation\b")
_MOVED = re.compile(r"\bem[- ]dash\b|\bcanonical[- ]invocation", re.IGNORECASE)
_GZ_ARB = re.compile(r"\bgz-arb\b")
_DATED = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_SENTENCE = re.compile(r"[.;!?]\s|\n\s*\n|\n(?=\s*(?:[-*+|]|\d+\.)\s?)")


def stale_restatements(text: str) -> list[str]:
    """Return each sentence of *text* that restates the dropped criterion or the moved home."""
    found: list[str] = []
    for sentence in _SENTENCE.split(text):
        flat = re.sub(r"\s+", " ", sentence.replace("`", "")).strip()
        if _DATED.search(flat):
            continue
        if (_PRECEDENT.search(flat) and _THRESHOLD.search(flat)) or (
            _ATTESTATION.search(flat) and _MOVED.search(flat) and not _GZ_ARB.search(flat)
        ):
            found.append(flat)
    return found


def _live_files() -> list[Path]:
    paths = [path for root in ROOTS for path in sorted(root.rglob("*")) if path.is_file()]
    paths.extend(ROOT_FILES)
    return [
        path
        for path in paths
        if path.suffix in SUFFIXES and not SKIPPED_PARTS.intersection(path.relative_to(REPO).parts)
    ]


class TestMovedAndDroppedFactsNotRestated(unittest.TestCase):
    def test_every_root_exists(self):
        missing = [p for p in (*ROOTS, *ROOT_FILES) if not p.exists()]
        self.assertEqual(missing, [], "a fence root moved; update the roots")

    def test_no_live_surface_restates_them(self):
        offenders = [
            f"{path.relative_to(REPO).as_posix()}: {hit}"
            for path in _live_files()
            for hit in stale_restatements(path.read_text(encoding="utf-8", errors="replace"))
        ]
        self.assertEqual(
            offenders,
            [],
            "the canonical invocations live in gz-arb, and the fix() precedent criterion was "
            "dropped on 2026-09-17 (GHI #1374): " + "; ".join(offenders),
        )

    def test_the_fence_tells_a_restatement_from_the_current_text(self):
        stale = (
            (
                "- Binding rule: `AGENTS.md` § Attestation (em-dash pattern + canonical "
                "invocations + lane behavior + receipt-ID discipline)"
            ),
            "single named surface; ≥3 recent `fix(` precedents) — fix in place",
            "Direct-fix: precedent check (`git log --since='60 days ago' --oneline`) → TDD cycle",
            "| Precedent | `git log --since='60 days ago' --oneline --grep='^fix('` ≥3 commits |",
            "enriched per `AGENTS.md` § Attestation (em-dash + session evidence + receipt IDs).",
        )
        current = (
            (
                "- Binding rule: `AGENTS.md` § Attestation (the operator's words verbatim, then "
                "concrete evidence; lane behavior; receipt-ID discipline). It points here for "
                "the canonical invocations, which step 1 lists."
            ),
            "surface the routing facts `AGENTS.md` § Defect-fix routing names — size, surface.",
            "Direct-fix: route per `AGENTS.md` § Defect-fix routing → TDD cycle",
            '"**GHI Triage** — 44 open issues | `fix()` precedent (60d): 262"',
            "Worked precedent: `84519da5` (GHI #852) pinned the authorship guard by LEVEL.",
            (
                "then append concrete evidence per `AGENTS.md` § Attestation: receipt IDs from "
                "the canonical invocations `gz-arb` lists, test counts, file paths."
            ),
            (
                "On 2026-04-23, the retired attestation rule itself was folded: binding content "
                "(em-dash pattern, canonical invocations) moved to `AGENTS.md` § Attestation."
            ),
        )
        for text in stale:
            with self.subTest(stale=text):
                self.assertTrue(stale_restatements(text))
        for text in current:
            with self.subTest(current=text):
                self.assertFalse(stale_restatements(text))


if __name__ == "__main__":
    unittest.main()
