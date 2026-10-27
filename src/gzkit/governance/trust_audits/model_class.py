"""Model-class-only scope (GHI #1284).

`.gzkit/rules/model-selection.md` names Claude models by class (`haiku`, `sonnet`,
`opus`, `fable`) and resolves a class to a model at dispatch. A release-pinned ID
written into canon goes stale at the next model launch with nothing to notice:
the rule's own class-to-ID mapping line did, its `haiku` entry left at
`claude-haiku-4-5` one release after the re-sourcing pass that updated `opus`.
Operator ruling, 2026-10-26: "cleary we should use class of model, not specific
version."

This scope fails closed on a versioned Claude model ID in rule, skill or agent
canon. Placeholders such as `claude-<tier>-<n>` carry no version digit and pass.
Records that name the model which did a piece of work (ledger, handoffs, data
provenance fields, the card registry in `data/frontier_model_cards.json`) are
outside the scanned roots and stay exact.
"""

import re
from typing import TYPE_CHECKING

from gzkit.core.validation_rules import ValidationError

if TYPE_CHECKING:
    from pathlib import Path

SCAN_ROOTS = (".gzkit/rules", ".gzkit/skills", ".gzkit/agents")

# A family name followed by a version digit (`claude-opus-5-5`), or the older
# version-first shape (`claude-3-5-sonnet`).
_VERSIONED_MODEL_ID = re.compile(r"\bclaude-(?:(?:haiku|sonnet|opus|fable)-\d|\d)[\w.-]*")

_MESSAGE = (
    "Versioned model ID `{model_id}` in canon. Name the class (`haiku`, `sonnet`, "
    "`opus`, `fable`); the harness resolves a class to its current model "
    "(`.gzkit/rules/model-selection.md`, GHI #1284). Replace the ID with its class, "
    "then run `uv run gz validate --model-class-only`."
)


def audit_model_class_only(project_root: Path) -> list[ValidationError]:
    """Flag every versioned Claude model ID in rule, skill and agent canon.

    Returns:
        One finding per versioned ID, attributed to its `path:line`.

    """
    errors: list[ValidationError] = []
    for root in SCAN_ROOTS:
        for path in sorted((project_root / root).rglob("*")):
            if path.is_file():
                errors.extend(_scan_file(path, project_root))
    return errors


def _scan_file(path: Path, project_root: Path) -> list[ValidationError]:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    rel_path = path.relative_to(project_root).as_posix()
    return [
        ValidationError(
            type="model_class_only",
            artifact=f"{rel_path}:{lineno}",
            message=_MESSAGE.format(model_id=match.group(0)),
        )
        for lineno, line in enumerate(content.splitlines(), start=1)
        for match in _VERSIONED_MODEL_ID.finditer(line)
    ]
