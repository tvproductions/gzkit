"""Tests for gz validate --unscoped-rules scope.

@covers ADR-0.0.20-agent-rule-placement-invariant
@covers OBPI-0.0.20-01-validator-and-allowlist
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from pydantic import ValidationError as PydanticValidationError

from gzkit.traceability import covers
from gzkit.validators.unscoped_rules import (
    UnscopedAllowlistEntry,
    UnscopedRulesResult,
    Violation,
    classify_paths_field,
    format_allowlist_listing,
    run_unscoped_rules,
)


class TestUnscopedAllowlistEntryModel(unittest.TestCase):
    """REQ-0.0.20-01-01 / REQ-0.0.20-01-02 — UnscopedAllowlistEntry contract."""

    @covers("REQ-0.0.20-01-01")
    @covers("REQ-0.0.20-01-02")
    def test_valid_entry_constructs(self) -> None:
        entry = UnscopedAllowlistEntry(
            file=".gzkit/rules/agent-contract.md",
            rationale="Pending consolidation per OBPI-02",
            tracking_ref="ADR-0.0.20",
            added_date=date(2026, 4, 21),
        )
        self.assertEqual(entry.file, ".gzkit/rules/agent-contract.md")
        self.assertEqual(entry.tracking_ref, "ADR-0.0.20")

    @covers("REQ-0.0.20-01-01")
    def test_entry_is_frozen(self) -> None:
        entry = UnscopedAllowlistEntry(
            file="x.md",
            rationale="Long enough rationale here.",
            tracking_ref="GHI-999",
            added_date=date(2026, 4, 21),
        )
        with self.assertRaises(PydanticValidationError):
            entry.file = "y.md"  # type: ignore

    @covers("REQ-0.0.20-01-02")
    def test_rationale_min_length_enforced(self) -> None:
        with self.assertRaises(PydanticValidationError):
            UnscopedAllowlistEntry(
                file="x.md",
                rationale="too short",
                tracking_ref="GHI-1",
                added_date=date(2026, 4, 21),
            )

    @covers("REQ-0.0.20-01-02")
    def test_tracking_ref_pattern_enforced(self) -> None:
        with self.assertRaises(PydanticValidationError):
            UnscopedAllowlistEntry(
                file="x.md",
                rationale="Long enough rationale string.",
                tracking_ref="bogus-ref",
                added_date=date(2026, 4, 21),
            )

    @covers("REQ-0.0.20-01-01")
    def test_extra_fields_forbidden(self) -> None:
        with self.assertRaises(PydanticValidationError):
            UnscopedAllowlistEntry(
                file="x.md",
                rationale="Long enough rationale string.",
                tracking_ref="ADR-0.0.20",
                added_date=date(2026, 4, 21),
                extra_key="nope",  # type: ignore
            )

    @covers("REQ-0.0.20-01-02")
    def test_tracking_ref_accepts_adr_and_ghi_forms(self) -> None:
        ok_refs = ["ADR-0.0.20", "ADR-0.17.0", "GHI-1", "GHI-12345", "ADR-0.0.20-foo"]
        for ref in ok_refs:
            UnscopedAllowlistEntry(
                file="x.md",
                rationale="Long enough rationale string.",
                tracking_ref=ref,
                added_date=date(2026, 4, 21),
            )


class TestViolationModel(unittest.TestCase):
    """REQ-0.0.20-01-02 — Violation contract."""

    @covers("REQ-0.0.20-01-02")
    def test_valid_violation_constructs(self) -> None:
        v = Violation(
            file=".gzkit/rules/foo.md",
            reason="missing-paths",
            allowlisted=False,
            detected_value=None,
        )
        self.assertEqual(v.reason, "missing-paths")
        self.assertFalse(v.allowlisted)

    @covers("REQ-0.0.20-01-02")
    def test_reason_literal_enforced(self) -> None:
        with self.assertRaises(PydanticValidationError):
            Violation(
                file="x.md",
                reason="invalid-reason",  # type: ignore
                allowlisted=False,
            )

    @covers("REQ-0.0.20-01-02")
    def test_violation_is_frozen(self) -> None:
        v = Violation(file="x.md", reason="universal-glob", allowlisted=True)
        with self.assertRaises(PydanticValidationError):
            v.allowlisted = False  # type: ignore


class TestUnscopedRulesResultModel(unittest.TestCase):
    """REQ-0.0.20-01-02 — UnscopedRulesResult contract."""

    @covers("REQ-0.0.20-01-02")
    def test_default_scope_and_construction(self) -> None:
        r = UnscopedRulesResult(
            result="pass",
            violations=[],
            allowlist_entries=[],
            canonical_root=".gzkit/rules",
            files_checked=0,
            exit_code=0,
        )
        self.assertEqual(r.scope, "unscoped-rules")
        self.assertEqual(r.exit_code, 0)

    @covers("REQ-0.0.20-01-02")
    def test_result_literal_enforced(self) -> None:
        with self.assertRaises(PydanticValidationError):
            UnscopedRulesResult(
                result="bogus",  # type: ignore
                violations=[],
                allowlist_entries=[],
                canonical_root=".gzkit/rules",
                files_checked=0,
                exit_code=0,
            )


class TestClassifyPathsField(unittest.TestCase):
    """REQ-0.0.20-01-06 — classify `paths:` values across YAML forms.

    Returns one of: "missing" | "universal-glob" | "concrete".
    """

    @covers("REQ-0.0.20-01-06")
    def test_frontmatter_without_paths_key_is_missing(self) -> None:
        fm = "id: foo\nstatus: Draft\n"
        verdict, detected = classify_paths_field(fm)
        self.assertEqual(verdict, "missing")

    @covers("REQ-0.0.20-01-06")
    def test_null_paths_is_missing(self) -> None:
        for raw in ("paths:\n", "paths: null\n", "paths: ~\n", "paths: \n"):
            with self.subTest(raw=raw):
                verdict, _ = classify_paths_field(raw)
                self.assertEqual(verdict, "missing")

    @covers("REQ-0.0.20-01-06")
    def test_universal_string_form_is_violation(self) -> None:
        for raw in ('paths: "**"\n', "paths: '**'\n", "paths: **\n"):
            with self.subTest(raw=raw):
                verdict, detected = classify_paths_field(raw)
                self.assertEqual(verdict, "universal-glob")
                self.assertEqual(detected, "**")

    @covers("REQ-0.0.20-01-06")
    def test_universal_inline_list_is_violation(self) -> None:
        for raw in ('paths: ["**"]\n', "paths: ['**']\n", 'paths: [ "**" ]\n'):
            with self.subTest(raw=raw):
                verdict, detected = classify_paths_field(raw)
                self.assertEqual(verdict, "universal-glob")
                self.assertEqual(detected, "**")

    @covers("REQ-0.0.20-01-06")
    def test_universal_block_list_is_violation(self) -> None:
        fm = 'paths:\n  - "**"\n'
        verdict, detected = classify_paths_field(fm)
        self.assertEqual(verdict, "universal-glob")
        self.assertEqual(detected, "**")

    @covers("REQ-0.0.20-01-06")
    def test_concrete_string_passes(self) -> None:
        for raw in ('paths: "src/**"\n', "paths: src/**\n"):
            with self.subTest(raw=raw):
                verdict, _ = classify_paths_field(raw)
                self.assertEqual(verdict, "concrete")

    @covers("REQ-0.0.20-01-06")
    def test_concrete_list_passes(self) -> None:
        for raw in (
            'paths: ["tests/**"]\n',
            'paths: ["src/**", "tests/**"]\n',
            'paths:\n  - "src/**"\n  - "tests/**"\n',
        ):
            with self.subTest(raw=raw):
                verdict, _ = classify_paths_field(raw)
                self.assertEqual(verdict, "concrete")


def _write_rule(rules_dir: Path, name: str, frontmatter_body: str) -> Path:
    """Helper: write a rule file with the given frontmatter body."""
    content = f"---\n{frontmatter_body}---\n\n# {name}\n\nbody\n"
    path = rules_dir / name
    path.write_text(content, encoding="utf-8")
    return path


def _make_project_root(root: Path, manifest: dict | None) -> Path:
    """Helper: scaffold .gzkit/rules/ and optional manifest."""
    rules = root / ".gzkit" / "rules"
    rules.mkdir(parents=True)
    if manifest is not None:
        (root / ".gzkit" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return rules


class TestRunUnscopedRules(unittest.TestCase):
    """REQ-0.0.20-01-06 / -07 / -18 — end-to-end classification + exit codes."""

    @covers("REQ-0.0.20-01-06")
    @covers("REQ-0.0.20-01-07")
    def test_clean_repo_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = _make_project_root(root, manifest={})
            _write_rule(rules, "a.md", 'paths: "src/**"\n')
            _write_rule(rules, "b.md", 'paths: ["tests/**"]\n')

            result = run_unscoped_rules(root)

            self.assertEqual(result.result, "pass")
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.violations, [])
            self.assertEqual(result.files_checked, 2)

    @covers("REQ-0.0.20-01-06")
    @covers("REQ-0.0.20-01-07")
    def test_missing_paths_fails_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = _make_project_root(root, manifest={})
            _write_rule(rules, "bad.md", "id: bad\n")

            result = run_unscoped_rules(root)

            self.assertEqual(result.result, "fail")
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(len(result.violations), 1)
            v = result.violations[0]
            self.assertEqual(v.reason, "missing-paths")
            self.assertFalse(v.allowlisted)

    @covers("REQ-0.0.20-01-06")
    @covers("REQ-0.0.20-01-07")
    def test_universal_glob_fails_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = _make_project_root(root, manifest={})
            _write_rule(rules, "bad.md", 'paths: "**"\n')

            result = run_unscoped_rules(root)

            self.assertEqual(result.result, "fail")
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.violations[0].reason, "universal-glob")
            self.assertEqual(result.violations[0].detected_value, "**")

    @covers("REQ-0.0.20-01-06")
    @covers("REQ-0.0.20-01-18")
    def test_allowlisted_file_does_not_fail_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowlist = [
                {
                    "file": ".gzkit/rules/bad.md",
                    "rationale": "Pending consolidation per OBPI-02",
                    "tracking_ref": "ADR-0.0.20",
                    "added_date": "2026-04-21",
                }
            ]
            manifest = {"rules": {"unscoped_allowlist": allowlist}}
            rules = _make_project_root(root, manifest=manifest)
            _write_rule(rules, "bad.md", 'paths: "**"\n')

            result = run_unscoped_rules(root)

            self.assertEqual(result.result, "pass")
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(len(result.violations), 1)
            self.assertTrue(result.violations[0].allowlisted)
            self.assertEqual(len(result.allowlist_entries), 1)

    @covers("REQ-0.0.20-01-04")
    def test_hierarchical_agents_md_is_not_a_rule_file(self) -> None:
        """AGENTS.md under .gzkit/rules/ is the canonical home per the invariant."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = _make_project_root(root, manifest={})
            # AGENTS.md has no frontmatter — should NOT be flagged missing-paths.
            (rules / "AGENTS.md").write_text("# Hierarchical AGENTS.md\nbody\n", encoding="utf-8")
            _write_rule(rules, "a.md", 'paths: "src/**"\n')

            result = run_unscoped_rules(root)

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.files_checked, 1)
            self.assertEqual(result.violations, [])

    @covers("REQ-0.0.20-01-04")
    def test_mirror_rules_are_not_enumerated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = _make_project_root(root, manifest={})
            # Canonical rule — clean.
            _write_rule(rules, "canonical.md", 'paths: "src/**"\n')
            # Mirror rule under .claude/rules/ — violating, must NOT be flagged.
            mirror = root / ".claude" / "rules"
            mirror.mkdir(parents=True)
            _write_rule(mirror, "mirror.md", 'paths: "**"\n')

            result = run_unscoped_rules(root)

            self.assertEqual(result.result, "pass")
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.files_checked, 1)

    @covers("REQ-0.0.20-01-07")
    def test_missing_manifest_returns_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_project_root(root, manifest=None)  # no manifest

            result = run_unscoped_rules(root)

            self.assertEqual(result.exit_code, 2)
            self.assertEqual(result.result, "fail")


class TestJsonRoundtrip(unittest.TestCase):
    """REQ-0.0.20-01-08 — `--json` output parses back through Pydantic."""

    @covers("REQ-0.0.20-01-08")
    def test_result_roundtrips_through_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = _make_project_root(root, manifest={})
            _write_rule(rules, "a.md", 'paths: "src/**"\n')
            _write_rule(rules, "bad.md", 'paths: "**"\n')

            result = run_unscoped_rules(root)
            # Coerce to JSON string and back.
            as_json = result.model_dump_json()
            parsed = json.loads(as_json)
            rehydrated = UnscopedRulesResult.model_validate(parsed)

            self.assertEqual(rehydrated.scope, "unscoped-rules")
            self.assertEqual(rehydrated.exit_code, result.exit_code)
            self.assertEqual(len(rehydrated.violations), len(result.violations))


class TestReadOnlyContract(unittest.TestCase):
    """REQ-0.0.20-01-20 — validator is strictly read-only."""

    @covers("REQ-0.0.20-01-20")
    def test_module_source_has_no_destructive_calls(self) -> None:
        import io
        import tokenize

        import gzkit.validators.unscoped_rules as mod

        source = Path(mod.__file__).read_text(encoding="utf-8")
        # Collect NAME and OP tokens only — ignore strings, comments, docstrings.
        code_fragments: list[str] = []
        readline = io.StringIO(source).readline
        for tok in tokenize.generate_tokens(readline):
            if tok.type in (tokenize.NAME, tokenize.OP, tokenize.NUMBER):
                code_fragments.append(tok.string)
        code_stream = " ".join(code_fragments)

        forbidden_substrings = (
            "shell = True",
            "subprocess .",
            "os . system",
            "os . remove",
            "os . unlink",
            ". write_text (",
            ". write_bytes (",
            "shutil .",
        )
        for token in forbidden_substrings:
            with self.subTest(token=token):
                self.assertNotIn(token, code_stream)


class TestAllowlistListing(unittest.TestCase):
    """REQ-0.0.20-01-09 — `--allowlist-only` renders entries legibly."""

    @covers("REQ-0.0.20-01-09")
    def test_listing_contains_rationale_and_tracking_ref(self) -> None:
        entries = [
            UnscopedAllowlistEntry(
                file=".gzkit/rules/agent-contract.md",
                rationale="Pending consolidation per OBPI-02",
                tracking_ref="ADR-0.0.20",
                added_date=date(2026, 4, 21),
            ),
            UnscopedAllowlistEntry(
                file=".gzkit/rules/attestation-enrichment.md",
                rationale="Pending consolidation per OBPI-03",
                tracking_ref="ADR-0.0.20",
                added_date=date(2026, 4, 21),
            ),
        ]
        rendered = format_allowlist_listing(entries)
        self.assertIn(".gzkit/rules/agent-contract.md", rendered)
        self.assertIn("Pending consolidation per OBPI-02", rendered)
        self.assertIn("ADR-0.0.20", rendered)
        self.assertIn(".gzkit/rules/attestation-enrichment.md", rendered)

    @covers("REQ-0.0.20-01-09")
    def test_empty_allowlist_renders_cleanly(self) -> None:
        rendered = format_allowlist_listing([])
        self.assertIn("no entries", rendered.lower())

    @covers("REQ-0.0.20-01-20")
    def test_run_does_not_mutate_fixture_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = _make_project_root(root, manifest={})
            rule = _write_rule(rules, "a.md", 'paths: "src/**"\n')
            before = rule.read_text(encoding="utf-8")

            run_unscoped_rules(root)

            after = rule.read_text(encoding="utf-8")
            self.assertEqual(before, after)
