"""Every registered invariant's structural_witness must resolve to a real command (GHI #623).

A ConstitutionalInvariant declares the gate that mechanically enforces its claim. A
witness naming a command that does not exist is the structural-witness theater GHI #623
was filed about, one layer up: the registry asserts an invariant is enforced while
nothing enforces it, and no check disagrees.

Caught live: ``foundation-adr-registers-invariant.json`` named
``gz validate --foundation-registers-invariant``, which has never existed.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.invariant_witness import validate_invariant_witnesses


def _write_invariant(root: Path, name: str, witnesses: list[str]) -> None:
    inv_dir = root / ".gzkit" / "invariants"
    inv_dir.mkdir(parents=True, exist_ok=True)
    (inv_dir / f"{name}.json").write_text(
        json.dumps(
            {
                "id": name,
                "claim": "A claim under test.",
                "structural_witness": witnesses,
                "composition_targets": [],
            }
        ),
        encoding="utf-8",
    )


class TestInvariantWitnessResolution(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_unresolvable_validate_flag_is_reported(self) -> None:
        """A `gz validate --<scope>` witness naming an unregistered scope fails closed."""
        _write_invariant(self._root, "vapor", ["gz validate --no-such-scope"])
        errors = validate_invariant_witnesses(self._root)
        self.assertEqual(len(errors), 1)
        self.assertIn("no-such-scope", errors[0].message)

    def test_registered_validate_flag_resolves(self) -> None:
        """A witness naming a real validate scope passes."""
        _write_invariant(self._root, "real", ["gz validate --invariant-coherence"])
        self.assertEqual(validate_invariant_witnesses(self._root), [])

    def test_unresolvable_verb_path_is_reported(self) -> None:
        """A witness naming a command path that is not registered fails closed."""
        _write_invariant(self._root, "vapor-verb", ["gz nonexistent subcommand"])
        errors = validate_invariant_witnesses(self._root)
        self.assertEqual(len(errors), 1)
        self.assertIn("nonexistent subcommand", errors[0].message)

    def test_registered_verb_path_resolves(self) -> None:
        """A witness naming a real nested command path passes."""
        _write_invariant(self._root, "real-verb", ["gz skill audit"])
        self.assertEqual(validate_invariant_witnesses(self._root), [])

    def test_parenthetical_annotation_is_stripped_before_resolution(self) -> None:
        """`gz obpi complete (stage 5)` resolves on the command, not the prose tail.

        CIC-2 annotates witnesses with the pipeline stage that fires them. The
        annotation is documentation; the command is the claim under test.
        """
        _write_invariant(self._root, "annotated", ["gz obpi complete (stage 5)"])
        self.assertEqual(validate_invariant_witnesses(self._root), [])

    def test_every_witness_in_an_entry_is_checked(self) -> None:
        """A good first witness does not excuse a vapor second one."""
        _write_invariant(
            self._root,
            "mixed",
            ["gz validate --invariant-coherence", "gz validate --no-such-scope"],
        )
        errors = validate_invariant_witnesses(self._root)
        self.assertEqual(len(errors), 1)
        self.assertIn("no-such-scope", errors[0].message)

    def test_no_registry_returns_empty(self) -> None:
        """Bootstrap-safe: a project with no invariants directory yields no findings."""
        self.assertEqual(validate_invariant_witnesses(self._root), [])

    def test_recovery_prose_names_the_entry_and_a_next_step(self) -> None:
        """Three-part recovery prose (.claude/rules/guardrail-feedback-prose.md)."""
        _write_invariant(self._root, "vapor", ["gz validate --no-such-scope"])
        message = validate_invariant_witnesses(self._root)[0].message
        self.assertIn("vapor", message)
        self.assertIn("gz validate --help", message)


class TestCommittedRegistryWitnesses(unittest.TestCase):
    """Fence on the real registry's vapor witnesses (GHI #623).

    The known set is now EMPTY: every committed invariant's structural witness resolves
    to a registered command. The fence stays shrink-only by construction — a NEW vapor
    witness fails immediately, and re-admitting one requires updating this set
    deliberately rather than letting it drift.

    Formerly known: `foundation-adr-registers-invariant` claimed "every foundation-kind
    ADR registers at least one invariant" witnessed by `gz validate
    --foundation-registers-invariant`, a scope that never existed. The claim was also
    unenforceable as written — `constitutional_invariant.json` carries no field naming
    which ADR registered an entry. Retired as superseded by the ADR-0.34.0 Foundation
    Sunset (operator ruling, Movement A item 3, 2026-08-02): the foundation kind is
    closed at both `adr_created` ingresses, so the claim's subject set is permanently
    frozen at the 51-entry grandfathered roster and can never be exercised again. The
    entry now states that sealed reality and is witnessed by `gz validate --taxonomy`.
    The file is retained rather than deleted because REQ-0.0.37-01-03 (attested) asserts
    it exists and loads; only its `claim` and `structural_witness` changed.
    """

    _KNOWN_UNRESOLVED: frozenset[str] = frozenset()

    def test_committed_registry_carries_no_vapor_witness(self) -> None:
        errors = validate_invariant_witnesses(Path("."))
        offenders = {Path(e.artifact).stem for e in errors}
        self.assertEqual(
            offenders,
            self._KNOWN_UNRESOLVED,
            "An unresolvable structural witness entered .gzkit/invariants/. Every "
            "registered invariant must name a command that resolves; run "
            "`gz validate --help` to confirm the scope exists.",
        )


if __name__ == "__main__":
    unittest.main()
