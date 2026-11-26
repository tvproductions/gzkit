"""No live surface credits `AGENTS.md` with naming or ruling the campaign (GHI #1376).

The 2026-09-17 rewrite of root `AGENTS.md` (8ecb176f0, GHI #921) moved the campaign
doctrine bullet ("The ACTIVE campaign plan … is Magna Carta: it rules every session") out
of § Operator Doctrine; campaign work selection is now carried verbatim by
`gz-obpi-pipeline`, and 64f35c53e removed the last mention. `gz-intent-trace` and
`docs/governance/untrusted-content.md` went on crediting `AGENTS.md` with it.

This is a phrasing fence over prose in the form ruled for M9 (operator, 2026-11-26, "a"):
it claims only the shape below, and its form is open under #1370. It drops backticks and
splits text into pieces at a ".", ";", "!" or "?" followed by whitespace, at a blank line,
before a list item ("-", "*" or "+" then whitespace, or a number, "." and whitespace)
and before a table row ("|"); a wrapped line opening with emphasis does not. It collapses
whitespace and refuses a piece that holds "Magna Carta" or "rules every session" together
with "AGENTS.md" or "Operator Doctrine". A piece holding an ISO date (YYYY-MM-DD) is
admitted as a dated record, which also admits a live credit that carries a date.

It reads the `.md`, `.py`, `.json`, `.toml`, `.yaml` and `.yml` files under
`.gzkit/skills`, `.gzkit/rules`, `.gzkit/templates`, `.gzkit/agents`, `.gzkit/personas`,
`.gzkit/chores`, `src/gzkit`, `scripts`, `data`, `docs/user` and `docs/governance`, and the
root contracts. It skips any path through a `proofs` or `archive` directory, any path whose
name holds an ISO date (dated plans, audits and snapshots), and
`docs/governance/rule-version-history.md`, which is version history. It does not judge a
credit in other words, a credit split across pieces, or a negation ("not in AGENTS.md"),
which it refuses.
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
        ".gzkit/chores",
        "src/gzkit",
        "scripts",
        "data",
        "docs/user",
        "docs/governance",
    )
)
ROOT_FILES = (REPO / "AGENTS.md", REPO / "CLAUDE.md", REPO / "README.md")
SUFFIXES = {".md", ".py", ".json", ".toml", ".yaml", ".yml"}
SKIPPED_PARTS = {"proofs", "archive"}
HISTORY_FILES = {"docs/governance/rule-version-history.md"}

_CAMPAIGN = re.compile(r"\bmagna carta\b|\brules every session\b", re.IGNORECASE)
_CANON = re.compile(r"\bAGENTS\.md\b|\bOperator Doctrine\b")
_DATED = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_SENTENCE = re.compile(r"[.;!?]\s|\n\s*\n|\n(?=\s*(?:[-*+]\s|\||\d+\.\s))")


def campaign_credited_to_canon(text: str) -> list[str]:
    """Return each piece of *text* that credits `AGENTS.md` with the campaign doctrine."""
    found: list[str] = []
    for sentence in _SENTENCE.split(text):
        flat = re.sub(r"\s+", " ", sentence.replace("`", "")).strip()
        if _DATED.search(flat):
            continue
        if _CAMPAIGN.search(flat) and _CANON.search(flat):
            found.append(flat)
    return found


def _is_live(path: Path) -> bool:
    relative = path.relative_to(REPO)
    return (
        path.suffix in SUFFIXES
        and not SKIPPED_PARTS.intersection(relative.parts)
        and not any(_DATED.search(part) for part in relative.parts)
        and relative.as_posix() not in HISTORY_FILES
    )


def _live_files() -> list[Path]:
    paths = [path for root in ROOTS for path in sorted(root.rglob("*")) if path.is_file()]
    paths.extend(ROOT_FILES)
    return [path for path in paths if _is_live(path)]


class TestCampaignNotCreditedToAgentsMd(unittest.TestCase):
    def test_every_root_exists(self):
        missing = [p for p in (*ROOTS, *ROOT_FILES) if not p.exists()]
        missing.extend(REPO / name for name in HISTORY_FILES if not (REPO / name).exists())
        self.assertEqual(missing, [], "a fence root moved; update the roots")

    def test_no_live_surface_credits_agents_md(self):
        offenders = [
            f"{path.relative_to(REPO).as_posix()}: {hit}"
            for path in _live_files()
            for hit in campaign_credited_to_canon(
                path.read_text(encoding="utf-8", errors="replace")
            )
        ]
        self.assertEqual(
            offenders,
            [],
            "campaign work selection is carried by gz-obpi-pipeline; AGENTS.md no longer "
            "names or rules the campaign (GHI #1376): " + "; ".join(offenders),
        )

    def test_the_fence_tells_a_credit_from_the_current_text(self):
        stale = (
            (
                "will compete with the active campaign, which is Magna Carta (`AGENTS.md` § "
                "Operator Doctrine). The sample's"
            ),
            (
                "acting on them is the work: `AGENTS.md` § Operator Doctrine states that the "
                'campaign plan *"rules every session"*.'
            ),
        )
        current = (
            (
                "will compete with the active campaign plan, which governs work selection "
                "(`gz-obpi-pipeline` carries that ruling, per `AGENTS.md` § Operator Doctrine)."
            ),
            "## Active campaign — Magna Carta",
            (
                "Boundary 1 was retired 2026-09-29: superseded by the Magna Carta's release "
                "prioritization, per AGENTS.md."
            ),
        )
        for text in stale:
            with self.subTest(stale=text):
                self.assertTrue(campaign_credited_to_canon(text))
        for text in current:
            with self.subTest(current=text):
                self.assertFalse(campaign_credited_to_canon(text))

    def test_dated_and_history_paths_are_records(self):
        self.assertFalse(_is_live(REPO / "docs/governance/build-to-1.0-campaign-2026-06-10.md"))
        self.assertFalse(_is_live(REPO / "docs/governance/rule-version-history.md"))
        self.assertTrue(_is_live(REPO / "docs/governance/untrusted-content.md"))


if __name__ == "__main__":
    unittest.main()
