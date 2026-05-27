"""REQ-derived tests for OBPI-0.0.57-03-foundation-triage-skill.

Asserts the canonical SKILL.md is structurally compliant, the bundled
triage helper is invocable without mutating any foundation ADR or the
ledger, and the cognitive-pass section names the port/adapter
reclassification check. Each test class covers exactly one REQ from the
brief's `## Requirements (FAIL-CLOSED)` list.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gzkit.skills import _parse_frontmatter
from gzkit.traceability import covers

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CANONICAL_SKILL = _REPO_ROOT / ".gzkit" / "skills" / "gz-foundation-triage" / "SKILL.md"
_WHEEL_SKILL = _REPO_ROOT / "src" / "gzkit" / "skills" / "gz-foundation-triage" / "SKILL.md"
_CLAUDE_MIRROR = _REPO_ROOT / ".claude" / "skills" / "gz-foundation-triage" / "SKILL.md"
_GITHUB_MIRROR = _REPO_ROOT / ".github" / "skills" / "gz-foundation-triage" / "SKILL.md"
_AGENTS_MIRROR = _REPO_ROOT / ".agents" / "skills" / "gz-foundation-triage" / "SKILL.md"
_TRIAGE_SCRIPT = _REPO_ROOT / ".gzkit" / "skills" / "gz-foundation-triage" / "scripts" / "triage.py"


def _frontmatter_and_body(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(text)
    return fm, body


class TestREQ01_FrontmatterAndDescription(unittest.TestCase):
    """REQ-0.0.57-03-01: frontmatter validates; description names the operator moment."""

    @covers("REQ-0.0.57-03-01")
    def test_skill_md_exists_at_canonical_path(self) -> None:
        self.assertTrue(_CANONICAL_SKILL.exists(), f"missing canonical skill: {_CANONICAL_SKILL}")

    @covers("REQ-0.0.57-03-01")
    def test_frontmatter_name_is_gz_foundation_triage(self) -> None:
        fm, _ = _frontmatter_and_body(_CANONICAL_SKILL)
        self.assertEqual(fm.get("name"), "gz-foundation-triage")

    @covers("REQ-0.0.57-03-01")
    def test_description_names_operator_moment(self) -> None:
        fm, _ = _frontmatter_and_body(_CANONICAL_SKILL)
        description = fm.get("description", "")
        self.assertIn("rank the in-flight foundation backlog", description.lower())


class TestREQ02_ThreeStepStructure(unittest.TestCase):
    """REQ-0.0.57-03-02: Step 1 → Step 2 → Step 3 headings appear in order."""

    @covers("REQ-0.0.57-03-02")
    def test_three_steps_appear_in_order(self) -> None:
        _, body = _frontmatter_and_body(_CANONICAL_SKILL)
        # Match heading form only ('### Step N' or '## Step N') so the
        # prose-level "from Step 3" backreferences elsewhere in the body
        # do not confuse the ordering check.
        heading_re = re.compile(r"^#{2,3}\s+Step\s+(\d)\b", re.MULTILINE)
        order = [int(m.group(1)) for m in heading_re.finditer(body)]
        self.assertEqual(
            order[:3],
            [1, 2, 3],
            msg=f"three-step headings must appear in 1→2→3 order; saw {order}",
        )


class TestREQ03_SkillIsRegistered(unittest.TestCase):
    """REQ-0.0.57-03-03: gz skill list includes gz-foundation-triage."""

    @covers("REQ-0.0.57-03-03")
    def test_skill_list_includes_gz_foundation_triage(self) -> None:
        from gzkit.skills import list_skills

        names = [s.name for s in list_skills(_REPO_ROOT)]
        self.assertIn("gz-foundation-triage", names)


class TestREQ04_EphemeralDiagnosisOnly(unittest.TestCase):
    """REQ-0.0.57-03-04: invoking triage does not mutate any foundation ADR or ledger entry."""

    @covers("REQ-0.0.57-03-04")
    def test_triage_run_leaves_governance_surfaces_untouched(self) -> None:
        self.assertTrue(_TRIAGE_SCRIPT.exists(), f"missing triage script: {_TRIAGE_SCRIPT}")
        scope = [
            "docs/design/adr/foundation/",
            ".gzkit/ledger.jsonl",
        ]
        before = subprocess.run(
            ["git", "status", "--porcelain", *scope],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        completed = subprocess.run(
            [sys.executable, str(_TRIAGE_SCRIPT), "--format", "json"],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        try:
            json.loads(completed.stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover — diagnostic clarity
            self.fail(f"triage --format json did not emit valid JSON: {exc}")
        after = subprocess.run(
            ["git", "status", "--porcelain", *scope],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        # Compare BEFORE vs AFTER rather than asserting fully-clean — the
        # ledger may already be dirty from a prior governance event (lock
        # claim, etc.). The ephemeral invariant says triage adds nothing.
        self.assertEqual(
            before,
            after,
            msg=f"triage mutated governance surfaces: before={before!r} after={after!r}",
        )


class TestREQ05_PortAdapterReclassification(unittest.TestCase):
    """REQ-0.0.57-03-05: cognitive-pass section includes port/adapter reclassification check."""

    @covers("REQ-0.0.57-03-05")
    def test_cognitive_pass_section_names_port_adapter_reclassification(self) -> None:
        _, body = _frontmatter_and_body(_CANONICAL_SKILL)
        step2_start = body.find("Step 2")
        step3_start = body.find("Step 3", step2_start + 1)
        self.assertGreaterEqual(step2_start, 0)
        self.assertGreater(step3_start, step2_start)
        step2_section = body[step2_start:step3_start]
        self.assertRegex(
            step2_section,
            re.compile(r"port[/\s-]?adapter\s+reclassification", re.IGNORECASE),
            msg="Step 2 must name the port/adapter reclassification check",
        )


class TestREQ06_VendorMirrorByteParity(unittest.TestCase):
    """REQ-0.0.57-03-06: after sync, canonical and vendor mirrors are byte-equivalent."""

    @covers("REQ-0.0.57-03-06")
    def test_wheel_copy_byte_equals_canonical(self) -> None:
        self.assertTrue(_WHEEL_SKILL.exists(), f"missing wheel copy: {_WHEEL_SKILL}")
        self.assertEqual(
            _CANONICAL_SKILL.read_bytes(),
            _WHEEL_SKILL.read_bytes(),
        )

    @covers("REQ-0.0.57-03-06")
    def test_claude_mirror_byte_equals_canonical(self) -> None:
        self.assertTrue(_CLAUDE_MIRROR.exists(), f"missing claude mirror: {_CLAUDE_MIRROR}")
        self.assertEqual(
            _CANONICAL_SKILL.read_bytes(),
            _CLAUDE_MIRROR.read_bytes(),
        )

    @covers("REQ-0.0.57-03-06")
    def test_github_mirror_byte_equals_canonical(self) -> None:
        self.assertTrue(_GITHUB_MIRROR.exists(), f"missing github mirror: {_GITHUB_MIRROR}")
        self.assertEqual(
            _CANONICAL_SKILL.read_bytes(),
            _GITHUB_MIRROR.read_bytes(),
        )

    @covers("REQ-0.0.57-03-06")
    def test_agents_mirror_byte_equals_canonical(self) -> None:
        self.assertTrue(_AGENTS_MIRROR.exists(), f"missing agents mirror: {_AGENTS_MIRROR}")
        self.assertEqual(
            _CANONICAL_SKILL.read_bytes(),
            _AGENTS_MIRROR.read_bytes(),
        )


class TestFoundationSubpackage(unittest.TestCase):
    """Composer subpackage smoke tests — supports REQ-04 ephemeral invariant."""

    @covers("REQ-0.0.57-03-04")
    def test_gzkit_foundation_importable(self) -> None:
        spec = importlib.util.find_spec("gzkit.foundation")
        self.assertIsNotNone(spec, "gzkit.foundation subpackage must be importable")

    @covers("REQ-0.0.57-03-04")
    def test_gather_in_flight_foundations_is_pure_read(self) -> None:
        from gzkit.foundation import gather_in_flight_foundations

        entries = gather_in_flight_foundations(_REPO_ROOT)
        self.assertIsInstance(entries, list)
        for entry in entries:
            self.assertIn("id", entry)
            self.assertIn("status", entry)


class TestFoundationShortIdHandlesCanonicalSlug(unittest.TestCase):
    """Regression for GHI #518: canonical-slug id shape (no `-foundation-`
    substring) is the real corpus convention; the previous split heuristic
    filtered every real entry. Asserts gather_in_flight_foundations recovers
    the short-id from the leading ``ADR-X.Y.Z`` prefix."""

    def test_gather_in_flight_returns_entry_for_canonical_slug_id(self) -> None:
        from gzkit.foundation import gather_in_flight_foundations

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            adr_dir = (
                project_root
                / "docs"
                / "design"
                / "adr"
                / "foundation"
                / "ADR-0.0.37-constitutional-invariant-composition"
            )
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-0.0.37-constitutional-invariant-composition.md").write_text(
                "---\n"
                "id: ADR-0.0.37-constitutional-invariant-composition\n"
                "status: Draft\n"
                "title: Composition\n"
                "kind: foundation\n"
                "---\n\n"
                "# ADR-0.0.37: Composition\n",
                encoding="utf-8",
            )
            entries = gather_in_flight_foundations(project_root)
        self.assertEqual(
            len(entries),
            1,
            msg=(
                "GHI #518: gather_in_flight_foundations must return one entry "
                "for a canonical-slug id (no '-foundation-' substring); got "
                f"{entries!r}"
            ),
        )
        self.assertEqual(entries[0]["id"], "ADR-0.0.37")
        self.assertEqual(entries[0]["status"], "Draft")


class TestTriageScriptProjectRootResolution(unittest.TestCase):
    """Regression for GHI #518: triage script's ``_project_root_from_script``
    was off-by-one and resolved to ``<repo>/.gzkit/`` instead of ``<repo>``,
    causing the bare CLI invocation to scan a non-existent foundation dir
    and return ``[]``. ``--project-root`` consumers (e2e fixtures) masked it."""

    def test_resolves_repo_root_from_skills_scripts_location(self) -> None:
        spec = importlib.util.spec_from_file_location("_triage_script", _TRIAGE_SCRIPT)
        self.assertIsNotNone(spec)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp).resolve()
            script_path = repo / ".gzkit" / "skills" / "x" / "scripts" / "y.py"
            script_path.parent.mkdir(parents=True)
            script_path.write_text("", encoding="utf-8")
            resolved = module._project_root_from_script(script_path)
        self.assertEqual(
            resolved,
            repo,
            msg=(
                "GHI #518: _project_root_from_script must resolve to the "
                "repository root (4 levels above the script), not .gzkit/."
            ),
        )


if __name__ == "__main__":
    unittest.main()
