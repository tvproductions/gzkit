"""`gz task start --req` must emit the canonical full OBPI slug (GHI #653).

`_sig_d_obpi_id_divergence` fail-closes when one `task_id` carries two
`obpi_id` spellings, and its own remediation names this producer:
"fix the producer (canonicalize the obpi_id at emission in
src/gzkit/commands/task.py)". The waiver set is shrink-only, so the producer
is the only legitimate place to fix it.

The regression these tests pin: `_resolve_obpi_id` bailed to the short form
whenever MORE THAN ONE artifact-graph key shared the short prefix — even when
only one of those candidates was real. A phantom Layer-2 graph key (an
`obpi_created` with no brief ever on disk) was enough to defeat
canonicalization and write a divergent short id.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.commands.task import _resolve_obpi_id
from gzkit.ledger import Ledger
from gzkit.traceability import covers

_SHORT = "OBPI-0.34.0-03"
_REAL = "OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement"
_PHANTOM = "OBPI-0.34.0-03-insight-harvester"


def _ledger_with(root: Path, obpi_ids: list[str]) -> Ledger:
    """Write a ledger whose artifact graph carries ``obpi_ids``."""
    gz = root / ".gzkit"
    gz.mkdir(parents=True, exist_ok=True)
    path = gz / "ledger.jsonl"
    path.write_text(
        "".join(
            json.dumps(
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "obpi_created",
                    "id": obpi_id,
                    "ts": "2026-07-29T00:00:00+00:00",
                    "agent": "test",
                }
            )
            + "\n"
            for obpi_id in obpi_ids
        ),
        encoding="utf-8",
    )
    return Ledger(path)


def _write_brief(root: Path, obpi_id: str) -> None:
    """Place a real OBPI brief on disk — Layer-1 canon for ``obpi_id``."""
    briefs = root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.34.0-x" / "obpis"
    briefs.mkdir(parents=True, exist_ok=True)
    (briefs / f"{obpi_id}.md").write_text(
        f"---\nid: {obpi_id}\n---\n# {obpi_id}\n", encoding="utf-8"
    )


class TestResolveObpiIdCanonicalization(unittest.TestCase):
    """The producer canonicalizes to the full slug, or refuses to guess."""

    @covers("REQ-0.34.0-03-01")
    def test_single_graph_match_resolves_to_full_slug(self) -> None:
        """The unambiguous case still resolves — the pre-existing contract."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = _ledger_with(root, [_REAL])

            self.assertEqual(_resolve_obpi_id(ledger, _SHORT, project_root=root), _REAL)

    @covers("REQ-0.34.0-03-01")
    def test_phantom_graph_key_does_not_defeat_canonicalization(self) -> None:
        """A Layer-2 key with no brief on disk must not force the short form.

        The observed regression. Two graph keys shared the `OBPI-0.34.0-03-`
        prefix, but only one had a brief on disk; the resolver counted matches
        without consulting Layer-1 and emitted the short id, producing the
        Signature (d) divergence that blocked the push.

        `docs/governance/state-doctrine.md`: Layer-1 canon is truth and Layer-2
        may carry records Layer-1 cannot show — `audit_obpi_lifecycle_coherence`
        exists precisely because orphaned `obpi_created` records accumulate.
        Disambiguating by on-disk brief is that doctrine applied.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = _ledger_with(root, [_REAL, _PHANTOM])
            _write_brief(root, _REAL)  # only the real one is Layer-1 canon

            self.assertEqual(
                _resolve_obpi_id(ledger, _SHORT, project_root=root),
                _REAL,
                "a phantom graph key must not force the divergent short form",
            )

    @covers("REQ-0.34.0-03-01")
    def test_genuine_ambiguity_still_refuses_to_guess(self) -> None:
        """Two REAL briefs remain ambiguous — the resolver must not pick one.

        The negative control that keeps the fix narrow. Disambiguation is
        licensed only by Layer-1 canon resolving to exactly one candidate;
        when two briefs genuinely exist, guessing would write a confidently
        wrong `obpi_id`, which is worse than the short form the divergence
        gate can still catch.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = _ledger_with(root, [_REAL, _PHANTOM])
            _write_brief(root, _REAL)
            _write_brief(root, _PHANTOM)

            self.assertEqual(_resolve_obpi_id(ledger, _SHORT, project_root=root), _SHORT)

    @covers("REQ-0.34.0-03-01")
    def test_no_graph_match_returns_short_form(self) -> None:
        """An unknown OBPI resolves to the short form rather than raising."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = _ledger_with(root, [])

            self.assertEqual(_resolve_obpi_id(ledger, _SHORT, project_root=root), _SHORT)


if __name__ == "__main__":
    unittest.main()
