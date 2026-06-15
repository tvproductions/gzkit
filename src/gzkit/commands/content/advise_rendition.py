"""gz content advise-rendition command handler — ADR-0.0.37, OBPI-0.0.37-24.

The advisor-QC record surface: an agent wielding the ``gz-advisor-qc`` skill
judges the information-retained-per-byte of a candidate rendition and records its
verdict here. This handler is **deterministic** — it performs NO in-code LLM or
network call. It validates the verdict shape (explanation-before-verdict), writes
the verdict ARB receipt via :mod:`gzkit.content.advisor_qc`, and emits a
``rendition_advisor_verdict`` ledger event.

It is **advisory, never gating** (ADR-0.0.39 Evidentiary invariant): ANY score is
recorded and the command exits 0. The ONLY non-zero exit is a structurally
malformed verdict — an empty/absent explanation — which writes no receipt and no
ledger event (fail-closed-before-write). The verdict value never gates.

Exit 0: verdict recorded + ledger event emitted (regardless of score).
Exit 1: malformed verdict (empty explanation) — no receipt written.
Exit 2: system/IO error writing the receipt.
"""

from __future__ import annotations

import sys

from gzkit.commands.common import get_project_root
from gzkit.content import advisor_qc
from gzkit.ledger import Ledger
from gzkit.ledger_events import rendition_advisor_verdict_event


def content_advise_rendition_cmd(
    *,
    surface: str,
    consumer: str | None,
    explanation: str,
    score: float,
) -> None:
    """Handle ``gz content advise-rendition <surface> [--consumer <vendor>] ...``.

    Exit 0 on a successful record (advisory, any score); 1 on a malformed
    verdict (empty explanation); 2 on IO error.
    """
    root = get_project_root()

    try:
        receipt_path = advisor_qc.record_verdict(
            root=root,
            surface=surface,
            consumer=consumer,
            explanation=explanation,
            score=score,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Error writing advisor-QC receipt: {exc}", file=sys.stderr)
        sys.exit(2)

    Ledger(root / ".gzkit" / "ledger.jsonl").append(
        rendition_advisor_verdict_event(
            surface=surface,
            consumer=consumer,
            receipt_id=receipt_path.stem,
            score=score,
        )
    )

    consumer_label = consumer if consumer is not None else "(surface-wide)"
    print(
        f"Advisor-QC verdict recorded: {surface} [{consumer_label}] "
        f"score={score} (information-retained-per-byte)\n"
        f"Receipt: {receipt_path.as_posix()} (advisory — cite at Gate 5; never gating)"
    )


__all__ = ["content_advise_rendition_cmd"]
