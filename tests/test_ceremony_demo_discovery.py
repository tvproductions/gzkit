"""Ceremony demo discovery: only documented ``gz`` commands reach the walkthrough.

Two coupled contracts are pinned here:

- GHI #539 / REQ-0.0.63-02-01: a multi-line fenced construct is parsed as ONE
  logical command, never shredded per-physical-line. (The multi-line *parsing*
  guard proper lives in ``tests/test_brief_commands.py``; here it is observed
  through the discovery layer's registered-``gz``-verb filter.)
- Ceremony Rule #4 enforcement (ADR-0.0.74 demo-compliance class-fix):
  ``_commands_from_demo_sections`` REJECTS any command that is not a registered
  ``gz`` invocation — non-``gz`` commands (``python -c``, raw ``unittest``,
  shell pipes) and unregistered ``gz`` verbs alike. The walkthrough is the
  operator's product-demonstration surface and never a place for improvised
  invocations; the doctrine (Rule #4) ships with coupled enforcement at the
  discovery layer rather than relying on brief authors to self-police.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.ceremony_data import _commands_from_demo_sections, discover_demo_commands
from gzkit.traceability import covers

_FIXTURE = Path(__file__).parent / "fixtures" / "ceremony_demos" / "multiline_demo.md"


class TestCeremonyDemoDiscovery(unittest.TestCase):
    @covers("REQ-0.0.63-02-01")
    def test_registered_gz_verb_validation_preserved(self) -> None:
        commands = _commands_from_demo_sections([_FIXTURE])
        self.assertTrue(any(c.startswith("uv run gz status") for c in commands))

    def test_non_gz_demo_command_is_rejected(self) -> None:
        # The fixture's ``## Demo`` holds a registered ``gz status`` command and
        # a multi-line ``python -c`` construct. Only the gz command may surface —
        # the non-gz construct is rejected (Ceremony Rule #4), not passed through
        # and not shredded into per-line fragments.
        commands = _commands_from_demo_sections([_FIXTURE])
        self.assertEqual(commands, ["uv run gz status --json"], f"got {commands!r}")
        self.assertFalse(
            any("python -c" in c for c in commands),
            f"non-gz python -c leaked into the walkthrough: {commands!r}",
        )

    def test_non_gz_and_unregistered_gz_both_rejected(self) -> None:
        # A registered *product* gz verb survives; a non-gz command and a ``gz``
        # whose verb is not registered in the parser are both dropped — no
        # improvised or stale invocations reach the walkthrough. (The survivor
        # here is ``gz status`` rather than ``gz check`` because ``check`` is now
        # housekeeping-denied — see test_housekeeping_gz_verbs_dropped_from_demos.)
        brief = (
            "---\nid: OBPI-FIXTURE\n---\n\n## Demo\n\n```bash\n"
            "uv run gz status --json\n"
            "uv run gz definitely-not-a-real-verb --json\n"
            "ls -la\n"
            "```\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            brief_path = Path(tmp) / "OBPI-FIXTURE.md"
            brief_path.write_text(brief, encoding="utf-8")
            commands = _commands_from_demo_sections([brief_path])
        self.assertEqual(commands, ["uv run gz status --json"], f"got {commands!r}")

    def test_housekeeping_gz_verbs_dropped_from_demos(self) -> None:
        # arb/check/test/lint are construction housekeeping (Evidence Summary
        # Template §3b: Quality Evidence), NOT yielded product (§3a). Each is a
        # *registered* gz verb, so the pre-existing registered-verb filter passed
        # them straight into the Product Demo walkthrough — the GHI #427/#516 leak
        # (operator: "I ABSOLUTELY DO NOT NEED A UNIT TEST AS A DEMO PROOF"). None
        # may survive; a genuine product verb in the same block still does.
        brief = (
            "---\nid: OBPI-FIXTURE\n---\n\n## Demo\n\n```bash\n"
            "uv run gz arb ruff\n"
            "uv run gz arb step --name unittest -- uv run -m unittest -q\n"
            "uv run gz check\n"
            "uv run gz test\n"
            "uv run gz lint\n"
            "uv run gz status --json\n"
            "```\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            brief_path = Path(tmp) / "OBPI-FIXTURE.md"
            brief_path.write_text(brief, encoding="utf-8")
            commands = _commands_from_demo_sections([brief_path])
        self.assertEqual(commands, ["uv run gz status --json"], f"got {commands!r}")

    def test_validate_survives_as_product_demo(self) -> None:
        # ``validate`` is deliberately EXCLUDED from the housekeeping denylist: a
        # delivered ``gz validate --<scope>`` validator is the yielded product of
        # the ADR that ships it. This guards against an over-broad denylist that
        # would suppress the very demos GHI #516 exists to strengthen.
        brief = (
            "---\nid: OBPI-FIXTURE\n---\n\n## Demo\n\n```bash\n"
            "uv run gz validate --documents\n"
            "```\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            brief_path = Path(tmp) / "OBPI-FIXTURE.md"
            brief_path.write_text(brief, encoding="utf-8")
            commands = _commands_from_demo_sections([brief_path])
        self.assertEqual(commands, ["uv run gz validate --documents"], f"got {commands!r}")


class TestWalkthroughSurfacesRefusals(unittest.TestCase):
    """The walkthrough must be able to demonstrate a REFUSAL (GHI #738).

    ADR-0.34.0's thesis was that four authoring doors now refuse; its closeout
    walked 11 commands that were all positive assertions. For an ADR asserting
    fail-closed behavior, an all-green demo set is indistinguishable from the
    enforcement never having been built — the campaign § 4 enforcement-claim rule
    stopped at the test boundary and never reached the attestation surface.

    `## Fidelity Assertions` could already express a negative and is mandatory on
    every non-pool ADR (ADR-0.0.73 BI #4). These pin that the two surfaces now
    share one representation.
    """

    _ADR = (
        "# ADR-9.9.9-probe\n\n"
        "## Fidelity Assertions\n\n"
        "| Claim | Command | Expected exit |\n"
        "|-------|---------|---------------|\n"
        "| The door refuses | `uv run gz plan create p --kind foundation` | 1 |\n"
        "| The tree is clean | `uv run gz validate --taxonomy` | 0 |\n\n"
        "## Next\n"
    )

    def _discover(self, tmp: Path, briefs: list[Path]):
        adr = tmp / "ADR-9.9.9-probe.md"
        adr.write_text(self._ADR, encoding="utf-8")
        return discover_demo_commands(tmp, "ADR-9.9.9-probe", briefs, adr)

    def test_refusal_demo_reaches_the_walkthrough(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            demos = self._discover(Path(tmp), [])
        refusals = [d for d in demos if d.expected_exit != 0]
        self.assertEqual(len(refusals), 1, f"got {demos!r}")
        self.assertIn("--kind foundation", refusals[0].command)
        self.assertEqual(refusals[0].claim, "The door refuses")

    def test_positive_assertions_still_reach_the_walkthrough(self) -> None:
        """Negative control: the merge must not admit ONLY negatives."""
        with tempfile.TemporaryDirectory() as tmp:
            demos = self._discover(Path(tmp), [])
        self.assertIn(
            "uv run gz validate --taxonomy",
            [d.command for d in demos],
        )

    def test_duplicate_commands_collapse(self) -> None:
        """A gate cited by four briefs is one demo, not four.

        ADR-0.34.0's queue carried 11 entries for 5 distinct commands, reading as
        more verification coverage than it performed.
        """
        brief = (
            "## Demo\n\n```bash\nuv run gz validate --taxonomy\n```\n",
            "## Demo\n\n```bash\nuv run gz validate --taxonomy\n```\n",
        )
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for i, text in enumerate(brief):
                p = Path(tmp) / f"OBPI-{i}.md"
                p.write_text(text, encoding="utf-8")
                paths.append(p)
            demos = self._discover(Path(tmp), paths)
        commands = [d.command for d in demos]
        self.assertEqual(len(commands), len(set(commands)), f"duplicates survived: {commands!r}")

    def test_fidelity_claim_enriches_a_duplicate_rather_than_adding_one(self) -> None:
        """A brief demo and a fidelity row naming the same command are ONE demo.

        Otherwise merging the two surfaces would reintroduce the duplication the
        dedupe exists to remove.
        """
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "OBPI-0.md"
            p.write_text("## Demo\n\n```bash\nuv run gz validate --taxonomy\n```\n", "utf-8")
            demos = self._discover(Path(tmp), [p])
        matching = [d for d in demos if d.command == "uv run gz validate --taxonomy"]
        self.assertEqual(len(matching), 1, f"got {demos!r}")
        self.assertEqual(matching[0].claim, "The tree is clean")


if __name__ == "__main__":
    unittest.main()
