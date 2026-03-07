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
            "- `post-edit-ruff.py`",
            "  PostToolUse (`Write|Edit`) hook that runs `ruff check --fix`",
            "  and `ruff format` on edited Python files.",
            "- `ledger-writer.py`",
            "  PostToolUse (`Write|Edit`) hook that records governance",
            "  artifact edits via `gzkit.hooks.core.record_artifact_edit`.",
            "",
            "## Notes",
            "",
            "- Blocking canonical hooks are intentionally deferred until compatibility",
            "  adaptation is defined under `ADR-0.9.0-airlineops-surface-breadth-parity`.",
            "- See intake matrix:",
            "  `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/",
            "claude-hooks-intake-matrix.md`",
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
