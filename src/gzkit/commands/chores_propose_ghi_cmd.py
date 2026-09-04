"""Implementation of ``gz chores propose-ghi`` — OBPI-0.0.26-04.

Reads proposal-*.json files from a chore's proofs/ directory and files
GitHub issues for unfiled proposals (TTY mode) or marks them advisory-only
(headless mode).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rich.markup import escape

from gzkit.chores.eval_feedback_cluster_lib import ProposalRecord
from gzkit.commands.common import console, get_project_root


def _project_chores_root_path(project_root: Path) -> Path:
    """Return ``<project_root>/.gzkit/chores``."""
    from gzkit.config import load_config

    cfg = load_config()
    return project_root / cfg.paths.chores


def _build_ghi_body(record: ProposalRecord) -> str:
    """Build the GHI issue body for a proposal record."""
    artifact_lines = "\n".join(f"- {aid}" for aid in record.source_artifact_ids)
    return (
        f"## Evaluation Feedback Cluster\n\n"
        f"**Cluster key:** {record.cluster_key}\n"
        f"**Recurrence count:** {record.recurrence_count}\n"
        f"**Summary:** {record.summary}\n"
        f"**Proposed rule target:** {record.proposed_rule_target}\n\n"
        f"**Source artifact IDs:**\n"
        f"{artifact_lines}\n\n"
        f"---\n"
        f"*Filed by `gz chores propose-ghi` from eval-feedback-cluster chore.*"
    )


def chores_propose_ghi(slug: str) -> None:
    """File GHI proposals for unfiled cluster proposal records.

    In TTY mode: prompts PROPOSE/skip per record, files via gh issue create,
    marks record filed. In headless mode: advisory output only, marks advisory.
    """
    project_root = get_project_root()
    proofs_dir = _project_chores_root_path(project_root) / slug / "proofs"

    if not proofs_dir.exists():
        console.print(f"No proofs directory for {slug}")
        return

    proposal_files = sorted(proofs_dir.glob("proposal-*.json"))
    records: list[tuple[Path, ProposalRecord]] = []
    for pf in proposal_files:
        try:
            data = pf.read_text(encoding="utf-8")
            record = ProposalRecord.model_validate_json(data)
            records.append((pf, record))
        except Exception:  # noqa: BLE001
            console.print(f"[yellow]Skipping unreadable proposal: {pf.name}[/yellow]")

    unfiled = [(p, r) for p, r in records if not r.filed]
    if not unfiled:
        console.print(f"No unfiled proposals for {slug}.")
        return

    is_tty = sys.stdin.isatty() and sys.stdout.isatty()

    for path, record in unfiled:
        if is_tty:
            _process_tty(path, record)
        else:
            _process_headless(path, record)


def _process_tty(path: Path, record: ProposalRecord) -> None:
    """Prompt operator in TTY mode; file GHI on PROPOSE confirmation."""
    console.print(f"\n[bold]Proposal:[/bold] {record.cluster_key}")
    console.print(f"  Recurrence: {record.recurrence_count}")
    console.print(f"  Summary: {escape(record.summary)}")
    console.print(f"  Rule target: {record.proposed_rule_target}")

    response = input("File GHI? [PROPOSE/skip]: ").strip().upper()
    if response == "PROPOSE":
        title = f"eval-feedback: {record.summary} (recurrence >= {record.recurrence_count})"
        body = _build_ghi_body(record)
        result = subprocess.run(
            [
                "gh",
                "issue",
                "create",
                "--title",
                title,
                "--body",
                body,
                "--label",
                "enhancement",
                "--label",
                "eval-feedback",
            ],
            capture_output=True,
            text=True,
            errors="replace",
            encoding="utf-8",
            check=True,
        )
        url = result.stdout.strip()
        updated_data = ProposalRecord(**record.model_dump() | {"filed": True, "ghi_url": url})
        path.write_text(updated_data.model_dump_json(indent=2), encoding="utf-8")
        console.print(f"Filed: {url}")
    else:
        console.print("Skipped.")


def _process_headless(path: Path, record: ProposalRecord) -> None:
    """Mark record advisory in headless mode; no GHI filed."""
    console.print(f"\n[bold]Advisory proposal:[/bold] {record.cluster_key}")
    console.print(f"  Recurrence: {record.recurrence_count}")
    console.print(f"  Summary: {escape(record.summary)}")
    console.print(f"  Rule target: {record.proposed_rule_target}")

    updated_data = ProposalRecord(**record.model_dump() | {"advisory": True})
    path.write_text(updated_data.model_dump_json(indent=2), encoding="utf-8")
    console.print(f"Advisory: would file GHI for {record.cluster_key}")
