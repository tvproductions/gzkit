"""BEHAVIOR tests for the handoff-resume Operator Authorization Gate (GHI #574).

WHY: `gz-session-handoff` SKILL.md § RESUME declares a universal Operator
Authorization Gate — "no file mutation / gz ceremony / migration until the
operator rules" — which was prose plus a template banner, enforced by nothing.
These assertions derive from that declared clause, not from the implementation.

Every permit-case carries a paired block-case (and vice versa), so an
always-allow or always-block implementation cannot false-pass: the gate must
track AUTHORIZATION, not any fixed answer.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.handoff_resume_gate import (
    MUTATING_TOOLS,
    UNWITNESSABLE,
    decide,
    is_resume_authorized,
    newest_handoff,
    record_refusal,
)
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


class LiftTimeStaysSessionScopedTests(unittest.TestCase):
    """Lift-time granularity is session-scoped, and that is load-bearing (GHI #795).

    The obvious fix for GHI #795 — comparing `handoff_path` inside
    `_lifts_the_gate` — is per-handoff arming reached from the other
    direction, and it reintroduces GHI #619 and GHI #755: the moment any new
    handoff becomes `newest_handoff()` mid-session, an already-granted
    clearance would stop matching and the gate would re-arm against a session
    the operator already cleared.

    This test is the fence. It fails if a future reader "helpfully" adds the
    equality check the module docstring warns against.
    """

    def test_a_handoff_authored_after_the_ruling_does_not_rearm_the_gate(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            ruled_on = _seed_handoff(base, "20260716T000000Z-ruled.md")
            _authorize(base, handoff=ruled_on.name)

            # A completion record / exit bookmark lands mid-session and becomes
            # the newest document — the GHI #619 shape.
            _seed_handoff(base, "20260812T000000Z-later.md", timestamp="2026-08-12T00:00:00Z")

            self.assertTrue(
                is_resume_authorized(base, _SESSION),
                "a clearance is AMENDED mid-flight, never revoked by a newer document",
            )

    def test_the_ruling_still_does_not_leak_across_sessions(self) -> None:
        """Session scope is the granularity that DOES bind."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            _authorize(base, session_id="some-other-session")
            self.assertFalse(is_resume_authorized(base, _SESSION))


class ResumeGateExemptionControlTests(unittest.TestCase):
    """The clearance half carries its own control (GHI #797).

    Both rule claims were registered, enrolled, and passing on every `gz check`
    for the whole life of GHI #795's coupling gap, because they assert
    refuse-unauthorized / permit-authorized and never ask WHICH document a
    ruling named.
    """

    def test_the_rule_claims_declare_which_control_covers_their_exemption(self) -> None:
        from gzkit.enforcement import get_enforcement_registry
        from gzkit.handoff_resume_gate import (
            RESUME_GATE_COUPLING_CLAIM_ID,
            _ensure_resume_gate_claims_registered,
        )

        _ensure_resume_gate_claims_registered()
        declared = {r.claim_id: r.exempts for r in get_enforcement_registry()}
        self.assertEqual(
            declared.get("handoff-resume-unauthorized-write"), RESUME_GATE_COUPLING_CLAIM_ID
        )
        self.assertIn(RESUME_GATE_COUPLING_CLAIM_ID, declared)
        # `handoff-resume-unauthorized-bash` was the second rule claim and is
        # RETIRED with the Bash arm (2026-08-14). A control still asserting that
        # `gz obpi complete` is refused would report enforcement the gate no
        # longer performs — the facade shape the NC system exists to refuse.
        self.assertNotIn("handoff-resume-unauthorized-bash", declared)

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


class ResumeGateBlocksUnauthorizedExecutionTests(unittest.TestCase):
    """The declared clause: no mutation until the operator rules."""

    def test_write_is_blocked_when_unauthorized(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            verdict = decide(base, session_id=_SESSION, tool_name="Write")
            self.assertTrue(verdict.blocked)

    def test_write_is_permitted_once_the_operator_rules(self) -> None:
        """Paired with the block case: the gate tracks authorization, not a constant."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            _authorize(base)
            self.assertFalse(decide(base, session_id=_SESSION, tool_name="Write").blocked)

    def test_every_mutating_tool_is_gated(self) -> None:
        """The contract's surviving half: 'no file mutation'."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for tool in sorted(MUTATING_TOOLS):
                with self.subTest(tool=tool):
                    verdict = decide(base, session_id=_SESSION, tool_name=tool, tool_input={})
                    self.assertTrue(verdict.blocked, f"{tool} must be gated")

    def test_bash_is_not_in_the_gated_set(self) -> None:
        """Pin the 2026-08-14 narrowing at the set itself.

        This assertion is the inverse of the one it replaces, which read "pin
        the clause that was nearly scoped out for being harder to hook." The
        clause was right about the contract and wrong about the artifact — see
        `BashIsNotGatedOnAHandoffTests` and `MUTATING_TOOLS` for the ruling.
        Re-adding Bash re-opens 13 corrections' worth of false refusals.
        """
        self.assertNotIn("Bash", MUTATING_TOOLS)
        self.assertEqual(MUTATING_TOOLS, frozenset({"Write", "Edit", "NotebookEdit"}))

    def test_read_only_tool_is_never_gated(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            self.assertFalse(decide(base, session_id=_SESSION, tool_name="Read").blocked)

    def test_no_handoff_means_no_resume_and_no_gate(self) -> None:
        """A session with nothing to resume is not a resume."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.assertFalse(decide(Path(tmp), session_id=_SESSION, tool_name="Write").blocked)
            self.assertIsNone(newest_handoff(base))


class ResumeGateCannotBeDefeatedTests(unittest.TestCase):
    """Adversarial cases — each is a way the gate could be walked around."""

    def test_another_sessions_authorization_does_not_authorize_this_one(self) -> None:
        """Session-scoped: yesterday's ruling is not today's license."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            _authorize(base, session_id="some-other-session")
            self.assertTrue(decide(base, session_id=_SESSION, tool_name="Write").blocked)
            self.assertFalse(is_resume_authorized(base, _SESSION))

    def test_empty_session_id_is_never_authorized(self) -> None:
        """A harness that supplies no session id must not open the gate."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            _authorize(base, session_id="")
            self.assertFalse(is_resume_authorized(base, ""))
            self.assertTrue(decide(base, session_id="", tool_name="Write").blocked)

    def test_missing_ledger_fails_closed(self) -> None:
        """A gate that opens when it cannot read its evidence is not a gate."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            self.assertFalse(is_resume_authorized(base, _SESSION))
            self.assertTrue(decide(base, session_id=_SESSION, tool_name="Write").blocked)

    def test_malformed_ledger_line_does_not_make_the_gate_unliftable(self) -> None:
        """A junk line elsewhere must not swallow a real authorization."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            ledger = base / ".gzkit" / "ledger.jsonl"
            ledger.parent.mkdir(parents=True, exist_ok=True)
            ledger.write_text("{not json\n", encoding="utf-8")
            _authorize(base)
            self.assertTrue(is_resume_authorized(base, _SESSION))

    def test_abandoned_register_entry_does_not_arm_the_gate(self) -> None:
        """Abandoned entries are a surrendered token, not context to resume."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base, name="20260716T000000Z-OBPI-x-abandoned.md", abandoned=True)
            self.assertIsNone(newest_handoff(base))
            self.assertFalse(decide(base, session_id=_SESSION, tool_name="Write").blocked)


class BashIsNotGatedOnAHandoffTests(unittest.TestCase):
    """The gate stops silent file edits. It does not police shell commands.

    Operator ruling 2026-08-14, verbatim: *"why is the handoff gate so picky? it
    is a reminder of what we were doing and what to do next, not a nanny"*,
    followed by *"i say the word"* authorizing this scope narrowing.

    The Bash arm was the whole recurrence. All thirteen admission-breadth
    corrections in twenty-nine days were Bash refusals — `rev-list`, the
    read-only git class, `find`, `-i`, `git-sync`, compound chains, `2>&1`,
    separators, `/dev/null`, reserved words, `fetch`. The `Write`/`Edit`/
    `NotebookEdit` arm needed none, because it has no allowlist to be
    incomplete. Removing the arm removes the defect's source rather than its
    latest instance.

    WHY the arm was wrong in principle, not merely noisy: a handoff is a
    *synthetic memory refresh* by operator canon (AGENTS.md, `invariant` tier,
    2026-08-06) — entry/exit authorization is TRANSIT's subject, the airlock's
    (ADR-0.33.0). A memory artifact has no natural blast radius, so "what should
    reading a reminder prevent?" had no principled answer; the answer invented
    was "every mutating tool call", then whittled by 44 read-exceptions. The
    gate's own charter (GHI #574) had quoted the remedy it was meant to apply:
    *"place the human at a mechanical gate, **not at every keystroke**."*

    What is retained is exactly what matches the artifact: an agent that reads a
    handoff and silently starts editing files is the failure worth a speed bump,
    and that arm needs no list.
    """

    def _verdict(self, base: Path, command: str):
        return decide(base, session_id=_SESSION, tool_name="Bash", tool_input={"command": command})

    def test_no_bash_command_is_ever_gated(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                # Reads that the allowlist admitted only after a live incident.
                "git rev-list --left-right --count origin/main...HEAD",
                "for n in 803 802; do gh issue view $n --json state; done",
                "uv run gz adr status ADR-0.35.0 2>&1 | head -60",
                "git status --short && echo '---' && git log --oneline -5",
                # Ceremony the arm used to refuse. No longer this gate's job:
                # Gate 5, pre-commit and pre-push still bind it.
                "uv run gz obpi complete OBPI-x",
                # Mutation via shell. Deliberately ungated here — see the class
                # docstring; the Write/Edit arm is where mutation is caught.
                "rm -rf src",
            ):
                with self.subTest(command=command):
                    self.assertFalse(self._verdict(base, command).blocked, command)

    def test_file_mutation_tools_are_still_gated(self) -> None:
        """The paired negative — the retained arm, which is the whole point.

        If this ever passes-through, the narrowing became a removal and the gate
        no longer does the one job its artifact supports.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for tool, payload in (
                ("Write", {"file_path": "src/x.py", "content": "x"}),
                ("Edit", {"file_path": "src/x.py"}),
                ("NotebookEdit", {"notebook_path": "n.ipynb"}),
            ):
                with self.subTest(tool=tool):
                    self.assertTrue(
                        decide(
                            base, session_id=_SESSION, tool_name=tool, tool_input=payload
                        ).blocked,
                        tool,
                    )


class ResumeGateRecordsWhatItRefusedTests(unittest.TestCase):
    """A refusal that leaves no trace cannot be counted, so it recurs.

    Operator report 2026-08-14, verbatim: "that class of error is happening
    frequently - why is it recurring?" and "I am this close to removing that
    hook". The answer was measurable: the ledger held 107
    `handoff_resume_authorized` plus 53 `handoff_resume_decided` events — 160
    records, every one of them the gate being LIFTED — and ZERO records of the
    gate blocking anything. The hook printed to stderr and exited 2.

    That asymmetry is the whole recurrence mechanism. A false PERMIT leaves a
    trace and can be audited after the fact; a false REFUSAL left none, so the
    only discovery channel was an operator getting annoyed enough to report it.
    Every dated observation in this module arrived that way, and a predicate
    ruled correct on 2026-08-12 was reversed on 2026-08-13 because the ruling
    had no measurement to be wrong against.

    The argument for recording is already written in this codebase, applied to
    the sibling half: `session_exit_bookmark_skipped_event` records a
    deliberate no-op because "a silent skip is indistinguishable from a crashed
    hook". A silent refusal is indistinguishable from a gate nobody tripped.

    IDENTITY ONLY, never payload. The event carries session, handoff and tool
    name — never the `file_path` the refused call named. A refused Write
    routinely names a path, and the operator-PII prohibition is absolute; the
    count is also the whole question, since every refusal now has the same
    subject (an edit) rather than a verb family to distinguish.
    """

    def _refusals(self, base: Path) -> list[dict]:
        ledger = base / ".gzkit" / "ledger.jsonl"
        if not ledger.exists():
            return []
        return [
            json.loads(line)
            for line in ledger.read_text(encoding="utf-8").splitlines()
            if line.strip() and json.loads(line).get("event") == "handoff_resume_blocked"
        ]

    def test_a_refusal_is_recorded(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            payload = {"file_path": "src/x.py", "content": "x"}
            self.assertTrue(
                decide(base, session_id=_SESSION, tool_name="Write", tool_input=payload).blocked
            )
            record_refusal(base, session_id=_SESSION, tool_name="Write", tool_input=payload)

            events = self._refusals(base)
            self.assertEqual(len(events), 1)
            event = events[0]
            self.assertEqual(event["session_id"], _SESSION)
            self.assertEqual(event["tool_name"], "Write")
            self.assertTrue(event["handoff_path"].endswith("20260716T000000Z-work.md"))

    def test_the_record_carries_no_payload_text(self) -> None:
        """Identity, never payload — the operator-PII prohibition is absolute.

        A refused Write routinely names a path. If the ledger stored tool input,
        the gate would turn every refusal into a durable, committed record of
        whatever the agent happened to be editing.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            record_refusal(
                base,
                session_id=_SESSION,
                tool_name="Write",
                tool_input={
                    "file_path": "/Users/someone/private/secrets.env",
                    "content": "API_KEY=hunter2",
                },
            )
            written = (base / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("secrets.env", written)
            self.assertNotIn("/Users/someone", written)
            self.assertNotIn("hunter2", written)
            self.assertIn("handoff_resume_blocked", written)

    def test_an_unblocked_call_records_nothing(self) -> None:
        """The paired negative. A counter that counts permits too counts nothing."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            # Bash is no longer gated at all, so it is the natural permit case.
            payload = {"command": "rm -rf src"}
            self.assertFalse(
                decide(base, session_id=_SESSION, tool_name="Bash", tool_input=payload).blocked
            )
            record_refusal(base, session_id=_SESSION, tool_name="Bash", tool_input=payload)
            self.assertEqual(self._refusals(base), [])

    def test_recording_never_changes_the_verdict(self) -> None:
        """Telemetry is fail-open; the gate is fail-closed. Never let one break the other.

        An unwritable ledger is a plumbing failure. If it could raise, the hook
        would crash and the harness would see a hook error instead of a block —
        turning a measurement improvement into a way to defeat the gate.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            # A directory where the ledger file must go: every write raises.
            (base / ".gzkit" / "ledger.jsonl").mkdir(parents=True, exist_ok=True)
            payload = {"file_path": "src/x.py", "content": "x"}
            self.assertFalse(
                record_refusal(base, session_id=_SESSION, tool_name="Write", tool_input=payload)
            )
            self.assertTrue(
                decide(base, session_id=_SESSION, tool_name="Write", tool_input=payload).blocked
            )


class ResumeGateDoesNotRevokeTheAuthorsClearanceTests(unittest.TestCase):
    """Authoring a handoff is not resuming one (GHI #755).

    Derived from the declared clause's own scope word: § RESUME gates every
    *resume*. A session that WROTE the newest handoff performed no resume, so
    the clause never reached it — yet the gate armed anyway, because it read the
    handoff's EXISTENCE as proof the session was un-cleared and never asked who
    authored it. The operator's frame: clearance is amended mid-flight, never
    revoked, "that would be Schrodinger's flight".

    No bypass is created. A session holding no clearance cannot Write, and
    `gz handoff create` is Bash outside the read allowlist — so a handoff
    carrying this session's id can only exist if the session was already
    permitted to write it.
    """

    def test_authoring_a_handoff_does_not_arm_the_gate_against_its_author(self) -> None:
        """The reported symptom: author a bookmark, then be refused a sync."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base, session_id=_SESSION)
            verdict = decide(base, session_id=_SESSION, tool_name="Write")
            self.assertFalse(verdict.blocked)

    def test_a_prior_sessions_handoff_still_arms_the_gate(self) -> None:
        """Paired block-case: the permit tracks AUTHORSHIP, not a constant."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base, session_id="session-from-a-prior-run")
            self.assertTrue(decide(base, session_id=_SESSION, tool_name="Write").blocked)

    def test_handoff_without_session_id_fails_closed(self) -> None:
        """The whole pre-existing corpus predates the field; absence must not permit."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            self.assertTrue(decide(base, session_id=_SESSION, tool_name="Write").blocked)

    def test_empty_session_id_cannot_match_an_unattributed_handoff(self) -> None:
        """Adversarial: an empty id must not equal an empty/absent frontmatter value."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base, session_id="")
            self.assertTrue(decide(base, session_id="", tool_name="Write").blocked)

    def test_mid_flight_checkpoint_does_not_revoke_an_existing_clearance(self) -> None:
        """A cleared session that bookmarks mid-flight stays cleared.

        The `gz obpi complete` completion-handoff case (GHI #619) the module's
        design notes already named — pinned so the ordering of the authorship
        and authorization checks cannot regress it.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base, name="20260716T000000Z-resumed.md")
            _authorize(base)
            _seed_handoff(base, name="20260717T000000Z-checkpoint.md", session_id=_SESSION)
            self.assertFalse(decide(base, session_id=_SESSION, tool_name="Write").blocked)


class ResumeGateNeverBlocksItsOwnRecoveryTests(unittest.TestCase):
    """A rule that blocks the command lifting it is worse than the hole it plugs."""

    def test_authorize_command_is_permitted_while_unauthorized(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            verdict = decide(
                base,
                session_id=_SESSION,
                tool_name="Bash",
                tool_input={"command": 'gz handoff authorize --handoff h.md --operator-text "go"'},
            )
            self.assertFalse(verdict.blocked, "the gate must never block its own recovery path")

    def test_uv_run_prefix_does_not_defeat_the_allowlist(self) -> None:
        """`uv run gz ...` is the canonical invocation per AGENTS.md § Execution Rules."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            verdict = decide(
                base,
                session_id=_SESSION,
                tool_name="Bash",
                tool_input={"command": "uv run gz handoff authorize --handoff h.md -o x"},
            )
            self.assertFalse(verdict.blocked)


class GitSyncIsNeverGatedOnAHandoffTests(unittest.TestCase):
    """A git-sync is ALWAYS authorized, ruled handoff or not.

    Operator canon, verbatim 2026-07-26: "a git-sync will ALWAYS be authorized -
    think about it, if we need to sync with remote, your local handoff is almost
    always likely to have been superseded by something on remote. Challenging me
    on a handoff for a git-sync is silly." The ruling was booked as handoff prose
    and mechanized by nothing, so the gate kept refusing syncs and every session
    re-litigated a closed question — reaffirmed 2026-08-09 after it blocked a
    `/git-sync` again: "handoffs should never, never, never, ever, block
    git-sync. NEVER."

    Assertions derive from that ruling, not from the implementation.

    **This class is now a REGRESSION PIN, and that is its main job** (operator
    ruling 2026-08-14, verbatim: *"I EXPLICITLY want this: 'gz git-sync is
    unconditionally permitted'"*). Since the Bash arm's removal these commands
    lift trivially — there is nothing to allowlist. That makes the assertions
    look redundant and they are not: if anyone re-introduces Bash gating, this
    is what fails first, and the paired
    `ResumeGateBlocksUnauthorizedExecutionTests.test_bash_is_not_in_the_gated_set`
    pins the set itself. The block-case pairings that used to live here
    (`gz git-sync && rm -rf docs`, `gz obpi complete`) are GONE, deliberately —
    they asserted refusals this gate no longer makes, and keeping them would
    have been asserting enforcement that does not exist.
    """

    def test_git_sync_is_permitted_while_unauthorized(self) -> None:
        """Every invocation form of the sync ceremony lifts, with no ledger ruling."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                "gz git-sync",
                "gz git-sync --apply",
                "gz git-sync --apply --lint --test",
                # `uv run` is stripped before matching, so the operator's actual
                # spelling must lift too — not just the normalized head.
                "uv run gz git-sync --apply",
            ):
                with self.subTest(command=command):
                    verdict = decide(
                        base,
                        session_id=_SESSION,
                        tool_name="Bash",
                        tool_input={"command": command},
                    )
                    self.assertFalse(
                        verdict.blocked,
                        f"{command!r} is the sync ceremony the operator ruled is never gated",
                    )


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


class ResumeGateProseTests(unittest.TestCase):
    """Block prose must satisfy `.claude/rules/guardrail-feedback-prose.md`."""

    def test_block_prose_is_three_part_and_names_the_recovery_command(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff = _seed_handoff(base)
            reason = decide(base, session_id=_SESSION, tool_name="Write").reason
            self.assertIn("BLOCKED", reason, "part 1: what failed")
            self.assertIn("gz-session-handoff", reason, "part 2: the cited rule")
            self.assertIn("gz handoff decide", reason, "part 3: a runnable next step")
            # The recovery command must be RUNNABLE, not merely named: only a
            # `proceed` decision lifts the gate (GHI #757), so prose that named
            # the verb without the flag would hand the blocked party a command
            # that books a record and leaves them still blocked.
            self.assertIn("--decision proceed", reason, "part 3 must be complete")
            self.assertIn(handoff.name, reason, "the prose names the specific handoff")

    def test_coverage_limits_are_declared(self) -> None:
        """A gate that hides what it cannot see advertises coverage it lacks."""
        self.assertTrue(UNWITNESSABLE)
        self.assertTrue(any("MCP" in limit for limit in UNWITNESSABLE))

    def test_block_prose_carries_the_session_id_for_a_runnable_recovery(self) -> None:
        """The blocked party cannot look up its own session id — so interpolate it.

        Dogfooding regression (2026-07-16): the first prose left `--session-id`
        unstated. The agent cannot read the harness session id (it lives in the
        hook payload, and the commands that would reveal it are themselves gated),
        so the "recovery command" could not be completed by the party it was
        addressed to. A recovery path the blocked party cannot run is not one.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            reason = decide(base, session_id=_SESSION, tool_name="Write").reason
            self.assertIn(f"--session-id {_SESSION}", reason)


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


class ResumeDecisionIsATransitNotAnAttestationTests(unittest.TestCase):
    """The gate books a transit decision, not a completion claim (GHI #757).

    ADR-0.33.0 § Alternatives rejects this conflation by name: *"completion-
    attestation is sacrosanct and reserved for claims about completed planned
    work; the airlock's every-transit gate is acknowledge-and-decide, a
    different sort -- conflating them would spend and cheapen the sacred word."*
    The handoff gate did exactly that, down to the event's own docstring
    claiming "the same relay model as Gate 5 attestation".

    Operator ruling (2026-08-05): keep the verbatim words, add the decision.
    The word is still recorded; what changes is that it is filed as a transit
    decision. The grammar is borrowed from `airlock.model.Decision`; the
    records stay the handoff layer's own — the two systems sit on different
    axes.
    """

    def _write_event(self, base: Path, event: dict) -> None:
        ledger = base / ".gzkit" / "ledger.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event) + "\n")

    def _decided(self, base: Path, decision: str, *, session_id: str = _SESSION) -> None:
        self._write_event(
            base,
            {
                "event": "handoff_resume_decided",
                "session_id": session_id,
                "handoff_path": "h.md",
                "operator_text": "close 757",
                "decision": decision,
            },
        )

    def test_proceed_lifts_the_gate(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._decided(base, "proceed")
            self.assertTrue(is_resume_authorized(base, _SESSION))

    def test_hold_does_not_lift_the_gate(self) -> None:
        """The capability the old shape could not express.

        `handoff_resume_authorized` was a boolean: booking it was consent, and
        there was no way to record that the operator looked and said *not yet*.
        A HOLD must leave the gate armed, or the register can only ever say yes.
        """
        for decision in ("hold", "pause", "revert"):
            with self.subTest(decision=decision), TemporaryDirectory() as tmp:
                base = Path(tmp)
                self._decided(base, decision)
                self.assertFalse(
                    is_resume_authorized(base, _SESSION),
                    f"{decision!r} is a ruling to NOT proceed; it must not lift the gate",
                )

    def test_the_legacy_authorized_event_still_lifts_the_gate(self) -> None:
        """Back-compat is load-bearing, not courtesy.

        Every authorization booked before this change is a
        `handoff_resume_authorized` event. A gate that stopped reading them
        would retroactively un-authorize the entire committed ledger.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _authorize(base)
            self.assertTrue(is_resume_authorized(base, _SESSION))

    def test_a_decision_for_another_session_does_not_lift_this_one(self) -> None:
        """Session scoping survives the new event shape (GHI #574's obligation)."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._decided(base, "proceed", session_id="some-other-session")
            self.assertFalse(is_resume_authorized(base, _SESSION))

    def test_an_unknown_decision_token_fails_closed(self) -> None:
        """A malformed or future token is not consent.

        The gate reads raw JSONL, so nothing upstream guarantees the token is
        in the enum. Anything that is not exactly PROCEED leaves the gate armed.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            self._decided(base, "PROCEED-ish")
            self.assertFalse(is_resume_authorized(base, _SESSION))


if __name__ == "__main__":
    unittest.main()
