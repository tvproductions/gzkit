"""Structural regression tests for OBPI-0.0.16-04's dogfood-state invariants.

The prior version of this file asserted the *current project root* passed
the validator and that a dry-run rewrote zero files. That invariant is
transient — any new ADR authored in short-form ``id:`` breaks it before the
next chore run — so those tests fired against downstream authoring drift,
not regressions in the chore itself (GHI #220).

These replacements pin the underlying policy at the library level using a
seeded fixture: given a project with known drift, the chore produces a
clean state, and a follow-on dry-run is idempotent.

REQ-0.0.16-04-04: after ``reconcile_frontmatter`` runs non-dry-run against a
    project with known drift, ``validate_frontmatter_coherence`` returns no
    active-surface errors.
REQ-0.0.16-04-05: after a successful reconcile, the next dry-run produces
    an empty ``files_rewritten`` list (idempotence).
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.commands.validate_frontmatter import validate_frontmatter_coherence
from gzkit.config import GzkitConfig
from gzkit.governance.frontmatter_coherence import reconcile_frontmatter
from gzkit.ledger import Ledger, adr_created_event
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _quick_init


def _scaffold_drifted_adr(root: Path) -> Path:
    """Seed a gzkit project with one drifted ADR and return its path.

    Uses the same path shape as the existing ``tests/governance`` fixtures
    (``{design_root}/adr/pre-release/{adr_id}-test/{adr_id}-test.md``) and
    seeds drift on both ``lane`` (heavy vs ledger's lite) and ``status``
    (Completed vs ledger's pending). Both terms are in
    ``STATUS_VOCAB_MAPPING`` so the chore does not raise ``UnmappedStatusBlocker``.
    """
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
    config = GzkitConfig.load(root / ".gzkit.json")
    adr_dir = root / config.paths.design_root / "adr" / "pre-release" / "ADR-0.1.0-test"
    adr_dir.mkdir(parents=True, exist_ok=True)
    path = adr_dir / "ADR-0.1.0-test.md"
    path.write_text(
        "---\n"
        "id: ADR-0.1.0\n"
        "parent: PRD-TEST-1.0.0\n"
        "lane: heavy\n"
        "status: Completed\n"
        "---\n# ADR\n",
        encoding="utf-8",
    )
    return path


class TestStructuralBackfillInvariants(unittest.TestCase):
    """Policy-level pins for the chore's post-run invariants."""

    @covers("REQ-0.0.16-04-04")
    def test_validator_clean_after_reconcile(self) -> None:
        """REQ-04: after reconcile, the validator has no active-surface errors."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            _scaffold_drifted_adr(root)

            receipt = reconcile_frontmatter(root, dry_run=False)
            self.assertGreaterEqual(
                len(receipt.files_rewritten),
                1,
                "fixture must have drift the chore can rewrite",
            )

            errors = validate_frontmatter_coherence(root)
            active_errors = [e for e in errors if "/adr/pool/" not in (e.artifact or "")]
            self.assertEqual(
                active_errors,
                [],
                msg=(
                    "Post-reconcile project has residual drift — the chore is not "
                    "producing a clean state:\n"
                    + "\n".join(f"  {e.artifact}: {e.message}" for e in active_errors[:5])
                ),
            )

    @covers("REQ-0.0.16-04-05")
    def test_dry_run_is_idempotent_after_reconcile(self) -> None:
        """REQ-05: a post-reconcile dry-run rewrites zero files."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            _scaffold_drifted_adr(root)

            reconcile_frontmatter(root, dry_run=False)
            second = reconcile_frontmatter(root, dry_run=True)

            self.assertEqual(
                list(second.files_rewritten),
                [],
                msg=(
                    "Chore is not idempotent — would rewrite "
                    f"{len(second.files_rewritten)} file(s) on second dry-run "
                    "against a post-reconcile project."
                ),
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
