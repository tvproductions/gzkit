"""Evidence-gather tests for gzkit.justify.evidence."""

from __future__ import annotations

import io
import json
import tempfile
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from gzkit.justify.evidence import TAXONOMY_REFERENCE_PATH, gather_evidence
from gzkit.justify.models import AnchorRef
from gzkit.traceability import covers


def _write_brief(root: Path, obpi_id: str) -> Path:
    brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.19-x" / "obpis"
    brief_dir.mkdir(parents=True, exist_ok=True)
    brief = brief_dir / f"{obpi_id}-sample.md"
    brief.write_text(
        "---\nid: " + obpi_id + "\nparent: ADR-0.0.19\n---\n"
        "# Objective\nx\n\n"
        "## Allowed Paths\n\n"
        "- `src/gzkit/commands/foo.py`\n"
        "- `tests/commands/test_foo.py`\n"
        "- `src/gzkit/justify/models.py`\n\n"
        "## Denied Paths\n\n- everything else\n",
        encoding="utf-8",
    )
    return brief


def _write_rule(root: Path, rule_id: str, globs: list[str]) -> Path:
    rules_dir = root / ".gzkit" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    content_lines = [
        "---",
        f"id: {rule_id}",
        "paths:",
    ]
    for g in globs:
        content_lines.append(f'  - "{g}"')
    content_lines += [
        f'description: "test rule {rule_id}"',
        "---",
        f"# {rule_id} body",
        "",
    ]
    path = rules_dir / f"{rule_id}.md"
    path.write_text("\n".join(content_lines), encoding="utf-8")
    return path


def _fake_run_exec_factory(*, ledger_payload: str | None = None, git_payload: str | None = None):
    """Return a run_exec stub that dispatches by cmd[0]."""

    def fake(cmd: list[str], cwd: Path, timeout: int | None = None) -> tuple[int, str, str]:
        head = cmd[0]
        if head == "git" and cmd[1] == "log":
            if git_payload is None:
                return (1, "", "git not available")
            return (0, git_payload, "")
        if head in {"uv", "gz"} and "state" in cmd:
            if ledger_payload is None:
                return (1, "", "ledger source unavailable")
            return (0, ledger_payload, "")
        if head == "gh":
            return (
                0,
                json.dumps(
                    {"number": 1, "title": "t", "body": "b", "labels": [], "author": {"login": "x"}}
                ),
                "",
            )
        return (0, "", "")

    return fake


class TestGatherEvidenceObpiSourcesPopulated(unittest.TestCase):
    @covers("REQ-0.0.19-01-07")
    def test_gather_evidence_obpi_all_sources_populated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = _write_brief(root, "OBPI-0.0.19-01")
            _write_rule(root, "cli", ["src/gzkit/commands/**"])
            _write_rule(root, "pythonic", ["**/*.py"])

            anchor = AnchorRef(
                kind="obpi",
                identifier="OBPI-0.0.19-01",
                source_path=str(brief),
                body=brief.read_text(encoding="utf-8"),
            )

            ledger_payload = json.dumps(
                {
                    "events": [
                        {
                            "event": "brief_created",
                            "id": "OBPI-0.0.19-01",
                            "ts": "2026-04-20T00:00:00Z",
                            "parent": "ADR-0.0.19",
                            "extra": {},
                        },
                        {
                            "event": "other_event",
                            "id": "OBPI-0.0.99-99",
                            "ts": "2026-04-20T00:00:00Z",
                            "parent": "ADR-0.0.99",
                            "extra": {},
                        },
                    ]
                }
            )
            git_payload = "abcdef1 fix(justify): add evidence gather (OBPI-0.0.19-01)\n"

            fake = _fake_run_exec_factory(ledger_payload=ledger_payload, git_payload=git_payload)
            with (
                patch("gzkit.justify.evidence.run_exec", side_effect=fake),
                patch("gzkit.justify.anchors.run_exec", side_effect=fake),
            ):
                bundle = gather_evidence(anchor, related=["GHI-232"], project_root=root)

        self.assertGreaterEqual(len(bundle.matching_rules), 1)
        self.assertEqual(len(bundle.ledger_events), 1)
        self.assertEqual(bundle.ledger_events[0].id, "OBPI-0.0.19-01")
        self.assertEqual(len(bundle.recent_commits), 1)
        self.assertEqual(bundle.recent_commits[0].sha, "abcdef1")
        self.assertEqual(len(bundle.related_anchors), 1)
        self.assertEqual(bundle.related_anchors[0].kind, "ghi")
        self.assertEqual(bundle.taxonomy_reference, TAXONOMY_REFERENCE_PATH)


class TestGatherEvidenceGracefulDegradation(unittest.TestCase):
    @covers("REQ-0.0.19-01-08")
    def test_gather_evidence_draft_has_no_ledger_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            anchor = AnchorRef(kind="draft", draft_text="refactor idea", draft_slug="refactor-idea")
            fake = _fake_run_exec_factory(git_payload="")
            with patch("gzkit.justify.evidence.run_exec", side_effect=fake):
                bundle = gather_evidence(anchor, project_root=root)
        self.assertEqual(bundle.ledger_events, ())
        self.assertTrue(
            any("ledger_events" in w and "not applicable" in w for w in bundle.warnings),
            bundle.warnings,
        )

    @covers("REQ-0.0.19-01-09")
    def test_gather_evidence_missing_ledger_graceful_degradation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = _write_brief(root, "OBPI-0.0.19-01")
            anchor = AnchorRef(
                kind="obpi",
                identifier="OBPI-0.0.19-01",
                source_path=str(brief),
                body=brief.read_text(encoding="utf-8"),
            )
            fake = _fake_run_exec_factory(ledger_payload=None, git_payload="")
            with patch("gzkit.justify.evidence.run_exec", side_effect=fake):
                bundle = gather_evidence(anchor, project_root=root)
        self.assertEqual(bundle.ledger_events, ())
        self.assertTrue(
            any("ledger_events" in w and "unavailable" in w for w in bundle.warnings),
            bundle.warnings,
        )

    @covers("REQ-0.0.19-01-09")
    def test_gather_evidence_missing_git_log_graceful_degradation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = _write_brief(root, "OBPI-0.0.19-01")
            anchor = AnchorRef(
                kind="obpi",
                identifier="OBPI-0.0.19-01",
                source_path=str(brief),
            )
            fake = _fake_run_exec_factory(ledger_payload=None, git_payload=None)
            with patch("gzkit.justify.evidence.run_exec", side_effect=fake):
                bundle = gather_evidence(anchor, project_root=root)
        self.assertEqual(bundle.recent_commits, ())
        self.assertTrue(
            any("recent_commits" in w and "unavailable" in w for w in bundle.warnings),
            bundle.warnings,
        )

    @covers("REQ-0.0.19-01-09")
    def test_gather_evidence_missing_rules_dir_graceful_degradation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = _write_brief(root, "OBPI-0.0.19-01")
            anchor = AnchorRef(
                kind="obpi",
                identifier="OBPI-0.0.19-01",
                source_path=str(brief),
            )
            fake = _fake_run_exec_factory(ledger_payload=None, git_payload=None)
            with patch("gzkit.justify.evidence.run_exec", side_effect=fake):
                bundle = gather_evidence(anchor, project_root=root)
        self.assertEqual(bundle.matching_rules, ())
        self.assertTrue(any("matching_rules" in w for w in bundle.warnings), bundle.warnings)

    @covers("REQ-0.0.19-01-07")
    def test_gather_evidence_related_anchor_failure_warns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            anchor = AnchorRef(kind="draft", draft_text="x", draft_slug="x")
            # one malformed, one GHI that succeeds
            fake = _fake_run_exec_factory()
            with (
                patch("gzkit.justify.evidence.run_exec", side_effect=fake),
                patch("gzkit.justify.anchors.run_exec", side_effect=fake),
            ):
                bundle = gather_evidence(
                    anchor, related=["not-an-anchor", "GHI-5"], project_root=root
                )
        self.assertEqual(len(bundle.related_anchors), 1)
        self.assertTrue(
            any("related_anchors" in w and "not-an-anchor" in w for w in bundle.warnings),
            bundle.warnings,
        )

    @covers("REQ-0.0.19-01-07")
    def test_gather_evidence_taxonomy_reference_literal_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            anchor = AnchorRef(kind="draft", draft_text="x", draft_slug="x")
            fake = _fake_run_exec_factory()
            with patch("gzkit.justify.evidence.run_exec", side_effect=fake):
                bundle = gather_evidence(anchor, project_root=root)
        self.assertEqual(bundle.taxonomy_reference, "docs/governance/model-regression-taxonomy.md")


class TestGatherEvidenceLibraryPurity(unittest.TestCase):
    @covers("REQ-0.0.19-01-10")
    def test_gather_evidence_never_emits_stdout_stderr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(root, "OBPI-0.0.19-01")
            anchor = AnchorRef(kind="draft", draft_text="x", draft_slug="x")
            stdout_buf = io.StringIO()
            stderr_buf = io.StringIO()
            fake = _fake_run_exec_factory()
            with (
                redirect_stdout(stdout_buf),
                redirect_stderr(stderr_buf),
                patch("gzkit.justify.evidence.run_exec", side_effect=fake),
            ):
                gather_evidence(anchor, project_root=root)
        self.assertEqual(stdout_buf.getvalue(), "")
        self.assertEqual(stderr_buf.getvalue(), "")

    @covers("REQ-0.0.19-01-10")
    def test_gather_evidence_under_3_seconds_with_representative_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Scaled representative fixture: ~20 ADRs, ~50 OBPIs, a handful of rules.
            for i in range(20):
                adr_dir = root / "docs" / "design" / "adr" / "foundation" / f"ADR-0.0.{i}-x"
                obpi_dir = adr_dir / "obpis"
                obpi_dir.mkdir(parents=True, exist_ok=True)
                for j in range(3):
                    obpi = obpi_dir / f"OBPI-0.0.{i}-0{j}-sample.md"
                    obpi.write_text("# o\n## Allowed Paths\n- `src/**`\n", encoding="utf-8")
            for rid in ("cli", "pythonic", "tests", "models", "cross-platform"):
                _write_rule(root, rid, ["src/**", "**/*.py"])

            brief = _write_brief(root, "OBPI-0.0.19-01")
            anchor = AnchorRef(
                kind="obpi",
                identifier="OBPI-0.0.19-01",
                source_path=str(brief),
                body=brief.read_text(encoding="utf-8"),
            )

            ledger_payload = json.dumps({"events": []})
            git_payload = ""
            fake = _fake_run_exec_factory(ledger_payload=ledger_payload, git_payload=git_payload)
            start = time.monotonic()
            with (
                patch("gzkit.justify.evidence.run_exec", side_effect=fake),
                patch("gzkit.justify.anchors.run_exec", side_effect=fake),
            ):
                gather_evidence(anchor, related=["GHI-1", "GHI-2", "GHI-3"], project_root=root)
            elapsed = time.monotonic() - start
        self.assertLess(elapsed, 3.0, f"gather_evidence too slow: {elapsed:.3f}s")


if __name__ == "__main__":
    unittest.main()
