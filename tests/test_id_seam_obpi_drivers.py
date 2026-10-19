"""Drivers for the OBPI readers tranche 3 moved onto the identity seam (drydock RO-2).

`docs/governance/harbor-ro2-identity-seam.md` § Tranches row 3. Each reader once spelled its
own OBPI width; each now embeds a seam body, so every one reads the seam's short form
(``OBPI-<semver>-<NN>``) and none reads an id the seam does not. The hook generators
substitute the bodies at render time, so a rendered script carries them and no placeholder.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import gzkit.adr_eval  # noqa: F401  (the two adr_eval modules import each other; this one must enter first)
from gzkit.adr_eval_scoring import (
    _score_feature_checklist,
    _score_obpi_decomposition,
    _score_obpi_independence,
)
from gzkit.commands import state as state_cmd
from gzkit.commands import task as task_cmd
from gzkit.commands import validate_frontmatter as vfm
from gzkit.commands.adr_coverage import _req_prefix_for_obpi
from gzkit.commands.ceremony_data import _short_obpi_id, extract_brief_metadata
from gzkit.commands.obpi_audit_cmd import _extract_obpi_id
from gzkit.commands.plan_audit_cmd import _derive_adr_id
from gzkit.commands.specify_cmd import _normalized_objective_from_checklist_item
from gzkit.commands.validate_task_envelope import _obpi_lineage_id
from gzkit.core.models import OBPI_SHORT_ID_BODY
from gzkit.governance import brief_structure
from gzkit.governance.frontmatter_coherence import _resolve_artifact_id
from gzkit.governance.trust_audits import absorption_duplicates, briefs
from gzkit.governance.trust_audits.evaluation_justify_binding import _subject_key
from gzkit.handoff_validation import _OBPI_ID_RE as _HANDOFF_OBPI_ID_RE
from gzkit.hooks.scripts.pipeline import _plan_audit_gate_script
from gzkit.hooks.scripts.quality import _stop_turn_feedback_script
from gzkit.hooks.scripts.validation import _obpi_completion_validator_script
from gzkit.justify.anchors import _OBPI_PATTERN as _ANCHOR_OBPI_PATTERN
from gzkit.ledger import extract_bare_obpi_id
from gzkit.lock_manager import adr_id_from_obpi
from gzkit.obpi_completion_fence import obpi_id_from_path
from gzkit.pipeline_markers import _obpi_short_form
from gzkit.pipeline_position import _short_form
from gzkit.quality import _is_non_obpi_register_entry
from gzkit.sync import PARENT_LINK_RE
from gzkit.tasks import in_scope_task_id
from gzkit.triangle import _extract_obpi_short_id

_FULL = "OBPI-0.28.0-01-context-core"
_SHORT = "OBPI-0.28.0-01"


class TestShortFormExtractors(unittest.TestCase):
    """A reader that cuts the short form out of a longer string stops at the seam's item."""

    def test_each_extractor_returns_the_short_form_of_a_full_id(self) -> None:
        extractors = (
            _extract_obpi_id_from_name,
            _obpi_lineage_id,
            _obpi_short_form,
            _resolve_artifact_id_from_stem,
            _extract_obpi_short_id,
            extract_bare_obpi_id,
        )
        for extract in extractors:
            with self.subTest(extractor=extract.__name__):
                self.assertEqual(extract(_FULL), _SHORT)
                self.assertEqual(extract(_SHORT), _SHORT)

    def test_path_readers_find_the_short_form_inside_a_path(self) -> None:
        path = f"docs/design/adr/ADR-0.28.0-x/obpis/{_FULL}.md"
        self.assertEqual(obpi_id_from_path(path), _SHORT)
        self.assertEqual(_extract_obpi_id(Path(path)), _SHORT)
        self.assertEqual(state_cmd._OBPI_SHORT_ID_RE.match(_FULL).group(1), _SHORT)
        self.assertEqual(task_cmd._OBPI_LINEAGE_RE.match(_FULL).group(1), _SHORT)
        self.assertEqual(vfm._OBPI_ID_PATTERN.match(_FULL).group(1), _SHORT)

    def test_a_one_digit_item_is_no_short_form(self) -> None:
        self.assertIsNone(obpi_id_from_path("obpis/OBPI-0.28.0-1-x.md"))
        self.assertIsNone(_extract_obpi_short_id("OBPI-0.28.0-1-x"))
        self.assertIsNone(extract_bare_obpi_id("OBPI-0.28.0-1-x"))
        self.assertIsNone(vfm._OBPI_ID_PATTERN.match("OBPI-0.28.0-1-x"))

    def test_the_run_short_form_keeps_the_whole_item_number(self) -> None:
        self.assertEqual(_short_form("OBPI-0.99.0-100-wide"), "OBPI-0.99.0-100")
        self.assertEqual(_short_form("OBPI-0.99.0-7-narrow"), "OBPI-0.99.0-7")


def _extract_obpi_id_from_name(value: str) -> str | None:
    return _extract_obpi_id(Path(value))


def _resolve_artifact_id_from_stem(value: str) -> str:
    return _resolve_artifact_id(Path(f"{value}.md"))


class TestParentOfAnObpi(unittest.TestCase):
    """The ADR an OBPI names is read from the seam's semver part."""

    def test_adr_is_derived_from_the_semver_part(self) -> None:
        for derive in (adr_id_from_obpi, _derive_adr_id):
            with self.subTest(derive=derive.__module__):
                self.assertEqual(derive(_FULL), "ADR-0.28.0")
                self.assertIsNone(derive("OBPI-x"))

    def test_req_prefix_names_the_item(self) -> None:
        self.assertEqual(_req_prefix_for_obpi(_FULL), "REQ-0.28.0-01-")
        self.assertIsNone(_req_prefix_for_obpi("OBPI-0.28.0-1"))

    def test_scope_lookup_reads_adr_and_obpi_scopes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            ledger.write_text(
                '{"event": "task_started", "task_id": "TASK-0.28.0-01-01-01"}\n',
                encoding="utf-8",
            )
            self.assertEqual(in_scope_task_id(ledger, _FULL), "TASK-0.28.0-01-01-01")
            self.assertEqual(in_scope_task_id(ledger, "ADR-0.28.0-x"), "TASK-0.28.0-01-01-01")
            self.assertIsNone(in_scope_task_id(ledger, "OBPI-0.28.0-02-other"))
            self.assertIsNone(in_scope_task_id(ledger, "REQ-0.28.0-01-01"))


class TestWholeIdReaders(unittest.TestCase):
    """Readers that accept or refuse a whole id agree with the seam's frontmatter pattern."""

    def test_brief_structure_handoff_and_anchor_accept_the_same_ids(self) -> None:
        for matcher in (
            brief_structure._OBPI_ID_RE.match,
            _HANDOFF_OBPI_ID_RE.match,
            _ANCHOR_OBPI_PATTERN.match,
        ):
            self.assertIsNotNone(matcher(_SHORT))
            self.assertIsNone(matcher("OBPI-0.28.0"))
            self.assertIsNone(matcher("OBPI-0.28.0-1"))

    def test_justify_binding_keys_a_short_and_a_full_id_together(self) -> None:
        self.assertEqual(_subject_key(_FULL), ("obpi", "0.28.0-01", "context-core"))
        self.assertEqual(_subject_key(_SHORT), ("obpi", "0.28.0-01", None))
        self.assertEqual(_subject_key("OBPI-0.28.0-1")[0], "id")

    def test_register_entry_is_non_obpi_only_when_the_key_is_no_obpi_id(self) -> None:
        self.assertTrue(_is_non_obpi_register_entry("obpi_id: mx-session\n"))
        self.assertFalse(_is_non_obpi_register_entry(f"obpi_id: {_SHORT}\n"))
        self.assertFalse(_is_non_obpi_register_entry(f"obpi_id: {_FULL}\n"))


class TestTextReaders(unittest.TestCase):
    """Readers of prose around an id."""

    def test_checklist_prefix_is_stripped_by_the_seam_short_form(self) -> None:
        self.assertEqual(
            _normalized_objective_from_checklist_item(f"{_SHORT}: Ship the loader"),
            "Ship the loader.",
        )

    def test_short_obpi_id_drops_the_semver(self) -> None:
        self.assertEqual(_short_obpi_id(_FULL), "01-context-core")
        self.assertEqual(_short_obpi_id("not-an-id"), "not-an-id")

    def test_brief_metadata_strips_the_id_from_the_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / f"{_FULL}.md"
            brief.write_text(f"---\nid: {_FULL}\n---\n# {_SHORT}: Context core\n", encoding="utf-8")
            self.assertEqual(extract_brief_metadata(brief)["title"], "Context core")

    def test_parent_link_reads_any_prd_adr_or_obpi_reference(self) -> None:
        for ref in ("PRD-gzkit", "ADR-0.1.0-x", _FULL):
            with self.subTest(ref=ref):
                self.assertEqual(PARENT_LINK_RE.search(f"**Parent:** [{ref}](x.md)").group(1), ref)

    def test_checklist_scoring_reads_the_seam_short_form(self) -> None:
        good = f"## Checklist\n- [ ] {_SHORT}: a\n"
        bad = "## Checklist\n- [ ] a thing without an id\n"
        self.assertEqual(_score_feature_checklist(good, 1)[0], 4)
        self.assertLess(_score_feature_checklist(bad, 1)[0], 4)

    def test_decomposition_numbers_items_from_the_file_stem(self) -> None:
        paths = [Path(f"OBPI-0.28.0-0{n}-x.md") for n in (1, 2, 3)]
        gap = [Path("OBPI-0.28.0-01-x.md"), Path("OBPI-0.28.0-03-x.md")]
        with_sequence = _score_obpi_decomposition(paths, ["a"] * 3)[0]
        with_gap = _score_obpi_decomposition(gap, ["a"] * 2)[0]
        self.assertGreater(with_sequence, with_gap)

    def test_independence_requires_the_dependency_to_be_declared_by_id(self) -> None:
        body = f"This work depends on {_SHORT} first.\n"
        declared = f"{body}\n## Dependencies\n- depends on {_SHORT}\n"
        other = f"{body}\n## Dependencies\n- depends on OBPI-0.28.0-02\n"
        self.assertEqual(_score_obpi_independence(declared), 3)
        self.assertEqual(_score_obpi_independence(other), 2)
        self.assertEqual(_score_obpi_independence("No dependencies.\n"), 4)


class TestTrustAuditReaders(unittest.TestCase):
    """The brief audits read frontmatter ids and file names by the seam."""

    def test_frontmatter_id_lines_carry_the_short_form_and_its_slug(self) -> None:
        fm = f"id: {_FULL}\nparent: ADR-0.28.0-x\npaired_with: {_SHORT}\n"
        self.assertEqual(absorption_duplicates._OBPI_ID_LINE.search(fm).group(1), _FULL)
        self.assertEqual(absorption_duplicates._PAIRED_WITH_LINE.search(fm).group(1), _SHORT)
        self.assertEqual(briefs._OBPI_ID_IN_FRONTMATTER.search(fm).group(1), _FULL)
        self.assertIsNone(briefs._OBPI_ID_IN_FRONTMATTER.search("id: OBPI-0.28.0-1\n"))

    def test_brief_file_names_split_into_semver_and_item(self) -> None:
        match = briefs._OBPI_FILE_PATTERN.match(f"{_FULL}.md")
        self.assertEqual((match["semver"], match["item"]), ("0.28.0", "01"))
        self.assertIsNone(briefs._OBPI_FILE_PATTERN.match("OBPI-0.28.0-1-x.md"))

    def test_cross_references_read_a_malformed_item_as_a_reference(self) -> None:
        found = [
            m.group(0)
            for m in briefs._BRIEF_CROSS_REF_PATTERN.finditer(
                f"see {_FULL} and OBPI-0.28.0-2 and ADR-0.28.0"
            )
        ]
        self.assertEqual(found, [_FULL, "OBPI-0.28.0-2", "ADR-0.28.0"])


class TestRenderedHooksCarryTheSeamBodies(unittest.TestCase):
    """A hook script is rendered with the seam's bodies and keeps no placeholder."""

    def test_rendered_scripts_embed_the_seam_body_and_compile(self) -> None:
        for render in (
            _plan_audit_gate_script,
            _obpi_completion_validator_script,
            _stop_turn_feedback_script,
        ):
            with self.subTest(script=render.__name__):
                script = render()
                self.assertNotIn("__obpi", script)
                self.assertNotIn("__adr", script)
                self.assertIn(OBPI_SHORT_ID_BODY, script)
                compile(script, render.__name__, "exec")


if __name__ == "__main__":
    unittest.main()
