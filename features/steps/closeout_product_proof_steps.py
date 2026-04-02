"""BDD steps for closeout product proof gate."""

from __future__ import annotations

import io
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import given

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, obpi_created_event, obpi_receipt_emitted_event


def _invoke(args: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


def _git_init() -> str:
    """Initialize a git repo and return the HEAD commit hash."""
    subprocess.run(["git", "init", "-b", "main"], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.name", "BDD User"], check=True, capture_output=True, text=True
    )
    subprocess.run(
        ["git", "config", "user.email", "bdd@example.com"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed"], check=True, capture_output=True, text=True)
    return subprocess.run(
        ["git", "rev-parse", "--short=7", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@given("a heavy ADR exists with an OBPI brief")
def step_heavy_adr_with_obpi(context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke(["plan", "create", "0.1.0", "--lane", "heavy"])
    assert code == 0, output

    # Create OBPI brief with allowed paths
    config = GzkitConfig.load(Path(".gzkit.json"))
    obpi_dir = Path(config.paths.adrs) / "obpis"
    obpi_dir.mkdir(parents=True, exist_ok=True)
    brief_path = obpi_dir / "OBPI-0.1.0-01-demo-feature.md"
    brief_path.write_text(
        "\n".join(
            [
                "---",
                "id: OBPI-0.1.0-01-demo-feature",
                "parent: ADR-0.1.0",
                "item: 1",
                "lane: Heavy",
                "status: Completed",
                "---",
                "",
                "# OBPI-0.1.0-01 — Demo Feature",
                "",
                "**Brief Status:** Completed",
                "",
                "## OBJECTIVE",
                "",
                "Demonstrate product proof gate.",
                "",
                "## ALLOWED PATHS",
                "",
                "- `src/gzkit/demo.py`",
                "- `docs/user/commands/demo.md`",
                "",
                "## REQUIREMENTS (FAIL-CLOSED)",
                "",
                "1. REQUIREMENT: Demo feature works",
                "",
                "## Evidence",
                "",
                "### Implementation Summary",
                "- Files created/modified: src/gzkit/demo.py",
                "- Validation commands run: uv run gz test",
                "- Date completed: 2026-03-28",
                "",
                "### Key Proof",
                "uv run gz test",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    # Git init for anchor tracking
    head = _git_init()

    # Register OBPI and emit completion receipt in ledger
    ledger = Ledger(Path(".gzkit/ledger.jsonl"))
    ledger.append(obpi_created_event("OBPI-0.1.0-01-demo-feature", "ADR-0.1.0"))
    ledger.append(
        obpi_receipt_emitted_event(
            obpi_id="OBPI-0.1.0-01-demo-feature",
            parent_adr="ADR-0.1.0",
            receipt_event="completed",
            attestor="human:bdd",
            obpi_completion="completed",
            evidence={
                "value_narrative": "Demo feature for product proof testing.",
                "key_proof": "uv run gz test",
                "scope_audit": {
                    "allowlist": ["src/gzkit/demo.py"],
                    "changed_files": ["src/gzkit/demo.py"],
                    "out_of_scope_files": [],
                },
                "git_sync_state": {
                    "dirty": False,
                    "ahead": 0,
                    "behind": 0,
                    "diverged": False,
                    "blockers": [],
                },
            },
            anchor={"commit": head, "semver": "0.1.0"},
        )
    )


@given("the OBPI source file has public docstrings")
def step_obpi_source_with_docstrings(context) -> None:  # type: ignore[no-untyped-def]
    src_dir = Path("src") / "gzkit"
    src_dir.mkdir(parents=True, exist_ok=True)
    demo_file = src_dir / "demo.py"
    demo_file.write_text(
        "\n".join(
            [
                '"""Demo module for product proof gate."""',
                "",
                "",
                "def demo_feature():",
                '    """Demonstrate the product proof gate validation."""',
                "    return True",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    # Commit so anchor check doesn't flag drift
    subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "add demo source"],
        check=True,
        capture_output=True,
        text=True,
    )
