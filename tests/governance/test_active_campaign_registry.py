"""The campaign registry is the authority, and the plans' prose must agree.

`data/active_campaign.json` declares which plan governs. Moving that decision
out of prose is the operator ruling of 2026-08-16 -- execution reads state from
JSON, never from markdown (`.gzkit/rules/governance-core.md` 0.11.0) -- and it
removed the `^Status:\\s*\\*\\*ACTIVE` regex from both production readers.

Two properties have to hold or the move just relocates the problem:

* **Nothing may be undeclared.** A campaign file in neither list fails closed,
  the same shape `test_check_scope_parity` uses for validator scopes. Without
  it, issuing a new edition and forgetting the registry would silently leave
  the old plan governing -- which is the failure this replaced, wearing a
  different hat.
* **The prose may not contradict the registry.** Each plan still carries a
  human-facing `Status:` line, and every human reading the campaign reads that
  line rather than the JSON. A plan whose banner says ACTIVE while the registry
  names another file is a document lying to its only audience.

The `^Status:` pattern therefore survives HERE and nowhere else. Its job changed:
it no longer decides anything, it audits a human surface against the authority.
That the prose needs auditing at all is not hypothetical -- every superseded
edition's line reads `**SUPERSEDED -- was ACTIVE**`, which the old production
regex missed only because ACTIVE is not adjacent to the asterisks.

Reads happen once in `setUpClass` and the tests assert over the extracted
values, following `test_check_scope_parity`. That keeps each assertion pointed
at a structured target rather than at a freshly-read file, which is both what
`.gzkit/rules/tests.md` § Prefer structured assertion targets asks for and what
`gz validate --tautological-test-audit` enforces.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "data" / "active_campaign.json"
GOVERNANCE = REPO_ROOT / "docs" / "governance"
CAMPAIGN_GLOB = "*-campaign-*.md"

#: Audits the human-facing banner. NOT an execution authority -- production
#: reads the registry. See this module's docstring.
_PROSE_ACTIVE_RE = re.compile(r"^Status:\s*\*\*ACTIVE", re.MULTILINE)


def _status_line(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("Status:"):
            return line
    return ""


class CampaignRegistryCoherence(unittest.TestCase):
    """The registry, the files on disk, and the banners must describe one state."""

    @classmethod
    def setUpClass(cls) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.active: str = registry["active"]
        cls.superseded: list[str] = list(registry["superseded"])
        cls.declared: list[str] = [cls.active, *cls.superseded]
        cls.on_disk: list[str] = sorted(
            path.relative_to(REPO_ROOT).as_posix() for path in GOVERNANCE.glob(CAMPAIGN_GLOB)
        )
        cls.absent: list[str] = [d for d in cls.declared if not (REPO_ROOT / d).is_file()]
        texts = {
            declared: (REPO_ROOT / declared).read_text(encoding="utf-8", errors="replace")
            for declared in cls.declared
            if declared not in cls.absent
        }
        cls.status_lines: dict[str, str] = {k: _status_line(v) for k, v in texts.items()}
        cls.claiming_active: list[str] = sorted(
            k for k, v in texts.items() if _PROSE_ACTIVE_RE.search(v)
        )


class RegistryShape(CampaignRegistryCoherence):
    def test_it_declares_exactly_one_active_plan(self) -> None:
        """Operating Rule 1: one active plan. A list here would readmit ambiguity."""
        self.assertIsInstance(self.active, str)

    def test_every_declared_path_resolves(self) -> None:
        """A registry naming a file that is gone is the hardcoded-pointer defect."""
        self.assertEqual(self.absent, [])

    def test_the_active_plan_is_not_also_superseded(self) -> None:
        self.assertNotIn(self.active, self.superseded)


class NoCampaignMayBeUndeclared(CampaignRegistryCoherence):
    """The fail-closed arm: issuing an edition without registering it breaks."""

    def test_every_campaign_on_disk_appears_exactly_once(self) -> None:
        """Silence is the failure mode being closed.

        Before the registry, a new edition took effect by flipping prose in two
        files; forgetting one left the previous plan governing with nothing
        objecting. Here, forgetting the registry fails the build instead.
        """
        self.assertEqual(sorted(self.declared), self.on_disk)

    def test_no_plan_is_declared_twice(self) -> None:
        self.assertEqual(len(self.declared), len(set(self.declared)))


class ProseAgreesWithTheRegistry(CampaignRegistryCoherence):
    """The plans' banners are a restatement, and a restatement may not diverge."""

    def test_exactly_the_active_plan_claims_active_in_prose(self) -> None:
        """Both directions in one assertion, because both have gone wrong.

        A governing plan whose banner does not say so misleads every human
        reader; a retired plan whose banner still says ACTIVE is the stale
        banner that made a superseded edition look current for two days.
        """
        self.assertEqual(self.claiming_active, [self.active])

    def test_every_plan_carries_a_status_line_at_all(self) -> None:
        """A missing banner would satisfy the check above by vacuous truth."""
        self.assertEqual(
            [k for k, line in self.status_lines.items() if not line.startswith("Status:")],
            [],
        )


if __name__ == "__main__":
    unittest.main()
