"""BDD fixture steps for gz validate --fidelity-presence scenarios (OBPI-0.0.73-08).

The shared When/Then steps (``When I run``, ``Then it exits with code``,
``And the output contains``) live in features/steps/obpi_lock_steps.py and
features/steps/gz_steps.py; only the ADR-fixture Given steps are defined here.

@covers REQ-0.0.73-08-01
"""

from __future__ import annotations

import os
from pathlib import Path

from behave import given

_FIDELITY_BLOCK = (
    "\n## Fidelity Assertions\n\n"
    "| Claim | Command | Expected exit |\n"
    "|-------|---------|---------------|\n"
    "| The gz CLI is invokable against the real system. | uv run gz --version | 0 |\n"
)


def _write_adr(root: Path, adr_id: str, *, with_block: bool) -> None:
    pkg = root / "docs" / "design" / "adr" / "foundation" / adr_id
    pkg.mkdir(parents=True, exist_ok=True)
    body = (
        f"---\nid: {adr_id}\nkind: foundation\nlane: heavy\n---\n# {adr_id}\n\n## Decision\n\nX.\n"
    )
    if with_block:
        body += _FIDELITY_BLOCK
    (pkg / f"{adr_id}.md").write_text(body, encoding="utf-8")


@given("a project with a block-less non-pool ADR Decision")
def step_block_less_adr(context) -> None:
    """A foundation ADR Decision with no ## Fidelity Assertions block."""
    root: Path = context._tmpdir
    _write_adr(root, "ADR-0.0.1-blockless", with_block=False)
    os.chdir(root)


@given("a project where every non-pool ADR Decision carries a Fidelity Assertions block")
def step_compliant_corpus(context) -> None:
    """Every non-pool ADR Decision ships a parseable block."""
    root: Path = context._tmpdir
    _write_adr(root, "ADR-0.0.1-compliant", with_block=True)
    os.chdir(root)
