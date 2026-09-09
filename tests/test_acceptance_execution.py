"""Executable acceptance proof checks use contract literals and real subprocess controls."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.acceptance_execution import (
    canonical_obligations,
    digest_components,
    input_digest,
    prove,
)
from gzkit.mutation_witness import Mutation

REQ = "REQ-0.1.0-01-01"
SELECTOR = "tests.test_engine.EngineTests.test_double"
BRIEF = """---
id: OBPI-0.1.0-01-engine
parent: ADR-0.1.0-engine
reqs:
- REQ-0.1.0-01-01
---
# Engine
## Objective
Double the input.
## Allowed Paths
- src/engine.py
## Acceptance Criteria
- [ ] REQ-0.1.0-01-01 [BEHAVIOR]: Double two to four.
## Evidence
Historical round one was wrong.
"""
TEST = """import unittest
from src.engine import double

def covers(req):
    return lambda function: function

class EngineTests(unittest.TestCase):
    @covers("REQ-0.1.0-01-01")
    def test_double(self):
        self.assertEqual(double(2), 4)
"""


class ExecutionFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.brief = self.root / "design/adr/obpis/brief.md"
        self.write("design/adr/obpis/brief.md", BRIEF)
        self.write(
            "design/adr/ADR-0.1.0-engine.md",
            "## Decision\nMultiply by two.\n## Evidence\nOld review.\n",
        )
        self.write("src/__init__.py", "")
        self.write("src/engine.py", "def double(value):\n    return value * 2\n")
        self.write("tests/__init__.py", "")
        self.write("tests/test_engine.py", TEST)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def run_proof(self):
        return prove(
            self.root,
            self.brief,
            REQ,
            source=Path("src/engine.py"),
            selectors=[SELECTOR],
            mutations=[
                Mutation(
                    find="return value * 2",
                    replace="return value * 3",
                    label="triples instead of doubles",
                    expected_tests=[SELECTOR],
                )
            ],
        )


class AcceptanceInputTests(ExecutionFixture):
    def test_declared_execution_condition_changes_claim_without_changing_artifact(self):
        """AS-5: only explicitly nominated conditions affect this proof claim."""
        with patch(
            "gzkit.acceptance_execution._behavior_evidence",
            return_value=({"control": "killed"}, True),
        ):
            with patch.dict("os.environ", {"ENGINE_MODE": "one"}):
                first = prove(self.root, self.brief, REQ, environment_keys=("ENGINE_MODE",))
            with patch.dict("os.environ", {"ENGINE_MODE": "two"}):
                changed = prove(self.root, self.brief, REQ, environment_keys=("ENGINE_MODE",))
        self.assertEqual(first.input_digest, changed.input_digest)
        self.assertNotEqual(first.claim_digest, changed.claim_digest)
        self.assertEqual(first.environment_keys, ("ENGINE_MODE",))

    def test_producer_claim_ignores_run_timing_but_retains_actual_results(self):
        """AS-4/AS-5: only execution occurrence noise is outside claim identity."""
        from gzkit.acceptance_execution import proof_claim_digest

        payload = {"command": ["uv", "run"], "output": "Ran 1 test in 0.100s\n4 != 6"}
        digest = proof_claim_digest(self.root, payload)
        self.assertEqual(
            digest,
            proof_claim_digest(
                self.root,
                {
                    **payload,
                    "output": "Ran 1 test in 0.999s\n4 != 6",
                },
            ),
        )
        for changed in (
            {**payload, "output": "Ran 1 test in 0.100s\n2 != 9"},
            {**payload, "command": ["another-runner"]},
            {**payload, "conditions": {"FEATURE": "on"}},
        ):
            self.assertNotEqual(digest, proof_claim_digest(self.root, changed))

    def test_obligation_comes_from_contract_not_historical_analysis(self):
        (obligation,) = canonical_obligations(self.root, self.brief)
        self.assertEqual(
            (obligation.id, obligation.kind, obligation.statement),
            (REQ, "BEHAVIOR", "Double two to four."),
        )

    def test_history_changes_preserve_digest_but_contract_changes_invalidate(self):
        before = input_digest(self.root, self.brief)
        self.brief.write_text(
            BRIEF.replace("Historical round one was wrong.", "Fixed historical typo."),
            encoding="utf-8",
        )
        self.assertEqual(input_digest(self.root, self.brief), before)
        self.brief.write_text(
            BRIEF.replace("Double two to four.", "Triple two to six."), encoding="utf-8"
        )
        self.assertNotEqual(input_digest(self.root, self.brief), before)

    def test_source_addition_change_and_removal_invalidate_without_git(self):
        original = input_digest(self.root, self.brief)
        added = self.write("src/new_dependency.py", "VALUE = 1\n")
        addition = input_digest(self.root, self.brief)
        self.assertNotEqual(addition, original)
        added.write_text("VALUE = 2\n", encoding="utf-8")
        self.assertNotEqual(input_digest(self.root, self.brief), addition)
        added.unlink()
        self.assertEqual(input_digest(self.root, self.brief), original)

    def test_configured_source_root_is_included(self):
        self.write(".gzkit.json", json.dumps({"paths": {"source_root": "application"}}))
        self.write("application/engine.py", "VALUE = 1\n")
        before = input_digest(self.root, self.brief)
        self.write("application/engine.py", "VALUE = 2\n")
        self.assertNotEqual(input_digest(self.root, self.brief), before)

    def test_unrelated_environment_does_not_invalidate_the_reviewed_inputs(self):
        """An ambient variable is not a reviewed input (GHI #989).

        The digest answers "were these the reviewed INPUTS" -- the file roster
        and the contract. A reviewer's own process environment is provenance of
        its execution, never identity of what it read. Hashing it made a review
        executed in another process (the mandated tier-1 cross-vendor adversary,
        CI, a second terminal) structurally unimportable: it copies the digest it
        was handed, and the importing process recomputes a different one from an
        unchanged tree.
        """
        with patch.dict("os.environ", {"ACCEPTANCE_TEST_FEATURE": "one"}):
            before = input_digest(self.root, self.brief)
        with patch.dict("os.environ", {"ACCEPTANCE_TEST_FEATURE": "two"}):
            self.assertEqual(input_digest(self.root, self.brief), before)
        with patch.dict("os.environ", {"CI": "true"}):
            self.assertEqual(input_digest(self.root, self.brief), before)

    def test_a_reviewed_input_still_invalidates_under_a_changed_environment(self):
        """Negative control: the guard still bites when an actual input changes.

        Stability under ambient variables must not be bought by making the digest
        insensitive. A real edit inside the audited population still moves it,
        even while an unrelated variable is also changing.
        """
        with patch.dict("os.environ", {"ACCEPTANCE_TEST_FEATURE": "one"}):
            before = input_digest(self.root, self.brief)
        self.write("src/engine.py", "def double(value):\n    return value * 4\n")
        with patch.dict("os.environ", {"ACCEPTANCE_TEST_FEATURE": "two"}):
            self.assertNotEqual(input_digest(self.root, self.brief), before)

    def test_digest_components_name_the_two_reviewed_terms(self):
        """`digest_components` exposes which term moved, so a refusal can say so.

        The refusal previously read "stale file contents" whichever term differed,
        sending a reader to look for a file change that need not exist (GHI #989).
        """
        components = digest_components(self.root, self.brief)
        self.assertEqual(set(components), {"files", "contract"})
        self.write("src/engine.py", "def double(value):\n    return value * 5\n")
        moved = digest_components(self.root, self.brief)
        self.assertNotEqual(moved["files"], components["files"])
        self.assertEqual(moved["contract"], components["contract"])

    def test_missing_requirement_declaration_cannot_shrink_obligations(self):
        self.brief.write_text(
            BRIEF.replace("- [ ] REQ-0.1.0-01-01", "- REQ-0.1.0-01-01"), encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "unique parsed requirements"):
            canonical_obligations(self.root, self.brief)

    def test_nonmatching_frontmatter_roster_is_refused(self):
        self.brief.write_text(
            BRIEF.replace("reqs:\n- REQ-0.1.0-01-01", "reqs:\n- REQ-0.1.0-01-02"), encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "roster disagrees"):
            canonical_obligations(self.root, self.brief)

    def test_wrong_covering_selector_is_rejected_before_execution(self):
        with patch("gzkit.acceptance_execution.run_mutation_sweep") as run:
            with self.assertRaisesRegex(ValueError, "must cover"):
                prove(
                    self.root,
                    self.brief,
                    REQ,
                    source=Path("src/engine.py"),
                    selectors=["tests.test_engine.EngineTests.test_unrelated"],
                    mutations=[
                        Mutation(find="2", replace="3", label="wrong", expected_tests=[SELECTOR])
                    ],
                )
            run.assert_not_called()

    def test_test_file_cannot_be_used_as_semantic_production_control(self):
        with self.assertRaisesRegex(ValueError, "production source"):
            prove(
                self.root,
                self.brief,
                REQ,
                source=Path("tests/test_engine.py"),
                selectors=[SELECTOR],
                mutations=[
                    Mutation(
                        find="4", replace="6", label="changed oracle", expected_tests=[SELECTOR]
                    )
                ],
            )

    def test_parent_contract_change_invalidates_and_history_does_not(self):
        before = input_digest(self.root, self.brief)
        self.write(
            "design/adr/ADR-0.1.0-engine.md",
            "## Decision\nMultiply by two.\n## Evidence\nCorrected review.\n",
        )
        self.assertEqual(input_digest(self.root, self.brief), before)
        self.write("design/adr/ADR-0.1.0-engine.md", "## Decision\nMultiply by three.\n")
        self.assertNotEqual(input_digest(self.root, self.brief), before)


class ExecutedBehaviorTests(ExecutionFixture):
    def test_real_semantic_counterexample_is_killed_and_original_behavior_restored(self):
        proof = self.run_proof()
        payload = json.loads(proof.evidence)
        self.assertTrue(proof.valid, proof.evidence)
        self.assertEqual(payload["sweep"]["witnesses"][0]["outcome"], "killed")
        self.assertIn("6 != 4", payload["sweep"]["witnesses"][0]["output_tail"])
        self.assertEqual(payload["restored"]["executed_tests"], [SELECTOR])
        self.assertEqual(
            (self.root / "src/engine.py").read_text(encoding="utf-8"),
            "def double(value):\n    return value * 2\n",
        )

    def test_hollow_test_passing_broken_production_is_invalid_proof(self):
        self.write(
            "tests/test_engine.py",
            TEST.replace("self.assertEqual(double(2), 4)", "self.assertEqual(4, 4)"),
        )
        proof = self.run_proof()
        self.assertFalse(proof.valid)
        self.assertEqual(json.loads(proof.evidence)["sweep"]["witnesses"][0]["outcome"], "survived")

    def test_always_refusing_implementation_cannot_satisfy_positive_baseline(self):
        self.write("src/engine.py", "def double(value):\n    raise ValueError('refused')\n")
        proof = self.run_proof()
        self.assertFalse(proof.valid)
        self.assertFalse(json.loads(proof.evidence)["sweep"]["baseline_green"])

    def test_runtime_error_in_nominated_test_is_not_semantic_proof(self):
        proof = prove(
            self.root,
            self.brief,
            REQ,
            source=Path("src/engine.py"),
            selectors=[SELECTOR],
            mutations=[
                Mutation(
                    find="return value * 2",
                    replace="return value + None",
                    label="unusable runtime",
                    expected_tests=[SELECTOR],
                )
            ],
        )
        self.assertFalse(proof.valid)
        self.assertEqual(
            json.loads(proof.evidence)["sweep"]["witnesses"][0]["outcome"], "inconclusive"
        )

    def test_mutant_side_effect_invalidates_even_when_required_assertion_kills_it(self):
        proof = prove(
            self.root,
            self.brief,
            REQ,
            source=Path("src/engine.py"),
            selectors=[SELECTOR],
            mutations=[
                Mutation(
                    find="return value * 2",
                    replace="from pathlib import Path\n"
                    "    Path('src/residue.py').write_text('x=1')\n"
                    "    return value * 3",
                    label="triples and leaves residue",
                    expected_tests=[SELECTOR],
                )
            ],
        )
        evidence = json.loads(proof.evidence)
        self.assertEqual(evidence["sweep"]["witnesses"][0]["outcome"], "killed")
        self.assertNotEqual(evidence["input_before"], evidence["input_after"])
        self.assertFalse(proof.valid)


class ExistingProofChannelTests(ExecutionFixture):
    def test_structural_fence_uses_anchored_parent_resolver_without_mutating(self):
        self.write(".gzkit.json", json.dumps({"paths": {"adrs": "docs/design/adr"}}))
        self.write(
            "docs/design/adr/ADR-0.1.0-engine/ADR-0.1.0-engine.md",
            "## Boundary Invariants\nBI-01: Identity is retained (OBPI-01).\n",
        )
        self.brief.write_text(BRIEF.replace("[BEHAVIOR]", "[STRUCTURAL-FENCE]"), encoding="utf-8")
        proof = prove(self.root, self.brief, REQ)
        self.assertTrue(proof.valid)
        evidence = json.loads(proof.evidence)
        self.assertEqual(evidence["resolver"], "gzkit.req_kind_fence.resolve_fence_proof")
        self.assertEqual(evidence["result"], "pass")
        self.assertEqual(proof.selectors, ())

    def test_missing_fence_anchor_does_not_generate_valid_proof(self):
        self.brief.write_text(BRIEF.replace("[BEHAVIOR]", "[STRUCTURAL-FENCE]"), encoding="utf-8")
        proof = prove(self.root, self.brief, REQ)
        self.assertFalse(proof.valid)
        self.assertEqual(json.loads(proof.evidence)["result"], "unproven-fence")

    def test_undeclared_support_witness_is_invalid(self):
        self.brief.write_text(BRIEF.replace("[BEHAVIOR]", "[SUPPORT]"), encoding="utf-8")
        proof = prove(self.root, self.brief, REQ)
        self.assertFalse(proof.valid)
        self.assertEqual(json.loads(proof.evidence)["result"], "undeclared-support")
