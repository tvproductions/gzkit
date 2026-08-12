"""Negative controls must discriminate the claim they name (GHI #699).

The enforcement-floor audit reported 47/47 verified while 32 of those negative
controls could not distinguish "the enforcement caught the violation" from
"something unrelated went wrong". These tests pin the discrimination contract
itself, so a future coarsening of the signal fails here rather than shipping as
a green floor.

Semantics under test (derived from the campaign plan
``docs/governance/build-to-1.0-campaign-2026-06-30.md`` §5, clauses (b) and (c)):
a negative control must run the real path in its **production** configuration
and assert it fails **for the reason the claim names**.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


class TestCommandFailsDiscriminatesExitCode(unittest.TestCase):
    """A subprocess NC must not score a launch failure as a caught violation.

    §5 clause (c): the control asserts the production path *fails* — but a tool
    that never ran did not fail, it was absent. Scoring both as "caught" makes
    the control unable to detect that the enforcement was removed entirely.
    """

    def test_missing_binary_is_not_a_caught_violation(self) -> None:
        """A command that cannot launch (returncode -1) must score as NOT caught."""
        from gzkit.governance.trust_audits._qc_nc_entrypoints import _command_fails

        root = Path(tempfile.mkdtemp(prefix="gzkit-nc-discrim-"))
        signal = _command_fails("gzkit-no-such-binary-deadbeef", root, expected_exit=1)

        self.assertEqual(
            signal,
            0,
            "A tool that failed to launch (returncode -1) must NOT be scored as "
            "having caught the violation. Scoring any non-zero exit as 'caught' "
            "means deleting the enforcement entirely leaves the NC green "
            "(GHI #699 generator #1).",
        )

    def test_expected_exit_code_is_a_caught_violation(self) -> None:
        """The documented violation exit code must score as caught."""
        from gzkit.governance.trust_audits._qc_nc_entrypoints import _command_fails

        root = Path(tempfile.mkdtemp(prefix="gzkit-nc-discrim-"))
        (root / "pyproject.toml").write_text(
            "[project]\nname = 'x'\nversion = '0.0.0'\n", encoding="utf-8"
        )
        (root / "bad.py").write_text("import sys\n", encoding="utf-8")

        signal = _command_fails("uv run ruff check .", root, expected_exit=1)

        self.assertEqual(
            signal,
            1,
            "ruff exits 1 on a lint violation; that is the claim's documented "
            "catch signal and must score as caught.",
        )

    def test_clean_tree_is_not_a_caught_violation(self) -> None:
        """The second pole: a clean project must NOT trip the control."""
        from gzkit.governance.trust_audits._qc_nc_entrypoints import _command_fails

        root = Path(tempfile.mkdtemp(prefix="gzkit-nc-discrim-clean-"))
        (root / "pyproject.toml").write_text(
            "[project]\nname = 'x'\nversion = '0.0.0'\n", encoding="utf-8"
        )
        (root / "good.py").write_text('"""Doc."""\n', encoding="utf-8")

        signal = _command_fails("uv run ruff check .", root, expected_exit=1)

        self.assertEqual(
            signal,
            0,
            "A guard that fires on a clean tree is as broken as one that never "
            "fires; only this pole catches it.",
        )


class TestSubprocessEntrypointsExerciseTheWorkingTree(unittest.TestCase):
    """§5 clause (b): the control must run the path in its production configuration.

    A ``uv run gz ...`` subprocess launched from a scratch directory resolves
    ``gz`` from whatever is on PATH — under a bare (non-``uv run``) invocation
    that is the installed wheel at ``~/.local/bin/gz``, not ``src/gzkit/``.
    Gutting the working tree then leaves the control green.

    The fix is not to pin PATH but to stop shelling out: a gz-owned check is a
    Python callable and must be invoked as one, which makes the working tree
    definitionally the code under test.
    """

    #: Claims whose enforcement lives in gzkit's own Python, not an external tool.
    GZ_OWNED_CLAIMS = (
        "skill-audit",
        "readiness-audit",
        "cli-audit",
        "preflight",
        "parity-check",
    )

    def test_gz_owned_claims_do_not_shell_out(self) -> None:
        """gz-owned NC entrypoints must call production Python, not `uv run gz`."""
        import inspect

        from gzkit.governance.trust_audits import _qc_negative_controls as ncs

        table = {entry[0]: entry[2] for entry in ncs._QC_NEGATIVE_CONTROL_TABLE}

        offenders: list[str] = []
        for claim in self.GZ_OWNED_CLAIMS:
            entrypoint = table[claim]
            source = inspect.getsource(entrypoint)
            if "uv run gz" in source:
                offenders.append(claim)

        self.assertEqual(
            offenders,
            [],
            "These NC entrypoints shell out to `uv run gz`, which resolves to the "
            "installed wheel rather than src/gzkit/ — gutting the working tree "
            "leaves them green (GHI #699 generator #5). Invoke the production "
            f"Python callable directly instead. Offenders: {offenders}",
        )


class TestExpectedFindingDiscriminatesTheReason(unittest.TestCase):
    """§5 clause (c): the control must fail *for the reason the claim names*.

    The runner previously reduced every entrypoint result to ``bool()``, so a
    validator that bailed on configuration, crashed, or flagged an unrelated
    artifact was indistinguishable from one that caught the planted violation
    (GHI #699 generator #3). ``EnforcementClaimRecord.expect`` pins the reason.
    """

    @staticmethod
    def _record(expect: str | None, findings: list[object]):
        from gzkit.enforcement import EnforcementClaimRecord

        return EnforcementClaimRecord(
            claim_id="line-endings",
            fixture=lambda: None,
            entrypoint=lambda _fx: findings,
            source_fn="test.entrypoint",
            expect=expect,
        )

    def test_finding_matching_expect_passes(self) -> None:
        """A finding that names the claim's reason is a genuine catch."""
        from gzkit.core.validation_rules import ValidationError
        from gzkit.enforcement import _run_single_claim

        finding = ValidationError(
            type="line_endings", artifact="x", message="lacks the LF-normalization directive"
        )
        result = _run_single_claim(self._record("LF-normalization", [finding]))

        self.assertEqual(result.outcome, "PASS", result.message)

    def test_finding_not_matching_expect_is_a_facade(self) -> None:
        """A failure for an unrelated reason must NOT be scored as a catch.

        This is the mutation the whole repair exists to catch: the fixture stops
        planting the violation, the validator still fails (missing artifact), and
        the old ``bool()`` signal reported PASS.
        """
        from gzkit.core.validation_rules import ValidationError
        from gzkit.enforcement import _run_single_claim

        unrelated = ValidationError(
            type="line_endings", artifact="x", message="Missing `.gitattributes`"
        )
        result = _run_single_claim(self._record("LF-normalization", [unrelated]))

        self.assertEqual(
            result.outcome,
            "FACADE",
            "A validator that failed for a DIFFERENT reason than the claim names "
            "must surface as FACADE, not PASS (GHI #699 generator #3).",
        )
        self.assertIn("NOT for the reason the claim names", result.message)

    def test_exit_code_result_cannot_satisfy_an_expect(self) -> None:
        """A bare int carries no reason, so it can never satisfy ``expect``.

        Deliberate: an exit code is precisely the signal that cannot distinguish
        catching the violation from crashing.
        """
        from gzkit.enforcement import _run_single_claim

        result = _run_single_claim(self._record("LF-normalization", 1))

        self.assertEqual(result.outcome, "FACADE", result.message)


class TestRewrittenFixturesPlantExactlyOneViolation(unittest.TestCase):
    """Generator #2: a fixture must be a valid project with ONE planted violation.

    A bare temp dir violates every claim at once, so the validator's *missing
    artifact* branch answers — never the branch the claim names. Each fixture
    below must yield exactly one finding, and it must be the claim's own.
    """

    CLAIMS = (
        "session-green-gate",
        "orientation-freshness",
        "complexity-thresholds",
        "line-endings",
    )

    def test_each_rewritten_fixture_yields_only_its_own_finding(self) -> None:
        import shutil
        from pathlib import Path

        from gzkit.governance.trust_audits import _qc_negative_controls as ncs

        table = {entry[0]: entry for entry in ncs._QC_NEGATIVE_CONTROL_TABLE}

        for claim in self.CLAIMS:
            with self.subTest(claim=claim):
                _cid, fixture, entrypoint, expect = table[claim]
                root = fixture()
                try:
                    findings = entrypoint(root)
                finally:
                    shutil.rmtree(Path(root), ignore_errors=True)

                self.assertEqual(
                    len(findings),
                    1,
                    f"{claim}: expected exactly one planted violation, got "
                    f"{[getattr(f, 'message', f) for f in findings]}. More than one "
                    "means the fixture is degenerate rather than minimal-valid.",
                )
                self.assertIn(expect, findings[0].message)

    def test_no_claim_uses_the_deprecated_empty_fixture_for_a_repaired_claim(self) -> None:
        """The four repaired claims must no longer route through ``_build_empty``."""
        import inspect

        from gzkit.governance.trust_audits import _qc_negative_controls as ncs

        table = {entry[0]: entry[1] for entry in ncs._QC_NEGATIVE_CONTROL_TABLE}
        for claim in self.CLAIMS:
            with self.subTest(claim=claim):
                self.assertNotIn(
                    "_build_empty",
                    inspect.getsource(table[claim]),
                    f"{claim} still builds its violation by absence (GHI #699 generator #2).",
                )


class TestQcBindingCertifiesABehavioralChannel(unittest.TestCase):
    """The claim certifying the theater detector must exercise a real channel.

    `qc-binding` registered ``_check_theater_signatures`` as its entrypoint against
    a fixture that self-declared ``theater_flags=["copy-vs-self"]`` — a set-membership
    test between two literals in the same module. Both of the audit's real channels
    could be deleted and the control stayed green (GHI #699).
    """

    @staticmethod
    def _record():
        from gzkit.enforcement import (
            _ensure_production_claims_registered,
            get_enforcement_registry,
        )

        _ensure_production_claims_registered()
        return next(r for r in get_enforcement_registry() if r.claim_id == "qc-binding")

    def test_entrypoint_is_not_the_self_declared_flag_renderer(self) -> None:
        """The entrypoint must not be the tautological ``theater_flags`` renderer."""
        self.assertNotIn(
            "_check_theater_signatures",
            self._record().source_fn,
            "qc-binding must certify a behavioral channel, not a membership test "
            "between two literals in its own module (GHI #699).",
        )

    def test_claim_passes_against_a_planted_facade(self) -> None:
        """The real analyzer must catch the planted copy-vs-self facade."""
        from gzkit.enforcement import _run_single_claim

        result = _run_single_claim(self._record())

        self.assertEqual(result.outcome, "PASS", result.message)

    def test_claim_goes_facade_when_the_facade_is_not_planted(self) -> None:
        """Mutation: a fixture that plants nothing must NOT keep the control green."""
        import tempfile
        from pathlib import Path

        from gzkit.enforcement import _run_single_claim

        gutted = self._record().model_copy(
            update={"fixture": lambda: Path(tempfile.mkdtemp(prefix="gzkit-nc-mutation-"))}
        )

        self.assertEqual(
            _run_single_claim(gutted).outcome,
            "FACADE",
            "With nothing planted the analyzer has nothing to catch; scoring that "
            "as PASS is the self-certifying defect this claim exists to prevent.",
        )


class TestCompositeClaimsAreDecomposed(unittest.TestCase):
    """Generator #4: one claim per independently-deletable invariant.

    `surface-fidelity` fans out to four sub-validators, `task-envelope-coherence`
    to four signatures, `waiver-ratchet` to three mechanisms — but each carried a
    single negative control, so every invariant its one fixture did not happen to
    violate could be deleted and the control stayed green (GHI #699).
    """

    #: claim id -> the invariant its fixture plants
    SIBLINGS = {
        "surface-fidelity-bullet-retention": "bullet retention",
        "surface-fidelity-surface-weight": "surface weight band",
        "task-envelope-subdivision": "signature (b)",
        "task-envelope-layer-drift": "signature (c)",
        "task-envelope-obpi-divergence": "signature (d)",
        "waiver-ratchet-closed-set-lock": "closed-set-lock mechanism",
        "waiver-ratchet-dated-cutover": "dated-cutover mechanism",
        "waiver-ratchet-silent-bypass": "unregistered waiver surface",
        "handoff-documents-populated-sections": "present-but-empty required section",
    }

    @staticmethod
    def _registry() -> dict:
        from gzkit.enforcement import (
            _ensure_production_claims_registered,
            get_enforcement_registry,
        )

        _ensure_production_claims_registered()
        return {r.claim_id: r for r in get_enforcement_registry()}

    def test_every_sibling_claim_is_registered(self) -> None:
        """Each decomposed invariant must have its own claim."""
        registered = self._registry()
        missing = [c for c in self.SIBLINGS if c not in registered]

        self.assertEqual(
            missing,
            [],
            f"Composite claims must decompose one-per-invariant; missing: {missing}",
        )

    def test_every_sibling_pins_its_own_reason(self) -> None:
        """A sibling without an ``expect`` would collapse back into the parent."""
        registry = self._registry()
        for claim in self.SIBLINGS:
            with self.subTest(claim=claim):
                self.assertIsNotNone(
                    registry[claim].expect,
                    f"{claim} must pin the finding it certifies, otherwise any "
                    "sibling's failure would satisfy it.",
                )

    def test_every_sibling_passes_on_its_planted_violation(self) -> None:
        from gzkit.enforcement import _run_single_claim

        registry = self._registry()
        for claim, invariant in self.SIBLINGS.items():
            with self.subTest(claim=claim):
                result = _run_single_claim(registry[claim])
                self.assertEqual(result.outcome, "PASS", f"{claim} ({invariant}): {result.message}")

    def test_every_sibling_goes_facade_when_nothing_is_planted(self) -> None:
        """The mutation that matters: a fixture that stops planting must redden."""
        import tempfile
        from pathlib import Path

        from gzkit.enforcement import _run_single_claim

        registry = self._registry()
        for claim in self.SIBLINGS:
            with self.subTest(claim=claim):
                gutted = registry[claim].model_copy(
                    update={"fixture": lambda: Path(tempfile.mkdtemp(prefix="gzkit-nc-mut-"))}
                )
                self.assertEqual(
                    _run_single_claim(gutted).outcome,
                    "FACADE",
                    f"{claim} still passes with nothing planted — it is not "
                    "actually certifying its invariant.",
                )


class TestHandoffPopulatedSectionsFixtureIsolation(unittest.TestCase):
    """GHI #698: the present-but-empty fixture must fail ONLY on the empty-section check.

    If it also failed for another reason (bad frontmatter, a missing heading),
    deleting ``validate_sections_populated`` would leave it red for that other
    reason and the control would never notice the deletion — the exact
    under-scoping this GHI names. Every blocking finding must be an
    ``Empty required section`` finding.
    """

    def test_fixture_isolates_the_empty_section_finding(self) -> None:
        from gzkit.governance.trust_audits._qc_nc_composite import (
            build_handoff_populated_sections,
        )
        from gzkit.quality import run_handoff_document_audit

        root = build_handoff_populated_sections()
        result = run_handoff_document_audit(root)

        self.assertFalse(result.success, "a present-but-empty handoff must fail the audit")
        finding_lines = [
            line for line in result.stdout.splitlines() if line.startswith(".gzkit/handoffs/")
        ]
        self.assertTrue(finding_lines, f"expected blocking findings; got: {result.stdout!r}")
        for line in finding_lines:
            self.assertIn(
                "Empty required section",
                line,
                f"fixture fails for a non-empty-section reason (breaks isolation): {line}",
            )


class TestRemainingClaimsBite(unittest.TestCase):
    """The claims whose fixtures previously bailed before reaching their verdict.

    Each was green for a reason unrelated to its claim: `behave` died on
    `ConfigError: No steps directory`, `preflight` on "gzkit not initialized",
    `readiness-audit` on an empty project failing all six required surfaces at
    once (GHI #699).
    """

    CLAIMS = ("behave", "preflight", "parity-check", "readiness-audit")

    @staticmethod
    def _registry() -> dict:
        from gzkit.enforcement import (
            _ensure_production_claims_registered,
            get_enforcement_registry,
        )

        _ensure_production_claims_registered()
        return {r.claim_id: r for r in get_enforcement_registry()}

    def test_each_claim_passes_on_its_planted_violation(self) -> None:
        from gzkit.enforcement import _run_single_claim

        registry = self._registry()
        for claim in self.CLAIMS:
            with self.subTest(claim=claim):
                result = _run_single_claim(registry[claim])
                self.assertEqual(result.outcome, "PASS", result.message)

    def test_each_claim_goes_facade_on_a_bare_directory(self) -> None:
        """A bare dir is the shape every one of these previously accepted."""
        import tempfile
        from pathlib import Path

        from gzkit.enforcement import _run_single_claim

        registry = self._registry()
        for claim in self.CLAIMS:
            with self.subTest(claim=claim):
                gutted = registry[claim].model_copy(
                    update={"fixture": lambda: Path(tempfile.mkdtemp(prefix="gzkit-nc-mut-"))}
                )
                self.assertEqual(
                    _run_single_claim(gutted).outcome,
                    "FACADE",
                    f"{claim} still passes against an empty project — it is "
                    "certifying its own bail-out path, not its claim.",
                )

    def test_no_fixture_builds_its_violation_by_absence(self) -> None:
        """`_build_empty` must have no remaining callers in the claim table."""
        import inspect

        from gzkit.governance.trust_audits import _qc_negative_controls as ncs

        offenders = [
            entry[0]
            for entry in ncs._QC_NEGATIVE_CONTROL_TABLE
            if "_build_empty" in inspect.getsource(entry[1])
        ]

        self.assertEqual(
            offenders,
            [],
            "Violation-by-absence fixtures answer from the validator's "
            f"missing-artifact branch, never the claim's own: {offenders}",
        )


class TestFloorDiscoversProductionClaims(unittest.TestCase):
    """The floor's own control must not exclude production discovery.

    `_ep_enforcement_floor` passes `registry=` explicitly, which skips
    `_ensure_production_claims_registered()`. That is correct for testing FACADE
    detection against a synthetic registry, but it means the discovery seam has
    no coverage from the control that certifies the floor (GHI #699). Enumerating
    unregistered floor members — the ORPHAN class — is #648's cut; this pins only
    that the seam is still wired.
    """

    def test_default_run_registers_production_claims(self) -> None:
        from unittest.mock import patch

        import gzkit.enforcement as enforcement

        with patch.object(enforcement, "_ensure_production_claims_registered") as ensure:
            enforcement.run_meta_validator(registry=[], root=None)

        ensure.assert_not_called()  # explicit registry -> discovery deliberately skipped

        with patch.object(enforcement, "_ensure_production_claims_registered") as ensure:
            enforcement.run_meta_validator(registry=None, root=None)

        ensure.assert_called_once_with()


class TestSubstringChannelIsInvariantUnderColour(unittest.TestCase):
    """The `expect_output` channel must not change verdict with terminal colour (GHI #793).

    GHI #699 established `expect_output` as the ONLY channel that can
    discriminate a genuine finding from an unrelated exit-1 on a gz verb, because
    `GzCliError`, an uncaught exception, and a real finding all exit 1. A channel
    whose answer flips on a presentation setting discriminates nothing.

    Observed 2026-08-12 with `FORCE_COLOR=3` in the environment: `gz preflight`
    caught its planted violation and exited 1, but Rich's number highlighter had
    written SGR codes INSIDE the identifier — `OBPI-[1;36m0.0[0m.[1;36m1[0m-...`
    — so the literal `OBPI-0.0.1-01-demo` did not occur in the captured output and
    the meta-validator reported FACADE against a check that works. `FORCE_COLOR`
    defeats the usual "not a TTY, so no colour" defence precisely because
    `capture_output=True` means the child never has a TTY to begin with.

    A FALSE facade is worse than a silent NC: it argues for deleting working
    enforcement, and it blocked `git commit` through the pre-commit floor, which
    is pressure toward `--no-verify`.
    """

    def test_child_runs_with_colour_disabled_even_when_the_parent_forces_it(self) -> None:
        """The class fix: every `_command_fails_argv` child is pinned colour-off.

        Asserted at the CHANNEL, not at the preflight fixture. Only one of the six
        `expect_output` controls carries a digit-bearing substring today; the other
        five survive by luck of phrasing, and the next NC to assert on a version,
        count, or identifier would reintroduce this without a channel-level pin.
        """
        import os
        import sys
        from unittest.mock import patch

        from gzkit.governance.trust_audits._qc_nc_entrypoints import _command_fails_argv

        root = Path(tempfile.mkdtemp(prefix="gzkit-nc-colour-"))
        probe = (
            "import os, sys;"
            "sys.stdout.write("
            "  os.environ.get('FORCE_COLOR', '<unset>') + '|' "
            "+ os.environ.get('NO_COLOR', '<unset>'));"
            "raise SystemExit(1)"
        )

        with patch.dict(os.environ, {"FORCE_COLOR": "3", "COLORTERM": "truecolor"}):
            signal = _command_fails_argv(
                [sys.executable, "-c", probe],
                root,
                expected_exit=1,
                expect_output="<unset>|1",
            )

        self.assertEqual(
            signal,
            1,
            "A negative-control child must run with colour disabled regardless of "
            "the parent environment. Observed child env was not "
            "FORCE_COLOR=<unset>, NO_COLOR=1 — so Rich may rewrite the very text "
            "the `expect_output` channel matches on, and the control's verdict "
            "becomes a function of the operator's terminal (GHI #793).",
        )

    def test_preflight_verdict_is_the_same_with_and_without_forced_colour(self) -> None:
        """The instance that proved it: same fixture, same claim, both environments.

        Derived from §5 clause (c) — the control asserts the production path fails
        for the reason the claim names — plus the observation that the reason did
        not change when the colour setting did. Asserts EQUALITY of the two
        verdicts and that both are `caught`, so the test fails if the channel
        regains an environmental dependence in either direction.
        """
        import os
        from unittest.mock import patch

        from gzkit.governance.trust_audits._qc_nc_entrypoints import _ep_preflight
        from gzkit.governance.trust_audits._qc_negative_controls import _build_preflight

        with patch.dict(os.environ, {"FORCE_COLOR": "3", "COLORTERM": "truecolor"}):
            forced = _ep_preflight(_build_preflight())

        scrubbed_env = {k: v for k, v in os.environ.items() if k != "FORCE_COLOR"}
        with patch.dict(os.environ, scrubbed_env, clear=True):
            plain = _ep_preflight(_build_preflight())

        self.assertEqual(
            forced,
            plain,
            "The preflight control returned different verdicts under forced colour "
            "versus plain output. The subject did not change between these two "
            "runs — only the presentation did (GHI #793).",
        )
        self.assertEqual(
            forced,
            1,
            "`gz preflight` does catch its planted stale marker and exits 1, so "
            "the control must score CAUGHT. A falsy verdict here is the false "
            "FACADE that accused a working check of being theater.",
        )


if __name__ == "__main__":
    unittest.main()
