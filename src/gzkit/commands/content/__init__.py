"""gz content subparser registrations.

Registers the `gz content` subcommand group with the `import` verb.

ADR-0.0.34 § Decision item #3 — reverse-parse migration tooling.
"""

from __future__ import annotations

import argparse
from typing import Any

from gzkit.cli.helpers import build_epilog


def _content(name: str) -> Any:
    """Resolve a content command handler lazily."""
    from importlib import import_module  # noqa: PLC0415

    module = import_module("gzkit.commands.content.import_")
    return getattr(module, name)


def register_content_parsers(commands: argparse._SubParsersAction) -> None:
    """Register the ``gz content`` sub-command group."""
    p_content = commands.add_parser(
        "content",
        help="Content model import and management commands",
        description=(
            "Commands for importing hand-authored markdown files into canonical "
            "Pydantic content models. Part of the ADR-0.0.34 rendering substrate."
        ),
        epilog=build_epilog(
            [
                "gz content import AGENTS.md --as AgentContract",
                "gz content import .gzkit/rules/tests.md --as Rule --write /tmp/out.md",
            ]
        ),
    )
    content_commands = p_content.add_subparsers(dest="content_command")
    content_commands.required = True

    _register_import(content_commands)


def _register_import(content_commands: argparse._SubParsersAction) -> None:
    p = content_commands.add_parser(
        "import",
        help="Import a markdown file into a canonical content model",
        description=(
            "Read a hand-authored or canonical markdown file, parse it into a Pydantic "
            "content model instance, and emit JSON to stdout. "
            "Use --write to persist a re-rendered canonical form."
        ),
        epilog=build_epilog(
            [
                "gz content import AGENTS.md --as AgentContract",
                "gz content import .gzkit/rules/tests.md --as Rule",
                "gz content import AGENTS.md --as AgentContract --write /tmp/agents-canonical.md",
            ]
        ),
    )
    p.add_argument("file", help="Path to the markdown file to import.")
    p.add_argument(
        "--as",
        dest="as_type",
        required=True,
        help="Content type name (e.g. AgentContract, Rule, Skill).",
    )
    p.add_argument(
        "--write",
        dest="write_path",
        default=None,
        help="Write re-rendered canonical form to this path.",
    )
    p.set_defaults(
        func=lambda a: _content("content_import_cmd")(
            file=a.file,
            as_type=a.as_type,
            write_path=a.write_path,
        )
    )
