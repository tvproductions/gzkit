"""No live surface credits `AGENTS.md` with naming the Magna Carta campaign (GHI #1376).

The 2026-09-17 rewrite of root `AGENTS.md` (8ecb176f0, GHI #921) moved the campaign
doctrine bullet ("The ACTIVE campaign plan … is Magna Carta") out of § Operator Doctrine;
campaign work selection is now carried verbatim by `gz-obpi-pipeline`, and 64f35c53e
removed the last mention. `gz-intent-trace` went on crediting `AGENTS.md` with the name.

This is a phrasing fence over prose in the form ruled for M9 (operator, 2026-11-26, "a"):
it claims only the shape below, and its form is open under #1370. It splits text at ". ",
"; ", "! ", "? ", blank lines and the start of a list item or table row, drops backticks,
collapses whitespace, and refuses a piece that holds "Magna Carta" and either "AGENTS.md"
or "Operator Doctrine". A piece holding an ISO date (YYYY-MM-DD) is a dated record and is
admitted.

It reads the `.md`, `.py`, `.json`, `.toml`, `.yaml` and `.yml` files under
`.gzkit/skills`, `.gzkit/rules`, `.gzkit/templates`, `.gzkit/agents`, `.gzkit/personas`,
`src/gzkit` and `docs/user`, and the root contracts, skipping any path through a `proofs`
or `archive` directory. It does not read `docs/governance`, whose mentions are dated
records, nor judge a restatement in other words or one split across sentences.
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

_CAMPAIGN = re.compile(r"\bmagna carta\b", re.IGNORECASE)
_CANON = re.compile(r"\bAGENTS\.md\b|\bOperator Doctrine\b")
_DATED = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_SENTENCE = re.compile(r"[.;!?]\s|\n\s*\n|\n(?=\s*(?:[-*+|]|\d+\.)\s?)")


def campaign_credited_to_canon(text: str) -> list[str]:
    """Return each sentence of *text* that credits `AGENTS.md` with the campaign name."""
    found: list[str] = []
    for sentence in _SENTENCE.split(text):
        flat = re.sub(r"\s+", " ", sentence.replace("`", "")).strip()
        if _DATED.search(flat):
            continue
        if _CAMPAIGN.search(flat) and _CANON.search(flat):
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


class TestCampaignNotCreditedToAgentsMd(unittest.TestCase):
    def test_every_root_exists(self):
        missing = [p for p in (*ROOTS, *ROOT_FILES) if not p.exists()]
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
            "names the campaign (GHI #1376): " + "; ".join(offenders),
        )

    def test_the_fence_tells_a_credit_from_the_current_text(self):
        stale = (
            (
                "will compete with the active campaign, which is Magna Carta (`AGENTS.md` § "
                "Operator Doctrine). The sample's"
            ),
            "- The campaign is Magna Carta per AGENTS.md: it rules every session",
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


if __name__ == "__main__":
    unittest.main()
