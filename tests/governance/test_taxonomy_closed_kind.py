"""Closed-kind and manifest-integrity assertions for the foundation sunset.

Covers ADR-0.34.0 / OBPI-0.34.0-01. The foundation kind is SEALED, not
deleted: ``data/foundation_grandfather.json`` is the committed closed
membership set, and these assertions make it binding. Without them the
manifest is decoration — anyone drops a ``kind: foundation`` ADR into the
tree and it is silently a member.

Each test builds its own temp project root; none depends on the real
repository's foundation set or manifest.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.governance.trust_audits.taxonomy import audit_foundation_closure
from gzkit.traceability import covers

_FOUNDATION_ADR = """---
id: {adr_id}
status: Validated
kind: foundation
semver: {semver}
lane: heavy
---

# {adr_id}: Test Foundation
"""


def _write_foundation_adr(root: Path, adr_id: str, semver: str) -> None:
    """Write a minimal ``kind: foundation`` ADR package under ``root``."""
    pkg = root / "docs" / "design" / "adr" / "foundation" / adr_id
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / f"{adr_id}.md").write_text(
        _FOUNDATION_ADR.format(adr_id=adr_id, semver=semver), encoding="utf-8"
    )


def _write_manifest(root: Path, entries: list[dict[str, str]]) -> None:
    """Write the grandfather manifest under ``root``."""
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "foundation_grandfather.json").write_text(
        json.dumps(entries, indent=2), encoding="utf-8"
    )


def _entry(adr_id: str, semver: str) -> dict[str, str]:
    return {
        "id": adr_id,
        "title": "Test Foundation",
        "semver": semver,
        "frozen_at": "2026-07-19",
    }


def _write_grandfathered_ledger(root: Path, adr_ids: list[str]) -> None:
    """Witness ``adr_ids`` as terminal via Layer-2 ``foundation_grandfathered``.

    A manifest entry is a *member*; the ledger event is what makes it
    *terminal* (ADR-0.34.0 OBPI-03). A fixture describing a fully-valid
    grandfathered foundation therefore needs both.
    """
    gz_dir = root / ".gzkit"
    gz_dir.mkdir(parents=True, exist_ok=True)
    (gz_dir / "ledger.jsonl").write_text(
        "".join(
            json.dumps({"event": "foundation_grandfathered", "id": adr_id, "attestor": "g0"}) + "\n"
            for adr_id in adr_ids
        ),
        encoding="utf-8",
    )


class TestFoundationKindClosed(unittest.TestCase):
    """An on-disk foundation ADR absent from the manifest is a breach."""

    @covers("REQ-0.34.0-01-01")
    def test_unlisted_foundation_adr_is_flagged(self) -> None:
        """A kind:foundation ADR not in the manifest emits foundation_kind_closed.

        Semantics, not string-matching: the manifest is the closed membership
        set, so the on-disk foundation set must be a SUBSET of it. An ADR on
        disk but absent from the manifest means the kind was reopened without
        editing the reviewed list — the silent-membership hole ADR-0.34.0
        exists to close.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_foundation_adr(root, "ADR-0.0.99-unlisted", "0.0.99")
            _write_manifest(root, [])

            errors = audit_foundation_closure(root)

            self.assertEqual(
                [e.type for e in errors],
                ["foundation_kind_closed"],
                "an unlisted on-disk foundation ADR must emit exactly one "
                "foundation_kind_closed finding",
            )
            self.assertIn("ADR-0.0.99-unlisted", errors[0].artifact + errors[0].message)

    @covers("REQ-0.34.0-01-01")
    def test_listed_foundation_adr_is_clean(self) -> None:
        """A kind:foundation ADR present in the manifest emits nothing.

        The negative control for the assertion above: without this, a check
        that flagged every foundation unconditionally would pass the test
        above while being useless.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_foundation_adr(root, "ADR-0.0.99-listed", "0.0.99")
            _write_manifest(root, [_entry("ADR-0.0.99-listed", "0.0.99")])
            _write_grandfathered_ledger(root, ["ADR-0.0.99-listed"])

            self.assertEqual(audit_foundation_closure(root), [])

    @covers("REQ-0.34.0-01-01")
    def test_guardrail_prose_is_three_part(self) -> None:
        """The finding names what failed, why forbidden, and the next step.

        Per .gzkit/rules/guardrail-feedback-prose.md: a bare finding forces the
        consuming agent to reconstruct operator intent from training memory.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_foundation_adr(root, "ADR-0.0.99-prose", "0.0.99")
            _write_manifest(root, [])

            message = audit_foundation_closure(root)[0].message

            self.assertIn("ADR-0.34.0", message, "must cite the closing ADR (why forbidden)")
            self.assertTrue(
                "--kind feature" in message or "gz adr demote" in message,
                "must name a runnable governed next step",
            )


class TestGrandfatherDangling(unittest.TestCase):
    """A manifest entry naming no on-disk package is a breach."""

    @covers("REQ-0.34.0-01-02")
    def test_manifest_entry_without_package_is_flagged(self) -> None:
        """A manifest entry with no on-disk ADR emits grandfather_dangling.

        The inverse containment check. Without it the manifest could name
        foundations that do not exist, making the "closed set" unfalsifiable
        in one direction.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "design" / "adr" / "foundation").mkdir(parents=True)
            _write_manifest(root, [_entry("ADR-0.0.98-ghost", "0.0.98")])

            errors = audit_foundation_closure(root)

            self.assertEqual(
                [e.type for e in errors],
                ["grandfather_dangling"],
                "a manifest entry with no on-disk package must emit exactly "
                "one grandfather_dangling finding",
            )
            self.assertIn("ADR-0.0.98-ghost", errors[0].artifact + errors[0].message)

    @covers("REQ-0.34.0-01-02")
    def test_both_directions_flagged_together(self) -> None:
        """Containment is checked in both directions independently."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_foundation_adr(root, "ADR-0.0.99-unlisted", "0.0.99")
            _write_manifest(root, [_entry("ADR-0.0.98-ghost", "0.0.98")])

            types = sorted(e.type for e in audit_foundation_closure(root))

            self.assertEqual(types, ["foundation_kind_closed", "grandfather_dangling"])


class TestClosedKindExitContract(unittest.TestCase):
    """Both closure findings must reach the operator as exit 3, not exit 1.

    REQ-0.34.0-01-01 and REQ-0.34.0-01-02 are each two-conjunct: emit the
    finding **and exit 3**. Every other test in this module asserts only the
    first conjunct by calling ``audit_foundation_closure`` directly, which
    never touches the CLI's exit path. The exit code is conferred by
    membership in ``_POLICY_BREACH_ERROR_TYPES``: an unregistered finding
    type falls through to ``SystemExit(0)`` and only a registered one
    reaches ``SystemExit(3)`` (``validate_cmd.py`` ``_print_validation_result``).

    Without these assertions, deleting either registration line leaves this
    whole module green while both REQs are violated. The sibling gate
    ``foundation_limbo`` carries the identical assertion
    (``tests/test_foundation_limbo_gate.py``) because a Step-4b adversary
    caught exactly that defect there; this back-fills it for OBPI-01's two
    types (audit shortfall S2, 2026-07-31).

    Asserted at the registry rather than by scraping console output because
    the registry IS the mechanism, and because a live repo carrying findings
    of the other type would make the real command exit 3 for someone else's
    reason and mask this one entirely.
    """

    @covers("REQ-0.34.0-01-01")
    def test_closed_kind_is_registered_as_a_policy_breach(self) -> None:
        """`foundation_kind_closed` routes to exit 3, per REQ-0.34.0-01-01."""
        from gzkit.commands.validate_cmd import _POLICY_BREACH_ERROR_TYPES

        self.assertIn(
            "foundation_kind_closed",
            _POLICY_BREACH_ERROR_TYPES,
            "foundation_kind_closed must be a registered policy breach or the "
            "finding renders and then exits 0, violating REQ-0.34.0-01-01's "
            "exit-3 conjunct",
        )

    @covers("REQ-0.34.0-01-02")
    def test_grandfather_dangling_is_registered_as_a_policy_breach(self) -> None:
        """`grandfather_dangling` routes to exit 3, per REQ-0.34.0-01-02."""
        from gzkit.commands.validate_cmd import _POLICY_BREACH_ERROR_TYPES

        self.assertIn(
            "grandfather_dangling",
            _POLICY_BREACH_ERROR_TYPES,
            "grandfather_dangling must be a registered policy breach or the "
            "finding renders and then exits 0, violating REQ-0.34.0-01-02's "
            "exit-3 conjunct",
        )


if __name__ == "__main__":
    unittest.main()
