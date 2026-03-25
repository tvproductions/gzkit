"""CLI consistency and convention enforcement tests.

Validates that the CLI follows naming conventions, has complete help text,
and maintains consistent presentation across all commands.

Run: uv run -m unittest tests.policy.test_cli_consistency -v
"""

from __future__ import annotations

import argparse
import subprocess
import time
import unittest
from pathlib import Path

from gzkit.cli.main import _build_parser

# ---------------------------------------------------------------------------
# Known exceptions / allowlists
# ---------------------------------------------------------------------------

# The ROOT parser ("gz") is exempt from description and epilog requirements
# because it functions as a dispatcher — its role is to list subcommands, not
# describe a single command's purpose.
ROOT_EXEMPT_PATHS: frozenset[str] = frozenset({"ROOT"})

# Actions whose dest values are exempt from help-text requirements.
# "help" is the auto-generated -h/--help action; "version" is --version.
HELP_EXEMPT_DESTS: frozenset[str] = frozenset({"help", "version"})

# Long options that are permitted to use underscores as deprecated aliases.
# Only add here if a hyphenated primary option also exists on the same argument.
# (Currently empty — gzkit enforces kebab-case uniformly.)
UNDERSCORE_ALIAS_ALLOWLIST: frozenset[str] = frozenset()


# ---------------------------------------------------------------------------
# Recursive parser auditor
# ---------------------------------------------------------------------------


class TestCLIConsistency(unittest.TestCase):
    """Enforce CLI consistency rules via recursive parser audit."""

    @classmethod
    def setUpClass(cls) -> None:
        """Build parser once for all tests in this class."""
        cls.parser = _build_parser()
        cls.audit_data = cls._audit_parser(cls.parser, [])

    @classmethod
    def _audit_parser(cls, parser: argparse.ArgumentParser, path: list[str]) -> list[dict]:
        """Recursively audit parser structure.

        Walks the argparse tree and returns a flat list of records — one per
        parser node — containing the command path, prog, description, epilog,
        and all arguments registered at that level.
        """
        records: list[dict] = []
        cmd_path = " ".join(path) if path else "ROOT"

        # Extract arguments at this level, excluding:
        # - help/version actions (auto-generated, not user-authored)
        # - _SubParsersAction instances (subcommand selectors, not arguments)
        args: list[dict] = []
        for action in parser._actions:
            if action.dest in HELP_EXEMPT_DESTS:
                continue
            if isinstance(action, argparse._SubParsersAction):
                continue
            arg_info = {
                "dest": action.dest,
                "option_strings": action.option_strings,
                "help": action.help,
            }
            args.append(arg_info)

        record: dict = {
            "path": cmd_path,
            "prog": parser.prog,
            "description": parser.description,
            "epilog": parser.epilog,
            "arguments": args,
            "subcommands": [],
        }

        # Recurse into subparsers
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                for name, subparser in action.choices.items():
                    subcommands = record["subcommands"]
                    assert isinstance(subcommands, list)
                    subcommands.append(name)
                    if isinstance(subparser, argparse.ArgumentParser):
                        records.extend(cls._audit_parser(subparser, path + [name]))

        records.append(record)
        return records

    # -----------------------------------------------------------------------
    # REQ-0.0.4-10-02: No underscores in long option names
    # -----------------------------------------------------------------------

    def test_no_underscores_in_long_option_names(self) -> None:
        """All -- options must use hyphens, not underscores (GNU/POSIX standard).

        Enforces REQ-0.0.4-10-02. Deprecated aliases (where a hyphenated primary
        also exists on the same argument) are permitted via UNDERSCORE_ALIAS_ALLOWLIST.
        """
        violations: list[str] = []
        for record in self.audit_data:
            for arg in record["arguments"]:
                for opt in arg["option_strings"]:
                    if not (opt.startswith("--") and "_" in opt):
                        continue
                    # Allow if the hyphenated form exists as another option string
                    other_opts = [o for o in arg["option_strings"] if o != opt]
                    hyphenated = opt.replace("_", "-")
                    if hyphenated in other_opts or opt in UNDERSCORE_ALIAS_ALLOWLIST:
                        continue
                    violations.append(f"{record['path']}: {opt}")

        self.assertEqual(
            [],
            violations,
            f"Found {len(violations)} option(s) using underscores without a hyphenated "
            "primary. Use --kebab-case for long options per GNU/POSIX conventions:\n  "
            + "\n  ".join(violations),
        )

    # -----------------------------------------------------------------------
    # REQ-0.0.4-10-03: Every command must have a description
    # -----------------------------------------------------------------------

    def test_all_commands_have_descriptions(self) -> None:
        """Every parser node must have a non-empty .description (ROOT exempt).

        Enforces REQ-0.0.4-10-03. An empty or None description means argparse
        renders no summary for that command, breaking discoverability.
        """
        missing = [
            r["path"]
            for r in self.audit_data
            if r["path"] not in ROOT_EXEMPT_PATHS and not r["description"]
        ]

        if missing:
            self.fail(
                f"{len(missing)} command(s) missing description:\n  "
                + "\n  ".join(missing[:20])
                + (f"\n  ... and {len(missing) - 20} more" if len(missing) > 20 else "")
                + "\nAdd description=... to the add_parser() call for each."
            )

    # -----------------------------------------------------------------------
    # REQ-0.0.4-10-04: Every argument must have help text
    # -----------------------------------------------------------------------

    def test_all_arguments_have_help_text(self) -> None:
        """Every argument/option must have .help set (not None, not SUPPRESS).

        Enforces REQ-0.0.4-10-04. Arguments without help text are invisible in
        the --help output and reduce operator discoverability.
        """
        violations: list[str] = []
        for record in self.audit_data:
            for arg in record["arguments"]:
                help_val = arg.get("help")
                if help_val is None or help_val == argparse.SUPPRESS:
                    label = arg["option_strings"] if arg["option_strings"] else arg["dest"]
                    violations.append(f"{record['path']}: {label}")

        if violations:
            self.fail(
                f"{len(violations)} argument(s) missing help text:\n  "
                + "\n  ".join(violations[:20])
                + (f"\n  ... and {len(violations) - 20} more" if len(violations) > 20 else "")
                + "\nAdd help=... to the add_argument() call for each."
            )

    # -----------------------------------------------------------------------
    # REQ-0.0.4-10-05: Every parser must have an epilog with required sections
    # -----------------------------------------------------------------------

    def test_all_parsers_have_epilog(self) -> None:
        """Every parser must have a non-empty .epilog with 'Examples' and 'Exit codes'.

        Enforces REQ-0.0.4-10-05. Use build_epilog() from gzkit.cli.helpers.epilog
        to produce conformant epilogs. ROOT is exempt because it acts as a dispatcher.
        """
        REQUIRED_SUBSTRINGS = ("Examples", "Exit codes")
        violations: list[str] = []

        for record in self.audit_data:
            if record["path"] in ROOT_EXEMPT_PATHS:
                continue
            epilog = record.get("epilog") or ""
            for substring in REQUIRED_SUBSTRINGS:
                if substring not in epilog:
                    violations.append(f"{record['path']}: epilog missing '{substring}'")

        if violations:
            self.fail(
                f"{len(violations)} parser(s) with non-conformant epilog:\n  "
                + "\n  ".join(violations[:20])
                + (f"\n  ... and {len(violations) - 20} more" if len(violations) > 20 else "")
                + "\nUse build_epilog() from gzkit.cli.helpers.epilog."
            )

    # -----------------------------------------------------------------------
    # REQ: No debugging artifacts in help text
    # -----------------------------------------------------------------------

    def test_no_debugging_artifacts_in_help(self) -> None:
        """Help text and descriptions must not contain debugging artifacts.

        Patterns like TODO, FIXME, XXX, print(, pdb.set_trace indicate
        in-progress work that should not appear in operator-facing CLI output.
        """
        FORBIDDEN_PATTERNS = ["TODO", "FIXME", "XXX", "print(", "pdb.set_trace"]
        violations: list[str] = []

        for record in self.audit_data:
            desc = record.get("description") or ""
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in desc:
                    violations.append(f"{record['path']}: description contains '{pattern}'")

            for arg in record["arguments"]:
                help_text = arg.get("help") or ""
                for pattern in FORBIDDEN_PATTERNS:
                    if pattern in help_text:
                        label = arg["option_strings"] if arg["option_strings"] else arg["dest"]
                        violations.append(f"{record['path']} {label}: help contains '{pattern}'")

        self.assertEqual(
            [],
            violations,
            "Debugging artifacts found in CLI help text:\n  " + "\n  ".join(violations),
        )

    # -----------------------------------------------------------------------
    # REQ: Help renders fast
    # -----------------------------------------------------------------------

    def test_help_renders_fast(self) -> None:
        """Full --help rendering must complete in under 1 second.

        Measures wall-clock time for `gz --help` via subprocess. A slow startup
        indicates an expensive import at module level in a CLI command module.
        """
        start = time.monotonic()
        result = subprocess.run(
            ["uv", "run", "gz", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(Path(__file__).parent.parent.parent),
        )
        elapsed = time.monotonic() - start

        # The command should exit 0 (help is successful)
        self.assertEqual(
            result.returncode,
            0,
            f"gz --help exited with code {result.returncode}.\nstderr: {result.stderr}",
        )

        self.assertLess(
            elapsed,
            1.0,
            f"gz --help took {elapsed:.3f}s (limit: 1.0s). "
            "Check for expensive top-level imports in CLI command modules.",
        )


# ---------------------------------------------------------------------------
# REQ: Self-isolation test
# ---------------------------------------------------------------------------


class TestCLIConsistencyIsolation(unittest.TestCase):
    """This test file imports only _build_parser from gzkit (by design).

    The recursive parser auditor must access the live argparse tree at runtime,
    which is why this module differs from the pure-AST policy tests. This class
    verifies that import creep does not introduce additional gzkit dependencies.
    """

    def test_this_module_uses_parser_import_only(self) -> None:
        """Verify this test file imports only _build_parser from gzkit.

        The parser auditor pattern requires exactly one gzkit import:
        _build_parser from gzkit.cli.main. Any additional gzkit imports
        in this file indicate scope creep and should be removed.
        """
        import ast

        this_file = Path(__file__)
        source = this_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(this_file))

        allowed_gzkit_imports: set[str] = {"gzkit.cli.main"}
        violations: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if (
                        alias.name == "gzkit" or alias.name.startswith("gzkit.")
                    ) and alias.name not in allowed_gzkit_imports:
                        violations.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if (
                    module == "gzkit" or module.startswith("gzkit.")
                ) and module not in allowed_gzkit_imports:
                    violations.append(f"from {module} import ...")

        if violations:
            self.fail(
                "This policy test imports unexpected gzkit modules "
                "(only gzkit.cli.main is permitted):\n  " + "\n  ".join(violations)
            )


if __name__ == "__main__":
    unittest.main()
