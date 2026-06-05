"""Post-migration invariants for the canonical handoff store (OBPI-0.0.65-01).

WHY: ADR-0.0.65 canonizes ``.gzkit/handoffs/`` as the single handoff write
location. OBPI-0.0.65-01 relocates the legacy per-ADR handoffs
(``docs/design/adr/**/handoffs/``) into the canonical store, preserving
``continues_from:`` chain integrity. These tests assert the *resulting repository
state* — they derive their assertions from the OBPI's BEHAVIOR acceptance
criteria (REQ-0.0.65-01-01..04), not from the migration implementation, so they
fail closed if a future change reintroduces a per-ADR handoff, breaks a chain
pointer, or regresses the skill-canon amendment.

Reference: ADR-0.0.65-handoff-system-consolidation, OBPI-0.0.65-01.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.handoff_validation import HandoffValidationError, parse_frontmatter
from gzkit.traceability import covers

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CANONICAL_DIR = _REPO_ROOT / ".gzkit" / "handoffs"
_ADR_ROOT = _REPO_ROOT / "docs" / "design" / "adr"
_SKILL = _REPO_ROOT / ".gzkit" / "skills" / "gz-session-handoff" / "SKILL.md"

# Migration baseline (REQ-0.0.65-01-02): migration produced 34 distinct handoffs —
# 11 that pre-dated it plus 23 relocated per-ADR handoffs (the 24th legacy source,
# ``20260524T181428Z-obpi-01-context-core-green.md``, was a byte-identical duplicate
# removed as a dedup; operator decision 2026-05-30). The canonical store must never
# shrink below that baseline — losing a migrated handoff is the regression this test
# exists to catch.
#
# This is a FLOOR, not an equality. Session handoffs accrete above it as normal
# end-of-session ceremony; that growth is legitimate and must NOT demand a manual
# count bump. The prior exact-count assertion was bumped six times in two weeks and
# still left ``main`` red whenever a session forgot to bump it — the silent-drift it
# claimed to prevent, inverted into a standing tax. Floor honors the REQ's intent
# (migration completeness) without re-breaking on every legitimate addition.
_MIGRATION_BASELINE_FLOOR = 34


def _canonical_handoffs() -> list[Path]:
    """Markdown handoffs in the canonical store, excluding the subtree-rules file."""
    return [p for p in _CANONICAL_DIR.glob("*.md") if p.name != "AGENTS.md"]


class HandoffMigrationStateTests(unittest.TestCase):
    """Assert the repository state OBPI-0.0.65-01 is contracted to produce."""

    @covers("REQ-0.0.65-01-01")
    def test_no_per_adr_handoffs_remain(self) -> None:
        """The per-ADR source surface is empty after migration."""
        stragglers = sorted(
            p.relative_to(_REPO_ROOT).as_posix()
            for p in _ADR_ROOT.rglob("*.md")
            if p.parent.name == "handoffs"
        )
        self.assertEqual(
            stragglers,
            [],
            f"per-ADR handoffs must be migrated into .gzkit/handoffs/; found: {stragglers}",
        )

    @covers("REQ-0.0.65-01-02")
    def test_canonical_store_holds_migration_baseline(self) -> None:
        """The canonical store never shrinks below the post-migration baseline.

        A floor, not an equality: migrated handoffs must all survive (loss is the
        regression), while additive session handoffs grow the store freely.
        """
        handoffs = _canonical_handoffs()
        self.assertGreaterEqual(
            len(handoffs),
            _MIGRATION_BASELINE_FLOOR,
            f"canonical store dropped below the migration baseline "
            f"({_MIGRATION_BASELINE_FLOOR}); a migrated handoff may have been lost. "
            f"found {len(handoffs)}: {sorted(p.name for p in handoffs)}",
        )

    @covers("REQ-0.0.65-01-03")
    def test_continues_from_chains_resolve(self) -> None:
        """Every non-empty continues_from pointer resolves to an existing file."""
        broken: list[str] = []
        for path in _canonical_handoffs():
            try:
                frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
            except HandoffValidationError:
                # Some legacy handoffs predate the frontmatter schema; with no
                # frontmatter there is no continues_from pointer to resolve.
                continue
            pointer = (frontmatter.get("continues_from") or "").strip()
            if not pointer:
                continue
            # A pointer either names a repo-relative path or a bare filename
            # resolved against the canonical store.
            target = _REPO_ROOT / pointer if "/" in pointer else _CANONICAL_DIR / pointer
            if not target.is_file():
                broken.append(f"{path.name} -> {pointer}")
        self.assertEqual(
            broken,
            [],
            f"continues_from chain pointers must resolve after migration; broken: {broken}",
        )

    @covers("REQ-0.0.65-01-04")
    def test_skill_canon_has_no_per_adr_write_path(self) -> None:
        """The gz-session-handoff skill no longer documents the per-ADR write path."""
        text = _SKILL.read_text(encoding="utf-8")
        self.assertNotIn(
            "{ADR-package}/handoffs/",
            text,
            "gz-session-handoff/SKILL.md must not document the legacy "
            "{ADR-package}/handoffs/ write location (ADR-0.0.65 canonical-location decision)",
        )


if __name__ == "__main__":
    unittest.main()
