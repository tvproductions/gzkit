"""Uncalled-gate inventory and disclosure (GHI #785).

A gate can exist, be correct, have teeth, and never be asked. Every reachability
mechanism in the repo polices its OWN membership -- the QC registry fail-closes on
an unclassified ``gz check`` step, the enforcement floor on an enrolled claim with
no negative control, the default-tier fence on a default-tier scope outside the
gate -- so none of them can ask *"what exists that is in none of us?"*. These tests
pin the mechanism that asks it: an inventory over every gate, a scan over every
automatic-caller surface, and an accepted-list that can only shrink.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.gate_callers import (
    ACCEPTED_REL,
    audit_gate_callers,
    uncalled_gates,
)


def _project(
    *,
    accepted: list[dict[str, str]] | None = None,
    quality_py: str = "",
    precommit: str = "",
    workflows: dict[str, str] | None = None,
    chores: dict[str, str] | None = None,
    membership: dict[str, object] | None = None,
) -> tempfile.TemporaryDirectory:
    """Build a fixture root carrying the caller surfaces the audit scans."""
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "data").mkdir(parents=True, exist_ok=True)
    if accepted is not None:
        (root / ACCEPTED_REL).write_text(json.dumps({"accepted_gates": accepted}), encoding="utf-8")
    if membership is not None:
        (root / "data" / "check_scope_membership.json").write_text(
            json.dumps(membership), encoding="utf-8"
        )
    quality = root / "src" / "gzkit" / "quality.py"
    quality.parent.mkdir(parents=True, exist_ok=True)
    quality.write_text(quality_py, encoding="utf-8")
    if precommit:
        (root / ".pre-commit-config.yaml").write_text(precommit, encoding="utf-8")
    for name, body in (workflows or {}).items():
        wf = root / ".github" / "workflows" / name
        wf.parent.mkdir(parents=True, exist_ok=True)
        wf.write_text(body, encoding="utf-8")
    for slug, script in (chores or {}).items():
        d = root / ".gzkit" / "chores" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / script).write_text("# gate script\n", encoding="utf-8")
    return tmp


class TestUncalledGateFailsClosed(unittest.TestCase):
    """A gz-check-uncalled scope with no other caller and no acceptance is flagged."""

    def test_scope_with_no_caller_is_flagged(self) -> None:
        with _project(accepted=[]) as d:
            errs = audit_gate_callers(Path(d), gz_check_uncalled_scopes=["lonely_scope"])
        self.assertTrue(errs)
        self.assertIn("lonely_scope", errs[0].artifact)
        self.assertIn("no automatic caller", errs[0].message)

    def test_accepted_scope_is_not_flagged(self) -> None:
        accepted = [{"gate": "validate:lonely_scope", "reason": "expensive; operator-invoked"}]
        with _project(accepted=accepted) as d:
            self.assertEqual(
                audit_gate_callers(Path(d), gz_check_uncalled_scopes=["lonely_scope"]), []
            )


class TestGzCheckHalfIsDelegated(unittest.TestCase):
    """The `gz check` arm is READ from GHI #744's declaration, never re-derived.

    A scope `gz check` invokes is in ``in_check``, so it never enters this
    population — and scanning ``quality.py`` for it here would be a second reader
    free to disagree with the first, the parallel model
    ``.claude/rules/hexagonal-architecture.md`` rule 8 forbids (operator ruling
    2026-08-09).
    """

    def test_membership_file_is_the_population_source(self) -> None:
        membership = {"out_of_check": ["from_the_file"]}
        with _project(accepted=[], membership=membership) as d:
            errs = audit_gate_callers(Path(d))
        self.assertEqual([e.artifact for e in errs], ["validate:from_the_file"])

    def test_unreadable_membership_fails_closed(self) -> None:
        with _project(accepted=[]) as d:
            errs = audit_gate_callers(Path(d))
        self.assertTrue(errs)
        self.assertIn("check_scope_membership.json", errs[0].artifact)

    def test_quality_py_is_not_consulted_for_scopes(self) -> None:
        """Even a literal `gz validate --x` in quality.py does not clear a scope.

        If it did, this module would be answering a question `in_check` already
        answers — and could answer it differently.
        """
        body = 'run_command("uv run gz validate --lonely-scope", cwd=project_root)'
        with _project(accepted=[], quality_py=body) as d:
            errs = audit_gate_callers(Path(d), gz_check_uncalled_scopes=["lonely_scope"])
        self.assertTrue(errs, "quality.py must not be a caller surface for validate scopes")


class TestCallerSurfaceBreadth(unittest.TestCase):
    """A caller on pre-commit or CI counts -- not only ``gz check``.

    This is the defect GHI #785's own measurement carried: it scanned
    ``src/gzkit/quality.py`` alone and reported 41 unreached scopes, three of which
    (``bullet_retention``, ``pointer_anchors``, ``surface_weight``) are invoked by
    ``.pre-commit-config.yaml`` on every commit. A gate whose only caller is
    pre-commit or CI is called; counting it unreached reproduces the
    single-surface blindness the issue names.
    """

    def test_precommit_caller_counts(self) -> None:
        yaml = "        entry: uv run gz validate --hooked-scope\n"
        with _project(accepted=[], precommit=yaml) as d:
            self.assertEqual(
                audit_gate_callers(Path(d), gz_check_uncalled_scopes=["hooked_scope"]), []
            )

    def test_ci_workflow_caller_counts(self) -> None:
        wf = {"ci.yml": "      - run: uv run gz validate --ci-scope\n"}
        with _project(accepted=[], workflows=wf) as d:
            self.assertEqual(audit_gate_callers(Path(d), gz_check_uncalled_scopes=["ci_scope"]), [])


class TestChoreGateScriptPopulation(unittest.TestCase):
    """Chore gate scripts are a second population, in no scope registry at all."""

    def test_chore_script_with_no_caller_is_flagged(self) -> None:
        with _project(accepted=[], chores={"orphan-chore": "check_thing.py"}) as d:
            errs = audit_gate_callers(Path(d), gz_check_uncalled_scopes=[])
        self.assertTrue(errs)
        self.assertIn("orphan-chore", errs[0].artifact)

    def test_chore_script_referenced_by_slug_is_not_flagged(self) -> None:
        body = 'script = _resolve_chore_dir("wired-chore").path / "check_thing.py"'
        with _project(accepted=[], quality_py=body, chores={"wired-chore": "check_thing.py"}) as d:
            self.assertEqual(audit_gate_callers(Path(d), gz_check_uncalled_scopes=[]), [])


class TestAcceptanceMustShrink(unittest.TestCase):
    """An acceptance that no longer applies is itself a finding.

    Without this arm the list never shrinks on its own: wiring a caller would
    leave the stale entry sitting in the file, and the shrink-ratchet baseline
    would keep counting it. The entry must be surrendered when the gate is wired,
    which is what makes the list monotonically drain.
    """

    def test_accepted_scope_that_gained_a_caller_is_flagged(self) -> None:
        accepted = [{"gate": "validate:now_wired", "reason": "stale"}]
        yaml = "        entry: uv run gz validate --now-wired\n"
        with _project(accepted=accepted, precommit=yaml) as d:
            errs = audit_gate_callers(Path(d), gz_check_uncalled_scopes=["now_wired"])
        self.assertTrue(errs)
        self.assertIn("now has an automatic caller", errs[0].message)

    def test_accepted_gate_that_no_longer_exists_is_flagged(self) -> None:
        accepted = [{"gate": "validate:deleted_scope", "reason": "gone"}]
        with _project(accepted=accepted) as d:
            errs = audit_gate_callers(Path(d), gz_check_uncalled_scopes=[])
        self.assertTrue(errs)
        self.assertIn("no longer exists", errs[0].message)


class TestAcceptanceEntryShape(unittest.TestCase):
    """Every acceptance carries a reason -- a bare id records nothing."""

    def test_entry_without_reason_is_flagged(self) -> None:
        with _project(accepted=[{"gate": "validate:x"}], quality_py="") as d:
            errs = audit_gate_callers(Path(d), gz_check_uncalled_scopes=["x"])
        self.assertTrue(errs)
        self.assertIn("reason", errs[0].message)

    def test_missing_accepted_file_fails_closed(self) -> None:
        with _project(accepted=None, quality_py="") as d:
            errs = audit_gate_callers(Path(d), gz_check_uncalled_scopes=["x"])
        self.assertTrue(errs)
        self.assertIn(ACCEPTED_REL.name, errs[0].message)


class TestRecoveryProse(unittest.TestCase):
    """Fail-closed prose carries what failed, why, and the runnable next step.

    Per ``.claude/rules/guardrail-feedback-prose.md`` § Invariant, asserted here
    because that rule's enforcement channel is per-surface covering tests.
    """

    def test_message_carries_three_parts(self) -> None:
        with _project(accepted=[], quality_py="") as d:
            errs = audit_gate_callers(Path(d), gz_check_uncalled_scopes=["lonely_scope"])
        msg = errs[0].message
        self.assertIn("lonely_scope", msg)
        self.assertIn("GHI #785", msg)
        self.assertIn("uv run gz validate --gate-callers", msg)


class TestRealTreeInventory(unittest.TestCase):
    """The committed accepted-list is green over the real tree."""

    def test_committed_accepted_list_is_green(self) -> None:
        errs = audit_gate_callers(Path.cwd())
        self.assertEqual(
            errs, [], f"uncalled-gate inventory not green: {[e.artifact for e in errs]}"
        )

    def test_inventory_reports_every_gate_with_a_verdict(self) -> None:
        """``uncalled_gates`` is the disclosure half: a count, not just a pass/fail."""
        report = uncalled_gates(Path.cwd())
        self.assertGreater(len(report), 0, "inventory found no gates at all")
        self.assertTrue(all(isinstance(g.called, bool) for g in report))


class TestGateCallersGatesItself(unittest.TestCase):
    """The inventory's own scope must not be in the population it reports.

    A gate that detects uncalled gates while itself being uncalled is the exact
    defect wearing the remedy's clothes.

    Note what is NOT asserted here: that `gate_callers` appears in the `in_check`
    list of `data/check_scope_membership.json`. That would read a file and assert
    on its contents -- proving content, not behavior, which
    `.gzkit/rules/tests.md` § The discriminator names as the wrong channel (and
    `gz validate --tautological-test-audit` flags). `test_check_scope_parity`
    already fail-closes on that declaration disagreeing with
    `_build_check_steps()`; duplicating it here would add a second reader without
    adding a witness.
    """

    def test_gate_callers_is_absent_from_its_own_candidate_population(self) -> None:
        """A scope `gz check` invokes is called by definition, so it is not a candidate.

        This is the behavioral form of the self-consistency claim: it exercises
        the derivation and asserts what it produced. If `gate_callers` ever
        appeared here it would mean the derivation had stopped trusting
        `in_check` -- the second-reader-disagreeing-with-the-first failure the
        derive ruling avoided.
        """
        gates = {g.gate for g in uncalled_gates(Path.cwd())}
        self.assertNotIn("validate:gate_callers", gates)


if __name__ == "__main__":
    unittest.main()
