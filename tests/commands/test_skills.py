import json
import os
import shutil
import tempfile
import unittest
from contextlib import ExitStack
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.quality import QualityResult
from gzkit.traceability import covers
from tests.commands.common import (
    CliRunner,
    start_init_subprocess_patches,
    stop_init_subprocess_patches,
)

# Module-level cache: run ``gz init`` once into a template dir. Each test
# copytrees the template into its own workspace instead of paying the init
# cost per test (GHI #253). ~130ms per init × 15 tests -> 1 × 130ms + 15 ×
# ~40ms copytree = ~0.7s saved.
_TEMPLATE_CTX: tempfile.TemporaryDirectory | None = None
_TEMPLATE_DIR: Path | None = None
_ORIG_CWD: Path | None = None


def setUpModule() -> None:
    """Stub init subprocesses and build a cached init'd project template."""
    global _TEMPLATE_CTX, _TEMPLATE_DIR, _ORIG_CWD
    start_init_subprocess_patches()
    _TEMPLATE_CTX = tempfile.TemporaryDirectory(prefix="gzkit-skills-tpl-")
    _TEMPLATE_DIR = Path(_TEMPLATE_CTX.name) / "project"
    _TEMPLATE_DIR.mkdir()
    _ORIG_CWD = Path.cwd()
    os.chdir(_TEMPLATE_DIR)
    try:
        CliRunner().invoke(main, ["init"])
    finally:
        os.chdir(_ORIG_CWD)


def tearDownModule() -> None:
    global _TEMPLATE_CTX, _TEMPLATE_DIR, _ORIG_CWD
    if _TEMPLATE_CTX is not None:
        _TEMPLATE_CTX.cleanup()
    _TEMPLATE_CTX = None
    _TEMPLATE_DIR = None
    _ORIG_CWD = None
    stop_init_subprocess_patches()


def _check_step_patch_targets(exclude: frozenset[str] | set[str] = frozenset()) -> list[str]:
    """Return a patch target for every `gz check` step, derived from the registry.

    Two namespaces are in play and the choice is not cosmetic: the handful of
    runners imported at `gzkit.commands.quality` module scope must be patched
    THERE, while the rest are imported lazily inside `_build_check_steps` and so
    resolve against `gzkit.quality` at call time.

    Derived rather than hand-listed because the hand-listed form silently
    omitted each newly added step, letting it execute for real against a temp
    project and fail a test about something else entirely (GHI #724/#725).
    """
    import gzkit.commands.quality as _cq  # noqa: PLC0415 - test-local, avoids import cycles

    targets = []
    for _label, runner in _cq._build_check_steps():
        name = runner.__name__
        if name in exclude:
            continue
        namespace = "gzkit.commands.quality" if hasattr(_cq, name) else "gzkit.quality"
        targets.append(f"{namespace}.{name}")
    return targets


class _InitFromTemplate:
    """Context manager: copytree cached init'd tree into a fresh tempdir.

    Drop-in for ``runner.isolated_filesystem()`` followed by
    ``runner.invoke(main, ["init"])`` — the result is the same post-init
    state, minus the ~130ms init cost.
    """

    def __init__(self) -> None:
        self._tmpctx: tempfile.TemporaryDirectory | None = None
        self._orig_cwd: Path | None = None

    def __enter__(self) -> None:
        assert _TEMPLATE_DIR is not None
        self._tmpctx = tempfile.TemporaryDirectory(prefix="gzkit-skills-test-")
        dest = Path(self._tmpctx.name) / "project"
        shutil.copytree(_TEMPLATE_DIR, dest)
        self._orig_cwd = Path.cwd()
        os.chdir(dest)

    def __exit__(self, *exc: object) -> None:
        if self._orig_cwd is not None:
            os.chdir(self._orig_cwd)
        if self._tmpctx is not None:
            self._tmpctx.cleanup()


class TestSkillCommands(unittest.TestCase):
    """Tests for skill subcommands."""

    @staticmethod
    def _write_stale_mirror_skill() -> None:
        stale = Path(".claude/skills/stale-skill")
        stale.mkdir(parents=True, exist_ok=True)
        (stale / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: stale-skill",
                    "description: stale mirror skill",
                    "lifecycle_state: active",
                    "owner: gzkit-governance",
                    "last_reviewed: 2026-03-01",
                    "---",
                    "",
                    "# SKILL.md",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _set_skill_last_reviewed_all_roots(skill_name: str, last_reviewed: str) -> None:
        roots = [".gzkit/skills", ".agents/skills", ".claude/skills"]
        for root in roots:
            skill_file = Path(root) / skill_name / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            updated = []
            for line in content.splitlines():
                if line.startswith("last_reviewed:"):
                    updated.append(f"last_reviewed: {last_reviewed}")
                else:
                    updated.append(line)
            skill_file.write_text("\n".join(updated) + "\n", encoding="utf-8")

    def test_skill_list(self) -> None:
        """skill list shows scaffolded skills."""
        runner = CliRunner()
        with _InitFromTemplate():
            result = runner.invoke(main, ["skill", "list"])
            self.assertEqual(result.exit_code, 0)
            # Should show core skills from init.  Active-skill fixture moved
            # from ``lint`` (retired in canonical 2026-04-03 → filtered by
            # scaffold_core_skills under OBPI-0.0.32-02) to ``gz-status``;
            # ``gz-adr-manager`` retired-and-not-scaffolded invariant is
            # what this test actually encodes.
            self.assertIn("gz-status", result.output)
            self.assertIn("gz-adr-create", result.output)
            self.assertNotIn("gz-adr-manager", result.output)

    @staticmethod
    def _mark_skill_retired(skill_name: str) -> None:
        """Rewrite a canonical skill file's lifecycle_state to retired."""
        skill_file = Path(".gzkit/skills") / skill_name / "SKILL.md"
        content = skill_file.read_text(encoding="utf-8")
        lines = [
            "lifecycle_state: retired" if line.startswith("lifecycle_state:") else line
            for line in content.splitlines()
        ]
        skill_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_skill_list_hides_retired_by_default(self) -> None:
        """skill list matches AGENTS catalog semantics — retired skills hidden.

        Fixture skill moved from ``lint`` (retired in canonical) to
        ``gz-status`` under OBPI-0.0.32-02; the test asserts the
        ``retired-then-hidden`` invariant, not anything ``lint``-specific.
        """
        runner = CliRunner()
        with _InitFromTemplate():
            self._mark_skill_retired("gz-status")
            result = runner.invoke(main, ["skill", "list"])
            self.assertEqual(result.exit_code, 0)
            json_result = runner.invoke(main, ["skill", "list", "--json"])
            self.assertEqual(json_result.exit_code, 0)
            names = [s["name"] for s in json.loads(json_result.output)["skills"]]
            self.assertNotIn("gz-status", names)
            self.assertIn("gz-adr-create", result.output)

    def test_skill_list_all_shows_retired_with_label(self) -> None:
        """skill list --all surfaces retired skills with an explicit label."""
        runner = CliRunner()
        with _InitFromTemplate():
            self._mark_skill_retired("gz-status")
            result = runner.invoke(main, ["skill", "list", "--all"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("gz-status", result.output)
            self.assertIn("retired", result.output.lower())

    def test_skill_list_json_default_filters_retired(self) -> None:
        """skill list --json excludes retired skills by default."""
        runner = CliRunner()
        with _InitFromTemplate():
            self._mark_skill_retired("gz-status")
            result = runner.invoke(main, ["skill", "list", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            names = [s["name"] for s in payload["skills"]]
            self.assertNotIn("gz-status", names)
            self.assertIn("gz-adr-create", names)
            self.assertFalse(payload["include_retired"])

    def test_skill_list_json_all_includes_lifecycle(self) -> None:
        """skill list --json --all includes every skill and its lifecycle_state."""
        runner = CliRunner()
        with _InitFromTemplate():
            self._mark_skill_retired("gz-status")
            result = runner.invoke(main, ["skill", "list", "--all", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            by_name = {s["name"]: s for s in payload["skills"]}
            self.assertIn("gz-status", by_name)
            self.assertEqual(by_name["gz-status"]["lifecycle_state"], "retired")
            self.assertEqual(by_name["gz-adr-create"]["lifecycle_state"], "active")
            self.assertTrue(payload["include_retired"])

    def test_skill_new(self) -> None:
        """skill new creates skill."""
        runner = CliRunner()
        with _InitFromTemplate():
            result = runner.invoke(main, ["skill", "new", "my-skill"])
            self.assertEqual(result.exit_code, 0)
            skill_file = Path(".gzkit/skills/my-skill/SKILL.md")
            self.assertTrue(skill_file.exists())
            content = skill_file.read_text(encoding="utf-8")
            self.assertIn("compatibility:", content)
            self.assertIn("invocation:", content)
            self.assertIn("gz_command:", content)
            self.assertIn("metadata:", content)

    def test_init_scaffolds_adr_create_and_removes_adr_manager(self) -> None:
        """core skill scaffolding uses gz-adr-create hard cutover."""
        with _InitFromTemplate():
            self.assertTrue(Path(".gzkit/skills/gz-adr-create/SKILL.md").exists())
            self.assertFalse(Path(".gzkit/skills/gz-adr-manager").exists())

    def test_init_scaffolds_git_sync_skill_with_canonical_body(self) -> None:
        """gz init delivers the git-sync skill that ``gz git-sync --skill`` advertises.

        Canonical contract: the path printed by ``gz git-sync --skill``
        (``.gzkit/skills/git-sync/SKILL.md``) MUST exist on consumer projects
        after ``gz init``, and the body MUST be the canonical workflow — not
        the generic ``Step 1 / Step 2 / Step 3`` template placeholder, which
        provides no operator value (GHI #315).
        """
        with _InitFromTemplate():
            skill_file = Path(".gzkit/skills/git-sync/SKILL.md")
            self.assertTrue(skill_file.exists())
            content = skill_file.read_text(encoding="utf-8")
            # Frontmatter resolves to the actual skill, not a placeholder.
            self.assertIn("name: git-sync", content)
            # Canonical body delivers the guarded-sync workflow, not the
            # generic template's "Step 1 / Step 2 / Step 3" filler.
            self.assertIn("uv run gz git-sync", content)
            self.assertNotIn("1. Step 1\n2. Step 2\n3. Step 3", content)

    def test_skill_audit_passes_after_init(self) -> None:
        """skill audit passes for freshly initialized project."""
        runner = CliRunner()
        with _InitFromTemplate():
            result = runner.invoke(main, ["skill", "audit"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("passed", result.output.lower())

    def test_skill_audit_warning_is_non_blocking_without_strict(self) -> None:
        """Stale mirror-only skills emit non-blocking warnings by default."""
        runner = CliRunner()
        with _InitFromTemplate():
            self._write_stale_mirror_skill()
            result = runner.invoke(main, ["skill", "audit"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("non-blocking", result.output.lower())
            self.assertIn("blocking: 0", result.output.lower())
            # At least one non-blocking warning, never an exact total: the fixture is
            # initialized from the real skill set, whose `last_reviewed:` dates age with
            # the calendar. Pinning the total made this fail on a date rollover with no
            # code change (observed 2026-08-20, when gz-content-remember crossed the
            # 75-day warn band). The claim under test is the DISPOSITION of the stale
            # mirror skill, not the fixture's warning census.
            self.assertRegex(result.output.lower(), r"non-blocking: [1-9]\d*")

    def test_skill_audit_strict_fails_on_non_blocking_warnings(self) -> None:
        """Strict mode escalates warnings to failure."""
        runner = CliRunner()
        with _InitFromTemplate():
            self._write_stale_mirror_skill()
            result = runner.invoke(main, ["skill", "audit", "--strict"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("non-blocking warnings", result.output.lower())
            self.assertIn("ska-mirror-dir-unexpected", result.output.lower())

    def test_skill_audit_json_includes_issue_codes_and_blocking_counts(self) -> None:
        """JSON payload includes additive policy fields for machine consumers."""
        runner = CliRunner()
        with _InitFromTemplate():
            self._write_stale_mirror_skill()
            result = runner.invoke(main, ["skill", "audit", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertIn("blocking_error_count", payload)
            self.assertIn("non_blocking_warning_count", payload)
            self.assertIn("max_review_age_days", payload)
            self.assertIn("stale_review_count", payload)
            self.assertGreaterEqual(payload["non_blocking_warning_count"], 1)
            self.assertEqual(payload["max_review_age_days"], 90)
            # Locate the issue by CODE, never by position: `issues[0]` assumed both an
            # ordering and a census of one. Calendar-driven review-age findings share the
            # list, so the subject of this test has to be named to be asserted about.
            mirror = [i for i in payload["issues"] if i.get("code") == "SKA-MIRROR-DIR-UNEXPECTED"]
            self.assertEqual(
                len(mirror), 1, f"expected one mirror finding, got {payload['issues']}"
            )
            issue = mirror[0]
            self.assertIn("code", issue)
            self.assertIn("blocking", issue)
            self.assertFalse(issue["blocking"], "a stale mirror-only skill must not block")

    def test_skill_audit_rejects_non_positive_max_review_age_days(self) -> None:
        """Non-positive max review age is rejected as invalid input."""
        runner = CliRunner()
        with _InitFromTemplate():
            result = runner.invoke(main, ["skill", "audit", "--max-review-age-days", "0"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("positive integer", result.output.lower())

    def test_skill_audit_max_review_age_override_relaxes_stale_failure(self) -> None:
        """Override can relax stale-review blocking checks when policy allows.

        Fixture skill changed from ``lint`` (retired in canonical 2026-04-03)
        to ``gz-prd`` (active CORE_SKILLS slug present in all four mirror
        surfaces) under OBPI-0.0.32-02 — ``scaffold_core_skills`` now reads
        ``lifecycle_state`` from canonical SKILL.md and skips retired slugs,
        making the prior ``lint`` fixture choice incidental rather than
        invariant.
        """
        runner = CliRunner()
        with _InitFromTemplate():
            stale_date = (date.today() - timedelta(days=120)).isoformat()
            self._set_skill_last_reviewed_all_roots("gz-prd", stale_date)

            default_result = runner.invoke(main, ["skill", "audit"])
            self.assertNotEqual(default_result.exit_code, 0)
            self.assertIn("ska-last-reviewed-stale", default_result.output.lower())

            relaxed_result = runner.invoke(main, ["skill", "audit", "--max-review-age-days", "365"])
            self.assertEqual(relaxed_result.exit_code, 0)

    def test_skill_audit_manpage_coverage_warns_when_index_exists(self) -> None:
        """Manpage coverage warns for active skills without manpages when index exists."""
        runner = CliRunner()
        with _InitFromTemplate():
            # Create the skills index to enable manpage checks
            index_dir = Path("docs/user/skills")
            index_dir.mkdir(parents=True, exist_ok=True)
            (index_dir / "index.md").write_text("# Skills\n", encoding="utf-8")
            result = runner.invoke(main, ["skill", "audit", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            manpage_issues = [i for i in payload["issues"] if i["code"] == "SKA-MANPAGE-MISSING"]
            self.assertTrue(len(manpage_issues) > 0)
            for issue in manpage_issues:
                self.assertFalse(issue["blocking"])

    def test_check_command_passes_with_non_blocking_skill_audit_warning(self) -> None:
        """Aggregate check remains pass when skill audit warning is non-blocking."""
        runner = CliRunner()
        with _InitFromTemplate():
            ok = QualityResult(success=True, command="cmd", stdout="", stderr="", returncode=0)
            warning_skill_audit = QualityResult(
                success=True,
                command="uv run gz skill audit",
                stdout="Warnings: SKA-MIRROR-DIR-UNEXPECTED",
                stderr="",
                returncode=0,
            )
            # Every gz check step is stubbed so the aggregate result depends
            # only on the non-blocking skill-audit warning under test. The
            # stubs are entered through an ExitStack rather than a
            # parenthesized `with`: the check pipeline has grown past 20
            # steps, and a parenthesized `with` hits Python's 20-block
            # static-nesting limit (SyntaxError) once it does.
            #
            # Targets are DERIVED from the live step registry, not hand-listed.
            # The hand-written tuple silently omitted every newly added step, so
            # the omitted step executed for real against the temp project — two
            # of them did exactly that (GHI #724/#725), failing this test for a
            # reason that had nothing to do with skill audits. A list that must
            # be updated in lockstep with another list, with nothing linking
            # them, is the same shape as the `GzkitConfig.load` key-list bug.
            ok_steps = _check_step_patch_targets(exclude={"run_skill_audit"})
            with ExitStack() as stack:
                for target in ok_steps:
                    stack.enter_context(patch(target, return_value=ok))
                stack.enter_context(
                    patch(
                        "gzkit.quality.run_skill_audit",
                        return_value=warning_skill_audit,
                    )
                )
                result = runner.invoke(main, ["check"])
            self.assertEqual(result.exit_code, 0)

    @covers("REQ-0.0.74-08-03")
    def test_gz_mx_skill_gz_command_resolves(self) -> None:
        """gz-mx skill's gz_command 'mx' resolves to the registered gz mx verb."""
        with _InitFromTemplate():
            skill_file = Path(".gzkit/skills/gz-mx/SKILL.md")
            self.assertTrue(skill_file.exists(), "gz-mx SKILL.md not scaffolded by gz init")
            content = skill_file.read_text(encoding="utf-8")
            self.assertIn("gz_command: mx", content, "gz-mx skill must declare gz_command: mx")
            runner = CliRunner()
            result = runner.invoke(main, ["mx", "--help"])
            self.assertEqual(result.exit_code, 0, "gz_command 'mx' must be a registered verb")
