"""Tests for gzkit validation engine."""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.validate import (
    extract_headers,
    parse_frontmatter,
    validate_document,
    validate_ledger,
    validate_manifest,
)


class TestParseFrontmatter(unittest.TestCase):
    """Tests for frontmatter parsing."""

    def test_no_frontmatter(self) -> None:
        """Content without frontmatter returns empty dict."""
        content = "# Title\n\nSome content"
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm, {})
        self.assertEqual(body, content)

    def test_with_frontmatter(self) -> None:
        """Content with frontmatter is parsed correctly."""
        content = """---
id: ADR-0.1.0
status: Draft
---

# Title

Content here."""
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm["id"], "ADR-0.1.0")
        self.assertEqual(fm["status"], "Draft")
        self.assertIn("# Title", body)

    def test_quoted_values(self) -> None:
        """Quoted values have quotes removed."""
        content = """---
title: "My Title"
name: 'Single quoted'
---

Body"""
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm["title"], "My Title")
        self.assertEqual(fm["name"], "Single quoted")


class TestExtractHeaders(unittest.TestCase):
    """Tests for header extraction."""

    def test_extracts_h2_headers(self) -> None:
        """Extracts ## level headers."""
        content = """# Title

## Section One

Content

## Section Two

More content

### Subsection

Not extracted"""
        headers = extract_headers(content)
        self.assertEqual(headers, ["Section One", "Section Two"])

    def test_strips_anchors(self) -> None:
        """Strips anchor tags from headers."""
        content = """## Section One {#section-one}

Content"""
        headers = extract_headers(content)
        self.assertEqual(headers, ["Section One"])


class TestValidateDocument(unittest.TestCase):
    """Tests for document validation."""

    def test_missing_file(self) -> None:
        """Missing file returns error."""
        errors = validate_document(Path("/nonexistent.md"), "adr")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "schema")
        self.assertIn("does not exist", errors[0].message)

    def test_valid_adr(self) -> None:
        """Valid ADR passes validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""---
id: ADR-0.1.0
status: Draft
semver: 0.1.0
lane: lite
parent: OBPI-core
date: 2026-01-01
---

# ADR-0.1.0: Test

## Intent

Test intent.

## Decision

Test decision.

## Consequences

Test consequences.

## Decomposition Scorecard

- Data/State: 0
- Logic/Engine: 0
- Interface: 0
- Observability: 0
- Lineage: 0
- Dimension Total: 0
- Baseline Range: 1-2
- Baseline Selected: 1
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 1

## Checklist

- [ ] OBPI-0.1.0-01: Define scope, constraints, and acceptance criteria

## Evidence

Test evidence.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
""")
            f.flush()
            errors = validate_document(Path(f.name), "adr")
            self.assertEqual(errors, [])

    def test_adr_decomposition_checklist_mismatch_fails(self) -> None:
        """Checklist count must match scorecard final target."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""---
id: ADR-0.1.0
status: Draft
semver: 0.1.0
lane: lite
parent: OBPI-core
date: 2026-01-01
---

# ADR-0.1.0: Test

## Intent

Test intent.

## Decision

Test decision.

## Consequences

Test consequences.

## Decomposition Scorecard

- Data/State: 0
- Logic/Engine: 0
- Interface: 0
- Observability: 0
- Lineage: 0
- Dimension Total: 0
- Baseline Range: 1-2
- Baseline Selected: 1
- Split Single-Narrative: 1
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 2

## Checklist

- [ ] OBPI-0.1.0-01: Define scope, constraints, and acceptance criteria

## Evidence

Test evidence.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
""")
            f.flush()
            errors = validate_document(Path(f.name), "adr")
            self.assertTrue(any(e.type == "decomposition" for e in errors))
            self.assertTrue(
                any(
                    "Checklist count must match scorecard final target" in e.message for e in errors
                )
            )

    def test_missing_frontmatter_field(self) -> None:
        """Missing frontmatter field returns error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""---
id: ADR-0.1.0
status: Draft
---

# Title

## Intent
""")
            f.flush()
            errors = validate_document(Path(f.name), "adr")
            # Should have errors for missing semver, lane, parent, date
            self.assertTrue(any(e.field == "semver" for e in errors))

    def test_obpi_frontmatter_id_must_match_filename_stem(self) -> None:
        """OBPI frontmatter id must match the slugified filename stem."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mismatched: short-form id vs slugified filename
            obpi_file = Path(temp_dir) / "OBPI-0.0.14-01-obpi-lock-command.md"
            obpi_file.write_text(
                "---\n"
                "id: OBPI-0.0.14-01\n"
                "parent: ADR-0.0.14-deterministic-obpi-commands\n"
                "item: 1\n"
                "lane: Heavy\n"
                "status: Draft\n"
                "---\n\n# OBPI-0.0.14-01: gz obpi lock command\n",
                encoding="utf-8",
            )
            errors = validate_document(obpi_file, "obpi")
            id_errors = [e for e in errors if e.field == "id" and "does not match" in e.message]
            self.assertEqual(len(id_errors), 1)
            self.assertIn("OBPI-0.0.14-01-obpi-lock-command", id_errors[0].message)

    def test_obpi_frontmatter_id_matching_stem_passes(self) -> None:
        """OBPI with matching slugified id passes stem check."""
        with tempfile.TemporaryDirectory() as temp_dir:
            obpi_file = Path(temp_dir) / "OBPI-0.0.14-01-obpi-lock-command.md"
            obpi_file.write_text(
                "---\n"
                "id: OBPI-0.0.14-01-obpi-lock-command\n"
                "parent: ADR-0.0.14-deterministic-obpi-commands\n"
                "item: 1\n"
                "lane: Heavy\n"
                "status: Draft\n"
                "---\n\n# OBPI-0.0.14-01: gz obpi lock command\n",
                encoding="utf-8",
            )
            errors = validate_document(obpi_file, "obpi")
            id_errors = [e for e in errors if e.field == "id" and "does not match" in e.message]
            self.assertEqual(len(id_errors), 0)

    def test_missing_section(self) -> None:
        """Missing required section returns error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""---
id: ADR-0.1.0
status: Draft
semver: 0.1.0
lane: lite
parent: OBPI-core
date: 2026-01-01
---

# Title

## Intent

Content but missing Decision section.
""")
            f.flush()
            errors = validate_document(Path(f.name), "adr")
            self.assertTrue(any(e.field == "Decision" for e in errors))


class TestValidateManifest(unittest.TestCase):
    """Tests for manifest validation."""

    def test_missing_manifest(self) -> None:
        """Missing manifest returns error."""
        errors = validate_manifest(Path("/nonexistent/manifest.json"))
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0].message)

    def test_valid_manifest(self) -> None:
        """Valid manifest passes validation."""
        import json

        manifest = {
            "schema": "gzkit.manifest.v2",
            "structure": {
                "source_root": "src",
                "tests_root": "tests",
                "docs_root": "docs",
                "design_root": "design",
            },
            "artifacts": {
                "prd": {"path": "design/prd", "schema": "gzkit.prd.v1"},
                "constitution": {"path": "design/constitutions", "schema": "gzkit.constitution.v1"},
                "obpi": {"path": "design/adr", "schema": "gzkit.obpi.v1"},
                "adr": {"path": "design/adr", "schema": "gzkit.adr.v1"},
            },
            "data": {
                "eval_datasets": "data/eval",
                "eval_schema": "data/schemas/eval_dataset.schema.json",
                "baselines": "artifacts/baselines",
                "schemas": "data/schemas",
            },
            "ops": {
                "chores": "config/chores",
                "receipts": "artifacts/receipts",
                "proofs": "artifacts/proofs",
            },
            "thresholds": {
                "coverage_floor": 40.0,
                "eval_regression_delta": 0.05,
                "function_lines": 50,
                "module_lines": 600,
                "class_lines": 300,
            },
            "control_surfaces": {
                "agents_md": "AGENTS.md",
                "claude_md": "CLAUDE.md",
                "hooks": ".claude/hooks",
                "skills": ".gzkit/skills",
                "claude_skills": ".claude/skills",
                "codex_skills": ".agents/skills",
                "copilot_skills": ".github/skills",
            },
            "verification": {
                "lint": "uv run gz lint",
                "format": "uv run gz format",
                "typecheck": "uv run gz typecheck",
                "test": "uv run gz test",
                "docs": "uv run mkdocs build --strict",
                "bdd": "uv run -m behave features/",
            },
            "gates": {
                "lite": [1, 2, 5],
                "heavy": [1, 2, 3, 4, 5],
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(manifest, f)
            f.flush()
            errors = validate_manifest(Path(f.name))
            self.assertEqual(errors, [])


class TestValidateLedger(unittest.TestCase):
    """Tests for ledger validation."""

    def test_missing_ledger(self) -> None:
        """Missing ledger returns error."""
        errors = validate_ledger(Path("/nonexistent/ledger.jsonl"))
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "ledger")
        self.assertIn("does not exist", errors[0].message)

    def test_valid_ledger(self) -> None:
        """Valid ledger events pass validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            entries = [
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "project_init",
                    "id": "gzkit",
                    "ts": "2026-02-14T00:00:00+00:00",
                    "mode": "lite",
                },
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "adr_created",
                    "id": "ADR-0.3.0",
                    "ts": "2026-02-14T00:00:01+00:00",
                    "lane": "heavy",
                },
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "audit_receipt_emitted",
                    "id": "ADR-0.3.0",
                    "ts": "2026-02-14T00:00:02+00:00",
                    "receipt_event": "completed",
                    "attestor": "human:jeff",
                    "evidence": {"scope": "OBPI-0.3.0-04"},
                },
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "obpi_receipt_emitted",
                    "id": "OBPI-0.3.0-04-demo",
                    "parent": "ADR-0.3.0",
                    "ts": "2026-02-14T00:00:03+00:00",
                    "receipt_event": "validated",
                    "attestor": "human:jeff",
                    "evidence": {
                        "acceptance": "observed",
                        "parent_lane": "heavy",
                        "attestation_requirement": "required",
                        "scope_audit": {
                            "allowlist": ["docs/design/adr/pre-release/ADR-0.3.0/**"],
                            "changed_files": [
                                "docs/design/adr/pre-release/ADR-0.3.0/obpis/OBPI-0.3.0-04-demo.md"
                            ],
                            "out_of_scope_files": [],
                        },
                        "git_sync_state": {
                            "branch": "main",
                            "remote": "origin",
                            "head": "abc1234",
                            "remote_head": "abc1234",
                            "dirty": False,
                            "ahead": 0,
                            "behind": 0,
                            "diverged": False,
                            "actions": ["git fetch --prune origin"],
                            "warnings": [],
                            "blockers": [],
                        },
                        "recorder_source": "hook:auto",
                        "recorder_warnings": [],
                        "req_proof_inputs": [
                            {
                                "name": "key_proof",
                                "kind": "command",
                                "source": "uv run gz adr status ADR-0.3.0 --json",
                                "status": "present",
                                "scope": "OBPI-0.3.0-04-demo",
                            }
                        ],
                    },
                },
            ]
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
            f.flush()
            errors = validate_ledger(Path(f.name))
            self.assertEqual(errors, [])

    def test_invalid_obpi_req_proof_inputs_rejected(self) -> None:
        """Malformed nested req_proof_inputs fail ledger validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_receipt_emitted",
                        "id": "OBPI-0.3.0-04-demo",
                        "parent": "ADR-0.3.0",
                        "ts": "2026-02-14T00:00:03+00:00",
                        "receipt_event": "completed",
                        "attestor": "human:jeff",
                        "evidence": {
                            "req_proof_inputs": [
                                {
                                    "name": "key_proof",
                                    "kind": "unknown",
                                    "source": "",
                                    "status": "done",
                                }
                            ]
                        },
                    }
                )
                + "\n"
            )
            f.flush()
            errors = validate_ledger(Path(f.name))
            self.assertTrue(
                any("req_proof_inputs" in error.field for error in errors if error.field)
            )

    def test_invalid_obpi_req_proof_optional_fields_rejected(self) -> None:
        """Optional proof-input metadata must be non-empty strings when present."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_receipt_emitted",
                        "id": "OBPI-0.3.0-04-demo",
                        "parent": "ADR-0.3.0",
                        "ts": "2026-02-14T00:00:03+00:00",
                        "receipt_event": "completed",
                        "attestor": "human:jeff",
                        "evidence": {
                            "req_proof_inputs": [
                                {
                                    "name": "proof_gap",
                                    "kind": "artifact",
                                    "source": "docs/proof.txt",
                                    "status": "missing",
                                    "scope": "",
                                    "gap_reason": 7,
                                }
                            ]
                        },
                    }
                )
                + "\n"
            )
            f.flush()
            errors = validate_ledger(Path(f.name))
            self.assertTrue(
                any(error.field == "evidence.req_proof_inputs[0].scope" for error in errors)
            )
            self.assertTrue(
                any(error.field == "evidence.req_proof_inputs[0].gap_reason" for error in errors)
            )

    def test_invalid_obpi_structured_receipt_context_rejected(self) -> None:
        """Malformed structured scope/git receipt context fails ledger validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_receipt_emitted",
                        "id": "OBPI-0.3.0-04-demo",
                        "parent": "ADR-0.3.0",
                        "ts": "2026-02-14T00:00:03+00:00",
                        "receipt_event": "completed",
                        "attestor": "human:jeff",
                        "evidence": {
                            "scope_audit": {
                                "allowlist": [""],
                                "changed_files": [],
                                "out_of_scope_files": [],
                            },
                            "git_sync_state": {
                                "branch": "main",
                                "remote": "origin",
                                "head": "abc1234",
                                "remote_head": "abc1234",
                                "dirty": "no",
                                "ahead": -1,
                                "behind": 0,
                                "diverged": False,
                                "actions": [],
                                "warnings": [],
                                "blockers": [],
                            },
                        },
                    }
                )
                + "\n"
            )
            f.flush()
            errors = validate_ledger(Path(f.name))
            self.assertTrue(
                any(error.field == "evidence.scope_audit.allowlist[0]" for error in errors)
            )
            self.assertTrue(any(error.field == "evidence.git_sync_state.dirty" for error in errors))
            self.assertTrue(any(error.field == "evidence.git_sync_state.ahead" for error in errors))

    def test_invalid_json_line(self) -> None:
        """Malformed JSON line returns ledger validation error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("{not-json}\n")
            f.flush()
            errors = validate_ledger(Path(f.name))
            self.assertTrue(any("Invalid JSON" in error.message for error in errors))

    def test_unknown_event_rejected(self) -> None:
        """Unknown event type fails closed."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "mystery_event",
                        "id": "ADR-0.3.0",
                        "ts": "2026-02-14T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            f.flush()
            errors = validate_ledger(Path(f.name))
            self.assertTrue(any("Unknown event type" in error.message for error in errors))

    def test_invalid_event_field_type_rejected(self) -> None:
        """Event field type violations are reported with line context."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "audit_receipt_emitted",
                        "id": "ADR-0.3.0",
                        "ts": "2026-02-14T00:00:00+00:00",
                        "receipt_event": "completed",
                        "attestor": "human:jeff",
                        "evidence": ["not", "an", "object"],
                    }
                )
                + "\n"
            )
            f.flush()
            errors = validate_ledger(Path(f.name))
            self.assertTrue(any("must be an object" in error.message for error in errors))


if __name__ == "__main__":
    unittest.main()
