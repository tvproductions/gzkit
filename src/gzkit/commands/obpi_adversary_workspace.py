"""Materialize the Step-4b adversary's disposable writable checkout (GHI #961).

The command's whole job is to make the writable review path *reachable without
improvisation*: it copies the reviewed source into a throwaway tree and prints
the exact mandated dispatch for it. An agent that has to hand-assemble the
sandbox argv will eventually assemble it pointing at the live repository, which
is the outcome the disposable checkout exists to prevent.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from rich.markup import escape

from gzkit.adversary_workspace import materialize_adversary_workspace
from gzkit.cli.helpers.exit_codes import EXIT_SUCCESS, EXIT_SYSTEM_ERROR
from gzkit.commands.common import console, get_project_root

_COMPANION = "$HOME/.claude/plugins/cache/openai-codex/codex/<ver>/scripts/codex-companion.mjs"


def _dispatch_command(workspace_path: str) -> str:
    """Render the mandated tier-1 argv for a writable Step-4b round at *workspace_path*."""
    return (
        "uv run gz arb step --name codexadversary --max-output-chars -1 -- \\\n"
        f'  node "{_COMPANION}" \\\n'
        f"  task --write --cwd {workspace_path} --prompt-file <prompt.md>"
    )


def obpi_adversary_workspace_cmd(
    *, obpi_id: str, destination: str | None = None, as_json: bool = False
) -> int:
    """Build the disposable checkout and report how to dispatch a reviewer at it.

    Returns 0 on success, 2 when the reviewed source cannot be reproduced.
    """
    root = get_project_root()
    target = (
        Path(destination)
        if destination
        else Path(tempfile.mkdtemp(prefix=f"gz-adversary-{obpi_id}-"))
    )

    try:
        workspace = materialize_adversary_workspace(root, target)
    except RuntimeError as error:
        console.print(
            f"[red]Cannot materialize the adversary workspace:[/red] {escape(str(error))}"
        )
        return EXIT_SYSTEM_ERROR

    if as_json:
        payload = workspace.model_dump()
        payload["dispatch_command"] = _dispatch_command(workspace.path)
        console.print_json(json.dumps(payload))
        return EXIT_SUCCESS

    console.print(f"Adversary workspace: {workspace.path}")
    console.print(
        f"  reviewed source:   {workspace.head_commit}{' +uncommitted' if workspace.dirty else ''}"
    )
    console.print(f"  files:             {workspace.file_count}")
    console.print(f"  source digest:     {workspace.source_digest}")
    console.print(f"  interpreter:       {workspace.interpreter}")
    console.print(f"  PYTHONPATH:        {workspace.python_path}")
    console.print("")
    console.print("The reviewer runs tests inside the checkout with:")
    console.print(
        f"  PYTHONPATH={workspace.python_path} {workspace.interpreter} -m unittest <selector>"
    )
    console.print("")
    console.print("Dispatch the tier-1 adversary at it with:")
    console.print(_dispatch_command(workspace.path))
    console.print("")
    console.print(
        "Cite this source digest in every replay record; delete the checkout when the round ends."
    )
    return EXIT_SUCCESS
