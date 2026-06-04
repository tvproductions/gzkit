"""REQ-coverage gate is ADR-0.0.59 kind-aware (loosening pass, 2026-06-04).

The `gz obpi complete` REQ-coverage gate (ADR-0.0.25) historically required a
passing `@covers` test for *every* brief REQ. But ADR-0.0.59 / `.gzkit/rules/tests.md`
declare that only **BEHAVIOR**-kind REQs are proven by `@covers`; **SUPPORT** REQs
are proven by a ledger `artifact_edited` event + structural validator, and
**STRUCTURAL-FENCE** REQs by a parent-ADR `## Boundary Invariants` entry. Authoring
a `@covers` test for a SUPPORT REQ is the named anti-pattern.

These tests pin the gate to that taxonomy: SUPPORT / STRUCTURAL-FENCE REQs must NOT
gap the coverage gate (no waiver needed), while an uncovered BEHAVIOR REQ must still
fail closed on heavy/foundation. Untagged (legacy) REQs keep the old behaviour.

Task: TASK-loosen-req-coverage-kind-aware
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.obpi_complete import _enforce_req_coverage_gate
from gzkit.governance.req_coverage import parse_brief_req_kinds, parse_brief_reqs

_BRIEF = """\
---
id: OBPI-9.9.9-01
parent: ADR-9.9.9
item: 1
lane: Heavy
status: Draft
---

# OBPI-9.9.9-01: kind-aware coverage fixture

## Acceptance Criteria

{criteria}

## Evidence
"""

_SUPPORT_CRITERIA = (
    "- [ ] REQ-9.9.9-01-01 [SUPPORT]: data file edited; "
    "proof = artifact_edited + gz validate --documents\n"
    "- [ ] REQ-9.9.9-01-02 [STRUCTURAL-FENCE]: changes remain inside Allowed Paths"
)
_BEHAVIOR_CRITERIA = "- [ ] REQ-9.9.9-01-01 [BEHAVIOR]: the command emits X when Y"


def _write_brief(root: Path, criteria: str) -> Path:
    (root / "tests").mkdir(exist_ok=True)
    brief = root / "brief.md"
    brief.write_text(_BRIEF.format(criteria=criteria), encoding="utf-8")
    return brief


class TestCoverageGateKindAware(unittest.TestCase):
    """ADR-0.0.59 kind discipline applied to the ADR-0.0.25 completion gate."""

    def test_parse_brief_req_kinds_reads_inline_tags(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            brief = _write_brief(Path(td), _SUPPORT_CRITERIA)
            self.assertEqual(
                parse_brief_req_kinds(brief),
                {"REQ-9.9.9-01-01": "SUPPORT", "REQ-9.9.9-01-02": "STRUCTURAL-FENCE"},
            )

    def test_support_and_structural_fence_reqs_do_not_require_covers(self) -> None:
        """Heavy/foundation, no @covers, no waiver: SUPPORT + STRUCTURAL-FENCE pass."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief = _write_brief(root, _SUPPORT_CRITERIA)
            # Sanity: both REQs are actually parsed (gate is not trivially empty).
            self.assertEqual(len(parse_brief_reqs(brief)), 2)
            # Must NOT raise — proven by ledger+validator / parent-ADR invariant.
            _enforce_req_coverage_gate(
                obpi_id="OBPI-9.9.9-01",
                parent_adr="ADR-9.9.9",
                parent_lane="heavy",
                parent_kind="foundation",
                brief_path=brief,
                project_root=root,
                as_json=False,
                dry_run=False,
            )

    def test_behavior_kind_uncovered_req_still_fails_closed(self) -> None:
        """Loosening must not over-reach: an uncovered BEHAVIOR REQ still blocks."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief = _write_brief(root, _BEHAVIOR_CRITERIA)
            with self.assertRaises(SystemExit):
                _enforce_req_coverage_gate(
                    obpi_id="OBPI-9.9.9-01",
                    parent_adr="ADR-9.9.9",
                    parent_lane="heavy",
                    parent_kind="foundation",
                    brief_path=brief,
                    project_root=root,
                    as_json=False,
                    dry_run=False,
                )


if __name__ == "__main__":
    unittest.main()
