"""Regression tests for PyInstaller packaging paths."""

import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "gz.spec"


class TestPyInstallerSpec(unittest.TestCase):
    """Ensure packaged data files point at real repository paths."""

    def _load_spec_namespace(self) -> dict[str, object]:
        prefix, _, _ = SPEC.read_text(encoding="utf-8").partition("a = Analysis(")
        namespace: dict[str, object] = {}
        cwd = Path.cwd()
        try:
            os.chdir(ROOT)
            exec(prefix, namespace)  # noqa: S102
        finally:
            os.chdir(cwd)
        return namespace

    def test_template_data_paths_match_repository_templates(self) -> None:
        """Template datas entries should map directly to markdown templates."""
        namespace = self._load_spec_namespace()
        expected = {
            (str(path), "gzkit/templates")
            for path in Path("src/gzkit/templates").iterdir()
            if path.suffix == ".md"
        }
        templates = namespace["TEMPLATES"]
        assert isinstance(templates, list)
        actual = set(templates)
        self.assertSetEqual(actual, expected)

    def test_schema_data_paths_match_repository_schemas(self) -> None:
        """Schema datas entries should map directly to JSON schema files."""
        namespace = self._load_spec_namespace()
        expected = {
            (str(path), "gzkit/schemas")
            for path in Path("src/gzkit/schemas").iterdir()
            if path.suffix == ".json"
        }
        schemas = namespace["SCHEMAS"]
        assert isinstance(schemas, list)
        actual = set(schemas)
        self.assertSetEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
