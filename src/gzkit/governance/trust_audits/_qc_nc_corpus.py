"""Negative-control fixtures for the corpus/ledger witness claims.

Split out of ``_qc_negative_controls`` by cohesion: that module sits within a
dozen SLOC of the canonical block band, so it cannot absorb another control, and
grandfathering it is the laundering ADR-0.0.73 Boundary Invariant #8 forbids.
The corpus-witness cohort is the natural seam — these fixtures build a corpus
store and a ledger together, which no other control does.

Genuineness is structural (Boundary Invariant #7): the fixture NEVER calls the
validator; only the runner does, via ``entrypoint(fixture())``.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.enforcement import create_fixture_tempdir

_TS = "2026-01-01T00:00:00+00:00"


def build_retirement_witness() -> Path:
    """Build a corpus tombstone whose retired id no ledger event names.

    The ledger deliberately carries a ``corpus_entry_retired`` row for a
    DIFFERENT id. A presence check passes this fixture; the subject-bound gate
    must not (GHI #885). That asymmetry is what makes the control genuine and
    un-forced rather than a fixture the validator cannot help but flag.
    """
    root = create_fixture_tempdir(prefix="gzkit-qc-nc-corpus-retirement-")
    base = {
        "surface": "AGENTS.md",
        "section": "attestation",
        "tier": "invariant",
        "classification": "Judgment",
        "origin": "negative-control",
        "ts": _TS,
    }
    rows = [
        {**base, "id": "live-entry", "text": "DOCTRINE"},
        {**base, "id": "tombstone", "text": "retires it", "retires": "live-entry"},
    ]
    corpus = root / ".gzkit" / "corpus" / "AGENTS.md.jsonl"
    corpus.parent.mkdir(parents=True, exist_ok=True)
    corpus.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    (root / ".gzkit" / "ledger.jsonl").write_text(
        json.dumps(
            {
                "schema": "gzkit.ledger.v1",
                "event": "corpus_entry_retired",
                "id": f"corpus-entry-retired-{_TS}",
                "ts": _TS,
                "surface": "AGENTS.md",
                "retired_entry_id": "SOME-OTHER-ENTRY",
                "retraction_entry_id": "other-tombstone",
                "reason": "unrelated",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return root
