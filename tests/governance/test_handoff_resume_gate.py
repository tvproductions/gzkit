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
)

_SESSION = "session-abc123"


def _seed_handoff(
    base: Path,
    name: str = "20260716T000000Z-work.md",
    *,
    abandoned: bool = False,
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
        "timestamp: '2026-07-16T00:00:00Z'",
        "agent: g0",
    ]
    if abandoned:
        lines.append("abandoned: true")
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
        """The allowlist is reads only — `gz` ceremony is named in the contract."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _seed_handoff(base)
            for command in ("gz obpi complete OBPI-x", "gz git-sync --apply", "gz adr promote x"):
                with self.subTest(command=command):
                    verdict = decide(
                        base,
                        session_id=_SESSION,
                        tool_name="Bash",
                        tool_input={"command": command},
                    )
                    self.assertTrue(verdict.blocked, f"{command!r} is ceremony, not a read")


class ResumeGateProseTests(unittest.TestCase):
    """Block prose must satisfy `.claude/rules/guardrail-feedback-prose.md`."""

    def test_block_prose_is_three_part_and_names_the_recovery_command(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff = _seed_handoff(base)
            reason = decide(base, session_id=_SESSION, tool_name="Write").reason
            self.assertIn("BLOCKED", reason, "part 1: what failed")
            self.assertIn("gz-session-handoff", reason, "part 2: the cited rule")
            self.assertIn("gz handoff authorize", reason, "part 3: a runnable next step")
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


if __name__ == "__main__":
    unittest.main()
