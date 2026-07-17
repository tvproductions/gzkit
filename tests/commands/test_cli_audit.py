"""Tests for CLI audit command with cross-coverage integration."""

import json
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli.main import main
from tests.commands.common import CliRunner


class TestCliAuditCrossCoverage(unittest.TestCase):
    """Verify cross-coverage data appears in cli audit output."""

    _json_data: dict
    _human_output: str

    @classmethod
    def setUpClass(cls) -> None:
        # ``gz cli audit`` runs the full cross-coverage scanner every time
        # and is ~1.5s per invocation. Share the expensive scanner call
        # across both JSON and human renderings so setUp pays the scan
        # once instead of twice (GHI #253).
        runner = CliRunner()
        from gzkit.doc_coverage.scanner import check_surfaces_report  # noqa: PLC0415

        original = check_surfaces_report

        cached_report: dict[str, object] = {}

        def _cached_scanner(project_root, *args, **kwargs):
            if "report" not in cached_report:
                cached_report["report"] = original(project_root, *args, **kwargs)
            return cached_report["report"]

        with patch(
            "gzkit.doc_coverage.scanner.check_surfaces_report",
            side_effect=_cached_scanner,
        ):
            json_result = runner.invoke(main, ["cli", "audit", "--json"])
            cls._json_data = json.loads(json_result.output)
            human_result = runner.invoke(main, ["cli", "audit"])
            cls._human_output = human_result.output

    def test_cli_audit_json_includes_cross_coverage(self) -> None:
        """JSON output must include a cross_coverage key with CoverageReport shape."""
        data = self._json_data
        self.assertIn("cross_coverage", data)
        cc = data["cross_coverage"]
        self.assertIn("commands_discovered", cc)
        self.assertIn("commands_fully_covered", cc)
        self.assertIn("commands_with_gaps", cc)
        self.assertIn("coverage", cc)
        self.assertIn("orphaned", cc)
        self.assertIn("passed", cc)
        self.assertGreater(cc["commands_discovered"], 0)

    def test_cli_audit_json_coverage_list_structure(self) -> None:
        """Each entry in cross_coverage.coverage must have expected fields."""
        cc = self._json_data["cross_coverage"]
        self.assertIsInstance(cc["coverage"], list)
        # At least one command should be present in the real project
        self.assertGreater(len(cc["coverage"]), 0)
        first = cc["coverage"][0]
        self.assertIn("command", first)
        self.assertIn("surfaces", first)
        self.assertIn("all_passed", first)
        self.assertIsInstance(first["surfaces"], list)
        self.assertGreater(len(first["surfaces"]), 0)
        surface = first["surfaces"][0]
        self.assertIn("surface", surface)
        self.assertIn("passed", surface)
        self.assertIn("detail", surface)

    def test_cli_audit_json_counts_consistent(self) -> None:
        """commands_fully_covered + commands_with_gaps must equal commands_discovered."""
        cc = self._json_data["cross_coverage"]
        self.assertEqual(
            cc["commands_fully_covered"] + cc["commands_with_gaps"],
            cc["commands_discovered"],
        )

    def test_cli_audit_human_shows_cross_coverage(self) -> None:
        """Human-readable output must include a Cross-coverage: section."""
        self.assertIn("Cross-coverage:", self._human_output)

    def test_cli_audit_json_result_has_valid_key(self) -> None:
        """JSON output must retain the existing 'valid' and 'issues' keys alongside cross_coverage.

        Ensures backward-compatible output contract is preserved.
        """
        data = self._json_data
        self.assertIn("valid", data)
        self.assertIn("issues", data)
        self.assertIn("cross_coverage", data)
        self.assertIsInstance(data["valid"], bool)
        self.assertIsInstance(data["issues"], list)


class TestPerFlagDocCoverage(unittest.TestCase):
    """Per-flag doc coverage: every registered argparse long flag must be documented (GHI #350)."""

    def test_discover_command_flags_extracts_long_flags_per_subcommand(self) -> None:
        """discover_command_flags returns {command: [flag, ...]} from add_argument calls."""
        from gzkit.doc_coverage.flag_scanner import discover_command_flags  # noqa: PLC0415

        source = textwrap.dedent(
            """
            def _build_parser():
                parser = StableArgumentParser()
                sub = parser.add_subparsers()
                p_validate = sub.add_parser("validate")
                p_validate.add_argument("--documents", action="store_true")
                p_validate.add_argument("--chores-layout", action="store_true")
                p_validate.set_defaults(func=lambda a: validate())
            """
        )
        flags = discover_command_flags(source)
        self.assertIn("validate", flags)
        self.assertIn("--documents", flags["validate"])
        self.assertIn("--chores-layout", flags["validate"])

    def test_discover_command_flags_scopes_parser_vars_per_register_function(self) -> None:
        """Sibling _register_* helpers reuse local var ``p`` without flag collision (GHI #355).

        Each ``_register_*(arb_commands)`` helper in ``parser_arb.py`` assigns
        ``p = arb_commands.add_parser("<verb>", ...)`` and then registers its
        flags via ``p.add_argument(...)``. With a global ``parser_vars`` dict,
        the last function's binding for ``p`` wins and every sibling's flags
        collapse onto that single leaf. Per-function scoping is the fix.
        """
        from gzkit.doc_coverage.flag_scanner import discover_command_flags  # noqa: PLC0415

        source = textwrap.dedent(
            """
            def _build_parser():
                parser = StableArgumentParser()
                commands = parser.add_subparsers()

            def register_arb_parsers(commands):
                p_arb = commands.add_parser("arb")
                arb_commands = p_arb.add_subparsers()
                _register_ruff(arb_commands)
                _register_step(arb_commands)
                _register_patterns(arb_commands)

            def _register_ruff(arb_commands):
                p = arb_commands.add_parser("ruff")
                p.add_argument("--fix", action="store_true")
                p.add_argument("--soft-fail", action="store_true")

            def _register_step(arb_commands):
                p = arb_commands.add_parser("step")
                p.add_argument("--name", required=True)
                p.add_argument("--soft-fail", action="store_true")

            def _register_patterns(arb_commands):
                p = arb_commands.add_parser("patterns")
                p.add_argument("--limit", type=int, default=500)
                p.add_argument("--compact", action="store_true")
            """
        )
        flags = discover_command_flags(source)
        self.assertEqual(sorted(flags.get("arb ruff", [])), ["--fix", "--soft-fail"])
        self.assertEqual(sorted(flags.get("arb step", [])), ["--name", "--soft-fail"])
        self.assertEqual(sorted(flags.get("arb patterns", [])), ["--compact", "--limit"])

    def test_discover_command_flags_handles_short_and_long_pair(self) -> None:
        """When add_argument has both -x and --xxx, only the long form is captured."""
        from gzkit.doc_coverage.flag_scanner import discover_command_flags  # noqa: PLC0415

        source = textwrap.dedent(
            """
            def _build_parser():
                parser = StableArgumentParser()
                sub = parser.add_subparsers()
                p_status = sub.add_parser("status")
                p_status.add_argument("-q", "--quiet", action="store_true")
                p_status.set_defaults(func=lambda a: status())
            """
        )
        flags = discover_command_flags(source)
        self.assertEqual(flags["status"], ["--quiet"])

    def test_check_flag_doc_coverage_flags_undocumented_flag(self) -> None:
        """check_flag_doc_coverage emits an issue when a flag has no doc mention (GHI #350).

        Closes the class of failure: a flag added to an existing command without
        any mention in the per-command doc previously survived every mechanical
        check (cli_audit reported 87/87 clean during the chores-layout gap).
        """
        import tempfile  # noqa: PLC0415

        from gzkit.doc_coverage.flag_scanner import check_flag_doc_coverage  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            commands_dir = Path(tmp)
            (commands_dir / "validate.md").write_text(
                "# gz validate\n\n## Examples\n\n### `--documents`\n\nDoc for documents.\n",
                encoding="utf-8",
            )
            flags_by_command = {"validate": ["--documents", "--undocumented-flag"]}
            issues = check_flag_doc_coverage(commands_dir, flags_by_command, waivers={})
            issue_text = " ".join(item["issue"] for item in issues)
            paths = {item["path"] for item in issues}
            self.assertEqual(len(issues), 1)
            self.assertIn("docs/user/manpages/validate.md", paths)
            self.assertIn("--undocumented-flag", issue_text)
            self.assertNotIn("--documents", issue_text)

    def test_per_flag_doc_waivers_match_real_project_drift(self) -> None:
        """Real-project per-flag drift must exactly equal the waiver snapshot (GHI #350).

        New flags added without docs => a fresh issue not in the waiver => fail.
        Stale waivers (flag waived but doc now exists, or flag removed from
        argparse) => over-waiver => fail.

        Drained when the GHI #353 doc-backlog work moves a waiver entry into
        an actual doc section.
        """
        from gzkit.commands.common import get_project_root  # noqa: PLC0415
        from gzkit.doc_coverage.flag_scanner import (  # noqa: PLC0415
            _PER_FLAG_DOC_WAIVERS,
            check_flag_doc_coverage,
            scan_command_flags,
        )

        project_root = get_project_root()
        flags_by_command = scan_command_flags(project_root)
        commands_dir = project_root / "docs" / "user" / "manpages"

        # 1. Audit with the live waiver: must surface zero drift.
        issues = check_flag_doc_coverage(commands_dir, flags_by_command)
        self.assertEqual(issues, [], f"New per-flag doc gaps surfaced: {issues}")

        # 2. Audit with empty waivers: every waivered flag must still be a real
        # gap in the live docs. A waiver entry whose flag is now documented
        # (or whose flag has been removed from argparse) is stale.
        no_waiver_issues = check_flag_doc_coverage(commands_dir, flags_by_command, waivers={})
        actual_gaps: dict[str, set[str]] = {}
        for issue in no_waiver_issues:
            slug = issue["path"].rsplit("/", 1)[-1].removesuffix(".md")
            command_name = slug.replace("-", " ", 1) if " " not in slug else slug
            flag = issue["issue"].split("`")[1]
            actual_gaps.setdefault(slug, set()).add(flag)

        for command_name, waived_flags in _PER_FLAG_DOC_WAIVERS.items():
            slug = command_name.replace(" ", "-")
            actual_for_command = actual_gaps.get(slug, set())
            stale = waived_flags - actual_for_command
            self.assertFalse(
                stale,
                f"Stale waivers for {command_name}: {sorted(stale)} — flags are now "
                f"documented (or removed); drop them from _PER_FLAG_DOC_WAIVERS.",
            )


class TestFlagSpecDiscovery(unittest.TestCase):
    """The scanner must carry a flag's contract, not merely its name (GHI #693).

    ``discover_command_flags`` returns names alone, which is why the audit can
    only ever check that a manpage *mentions* a flag. Truth-checking needs the
    argparse facts a manpage restates: whether the flag is required, and whether
    it takes a value.
    """

    def test_flag_spec_carries_required_and_value_taking_contract(self) -> None:
        """A discovered spec reports required-ness and whether the flag takes a value."""
        from gzkit.doc_coverage.flag_scanner import discover_command_flag_specs  # noqa: PLC0415

        source = textwrap.dedent(
            """
            def _build_parser():
                parser = StableArgumentParser()
                sub = parser.add_subparsers()
                p = sub.add_parser("authorize")
                p.add_argument("--handoff", required=True)
                p.add_argument("--json", action="store_true")
                p.add_argument("--note")
            """
        )
        specs = {spec.flag: spec for spec in discover_command_flag_specs(source)["authorize"]}

        self.assertTrue(specs["--handoff"].required)
        self.assertTrue(specs["--handoff"].takes_value)

        self.assertFalse(specs["--json"].required)
        self.assertFalse(
            specs["--json"].takes_value,
            "action='store_true' consumes no argument; a doc showing `--json VALUE` is false",
        )

        self.assertFalse(specs["--note"].required)
        self.assertTrue(specs["--note"].takes_value)


class TestPerFlagDocTruth(unittest.TestCase):
    """Manpage claims about a flag must AGREE with the parser, not merely mention it.

    GHI #693's class: a coupled-surface check that verifies the coupling EXISTS
    but not that it AGREES. `gz cli audit` asserted every flag was *mentioned*;
    nothing asserted that what the manpage *said* about it was true. The live
    instance (`gz handoff authorize --session-id`, 2026-07-16) shipped green
    while the manpage bracketed a required flag as optional.

    A wrong row is worse than a missing one: a missing row fails the audit
    loudly, while a wrong row passes green and is believed.
    """

    def _write_doc(self, tmp: str, body: str) -> Path:
        commands_dir = Path(tmp)
        (commands_dir / "authorize.md").write_text(body, encoding="utf-8")
        return commands_dir

    def test_required_flag_bracketed_as_optional_is_an_issue(self) -> None:
        """A required flag shown as `[--flag]` in Usage contradicts the parser (GHI #693).

        This is the observed instance: the parser declared
        ``required=True`` while the manpage's usage line bracketed
        ``[--session-id ID]``, and every gate was green.
        """
        import tempfile  # noqa: PLC0415

        from gzkit.doc_coverage.flag_scanner import FlagSpec, check_flag_doc_truth  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            commands_dir = self._write_doc(
                tmp,
                "# gz authorize\n\n## Usage\n\n```\n"
                "gz authorize --handoff PATH [--session-id ID]\n"
                "```\n",
            )
            specs = {
                "authorize": [
                    FlagSpec(flag="--handoff", required=True, takes_value=True),
                    FlagSpec(flag="--session-id", required=True, takes_value=True),
                ]
            }
            issues = check_flag_doc_truth(commands_dir, specs, waivers={})

            self.assertEqual(len(issues), 1, f"expected only the bracketed required flag: {issues}")
            self.assertIn("--session-id", issues[0]["issue"])
            self.assertIn("docs/user/manpages/authorize.md", issues[0]["path"])

    def test_optional_flag_bracketed_is_not_an_issue(self) -> None:
        """Brackets on a genuinely optional flag are correct, not drift."""
        import tempfile  # noqa: PLC0415

        from gzkit.doc_coverage.flag_scanner import FlagSpec, check_flag_doc_truth  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            commands_dir = self._write_doc(
                tmp,
                "# gz authorize\n\n## Usage\n\n```\ngz authorize [--json]\n```\n",
            )
            specs = {"authorize": [FlagSpec(flag="--json", required=False, takes_value=False)]}
            self.assertEqual(check_flag_doc_truth(commands_dir, specs, waivers={}), [])

    def test_valueless_flag_documented_with_an_argument_is_an_issue(self) -> None:
        """`action='store_true'` takes no value; `--json FILE` in Usage is a false claim."""
        import tempfile  # noqa: PLC0415

        from gzkit.doc_coverage.flag_scanner import FlagSpec, check_flag_doc_truth  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            commands_dir = self._write_doc(
                tmp,
                "# gz authorize\n\n## Usage\n\n```\ngz authorize [--json FILE]\n```\n",
            )
            specs = {"authorize": [FlagSpec(flag="--json", required=False, takes_value=False)]}
            issues = check_flag_doc_truth(commands_dir, specs, waivers={})

            self.assertEqual(len(issues), 1, f"expected the value-taking claim to fail: {issues}")
            self.assertIn("--json", issues[0]["issue"])

    def test_claims_outside_the_usage_block_are_not_read_as_usage(self) -> None:
        """Prose mentioning `[--session-id ID]` is not a usage-line claim.

        The check reads the Usage fenced block, never free prose — a doc that
        *discusses* bracket syntax (or quotes another command's usage in an
        example) must not be read as declaring this command's contract. Without
        this bound the check is a prose grader, which is the false-positive
        failure that routed GHI #690 away from a fail-closed home.
        """
        import tempfile  # noqa: PLC0415

        from gzkit.doc_coverage.flag_scanner import FlagSpec, check_flag_doc_truth  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            commands_dir = self._write_doc(
                tmp,
                "# gz authorize\n\n## Usage\n\n```\ngz authorize --session-id ID\n```\n\n"
                "## Notes\n\nEarlier releases documented this as `[--session-id ID]`.\n",
            )
            specs = {"authorize": [FlagSpec(flag="--session-id", required=True, takes_value=True)]}
            self.assertEqual(check_flag_doc_truth(commands_dir, specs, waivers={}), [])

    def test_flag_that_prefixes_a_sibling_flag_is_not_a_false_positive(self) -> None:
        """`[--attestor-present]` must not read as a bracket on `--attestor` (GHI #693).

        Caught by the first-run census: both real-project findings were this
        collision. `gz adr emit-receipt` documents `--attestor <text>` correctly
        unbracketed, then brackets the genuinely-optional sibling
        `[--attestor-present]`; a substring test for `[--attestor` matches the
        sibling and reports a contradiction that does not exist.

        A checker of contradictions asserting a false contradiction is the same
        defect class it exists to catch, and false positives are what routed
        GHI #690 away from a fail-closed home.
        """
        import tempfile  # noqa: PLC0415

        from gzkit.doc_coverage.flag_scanner import FlagSpec, check_flag_doc_truth  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            commands_dir = self._write_doc(
                tmp,
                "# gz authorize\n\n## Usage\n\n```bash\n"
                "gz authorize --attestor <text> [--attestor-present] [--dry-run]\n"
                "```\n",
            )
            specs = {
                "authorize": [
                    FlagSpec(flag="--attestor", required=True, takes_value=True),
                    FlagSpec(flag="--attestor-present", required=False, takes_value=False),
                    FlagSpec(flag="--dry-run", required=False, takes_value=False),
                ]
            }
            self.assertEqual(check_flag_doc_truth(commands_dir, specs, waivers={}), [])

    def test_missing_doc_is_not_a_truth_issue(self) -> None:
        """An absent doc is the presence check's defect, not this check's.

        Reporting it here would double-count the same drift under two issue
        classes and make the presence waiver un-drainable.
        """
        import tempfile  # noqa: PLC0415

        from gzkit.doc_coverage.flag_scanner import FlagSpec, check_flag_doc_truth  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            specs = {"authorize": [FlagSpec(flag="--handoff", required=True, takes_value=True)]}
            self.assertEqual(check_flag_doc_truth(Path(tmp), specs, waivers={}), [])

    def test_live_manpages_carry_no_usage_line_contradiction(self) -> None:
        """The real docs must agree with the real parser — zero drift, zero waivers (GHI #693).

        This check landed with an EMPTY ``_FLAG_TRUTH_WAIVERS``: the first-run
        census over 85 commands / 330 flags found no true contradiction, because
        the one known instance (`--session-id`) was corrected in 35c225f9. There
        is therefore no historical drift to grandfather, and the waiver exists
        only as the drain path if a future census surfaces a batch.

        A new contradiction — a flag made ``required=True`` without unbracketing
        its usage line — fails here and in ``gz cli audit``.
        """
        from gzkit.commands.common import get_project_root  # noqa: PLC0415
        from gzkit.doc_coverage.flag_scanner import (  # noqa: PLC0415
            _FLAG_TRUTH_WAIVERS,
            check_flag_doc_truth,
            scan_command_flag_specs,
        )

        project_root = get_project_root()
        specs = scan_command_flag_specs(project_root)
        commands_dir = project_root / "docs" / "user" / "manpages"

        issues = check_flag_doc_truth(commands_dir, specs)
        self.assertEqual(issues, [], f"Usage lines contradict the parser: {issues}")

        # The waiver must never outlive the drift it snapshots: an entry whose
        # doc is now correct is over-waiver, and silently blinds the check.
        unwaived = check_flag_doc_truth(commands_dir, specs, waivers={})
        real_drift: dict[str, set[str]] = {}
        for issue in unwaived:
            slug = issue["path"].rsplit("/", 1)[-1].removesuffix(".md")
            real_drift.setdefault(slug, set()).add(issue["issue"].split("`")[1])
        for command_name, waived_flags in _FLAG_TRUTH_WAIVERS.items():
            stale = waived_flags - real_drift.get(command_name.replace(" ", "-"), set())
            self.assertFalse(
                stale,
                f"Stale truth waivers for {command_name}: {sorted(stale)} — the usage "
                f"line is now correct; drop them from _FLAG_TRUTH_WAIVERS.",
            )
