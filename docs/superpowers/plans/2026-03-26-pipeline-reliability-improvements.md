# Pipeline Reliability Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce agent friction and pipeline deadlocks via three targeted improvements: an atomic import rule, a `gz preflight` cleanup command, and mandatory baseline verification checks in the OBPI pipeline.

**Architecture:** Three independent changes. (1) A behavioral rule addition to `agents.local.md`. (2) A new `gz preflight` CLI command in `src/gzkit/commands/preflight.py` registered in `src/gzkit/cli/main.py`. (3) A prepend of baseline checks in `_pipeline_verification_commands()` in `src/gzkit/commands/obpi_cmd.py`.

**Tech Stack:** Python 3.13+, argparse CLI, unittest, ruff, uv

---

### Task 1: Add Atomic Import Rule to agents.local.md

**Files:**
- Modify: `agents.local.md`

- [ ] **Step 1: Add the rule**

Append this line to `agents.local.md` after the existing semantic-version ordering rules:

```markdown
- When adding imports in an Edit call, always include the code that uses them in the same edit. The post-edit ruff hook removes unused imports immediately — splitting import addition and usage across separate edits causes the import to be deleted before it's referenced.
```

- [ ] **Step 2: Regenerate control surfaces**

Run: `uv run gz agent sync control-surfaces`

This propagates the rule from `agents.local.md` into `AGENTS.md` (between the `<!-- BEGIN/END agents.local.md -->` markers).

- [ ] **Step 3: Verify the rule appears in AGENTS.md**

Run: `grep -A1 "post-edit ruff hook" AGENTS.md`

Expected: The new rule text appears in the local agent rules section.

- [ ] **Step 4: Commit**

```bash
git add agents.local.md AGENTS.md
git commit -m "docs: add atomic import rule to agents.local.md"
```

---

### Task 2: Add Baseline Verification to Pipeline Stage 3

**Files:**
- Modify: `src/gzkit/commands/obpi_cmd.py:139-160`
- Create: `tests/commands/test_pipeline_baseline_verification.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/commands/test_pipeline_baseline_verification.py`:

```python
import unittest

from gzkit.commands.obpi_cmd import _pipeline_verification_commands


class TestPipelineBaselineVerification(unittest.TestCase):
    """Tests for mandatory baseline checks in pipeline Stage 3."""

    def test_baseline_commands_present_when_brief_is_empty(self) -> None:
        result = _pipeline_verification_commands("", "lite")
        self.assertEqual(
            result[:3],
            ["uv run gz lint", "uv run gz typecheck", "uv run gz test"],
        )

    def test_baseline_commands_present_when_brief_has_custom_commands(self) -> None:
        brief = (
            "## Verification\n\n"
            "```bash\n"
            "uv run gz validate --documents\n"
            "python -c \"print('ok')\"\n"
            "```\n"
        )
        result = _pipeline_verification_commands(brief, "lite")
        self.assertEqual(
            result[:3],
            ["uv run gz lint", "uv run gz typecheck", "uv run gz test"],
        )
        self.assertIn("uv run gz validate --documents", result)
        self.assertIn("python -c \"print('ok')\"", result)

    def test_baseline_not_duplicated_when_brief_includes_them(self) -> None:
        brief = (
            "## Verification\n\n"
            "```bash\n"
            "uv run gz lint\n"
            "uv run gz test\n"
            "uv run gz validate --documents\n"
            "```\n"
        )
        result = _pipeline_verification_commands(brief, "lite")
        lint_count = result.count("uv run gz lint")
        test_count = result.count("uv run gz test")
        self.assertEqual(lint_count, 1)
        self.assertEqual(test_count, 1)

    def test_heavy_lane_extras_append_after_brief_commands(self) -> None:
        brief = (
            "## Verification\n\n"
            "```bash\n"
            "uv run gz validate --documents\n"
            "```\n"
        )
        result = _pipeline_verification_commands(brief, "heavy")
        self.assertIn("uv run mkdocs build --strict", result)
        self.assertIn("uv run -m behave features/", result)
        # Heavy extras come after baseline and brief commands
        validate_idx = result.index("uv run gz validate --documents")
        mkdocs_idx = result.index("uv run mkdocs build --strict")
        self.assertGreater(mkdocs_idx, validate_idx)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run -m unittest tests/commands/test_pipeline_baseline_verification.py -v`

Expected: `test_baseline_commands_present_when_brief_is_empty` FAILS because baseline commands are not prepended.

- [ ] **Step 3: Add baseline constant and prepend in the function**

Modify `src/gzkit/commands/obpi_cmd.py`. Before the `_pipeline_verification_commands` function (line 139), add the constant. Then change the function to start with the baseline:

```python
BASELINE_VERIFICATION = [
    "uv run gz lint",
    "uv run gz typecheck",
    "uv run gz test",
]


def _pipeline_verification_commands(obpi_content: str, lane: str) -> list[str]:
    """Parse the Verification block into executable shell commands."""
    commands: list[str] = list(BASELINE_VERIFICATION)
    section = extract_markdown_section(obpi_content, "Verification") or ""
    matches = re.findall(r"```bash\n(.*?)```", section, flags=re.DOTALL)
    for block in matches:
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line == "command --to --verify":
                continue
            commands.append(line)
    if lane == "heavy":
        commands.extend(["uv run mkdocs build --strict", "uv run -m behave features/"])

    deduped: list[str] = []
    seen: set[str] = set()
    for command in commands:
        if command in seen:
            continue
        seen.add(command)
        deduped.append(command)
    return deduped
```

- [ ] **Step 4: Run the new tests to verify they pass**

Run: `uv run -m unittest tests/commands/test_pipeline_baseline_verification.py -v`

Expected: All 4 tests PASS.

- [ ] **Step 5: Update existing pipeline test expectations**

The test `test_verify_runs_commands_and_preserves_markers` in `tests/commands/test_obpi_pipeline.py` (line 181) asserts specific command order. The baseline commands will now appear first. The brief in the test fixture includes `uv run gz lint`, `uv run gz typecheck`, and `uv run gz test` — dedup will keep the baseline's copies and skip the brief's duplicates.

Update the expected command list at line 207 in `tests/commands/test_obpi_pipeline.py`:

```python
            verify_commands = [call.args[0] for call in run_command_mock.call_args_list[:7]]
            self.assertEqual(
                verify_commands,
                [
                    "uv run gz lint",
                    "uv run gz typecheck",
                    "uv run gz test",
                    "uv run gz validate --documents",
                    "python -c \"print('verify ok')\"",
                    "uv run mkdocs build --strict",
                    "uv run -m behave features/",
                ],
            )
```

The command count stays at 7 (3 baseline + 2 brief-only + 2 heavy extras), but order changes: baseline first, then brief-specific commands that aren't duplicates.

- [ ] **Step 6: Run the full pipeline test suite**

Run: `uv run -m unittest tests/commands/test_obpi_pipeline.py -v`

Expected: All tests PASS.

- [ ] **Step 7: Lint and format**

Run: `uv run ruff check . --fix && uv run ruff format .`

Expected: Clean.

- [ ] **Step 8: Commit**

```bash
git add src/gzkit/commands/obpi_cmd.py tests/commands/test_pipeline_baseline_verification.py tests/commands/test_obpi_pipeline.py
git commit -m "feat: enforce baseline lint/typecheck/test in pipeline Stage 3"
```

---

### Task 3: Create `gz preflight` Command

**Files:**
- Create: `src/gzkit/commands/preflight.py`
- Modify: `src/gzkit/cli/main.py`
- Create: `tests/commands/test_preflight.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/commands/test_preflight.py`:

```python
import json
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner, _quick_init


class TestPreflightCommand(unittest.TestCase):
    """Tests for the gz preflight command."""

    def test_clean_state_exits_zero(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            result = runner.invoke(main, ["preflight"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("clean", result.output.lower())

    def test_detects_stale_pipeline_marker(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            plans_dir = Path(".claude/plans")
            plans_dir.mkdir(parents=True, exist_ok=True)
            stale_time = (datetime.now(UTC) - timedelta(hours=5)).isoformat()
            marker = {
                "obpi_id": "OBPI-0.1.0-01",
                "updated_at": stale_time,
            }
            (plans_dir / ".pipeline-active-OBPI-0.1.0-01.json").write_text(
                json.dumps(marker), encoding="utf-8"
            )
            result = runner.invoke(main, ["preflight"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("OBPI-0.1.0-01", result.output)
            self.assertIn("marker", result.output.lower())

    def test_detects_expired_lock(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            locks_dir = Path(".gzkit/locks/obpi")
            locks_dir.mkdir(parents=True, exist_ok=True)
            expired_time = (datetime.now(UTC) - timedelta(hours=3)).isoformat()
            lock = {
                "obpi_id": "OBPI-0.2.0-01",
                "claimed_at": expired_time,
                "ttl_minutes": 120,
                "agent": "claude-code",
                "pid": 0,
                "session_id": "test",
                "branch": "main",
            }
            (locks_dir / "OBPI-0.2.0-01.lock.json").write_text(
                json.dumps(lock), encoding="utf-8"
            )
            result = runner.invoke(main, ["preflight"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("OBPI-0.2.0-01", result.output)
            self.assertIn("lock", result.output.lower())

    def test_detects_orphan_receipt(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            plans_dir = Path(".claude/plans")
            plans_dir.mkdir(parents=True, exist_ok=True)
            receipt = {
                "obpi_id": "OBPI-0.3.0-01",
                "verdict": "PASS",
                "timestamp": "2026-03-01T12:00:00Z",
            }
            (plans_dir / ".plan-audit-receipt-OBPI-0.3.0-01.json").write_text(
                json.dumps(receipt), encoding="utf-8"
            )
            # No matching plan file or marker — receipt is orphaned
            result = runner.invoke(main, ["preflight"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("OBPI-0.3.0-01", result.output)
            self.assertIn("receipt", result.output.lower())

    def test_apply_removes_stale_artifacts(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            plans_dir = Path(".claude/plans")
            plans_dir.mkdir(parents=True, exist_ok=True)
            stale_time = (datetime.now(UTC) - timedelta(hours=5)).isoformat()
            marker_path = plans_dir / ".pipeline-active-OBPI-0.1.0-01.json"
            marker_path.write_text(
                json.dumps({"obpi_id": "OBPI-0.1.0-01", "updated_at": stale_time}),
                encoding="utf-8",
            )
            result = runner.invoke(main, ["preflight", "--apply"])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(marker_path.exists())

    def test_json_output(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            result = runner.invoke(main, ["preflight", "--json"])
            self.assertEqual(result.exit_code, 0)
            data = json.loads(result.output)
            self.assertIn("stale_markers", data)
            self.assertIn("orphan_receipts", data)
            self.assertIn("expired_locks", data)

    def test_no_issues_with_apply_exits_zero(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            result = runner.invoke(main, ["preflight", "--apply"])
            self.assertEqual(result.exit_code, 0)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run -m unittest tests/commands/test_preflight.py -v`

Expected: ImportError or AttributeError — `preflight` command doesn't exist yet.

- [ ] **Step 3: Create the preflight command module**

Create `src/gzkit/commands/preflight.py`:

```python
"""Preflight scan and cleanup for stale pipeline artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gzkit.commands.common import console, get_project_root
from gzkit.pipeline_runtime import (
    find_stale_pipeline_markers,
    load_pipeline_json,
)


def _find_orphan_receipts(plans_dir: Path) -> list[tuple[Path, str]]:
    """Find receipts with no matching pipeline marker or plan file."""
    orphans: list[tuple[Path, str]] = []
    for receipt_path in sorted(plans_dir.glob(".plan-audit-receipt-*.json")):
        receipt = load_pipeline_json(receipt_path)
        if receipt is None:
            orphans.append((receipt_path, "unreadable"))
            continue
        obpi_id = str(receipt.get("obpi_id") or "unknown")
        marker_path = plans_dir / f".pipeline-active-{obpi_id}.json"
        has_marker = marker_path.exists()
        plan_files = list(plans_dir.glob("*.md"))
        has_plan = any(obpi_id in p.read_text(encoding="utf-8") for p in plan_files if p.is_file())
        if not has_marker and not has_plan:
            orphans.append((receipt_path, obpi_id))
    # Also check legacy receipt
    legacy = plans_dir / ".plan-audit-receipt.json"
    if legacy.exists():
        receipt = load_pipeline_json(legacy)
        if receipt is not None:
            obpi_id = str(receipt.get("obpi_id") or "unknown")
            marker_path = plans_dir / f".pipeline-active-{obpi_id}.json"
            has_marker = marker_path.exists()
            plan_files = list(plans_dir.glob("*.md"))
            has_plan = any(
                obpi_id in p.read_text(encoding="utf-8") for p in plan_files if p.is_file()
            )
            if not has_marker and not has_plan:
                orphans.append((legacy, obpi_id))
    return orphans


def _find_expired_locks(locks_dir: Path) -> list[tuple[Path, str, float]]:
    """Find lock files whose claimed_at + ttl_minutes has passed."""
    expired: list[tuple[Path, str, float]] = []
    if not locks_dir.is_dir():
        return expired
    now = datetime.now(UTC)
    for lock_path in sorted(locks_dir.glob("*.lock.json")):
        lock = load_pipeline_json(lock_path)
        if lock is None:
            expired.append((lock_path, "unreadable", 0))
            continue
        obpi_id = str(lock.get("obpi_id") or "unknown")
        claimed_at = str(lock.get("claimed_at") or "")
        ttl_minutes = int(lock.get("ttl_minutes") or 120)
        if not claimed_at:
            expired.append((lock_path, obpi_id, 0))
            continue
        try:
            claim_time = datetime.fromisoformat(claimed_at.replace("Z", "+00:00"))
        except ValueError:
            expired.append((lock_path, obpi_id, 0))
            continue
        age_minutes = (now - claim_time).total_seconds() / 60
        if age_minutes > ttl_minutes:
            expired.append((lock_path, obpi_id, age_minutes))
    return expired


def preflight_cmd(*, apply: bool = False, as_json: bool = False) -> None:
    """Scan for stale pipeline artifacts and optionally clean them up."""
    project_root = get_project_root()
    plans_dir = project_root / ".claude" / "plans"
    locks_dir = project_root / ".gzkit" / "locks" / "obpi"

    stale_markers = find_stale_pipeline_markers(plans_dir) if plans_dir.is_dir() else []
    orphan_receipts = _find_orphan_receipts(plans_dir) if plans_dir.is_dir() else []
    expired_locks = _find_expired_locks(locks_dir)

    if as_json:
        data = {
            "stale_markers": [
                {"path": str(p.name), "obpi_id": str(m.get("obpi_id", "unknown"))}
                for p, m in stale_markers
            ],
            "orphan_receipts": [
                {"path": str(p.name), "obpi_id": oid} for p, oid in orphan_receipts
            ],
            "expired_locks": [
                {"path": str(p.name), "obpi_id": oid, "age_minutes": round(age, 1)}
                for p, oid, age in expired_locks
            ],
        }
        console.print(json.dumps(data, indent=2))
        if apply:
            _apply_cleanup(stale_markers, orphan_receipts, expired_locks)
        return

    total = len(stale_markers) + len(orphan_receipts) + len(expired_locks)

    if total == 0:
        console.print("Preflight scan: [green]clean[/green]")
        return

    console.print("Preflight scan:")
    for path, marker in stale_markers:
        obpi_id = str(marker.get("obpi_id", "unknown"))
        console.print(f"  Stale marker:   {path.name} ({obpi_id})")
    for path, obpi_id in orphan_receipts:
        console.print(f"  Orphan receipt:  {path.name} ({obpi_id})")
    for path, obpi_id, age in expired_locks:
        console.print(f"  Expired lock:    {path.name} ({obpi_id}, {age:.0f}m)")

    if apply:
        _apply_cleanup(stale_markers, orphan_receipts, expired_locks)
        console.print("[green]Cleanup applied.[/green]")
    else:
        console.print(f"\n{total} issue(s) found. Run with --apply to clean up.")
        raise SystemExit(1)


def _apply_cleanup(
    stale_markers: list[tuple[Path, dict[str, Any]]],
    orphan_receipts: list[tuple[Path, str]],
    expired_locks: list[tuple[Path, str, float]],
) -> None:
    """Remove stale artifacts."""
    for path, _ in stale_markers:
        path.unlink(missing_ok=True)
    for path, _ in orphan_receipts:
        path.unlink(missing_ok=True)
    for path, _, _ in expired_locks:
        path.unlink(missing_ok=True)
```

- [ ] **Step 4: Register the command in main.py**

Add the import to `src/gzkit/cli/main.py` alongside the other command imports (after line 64):

```python
from gzkit.commands.preflight import preflight_cmd
```

Add the parser registration. Find a suitable location in the command registration section — after `check-config-paths` (line 788) is a natural spot:

```python
    p_preflight = commands.add_parser(
        "preflight",
        help="Scan for stale pipeline artifacts",
        description="Detect and clean stale markers, orphan receipts, and expired locks.",
        epilog=build_epilog(
            [
                "gz preflight",
                "gz preflight --apply",
                "gz preflight --json",
            ]
        ),
    )
    p_preflight.add_argument(
        "--apply",
        action="store_true",
        help="Remove stale artifacts (default: dry-run report only)",
    )
    add_json_flag(p_preflight)
    p_preflight.set_defaults(func=lambda a: preflight_cmd(apply=a.apply, as_json=a.as_json))
```

- [ ] **Step 5: Run the preflight tests**

Run: `uv run -m unittest tests/commands/test_preflight.py -v`

Expected: All 7 tests PASS.

- [ ] **Step 6: Run the full test suite to check for regressions**

Run: `uv run -m unittest -q`

Expected: All tests PASS, no regressions.

- [ ] **Step 7: Lint and format**

Run: `uv run ruff check . --fix && uv run ruff format .`

Expected: Clean.

- [ ] **Step 8: Verify CLI help works**

Run: `uv run gz preflight --help`

Expected: Help text with `--apply` and `--json` flags documented.

- [ ] **Step 9: Commit**

```bash
git add src/gzkit/commands/preflight.py src/gzkit/cli/main.py tests/commands/test_preflight.py
git commit -m "feat: add gz preflight command for stale artifact detection and cleanup"
```

---

### Task 4: Final Verification and Quality Checks

**Files:**
- No new files

- [ ] **Step 1: Run full quality checks**

Run: `uv run gz check`

Expected: All checks pass (lint, format, typecheck, test, skill audit, parity, readiness).

- [ ] **Step 2: Verify preflight against live state**

Run: `uv run gz preflight`

Expected: Either "clean" or a report of actual stale artifacts in the working tree.

- [ ] **Step 3: Verify AGENTS.md has the new rule**

Run: `grep "post-edit ruff hook" AGENTS.md`

Expected: The atomic import rule appears in the local agent rules section.
