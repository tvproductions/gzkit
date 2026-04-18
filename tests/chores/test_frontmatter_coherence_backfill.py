"""Regression test pinning post-backfill cleanliness (OBPI-0.0.16-04).

After the one-time backfill chore runs against the live repo (live receipt
``artifacts/receipts/frontmatter-coherence/20260418T100437Z.json``), the
governed-frontmatter surface is fully reconciled with the ledger. Two
properties must hold from that point forward and are pinned here:

REQ-0.0.16-04-04: ``gz validate --frontmatter`` exits 0 on the live repo.
REQ-0.0.16-04-05: A dry-run of the chore on the post-backfill repo
    produces an empty ``files_rewritten`` list (idempotence).

If either regresses (e.g. a future ledger event introduces drift the chore
no longer canonicalizes), this test fires and points the operator at the
cause: re-run the chore, then investigate why drift reappeared.
"""

import unittest

from gzkit.commands.common import get_project_root
from gzkit.commands.validate_frontmatter import validate_frontmatter_coherence
from gzkit.governance.frontmatter_coherence import reconcile_frontmatter
from gzkit.traceability import covers


class TestFrontmatterCoherenceBackfillStability(unittest.TestCase):
    """Pin post-backfill cleanliness against the live repo."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.project_root = get_project_root()
        if not (cls.project_root / ".gzkit" / "ledger.jsonl").is_file():
            raise unittest.SkipTest("Not inside a gzkit project — skipping live-repo test")

    @covers("REQ-0.0.16-04-04")
    def test_validate_frontmatter_exits_clean_on_live_repo(self) -> None:
        """REQ-04: post-backfill repo has zero frontmatter-vs-ledger drift.

        Calls the validator's coherence function directly (same path the
        ``gz validate --frontmatter`` CLI takes) and asserts an empty
        error list. Pool ADRs are skipped per GHI #192 fix; only
        active-surface drift would surface here.
        """
        errors = validate_frontmatter_coherence(self.project_root)
        active_errors = [e for e in errors if "/adr/pool/" not in (e.artifact or "")]
        self.assertEqual(
            active_errors,
            [],
            msg=(
                f"Post-backfill repo regressed — {len(active_errors)} "
                f"active-surface frontmatter drift error(s). Re-run "
                f"`gz frontmatter reconcile` and investigate the cause:\n"
                + "\n".join(f"  {e.artifact}: {e.message}" for e in active_errors[:10])
            ),
        )

    @covers("REQ-0.0.16-04-05")
    def test_reconcile_dry_run_is_empty_on_live_repo(self) -> None:
        """REQ-05: chore dry-run produces empty rewrite list (idempotence).

        Invokes the chore library's ``reconcile_frontmatter`` directly in
        dry-run mode. If the receipt's ``files_rewritten`` list grows,
        the chore is no longer at a fixed point against the ledger —
        either the ledger advanced or the canonicalization changed.
        """
        receipt = reconcile_frontmatter(self.project_root, dry_run=True)
        self.assertEqual(
            list(receipt.files_rewritten),
            [],
            msg=(
                f"Chore is no longer idempotent — would rewrite "
                f"{len(receipt.files_rewritten)} file(s). Receipt cursor: "
                f"{receipt.ledger_cursor}. Re-run "
                f"`gz frontmatter reconcile` and capture a new receipt."
            ),
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
