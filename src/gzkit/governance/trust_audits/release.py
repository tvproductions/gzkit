"""Release-discipline trust audits.

* ``audit_version_release`` — every ``pyproject.toml`` version bump must
  have a matching ``vX.Y.Z`` git tag (or a ``docs/releases/{PATCH,RELEASE}-vX.Y.Z.md``
  manifest in flight). GHI #205 / GHI #217 / GHI #739.
* ``audit_advisory_scorecard`` — every rule under ``.gzkit/rules/`` must
  appear in ``docs/governance/advisory-rules-audit.md`` so the scorecard
  remains a complete index. GHI #212.
"""

from __future__ import annotations

import re
from pathlib import Path

from gzkit.validate import ValidationError

#: Filename prefixes accepted as in-flight release evidence (GHI #217, GHI #739).
#: ``PATCH-`` is written by ``gz patch release``; ``RELEASE-`` by ``gz closeout``,
#: whose bumps are minor. Both denote the same window — between the bump commit
#: and ``gh release create`` — so both are equivalent evidence. The prefix names
#: the ceremony that bumped, never a different kind of proof.
IN_FLIGHT_MANIFEST_PREFIXES: tuple[str, ...] = ("PATCH", "RELEASE")


def in_flight_manifest_path(project_root: Path, version: str, prefix: str = "RELEASE") -> Path:
    """Return the manifest path a bump of *version* must file to stay syncable.

    Single source for the path contract shared by the writers
    (``gz patch release``, ``gz closeout``) and the audit that reads it.
    """
    return project_root / "docs" / "releases" / f"{prefix}-v{version}.md"


def audit_version_release(project_root: Path) -> list[ValidationError]:
    """Fail if ``pyproject.toml`` version has no matching ``vX.Y.Z`` git tag.

    Every version bump is a release (CLAUDE.md local rule 11). This audit
    compares the declared pyproject version against the local git-tag set;
    if the bump landed without a tag, the release step was skipped.

    Per GHI #217, the audit also accepts an in-flight release manifest under
    ``docs/releases/`` as equivalent evidence, written before the bump commit
    is attempted, so it satisfies the audit during the brief window between
    the commit and ``gh release create`` (which creates the tag).

    Per GHI #739 the lookup accepts both ``IN_FLIGHT_MANIFEST_PREFIXES``.
    ``PATCH-`` alone was hardcoded here, which had two consequences: minor
    releases from ``gz closeout`` had to file an artifact mislabelled as a
    patch (``PATCH-v0.30.0.md``, ``PATCH-v0.34.0.md``), and because
    ``gz closeout`` wrote no manifest at all, its bump made ``gz test`` red
    while the ceremony's own Step 10 ran that gate before creating the tag —
    a deadlock on every minor release.
    """
    import subprocess  # noqa: PLC0415

    pyproject = project_root / "pyproject.toml"
    if not pyproject.is_file():
        return []
    version = _read_pyproject_version(pyproject)
    if version is None:
        return []
    expected = f"v{version}"
    if any(
        in_flight_manifest_path(project_root, version, prefix).is_file()
        for prefix in IN_FLIGHT_MANIFEST_PREFIXES
    ):
        return []
    try:
        result = subprocess.run(
            ["git", "tag", "--list", "v*"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            errors="replace",
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
                artifact=rule_md.relative_to(project_root).as_posix(),
                message=(
                    f"Rule file `{rule_md.name}` is not referenced by the advisory "
                    "scorecard. Add a row to `docs/governance/advisory-rules-audit.md` "
                    "with a score (Mechanical / Promotable / Judgment / Ambiguous)."
                ),
            )
        )
    return errors
