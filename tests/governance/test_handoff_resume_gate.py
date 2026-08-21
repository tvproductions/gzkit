"""BEHAVIOR tests for handoff-resume selection and booking coupling.

WHY: this module once carried an Operator Authorization Gate that refused tool
calls on an unruled handoff. **That gate is retired** — the Bash arm on
2026-08-14, the Write|Edit|NotebookEdit arm on 2026-08-15 (operator ruling: a
handoff is an advisor, not a gate-keeping nanny). The eight enforcement test
classes went with the behavior they asserted; keeping them would have pinned a
contract the code no longer offers.

What these assertions derive from is what survives: `newest_handoff`'s selection
rule (which document a session is advised about) and
`booking_targets_the_armed_handoff` (that `gz handoff decide` records a ruling
against the document the operator actually read, GHI #795). Both are properties
of the ADVISORY half and never depended on the gate.

`ResumeGateExemptionControlTests` carries the retirement pin: it asserts the two
enforcement claims are absent and the module exposes no enforcement surface, so
re-adding one is a test failure rather than a silent re-arming.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.handoff_resume_gate import newest_handoff
from gzkit.session_exit import FLOOR_BOOKMARK_AGENT

_SESSION = "session-abc123"


def _seed_handoff(
    base: Path,
    name: str = "20260716T000000Z-work.md",
    *,
    abandoned: bool = False,
    session_id: str | None = None,
    agent: str = "g0",
    timestamp: str = "2026-07-16T00:00:00Z",
) -> Path:
    """Write a resumable handoff.

    Carries `mode` and `timestamp`: recency is a frontmatter property, and a
    document without `mode` is not a handoff at all (it is how the generated
    `.gzkit/handoffs/AGENTS.md`, which has no frontmatter, is excluded). A
    fixture missing them would not arm the gate, so the tests would pass while
    proving nothing.

    `mode` — not `adr_id` — is the discriminator (GHI #709): `adr_id` is
    optional because a handoff carries continuity for any work, so an ADR-less
    handoff must still arm the gate. `mode` is required by `HandoffFrontmatter`,
    so a fixture omitting it was never a document the schema would admit.
    """
    d = base / ".gzkit" / "handoffs"
    d.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "mode: CREATE",
        "adr_id: ADR-0.0.65",
        "branch: main",
        f"timestamp: '{timestamp}'",
        f"agent: {agent}",
    ]
    if abandoned:
        lines.append("abandoned: true")
    if session_id is not None:
        lines.append(f"session_id: {session_id}")
    lines += ["---", "", "## Decisions Made", "", "body", ""]
    path = d / name
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _authorize(base: Path, *, session_id: str = _SESSION, handoff: str = "h.md") -> None:
    ledger = base / ".gzkit" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "event": "handoff_resume_authorized",
        "session_id": session_id,
        "handoff_path": handoff,
        "operator_text": "focus on handoff first",
    }
    with ledger.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


class BookingIsCoupledToTheArmedHandoffTests(unittest.TestCase):
    """A ruling must name the document the gate actually armed on (GHI #795).

    `handoff_path` is written into every decision event and read back by
    nothing, so consent recorded against document A discharged a gate armed on
    document B. These assertions derive from § RESUME's clause — "until the
    operator rules" is a claim about a specific document's advised steps — not
    from the implementation.

    The coupling is enforced at BOOKING time deliberately. See
    `LiftTimeStaysSessionScopedTests` for the pole that forbids the
    lift-time form of the same check.
    """

    def test_booking_on_a_handoff_the_gate_did_not_arm_on_is_refused(self) -> None:
        """The defect, stated: rule on A while the gate armed on B."""
        from gzkit.handoff_resume_gate import booking_targets_the_armed_handoff

        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            older = _seed_handoff(base, "20260716T000000Z-older.md")
            _seed_handoff(base, "20260812T000000Z-armed.md", timestamp="2026-08-12T00:00:00Z")
            self.assertFalse(
                booking_targets_the_armed_handoff(base, older),
                "a ruling on the older document does not discharge the armed one",
            )

    def test_booking_on_the_armed_handoff_is_accepted(self) -> None:
        """The permit pole — without it an always-refuse impl would false-pass."""
        from gzkit.handoff_resume_gate import booking_targets_the_armed_handoff

        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base, "20260716T000000Z-older.md")
            armed = _seed_handoff(
                base, "20260812T000000Z-armed.md", timestamp="2026-08-12T00:00:00Z"
            )
            self.assertTrue(booking_targets_the_armed_handoff(base, armed))

    def test_booking_is_permitted_when_no_handoff_is_armed(self) -> None:
        """Nothing armed means nothing to mismatch.

        Refusing here would block a harmless no-op booking, and the gate's
        standing rule is that it never blocks its own recovery.
        """
        from gzkit.handoff_resume_gate import booking_targets_the_armed_handoff

        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.assertTrue(booking_targets_the_armed_handoff(base, base / "anything.md"))

    def test_a_relative_path_resolves_against_the_project_root(self) -> None:
        """The block prose prints a repo-relative path; that spelling must match.

        A predicate that compared only absolute paths would refuse the exact
        string its own recovery command tells the operator to run.
        """
        from gzkit.handoff_resume_gate import booking_targets_the_armed_handoff

        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base, "20260812T000000Z-armed.md", timestamp="2026-08-12T00:00:00Z")
            self.assertTrue(
                booking_targets_the_armed_handoff(
                    base, Path(".gzkit/handoffs/20260812T000000Z-armed.md")
                )
            )


class ResumeGateExemptionControlTests(unittest.TestCase):
    """The coupling control is what survives the gate's retirement (GHI #797).

    It never asserted enforcement. It asserts that a ruling is booked against
    the document the operator actually read — a property of `gz handoff decide`,
    which outlives the PreToolUse arms entirely.
    """

    def test_both_enforcement_claims_are_retired_with_their_arms(self) -> None:
        """No claim may assert a refusal this module no longer performs.

        The retirement pin. `-bash` went with the Bash arm (2026-08-14) and
        `-write` with the Write|Edit|NotebookEdit arm (2026-08-15, operator
        ruling: a handoff is an advisor, not a gate-keeping nanny). A control
        asserting enforcement that does not happen reports green while blind,
        which is the facade shape the negative-control system exists to refuse.
        Re-registering either without restoring its arm re-opens that hole.
        """
        from gzkit.enforcement import get_enforcement_registry
        from gzkit.handoff_resume_gate import (
            RESUME_GATE_CLAIM_IDS,
            RESUME_GATE_COUPLING_CLAIM_ID,
            _ensure_resume_gate_claims_registered,
        )

        _ensure_resume_gate_claims_registered()
        declared = {r.claim_id: r.exempts for r in get_enforcement_registry()}
        self.assertIn(RESUME_GATE_COUPLING_CLAIM_ID, declared)
        self.assertNotIn("handoff-resume-unauthorized-bash", declared)
        self.assertNotIn("handoff-resume-unauthorized-write", declared)
        # The claim SET is pinned too, not just the registry: a member added
        # back here would be admitted by `set_known_claims` and become
        # dischargeable again without anyone re-reading this test.
        self.assertEqual(RESUME_GATE_CLAIM_IDS, frozenset({RESUME_GATE_COUPLING_CLAIM_ID}))

    def test_the_module_exposes_no_enforcement_surface(self) -> None:
        """The arm is gone from the API, not merely unregistered.

        A retired gate that still exports `decide`/`MUTATING_TOOLS` invites a
        future hook to re-register it in one line. Asserting the absence is what
        makes the retirement structural rather than a configuration choice.
        """
        import gzkit.handoff_resume_gate as gate

        for name in ("decide", "record_refusal", "MUTATING_TOOLS", "Verdict", "UNWITNESSABLE"):
            self.assertFalse(hasattr(gate, name), f"{name} survived the arm it belonged to")

    def test_the_exemption_control_catches_a_mis_targeted_booking(self) -> None:
        import shutil

        from gzkit.handoff_resume_gate import (
            _build_mis_targeted_booking_violation,
            _ep_resume_gate_booking_coupling,
        )

        root = _build_mis_targeted_booking_violation()
        try:
            self.assertEqual(_ep_resume_gate_booking_coupling(root), 1)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_the_fixture_plants_two_handoffs_so_the_control_can_discriminate(self) -> None:
        """A one-handoff fixture would pass against a gate comparing nothing.

        With a single document on disk every booking targets the armed one, so
        the control could not tell a working coupling from an absent one — the
        facade shape the enforcement floor exists to refuse.
        """
        import shutil

        from gzkit.handoff_resume_gate import _build_mis_targeted_booking_violation

        root = _build_mis_targeted_booking_violation()
        try:
            planted = sorted(p.name for p in (root / ".gzkit" / "handoffs").glob("*.md"))
            self.assertEqual(len(planted), 2, f"need two candidates to discriminate: {planted}")
        finally:
            shutil.rmtree(root, ignore_errors=True)


class FloorBookmarkIsAFloorNotAPreferenceTests(unittest.TestCase):
    """A machine floor bookmark must never displace an authored handoff (GHI #758).

    GHI #756 built the exit-beat bookmark and named this exact hazard while closing
    it on the SIBLING selector — from its close comment, on
    `find_exchange_for_release`: *"skipping rather than returning-and-rejecting,
    because a later checkpoint would otherwise win the newest-candidate sort and
    take a genuine register entry down with it."* `newest_handoff` sorts the same
    corpus newest-first and read only `abandoned`, so the hazard stayed open here.

    It is not an ordering accident. A floor bookmark is written at EVERY session
    end, so it is always the newest document on disk — the precaution structurally
    out-competes the artifact it exists to back up, on every session.

    Observed live 2026-08-05: a 1,765-byte bookmark reading "Unknown to the writer"
    was selected over a 24,877-byte authored handoff written 48 minutes earlier, and
    the session's whole orientation was built on the empty one.

    The discriminator is AUTHORSHIP, not mode. Both documents in that incident were
    `mode: CHECKPOINT` — a mode filter here would have discarded the authored one,
    which is the opposite of the fix. Mode is right for the release arm (no
    CHECKPOINT surrenders a token, whoever wrote it) and wrong for this one.
    """

    def test_an_authored_handoff_outranks_a_newer_floor_bookmark(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            authored = _seed_handoff(
                base,
                "20260716T000000Z-real-work.md",
                agent="claude-code",
                timestamp="2026-07-16T00:00:00Z",
            )
            _seed_handoff(
                base,
                "20260716T235959Z-session-exit-bookmark.md",
                agent=FLOOR_BOOKMARK_AGENT,
                timestamp="2026-07-16T23:59:59Z",
            )
            self.assertEqual(
                newest_handoff(base),
                authored,
                "the newer floor bookmark shadowed the authored handoff",
            )

    def test_the_floor_still_wins_when_it_is_the_only_record(self) -> None:
        """Deprioritize, never skip — the floor is why GHI #756 built it.

        A session that crashed or `/clear`ed before authoring leaves nothing else,
        and that is precisely the case the exit beat exists to cover. A filter that
        skipped floor bookmarks outright would delete the guarantee.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            floor = _seed_handoff(
                base,
                "20260716T235959Z-session-exit-bookmark.md",
                agent=FLOOR_BOOKMARK_AGENT,
                timestamp="2026-07-16T23:59:59Z",
            )
            self.assertEqual(newest_handoff(base), floor)

    def test_the_newest_floor_wins_among_floors(self) -> None:
        """Recency still orders within a class; the preference is between classes."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(
                base,
                "20260716T000000Z-session-exit-bookmark.md",
                agent=FLOOR_BOOKMARK_AGENT,
                timestamp="2026-07-16T00:00:00Z",
            )
            newer = _seed_handoff(
                base,
                "20260716T235959Z-session-exit-bookmark.md",
                agent=FLOOR_BOOKMARK_AGENT,
                timestamp="2026-07-16T23:59:59Z",
            )
            self.assertEqual(newest_handoff(base), newer)

    def test_an_abandoned_authored_handoff_does_not_outrank_the_floor(self) -> None:
        """The existing `abandoned` skip composes with the new preference.

        An abandoned register entry describes a surrendered token, not context to
        resume (OBPI-0.0.72-02). Preferring authorship must not resurrect one.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(
                base,
                "20260716T000000Z-real-work.md",
                agent="claude-code",
                abandoned=True,
                timestamp="2026-07-16T00:00:00Z",
            )
            floor = _seed_handoff(
                base,
                "20260716T235959Z-session-exit-bookmark.md",
                agent=FLOOR_BOOKMARK_AGENT,
                timestamp="2026-07-16T23:59:59Z",
            )
            self.assertEqual(newest_handoff(base), floor)


class ResumeGateNewestHandoffSelectionTests(unittest.TestCase):
    """Recency is a frontmatter-timestamp property, never a filename sort.

    Dogfooding regression (2026-07-16): a newest-by-FILENAME sort named a
    months-old handoff, because 14 of 205 on-disk handoffs are not
    timestamp-prefixed and `OBPI-…` sorts after `20260716T…` in ASCII. The gate
    then told the operator to authorize the wrong document.
    """

    @staticmethod
    def _write(base: Path, name: str, *, timestamp: str, abandoned: bool = False) -> Path:
        d = base / ".gzkit" / "handoffs"
        d.mkdir(parents=True, exist_ok=True)
        lines = [
            "---",
            "mode: CREATE",
            "adr_id: ADR-0.0.65",
            "branch: main",
            f"timestamp: '{timestamp}'",
        ]
        lines.append("agent: g0")
        if abandoned:
            lines.append("abandoned: true")
        lines += ["---", "", "## Decisions Made", "", "body", ""]
        path = d / name
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def test_non_timestamp_prefixed_name_does_not_win_on_lexical_sort(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            newest = self._write(
                base, "20260716T204012Z-recent.md", timestamp="2026-07-16T20:40:12Z"
            )
            # Sorts AFTER the timestamped name in ASCII but is months older.
            self._write(base, "OBPI-0.27.0-03-router-tables.md", timestamp="2026-05-01T00:00:00Z")
            self.assertEqual(newest_handoff(base), newest)

    def test_generated_agents_md_is_not_a_handoff(self) -> None:
        """`.gzkit/handoffs/AGENTS.md` is a subtree-rules file with no frontmatter."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            real = self._write(base, "20260101T000000Z-real.md", timestamp="2026-01-01T00:00:00Z")
            (base / ".gzkit" / "handoffs" / "AGENTS.md").write_text(
                "# Subtree rules\n\nnot a handoff\n", encoding="utf-8"
            )
            self.assertEqual(newest_handoff(base), real)

    def test_newest_abandoned_falls_through_to_the_newest_resumable(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            resumable = self._write(
                base, "20260701T000000Z-work.md", timestamp="2026-07-01T00:00:00Z"
            )
            self._write(
                base,
                "20260716T000000Z-x-abandoned.md",
                timestamp="2026-07-16T00:00:00Z",
                abandoned=True,
            )
            self.assertEqual(newest_handoff(base), resumable)


class RetiredGateProseTests(unittest.TestCase):
    """No production prose may assert the refusal the retired gate no longer performs.

    WHY this exists as a separate pin (GHI #805, reopened 2026-08-21). The two
    controls in `ResumeGateExemptionControlTests` read the enforcement REGISTRY
    and the module API — machine surfaces. Neither reads a string shown to a
    human. #805's own class section named that asymmetry as the general shape
    that survived its closure: *"a string template that documents its own
    enforcement scope has two consumers (the reader and the matcher) and only
    one of them is tested."*

    It reproduced six days after #805 closed. The retirement commit rewrote the
    module that IMPLEMENTED the gate and left five modules that only DESCRIBED
    it, so `gz handoff decide --help` and the SessionStart advisement both told
    a resuming agent the gate was armed while the registry pin above stayed
    green. The advisement was self-contradictory in one block — "A handoff
    advises; it does not authorize" three lines above "leave the gate armed" —
    and the agent believed the second half.

    Scope is bounded and stated: the pin covers present-tense assertion phrases,
    which is what makes a false claim false. Past-tense narrative about the
    gate's own history is deliberately NOT matched — `handoff_api.py` explains a
    GHI #758 defect in terms of what the gate did at the time, and
    `handoff_resume_gate.py` is the retirement record itself. A dated account of
    what was true on its date is not drift.
    """

    #: Phrases that only parse as a live claim of enforcement.
    RETIRED_CLAIMS = (
        "lifts the resume gate",
        "resume gate refuses",
        "leave the gate armed",
        "refuses every mutating tool call",
    )

    #: The module whose documented SUBJECT is the retirement.
    NARRATES_THE_RETIREMENT = "handoff_resume_gate.py"

    def test_no_production_module_asserts_the_retired_gate(self) -> None:
        src = Path(__file__).resolve().parents[2] / "src" / "gzkit"
        self.assertTrue(src.is_dir(), f"source tree not found at {src}")

        offenders: list[str] = []
        for path in sorted(src.rglob("*.py")):
            if path.name == self.NARRATES_THE_RETIREMENT:
                continue
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                for claim in self.RETIRED_CLAIMS:
                    if claim in line:
                        rel = path.relative_to(src.parents[1])
                        offenders.append(f"{rel}:{lineno}: {claim!r} in {line.strip()!r}")

        self.assertEqual(
            offenders,
            [],
            "Production prose asserts a resume gate retired 2026-08-15 "
            "(operator: 'the handoff should be an advisor, not a gate-keeping "
            "nanny'). Reword to describe the advisory record, never a refusal:\n"
            + "\n".join(offenders),
        )
