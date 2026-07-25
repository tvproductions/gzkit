"""Operator-doc references to manpages must use the <verb>.md convention (GHI #532).

No manpage file under docs/user/manpages/ carries a ``gz-`` prefix, so a
``manpages/gz-<verb>.md`` reference is always a dead pointer. The audit fails
closed on that convention; terminal (sealed) OBPI briefs are exempt.

The canonical logic lives in
``gzkit.governance.trust_audits.audit_manpage_alignment`` and is exposed under
``gz validate --cli-alignment``.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_manpage_alignment

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _write_brief(root: Path, *, obpi_id: str, manpage_ref: str, status: str = "Draft") -> Path:
    obpi_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-fixture" / "obpis"
    obpi_dir.mkdir(parents=True, exist_ok=True)
    brief = obpi_dir / f"{obpi_id}.md"
    brief.write_text(
        f"---\nid: {obpi_id}\nstatus: {status}\n---\n\n# {obpi_id}\n\n- `{manpage_ref}` — doc\n",
        encoding="utf-8",
    )
    return brief


class ManpageAlignmentBehavior(unittest.TestCase):
    """audit_manpage_alignment fails closed on the gz-<verb>.md convention."""

    def test_gz_prefixed_manpage_ref_in_open_brief_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root, obpi_id="OBPI-open-01", manpage_ref="docs/user/manpages/gz-validate.md"
            )
            errors = audit_manpage_alignment(root)

        self.assertEqual(len(errors), 1, f"expected one manpage_alignment error, got {errors}")
        self.assertEqual(errors[0].type, "manpage_alignment")
        self.assertIn("gz-validate.md", errors[0].message)
        self.assertIn("manpages/validate.md", errors[0].message)  # recovery names the fix

    def test_correct_convention_reference_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(root, obpi_id="OBPI-open-02", manpage_ref="docs/user/manpages/validate.md")
            self.assertEqual(audit_manpage_alignment(root), [])

    def test_terminal_brief_is_exempt(self) -> None:
        """A sealed brief's frozen references are not re-gated (sealed-record doctrine)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                obpi_id="OBPI-sealed-01",
                manpage_ref="docs/user/manpages/gz-validate.md",
                status="Completed",
            )
            self.assertEqual(audit_manpage_alignment(root), [])

    def test_generated_release_manifest_is_exempt(self) -> None:
        """A release manifest quotes GHI titles verbatim; it is a sealed record.

        ``gz patch release`` renders one row per discovered GHI from the issue's
        title. When a GHI is *about* the gz- prefix drift, its title contains the
        forbidden string as quoted evidence — not as a pointer telling a reader
        where to go. Rewriting it would falsify what the issue was called, the
        same reason terminal briefs are exempt.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            releases = root / "docs" / "releases"
            releases.mkdir(parents=True, exist_ok=True)
            (releases / "PATCH-v0.33.2.md").write_text(
                "| # | Title |\n|---|-------|\n"
                "| 532 | manpages: 4 briefs reference docs/user/manpages/gz-validate.md |\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_manpage_alignment(root), [])

    def test_live_operator_doc_outside_releases_still_gates(self) -> None:
        """The exemption is scoped to docs/releases/, not to docs/ generally."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            user_docs = root / "docs" / "user"
            user_docs.mkdir(parents=True, exist_ok=True)
            (user_docs / "runbook.md").write_text(
                "See `docs/user/manpages/gz-validate.md`\n", encoding="utf-8"
            )
            errors = audit_manpage_alignment(root)

        self.assertEqual(len(errors), 1, f"live operator docs must still gate, got {errors}")
        self.assertIn("gz-validate.md", errors[0].message)

    def test_skill_surface_is_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / ".gzkit" / "skills" / "gz-demo"
            skill.mkdir(parents=True, exist_ok=True)
            (skill / "SKILL.md").write_text(
                "Manpage: `docs/user/manpages/gz-issue.md`\n", encoding="utf-8"
            )
            errors = audit_manpage_alignment(root)

        self.assertEqual(len(errors), 1, f"skill surface must be scanned, got {errors}")
        self.assertIn("gz-issue.md", errors[0].message)


class ManpageAlignmentRepoClean(unittest.TestCase):
    """The live tree carries no gz-<verb>.md manpage references (GHI #532 drain gate)."""

    def test_repo_has_no_gz_prefixed_manpage_refs(self) -> None:
        errors = audit_manpage_alignment(_PROJECT_ROOT)
        self.assertFalse(
            errors,
            msg=(
                "Operator docs / open briefs / skills reference the non-existent "
                "manpages/gz-<verb>.md convention. Drop the gz- prefix.\n"
                + "\n".join(f"  {e.artifact}: {e.message}" for e in errors)
            ),
        )


if __name__ == "__main__":
    unittest.main()
