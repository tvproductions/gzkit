"""Tests for gzkit validation engine."""

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from gzkit.core.validation_rules import ValidationError
from gzkit.schemas import load_schema
from gzkit.validate import (
    extract_headers,
    parse_frontmatter,
    validate_document,
    validate_ledger,
    validate_manifest,
)
from gzkit.validate_pkg.ledger_check import _validate_ledger_conditionals

# Sentinel for "this key is absent from the row", distinct from an empty value.
# The conditional-rule tests turn on exactly that difference: an omitted
# discriminator must leave the rule dormant, while an empty guarded field must
# trip it.
_ABSENT = object()


def _conditional_findings(
    entry: dict[str, Any], conditionals: list[dict[str, Any]]
) -> list[ValidationError]:
    """Run one ad-hoc conditional rule list against *entry*.

    Exercises rule forms that are not (and should not be) authored into the
    shipped `ledger.json` -- a misauthored `when` clause, a rule missing its
    recovery prose. Driving those through `validate_ledger` would mean
    shipping a broken rule to prove the validator rejects broken rules.
    """
    errors: list[ValidationError] = []
    _validate_ledger_conditionals(
        entry=entry,
        event_name=str(entry.get("event", "")),
        conditionals=conditionals,
        errors=errors,
        ledger_path=Path("ledger.jsonl"),
        line_no=1,
    )
    return errors


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
id: ADR-0.1.0-test-feature
status: Draft
semver: 0.1.0
lane: lite
kind: feature
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


class TestValidateDocumentNarrowGuards(unittest.TestCase):
    """Narrow scope guards on ADR validation (GHI #480; OBPI-0.0.54-03).

    Two coupled-surface coherence guards landed under the schema-enum fix:

    1. Kind-aware pool ADR skip -- pool ADRs carry a structurally distinct
       shape contract; applying the foundation/feature adr schema to them is
       the "validator scope mismatch" named in GHI #480 reopen comment.
    2. Lifecycle-aware grandfather skip -- ADRs in ``status: Validated`` or
       ``Completed`` had their shape locked at authoring/attestation time;
       retroactively binding new required sections is a trust-doctrine T1
       violation. Mirror of the lifecycle-aware precedent at
       ``trust_audits/briefs.py:_BDD_GATED_BRIEF_STATUSES`` with inverted
       polarity.
    """

    def _write_adr(self, dir_path: Path, stem: str, content: str) -> Path:
        path = dir_path / f"{stem}.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_pool_adr_stem_skips_all_adr_schema_validation(self) -> None:
        """Pool ADRs (stem ``ADR-pool.*``) bypass adr-schema validation entirely.

        Asserts the kind-aware guard returns ``[]`` for a pool ADR file
        whose frontmatter and body deliberately omit the foundation/feature
        required fields and sections. Pool ADRs by Layer-1-canon contract
        carry only Intent / Target Scope / Non-Goals; the foundation schema
        is the wrong instrument for them.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._write_adr(
                Path(temp_dir),
                "ADR-pool.test-skip-scope",
                "---\n"
                "id: ADR-pool.test-skip-scope\n"
                "status: Pool\n"
                "---\n\n"
                "# ADR-pool.test-skip-scope: Test\n\n"
                "## Intent\n\nPool placeholder.\n",
            )
            errors = validate_document(path, "adr")
            self.assertEqual(errors, [])

    def test_validated_adr_skips_required_sections(self) -> None:
        """``status: Validated`` ADRs are exempt from required_headers enforcement.

        Trust-doctrine T1: Validated artifacts had their shape locked at
        attestation time and the canonical schema does not retroactively
        bind canonical provenance.
        """
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                "---\n"
                "id: ADR-0.1.0\n"
                "status: Validated\n"
                "semver: 0.1.0\n"
                "lane: lite\n"
                "parent: OBPI-core\n"
                "date: 2026-01-01\n"
                "---\n\n"
                "# Title\n\n"
                "## Intent\n\n"
                "Body but missing Decision, Consequences, Decomposition Scorecard, etc.\n"
            )
            f.flush()
            errors = validate_document(Path(f.name), "adr")
            section_errors = [e for e in errors if e.type == "header"]
            decomposition_errors = [e for e in errors if e.type == "decomposition"]
            self.assertEqual(section_errors, [])
            self.assertEqual(decomposition_errors, [])

    def test_completed_adr_skips_required_sections(self) -> None:
        """``status: Completed`` ADRs are exempt from required_headers enforcement.

        Completed is a post-Accepted lifecycle state; same trust-doctrine
        argument as Validated.
        """
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                "---\n"
                "id: ADR-0.1.0\n"
                "status: Completed\n"
                "semver: 0.1.0\n"
                "lane: lite\n"
                "parent: OBPI-core\n"
                "date: 2026-01-01\n"
                "---\n\n"
                "# Title\n\n"
                "## Intent\n\nBody without Decomposition Scorecard.\n"
            )
            f.flush()
            errors = validate_document(Path(f.name), "adr")
            section_errors = [e for e in errors if e.type == "header"]
            self.assertEqual(section_errors, [])

    def test_validated_adr_keeps_enum_and_pattern_frontmatter_checks(self) -> None:
        """Lifecycle skip preserves mechanical-invariant frontmatter checks.

        Missing-required-field checks are grandfathered along with
        required_headers (same trust-doctrine T1 argument across both axes).
        Enum, pattern, and type checks continue to fire because they are
        mechanical invariants on values that ARE present, not authoring-era
        shape requirements.
        """
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                "---\n"
                "id: ADR-0.1.0\n"
                "status: Validated\n"
                "semver: 0.1.0\n"
                "lane: bogus-lane-value\n"
                "parent: OBPI-core\n"
                "date: 2026-01-01\n"
                "---\n\n"
                "# Title\n\n"
                "## Intent\n\nBody.\n"
            )
            f.flush()
            errors = validate_document(Path(f.name), "adr")
            self.assertTrue(any(e.field == "lane" for e in errors))

    def test_validated_adr_skips_missing_required_frontmatter_field(self) -> None:
        """``status: Validated`` ADRs are exempt from missing-required-field checks.

        Same trust-doctrine T1 argument as required_headers: the schema
        cannot retroactively require frontmatter fields that did not exist
        in the schema at attestation time. Symmetric coverage with the
        sections grandfather.
        """
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                "---\n"
                "id: ADR-0.1.0\n"
                "status: Validated\n"
                "semver: 0.1.0\n"
                "lane: lite\n"
                "parent: OBPI-core\n"
                "---\n\n"
                "# Title\n\n"
                "## Intent\n\nBody but missing date frontmatter.\n"
            )
            f.flush()
            errors = validate_document(Path(f.name), "adr")
            missing_field_errors = [
                e for e in errors if e.message.startswith("Missing required frontmatter field")
            ]
            self.assertEqual(missing_field_errors, [])

    def test_draft_adr_still_requires_sections(self) -> None:
        """Regression invariant: pre-Accepted ADRs are NOT grandfathered.

        Only ``Validated`` and ``Completed`` are grandfather-exempt. Draft,
        Proposed, Accepted, etc. continue to receive the full ``required_headers``
        enforcement so in-flight authoring catches missing sections.
        """
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                "---\n"
                "id: ADR-0.1.0\n"
                "status: Draft\n"
                "semver: 0.1.0\n"
                "lane: lite\n"
                "parent: OBPI-core\n"
                "date: 2026-01-01\n"
                "---\n\n"
                "# Title\n\n"
                "## Intent\n\nBody but missing Decision.\n"
            )
            f.flush()
            errors = validate_document(Path(f.name), "adr")
            self.assertTrue(any(e.field == "Decision" for e in errors))

    def test_accepted_adr_still_requires_sections(self) -> None:
        """Accepted is pre-Validated; not grandfathered.

        Grandfather threshold is post-Accepted (Validated/Completed). Accepted
        ADRs are still in their authoring window and must satisfy current shape.
        """
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                "---\n"
                "id: ADR-0.1.0\n"
                "status: Accepted\n"
                "semver: 0.1.0\n"
                "lane: lite\n"
                "parent: OBPI-core\n"
                "date: 2026-01-01\n"
                "---\n\n"
                "# Title\n\n"
                "## Intent\n\nBody but missing Decision.\n"
            )
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

    def test_descending_timestamps_rejected(self) -> None:
        """A row whose ts precedes its predecessor's is rejected (GHI #812).

        The ledger is an append-only log: rows are written in the order events
        occur, so time never runs backwards across adjacent rows. Every row
        validated in isolation here is individually well-formed — the defect is
        only visible between rows, which is the phase the validator lacked.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for ts in ("2026-02-14T00:00:02+00:00", "2026-02-14T00:00:01+00:00"):
                f.write(
                    json.dumps(
                        {
                            "schema": "gzkit.ledger.v1",
                            "event": "project_init",
                            "id": "gzkit",
                            "ts": ts,
                            "mode": "lite",
                        }
                    )
                    + "\n"
                )
            f.flush()
            errors = validate_ledger(Path(f.name))

        self.assertTrue(
            any(error.field == "ts" for error in errors),
            f"descending ts must be rejected, got: {errors}",
        )

    def _ledger_with_timestamps(self, timestamps: tuple[str, ...]) -> list[ValidationError]:
        """Validate a ledger whose rows differ only in `ts`."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for ts in timestamps:
                f.write(
                    json.dumps(
                        {
                            "schema": "gzkit.ledger.v1",
                            "event": "project_init",
                            "id": "gzkit",
                            "ts": ts,
                            "mode": "lite",
                        }
                    )
                    + "\n"
                )
            f.flush()
            return validate_ledger(Path(f.name))

    def test_equal_timestamps_accepted(self) -> None:
        """Two events at the same instant are ordered, not inverted (GHI #812).

        The invariant is non-decreasing, not strictly increasing: nothing stops
        two events sharing a timestamp, and rejecting them would fail closed on
        a correct ledger.
        """
        errors = self._ledger_with_timestamps(
            ("2026-02-14T00:00:01+00:00", "2026-02-14T00:00:01+00:00")
        )
        self.assertEqual(errors, [], f"equal timestamps must be accepted, got: {errors}")

    def test_ordering_compares_instants_not_strings(self) -> None:
        """Ordering is by real instant, so UTC offsets are honoured (GHI #812).

        These two rows ascend in real time (09:00Z then 10:00Z) but *descend*
        lexically, because '2026-02-14T10:00:00+01:00' sorts before
        '2026-02-14T09:30:00+00:00'. A string comparison — the obvious
        implementation, and the one the reporting probe used — calls this an
        inversion and fails a correct ledger.
        """
        errors = self._ledger_with_timestamps(
            ("2026-02-14T10:00:00+01:00", "2026-02-14T09:30:00+00:00")
        )
        self.assertEqual(errors, [], f"offsets must be normalized before comparison, got: {errors}")

    def test_naive_timestamp_does_not_crash_ordering(self) -> None:
        """A naive timestamp is read as UTC rather than raising (GHI #812).

        Comparing a naive datetime against an aware one raises TypeError. A
        malformed row must surface as a finding, never as a crash that takes
        the whole validation run down with it.
        """
        errors = self._ledger_with_timestamps(("2026-02-14T00:00:01+00:00", "2026-02-14T00:00:00"))
        self.assertTrue(
            any(error.field == "ts" for error in errors),
            f"naive descending ts must be reported, not raised, got: {errors}",
        )

    def test_chore_decommission_compound_dispositions_accepted(self) -> None:
        """Compound/extended dispositions recorded by the OBPI-0.0.59-05 sweep validate clean.

        The ledger-schema disposition enum is the *historical-record acceptance* surface —
        distinct from ProposedDisposition (the forward proposal menu locked at four by
        REQ-0.0.59-04-02). The sweep authored combined dispositions through the free-str
        event field, so the ledger must accept them as valid recorded states.
        """
        recorded_dispositions = [
            "fold-to-validator+keep-as-fixture",
            "fold-to-validator-whole-file-delete",
            "no-op-already-clean",
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for i, disposition in enumerate(recorded_dispositions):
                entry = {
                    "schema": "gzkit.ledger.v1",
                    "event": "chore_decommission_processed",
                    "id": f"tests/governance/test_example_{i}.py",
                    "ts": "2026-05-27T06:30:00+00:00",
                    "file_path": f"tests/governance/test_example_{i}.py",
                    "disposition": disposition,
                    "obpi_id": "OBPI-0.0.59-05-first-sweep-wave-top-5-offenders",
                }
                f.write(json.dumps(entry) + "\n")
            f.flush()
            errors = validate_ledger(Path(f.name))
        self.assertEqual(errors, [], f"compound dispositions rejected: {errors}")

    def test_chore_decommission_unknown_disposition_rejected(self) -> None:
        """An unrecognized disposition is still rejected — widening did not remove the enum."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            entry = {
                "schema": "gzkit.ledger.v1",
                "event": "chore_decommission_processed",
                "id": "tests/governance/test_bogus.py",
                "ts": "2026-05-27T06:30:00+00:00",
                "file_path": "tests/governance/test_bogus.py",
                "disposition": "totally-made-up-disposition",
                "obpi_id": "OBPI-0.0.59-05-first-sweep-wave-top-5-offenders",
            }
            f.write(json.dumps(entry) + "\n")
            f.flush()
            errors = validate_ledger(Path(f.name))
        self.assertTrue(
            any("disposition" in error.message for error in errors),
            "unknown disposition should be rejected by the enum",
        )

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

    def test_audit_receipt_emitted_accepts_runtime_emitted_events(self) -> None:
        """GHI #414: schema accepts every ``receipt_event`` value the runtime emits.

        The producers — ``_enforce_attestation_receipt_gate`` in
        ``obpi_complete.py`` and ``_emit_adr_closeout_receipt`` in
        ``adr_audit.py`` — emit ``audit_receipt_emitted`` events with
        ``receipt_event`` values beyond the original ``completed`` /
        ``validated`` pair: ``meta-receipt-bind`` (REQ-0.0.24-02 receipt
        binding) and ``closed`` (ADR-0.0.25-02 closeout). The schema
        ``audit_receipt_emitted.receipt_event.enum`` must accept all of
        them or runtime-emitted ledger lines are reported as drift.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for value in ("completed", "validated", "meta-receipt-bind", "closed"):
                f.write(
                    json.dumps(
                        {
                            "schema": "gzkit.ledger.v1",
                            "event": "audit_receipt_emitted",
                            "id": "ADR-0.3.0",
                            "ts": "2026-02-14T00:00:00+00:00",
                            "receipt_event": value,
                            "attestor": "human:jeff",
                        }
                    )
                    + "\n"
                )
            f.flush()
            errors = validate_ledger(Path(f.name))
        self.assertEqual(errors, [])

    def test_audit_receipt_emitted_rejects_unknown_receipt_event(self) -> None:
        """GHI #414: schema still rejects values the runtime never emits.

        Extending the enum for runtime parity must not become a free-for-all.
        ``not-a-real-event`` is not a producer-side value and must fail.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "audit_receipt_emitted",
                        "id": "ADR-0.3.0",
                        "ts": "2026-02-14T00:00:00+00:00",
                        "receipt_event": "not-a-real-event",
                        "attestor": "human:jeff",
                    }
                )
                + "\n"
            )
            f.flush()
            errors = validate_ledger(Path(f.name))
        self.assertTrue(
            any(
                "must be one of" in error.message and "not-a-real-event" in error.message
                for error in errors
            )
        )


class TestLedgerConditionalRules(unittest.TestCase):
    """Cross-field conditional rules in ledger.json (GHI #882).

    Every other rule form in `ledger_check.py` reads one field in isolation:
    an unconditional `required` list, and per-field type/enum/min/min_length.
    An invariant spanning TWO fields was therefore inexpressible, so where a
    runtime gate's condition is recorded in the payload the validator could
    detect a violation by inspection but never reject one.

    The instance that surfaced it: `gz content retire` refuses a retirement
    that moves invariant-tier liveness without a named `--attestor`, and
    `corpus_entry_retired` records `floor_direction` — the gate's own
    discriminator. A hand-authored row with `floor_direction: "grew"` and
    `attestor: ""` validated clean.

    These tests assert the RULE FORM, not the one event: an event whose
    payload carries a discriminator plus a field required only for some of
    its values. Binding the assertions to `corpus_entry_retired` alone would
    reproduce the bespoke-check repair the GHI names as wrong.
    """

    MOVED_DIRECTIONS = ("shrank", "grew", "changed")

    def _retirement(self, **overrides: object) -> dict[str, object]:
        entry: dict[str, object] = {
            "schema": "gzkit.ledger.v1",
            "event": "corpus_entry_retired",
            "id": "corpus-entry-retired-2026-08-27T00:00:00+00:00",
            "ts": "2026-08-27T00:00:00+00:00",
            "surface": "AGENTS.md",
            "retired_entry_id": "corpus-some-entry",
            "retraction_entry_id": "corpus-retraction-some-entry",
            "reason": "superseded by a sharper statement",
            "tier": "invariant",
        }
        entry.update(overrides)
        return {k: v for k, v in entry.items() if v is not _ABSENT}

    def _validate(self, *entries: dict[str, object]) -> list[ValidationError]:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
            f.flush()
            return validate_ledger(Path(f.name))

    def test_moving_the_floor_without_a_witness_is_rejected(self) -> None:
        """The gate's own condition, asserted at Layer 2.

        This is the defect verbatim from GHI #882: an event that records a
        floor move and an empty attestor described a state the runtime gate
        refuses to produce, and the validator accepted it.
        """
        for direction in self.MOVED_DIRECTIONS:
            with self.subTest(floor_direction=direction):
                errors = self._validate(
                    self._retirement(
                        floor_direction=direction,
                        floor_moved_ids=["corpus-operator-doctrine"],
                        attestor="",
                    )
                )
                self.assertTrue(
                    any(error.field == "attestor" for error in errors),
                    f"floor_direction={direction!r} with an empty attestor must be "
                    f"rejected, got: {errors}",
                )

    def test_a_whitespace_attestor_is_not_a_witness(self) -> None:
        """Same stripped-length semantics the unconditional guard already uses.

        A raw character count is satisfied by whitespace, so the conditional
        form must measure the same way its unconditional sibling does or the
        gate is reopened one space at a time.
        """
        errors = self._validate(
            self._retirement(
                floor_direction="grew",
                floor_moved_ids=["corpus-operator-doctrine"],
                attestor="   ",
            )
        )
        self.assertTrue(
            any(error.field == "attestor" for error in errors),
            f"a whitespace-only attestor must be rejected, got: {errors}",
        )

    def test_an_omitted_attestor_is_reported_as_missing(self) -> None:
        """Absent is not the same shape as empty, and both must fail.

        `then.required` and `then.properties` are separate arms; an event that
        simply omits the key never reaches the min_length arm at all.
        """
        errors = self._validate(
            self._retirement(
                floor_direction="grew",
                floor_moved_ids=["corpus-operator-doctrine"],
                attestor=_ABSENT,
            )
        )
        self.assertTrue(
            any(error.field == "attestor" for error in errors),
            f"an omitted attestor must be rejected when the floor moved, got: {errors}",
        )

    def test_a_named_attestor_satisfies_the_condition(self) -> None:
        """The rule must not fail closed on the state it exists to require."""
        errors = self._validate(
            self._retirement(
                floor_direction="grew",
                floor_moved_ids=["corpus-operator-doctrine"],
                attestor="g0",
            )
        )
        self.assertEqual(errors, [], f"a witnessed floor move must validate, got: {errors}")

    def test_an_unchanged_floor_needs_no_attestor(self) -> None:
        """`attestor` is LEGITIMATELY empty on a routine compressible retirement.

        This is why the requirement could not simply join `required` with a
        `min_length` — the asymmetry between the two directions is the whole
        reason a conditional form was needed.
        """
        errors = self._validate(
            self._retirement(
                tier="compressible",
                floor_direction="unchanged",
                floor_moved_ids=[],
                attestor="",
            )
        )
        self.assertEqual(
            errors, [], f"an unchanged floor must not require an attestor, got: {errors}"
        )

    def test_a_row_predating_the_discriminator_is_untouched(self) -> None:
        """Append-only history must keep validating (GHI #877's split).

        The five committed `corpus_entry_retired` rows predate
        `floor_direction` entirely. A conditional keyed on a field's PRESENCE
        and value is dormant on them by construction — this test pins that
        property rather than trusting it, because the alternative reading
        (absent discriminator treated as any-value) would reject every
        historical row and the ledger cannot be edited to comply.
        """
        errors = self._validate(
            self._retirement(
                tier="invariant",
                floor_direction=_ABSENT,
                floor_moved_ids=_ABSENT,
                attestor=_ABSENT,
            )
        )
        self.assertEqual(
            errors, [], f"a row predating floor_direction must still validate, got: {errors}"
        )

    def test_recovery_prose_names_the_condition_and_a_next_step(self) -> None:
        """A fail-closed surface owes three-part recovery prose.

        `.claude/rules/guardrail-feedback-prose.md` § Invariant binds every
        fail-closed validator: what failed, why it is forbidden, and the
        governed next step. A conditional rule's "why" is specific to that
        rule, so the schema carries it and the validator composes — a bare
        "missing required field: attestor" would tell a reader nothing about
        the condition that made it required.
        """
        errors = self._validate(
            self._retirement(
                floor_direction="grew",
                floor_moved_ids=["corpus-operator-doctrine"],
                attestor="",
            )
        )
        messages = [error.message for error in errors if error.field == "attestor"]
        self.assertTrue(messages, "expected an attestor finding")
        joined = " ".join(messages)
        self.assertIn("floor_direction", joined, "the message must name the condition")
        self.assertIn("grew", joined, "the message must name the observed value")
        self.assertIn("gz content retire", joined, "the message must name a governed next step")

    def test_an_unsupported_conditional_is_reported_not_silently_skipped(self) -> None:
        """A rule the validator cannot read must fail loud, never go inert.

        This is the presence-check family AGENTS.md names: a gate whose only
        witness is that a rule was authored. A misauthored `when` clause that
        the validator quietly ignores reads exactly like a passing check, and
        every row it was meant to guard sails through. Schema-authoring
        defects are surfaced as findings against the rows they failed to
        cover.
        """
        errors = _conditional_findings(
            self._retirement(floor_direction="grew", attestor=""),
            [{"when": {"field": "floor_direction", "matches": "^g"}, "then": {}}],
        )
        self.assertTrue(
            any("unsupported" in error.message for error in errors),
            f"an unreadable conditional must be reported, got: {errors}",
        )

    def test_a_conditional_without_recovery_prose_is_unsupported(self) -> None:
        """The prose bar is mechanical for this rule form, not aspirational.

        `guardrail-feedback-prose.md` is scored advisory repo-wide because no
        witness could attribute prose quality generally. Here it is decidable:
        a conditional rule carries its own `because` text or the validator
        cannot compose a three-part message, so an omitted one is a schema
        defect rather than a terse-but-valid rule.
        """
        errors = _conditional_findings(
            self._retirement(floor_direction="grew", attestor=""),
            [
                {
                    "when": {"field": "floor_direction", "in": ["grew"]},
                    "then": {"required": ["attestor"]},
                }
            ],
        )
        self.assertTrue(
            any("unsupported" in error.message for error in errors),
            f"a conditional with no `because` prose must be reported, got: {errors}",
        )

    def test_every_moving_direction_is_covered_by_the_shipped_rule(self) -> None:
        """The enum's non-`unchanged` members are the family, exhaustively.

        Enumerated from the schema rather than transcribed: a fifth direction
        added later with no conditional coverage is the same defect this GHI
        closes, and a hand-written list would not notice it.
        """
        schema = load_schema("ledger")
        rules = schema["events"]["corpus_entry_retired"]
        enum = set(rules["properties"]["floor_direction"]["enum"])
        guarded: set[str] = set()
        for rule in rules.get("conditional", []):
            when = rule.get("when", {})
            if when.get("field") == "floor_direction":
                guarded.update(when.get("in", []))
        self.assertEqual(
            enum - {"unchanged"},
            guarded,
            "every floor_direction that MOVES the floor must be guarded; "
            "`unchanged` is the only value that legitimately needs no attestor",
        )


if __name__ == "__main__":
    unittest.main()
