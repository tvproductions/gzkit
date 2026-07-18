"""BEHAVIOR tests for the programmatic handoff authoring API (OBPI-0.0.65-02).

Each test derives its assertion from the brief's Acceptance Criteria, not from a
run of the implementation. Fixtures are deterministic and hermetic: a
``tempfile.TemporaryDirectory`` is the ``base_path``, no network, no ledger read.
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest import mock

from gzkit.handoff_api import (
    ObservedState,
    StalenessLevel,
    create_handoff,
    list_handoffs,
    load_handoff_chain,
    resume_handoff,
    scaffold_handoff,
)
from gzkit.handoff_validation import (
    HandoffValidationError,
    find_handoff_for_release,
    parse_frontmatter,
)
from gzkit.traceability import covers

_SEVEN_SECTIONS = {
    "Current State Summary": "Work paused after landing the API skeleton.",
    "Important Context": "The validation gate is the single write path.",
    "Decisions Made": "Chose to wrap validate_handoff_document rather than reimplement.",
    "Immediate Next Steps": "1. Wire the gz handoff CLI verb (OBPI-03).",
    "Pending Work / Open Loops": "CLI surface still pending.",
    "Verification Checklist": "- [ ] Tests pass.",
    "Evidence / Artifacts": "The ledger receipt records completion.",
}


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_frontmatter_handoff(
    directory: Path,
    *,
    name: str,
    adr_id: str | None,
    timestamp: str,
    obpi_id: str | None = None,
    continues_from: str | None = None,
) -> Path:
    """Write a minimal frontmatter-only fixture handoff (bypasses the gate)."""
    fm_lines = ["---", "mode: CREATE"]
    if adr_id is not None:
        fm_lines.append(f"adr_id: {adr_id}")
    fm_lines.append("branch: main")
    fm_lines.append(f"timestamp: {timestamp}")
    fm_lines.append("agent: test-agent")
    if obpi_id is not None:
        fm_lines.append(f"obpi_id: {obpi_id}")
    if continues_from is not None:
        fm_lines.append(f"continues_from: {continues_from}")
    fm_lines.append("---")
    body = "\n".join(fm_lines) + "\n\n## Immediate Next Steps\n\n1. Resume the traversal.\n"
    path = directory / name
    path.write_text(body, encoding="utf-8", newline="\n")
    return path


class TestCreateHandoff(unittest.TestCase):
    @covers("REQ-0.0.65-02-01")
    def test_writes_valid_and_fails_closed_on_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff_dir = base / ".gzkit" / "handoffs"

            path = create_handoff(
                adr_id="ADR-0.0.65",
                branch="main",
                agent="test-agent",
                slug="valid-doc",
                sections=_SEVEN_SECTIONS,
                base_path=base,
                timestamp="2026-07-12T10:00:00Z",
            )
            self.assertTrue(path.exists(), "clean document must be written to disk")
            self.assertEqual(path.parent, handoff_dir)
            before = len(list(handoff_dir.glob("*.md")))

            invalid = dict(_SEVEN_SECTIONS)
            invalid["Current State Summary"] = "This section has a TODO marker."
            with self.assertRaises(HandoffValidationError):
                create_handoff(
                    adr_id="ADR-0.0.65",
                    branch="main",
                    agent="test-agent",
                    slug="invalid-doc",
                    sections=invalid,
                    base_path=base,
                    timestamp="2026-07-12T11:00:00Z",
                )
            after = len(list(handoff_dir.glob("*.md")))
            self.assertEqual(before, after, "invalid document must NOT be written")

    @covers("REQ-0.0.65-02-01")
    def test_written_document_has_single_trailing_newline(self) -> None:
        # The repo EOF policy (end-of-file-fixer pre-commit hook) requires exactly
        # one trailing newline; a create_handoff-authored file must be commit-clean
        # on the first pass, not tripped by the hook on every write (GHI #684).
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = create_handoff(
                adr_id="ADR-0.0.65",
                branch="main",
                agent="test-agent",
                slug="eof-check",
                sections=_SEVEN_SECTIONS,
                base_path=base,
                timestamp="2026-07-12T10:00:00Z",
            )
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.endswith("\n"), "document must end with a newline")
            self.assertFalse(
                text.endswith("\n\n"), "document must not end with a trailing blank line"
            )


class TestScaffoldHandoff(unittest.TestCase):
    @covers("REQ-0.0.65-02-02")
    def test_deterministic_bytewise_prefill(self) -> None:
        observed = ObservedState(
            ledger_events=("obpi_lock_claimed", "gate_checked"),
            receipts=("arb-step-unittest-abc", "arb-ruff-def"),
            changed_files=("src/gzkit/handoff_api.py", "tests/governance/test_handoff_api.py"),
        )
        first = scaffold_handoff(adr_id="ADR-0.0.65", observed=observed, now="2026-07-12T10:00:00Z")
        second = scaffold_handoff(
            adr_id="ADR-0.0.65", observed=observed, now="2026-07-12T10:00:00Z"
        )

        self.assertEqual(first, second, "identical inputs must yield byte-identical sections")

        # Exact expected output (not substring presence): this rejects an
        # implementation that drops an injected observation OR invents a factual
        # claim the observed state never carried. A substring `assertIn` would
        # accept both failure modes (adversary Step 4b, REQ-02 falsifiability
        # hole). Sections are sorted deterministically; judgment sections are
        # intentionally absent.
        expected = {
            "Current State Summary": (
                "Scaffolded for ADR-0.0.65 at 2026-07-12T10:00:00Z.\n\n"
                "Ledger events observed:\n"
                "- gate_checked\n"
                "- obpi_lock_claimed"
            ),
            "Evidence / Artifacts": ("Receipts observed:\n- arb-ruff-def\n- arb-step-unittest-abc"),
            "Verification Checklist": (
                "Changed files to verify:\n"
                "- [ ] Review src/gzkit/handoff_api.py\n"
                "- [ ] Review tests/governance/test_handoff_api.py"
            ),
        }
        self.assertEqual(
            first, expected, "scaffold must render observed state exactly, no invention"
        )
        # Judgment sections are NOT pre-filled (only the three factual keys exist).
        self.assertEqual(
            set(first),
            {"Current State Summary", "Evidence / Artifacts", "Verification Checklist"},
        )


class TestListHandoffs(unittest.TestCase):
    @covers("REQ-0.0.65-02-03")
    def test_filters_to_adr_bearing_and_sorts_newest_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            hd = base / ".gzkit" / "handoffs"
            hd.mkdir(parents=True)
            _write_frontmatter_handoff(
                hd, name="a.md", adr_id="ADR-0.0.65", timestamp="2026-07-10T10:00:00Z"
            )
            _write_frontmatter_handoff(
                hd, name="b.md", adr_id="ADR-0.0.65", timestamp="2026-07-12T10:00:00Z"
            )
            _write_frontmatter_handoff(
                hd, name="c.md", adr_id="ADR-0.0.99", timestamp="2026-07-11T10:00:00Z"
            )
            # No adr_id → must be excluded even though it is a .md file.
            _write_frontmatter_handoff(
                hd, name="noadr.md", adr_id=None, timestamp="2026-07-13T10:00:00Z"
            )

            unscoped = list_handoffs(base_path=base)
            self.assertEqual(
                [i.path for i in unscoped],
                [(hd / "b.md").as_posix(), (hd / "c.md").as_posix(), (hd / "a.md").as_posix()],
            )

            scoped = list_handoffs(adr_id="ADR-0.0.65", base_path=base)
            self.assertEqual([Path(i.path).name for i in scoped], ["b.md", "a.md"])

    @covers("REQ-0.0.65-02-03")
    def test_orders_chronologically_across_utc_offsets(self) -> None:
        # "Newest-first" is a chronological property, not a lexicographic one.
        # An offset-bearing timestamp is a valid handoff frontmatter value
        # (accepted by the validator), and 10:00+05:00 == 05:00Z is EARLIER than
        # 08:00Z. A raw-string sort returns them in the wrong order; only a
        # parsed-datetime sort is correct (adversary Step 4b, REQ-03 regression).
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            hd = base / ".gzkit" / "handoffs"
            hd.mkdir(parents=True)
            _write_frontmatter_handoff(
                hd, name="offset.md", adr_id="ADR-0.0.65", timestamp="2026-07-12T10:00:00+05:00"
            )
            _write_frontmatter_handoff(
                hd, name="utc.md", adr_id="ADR-0.0.65", timestamp="2026-07-12T08:00:00Z"
            )
            ordered = [Path(i.path).name for i in list_handoffs(base_path=base)]
            # utc.md (08:00Z) is genuinely newer than offset.md (05:00Z); it must
            # come first. Lexicographic string order would put "offset" first.
            self.assertEqual(ordered, ["utc.md", "offset.md"])


class TestLoadHandoffChain(unittest.TestCase):
    @covers("REQ-0.0.65-02-04")
    def test_traverses_oldest_first_and_is_cycle_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            hd = base / ".gzkit" / "handoffs"
            hd.mkdir(parents=True)
            # Linear: c continues_from b continues_from a.
            _write_frontmatter_handoff(
                hd, name="a.md", adr_id="ADR-0.0.65", timestamp="2026-07-10T10:00:00Z"
            )
            _write_frontmatter_handoff(
                hd,
                name="b.md",
                adr_id="ADR-0.0.65",
                timestamp="2026-07-11T10:00:00Z",
                continues_from="a.md",
            )
            c = _write_frontmatter_handoff(
                hd,
                name="c.md",
                adr_id="ADR-0.0.65",
                timestamp="2026-07-12T10:00:00Z",
                continues_from="b.md",
            )
            chain = load_handoff_chain(c, base_path=base)
            self.assertEqual([p.name for p in chain], ["a.md", "b.md", "c.md"])

            # Cycle: x <-> y must terminate, never infinite-loop.
            _write_frontmatter_handoff(
                hd,
                name="x.md",
                adr_id="ADR-0.0.65",
                timestamp="2026-07-10T10:00:00Z",
                continues_from="y.md",
            )
            y = _write_frontmatter_handoff(
                hd,
                name="y.md",
                adr_id="ADR-0.0.65",
                timestamp="2026-07-11T10:00:00Z",
                continues_from="x.md",
            )
            cyclic = load_handoff_chain(y, base_path=base)
            # Isolate the visited-set guard, not merely the depth bound: y→x→y
            # must terminate at exactly two entries. len<=20 would still pass if
            # the visited-set early-termination regressed while the depth limit
            # held, so it cannot witness the cycle-safety the REQ names.
            self.assertEqual(len(cyclic), 2, "visited-set guard must stop the cycle at 2 entries")
            self.assertEqual({p.name for p in cyclic}, {"x.md", "y.md"})


class TestResumeHandoff(unittest.TestCase):
    @covers("REQ-0.0.65-02-05")
    def test_staleness_buckets_and_next_step(self) -> None:
        now = datetime(2026, 7, 12, 12, 0, 0, tzinfo=UTC)
        cases = [
            (now - timedelta(hours=1), StalenessLevel.FRESH, False),
            (now - timedelta(hours=48), StalenessLevel.SLIGHTLY_STALE, False),
            (now - timedelta(hours=100), StalenessLevel.STALE, True),
            (now - timedelta(days=10), StalenessLevel.VERY_STALE, True),
        ]
        for age_ts, expected_level, expected_flag in cases:
            with self.subTest(level=expected_level), tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                hd = base / ".gzkit" / "handoffs"
                hd.mkdir(parents=True)
                _write_frontmatter_handoff(
                    hd, name="h.md", adr_id="ADR-0.0.65", timestamp=_iso(age_ts)
                )
                result = resume_handoff(adr_id="ADR-0.0.65", base_path=base, now=_iso(now))
                self.assertEqual(result.staleness, expected_level)
                self.assertEqual(result.requires_human_verification, expected_flag)
                self.assertEqual(result.first_next_step, "Resume the traversal.")


class TestResumeCarriesEveryNextStep(unittest.TestCase):
    """Every authored next step must survive the resume (GHI #696).

    The authoring contract (`gz-session-handoff/SKILL.md`) mandates an "Ordered
    list of 3-5 concrete next actions". A resume that surfaces only the first
    discards items 2-N, which then migrate into the successor handoff's open-loop
    section and are met by the next session as undecided work — the observed
    decay of GHI #691 from next-step #1 to a #4 sub-bullet across three sessions.
    """

    _FOUR_STEPS = (
        "Rule on GHI #691 (rules have no aging clock).",
        "Re-verify Pass A rows 1-8.",
        "Close out ADR-0.0.37.",
        "Author the ADR-0.34.0 capstone.",
    )

    def _handoff_with_steps(self, directory: Path, steps: tuple[str, ...]) -> None:
        numbered = "\n".join(f"{i}. {step}" for i, step in enumerate(steps, start=1))
        body = (
            "---\nmode: CREATE\nadr_id: ADR-0.0.65\nbranch: main\n"
            "timestamp: 2026-07-18T10:00:00Z\nagent: test-agent\n---\n\n"
            f"## Immediate Next Steps\n\n{numbered}\n"
        )
        (directory / "h.md").write_text(body, encoding="utf-8", newline="\n")

    def test_resume_surfaces_every_authored_next_step(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff_dir = base / ".gzkit" / "handoffs"
            handoff_dir.mkdir(parents=True)
            self._handoff_with_steps(handoff_dir, self._FOUR_STEPS)

            result = resume_handoff(adr_id="ADR-0.0.65", base_path=base, now="2026-07-18T11:00:00Z")

            self.assertEqual(
                list(result.next_steps),
                list(self._FOUR_STEPS),
                "every authored next step must survive the resume, in authored order",
            )

    def test_first_next_step_remains_the_head_of_next_steps(self) -> None:
        """The scalar stays a derived head, so the ``--json`` payload is unbroken."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff_dir = base / ".gzkit" / "handoffs"
            handoff_dir.mkdir(parents=True)
            self._handoff_with_steps(handoff_dir, self._FOUR_STEPS)

            result = resume_handoff(adr_id="ADR-0.0.65", base_path=base, now="2026-07-18T11:00:00Z")

            self.assertEqual(result.first_next_step, self._FOUR_STEPS[0])
            self.assertEqual(result.model_dump()["first_next_step"], self._FOUR_STEPS[0])

    def test_empty_next_steps_section_yields_empty_list_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff_dir = base / ".gzkit" / "handoffs"
            handoff_dir.mkdir(parents=True)
            self._handoff_with_steps(handoff_dir, ())

            result = resume_handoff(adr_id="ADR-0.0.65", base_path=base, now="2026-07-18T11:00:00Z")

            self.assertEqual(list(result.next_steps), [])
            self.assertEqual(result.first_next_step, "")


class TestChainLinkIsCorrectByConstruction(unittest.TestCase):
    """A successor handoff links to its predecessor without the author's help.

    ``continues_from`` was optional and mostly unpopulated — 7 of the 12 most
    recent handoffs omitted it, so walking the chain backward hit a dead end
    four hops in and carryover could not be traced mechanically (GHI #696). An
    optional field in a chain structure is not optional; the fix is to make the
    link correct by construction rather than to fail closed on the author.
    """

    def _create(self, base: Path, slug: str, ts: str, **kwargs: object) -> Path:
        return create_handoff(
            adr_id="ADR-0.0.65",
            branch="main",
            agent="test-agent",
            slug=slug,
            sections=_SEVEN_SECTIONS,
            base_path=base,
            timestamp=ts,
            **kwargs,  # type: ignore
        )

    def test_successor_auto_links_to_newest_predecessor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            first = self._create(base, "first", "2026-07-18T10:00:00Z")
            second = self._create(base, "second", "2026-07-18T11:00:00Z")

            fm = parse_frontmatter(second.read_text(encoding="utf-8"))
            self.assertEqual(
                fm.get("continues_from"),
                first.name,
                "a successor must link to its predecessor without author action",
            )

    def test_chain_root_carries_no_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = self._create(base, "root", "2026-07-18T10:00:00Z")

            fm = parse_frontmatter(root.read_text(encoding="utf-8"))
            self.assertIsNone(
                fm.get("continues_from"),
                "the first handoff for an ADR has no predecessor to link",
            )

    def test_explicit_link_is_never_overridden(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(base, "first", "2026-07-18T10:00:00Z")
            chosen = self._create(base, "chosen", "2026-07-18T10:30:00Z")
            third = self._create(base, "third", "2026-07-18T11:00:00Z", continues_from=chosen.name)

            fm = parse_frontmatter(third.read_text(encoding="utf-8"))
            self.assertEqual(fm.get("continues_from"), chosen.name)

    def test_auto_linked_chain_walks_back_unbroken(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(base, "one", "2026-07-18T10:00:00Z")
            self._create(base, "two", "2026-07-18T11:00:00Z")
            newest = self._create(base, "three", "2026-07-18T12:00:00Z")

            chain = load_handoff_chain(newest, base_path=base)

            self.assertEqual(
                [p.name.split("-", 1)[1] for p in chain],
                ["one.md", "two.md", "three.md"],
                "the auto-linked chain must walk back to the root, oldest-first",
            )


class TestFullSlugReleasePairing(unittest.TestCase):
    @covers("REQ-0.0.65-02-07")
    def test_full_slug_handoff_validates_and_is_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            full_slug = "OBPI-0.0.65-02-programmatic-api-implementation"
            path = create_handoff(
                adr_id="ADR-0.0.65",
                branch="main",
                agent="test-agent",
                slug="release-pairing",
                sections=_SEVEN_SECTIONS,
                obpi_id=full_slug,
                base_path=base,
                timestamp="2026-07-12T10:00:00Z",
            )
            self.assertTrue(path.exists())
            found = find_handoff_for_release(base, obpi_id=full_slug)
            self.assertEqual(found, path, "full-slug handoff must be the release-pairing match")


class TestNoNetwork(unittest.TestCase):
    @covers("REQ-0.0.65-02-08")
    def test_api_opens_no_socket(self) -> None:
        observed = ObservedState(
            ledger_events=("gate_checked",),
            receipts=("arb-ruff-x",),
            changed_files=("src/gzkit/handoff_api.py",),
        )
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch("socket.socket", side_effect=RuntimeError("network forbidden")),
        ):
            base = Path(tmp)
            # A pure scaffold must not touch a socket.
            scaffold_handoff(adr_id="ADR-0.0.65", observed=observed, now="2026-07-12T10:00:00Z")
            # A full create+validate path must complete without any socket.
            path = create_handoff(
                adr_id="ADR-0.0.65",
                branch="main",
                agent="test-agent",
                slug="offline",
                sections=_SEVEN_SECTIONS,
                base_path=base,
                timestamp="2026-07-12T10:00:00Z",
            )
            self.assertTrue(path.exists(), "create must run fully with no network available")


if __name__ == "__main__":
    unittest.main()
