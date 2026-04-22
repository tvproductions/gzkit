"""Surface-sync tests for OBPI-0.0.19-04 (REQ-05/06/07/08/10).

These tests never mutate `.gzkit/skills/` or `.claude/skills/` at the live
repository. `sync_skill_mirror` is invoked against tempfile-copied skill
directories so the test run is hermetic.
"""

from __future__ import annotations

import ast
import re
import shutil
import tempfile
import textwrap
import unittest
from pathlib import Path

import yaml

from gzkit.sync_skills import sync_skill_mirror
from gzkit.traceability import covers
from gzkit.validate_pkg.surface import validate_surfaces

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_SKILLS = PROJECT_ROOT / ".gzkit" / "skills"

SELF_PATH = Path(__file__).resolve()


def _read_skill(name: str) -> str:
    return (CANONICAL_SKILLS / name / "SKILL.md").read_text(encoding="utf-8")


def _parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        raise AssertionError("skill does not begin with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise AssertionError("skill frontmatter block is not closed")
    return yaml.safe_load(text[4:end]), text[end + 5 :]


def _skill_version(fm: dict[str, object]) -> str | None:
    direct = fm.get("skill-version")
    if isinstance(direct, str):
        return direct
    metadata = fm.get("metadata")
    if isinstance(metadata, dict):
        value = metadata.get("skill-version")
        if isinstance(value, str):
            return value
    return None


class TestGzAdrEvaluateLowScoreFooter(unittest.TestCase):
    """REQ-0.0.19-04-05 — adr-evaluate gains low-score footer block + version bump."""

    @covers("REQ-0.0.19-04-05")
    def test_adr_evaluate_has_low_score_footer_block(self) -> None:
        text = _read_skill("gz-adr-evaluate")
        fm, body = _parse_frontmatter(text)
        version = _skill_version(fm)
        self.assertIsNotNone(version, "skill-version missing from gz-adr-evaluate")
        assert version is not None
        self.assertTrue(
            version >= "6.3.0",
            f"gz-adr-evaluate skill-version must be >= 6.3.0 after REQ-05 (got {version})",
        )

        self.assertRegex(
            body,
            r"(?is)<\s*3\.0",
            "low-score footer must cite the <3.0 threshold",
        )
        self.assertRegex(
            body,
            r"(?i)(GHI|OBPI)",
            "low-score footer must reference tracking GHI or OBPI",
        )
        self.assertRegex(
            body,
            r"uv run -m gzkit justify",
            "low-score footer must include `uv run -m gzkit justify` suggestion",
        )
        self.assertRegex(
            body,
            r"(?i)ADR-0\.0\.19",
            "gz-adr-evaluate must cite ADR-0.0.19 in Related ADRs (REQ-08 linkage)",
        )


class TestGzObpiPipelineConfidenceBlock(unittest.TestCase):
    """REQ-0.0.19-04-06 — obpi-pipeline gains Stage 1→2 confidence block + version bump."""

    @covers("REQ-0.0.19-04-06")
    def test_obpi_pipeline_has_low_confidence_block(self) -> None:
        text = _read_skill("gz-obpi-pipeline")
        fm, body = _parse_frontmatter(text)
        version = _skill_version(fm)
        self.assertIsNotNone(version, "skill-version missing from gz-obpi-pipeline")
        assert version is not None
        self.assertTrue(
            version >= "6.9.0",
            f"gz-obpi-pipeline skill-version must be >= 6.9.0 after REQ-06 (got {version})",
        )

        self.assertRegex(
            body,
            r"(?is)<\s*90\s*%",
            "confidence block must cite the <90% threshold (Prime Directive invariant 11)",
        )
        self.assertRegex(
            body,
            r"(?i)invariant\s*11",
            "confidence block must cite Invariant 11 explicitly",
        )
        self.assertRegex(
            body,
            r"uv run -m gzkit justify.*--save",
            "confidence block must instruct `uv run -m gzkit justify <id> --save`",
        )
        self.assertRegex(
            body,
            r"(?i)ADR-0\.0\.19",
            "gz-obpi-pipeline must cite ADR-0.0.19 in Related ADRs (REQ-08 linkage)",
        )


class TestSurfaceSyncProducesMirrors(unittest.TestCase):
    """REQ-0.0.19-04-07 — sync_skill_mirror produces Claude+Copilot mirrors."""

    @covers("REQ-0.0.19-04-07")
    def test_sync_produces_equivalent_mirrors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            src_skills = tmp_root / ".gzkit" / "skills"
            src_skills.mkdir(parents=True)
            for name in ("gz-justify", "gz-adr-evaluate", "gz-obpi-pipeline"):
                shutil.copytree(CANONICAL_SKILLS / name, src_skills / name)

            for target_rel in (".claude/skills", ".github/skills"):
                written = sync_skill_mirror(
                    tmp_root,
                    ".gzkit/skills",
                    target_rel,
                    exclude_dirs=set(),
                )
                self.assertTrue(
                    any("gz-justify" in path for path in written),
                    f"sync_skill_mirror did not mirror gz-justify into {target_rel}; "
                    f"wrote={written}",
                )

                for name in ("gz-justify", "gz-adr-evaluate", "gz-obpi-pipeline"):
                    mirror = tmp_root / target_rel / name / "SKILL.md"
                    self.assertTrue(
                        mirror.exists(),
                        f"expected mirror at {mirror.relative_to(tmp_root)}",
                    )
                    canon_body = (src_skills / name / "SKILL.md").read_text(encoding="utf-8")
                    mirror_body = mirror.read_text(encoding="utf-8")
                    # Canonical body must appear within (or equal) mirror body;
                    # vendors may add a generated-by header but must not mutate canon.
                    self.assertTrue(
                        canon_body.strip() in mirror_body
                        or mirror_body.strip() == canon_body.strip(),
                        f"{target_rel}/{name}/SKILL.md body drifted from canon",
                    )

                # gz-justify specifically carries gz_command: justify — confirm mirror preserves it.
                justify_mirror = (tmp_root / target_rel / "gz-justify" / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn(
                    "gz_command: justify",
                    justify_mirror,
                    f"{target_rel}/gz-justify lost `gz_command: justify` directive after sync",
                )


class TestValidateSurfacesForJustifySkill(unittest.TestCase):
    """REQ-0.0.19-04-08 — validate_surfaces accepts gz-justify frontmatter (non-parity check)."""

    @covers("REQ-0.0.19-04-08")
    def test_validate_surfaces_accepts_justify_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "AGENTS.md").write_text(
                textwrap.dedent(
                    """\
                    # AGENTS.md

                    ## Project Identity

                    ## Persona

                    ## Prime Directive (Ownership)

                    ## Behavior Rules

                    ## Pattern Discovery

                    ## Skills

                    ## Gate Covenant

                    ## OBPI Acceptance Protocol

                    ## Execution Rules

                    ## Control Surfaces
                    """
                ),
                encoding="utf-8",
            )
            (tmp_root / "CLAUDE.md").write_text("# CLAUDE.md\n", encoding="utf-8")

            skill_dir = tmp_root / ".gzkit" / "skills" / "gz-justify"
            skill_dir.mkdir(parents=True)
            shutil.copy2(
                CANONICAL_SKILLS / "gz-justify" / "SKILL.md",
                skill_dir / "SKILL.md",
            )

            errors = validate_surfaces(tmp_root, check_sync_parity=False)
            justify_errors = [
                err for err in errors if "gz-justify" in str(getattr(err, "artifact", ""))
            ]
            self.assertEqual(
                justify_errors,
                [],
                f"validate_surfaces flagged gz-justify: {justify_errors}",
            )


class TestTestsDoNotMutateLivePaths(unittest.TestCase):
    """REQ-0.0.19-04-10 — tests in this module never write under live `.gzkit/` or `.claude/`."""

    @covers("REQ-0.0.19-04-10")
    def test_tests_do_not_mutate_live_repo_paths(self) -> None:
        for test_file in (
            PROJECT_ROOT / "tests" / "skills" / "test_gz_justify_skill.py",
            SELF_PATH,
        ):
            source = test_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
            offenders: list[str] = []
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                name = ""
                if isinstance(func, ast.Attribute):
                    name = func.attr
                elif isinstance(func, ast.Name):
                    name = func.id
                if name not in {
                    "write_text",
                    "write_bytes",
                    "unlink",
                    "mkdir",
                    "rmtree",
                    "copytree",
                    "copy",
                    "copy2",
                }:
                    continue
                for arg in node.args:
                    literal = self._literal_of(arg)
                    if literal is None:
                        continue
                    if re.search(
                        r"^(?!.*tmp).*\.(gzkit|claude|github)/skills",
                        literal,
                    ):
                        offenders.append(f"{test_file.name}: {name}({literal!r})")
            self.assertEqual(
                offenders,
                [],
                f"tests must not write to live skill paths: {offenders}",
            )

    @staticmethod
    def _literal_of(node: ast.AST) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None


if __name__ == "__main__":
    unittest.main()
