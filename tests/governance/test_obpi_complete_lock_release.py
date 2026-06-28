"""Unit tests for the token-block exit edge: mechanical lock-surrender + handoff
written at OBPI completion.

Derived from GHI #619 ("completed OBPI has no register path, only handoff/abandon")
and token-block discipline § Sub-Invariant 2 (register-entry minimum-information).

The completion edge of the token-block lifecycle is mechanical: `gz obpi complete`
writes a full register entry (a completion handoff) and, if a lock is held,
surrenders it (deletes the lock + emits an ``obpi_lock_released`` event citing the
handoff). No operator prompt, no manual ``gz obpi lock release`` chore — that ad-hoc
prompt was the defect this work corrects.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.commands.obpi_complete import _surrender_lock_at_completion
from gzkit.handoff_validation import (
    parse_frontmatter,
    validate_handoff_document,
    validate_no_placeholders,
    write_completion_handoff,
)
from gzkit.ledger import Ledger
from gzkit.lock_manager import LockData, read_lock, write_lock

_OBPI = "OBPI-0.0.41-09-completion-surrender"


def _scaffold(tmp: Path) -> tuple[Path, str]:
    """Create a minimal project root with a ledger and a brief; return (root, brief_rel)."""
    root = tmp
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    (root / ".gzkit" / "ledger.jsonl").write_text("", encoding="utf-8")
    brief = root / "docs" / "brief.md"
    brief.parent.mkdir(parents=True, exist_ok=True)
    brief.write_text(f"# {_OBPI}\n", encoding="utf-8")
    return root, brief.relative_to(root).as_posix()


class TestWriteCompletionHandoff(unittest.TestCase):
    """The auto-drafted completion handoff is a valid, non-abandoned register entry."""

    def _write(self, root: Path, brief_rel: str, *, implementation_summary: str) -> Path:
        return write_completion_handoff(
            root,
            obpi_id=_OBPI,
            agent="claude-code",
            attestor="g0",
            attestation_text="attest completed -- wired the token-block exit edge",
            implementation_summary=implementation_summary,
            key_proof="uv run -m unittest passes.",
            last_lock_event_timestamp="2026-06-28T10:00:00+00:00",
            commit_sha="abcdef0",
            branch="main",
            brief_rel_path=brief_rel,
        )

    def test_produces_validator_clean_handoff(self) -> None:
        # GHI #619: the mechanical completion handoff must be a *valid* register
        # entry — find_handoff_for_release accepts only non-abandoned handoffs that
        # pass the full seven-section + referenced-file contract.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root, brief_rel = _scaffold(root)
            path = self._write(root, brief_rel, implementation_summary="Added surrender edge.")
            self.assertTrue(path.is_file())
            content = path.read_text(encoding="utf-8")
            self.assertEqual(validate_handoff_document(content, root), [])

    def test_frontmatter_carries_min_info_and_is_not_abandoned(self) -> None:
        # Token-block § Sub-Invariant 2: last_lock_event_timestamp, last_commit_sha,
        # branch are the minimum-information fields the coupling consumer requires.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root, brief_rel = _scaffold(root)
            content = self._write(root, brief_rel, implementation_summary="x").read_text(
                encoding="utf-8"
            )
            fm = parse_frontmatter(content)
            self.assertEqual(fm["mode"], "CREATE")
            self.assertEqual(fm["branch"], "main")
            self.assertIn("last_commit_sha", fm)
            self.assertIn("last_lock_event_timestamp", fm)
            self.assertIsNone(fm.get("abandoned"))

    def test_adr_id_normalized_to_bare_form(self) -> None:
        # HandoffFrontmatter requires bare ^ADR-X.Y.Z$ — the slug-bearing parent id
        # must be normalized from the OBPI semver, not passed through.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root, brief_rel = _scaffold(root)
            content = self._write(root, brief_rel, implementation_summary="x").read_text(
                encoding="utf-8"
            )
            self.assertRegex(parse_frontmatter(content)["adr_id"], r"^ADR-\d+\.\d+\.\d+$")

    def test_ellipsis_in_evidence_is_sanitized(self) -> None:
        # Auto-drafted text may carry an elision; the placeholder gate forbids a
        # bare "..." — the writer must neutralize it rather than emit a handoff that
        # fails its own validator at gz check time.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root, brief_rel = _scaffold(root)
            content = self._write(
                root, brief_rel, implementation_summary="did A ... then B"
            ).read_text(encoding="utf-8")
            self.assertEqual(validate_no_placeholders(content), [])


class TestSurrenderLockAtCompletion(unittest.TestCase):
    """Completion mechanically surrenders a held lock and pairs it with a register entry."""

    def _surrender(self, root: Path, ledger: Ledger, brief_rel: str) -> None:
        _surrender_lock_at_completion(
            project_root=root,
            ledger=ledger,
            obpi_id=_OBPI,
            attestor="g0",
            attestation_text="attest completed -- exit edge",
            implementation_summary="Surrender edge wired.",
            key_proof="unittest passes.",
            commit_sha="abcdef0",
            brief_rel_path=brief_rel,
        )

    @staticmethod
    def _events(root: Path) -> list[dict]:
        raw = (root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
        return [json.loads(line) for line in raw.splitlines() if line.strip()]

    @staticmethod
    def _released(events: list[dict]) -> list[dict]:
        return [e for e in events if e.get("event") == "obpi_lock_released"]

    @staticmethod
    def _handoff_path(event: dict) -> str | None:
        return event.get("handoff_path") or event.get("extra", {}).get("handoff_path")

    def test_releases_held_lock_and_emits_event_citing_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root, brief_rel = _scaffold(root)
            write_lock(
                root,
                LockData(
                    obpi_id=_OBPI,
                    agent="implementer",
                    pid=123,
                    session_id="s",
                    claimed_at="2026-06-28T09:00:00+00:00",
                    branch="main",
                    ttl_minutes=1440,
                ),
            )
            self.assertIsNotNone(read_lock(root, _OBPI))

            self._surrender(root, Ledger(root / ".gzkit" / "ledger.jsonl"), brief_rel)

            self.assertIsNone(read_lock(root, _OBPI))  # token surrendered
            released = self._released(self._events(root))
            self.assertEqual(len(released), 1)
            hp = self._handoff_path(released[0])
            self.assertIsNotNone(hp)
            self.assertTrue((root / hp).is_file())  # cited register entry exists

    def test_no_lock_writes_handoff_but_no_release_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root, brief_rel = _scaffold(root)
            self.assertIsNone(read_lock(root, _OBPI))

            self._surrender(root, Ledger(root / ".gzkit" / "ledger.jsonl"), brief_rel)

            # No lock was held → no surrender event, but the handoff is still written.
            self.assertEqual(self._released(self._events(root)), [])
            handoffs = list((root / ".gzkit" / "handoffs").glob(f"*-{_OBPI}-complete.md"))
            self.assertEqual(len(handoffs), 1)


if __name__ == "__main__":
    unittest.main()
