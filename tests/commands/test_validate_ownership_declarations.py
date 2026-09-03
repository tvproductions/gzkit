"""Tests for the `.gzkit/ownership/*.json` validator in `gz validate --documents`.

REQ-0.35.0-04-08 [support]: `gz validate --documents` must admit the shape of
every section-ownership declaration -- schema-validate against
`src/gzkit/schemas/section_ownership.json`, then construct
`OwnershipDeclaration`. Step-4b adversary finding 3 (OBPI-0.35.0-04):
`--documents` never read `.gzkit/ownership/*.json`, so a malformed declaration
produced `documents_error_count 0` and the REQ's proof channel was vacuous.

These tests exercise `_validate_ownership_declarations` directly (isolation)
and `_validate_manifest_documents` / the `gz validate --documents` CLI path
(wiring) so the errors are proven to actually reach the scope's output, not
merely a helper that nothing calls.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.commands.common import CliRunner, _quick_init

_WELL_FORMED_DECLARATION = {
    "surface": "AGENTS.md",
    "sections": {
        "project-identity": "corpus-owned",
        "local-agent-rules": "unowned",
    },
    "unowned_byte_floor": 42,
    "measured_at": "2026-09-01T00:00:00Z",
    "floor_event_id": "section-ownership-genesis-AGENTS.md-test",
}


def _write_ownership_file(root: Path, name: str, content: str) -> Path:
    ownership_dir = root / ".gzkit" / "ownership"
    ownership_dir.mkdir(parents=True, exist_ok=True)
    path = ownership_dir / name
    path.write_text(content, encoding="utf-8")
    return path


class TestValidateOwnershipDeclarationsHelper(unittest.TestCase):
    """Unit tests against `_validate_ownership_declarations` in isolation."""

    def test_well_formed_declaration_produces_no_errors(self) -> None:
        """The control: a well-formed declaration must not raise -- otherwise
        the negative tests below prove nothing."""
        from gzkit.commands.validate_cmd import _validate_ownership_declarations

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ownership_file(root, "AGENTS.md.json", json.dumps(_WELL_FORMED_DECLARATION))
            errors = _validate_ownership_declarations(root)
            self.assertEqual(
                errors, [], msg=f"well-formed declaration must not raise; got {errors}"
            )

    def test_absent_ownership_directory_produces_no_errors(self) -> None:
        """No `.gzkit/ownership/` directory at all -> no errors (not yet authored)."""
        from gzkit.commands.validate_cmd import _validate_ownership_declarations

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            errors = _validate_ownership_declarations(root)
            self.assertEqual(errors, [])

    def test_malformed_json_produces_error_naming_the_file(self) -> None:
        """Malformed JSON must produce an `ownership_declaration` error naming the file."""
        from gzkit.commands.validate_cmd import _validate_ownership_declarations

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ownership_file(root, "AGENTS.md.json", "{not valid json")
            errors = _validate_ownership_declarations(root)
            self.assertEqual(len(errors), 1, msg=f"expected one error; got {errors}")
            self.assertEqual(errors[0].type, "ownership_declaration")
            self.assertIn("AGENTS.md.json", errors[0].artifact)

    def test_missing_required_key_produces_error(self) -> None:
        """A declaration missing `floor_event_id` (schema-required) must fail closed."""
        from gzkit.commands.validate_cmd import _validate_ownership_declarations

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            broken = dict(_WELL_FORMED_DECLARATION)
            del broken["floor_event_id"]
            _write_ownership_file(root, "AGENTS.md.json", json.dumps(broken))
            errors = _validate_ownership_declarations(root)
            self.assertEqual(len(errors), 1, msg=f"expected one error; got {errors}")
            self.assertEqual(errors[0].type, "ownership_declaration")

    def test_section_value_outside_closed_enum_produces_error(self) -> None:
        """A section value outside {corpus-owned, unowned} must fail closed."""
        from gzkit.commands.validate_cmd import _validate_ownership_declarations

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            broken = json.loads(json.dumps(_WELL_FORMED_DECLARATION))
            broken["sections"]["project-identity"] = "orphaned"
            _write_ownership_file(root, "AGENTS.md.json", json.dumps(broken))
            errors = _validate_ownership_declarations(root)
            self.assertEqual(len(errors), 1, msg=f"expected one error; got {errors}")
            self.assertEqual(errors[0].type, "ownership_declaration")


class TestValidateOwnershipDeclarationsWiring(unittest.TestCase):
    """Wiring tests: errors must reach `gz validate --documents`, not just the helper."""

    def test_errors_reach_validate_manifest_documents(self) -> None:
        """`_validate_manifest_documents` -- the function the `documents` scope
        runner calls -- must include ownership_declaration errors."""
        from gzkit.commands.validate_cmd import _validate_manifest_documents

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_dir = root / ".gzkit"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "manifest.json").write_text(
                json.dumps({"schema": "gzkit.manifest.v2", "artifacts": {}}),
                encoding="utf-8",
            )
            _write_ownership_file(root, "AGENTS.md.json", "{not valid json")
            errors = _validate_manifest_documents(root)
            ownership_errors = [e for e in errors if e.type == "ownership_declaration"]
            self.assertEqual(
                len(ownership_errors),
                1,
                msg=f"expected one ownership_declaration error in documents scope; got {errors}",
            )

    def test_errors_reach_gz_validate_documents_cli_output(self) -> None:
        """A malformed declaration must surface in `gz validate --documents` CLI output.

        # output-contract: proves the ownership_declaration error message
        # (not merely the helper's return value) reaches the CLI surface
        # REQ-0.35.0-04-08 names by name -- the exact gap the Step-4b
        # adversary's finding 3 demonstrated.
        """
        from gzkit.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_ownership_file(Path.cwd(), "AGENTS.md.json", "{not valid json")
            result = runner.invoke(main, ["validate", "--documents"])
            self.assertIn(
                "AGENTS.md.json",
                result.output,
                msg=f"expected the ownership artifact path in CLI output; got:\n{result.output}",
            )
            self.assertIn(
                "REQ-0.35.0-04-08",
                result.output,
                msg=(
                    "expected the ownership_declaration error's recovery prose "
                    f"(citing REQ-0.35.0-04-08) in CLI output; got:\n{result.output}"
                ),
            )


if __name__ == "__main__":
    unittest.main()
