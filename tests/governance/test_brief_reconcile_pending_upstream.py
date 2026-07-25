"""Unstarted-brief Discovery scoping narrows by predicate, never by exemption (GHI #615).

Operator ruling 2026-07-25: the residual Discovery findings are three classes,
not one, and the split is computable from Layer-1 canon (each brief's own
``## Allowed Paths``) rather than from a marker an author asserts about their
own row:

* **own-deliverable** — the path is in this brief's Allowed Paths
* **pending-upstream** — the path is a non-terminal sibling OBPI's deliverable
* **dead-citation** — nothing under this ADR will ever create it

The first two stop gating. The third must keep gating: those are the stale
references to surfaces that moved (``src/gzkit/cli/validate.py`` when the module
is ``commands/validate_cmd.py``) that GHI #581 exists to catch. A change that
silenced them would trade one defect for another.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.brief_reconcile import reconcile_brief


def _brief(status: str, allowed: list[str], discovery: list[str]) -> str:
    allow_rows = "\n".join(f"- `{p}` — NEW" for p in allowed)
    disc_rows = "\n".join(f"- [ ] `{p}`" for p in discovery)
    return (
        "---\n"
        "id: OBPI-0.9.9-0X-demo\n"
        "parent: ADR-0.9.9-demo\n"
        f"status: {status}\n"
        "---\n\n"
        "# OBPI-0.9.9-0X-demo: Demo\n\n"
        "## Allowed Paths\n\n"
        f"{allow_rows}\n\n"
        "## Discovery Checklist\n\n"
        f"{disc_rows}\n\n"
        "## Verification\n\n"
        "- none\n"
    )


class UnstartedDiscoveryScoping(unittest.TestCase):
    """A Draft brief gates on prerequisites nobody will build, not on sequence."""

    def _package(self, tmp: str):
        root = Path(tmp)
        obpis = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.9.9-demo" / "obpis"
        obpis.mkdir(parents=True)
        return root, obpis

    def test_sibling_deliverable_is_sequence_not_drift(self) -> None:
        """OBPI-02 needing what unstarted OBPI-01 will create is sequence.

        The corpus case: OBPI-0.0.43-02's Discovery row names
        `domain_models.py` annotated `(OBPI-01 product)`. No edit to either
        brief makes that path exist sooner.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root, obpis = self._package(tmp)
            (obpis / "OBPI-0.9.9-01-producer.md").write_text(
                _brief("Draft", ["src/demo/produced.py"], []), encoding="utf-8"
            )
            target = obpis / "OBPI-0.9.9-02-consumer.md"
            target.write_text(
                _brief("Draft", ["src/demo/consumer.py"], ["src/demo/produced.py"]),
                encoding="utf-8",
            )
            result = reconcile_brief(target, root)
        self.assertEqual(result.discovery_delta.unresolved_paths, [])
        self.assertFalse(result.has_drift)

    def test_own_deliverable_does_not_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, obpis = self._package(tmp)
            target = obpis / "OBPI-0.9.9-01-selfmade.md"
            target.write_text(
                _brief("Draft", ["src/demo/mine.py"], ["src/demo/mine.py"]), encoding="utf-8"
            )
            result = reconcile_brief(target, root)
        self.assertEqual(result.discovery_delta.unresolved_paths, [])

    def test_dead_citation_still_gates(self) -> None:
        """The fence that must survive: no OBPI under this ADR creates the path."""
        with tempfile.TemporaryDirectory() as tmp:
            root, obpis = self._package(tmp)
            (obpis / "OBPI-0.9.9-01-producer.md").write_text(
                _brief("Draft", ["src/demo/produced.py"], []), encoding="utf-8"
            )
            target = obpis / "OBPI-0.9.9-02-consumer.md"
            target.write_text(
                _brief("Draft", ["src/demo/consumer.py"], ["src/gzkit/cli/validate.py"]),
                encoding="utf-8",
            )
            result = reconcile_brief(target, root)
        self.assertEqual(result.discovery_delta.unresolved_paths, ["src/gzkit/cli/validate.py"])
        self.assertTrue(
            result.has_drift,
            "a Discovery path no OBPI under this ADR creates is drift, not sequence",
        )

    def test_terminal_sibling_does_not_launder_a_dead_path(self) -> None:
        """A completed sibling's Allowed Paths prove the file should already exist.

        If the producer is done and the path still is not on disk, that is real
        drift — treating it as pending-upstream would suppress exactly the case
        where something was renamed or deleted after its OBPI closed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root, obpis = self._package(tmp)
            (obpis / "OBPI-0.9.9-01-producer.md").write_text(
                _brief("attested_completed", ["src/demo/produced.py"], []), encoding="utf-8"
            )
            target = obpis / "OBPI-0.9.9-02-consumer.md"
            target.write_text(
                _brief("Draft", ["src/demo/consumer.py"], ["src/demo/produced.py"]),
                encoding="utf-8",
            )
            result = reconcile_brief(target, root)
        self.assertEqual(result.discovery_delta.unresolved_paths, ["src/demo/produced.py"])
        self.assertTrue(result.has_drift)

    def test_existing_path_never_reaches_the_scoping(self) -> None:
        """Scoping only ever removes unresolved paths; a real file is not one."""
        with tempfile.TemporaryDirectory() as tmp:
            root, obpis = self._package(tmp)
            (root / "src" / "demo").mkdir(parents=True)
            (root / "src" / "demo" / "real.py").write_text("", encoding="utf-8")
            target = obpis / "OBPI-0.9.9-01-demo.md"
            target.write_text(
                _brief("Draft", ["src/demo/other.py"], ["src/demo/real.py"]), encoding="utf-8"
            )
            result = reconcile_brief(target, root)
        self.assertEqual(result.discovery_delta.unresolved_paths, [])
        self.assertFalse(result.has_drift)


class StartedBriefUnaffected(unittest.TestCase):
    """The narrowing is scoped to unstarted briefs and must not leak past them."""

    def test_active_brief_still_gates_on_its_own_deliverable(self) -> None:
        """Once work has begun, a Discovery path that does not exist is drift.

        This is the boundary REQ-0.0.37-05-02 draws its contrast on: an Active
        brief makes live claims, so the unstarted narrowing must not reach it.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpis = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.9.9-demo" / "obpis"
            obpis.mkdir(parents=True)
            target = obpis / "OBPI-0.9.9-01-demo.md"
            target.write_text(
                _brief("Active", ["src/demo/mine.py"], ["src/demo/mine.py"]), encoding="utf-8"
            )
            result = reconcile_brief(target, root)
        self.assertEqual(result.discovery_delta.unresolved_paths, ["src/demo/mine.py"])
        self.assertTrue(result.has_drift)


if __name__ == "__main__":
    unittest.main()
