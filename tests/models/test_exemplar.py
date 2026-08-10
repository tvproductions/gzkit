"""Pydantic model tests for ExemplarProject, ExcludedPath, VacantCell, ExemplarCorpus.

Covers:
- REQ-0.0.27-02-01 (loader returns frozen ExemplarCorpus)
- REQ-0.0.27-02-02 (SHA40 validation)
- REQ-0.0.27-02-03 (path-filter requiredness)
- REQ-0.0.27-02-04 (VacantCell shape + field bounds)
- REQ-0.0.27-02-07 (frozen + extra='forbid' on every model; mutation raises)
- REQ-0.0.27-02-08 (JSON Schema parity + ExemplarCorpus shape)
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.traceability import covers  # noqa: F401


def _minimal_excluded_path() -> dict[str, object]:
    return {"glob": "src/example/generated/**", "exclusion_rationale": "Generated code."}


def _minimal_project(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "name": "example-project",
        "canonical_url": "https://github.com/example/project",
        "commit_sha": "a" * 40,
        "archetypal_cell": 3,
        "cell_label": "HTTP client library",
        "included_paths": ("src/example/core/**",),
        "excluded_paths_with_rationale": (),
        "path_filter_rationale": "Core implementation only; excludes generated code.",
        "longevity_evidence": "10+ years of active development.",
        "maintenance_health_evidence": "Released 2024-01-15.",
        "practitioner_reputation_citation": "Cited in PEP 3156.",
        "pure_python_loc_ratio": 0.95,
        "craftsmanship_signal_narrative": "Clean separation of concerns.",
        "project_doctrine_fitness_narrative": "Pure Python; stdlib-first design.",
    }
    base.update(overrides)
    return base


def _minimal_corpus(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "schema_version": "1.0.0",
        "corpus_revision": 1,
        "projects": [_minimal_project()],
        "vacant_cells": [],
    }
    base.update(overrides)
    return base


class TestExemplarProjectFrozenContract(unittest.TestCase):
    """REQ-0.0.27-02-07: frozen=True + extra='forbid' on every model."""

    @covers("REQ-0.0.27-02-07")
    def test_exemplar_project_model_config_frozen(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        self.assertTrue(ExemplarProject.model_config.get("frozen"))

    @covers("REQ-0.0.27-02-07")
    def test_exemplar_project_model_config_extra_forbid(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        self.assertEqual(ExemplarProject.model_config.get("extra"), "forbid")

    @covers("REQ-0.0.27-02-07")
    def test_excluded_path_model_config_frozen(self) -> None:
        from gzkit.models.exemplar import ExcludedPath

        self.assertTrue(ExcludedPath.model_config.get("frozen"))

    @covers("REQ-0.0.27-02-07")
    def test_excluded_path_model_config_extra_forbid(self) -> None:
        from gzkit.models.exemplar import ExcludedPath

        self.assertEqual(ExcludedPath.model_config.get("extra"), "forbid")

    @covers("REQ-0.0.27-02-07")
    def test_vacant_cell_model_config_frozen(self) -> None:
        from gzkit.models.exemplar import VacantCell

        self.assertTrue(VacantCell.model_config.get("frozen"))

    @covers("REQ-0.0.27-02-07")
    def test_vacant_cell_model_config_extra_forbid(self) -> None:
        from gzkit.models.exemplar import VacantCell

        self.assertEqual(VacantCell.model_config.get("extra"), "forbid")

    @covers("REQ-0.0.27-02-07")
    def test_exemplar_corpus_model_config_frozen(self) -> None:
        from gzkit.models.exemplar import ExemplarCorpus

        self.assertTrue(ExemplarCorpus.model_config.get("frozen"))

    @covers("REQ-0.0.27-02-07")
    def test_exemplar_corpus_model_config_extra_forbid(self) -> None:
        from gzkit.models.exemplar import ExemplarCorpus

        self.assertEqual(ExemplarCorpus.model_config.get("extra"), "forbid")

    @covers("REQ-0.0.27-02-07")
    def test_mutation_of_exemplar_project_field_raises(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        proj = ExemplarProject(**_minimal_project())
        with self.assertRaises(ValidationError):
            proj.name = "altered"  # ty: ignore[invalid-assignment]

    @covers("REQ-0.0.27-02-07")
    def test_extra_key_on_exemplar_project_raises(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(unknown_field="extra"))


class TestExemplarProjectShaValidation(unittest.TestCase):
    """REQ-0.0.27-02-02: commit_sha must be exactly 40 lowercase hex chars."""

    @covers("REQ-0.0.27-02-02")
    def test_branch_name_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(commit_sha="main"))

    @covers("REQ-0.0.27-02-02")
    def test_tag_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(commit_sha="v1.0"))

    @covers("REQ-0.0.27-02-02")
    def test_short_hash_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(commit_sha="abc1234"))

    @covers("REQ-0.0.27-02-02")
    def test_39_char_hex_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(commit_sha="a" * 39))

    @covers("REQ-0.0.27-02-02")
    def test_41_char_hex_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(commit_sha="a" * 41))

    @covers("REQ-0.0.27-02-02")
    def test_non_hex_40_char_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        sha = "g" + "a" * 39  # 'g' is not a hex character
        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(commit_sha=sha))

    @covers("REQ-0.0.27-02-02")
    def test_valid_40_char_lowercase_hex_accepted(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        proj = ExemplarProject(**_minimal_project(commit_sha="a" * 40))
        self.assertEqual(proj.commit_sha, "a" * 40)


class TestExemplarProjectPathFilterRequired(unittest.TestCase):
    """REQ-0.0.27-02-03: path filter fields are required and non-empty."""

    @covers("REQ-0.0.27-02-03")
    def test_empty_included_paths_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(included_paths=()))

    @covers("REQ-0.0.27-02-03")
    def test_missing_excluded_paths_raises(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        kwargs = _minimal_project()
        del kwargs["excluded_paths_with_rationale"]
        with self.assertRaises(ValidationError):
            ExemplarProject(**kwargs)

    @covers("REQ-0.0.27-02-03")
    def test_empty_string_path_filter_rationale_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(path_filter_rationale=""))

    @covers("REQ-0.0.27-02-03")
    def test_excluded_path_empty_glob_rejected(self) -> None:
        from gzkit.models.exemplar import ExcludedPath

        with self.assertRaises(ValidationError):
            ExcludedPath(glob="", exclusion_rationale="Some reason.")

    @covers("REQ-0.0.27-02-03")
    def test_excluded_path_empty_rationale_rejected(self) -> None:
        from gzkit.models.exemplar import ExcludedPath

        with self.assertRaises(ValidationError):
            ExcludedPath(glob="tests/**", exclusion_rationale="")


class TestExemplarProjectFieldBounds(unittest.TestCase):
    """Defense-in-depth field bounds supporting REQ-0.0.27-02-04."""

    @covers("REQ-0.0.27-02-04")
    def test_archetypal_cell_zero_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(archetypal_cell=0))

    @covers("REQ-0.0.27-02-04")
    def test_archetypal_cell_eleven_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(archetypal_cell=11))

    @covers("REQ-0.0.27-02-04")
    def test_archetypal_cell_negative_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(archetypal_cell=-1))

    @covers("REQ-0.0.27-02-04")
    def test_pure_python_loc_ratio_negative_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(pure_python_loc_ratio=-0.1))

    @covers("REQ-0.0.27-02-04")
    def test_pure_python_loc_ratio_above_one_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        with self.assertRaises(ValidationError):
            ExemplarProject(**_minimal_project(pure_python_loc_ratio=1.5))


class TestVacantCellModel(unittest.TestCase):
    """REQ-0.0.27-02-04: VacantCell requires archetypal_cell and vacancy_rationale."""

    @covers("REQ-0.0.27-02-04")
    def test_vacant_cell_requires_archetypal_cell_and_rationale(self) -> None:
        from gzkit.models.exemplar import VacantCell

        vc = VacantCell(archetypal_cell=7, vacancy_rationale="No qualifying project found.")
        self.assertEqual(vc.archetypal_cell, 7)
        self.assertEqual(vc.vacancy_rationale, "No qualifying project found.")

    @covers("REQ-0.0.27-02-04")
    def test_vacant_cell_empty_rationale_rejected(self) -> None:
        from gzkit.models.exemplar import VacantCell

        with self.assertRaises(ValidationError):
            VacantCell(archetypal_cell=7, vacancy_rationale="")

    @covers("REQ-0.0.27-02-04")
    def test_vacant_cell_archetypal_cell_bounds_enforced(self) -> None:
        from gzkit.models.exemplar import VacantCell

        with self.assertRaises(ValidationError):
            VacantCell(archetypal_cell=0, vacancy_rationale="Some rationale.")
        with self.assertRaises(ValidationError):
            VacantCell(archetypal_cell=11, vacancy_rationale="Some rationale.")


class TestExemplarCorpusShape(unittest.TestCase):
    """REQ-0.0.27-02-08: ExemplarCorpus wraps schema_version, corpus_revision, projects, cells."""

    @covers("REQ-0.0.27-02-08")
    def test_exemplar_corpus_fields_present(self) -> None:
        from gzkit.models.exemplar import ExemplarCorpus, ExemplarProject, VacantCell

        proj = ExemplarProject(**_minimal_project())
        vc = VacantCell(archetypal_cell=7, vacancy_rationale="No candidate found.")
        corpus = ExemplarCorpus(
            schema_version="1.0.0",
            corpus_revision=1,
            projects=(proj,),
            vacant_cells=(vc,),
        )
        self.assertEqual(corpus.schema_version, "1.0.0")
        self.assertEqual(corpus.corpus_revision, 1)
        self.assertIsInstance(corpus.projects, tuple)
        self.assertIsInstance(corpus.vacant_cells, tuple)

    @covers("REQ-0.0.27-02-08")
    def test_exemplar_corpus_empty_schema_version_rejected(self) -> None:
        from gzkit.models.exemplar import ExemplarCorpus

        with self.assertRaises(ValidationError):
            ExemplarCorpus(
                schema_version="",
                corpus_revision=1,
                projects=(),
                vacant_cells=(),
            )

    @covers("REQ-0.0.27-02-08")
    def test_exemplar_corpus_revision_ge_one(self) -> None:
        from gzkit.models.exemplar import ExemplarCorpus

        with self.assertRaises(ValidationError):
            ExemplarCorpus(
                schema_version="1.0.0",
                corpus_revision=0,
                projects=(),
                vacant_cells=(),
            )


class TestExemplarCorpusLoader(unittest.TestCase):
    """REQ-0.0.27-02-01, REQ-0.0.27-02-07: loader returns frozen ExemplarCorpus."""

    @covers("REQ-0.0.27-02-01")
    def test_loader_returns_exemplar_corpus(self) -> None:
        from gzkit.models.exemplar import ExemplarCorpus, load_corpus

        with tempfile.TemporaryDirectory() as tmp:
            corpus_path = Path(tmp) / "exemplar_corpus.json"
            corpus_path.write_text(json.dumps(_minimal_corpus()), encoding="utf-8")
            result = load_corpus(corpus_path)
            self.assertIsInstance(result, ExemplarCorpus)

    @covers("REQ-0.0.27-02-07")
    def test_loader_returns_frozen_tuple_of_projects(self) -> None:
        from gzkit.models.exemplar import ExemplarProject, load_corpus

        with tempfile.TemporaryDirectory() as tmp:
            corpus_path = Path(tmp) / "exemplar_corpus.json"
            corpus_path.write_text(json.dumps(_minimal_corpus()), encoding="utf-8")
            result = load_corpus(corpus_path)
            self.assertIsInstance(result.projects, tuple)
            self.assertIsInstance(result.projects[0], ExemplarProject)

    @covers("REQ-0.0.27-02-07")
    def test_loader_frozen_corpus_mutation_raises(self) -> None:
        from gzkit.models.exemplar import load_corpus

        with tempfile.TemporaryDirectory() as tmp:
            corpus_path = Path(tmp) / "exemplar_corpus.json"
            corpus_path.write_text(json.dumps(_minimal_corpus()), encoding="utf-8")
            result = load_corpus(corpus_path)
            with self.assertRaises(ValidationError):
                result.schema_version = "2.0.0"  # ty: ignore[invalid-assignment]

    @covers("REQ-0.0.27-02-01")
    def test_loader_malformed_json_raises_validation_error(self) -> None:
        from gzkit.models.exemplar import load_corpus

        with tempfile.TemporaryDirectory() as tmp:
            corpus_path = Path(tmp) / "exemplar_corpus.json"
            # Missing required fields (commit_sha is not a valid 40-char hex)
            bad_data = {
                "schema_version": "1.0.0",
                "corpus_revision": 1,
                "projects": [{"name": "bad", "commit_sha": "notasha"}],
                "vacant_cells": [],
            }
            corpus_path.write_text(json.dumps(bad_data), encoding="utf-8")
            with self.assertRaises(ValidationError):
                load_corpus(corpus_path)


class TestJsonSchemaParity(unittest.TestCase):
    """REQ-0.0.27-02-08: JSON Schema at exemplar_corpus.json mirrors Pydantic model."""

    _SCHEMA_PATH = (
        Path(__file__).parent.parent.parent / "src" / "gzkit" / "schemas" / "exemplar_corpus.json"
    )

    @covers("REQ-0.0.27-02-08")
    def test_schema_declares_draft_2020_12(self) -> None:
        schema = json.loads(self._SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema.get("$schema"), "https://json-schema.org/draft/2020-12/schema")

    @covers("REQ-0.0.27-02-08")
    def test_schema_project_properties_match_pydantic_fields(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        schema = json.loads(self._SCHEMA_PATH.read_text(encoding="utf-8"))
        project_schema = schema["$defs"]["ExemplarProject"]
        schema_props = set(project_schema["properties"].keys())
        pydantic_fields = set(ExemplarProject.model_fields.keys())
        self.assertEqual(schema_props, pydantic_fields)

    @covers("REQ-0.0.27-02-08")
    def test_schema_project_required_matches_pydantic_required(self) -> None:
        from gzkit.models.exemplar import ExemplarProject

        schema = json.loads(self._SCHEMA_PATH.read_text(encoding="utf-8"))
        project_schema = schema["$defs"]["ExemplarProject"]
        schema_required = set(project_schema["required"])
        pydantic_required = {
            name for name, field in ExemplarProject.model_fields.items() if field.is_required()
        }
        self.assertEqual(schema_required, pydantic_required)

    @covers("REQ-0.0.27-02-08")
    def test_schema_commit_sha_pattern(self) -> None:
        schema = json.loads(self._SCHEMA_PATH.read_text(encoding="utf-8"))
        project_schema = schema["$defs"]["ExemplarProject"]
        sha_prop = project_schema["properties"]["commit_sha"]
        self.assertEqual(sha_prop.get("pattern"), "^[0-9a-f]{40}$")

    @covers("REQ-0.0.27-02-08")
    def test_schema_additional_properties_false_on_all_objects(self) -> None:
        schema = json.loads(self._SCHEMA_PATH.read_text(encoding="utf-8"))
        # Top-level corpus object
        self.assertFalse(schema.get("additionalProperties", True))
        # Each $defs object
        for def_name in ("ExemplarProject", "ExcludedPath", "VacantCell"):
            with self.subTest(def_name=def_name):
                def_schema = schema["$defs"][def_name]
                self.assertFalse(
                    def_schema.get("additionalProperties", True),
                    msg=f"$defs.{def_name} missing additionalProperties: false",
                )


class TestValidateDocumentsCorpusIntegration(unittest.TestCase):
    """REQ-0.0.27-02-08: gz validate --documents surfaces corpus schema drift."""

    # Minimal manifest JSON that satisfies the existing manifest-walk logic
    _MINIMAL_MANIFEST: dict[str, object] = {
        "schema": "gzkit.manifest.v2",
        "structure": {
            "source_root": "src",
            "tests_root": "tests",
            "docs_root": "docs",
            "design_root": "docs/design",
        },
        "artifacts": {},
        "data": {},
        "ops": {},
        "thresholds": {},
        "control_surfaces": {},
        "verification": {},
        "gates": {},
        "rules": {},
    }

    def _write_manifest(self, root: Path) -> None:
        """Write a minimal .gzkit/manifest.json so the existing walk doesn't early-exit."""
        gzkit_dir = root / ".gzkit"
        gzkit_dir.mkdir(parents=True, exist_ok=True)
        (gzkit_dir / "manifest.json").write_text(
            json.dumps(self._MINIMAL_MANIFEST), encoding="utf-8"
        )

    def _write_corpus(self, root: Path, data: object) -> None:
        """Write data/exemplar_corpus.json."""
        data_dir = root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "exemplar_corpus.json").write_text(json.dumps(data), encoding="utf-8")

    def _write_corpus_raw(self, root: Path, raw: str) -> None:
        """Write raw bytes to data/exemplar_corpus.json (for malformed-JSON tests)."""
        data_dir = root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "exemplar_corpus.json").write_text(raw, encoding="utf-8")

    @covers("REQ-0.0.27-02-08")
    def test_absent_corpus_is_noop(self) -> None:
        """When data/exemplar_corpus.json is absent, no corpus errors are returned."""
        from gzkit.commands.validate_cmd import _validate_manifest_documents

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root)
            # Corpus file intentionally not written
            errors = _validate_manifest_documents(root)
            corpus_errors = [e for e in errors if e.type == "exemplar_corpus"]
            self.assertEqual(corpus_errors, [])

    @covers("REQ-0.0.27-02-08")
    def test_valid_corpus_passes(self) -> None:
        """When data/exemplar_corpus.json has a valid corpus, no corpus errors are returned."""
        from gzkit.commands.validate_cmd import _validate_manifest_documents

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root)
            self._write_corpus(root, _minimal_corpus())
            errors = _validate_manifest_documents(root)
            corpus_errors = [e for e in errors if e.type == "exemplar_corpus"]
            self.assertEqual(corpus_errors, [])

    @covers("REQ-0.0.27-02-08")
    def test_malformed_json_fails_closed(self) -> None:
        """When exemplar_corpus.json contains invalid JSON, at least one error references it."""
        from gzkit.commands.validate_cmd import _validate_manifest_documents

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root)
            self._write_corpus_raw(root, "{not valid json")
            errors = _validate_manifest_documents(root)
            corpus_errors = [e for e in errors if e.type == "exemplar_corpus"]
            self.assertGreater(len(corpus_errors), 0)
            self.assertTrue(
                any("exemplar_corpus.json" in e.artifact for e in corpus_errors),
                msg="Expected at least one error referencing exemplar_corpus.json",
            )

    @covers("REQ-0.0.27-02-08")
    def test_schema_drift_missing_required_field_fails_closed(self) -> None:
        """When a projects entry is missing commit_sha, at least one error is returned."""
        from gzkit.commands.validate_cmd import _validate_manifest_documents

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root)
            bad_project = _minimal_project()
            del bad_project["commit_sha"]
            self._write_corpus(root, _minimal_corpus(projects=[bad_project]))
            errors = _validate_manifest_documents(root)
            corpus_errors = [e for e in errors if e.type == "exemplar_corpus"]
            self.assertGreater(len(corpus_errors), 0)

    @covers("REQ-0.0.27-02-08")
    def test_schema_drift_non_sha_commit_sha_fails_closed(self) -> None:
        """When commit_sha is 'main' (not a valid SHA), at least one error references the field."""
        from gzkit.commands.validate_cmd import _validate_manifest_documents

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root)
            self._write_corpus(
                root, _minimal_corpus(projects=[_minimal_project(commit_sha="main")])
            )
            errors = _validate_manifest_documents(root)
            corpus_errors = [e for e in errors if e.type == "exemplar_corpus"]
            self.assertGreater(len(corpus_errors), 0)

    @covers("REQ-0.0.27-02-08")
    def test_extra_key_fails_closed(self) -> None:
        """When a projects entry contains an extra field, validation fails (extra='forbid')."""
        from gzkit.commands.validate_cmd import _validate_manifest_documents

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root)
            self._write_corpus(root, _minimal_corpus(projects=[_minimal_project(random_extra="x")]))
            errors = _validate_manifest_documents(root)
            corpus_errors = [e for e in errors if e.type == "exemplar_corpus"]
            self.assertGreater(len(corpus_errors), 0)


if __name__ == "__main__":
    unittest.main()
