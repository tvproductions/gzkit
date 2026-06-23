"""Composition drift validator: diffs committed-rendition playback against committed AGENTS.md.

Re-pointed from registry-re-render byte-compare to rendition-playback-vs-committed-surface
diff (ADR-0.0.37, OBPI-0.0.37-22). Fail-closed on drift (exit 3). Emits
composition_drift_detected on drift; emits composition_rendered on every playback run.

Bootstrap-safe: returns [] when no committed rendition exists (fresh-init or pre-OBPI-22).
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

_AGENTS_MD_PATH = "AGENTS.md"


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


def validate_invariant_coherence(root: Path, *, emit: bool = True) -> list[ValidationError]:
    """Diff deterministic playback of the committed rendition against committed AGENTS.md.

    Returns empty list on match (exit 0); one ValidationError on drift (exit 3).

    ``emit`` (default ``True``) governs ledger side-effects: ``composition_rendered``
    on every run and ``composition_drift_detected`` on drift. Set ``emit=False`` for
    a pure read-only check — required when this runs inside the ``gz check`` /
    pre-push gate, where a validator that mutates the ledger would dirty the tree
    and the pre-commit framework would reject the push ("files modified by this
    hook"). Standalone ``gz validate --invariant-coherence`` keeps ``emit=True``
    (REQ-0.0.37-03-03 telemetry contract unchanged).

    Bootstrap-safe: returns [] when no committed rendition exists (fresh-init;
    rendition-playback path requires a committed artifact).
    """
    rendered_bytes = render_agents_md({}, Path(), root)
    if not rendered_bytes:
        return []

    committed_bytes = _read_committed(root)

    if emit:
        emit_composition_rendered(
            root=root,
            invariant_count=0,
            target=_AGENTS_MD_PATH,
            byte_count=len(rendered_bytes),
        )

    if rendered_bytes == committed_bytes:
        return []

    diff_text = _build_diff(rendered_bytes, committed_bytes)
    if emit:
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
                "AGENTS.md drifted from committed rendition playback. "
                "Run `gz content compose AGENTS.md` and attest to recompose,\n"
                "or `gz agent sync control-surfaces` to play back the current rendition.\n\n"
                f"Diff (first 50 lines):\n{diff_text}"
            ),
        )
    ]
