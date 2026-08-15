"""BEHAVIOR tests for ``gz handoff archive`` (ADR-0.0.65, OBPI-0.0.65-05).

WHY: OBPI-0.0.65-05 adds a governed move-not-delete retention verb over the
canonical handoff store. These assertions derive from the OBPI's BEHAVIOR
acceptance criteria (REQ-0.0.65-05-01..05), NOT from the implementation — each
guard test also asserts that a co-present *eligible* handoff IS moved, so a no-op
implementation cannot false-pass the guard.

Reference: ADR-0.0.65-handoff-system-consolidation, OBPI-0.0.65-05.
"""

from __future__ import annotations

import json
import unittest
from contextlib import redirect_stdout
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.commands.handoff_archive import handoff_archive_cmd
from gzkit.handoff_api import resolve_continues_from
from gzkit.handoff_archive import execute_archive, plan_archive
from gzkit.traceability import covers

_NOW = datetime(2026, 7, 15, tzinfo=UTC)
_OLD_TS = "2026-01-01T00:00:00Z"  # > 30 days before _NOW
_RECENT_TS = "2026-07-14T00:00:00Z"  # < 30 days before _NOW


def _handoffs_dir(base: Path) -> Path:
    d = base / ".gzkit" / "handoffs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_handoff(
    base: Path,
    name: str,
    *,
    timestamp: str,
    continues_from: str | None = None,
    adr_id: str = "ADR-0.0.65",
) -> Path:
    """Write a minimal valid handoff and return its path."""
    lines = ["---", f"adr_id: {adr_id}", "branch: main", f"timestamp: '{timestamp}'", "agent: g0"]
    if continues_from is not None:
        lines.append(f"continues_from: {continues_from}")
    lines += ["---", "", "## Decisions Made", "", f"body of {name}", ""]
    path = _handoffs_dir(base) / name
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def _record_lock_release(base: Path, handoff_rel: str) -> None:
    """Write a minimal obpi_lock_released ledger line carrying handoff_path.

    Written directly (not through the ledger API) so this test does not import
    the ``ledger*`` security surface the brief denies; the runtime reads the same
    line through its sanctioned read-only import. The extra keys (agent, force,
    handoff_path) flow into ``LedgerEvent.extra`` on read-back.
    """
    ledger_path = base / ".gzkit" / "ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "event": "obpi_lock_released",
        "id": "OBPI-0.0.65-99-fixture",
        "agent": "g0",
        "force": False,
        "handoff_path": handoff_rel,
    }
    ledger_path.write_text(json.dumps(event) + "\n", encoding="utf-8", newline="\n")


class HandoffArchiveBehaviorTests(unittest.TestCase):
    """Assert the retention behavior OBPI-0.0.65-05 is contracted to produce."""

    @covers("REQ-0.0.65-05-01")
    def test_eligible_handoff_is_moved_not_deleted(self) -> None:
        """An old, uncoupled handoff moves to archive/ with bytes unchanged."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            src = _write_handoff(base, "old-free.md", timestamp=_OLD_TS)
            original = src.read_bytes()

            plan = plan_archive(base_path=base, older_than_days=30, now=_NOW)
            result = execute_archive(plan, base_path=base)

            rel = ".gzkit/handoffs/old-free.md"
            archived = base / ".gzkit" / "handoffs" / "archive" / "old-free.md"
            self.assertIn(rel, result.moved)
            self.assertFalse(src.exists(), "source must no longer exist after move")
            self.assertTrue(archived.is_file(), "handoff must exist under archive/")
            self.assertEqual(archived.read_bytes(), original, "byte content must be unchanged")

    @covers("REQ-0.0.65-05-02")
    def test_lock_coupled_handoff_is_skipped(self) -> None:
        """A lock-referenced handoff stays; a co-present free handoff still moves."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            locked = _write_handoff(base, "locked.md", timestamp=_OLD_TS)
            free = _write_handoff(base, "free.md", timestamp=_OLD_TS)
            _record_lock_release(base, ".gzkit/handoffs/locked.md")

            plan = plan_archive(base_path=base, older_than_days=30, now=_NOW)
            result = execute_archive(plan, base_path=base)

            self.assertIn(".gzkit/handoffs/locked.md", plan.skipped_locked)
            self.assertTrue(locked.exists(), "lock-coupled handoff must remain canonical")
            self.assertNotIn(".gzkit/handoffs/locked.md", result.moved)
            # discriminator: the guard must not over-skip the uncoupled handoff
            self.assertIn(".gzkit/handoffs/free.md", result.moved)
            self.assertFalse(free.exists())

    @covers("REQ-0.0.65-05-03")
    def test_chain_target_handoff_is_skipped(self) -> None:
        """A continues_from target of a canonical handoff stays; a free one moves."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = _write_handoff(base, "target.md", timestamp=_OLD_TS)
            # a still-canonical (recent) handoff whose chain points at target
            _write_handoff(base, "child.md", timestamp=_RECENT_TS, continues_from="target.md")
            free = _write_handoff(base, "free.md", timestamp=_OLD_TS)

            plan = plan_archive(base_path=base, older_than_days=30, now=_NOW)
            result = execute_archive(plan, base_path=base)

            self.assertIn(".gzkit/handoffs/target.md", plan.skipped_chained)
            self.assertTrue(target.exists(), "chain target must remain canonical (not orphaned)")
            self.assertNotIn(".gzkit/handoffs/target.md", result.moved)
            # discriminator: the guard must not over-skip the free handoff
            self.assertIn(".gzkit/handoffs/free.md", result.moved)
            self.assertFalse(free.exists())

    @covers("REQ-0.0.65-05-01")
    def test_recent_handoff_is_not_planned_for_archive(self) -> None:
        """A handoff newer than the threshold is not eligible (REQ-01 age precondition)."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write_handoff(base, "recent.md", timestamp=_RECENT_TS)

            plan = plan_archive(base_path=base, older_than_days=30, now=_NOW)

            self.assertEqual(plan.eligible, [], "recent handoff must not be eligible")
            self.assertIn(".gzkit/handoffs/recent.md", plan.skipped_recent)

    @covers("REQ-0.0.65-05-05")
    def test_dry_run_reports_would_move_and_mutates_nothing(self) -> None:
        """--dry-run reports the would-move set and leaves every file in place."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            old = _write_handoff(base, "old-free.md", timestamp=_OLD_TS)

            buffer = StringIO()
            with redirect_stdout(buffer):
                handoff_archive_cmd(
                    older_than="30d", dry_run=True, as_json=True, base_path=base, now=_NOW
                )
            payload = json.loads(buffer.getvalue())

            self.assertTrue(payload["dry_run"])
            self.assertIn(".gzkit/handoffs/old-free.md", payload["would_move"])
            # mutates nothing: the handoff is still canonical, archive/ was not created
            self.assertTrue(old.exists(), "dry-run must not move the handoff")
            self.assertFalse((base / ".gzkit" / "handoffs" / "archive").exists())

    @covers("REQ-0.0.65-05-01")
    def test_archive_never_overwrites_existing_archived_handoff(self) -> None:
        """A same-name file already in archive/ is never clobbered (move-not-delete).

        Adversary counterexample (Step 4b): shutil.move with an unchecked
        destination silently overwrites a prior archived handoff, destroying an
        audit artifact and dropping the floor while reporting success.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            archive = base / ".gzkit" / "handoffs" / "archive"
            archive.mkdir(parents=True)
            prior = archive / "collision.md"
            prior.write_text("PRIOR ARCHIVED CONTENT", encoding="utf-8", newline="\n")
            src = _write_handoff(base, "collision.md", timestamp=_OLD_TS)
            src_bytes = src.read_bytes()

            plan = plan_archive(base_path=base, older_than_days=30, now=_NOW)
            result = execute_archive(plan, base_path=base)

            # NEVER overwrite the prior archived artifact
            self.assertEqual(prior.read_text(encoding="utf-8"), "PRIOR ARCHIVED CONTENT")
            # the colliding source is preserved (left canonical), never destroyed
            self.assertTrue(src.exists(), "colliding source must not be deleted")
            self.assertEqual(src.read_bytes(), src_bytes)
            # conflict is classified at PLAN time so dry-run and execute agree
            self.assertIn(".gzkit/handoffs/collision.md", plan.skipped_conflict)
            self.assertNotIn(".gzkit/handoffs/collision.md", plan.eligible)
            self.assertNotIn(".gzkit/handoffs/collision.md", result.moved)

    @covers("REQ-0.0.65-05-03")
    def test_chain_target_protected_when_referrer_already_archived(self) -> None:
        """A target referenced by an ALREADY-archived handoff stays protected.

        Adversary counterexample (Step 4b): across repeated runs, once referrer A
        is archived the chain guard (canonical-only) stops protecting target B, so
        B is archived on the next run and A's continues_from pointer is orphaned.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            archive = base / ".gzkit" / "handoffs" / "archive"
            archive.mkdir(parents=True)
            (archive / "a.md").write_text(
                "---\nadr_id: ADR-0.0.65\nbranch: main\n"
                f"timestamp: '{_OLD_TS}'\nagent: g0\n"
                "continues_from: .gzkit/handoffs/b.md\n---\n\n## Decisions Made\n",
                encoding="utf-8",
                newline="\n",
            )
            b = _write_handoff(base, "b.md", timestamp=_OLD_TS)

            plan = plan_archive(base_path=base, older_than_days=30, now=_NOW)
            execute_archive(plan, base_path=base)

            self.assertIn(".gzkit/handoffs/b.md", plan.skipped_chained)
            self.assertTrue(b.exists(), "target referenced by an archived handoff must not orphan")

    @covers("REQ-0.0.65-05-03")
    def test_chain_survives_real_resolver_after_archive(self) -> None:
        """The production load_handoff_chain still walks the chain after an archive run.

        Adversary follow-up (Step 4b, round 2): a guard that reimplements
        resolution can pass while the real resolver breaks. This exercises the
        actual gzkit.handoff_api.load_handoff_chain — the conservative guard keeps
        BOTH ends canonical, so resolution is provably unchanged.
        """
        from gzkit.handoff_api import load_handoff_chain

        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            b = _write_handoff(base, "b.md", timestamp=_OLD_TS)
            a = _write_handoff(base, "a.md", timestamp=_OLD_TS, continues_from="b.md")

            plan = plan_archive(base_path=base, older_than_days=30, now=_NOW)
            execute_archive(plan, base_path=base)

            # both ends of the chain are protected → stay canonical
            self.assertIn(".gzkit/handoffs/a.md", plan.skipped_chained)
            self.assertIn(".gzkit/handoffs/b.md", plan.skipped_chained)
            self.assertTrue(a.exists() and b.exists())
            # the REAL resolver still reaches the target
            chain_keys = {p.resolve().as_posix() for p in load_handoff_chain(a, base_path=base)}
            self.assertIn(b.resolve().as_posix(), chain_keys)

    @covers("REQ-0.0.65-05-03")
    def test_chain_target_protected_via_normalized_pointer(self) -> None:
        """A target referenced by a ./-bearing explicit pointer is still protected.

        Adversary follow-up (Step 4b, round 2): raw-string pointer comparison lets
        `.gzkit/handoffs/./target.md` miss the real `.gzkit/handoffs/target.md`,
        orphaning it. Resolution must normalize both sides.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = _write_handoff(base, "target.md", timestamp=_OLD_TS)
            _write_handoff(
                base,
                "child.md",
                timestamp=_RECENT_TS,
                continues_from=".gzkit/handoffs/./target.md",
            )

            plan = plan_archive(base_path=base, older_than_days=30, now=_NOW)
            execute_archive(plan, base_path=base)

            self.assertIn(".gzkit/handoffs/target.md", plan.skipped_chained)
            self.assertTrue(target.exists(), "normalized-pointer target must not be orphaned")

    @covers("REQ-0.0.65-05-03")
    def test_chain_target_protected_by_filesystem_identity_case_alias(self) -> None:
        """On a case-insensitive filesystem, a differently-cased pointer still protects.

        Adversary follow-up (Step 4b, round 3): resolved-STRING keys treat
        `TARGET.md` and `target.md` as distinct even though they are one inode on a
        case-insensitive FS, orphaning the target. Identity keying by (dev, ino)
        fixes it. Skipped where the FS is case-sensitive (the alias is then a
        genuinely different file and non-protection is correct).
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            probe = base / "CASEPROBE"
            probe.mkdir()
            case_insensitive = (base / "caseprobe").exists()
            probe.rmdir()
            target = _write_handoff(base, "target.md", timestamp=_OLD_TS)
            _write_handoff(base, "child.md", timestamp=_RECENT_TS, continues_from="TARGET.md")

            plan = plan_archive(base_path=base, older_than_days=30, now=_NOW)
            execute_archive(plan, base_path=base)

            # Both filesystems are asserted, neither is skipped. Case-sensitivity
            # is a real, irreducible platform difference — but "the platform
            # differs" is a reason to assert the OTHER behaviour, never a reason
            # to assert nothing. On a case-sensitive filesystem `TARGET.md` names
            # no existing file, so the chain does not exist and archiving
            # `target.md` is correct; on a case-insensitive one it resolves and
            # the pointer target must be protected.
            if case_insensitive:
                self.assertIn(".gzkit/handoffs/target.md", plan.skipped_chained)
                self.assertTrue(target.exists(), "case-alias pointer target must not be orphaned")
            else:
                self.assertNotIn(".gzkit/handoffs/target.md", plan.skipped_chained)
                self.assertFalse(target.exists(), "no chain exists on a case-sensitive filesystem")

    @covers("REQ-0.0.65-05-05")
    def test_dry_run_flags_dangling_symlink_conflict(self) -> None:
        """A dangling-symlink dest is classified as a conflict at plan time.

        Adversary follow-up (Step 4b, round 3): Path.exists() follows symlinks and
        misses a dangling entry, but os.link still fails on it — so dry-run must
        agree with execute. Skipped where symlinks are unavailable.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            archive = base / ".gzkit" / "handoffs" / "archive"
            archive.mkdir(parents=True)
            # Asserted, not skipped. gzkit treats Windows/macOS/Linux as co-equal
            # (`.claude/rules/cross-platform.md`), and a dangling-symlink dest is
            # a real conflict shape on all three — so an environment that cannot
            # create one cannot verify this behaviour, and must SAY so rather than
            # report green. On Windows this needs Developer Mode or an elevated
            # shell; that is an environment requirement, not an optional extra.
            try:
                (archive / "dup.md").symlink_to(base / "no-such-target.md")
            except (OSError, NotImplementedError) as exc:  # pragma: no cover - env capability
                self.fail(
                    f"cannot create a symlink, so the dangling-dest conflict path is "
                    f"unverifiable here: {exc}. On Windows enable Developer Mode."
                )
            _write_handoff(base, "dup.md", timestamp=_OLD_TS)

            plan = plan_archive(base_path=base, older_than_days=30, now=_NOW)

            self.assertIn(".gzkit/handoffs/dup.md", plan.skipped_conflict)
            self.assertNotIn(".gzkit/handoffs/dup.md", plan.eligible)

    @covers("REQ-0.0.65-05-05")
    def test_dry_run_reports_preexisting_conflict(self) -> None:
        """--dry-run classifies a pre-existing archive/ collision (dry-run == execute)."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            archive = base / ".gzkit" / "handoffs" / "archive"
            archive.mkdir(parents=True)
            (archive / "dup.md").write_text("PRIOR", encoding="utf-8", newline="\n")
            _write_handoff(base, "dup.md", timestamp=_OLD_TS)

            buffer = StringIO()
            with redirect_stdout(buffer):
                handoff_archive_cmd(
                    older_than="30d", dry_run=True, as_json=True, base_path=base, now=_NOW
                )
            payload = json.loads(buffer.getvalue())

            self.assertIn(".gzkit/handoffs/dup.md", payload["skipped_conflict"])
            self.assertNotIn(".gzkit/handoffs/dup.md", payload["would_move"])

    @covers("REQ-0.0.65-05-04")
    def test_archive_preserves_combined_floor_count(self) -> None:
        """Move-not-delete keeps the canonical + archive total constant."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoffs_dir = base / ".gzkit" / "handoffs"
            for i in range(5):
                _write_handoff(base, f"old-{i}.md", timestamp=_OLD_TS)

            def _combined_count() -> int:
                canonical = [p for p in handoffs_dir.glob("*.md") if p.name != "AGENTS.md"]
                archived = list((handoffs_dir / "archive").glob("*.md"))
                return len(canonical) + len(archived)

            before = _combined_count()
            plan = plan_archive(base_path=base, older_than_days=30, now=_NOW)
            result = execute_archive(plan, base_path=base)

            self.assertGreater(len(result.moved), 0, "fixture must archive at least one handoff")
            self.assertEqual(
                _combined_count(),
                before,
                "archiving must preserve the canonical + archive total (move-not-delete)",
            )
            self.assertGreater(
                len(list((handoffs_dir / "archive").glob("*.md"))),
                0,
                "archived handoffs must land in the archive subdir",
            )


# ---------------------------------------------------------------------------
# continues_from resolver — ONE implementation, two consumers (GHI #689)
#
# The chain-integrity guard's correctness depends on the archive side resolving
# every pointer form exactly as the production CREATE/RESUME path does. That
# dependency used to be asserted in a docstring and mirrored by hand across a
# brief boundary, with no test binding the copies. These tests bind the contract
# to behavior instead of to prose.
# ---------------------------------------------------------------------------


class ResolveContinuesFromSemanticsTests(unittest.TestCase):
    """Pin the pointer-form resolution contract the archive guard depends on."""

    def test_absolute_pointer_resolves_as_is(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = _write_handoff(base, "target.md", timestamp=_OLD_TS)
            referrer = _handoffs_dir(base) / "referrer.md"
            resolved = resolve_continues_from(str(target), referrer, base)
            self.assertEqual(resolved, target)

    def test_bare_sibling_pointer_resolves_against_the_referrer(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = _write_handoff(base, "target.md", timestamp=_OLD_TS)
            referrer = _handoffs_dir(base) / "referrer.md"
            self.assertEqual(resolve_continues_from("target.md", referrer, base), target)

    def test_project_relative_pointer_resolves_against_base(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = _write_handoff(base, "target.md", timestamp=_OLD_TS)
            referrer = _handoffs_dir(base) / "referrer.md"
            resolved = resolve_continues_from(".gzkit/handoffs/target.md", referrer, base)
            self.assertEqual(resolved.resolve(), target.resolve())

    def test_nonexistent_pointer_falls_back_to_sibling(self) -> None:
        """The else-branch: an unresolvable pointer keys to the sibling candidate.

        Load-bearing for the archive guard — a dangling pointer must still yield a
        stable key rather than raising, so a broken chain link cannot crash a scan.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            referrer = _handoffs_dir(base) / "referrer.md"
            resolved = resolve_continues_from("gone.md", referrer, base)
            self.assertEqual(resolved, referrer.parent / "gone.md")


class ArchiveGuardUsesTheProductionResolverTests(unittest.TestCase):
    """The chain guard protects a target named by ANY form the resolver accepts.

    This is the GHI #689 class fix's proof. It does not compare two functions —
    it asserts the BEHAVIOR that can only hold if the archive guard resolves
    through the same resolver the CREATE/RESUME path uses. Re-duplicating the
    resolver and letting it diverge on any of these forms fails this test.
    """

    def _assert_target_protected(self, pointer_form: str) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write_handoff(base, "target.md", timestamp=_OLD_TS)
            _write_handoff(base, "referrer.md", timestamp=_OLD_TS, continues_from=pointer_form)
            _write_handoff(base, "loose.md", timestamp=_OLD_TS)

            plan = plan_archive(base_path=base, older_than_days=30, now=_NOW)

            self.assertNotIn(
                ".gzkit/handoffs/target.md",
                plan.eligible,
                f"a chain target named as {pointer_form!r} must never be archived",
            )
            # Negative control: a no-op planner would trivially pass the guard
            # above, so prove an uncoupled handoff IS still eligible.
            self.assertIn(
                ".gzkit/handoffs/loose.md",
                plan.eligible,
                "an uncoupled old handoff must remain eligible",
            )

    def test_bare_pointer_protects_target(self) -> None:
        self._assert_target_protected("target.md")

    def test_dot_slash_pointer_protects_target(self) -> None:
        self._assert_target_protected("./target.md")

    def test_project_relative_pointer_protects_target(self) -> None:
        self._assert_target_protected(".gzkit/handoffs/target.md")


if __name__ == "__main__":
    unittest.main()
