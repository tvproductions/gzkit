"""Drivers for the readers RO-2 tranche 4 moved onto the identity seam.

Each test calls a moved reader on an ADR spelling and asserts the answer the
reader gave before the move, so reverting the move to a wrong body fails here.
"""

from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import ValidationError

from gzkit.commands import adr_demote, common, validate_task_envelope
from gzkit.commands.adr_audit import _is_foundation_adr
from gzkit.commands.adr_coverage import _extract_adr_semver
from gzkit.commands.context_cmd import _adr_semver
from gzkit.commands.plan_audit_cmd import _adr_id_from_dir
from gzkit.commands.specify_cmd import _extract_semver
from gzkit.commands.version_sync import _extract_adr_version
from gzkit.foundation import rubric, sunset_migrate, triage
from gzkit.governance.frontmatter_coherence import _resolve_artifact_id
from gzkit.hooks.obpi import ObpiValidator
from gzkit.hooks.scripts.validation import _obpi_completion_validator_script
from gzkit.justify import cli as justify_cli
from gzkit.mx.log import parse_artifacts
from gzkit.validators.unscoped_rules import UnscopedAllowlistEntry


class TestSemverReaders(unittest.TestCase):
    def test_every_semver_reader_gives_the_semver_of_a_full_id(self) -> None:
        for read in (_adr_semver, _extract_adr_semver, _extract_semver, _extract_adr_version):
            self.assertEqual(read("ADR-0.18.0-slug"), "0.18.0", read)
            self.assertIsNone(read("ADR-pool.slug"), read)

    def test_plan_audit_recovers_the_short_id_from_a_directory(self) -> None:
        self.assertEqual(_adr_id_from_dir("ADR-0.3.1-foo-bar"), "ADR-0.3.1")
        self.assertIsNone(_adr_id_from_dir("notes"))


class TestFoundationReaders(unittest.TestCase):
    def test_audit_delegate_and_hook_validator_agree_with_the_seam(self) -> None:
        self.assertTrue(_is_foundation_adr("ADR-0.0.36-x"))
        self.assertFalse(_is_foundation_adr("ADR-0.1.0-x"))
        validator = ObpiValidator.__new__(ObpiValidator)
        self.assertTrue(validator._is_foundation_series("ADR-0.0.9"))
        self.assertFalse(validator._is_foundation_series("ADR-0.2.0"))

    def test_foundation_pattern_takes_only_a_bare_short_id(self) -> None:
        self.assertTrue(triage._FOUNDATION_ID_PATTERN.match("ADR-0.0.7"))
        self.assertFalse(triage._FOUNDATION_ID_PATTERN.match("ADR-0.0.7-slug"))
        prefix = triage._FOUNDATION_SHORT_ID_PREFIX.match("ADR-0.0.7-slug")
        assert prefix is not None
        self.assertEqual(prefix.group(1), "ADR-0.0.7")
        for pattern in (rubric._FOUNDATION_SHORT_ID_PREFIX, sunset_migrate._ADR_SHORT_ID_RE):
            matched = pattern.match("ADR-1.2.3-s")
            assert matched is not None
            self.assertEqual(matched.group(1), "ADR-1.2.3")


class TestLooseReaders(unittest.TestCase):
    def test_artifact_id_from_a_file_stem(self) -> None:
        self.assertEqual(_resolve_artifact_id(Path("ADR-0.1.0-slug.md")), "ADR-0.1.0")
        self.assertEqual(_resolve_artifact_id(Path("ADR-pool.some.slug.md")), "ADR-pool.some.slug")
        self.assertEqual(_resolve_artifact_id(Path("OBPI-0.0.16-03-x.md")), "OBPI-0.0.16-03")

    def test_commit_message_names_the_adrs_it_cites(self) -> None:
        found = parse_artifacts("fix(x): ADR-0.18.0 and ADR-0.0.3-slug, not ADR-pool.y")
        self.assertEqual(found["ADR"], ["ADR-0.18.0", "ADR-0.0.3"])

    def test_justify_anchor_pattern_rejects_a_bare_short_adr(self) -> None:
        self.assertTrue(justify_cli._ADR_PATTERN.match("adr-0.1.0"))
        self.assertFalse(justify_cli._ADR_PATTERN.match("ADR-0.1.0-slug"))

    def test_task_envelope_decision_doc_pattern(self) -> None:
        pattern = validate_task_envelope._ADR_DECISION_DOC_RE
        self.assertTrue(pattern.search("/x/adr/pre-release/ADR-0.1.0-s/ADR-0.1.0-s.md"))
        self.assertTrue(pattern.search("/x/adr/pool/ADR-pool.s.md"))
        self.assertFalse(pattern.search("/x/adr/pool/OBPI-0.1.0-01-s.md"))

    def test_command_id_patterns(self) -> None:
        self.assertTrue(common.ADR_SEMVER_ID_RE.match("ADR-0.1.0-slug"))
        self.assertFalse(common.ADR_SEMVER_ID_RE.match("ADR-pool.slug"))
        self.assertTrue(common.ADR_POOL_ID_RE.match("ADR-pool.slug"))
        self.assertFalse(common.ADR_POOL_ID_RE.match("ADR-0.1.0"))
        slug = adr_demote._CANONICAL_ID_RE.match("ADR-0.1.0-the-slug")
        assert slug is not None
        self.assertEqual(slug["slug"], "the-slug")
        h1 = adr_demote._H1_ID_RE.match("# ADR-0.27.0: Title")
        assert h1 is not None
        self.assertEqual(h1["id"], "ADR-0.27.0")

    def test_allowlist_tracking_ref_takes_a_ghi_or_an_adr(self) -> None:
        def entry(ref: str) -> UnscopedAllowlistEntry:
            return UnscopedAllowlistEntry(
                file="a.md",
                rationale="x" * 20,
                tracking_ref=ref,
                added_date=date(2026, 1, 1),
            )

        self.assertEqual(entry("ADR-0.20.0-x").tracking_ref, "ADR-0.20.0-x")
        with self.assertRaises(ValidationError):
            entry("PRD-1")


class TestHookGeneratorCarriesTheSeamBody(unittest.TestCase):
    def test_parent_adr_finder_in_the_rendered_hook_matches_a_dated_adr_file(self) -> None:
        namespace: dict[str, object] = {"__name__": "rendered_hook"}
        exec(compile(_obpi_completion_validator_script(), "hook", "exec"), namespace)  # noqa: S102
        find = namespace["find_parent_adr_file"]
        assert callable(find)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ADR-pool.not-this.md").write_text("x", encoding="utf-8")
            (root / "ADR-0.1.0-real.md").write_text("x", encoding="utf-8")
            self.assertEqual(find(root), root / "ADR-0.1.0-real.md")


if __name__ == "__main__":
    unittest.main()
