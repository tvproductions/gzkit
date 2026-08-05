"""Clause-coverage enforcement for the advisory scorecard (GHI #754).

`audit_advisory_scorecard` asserted only that a rule file's *filename stem*
appeared somewhere in `docs/governance/advisory-rules-audit.md`. Its docstring
promised the scorecard stays "a complete index" -- complete over *files*, never
over *rules*. Two consequences shipped undetected:

* `.gzkit/rules/tests.md` gained `§ Verification exit-code integrity` in rule
  version `0.8.0` (GHI #589) and it was never scored -- the stem `tests` was
  already present, so the audit could not see the addition.
* Scorecard row 60 still asserted `tasks:` enforcement was "deferred to
  OBPI-0.0.64-04" after `task-discovery.md` `0.7.0` (GHI #753) declared it LIVE
  and retired the deferral -- a row contradicting the rule it scores.

The anchor is the `<!-- rule-version: X.Y.Z -->` marker, which
`gz validate --rule-version-markers` already enforces on every canonical rule.
The scorecard declares which version of each rule it was scored against; a bump
that is not reflected there is unreviewed coverage. This is version-string
equality, never prose or shape grading -- deliberately so, because a heuristic
clause extractor would reintroduce the `shape-graded-not-substance` theater
signature this audit exists to catch (ADR-0.0.73; `theater_signature_scan`
§ "Deliberately NOT detected").
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.governance.trust_audits import audit_advisory_scorecard

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

_RULE_BODY = """---
name: sample
---

<!-- rule-version: {version} -->

> **Rule version:** `{version}` -- sample.

## Invariant

**Something binding.**
"""

_LEDGER = """# Advisory Rules Audit

## Coverage Ledger

| Rule file | Scored at rule-version |
|---|---|
{rows}

### Sample (`.gzkit/rules/sample.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | Something binding | **Judgment** | prose |
"""


def _build(root: Path, *, rule_version: str, scored_version: str | None) -> None:
    """Write a minimal project with one rule and one scorecard."""
    rules = root / ".gzkit" / "rules"
    rules.mkdir(parents=True)
    (rules / "sample.md").write_text(_RULE_BODY.format(version=rule_version), encoding="utf-8")
    gov = root / "docs" / "governance"
    gov.mkdir(parents=True)
    rows = "" if scored_version is None else f"| `sample.md` | `{scored_version}` |"
    (gov / "advisory-rules-audit.md").write_text(_LEDGER.format(rows=rows), encoding="utf-8")


class AdvisoryScorecardClauseCoverage(unittest.TestCase):
    """The audit must track rule *versions*, not merely rule *filenames*."""

    def test_rule_bumped_past_its_scored_version_is_a_finding(self) -> None:
        """A rule edited after it was scored is unreviewed coverage.

        This is the row-60 shape: `task-discovery.md` reached `0.7.0` while the
        scorecard still described its `0.5.x` behavior. Under the filename-stem
        check this was invisible, because the stem never stopped matching.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build(root, rule_version="0.7.0", scored_version="0.5.0")
            errors = audit_advisory_scorecard(root)
        self.assertTrue(
            errors,
            "A rule whose current version exceeds its scored version must be a "
            "finding; the scorecard has not been reviewed against the new clauses.",
        )
        self.assertIn("0.7.0", " ".join(e.message for e in errors))

    def test_rule_absent_from_the_coverage_ledger_is_a_finding(self) -> None:
        """A rule with no ledger entry has never been scored at any version."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build(root, rule_version="0.1.0", scored_version=None)
            errors = audit_advisory_scorecard(root)
        self.assertTrue(errors, "A rule missing from the coverage ledger must be a finding.")

    def test_rule_scored_at_its_current_version_is_clean(self) -> None:
        """Version equality is the pass condition -- no false positives."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build(root, rule_version="0.3.1", scored_version="0.3.1")
            errors = audit_advisory_scorecard(root)
        self.assertEqual([], errors, f"Matching versions must pass; got {errors}")

    def test_filename_presence_alone_does_not_satisfy_the_audit(self) -> None:
        """The regression guard: the old proxy must no longer be sufficient.

        The pre-GHI-754 implementation was `if stem in scorecard_text: continue`.
        Here the stem `sample` appears in the scorecard body, but the rule is
        absent from the coverage ledger. If this test passes with zero errors,
        the filename proxy has returned.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build(root, rule_version="0.1.0", scored_version=None)
            scorecard = root / "docs" / "governance" / "advisory-rules-audit.md"
            self.assertIn("sample", scorecard.read_text(encoding="utf-8"))
            errors = audit_advisory_scorecard(root)
        self.assertTrue(
            errors,
            "Filename presence must not satisfy the audit -- that is the "
            "shape-graded-not-substance proxy GHI #754 removed.",
        )


class AdvisoryScorecardLiveTree(unittest.TestCase):
    """The live repository must satisfy the strengthened audit."""

    def test_live_tree_is_clean(self) -> None:
        errors = audit_advisory_scorecard(_PROJECT_ROOT)
        self.assertEqual(
            [],
            errors,
            "Every canonical rule must be scored at its current rule-version. "
            "Recovery: review the rule's clauses, update its scorecard rows, and "
            "bump its row in the scorecard's Coverage Ledger.\n"
            + "\n".join(f"  - {e.artifact}: {e.message}" for e in errors),
        )


if __name__ == "__main__":
    unittest.main()
