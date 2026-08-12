"""Multi-parent handoff lineage (GHI #790).

``continues_from`` was ``str | None``, encoding a lineage cardinality of {0, 1}.
Both boundaries of that range have now been discovered as their own silent
ruling-inheritance failure: 0 parents was GHI #717, and >1 is this one. When the
2026-08-11 fork collapsed, the two heads held DISJOINT ruling corpora — 145 and
72, measured intersection zero — and only a union was lossless. The field held
one pointer, so the second ancestor's rulings arrived only because a human
noticed the fork and hand-seated them.

The channel is supposed to be self-populating by construction
(:func:`gzkit.handoff_api._carried_settled`): *"a ruling booked once keeps
arriving, so it is never re-filed as an open loop and re-adjudicated."* A merge
is a real event in this repo's chain topology, so inheritance from BOTH ancestors
must be mechanical exactly as it is from one.

Operator ruled the widening shape 2026-08-11: ``str | list[str]`` on the same
key, so all 297 authored scalar handoffs stay readable with no migration, and
every reader delegates to one shared normalizer rather than each re-deciding what
the field means.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.handoff_api import _carried_settled, load_handoff_chain
from gzkit.handoff_validation import HandoffFrontmatter, continues_from_refs


def _write(
    directory: Path,
    *,
    name: str,
    timestamp: str,
    continues_from: str | list[str] | None = None,
    settled: list[str] | None = None,
) -> Path:
    """Write a minimal fixture handoff, optionally with multiple parents."""
    lines = ["---", "mode: CREATE", "branch: main", f"timestamp: {timestamp}", "agent: test-agent"]
    if isinstance(continues_from, str):
        lines.append(f"continues_from: {continues_from}")
    elif isinstance(continues_from, list):
        lines.append("continues_from:")
        lines.extend(f"  - {ref}" for ref in continues_from)
    lines.append("---")
    body = "\n".join(lines) + "\n\n## Immediate Next Steps\n\n1. Resume.\n"
    if settled:
        body += "\n## Settled Rulings\n\n" + "\n".join(f"- {s}" for s in settled) + "\n"
    path = directory / name
    path.write_text(body, encoding="utf-8", newline="\n")
    return path


class TestNormalizerFolds(unittest.TestCase):
    """One shared fold, so no reader re-decides what the field means."""

    def test_absent_yields_no_parents(self) -> None:
        self.assertEqual(continues_from_refs(None), [])

    def test_scalar_yields_one_parent(self) -> None:
        self.assertEqual(continues_from_refs("a.md"), ["a.md"])

    def test_list_yields_every_parent_in_order(self) -> None:
        self.assertEqual(continues_from_refs(["a.md", "b.md"]), ["a.md", "b.md"])

    def test_blank_entries_are_dropped_not_resolved(self) -> None:
        self.assertEqual(
            continues_from_refs(["a.md", "   ", ""]),
            ["a.md"],
            "A blank pointer must not become a resolution attempt against the handoffs dir",
        )


class TestScalarFormStaysReadable(unittest.TestCase):
    """297 authored handoffs carry the scalar; the widening must not orphan them."""

    def test_model_accepts_the_scalar_form(self) -> None:
        fm = HandoffFrontmatter(
            mode="CREATE",
            branch="main",
            timestamp="2026-08-11T00:00:00Z",
            agent="a",
            continues_from="a.md",
        )
        self.assertEqual(continues_from_refs(fm.continues_from), ["a.md"])

    def test_model_accepts_the_list_form(self) -> None:
        fm = HandoffFrontmatter(
            mode="CREATE",
            branch="main",
            timestamp="2026-08-11T00:00:00Z",
            agent="a",
            continues_from=["a.md", "b.md"],
        )
        self.assertEqual(continues_from_refs(fm.continues_from), ["a.md", "b.md"])


class TestRulingsInheritFromEveryAncestor(unittest.TestCase):
    """The defect itself: a merge must inherit both corpora, mechanically."""

    def test_union_carries_rulings_from_both_parents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            hd = base / ".gzkit" / "handoffs"
            hd.mkdir(parents=True)
            _write(hd, name="left.md", timestamp="2026-08-10T10:00:00Z", settled=["Ruling L"])
            _write(hd, name="right.md", timestamp="2026-08-10T11:00:00Z", settled=["Ruling R"])

            carried = _carried_settled(["left.md", "right.md"], base)
            self.assertIn("Ruling L", carried)
            self.assertIn(
                "Ruling R",
                carried,
                "The second ancestor's rulings must arrive by construction, not by a "
                "human noticing the fork and hand-seating them",
            )

    def test_shared_ruling_is_not_duplicated_by_the_merge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            hd = base / ".gzkit" / "handoffs"
            hd.mkdir(parents=True)
            shared = "Both heads booked this one"
            _write(hd, name="left.md", timestamp="2026-08-10T10:00:00Z", settled=[shared])
            _write(hd, name="right.md", timestamp="2026-08-10T11:00:00Z", settled=[shared])

            carried = _carried_settled(["left.md", "right.md"], base)
            self.assertEqual(
                carried.count(shared),
                1,
                "Converging lineage must not multiply a ruling both ancestors carried",
            )

    def test_scalar_predecessor_still_inherits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            hd = base / ".gzkit" / "handoffs"
            hd.mkdir(parents=True)
            _write(hd, name="only.md", timestamp="2026-08-10T10:00:00Z", settled=["Ruling S"])
            self.assertIn("Ruling S", _carried_settled("only.md", base))

    def test_no_predecessor_still_inherits_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / ".gzkit" / "handoffs").mkdir(parents=True)
            self.assertEqual(_carried_settled(None, base), [])
            self.assertEqual(_carried_settled([], base), [])


class TestChainWalkReachesEveryAncestor(unittest.TestCase):
    """A merged chain's lineage listing must not silently omit one side."""

    def test_both_ancestors_appear_in_the_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            hd = base / ".gzkit" / "handoffs"
            hd.mkdir(parents=True)
            _write(hd, name="a.md", timestamp="2026-08-10T09:00:00Z")
            _write(hd, name="b.md", timestamp="2026-08-10T10:00:00Z")
            merged = _write(
                hd, name="c.md", timestamp="2026-08-10T11:00:00Z", continues_from=["a.md", "b.md"]
            )
            names = [p.name for p in load_handoff_chain(merged, base_path=base)]
            self.assertEqual(names[-1], "c.md", "The start handoff remains newest-last")
            self.assertIn("a.md", names)
            self.assertIn("b.md", names)

    def test_multi_parent_cycle_still_terminates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            hd = base / ".gzkit" / "handoffs"
            hd.mkdir(parents=True)
            _write(hd, name="x.md", timestamp="2026-08-10T09:00:00Z", continues_from=["y.md"])
            y = _write(
                hd, name="y.md", timestamp="2026-08-10T10:00:00Z", continues_from=["x.md", "y.md"]
            )
            chain = load_handoff_chain(y, base_path=base)
            self.assertEqual(
                {p.name for p in chain},
                {"x.md", "y.md"},
                "The visited-set guard must still terminate a multi-parent cycle",
            )


class TestArchiveGuardProtectsEveryAncestor(unittest.TestCase):
    """Widening the field must not open an archival hole for the second parent."""

    def test_second_parent_is_chain_protected(self) -> None:
        from gzkit.handoff_archive import _chain_target_keys, _key  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            hd = base / ".gzkit" / "handoffs"
            hd.mkdir(parents=True)
            a = _write(hd, name="a.md", timestamp="2026-08-10T09:00:00Z")
            b = _write(hd, name="b.md", timestamp="2026-08-10T10:00:00Z")
            merged = _write(
                hd, name="c.md", timestamp="2026-08-10T11:00:00Z", continues_from=["a.md", "b.md"]
            )
            keys = _chain_target_keys([a, b, merged], base)
            self.assertIn(_key(a), keys)
            self.assertIn(
                _key(b),
                keys,
                "A second ancestor unseen by the guard becomes archivable while live",
            )
