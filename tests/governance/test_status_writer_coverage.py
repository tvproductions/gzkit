"""Writer-coverage audit for frontmatter ``status:`` writes (GHI #669).

The audit exists because ADR-0.31.0 Decision item 4's *"single invariant
monitor"* was enforced by convention: every writer routed through the monitor,
and nothing would have discovered the next one that did not.

These tests are written against synthetic trees rather than the live repo on
purpose. A test that only asserts the live tree is clean would pass equally
well if the audit had no teeth at all — which is the exact shape of defect
this audit was built to close.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.status_writer_coverage import (
    _REGISTERED_WRITERS,
    audit_status_writer_coverage,
)


def _plant(root: Path, name: str, body: str) -> None:
    target = root / "src" / "gzkit" / "commands" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")


def _bypass_findings(root: Path, name: str) -> list[str]:
    """Findings about one planted module, excluding the register's own noise."""
    return [e.artifact for e in audit_status_writer_coverage(root) if name in e.artifact]


class TestBypassDetection(unittest.TestCase):
    """A writer that reaches ``status:`` without the monitor must be refused."""

    def test_flags_an_unguarded_upsert(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _plant(
                root,
                "rogue.py",
                "def promote(content: str) -> str:\n"
                '    return _upsert_frontmatter_value(content, "status", "Completed")\n',
            )
            self.assertTrue(_bypass_findings(root, "rogue.py"))

    def test_flags_an_unguarded_governed_key_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _plant(
                root,
                "rogue.py",
                "def promote(path) -> None:\n"
                '    rewrite_governed_keys_in_place(path, {"status": "Completed"})\n',
            )
            self.assertTrue(_bypass_findings(root, "rogue.py"))

    def test_flags_an_opaque_edits_mapping(self) -> None:
        """An edits dict the audit cannot inspect may carry ``status``.

        Refusing the unprovable case is the point: assuming the benign reading
        is how a convention-only guard decays.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _plant(
                root,
                "rogue.py",
                "def promote(path, edits) -> None:\n"
                "    rewrite_governed_keys_in_place(path, edits)\n",
            )
            self.assertTrue(_bypass_findings(root, "rogue.py"))

    def test_ignores_a_write_to_some_other_governed_key(self) -> None:
        """The audit's scope is ``status:``, not every frontmatter key."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _plant(
                root,
                "rogue.py",
                "def retag(content: str) -> str:\n"
                '    return _upsert_frontmatter_value(content, "kind", "foundation")\n',
            )
            self.assertEqual([], _bypass_findings(root, "rogue.py"))


class TestSanctionedConsultation(unittest.TestCase):
    """Consulting any sanctioned monitor discharges the obligation."""

    def test_monitor_consultation_clears_the_writer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _plant(
                root,
                "guarded.py",
                "def promote(content: str, current: str) -> str | None:\n"
                "    refusal = obpi_status_write_refusal(\n"
                '        brief_name="b.md", current_status=current, target_status="Completed"\n'
                "    )\n"
                "    if refusal is not None:\n"
                "        return None\n"
                '    return _upsert_frontmatter_value(content, "status", "Completed")\n',
            )
            self.assertEqual([], _bypass_findings(root, "guarded.py"))

    def test_stricter_transition_gate_also_clears_the_writer(self) -> None:
        """``_should_refuse_rewrite`` enforces the full transition table.

        A superset of the monitor's refusals is a stronger guarantee, so
        admitting it is not a loophole.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _plant(
                root,
                "reconcile.py",
                "def apply(monitor, path, rewrite, edits) -> None:\n"
                "    if _should_refuse_rewrite(monitor, path, rewrite):\n"
                "        return\n"
                "    rewrite_governed_keys_in_place(path, edits)\n",
            )
            self.assertEqual([], _bypass_findings(root, "reconcile.py"))


class TestQualifiedNameResolution(unittest.TestCase):
    """Function identity is qualified, so same-named siblings cannot mask."""

    def test_a_guarded_namesake_does_not_clear_an_unguarded_writer(self) -> None:
        """Two classes, one method name, opposite behavior.

        With bare-name matching the guarded namesake's consultation would clear
        the bypass — a hole in a guard whose whole purpose is closing holes.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _plant(
                root,
                "namesakes.py",
                "class Guarded:\n"
                "    def promote(self, content: str, current: str) -> str:\n"
                "        obpi_status_write_refusal(\n"
                '            brief_name="b", current_status=current, target_status="Completed"\n'
                "        )\n"
                '        return _upsert_frontmatter_value(content, "status", "Completed")\n'
                "\n\n"
                "class Rogue:\n"
                "    def promote(self, content: str) -> str:\n"
                '        return _upsert_frontmatter_value(content, "status", "Completed")\n',
            )
            findings = _bypass_findings(root, "namesakes.py")
            self.assertEqual(1, len(findings), "exactly the Rogue write must be flagged")


class TestRegisterDiscipline(unittest.TestCase):
    """The register is a record, not an escape hatch."""

    def test_every_live_register_entry_is_justified_on_this_tree(self) -> None:
        """No entry may be inert.

        GHI #727 found the sole ``_DATACLASS_WAIVERS`` entry exempting nothing,
        because its staleness predicate asked *does this class still exist*
        rather than *does it still need the exemption*. This asserts the
        stronger question against the live repo.
        """
        inert = [
            e.artifact
            for e in audit_status_writer_coverage(Path(__file__).resolve().parents[2])
            if "is inert" in e.message
        ]
        self.assertEqual([], inert)

    def test_no_registered_reason_is_empty(self) -> None:
        for key, reason in _REGISTERED_WRITERS.items():
            with self.subTest(key=key):
                self.assertTrue(reason.strip(), f"{key} carries an empty reason")

    def test_every_registered_reason_names_its_scope(self) -> None:
        """Scope is what was unrecorded in this audit's class of failure.

        GHI #607 shipped a gate whose reach nobody had written down, and it
        broke an adopter's build for two months. An entry that says only
        "exempt" repeats that.
        """
        for key, reason in _REGISTERED_WRITERS.items():
            with self.subTest(key=key):
                self.assertIn("Scope:", reason, f"{key} does not state what it writes")


class TestAuditScope(unittest.TestCase):
    """Boundaries of the walk itself."""

    def test_returns_empty_when_there_is_no_src_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual([], audit_status_writer_coverage(Path(tmp)))

    def test_unparseable_module_does_not_abort_the_walk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _plant(root, "broken.py", "def (:\n")
            _plant(
                root,
                "rogue.py",
                "def promote(content: str) -> str:\n"
                '    return _upsert_frontmatter_value(content, "status", "Completed")\n',
            )
            self.assertTrue(_bypass_findings(root, "rogue.py"))


if __name__ == "__main__":
    unittest.main()
