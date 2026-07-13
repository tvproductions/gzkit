"""Hermetic structural validator for ``CHANGELOG.md`` (GHI #685).

Asserts the changelog conforms to ``.gzkit/templates/changelog.md``: version
headers are ``## [Unreleased]`` or ``## vX.Y.Z (YYYY-MM-DD)`` (SemVer + ISO
date), section headings are drawn from the closed Good-Docs category set, and
every entry cites ``GHI #N`` (Release highlights are prose summaries and are
exempt).

Offline and deterministic by contract: the closed-GHI *coverage* half of the
enforcement (every closed-since-tag GHI appears) needs the network and lives in
``gz-patch-release``, not here. See ``.gzkit/rules/changelog-release-notes.md``
§ Enforcement for the hermeticity split.
"""

import re
from pathlib import Path

from gzkit.core.validation_rules import ValidationError

_ALLOWED_CATEGORIES = frozenset(
    {
        "Release highlights",
        "Added",
        "Changed",
        "Deprecated",
        "Fixed",
        "Security",
        "Breaking changes",
    }
)

# Categories whose entries are prose summaries, not change records — exempt from
# the GHI-citation requirement.
_CITATION_EXEMPT = frozenset({"Release highlights"})

_VERSION_RE = re.compile(r"^## (?:\[Unreleased\]|v?\d+\.\d+\.\d+ \(\d{4}-\d{2}-\d{2}\))$")
_GHI_RE = re.compile(r"GHI #\d+")


def validate_changelog(project_root: Path) -> list[ValidationError]:
    """Validate ``CHANGELOG.md`` structure. Returns errors (empty if conforming)."""
    path = project_root / "CHANGELOG.md"
    if not path.is_file():
        return [
            ValidationError(
                type="changelog",
                artifact="CHANGELOG.md",
                message="CHANGELOG.md not found (required by the changelog-release-notes rule)",
            )
        ]

    errors: list[ValidationError] = []
    in_body = False  # True once the first version header is seen
    current_category: str | None = None

    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.startswith("## "):
            in_body = True
            current_category = None
            if not _VERSION_RE.match(line):
                errors.append(
                    ValidationError(
                        type="changelog",
                        artifact="CHANGELOG.md",
                        field="version",
                        message=(
                            f"Line {lineno}: version header must be '## [Unreleased]' or "
                            f"'## vX.Y.Z (YYYY-MM-DD)': {line!r}"
                        ),
                    )
                )
            continue

        if line.startswith("### "):
            current_category = line[len("### ") :].strip()
            if current_category not in _ALLOWED_CATEGORIES:
                errors.append(
                    ValidationError(
                        type="changelog",
                        artifact="CHANGELOG.md",
                        field="category",
                        message=(
                            f"Line {lineno}: '{current_category}' is not an allowed changelog "
                            f"category {sorted(_ALLOWED_CATEGORIES)}"
                        ),
                    )
                )
            continue

        # Top-level entry bullets inside an allowed, non-exempt category.
        if (
            in_body
            and line.startswith("- ")
            and current_category in _ALLOWED_CATEGORIES
            and current_category not in _CITATION_EXEMPT
            and not _GHI_RE.search(line)
        ):
            errors.append(
                ValidationError(
                    type="changelog",
                    artifact="CHANGELOG.md",
                    field="ghi-citation",
                    message=f"Line {lineno}: changelog entry must cite 'GHI #N': {line!r}",
                )
            )

    return errors
