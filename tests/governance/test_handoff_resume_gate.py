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
    _refused_segments,
    _segments,
    decide,
    is_resume_authorized,
    newest_handoff,
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
        for rule_claim in (
            "handoff-resume-unauthorized-write",
            "handoff-resume-unauthorized-bash",
        ):
            self.assertEqual(declared.get(rule_claim), RESUME_GATE_COUPLING_CLAIM_ID)
        self.assertIn(RESUME_GATE_COUPLING_CLAIM_ID, declared)

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
        """The contract says 'no file mutation', not 'no Write'.

        A Write|Edit-only gate would enforce one third of the declared clause —
        `gz` ceremony and migration both run through Bash.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for tool in sorted(MUTATING_TOOLS):
                tool_input = {"command": "rm -rf src"} if tool == "Bash" else {}
                with self.subTest(tool=tool):
                    verdict = decide(
                        base, session_id=_SESSION, tool_name=tool, tool_input=tool_input
                    )
                    self.assertTrue(verdict.blocked, f"{tool} must be gated")

    def test_bash_is_in_the_gated_set(self) -> None:
        """Pin the clause that was nearly scoped out for being harder to hook."""
        self.assertIn("Bash", MUTATING_TOOLS)

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

    def test_compound_command_cannot_ride_in_on_an_allowlisted_prefix(self) -> None:
        """`gz state && rm -rf x` is not a read of gz state."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                "gz state && rm -rf src",
                "gz state; rm -rf src",
                "gz state | tee /tmp/x",
                "gz state > out.txt",
                "echo $(rm -rf src)",
                "gz state `rm -rf src`",
            ):
                with self.subTest(command=command):
                    verdict = decide(
                        base,
                        session_id=_SESSION,
                        tool_name="Bash",
                        tool_input={"command": command},
                    )
                    self.assertTrue(verdict.blocked, f"{command!r} must not pass as read-only")

    def test_command_substitution_is_blocked_regardless_of_quoting(self) -> None:
        """`$(...)` and backticks are refused in EVERY quoting form — deliberately.

        Paired with `test_quoted_metacharacters_are_not_compound_operators`: quote
        awareness must not decay into "anything quoted is a read". Two facts force
        the conservative line, both observed against the real lexer:

        * Double quotes do NOT make substitution inert — bash expands
          `"$(rm -rf x)"` and ``"`rm -rf x`"`` exactly as it would bare.
        * `shlex` in posix mode (required, so that a quote opening mid-token like
          `--grep='^fix('` parses at all) STRIPS quotes, so the single- and
          double-quoted forms are indistinguishable by the time we see tokens.

        Given that ambiguity the gate refuses both. The cost is a false refusal on
        a literal `$(`-in-a-search-pattern — which no claim verification needs. A
        false PERMIT on a live subshell is the strictly worse trade.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                'grep "$(rm -rf src)" f',
                "grep '$(rm -rf src)' f",
                'grep "`rm -rf src`" f',
                "gz state `rm -rf src`",
            ):
                with self.subTest(command=command):
                    verdict = decide(
                        base,
                        session_id=_SESSION,
                        tool_name="Bash",
                        tool_input={"command": command},
                    )
                    self.assertTrue(verdict.blocked, f"{command!r} can spawn a subshell")

    def test_unparseable_command_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            verdict = decide(
                base, session_id=_SESSION, tool_name="Bash", tool_input={"command": 'gz state "'}
            )
            self.assertTrue(verdict.blocked)

    def test_abandoned_register_entry_does_not_arm_the_gate(self) -> None:
        """Abandoned entries are a surrendered token, not context to resume."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base, name="20260716T000000Z-OBPI-x-abandoned.md", abandoned=True)
            self.assertIsNone(newest_handoff(base))
            self.assertFalse(decide(base, session_id=_SESSION, tool_name="Write").blocked)


class ResumeGateAdmitsAWhollyAdmittedCompoundTests(unittest.TestCase):
    """A chain whose EVERY segment is admitted is a read, not a shape to refuse.

    Operator ruling 2026-08-13 (GHI #800), reversing the 2026-08-12 disposition-1
    ruling that `_is_compound`'s docstring had recorded as "RULED CORRECT AS
    DESIGNED". Verbatim: "I want this fixed now, highest priority, I can't
    tolerate this". The refusal's cost was not abstract — the block prose listed
    the very segments it refused back to the caller as "permitted RIGHT NOW",
    so the gate spent its own recovery text proving it had the information to
    admit and declined to use it.

    The disposition-1 rationale claimed narrowing "would reopen both holes" named
    by the two lexer facts. It does not, and GHI #800's own body says so: admission
    is computed by re-running the REAL predicates per segment, and
    `_bash_is_read_only` calls `_is_compound` internally. So substitution is caught
    by `_can_expand` INSIDE each segment's check, and a redirect refuses because
    its target (`out.txt`) is a segment matching no allowlisted head — never
    because of the operator token. `test_one_unadmitted_segment_refuses_the_whole_command`
    is the paired negative that keeps this honest, per this module's docstring.
    """

    def _verdict(self, base: Path, command: str):
        return decide(base, session_id=_SESSION, tool_name="Bash", tool_input={"command": command})

    def test_a_chain_of_admitted_reads_is_permitted(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                # The 2026-08-13 refusal, verbatim from the operator's report.
                'git log --oneline -12 && echo "---STATUS---" && git status --short',
                # GHI #800's own canonical example. Its `uv run gz git-sync`
                # segment is admitted UNCONDITIONALLY by `_ALWAYS_AUTHORIZED_BASH`,
                # so refusing this chain also refused the standing operator ruling
                # that a git-sync is "never, never, never, ever" gated.
                'git status --short && echo "---" && uv run gz git-sync',
                "ls && git log",
                "git status; git diff",
            ):
                with self.subTest(command=command):
                    self.assertFalse(self._verdict(base, command).blocked, command)

    def test_one_unadmitted_segment_refuses_the_whole_command(self) -> None:
        """Admission is unanimous or it is nothing.

        The redirect and pipe cases are the load-bearing ones: they now refuse
        because the redirect TARGET and the filter are segments matching no
        allowlisted head, not because an operator token was seen. That is the
        same verdict by a different route, which is why it needs its own witness.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                "git status --short && rm -rf src",
                "ls && git log && sed -i s/a/b/ f",
                # Redirect: `out.txt` is a segment, and it is not admitted.
                "git log --oneline && git status > out.txt",
                # Pipe: `tee` is not an admitted verb.
                "git status && git log | tee /tmp/x",
                # Substitution inside an otherwise wholly-admitted chain.
                "git status && echo `rm -rf src`",
                'git status && echo "$(rm -rf src)"',
            ):
                with self.subTest(command=command):
                    self.assertTrue(self._verdict(base, command).blocked, command)


class ResumeGateReadsFdDuplicationAsNotARedirectTests(unittest.TestCase):
    """`2>&1` duplicates a descriptor; it names no file and writes nothing.

    Operator report 2026-08-14, verbatim: "once again this bullshit", quoting a
    refusal of `uv run gz adr status <ADR> 2>&1 | head -60` — a read of a read
    verb. The gate answered by naming `1` as the unadmitted part, which is not a
    command the caller wrote: `shlex` with `punctuation_chars` lexes `2>&1` as
    `['2', '>', '&1']`, `_is_shell_operator` accepts the bare `>`, and
    `_segments` derives its separators from that character shape — so the
    duplication's target became a phantom segment matching no allowlisted head.

    This was a KNOWN state, not an oversight, and that is the defect worth
    naming. `_compound_is_wholly_admitted`'s docstring carried it under "Still
    refused, deliberately: ... and `2>&1` -- whose `1` is a segment matching no
    head", filed beside the genuine redirect case on the strength of a shared
    `>` character. The two are not the same question: a redirect takes a FILE
    operand and its target is unmodelled (correctly still refused, per the
    paired negative below), while a duplication takes a DESCRIPTOR and can
    create no file under any target model. Grouping them made an lexer artifact
    read as a policy.

    Reading combined output is how an agent verifies before it is authorized to
    act, so refusing it taxes exactly the pre-ruling verification the resume
    gate's own recovery prose demands.
    """

    def _verdict(self, base: Path, command: str):
        return decide(base, session_id=_SESSION, tool_name="Bash", tool_input={"command": command})

    def test_fd_duplication_does_not_refuse_an_otherwise_admitted_read(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                # The 2026-08-14 refusal, verbatim from the operator's report.
                "uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing 2>&1 | head -60",
                # Duplication with no pipe at all — refused on shape alone before.
                "git status --short 2>&1",
                # The reverse direction, and the target-only form.
                "git log --oneline 1>&2",
                "git status >&2",
            ):
                with self.subTest(command=command):
                    self.assertFalse(self._verdict(base, command).blocked, command)

    def test_input_redirection_is_admitted_because_no_form_of_it_writes(self) -> None:
        """`< path` is the duplication's sibling, found by asking for the class.

        The reported instance was `2>&1`. Fixing only it would have left the
        other operator that cannot write still refusing reads — the shape
        AGENTS.md § DO IT RIGHT #1 names, where the instance is patched and the
        family is not. `<<` and `<<<` are deliberately excluded: they are
        distinct tokens whose body is not in this command string.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            self.assertFalse(self._verdict(base, "grep -c foo < README.md").blocked)
            self.assertTrue(self._verdict(base, "cat <<EOF").blocked)

    def test_a_real_redirect_is_still_refused_alongside_a_duplication(self) -> None:
        """The paired negative: dropping `2>&1` must not drop the file write.

        `git log 2>&1 > out.txt` carries both forms. Reading the duplication
        correctly is worthless if it also swallows the `> out.txt` that follows
        it — the failure mode a token-dropping fix invites, and the reason this
        witness sits next to the positive rather than trusting it.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                "git log --oneline 2>&1 > out.txt",
                "git status 2>&1 && rm -rf src",
                "git status 2>&1 | tee /tmp/x",
                # `>&` with a FILE target is csh-style both-streams redirection,
                # a genuine write sharing the duplication's operator token. The
                # digit target is the discriminator, not the operator.
                "git status >& out.txt",
            ):
                with self.subTest(command=command):
                    self.assertTrue(self._verdict(base, command).blocked, command)


class ResumeGateNamesACommandTheCallerWroteTests(unittest.TestCase):
    """A refusal must point at a command, never at a redirection's operand.

    This is the CAUSE the `2>&1` fix reached only one instance of. `_segments`
    derived its separator set by character shape — anything built from `;|&<>()`
    — so a redirection operator split a command from its own OPERAND, and the
    gate then reported the operand as the part that was not admitted. `2>&1`
    made it a wrong verdict; `> out.txt` keeps the right verdict and names a
    FILENAME as an unadmitted command, which is the same incoherence surviving
    in the prose.

    Verdicts are deliberately unchanged here: a redirect still refuses, now from
    inside its segment via `_is_compound`. Only the part named back to the
    caller changes, which is why this needs a witness of its own — nothing in
    the blocked/not-blocked assertions elsewhere can see it.
    """

    def test_a_refused_redirect_names_the_command_not_the_filename(self) -> None:
        for command, operand in (
            ("git log --oneline > out.txt", "out.txt"),
            ("git status >& dump.log", "dump.log"),
        ):
            with self.subTest(command=command):
                self.assertEqual(_segments(command), [command])
                self.assertNotIn(operand, _refused_segments(command))
                self.assertEqual(_refused_segments(command), [command])


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


class ResumeGatePermitsTheMandatedVerificationTests(unittest.TestCase):
    """§ Trust Model requires reading Layer-2 BEFORE presenting to the operator.

    Blocking these would make the skill's own Claim Verification Gate
    unexecutable — the agent could not verify the handoff's claims in order to
    present them, so it could never reach the ruling that lifts the gate.
    """

    def test_declared_layer2_read_surfaces_are_permitted(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                "gz obpi status",
                "gz obpi lock list",
                "gz gates",
                "gz state",
                "gz handoff list",
                "gz handoff resume --adr ADR-0.0.65",
            ):
                with self.subTest(command=command):
                    verdict = decide(
                        base,
                        session_id=_SESSION,
                        tool_name="Bash",
                        tool_input={"command": command},
                    )
                    self.assertFalse(verdict.blocked, f"{command!r} is a declared RESUME read")

    def test_github_issue_state_reads_are_permitted(self) -> None:
        """A GHI-state claim is verifiable through `gh` and nothing else.

        The § Claim Verification Gate mandates verifying EVERY completion claim a
        handoff makes before presenting it. Handoffs routinely claim "GHI #N
        CLOSED" and advise "rule on GHI #M" as a next step — claims whose only
        Layer-2 surface is GitHub. The first allowlist was derived from the
        § Trust Model's four example `gz` verbs rather than from that obligation,
        so `gh` was refused and those claims were structurally unverifiable
        (operator ruling, 2026-07-17: "this is essential").
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                "gh issue view 693",
                "gh issue view 693 --json state,title",
                "gh issue list --state open --limit 200",
                "gh pr view 42",
                "gh pr list",
                "gh pr diff 42",
                # The jq filter's `|` is single-quoted: inert, and the canonical
                # form of the very query that verifies a batch of GHI claims.
                "gh issue list --json number,state -q '.[] | select(.state == \"OPEN\")'",
            ):
                with self.subTest(command=command):
                    verdict = decide(
                        base,
                        session_id=_SESSION,
                        tool_name="Bash",
                        tool_input={"command": command},
                    )
                    self.assertFalse(verdict.blocked, f"{command!r} is a GHI-state read")

    def test_github_mutating_verbs_are_still_blocked(self) -> None:
        """Paired with the read case: `gh` is admitted as a READ surface only.

        `gh issue create` is independently forbidden by AGENTS.md § Behavior Rules
        — Always #13 (author GHIs through `/ghi-author`, never `gh` directly), so
        an allowlist that admitted it would put the gate in conflict with the
        contract it serves.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                "gh issue create --title x --body y",
                "gh issue close 693",
                "gh issue comment 693 --body x",
                "gh issue edit 693 --add-label x",
                "gh pr merge 42",
                "gh pr create --fill",
                "gh release create v1.0.0",
                # `gh api` is write-capable via `-X POST`; it is not an admitted head.
                "gh api -X POST /repos/x/y/issues",
            ):
                with self.subTest(command=command):
                    verdict = decide(
                        base,
                        session_id=_SESSION,
                        tool_name="Bash",
                        tool_input={"command": command},
                    )
                    self.assertTrue(verdict.blocked, f"{command!r} is not a read")

    def test_a_gz_ceremony_verb_is_still_blocked(self) -> None:
        """The allowlist is reads only — `gz` ceremony is named in the contract.

        `gz git-sync` used to be asserted here and is deliberately gone: it is
        the one ceremony the operator ruled is NEVER gated on a handoff, proven
        by `GitSyncIsNeverGatedOnAHandoffTests`. The two verbs left are ordinary
        ceremony and stay blocked, so this case still discriminates.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in ("gz obpi complete OBPI-x", "gz adr promote x"):
                with self.subTest(command=command):
                    verdict = decide(
                        base,
                        session_id=_SESSION,
                        tool_name="Bash",
                        tool_input={"command": command},
                    )
                    self.assertTrue(verdict.blocked, f"{command!r} is ceremony, not a read")


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

    Assertions derive from that ruling, not from the implementation. The permit
    cases are paired with block cases below so an always-allow implementation
    cannot false-pass them.
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

    def test_the_exemption_does_not_generalize_to_other_ceremony(self) -> None:
        """Scoped to the sync verb — a blanket ceremony permit would gut the gate."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in ("gz obpi complete OBPI-x", "gz adr promote x", "gz attest"):
                with self.subTest(command=command):
                    verdict = decide(
                        base,
                        session_id=_SESSION,
                        tool_name="Bash",
                        tool_input={"command": command},
                    )
                    self.assertTrue(verdict.blocked, f"{command!r} is ordinary ceremony")

    def test_nothing_rides_in_chained_onto_a_sync(self) -> None:
        """The ruling covers the sync, not whatever is chained onto its prefix."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                "gz git-sync --apply && rm -rf docs",
                "gz git-sync; gz obpi complete OBPI-x",
                "gz git-sync --apply | tee out.log",
            ):
                with self.subTest(command=command):
                    verdict = decide(
                        base,
                        session_id=_SESSION,
                        tool_name="Bash",
                        tool_input={"command": command},
                    )
                    self.assertTrue(verdict.blocked, f"{command!r} is compound")


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

    def test_block_prose_names_the_refused_part_of_a_mixed_command(self) -> None:
        """A mixed chain must name WHICH part refused, not just that one did.

        Dogfooding regression (2026-08-12): a session opened a resume with
        `git status --short && uv run gz git-sync`. Both halves are admitted —
        the first by `_PERMITTED_BASH`, the second unconditionally by
        `_ALWAYS_AUTHORIZED_BASH` — and the refusal came entirely from the `&&`.
        Every reason the prose then gave was about the operator not having ruled,
        so the session concluded the standing "never gate a git-sync" ruling had
        regressed and asked the operator to re-fix a defect that had landed three
        days earlier. **That exact command is now permitted outright** (GHI #800,
        operator ruling 2026-08-13), which is the stronger fix; what survives here
        is the residual case the note still owns — a genuinely MIXED command.

        The refused segment is the one fact the caller cannot derive: it can see
        its own command, but not the allowlist that judged it.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            reason = decide(
                base,
                session_id=_SESSION,
                tool_name="Bash",
                tool_input={"command": "git status --short && rm -rf build && uv run gz git-sync"},
            ).reason
            self.assertIn("rm -rf build", reason, "the prose must name what refused")
            # The admitted parts are quoted back so the caller can reissue them
            # without re-deriving the allowlist it cannot read.
            self.assertIn("git status --short", reason)
            self.assertIn("uv run gz git-sync", reason)

    def test_mixed_note_is_withheld_when_no_part_would_be_admitted(self) -> None:
        """The note is driven by the predicates, not printed for every compound.

        Without this, "these parts are permitted RIGHT NOW" would be printed over
        a chained `rm -rf` — false, and an invitation to reissue it bare.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            reason = decide(
                base,
                session_id=_SESSION,
                tool_name="Bash",
                tool_input={"command": "rm -rf build && chmod 777 dist"},
            ).reason
            self.assertNotIn("permitted RIGHT NOW", reason)
            self.assertNotIn("mixed admitted and unadmitted", reason)
            self.assertIn("BLOCKED", reason, "the ordinary refusal still stands")


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


class ResumeGatePermitsPlainShellReadsTests(unittest.TestCase):
    """The § Claim Verification Gate's real instrument when no Grep/Glob tool exists.

    Dogfooding regression (2026-07-16): the first allowlist permitted only `gz`
    verbs, on the false premise that "Read/Grep/Glob are never gated, so Bash is
    not the read path". In the harness this skill runs in, Grep/Glob may be
    absent — making Bash `grep`/`cat`/`git log` the ONLY way to satisfy the
    verification this same skill MANDATES before presenting. A gate that forbids
    the verification its own skill requires cannot be complied with.
    """

    def _verdict(self, base: Path, command: str):
        return decide(base, session_id=_SESSION, tool_name="Bash", tool_input={"command": command})

    def test_plain_reads_are_permitted(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                "git status -sb",
                "git log --oneline -5",
                "grep -rn pattern src/",
                "rg pattern",
                "cat src/gzkit/handoff_api.py",
                "ls -la",
                "head -20 file.md",
            ):
                with self.subTest(command=command):
                    self.assertFalse(self._verdict(base, command).blocked, command)

    def test_quoted_metacharacters_are_not_compound_operators(self) -> None:
        """A `|` inside a quoted search pattern is data, not a pipe.

        Dogfooding regression (2026-07-17): compound detection ran a regex over the
        RAW command string before any tokenization, so `grep -n "A\\|B" file` — an
        alternation pattern, the most ordinary instrument the § Claim Verification
        Gate has — was refused as a compound command. Three of the first four
        verification calls of a resume died on it. A gate whose read path forbids
        ordinary reads gets worked around; `shlex` was already imported one
        function away and knows quoting.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                'grep -n "READ_ONLY\\|ALLOW\\|MUTATING" src/gzkit/handoff_resume_gate.py',
                "grep -rn 'a|b' src/",
                'rg "foo|bar" src/',
                'git log --grep="^fix(\\|^feat(" --oneline',
                # AGENTS.md § Defect-fix routing MANDATES running exactly this to
                # compute the precedent count. A gate that refuses it puts the
                # agent in an unsatisfiable position between two binding rules.
                "git log --since='60 days ago' --oneline --grep='^fix('",
                # The canonical batch GHI-state query: `|` inside a jq filter.
                "gh issue list --json number,state -q '.[] | select(.state == \"OPEN\")'",
            ):
                with self.subTest(command=command):
                    self.assertFalse(self._verdict(base, command).blocked, command)

    def test_write_capable_flags_defeat_the_read_allowlist(self) -> None:
        """An allowlisted head does not license a mutation wearing a read's name."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in ("find . -delete", "find . -exec rm {} ;", "grep x y --fix"):
                with self.subTest(command=command):
                    self.assertTrue(self._verdict(base, command).blocked, command)

    def test_case_insensitive_search_is_a_read(self) -> None:
        """`-i` is a write flag only for verbs this gate already excludes.

        Dogfooding regression (2026-08-08): `grep -rn -i "skill" <file>` was
        refused mid-resume while the identical grep without `-i` was permitted.
        `_MUTATING_FLAGS` carried `-i` for its `sed`/`perl` in-place meaning —
        but the membership predicate (read-only BY CONSTRUCTION) already excludes
        every verb for which `-i` means in-place, and `sed -i` is refused at the
        HEAD, never at the flag. What remained was a guard that could not reach
        the verbs it was written for while blocking the two admitted verbs where
        `-i` means case-insensitive.

        This is the `find` over-grant mirrored: there, the guard was trusted to
        cover a verb whose writes it could not see; here, it fired for a verb
        that was not there. Both are the flag set being read as the predicate.

        The guard's own docstring states the premise this test pins — "every verb
        in `_PERMITTED_BASH` is read-only by construction, so nothing admitted can
        legally carry one of these". A flag that an admitted verb DOES legally
        carry falsifies that premise and does not belong in the set.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                'grep -rn -i "skill" docs/governance/advisory-rules-audit.md',
                "grep -i pattern file",
                "rg -i foo src/",
                "git log -i --grep='^fix('",
            ):
                with self.subTest(command=command):
                    self.assertFalse(
                        self._verdict(base, command).blocked,
                        f"{command!r} is a case-insensitive READ and must be permitted",
                    )

    def test_in_place_edit_stays_blocked_at_the_head(self) -> None:
        """Removing `-i` from the flag guard does not admit any in-place editor.

        The companion to `test_case_insensitive_search_is_a_read`: it would be a
        real weakening if `-i`'s removal let an in-place edit through. It cannot,
        because every verb that HAS an in-place form fails the membership
        predicate first — the flag guard was never what stopped them.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in ("sed -i s/a/b/ f", "perl -i -pe s/a/b/ f", "ruff check . --fix"):
                with self.subTest(command=command):
                    self.assertTrue(
                        self._verdict(base, command).blocked,
                        f"{command!r} edits in place and must stay blocked",
                    )

    def test_branch_sync_claims_are_verifiable(self) -> None:
        """An "origin/main in sync" claim needs a counting instrument.

        Dogfooding regression (2026-08-02): a handoff asserted "origin/main in
        sync" and prescribed `git rev-list --left-right --count
        origin/main...HEAD` in its OWN Verification Checklist — and the gate
        refused it. `rev-parse` was allowlisted; `rev-list`, the only verb that
        counts ahead/behind, was not. Third instance of the same root: the
        allowlist was derived from example commands rather than from the
        § Claim Verification Gate's obligation to verify EVERY readiness claim.

        Read-only by construction — `rev-list` has no write form.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                "git rev-list --left-right --count origin/main...HEAD",
                "git rev-list --count HEAD",
            ):
                with self.subTest(command=command):
                    self.assertFalse(self._verdict(base, command).blocked, command)

    def test_read_only_git_plumbing_is_permitted(self) -> None:
        """The whole read-only git family, not one verb at a time.

        GHI #732 named the CLASS — "read-only git plumbing/porcelain verbs absent
        from an allowlist that advertises 'git reads' generically ... The instance
        is `rev-list`; the class is enumerate-the-examples scoping" — and listed
        these six. The rev-list fix took the instance, so the class stayed open and
        would have produced a fourth narrow miss.

        Every verb here is read-only BY CONSTRUCTION: none has a write form. That
        is the membership predicate, and it is what makes the set closable rather
        than extendable-on-demand.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                "git blame src/gzkit/handoff_resume_gate.py",
                "git shortlog -sn",
                "git describe --tags",
                "git merge-base origin/main HEAD",
                "git cat-file -p HEAD",
                "git for-each-ref refs/heads",
            ):
                with self.subTest(command=command):
                    self.assertFalse(self._verdict(base, command).blocked, command)

    def test_plain_mutators_remain_blocked(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in ("rm -rf src", "mv a b", "sed -i s/a/b/ f", "git commit -m x"):
                with self.subTest(command=command):
                    self.assertTrue(self._verdict(base, command).blocked, command)

    def test_a_plain_verb_with_any_write_form_is_refused(self) -> None:
        """The plain-shell arm is closed by the SAME predicate as the git arm.

        GHI #732 reopened for a fourth miss: the git arm got a stated membership
        predicate ("read-only by construction") while the plain-shell arm stayed a
        bare enumeration, so judging a candidate meant asking "is it in the list?"
        — answerable only by discovering a miss.

        The reopened issue proposed a WEAKER predicate for this arm — admit a
        write-capable verb when "every write-enabling flag is in `_MUTATING_FLAGS`"
        — on the premise that `find`'s admission proved the flag guard was the
        intended pattern. Probing the real tools disproved the premise: a verb's
        write surface is not reachable only through flags.

        * `find . -fprint FILE` / `-fls` / `-fprintf` write via unguarded PRIMITIVES,
          not flags. Observed writing a file 2026-08-05 while this gate permitted it.
        * `sed -n '1,2w FILE'` and `sed -n 's/a/z/w FILE'` write via a command INSIDE
          the script operand, where no flag set can see it. `-i` is not sed's only
          write form, only its most famous one.

        So `find`'s grant was the hole, not the precedent — and one predicate governs
        both arms: a verb is admitted only when it has NO write form at all. Flags are
        defense-in-depth beneath that, never a substitute for it.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                # find: write primitives that `_MUTATING_FLAGS` never enumerated.
                "find . -fprint /tmp/out",
                "find . -fls /tmp/out",
                "find . -fprintf /tmp/out %p",
                "find . -name x -delete",
                # sed: in-script writes, invisible to any flag guard.
                "sed -n '1,2w /tmp/out' f",
                "sed -n 's/a/z/w /tmp/out' f",
                "sed -i s/a/b/ f",
                # The rest of the family the predicate excludes, each for a stated
                # reason: in-program redirect, a write flag that collides with an
                # admitted verb's read syntax, a positional output operand, writing
                # by definition, and arbitrary-command execution.
                "awk '{print > \"/tmp/out\"}' f",
                "sort -o /tmp/out f",
                "uniq f /tmp/out",
                "tee /tmp/out",
                "env rm -rf src",
                "xargs rm",
            ):
                with self.subTest(command=command):
                    self.assertTrue(
                        self._verdict(base, command).blocked,
                        f"{command!r} has a write form and must not be admitted",
                    )

    def test_read_only_by_construction_plain_verbs_stay_permitted(self) -> None:
        """Closing the predicate must not cost the reads the Gate actually mandates.

        These have no write form in any flag or script combination, so the same
        predicate that excludes `find`/`sed` admits every one of them. `rg --files`
        and `git ls-files` are the file-location instruments that make `find`'s
        removal a no-op for the § Claim Verification Gate's obligation.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in (
                "rg --files src/",
                "git ls-files src/gzkit",
                "wc -l src/gzkit/handoff_resume_gate.py",
                "tail -40 .gzkit/ledger.jsonl",
                "jq .event .gzkit/ledger.jsonl",
                "pwd",
            ):
                with self.subTest(command=command):
                    self.assertFalse(self._verdict(base, command).blocked, command)

    def test_a_readiness_read_is_admitted_but_its_ceremony_successor_is_not(self) -> None:
        """`gz gates` is a readiness READ; `gz closeout` writes in its bare form.

        Recorded on GHI #732 by the #743 control-surface audit as an over-grant /
        under-grant pair: the allowlist admits `gz gates` (deprecated under #705,
        successor `gz closeout`) while refusing the successor. Re-derived here rather
        than inherited — the pair is CORRECT under the obligation predicate, and the
        reason has to be recorded or the next audit re-files it.

        Deprecation governs what docs may PRESCRIBE, not what this gate may READ:
        `gz gates` still runs and still answers a gate-status claim. `gz closeout`
        is ceremony — only `--dry-run` is a read, and `_PERMITTED_BASH` matches
        LEADING tokens, so admitting the head would license the write form. Its
        dry-run is an advised step requiring authorization, not a claim-verification
        read; `gz status` answers the claim.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            self.assertFalse(self._verdict(base, "gz gates").blocked, "gz gates is a read")
            for command in ("gz closeout ADR-0.0.1", "gz closeout ADR-0.0.1 --dry-run"):
                with self.subTest(command=command):
                    self.assertTrue(self._verdict(base, command).blocked, command)


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
