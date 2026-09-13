"""Chore metadata has one authority: its JSON (GHI #1002).

A chore's acceptance criteria and registry metadata were authored twice, in
``CHORE.md`` prose and in the JSON ``gz chores`` executes, and 17 of 40 chores'
criteria plus 7 versions had drifted. ``.gzkit/rules/governance-core.md``: *"A
value written in a Markdown doc is ILLUSTRATIVE, never authoritative ... Cite
the authority, not the value."*

These tests pin why that matters: an agent following ``CHORE.md`` must never be
told a criterion the runner does not check, or a version, lane, slug, vendor or
timeout the registry does not carry.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_chore_metadata_authority

_CITING_SECTION = (
    "## Acceptance Criteria\n\n"
    "The machine criteria live in `acceptance.json`; render them with "
    "`uv run gz chores plan demo`.\n"
)


def _tree(
    root: Path,
    chore_md: str,
    *,
    commands: tuple[str, ...] = ("uv run gz lint",),
    entry: dict | None = None,
) -> None:
    """Write one registered chore under the default ``.gzkit/chores`` surface."""
    chores = root / ".gzkit" / "chores"
    slug_dir = chores / "demo"
    slug_dir.mkdir(parents=True)
    (root / ".gzkit.json").write_text("{}", encoding="utf-8")
    registry_entry = {
        "slug": "demo",
        "title": "Demo",
        "version": "1.2.0",
        "path": ".gzkit/chores/demo",
        "lane": "lite",
        "timeoutSeconds": 300,
    }
    registry_entry.update(entry or {})
    (chores / "registry.json").write_text(
        json.dumps({"chores": [registry_entry]}), encoding="utf-8"
    )
    criteria = [{"type": "exitCodeEquals", "command": c, "expected": 0} for c in commands]
    (slug_dir / "acceptance.json").write_text(json.dumps({"criteria": criteria}), encoding="utf-8")
    (slug_dir / "CHORE.md").write_text(chore_md, encoding="utf-8")


class TestLiveTree(unittest.TestCase):
    def test_every_registered_chore_defers_to_its_json(self) -> None:
        root = Path(__file__).resolve().parents[2]
        errors = audit_chore_metadata_authority(root)
        self.assertEqual(errors, [], "\n".join(f"{e.artifact}: {e.message}" for e in errors))


class TestVersion(unittest.TestCase):
    def test_a_version_stated_in_chore_md_is_refused_even_when_it_matches(self) -> None:
        # Equality today is not the property: the copy is what drifted in 7
        # chores, so the registry must be the only place a version is written.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, "# Demo\n\n**Version:** 1.2.0\n\n" + _CITING_SECTION)
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("version", errors[0].message)
        self.assertIn("registry.json", errors[0].message)

    def test_a_history_note_newer_than_the_registry_is_refused(self) -> None:
        # A change note names a version too: announcing 1.3.0 while the
        # registry still carries 1.2.0 is the same drift in another place.
        body = "# Demo\n\n> **1.3.0 (2026-09-13):** tightened.\n\n" + _CITING_SECTION
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, body)
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("1.3.0", errors[0].message)

    def test_history_notes_whose_newest_is_the_registry_version_pass(self) -> None:
        body = (
            "# Demo\n\n> **Version 1.2.0 (2026-09-13):** tightened.\n\n"
            "> **1.1.0 (2026-08-01):** first cut.\n\n" + _CITING_SECTION
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, body)
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(errors, [])


class TestHeaderFields(unittest.TestCase):
    def test_a_lane_that_disagrees_with_the_registry_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, "# Demo\n\n- **Lane:** Heavy\n\n" + _CITING_SECTION)
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("Lane", errors[0].message)

    def test_agreeing_fields_with_rationale_pass(self) -> None:
        body = (
            "# Demo\n\n- **Lane:** Lite\n- **Slug:** `demo`\n"
            "- **Timeout:** 300s — calibrated to the suite\n\n"
            "## Policy\n\n- **Lane:** Lite — internal refactoring only\n\n" + _CITING_SECTION
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, body)
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(errors, [])

    def test_every_held_field_is_compared_with_its_registry_key(self) -> None:
        cases = (
            ("Slug", "- **Slug:** `other`\n", {}),
            ("Vendor", "- **Vendor:** `codex`\n", {"vendor": "claude"}),
            ("Vendor", "- **Vendor:** `claude`\n", {}),  # stated, registry carries none
        )
        for field, line, entry in cases:
            with self.subTest(field=field, line=line), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _tree(root, "# Demo\n\n" + line + "\n" + _CITING_SECTION, entry=entry)
                errors = audit_chore_metadata_authority(root)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn(field, errors[0].message)

    def test_a_timeout_that_disagrees_with_the_registry_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, "# Demo\n\n**Timeout:** 900s\n\n" + _CITING_SECTION)
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("Timeout", errors[0].message)


class TestCriteria(unittest.TestCase):
    def test_a_criterion_command_the_json_does_not_run_is_refused(self) -> None:
        # The measured shape: CHORE.md said `test -f`, the JSON ran a freshness check.
        body = _CITING_SECTION + "\n- `test -f proofs/summary.md` exits 0\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, "# Demo\n\n" + body)
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("test -f proofs/summary.md", errors[0].message)

    def test_a_criteria_table_is_refused_even_without_code_spans(self) -> None:
        # The section cites the JSON, so a table there can only be a second copy.
        body = (
            _CITING_SECTION
            + "\n| Type | Command |\n|---|---|\n| exitCodeEquals | uv run gz lint |\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, "# Demo\n\n" + body)
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("table", errors[0].message)

    def test_a_fenced_criterion_the_json_does_not_run_is_refused(self) -> None:
        body = _CITING_SECTION + "\n```bash\nuv run gz validate --documents\n```\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, "# Demo\n\n" + body)
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("uv run gz validate --documents", errors[0].message)

    def test_naming_a_command_the_json_runs_passes(self) -> None:
        # Rationale may quote a criterion, exactly or as its bare `gz` form.
        rationale = "\n`uv run gz lint` holds the baseline; `gz lint` is the same check.\n"
        body = _CITING_SECTION + rationale
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, "# Demo\n\n" + body)
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(errors, [])

    def test_commands_outside_the_criteria_section_are_not_criteria(self) -> None:
        # Evidence and workflow commands write proofs; the runner never gates on them.
        body = (
            "# Demo\n\n## Workflow\n\n```bash\nuv run gz status --table\n```\n\n"
            + _CITING_SECTION
            + "\n## Evidence Commands\n\n```bash\nuv run gz cli audit > proofs/a.txt\n```\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, body)
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(errors, [])

    def test_a_criteria_section_that_does_not_cite_the_json_is_refused(self) -> None:
        # Without the citation a reader cannot tell the section is incomplete.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, "# Demo\n\n## Acceptance Criteria\n\nRun the checks.\n")
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("acceptance.json", errors[0].message)

    def test_a_chore_with_no_criteria_section_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, "# Demo\n\n## Workflow\n\nDo the thing.\n")
            errors = audit_chore_metadata_authority(root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("acceptance.json", errors[0].message)


if __name__ == "__main__":
    unittest.main()
