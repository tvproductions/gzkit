"""Doc-surface parity audit (GHI #418).

Fail-closed if any .md file lingers under docs/user/commands/ after
the canonical surface was consolidated to docs/user/manpages/.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.doc_surface_parity import audit_doc_surface_parity


class TestDocSurfaceParity(unittest.TestCase):
    def test_clean_project_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user" / "manpages").mkdir(parents=True)
            (root / "docs" / "user" / "manpages" / "validate.md").write_text(
                "# gz validate\n", encoding="utf-8"
            )
            errors = audit_doc_surface_parity(root)
            self.assertEqual(errors, [])

    def test_decommissioned_dir_with_md_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user" / "commands").mkdir(parents=True)
            (root / "docs" / "user" / "commands" / "stale.md").write_text(
                "# stale\n", encoding="utf-8"
            )
            errors = audit_doc_surface_parity(root)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, "doc_surface_parity")
            self.assertIn("decommissioned", errors[0].message)

    def test_empty_decommissioned_dir_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user" / "commands").mkdir(parents=True)
            errors = audit_doc_surface_parity(root)
            self.assertEqual(errors, [])

    def test_multiple_stale_files_each_get_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cmds = root / "docs" / "user" / "commands"
            cmds.mkdir(parents=True)
            (cmds / "a.md").write_text("a\n", encoding="utf-8")
            (cmds / "b.md").write_text("b\n", encoding="utf-8")
            errors = audit_doc_surface_parity(root)
            self.assertEqual(len(errors), 2)

    def test_real_project_has_no_commands_dir(self) -> None:
        from gzkit.commands.common import get_project_root

        root = get_project_root()
        errors = audit_doc_surface_parity(root)
        self.assertEqual(errors, [], f"docs/user/commands/ still has .md files: {errors}")
