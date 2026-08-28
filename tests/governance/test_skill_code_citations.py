"""Skill prose citing a `src/gzkit/` module must cite one that exists (GHI #896).

`gz validate --cli-alignment` already walks every ``.gzkit/skills/**/SKILL.md``:
it resolves the ``gz <verb>`` strings a skill NAMES and the manpage filenames it
POINTS AT. It had no arm for the implementation a skill DESCRIBES, so a rename or
a module-to-package split left the pointer rotting with nothing objecting.

Measured 2026-08-27 before this arm existed: three cited paths did not resolve --
``src/gzkit/cli.py`` (four skills), ``src/gzkit/commands/validate.py`` (two), and
``src/gzkit/governance/trust_audits.py`` (one, inside ``ghi-close/SKILL.md``
itself). Four were ``Command implementation:`` lines whose entire job is telling
an agent where the code lives; two were copy-paste examples an operator would run
verbatim. ``uv run gz check`` was green throughout.

The canonical instance of the class is GHI #884's origin: ``69bc4a84`` made the
Codex plugin the only permitted tier-1 dispatch surface AND, in the same commit,
left every surface describing that gate saying the proof was ``step.command[0]``.
The directive and the description of the gate it must satisfy drifted apart
inside one commit.

Scope is deliberately the existence half only. Whether prose still DESCRIBES what
the code does is a reading, not a state; whether a cited path resolves is
mechanical, and it was the half measuring 3-for-3 wrong.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_skill_code_citations

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _write_skill(root: Path, *, slug: str, body: str) -> Path:
    skill_dir = root / ".gzkit" / "skills" / slug
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill = skill_dir / "SKILL.md"
    skill.write_text(f"---\nname: {slug}\n---\n\n# {slug}\n\n{body}\n", encoding="utf-8")
    return skill


def _write_module(root: Path, relpath: str) -> None:
    target = root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("", encoding="utf-8")


class SkillCodeCitationBehavior(unittest.TestCase):
    """The arm fails closed on a cited module that does not exist."""

    def test_dangling_citation_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(
                root, slug="gz-thing", body="- Command implementation: `src/gzkit/gone.py`"
            )
            errors = audit_skill_code_citations(root)

        self.assertEqual(len(errors), 1, f"expected one error, got {errors}")
        self.assertEqual(errors[0].type, "skill_code_citation")
        self.assertIn("src/gzkit/gone.py", errors[0].message)

    def test_resolving_citation_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_module(root, "src/gzkit/here.py")
            _write_skill(
                root, slug="gz-thing", body="- Command implementation: `src/gzkit/here.py`"
            )
            self.assertEqual(audit_skill_code_citations(root), [])

    def test_package_split_is_flagged_and_recovery_names_the_package(self) -> None:
        """The measured shape: a module became a package of the same name.

        `src/gzkit/governance/trust_audits.py` -> `src/gzkit/governance/trust_audits/`
        is the exact drift found in `ghi-close/SKILL.md`. The message must name the
        package, because "does not exist" alone sends the reader hunting for a
        module that was never deleted so much as reshaped.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_module(root, "src/gzkit/governance/trust_audits/__init__.py")
            _write_skill(
                root,
                slug="gz-thing",
                body="fix touches `src/gzkit/governance/trust_audits.py` (validator)",
            )
            errors = audit_skill_code_citations(root)

        self.assertEqual(len(errors), 1, f"expected one error, got {errors}")
        self.assertIn("src/gzkit/governance/trust_audits/", errors[0].message)

    def test_citation_reports_its_line_number(self) -> None:
        """A repo-wide sweep is only actionable if each hit names where it lives."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root, slug="gz-thing", body="line one\n\n- see `src/gzkit/gone.py`")
            errors = audit_skill_code_citations(root)

        self.assertEqual(len(errors), 1)
        self.assertTrue(
            errors[0].artifact.endswith(":9"),
            f"artifact should carry the citing line, got {errors[0].artifact!r}",
        )

    def test_non_gzkit_paths_are_out_of_scope(self) -> None:
        """Deliberately narrow: only `src/gzkit/**/*.py`, the set measured wrong.

        Widening to every repo-relative path in skill prose is the same class on
        more surfaces and needs its own measurement first -- widening a checklist
        without measuring is how one comes to undercount its obligations (#854).
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root, slug="gz-thing", body="- see `scripts/nope.py` and `docs/nope.md`")
            self.assertEqual(audit_skill_code_citations(root), [])


class SkillCodeCitationRepoClean(unittest.TestCase):
    """The live tree cites no `src/gzkit/` module that fails to resolve (GHI #896)."""

    def test_repo_skills_cite_only_modules_that_exist(self) -> None:
        errors = audit_skill_code_citations(_PROJECT_ROOT)
        self.assertFalse(
            errors,
            msg=(
                "Skill prose points at src/gzkit/ modules that do not exist. An agent "
                "reading the skill to find where a gate lives reasons about a module "
                "that is not there.\n" + "\n".join(f"  {e.artifact}: {e.message}" for e in errors)
            ),
        )


if __name__ == "__main__":
    unittest.main()
