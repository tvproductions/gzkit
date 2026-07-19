"""Composition drift validator: diffs committed-rendition playback against committed AGENTS.md.

Re-pointed from registry-re-render byte-compare to rendition-playback-vs-committed-surface
diff (ADR-0.0.37, OBPI-0.0.37-22). Fail-closed on drift (exit 3). Read-only on a clean
run (no ledger event); emits composition_drift_detected only on drift — clean-run purity
that lets it serve as a gz check / pre-push gate. (The former per-run composition_rendered
emission was removed: no consumer, and it broke the pre-push gate; the event type stays
defined for historical-ledger compatibility.)

Bootstrap-safe: returns [] when no committed rendition exists (fresh-init or pre-OBPI-22).
"""

from __future__ import annotations

import difflib
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.compose import render_agents_md
from gzkit.governance.events import emit_composition_drift_detected

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


def validate_invariant_coherence(root: Path) -> list[ValidationError]:
    """Diff deterministic playback of the committed rendition against committed AGENTS.md.

    Returns empty list on match (exit 0); one ValidationError on drift (exit 3).

    Read-only on a clean run: emits NO ledger event when the surface matches its
    rendition. On drift it emits a single ``composition_drift_detected`` audit
    event (the same shape as the sibling ``rendition_freshness`` /
    ``rendition_floor_coherence`` gates). This clean-run purity is what lets the
    validator serve as a ``gz check`` / pre-push gate without dirtying the tree
    mid-hook — a validator that wrote the ledger on every run made the pre-commit
    pre-push gate reject the push ("files modified by this hook").

    Historical note: this previously emitted a ``composition_rendered`` event on
    *every* invocation (REQ-0.0.37-03-03 as first authored). That telemetry had no
    consumer and forced two workarounds (the task-envelope attribution exclusion
    and a gate-side ``emit=False`` flag); the emission was removed (ADR-0.0.37 is
    Draft, OBPI-0.0.37-03 repudiated). The ``composition_rendered`` event type
    remains defined for historical-ledger compatibility but is no longer emitted.

    Bootstrap-safe: returns [] when no committed rendition exists (fresh-init;
    rendition-playback path requires a committed artifact).
    """
    rendered_bytes = render_agents_md(root)
    if not rendered_bytes:
        return []

    committed_bytes = _read_committed(root)
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
                "AGENTS.md drifted from committed rendition playback. "
                "Run `gz content compose AGENTS.md` and attest to recompose,\n"
                "or `gz agent sync control-surfaces` to play back the current rendition.\n\n"
                f"Diff (first 50 lines):\n{diff_text}"
            ),
        )
    ]
