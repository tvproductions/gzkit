"""Manpage coverage contract for ``gz justify`` (OBPI-0.0.19-05).

Pins the structural sections required by the brief's REQ-0.0.19-05-01:
NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXIT STATUS, EXAMPLES, SEE ALSO.
Also asserts at least three EXAMPLES blocks (GHI invocation, OBPI with
``--save``, ``validate`` invocation), explicit exit-code 0/1/2 documentation,
and that every flag from the live ``gz justify --help`` surface is named in
the OPTIONS section so the manpage cannot drift behind the CLI silently.
"""

import contextlib
import io
import re
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from gzkit.cli import main
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_MANPAGE_PATH = _PROJECT_ROOT / "docs" / "user" / "manpages" / "gz-justify.md"

_REQUIRED_SECTIONS = (
    "NAME",
    "SYNOPSIS",
    "DESCRIPTION",
    "OPTIONS",
    "EXIT STATUS",
    "EXAMPLES",
    "SEE ALSO",
)

_EXIT_CODES = ("0", "1", "2")

_LINE_LIMIT = 80


def _capture_help(args: list[str]) -> str:
    out = io.StringIO()
    with redirect_stdout(out), redirect_stderr(out), contextlib.suppress(SystemExit):
        main(args)
    return out.getvalue()


def _flag_names_from_help(help_text: str) -> set[str]:
    return {match.group(0) for match in re.finditer(r"--[A-Za-z][A-Za-z0-9-]*", help_text)}


class GzJustifyManpageContract(unittest.TestCase):
    """Manpage at docs/user/manpages/gz-justify.md must satisfy REQ-0.0.19-05-01."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._content = _MANPAGE_PATH.read_text(encoding="utf-8") if _MANPAGE_PATH.exists() else ""

    @covers("REQ-0.0.19-05-01")
    def test_manpage_file_exists(self) -> None:
        self.assertTrue(
            _MANPAGE_PATH.is_file(),
            f"missing manpage: {_MANPAGE_PATH.relative_to(_PROJECT_ROOT)}",
        )

    @covers("REQ-0.0.19-05-01")
    def test_heading_uses_manpage_convention(self) -> None:
        self.assertTrue(self._content, "manpage is empty")
        first_line = self._content.lstrip().splitlines()[0]
        self.assertEqual(
            first_line.strip(),
            "# gz-justify",
            f"manpage heading must be '# gz-justify' (got: {first_line!r})",
        )

    @covers("REQ-0.0.19-05-01")
    def test_required_sections_present(self) -> None:
        missing = [
            section
            for section in _REQUIRED_SECTIONS
            if not re.search(rf"^##\s+{re.escape(section)}\s*$", self._content, re.MULTILINE)
        ]
        self.assertEqual([], missing, f"manpage missing required sections: {missing}")

    @covers("REQ-0.0.19-05-01")
    def test_examples_section_has_at_least_three_examples(self) -> None:
        examples_block = self._extract_section("EXAMPLES")
        fenced = re.findall(r"```(?:bash|text)?\n(.*?)```", examples_block, re.DOTALL)
        invocations: list[str] = []
        for block in fenced:
            for line in block.splitlines():
                stripped = line.strip()
                if stripped.startswith(("gz justify", "uv run gz justify")):
                    invocations.append(stripped)
        self.assertGreaterEqual(
            len(invocations),
            3,
            f"EXAMPLES must contain >=3 distinct gz justify invocations (got {invocations!r})",
        )
        joined = "\n".join(invocations)
        self.assertIn("GHI", joined, "missing GHI anchor example")
        self.assertIn("--save", joined, "missing --save example")
        self.assertIn("validate", joined, "missing validate subverb example")

    @covers("REQ-0.0.19-05-01")
    def test_exit_status_documents_all_codes(self) -> None:
        block = self._extract_section("EXIT STATUS")
        for code in _EXIT_CODES:
            self.assertRegex(
                block,
                rf"(?m)^[\s\-\|*]*[`*]?{code}[`*]?\s*[—\-:|]",
                f"EXIT STATUS must document code {code} in a row or bullet",
            )

    @covers("REQ-0.0.19-05-01")
    def test_options_section_names_every_cli_flag(self) -> None:
        options_block = self._extract_section("OPTIONS")
        help_text = _capture_help(["justify", "--help"])
        cli_flags = _flag_names_from_help(help_text) - {"--help"}
        missing = sorted(flag for flag in cli_flags if flag not in options_block)
        self.assertEqual(
            [],
            missing,
            f"OPTIONS section omits flags exposed by 'gz justify --help': {missing}",
        )

    @covers("REQ-0.0.19-05-01")
    def test_lines_under_eighty_chars(self) -> None:
        offenders = [
            (i, line)
            for i, line in enumerate(self._content.splitlines(), start=1)
            if len(line) > _LINE_LIMIT
        ]
        self.assertEqual(
            [],
            offenders,
            f"lines exceed {_LINE_LIMIT} chars (CLI doctrine): {offenders[:3]}",
        )

    @covers("REQ-0.0.19-05-01")
    def test_see_also_links_upstream_skills(self) -> None:
        see_also = self._extract_section("SEE ALSO")
        self.assertIn("gz-adr-evaluate", see_also, "SEE ALSO must reference gz-adr-evaluate")
        self.assertIn("gz-obpi-pipeline", see_also, "SEE ALSO must reference gz-obpi-pipeline")

    def _extract_section(self, name: str) -> str:
        pattern = rf"^##\s+{re.escape(name)}\s*$(.*?)(?=^##\s+|\Z)"
        match = re.search(pattern, self._content, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(match, f"section '{name}' not found in manpage")
        assert match is not None  # for type checker
        return match.group(1)


_COMMAND_DOC_PATH = _PROJECT_ROOT / "docs" / "user" / "commands" / "justify.md"
_OPERATOR_RUNBOOK = _PROJECT_ROOT / "docs" / "user" / "runbook.md"
_GOVERNANCE_RUNBOOK = _PROJECT_ROOT / "docs" / "governance" / "governance_runbook.md"
_DOC_COVERAGE_MANIFEST = _PROJECT_ROOT / "config" / "doc-coverage.json"
_COMMANDS_INDEX = _PROJECT_ROOT / "docs" / "user" / "commands" / "index.md"


class GzJustifyCommandDocContract(unittest.TestCase):
    """Operator command doc at docs/user/commands/justify.md (REQ-0.0.19-05-02)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._doc = _COMMAND_DOC_PATH.read_text(encoding="utf-8")

    @covers("REQ-0.0.19-05-02")
    def test_anchor_types_table_documents_three_anchor_kinds(self) -> None:
        for kind in ("GHI", "OBPI", "Draft"):
            self.assertRegex(
                self._doc,
                rf"\|[^|\n]*{kind}[^|\n]*\|",
                f"command doc must document anchor kind {kind} in a table row",
            )

    @covers("REQ-0.0.19-05-02")
    def test_options_table_includes_save_and_draft_slug(self) -> None:
        for flag in ("--save", "--output", "--draft", "--draft-slug", "--related"):
            self.assertIn(
                f"`{flag}",
                self._doc,
                f"command doc must document {flag} in the options table",
            )

    @covers("REQ-0.0.19-05-02")
    def test_exit_code_table_lists_zero_one_two(self) -> None:
        self.assertRegex(self._doc, r"(?m)^\|\s*0\s*\|", "exit code 0 row missing")
        self.assertRegex(self._doc, r"(?m)^\|\s*1\s*\|", "exit code 1 row missing")
        self.assertRegex(self._doc, r"(?m)^\|\s*2\s*\|", "exit code 2 row missing")

    @covers("REQ-0.0.19-05-02")
    def test_troubleshooting_note_for_draft_slug_required(self) -> None:
        self.assertIn(
            "--draft-slug",
            self._doc,
            "command doc must include troubleshooting note for missing --draft-slug",
        )
        self.assertRegex(
            self._doc,
            r"(?i)troubleshooting",
            "command doc must include a Troubleshooting section",
        )


class GzJustifyOperatorRunbookContract(unittest.TestCase):
    """Operator runbook integration (REQ-0.0.19-05-03)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._runbook = _OPERATOR_RUNBOOK.read_text(encoding="utf-8")

    @covers("REQ-0.0.19-05-03")
    def test_runbook_has_justify_section_inside_loop_a(self) -> None:
        loop_a_idx = self._runbook.find("## Loop A:")
        verification_idx = self._runbook.find("## Verification Checklist")
        self.assertGreater(loop_a_idx, -1, "Loop A section must exist")
        self.assertGreater(verification_idx, -1, "Verification Checklist section must exist")
        loop_a_block = self._runbook[loop_a_idx:verification_idx]
        self.assertIn(
            "gz justify",
            loop_a_block,
            "Loop A must reference gz justify (not as standalone appendix)",
        )

    @covers("REQ-0.0.19-05-03")
    def test_runbook_documents_all_three_anchor_types(self) -> None:
        loop_a_idx = self._runbook.find("## Loop A:")
        verification_idx = self._runbook.find("## Verification Checklist")
        loop_a_block = self._runbook[loop_a_idx:verification_idx]
        for kind in ("GHI", "OBPI", "draft"):
            self.assertIn(
                kind,
                loop_a_block,
                f"justify section must mention anchor type {kind}",
            )

    @covers("REQ-0.0.19-05-03")
    def test_runbook_documents_validate_subverb(self) -> None:
        loop_a_idx = self._runbook.find("## Loop A:")
        verification_idx = self._runbook.find("## Verification Checklist")
        loop_a_block = self._runbook[loop_a_idx:verification_idx]
        self.assertIn(
            "justify validate",
            loop_a_block,
            "justify section must document the validate subverb flow",
        )


class GzJustifyGovernanceRunbookContract(unittest.TestCase):
    """Governance runbook 5b extension (REQ-0.0.19-05-04)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._runbook = _GOVERNANCE_RUNBOOK.read_text(encoding="utf-8")

    @covers("REQ-0.0.19-05-04")
    def test_governance_runbook_cites_invariant_11(self) -> None:
        self.assertRegex(
            self._runbook,
            r"invariant\s*11",
            "governance runbook must cite Prime Directive invariant 11",
        )

    @covers("REQ-0.0.19-05-04")
    def test_governance_runbook_names_both_upstream_skills(self) -> None:
        self.assertIn(
            "gz-adr-evaluate",
            self._runbook,
            "governance runbook must name gz-adr-evaluate as upstream skill",
        )
        self.assertIn(
            "gz-obpi-pipeline",
            self._runbook,
            "governance runbook must name gz-obpi-pipeline as upstream skill",
        )

    @covers("REQ-0.0.19-05-04")
    def test_governance_runbook_5b_subsection_under_create_promote(self) -> None:
        create_idx = self._runbook.find("## Workflow: Create or Promote ADR")
        next_workflow_idx = self._runbook.find("## Workflow:", create_idx + 1)
        self.assertGreater(create_idx, -1, "Create or Promote ADR workflow must exist")
        self.assertGreater(next_workflow_idx, create_idx, "next workflow must follow")
        block = self._runbook[create_idx:next_workflow_idx]
        self.assertRegex(
            block,
            r"5b\.\s*Pre-execution reasoning",
            "5b subsection must appear under Create or Promote ADR workflow",
        )


class GzJustifyDocsBuildContract(unittest.TestCase):
    """Mkdocs nav and doc-coverage manifest contracts (REQ-0.0.19-05-07/08)."""

    @covers("REQ-0.0.19-05-07")
    def test_manpage_path_is_valid_markdown_for_mkdocs(self) -> None:
        content = _MANPAGE_PATH.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("# "), "manpage must begin with H1 for mkdocs")
        self.assertNotIn("](broken", content, "manpage must not contain broken-link sentinels")

    @covers("REQ-0.0.19-05-08")
    def test_doc_coverage_manifest_marks_justify_as_governance_relevant(self) -> None:
        import json

        manifest = json.loads(_DOC_COVERAGE_MANIFEST.read_text(encoding="utf-8"))
        justify_entry = manifest["commands"]["justify"]
        self.assertTrue(
            justify_entry["governance_relevant"],
            "doc-coverage manifest must mark justify as governance_relevant",
        )
        for surface in (
            "manpage",
            "index_entry",
            "operator_runbook",
            "governance_runbook",
            "docstring",
        ):
            self.assertTrue(
                justify_entry["surfaces"][surface],
                f"doc-coverage manifest must require justify surface: {surface}",
            )

    @covers("REQ-0.0.19-05-08")
    def test_commands_index_lists_justify(self) -> None:
        index_content = _COMMANDS_INDEX.read_text(encoding="utf-8")
        self.assertIn(
            "justify.md",
            index_content,
            "commands/index.md must link to justify.md",
        )


class GzJustifyAdrAuditCheckContract(unittest.TestCase):
    """The ADR-level audit-check verb is reachable for closeout (REQ-0.0.19-05-10)."""

    @covers("REQ-0.0.19-05-10")
    def test_adr_audit_check_verb_is_registered(self) -> None:
        help_text = _capture_help(["adr", "audit-check", "--help"])
        self.assertIn(
            "audit-check",
            help_text,
            "gz adr audit-check verb must be registered for ADR closeout",
        )


class GzJustifyClosingCeremonyContract(unittest.TestCase):
    """The closeout/attest verbs are reachable for ceremony evidence (REQ-0.0.19-05-09/11/12)."""

    @covers("REQ-0.0.19-05-09")
    def test_arb_canonical_invocations_are_registered(self) -> None:
        for subcmd in ("ruff", "typecheck", "step", "coverage"):
            help_text = _capture_help(["arb", subcmd, "--help"])
            self.assertIn(
                subcmd,
                help_text,
                f"gz arb {subcmd} must be a registered ARB invocation",
            )

    @covers("REQ-0.0.19-05-11")
    def test_closeout_and_attest_verbs_are_registered(self) -> None:
        closeout_help = _capture_help(["closeout", "--help"])
        attest_help = _capture_help(["attest", "--help"])
        self.assertIn(
            "closeout",
            closeout_help,
            "gz closeout must be registered for ADR closeout ceremony",
        )
        self.assertIn(
            "attest",
            attest_help,
            "gz attest must be registered for ADR attestation",
        )

    @covers("REQ-0.0.19-05-12")
    def test_attest_command_accepts_status_completed(self) -> None:
        attest_help = _capture_help(["attest", "--help"])
        self.assertIn(
            "--status",
            attest_help,
            "gz attest must expose --status for the Attestation Block update",
        )


if __name__ == "__main__":
    unittest.main()
