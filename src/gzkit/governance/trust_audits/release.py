"""Release-discipline trust audits.

* ``audit_version_release`` — every ``pyproject.toml`` version bump must
  have a matching ``vX.Y.Z`` git tag (or a ``docs/releases/PATCH-vX.Y.Z.md``
  manifest in flight). GHI #205 / GHI #217.
* ``audit_advisory_scorecard`` — every rule under ``.gzkit/rules/`` must
  appear in ``docs/governance/advisory-rules-audit.md`` so the scorecard
  remains a complete index. GHI #212.
"""

from __future__ import annotations

import re
from pathlib import Path

from gzkit.validate import ValidationError


def audit_version_release(project_root: Path) -> list[ValidationError]:
    """Fail if ``pyproject.toml`` version has no matching ``vX.Y.Z`` git tag.

    Every version bump is a release (CLAUDE.md local rule 11). This audit
    compares the declared pyproject version against the local git-tag set;
    if the bump landed without a tag, the release step was skipped.

    Per GHI #217, the audit also accepts an in-flight release manifest at
    ``docs/releases/PATCH-v{version}.md`` as equivalent evidence. The
    manifest is written by ``gz patch release`` before the bump commit is
    attempted, so it satisfies the audit during the brief window between
    the commit and ``gh release create`` (which creates the tag).
    """
    import subprocess  # noqa: PLC0415

    pyproject = project_root / "pyproject.toml"
    if not pyproject.is_file():
        return []
    version = _read_pyproject_version(pyproject)
    if version is None:
        return []
    expected = f"v{version}"
    manifest = project_root / "docs" / "releases" / f"PATCH-{expected}.md"
    if manifest.is_file():
        return []
    try:
        result = subprocess.run(
            ["git", "tag", "--list", "v*"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    tags = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    if expected in tags:
        return []
    return [
        ValidationError(
            type="version_release",
            artifact=f"pyproject.toml::version={version}",
            message=(
                f"Declared version `{version}` has no matching git tag `{expected}`. "
                "Every version bump is a release (CLAUDE.md local rule 11) — "
                f"create one via `gh release create {expected} --target main "
                f'--title "{expected}" --latest --notes "..."`.'
            ),
        )
    ]


def _read_pyproject_version(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("version"):
            continue
        match = re.match(r'version\s*=\s*"([^"]+)"', stripped)
        if match:
            return match.group(1)
    return None


def audit_advisory_scorecard(project_root: Path) -> list[ValidationError]:
    """Every rule file under ``.gzkit/rules/`` must appear in the scorecard.

    The scorecard at ``docs/governance/advisory-rules-audit.md`` catalogues
    rules and scores their enforceability. When a new rule file lands
    without a scorecard entry, this audit flags the drift so the scorecard
    stays a complete index (trust-doctrine §3 — doctrine that survives agent
    rotation is doctrine that's mechanical).
    """
    scorecard = project_root / "docs" / "governance" / "advisory-rules-audit.md"
    rules_root = project_root / ".gzkit" / "rules"
    if not scorecard.is_file() or not rules_root.is_dir():
        return []
    scorecard_text = scorecard.read_text(encoding="utf-8").lower()
    errors: list[ValidationError] = []
    for rule_md in sorted(rules_root.glob("*.md")):
        stem = rule_md.stem.lower()
        if stem in scorecard_text:
            continue
        errors.append(
            ValidationError(
                type="advisory_scorecard",
                artifact=str(rule_md.relative_to(project_root)),
                message=(
                    f"Rule file `{rule_md.name}` is not referenced by the advisory "
                    "scorecard. Add a row to `docs/governance/advisory-rules-audit.md` "
                    "with a score (Mechanical / Promotable / Judgment / Ambiguous)."
                ),
            )
        )
    return errors
