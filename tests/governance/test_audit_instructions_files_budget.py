"""Fixture-level tests for ``audit_instructions_files_budget`` (GHI #373).

These tests pin the scan semantics — at-budget passes, +1 char is reported —
and isolate the audit from the live AGENTS.md / CLAUDE.md / .claude/rules/.

**Posture: advisory until 1.0** (operator ruling 2026-08-17, verbatim: *"temporary
stay of all control surface budget limits until version 1.0. I want to be warned,
and we may lift the limits as needed, but no blockers."*). The two properties that
must hold together are therefore in tension by design, and each is asserted
separately: an overrun is still MEASURED and REPORTED, and it contributes NO
finding. A test that only checked the empty return would pass against an audit
that had stopped looking, which is the failure mode the stay must not become.
"""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from gzkit.advisory import ADVISORY_MARKER
from gzkit.governance.trust_audits import audit_instructions_files_budget


def _run(root: Path) -> tuple[list[object], str]:
    """Run the audit, returning (findings, captured advisory stream)."""
    buffer = io.StringIO()
    with contextlib.redirect_stderr(buffer):
        findings = audit_instructions_files_budget(root)
    return list(findings), buffer.getvalue()


class InstructionsFilesBudgetAuditTests(unittest.TestCase):
    """Audit walks AGENTS.md / CLAUDE.md / glob-matched rule files."""

    def _write_budget(
        self, root: Path, files: dict[str, int], globs: list[dict[str, object]] | None = None
    ) -> None:
        target = root / "data" / "instructions_files_budget.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, object] = {"files": files}
        if globs is not None:
            payload["globs"] = globs
        target.write_text(json.dumps(payload), encoding="utf-8")

    def test_at_budget_boundary_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 100})
            (root / "AGENTS.md").write_text("x" * 100, encoding="utf-8")
            findings, advisories = _run(root)
            self.assertEqual(findings, [])
            self.assertNotIn("AGENTS.md", advisories)

    def test_overrun_contributes_no_finding(self) -> None:
        """The stay: an overrun must not change the exit code."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 100})
            (root / "AGENTS.md").write_text("x" * 101, encoding="utf-8")
            findings, _ = _run(root)
            self.assertEqual(findings, [])

    def test_overrun_is_still_measured_and_reported(self) -> None:
        """The stay suspends the consequence, never the observation."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 100})
            (root / "AGENTS.md").write_text("x" * 175, encoding="utf-8")
            _, advisories = _run(root)
            self.assertIn("AGENTS.md", advisories)
            self.assertIn("175", advisories)
            self.assertIn("100", advisories)
            self.assertIn("75", advisories)

    def test_overrun_advisory_names_the_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 10})
            (root / "AGENTS.md").write_text("x" * 11, encoding="utf-8")
            _, advisories = _run(root)
            self.assertIn("gz-context-diet", advisories)

    def test_under_budget_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"CLAUDE.md": 100})
            (root / "CLAUDE.md").write_text("x" * 50, encoding="utf-8")
            findings, advisories = _run(root)
            self.assertEqual(findings, [])
            self.assertNotIn("CLAUDE.md", advisories)

    def test_missing_file_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 100, "CLAUDE.md": 100})
            findings, advisories = _run(root)
            self.assertEqual(findings, [])
            self.assertEqual(advisories, "")

    def test_glob_arm_reports_only_the_overrunning_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)
            (rules / "ok.md").write_text("x" * 100, encoding="utf-8")
            (rules / "fat.md").write_text("x" * 200, encoding="utf-8")
            self._write_budget(
                root, {}, [{"pattern": ".claude/rules/*.md", "max_chars_per_file": 100}]
            )
            findings, advisories = _run(root)
            self.assertEqual(findings, [])
            self.assertIn("fat.md", advisories)
            self.assertNotIn("ok.md", advisories)

    def test_glob_no_matches_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(
                root, {}, [{"pattern": ".claude/rules/*.md", "max_chars_per_file": 100}]
            )
            findings, advisories = _run(root)
            self.assertEqual(findings, [])
            self.assertEqual(advisories, "")

    def test_missing_budget_data_uses_packaged_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("x" * 100, encoding="utf-8")
            findings, advisories = _run(root)
            self.assertEqual(findings, [])
            self.assertEqual(advisories, "")

    def test_budgets_stay_per_file_so_they_can_be_lifted_individually(self) -> None:
        """ "we may lift the limits as needed" — the data file stays the dial."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 10, "CLAUDE.md": 10_000})
            (root / "AGENTS.md").write_text("x" * 50, encoding="utf-8")
            (root / "CLAUDE.md").write_text("x" * 50, encoding="utf-8")
            _, advisories = _run(root)
            self.assertIn("AGENTS.md", advisories)
            self.assertNotIn("CLAUDE.md", advisories)


def _advisory_lines(stream: str) -> list[str]:
    return [line for line in stream.splitlines() if line.startswith(ADVISORY_MARKER)]


class SurfaceTotalsTests(unittest.TestCase):
    """Every surface an agent loads is measured against a total (GHI #1249, WP-13)."""

    def _write_config(self, root: Path, payload: dict[str, object]) -> None:
        target = root / "data" / "instructions_files_budget.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload), encoding="utf-8")

    def _write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_a_total_over_budget_is_one_advisory_with_size_budget_and_distance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root / ".claude" / "agents" / "a.md", "x" * 70)
            self._write(root / ".claude" / "agents" / "b.md", "x" * 60)
            self._write_config(
                root,
                {
                    "totals": [
                        {
                            "surface": "agent definitions",
                            "pattern": ".claude/agents/*.md",
                            "max_bytes": 100,
                        }
                    ]
                },
            )
            findings, stream = _run(root)
            self.assertEqual(findings, [])
            advisories = _advisory_lines(stream)
            self.assertEqual(len(advisories), 1)
            self.assertIn("agent definitions", advisories[0])
            self.assertIn("130", advisories[0])
            self.assertIn("100", advisories[0])
            self.assertIn("by 30", advisories[0])

    def test_a_total_within_budget_is_reported_but_is_not_an_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root / ".gzkit" / "personas" / "p.md", "x" * 40)
            self._write_config(
                root,
                {
                    "totals": [
                        {"surface": "personas", "pattern": ".gzkit/personas/*.md", "max_bytes": 100}
                    ]
                },
            )
            findings, stream = _run(root)
            self.assertEqual(findings, [])
            self.assertEqual(_advisory_lines(stream), [])
            self.assertIn("personas: 40 of 100 B", stream)

    def test_totals_measure_utf8_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root / ".gzkit" / "personas" / "p.md", "é" * 10)
            self._write_config(
                root,
                {
                    "totals": [
                        {"surface": "personas", "pattern": ".gzkit/personas/*.md", "max_bytes": 100}
                    ]
                },
            )
            _, stream = _run(root)
            self.assertIn("personas: 20 of 100 B", stream)

    def test_skill_descriptions_count_yaml_description_chars_of_model_invoked_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / ".claude" / "skills"
            self._write(
                skills / "plain" / "SKILL.md", "---\nname: plain\ndescription: abcde\n---\nbody\n"
            )
            # A block scalar is read whole, not as its first line `>`.
            self._write(
                skills / "folded" / "SKILL.md",
                "---\nname: folded\ndescription: >\n  fghij\n  klmno\n---\nbody "
                + "x" * 500
                + "\n",
            )
            self._write(
                skills / "manual" / "SKILL.md",
                "---\nname: manual\ndescription: zzzzzzzzzz\ndisable-model-invocation: true\n---\n",
            )
            self._write_config(
                root,
                {
                    "totals": [
                        {
                            "surface": "skill descriptions",
                            "pattern": ".claude/skills/*/SKILL.md",
                            "measure": "description_chars",
                            "max_chars": 100,
                        }
                    ]
                },
            )
            _, stream = _run(root)
            # abcde (5) + "fghij klmno" (11); the manual skill's description never loads.
            self.assertIn("skill descriptions: 16 of 100 chars", stream)

    def test_an_unterminated_frontmatter_is_not_a_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / ".claude" / "skills"
            self._write(skills / "good" / "SKILL.md", "---\nname: good\ndescription: abcde\n---\n")
            self._write(skills / "open" / "SKILL.md", "---\nname: open\ndescription: zzz\n")
            self._write_config(
                root,
                {
                    "totals": [
                        {
                            "surface": "skill descriptions",
                            "pattern": ".claude/skills/*/SKILL.md",
                            "measure": "description_chars",
                            "max_chars": 100,
                        }
                    ]
                },
            )
            _, stream = _run(root)
            self.assertIn("skill descriptions: 5 of 100 chars", stream)

    def test_an_unparseable_skill_frontmatter_is_reported_not_raised(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / ".claude" / "skills"
            self._write(skills / "good" / "SKILL.md", "---\nname: good\ndescription: abcde\n---\n")
            self._write(
                skills / "broken" / "SKILL.md",
                "---\nname: broken\ndescription: one: two: three\n---\n",
            )
            self._write_config(
                root,
                {
                    "totals": [
                        {
                            "surface": "skill descriptions",
                            "pattern": ".claude/skills/*/SKILL.md",
                            "measure": "description_chars",
                            "max_chars": 100,
                        }
                    ]
                },
            )
            findings, stream = _run(root)
            self.assertEqual(findings, [])
            self.assertIn("skill descriptions: 5 of 100 chars", stream)
            advisories = _advisory_lines(stream)
            self.assertEqual(len(advisories), 1)
            self.assertIn(".claude/skills/broken/SKILL.md", advisories[0])
            self.assertIn("YAML", advisories[0])

    def test_excluded_prefixes_are_not_counted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root / "AGENTS.md", "x" * 1000)
            self._write(root / "src" / "AGENTS.md", "x" * 30)
            self._write(root / "docs" / "deep" / "AGENTS.md", "x" * 20)
            self._write(root / ".claude" / "skills" / "AGENTS.md", "x" * 500)
            self._write(root / ".venv" / "lib" / "AGENTS.md", "x" * 500)
            self._write_config(
                root,
                {
                    "totals": [
                        {
                            "surface": "nested AGENTS.md",
                            "pattern": "**/AGENTS.md",
                            "exclude": ["AGENTS.md", ".claude/"],
                            "max_bytes": 1000,
                        }
                    ]
                },
            )
            _, stream = _run(root)
            self.assertIn("nested AGENTS.md: 50 of 1000 B", stream)

    def test_the_mx_banner_is_measured_against_the_injected_hook_text_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root / ".gzkit" / "mx.json",
                json.dumps({"session_id": "s", "mode": "safe", "contract": "c.md"}),
            )
            self._write_config(root, {"injected_hook_text": {"max_bytes": 10}})
            findings, stream = _run(root)
            self.assertEqual(findings, [])
            advisories = _advisory_lines(stream)
            self.assertEqual(len(advisories), 1)
            self.assertIn("MX banner", advisories[0])

    def test_no_marker_means_no_banner_is_injected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            self._write_config(root, {"injected_hook_text": {"max_bytes": 10}})
            _, stream = _run(root)
            self.assertEqual(_advisory_lines(stream), [])
            self.assertIn("MX banner: 0 of 10 B", stream)


class LiveBudgetFileTests(unittest.TestCase):
    """The project's budget file names every surface the drydock exit table lists."""

    def test_every_loaded_surface_has_a_budget(self) -> None:
        root = Path(__file__).resolve().parents[2]
        config = json.loads((root / "data" / "instructions_files_budget.json").read_text("utf-8"))
        surfaces = {entry["surface"] for entry in config["totals"]}
        self.assertEqual(
            surfaces,
            {"rules", "skill descriptions", "agent definitions", "nested AGENTS.md", "personas"},
        )
        self.assertIn("max_bytes", config["injected_hook_text"])
        rule_globs = [g for g in config["globs"] if g["pattern"] == ".claude/rules/*.md"]
        self.assertEqual(len(rule_globs), 1)


if __name__ == "__main__":
    unittest.main()
