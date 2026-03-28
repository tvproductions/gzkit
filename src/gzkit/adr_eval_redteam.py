"""Red-team prompt composition and result parsing for ADR evaluation.

Follows the compose/parse pattern from ``pipeline_runtime.py``.  The CLI
composes the prompt; the agent dispatches it to a subagent and feeds the
output back through ``parse_redteam_result()``.
"""

import json
import re
from pathlib import Path

from gzkit.adr_eval import RedTeamChallengeResult

# The 10 canonical challenge names from the evaluation framework.
CHALLENGE_NAMES: list[str] = [
    "So What?",
    "Scope",
    "Alternative",
    "Dependency",
    "Gold Standard",
    "Timeline",
    "Evidence",
    "Consumer",
    "Regression",
    "Parity",
]

_RESULT_JSON_RE = re.compile(r"```json\s*([\s\S]*?)```")


def load_framework_redteam_prompt(skill_assets_dir: Path) -> str:
    """Load the Part 4 red-team prompt from ADR_EVALUATION_FRAMEWORK.md.

    Extracts the text between ``### RED-TEAM PROMPT`` and the next ``---``
    or end of file.
    """
    framework_path = skill_assets_dir / "ADR_EVALUATION_FRAMEWORK.md"
    if not framework_path.exists():
        msg = f"Evaluation framework not found: {framework_path}"
        raise FileNotFoundError(msg)

    content = framework_path.read_text(encoding="utf-8")
    match = re.search(
        r"### RED-TEAM PROMPT\s*```text\s*([\s\S]*?)```",
        content,
    )
    if not match:
        msg = "Could not extract RED-TEAM PROMPT from framework"
        raise ValueError(msg)
    return match.group(1).strip()


def compose_adr_redteam_prompt(
    adr_content: str,
    obpi_contents: list[tuple[str, str]],
    framework_prompt: str,
) -> str:
    """Build the red-team challenge prompt for subagent dispatch.

    Args:
        adr_content: Full markdown of the ADR document.
        obpi_contents: List of ``(obpi_id, markdown_content)`` tuples.
        framework_prompt: The Part 4 prompt template from the framework.

    Returns:
        Complete prompt string ready for subagent dispatch.

    """
    obpi_section = ""
    for obpi_id, content in obpi_contents:
        obpi_section += f"\n\n--- OBPI: {obpi_id} ---\n\n{content}"

    result_schema = json.dumps(
        {
            "challenges": [
                {
                    "challenge_number": 1,
                    "challenge_name": "So What?",
                    "passed": True,
                    "notes": "string",
                }
            ]
        },
        indent=2,
    )

    return (
        f"{framework_prompt}\n\n"
        f"ADR DOCUMENT:\n\n{adr_content}\n\n"
        f"OBPI BRIEFS:\n{obpi_section}\n\n"
        f"RESPONSE FORMAT: Return a JSON code block with this schema:\n"
        f"```json\n{result_schema}\n```\n\n"
        f"Each challenge object must have: challenge_number (1-10), "
        f"challenge_name, passed (boolean), notes (string).\n"
        f"All 10 challenges must be present. N/A is not acceptable."
    )


def parse_redteam_result(
    reviewer_output: str,
) -> list[RedTeamChallengeResult] | None:
    """Extract structured red-team results from reviewer subagent output.

    Returns ``None`` if parsing fails.
    """
    match = _RESULT_JSON_RE.search(reviewer_output)
    if not match:
        return None

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None

    challenges = data if isinstance(data, list) else data.get("challenges")
    if not isinstance(challenges, list):
        return None

    results: list[RedTeamChallengeResult] = []
    for item in challenges:
        if not isinstance(item, dict):
            return None
        try:
            results.append(
                RedTeamChallengeResult(
                    challenge_number=int(item["challenge_number"]),
                    challenge_name=str(item.get("challenge_name", "")),
                    passed=bool(item["passed"]),
                    notes=str(item.get("notes", "")),
                )
            )
        except (KeyError, TypeError, ValueError):
            return None

    return results if len(results) == 10 else None
