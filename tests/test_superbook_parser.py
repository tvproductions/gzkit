"""Tests for superbook markdown parser."""

import tempfile
import unittest
from pathlib import Path

from gzkit.superbook_parser import extract_commits, parse_plan, parse_spec

SAMPLE_SPEC = """\
# AGENTS.md Tidy: Control Surface Schema and Rules Mirroring

**Date**: 2026-03-15
**Status**: Design approved

## Problem

Context window bloat from duplicated governance content.

## Goals

1. **Reduce context window bloat** — ~80% token reduction
2. **Maintain strict agent guardrails**

## Architecture

### Three-layer control surface model

Layer 1: Canonical, Layer 2: Mirrors, Layer 3: Documents.

## Implementation Scope

### Files to modify

| File | Change |
|------|--------|
| `src/gzkit/sync.py` | Add sync_claude_rules() |
| `src/gzkit/templates/claude.md` | Slim to ~40 lines |
"""

SAMPLE_PLAN = """\
# Feature Implementation Plan

**Goal:** Reduce context window bloat ~80%.

**Architecture:** Three-layer model.

**Tech Stack:** Python 3.13, stdlib unittest

---

## Chunk 1: Categorized Skill Catalog

### Task 1: Add category field

**Files:**
- Modify: `src/gzkit/sync.py`
- Test: `tests/test_sync.py`

- [ ] **Step 1: Write the failing test**

Expected: FAIL with KeyError

- [ ] **Step 2: Implement**

Add _extract_skill_frontmatter_field helper.

- [ ] **Step 3: Commit**

### Task 2: Add categorized rendering

**Files:**
- Modify: `src/gzkit/sync.py`

- [ ] **Step 1: Write tests**

Three new tests for categorized rendering.

## Chunk 2: Rules Mirroring

### Task 3: Implement sync_claude_rules()

**Files:**
- Modify: `src/gzkit/sync.py`
- Test: `tests/test_sync.py`

- [ ] **Step 1: Write 6 tests**

Tests for mirroring, unconditional, comma-split, exclusion, file filter, stale cleanup.
"""


class TestParseSpec(unittest.TestCase):
    def test_parse_spec_extracts_title(self) -> None:
        """Parser extracts spec title from first H1."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(SAMPLE_SPEC)
            f.flush()
            spec = parse_spec(Path(f.name))
        self.assertEqual(
            spec.title,
            "AGENTS.md Tidy: Control Surface Schema and Rules Mirroring",
        )

    def test_parse_spec_extracts_goal(self) -> None:
        """Parser extracts goal from Goals section."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(SAMPLE_SPEC)
            f.flush()
            spec = parse_spec(Path(f.name))
        self.assertIn("80% token reduction", spec.goal)

    def test_parse_spec_extracts_architecture(self) -> None:
        """Parser extracts architecture summary."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(SAMPLE_SPEC)
            f.flush()
            spec = parse_spec(Path(f.name))
        self.assertIn("Three-layer", spec.architecture)

    def test_parse_spec_extracts_file_scope(self) -> None:
        """Parser extracts file paths from Implementation Scope."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(SAMPLE_SPEC)
            f.flush()
            spec = parse_spec(Path(f.name))
        self.assertIn("src/gzkit/sync.py", spec.file_scope)
        self.assertIn("src/gzkit/templates/claude.md", spec.file_scope)


class TestParsePlan(unittest.TestCase):
    def test_parse_plan_extracts_goal(self) -> None:
        """Parser extracts plan goal."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(SAMPLE_PLAN)
            f.flush()
            plan = parse_plan(Path(f.name))
        self.assertIn("80%", plan.goal)

    def test_parse_plan_extracts_tech_stack(self) -> None:
        """Parser extracts tech stack."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(SAMPLE_PLAN)
            f.flush()
            plan = parse_plan(Path(f.name))
        self.assertIn("Python 3.13", plan.tech_stack)

    def test_parse_plan_extracts_chunks(self) -> None:
        """Parser extracts chunk names."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(SAMPLE_PLAN)
            f.flush()
            plan = parse_plan(Path(f.name))
        self.assertEqual(len(plan.chunks), 2)
        self.assertEqual(plan.chunks[0].name, "Categorized Skill Catalog")
        self.assertEqual(plan.chunks[1].name, "Rules Mirroring")

    def test_parse_plan_extracts_tasks_per_chunk(self) -> None:
        """Parser extracts tasks within each chunk."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(SAMPLE_PLAN)
            f.flush()
            plan = parse_plan(Path(f.name))
        self.assertEqual(len(plan.chunks[0].tasks), 2)
        self.assertEqual(plan.chunks[0].tasks[0].name, "Add category field")
        self.assertEqual(len(plan.chunks[1].tasks), 1)

    def test_parse_plan_extracts_file_paths_per_chunk(self) -> None:
        """Parser collects file paths from all tasks in a chunk."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(SAMPLE_PLAN)
            f.flush()
            plan = parse_plan(Path(f.name))
        self.assertIn("src/gzkit/sync.py", plan.chunks[0].file_paths)
        self.assertIn("tests/test_sync.py", plan.chunks[0].file_paths)


class TestExtractCommits(unittest.TestCase):
    def test_extract_commits_returns_list(self) -> None:
        """extract_commits returns a list of CommitData."""
        project_root = Path(__file__).resolve().parent.parent
        commits = extract_commits(
            plan_date="2026-03-15",
            project_root=project_root,
        )
        self.assertIsInstance(commits, list)
        if commits:
            self.assertTrue(commits[0].sha)
            self.assertTrue(commits[0].message)
            self.assertTrue(commits[0].date)


if __name__ == "__main__":
    unittest.main()
