"""Reviewer capability disclosure and verdict isolation (GHI #941).

A spec-review dispatch asked the reviewer to re-derive a byte span and re-run a
behave selection. The reviewer persona is granted `Read, Glob, Grep` and no
`Bash`, so it could not, said so honestly, and returned CONCERNS with every
finding at `info` severity and none about the code. Re-derived afterwards both
checks passed: a PASS-shaped review reported as CONCERNS.

Two arms, one root. The reviewer's own coverage gap entered the same
`findings` list as defects in the code under review, and nothing told the
dispatcher what the reviewer could actually do.

These tests pin: a self-reported gap travels in its own channel and can never
reach the blocking predicate, and the composed prompt states the reviewer's
capability by READING the agent definition — so the disclosure cannot drift from
the tool grant, and corrects itself if the grant ever changes.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.pipeline_dispatch import (
    DispatchRecord,
    DispatchState,
    DispatchTask,
    TaskComplexity,
    compose_spec_review_prompt,
    handle_review_cycle,
    review_blocks_advancement,
    reviewer_capability,
)
from gzkit.roles import ReviewFinding, ReviewFindingSeverity, ReviewResult, ReviewVerdict


def _agents(root: Path, tools: str, name: str = "spec-reviewer") -> Path:
    d = root / ".claude" / "agents"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.md").write_text(
        f"---\nname: {name}\ndescription: Read-only independent review.\n"
        f"tools: {tools}\nmodel: inherit\n---\n\nBody.\n",
        encoding="utf-8",
    )
    return root


class TestReviewerCapability(unittest.TestCase):
    def test_capability_is_read_from_the_agent_definition(self) -> None:
        # Read, never hardcoded: the whole defect is a disclosure that does not
        # track the grant. A literal "read-only" string in the composer would be
        # wrong the moment the grant changes, which is exactly remedy 3.
        with TemporaryDirectory() as td:
            root = _agents(Path(td), "Read, Glob, Grep")
            cap = reviewer_capability(root, "spec-reviewer")
        self.assertEqual(cap.tools, ["Read", "Glob", "Grep"])
        self.assertFalse(cap.can_execute)

    def test_granting_execution_flips_the_capability(self) -> None:
        # If the operator ever rules that reviewers get Bash, the disclosure
        # follows automatically instead of contradicting the new grant.
        with TemporaryDirectory() as td:
            root = _agents(Path(td), "Read, Glob, Grep, Bash")
            cap = reviewer_capability(root, "spec-reviewer")
        self.assertTrue(cap.can_execute)

    def test_an_unreadable_definition_reports_no_execution(self) -> None:
        # Fail safe toward the restrictive claim: promising execution the agent
        # may not have is the direction that produces the unrunnable ask.
        with TemporaryDirectory() as td:
            cap = reviewer_capability(Path(td), "spec-reviewer")
        self.assertFalse(cap.can_execute)
        self.assertEqual(cap.tools, [])


class TestPromptDisclosesCapability(unittest.TestCase):
    def _prompt(self, tools: str) -> str:
        with TemporaryDirectory() as td:
            root = _agents(Path(td), tools)
            return compose_spec_review_prompt(
                _task(),
                ["REQ-1 must hold"],
                ["src/x.py"],
                why="because",
                project_root=root,
            )

    def test_a_read_only_reviewer_is_told_not_to_verify_by_running(self) -> None:
        prompt = self._prompt("Read, Glob, Grep")
        self.assertIn("Read, Glob, Grep", prompt)
        self.assertIn("cannot execute", prompt.lower())

    def test_every_prompt_routes_coverage_gaps_out_of_the_verdict(self) -> None:
        # The instruction that closes arm 1 at the source: the verdict describes
        # the code, and what the reviewer could not check goes elsewhere.
        prompt = self._prompt("Read, Glob, Grep")
        self.assertIn("verification_gaps", prompt)

    def test_an_executing_reviewer_is_not_told_it_cannot_execute(self) -> None:
        prompt = self._prompt("Read, Glob, Grep, Bash")
        self.assertNotIn("cannot execute", prompt.lower())


class TestVerdictIsolation(unittest.TestCase):
    def test_a_coverage_gap_travels_in_its_own_channel(self) -> None:
        result = ReviewResult(
            verdict=ReviewVerdict.PASS,
            findings=[],
            verification_gaps=["No shell tool; could not run the behave selection."],
            summary="Implementation satisfies every requirement.",
        )
        self.assertEqual(result.findings, [])
        self.assertEqual(len(result.verification_gaps), 1)

    def test_gaps_alone_never_block_advancement(self) -> None:
        # The observed instance, reconstructed with the gap in its own channel:
        # the code was fine, so nothing may block.
        result = ReviewResult(
            verdict=ReviewVerdict.PASS,
            verification_gaps=["could not execute the reproduction command"],
        )
        self.assertFalse(review_blocks_advancement(result))

    def test_a_gap_cannot_be_smuggled_in_as_a_critical_finding(self) -> None:
        # The failure this isolation exists to prevent: a self-coverage gap
        # reported at critical severity WOULD block, because the predicate reads
        # findings. Keeping the channels separate is what makes that impossible
        # to do by accident — a real critical finding still blocks.
        real_defect = ReviewResult(
            verdict=ReviewVerdict.CONCERNS,
            findings=[
                ReviewFinding(
                    file="src/x.py",
                    line=1,
                    severity=ReviewFindingSeverity.CRITICAL,
                    message="REQ-1 is not implemented",
                )
            ],
        )
        self.assertTrue(review_blocks_advancement(real_defect))

    def test_the_review_cycle_advances_a_pass_carrying_gaps(self) -> None:
        # End to end: the observed instance would now advance, where a CONCERNS
        # verdict built out of the reviewer's own limits reported otherwise.
        state = DispatchState(
            obpi_id="OBPI-0.1.0-01",
            parent_adr="ADR-0.1.0",
            records=[DispatchRecord(task=_task())],
        )
        result = ReviewResult(verdict=ReviewVerdict.PASS, verification_gaps=["no shell"])
        self.assertEqual(handle_review_cycle(state, 0, result, None), "advance")
        self.assertEqual(state.records[0].review_fix_count, 0)


def _task() -> DispatchTask:
    return DispatchTask(
        task_id=1,
        description="d",
        complexity=TaskComplexity.SIMPLE,
        model="sonnet",
    )
