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

    def test_a_pipeline_in_a_later_statement_does_not_taint_the_verifier(self) -> None:
        """`;` ends the pipeline. The verifier ran unpiped; `ls | head` is unrelated."""
        self.assertIsNone(masked_verifier("uv run gz check; ls | head -3"))


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


if __name__ == "__main__":
    unittest.main()
