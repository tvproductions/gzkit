"""Behave step definitions for gz justify complexity-hints integration (OBPI-0.0.30-05).

Sets up fixture OBPI briefs and environments for the three canonical
complexity-hints paths: hints injected, hints absent (no .py paths),
and engine-failure fail-open.

Reuses the canonical ``When I run the gz command "..."`` /
``Then the command exits with code N`` step pair from ``gz_steps.py``.

@covers REQ-0.0.30-05-01
@covers REQ-0.0.30-05-02
@covers REQ-0.0.30-05-03
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from behave import given, then

# Resolve the canonical project root (parent of features/) so the skill-amendment
# scenarios can read .gzkit/skills/gz-justify/SKILL.md regardless of the per-scenario
# tempdir cwd that environment.py sets up.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CANONICAL_SKILL = _PROJECT_ROOT / ".gzkit" / "skills" / "gz-justify" / "SKILL.md"
_VENDOR_MIRRORS = (
    _PROJECT_ROOT / ".claude" / "skills" / "gz-justify" / "SKILL.md",
    _PROJECT_ROOT / ".agents" / "skills" / "gz-justify" / "SKILL.md",
    _PROJECT_ROOT / ".github" / "skills" / "gz-justify" / "SKILL.md",
)

# CC = 5 — crosses advise (>=4) but not warn (>=7)
_ADVISE_SOURCE = """\
def advise_band(x):
    if x > 0:
        if x > 1:
            return 1
        elif x > 2:
            return 2
        elif x > 3:
            return 3
        else:
            return 4
    return 0
"""

_DISTILLED_DOC = """\
---
corpus_revision: 1
---

# Distilled complexity characteristics — fixture

## Metric: `radon_cc`

Across the corpus, synthetic distribution applies.

**Doctrinal frame:** Martin (Clean Code) — function decomposition signal.

### Practitioner-eye observation

Refactor signal: extract the responsibility seam and re-test.
"""


def _write_threshold_table(cwd: Path, distilled_path: Path) -> None:
    rule_dir = cwd / ".gzkit" / "rules"
    rule_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "corpus_revision": 1,
        "citation": {
            "distilled_characteristics_path": distilled_path.relative_to(cwd).as_posix(),
            "section_anchor": "radon-cc",
            "corpus_revision": 1,
        },
        "bands": [
            {
                "metric": "radon_cc",
                "corpus_percentile": 75,
                "absolute_number": 4.0,
                "trigger_semantic": "advise",
            },
            {
                "metric": "radon_cc",
                "corpus_percentile": 90,
                "absolute_number": 7.0,
                "trigger_semantic": "warn",
            },
            {
                "metric": "radon_cc",
                "corpus_percentile": 95,
                "absolute_number": 11.0,
                "trigger_semantic": "block",
            },
        ],
    }
    (rule_dir / "complexity-thresholds.json").write_text(json.dumps(data), encoding="utf-8")


def _write_obpi_brief(cwd: Path, identifier: str, allowed_paths_lines: list[str]) -> None:
    brief_dir = cwd / "docs/design/adr/foundation/ADR-0.99.1-fixture/obpis"
    brief_dir.mkdir(parents=True, exist_ok=True)
    if allowed_paths_lines:
        allowed = "\n".join(f"- {p}" for p in allowed_paths_lines)
    else:
        allowed = "- docs/user/runbook.md"
    brief_text = (
        "---\n"
        f"id: {identifier}-fixture\n"
        "parent: ADR-0.99.1\n"
        "lane: Lite\n"
        "status: Draft\n"
        "---\n\n"
        f"# {identifier}: Fixture brief\n\n"
        "## Allowed Paths\n\n"
        f"{allowed}\n\n"
        "## Objective\n\nFixture brief for complexity-hints integration BDD scenarios.\n"
    )
    (brief_dir / f"{identifier}-fixture.md").write_text(brief_text, encoding="utf-8")


@given("a justify fixture with .py allowed paths and an advise-band Python source")
def step_fixture_with_py_paths_and_crossings(_context) -> None:
    cwd = Path.cwd()
    complexity_dir = cwd / "docs/governance/complexity"
    complexity_dir.mkdir(parents=True, exist_ok=True)
    distilled_path = complexity_dir / "distilled-characteristics-fixture.md"
    distilled_path.write_text(_DISTILLED_DOC, encoding="utf-8")
    _write_threshold_table(cwd, distilled_path)
    subject = cwd / "subject.py"
    subject.write_text(_ADVISE_SOURCE, encoding="utf-8")
    _write_obpi_brief(cwd, "OBPI-0.99.1-01", ["subject.py"])


@given("a justify fixture with no .py allowed paths")
def step_fixture_without_py_paths(_context) -> None:
    cwd = Path.cwd()
    _write_obpi_brief(cwd, "OBPI-0.99.1-02", ["docs/user/runbook.md"])


@given("a justify fixture with .py allowed paths but engine unavailable")
def step_fixture_with_py_paths_engine_unavailable(_context) -> None:
    cwd = Path.cwd()
    subject = cwd / "subject.py"
    subject.write_text(_ADVISE_SOURCE, encoding="utf-8")
    # Intentionally do NOT create the threshold table — engine.analyze will fail.
    _write_obpi_brief(cwd, "OBPI-0.99.1-03", ["subject.py"])


@given("the canonical gz-justify skill amendment is in place")
def step_skill_amendment_in_place(context) -> None:
    """Read canonical SKILL.md once and stash content/frontmatter on context."""
    canonical = _CANONICAL_SKILL.read_text(encoding="utf-8")
    end = canonical.find("\n---\n", 4)
    frontmatter = yaml.safe_load(canonical[4:end])
    context._skill_canonical = canonical
    context._skill_frontmatter = frontmatter


@then('the gz-justify skill version is at least "{version}"')
def step_skill_version_at_least(context, version: str) -> None:
    """Assert the amendment baseline has not regressed.

    The REQ requires the amendment to have landed with a *bumped* version, not
    to sit at one exact string forever: pinning equality made every later edit
    to the skill break this scenario (observed 2026-07-21, when a staleness
    repair bumped 6.1.0 -> 6.1.1). Compare semver order so the assertion
    tracks the requirement instead of a snapshot.
    """
    metadata = context._skill_frontmatter.get("metadata", {})
    actual = metadata.get("skill-version")
    assert actual is not None, "canonical gz-justify SKILL.md declares no metadata.skill-version"

    def parse(value: str) -> tuple[int, ...]:
        return tuple(int(part) for part in str(value).split("."))

    assert parse(actual) >= parse(version), (
        f"skill-version {actual!r} is below the amendment baseline {version!r}"
    )


@then('the gz-justify skill body contains "{token}"')
def step_skill_body_contains(context, token: str) -> None:
    assert token in context._skill_canonical, f"skill body missing required token {token!r}"


@then("the gz-justify vendor mirrors are byte-identical to the canonical")
def step_vendor_mirrors_byte_identical(context) -> None:
    canonical = context._skill_canonical
    for mirror in _VENDOR_MIRRORS:
        assert mirror.exists(), f"vendor mirror missing: {mirror}"
        mirror_text = mirror.read_text(encoding="utf-8")
        assert mirror_text == canonical, f"vendor mirror diverges from canonical: {mirror}"
