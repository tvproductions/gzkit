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
from gzkit.verifier_pipe_gate import decide, masked_verifier


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
        """`||` is a control operator, not a pipeline — the verifier's exit survives."""
        self.assertIsNone(masked_verifier("uv run gz check || echo FAILED"))

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
