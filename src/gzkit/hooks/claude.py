"""Claude Code hook generation and management.

Generates Claude hook settings for governance-safe pre/post edit automation.
"""

import json
from pathlib import Path
from textwrap import dedent

from gzkit.config import GzkitConfig
from gzkit.hooks.core import write_hook_script


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
            `/gz-obpi-pipeline` after plan approval for OBPI work.

            How it works:
              1. Reads `.claude/plans/.plan-audit-receipt.json`
              2. If the receipt exists, names an OBPI, and has verdict `PASS`,
                 emit a routing instruction on stdout directing the agent to
                 invoke `/gz-obpi-pipeline`
              3. If the receipt is absent, invalid, or not `PASS`, exit silently

            Exit codes:
              0 - Always (PostToolUse hooks should not block)
            \"\"\"

            import json
            import os
            import sys
            from pathlib import Path

            RECEIPT_FILE = ".plan-audit-receipt.json"


            def main() -> None:
                \"\"\"Route approved OBPI plans into the pipeline.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                cwd = input_data.get("cwd", os.getcwd())
                receipt_path = Path(cwd) / ".claude" / "plans" / RECEIPT_FILE
                if not receipt_path.exists():
                    sys.exit(0)

                try:
                    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    sys.exit(0)

                obpi_id = receipt.get("obpi_id", "")
                verdict = receipt.get("verdict", "")
                if not obpi_id or verdict != "PASS":
                    sys.exit(0)

                print(
                    f"OBPI plan approved: {obpi_id}\\n"
                    f"\\n"
                    f"REQUIRED: Execute the approved plan via the governance pipeline:\\n"
                    f"  /gz-obpi-pipeline {obpi_id}\\n"
                    f"\\n"
                    f"Do NOT implement directly; the pipeline preserves the required\\n"
                    f"verification, acceptance ceremony, and sync stages.\\n"
                    f"\\n"
                    f"If implementation is already done, use --from=verify or --from=ceremony."
                )
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

            RECEIPT_FILE = ".plan-audit-receipt.json"
            LEGACY_MARKER = ".pipeline-active.json"


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


            def load_json(path: Path) -> dict | None:
                \"\"\"Best-effort JSON reader for receipt and marker files.\"\"\"
                try:
                    return json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    return None


            def marker_matches(marker_path: Path, obpi_id: str) -> bool:
                \"\"\"Return whether a marker exists and matches the target OBPI.\"\"\"
                if not marker_path.exists():
                    return False
                marker = load_json(marker_path)
                return bool(marker and marker.get("obpi_id") == obpi_id)


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

                cwd_path = Path(input_data.get("cwd", os.getcwd())).resolve()
                plans_dir = cwd_path / ".claude" / "plans"
                receipt = load_json(plans_dir / RECEIPT_FILE)
                if not receipt:
                    sys.exit(0)

                obpi_id = receipt.get("obpi_id", "")
                verdict = receipt.get("verdict", "")
                if not obpi_id or verdict != "PASS":
                    sys.exit(0)

                obpi_marker = plans_dir / f".pipeline-active-{obpi_id}.json"
                if marker_matches(obpi_marker, obpi_id):
                    sys.exit(0)

                legacy_marker = plans_dir / LEGACY_MARKER
                if marker_matches(legacy_marker, obpi_id):
                    sys.exit(0)

                print(
                    f"BLOCKED: Pipeline not invoked for {obpi_id}.\\n"
                    f"\\n"
                    f"A plan-audit receipt exists but the governance pipeline has not\\n"
                    f"been started. Implementation writes to src/ and tests/ are gated\\n"
                    f"until the pipeline is invoked.\\n"
                    f"\\n"
                    f"REQUIRED: Invoke the pipeline:\\n"
                    f"  /gz-obpi-pipeline {obpi_id}\\n"
                    f"\\n"
                    f"If implementation is already complete, use:\\n"
                    f"  /gz-obpi-pipeline {obpi_id} --from=verify\\n",
                    file=sys.stderr,
                )
                sys.exit(2)


            if __name__ == "__main__":
                main()
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
            "- `instruction-router.py`",
            "  PreToolUse (`Write|Edit`) hook that auto-surfaces",
            "  `.github/instructions/*.instructions.md` constraints.",
            "- `plan-audit-gate.py`",
            "  PreToolUse (`ExitPlanMode`) hook that validates the latest",
            "  OBPI plan against `.claude/plans/.plan-audit-receipt.json`.",
            "- `pipeline-router.py`",
            "  PostToolUse (`ExitPlanMode`) hook that routes PASS receipts into",
            "  `gz-obpi-pipeline`.",
            "- `pipeline-gate.py`",
            "  PreToolUse (`Write|Edit`) hook that blocks `src/` and `tests/`",
            "  writes until the active pipeline marker exists.",
            "- `post-edit-ruff.py`",
            "  PostToolUse (`Write|Edit`) hook that runs `ruff check --fix`",
            "  and `ruff format` on edited Python files.",
            "- `ledger-writer.py`",
            "  PostToolUse (`Write|Edit`) hook that records governance",
            "  artifact edits via `gzkit.hooks.core.record_artifact_edit`.",
            "",
            "## Notes",
            "",
            "- The operator-facing `gz-plan-audit` skill and receipt contract are",
            "  ported under `ADR-0.12.0-obpi-pipeline-enforcement-parity`.",
            "- `plan-audit-gate.py`, `pipeline-router.py`, and",
            "  `pipeline-gate.py` are generated locally but not yet active in",
            "  `.claude/settings.json`.",
            "  Registration and ordering stay with `OBPI-0.12.0-06`.",
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
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Write|Edit",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/instruction-router.py",
                        }
                    ],
                }
            ],
            "PostToolUse": [
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
                    ],
                }
            ],
        }
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
    script_path = write_hook_script(project_root, "claude", config.paths.claude_hooks)
    created.append(str(script_path.relative_to(project_root)))

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
