"""Tests for the git-facing merge-driver adapter (GHI #811)."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from gzkit.commands.init_cmd import _jsonl_merge_statuses
from gzkit.commands.ledger import (
    JSONL_MERGE_PATTERNS,
    MERGE_DRIVER_NAME,
    ensure_jsonl_merge_attributes,
    ensure_jsonl_merge_driver,
    ledger_merge_driver_cmd,
)
from tests.commands.common import _isolated_git_env


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
            env=_isolated_git_env(),
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

            configured = subprocess.run(  # noqa: S603 — argv this test builds, list form
                ["git", "config", "--get", f"merge.{MERGE_DRIVER_NAME}.driver"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
                errors="replace",
                env=_isolated_git_env(),
            ).stdout.strip()

        self.assertEqual(configured, "uv run gz ledger merge-driver %O %A %B")

    def test_outside_a_repository_reports_nothing_registered(self) -> None:
        """A failed `git config` write is not a registration (GHI #1363).

        Repair runs this on every invocation; a directory that is not a git
        repository must not be told, each time, that a driver was registered.
        """
        with tempfile.TemporaryDirectory() as td:
            self.assertFalse(ensure_jsonl_merge_driver(Path(td)))


_ROUTED_FILES = (
    ".gzkit/ledger.jsonl",
    ".gzkit/insights/agent-insights.jsonl",
    ".gzkit/corpus/AGENTS.md.jsonl",
)


class TestEnsureMergeAttributes(unittest.TestCase):
    """An adopter's `.gitattributes` routes gzkit's append-only JSONL to the driver (GHI #1363).

    The driver in local config is half of #811's fix; without the routing lines
    in the adopter's own `.gitattributes`, git never invokes it.
    """

    def _init_repo(self, root: Path) -> None:
        subprocess.run(
            ["git", "init", "-q"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            errors="replace",
            env=_isolated_git_env(),
        )

    def _merge_attribute(self, root: Path, path: str) -> str:
        out = subprocess.run(  # noqa: S603 — argv this test builds, list form
            ["git", "check-attr", "merge", "--", path],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            errors="replace",
            env=_isolated_git_env(),
        ).stdout
        return out.rsplit(": ", 1)[-1].strip()

    def test_absent_file_is_created_and_routes_every_append_only_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_repo(root)

            added = ensure_jsonl_merge_attributes(root)

            self.assertEqual(added, list(JSONL_MERGE_PATTERNS))
            for path in _ROUTED_FILES:
                self.assertEqual(self._merge_attribute(root, path), MERGE_DRIVER_NAME, path)

    def test_existing_rules_are_kept_and_missing_lines_added_once(self) -> None:
        adopter = "* text=auto eol=lf\n*.png binary\n.gzkit/ledger.jsonl merge=gzkit-jsonl"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_repo(root)
            attributes = root / ".gitattributes"
            attributes.write_text(adopter, encoding="utf-8")

            added = ensure_jsonl_merge_attributes(root)
            after_first = attributes.read_text(encoding="utf-8")
            again = ensure_jsonl_merge_attributes(root)

            self.assertEqual(added, [p for p in JSONL_MERGE_PATTERNS if p != ".gzkit/ledger.jsonl"])
            self.assertTrue(after_first.startswith(adopter + "\n"), after_first)
            self.assertEqual(again, [])
            self.assertEqual(attributes.read_text(encoding="utf-8"), after_first)
            # The adopter's own `binary` rule still applies: the macro unsets merge.
            self.assertEqual(self._merge_attribute(root, "logo.png"), "unset")
            for path in _ROUTED_FILES:
                self.assertEqual(self._merge_attribute(root, path), MERGE_DRIVER_NAME, path)

    def test_dry_run_reports_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            planned = ensure_jsonl_merge_attributes(root, dry_run=True)

            self.assertEqual(planned, list(JSONL_MERGE_PATTERNS))
            self.assertFalse((root / ".gitattributes").exists())

    def test_existing_bytes_are_kept_exactly(self) -> None:
        """Appending never re-encodes: a BOM, CRLF and non-UTF-8 bytes survive."""
        adopter = b"\xef\xbb\xbf* text=auto\r\n# caf\xe9\r\n*.png binary"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_repo(root)
            attributes = root / ".gitattributes"
            attributes.write_bytes(adopter)

            added = ensure_jsonl_merge_attributes(root)

            self.assertEqual(added, list(JSONL_MERGE_PATTERNS))
            self.assertTrue(attributes.read_bytes().startswith(adopter), attributes.read_bytes())
            for path in _ROUTED_FILES:
                self.assertEqual(self._merge_attribute(root, path), MERGE_DRIVER_NAME, path)

    def test_anchored_pattern_counts_as_the_same_route(self) -> None:
        """`/.gzkit/ledger.jsonl` and `.gzkit/ledger.jsonl` name one file at the root."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".gitattributes").write_text(
                "/.gzkit/ledger.jsonl merge=gzkit-jsonl\n", encoding="utf-8"
            )

            planned = ensure_jsonl_merge_attributes(root, dry_run=True)

            self.assertNotIn(".gzkit/ledger.jsonl", planned)

    def test_gzkits_own_attributes_route_exactly_the_shipped_set(self) -> None:
        """The repository and the wheel name one set; neither may drift from the other."""
        repo_root = Path(__file__).resolve().parents[1]
        text = (repo_root / ".gitattributes").read_text(encoding="utf-8")
        routed = {
            line.split()[0]
            for line in text.splitlines()
            if line.split() and f"merge={MERGE_DRIVER_NAME}" in line.split()[1:]
        }

        self.assertEqual(routed, set(JSONL_MERGE_PATTERNS))


class TestJsonlMergeStatuses(unittest.TestCase):
    """`gz init` announces both halves on a dry run and writes neither (GHI #1363)."""

    def _git(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(  # noqa: S603 — argv this test builds, list form
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            errors="replace",
            env=_isolated_git_env(),
        )

    def test_dry_run_announces_the_driver_and_registers_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._git(root, "init", "-q")

            planned = _jsonl_merge_statuses(root, dry_run=True)

            self.assertEqual(len(planned), 2, planned)
            self.assertIn(MERGE_DRIVER_NAME, planned[1])
            self.assertFalse((root / ".gitattributes").exists())
            key = f"merge.{MERGE_DRIVER_NAME}.driver"
            self.assertNotEqual(self._git(root, "config", "--get", key).returncode, 0)

            written = _jsonl_merge_statuses(root)

            self.assertEqual(len(written), len(planned), written)
            self.assertEqual(_jsonl_merge_statuses(root, dry_run=True), [])

    def test_dry_run_outside_a_repository_announces_only_the_routing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            planned = _jsonl_merge_statuses(Path(td), dry_run=True)

            self.assertEqual(len(planned), 1, planned)
            self.assertIn(".gitattributes", planned[0])


if __name__ == "__main__":
    unittest.main()
