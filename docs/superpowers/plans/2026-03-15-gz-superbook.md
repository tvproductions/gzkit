# gz superbook Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `gz superbook` — a CLI command that bridges superpowers specs/plans into GovZero ADR + OBPI governance artifacts, supporting both retroactive and forward booking.

**Architecture:** Two modules: `superbook_parser.py` (pure markdown parsing) and `superbook.py` (pipeline orchestration: classify, score, map, generate, present, apply). A thin CLI wrapper in `commands/superbook.py` registers the `gz superbook` subcommand. All data structures are Pydantic BaseModel. Generated artifacts use existing ADR/OBPI templates via `render_template()`.

**Tech Stack:** Python 3.13, Pydantic BaseModel, stdlib `unittest`, existing `gzkit.ledger`, `gzkit.decomposition`, `gzkit.templates`.

**Spec:** `docs/superpowers/specs/2026-03-15-gz-superbook-design.md`

---

## Chunk 1: Pydantic Data Models

### Task 1: Define all Pydantic data models

**Files:**
- Create: `src/gzkit/superbook_models.py`
- Test: `tests/test_superbook_models.py`

- [ ] **Step 1: Write the failing test for SpecData**

```python
"""Tests for superbook Pydantic models."""

import unittest

from gzkit.superbook_models import SpecData


class TestSpecData(unittest.TestCase):
    def test_spec_data_round_trips(self) -> None:
        """SpecData can be constructed and serialized."""
        spec = SpecData(
            title="Test Spec",
            goal="Reduce bloat",
            architecture="Three-layer model",
            decisions=["Use rules mirroring", "Categorize skills"],
            file_scope=["src/gzkit/sync.py", "src/gzkit/templates/claude.md"],
        )
        self.assertEqual(spec.title, "Test Spec")
        data = spec.model_dump()
        self.assertEqual(data["goal"], "Reduce bloat")
        self.assertEqual(len(data["decisions"]), 2)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run -m unittest tests.test_superbook_models.TestSpecData.test_spec_data_round_trips -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'gzkit.superbook_models'`

- [ ] **Step 3: Implement all models**

Create `src/gzkit/superbook_models.py`:

```python
"""Pydantic data models for gz superbook pipeline.

These are the first Pydantic models in gzkit (per ADR-0.15.0 migration).
They are internal to the superbook pipeline and do not replace existing
dataclasses used by ledger, decomposition, or config.
"""

from pydantic import BaseModel, ConfigDict, Field


class SpecData(BaseModel):
    """Parsed superpowers spec document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    title: str = Field(..., description="Spec title from first H1 heading")
    goal: str = Field(..., description="Goal statement from spec")
    architecture: str = Field("", description="Architecture summary")
    decisions: list[str] = Field(default_factory=list, description="Design decisions")
    file_scope: list[str] = Field(default_factory=list, description="Files in scope")


class TaskData(BaseModel):
    """A single task within a plan chunk."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., description="Task heading text")
    file_paths: list[str] = Field(default_factory=list, description="Files touched")
    steps: list[str] = Field(default_factory=list, description="Step descriptions")


class ChunkData(BaseModel):
    """A plan chunk containing tasks."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., description="Chunk heading text")
    tasks: list[TaskData] = Field(default_factory=list, description="Tasks in chunk")
    file_paths: list[str] = Field(default_factory=list, description="Union of task file paths")
    criteria: list[str] = Field(default_factory=list, description="Verifiable outcomes")


class PlanData(BaseModel):
    """Parsed superpowers plan document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    goal: str = Field(..., description="Plan goal statement")
    tech_stack: str = Field("", description="Tech stack line")
    chunks: list[ChunkData] = Field(default_factory=list, description="Plan chunks")


class CommitData(BaseModel):
    """A git commit extracted for retroactive evidence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    sha: str = Field(..., description="Short commit SHA")
    message: str = Field(..., description="Commit message first line")
    files: list[str] = Field(default_factory=list, description="Changed file paths")
    date: str = Field(..., description="ISO date string")


class LaneClassification(BaseModel):
    """Result of rules-based lane classification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    lane: str = Field(..., description="lite or heavy")
    signals: list[str] = Field(default_factory=list, description="Triggering file patterns")
    confidence: str = Field("auto", description="auto or override")


class REQData(BaseModel):
    """A single requirement identifier with description."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="REQ-X.Y.Z-NN-CC format")
    description: str = Field(..., description="What the requirement verifies")


class OBPIDraft(BaseModel):
    """Draft OBPI brief for generation."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="OBPI-X.Y.Z-NN-slug")
    objective: str = Field(..., description="Single-narrative objective")
    parent: str = Field(..., description="Parent ADR ID")
    item: int = Field(..., description="Checklist item number (1-based)")
    lane: str = Field(..., description="lite or heavy")
    status: str = Field("Draft", description="Draft or Pending-Attestation")
    allowed_paths: list[str] = Field(default_factory=list)
    reqs: list[REQData] = Field(default_factory=list)
    work_breakdown: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class ADRDraft(BaseModel):
    """Draft ADR for generation."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="ADR-X.Y.Z")
    title: str = Field(...)
    semver: str = Field(...)
    lane: str = Field(...)
    status: str = Field("Draft")
    intent: str = Field(...)
    decision: str = Field(...)
    checklist: list[str] = Field(default_factory=list)
    scorecard: dict[str, int] = Field(default_factory=dict)
    obpis: list[OBPIDraft] = Field(default_factory=list)
```

- [ ] **Step 4: Add remaining model tests**

Add to `tests/test_superbook_models.py`:

```python
from gzkit.superbook_models import (
    ADRDraft,
    ChunkData,
    CommitData,
    LaneClassification,
    OBPIDraft,
    PlanData,
    REQData,
    SpecData,
    TaskData,
)


class TestPlanData(unittest.TestCase):
    def test_plan_data_with_chunks_and_tasks(self) -> None:
        """PlanData nests ChunkData and TaskData correctly."""
        plan = PlanData(
            goal="Implement feature",
            tech_stack="Python 3.13",
            chunks=[
                ChunkData(
                    name="Core Logic",
                    tasks=[TaskData(name="Task 1", file_paths=["src/foo.py"], steps=["Write test"])],
                    file_paths=["src/foo.py"],
                    criteria=["foo() returns expected"],
                ),
            ],
        )
        self.assertEqual(len(plan.chunks), 1)
        self.assertEqual(plan.chunks[0].tasks[0].name, "Task 1")


class TestLaneClassification(unittest.TestCase):
    def test_lane_classification_defaults(self) -> None:
        """LaneClassification defaults confidence to auto."""
        lc = LaneClassification(lane="heavy", signals=["src/gzkit/cli.py"])
        self.assertEqual(lc.confidence, "auto")


class TestADRDraft(unittest.TestCase):
    def test_adr_draft_with_obpis(self) -> None:
        """ADRDraft contains OBPIDraft list."""
        adr = ADRDraft(
            id="ADR-0.17.0",
            title="Test ADR",
            semver="0.17.0",
            lane="heavy",
            intent="Reduce bloat",
            decision="Use rules mirroring",
            checklist=["Categorized catalog", "Rules mirroring"],
            scorecard={"data_state": 1, "logic_engine": 2},
            obpis=[
                OBPIDraft(
                    id="OBPI-0.17.0-01-catalog",
                    objective="Categorized skill catalog",
                    parent="ADR-0.17.0",
                    item=1,
                    lane="heavy",
                    reqs=[REQData(id="REQ-0.17.0-01-01", description="Category extraction")],
                ),
            ],
        )
        self.assertEqual(len(adr.obpis), 1)
        self.assertEqual(adr.obpis[0].reqs[0].id, "REQ-0.17.0-01-01")


class TestFrozenModels(unittest.TestCase):
    def test_spec_data_is_frozen(self) -> None:
        """Frozen models reject mutation."""
        spec = SpecData(title="T", goal="G")
        with self.assertRaises(Exception):
            spec.title = "Modified"

    def test_commit_data_is_frozen(self) -> None:
        """CommitData is frozen."""
        commit = CommitData(sha="abc123", message="feat: test", date="2026-03-15")
        with self.assertRaises(Exception):
            commit.sha = "modified"
```

- [ ] **Step 5: Run all model tests**

Run: `uv run -m unittest tests.test_superbook_models -v`
Expected: all tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/gzkit/superbook_models.py tests/test_superbook_models.py
git commit -m "feat(superbook): add Pydantic data models for superbook pipeline"
```

---

## Chunk 2: Markdown Parser

### Task 2: Implement spec parser

**Files:**
- Create: `src/gzkit/superbook_parser.py`
- Create: `tests/test_superbook_parser.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for superbook markdown parser."""

import unittest
from pathlib import Path
import tempfile

from gzkit.superbook_parser import parse_spec


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run -m unittest tests.test_superbook_parser.TestParseSpec -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `parse_spec()`**

Create `src/gzkit/superbook_parser.py`:

```python
"""Markdown parser for superpowers spec and plan documents.

Pure functions, no side effects. Extracts structured data from markdown
for the superbook pipeline.
"""

from __future__ import annotations

import re
from pathlib import Path

from gzkit.superbook_models import ChunkData, PlanData, SpecData, TaskData


def _extract_section(content: str, heading: str, level: int = 2) -> str:
    """Extract a markdown section by heading.

    Args:
        content: Full markdown text.
        heading: Heading text to find (case-insensitive).
        level: Heading level (2 = ##, 3 = ###).

    Returns:
        Section body text, or empty string if not found.
    """
    prefix = "#" * level
    pattern = re.compile(
        rf"^{prefix}\s+{re.escape(heading)}\b.*?\n(.*?)(?=^{prefix}\s|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(content)
    return match.group(1).strip() if match else ""


def _extract_title(content: str) -> str:
    """Extract the first H1 heading text."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def _extract_file_paths_from_table(section: str) -> list[str]:
    """Extract backtick-quoted file paths from a markdown table."""
    return re.findall(r"`([^`]+\.[a-z]+)`", section)


def parse_spec(path: Path) -> SpecData:
    """Parse a superpowers spec document into structured data.

    Args:
        path: Path to the spec markdown file.

    Returns:
        SpecData with extracted fields.
    """
    content = path.read_text(encoding="utf-8")

    title = _extract_title(content)

    # Goal: extract from "## Goals" or "## Problem" section
    goals_section = _extract_section(content, "Goals")
    problem_section = _extract_section(content, "Problem")
    goal = goals_section or problem_section

    # Architecture
    arch_section = _extract_section(content, "Architecture")

    # Decisions: extract numbered list items from Goals or Design Decisions
    decisions_section = _extract_section(content, "Design Decisions")
    decisions: list[str] = []
    for line in (decisions_section or goals_section).splitlines():
        stripped = line.strip()
        if re.match(r"^\d+\.\s+\*\*", stripped):
            decisions.append(stripped)

    # File scope from Implementation Scope table
    scope_section = _extract_section(content, "Implementation Scope")
    file_scope = _extract_file_paths_from_table(scope_section)

    return SpecData(
        title=title,
        goal=goal,
        architecture=arch_section,
        decisions=decisions,
        file_scope=file_scope,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run -m unittest tests.test_superbook_parser.TestParseSpec -v`
Expected: all 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/gzkit/superbook_parser.py tests/test_superbook_parser.py
git commit -m "feat(superbook): implement spec markdown parser"
```

### Task 3: Implement plan parser

**Files:**
- Modify: `src/gzkit/superbook_parser.py`
- Modify: `tests/test_superbook_parser.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_superbook_parser.py`:

```python
from gzkit.superbook_parser import parse_plan

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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run -m unittest tests.test_superbook_parser.TestParsePlan -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement `parse_plan()`**

Add to `src/gzkit/superbook_parser.py`:

```python
def _extract_bold_field(content: str, field: str) -> str:
    """Extract a **Field:** value from plan header."""
    match = re.search(rf"\*\*{re.escape(field)}:\*\*\s*(.+)", content)
    return match.group(1).strip() if match else ""


def parse_plan(path: Path) -> PlanData:
    """Parse a superpowers plan document into structured data.

    Extracts chunks (## Chunk N: Name), tasks (### Task N: Name),
    and file paths from task **Files:** sections.

    Args:
        path: Path to the plan markdown file.

    Returns:
        PlanData with extracted chunks and tasks.
    """
    content = path.read_text(encoding="utf-8")

    goal = _extract_bold_field(content, "Goal")
    tech_stack = _extract_bold_field(content, "Tech Stack")

    # Split into chunk sections by ## Chunk N: heading
    chunk_pattern = re.compile(
        r"^##\s+Chunk\s+\d+:\s+(.+?)$", re.MULTILINE
    )
    chunk_starts = list(chunk_pattern.finditer(content))

    chunks: list[ChunkData] = []
    for i, match in enumerate(chunk_starts):
        chunk_name = match.group(1).strip()
        start = match.end()
        end = chunk_starts[i + 1].start() if i + 1 < len(chunk_starts) else len(content)
        chunk_body = content[start:end]

        # Extract tasks within chunk
        task_pattern = re.compile(
            r"^###\s+Task\s+\d+:\s+(.+?)$", re.MULTILINE
        )
        task_starts = list(task_pattern.finditer(chunk_body))

        tasks: list[TaskData] = []
        all_file_paths: list[str] = []
        for j, tmatch in enumerate(task_starts):
            task_name = tmatch.group(1).strip()
            tstart = tmatch.end()
            tend = task_starts[j + 1].start() if j + 1 < len(task_starts) else len(chunk_body)
            task_body = chunk_body[tstart:tend]

            # Extract file paths from **Files:** section or backtick paths
            file_paths = re.findall(r"`([^`]+\.[a-z]{1,4})`", task_body)
            # Filter to likely file paths (contain / or start with src/tests/docs)
            file_paths = sorted(
                set(
                    p for p in file_paths
                    if "/" in p or p.startswith(("src", "tests", "docs", ".gzkit"))
                )
            )

            # Extract step descriptions
            steps = re.findall(r"- \[ \] \*\*Step \d+: (.+?)\*\*", task_body)

            tasks.append(TaskData(name=task_name, file_paths=file_paths, steps=steps))
            all_file_paths.extend(file_paths)

        chunks.append(
            ChunkData(
                name=chunk_name,
                tasks=tasks,
                file_paths=sorted(set(all_file_paths)),
                criteria=[],  # Populated later from task step assertions
            )
        )

    return PlanData(goal=goal, tech_stack=tech_stack, chunks=chunks)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run -m unittest tests.test_superbook_parser.TestParsePlan -v`
Expected: all 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/gzkit/superbook_parser.py tests/test_superbook_parser.py
git commit -m "feat(superbook): implement plan markdown parser with chunk/task extraction"
```

### Task 4: Implement commit extraction (retroactive mode)

**Files:**
- Modify: `src/gzkit/superbook_parser.py`
- Modify: `tests/test_superbook_parser.py`

- [ ] **Step 1: Write the failing test**

```python
from gzkit.superbook_parser import extract_commits


class TestExtractCommits(unittest.TestCase):
    def test_extract_commits_returns_commit_data(self) -> None:
        """extract_commits returns CommitData from git log."""
        # This test runs against the actual repo
        from pathlib import Path

        project_root = Path(__file__).resolve().parent.parent
        commits = extract_commits(
            plan_date="2026-03-15",
            project_root=project_root,
        )
        # We should have commits from today
        self.assertIsInstance(commits, list)
        if commits:
            self.assertTrue(commits[0].sha)
            self.assertTrue(commits[0].message)
            self.assertTrue(commits[0].date)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run -m unittest tests.test_superbook_parser.TestExtractCommits -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement `extract_commits()`**

Add to `src/gzkit/superbook_parser.py`:

```python
import subprocess

from gzkit.superbook_models import CommitData


def extract_commits(
    plan_date: str,
    project_root: Path,
) -> list[CommitData]:
    """Extract git commits since a given date.

    Args:
        plan_date: ISO date string (YYYY-MM-DD) to start from.
        project_root: Git repository root.

    Returns:
        List of CommitData sorted oldest-first.
    """
    try:
        result = subprocess.run(
            [
                "git", "log",
                f"--since={plan_date}",
                "--format=%H|%s|%ai",
                "--name-only",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(project_root),
        )
    except (OSError, FileNotFoundError):
        return []

    if result.returncode != 0:
        return []

    commits: list[CommitData] = []
    current_sha = ""
    current_msg = ""
    current_date = ""
    current_files: list[str] = []

    for line in result.stdout.splitlines():
        if "|" in line and len(line.split("|")) == 3:
            # Flush previous commit
            if current_sha:
                commits.append(
                    CommitData(
                        sha=current_sha[:8],
                        message=current_msg,
                        files=current_files,
                        date=current_date[:10],
                    )
                )
            parts = line.split("|")
            current_sha = parts[0]
            current_msg = parts[1]
            current_date = parts[2]
            current_files = []
        elif line.strip():
            current_files.append(line.strip())

    # Flush last commit
    if current_sha:
        commits.append(
            CommitData(
                sha=current_sha[:8],
                message=current_msg,
                files=current_files,
                date=current_date[:10],
            )
        )

    # Return oldest-first
    commits.reverse()
    return commits
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run -m unittest tests.test_superbook_parser.TestExtractCommits -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/gzkit/superbook_parser.py tests/test_superbook_parser.py
git commit -m "feat(superbook): implement git commit extraction for retroactive evidence"
```

---

## Chunk 3: Pipeline Core

### Task 5: Implement lane classification

**Files:**
- Create: `src/gzkit/superbook.py`
- Create: `tests/test_superbook.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for superbook pipeline."""

import unittest

from gzkit.superbook import classify_lane
from gzkit.superbook_models import PlanData, ChunkData, SpecData


class TestClassifyLane(unittest.TestCase):
    def test_heavy_when_cli_touched(self) -> None:
        """Lane is heavy when CLI file is in scope."""
        plan = PlanData(
            goal="Test",
            chunks=[ChunkData(name="C1", file_paths=["src/gzkit/cli.py"])],
        )
        spec = SpecData(title="T", goal="G")
        result = classify_lane(spec, plan)
        self.assertEqual(result.lane, "heavy")
        self.assertIn("src/gzkit/cli.py", result.signals)

    def test_heavy_when_schemas_touched(self) -> None:
        """Lane is heavy when schema files are in scope."""
        plan = PlanData(
            goal="Test",
            chunks=[ChunkData(name="C1", file_paths=[".gzkit/schemas/skill.schema.json"])],
        )
        spec = SpecData(title="T", goal="G")
        result = classify_lane(spec, plan)
        self.assertEqual(result.lane, "heavy")

    def test_lite_when_no_heavy_signals(self) -> None:
        """Lane is lite when no heavy signals present."""
        plan = PlanData(
            goal="Test",
            chunks=[ChunkData(name="C1", file_paths=["src/gzkit/foo.py"])],
        )
        spec = SpecData(title="T", goal="G")
        result = classify_lane(spec, plan)
        self.assertEqual(result.lane, "lite")
        self.assertEqual(result.signals, [])

    def test_heavy_when_templates_touched(self) -> None:
        """Lane is heavy when template files are in scope."""
        plan = PlanData(
            goal="Test",
            chunks=[ChunkData(name="C1", file_paths=["src/gzkit/templates/claude.md"])],
        )
        spec = SpecData(title="T", goal="G")
        result = classify_lane(spec, plan)
        self.assertEqual(result.lane, "heavy")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run -m unittest tests.test_superbook.TestClassifyLane -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `classify_lane()`**

Create `src/gzkit/superbook.py`:

```python
"""Superbook pipeline: bridge superpowers artifacts to GovZero governance.

Orchestrates: classify lane, compute scorecard, map chunks to OBPIs,
generate ADR/OBPI drafts, present for review, apply on approval.
"""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

from gzkit.superbook_models import (
    ADRDraft,
    ChunkData,
    CommitData,
    LaneClassification,
    OBPIDraft,
    PlanData,
    REQData,
    SpecData,
)

HEAVY_SIGNAL_PATTERNS = [
    "src/gzkit/cli.py",
    ".gzkit/schemas/*",
    "src/gzkit/templates/*",
    "**/api/**",
]


def classify_lane(spec: SpecData, plan: PlanData) -> LaneClassification:
    """Classify governance lane from file scope.

    Args:
        spec: Parsed spec data.
        plan: Parsed plan data.

    Returns:
        LaneClassification with inferred lane and triggering signals.
    """
    all_paths: list[str] = list(spec.file_scope)
    for chunk in plan.chunks:
        all_paths.extend(chunk.file_paths)

    signals: list[str] = []
    for path in sorted(set(all_paths)):
        for pattern in HEAVY_SIGNAL_PATTERNS:
            if fnmatch(path, pattern) or path.startswith(pattern.rstrip("*")):
                signals.append(path)
                break

    lane = "heavy" if signals else "lite"
    return LaneClassification(lane=lane, signals=sorted(set(signals)))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run -m unittest tests.test_superbook.TestClassifyLane -v`
Expected: all 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/gzkit/superbook.py tests/test_superbook.py
git commit -m "feat(superbook): implement rules-based lane classification"
```

### Task 6: Implement chunk-to-OBPI mapping and semver utilities

**Files:**
- Modify: `src/gzkit/superbook.py`
- Modify: `tests/test_superbook.py`

- [ ] **Step 1: Write the failing tests**

```python
from gzkit.superbook import map_chunks_to_obpis, next_semver


class TestNextSemver(unittest.TestCase):
    def test_next_semver_increments_minor(self) -> None:
        """next_semver increments minor version."""
        self.assertEqual(next_semver(["0.15.0", "0.16.0"]), "0.17.0")

    def test_next_semver_defaults_when_empty(self) -> None:
        """next_semver returns 0.1.0 when no existing ADRs."""
        self.assertEqual(next_semver([]), "0.1.0")

    def test_next_semver_handles_semantic_ordering(self) -> None:
        """next_semver orders semantically, not lexicographically."""
        self.assertEqual(next_semver(["0.9.0", "0.10.0"]), "0.11.0")


class TestMapChunksToObpis(unittest.TestCase):
    def test_map_produces_one_obpi_per_chunk(self) -> None:
        """Each chunk maps to exactly one OBPI."""
        plan = PlanData(
            goal="Test",
            chunks=[
                ChunkData(name="Catalog", file_paths=["src/sync.py"], criteria=["criterion A"]),
                ChunkData(name="Mirroring", file_paths=["src/sync.py"], criteria=["criterion B"]),
            ],
        )
        obpis = map_chunks_to_obpis(plan, "0.17.0", "heavy")
        self.assertEqual(len(obpis), 2)
        self.assertEqual(obpis[0].id, "OBPI-0.17.0-01-catalog")
        self.assertEqual(obpis[1].id, "OBPI-0.17.0-02-mirroring")

    def test_map_generates_req_ids(self) -> None:
        """REQ IDs are generated from chunk criteria."""
        plan = PlanData(
            goal="Test",
            chunks=[
                ChunkData(
                    name="Catalog",
                    file_paths=["src/sync.py"],
                    criteria=["Category extraction", "Categorized renderer"],
                ),
            ],
        )
        obpis = map_chunks_to_obpis(plan, "0.17.0", "heavy")
        self.assertEqual(len(obpis[0].reqs), 2)
        self.assertEqual(obpis[0].reqs[0].id, "REQ-0.17.0-01-01")
        self.assertEqual(obpis[0].reqs[1].id, "REQ-0.17.0-01-02")

    def test_map_slugifies_chunk_name(self) -> None:
        """OBPI slug is derived from chunk name."""
        plan = PlanData(
            goal="Test",
            chunks=[
                ChunkData(name="Slim CLAUDE.md Template", file_paths=[]),
            ],
        )
        obpis = map_chunks_to_obpis(plan, "0.17.0", "heavy")
        self.assertEqual(obpis[0].id, "OBPI-0.17.0-01-slim-claude-md-template")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run -m unittest tests.test_superbook -v -k "semver or map"`
Expected: FAIL

- [ ] **Step 3: Implement**

Add to `src/gzkit/superbook.py`:

```python
import re


def _slugify(text: str, max_length: int = 50) -> str:
    """Convert text to a URL-safe slug."""
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug).strip("-")
    return slug[:max_length]


def next_semver(existing: list[str]) -> str:
    """Compute next minor semver from existing ADR semvers.

    Args:
        existing: List of existing semver strings (e.g., ["0.15.0", "0.16.0"]).

    Returns:
        Next semver string (e.g., "0.17.0").
    """
    if not existing:
        return "0.1.0"

    def _parse(s: str) -> tuple[int, int, int]:
        parts = s.split(".")
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    versions = sorted(_parse(v) for v in existing)
    major, minor, _patch = versions[-1]
    return f"{major}.{minor + 1}.0"


def map_chunks_to_obpis(
    plan: PlanData, semver: str, lane: str
) -> list[OBPIDraft]:
    """Map plan chunks to OBPI drafts.

    Args:
        plan: Parsed plan data.
        semver: ADR semver for ID generation.
        lane: Governance lane (lite/heavy).

    Returns:
        List of OBPIDraft, one per chunk.
    """
    obpis: list[OBPIDraft] = []
    for idx, chunk in enumerate(plan.chunks, start=1):
        slug = _slugify(chunk.name)
        obpi_id = f"OBPI-{semver}-{idx:02d}-{slug}"

        reqs: list[REQData] = []
        for c_idx, criterion in enumerate(chunk.criteria, start=1):
            reqs.append(
                REQData(
                    id=f"REQ-{semver}-{idx:02d}-{c_idx:02d}",
                    description=criterion,
                )
            )

        work_breakdown = [t.name for t in chunk.tasks]

        obpis.append(
            OBPIDraft(
                id=obpi_id,
                objective=chunk.name,
                parent=f"ADR-{semver}",
                item=idx,
                lane=lane,
                allowed_paths=chunk.file_paths,
                reqs=reqs,
                work_breakdown=work_breakdown,
            )
        )

    return obpis
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run -m unittest tests.test_superbook -v -k "semver or map"`
Expected: all 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/gzkit/superbook.py tests/test_superbook.py
git commit -m "feat(superbook): implement chunk-to-OBPI mapping and semver utilities"
```

### Task 7: Implement ADR draft generation

**Files:**
- Modify: `src/gzkit/superbook.py`
- Modify: `tests/test_superbook.py`

- [ ] **Step 1: Write the failing test**

```python
from gzkit.superbook import generate_adr_draft


class TestGenerateADRDraft(unittest.TestCase):
    def test_generate_adr_draft_from_spec_and_plan(self) -> None:
        """ADR draft is generated from spec and plan data."""
        spec = SpecData(
            title="Test Feature",
            goal="Reduce bloat",
            architecture="Three-layer model",
            decisions=["Use mirroring"],
        )
        plan = PlanData(
            goal="Implement feature",
            chunks=[
                ChunkData(name="Catalog", file_paths=["src/sync.py"], criteria=["Works"]),
                ChunkData(name="Mirror", file_paths=["src/sync.py"], criteria=["Mirrors"]),
            ],
        )
        adr = generate_adr_draft(spec, plan, lane="heavy", semver="0.17.0")
        self.assertEqual(adr.id, "ADR-0.17.0")
        self.assertEqual(adr.title, "Test Feature")
        self.assertEqual(adr.lane, "heavy")
        self.assertEqual(len(adr.checklist), 2)
        self.assertIn("Catalog", adr.checklist[0])
        self.assertEqual(len(adr.obpis), 2)
        self.assertEqual(adr.obpis[0].parent, "ADR-0.17.0")
```

- [ ] **Step 2: Implement `generate_adr_draft()`**

Add to `src/gzkit/superbook.py`:

```python
def generate_adr_draft(
    spec: SpecData,
    plan: PlanData,
    *,
    lane: str,
    semver: str,
    status: str = "Draft",
) -> ADRDraft:
    """Generate an ADR draft from spec and plan data.

    Args:
        spec: Parsed spec.
        plan: Parsed plan.
        lane: Governance lane.
        semver: ADR semver.
        status: Initial status (Draft or Pending-Attestation).

    Returns:
        ADRDraft with populated OBPIs.
    """
    obpis = map_chunks_to_obpis(plan, semver, lane)

    checklist = [
        f"OBPI-{semver}-{idx:02d}: {chunk.name}"
        for idx, chunk in enumerate(plan.chunks, start=1)
    ]

    return ADRDraft(
        id=f"ADR-{semver}",
        title=spec.title,
        semver=semver,
        lane=lane,
        status=status,
        intent=spec.goal,
        decision=spec.architecture,
        checklist=checklist,
        scorecard={},
        obpis=obpis,
    )
```

- [ ] **Step 3: Run tests**

Run: `uv run -m unittest tests.test_superbook -v`
Expected: all tests PASS

- [ ] **Step 4: Commit**

```bash
git add src/gzkit/superbook.py tests/test_superbook.py
git commit -m "feat(superbook): implement ADR draft generation from spec and plan"
```

### Task 8: Implement draft presentation and commit-to-chunk evidence mapping

**Files:**
- Modify: `src/gzkit/superbook.py`
- Modify: `tests/test_superbook.py`

- [ ] **Step 1: Write failing tests**

```python
from gzkit.superbook import present_draft, map_commits_to_chunks


class TestPresentDraft(unittest.TestCase):
    def test_present_draft_includes_adr_summary(self) -> None:
        """Presentation includes ADR ID, title, lane."""
        adr = ADRDraft(
            id="ADR-0.17.0",
            title="Test",
            semver="0.17.0",
            lane="heavy",
            intent="G",
            decision="D",
            checklist=["OBPI-0.17.0-01: Catalog"],
            obpis=[],
        )
        output = present_draft(adr)
        self.assertIn("ADR-0.17.0", output)
        self.assertIn("heavy", output.lower())
        self.assertIn("Catalog", output)


class TestMapCommitsToChunks(unittest.TestCase):
    def test_map_by_file_overlap(self) -> None:
        """Commits are mapped to chunks by file-path overlap."""
        chunks = [
            ChunkData(name="A", file_paths=["src/a.py", "tests/test_a.py"]),
            ChunkData(name="B", file_paths=["src/b.py"]),
        ]
        commits = [
            CommitData(sha="aaa", message="feat A", files=["src/a.py"], date="2026-03-15"),
            CommitData(sha="bbb", message="feat B", files=["src/b.py"], date="2026-03-15"),
        ]
        mapping = map_commits_to_chunks(commits, chunks)
        self.assertEqual(mapping[0], [commits[0]])  # chunk A
        self.assertEqual(mapping[1], [commits[1]])  # chunk B

    def test_unmapped_commits_in_last_bucket(self) -> None:
        """Commits matching no chunk go to unmapped list."""
        chunks = [ChunkData(name="A", file_paths=["src/a.py"])]
        commits = [
            CommitData(sha="xxx", message="unrelated", files=["docs/readme.md"], date="2026-03-15"),
        ]
        mapping = map_commits_to_chunks(commits, chunks)
        self.assertEqual(mapping[0], [])  # chunk A got nothing
        self.assertEqual(mapping[-1], [commits[0]])  # unmapped bucket
```

- [ ] **Step 2: Implement**

Add to `src/gzkit/superbook.py`:

```python
def map_commits_to_chunks(
    commits: list[CommitData], chunks: list[ChunkData]
) -> list[list[CommitData]]:
    """Map commits to chunks by file-path overlap.

    Returns a list of length len(chunks) + 1. Index i contains commits
    mapped to chunks[i]. The last element contains unmapped commits.
    """
    buckets: list[list[CommitData]] = [[] for _ in range(len(chunks) + 1)]

    for commit in commits:
        commit_files = set(commit.files)
        best_idx = -1
        best_score = 0
        for idx, chunk in enumerate(chunks):
            chunk_files = set(chunk.file_paths)
            score = len(commit_files & chunk_files)
            if score > best_score:
                best_score = score
                best_idx = idx
        if best_idx >= 0:
            buckets[best_idx].append(commit)
        else:
            buckets[-1].append(commit)  # unmapped

    return buckets


def present_draft(adr: ADRDraft) -> str:
    """Render a human-readable summary of the booking draft.

    Args:
        adr: ADR draft with OBPIs.

    Returns:
        Formatted string for terminal display.
    """
    lines = [
        "",
        "=" * 50,
        "  gz superbook — Governance Booking Draft",
        "=" * 50,
        "",
        f"ADR: {adr.id} — {adr.title}",
        f"Lane: {adr.lane.title()} (signals: {', '.join(o.allowed_paths[:3] for o in adr.obpis[:1]) or 'none'})",
        f"Status: {adr.status}",
        "",
        "Feature Checklist:",
    ]
    for item in adr.checklist:
        req_count = 0
        for obpi in adr.obpis:
            if item.startswith(obpi.id.rsplit("-", 1)[0]):
                req_count = len(obpi.reqs)
                break
        lines.append(f"  {item} ({req_count} REQs)")

    lines.append("")
    lines.append(f"OBPIs: {len(adr.obpis)}")
    lines.append("")
    lines.append("Run with --apply to book, or adjust with --semver/--lane.")
    lines.append("")

    return "\n".join(lines)
```

- [ ] **Step 3: Run tests**

Run: `uv run -m unittest tests.test_superbook -v`
Expected: all tests PASS

- [ ] **Step 4: Commit**

```bash
git add src/gzkit/superbook.py tests/test_superbook.py
git commit -m "feat(superbook): implement draft presentation and commit-to-chunk mapping"
```

---

## Chunk 4: Apply and CLI

### Task 9: Implement `apply_draft()` — write files and ledger events

**Files:**
- Modify: `src/gzkit/superbook.py`
- Modify: `tests/test_superbook.py`

- [ ] **Step 1: Write the failing test**

```python
import tempfile


class TestApplyDraft(unittest.TestCase):
    def test_apply_creates_adr_directory_and_files(self) -> None:
        """apply_draft writes ADR and OBPI files to disk."""
        from gzkit.superbook import apply_draft

        adr = ADRDraft(
            id="ADR-0.17.0",
            title="Test Feature",
            semver="0.17.0",
            lane="heavy",
            intent="Reduce bloat",
            decision="Use mirroring",
            checklist=["OBPI-0.17.0-01: Catalog"],
            obpis=[
                OBPIDraft(
                    id="OBPI-0.17.0-01-catalog",
                    objective="Categorized catalog",
                    parent="ADR-0.17.0",
                    item=1,
                    lane="heavy",
                    reqs=[REQData(id="REQ-0.17.0-01-01", description="Works")],
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            # Create ledger file
            gzkit_dir = project_root / ".gzkit"
            gzkit_dir.mkdir()
            (gzkit_dir / "ledger.jsonl").write_text("")

            apply_draft(adr, project_root)

            # ADR file exists
            adr_dir = project_root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.17.0-test-feature"
            self.assertTrue(adr_dir.exists())
            adr_file = adr_dir / "ADR-0.17.0-test-feature.md"
            self.assertTrue(adr_file.exists())
            content = adr_file.read_text(encoding="utf-8")
            self.assertIn("ADR-0.17.0", content)
            self.assertIn("Reduce bloat", content)

            # OBPI file exists
            obpi_file = adr_dir / "obpis" / "OBPI-0.17.0-01-catalog.md"
            self.assertTrue(obpi_file.exists())
            obpi_content = obpi_file.read_text(encoding="utf-8")
            self.assertIn("Categorized catalog", obpi_content)

            # Ledger has events
            ledger_content = (gzkit_dir / "ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("adr_created", ledger_content)
            self.assertIn("obpi_created", ledger_content)
```

- [ ] **Step 2: Implement `apply_draft()`**

Add to `src/gzkit/superbook.py`:

```python
from datetime import date

from gzkit.ledger import Ledger, adr_created_event, obpi_created_event
from gzkit.templates import render_template


def apply_draft(adr: ADRDraft, project_root: Path) -> list[str]:
    """Write ADR, OBPI files, and ledger events to disk.

    Args:
        adr: ADR draft with OBPIs.
        project_root: Project root directory.

    Returns:
        List of created file paths (relative to project_root).
    """
    slug = _slugify(adr.title)
    bucket = "foundation" if adr.semver.startswith("0.0.") else "pre-release"
    adr_dir_name = f"{adr.id}-{slug}"
    adr_dir = project_root / "docs" / "design" / "adr" / bucket / adr_dir_name
    obpis_dir = adr_dir / "obpis"
    audit_dir = adr_dir / "audit"

    adr_dir.mkdir(parents=True, exist_ok=True)
    obpis_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    created: list[str] = []

    # Write ADR file
    checklist_md = "\n".join(f"- [ ] {item}" for item in adr.checklist)
    adr_content = render_template(
        "adr",
        id=adr.id,
        title=adr.title,
        semver=adr.semver,
        lane=adr.lane,
        parent="",
        date=date.today().isoformat(),
        status=adr.status,
        intent=adr.intent,
        decision=adr.decision,
        positive_consequences="Governance visibility for superpowers work.",
        negative_consequences="Additional booking step in workflow.",
        decomposition_scorecard="Auto-generated by gz superbook.",
        checklist=checklist_md,
        qa_transcript="Generated from superpowers spec.",
        alternatives="Manual gz plan + gz specify (two-step).",
    )
    adr_file = adr_dir / f"{adr_dir_name}.md"
    adr_file.write_text(adr_content, encoding="utf-8")
    created.append(str(adr_file.relative_to(project_root)))

    # Write OBPI files
    for obpi in adr.obpis:
        criteria_md = "\n".join(
            f"- [ ] {req.id}: {req.description}" for req in obpi.reqs
        )
        work_md = "\n".join(f"- {item}" for item in obpi.work_breakdown)
        evidence_md = "\n".join(f"- {e}" for e in obpi.evidence) if obpi.evidence else ""

        obpi_content = render_template(
            "obpi",
            id=obpi.id,
            title=obpi.objective,
            parent_adr=obpi.parent,
            item_number=str(obpi.item),
            lane=obpi.lane,
            status=obpi.status,
            objective=obpi.objective,
            acceptance_criteria_seed=criteria_md,
            lane_rationale=f"Inherited from parent {obpi.parent} ({obpi.lane}).",
            allowed_paths="\n".join(f"- `{p}`" for p in obpi.allowed_paths),
            denied_paths="- All paths not in allowed list",
            requirements=work_md,
            evidence=evidence_md,
        )
        obpi_file = obpis_dir / f"{obpi.id}.md"
        obpi_file.write_text(obpi_content, encoding="utf-8")
        created.append(str(obpi_file.relative_to(project_root)))

    # Emit ledger events
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    ledger = Ledger(ledger_path)
    ledger.append(
        adr_created_event(adr.id, "", adr.lane, extra={"source": "gz-superbook"})
    )
    for obpi in adr.obpis:
        ledger.append(
            obpi_created_event(obpi.id, adr.id, extra={"source": "gz-superbook"})
        )

    return created
```

Note: The `adr_created_event` and `obpi_created_event` factory functions may not accept an `extra` keyword yet. If not, pass it through the `LedgerEvent` constructor directly or update the factories. Check during implementation.

- [ ] **Step 3: Run test**

Run: `uv run -m unittest tests.test_superbook.TestApplyDraft -v`
Expected: PASS (may need to adjust template variable names to match existing templates — check `src/gzkit/templates/adr.md` and `obpi.md` for exact placeholder names)

- [ ] **Step 4: Run full suite**

Run: `uv run -m unittest tests.test_superbook -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/gzkit/superbook.py tests/test_superbook.py
git commit -m "feat(superbook): implement apply_draft() — write ADR, OBPIs, and ledger events"
```

### Task 10: Register `gz superbook` CLI subcommand

**Files:**
- Create: `src/gzkit/commands/superbook.py`
- Modify: `src/gzkit/cli.py`

- [ ] **Step 1: Create the thin CLI wrapper**

Create `src/gzkit/commands/superbook.py`:

```python
"""CLI command for gz superbook — bridge superpowers to GovZero governance."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from gzkit.superbook import (
    apply_draft,
    classify_lane,
    generate_adr_draft,
    next_semver,
    present_draft,
)
from gzkit.superbook_parser import extract_commits, parse_plan, parse_spec


def superbook_cmd(
    mode: str,
    spec_path: str,
    plan_path: str,
    *,
    semver: str | None = None,
    lane: str | None = None,
    apply: bool = False,
) -> None:
    """Execute the superbook pipeline.

    Args:
        mode: "retroactive" or "forward".
        spec_path: Path to superpowers spec document.
        plan_path: Path to superpowers plan document.
        semver: Optional semver override.
        lane: Optional lane override.
        apply: If True, write artifacts. Otherwise dry-run.
    """
    console = Console()
    project_root = Path.cwd()

    # Step 1: Parse
    spec = parse_spec(Path(spec_path))
    plan = parse_plan(Path(plan_path))

    if not plan.chunks:
        console.print("[red]Error: No chunks found in plan.[/red]")
        raise SystemExit(1)

    # Step 2: Classify lane
    if lane:
        from gzkit.superbook_models import LaneClassification

        classification = LaneClassification(lane=lane, confidence="override")
    else:
        classification = classify_lane(spec, plan)

    # Step 3: Determine semver
    if not semver:
        from gzkit.ledger import Ledger

        ledger = Ledger(project_root / ".gzkit" / "ledger.jsonl")
        existing = [
            e.id.replace("ADR-", "")
            for e in ledger.read_all()
            if e.event == "adr_created"
        ]
        semver = next_semver(existing)

    # Step 4: Generate draft
    status = "Pending-Attestation" if mode == "retroactive" else "Draft"
    adr = generate_adr_draft(
        spec, plan, lane=classification.lane, semver=semver, status=status
    )

    # Step 5: Retroactive evidence
    if mode == "retroactive":
        commits = extract_commits(
            plan_date=spec_path.split("/")[-1][:10],  # YYYY-MM-DD from filename
            project_root=project_root,
        )
        if commits:
            from gzkit.superbook import map_commits_to_chunks

            mapping = map_commits_to_chunks(commits, list(plan.chunks))
            for idx, obpi in enumerate(adr.obpis):
                chunk_commits = mapping[idx] if idx < len(mapping) - 1 else []
                obpi.evidence = [
                    f"{c.sha} {c.message} ({', '.join(c.files[:3])})"
                    for c in chunk_commits
                ]

    # Step 6: Present
    console.print(present_draft(adr))

    if not apply:
        console.print("[yellow]Dry run. Use --apply to book.[/yellow]")
        return

    # Apply
    created = apply_draft(adr, project_root)
    console.print(f"\n[green]Booked {len(created)} artifacts.[/green]")
    for path in created:
        console.print(f"  {path}")
```

- [ ] **Step 2: Register in cli.py**

Find the subcommand registration area in `src/gzkit/cli.py` (near line 4670 where `plan` is registered). Add after the last subcommand registration:

```python
    # superbook
    p_superbook = commands.add_parser("superbook", help="Bridge superpowers artifacts to GovZero governance")
    p_superbook.add_argument("mode", choices=["retroactive", "forward"], help="Booking mode")
    p_superbook.add_argument("--spec", required=True, help="Path to superpowers spec")
    p_superbook.add_argument("--plan", required=True, help="Path to superpowers plan")
    p_superbook.add_argument("--semver", default=None, help="Override auto-assigned semver")
    p_superbook.add_argument("--lane", default=None, choices=["lite", "heavy"], help="Override lane")
    p_superbook.add_argument("--apply", action="store_true", help="Write artifacts (default: dry-run)")
    p_superbook.set_defaults(
        func=lambda a: superbook_cmd(
            mode=a.mode,
            spec_path=a.spec,
            plan_path=a.plan,
            semver=a.semver,
            lane=a.lane,
            apply=a.apply,
        )
    )
```

Note: Import `superbook_cmd` at top of cli.py or use lazy import matching existing patterns in the file.

- [ ] **Step 3: Test CLI registration**

Run: `uv run gz superbook --help`
Expected: shows usage with `retroactive`/`forward` modes and flags

- [ ] **Step 4: Commit**

```bash
git add src/gzkit/commands/superbook.py src/gzkit/cli.py
git commit -m "feat(cli): register gz superbook subcommand"
```

---

## Chunk 5: Skill Wrapper and Integration Test

### Task 11: Create the skill wrapper

**Files:**
- Create: `.gzkit/skills/gz-superbook/SKILL.md`

- [ ] **Step 1: Write the skill file**

```markdown
---
name: gz-superbook
description: Bridge superpowers specs/plans to GovZero ADR/OBPI governance artifacts. Supports retroactive booking of completed work and forward booking before implementation.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-15
---

# gz superbook

Bridge superpowers artifacts to GovZero governance.

## Trigger

- After completing superpowers plan execution (retroactive booking)
- After superpowers plan is approved, before implementation (forward booking)
- User asks to "book", "superbook", or "create ADR from plan"

## Usage

### Retroactive (book completed work)

```bash
uv run gz superbook retroactive \
  --spec docs/superpowers/specs/<spec>.md \
  --plan docs/superpowers/plans/<plan>.md \
  --apply
```

### Forward (book before implementation)

```bash
uv run gz superbook forward \
  --spec docs/superpowers/specs/<spec>.md \
  --plan docs/superpowers/plans/<plan>.md \
  --apply
```

## Behavior

1. Parses superpowers spec and plan markdown
2. Auto-classifies governance lane (lite/heavy) from file scope
3. Maps plan chunks to OBPI briefs with REQ IDs
4. Presents draft for human review
5. On --apply: writes ADR, OBPIs, and ledger events

## Constraints

- Always run dry-run first (default without --apply)
- Human must review and approve before booking
- Retroactive mode sets status to Pending-Attestation (human must still run gz attest)
- Forward mode sets status to Draft
```

- [ ] **Step 2: Commit**

```bash
git add .gzkit/skills/gz-superbook/
git commit -m "feat(skills): add gz-superbook skill wrapper"
```

### Task 12: End-to-end integration test with actual artifacts

**Files:**
- No new files — verification step

- [ ] **Step 1: Run superbook retroactive dry-run against our actual work**

```bash
uv run gz superbook retroactive \
  --spec docs/superpowers/specs/2026-03-15-agents-md-tidy-design.md \
  --plan docs/superpowers/plans/2026-03-15-agents-md-tidy.md
```

Expected: prints draft summary showing ADR with 5 OBPIs, heavy lane, evidence from commits.

- [ ] **Step 2: Review the draft output**

Verify: correct semver, correct lane classification, chunks mapped to OBPIs, REQ IDs generated, evidence populated.

- [ ] **Step 3: Run with --apply if draft looks correct**

```bash
uv run gz superbook retroactive \
  --spec docs/superpowers/specs/2026-03-15-agents-md-tidy-design.md \
  --plan docs/superpowers/plans/2026-03-15-agents-md-tidy.md \
  --apply
```

- [ ] **Step 4: Verify artifacts created**

```bash
ls -la docs/design/adr/pre-release/ADR-*agents-md-tidy*/
ls -la docs/design/adr/pre-release/ADR-*agents-md-tidy*/obpis/
```

- [ ] **Step 5: Run quality gates**

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --surfaces
```

- [ ] **Step 6: Run gz status to verify booking is visible**

```bash
uv run gz status --table
```

Expected: new ADR appears in status table.

- [ ] **Step 7: Commit**

```bash
git add docs/design/adr/ .gzkit/ledger.jsonl
git commit -m "chore: retroactively book AGENTS.md tidy work via gz superbook"
```

- [ ] **Step 8: Sync**

```bash
uv run gz git-sync --apply --lint --test
```
