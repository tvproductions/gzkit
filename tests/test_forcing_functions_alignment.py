"""Forcing functions must have a channel end to end (GHI #719).

`gz-adr-create` SKILL.md declares seven forcing-function techniques
non-negotiable, plus a closing question it says to "always ask last". They were
asked in practice and the answers written to the interview JSON — but the ADR
question set had no field for them, the ADR template had no section, and nothing
read the file. 2 of 25 interview records captured them, under an invented
`forcing_functions` key; the other 23 lost the reasoning entirely.

These tests pin the chain the alignment restored: declared -> asked -> rendered
-> scaffolded. Each asserts a link that, if broken, silently drops operator-
attested design reasoning rather than failing loudly.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.commands.common import GzCliError
from gzkit.commands.interview_cmd import _load_answers_from_file
from gzkit.interview import get_interview_questions
from gzkit.templates import render_template
from gzkit.templates.author_prompts import AUTHOR_PROMPTS, PERSONA_PROMPT

PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: The seven techniques `gz-adr-create` SKILL.md § Forcing Functions declares
#: non-negotiable, plus its closing question. Spelled here so a silent deletion
#: from the question set fails rather than shrinking the contract unnoticed.
FORCING_FUNCTION_IDS = (
    "pre_mortem",
    "wwhtbt",
    "constraint_archaeology",
    "assumption_surfacing",
    "operator_2am",
    "reversibility",
    "scope_minimization",
    "downstream_adrs",
)


class TestInterviewAsksThem(unittest.TestCase):
    def test_every_declared_forcing_function_has_an_interview_question(self) -> None:
        asked = {q.id for q in get_interview_questions("adr")}
        self.assertEqual(
            set(FORCING_FUNCTION_IDS) - asked,
            set(),
            "a forcing function the skill declares non-negotiable has no interview field, "
            "so its answer has nowhere to go",
        )

    def test_they_are_grouped_under_one_section(self) -> None:
        # Section drives where the answer lands in the rendered ADR; a stray section
        # name would scatter the reasoning instead of collecting it.
        sections = {
            q.section for q in get_interview_questions("adr") if q.id in FORCING_FUNCTION_IDS
        }
        self.assertEqual(sections, {"Forcing Functions"})


def _render_adr(**overrides: str) -> str:
    """Render the ADR template the way a scaffolding caller does."""
    variables: dict[str, str] = dict(AUTHOR_PROMPTS["adr"])
    variables["persona"] = PERSONA_PROMPT
    variables.update(
        id="ADR-0.99.0-fixture",
        title="Fixture",
        status="Draft",
        kind="feature",
        semver="0.99.0",
        lane="lite",
        parent="PRD-GZKIT-1.0.0",
        date="2026-08-06",
        checklist="1. item",
        why_foundation_tier="",
        decomposition_scorecard="n/a",
        fidelity_assertions="n/a",
        evidence="n/a",
    )
    variables.update(overrides)
    return render_template("adr", **variables)


class TestTemplateRendersThem(unittest.TestCase):
    """Render behavior, not template text: an answer must reach the document."""

    def test_each_answer_reaches_the_rendered_adr(self) -> None:
        # Asserting the template *contains* `{pre_mortem}` would pass on a slot that
        # is never substituted. Rendering a distinguishable value per function and
        # finding it in the output proves the slot is wired, which is the behavior.
        sentinels = {fid: f"SENTINEL-{fid.upper()}" for fid in FORCING_FUNCTION_IDS}
        rendered = _render_adr(**sentinels)
        dropped = [fid for fid, token in sentinels.items() if token not in rendered]
        self.assertEqual(
            dropped, [], "answers to these forcing functions never reach the rendered ADR"
        )

    def test_scaffold_render_leaves_no_unsubstituted_token(self) -> None:
        # `render_template` raises on a missing variable, so this guards the other
        # direction: a slot whose scaffold default is absent from AUTHOR_PROMPTS.
        rendered = _render_adr()
        for fid in FORCING_FUNCTION_IDS:
            with self.subTest(forcing_function=fid):
                self.assertNotIn(f"{{{fid}}}", rendered)


class TestExistingRecordsRemainReadable(unittest.TestCase):
    def test_every_interview_record_survives_the_loader(self) -> None:
        # The loader rejects unknown keys, so this is also what proves no record still
        # carries the superseded nested `forcing_functions` shape — a reappearance
        # would be an unknown key and would fail here rather than needing its own
        # filesystem probe.
        records = sorted(Path(PROJECT_ROOT / "docs" / "design" / "adr").rglob("*interview*.json"))
        self.assertTrue(records, "no interview records found — the survey target moved")
        for path in records:
            with self.subTest(record=path.name):
                _load_answers_from_file(str(path), "adr")

    def test_a_nested_forcing_functions_key_is_rejected(self) -> None:
        # Pins the mechanism the test above relies on: the superseded shape does not
        # quietly load. Without this, "every record loads" could pass because the
        # loader had become permissive rather than because the records were migrated.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy-interview.json"
            path.write_text(
                json.dumps({"id": "ADR-0.1.0-x", "forcing_functions": {"pre_mortem": "…"}}),
                encoding="utf-8",
            )
            with self.assertRaises(GzCliError):
                _load_answers_from_file(str(path), "adr")


if __name__ == "__main__":
    unittest.main()
