"""Tests for gz chores propose-ghi — OBPI-0.0.26-04."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gzkit.traceability import covers


def _write_proposal(path: Path, **kwargs: object) -> None:
    """Write a minimal ProposalRecord JSON file at path."""
    defaults: dict[str, object] = {
        "cluster_key": "dim:clarity:low",
        "recurrence_count": 3,
        "source_artifact_ids": ["ADR-0.1.0", "ADR-0.2.0", "ADR-0.3.0"],
        "source_artifact_paths": [
            "artifacts/justify/ADR-0.1.0.md",
            "artifacts/justify/ADR-0.2.0.md",
            "artifacts/justify/ADR-0.3.0.md",
        ],
        "summary": "Dimension 'clarity' scored in the 'low' band across 3 distinct artifacts",
        "proposed_rule_target": "docs/governance/clarity-low-improvement.md",
        "content_hash": "abc123def456abcd",
        "filed": False,
        "ghi_url": None,
        "advisory": False,
    }
    defaults.update(kwargs)
    path.write_text(json.dumps(defaults, indent=2), encoding="utf-8")


def _make_proofs_dir(tmp_path: Path, slug: str = "eval-feedback-cluster") -> Path:
    """Create and return the proofs dir for a slug under tmp_path."""
    proofs_dir = tmp_path / slug / "proofs"
    proofs_dir.mkdir(parents=True, exist_ok=True)
    return proofs_dir


def _chores_root_patcher(tmp_path: Path) -> object:
    """Return a patch context that makes _project_chores_root_path return tmp_path."""
    return patch(
        "gzkit.commands.chores_propose_ghi_cmd._project_chores_root_path",
        return_value=tmp_path,
    )


class TestChoreProposeGhiTtyConfirm(unittest.TestCase):
    """REQ-0.0.26-04-01: TTY + PROPOSE confirmation → GHI filed."""

    @covers("REQ-0.0.26-04-01")
    @covers("REQ-0.0.26-04-12")
    def test_tty_confirm_files_ghi(self) -> None:
        """TTY + PROPOSE confirmation → gh issue create called, record marked filed."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            proofs_dir = _make_proofs_dir(tmp_path)
            proposal_file = proofs_dir / "proposal-20260101T120000000000.json"
            _write_proposal(proposal_file)

            fake_result = MagicMock()
            fake_result.stdout = "https://github.com/owner/repo/issues/99\n"

            with (
                _chores_root_patcher(tmp_path),
                patch("gzkit.commands.chores_propose_ghi_cmd.sys") as mock_sys,
                patch(
                    "gzkit.commands.chores_propose_ghi_cmd.subprocess.run",
                    return_value=fake_result,
                ) as mock_run,
            ):
                mock_sys.stdin.isatty.return_value = True
                mock_sys.stdout.isatty.return_value = True

                with patch("builtins.input", return_value="PROPOSE"):
                    from gzkit.commands.chores import chores_propose_ghi

                    chores_propose_ghi("eval-feedback-cluster")

            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            self.assertIn("gh", call_args)
            self.assertIn("issue", call_args)
            self.assertIn("create", call_args)

            updated = json.loads(proposal_file.read_text(encoding="utf-8"))
            self.assertTrue(updated["filed"])
            self.assertEqual(updated["ghi_url"], "https://github.com/owner/repo/issues/99")

    @covers("REQ-0.0.26-04-01")
    def test_ghi_title_pattern(self) -> None:
        """Title follows 'eval-feedback: <summary> (recurrence >= N)'."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            proofs_dir = _make_proofs_dir(tmp_path)
            proposal_file = proofs_dir / "proposal-20260101T120000000000.json"
            _write_proposal(
                proposal_file,
                summary="Dimension 'clarity' scored in the 'low' band across 3 artifacts",
                recurrence_count=5,
            )

            fake_result = MagicMock()
            fake_result.stdout = "https://github.com/owner/repo/issues/100\n"

            captured_title: list[str] = []

            def capture_run(cmd: list[str], **_kwargs: object) -> MagicMock:
                for i, arg in enumerate(cmd):
                    if arg == "--title" and i + 1 < len(cmd):
                        captured_title.append(cmd[i + 1])
                return fake_result

            with (
                _chores_root_patcher(tmp_path),
                patch("gzkit.commands.chores_propose_ghi_cmd.sys") as mock_sys,
                patch(
                    "gzkit.commands.chores_propose_ghi_cmd.subprocess.run",
                    side_effect=capture_run,
                ),
            ):
                mock_sys.stdin.isatty.return_value = True
                mock_sys.stdout.isatty.return_value = True

                with patch("builtins.input", return_value="PROPOSE"):
                    from gzkit.commands.chores import chores_propose_ghi

                    chores_propose_ghi("eval-feedback-cluster")

            self.assertTrue(len(captured_title) > 0, "No --title argument captured")
            title = captured_title[0]
            self.assertTrue(
                title.startswith("eval-feedback:"),
                f"Title should start with 'eval-feedback:' but was: {title!r}",
            )
            self.assertIn(
                "recurrence",
                title.lower(),
                f"Title should mention recurrence but was: {title!r}",
            )
            self.assertIn(
                "5",
                title,
                f"Title should include recurrence count 5 but was: {title!r}",
            )

    @covers("REQ-0.0.26-04-01")
    def test_ghi_body_includes_required_fields(self) -> None:
        """Body includes cluster_key, recurrence_count, source_artifact_ids, summary."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            proofs_dir = _make_proofs_dir(tmp_path)
            proposal_file = proofs_dir / "proposal-20260101T120000000000.json"
            _write_proposal(proposal_file)

            fake_result = MagicMock()
            fake_result.stdout = "https://github.com/owner/repo/issues/101\n"

            captured_body: list[str] = []

            def capture_run(cmd: list[str], **_kwargs: object) -> MagicMock:
                for i, arg in enumerate(cmd):
                    if arg == "--body" and i + 1 < len(cmd):
                        captured_body.append(cmd[i + 1])
                return fake_result

            with (
                _chores_root_patcher(tmp_path),
                patch("gzkit.commands.chores_propose_ghi_cmd.sys") as mock_sys,
                patch(
                    "gzkit.commands.chores_propose_ghi_cmd.subprocess.run",
                    side_effect=capture_run,
                ),
            ):
                mock_sys.stdin.isatty.return_value = True
                mock_sys.stdout.isatty.return_value = True

                with patch("builtins.input", return_value="PROPOSE"):
                    from gzkit.commands.chores import chores_propose_ghi

                    chores_propose_ghi("eval-feedback-cluster")

            self.assertTrue(len(captured_body) > 0, "No --body argument captured")
            body = captured_body[0]
            self.assertIn("dim:clarity:low", body, "Body should contain cluster_key")
            self.assertIn("3", body, "Body should contain recurrence_count")
            self.assertIn("ADR-0.1.0", body, "Body should contain source_artifact_ids")
            self.assertIn(
                "clarity-low-improvement",
                body,
                "Body should contain proposed_rule_target",
            )


class TestChoreProposeGhiHeadless(unittest.TestCase):
    """REQ-0.0.26-04-02: Headless → no GHI, record advisory=True."""

    @covers("REQ-0.0.26-04-02")
    def test_headless_advisory_only(self) -> None:
        """No TTY → no gh call, record annotated advisory=True."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            proofs_dir = _make_proofs_dir(tmp_path)
            proposal_file = proofs_dir / "proposal-20260101T120000000000.json"
            _write_proposal(proposal_file)

            with (
                _chores_root_patcher(tmp_path),
                patch("gzkit.commands.chores_propose_ghi_cmd.sys") as mock_sys,
                patch("gzkit.commands.chores_propose_ghi_cmd.subprocess.run") as mock_run,
            ):
                mock_sys.stdin.isatty.return_value = False
                mock_sys.stdout.isatty.return_value = False

                from gzkit.commands.chores import chores_propose_ghi

                chores_propose_ghi("eval-feedback-cluster")

            mock_run.assert_not_called()

            updated = json.loads(proposal_file.read_text(encoding="utf-8"))
            self.assertTrue(
                updated["advisory"],
                "Record should be marked advisory=True in headless mode",
            )
            self.assertFalse(
                updated["filed"],
                "Record should NOT be marked filed in headless mode",
            )


class TestChoreProposeGhiIdempotent(unittest.TestCase):
    """REQ-0.0.26-04-03: Idempotency checks."""

    @covers("REQ-0.0.26-04-03")
    def test_refile_idempotent(self) -> None:
        """Already-filed record is skipped on re-run."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            proofs_dir = _make_proofs_dir(tmp_path)
            proposal_file = proofs_dir / "proposal-20260101T120000000000.json"
            _write_proposal(
                proposal_file,
                filed=True,
                ghi_url="https://github.com/owner/repo/issues/42",
            )

            with (
                _chores_root_patcher(tmp_path),
                patch("gzkit.commands.chores_propose_ghi_cmd.sys") as mock_sys,
                patch("gzkit.commands.chores_propose_ghi_cmd.subprocess.run") as mock_run,
            ):
                mock_sys.stdin.isatty.return_value = True
                mock_sys.stdout.isatty.return_value = True

                from gzkit.commands.chores import chores_propose_ghi

                chores_propose_ghi("eval-feedback-cluster")

            mock_run.assert_not_called()

    @covers("REQ-0.0.26-04-03")
    def test_no_proposals_exits_cleanly(self) -> None:
        """Empty proofs dir → clean exit, no error."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            with _chores_root_patcher(tmp_path):
                from gzkit.commands.chores import chores_propose_ghi

                # Should not raise
                chores_propose_ghi("eval-feedback-cluster")


if __name__ == "__main__":
    unittest.main()
