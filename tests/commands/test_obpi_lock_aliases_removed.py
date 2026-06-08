"""Tests for OBPI-0.0.67-03: Deprecated lock aliases removed.

Regression test verifying deprecated flat-form aliases (obpi lock-claim,
obpi lock-release, obpi lock-status) are no longer registered; canonical
space-form verbs remain active.
"""

from __future__ import annotations

import unittest

from gzkit.governance.trust_audits.cli import _NO_SKILL_VERBS, _known_cli_verb_paths
from gzkit.traceability import covers


class TestObpiLockAliasesRemoved(unittest.TestCase):
    """Deprecated obpi lock-* aliases must not be registered (REQ-0.0.67-03-01)."""

    @covers("REQ-0.0.67-03-01")
    def test_deprecated_aliases_not_registered(self) -> None:
        """Assert deprecated flat-form aliases are absent from CLI surface.

        After removal, "obpi lock-claim", "obpi lock-release", and
        "obpi lock-status" must not appear in the registered verb paths.
        """
        known_verbs = _known_cli_verb_paths()
        deprecated_aliases = {"obpi lock-claim", "obpi lock-release", "obpi lock-status"}
        for alias in deprecated_aliases:
            self.assertNotIn(
                alias,
                known_verbs,
                msg=f"Deprecated alias '{alias}' should not be registered",
            )

    @covers("REQ-0.0.67-03-01")
    def test_canonical_space_forms_still_registered(self) -> None:
        """Assert canonical space-form verbs remain registered.

        The canonical verbs "obpi lock claim", "obpi lock release", and
        "obpi lock list" must still be present in the registered verb paths.
        """
        known_verbs = _known_cli_verb_paths()
        canonical_forms = {"obpi lock claim", "obpi lock release", "obpi lock list"}
        for form in canonical_forms:
            self.assertIn(
                form,
                known_verbs,
                msg=f"Canonical form '{form}' must remain registered",
            )

    @covers("REQ-0.0.67-03-01")
    def test_deleted_aliases_have_no_stale_skill_waiver(self) -> None:
        """Assert deleted aliases leave no stale `_NO_SKILL_VERBS` waiver.

        Coupled-surface coherence: a waiver naming a now-unregistered verb
        fails the skill-alignment stale-waiver check. Deleting the verbs
        (parser) and removing their waivers must happen together.
        """
        deprecated_aliases = {"obpi lock-claim", "obpi lock-release", "obpi lock-status"}
        for alias in deprecated_aliases:
            self.assertNotIn(
                alias,
                _NO_SKILL_VERBS,
                msg=f"Stale skill waiver for deleted verb '{alias}' must be removed",
            )
