"""State command implementation."""

import json

from rich.table import Table

from gzkit.commands.common import (
    _attestation_gate_snapshot,
    console,
    ensure_initialized,
    get_project_root,
)
from gzkit.ledger import Ledger


def state(as_json: bool, blocked: bool, ready: bool) -> None:
    """Query ledger state and artifact relationships."""
    config = ensure_initialized()
    project_root = get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    raw_graph = ledger.get_artifact_graph()
    graph = {artifact_id: dict(info) for artifact_id, info in raw_graph.items()}
    for _artifact_id, info in graph.items():
        if info.get("type") == "adr":
            info.update(Ledger.derive_adr_semantics(info))

    # Filter if requested
    if blocked:
        graph = {k: v for k, v in graph.items() if not v.get("attested")}
    if ready:
        ready_ids: set[str] = set()
        for artifact_id, info in graph.items():
            if info.get("type") != "adr" or info.get("attested"):
                continue
            snapshot = _attestation_gate_snapshot(project_root, config, ledger, artifact_id)
            if snapshot["ready"]:
                ready_ids.add(artifact_id)
        graph = {k: v for k, v in graph.items() if k in ready_ids}

    if as_json:
        print(json.dumps(graph, indent=2))
        return

    if not graph:
        console.print("No artifacts found.")
        return

    # Display as tree
    table = Table(title="Artifact State")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Parent")
    table.add_column("Attested", style="yellow")

    for artifact_id, info in sorted(graph.items()):
        attested = "[green]Yes[/green]" if info.get("attested") else "[red]No[/red]"
        table.add_row(
            artifact_id,
            info.get("type", "unknown"),
            info.get("parent") or "-",
            attested,
        )

    console.print(table)
