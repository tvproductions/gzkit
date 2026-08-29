"""BDD steps for ``gz justify`` (OBPI-0.0.19-05).

Mocks the ``gh issue view`` subprocess (used by the GHI resolver),
materializes fixture OBPI briefs in the per-scenario tempdir, and
authors complete/incomplete/malformed walkthrough fixtures used by the
``validate`` subverb scenarios.

Reuses the canonical ``When I run the gz command "..."`` /
``Then the command exits with code N`` step pair from ``gz_steps.py``;
this module only adds justify-specific Given/Then steps.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

from behave import given, then

from gzkit.justify.walkthrough import SECTION_HEADINGS, SECTION_PROMPTS


@given('gh issue view returns fixture body for "{anchor}"')
def step_mock_gh_issue_view(_context, anchor: str) -> None:
    number = anchor.replace("GHI-", "").replace("#", "")
    payload = {
        "number": int(number),
        "title": f"Fixture issue {number}",
        "body": "Fixture issue body for justify scenario.",
        "labels": [{"name": "defect"}],
        "author": {"login": "fixture-bot"},
    }
    stdout = json.dumps(payload)

    def fake_run_exec(cmd, cwd, timeout=None):  # noqa: ARG001
        if len(cmd) >= 2 and cmd[0] == "gh" and cmd[1] == "issue":
            return (0, stdout, "")
        return (1, "", "fake_run_exec: unexpected command")

    # Started and deliberately NOT stopped here: `after_scenario` calls
    # `mock.patch.stopall()`, which binds every patcher's lifetime to the
    # scenario that started it (GHI #916). A local teardown would be a second
    # owner of the same obligation, and the one this module used to carry was
    # never wired -- it read as handled while handling nothing (GHI #918).
    mock.patch("gzkit.justify.anchors.run_exec", side_effect=fake_run_exec).start()


@given('a fixture OBPI brief for "{identifier}"')
def step_fixture_obpi_brief(_context, identifier: str) -> None:
    brief_dir = Path("docs/design/adr/foundation/ADR-0.99.0-fixture/obpis")
    brief_dir.mkdir(parents=True, exist_ok=True)
    brief = brief_dir / f"{identifier}-fixture.md"
    brief.write_text(
        "---\n"
        f"id: {identifier}-fixture\n"
        "parent: ADR-0.99.0\n"
        "lane: Lite\n"
        "status: Draft\n"
        "---\n\n"
        f"# {identifier}: Fixture brief\n\n"
        "## Objective\n\nFixture content for behave OBPI anchor scenario.\n\n"
        "## Acceptance Criteria\n\n"
        "- [ ] REQ-0.99.0-01-01: fixture criterion.\n",
        encoding="utf-8",
    )


def _render_complete_walkthrough(anchor_id: str) -> str:
    lines = [
        "---",
        f"anchor_id: {anchor_id}",
        "anchor_kind: draft",
        "generated_at: 2026-04-22T05:15:00+00:00",
        "scaffold_version: 1",
        "---",
        "",
        f"# Walkthrough: {anchor_id}",
        "",
    ]
    for ordinal, heading in enumerate(SECTION_HEADINGS, start=1):
        lines.extend(
            [
                f"## {ordinal}. {heading}",
                "",
                f"**Prompt:** *{SECTION_PROMPTS[ordinal]}*",
                "",
                "**Evidence:**",
                "",
                "- _(no citations for this section)_",
                "",
                f"Filled reasoning for section {ordinal}.",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def _render_incomplete_walkthrough(anchor_id: str) -> str:
    text = _render_complete_walkthrough(anchor_id)
    return text.replace(
        "Filled reasoning for section 5.",
        "_[To be filled]_",
        1,
    )


@given('a complete justify walkthrough fixture at "{path}"')
def step_complete_walkthrough(_context, path: str) -> None:
    Path(path).write_text(_render_complete_walkthrough("GHI-9999"), encoding="utf-8")


@given('an incomplete justify walkthrough fixture at "{path}"')
def step_incomplete_walkthrough(_context, path: str) -> None:
    Path(path).write_text(_render_incomplete_walkthrough("GHI-9999"), encoding="utf-8")


@given('a malformed justify walkthrough fixture at "{path}"')
def step_malformed_walkthrough(_context, path: str) -> None:
    Path(path).write_text(
        "this is not a walkthrough\nno frontmatter, no headings\n",
        encoding="utf-8",
    )


@then('a scaffold artifact is written under "{relative_dir}"')
def step_scaffold_written(_context, relative_dir: str) -> None:
    artifacts = list(Path(relative_dir).glob("*.md"))
    assert artifacts, f"no scaffold artifact written under {relative_dir!r}"


@then("the output names an unfilled section ordinal")
def step_output_names_unfilled(context) -> None:
    output = getattr(context, "output", "")
    assert any(token in output for token in ("section", "ordinal", "unfilled", "5")), (
        f"validate output should name an unfilled section; got: {output!r}"
    )
