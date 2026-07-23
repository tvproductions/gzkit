"""Guard: `@covers` may only decorate a BEHAVIOR REQ (GHI #711).

Each ADR-0.0.59 kind has exactly one proof channel: BEHAVIOR → a `@covers` test,
SUPPORT → ledger event + structural validator, STRUCTURAL-FENCE → parent-ADR
`## Boundary Invariants` entry. A `@covers` decorating a SUPPORT or
STRUCTURAL-FENCE REQ is an inverted proof channel — it inflates the decoration
census with an assertion that cannot fail when production behavior changes
(`.gzkit/rules/tests.md` § REQ Scope Discipline, rule (c)).

`gz validate --req-kind-discipline` governs the *declaration* side; this test is
the mechanical guard for the *decoration* side, which had none (GHI #711). It
fails closed inside `gz check` on any `@covers` whose declared REQ kind is not
BEHAVIOR. Untagged/legacy REQs default to BEHAVIOR (the conservative channel
that owes proof), matching `parse_brief_req_kinds`'s caller contract, so only an
explicitly SUPPORT/STRUCTURAL-FENCE tag trips the guard.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.governance.req_coverage import parse_brief_req_kinds
from gzkit.traceability import find_covers_in_source

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _req_kind_map() -> dict[str, str]:
    """Merge declared `[kind]` tags across every ADR/OBPI brief in the repo."""
    kinds: dict[str, str] = {}
    for brief in (_REPO_ROOT / "docs" / "design" / "adr").rglob("*.md"):
        kinds.update(parse_brief_req_kinds(brief))
    return kinds


def _non_behavior_covers() -> list[tuple[str, str, str]]:
    """Return (location, req_id, kind) for every @covers on a non-BEHAVIOR REQ."""
    kinds = _req_kind_map()
    violations: list[tuple[str, str, str]] = []
    for test_file in (_REPO_ROOT / "tests").rglob("*.py"):
        content = test_file.read_text(encoding="utf-8")
        for req_id, line in find_covers_in_source(content):
            kind = kinds.get(req_id)
            if kind is not None and kind != "BEHAVIOR":
                rel = test_file.relative_to(_REPO_ROOT).as_posix()
                violations.append((f"{rel}:{line}", req_id, kind))
    return violations


class TestCoversDecoratesOnlyBehaviorReqs(unittest.TestCase):
    def test_no_covers_on_non_behavior_req(self) -> None:
        violations = _non_behavior_covers()
        detail = "\n".join(f"  {loc}  {rid} [{kind}]" for loc, rid, kind in sorted(violations))
        self.assertEqual(
            violations,
            [],
            "@covers must decorate a BEHAVIOR REQ only — its channel is the proof "
            "channel for no other kind (SUPPORT → ledger + validator; "
            "STRUCTURAL-FENCE → parent-ADR boundary invariant). Remove these "
            f"decorations (GHI #711):\n{detail}",
        )


if __name__ == "__main__":
    unittest.main()
