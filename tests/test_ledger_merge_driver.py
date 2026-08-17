"""Tests for the git-facing merge-driver adapter (GHI #811)."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from gzkit.commands.ledger import (
    MERGE_DRIVER_NAME,
    ensure_jsonl_merge_driver,
    ledger_merge_driver_cmd,
)


def _row(ts: str, event: str = "project_init") -> str:
    return json.dumps({"schema": "gzkit.ledger.v1", "event": event, "id": "gzkit", "ts": ts})


class TestLedgerMergeDriverCmd(unittest.TestCase):
    """The adapter writes merged rows over `ours` and signals conflict via exit 1."""

    def _write_sides(self, root: Path, ours: list[str], theirs: list[str], base: list[str]) -> None:
        (root / "O").write_text("\n".join(base) + "\n", encoding="utf-8")
        (root / "A").write_text("\n".join(ours) + "\n", encoding="utf-8")
        (root / "B").write_text("\n".join(theirs) + "\n", encoding="utf-8")

    def test_merged_result_is_written_over_ours(self) -> None:
        """Git reads the result from the `ours` path, so that is where it must land."""
        base = [_row("2026-02-14T00:00:00+00:00")]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_sides(
                root,
                ours=base + [_row("2026-02-14T00:00:03+00:00")],
                theirs=base + [_row("2026-02-14T00:00:01+00:00")],
                base=base,
            )
            ledger_merge_driver_cmd(str(root / "O"), str(root / "A"), str(root / "B"))
            written = [
                json.loads(line)["ts"]
                for line in (root / "A").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]

        self.assertEqual(
            written,
            [
                "2026-02-14T00:00:00+00:00",
                "2026-02-14T00:00:01+00:00",
                "2026-02-14T00:00:03+00:00",
            ],
        )

    def test_unmergeable_sides_exit_nonzero_and_leave_ours_untouched(self) -> None:
        """A refusal must not half-write: git needs the conflict intact for the human."""
        base = [_row("2026-02-14T00:00:00+00:00"), _row("2026-02-14T00:00:01+00:00")]
        rewritten = [_row("2026-02-14T00:00:00+00:00"), _row("2026-02-14T00:00:09+00:00")]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_sides(
                root,
                ours=rewritten,
                theirs=base + [_row("2026-02-14T00:00:02+00:00")],
                base=base,
            )
            before = (root / "A").read_text(encoding="utf-8")

            with self.assertRaises(SystemExit) as caught:
                ledger_merge_driver_cmd(str(root / "O"), str(root / "A"), str(root / "B"))

            self.assertEqual(caught.exception.code, 1)
            self.assertEqual((root / "A").read_text(encoding="utf-8"), before)


class TestEnsureMergeDriverRegistration(unittest.TestCase):
    """Registration is per-clone, so it must self-heal and must not thrash."""

    def _init_repo(self, root: Path) -> None:
        subprocess.run(
            ["git", "init", "-q"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            errors="replace",
        )

    def test_registers_driver_then_is_idempotent(self) -> None:
        """First call installs; a second call reports nothing to do.

        Idempotence is what lets `gz git-sync` call this unconditionally on
        every apply without rewriting config or emitting a warning each run.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_repo(root)

            self.assertTrue(ensure_jsonl_merge_driver(root), "first call should register")
            self.assertFalse(ensure_jsonl_merge_driver(root), "second call should be a no-op")

            configured = subprocess.run(
                ["git", "config", "--get", f"merge.{MERGE_DRIVER_NAME}.driver"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
                errors="replace",
            ).stdout.strip()

        self.assertEqual(configured, "uv run gz ledger merge-driver %O %A %B")


if __name__ == "__main__":
    unittest.main()
