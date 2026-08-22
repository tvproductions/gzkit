"""The completion gate must observe the commit, not the tool that wrote it (GHI #847).

`.claude/hooks/obpi-completion-validator.py` is a PreToolUse hook bound to
`Write|Edit|NotebookEdit` and keyed on `tool_input.file_path` — a field a Bash
payload does not carry. So a brief hand-flipped to Completed with `sed`, a
heredoc, or inline `python` reaches the commit having passed no gate at all.
Measured for the sibling member (GHI #844, 2026-08-21): 348 Bash calls, 0
Write/Edit calls across three sessions, every write-side gate executing zero
times.

These tests write the brief with plain filesystem calls and stage it -- never
through any tool the hook can see -- because that is the bypass, and a test that
went through the hook's own matcher would prove nothing about it.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from gzkit.hooks.guards import forbid_unattested_obpi_completion_commits

_OBPI = "OBPI-0.35.0-09"
_BRIEF_REL = f"docs/design/adr/pre-release/ADR-0.35.0-x/obpis/{_OBPI}-codex-playback.md"

_DRAFT = """# OBPI-0.35.0-09

**Status:** In Progress

### Implementation Summary

- Files: -

### Key Proof

-

## Human Attestation

- Attestor: `<name>`
- Attestation: n/a
- Date: n/a
"""

_COMPLETED_NO_EVIDENCE = _DRAFT.replace("**Status:** In Progress", "**Status:** Completed")

_COMPLETED_WITH_EVIDENCE = """# OBPI-0.35.0-09

**Status:** Completed

### Implementation Summary

- Files created/modified: src/gzkit/codex_playback.py, tests/test_codex_playback.py

### Key Proof

`uv run -m unittest tests.test_codex_playback` -> Ran 11 tests, OK

## Human Attestation

- Attestor: `g0`
- Attestation: reviewed the playback wiring against the brief and attest completed
- Date: 2026-08-21
"""


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _repo(*, brief_at_head: str = _DRAFT, audit_evidence: bool = False) -> Path:
    root = Path(tempfile.mkdtemp(prefix="gzkit-847-"))
    _git(["init", "-q", "-b", "main"], root)
    _git(["config", "user.email", "g0@users.noreply.github.com"], root)
    _git(["config", "user.name", "g0"], root)
    brief = root / _BRIEF_REL
    brief.parent.mkdir(parents=True)
    brief.write_text(brief_at_head, encoding="utf-8")
    if audit_evidence:
        logs = brief.parent.parent / "logs"
        logs.mkdir(parents=True, exist_ok=True)
        (logs / "obpi-audit.jsonl").write_text(
            json.dumps(
                {
                    "type": "obpi-completion",
                    "obpi_id": f"{_OBPI}-codex-playback",
                    "evidence": {"human_attestation": True},
                }
            )
            + "\n",
            encoding="utf-8",
        )
    _git(["add", "-A"], root)
    _git(["commit", "-qm", "base"], root)
    return root


def _stage(root: Path, text: str) -> None:
    """Write the brief WITHOUT any Write/Edit tool, then stage it -- the bypass."""
    (root / _BRIEF_REL).write_text(text, encoding="utf-8")
    _git(["add", "-A"], root)


class TestCompletionFlipIsGatedAtTheCommit(unittest.TestCase):
    """The transition to Completed must carry its evidence, whatever wrote it."""

    def test_flip_without_evidence_is_refused(self) -> None:
        root = _repo()
        _stage(root, _COMPLETED_NO_EVIDENCE)
        self.assertEqual(
            forbid_unattested_obpi_completion_commits(root),
            1,
            "a brief flipped to Completed with placeholder evidence must not commit, "
            "even though no Write/Edit tool call ever occurred",
        )

    def test_flip_with_full_evidence_is_allowed(self) -> None:
        root = _repo(audit_evidence=True)
        _stage(root, _COMPLETED_WITH_EVIDENCE)
        self.assertEqual(
            forbid_unattested_obpi_completion_commits(root),
            0,
            "the governed path writes brief, audit ledger, and receipt together; "
            "its output must pass the gate it is judged by",
        )

    def test_evidence_in_the_brief_alone_is_not_enough(self) -> None:
        root = _repo(audit_evidence=False)
        _stage(root, _COMPLETED_WITH_EVIDENCE)
        self.assertEqual(
            forbid_unattested_obpi_completion_commits(root),
            1,
            "a brief that READS attested is Layer-1 authorship; the audit ledger is "
            "what records that the completion happened (AGENTS.md Never #7)",
        )


class TestGuardIsScopedToTheTransition(unittest.TestCase):
    """A brief already Completed at HEAD is not re-judged by a later era's bar."""

    def test_editing_an_already_completed_brief_is_allowed(self) -> None:
        root = _repo(brief_at_head=_COMPLETED_NO_EVIDENCE)
        _stage(root, _COMPLETED_NO_EVIDENCE + "\n<!-- typo repair -->\n")
        self.assertEqual(
            forbid_unattested_obpi_completion_commits(root),
            0,
            "gating the STATE rather than the TRANSITION would refuse ordinary "
            "maintenance on every historical brief that predates this bar",
        )

    def test_deleting_a_brief_is_allowed(self) -> None:
        root = _repo(brief_at_head=_COMPLETED_NO_EVIDENCE)
        (root / _BRIEF_REL).unlink()
        _git(["add", "-A"], root)
        self.assertEqual(forbid_unattested_obpi_completion_commits(root), 0)

    def test_unrelated_file_is_ignored(self) -> None:
        root = _repo()
        (root / "notes.md").write_text("**Status:** Completed\n", encoding="utf-8")
        _git(["add", "-A"], root)
        self.assertEqual(
            forbid_unattested_obpi_completion_commits(root),
            0,
            "the fence governs OBPI briefs, not every file that says Completed",
        )
