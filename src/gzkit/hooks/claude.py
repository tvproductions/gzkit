"""Claude Code hook generation and management.

Generates Claude hook settings for governance-safe pre/post edit automation.
"""

import json
from pathlib import Path
from textwrap import dedent

from gzkit.config import GzkitConfig


def _instruction_router_script() -> str:
    """Return the non-blocking instruction router hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"Instruction Auto-Injection Hook.

            PreToolUse hook that automatically surfaces relevant domain constraints
            when editing files, based on .github/instructions/*.instructions.md
            applyTo glob patterns.

            Informational only — never blocks operations. Outputs constraint
            reminders to stderr so they appear in the agent's context.

            Deduplication: tracks surfaced instructions in a state file and
            suppresses repeats within a 2-hour window per instruction file.

            Exit codes:
              0 - Always (non-blocking; informational only)
            \"\"\"

            import fnmatch
            import json
            import re
            import sys
            import time
            from pathlib import Path

            DEDUP_WINDOW_SECONDS = 2 * 60 * 60
            CONSTRAINT_KEYWORDS = (
                "prohibited",
                "must not",
                "must",
                "anti-pattern",
                "covenant",
                "core principles",
                "responsibilities",
            )
            MAX_LINES_PER_FILE = 15
            UNIVERSAL_INSTRUCTION = "cross-platform.instructions.md"


            def parse_apply_to(file_path):
                \"\"\"Extract applyTo glob patterns from instruction frontmatter.\"\"\"
                try:
                    text = file_path.read_text(encoding="utf-8")
                except OSError:
                    return []

                if not text.startswith("---"):
                    return []

                end = text.find("---", 3)
                if end == -1:
                    return []

                frontmatter = text[3:end]
                for line in frontmatter.splitlines():
                    line = line.strip()
                    if line.startswith("applyTo:"):
                        value = line[len("applyTo:") :].strip().strip('"').strip("'")
                        return [pattern.strip() for pattern in value.split(",") if pattern.strip()]
                return []


            def extract_constraint_sections(file_path):
                \"\"\"Extract key constraint sections from an instruction file.\"\"\"
                try:
                    text = file_path.read_text(encoding="utf-8")
                except OSError:
                    return []

                lines = text.splitlines()
                result = []
                capturing = False
                capture_level = 0

                for line in lines:
                    heading_match = re.match(r"^(#{1,6})\\s+(.*)", line)
                    if heading_match:
                        level = len(heading_match.group(1))
                        title = heading_match.group(2).lower()

                        if capturing and level <= capture_level:
                            capturing = False

                        if any(keyword in title for keyword in CONSTRAINT_KEYWORDS):
                            capturing = True
                            capture_level = level
                            result.append(line)
                            continue

                    if capturing and (not result or result[-1].strip() or line.strip()):
                        result.append(line)

                    if len(result) >= MAX_LINES_PER_FILE:
                        break

                return result[:MAX_LINES_PER_FILE]


            def load_state(state_path):
                \"\"\"Load dedup state from JSON file.\"\"\"
                try:
                    return json.loads(state_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    return {}


            def save_state(state_path, state):
                \"\"\"Persist dedup state to JSON file.\"\"\"
                try:
                    state_path.parent.mkdir(parents=True, exist_ok=True)
                    state_path.write_text(json.dumps(state, indent=2) + "\\n", encoding="utf-8")
                except OSError:
                    pass


            def main():
                \"\"\"Route file edits to matching instruction constraints.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                tool_input = input_data.get("tool_input", {})
                file_path = tool_input.get("file_path", "")
                cwd = input_data.get("cwd", "")

                if not file_path or not cwd:
                    sys.exit(0)

                try:
                    abs_path = Path(file_path).resolve()
                    cwd_path = Path(cwd).resolve()
                    rel_path = abs_path.relative_to(cwd_path)
                    rel_str = rel_path.as_posix()
                except (ValueError, TypeError):
                    sys.exit(0)

                instructions_dir = cwd_path / ".github" / "instructions"
                if not instructions_dir.is_dir():
                    sys.exit(0)

                instruction_files = sorted(instructions_dir.glob("*.instructions.md"))
                if not instruction_files:
                    sys.exit(0)

                matched = []
                is_python_file = rel_str.endswith(".py")

                for inst_file in instruction_files:
                    patterns = parse_apply_to(inst_file)
                    for pattern in patterns:
                        if fnmatch.fnmatch(rel_str, pattern):
                            matched.append(inst_file)
                            break

                if is_python_file:
                    universal = instructions_dir / UNIVERSAL_INSTRUCTION
                    if universal.is_file() and universal not in matched:
                        matched.append(universal)

                if not matched:
                    sys.exit(0)

                state_path = cwd_path / ".claude" / "hooks" / ".instruction-state.json"
                state = load_state(state_path)
                now = time.time()

                to_surface = []
                for inst_file in matched:
                    key = inst_file.name
                    last_surfaced = state.get(key, 0)
                    if (now - last_surfaced) >= DEDUP_WINDOW_SECONDS:
                        to_surface.append(inst_file)

                if not to_surface:
                    sys.exit(0)

                output_parts = []
                output_parts.append("INSTRUCTION CONSTRAINTS (auto-surfaced)")
                output_parts.append("=" * 45)
                output_parts.append(f"Triggered by: {rel_str}")
                output_parts.append("")

                for inst_file in to_surface:
                    sections = extract_constraint_sections(inst_file)
                    if not sections:
                        continue

                    output_parts.append(f"--- {inst_file.name} ---")
                    output_parts.extend(sections)
                    output_parts.append("")
                    state[inst_file.name] = now

                has_content = any(
                    line.startswith("--- ") and line.endswith(" ---") for line in output_parts
                )
                if not has_content:
                    sys.exit(0)

                save_state(state_path, state)
                print("\\n".join(output_parts), file=sys.stderr)
                sys.exit(0)


            if __name__ == "__main__":
                main()
            """
        )
        + "\n"
    )


def _post_edit_ruff_script() -> str:
    """Return the non-blocking post-edit ruff hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"Post-Edit Ruff Hook.

            PostToolUse hook that runs ruff check --fix and ruff format on edited
            Python files immediately after each Write/Edit operation.

            Shifts lint enforcement left: from pre-commit (batch) to post-edit
            (immediate), eliminating the "fix lint at the end" friction pattern.

            Exit codes:
              0 - Always (non-blocking; lint failures do not prevent edits)
            \"\"\"

            import json
            import subprocess
            import sys
            from contextlib import suppress
            from pathlib import Path

            TIMEOUT_SECONDS = 8


            def main():
                \"\"\"Run ruff on the edited file if it is a Python file.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                tool_input = input_data.get("tool_input", {})
                file_path = tool_input.get("file_path", "")

                if not file_path.endswith(".py"):
                    sys.exit(0)

                cwd = input_data.get("cwd", "")
                try:
                    target = Path(file_path)
                    if not target.is_absolute() and cwd:
                        target = Path(cwd) / target
                    target = target.resolve()
                except (ValueError, TypeError, OSError):
                    sys.exit(0)

                if not target.is_file():
                    sys.exit(0)

                posix_path = target.as_posix()

                with suppress(FileNotFoundError, subprocess.TimeoutExpired, OSError):
                    subprocess.run(
                        ["uv", "run", "ruff", "check", "--fix", "--quiet", posix_path],
                        capture_output=True,
                        timeout=TIMEOUT_SECONDS,
                    )

                with suppress(FileNotFoundError, subprocess.TimeoutExpired, OSError):
                    subprocess.run(
                        ["uv", "run", "ruff", "format", "--quiet", posix_path],
                        capture_output=True,
                        timeout=TIMEOUT_SECONDS,
                    )

                sys.exit(0)


            if __name__ == "__main__":
                main()
            """
        )
        + "\n"
    )


def _control_surface_sync_script() -> str:
    """Return the post-edit control-surface sync hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"Control Surface Sync Hook.

            PostToolUse hook that runs `gz agent sync control-surfaces` after edits
            to canonical governance files in .gzkit/.

            .gzkit/ holds master versions of all control surfaces:
              - skills/ — universal, mirrored identically across vendors
              - hooks/ — master source, rendered to platform-specific forms
              - rules/ — master source, rendered to platform-specific forms

            Exit codes:
              0 - Always (non-blocking; sync failures do not prevent edits)
            \"\"\"

            import json
            import subprocess
            import sys
            from contextlib import suppress
            from pathlib import Path

            TIMEOUT_SECONDS = 30

            CONTROL_SURFACE_PATTERNS = (
                ".gzkit/",
            )


            def main():
                \"\"\"Run control-surface sync if the edited file is a canonical source.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                tool_input = input_data.get("tool_input", {})
                file_path = tool_input.get("file_path", "")

                cwd = input_data.get("cwd", "")
                try:
                    target = Path(file_path)
                    if not target.is_absolute() and cwd:
                        target = Path(cwd) / target
                    target = target.resolve()
                    # Find project root
                    project_root = Path(cwd).resolve() if cwd else Path.cwd()
                    current = project_root
                    while current != current.parent:
                        if (current / ".gzkit").is_dir():
                            project_root = current
                            break
                        current = current.parent
                    rel_path = target.relative_to(project_root).as_posix()
                except (ValueError, TypeError, OSError):
                    sys.exit(0)

                matches = any(
                    rel_path.startswith(p) or rel_path == p.rstrip("/")
                    for p in CONTROL_SURFACE_PATTERNS
                )
                if not matches:
                    sys.exit(0)

                print(f"Control surface edited: {rel_path}", file=sys.stderr)
                print("Running gz agent sync control-surfaces...", file=sys.stderr)

                with suppress(FileNotFoundError, subprocess.TimeoutExpired, OSError):
                    result = subprocess.run(
                        ["uv", "run", "gz", "agent", "sync", "control-surfaces"],
                        capture_output=True,
                        text=True,
                        timeout=TIMEOUT_SECONDS,
                        cwd=str(project_root),
                    )
                    if result.returncode == 0:
                        print("Sync complete.", file=sys.stderr)
                    else:
                        print(f"Sync failed (exit {result.returncode}).", file=sys.stderr)
                        if result.stderr:
                            print(result.stderr[:500], file=sys.stderr)

                sys.exit(0)


            if __name__ == "__main__":
                main()
            """
        )
        + "\n"
    )


def _plan_audit_gate_script() -> str:
    """Return the plan-exit audit gate hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"Plan Audit Gate Hook.

            PreToolUse hook on ExitPlanMode that enforces the gz-plan-audit pre-flight
            alignment check. If the most recent plan in .claude/plans/ references an OBPI,
            the agent cannot exit plan mode until /gz-plan-audit has been run.

            How it works:
              1. Finds the most recently modified plan file in .claude/plans/
              2. Checks if the plan references an OBPI ID (pattern: OBPI-X.Y.Z-NN)
              3. If yes, looks for an audit receipt at .claude/plans/.plan-audit-receipt.json
              4. Receipt must reference the same OBPI and be newer than the plan file
              5. No valid receipt -> exit 2 (blocked)

            Receipt format (.claude/plans/.plan-audit-receipt.json):
              {
                "obpi_id": "OBPI-0.12.0-02",
                "timestamp": "2026-03-12T12:00:00Z",
                "verdict": "PASS"
              }

            Exit codes:
              0 - Allow operation (no OBPI plan, or audit receipt valid)
              2 - Block operation (OBPI plan exists but no valid audit receipt)
            \"\"\"

            import json
            import os
            import re
            import sys
            from pathlib import Path

            RECEIPT_FILE = ".plan-audit-receipt.json"
            OBPI_PATTERN = re.compile(r"OBPI-[\\d.]+-\\d+")
            NEW_FILE_PATTERNS = re.compile(
                r"\\(new\\)|\\bcreate\\s+`?(?:src|tests)/|new\\s+file|new\\s+module",
                re.IGNORECASE,
            )
            PRIOR_ART_PATTERNS = re.compile(
                r"existing\\s+pattern|prior\\s+art|/prior-art|registry|grep|"
                r"already\\s+exist|codebase\\s+inventory|search.*before|pattern\\s+discovery",
                re.IGNORECASE,
            )


            def find_plans_dir(cwd: str) -> Path | None:
                \"\"\"Find .claude/plans/ directory.\"\"\"
                plans_dir = Path(cwd) / ".claude" / "plans"
                return plans_dir if plans_dir.is_dir() else None


            def find_most_recent_plan(plans_dir: Path) -> Path | None:
                \"\"\"Find the most recently modified non-hidden markdown plan.\"\"\"
                md_files = [
                    path
                    for path in plans_dir.iterdir()
                    if path.suffix == ".md" and not path.name.startswith(".")
                ]
                if not md_files:
                    return None
                return max(md_files, key=lambda path: path.stat().st_mtime)


            def extract_obpi_ids(plan_path: Path) -> list[str]:
                \"\"\"Extract all referenced OBPI ids from a plan file.\"\"\"
                try:
                    content = plan_path.read_text(encoding="utf-8")
                except OSError:
                    return []
                return list(set(OBPI_PATTERN.findall(content)))


            def check_audit_receipt(
                plans_dir: Path, obpi_ids: list[str], plan_mtime: float
            ) -> tuple[bool, str]:
                \"\"\"Check whether a valid audit receipt exists.\"\"\"
                receipt_path = plans_dir / RECEIPT_FILE
                if not receipt_path.exists():
                    return False, "No audit receipt found"

                try:
                    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    return False, "Audit receipt is corrupted"

                receipt_obpi = receipt.get("obpi_id", "")
                receipt_verdict = receipt.get("verdict", "")

                if receipt_obpi not in obpi_ids:
                    return (
                        False,
                        f"Audit receipt is for {receipt_obpi}, but plan references "
                        f"{', '.join(obpi_ids)}",
                    )

                receipt_mtime = receipt_path.stat().st_mtime
                if receipt_mtime < plan_mtime:
                    return (
                        False,
                        "Audit receipt is older than plan file "
                        "(plan was modified after audit)",
                    )

                if receipt_verdict not in ("PASS", "FAIL"):
                    return False, f"Audit receipt has invalid verdict: {receipt_verdict!r}"

                return True, f"Valid receipt: {receipt_obpi} -> {receipt_verdict}"


            def check_prior_art_awareness(plan_path: Path) -> str | None:
                \"\"\"Warn when new-file plans omit evidence of prior-art discovery.\"\"\"
                try:
                    content = plan_path.read_text(encoding="utf-8")
                except OSError:
                    return None

                has_new_files = bool(NEW_FILE_PATTERNS.search(content))
                has_prior_art = bool(PRIOR_ART_PATTERNS.search(content))

                if has_new_files and not has_prior_art:
                    return (
                        "PRIOR ART REMINDER: Plan proposes new files but does not "
                        "reference existing codebase patterns. Consider running "
                        "/prior-art before implementing to avoid duplicating "
                        "existing capabilities."
                    )
                return None


            def main() -> None:
                \"\"\"Gate ExitPlanMode on gz-plan-audit completion.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                cwd = input_data.get("cwd", os.getcwd())

                plans_dir = find_plans_dir(cwd)
                if not plans_dir:
                    sys.exit(0)

                plan_file = find_most_recent_plan(plans_dir)
                if not plan_file:
                    sys.exit(0)

                prior_art_warning = check_prior_art_awareness(plan_file)
                if prior_art_warning:
                    print(prior_art_warning, file=sys.stderr)

                obpi_ids = extract_obpi_ids(plan_file)
                if not obpi_ids:
                    sys.exit(0)

                is_valid, reason = check_audit_receipt(
                    plans_dir, obpi_ids, plan_file.stat().st_mtime
                )
                if is_valid:
                    sys.exit(0)

                print(
                    f"BLOCKED: Cannot exit plan mode - plan audit required.\\n"
                    f"\\n"
                    f"Plan '{plan_file.name}' references: {', '.join(obpi_ids)}\\n"
                    f"Reason: {reason}\\n"
                    f"\\n"
                    f"REQUIRED: Run the pre-flight alignment audit first:\\n"
                    f"  /gz-plan-audit {obpi_ids[0]}\\n"
                    f"\\n"
                    f"This verifies ADR <-> OBPI <-> Plan alignment before "
                    f"implementation begins.\\n",
                    file=sys.stderr,
                )
                sys.exit(2)


            if __name__ == "__main__":
                main()
            """
        )
        + "\n"
    )


def _pipeline_router_script() -> str:
    """Return the pipeline router hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"Pipeline Router Hook.

            PostToolUse hook on ExitPlanMode that routes the agent to
            `uv run gz obpi pipeline` after plan approval for OBPI work.

            How it works:
              1. Reads `.claude/plans/.plan-audit-receipt.json`
              2. If the receipt exists, names an OBPI, and has verdict `PASS`,
                 emit a routing instruction on stdout directing the agent to
                 invoke the canonical runtime command
              3. If the receipt is absent, invalid, or not `PASS`, exit silently

            Exit codes:
              0 - Always (PostToolUse hooks should not block)
            \"\"\"

            import json
            import os
            import sys
            from pathlib import Path


            def find_project_root(start: Path) -> Path:
                \"\"\"Find the project root by looking for .gzkit or src/gzkit.\"\"\"
                current = start
                while current != current.parent:
                    if (current / ".gzkit").is_dir() or (current / "src" / "gzkit").is_dir():
                        return current
                    current = current.parent
                return start


            def main() -> None:
                \"\"\"Route approved OBPI plans into the pipeline.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                project_root = find_project_root(Path(input_data.get("cwd", os.getcwd())).resolve())
                sys.path.insert(0, str(project_root / "src"))

                try:
                    from gzkit.pipeline_runtime import (
                        load_plan_audit_receipt,
                        pipeline_plans_dir,
                        pipeline_router_message,
                    )
                except Exception:
                    sys.exit(0)

                plans_dir = pipeline_plans_dir(project_root)
                receipt_path = plans_dir / ".plan-audit-receipt.json"
                if not receipt_path.exists():
                    sys.exit(0)

                receipt_state, _warnings, receipt = load_plan_audit_receipt(plans_dir, "")
                if receipt is None or receipt_state != "pass":
                    sys.exit(0)

                obpi_id = str(receipt.get("obpi_id") or "")
                if not obpi_id:
                    sys.exit(0)

                print(pipeline_router_message(obpi_id))
                sys.exit(0)


            if __name__ == "__main__":
                main()
            """
        )
        + "\n"
    )


def _pipeline_gate_script() -> str:
    """Return the pipeline gate hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"Pipeline Gate Hook.

            PreToolUse hook on Write|Edit that blocks implementation file writes
            under `src/` and `tests/` when an OBPI plan-audit receipt exists but
            the governance pipeline has not been activated.

            Exit codes:
              0 - Allow operation
              2 - Block operation (pipeline not invoked)
            \"\"\"

            import json
            import os
            import sys
            from pathlib import Path


            def resolve_repo_path(cwd: str, file_path: str) -> str | None:
                \"\"\"Resolve a tool file path into a repo-relative POSIX path.\"\"\"
                if not cwd or not file_path:
                    return None

                try:
                    cwd_path = Path(cwd).resolve()
                    target = Path(file_path)
                    if not target.is_absolute():
                        target = cwd_path / target
                    rel_path = target.resolve().relative_to(cwd_path)
                except (OSError, TypeError, ValueError):
                    return None

                return rel_path.as_posix()


            def find_project_root(start: Path) -> Path:
                \"\"\"Find the project root by looking for .gzkit or src/gzkit.\"\"\"
                current = start
                while current != current.parent:
                    if (current / ".gzkit").is_dir() or (current / "src" / "gzkit").is_dir():
                        return current
                    current = current.parent
                return start


            def main() -> None:
                \"\"\"Gate implementation writes until the pipeline is active.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                tool_input = input_data.get("tool_input", {})
                rel_path = resolve_repo_path(
                    input_data.get("cwd", os.getcwd()),
                    tool_input.get("file_path", ""),
                )
                if rel_path is None or not rel_path.startswith(("src/", "tests/")):
                    sys.exit(0)

                project_root = find_project_root(Path(input_data.get("cwd", os.getcwd())).resolve())
                sys.path.insert(0, str(project_root / "src"))

                try:
                    from gzkit.pipeline_runtime import (
                        load_plan_audit_receipt,
                        marker_matches,
                        pipeline_gate_message,
                        pipeline_marker_paths,
                        pipeline_plans_dir,
                    )
                except Exception:
                    sys.exit(0)

                plans_dir = pipeline_plans_dir(project_root)
                receipt_path = plans_dir / ".plan-audit-receipt.json"
                if not receipt_path.exists():
                    sys.exit(0)

                receipt_state, _warnings, receipt = load_plan_audit_receipt(plans_dir, "")
                if receipt is None or receipt_state != "pass":
                    sys.exit(0)

                obpi_id = str(receipt.get("obpi_id") or "")
                if not obpi_id:
                    sys.exit(0)

                obpi_marker, legacy_marker = pipeline_marker_paths(plans_dir, obpi_id)
                if marker_matches(obpi_marker, obpi_id):
                    sys.exit(0)

                if marker_matches(legacy_marker, obpi_id):
                    sys.exit(0)

                print(pipeline_gate_message(obpi_id), file=sys.stderr)
                sys.exit(2)


            if __name__ == "__main__":
                main()
            """
        )
        + "\n"
    )


def _pipeline_completion_reminder_script() -> str:
    """Return the pipeline completion reminder hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"Pipeline Completion Reminder Hook.

            PreToolUse hook on Bash that emits a non-blocking reminder before
            `git commit` or `git push` when an OBPI pipeline is still active
            and the corresponding brief has not been completed.

            Exit codes:
              0 - Always (advisory only)
            \"\"\"

            import json
            import os
            import sys
            from pathlib import Path


            def find_project_root(start: Path) -> Path:
                \"\"\"Find the project root by looking for .gzkit or src/gzkit.\"\"\"
                current = start
                while current != current.parent:
                    if (current / ".gzkit").is_dir() or (current / "src" / "gzkit").is_dir():
                        return current
                    current = current.parent
                return start


            def main() -> None:
                \"\"\"Emit a reminder before commit/push when the pipeline is incomplete.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                tool_input = input_data.get("tool_input", {})
                command = tool_input.get("command", "")
                if not any(git_cmd in command for git_cmd in ("git commit", "git push")):
                    sys.exit(0)

                project_root = find_project_root(Path(input_data.get("cwd", os.getcwd())).resolve())
                sys.path.insert(0, str(project_root / "src"))

                try:
                    from gzkit.pipeline_runtime import (
                        extract_brief_status,
                        find_active_pipeline_marker,
                        find_obpi_brief,
                        pipeline_completion_reminder_message,
                        pipeline_plans_dir,
                    )
                except Exception:
                    sys.exit(0)

                plans_dir = pipeline_plans_dir(project_root)
                if not plans_dir.is_dir():
                    sys.exit(0)

                marker = find_active_pipeline_marker(plans_dir)
                if not marker:
                    sys.exit(0)

                obpi_id = marker.get("obpi_id", "")
                if not obpi_id:
                    sys.exit(0)

                brief_path = find_obpi_brief(project_root / "docs" / "design" / "adr", obpi_id)
                if brief_path is None:
                    sys.exit(0)

                message = pipeline_completion_reminder_message(
                    marker,
                    brief_status=extract_brief_status(brief_path),
                )
                if not message:
                    sys.exit(0)

                print(message, file=sys.stderr)
                sys.exit(0)


            if __name__ == "__main__":
                main()
            """
        )
        + "\n"
    )


def _session_staleness_check_script() -> str:
    """Return the session staleness check hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"Session Staleness Check Hook (gzkit adaptation).

            PreToolUse hook on Write|Edit that detects stale pipeline artifacts
            left from previous sessions and emits warnings so the agent can
            clean up before hitting gate blocks.

            Adapted from airlineops canonical session-staleness-check.py.
            Uses gzkit's OBPI path structure (design/adr/.../obpis/) instead of
            airlineops briefs layout.

            Checks for:
              1. .pipeline-active.json referencing a completed OBPI
              2. .plan-audit-receipt.json referencing a completed OBPI

            Non-blocking — emits warnings only (exit 0 always).
            \"\"\"

            import json
            import sys
            from pathlib import Path


            def _read_json(path: Path) -> dict | None:
                \"\"\"Read a JSON file, returning None on any error.\"\"\"
                if not path.exists():
                    return None
                try:
                    return json.loads(path.read_bytes())
                except (json.JSONDecodeError, OSError):
                    return None


            def _brief_is_completed(cwd: Path, obpi_id: str) -> bool:
                \"\"\"Check if the referenced OBPI brief has status Completed.

                gzkit stores briefs under design/adr/pre-release/ADR-X.Y.Z-.../obpis/OBPI-*.md
                \"\"\"
                # Extract numeric prefix (e.g., OBPI-0.14.0-02-... -> 0.14.0)
                stripped = obpi_id.replace("OBPI-", "")
                parts = stripped.rsplit("-", 1)
                if len(parts) < 2:
                    return False

                # Search design/adr for matching OBPI files
                adr_root = cwd / "docs" / "design" / "adr"
                if not adr_root.exists():
                    return False

                # gzkit uses pre-release/ADR-X.Y.Z-.../obpis/ structure
                for brief_path in adr_root.rglob(f"OBPI-{stripped}*.md"):
                    try:
                        text = brief_path.read_text(encoding="utf-8")
                        for line in text.splitlines()[:15]:
                            if "Status:" in line and "Completed" in line:
                                return True
                    except OSError:
                        continue

                return False


            def main():
                \"\"\"Check for stale pipeline artifacts and warn.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                cwd = input_data.get("cwd", "")
                if not cwd:
                    sys.exit(0)

                cwd_path = Path(cwd).resolve()
                plans_dir = cwd_path / ".claude" / "plans"

                marker_path = plans_dir / ".pipeline-active.json"
                receipt_path = plans_dir / ".plan-audit-receipt.json"

                marker = _read_json(marker_path)
                receipt = _read_json(receipt_path)

                warnings = []

                if marker:
                    obpi_id = marker.get("obpi_id", "")
                    if obpi_id and _brief_is_completed(cwd_path, obpi_id):
                        warnings.append(
                            f"Stale .pipeline-active.json: references {obpi_id} "
                            f"which is already Completed. "
                            f"Clean up: delete {marker_path.relative_to(cwd_path)}"
                        )

                if receipt:
                    obpi_id = receipt.get("obpi_id", "")
                    if obpi_id and _brief_is_completed(cwd_path, obpi_id):
                        warnings.append(
                            f"Stale .plan-audit-receipt.json: references {obpi_id} "
                            f"which is already Completed. "
                            f"Clean up: delete {receipt_path.relative_to(cwd_path)}"
                        )

                if warnings:
                    print(
                        "SESSION STALENESS WARNING\\n"
                        + "\\n".join(f"  - {w}" for w in warnings)
                        + "\\n\\nClean up stale artifacts to avoid gate blocks.",
                        file=sys.stderr,
                    )

                # Always non-blocking
                sys.exit(0)


            if __name__ == "__main__":
                main()
            """
        )
        + "\n"
    )


def _obpi_completion_validator_script() -> str:
    """Return the OBPI completion validator hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"OBPI Completion Validator Hook.

            PreToolUse hook that gates OBPI brief completion by checking ledger evidence
            before allowing status changes to 'Completed'.

            Aligned with airlineops canonical obpi-completion-validator.py.
            Uses ADR-local audit ledger ({adr-dir}/logs/obpi-audit.jsonl) as evidence source.

            Adaptations from canonical:
              - Path check: /obpis/OBPI- (gzkit) instead of /briefs/OBPI- (airlineops)
              - Lane resolution: checks both ADR markdown and frontmatter for Heavy lane

            Exit codes:
              0 - Allow operation
              2 - Block operation (evidence missing or attestation required)
            \"\"\"

            import json
            import re
            import sys
            from pathlib import Path


            def find_project_root() -> Path:
                \"\"\"Find the project root by looking for .gzkit directory.\"\"\"
                current = Path.cwd()
                while current != current.parent:
                    if (current / ".gzkit").is_dir():
                        return current
                    current = current.parent
                return Path.cwd()


            def find_parent_adr_dir(brief_path: Path) -> Path | None:
                \"\"\"Find the parent ADR directory from a brief path.

                gzkit stores briefs in /obpis/ (airlineops uses /briefs/).
                \"\"\"
                parent_dir = brief_path.parent
                if parent_dir.name not in ("obpis", "briefs"):
                    return None
                return parent_dir.parent


            def find_parent_adr_file(adr_dir: Path) -> Path | None:
                \"\"\"Find the parent ADR markdown file.\"\"\"
                for f in adr_dir.iterdir():
                    if (
                        f.name.startswith("ADR-")
                        and f.name.endswith(".md")
                        and re.match(r"ADR-[\\d.]+-", f.name)
                    ):
                        return f
                return None


            def check_status_change_to_completed(new_string: str) -> bool:
                \"\"\"Check if the edit changes status to Completed.\"\"\"
                status_patterns = [
                    r"\\*\\*(?:Brief\\s+)?Status:\\*\\*\\s*Completed",
                    r"^(?:Brief\\s+)?Status:\\s*Completed",
                    r"^\\|\\s*(?:Brief\\s+)?Status\\s*\\|\\s*Completed\\s*\\|",
                ]
                return any(
                    re.search(pattern, new_string, re.MULTILINE | re.IGNORECASE)
                    for pattern in status_patterns
                )


            def extract_obpi_id(file_path: str) -> str | None:
                \"\"\"Extract OBPI short ID (e.g. OBPI-0.14.0-04) from file path.\"\"\"
                match = re.search(r"(OBPI-[\\d.]+-\\d+)", file_path)
                return match.group(1) if match else None


            def extract_adr_id(obpi_id: str) -> str | None:
                \"\"\"Extract parent ADR ID from OBPI ID.

                e.g. OBPI-0.14.0-04 -> ADR-0.14.0
                \"\"\"
                match = re.match(r"OBPI-([\\d.]+)-\\d+", obpi_id)
                return f"ADR-{match.group(1)}" if match else None


            def is_foundation_adr(adr_id: str) -> bool:
                \"\"\"Check if ADR is foundation series (0.0.x).\"\"\"
                return adr_id.startswith("ADR-0.0.")


            def get_parent_adr_lane(adr_file: Path | None) -> str:
                \"\"\"Determine parent ADR's lane (Heavy or Lite).\"\"\"
                if adr_file is None:
                    return "unknown"
                try:
                    content = adr_file.read_text(encoding="utf-8")
                except OSError:
                    return "unknown"

                heavy_patterns = [
                    r"##\\s*Lane[\\s\\S]{0,50}Heavy",
                    r"\\*\\*Lane:\\*\\*\\s*Heavy",
                    r"Lane:\\s*Heavy",
                    r"\\|\\s*Lane\\s*\\|\\s*Heavy\\s*\\|",
                ]
                for pattern in heavy_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return "Heavy"

                return "Lite"


            def get_execution_mode(adr_file: Path | None) -> str:
                \"\"\"Read execution mode from ADR's ## Execution Mode section.\"\"\"
                if adr_file is None:
                    return "normal"
                try:
                    content = adr_file.read_text(encoding="utf-8")
                except OSError:
                    return "normal"

                exception_patterns = [
                    r"\\*\\*Mode:\\*\\*\\s*Exception",
                    r"Mode:\\s*Exception",
                ]
                for pattern in exception_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return "exception"

                return "normal"


            STRICT_PLACEHOLDERS = frozenset({
                "-", "tbd", "(none)", "n/a", "...", "paste test output here",
            })


            def has_substantive_implementation_summary(content: str) -> bool:
                \"\"\"Check for substantive bullet points in Implementation Summary.\"\"\"
                match = re.search(
                    r"^### Implementation Summary\\s*$([\\s\\S]*?)(?:^### |\\n---|\\Z)",
                    content,
                    flags=re.MULTILINE,
                )
                if not match:
                    return False
                section = match.group(1)
                # Primary: "- Key: value" bullets
                bullets = re.findall(r"^- [^:\\n]+:[ \\t]*(.+)$", section, flags=re.MULTILINE)
                if not bullets:
                    # Fallback: plain "- text" bullets
                    bullets = re.findall(r"^- \\s*(.+)$", section, flags=re.MULTILINE)
                for bullet in bullets:
                    normalized = bullet.strip().lower()
                    if normalized and normalized not in STRICT_PLACEHOLDERS:
                        return True
                return False


            def has_substantive_key_proof(content: str) -> bool:
                \"\"\"Check for substantive Key Proof section.\"\"\"
                for heading in ("Key Proof", "Verification", "Gate Evidence"):
                    match = re.search(
                        rf"^### {re.escape(heading)}\\s*$([\\s\\S]*?)(?:^### |\\n---|\\Z)",
                        content,
                        flags=re.MULTILINE,
                    )
                    if match:
                        body = match.group(1).strip()
                        if body and body.lower() not in STRICT_PLACEHOLDERS:
                            return True
                return False


            def resolve_would_be_content(abs_path: Path, tool_input: dict) -> str:
                \"\"\"Resolve the file content that would result from the edit/write.\"\"\"
                content_field = tool_input.get("content")
                if content_field:
                    # Write tool: content IS the full new file
                    return content_field
                # Edit tool: read current file, apply old_string -> new_string
                old = tool_input.get("old_string", "")
                new = tool_input.get("new_string", "")
                try:
                    current = abs_path.read_text(encoding="utf-8")
                except OSError:
                    return new
                if old and old in current:
                    return current.replace(old, new, 1)
                return current


            def has_audit_evidence(adr_dir: Path, obpi_id: str) -> bool:
                \"\"\"Check if audit ledger entry exists for this OBPI in ADR-local ledger.\"\"\"
                ledger_file = adr_dir / "logs" / "obpi-audit.jsonl"

                if not ledger_file.exists():
                    return False

                try:
                    with ledger_file.open("r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                entry = json.loads(line)
                                entry_type = entry.get("type", "")
                                entry_obpi = entry.get("obpi_id", "")
                                if entry_obpi == obpi_id and entry_type in (
                                    "obpi-audit",
                                    "obpi-completion",
                                ):
                                    return True
                            except json.JSONDecodeError:
                                continue
                except OSError:
                    return False

                return False


            def has_human_attestation(adr_dir: Path, obpi_id: str) -> bool:
                \"\"\"Check if human attestation exists in ADR-local ledger for this OBPI.\"\"\"
                ledger_file = adr_dir / "logs" / "obpi-audit.jsonl"

                if not ledger_file.exists():
                    return False

                try:
                    with ledger_file.open("r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                entry = json.loads(line)
                                entry_obpi = entry.get("obpi_id", "")
                                if entry_obpi == obpi_id:
                                    evidence = entry.get("evidence", {})
                                    if evidence.get("human_attestation"):
                                        return True
                                    if entry.get("attestation_type") == "human":
                                        return True
                            except json.JSONDecodeError:
                                continue
                except OSError:
                    return False

                return False


            def main():
                \"\"\"Validate and gate OBPI completion.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                tool_input = input_data.get("tool_input", {})
                file_path = tool_input.get("file_path", "")
                new_string = tool_input.get("new_string", "") or tool_input.get("content", "")

                # Normalize path
                try:
                    project_root = find_project_root()
                    abs_path = Path(file_path).resolve()
                    rel_path = abs_path.relative_to(project_root)
                    rel_str = rel_path.as_posix()
                except (ValueError, TypeError):
                    sys.exit(0)

                # 1. Is this an OBPI brief file? (gzkit uses /obpis/, airlineops uses /briefs/)
                if "/obpis/OBPI-" not in rel_str or not rel_str.endswith(".md"):
                    sys.exit(0)

                # 2. Is this changing status to Completed?
                #    If old_string already contains Completed, the file is already in that state
                #    and this edit is not introducing a status transition — allow it through.
                old_string = tool_input.get("old_string", "")
                if not check_status_change_to_completed(new_string):
                    sys.exit(0)
                if old_string and check_status_change_to_completed(old_string):
                    sys.exit(0)

                # 3. Extract identifiers
                obpi_id = extract_obpi_id(rel_str)
                if not obpi_id:
                    sys.exit(0)

                adr_id = extract_adr_id(obpi_id)
                if not adr_id:
                    sys.exit(0)

                # 4. Find parent ADR directory and file
                adr_dir = find_parent_adr_dir(abs_path)
                if not adr_dir or not adr_dir.exists():
                    sys.exit(0)

                adr_file = find_parent_adr_file(adr_dir)

                # 5. Check brief content quality (hard block)
                would_be = resolve_would_be_content(abs_path, tool_input)
                brief_blocks = []
                if not has_substantive_implementation_summary(would_be):
                    brief_blocks.append(
                        "  - Missing or non-substantive 'Implementation Summary' "
                        "(requires bullet format: '- Key: value')"
                    )
                if not has_substantive_key_proof(would_be):
                    brief_blocks.append(
                        "  - Missing or non-substantive 'Key Proof' "
                        "(requires test command output or verification evidence)"
                    )
                if brief_blocks:
                    details = "\\n".join(brief_blocks)
                    print(
                        f"\\n\\u26d4 BLOCKED: Cannot mark {obpi_id} as Completed.\\n"
                        f"\\n"
                        f"Brief content quality checks failed:\\n"
                        f"{details}\\n"
                        f"\\n"
                        f"REQUIRED: Add substantive content to these sections before "
                        f"marking the OBPI as Completed.\\n",
                        file=sys.stderr,
                    )
                    sys.exit(2)

                # 6. Check for audit evidence in ADR-local ledger
                if not has_audit_evidence(adr_dir, obpi_id):
                    print(
                        f"\\n\\u26d4 BLOCKED: Cannot mark {obpi_id} as Completed.\\n"
                        f"\\n"
                        f"No audit evidence found in {adr_dir.name}/logs/obpi-audit.jsonl\\n"
                        f"\\n"
                        f"REQUIRED: Run gz-obpi-audit first to verify and record evidence:\\n"
                        f"  /gz-obpi-audit {obpi_id}\\n",
                        file=sys.stderr,
                    )
                    sys.exit(2)

                # 7. Check attestation requirements
                execution_mode = get_execution_mode(adr_file)

                if execution_mode == "exception":
                    # Exception mode: self-close allowed. Audit evidence already
                    # validated above. Human reviews at ADR closeout.
                    sys.exit(0)

                # Normal mode: check lane for attestation rigor
                is_foundation = is_foundation_adr(adr_id)
                parent_lane = get_parent_adr_lane(adr_file)
                requires_human = is_foundation or parent_lane == "Heavy"

                if requires_human and not has_human_attestation(adr_dir, obpi_id):
                    lane_reason = "Foundation (0.0.x)" if is_foundation else "Heavy lane"
                    print(
                        f"\\n\\u26d4 BLOCKED: {obpi_id} requires human attestation.\\n"
                        f"\\n"
                        f"Parent {adr_id} is {lane_reason}.\\n"
                        f"Per AGENTS.md, OBPIs under Heavy/Foundation ADRs "
                        f"inherit attestation rigor.\\n"
                        f"\\n"
                        f"REQUIRED: Present evidence and receive human attestation:\\n"
                        f"  1. Show verification command outputs and test results\\n"
                        f"  2. Wait for human to respond 'attested' or 'approved'\\n"
                        f"  3. Record attestation in ledger, then complete\\n",
                        file=sys.stderr,
                    )
                    sys.exit(2)

                # All validations passed
                sys.exit(0)


            if __name__ == "__main__":
                main()
            """
        )
        + "\n"
    )


def _ledger_writer_script() -> str:
    """Return the ledger writer hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"gzkit ledger writer and validator hook for claude.

            This hook records governance artifact edits and enforces completion gates.
            \"\"\"

            import json
            import os
            import sys
            from pathlib import Path


            def find_project_root() -> Path:
                \"\"\"Find the project root by looking for .gzkit directory.\"\"\"
                current = Path.cwd()
                while current != current.parent:
                    if (current / ".gzkit").is_dir():
                        return current
                    current = current.parent
                return Path.cwd()


            def main() -> int:
                \"\"\"Main hook entry point.\"\"\"
                # Read tool use info from stdin (Claude Code format)
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    return 0  # Silently continue if no valid input

                # Extract file path from tool use
                tool_name = input_data.get("tool_name", "")
                tool_input = input_data.get("tool_input", {})

                if tool_name not in ("Edit", "Write"):
                    return 0

                file_path = tool_input.get("file_path", "")
                if not file_path:
                    return 0

                # Make path relative to project root
                project_root = find_project_root()
                try:
                    rel_path = Path(file_path).relative_to(project_root)
                except ValueError:
                    return 0

                # Import gzkit and record edit/validate
                sys.path.insert(0, str(project_root / "src"))
                try:
                    from gzkit.hooks.core import record_artifact_edit

                    session = os.environ.get("CLAUDE_SESSION_ID") or os.environ.get(
                        "COPILOT_SESSION_ID"
                    )

                    # This will trigger validation and raise if it fails
                    record_artifact_edit(project_root, str(rel_path), session)

                except ImportError:
                    pass  # gzkit not installed, skip
                except Exception as exc:
                    print(f"\\n[GOVERNANCE BLOCK] {exc}\\n", file=sys.stderr)
                    return 1

                return 0


            if __name__ == "__main__":
                sys.exit(main())
            """
        )
        + "\n"
    )


def _claude_hooks_readme() -> str:
    """Return the generated local README for the Claude hook surface."""
    return "\n".join(
        [
            "# gzkit Claude Hooks",
            "",
            "Current hook surface in gzkit:",
            "",
            "- `session-staleness-check.py`",
            "  PreToolUse (`Write|Edit`) hook that detects stale pipeline",
            "  artifacts from previous sessions and emits warnings.",
            "- `instruction-router.py`",
            "  PreToolUse (`Write|Edit`) hook that auto-surfaces",
            "  `.github/instructions/*.instructions.md` constraints.",
            "- `obpi-completion-validator.py`",
            "  PreToolUse (`Write|Edit`) hook that gates OBPI brief completion",
            "  by checking ledger evidence before allowing status changes.",
            "- `plan-audit-gate.py`",
            "  PreToolUse (`ExitPlanMode`) hook that validates the latest",
            "  OBPI plan against `.claude/plans/.plan-audit-receipt.json`.",
            "- `pipeline-router.py`",
            "  PostToolUse (`ExitPlanMode`) hook that routes PASS receipts into",
            "  `uv run gz obpi pipeline`.",
            "- `pipeline-gate.py`",
            "  PreToolUse (`Write|Edit`) hook that blocks `src/` and `tests/`",
            "  writes until the runtime-owned active pipeline marker exists.",
            "- `pipeline-completion-reminder.py`",
            "  PreToolUse (`Bash`) hook that warns before `git commit` and",
            "  `git push` when an active OBPI runtime still appears incomplete.",
            "- `post-edit-ruff.py`",
            "  PostToolUse (`Write|Edit`) hook that runs `ruff check --fix`",
            "  and `ruff format` on edited Python files.",
            "- `ledger-writer.py`",
            "  PostToolUse (`Write|Edit`) hook that records governance",
            "  artifact edits via `gzkit.hooks.core.record_artifact_edit`.",
            "- `control-surface-sync.py`",
            "  PostToolUse (`Write|Edit`) hook that auto-syncs control surfaces",
            "  when canonical .gzkit/ files are edited.",
            "",
            "## Notes",
            "",
            "- The operator-facing `gz-plan-audit` skill and receipt contract are",
            "  ported under `ADR-0.12.0-obpi-pipeline-enforcement-parity`.",
            "- `src/gzkit/pipeline_runtime.py` is the canonical shared runtime used",
            "  by the CLI and generated pipeline hooks.",
            "- The pipeline enforcement hooks are active in `.claude/settings.json`",
            "  with the generated runtime order described below.",
            "",
            "## Registration Order",
            "",
            "- `PreToolUse` `ExitPlanMode`: `plan-audit-gate.py`",
            "- `PostToolUse` `ExitPlanMode`: `pipeline-router.py`",
            "- `PreToolUse` `Write|Edit`: `session-staleness-check.py`,",
            "  then `pipeline-gate.py`, then `obpi-completion-validator.py`,",
            "  then `instruction-router.py`",
            "- `PreToolUse` `Bash`: `pipeline-completion-reminder.py`",
            "- `PostToolUse` `Edit|Write`: `post-edit-ruff.py`,",
            "  then `ledger-writer.py`, then `control-surface-sync.py`",
            "- Historical intake matrix:",
            "  `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/",
            "claude-hooks-intake-matrix.md`",
            "- Active successor contract:",
            "  `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/",
            "claude-pipeline-hooks-parity-matrix.md`",
            "",
        ]
    )


def _write_hook_file(path: Path, content: str, executable: bool = False) -> None:
    """Write a generated Claude hook artifact."""
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def generate_claude_settings(config: GzkitConfig) -> dict:
    """Generate .claude/settings.json content.

    Args:
        config: Project configuration.

    Returns:
        Settings dictionary for Claude Code.

    """
    hooks_dir = config.paths.claude_hooks
    return {
        "enabledPlugins": {"superpowers@claude-plugins-official": False},
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "ExitPlanMode",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/plan-audit-gate.py",
                        }
                    ],
                },
                {
                    "matcher": "Write|Edit",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/session-staleness-check.py",
                        },
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/pipeline-gate.py",
                        },
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/obpi-completion-validator.py",
                        },
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/instruction-router.py",
                        },
                    ],
                },
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": (
                                f"uv run python {hooks_dir}/pipeline-completion-reminder.py"
                            ),
                        }
                    ],
                },
            ],
            "PostToolUse": [
                {
                    "matcher": "ExitPlanMode",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/pipeline-router.py",
                        }
                    ],
                },
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/post-edit-ruff.py",
                        },
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/ledger-writer.py",
                        },
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/control-surface-sync.py",
                        },
                    ],
                },
            ],
        },
    }


def setup_claude_hooks(project_root: Path, config: GzkitConfig | None = None) -> list[str]:
    """Set up Claude Code hooks for the project.

    Args:
        project_root: Project root directory.
        config: Optional configuration. Loaded if not provided.

    Returns:
        List of files created/updated.

    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    created = []

    hooks_path = project_root / config.paths.claude_hooks
    hooks_path.mkdir(parents=True, exist_ok=True)

    # Write hook scripts
    instruction_router_path = hooks_path / "instruction-router.py"
    _write_hook_file(instruction_router_path, _instruction_router_script(), executable=True)
    created.append(str(instruction_router_path.relative_to(project_root)))

    post_edit_ruff_path = hooks_path / "post-edit-ruff.py"
    _write_hook_file(post_edit_ruff_path, _post_edit_ruff_script(), executable=True)
    created.append(str(post_edit_ruff_path.relative_to(project_root)))

    plan_audit_gate_path = hooks_path / "plan-audit-gate.py"
    _write_hook_file(plan_audit_gate_path, _plan_audit_gate_script(), executable=True)
    created.append(str(plan_audit_gate_path.relative_to(project_root)))

    pipeline_router_path = hooks_path / "pipeline-router.py"
    _write_hook_file(pipeline_router_path, _pipeline_router_script(), executable=True)
    created.append(str(pipeline_router_path.relative_to(project_root)))

    pipeline_gate_path = hooks_path / "pipeline-gate.py"
    _write_hook_file(pipeline_gate_path, _pipeline_gate_script(), executable=True)
    created.append(str(pipeline_gate_path.relative_to(project_root)))

    pipeline_completion_reminder_path = hooks_path / "pipeline-completion-reminder.py"
    _write_hook_file(
        pipeline_completion_reminder_path,
        _pipeline_completion_reminder_script(),
        executable=True,
    )
    created.append(str(pipeline_completion_reminder_path.relative_to(project_root)))

    session_staleness_path = hooks_path / "session-staleness-check.py"
    _write_hook_file(session_staleness_path, _session_staleness_check_script(), executable=True)
    created.append(str(session_staleness_path.relative_to(project_root)))

    obpi_validator_path = hooks_path / "obpi-completion-validator.py"
    _write_hook_file(obpi_validator_path, _obpi_completion_validator_script(), executable=True)
    created.append(str(obpi_validator_path.relative_to(project_root)))

    ledger_writer_path = hooks_path / "ledger-writer.py"
    _write_hook_file(ledger_writer_path, _ledger_writer_script(), executable=True)
    created.append(str(ledger_writer_path.relative_to(project_root)))

    control_surface_sync_path = hooks_path / "control-surface-sync.py"
    _write_hook_file(control_surface_sync_path, _control_surface_sync_script(), executable=True)
    created.append(str(control_surface_sync_path.relative_to(project_root)))

    readme_path = hooks_path / "README.md"
    _write_hook_file(readme_path, _claude_hooks_readme())
    created.append(str(readme_path.relative_to(project_root)))

    # Write settings.json
    settings = generate_claude_settings(config)
    settings_path = project_root / config.paths.claude_settings
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")

    created.append(str(settings_path.relative_to(project_root)))

    return created
