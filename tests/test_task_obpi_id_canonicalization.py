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
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.commands.task import _resolve_obpi_id
from gzkit.ledger import Ledger

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


def _cutover_tolerated(ledger_path: Path, cutover: datetime) -> set[str]:
    """Return the task_ids whose obpi_id divergence ``cutover`` excuses.

    Mirrors `_sig_d_obpi_id_divergence`'s tolerance branch (same-lineage,
    latest event at or before the cutover, not already grandfathered). Taking
    the ledger path and cutover as PARAMETERS is what makes the ratchet
    falsifiable: the real repo carries no divergence after the current cutover,
    so a test bound to the live ledger passes whether or not the guard works.
    """
    from collections import defaultdict

    from gzkit.commands.validate_task_envelope import (
        _OBPI_ID_DIVERGENCE_GRANDFATHER,
        _TASK_LIFECYCLE_TYPES,
        _obpi_lineage_id,
    )

    spellings: dict[str, set[str]] = defaultdict(set)
    latest: dict[str, datetime] = {}
    for raw in ledger_path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            ev = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(ev, dict) or ev.get("event") not in _TASK_LIFECYCLE_TYPES:
            continue
        task_id, obpi_id = ev.get("task_id"), ev.get("obpi_id")
        if not (isinstance(task_id, str) and task_id and isinstance(obpi_id, str) and obpi_id):
            continue
        spellings[task_id].add(obpi_id)
        stamp = str(ev.get("ts") or ev.get("timestamp") or "").replace("Z", "+00:00")
        try:
            seen = datetime.fromisoformat(stamp)
        except ValueError:
            continue
        if task_id not in latest or seen > latest[task_id]:
            latest[task_id] = seen

    return {
        task_id
        for task_id, forms in spellings.items()
        if task_id not in _OBPI_ID_DIVERGENCE_GRANDFATHER
        and len(forms) > 1
        and len({_obpi_lineage_id(f) for f in forms}) == 1
        and task_id in latest
        and latest[task_id] <= cutover
    }


class TestResolveObpiIdCanonicalization(unittest.TestCase):
    """The producer canonicalizes to the full slug, or refuses to guess."""

    def test_single_graph_match_resolves_to_full_slug(self) -> None:
        """The unambiguous case still resolves — the pre-existing contract."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = _ledger_with(root, [_REAL])

            self.assertEqual(_resolve_obpi_id(ledger, _SHORT, project_root=root), _REAL)

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

    def test_no_graph_match_returns_short_form(self) -> None:
        """An unknown OBPI resolves to the short form rather than raising."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = _ledger_with(root, [])

            self.assertEqual(_resolve_obpi_id(ledger, _SHORT, project_root=root), _SHORT)


class TestCutoverToleranceRatchet(unittest.TestCase):
    """`_OBPI_ID_CANONICAL_CUTOVER` must never be advanced to swallow new rows."""

    # Shrink-only. Every task_id the cutover currently excuses, pinned. Advancing
    # the cutover to hide a NEW divergence grows this set and fails the test;
    # repairing history shrinks it, which is always allowed.
    #
    # This constant is the one escape hatch in Signature (d): the grandfather
    # frozenset is shrink-only and guarded, but the cutover is a bare date that
    # silently excuses everything before it. Twice now it has been advanced for
    # the same GHI (#653). Without a ratchet, "advance the date" is a one-line
    # way to make any divergence disappear.
    _TOLERATED: frozenset[str] = frozenset(
        {
            "TASK-0.34.0-03-01-02",  # 2026-07-29 --req producer repair
            "TASK-0.34.0-03-01-03",  # 2026-07-29 --req producer repair
            "TASK-0.44.0-01-01-01",  # predates the 2026-07-29 advance
            "TASK-0.44.0-01-03-01",  # predates the 2026-07-29 advance
        }
    )

    def test_cutover_excuses_only_the_pinned_task_ids(self) -> None:
        """The set of divergences excused by the cutover may shrink, never grow."""
        from gzkit.commands.validate_task_envelope import _OBPI_ID_CANONICAL_CUTOVER

        ledger = Path(__file__).resolve().parents[1] / ".gzkit" / "ledger.jsonl"
        tolerated = _cutover_tolerated(ledger, _OBPI_ID_CANONICAL_CUTOVER)

        self.assertEqual(
            tolerated - self._TOLERATED,
            set(),
            "the cutover now excuses task_ids that are not pinned — it was "
            "advanced to hide a new divergence. Fix the producer that wrote the "
            "short obpi_id instead (src/gzkit/commands/task.py), per the "
            "shrink-only rule on _OBPI_ID_DIVERGENCE_GRANDFATHER.",
        )

    def test_ratchet_detects_a_cutover_advanced_to_bury_a_divergence(self) -> None:
        """The guard bites — proven against a synthetic ledger, not asserted.

        A ratchet that cannot fail is theater. The real repo has no divergence
        after the current cutover, so simply moving the date changes nothing and
        the primary test above stays green either way. This drives the same
        helper with a ledger that DOES carry a fresh divergence and confirms an
        advanced cutover starts excusing it.
        """
        with TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            rows = [
                {
                    "event": "task_started",
                    "task_id": "TASK-9.9.9-01-01-01",
                    "obpi_id": "OBPI-9.9.9-01",
                    "ts": "2027-01-01T00:00:00+00:00",
                },
                {
                    "event": "task_completed",
                    "task_id": "TASK-9.9.9-01-01-01",
                    "obpi_id": "OBPI-9.9.9-01-slug",
                    "ts": "2027-01-01T01:00:00+00:00",
                },
            ]
            ledger.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

            before = _cutover_tolerated(ledger, datetime(2026, 7, 29, tzinfo=UTC))
            after = _cutover_tolerated(ledger, datetime(2027, 6, 1, tzinfo=UTC))

            self.assertEqual(before, set(), "a post-cutover divergence must NOT be excused")
            self.assertEqual(
                after,
                {"TASK-9.9.9-01-01-01"},
                "advancing the cutover past a divergence must start excusing it, "
                "which is exactly what the pinned set makes visible",
            )


class TestSigCComparisonSurface(unittest.TestCase):
    """Signature (c)'s comparison surface is declared, pinned, and falsifiable."""

    _REPO = Path(__file__).resolve().parents[1]

    # Shrink-only. OBPIs whose channel disagreement is sealed in append-only
    # history: their commits declared one TASK while the ledger recorded 4-6,
    # and a commit cannot gain a trailer retroactively.
    _EXPECTED_GRANDFATHER: frozenset[str] = frozenset({"OBPI-0.0.41-03", "OBPI-0.0.63-01"})

    def test_grandfather_set_is_shrink_only(self) -> None:
        """No OBPI may be added to the Signature (c) grandfather.

        A new channel disagreement means an author under-declared `Task:`
        trailers on a commit they can still amend, or the pipeline minted TASKs
        it never attributed. Both are fixable at the source, so growing this
        list would convert a real finding into a permanent exemption.
        """
        from gzkit.commands.validate_task_envelope import _SIG_C_DRIFT_GRANDFATHER

        self.assertEqual(
            set(_SIG_C_DRIFT_GRANDFATHER) - self._EXPECTED_GRANDFATHER,
            set(),
            "Signature (c) grandfather grew — fix the TASK attribution instead",
        )

    def test_comparison_coverage_does_not_silently_regress(self) -> None:
        """The gate must keep comparing at least as many OBPIs as it does today.

        Measured 2026-07-29: 6 compared of 669. That is LOW by design limit, not
        by accident — `@advances` and brief-frontmatter `tasks:` are unpopulated
        repo-wide (0 keys each), so only ledger x commit_trailer can ever pair,
        and just 12 OBPIs carry OBPI-scoped `Task:` trailers.

        Pinned so the number cannot drift toward zero unnoticed. A gate that
        stops comparing looks exactly like a gate finding nothing (GHI #731).
        """
        from gzkit.commands.validate_task_envelope import _sig_c_comparison_coverage

        compared, total = _sig_c_comparison_coverage(self._REPO)

        self.assertGreaterEqual(
            compared,
            6,
            f"Signature (c) now compares {compared} of {total} OBPIs, down from "
            "the 6 pinned on 2026-07-29 — the gate is going inert",
        )

    def test_advances_channel_is_asserted_dead_not_assumed_dead(self) -> None:
        """`@advances` carries no keys, and that is recorded rather than inferred.

        Scope narrowed under GHI #752. This asserted BOTH dead channels until
        `tasks:` gained a producer (`_stamp_brief_task_declaration`, stamped by
        `gz task start`). Keeping the frontmatter arm would have inverted the
        test's meaning: the first genuine stamp would fail the suite, so a
        WORKING producer would read as a regression — the assertion would be
        pinning the defect open instead of pinning the measurement honest.

        `@advances` keeps the assertion because it is dead by construction, not
        by neglect: it marks the function an author judges materially advances a
        TASK, and no runtime can know which function that is. It is demoted to
        advisory in `.gzkit/rules/task-discovery.md`. If it ever becomes
        populated, that is a design change and Signature (c)'s coverage floor
        must be re-derived — which is what this test forces.
        """
        from gzkit.commands.validate_task_envelope import _advances_channel_map

        self.assertEqual(
            len(_advances_channel_map()),
            0,
            "the @advances channel is now populated — it is demoted to advisory "
            "with no producer, so this is a design change; re-derive Signature "
            "(c)'s coverage floor and the GHI #752 measurements",
        )


if __name__ == "__main__":
    unittest.main()
