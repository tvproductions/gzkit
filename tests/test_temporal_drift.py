"""Tests for the temporal drift detection module.

@covers ADR-0.25.0-core-infrastructure-pattern-absorption
@covers OBPI-0.25.0-26-drift-detection-pattern
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.temporal_drift import (
    DriftResult,
    ObpiDriftResult,
    _count_commits_between,
    _get_head_commit,
    _is_ancestor,
    _resolve_full_commit,
    classify_drift,
    detect_drift,
    detect_obpi_drift,
)
from gzkit.traceability import covers


def _git(cwd: Path, *args: str) -> str:
    """Run a git command for test setup; return stdout (UTF-8, stripped)."""
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout.strip()


def _init_repo(repo: Path) -> None:
    """Initialize a deterministic temp repo with a single 'main' branch."""
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "commit.gpgsign", "false")


def _commit(repo: Path, filename: str, content: str, message: str) -> str:
    """Write a file, stage it, commit, and return the full commit SHA."""
    (repo / filename).write_text(content, encoding="utf-8")
    _git(repo, "add", filename)
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


# ---------------------------------------------------------------------------
# Pure classifier tests (REQ-0.25.0-26-01, REQ-0.25.0-26-03)
# ---------------------------------------------------------------------------


class TestClassifyDriftSameCommit(unittest.TestCase):
    """@covers REQ-0.25.0-26-01
    @covers REQ-0.25.0-26-03
    """

    @covers("REQ-0.25.0-26-01")
    def test_same_commit_returns_none_status(self) -> None:
        sha = "a" * 40
        result = classify_drift("ADR-0.25.0", sha, sha, True, 0)
        self.assertIsInstance(result, DriftResult)
        self.assertEqual(result.status, "none")
        self.assertEqual(result.commits_ahead, 0)
        self.assertIn("validated at current HEAD", result.message)
        self.assertIn(sha[:7], result.message)


class TestClassifyDriftCommitsAhead(unittest.TestCase):
    """@covers REQ-0.25.0-26-03"""

    @covers("REQ-0.25.0-26-03")
    def test_anchor_is_ancestor_returns_commits_ahead(self) -> None:
        anchor = "a" * 40
        head = "b" * 40
        result = classify_drift("ADR-0.25.0", anchor, head, True, 5)
        self.assertEqual(result.status, "commits_ahead")
        self.assertEqual(result.commits_ahead, 5)
        self.assertIn("validated 5 commit(s) ago", result.message)

    @covers("REQ-0.25.0-26-03")
    def test_count_none_coerces_to_zero(self) -> None:
        anchor = "a" * 40
        head = "b" * 40
        result = classify_drift("ADR-0.25.0", anchor, head, True, None)
        self.assertEqual(result.status, "commits_ahead")
        self.assertEqual(result.commits_ahead, 0)


class TestClassifyDriftDiverged(unittest.TestCase):
    """@covers REQ-0.25.0-26-03"""

    @covers("REQ-0.25.0-26-03")
    def test_anchor_not_ancestor_returns_diverged(self) -> None:
        anchor = "a" * 40
        head = "b" * 40
        result = classify_drift("ADR-0.25.0", anchor, head, False, None)
        self.assertEqual(result.status, "diverged")
        self.assertIsNone(result.commits_ahead)
        self.assertIn("has diverged from HEAD", result.message)

    @covers("REQ-0.25.0-26-03")
    def test_anchor_not_in_repo_returns_diverged(self) -> None:
        anchor = "a" * 40
        head = "b" * 40
        result = classify_drift("ADR-0.25.0", anchor, head, None, None)
        self.assertEqual(result.status, "diverged")
        self.assertIsNone(result.commits_ahead)
        self.assertIn("not found in repository history", result.message)


class TestClassifyDriftFrozen(unittest.TestCase):
    """@covers REQ-0.25.0-26-03"""

    @covers("REQ-0.25.0-26-03")
    def test_drift_result_is_frozen(self) -> None:
        sha = "a" * 40
        result = classify_drift("ADR-0.25.0", sha, sha, True, 0)
        with self.assertRaises(ValidationError):
            result.status = "diverged"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Git helpers — real temp repo, no mocks (REQ-0.25.0-26-03)
# ---------------------------------------------------------------------------


class TestGitHelpersRealRepo(unittest.TestCase):
    """@covers REQ-0.25.0-26-03"""

    @covers("REQ-0.25.0-26-03")
    def test_get_head_commit_returns_full_sha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            sha = _commit(repo, "a.txt", "one\n", "first")
            self.assertEqual(_get_head_commit(repo), sha)
            self.assertEqual(len(sha), 40)

    @covers("REQ-0.25.0-26-03")
    def test_resolve_full_commit_from_short_sha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            sha = _commit(repo, "a.txt", "one\n", "first")
            resolved = _resolve_full_commit(repo, sha[:7])
            self.assertEqual(resolved, sha)

    @covers("REQ-0.25.0-26-03")
    def test_resolve_full_commit_unknown_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _commit(repo, "a.txt", "one\n", "first")
            self.assertIsNone(_resolve_full_commit(repo, "deadbee"))

    @covers("REQ-0.25.0-26-03")
    def test_is_ancestor_linear_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            first = _commit(repo, "a.txt", "1\n", "c1")
            second = _commit(repo, "a.txt", "2\n", "c2")
            self.assertIs(_is_ancestor(repo, first, second), True)
            self.assertIs(_is_ancestor(repo, second, first), False)

    @covers("REQ-0.25.0-26-03")
    def test_is_ancestor_unknown_commit_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            head = _commit(repo, "a.txt", "1\n", "c1")
            self.assertIsNone(_is_ancestor(repo, "0" * 40, head))

    @covers("REQ-0.25.0-26-03")
    def test_count_commits_between_linear(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            first = _commit(repo, "a.txt", "1\n", "c1")
            _commit(repo, "a.txt", "2\n", "c2")
            head = _commit(repo, "a.txt", "3\n", "c3")
            self.assertEqual(_count_commits_between(repo, first, head), 2)

    @covers("REQ-0.25.0-26-03")
    def test_count_commits_between_unknown_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            head = _commit(repo, "a.txt", "1\n", "c1")
            self.assertIsNone(_count_commits_between(repo, "0" * 40, head))


# ---------------------------------------------------------------------------
# detect_drift orchestrator (REQ-0.25.0-26-01, REQ-0.25.0-26-02)
# ---------------------------------------------------------------------------


def _make_ledger(root: Path, events: list[dict]) -> None:
    """Write a JSONL ledger at <root>/.gzkit/ledger.jsonl from a list of dicts."""
    ledger_dir = root / ".gzkit"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = ledger_dir / "ledger.jsonl"
    with ledger_path.open("w", encoding="utf-8") as fh:
        for event in events:
            fh.write(json.dumps(event) + "\n")


class TestDetectDriftOrchestrator(unittest.TestCase):
    """@covers REQ-0.25.0-26-01
    @covers REQ-0.25.0-26-02
    """

    @covers("REQ-0.25.0-26-01")
    def test_returns_none_when_ledger_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _commit(repo, "a.txt", "1\n", "c1")
            self.assertIsNone(detect_drift("ADR-0.25.0", project_root=repo))

    @covers("REQ-0.25.0-26-01")
    def test_returns_none_when_no_anchored_audit_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _commit(repo, "a.txt", "1\n", "c1")
            _make_ledger(
                repo,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "audit_receipt_emitted",
                        "id": "ADR-0.25.0",
                        "ts": "2026-01-01T00:00:00+00:00",
                        "receipt_event": "completed",
                        "attestor": "Tester",
                    }
                ],
            )
            self.assertIsNone(detect_drift("ADR-0.25.0", project_root=repo))

    @covers("REQ-0.25.0-26-02")
    def test_anchor_at_head_yields_none_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            sha = _commit(repo, "a.txt", "1\n", "c1")
            _make_ledger(
                repo,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "audit_receipt_emitted",
                        "id": "ADR-0.25.0",
                        "ts": "2026-01-01T00:00:00+00:00",
                        "receipt_event": "validated",
                        "attestor": "Tester",
                        "anchor": {"commit": sha[:7], "semver": "0.25.0"},
                    }
                ],
            )
            result = detect_drift("ADR-0.25.0", project_root=repo)
            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual(result.status, "none")
            self.assertEqual(result.adr_id, "ADR-0.25.0")
            self.assertEqual(result.anchor_commit, sha)

    @covers("REQ-0.25.0-26-02")
    def test_anchor_two_commits_behind_yields_commits_ahead(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            anchor_sha = _commit(repo, "a.txt", "1\n", "c1")
            _commit(repo, "a.txt", "2\n", "c2")
            _commit(repo, "a.txt", "3\n", "c3")
            _make_ledger(
                repo,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "audit_receipt_emitted",
                        "id": "ADR-0.25.0",
                        "ts": "2026-01-01T00:00:00+00:00",
                        "receipt_event": "validated",
                        "attestor": "Tester",
                        "anchor": {"commit": anchor_sha[:7], "semver": "0.25.0"},
                    }
                ],
            )
            result = detect_drift("ADR-0.25.0", project_root=repo)
            assert result is not None
            self.assertEqual(result.status, "commits_ahead")
            self.assertEqual(result.commits_ahead, 2)

    @covers("REQ-0.25.0-26-02")
    def test_unresolvable_anchor_yields_diverged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _commit(repo, "a.txt", "1\n", "c1")
            _make_ledger(
                repo,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "audit_receipt_emitted",
                        "id": "ADR-0.25.0",
                        "ts": "2026-01-01T00:00:00+00:00",
                        "receipt_event": "validated",
                        "attestor": "Tester",
                        "anchor": {"commit": "deadbee", "semver": "0.25.0"},
                    }
                ],
            )
            result = detect_drift("ADR-0.25.0", project_root=repo)
            assert result is not None
            self.assertEqual(result.status, "diverged")
            self.assertIsNone(result.commits_ahead)

    @covers("REQ-0.25.0-26-02")
    def test_latest_anchored_event_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            old = _commit(repo, "a.txt", "1\n", "c1")
            new = _commit(repo, "a.txt", "2\n", "c2")
            _make_ledger(
                repo,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "audit_receipt_emitted",
                        "id": "ADR-0.25.0",
                        "ts": "2026-01-01T00:00:00+00:00",
                        "receipt_event": "validated",
                        "attestor": "Tester",
                        "anchor": {"commit": old[:7], "semver": "0.25.0"},
                    },
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "audit_receipt_emitted",
                        "id": "ADR-0.25.0",
                        "ts": "2026-01-02T00:00:00+00:00",
                        "receipt_event": "validated",
                        "attestor": "Tester",
                        "anchor": {"commit": new[:7], "semver": "0.25.0"},
                    },
                ],
            )
            result = detect_drift("ADR-0.25.0", project_root=repo)
            assert result is not None
            self.assertEqual(result.anchor_commit, new)
            self.assertEqual(result.status, "none")


# ---------------------------------------------------------------------------
# detect_obpi_drift orchestrator (REQ-0.25.0-26-02, REQ-0.25.0-26-04)
# ---------------------------------------------------------------------------


class TestDetectObpiDriftOrchestrator(unittest.TestCase):
    """@covers REQ-0.25.0-26-02
    @covers REQ-0.25.0-26-04
    """

    @covers("REQ-0.25.0-26-04")
    def test_empty_when_no_obpi_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _commit(repo, "a.txt", "1\n", "c1")
            _make_ledger(repo, [])
            self.assertEqual(detect_obpi_drift("ADR-0.25.0", project_root=repo), [])

    @covers("REQ-0.25.0-26-02")
    def test_filters_by_parent_adr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            sha = _commit(repo, "a.txt", "1\n", "c1")
            _make_ledger(
                repo,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_receipt_emitted",
                        "id": "OBPI-0.25.0-26",
                        "parent": "ADR-0.25.0",
                        "ts": "2026-01-01T00:00:00+00:00",
                        "receipt_event": "completed",
                        "attestor": "Tester",
                        "anchor": {"commit": sha[:7], "semver": "0.25.0"},
                    },
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_receipt_emitted",
                        "id": "OBPI-0.99.0-01",
                        "parent": "ADR-0.99.0",
                        "ts": "2026-01-01T00:00:00+00:00",
                        "receipt_event": "completed",
                        "attestor": "Tester",
                        "anchor": {"commit": sha[:7], "semver": "0.99.0"},
                    },
                ],
            )
            results = detect_obpi_drift("ADR-0.25.0", project_root=repo)
            self.assertEqual(len(results), 1)
            self.assertIsInstance(results[0], ObpiDriftResult)
            self.assertEqual(results[0].obpi_id, "OBPI-0.25.0-26")
            self.assertEqual(results[0].adr_id, "ADR-0.25.0")
            self.assertEqual(results[0].status, "none")

    @covers("REQ-0.25.0-26-02")
    def test_filter_by_obpi_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            sha = _commit(repo, "a.txt", "1\n", "c1")
            events = [
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "obpi_receipt_emitted",
                    "id": f"OBPI-0.25.0-{n:02d}",
                    "parent": "ADR-0.25.0",
                    "ts": "2026-01-01T00:00:00+00:00",
                    "receipt_event": "completed",
                    "attestor": "Tester",
                    "anchor": {"commit": sha[:7], "semver": "0.25.0"},
                }
                for n in (24, 25, 26)
            ]
            _make_ledger(repo, events)
            results = detect_obpi_drift("ADR-0.25.0", obpi_id="OBPI-0.25.0-25", project_root=repo)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].obpi_id, "OBPI-0.25.0-25")

    @covers("REQ-0.25.0-26-02")
    def test_results_sorted_by_obpi_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            sha = _commit(repo, "a.txt", "1\n", "c1")
            events = [
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "obpi_receipt_emitted",
                    "id": oid,
                    "parent": "ADR-0.25.0",
                    "ts": "2026-01-01T00:00:00+00:00",
                    "receipt_event": "completed",
                    "attestor": "Tester",
                    "anchor": {"commit": sha[:7], "semver": "0.25.0"},
                }
                for oid in ("OBPI-0.25.0-26", "OBPI-0.25.0-24", "OBPI-0.25.0-25")
            ]
            _make_ledger(repo, events)
            results = detect_obpi_drift("ADR-0.25.0", project_root=repo)
            self.assertEqual(
                [r.obpi_id for r in results],
                ["OBPI-0.25.0-24", "OBPI-0.25.0-25", "OBPI-0.25.0-26"],
            )

    @covers("REQ-0.25.0-26-02")
    def test_obpi_message_includes_obpi_id_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            sha = _commit(repo, "a.txt", "1\n", "c1")
            _make_ledger(
                repo,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_receipt_emitted",
                        "id": "OBPI-0.25.0-26",
                        "parent": "ADR-0.25.0",
                        "ts": "2026-01-01T00:00:00+00:00",
                        "receipt_event": "completed",
                        "attestor": "Tester",
                        "anchor": {"commit": sha[:7], "semver": "0.25.0"},
                    }
                ],
            )
            results = detect_obpi_drift("ADR-0.25.0", project_root=repo)
            self.assertEqual(len(results), 1)
            self.assertTrue(results[0].message.startswith("OBPI-0.25.0-26: "))


# ---------------------------------------------------------------------------
# REQ-0.25.0-26-05: BDD N/A — module is library only, no operator-visible
# behavior change. The brief records this rationale; this test asserts the
# library surface stays library-only and exposes the documented public API.
# ---------------------------------------------------------------------------


class TestPublicSurface(unittest.TestCase):
    """@covers REQ-0.25.0-26-05"""

    @covers("REQ-0.25.0-26-05")
    def test_module_exports_match_documented_public_api(self) -> None:
        import gzkit.temporal_drift as mod

        expected = {
            "DriftResult",
            "DriftStatus",
            "ObpiDriftResult",
            "classify_drift",
            "detect_drift",
            "detect_obpi_drift",
        }
        self.assertEqual(set(mod.__all__), expected)
        for name in expected:
            self.assertTrue(hasattr(mod, name), f"missing public symbol: {name}")


if __name__ == "__main__":
    unittest.main()
