"""Verification exit-code integrity gate — the clause's teeth (GHI #589).

`.gzkit/rules/tests.md` § Verification exit-code integrity binds:

    "A verifier's truth is its own exit code, never a downstream filter's.
    NEVER pipe `unittest`/`behave`/`mkdocs --strict` (or any ARB-wrapped
    verifier) through `tail`/`head`/`grep`/`Select-Object`: the shell reports
    the *last* process's exit (the filter's — always 0), masking a failing
    suite as a green run."

These assertions derive from that clause, not from a run of the implementation.
The discriminating question for each (`.gzkit/rules/tests.md` § The discriminator):
*if the masking rule changed but the code text did not, would this test fail?*
Each case below names a distinct way a verifier's exit status can or cannot be
masked, so a gate that stopped tracking masking fails here rather than passing
on shape.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.arb.validator import CANONICAL_STEP_COMMANDS
from gzkit.verifier_pipe_gate import decide, masked_verifier, masked_verifier_reason


class TestMaskedVerifierDetection(unittest.TestCase):
    """The predicate: does this command send a verifier's exit status to /dev/null?"""

    def test_the_three_filters_the_clause_names_are_refused(self) -> None:
        """`tail`/`head`/`grep` are the clause's verbatim instances."""
        for filter_cmd in ("tail -5", "head -20", "grep FAIL"):
            with self.subTest(filter=filter_cmd):
                command = f"uv run -m unittest -q | {filter_cmd}"
                self.assertEqual(masked_verifier(command), "unittest")

    def test_masking_is_the_pipe_not_the_filter_identity(self) -> None:
        """The class fix: ANY downstream process masks, not just the three named.

        The shell reports the LAST process's exit regardless of what that
        process is, so a gate keyed to a filter allowlist would pass
        `gz check | cat` — the identical defect wearing a different name.
        """
        for downstream in ("cat", "wc -l", "sort", "tee out.log", "jq .", "less"):
            with self.subTest(downstream=downstream):
                command = f"uv run gz check | {downstream}"
                self.assertEqual(masked_verifier(command), "gz check")

    def test_the_clause_prescribed_redirect_form_is_permitted(self) -> None:
        """Capture-to-file is what the clause tells the agent to do instead."""
        self.assertIsNone(masked_verifier("uv run gz check > check.log 2>&1"))

    def test_a_bare_verifier_is_permitted(self) -> None:
        self.assertIsNone(masked_verifier("uv run -m unittest -q"))

    def test_a_non_verifier_piped_into_a_filter_is_permitted(self) -> None:
        """`gz state | grep x` masks nothing anyone attests on."""
        self.assertIsNone(masked_verifier("uv run gz state | grep ADR-0.35.0"))
        self.assertIsNone(masked_verifier("git log --oneline | head -20"))

    def test_a_verifier_in_the_final_segment_is_permitted(self) -> None:
        """The last process's exit IS the command's exit — nothing is masked."""
        self.assertIsNone(masked_verifier("cat manifest.txt | uv run gz validate --documents"))

    def test_a_quoted_pipe_is_data_not_an_operator(self) -> None:
        """Quote-awareness: `shlex` knows `"a|b"` is an argument, a regex does not."""
        self.assertIsNone(masked_verifier('uv run gz check --filter "unit|integration"'))

    def test_logical_or_is_not_a_pipe(self) -> None:
        """AMENDED under GHI #970. `||` is not a PIPE; it does not preserve the status.

        The half that was right is kept: `||` is a control operator, so the PIPE
        arm must not claim it. The premise appended to it — "the verifier's exit
        survives" — was the defect. A `||` branch runs only on failure and then
        REPLACES the failing status with its own, so the aggregate is 0 exactly
        when the verifier failed.
        """
        self.assertEqual(
            masked_verifier_reason("uv run gz check || echo FAILED"),
            ("gz check", "or-else"),
        )

    def test_a_later_pipeline_does_not_taint_the_verifier_but_the_sequence_masks_it(
        self,
    ) -> None:
        """AMENDED under GHI #940. `;` ends the PIPELINE; it does not preserve the status.

        This assertion previously read `assertIsNone` on the premise that "`gz
        check; ls | head` masks nothing" — the module comment GHI #940 quotes as
        the defect itself. The premise is half right and was applied whole: the
        later pipe is genuinely unrelated to the verifier, so ARM 1 must stay
        silent about it. But the shell reports the LAST statement's status, so
        `ls | head` overwrites the verifier's exit just as a pipe would.

        What is pinned here is that the refusal comes from the SEQUENCE arm and
        names the verifier — not that the later pipeline tainted it.
        """
        self.assertEqual(masked_verifier("uv run gz check; ls | head -3"), "gz check")
        # Same statement shape, verifier last: nothing overwrites its status.
        self.assertIsNone(masked_verifier("ls | head -3; uv run gz check"))


class TestExitPreservingEscapes(unittest.TestCase):
    """Two shell constructs genuinely preserve the verifier's exit through a pipe."""

    def test_pipefail_permits_the_pipeline(self) -> None:
        """With `pipefail` the shell reports the first failing stage, not the last."""
        command = "set -o pipefail; uv run -m unittest -q | tail -5"
        self.assertIsNone(masked_verifier(command))

    def test_pipestatus_permits_the_pipeline(self) -> None:
        """Reading `PIPESTATUS[0]` is the clause's own named remedy."""
        command = 'uv run -m unittest -q | tail -5; echo "REAL EXIT: ${PIPESTATUS[0]}"'
        self.assertIsNone(masked_verifier(command))

    def test_set_with_combined_flags_still_sets_pipefail(self) -> None:
        """`set -euo pipefail` is the common spelling and must keep working."""
        command = "set -euo pipefail; uv run -m unittest -q | tail -5"
        self.assertIsNone(masked_verifier(command))


class TestEscapesMustBeUsedNotNamedTests(unittest.TestCase):
    """An escape is honored when USED, never when merely mentioned (GHI #796).

    The module states the principle these assert (`verifier_pipe_gate.py`
    § Design notes): *"A verifier is what a segment RUNS, not a name that
    appears in it. A substring or token-presence check would refuse
    `grep -rn "unittest" src/`, which mentions a verifier and runs none."*

    That standard was applied to the REFUSE half and not to the EXCUSE half,
    so the fail-open direction was the lexical one. These derive from the
    module's own claim that the two escapes are *"explicit operator opt-ins"* —
    a word inside a grep pattern opts in to nothing.
    """

    def test_grepping_for_the_word_does_not_disarm_the_gate(self) -> None:
        """Searching the docs for the escape's name is ordinary work.

        Doing it in the same command as a piped verifier must not turn the
        gate off — this is the likeliest real-world route to the bypass,
        because reading this very rule is what puts the word on the line.
        """
        command = 'grep -rn "pipefail" docs/ ; uv run gz check | tail -5'
        self.assertEqual(masked_verifier(command), "gz check")

    def test_echoing_the_word_does_not_disarm_the_gate(self) -> None:
        command = "echo pipefail; uv run -m unittest -q | tail -5"
        self.assertEqual(masked_verifier(command), "unittest")

    def test_a_filename_containing_the_marker_does_not_disarm_the_gate(self) -> None:
        """`PIPESTATUS.md` is a bare word, not a parameter reference."""
        command = "cat PIPESTATUS.md; uv run gz check | tail -3"
        self.assertEqual(masked_verifier(command), "gz check")

    def test_a_flag_value_containing_the_marker_does_not_disarm_the_gate(self) -> None:
        command = "gz state --note=pipefail; uv run ruff check . | head -5"
        self.assertEqual(masked_verifier(command), "ruff")

    def test_pipefail_set_after_the_pipeline_does_not_protect_it(self) -> None:
        """Order is semantics, not decoration.

        A shell option set after a pipeline has already run cannot have
        reported that pipeline's status. Permitting it would swap one lexical
        check for a slightly better lexical check.
        """
        command = "uv run gz check | tail -5; set -o pipefail"
        self.assertEqual(masked_verifier(command), "gz check")


class TestExemptionControlIsRegisteredAndCatches(unittest.TestCase):
    """This gate's exemption half carries its own control (GHI #797).

    `verifier-exit-status-masked` was registered, enrolled, and passing on every
    `gz check` for the whole life of GHI #796's bypass, because it asserts
    refuse-piped / permit-unpiped and never touches the escape. A gate with an
    exemption makes two claims; only one of them was controlled.
    """

    def test_the_rule_claim_declares_which_control_covers_its_exemption(self) -> None:
        from gzkit.enforcement import get_enforcement_registry
        from gzkit.verifier_pipe_gate import (
            VERIFIER_ESCAPE_CLAIM_ID,
            VERIFIER_PIPE_CLAIM_ID,
            _ensure_verifier_pipe_claims_registered,
        )

        _ensure_verifier_pipe_claims_registered()
        declared = {r.claim_id: r.exempts for r in get_enforcement_registry()}
        self.assertEqual(declared.get(VERIFIER_PIPE_CLAIM_ID), VERIFIER_ESCAPE_CLAIM_ID)
        self.assertIn(VERIFIER_ESCAPE_CLAIM_ID, declared, "the named control must be registered")

    def test_the_exemption_control_catches_a_named_but_unused_escape(self) -> None:
        """The differential the rule control cannot express."""
        from gzkit.enforcement import EnforcementClaimRecord, _run_single_claim
        from gzkit.verifier_pipe_gate import (
            _build_masked_verifier_violation,
            _ep_verifier_escape_must_be_used,
        )

        signals: list[int] = []

        def capture(root: Path) -> int:
            signal = _ep_verifier_escape_must_be_used(root)
            signals.append(signal)
            return signal

        result = _run_single_claim(
            EnforcementClaimRecord(
                claim_id="verifier-pipe-escape-test",
                fixture=_build_masked_verifier_violation,
                entrypoint=capture,
                source_fn="test.verifier_pipe_escape",
            )
        )

        self.assertEqual(result.outcome, "PASS", result.message)
        self.assertEqual(signals, [1])


class TestVerifierInvocationForms(unittest.TestCase):
    """A verifier is recognized by what it RUNS, not by where its name appears."""

    def test_the_dash_m_module_form_is_recognized(self) -> None:
        """`uv run -m unittest` leaves `-m` as the head once `uv run` is stripped."""
        self.assertEqual(masked_verifier("uv run -m unittest -q | tail"), "unittest")

    def test_the_python_dash_m_form_is_recognized(self) -> None:
        self.assertEqual(masked_verifier("python -m unittest discover | head"), "unittest")

    def test_the_coverage_wrapper_form_is_recognized(self) -> None:
        command = "coverage run -m unittest discover -s tests -t . | tail"
        self.assertEqual(masked_verifier(command), "coverage")

    def test_a_verifier_name_as_a_quoted_argument_is_not_an_invocation(self) -> None:
        """The false positive a substring check would produce.

        `grep "unittest" …` mentions a verifier; it does not run one. A gate
        that matched on token presence would refuse ordinary reads.
        """
        self.assertIsNone(masked_verifier('grep -rn "unittest" src/ | head -20'))

    def test_an_absolute_path_invocation_is_recognized(self) -> None:
        self.assertEqual(masked_verifier("/usr/local/bin/ruff check . | tail"), "ruff")

    def test_a_non_verifier_gz_verb_is_not_a_verifier(self) -> None:
        """`gz` alone is too coarse — the sub-verb decides."""
        self.assertIsNone(masked_verifier("uv run gz status | head -5"))


class TestCanonicalRegistryCoherence(unittest.TestCase):
    """Coupled-surface coherence (AGENTS.md § DO IT RIGHT 1a).

    `CANONICAL_STEP_COMMANDS` is the locked authority for what an "ARB-wrapped
    verifier" is (AGENTS.md § Attestation). The clause governs *any* of them, so
    a canonical command this gate cannot see is a hole opened by an edit to a
    different file. Reading the registry rather than restating it is what makes
    that impossible.
    """

    def test_every_runnable_canonical_step_command_is_detected(self) -> None:
        for name, argv in CANONICAL_STEP_COMMANDS.items():
            if not argv:
                continue  # reserved slot; no runnable invocation yet
            with self.subTest(step=name):
                command = " ".join(argv) + " | tail -5"
                self.assertIsNotNone(
                    masked_verifier(command),
                    f"canonical step {name!r} ({' '.join(argv)}) is invisible to the gate",
                )


class TestVerifiersThatLeftTheCanonicalTable(unittest.TestCase):
    """Coverage must not be a side effect of a command's presence in the table.

    `_canonical_program_names` derives from `CANONICAL_STEP_COMMANDS`, so the
    sibling test above only ever asserts what the table currently names. That
    makes it blind in one direction: a verifier REMOVED from the table silently
    loses protection, and the removal looks like an edit to a different concern.

    GHI #856 walked into exactly that. Moving the canonical `unittest` step to
    the pinned `unittest-parallel` runner dropped bare `unittest` out of
    `VERIFIER_PROGRAMS` — while `uv run -m unittest <module>` remained how a
    scoped run is spelled at ~3,100 call sites in this repo. `_DECLARED_BEYOND_ARB`
    is what holds it, and this is the test that says so.
    """

    def test_a_scoped_module_run_is_still_protected(self) -> None:
        """The `-m unittest` form no longer appears in any canonical command."""
        self.assertEqual(
            masked_verifier("uv run -m unittest tests.arb.test_validator -v | tail -5"),
            "unittest",
            msg=(
                "Bare `unittest` lost pipe-gate protection. It left "
                "CANONICAL_STEP_COMMANDS when the canonical step moved to "
                "unittest-parallel (GHI #856); `_DECLARED_BEYOND_ARB` must carry it."
            ),
        )

    def test_both_runners_are_protected_at_once(self) -> None:
        """The swap adds a verifier; it must not trade one for the other."""
        self.assertEqual(masked_verifier("uv run -m unittest -q | tail -5"), "unittest")
        self.assertEqual(
            masked_verifier("uv run unittest-parallel -t . -s tests --buffer | tail -5"),
            "unittest-parallel",
        )

    def test_naming_a_runner_is_not_running_one(self) -> None:
        """Negative control: resolution is by command head, never token presence."""
        self.assertIsNone(masked_verifier("grep -rn unittest-parallel src/ | head -5"))
        self.assertIsNone(masked_verifier("echo unittest | tail -1"))


class TestDecideContract(unittest.TestCase):
    """The hook-facing verdict."""

    def test_non_bash_tools_are_out_of_scope(self) -> None:
        verdict = decide("Write", {"file_path": "src/x.py"})
        self.assertFalse(verdict.blocked)

    def test_a_masked_verifier_blocks(self) -> None:
        verdict = decide("Bash", {"command": "uv run gz check | tail -5"})
        self.assertTrue(verdict.blocked)

    def test_an_unparseable_command_is_not_this_gates_call(self) -> None:
        """Unbalanced quotes: the shell will reject it; this gate does not guess."""
        verdict = decide("Bash", {"command": 'uv run gz check "unclosed | tail'})
        self.assertFalse(verdict.blocked)

    def test_block_prose_carries_all_three_parts(self) -> None:
        """`.claude/rules/guardrail-feedback-prose.md` § Invariant.

        What failed, why it is forbidden (cited), and a runnable next step.
        Same bar `tests/hooks/test_stop_turn_feedback.py` asserts.
        """
        reason = decide("Bash", {"command": "uv run -m unittest -q | tail -5"}).reason
        self.assertIn("unittest", reason, "what failed: names the masked verifier")
        self.assertIn(
            "exit-code integrity",
            reason,
            "why forbidden: cites the binding clause by name",
        )
        self.assertIn("> ", reason, "next step: shows the runnable redirect form")
        self.assertIn("PIPESTATUS", reason, "next step: names the escape the clause allows")


class TheRecoveryIsTheCallersOwnCommandTests(unittest.TestCase):
    """The next step must be paste-ready, not a shape to translate.

    `.claude/rules/guardrail-feedback-prose.md` — the feedback IS the prompt the
    operator would otherwise have typed. Two permitted routes preserve the status;
    the prose used to lead with the two-call file-capture one and demote the
    one-call `pipefail` form to a clause behind "if you genuinely need the pipe",
    so the reader took the expensive route 11 times in one session while the cheap
    one sat unread. Both routes are still offered -- the ordering is the fix, and
    the refusal predicate is untouched.
    """

    def test_the_next_step_hands_back_the_command_with_pipefail_prepended(self) -> None:
        command = "uv run -m unittest tests.governance.test_enforces_registry -v 2>&1 | tail -30"
        reason = decide("Bash", {"command": command}).reason
        self.assertIn(f"set -o pipefail; {command}", reason)

    def test_the_cheap_route_is_named_before_the_expensive_one(self) -> None:
        """Ordering IS the defect: whichever route NEXT STEP names first is taken."""
        reason = decide("Bash", {"command": "uv run gz check | tail -5"}).reason
        self.assertLess(
            reason.index("pipefail"),
            reason.index("out.log"),
            "the one-call escape must precede the two-call file capture",
        )

    def test_the_file_capture_route_survives_as_the_alternative(self) -> None:
        """Reordering must not delete a working route -- inspecting a long
        capture separately is legitimate, and only its precedence was wrong.
        """
        reason = decide("Bash", {"command": "uv run gz check | tail -5"}).reason
        self.assertIn("out.log", reason)
        self.assertIn("REAL EXIT", reason)

    def test_a_multi_statement_command_is_handed_back_whole(self) -> None:
        """Prepending to the whole command is what runs; rewriting only the
        piped statement would hand back something the caller never typed.
        """
        command = 'grep -rn "x" docs/ ; uv run gz check | tail -5'
        reason = decide("Bash", {"command": command}).reason
        self.assertIn(f"set -o pipefail; {command}", reason)


if __name__ == "__main__":
    unittest.main()


class TestSequenceFormMasking(unittest.TestCase):
    """GHI #940: the pipe form was guarded; the SEQUENCE form was not.

    `gz check > log; tail log` masks exactly as thoroughly as `gz check | tail`:
    the shell reports the LAST statement's status either way. The module scoped
    its predicate to pipes and treated a statement separator as ENDING the risk —
    true for the verifier's own visible output in a foreground run, false for the
    aggregate status, which is the only signal a backgrounded run surfaces.

    The discriminator applied here is the one GHI #942 landed one surface over:
    a trailing statement that SURFACES the status is a legitimate explicit failure
    demonstration; one that says nothing about it presents a masked failure as
    success. These cases pin that line, not a list of filter names.
    """

    def test_a_verifier_followed_by_a_filter_statement_is_masked(self) -> None:
        # The issue's named class. No pipe, so the old predicate saw nothing.
        self.assertEqual(masked_verifier("uv run gz check > log 2>&1; tail -6 log"), "gz check")

    def test_masking_does_not_depend_on_the_trailing_statement_being_a_filter(self) -> None:
        # Keying to tail/head/grep would repeat the enumerate-the-examples miss
        # the module's own docstring names. `echo done` discards the status just
        # as completely, and `true` is the shape GHI #942 closed on the packet side.
        for trailer in ("echo done", "true", ":", "ls"):
            with self.subTest(trailer=trailer):
                self.assertEqual(
                    masked_verifier(f"uv run gz check > log 2>&1; {trailer}"), "gz check"
                )

    def test_a_newline_separated_sequence_masks_the_same_way(self) -> None:
        # The harness `run_in_background` surface sends newline-separated
        # statements; that is the shape the defect was observed on.
        self.assertEqual(masked_verifier("uv run gz check > log 2>&1\ntail -6 log"), "gz check")

    def test_reading_the_status_immediately_after_is_preserved(self) -> None:
        # THE LEGITIMATE EXPLICIT FAILURE DEMONSTRATION. This exact shape is what
        # the gate's own block prose tells the caller to write; refusing it would
        # make the rule un-compliable by its own recovery instruction.
        self.assertIsNone(masked_verifier('uv run gz check > log 2>&1; echo "REAL EXIT: $?"'))

    def test_a_status_read_after_an_intervening_statement_does_not_protect(self) -> None:
        # `$?` reads the LAST statement's status. After `tail` has run, it reports
        # tail's exit, not the verifier's — the read looks like evidence and is not.
        self.assertEqual(
            masked_verifier('uv run gz check > log 2>&1; tail -6 log; echo "exit $?"'),
            "gz check",
        )

    def test_and_and_propagates_failure_so_it_is_not_masking(self) -> None:
        # `&&` short-circuits: a failing verifier aborts the sequence and its
        # status IS the aggregate. Blocking this would be a false refusal.
        self.assertIsNone(masked_verifier("uv run gz check && echo ok"))

    def test_errexit_protects_the_statements_that_follow_it(self) -> None:
        # `set -e` aborts on the verifier's failure, so the aggregate carries it.
        # Honored on USE, like pipefail: the head must be `set` (GHI #796).
        self.assertIsNone(masked_verifier("set -e; uv run gz check > log; tail log"))

    def test_naming_errexit_without_setting_it_does_not_disarm_the_gate(self) -> None:
        # The GHI #796 rule applied to the new escape: the word is not the state.
        self.assertEqual(
            masked_verifier('grep -rn "set -e" docs/; uv run gz check > log; tail log'),
            "gz check",
        )

    def test_pipefail_alone_does_not_enable_errexit(self) -> None:
        # Isolates the OPERAND half of the errexit escape. The named-not-used test
        # above is guarded by the `set` HEAD check and so never reaches this logic —
        # a mutation loosening the operand test to a bare `"e" in token` survived it,
        # because `pipefail` contains an `e`. `set -o pipefail` enables a different
        # option entirely and must leave the sequence arm armed.
        self.assertEqual(
            masked_verifier("set -o pipefail; uv run gz check > log; tail log"),
            "gz check",
        )

    def test_a_long_form_errexit_operand_is_honored(self) -> None:
        # `set -o errexit` is the same state by its other spelling.
        self.assertIsNone(masked_verifier("set -o errexit; uv run gz check > log; tail log"))

    def test_a_verifier_in_the_final_statement_is_not_masked(self) -> None:
        self.assertIsNone(masked_verifier("ls > log; uv run gz check"))

    def test_a_trailing_separator_does_not_make_the_verifier_non_final(self) -> None:
        # `gz check;` splits into the verifier plus an EMPTY tail segment, so an
        # index-based "is this the last statement" test says no and the arm would
        # refuse a command that masks nothing. Nothing runs after the verifier, so
        # nothing overwrites its status. Pinned because the empty-tail filter that
        # prevents this survived its first mutation sweep untested.
        for command in (
            "uv run gz check;",
            "uv run gz check; ",
            "uv run gz check\n",
        ):
            with self.subTest(command=command):
                self.assertIsNone(masked_verifier(command))

    def test_a_non_verifier_sequence_is_not_this_gates_business(self) -> None:
        self.assertIsNone(masked_verifier("ls > log; tail -6 log"))


class TestArmSpecificRecovery(unittest.TestCase):
    """The two arms have DIFFERENT remedies, so one prose for both would misinform.

    `.claude/rules/guardrail-feedback-prose.md` requires the NEXT STEP be the
    caller's own command corrected. `set -o pipefail` genuinely fixes a pipe and
    genuinely does NOT fix a sequence — prepending it to `gz check > log; tail log`
    leaves the command exactly as masked. Handing that back as the correction
    would teach the caller a fix that does not fix.
    """

    def _reason(self, command: str) -> str:
        verdict = decide("Bash", {"command": command})
        self.assertTrue(verdict.blocked, command)
        return verdict.reason or ""

    def test_the_pipe_arm_recommends_pipefail(self) -> None:
        reason = self._reason("uv run gz check | tail -1")
        self.assertIn("set -o pipefail; uv run gz check | tail -1", reason)

    def test_the_sequence_arm_recommends_errexit_not_pipefail(self) -> None:
        reason = self._reason("uv run gz check > log 2>&1; tail -6 log")
        self.assertIn("set -e; uv run gz check > log 2>&1; tail -6 log", reason)
        self.assertNotIn("set -o pipefail; uv run gz check", reason)

    def test_the_sequence_arm_says_pipefail_will_not_help(self) -> None:
        # Naming the non-remedy matters: pipefail is the escape this gate has
        # taught for a year, so a caller meeting the sequence block will reach
        # for it first unless told plainly that it does nothing here.
        reason = self._reason("uv run gz check > log 2>&1; tail -6 log")
        self.assertIn("`pipefail` does NOT help here", reason)

    def test_the_sequence_arm_names_the_verifier_not_the_pipe(self) -> None:
        reason = self._reason("uv run gz check > log 2>&1; tail -6 log")
        self.assertIn("not the last statement", reason)
        self.assertNotIn("this command pipes", reason)

    def test_both_arms_carry_all_three_guardrail_parts(self) -> None:
        for command in (
            "uv run gz check | tail -1",
            "uv run gz check > log 2>&1; tail -6 log",
        ):
            with self.subTest(command=command):
                reason = self._reason(command)
                self.assertIn("BLOCKED:", reason)
                self.assertIn("WHY:", reason)
                self.assertIn("NEXT STEP:", reason)


class TestOrElseArm(unittest.TestCase):
    """`||` replaces a failing verifier's status with the branch's (GHI #970).

    The exclusion this class overturns was reasoned, not careless: a `||` branch
    runs ONLY on failure and announces it, so on a surface where the caller reads
    the whole terminal the failure is visible. What that reasoning missed is that
    the announcement is not the STATUS. `verifier || echo failed` exits 0 precisely
    when the verifier failed, so every consumer reading the aggregate — a harness
    notification, a packet replay — sees green at the exact moment there is
    something to hide.

    Scope is the canonical one, and it is what keeps the verdict idiom alive: the
    arm fires on a recognized VERIFIER, so `test -f x && echo DEFECT || echo OK`
    (whose left side exits non-zero by design, and whose head runs no verifier) is
    untouched. Measured 2026-09-06 over 1154 packet transcripts in this repository:
    3 carry a top-level `||`, all 3 are that idiom, and all 3 stay permitted.
    """

    def test_an_or_else_branch_masks_the_verifier(self) -> None:
        self.assertEqual(masked_verifier("uv run gz check || echo failed"), "gz check")

    def test_it_is_not_keyed_to_what_the_branch_says(self) -> None:
        # The concealment does not depend on the branch's text: `echo failed`
        # announces and `true` does not, and BOTH exit 0 over a failed verifier.
        # Keying to a reassuring-word list would repeat the enumerate-the-examples
        # miss the module's own docstring names.
        for branch in ("echo failed", "echo 'all good'", "true", ":", "tail -6 log"):
            with self.subTest(branch=branch):
                self.assertEqual(masked_verifier(f"uv run gz check || {branch}"), "gz check")

    def test_reading_the_status_in_the_branch_is_preserved(self) -> None:
        # THE LEGITIMATE FAILURE DEMONSTRATION, and the caller's own shape kept:
        # the branch still runs only on failure, and now reports the real status.
        # This is what the or-else block prose hands back, so refusing it would
        # make the rule un-compliable by its own recovery instruction.
        self.assertIsNone(masked_verifier('uv run gz check || echo "REAL EXIT: $?"'))

    def test_a_non_verifier_verdict_idiom_is_not_this_gates_business(self) -> None:
        # The three shapes actually present in this repository's packet corpus.
        # Their left side exits non-zero when the ASSERTION HOLDS — that non-zero
        # is the verdict, not a suppressed failure — and none of them runs a
        # recognized verifier.
        for command in (
            'test -d ops/chores && echo "DEFECT" || echo "OK: ops/chores deleted"',
            'test -f config/gzkit.chores.json && echo "DEFECT" || echo "OK: deleted"',
            'rg -n "vendor == .claude." src/ && echo "FAIL" || echo "PASS: no branches"',
        ):
            with self.subTest(command=command):
                self.assertIsNone(masked_verifier(command))

    def test_errexit_does_not_protect_an_or_else(self) -> None:
        # THE ESCAPE THAT DOES NOT ESCAPE. POSIX suppresses errexit for a command
        # on the left of `||`, so `set -e` aborts nothing here. Honoring it would
        # hand the caller a disarm that disarms only the gate.
        self.assertEqual(masked_verifier("set -e; uv run gz check || echo failed"), "gz check")

    def test_errexit_does_not_protect_a_backgrounded_verifier(self) -> None:
        # The same defect's other instance, fixed as a class: errexit cannot abort
        # on a background job's failure either, so `&` is not a separator it
        # protects. The escape is now scoped to the separators where the shell
        # genuinely aborts — `;` and a newline.
        self.assertEqual(masked_verifier("set -e; uv run gz check & tail -6 log"), "gz check")

    def test_errexit_still_protects_the_sequence_it_does_abort(self) -> None:
        # The other direction, so the narrowing above cannot be over-applied.
        self.assertIsNone(masked_verifier("set -e; uv run gz check > log; tail log"))
        self.assertIsNone(masked_verifier("set -e\nuv run gz check > log\ntail log"))


class TestOrElseRecovery(unittest.TestCase):
    """The or-else arm's remedy differs from BOTH existing arms (GHI #970).

    `pipefail` fixes a pipe and `set -e` fixes a sequence; neither fixes this one,
    and `set -e` is the actively misleading suggestion because the shell
    SUPPRESSES it left of `||`. Handing it back would satisfy
    `.claude/rules/guardrail-feedback-prose.md`'s shape while teaching a fix that
    does not fix — the exact failure the sequence arm's prose was branched to avoid.
    """

    def _reason(self, command: str) -> str:
        verdict = decide("Bash", {"command": command})
        self.assertTrue(verdict.blocked, command)
        return verdict.reason or ""

    def test_the_or_else_arm_recommends_reading_the_status_in_the_branch(self) -> None:
        # No PREFIX corrects this arm — that is the point, and why the prose
        # cannot follow the other two arms' "paste your command back" shape. The
        # correction is a one-token substitution inside the branch the caller wrote.
        reason = self._reason("uv run gz check || echo failed")
        self.assertIn('|| echo "REAL EXIT: $?"', reason)

    def test_the_or_else_arm_says_errexit_will_not_help(self) -> None:
        reason = self._reason("uv run gz check || echo failed")
        self.assertIn("`set -e` does NOT help here", reason)
        self.assertNotIn("set -e; uv run gz check || echo failed", reason)

    def test_the_or_else_arm_names_the_branch_not_the_pipe_or_the_sequence(self) -> None:
        reason = self._reason("uv run gz check || echo failed")
        self.assertNotIn("this command pipes", reason)
        self.assertNotIn("not the last statement", reason)

    def test_the_or_else_arm_carries_all_three_guardrail_parts(self) -> None:
        reason = self._reason("uv run gz check || echo failed")
        for part in ("BLOCKED:", "WHY:", "NEXT STEP:"):
            self.assertIn(part, reason)


class TestAndOrListMasking(unittest.TestCase):
    """What reports the status is the separator ending the verifier's LIST (GHI #971).

    Every earlier arm read the separator ending the verifier's own STATEMENT.
    `&&` propagates a failure through an AND-OR list, so its terminator is not the
    one that decides: the list's end is. Measured 2026-09-14 in bash and `/bin/sh`:

        false && echo ok                         -> exit 1
        false && echo ok; ls                     -> exit 0
        false && echo ok || echo caught          -> exit 0
        set -e; false && echo ok; ls             -> exit 0
        false && echo ok; echo "REAL EXIT: $?"   -> REAL EXIT: 1
        false & echo "REAL EXIT: $?"             -> REAL EXIT: 0
        set -o pipefail; false | cat; ls         -> exit 0

    The same question — does the verifier's failure reach the separator that ends
    its list — also covers a pipeline under `pipefail` and a `$?` read after `&`.
    """

    def test_a_chain_that_runs_to_the_end_of_the_command_is_permitted(self) -> None:
        # The case the old exclusion reasoned about, which stays true.
        self.assertIsNone(masked_verifier("uv run gz check && echo ok"))
        self.assertIsNone(masked_verifier("uv run gz check && echo ok && ls"))

    def test_a_chain_caught_by_a_later_statement_is_masked(self) -> None:
        for command in (
            "uv run gz check && echo ok; ls",
            "uv run gz check && echo ok\nls",
            "uv run gz check && echo ok || echo caught",
            "uv run gz check && echo ok && echo more; ls",
            "cd src && uv run gz check && echo ok; ls",
        ):
            with self.subTest(command=command):
                self.assertEqual(masked_verifier(command), "gz check")

    def test_errexit_does_not_rescue_a_chain(self) -> None:
        # POSIX suppresses errexit for a command that is not the last in an
        # AND-OR list, so `set -e` aborts nothing and the list's end still masks.
        self.assertEqual(masked_verifier("set -e; uv run gz check && echo ok; ls"), "gz check")

    def test_errexit_still_protects_a_verifier_that_ends_its_chain(self) -> None:
        # The other direction: the verifier IS the list's last command, so
        # errexit fires on it. Unchanged sequence-arm behavior.
        self.assertIsNone(masked_verifier("set -e; cd src && uv run gz check; ls"))

    def test_reading_the_status_right_after_the_chain_is_preserved(self) -> None:
        # When the chain short-circuits, the list's status IS the verifier's, so
        # the immediate `$?` read reports the real failure in either shape.
        self.assertIsNone(masked_verifier('uv run gz check && echo ok; echo "REAL EXIT: $?"'))
        self.assertIsNone(masked_verifier('uv run gz check && echo ok || echo "REAL EXIT: $?"'))

    def test_a_status_read_inside_the_chain_does_not_protect_the_list_end(self) -> None:
        # `$?` read by a chain member runs only on success; the list end still masks.
        self.assertEqual(
            masked_verifier('uv run gz check && echo "exit $?"; ls'),
            "gz check",
        )

    def test_a_status_read_after_a_background_separator_does_not_protect(self) -> None:
        # After `&`, `$?` is the background LAUNCH's status — 0 — not the
        # verifier's. The read looks like evidence and reports success.
        for command in (
            'uv run gz check & echo "REAL EXIT: $?"',
            'uv run gz check && echo ok & echo "REAL EXIT: $?"',
        ):
            with self.subTest(command=command):
                self.assertEqual(masked_verifier(command), "gz check")

    def test_a_pipeline_under_pipefail_carries_the_status_to_its_terminator(self) -> None:
        # pipefail makes an upstream verifier's failure the pipeline's status, so
        # a later statement replaces the VERIFIER's status, not the filter's.
        self.assertEqual(
            masked_verifier("set -o pipefail; uv run gz check | tail -3; ls"), "gz check"
        )

    def test_a_pipeline_under_pipefail_keeps_both_escapes(self) -> None:
        for command in (
            'set -o pipefail; uv run gz check | tail -3; echo "REAL EXIT: $?"',
            "set -eo pipefail; uv run gz check | tail -3; ls",
            "set -o pipefail; uv run gz check | tail -3",
        ):
            with self.subTest(command=command):
                self.assertIsNone(masked_verifier(command))

    def test_without_pipefail_an_upstream_verifier_is_still_the_pipe_arm(self) -> None:
        self.assertEqual(
            masked_verifier_reason("uv run gz check | tail -3; ls"), ("gz check", "pipe")
        )


class TestEveryArmsCorrectionIsAdmitted(unittest.TestCase):
    """A correction the gate refuses again is a loop, not a recovery (GHI #971).

    `.claude/rules/guardrail-feedback-prose.md` requires a runnable next step. For
    `gz check & ls` the prose handed back `set -e; <command>`, which this gate
    refused again — errexit is not honored for `&` — and which exits 0 when run.
    Each arm's named correction is fed back through `decide` here.
    """

    def _reason(self, command: str) -> tuple[str, str]:
        found = masked_verifier_reason(command)
        self.assertIsNotNone(found, command)
        verdict = decide("Bash", {"command": command})
        self.assertTrue(verdict.blocked, command)
        return (found or ("", ""))[1], verdict.reason

    def test_a_backgrounded_verifier_gets_its_own_arm(self) -> None:
        arm, reason = self._reason("uv run gz check & tail -6 log")
        self.assertEqual(arm, "background")
        self.assertNotIn("set -e; uv run gz check & tail -6 log", reason)
        self.assertIn("`set -e` does NOT help here", reason)

    def test_the_background_correction_is_admitted(self) -> None:
        _arm, reason = self._reason("uv run gz check & tail -6 log")
        correction = '<verifier> > out.log 2>&1; echo "REAL EXIT: $?"'
        self.assertIn(correction, reason)
        self.assertIsNone(masked_verifier(correction.replace("<verifier>", "uv run gz check")))

    def test_a_caught_chain_gets_its_own_arm(self) -> None:
        for command in ("uv run gz check && echo ok; ls", "uv run gz check && echo ok || echo x"):
            with self.subTest(command=command):
                arm, reason = self._reason(command)
                self.assertEqual(arm, "chain")
                self.assertIn("`set -e` does NOT help here", reason)
                self.assertNotIn(f"set -e; {command}", reason)

    def test_the_chain_corrections_are_admitted(self) -> None:
        _arm, reason = self._reason("uv run gz check && echo ok; ls")
        for correction in (
            '<your chain>; echo "REAL EXIT: $?"',
            '<your chain> || echo "REAL EXIT: $?"',
        ):
            with self.subTest(correction=correction):
                self.assertIn(correction, reason)
                concrete = correction.replace("<your chain>", "uv run gz check && echo ok")
                self.assertIsNone(masked_verifier(concrete))

    def test_every_pasteable_prefix_correction_is_admitted(self) -> None:
        # The pipe and sequence arms hand back the caller's whole command with a
        # prefix. That pasted line must pass the gate that proposed it.
        for command, prefix in (
            ("uv run gz check | tail -1", "set -o pipefail; "),
            ("uv run gz check > log 2>&1; tail -6 log", "set -e; "),
        ):
            with self.subTest(command=command):
                _arm, reason = self._reason(command)
                self.assertIn(prefix + command, reason)
                self.assertIsNone(masked_verifier(prefix + command))

    def test_the_new_arms_carry_all_three_guardrail_parts(self) -> None:
        for command in ("uv run gz check & tail -6 log", "uv run gz check && echo ok; ls"):
            with self.subTest(command=command):
                _arm, reason = self._reason(command)
                for part in ("BLOCKED:", "WHY:", "NEXT STEP:"):
                    self.assertIn(part, reason)


class TestGroupedVerifierRecognition(unittest.TestCase):
    """A verifier inside `( … )` or `{ …; }` is refused on the same terms (GHI #1008).

    Resolution is by command head, and the head of a group is the grouping token, so
    every arm saw no verifier at all. A group is ONE command of its list, reporting
    its own last statement. Measured 2026-09-15 in bash and `/bin/sh`, `false`
    standing in for the verifier:

        (false); ls                     -> 0     (false)                        -> 1
        { false; }; ls                  -> 0     (cd . && false)                -> 1
        (false; ls)                     -> 0     (false); echo "REAL EXIT: $?"  -> 1
        (false) || echo x               -> 0     set -e; (false); ls            -> 1
        (set -e); false; ls             -> 0     { set -e; }; false; ls         -> 1
        { set -e; } | cat; false; ls    -> 0     set -o pipefail; (false) | cat -> 1
        set -e; (false; ls) || echo x   -> 0     set -e; (false; ls)            -> 1
    """

    def test_a_group_followed_by_a_replacing_statement_is_masked_by_that_arm(self) -> None:
        for command, arm in (
            ("(uv run gz check); ls", "sequence"),
            ("{ uv run gz check; }; ls", "sequence"),
            ("(uv run gz check) > log 2>&1; tail -6 log", "sequence"),
            ("(uv run gz check) || echo failed", "or-else"),
            ("(uv run gz check) && echo ok; ls", "chain"),
            ("(uv run gz check) & tail -6 log", "background"),
            ("(uv run gz check) | tail -3", "pipe"),
        ):
            with self.subTest(command=command):
                self.assertEqual(masked_verifier_reason(command), ("gz check", arm))

    def test_a_group_written_against_an_operator_is_still_read(self) -> None:
        # The lexer merges adjacent punctuation: `(x);ls` yields `);` and `ls;(x)`
        # yields `;(`, so the separator hides inside the same token as the paren.
        for command in (
            "(uv run gz check);ls",
            "ls;(uv run gz check);ls",
            "(uv run gz check)|tail -3",
            "(uv run gz check)&&echo ok;ls",
            "(uv run gz check)\nls",
        ):
            with self.subTest(command=command):
                self.assertEqual(masked_verifier(command), "gz check")

    def test_a_statement_after_the_verifier_inside_the_group_masks_it(self) -> None:
        # The group reports its LAST statement, exactly as a command does.
        for command in (
            "(uv run gz check; ls)",
            "{ uv run gz check; ls; }",
            "(cd src && uv run gz check && echo ok; ls)",
            "( (uv run gz check) ); ls",
            "{ (uv run gz check); }; ls",
        ):
            with self.subTest(command=command):
                self.assertEqual(masked_verifier(command), "gz check")

    def test_a_group_whose_status_is_the_verifiers_is_permitted(self) -> None:
        for command in (
            "(uv run gz check)",
            "{ uv run gz check; }",
            "(cd src && uv run gz check)",
            "(uv run gz check) > log 2>&1",
            "ls; (uv run gz check)",
            "( (uv run gz check) )",
        ):
            with self.subTest(command=command):
                self.assertIsNone(masked_verifier(command))

    def test_reading_the_status_right_after_the_group_or_inside_it_is_preserved(self) -> None:
        for command in (
            '(uv run gz check); echo "REAL EXIT: $?"',
            # The committed transcript corpus's one grouped verifier.
            '(cd /tmp/layout-drift && uv run gz validate --chores-layout); echo "exit:$?"',
            '(uv run gz check; echo "REAL EXIT: $?")',
            '(uv run gz check) && echo ok; echo "REAL EXIT: $?"',
        ):
            with self.subTest(command=command):
                self.assertIsNone(masked_verifier(command))

    def test_a_status_read_by_the_first_statement_of_a_following_group_is_preserved(
        self,
    ) -> None:
        # A subshell inherits `$?`: `(false); (echo "$?")` prints 1, and
        # `(false); (ls; echo "$?")` prints ls's 0. Immediacy holds inside the group.
        self.assertIsNone(masked_verifier('(uv run gz check); (echo "REAL EXIT: $?")'))
        self.assertEqual(masked_verifier('(uv run gz check); (ls; echo "S: $?")'), "gz check")

    def test_a_pipestatus_read_inside_a_later_group_is_preserved(self) -> None:
        # Measured: `false | cat; (echo "${PIPESTATUS[0]}")` prints 1.
        self.assertIsNone(masked_verifier('uv run gz check | tail -3; (echo "${PIPESTATUS[0]}")'))

    def test_a_status_read_after_a_backgrounded_group_does_not_protect(self) -> None:
        self.assertEqual(masked_verifier('(uv run gz check) & echo "REAL EXIT: $?"'), "gz check")

    def test_a_verifier_backgrounded_at_the_end_of_a_group_is_masked_by_what_follows(
        self,
    ) -> None:
        # The group reports the background LAUNCH: `(false &); ls` exits 0 and
        # `(false &); echo "$?"` prints 0, so no read after the group recovers it.
        for command in (
            "(uv run gz check &); ls",
            "( (uv run gz check &) ); ls",
            "(uv run gz check &) && ls",
            '(uv run gz check &); echo "REAL EXIT: $?"',
        ):
            with self.subTest(command=command):
                self.assertEqual(masked_verifier_reason(command), ("gz check", "background"))
        # Nothing after it: the same terms as an ungrouped trailing `verifier &`.
        self.assertIsNone(masked_verifier("(uv run gz check &)"))
        self.assertIsNone(masked_verifier("uv run gz check &"))

    def test_errexit_reaches_into_a_group_that_ends_its_list(self) -> None:
        for command in (
            "set -e; (uv run gz check); ls",
            "set -e; { uv run gz check; }; ls",
            "set -e; (uv run gz check; ls)",
            "set -e; { uv run gz check; ls; }",
            "set -e; (cd src && uv run gz check; ls)",
        ):
            with self.subTest(command=command):
                self.assertIsNone(masked_verifier(command))

    def test_a_verifier_errexit_aborts_on_is_still_the_groups_status_outside(self) -> None:
        # errexit makes the group exit with the verifier's status — which an outer
        # pipe then replaces: `set -e; (false; ls) | cat` exits 0.
        self.assertEqual(
            masked_verifier_reason("set -e; (uv run gz check; ls) | tail -3"), ("gz check", "pipe")
        )

    def test_errexit_does_not_reach_into_a_group_inside_an_and_or_list(self) -> None:
        # POSIX suppresses errexit for EVERY command inside a group that is not last
        # in its AND-OR list, so the statement after the verifier still reports.
        for command in (
            "set -e; (uv run gz check; ls) || echo x",
            "set -e; (uv run gz check; ls) && echo ok",
            "set -e; { uv run gz check; ls; } || echo x",
            "set -e; ( (uv run gz check; ls) ) || echo x",
        ):
            with self.subTest(command=command):
                self.assertEqual(masked_verifier(command), "gz check")

    def test_errexit_does_not_rescue_a_grouped_verifier_in_a_chain(self) -> None:
        self.assertEqual(masked_verifier("set -e; (uv run gz check) && echo ok; ls"), "gz check")

    def test_shell_state_set_in_a_subshell_does_not_leak_out(self) -> None:
        for command, name in (
            ("(set -e); uv run gz check; ls", "gz check"),
            ("(set -o pipefail); uv run gz check | tail -3", "gz check"),
            ("{ set -e; } | cat; uv run gz check; ls", "gz check"),
            ("{ set -e; } & wait; uv run gz check; ls", "gz check"),
        ):
            with self.subTest(command=command):
                self.assertEqual(masked_verifier(command), name)

    def test_shell_state_set_in_a_brace_group_statement_does_leak_out(self) -> None:
        for command in (
            "{ set -e; }; uv run gz check; ls",
            "{ set -o pipefail; }; uv run gz check | tail -3",
        ):
            with self.subTest(command=command):
                self.assertIsNone(masked_verifier(command))

    def test_pipefail_reaches_a_grouped_pipeline_stage(self) -> None:
        self.assertIsNone(masked_verifier("set -o pipefail; (uv run gz check) | tail -3"))
        self.assertIsNone(masked_verifier("set -o pipefail; (uv run gz check | tail -3)"))
        self.assertEqual(
            masked_verifier("set -o pipefail; (uv run gz check | tail -3); ls"), "gz check"
        )

    def test_a_group_that_runs_no_verifier_is_not_this_gates_business(self) -> None:
        for command in ("(cd src && ls); ls", "{ ls; }; tail -6 log", "(ls) || echo x"):
            with self.subTest(command=command):
                self.assertIsNone(masked_verifier(command))

    def test_parentheses_that_are_not_a_grouping_are_not_read_as_one(self) -> None:
        # An array assignment, a process substitution and a function definition
        # all carry parens outside command position.
        for command in (
            "a=(1 2); uv run gz check",
            "diff <(ls) x; uv run gz check",
            "f() { ls; }; uv run gz check",
        ):
            with self.subTest(command=command):
                self.assertIsNone(masked_verifier(command))

    def test_a_substitution_closed_against_a_separator_no_longer_hides_the_next_verifier(
        self,
    ) -> None:
        # The same merged-punctuation cause, observed in session history: `$(…);`
        # lexed as one `);` token, so the verifier after it shared a statement with
        # the assignment and its head was never read. The later statement replaces
        # the verifier's status.
        for command, verifier in (
            (
                'S=$(date +%s); uv run gz validate --documents > /dev/null 2>&1; echo "took"',
                "gz validate",
            ),
            ("S=$(date +%s)\nuv run gz check > log 2>&1\nE=$(date +%s)", "gz check"),
        ):
            with self.subTest(command=command):
                self.assertEqual(masked_verifier_reason(command), (verifier, "sequence"))

    def test_prose_parens_in_a_heredoc_body_keep_their_lexing(self) -> None:
        # A `(` after a plain word is not shell syntax. Splitting its `);` turned
        # attestation prose into commands and refused writing the file; measured on
        # two session commands that the gate had admitted before groups were read.
        command = (
            "cat > attest.txt <<'EOF'\n"
            "lint clean (arb-ruff-1); mkdocs --strict clean (arb-step-mkdocs-2); behave 7/7\n"
            "EOF"
        )
        self.assertIsNone(masked_verifier(command))

    def test_non_grouping_parens_do_not_stop_a_later_group_being_read(self) -> None:
        # Both kinds of non-grouping paren must still balance, or the whole command
        # would fall back to the ungrouped reading and hide the grouped verifier.
        # A `}` outside command position is a word, not a closer.
        for command in (
            "a=(1 2); (uv run gz check); ls",
            "cat > f <<'EOF'\nnote (x); more\nEOF\n(uv run gz check); ls",
            "echo }; (uv run gz check); ls",
        ):
            with self.subTest(command=command):
                self.assertEqual(masked_verifier(command), "gz check")

    def test_unbalanced_parens_keep_the_ungrouped_reading(self) -> None:
        # A quoted lone paren lexes exactly like an operator, so the command is read
        # without groups, in both directions.
        self.assertEqual(masked_verifier('grep ")" f; uv run gz check | tail -3'), "gz check")
        self.assertIsNone(masked_verifier('grep "(" f; uv run gz check'))


class TestGroupedVerifierRecovery(unittest.TestCase):
    """Each grouped refusal's named correction must pass the gate (GHI #1008, #971)."""

    def _reason(self, command: str) -> tuple[str, str]:
        found = masked_verifier_reason(command)
        self.assertIsNotNone(found, command)
        verdict = decide("Bash", {"command": command})
        self.assertTrue(verdict.blocked, command)
        return (found or ("", ""))[1], verdict.reason

    def test_the_sequence_prefix_correction_is_admitted_for_a_group(self) -> None:
        for command in ("(uv run gz check); ls", "{ uv run gz check; ls; }"):
            with self.subTest(command=command):
                arm, reason = self._reason(command)
                self.assertEqual(arm, "sequence")
                self.assertIn(f"set -e; {command}", reason)
                self.assertIsNone(masked_verifier(f"set -e; {command}"))

    def test_a_sequence_errexit_cannot_reach_gets_its_own_arm(self) -> None:
        # `set -e;` would be refused again here, and the shell exits 0 with it.
        for command in (
            "(uv run gz check; ls) || echo x",
            "set -e; (uv run gz check; ls) && echo ok",
        ):
            with self.subTest(command=command):
                arm, reason = self._reason(command)
                self.assertEqual(arm, "errexit-suppressed")
                self.assertNotIn(f"set -e; {command}", reason)
                self.assertIn("`set -e` does NOT help here", reason)
                for part in ("BLOCKED:", "WHY:", "NEXT STEP:"):
                    self.assertIn(part, reason)

    def test_the_errexit_suppressed_correction_is_admitted(self) -> None:
        _arm, reason = self._reason("(uv run gz check; ls) || echo x")
        correction = '( <verifier> > out.log 2>&1; echo "REAL EXIT: $?"; <rest> )'
        self.assertIn(correction, reason)
        concrete = correction.replace("<verifier>", "uv run gz check").replace("<rest>", "ls")
        self.assertIsNone(masked_verifier(f"{concrete} || echo x"))
