"""Composition drift validator: byte-compares rendered registry against committed AGENTS.md.

Wires OBPI-02's renderer into the gz validate scope catalog as --invariant-coherence.
Fail-closed on drift (exit 3). Emits composition_rendered on every run; additionally
emits composition_drift_detected on drift (ADR-0.0.37, OBPI-0.0.37-03).
"""

from __future__ import annotations

import difflib
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.compose import render_agents_md
from gzkit.governance.events import (
    emit_composition_drift_detected,
    emit_composition_rendered,
)
from gzkit.governance.invariants import load_invariants

_AGENTS_MD_PATH = "AGENTS.md"


def _render_registry(root: Path) -> tuple[bytes, int]:
    """Load invariants and render to bytes.

    Returns (rendered_bytes, invariant_count).
    """
    invariants = load_invariants(root)
    template_root = root / ".gzkit" / "templates"
    rendered_bytes = render_agents_md(invariants, template_root)
    return rendered_bytes, len(invariants)


def _read_committed(root: Path) -> bytes:
    """Read the committed AGENTS.md bytes, or empty bytes if absent."""
    agents_path = root / _AGENTS_MD_PATH
    return agents_path.read_bytes() if agents_path.exists() else b""


def _build_diff(rendered: bytes, committed: bytes) -> str:
    """Build unified diff of first 50 lines."""
    rendered_lines = rendered.decode("utf-8", errors="replace").splitlines(keepends=True)
    committed_lines = committed.decode("utf-8", errors="replace").splitlines(keepends=True)
    diff = difflib.unified_diff(
        committed_lines,
        rendered_lines,
        fromfile="AGENTS.md (committed)",
        tofile="AGENTS.md (rendered)",
    )
    return "".join(list(diff)[:50])


def validate_invariant_coherence(root: Path) -> list[ValidationError]:
    """Re-render registry bytes and byte-compare against committed AGENTS.md.

    Returns empty list on match (exit 0); one ValidationError on drift (exit 3).
    Emits ledger events via gzkit.governance.events regardless of outcome.

    Bootstrap-safe: returns [] when the template file is absent (fresh-init
    state); the template is the composition source, not this validator's
    authoring concern. The invariants directory may be empty/absent —
    load_invariants returns {} gracefully and rendering proceeds.
    """
    template_path = root / ".gzkit" / "templates" / "agents.md"
    if not template_path.exists():
        return []

    rendered_bytes, invariant_count = _render_registry(root)
    committed_bytes = _read_committed(root)

    emit_composition_rendered(
        root=root,
        invariant_count=invariant_count,
        target=_AGENTS_MD_PATH,
        byte_count=len(rendered_bytes),
    )

    if rendered_bytes == committed_bytes:
        return []

    diff_text = _build_diff(rendered_bytes, committed_bytes)
    emit_composition_drift_detected(
        root=root,
        target=_AGENTS_MD_PATH,
        diff_first_50_lines=diff_text,
    )

    return [
        ValidationError(
            type="invariant_coherence",
            artifact=_AGENTS_MD_PATH,
            message=(
                "AGENTS.md drifted from rendered registry output. "
                "Run `gz governance render --target agents-md` to regenerate.\n\n"
                f"Diff (first 50 lines):\n{diff_text}"
            ),
        )
    ]
