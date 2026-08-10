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

from gzkit.exchange_records import (
    find_exchange_for_release,
    write_completion_exchange,
)
from gzkit.handoff_api import (
    DecisionAttribution,
    ObservedState,
    ReferenceKind,
    ReferenceState,
    StalenessLevel,
    StepReference,
    create_handoff,
    list_handoffs,
    load_handoff_chain,
    parse_decisions,
    resume_handoff,
    scaffold_handoff,
    settled_rulings,
)
from gzkit.handoff_validation import (
    PROSPECTIVE_SECTIONS,
    REQUIRED_SECTIONS,
    SETTLED_SECTION,
    HandoffValidationError,
    parse_frontmatter,
    validate_handoff_document,
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
    def test_lists_adr_less_handoffs_and_sorts_newest_first(self) -> None:
        """An ADR-less handoff is listed unscoped and omitted when ADR-scoped.

        GHI #709: a handoff carries continuity for any work, so ``adr_id`` is
        optional and cannot be the is-this-a-handoff discriminator. Scoping to
        an ADR still excludes ADR-less handoffs — that is the filter doing its
        job, not the discriminator rejecting a non-handoff.
        """
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
            # No adr_id — a design/triage session. Newest, so it heads the
            # unscoped listing and is absent from the ADR-scoped one.
            _write_frontmatter_handoff(
                hd, name="noadr.md", adr_id=None, timestamp="2026-07-13T10:00:00Z"
            )

            unscoped = list_handoffs(base_path=base)
            self.assertEqual(
                [Path(i.path).name for i in unscoped],
                ["noadr.md", "b.md", "c.md", "a.md"],
            )
            self.assertIsNone(unscoped[0].adr_id)

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

    @covers("REQ-0.0.65-02-03")
    def test_orders_deterministically_when_timestamps_tie(self) -> None:
        # "Newest-first" must be a TOTAL order. Sorting on the timestamp alone
        # leaves equal-timestamp handoffs in `Path.glob` order, which is
        # `readdir` order and therefore filesystem-dependent: APFS returns a
        # hash order, ext4 returns roughly insertion order, so the same tree
        # ranks differently on a developer laptop and on CI.
        #
        # This is not cosmetic. `_newest_predecessor` takes element [0] to build
        # the `continues_from` chain link, and `handoff_resume_gate.newest_handoff`
        # takes the first resumable entry to decide which handoff an operator
        # must authorize. Two handoffs written in the same second — reachable
        # whenever `gz obpi complete` writes its mechanical completion register
        # entry alongside an authored one — would otherwise pick a different
        # handoff on each platform.
        #
        # The tie-break is the path, which carries no recency meaning; its job
        # is to be total, not to be semantically "newer".
        names = ["20260714T090000Z-alpha.md", "20260714T090000Z-beta.md"]
        listings = []
        for creation_order in (names, list(reversed(names))):
            with tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                hd = base / ".gzkit" / "handoffs"
                hd.mkdir(parents=True)
                for name in creation_order:
                    _write_frontmatter_handoff(
                        hd, name=name, adr_id="ADR-0.0.65", timestamp="2026-07-14T09:00:00Z"
                    )
                listings.append([Path(i.path).name for i in list_handoffs(base_path=base)])

        # Creation order must not change the ranking...
        self.assertEqual(listings[0], listings[1])
        # ...and the ranking is the declared one, so the tie-break cannot drift
        # into whatever the host filesystem happens to hand back.
        self.assertEqual(listings[0], sorted(names, reverse=True))


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

    def test_enumeration_collapsed_onto_one_line_still_yields_every_step(self) -> None:
        """A run of ``1. … 2. … 3. …`` in one paragraph is still N steps.

        ``gz handoff create --next-steps`` takes the section as a single string,
        so an author who numbers inline authors one LINE holding four STEPS.
        Matching enumeration only at line start consumed the first and dropped
        the rest — the identical "authored 3-5, consumed 1" outcome GHI #696
        names, reached through authoring shape rather than through the scalar
        return. Observed on `20260724T114926Z`, whose four advised steps
        rendered as `next steps (1)`.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff_dir = base / ".gzkit" / "handoffs"
            handoff_dir.mkdir(parents=True)
            collapsed = (
                "Resume the degrading tier in rank order. 2. VERIFY reproduction "
                "before fixing each item. 3. #607 is GOVERNANCE-PARKED; surface it. "
                "4. Obtain operator authorization before executing any of them."
            )
            self._handoff_with_steps(handoff_dir, (collapsed,))

            result = resume_handoff(adr_id="ADR-0.0.65", base_path=base, now="2026-07-18T11:00:00Z")

            self.assertEqual(
                list(result.next_steps),
                [
                    "Resume the degrading tier in rank order.",
                    "VERIFY reproduction before fixing each item.",
                    "#607 is GOVERNANCE-PARKED; surface it.",
                    "Obtain operator authorization before executing any of them.",
                ],
                "an inline-numbered run must split into one entry per authored step",
            )

    def test_decimal_bearing_prose_is_not_split_into_bogus_steps(self) -> None:
        """Splitting keys on ``N. `` — a version or ratio must not trigger it."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff_dir = base / ".gzkit" / "handoffs"
            handoff_dir.mkdir(parents=True)
            self._handoff_with_steps(
                handoff_dir,
                ("Bump to 0.33.1 and re-verify ADR-0.0.65; coverage held at 40.00%.",),
            )

            result = resume_handoff(adr_id="ADR-0.0.65", base_path=base, now="2026-07-18T11:00:00Z")

            self.assertEqual(
                list(result.next_steps),
                ["Bump to 0.33.1 and re-verify ADR-0.0.65; coverage held at 40.00%."],
            )

    def test_empty_next_steps_section_yields_empty_list_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff_dir = base / ".gzkit" / "handoffs"
            handoff_dir.mkdir(parents=True)
            self._handoff_with_steps(handoff_dir, ())

            result = resume_handoff(adr_id="ADR-0.0.65", base_path=base, now="2026-07-18T11:00:00Z")

            self.assertEqual(list(result.next_steps), [])
            self.assertEqual(result.first_next_step, "")


class TestResumeVerifiesStepReferences(unittest.TestCase):
    """An advised next step is checked against live state before it is relayed.

    The resume contract (`gz-session-handoff/SKILL.md` § Claim Verification Gate)
    requires verifying "the precondition of each advised step ... a step whose
    precondition is STALE is void". Nothing mechanized that: ``resume_handoff``
    returned authored strings, so a step could advise work that was already done.

    Observed instance (GHI #696 defect 2): the `20260717T015912Z` handoff advised
    as its #1 action "RULE ON GHI #693 ... the only NEEDED FIX this session leaves
    open". GHI #693 had been closed by commit `8aa9b887` BEFORE that handoff was
    written. The advisory was authored from session working memory and never
    checked, so the successor session re-adjudicated a settled question.
    """

    def _handoff_with_steps(self, directory: Path, steps: tuple[str, ...]) -> None:
        numbered = "\n".join(f"{i}. {step}" for i, step in enumerate(steps, start=1))
        body = (
            "---\nmode: CREATE\nadr_id: ADR-0.0.65\nbranch: main\n"
            "timestamp: 2026-07-18T10:00:00Z\nagent: test-agent\n---\n\n"
            f"## Immediate Next Steps\n\n{numbered}\n"
        )
        (directory / "h.md").write_text(body, encoding="utf-8", newline="\n")

    def _resume(
        self,
        steps: tuple[str, ...],
        checker: object = None,
        tmp: str | None = None,
    ) -> object:
        with tempfile.TemporaryDirectory() as made:
            base = Path(tmp or made)
            handoff_dir = base / ".gzkit" / "handoffs"
            handoff_dir.mkdir(parents=True, exist_ok=True)
            self._handoff_with_steps(handoff_dir, steps)
            return resume_handoff(
                adr_id="ADR-0.0.65",
                base_path=base,
                now="2026-07-18T11:00:00Z",
                reference_checker=checker,
            )

    def test_settled_reference_voids_the_step_that_depends_on_it(self) -> None:
        """A step whose cited precondition is settled is not actionable."""

        def checker(reference: StepReference) -> ReferenceState:
            return ReferenceState.SETTLED if reference.identifier == "693" else ReferenceState.LIVE

        result = self._resume(
            ("Rule on GHI #693 (cli audit presence-vs-truth).", "Close out ADR-0.0.37."),
            checker=checker,
        )

        self.assertTrue(
            result.steps[0].cites_settled,
            "a step citing a settled reference must be flagged, not relayed unexamined",
        )
        self.assertFalse(result.steps[1].cites_settled)

    def test_live_reference_leaves_the_step_actionable(self) -> None:
        result = self._resume(
            ("Rule on GHI #691 (rules have no aging clock).",),
            checker=lambda _reference: ReferenceState.LIVE,
        )

        self.assertFalse(result.steps[0].cites_settled)

    def test_every_governance_reference_kind_is_extracted(self) -> None:
        """GHI, ADR, and OBPI tokens all reach the checker as domain references."""
        result = self._resume(
            ("Finish OBPI-0.0.65-02 under ADR-0.0.65, then rule on #691.",),
            checker=lambda _reference: ReferenceState.LIVE,
        )

        found = {(ref.kind, ref.identifier) for ref in result.steps[0].references}
        self.assertEqual(
            found,
            {
                (ReferenceKind.OBPI, "OBPI-0.0.65-02"),
                (ReferenceKind.ADR, "ADR-0.0.65"),
                (ReferenceKind.GHI, "691"),
            },
        )

    def test_absent_checker_yields_unknown_never_live(self) -> None:
        """With no adapter injected the core resolves nothing — and says so.

        UNKNOWN must not collapse into LIVE. A resume that cannot reach live
        state has not verified the step; rendering that as verified is the
        failure this seam exists to prevent.
        """
        result = self._resume(("Rule on GHI #693.",))

        states = [ref.state for ref in result.steps[0].references]
        self.assertEqual(states, [ReferenceState.UNKNOWN])
        self.assertFalse(
            result.steps[0].cites_settled,
            "unknown is not settled — an unresolvable reference must not be flagged",
        )

    def test_step_without_references_is_never_void(self) -> None:
        result = self._resume(
            ("Verify reproduction before fixing each item.",),
            checker=lambda _reference: ReferenceState.SETTLED,
        )

        self.assertEqual(result.steps[0].references, ())
        self.assertFalse(result.steps[0].cites_settled)

    def test_next_steps_stays_the_derived_text_projection(self) -> None:
        """Defect 1's contract survives: every authored step, in authored order."""
        authored = ("Rule on GHI #691.", "Re-verify Pass A rows 1-8.", "Close ADR-0.0.37.")

        result = self._resume(authored, checker=lambda _reference: ReferenceState.LIVE)

        self.assertEqual(list(result.next_steps), list(authored))
        self.assertEqual(result.first_next_step, authored[0])
        self.assertEqual(result.model_dump()["next_steps"], list(authored))


class TestDecisionAttribution(unittest.TestCase):
    """An operator ruling must be distinguishable from an agent's own choice.

    GHI #696 defect 4: in `20260716T204012Z`, DECISION 5 was "(operator ruling):
    route GHI #690 to a chore" and DECISION 3 was a unilateral agent choice about
    glob width — same section, same numbering, same apparent authority. Nothing
    distinguished them, so both arrived at the next session equally re-arguable.
    Operator canon, verbatim: "MY WORD IS AUTHORITY IN ALL CASES."

    ``UNATTRIBUTED`` is first-class: an unmarked decision is never silently
    promoted to an operator ruling, and never silently demoted to an agent choice.
    """

    def _decisions(self, body: str) -> list:
        content = (
            "---\nmode: CREATE\nadr_id: ADR-0.0.65\nbranch: main\n"
            "timestamp: 2026-07-18T10:00:00Z\nagent: test-agent\n---\n\n"
            f"## Decisions Made\n\n{body}\n\n## Immediate Next Steps\n\n1. Continue.\n"
        )
        return parse_decisions(content)

    def test_operator_ruled_and_agent_chose_are_separated(self) -> None:
        decisions = self._decisions(
            "- [operator-ruled] Route GHI #690 to a chore.\n"
            "- [agent-chose] Widened the glob to cover nested rule dirs."
        )

        self.assertEqual(
            [(d.attribution, d.text) for d in decisions],
            [
                (DecisionAttribution.OPERATOR_RULED, "Route GHI #690 to a chore."),
                (
                    DecisionAttribution.AGENT_CHOSE,
                    "Widened the glob to cover nested rule dirs.",
                ),
            ],
        )

    def test_unmarked_decision_is_unattributed_not_guessed(self) -> None:
        decisions = self._decisions("- Chose to wrap the validator rather than reimplement it.")

        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0].attribution, DecisionAttribution.UNATTRIBUTED)
        self.assertEqual(
            decisions[0].text,
            "Chose to wrap the validator rather than reimplement it.",
            "the marker is stripped from the text; absent marker leaves text intact",
        )

    def test_attribution_marker_is_case_and_spacing_tolerant(self) -> None:
        decisions = self._decisions("- [Operator-Ruled]  Do NOT promote sensitivity into GATE5.")

        self.assertEqual(decisions[0].attribution, DecisionAttribution.OPERATOR_RULED)
        self.assertEqual(decisions[0].text, "Do NOT promote sensitivity into GATE5.")

    def test_resume_surfaces_the_attributed_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff_dir = base / ".gzkit" / "handoffs"
            handoff_dir.mkdir(parents=True)
            (handoff_dir / "h.md").write_text(
                "---\nmode: CREATE\nadr_id: ADR-0.0.65\nbranch: main\n"
                "timestamp: 2026-07-18T10:00:00Z\nagent: test-agent\n---\n\n"
                "## Decisions Made\n\n- [operator-ruled] Defer #641 to Movement IV.\n\n"
                "## Immediate Next Steps\n\n1. Continue.\n",
                encoding="utf-8",
                newline="\n",
            )

            result = resume_handoff(adr_id="ADR-0.0.65", base_path=base, now="2026-07-18T11:00:00Z")

            self.assertEqual(len(result.decisions), 1)
            self.assertEqual(result.decisions[0].attribution, DecisionAttribution.OPERATOR_RULED)


class TestSettledRulingsCarryForward(unittest.TestCase):
    """A settled ruling has a home, and reaches the next session without authoring.

    GHI #696 defect 3: `Decisions Made` is scoped to THIS session and
    `Pending Work / Open Loops` to UNFINISHED, so a ruling that is settled AND
    still relevant had no channel — it was re-filed as an open loop and read as
    undecided. `20260716T204012Z` DECISION 10 settled "do NOT promote
    `sensitivity` into `GATE5_INVARIANTS`" with full rationale; it reappeared in
    the next two handoffs inside the open-loop channel.

    The section is OPTIONAL and self-populating. Making it required would break
    every post-cutover handoff the `handoff-documents` gate validates, and making
    it hand-filled would add a section an author must remember — the failure mode
    this GHI documents, not its cure.
    """

    _SECTIONS = dict(_SEVEN_SECTIONS)

    def _create(self, base: Path, slug: str, decisions: str, *, hour: int = 10) -> Path:
        """Author one handoff. ``hour`` is explicit so chain order is deterministic.

        ``create_handoff`` stamps second-resolution timestamps, so three handoffs
        authored inside one second tie and "newest predecessor" becomes arbitrary.
        Real handoffs are minutes apart; the fixture must not depend on that.
        """
        sections = dict(self._SECTIONS)
        sections["Decisions Made"] = decisions
        return create_handoff(
            adr_id="ADR-0.0.65",
            branch="main",
            agent="test-agent",
            slug=slug,
            sections=sections,
            base_path=base,
            timestamp=f"2026-07-18T{hour:02d}:00:00Z",
        )

    def test_operator_ruling_is_promoted_into_the_successor_settled_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(
                base,
                "first",
                "- [operator-ruled] Do NOT promote sensitivity into GATE5_INVARIANTS.",
                hour=10,
            )

            second = self._create(base, "second", "- [agent-chose] Used a shared helper.", hour=11)

            settled = settled_rulings(second.read_text(encoding="utf-8"))
            self.assertIn(
                "Do NOT promote sensitivity into GATE5_INVARIANTS.",
                " ".join(settled),
                "a booked operator ruling reaches the next session as SETTLED, not as an open loop",
            )

    def test_agent_choice_is_not_promoted(self) -> None:
        """Only operator rulings are settled — an agent's own choice stays re-arguable."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(base, "first", "- [agent-chose] Widened the glob.", hour=10)

            second = self._create(base, "second", "- [agent-chose] Used a shared helper.", hour=11)

            self.assertEqual(settled_rulings(second.read_text(encoding="utf-8")), [])

    def test_settled_rulings_accumulate_down_the_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(base, "first", "- [operator-ruled] Ruling one holds.", hour=10)
            self._create(base, "second", "- [operator-ruled] Ruling two holds.", hour=11)

            third = self._create(base, "third", "- [agent-chose] Nothing settled here.", hour=12)

            settled = " ".join(settled_rulings(third.read_text(encoding="utf-8")))
            self.assertIn("Ruling one holds.", settled)
            self.assertIn("Ruling two holds.", settled)

    def test_wrapped_ruling_survives_the_carry_intact(self) -> None:
        """A hard-wrapped ruling must carry forward whole, not first-line-only.

        `_section_items` matched the bullet marker per LINE, so an entry wrapped
        across lines lost everything after the first. Observed live on
        `20260726T004802Z`, whose ruling wrapped at four lines and arrived in its
        successor as *"Book the patch release as this session's work and leave
        the"* — the operative clause (`unauthorized`), the operator's verbatim
        words, and the session id all silently dropped. A ruling truncated
        mid-sentence can invert its own meaning, and it also fails to dedup
        against its untruncated twin, so BOTH survive down the chain.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(
                base,
                "first",
                "- [operator-ruled] Book the patch release as this session's work\n"
                "  and leave the resumed handoff's advised steps unauthorized\n"
                '  (operator verbatim: "/gz-patch-release").',
                hour=10,
            )
            second = self._create(base, "second", "- [agent-chose] Nothing new.", hour=11)

            settled = settled_rulings(second.read_text(encoding="utf-8"))
            self.assertEqual(len(settled), 1)
            self.assertIn("unauthorized", settled[0])
            self.assertIn("/gz-patch-release", settled[0])

    def test_continuation_join_does_not_merge_sibling_rulings(self) -> None:
        # Negative control — only INDENTED non-marker lines continue an entry.
        # Two separate bullets must stay two rulings, or the join would silently
        # weld distinct operator rulings into one, which is the same class of
        # loss the truncation causes.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(
                base,
                "first",
                "- [operator-ruled] Ruling one holds.\n- [operator-ruled] Ruling two holds.",
                hour=10,
            )
            second = self._create(base, "second", "- [agent-chose] Nothing new.", hour=11)

            settled = settled_rulings(second.read_text(encoding="utf-8"))
            self.assertEqual(len(settled), 2)

    def test_settled_entries_are_not_duplicated_on_re_carry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(base, "first", "- [operator-ruled] Ruling one holds.", hour=10)
            self._create(base, "second", "- [agent-chose] Nothing new.", hour=11)

            third = self._create(base, "third", "- [agent-chose] Still nothing new.", hour=12)

            settled = settled_rulings(third.read_text(encoding="utf-8"))
            self.assertEqual(
                len([entry for entry in settled if "Ruling one holds." in entry]),
                1,
                "carrying a ruling forward twice must not duplicate it",
            )

    def test_typographic_variance_does_not_re_carry_the_same_ruling(self) -> None:
        """One ruling authored in two sections with different quote glyphs is ONE ruling.

        Observed on `20260725T085656Z`: the #580 reframe ruling landed twice in
        Settled Rulings, byte-identical except `'...'` versus `"..."` around the
        operator's verbatim words. Its predecessor had hand-written the same
        ruling into both `Decisions Made` and `Settled Rulings` with different
        quoting, and the exact-string compare saw two rulings.

        This accretes rather than staying flat: every handoff carries the whole
        settled set forward, so a typographic near-duplicate is copied into every
        descendant. The blast radius is one line today; the shape is unbounded.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            sections = dict(self._SECTIONS)
            sections["Decisions Made"] = (
                '- [operator-ruled] Reframe #580 (operator verbatim: "truncation survival").'
            )
            sections[SETTLED_SECTION] = "- Reframe #580 (operator verbatim: 'truncation survival')."
            create_handoff(
                adr_id="ADR-0.0.65",
                branch="main",
                agent="test-agent",
                slug="first",
                sections=sections,
                base_path=base,
                timestamp="2026-07-18T10:00:00Z",
            )

            second = self._create(base, "second", "- [agent-chose] Nothing new.", hour=11)

            settled = settled_rulings(second.read_text(encoding="utf-8"))
            self.assertEqual(
                len([entry for entry in settled if "Reframe #580" in entry]),
                1,
                "quote-glyph variance is not a second ruling",
            )

    def test_distinct_rulings_are_never_collapsed(self) -> None:
        """The dedup key must not merge rulings that genuinely differ.

        Dropping a booked ruling is silent and is the exact decay the settled
        channel exists to stop, whereas a duplicate is visible and benign — so
        normalization stays conservative, and this is the assertion that pins it.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(
                base,
                "first",
                "- [operator-ruled] Ruling one holds.\n"
                "- [operator-ruled] Ruling one holds only for foundation ADRs.",
                hour=10,
            )

            second = self._create(base, "second", "- [agent-chose] Nothing new.", hour=11)

            settled = settled_rulings(second.read_text(encoding="utf-8"))
            self.assertEqual(len(settled), 2, "near-identical but distinct rulings both survive")

    def test_author_supplied_ruling_does_not_drop_carried_rulings(self) -> None:
        """Seating a late ruling must UNION with the carried set, never replace it.

        A ruling can arrive AFTER a handoff is authored — the operator rules on a
        GHI once the session's handoff is already committed. The only seat for it is
        the next handoff's Settled Rulings. If supplying that section suppressed
        inheritance, seating one late ruling would silently drop every ruling booked
        before it, which turns the cure into a new instance of the same decay.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(base, "first", "- [operator-ruled] Earlier ruling holds.", hour=10)

            sections = dict(self._SECTIONS)
            sections["Decisions Made"] = "- [agent-chose] Nothing new."
            sections[SETTLED_SECTION] = "- Late ruling arrived after the prior handoff."
            second = create_handoff(
                adr_id="ADR-0.0.65",
                branch="main",
                agent="test-agent",
                slug="second",
                sections=sections,
                base_path=base,
                timestamp="2026-07-18T11:00:00Z",
            )

            settled = settled_rulings(second.read_text(encoding="utf-8"))
            self.assertIn("Earlier ruling holds.", settled, "carried rulings must survive")
            self.assertIn("Late ruling arrived after the prior handoff.", settled)

    def test_carried_rulings_precede_the_newly_seated_one(self) -> None:
        """Carried first, then new — the settled list reads oldest-booked-first."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(base, "first", "- [operator-ruled] Earlier ruling holds.", hour=10)

            sections = dict(self._SECTIONS)
            sections["Decisions Made"] = "- [agent-chose] Nothing new."
            sections[SETTLED_SECTION] = "- Late ruling."
            second = create_handoff(
                adr_id="ADR-0.0.65",
                branch="main",
                agent="test-agent",
                slug="second",
                sections=sections,
                base_path=base,
                timestamp="2026-07-18T11:00:00Z",
            )

            self.assertEqual(
                settled_rulings(second.read_text(encoding="utf-8")),
                ["Earlier ruling holds.", "Late ruling."],
            )

    def test_reseating_an_already_carried_ruling_does_not_double_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(base, "first", "- [operator-ruled] Ruling one holds.", hour=10)

            sections = dict(self._SECTIONS)
            sections["Decisions Made"] = "- [agent-chose] Nothing new."
            sections[SETTLED_SECTION] = "- Ruling one holds."
            second = create_handoff(
                adr_id="ADR-0.0.65",
                branch="main",
                agent="test-agent",
                slug="second",
                sections=sections,
                base_path=base,
                timestamp="2026-07-18T11:00:00Z",
            )

            self.assertEqual(
                settled_rulings(second.read_text(encoding="utf-8")), ["Ruling one holds."]
            )

    def test_adr_less_handoff_inherits_no_settled_rulings(self) -> None:
        """Settled lineage and chain lineage must be the SAME authority.

        ``_newest_predecessor`` refuses to link an ADR-less handoff to the newest
        handoff overall — "the newest handoff overall is not its lineage, and
        linking to it would assert a continuity that does not exist". Carrying that
        handoff's rulings forward would assert exactly the continuity the chain
        link declined to assert, from a second, disagreeing authority.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(base, "adr-scoped", "- [operator-ruled] Unrelated ruling.", hour=10)

            sections = dict(self._SECTIONS)
            sections["Decisions Made"] = "- [agent-chose] Triage pass, no parent ADR."
            adr_less = create_handoff(
                adr_id=None,
                branch="main",
                agent="test-agent",
                slug="triage",
                sections=sections,
                base_path=base,
                timestamp="2026-07-18T11:00:00Z",
            )

            content = adr_less.read_text(encoding="utf-8")
            self.assertEqual(settled_rulings(content), [])
            self.assertNotIn(
                "continues_from",
                content,
                "the chain link is withheld for an ADR-less handoff; settled must agree",
            )

    def test_settled_section_is_not_required_for_validation(self) -> None:
        """The corpus predates this section; a handoff without it must stay valid."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = self._create(base, "only", "- [agent-chose] No rulings this session.", hour=10)

            self.assertEqual(
                validate_handoff_document(path.read_text(encoding="utf-8"), base_path=base),
                [],
            )

    def test_resume_surfaces_carried_settled_rulings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(base, "first", "- [operator-ruled] Ruling one holds.", hour=10)
            self._create(base, "second", "- [agent-chose] Nothing new.", hour=11)

            result = resume_handoff(adr_id="ADR-0.0.65", base_path=base, now="2026-07-18T11:00:00Z")

            self.assertIn("Ruling one holds.", " ".join(result.settled))


class TestAdrlessChainCarriesRulings(unittest.TestCase):
    """An asserted `continues_from` carries rulings, not just the chain link.

    `_newest_predecessor` refuses to INFER a predecessor for an ADR-less handoff
    (GHI #709) -- the newest handoff overall is not its lineage -- and its
    docstring names the remedy: *"Pass ``continues_from`` explicitly to chain
    ADR-less handoffs."* Following that remedy restored the frontmatter link and
    nothing else: `_carried_settled` still resolved lineage through
    `_newest_predecessor`, which returns `None` without an ADR, so the successor
    inherited no rulings at all.

    The result is worse than an unlinked handoff, because the frontmatter now
    ASSERTS a continuity the Settled Rulings section silently contradicts. That
    is the decay #696 closed, reappearing through the ADR-less door #709 opened.
    Observed on a live ADR-less handoff (2026-07-25): four booked operator
    rulings were dropped while `continues_from` named the handoff that booked
    them.
    """

    _SECTIONS = dict(_SEVEN_SECTIONS)

    def _create(
        self, base: Path, slug: str, decisions: str, *, settled: list[str] | None = None, **kw
    ) -> Path:
        sections = dict(self._SECTIONS)
        sections["Decisions Made"] = decisions
        if settled:
            # Same seating the CLI's --settled performs (commands/handoff.py).
            sections[SETTLED_SECTION] = "\n".join(f"- {entry}" for entry in settled)
        return create_handoff(
            adr_id=None,
            branch="main",
            agent="test-agent",
            slug=slug,
            sections=sections,
            base_path=base,
            **kw,
        )

    def test_explicit_link_carries_the_predecessors_rulings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            first = self._create(
                base,
                "first",
                "- [operator-ruled] Reframe #580 to truncation survival.",
                timestamp="2026-07-25T01:00:00Z",
            )
            second = self._create(
                base,
                "second",
                "- [agent-chose] Extended the triage script.",
                timestamp="2026-07-25T06:00:00Z",
                continues_from=first.name,
            )
            self.assertIn(
                "Reframe #580 to truncation survival.",
                " ".join(settled_rulings(second.read_text(encoding="utf-8"))),
            )

    def test_seating_a_late_ruling_does_not_drop_the_carried_ones(self) -> None:
        # The union property, on the ADR-less path specifically. Seating one
        # late ruling must never be the act that discards booked history.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            first = self._create(
                base,
                "first",
                "- [operator-ruled] Movement C is Reduce the accretion.",
                timestamp="2026-07-25T01:00:00Z",
            )
            second = self._create(
                base,
                "second",
                "- [agent-chose] Built the witness.",
                timestamp="2026-07-25T06:00:00Z",
                continues_from=first.name,
                settled=["GHI #607 is unparked."],
            )
            carried = " ".join(settled_rulings(second.read_text(encoding="utf-8")))
            self.assertIn("Movement C is Reduce the accretion.", carried)
            self.assertIn("GHI #607 is unparked.", carried)

    def test_unlinked_adrless_handoff_still_inherits_nothing(self) -> None:
        # The #709 guarantee is unchanged: absent an asserted link there is no
        # lineage to read, and the newest handoff overall must not be mistaken
        # for one.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._create(
                base,
                "unrelated",
                "- [operator-ruled] A ruling from unrelated work.",
                timestamp="2026-07-25T01:00:00Z",
            )
            second = self._create(
                base,
                "second",
                "- [agent-chose] Did something else.",
                timestamp="2026-07-25T06:00:00Z",
            )
            self.assertEqual([], settled_rulings(second.read_text(encoding="utf-8")))


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
            **kwargs,
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
    """The full-slug `obpi_id` form must survive a round trip through both systems.

    Re-pointed at the exchange corpus under GHI #763. It previously wrote a
    SESSION handoff via ``create_handoff`` and asserted the token finder returned
    it — encoding the very conflation that GHI as a passing test. The REQ's claim
    is about the slug-bearing id matching, not about which system owns the
    document, so both halves are asserted here against their own system.
    """

    @covers("REQ-0.0.65-02-07")
    def test_full_slug_handoff_validates(self) -> None:
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
            self.assertEqual(validate_handoff_document(path.read_text(encoding="utf-8"), base), [])

    @covers("REQ-0.0.65-02-07")
    def test_full_slug_exchange_record_is_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            full_slug = "OBPI-0.0.65-02-programmatic-api-implementation"
            written = write_completion_exchange(
                base,
                obpi_id=full_slug,
                agent="test-agent",
                attestor="g0",
                attestation_text="attest completed",
                implementation_summary="summary",
                key_proof="proof",
                last_lock_event_timestamp="2026-07-12T09:00:00Z",
                commit_sha="abc1234",
                branch="main",
                brief_rel_path="docs/brief.md",
            )
            found = find_exchange_for_release(base, obpi_id=full_slug)
            self.assertEqual(found, written, "full-slug id must be the release-pairing match")

    @covers("REQ-0.0.65-02-07")
    def test_a_session_handoff_never_pairs_a_token_release(self) -> None:
        """The regression fence for the conflation this class used to assert."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            full_slug = "OBPI-0.0.65-02-programmatic-api-implementation"
            create_handoff(
                adr_id="ADR-0.0.65",
                branch="main",
                agent="test-agent",
                slug="release-pairing",
                sections=_SEVEN_SECTIONS,
                obpi_id=full_slug,
                base_path=base,
                timestamp="2026-07-12T10:00:00Z",
            )
            self.assertIsNone(find_exchange_for_release(base, obpi_id=full_slug))


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


class TestAuthoringAnnotatesSettledCitations(unittest.TestCase):
    """A handoff cannot be WRITTEN naming a closed GHI as live work.

    ``gz handoff resume`` has verified cited references since GHI #696, but only
    on the READING side and only over ``Immediate Next Steps``. The authoring
    side had no check at all, so a stale citation was created first and caught
    later — if the next session happened to read the annotation.

    Observed instances: the `20260808T005049Z` handoff advised five GHIs as
    "still open" that were all CLOSED (#459 since 2026-05-12); its successor
    then recorded under ``Pending Work / Open Loops`` that "GHI #573 is still
    open and unaffected by the #708 repair" — #573 closed 2026-07-24, two weeks
    before that handoff was written.

    The #573 instance is why the section scope here is TWO sections, not the one
    the resume side reads: ``Pending Work / Open Loops`` is where a handoff parks
    work for a future session, so a stale citation there outlives every other
    kind. Both arms of the same mechanism shared the same blind spot.
    """

    def _sections(self, **overrides: str) -> dict[str, str]:
        return {**_SEVEN_SECTIONS, **overrides}

    def _write(self, base: Path, sections: dict[str, str], checker: object = None) -> str:
        path = create_handoff(
            adr_id="ADR-0.0.65",
            branch="main",
            agent="test-agent",
            slug="annotated",
            sections=sections,
            base_path=base,
            timestamp="2026-08-08T10:00:00Z",
            reference_checker=checker,
        )
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _settled(*numbers: str) -> object:
        settled = set(numbers)

        def check(reference: StepReference) -> ReferenceState:
            if reference.kind is not ReferenceKind.GHI:
                return ReferenceState.UNKNOWN
            if reference.identifier in settled:
                return ReferenceState.SETTLED
            return ReferenceState.LIVE

        return check

    def test_settled_citation_in_next_steps_is_annotated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            document = self._write(
                Path(tmp),
                self._sections(**{"Immediate Next Steps": "1. Rule on GHI #693 before pulling."}),
                checker=self._settled("693"),
            )
        self.assertIn("#693 [settled]", document)

    def test_settled_citation_in_pending_work_is_annotated(self) -> None:
        """The #573 instance: a closed GHI parked as future work for a later session."""
        with tempfile.TemporaryDirectory() as tmp:
            document = self._write(
                Path(tmp),
                self._sections(
                    **{"Pending Work / Open Loops": "1. GHI #573 is still open; needs a TDD redo."}
                ),
                checker=self._settled("573"),
            )
        self.assertIn("#573 [settled]", document)

    def test_retrospective_sections_are_never_annotated(self) -> None:
        """A closed GHI in a record of finished work is CORRECT, not drift.

        Sections are typed by tense. Only a prospective section can make a
        liveness claim, so only a prospective section can make a stale one —
        annotating the record of what a session DID would falsify the archive.
        """
        with tempfile.TemporaryDirectory() as tmp:
            document = self._write(
                Path(tmp),
                self._sections(
                    **{
                        "Current State Summary": "Reopened and closed GHI #708 this session.",
                        "Evidence / Artifacts": "Commit 4c77192d8 closes GHI #708.",
                        "Decisions Made": "- [agent-chose] Reopened GHI #708 over a fresh file.",
                    }
                ),
                checker=self._settled("708"),
            )
        self.assertNotIn("[settled]", document)

    def test_live_and_unknown_citations_are_left_alone(self) -> None:
        """UNKNOWN is not a synonym for SETTLED — an unresolved ref is unverified."""
        with tempfile.TemporaryDirectory() as tmp:
            document = self._write(
                Path(tmp),
                self._sections(
                    **{"Immediate Next Steps": "1. Give GHI #768 a remedy; see OBPI-0.35.0-05."}
                ),
                checker=self._settled("999"),
            )
        self.assertNotIn("[settled]", document)

    def test_no_checker_annotates_nothing(self) -> None:
        """The core is exercisable with no adapter (hexagonal § Operative rule 6)."""
        with tempfile.TemporaryDirectory() as tmp:
            document = self._write(
                Path(tmp),
                self._sections(**{"Immediate Next Steps": "1. Rule on GHI #693 before pulling."}),
            )
        self.assertNotIn("[settled]", document)

    def test_annotation_is_idempotent(self) -> None:
        """Re-authoring an already-annotated citation must not double-mark it."""
        with tempfile.TemporaryDirectory() as tmp:
            document = self._write(
                Path(tmp),
                self._sections(**{"Immediate Next Steps": "1. Rule on GHI #693 [settled]."}),
                checker=self._settled("693"),
            )
        self.assertEqual(document.count("[settled]"), 1)


class TestProspectiveSectionsAreRealSections(unittest.TestCase):
    def test_every_prospective_section_is_a_required_section(self) -> None:
        """A section rename must not silently orphan the annotation scope.

        ``PROSPECTIVE_SECTIONS`` names sections by string. If one were renamed in
        ``REQUIRED_SECTIONS`` alone, the annotation loop would look up a key that
        never exists and quietly stop checking — a fail-open with no symptom.
        """
        self.assertTrue(
            set(PROSPECTIVE_SECTIONS) <= set(REQUIRED_SECTIONS),
            f"{set(PROSPECTIVE_SECTIONS) - set(REQUIRED_SECTIONS)} is not a required section",
        )


if __name__ == "__main__":
    unittest.main()
