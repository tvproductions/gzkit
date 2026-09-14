"""Tests for the evaluation-justify-binding gate (OBPI-0.0.26-02, GHI #996).

Gate fires when an ``adr-evaluation`` ledger event has low dimension scores
or enough red-team challenges and no qualifying ``gz-justify`` artifact exists.

A qualifying artifact is completed reasoning about the evaluated subject, never
a directory entry whose name happens to match (GHI #996): it parses as a
walkthrough, every section is filled, its own frontmatter names the evaluated
subject, and it was generated at or after the evaluation it answers.

@covers OBPI-0.0.26-02-justify-binding-gate
"""

from __future__ import annotations

import json
import re
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from gzkit.governance.trust_audits.evaluation_justify_binding import (
    validate_evaluation_justify_binding,
)
from gzkit.justify.models import AnchorRef, EvidenceBundle
from gzkit.justify.walkthrough import render_markdown, render_scaffold
from gzkit.lifecycle import LifecycleStateMachine
from gzkit.traceability import covers

_EVALUATED_AT = "2026-01-01T00:00:00+00:00"
_AFTER_EVALUATION = datetime(2026, 1, 2, tzinfo=UTC)


def _write_thresholds(root: Path, *, low_score: float = 3.0) -> None:
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "eval_feedback_thresholds.json").write_text(
        json.dumps({"low_score_threshold": low_score, "red_team_count_threshold": 3}),
        encoding="utf-8",
    )


def _write_ledger_event(
    root: Path,
    artifact_id: str,
    dimensions: dict,
    red_team_challenges_fired: list | None = None,
) -> None:
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "schema": "gzkit.ledger.v1",
        "event": "adr-evaluation",
        "id": artifact_id,
        "dimensions": dimensions,
        "scores": dimensions,
        "weighted_total": sum(dimensions.values()) / len(dimensions),
        "red_team_challenges_fired": red_team_challenges_fired or [],
        "evaluator_persona": "main-session",
        "timestamp": _EVALUATED_AT,
        "ts": _EVALUATED_AT,
    }
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")


def _triggered_project(root: Path, artifact_id: str = "ADR-0.0.26") -> None:
    """A project whose latest evaluation of ``artifact_id`` trips the low-score trigger."""
    _write_thresholds(root)
    _write_ledger_event(root, artifact_id, {"clarity": 1.5, "structure": 4.0})


def _draft_anchor(slug: str) -> AnchorRef:
    return AnchorRef(kind="draft", draft_slug=slug, draft_text="reasoning", body="reasoning")


def _walkthrough(
    anchor: AnchorRef,
    *,
    generated_at: datetime = _AFTER_EVALUATION,
    filled: bool = True,
) -> str:
    """Render a walkthrough through the real producer, optionally with every section filled."""
    evidence = EvidenceBundle(
        anchor=anchor, taxonomy_reference="docs/governance/model-regression-taxonomy.md"
    )
    walkthrough = render_scaffold(anchor, evidence, now=generated_at)
    if filled:
        sections = [
            section.model_copy(update={"reasoning": f"Grounded reasoning {section.ordinal}."})
            for section in walkthrough.sections
        ]
        walkthrough = walkthrough.model_copy(update={"sections": sections})
    return render_markdown(walkthrough)


def _write_justify(root: Path, name: str, content: str) -> Path:
    justify_dir = root / "artifacts" / "justify"
    justify_dir.mkdir(parents=True, exist_ok=True)
    path = justify_dir / name
    path.write_text(content, encoding="utf-8")
    return path


class TestEvaluationJustifyBindingGate(unittest.TestCase):
    """Verify the evaluation-justify-binding gate returns correct results."""

    @covers("REQ-0.0.26-02-01")
    def test_low_score_no_justify_artifact_exits_3(self) -> None:
        """Low score + no justify artifact → ValidationError naming the failing dimension."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _triggered_project(root)

            result = validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

            self.assertEqual(len(result), 1, "Expected a ValidationError for low score")
            self.assertEqual(result[0].type, "evaluation-justify-binding")
            self.assertIn("clarity", result[0].message)

    @covers("REQ-0.0.26-02-02")
    def test_red_team_count_no_justify_artifact_exits_3(self) -> None:
        """Sufficient red-team challenges with no justify artifact returns ValidationError."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_thresholds(root)
            _write_ledger_event(
                root,
                "ADR-0.0.26",
                {"clarity": 4.0, "structure": 4.0},
                red_team_challenges_fired=["challenge-1", "challenge-2", "challenge-3"],
            )

            result = validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

            self.assertEqual(len(result), 1, "Expected a ValidationError for red-team count")
            self.assertEqual(result[0].type, "evaluation-justify-binding")

    @covers("REQ-0.0.26-02-03")
    def test_trigger_fires_justify_artifact_present_exits_0(self) -> None:
        """A complete walkthrough about the evaluated ADR, written after it, discharges the gate."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _triggered_project(root)
            _write_justify(
                root, "adr-0-0-26-20260102.md", _walkthrough(_draft_anchor("adr-0-0-26"))
            )

            result = validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

            self.assertEqual(result, [], f"Expected empty list but got: {result}")

    @covers("REQ-0.0.26-02-04")
    def test_no_trigger_all_scores_high_exits_0(self) -> None:
        """All dimensions >= threshold and no red-team challenges — gate passes (empty list)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_thresholds(root)
            _write_ledger_event(root, "ADR-0.0.26", {"clarity": 4.0, "structure": 5.0})

            result = validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

            self.assertEqual(result, [], f"Expected empty list but got: {result}")

    @covers("REQ-0.0.26-02-05")
    def test_threshold_config_reflected(self) -> None:
        """Custom threshold config is respected — score passing at 3.0 fails at 4.0."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_thresholds(root, low_score=4.0)
            _write_ledger_event(root, "ADR-0.0.26", {"clarity": 3.5})

            result = validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

            self.assertEqual(len(result), 1, "Expected gate to fire below the custom threshold")
            self.assertEqual(result[0].type, "evaluation-justify-binding")

    def test_no_adr_evaluation_events_returns_empty(self) -> None:
        """Empty ledger (no adr-evaluation events) — gate passes (empty list)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_thresholds(root)

            result = validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

            self.assertEqual(result, [], f"Expected empty list but got: {result}")


class TestPresentButFalseEvidenceIsRefused(unittest.TestCase):
    """Something present under the subject's name is not the reasoning ADR-0.0.26 requires.

    Each case plants a triggered evaluation next to evidence that EXISTS and is
    NOT a completed walkthrough. A gate that counts presence admits every one.
    """

    def _assert_refused(self, root: Path, artifact_id: str = "ADR-0.0.26") -> None:
        result = validate_evaluation_justify_binding(artifact_id, project_root=root)
        self.assertEqual(len(result), 1, f"present-but-false evidence was admitted: {result}")
        self.assertEqual(result[0].type, "evaluation-justify-binding")

    @covers("REQ-0.0.26-02-01")
    def test_empty_file_named_for_the_subject_is_refused(self) -> None:
        """The GHI #996 reproduction: a zero-byte file discharged required reasoning."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _triggered_project(root)
            _write_justify(root, "adr-0-0-26-20260102.md", "")

            self._assert_refused(root)

    @covers("REQ-0.0.26-02-01")
    def test_malformed_file_named_for_the_subject_is_refused(self) -> None:
        """Prose that does not parse as a walkthrough is not a walkthrough."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _triggered_project(root)
            _write_justify(root, "adr-0-0-26-20260102.md", "# Justify\n\nRationale here.")

            self._assert_refused(root)

    @covers("REQ-0.0.26-02-01")
    def test_unfilled_scaffold_for_the_subject_is_refused(self) -> None:
        """A scaffold whose reasoning is still placeholder has not been reasoned through."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _triggered_project(root)
            _write_justify(
                root,
                "adr-0-0-26-20260102.md",
                _walkthrough(_draft_anchor("adr-0-0-26"), filled=False),
            )

            self._assert_refused(root)

    @covers("REQ-0.0.26-02-01")
    def test_directory_named_for_the_subject_is_refused(self) -> None:
        """A directory entry is not a file, let alone reasoning."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _triggered_project(root)
            (root / "artifacts" / "justify" / "adr-0-0-26-20260102.md").mkdir(parents=True)

            self._assert_refused(root)


class TestSubjectIdentity(unittest.TestCase):
    """The walkthrough's own frontmatter must name the evaluated subject.

    Short and full ids bind only where they denote the same ADR or OBPI: the same
    semver, with slugs equal or one of them absent. String prefixes never bind.
    """

    def _result(self, artifact_id: str, anchor: AnchorRef) -> list:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _triggered_project(root, artifact_id)
            _write_justify(root, "adr-0-0-26-20260102.md", _walkthrough(anchor))
            return validate_evaluation_justify_binding(artifact_id, project_root=root)

    @covers("REQ-0.0.26-02-03")
    def test_same_subject_binds_across_short_and_full_ids(self) -> None:
        cases = [
            ("ADR-0.35.0-canon-entry-corpus-landing", _draft_anchor("adr-0-35-0")),
            ("ADR-0.35.0", _draft_anchor("adr-0-35-0-canon-entry-corpus-landing")),
            (
                "ADR-0.0.73-verification-layer-binding-audit",
                _draft_anchor("adr-0-0-73-verification-layer-binding-audit"),
            ),
            (
                "OBPI-0.26.0-03-cluster-chore",
                AnchorRef(kind="obpi", identifier="OBPI-0.26.0-03", body="brief"),
            ),
        ]
        for artifact_id, anchor in cases:
            with self.subTest(
                artifact_id=artifact_id, anchor=anchor.identifier or anchor.draft_slug
            ):
                self.assertEqual(self._result(artifact_id, anchor), [])

    @covers("REQ-0.0.26-02-03")
    def test_an_obpi_under_the_evaluated_adr_answers_it(self) -> None:
        """Operator ruling 2026-09-14 ("Draft slug or OBPI (Recommended)").

        `gz-adr-evaluate` routes a low ADR score to a walkthrough on an OBPI under the
        ADR, because an implementing agent lands short of confidence on one of them.
        """
        for artifact_id in ("ADR-0.35.0", "ADR-0.35.0-canon-entry-corpus-landing"):
            with self.subTest(artifact_id=artifact_id):
                anchor = AnchorRef(kind="obpi", identifier="OBPI-0.35.0-05", body="brief")
                self.assertEqual(self._result(artifact_id, anchor), [])

    @covers("REQ-0.0.26-02-01")
    def test_a_different_subject_never_binds(self) -> None:
        cases = [
            (
                "ADR-0.35.0",
                AnchorRef(kind="obpi", identifier="OBPI-0.36.0-05", body="brief"),
                "an OBPI under a different ADR",
            ),
            (
                "ADR-0.3.0",
                AnchorRef(kind="obpi", identifier="OBPI-0.33.0-01", body="brief"),
                "an OBPI whose ADR semver shares leading digits",
            ),
            (
                "OBPI-0.35.0-05-corpus-candidate-generator",
                _draft_anchor("adr-0-35-0"),
                "the parent ADR's walkthrough does not answer an OBPI's evaluation",
            ),
            (
                "ADR-0.0.26",
                AnchorRef(kind="obpi", identifier="ADR-0.0.26", body="brief"),
                "an obpi-kind anchor carrying an ADR id is malformed, not an OBPI",
            ),
            ("ADR-0.0.26", _draft_anchor("adr-0-0-27"), "different ADR"),
            ("ADR-0.0.26", _draft_anchor("adr-0-0-2"), "string prefix of the id"),
            ("ADR-0.3.0", _draft_anchor("adr-0-33-0"), "semver sharing leading digits"),
            ("ADR-0.35.0-canon-entry-corpus-landing", _draft_anchor("adr-0-35-0-other"), "slug"),
            (
                "OBPI-0.26.0-03-cluster-chore",
                AnchorRef(kind="obpi", identifier="OBPI-0.26.0-04", body="brief"),
                "different OBPI item",
            ),
            (
                "ADR-0.0.26",
                AnchorRef(kind="ghi", identifier="GHI-996", body="ADR-0.0.26"),
                "a GHI anchor is never the evaluated subject",
            ),
        ]
        for artifact_id, anchor, why in cases:
            with self.subTest(why=why):
                result = self._result(artifact_id, anchor)
                self.assertEqual(len(result), 1, f"{why}: wrong-subject walkthrough admitted")


class TestReasoningAnswersThisEvaluation(unittest.TestCase):
    """Reasoning generated before the evaluation cannot answer it (ADR-0.0.26 Decision 2).

    The evaluation's time is its schema-required ``timestamp``; the ledger ``ts``
    stands in when ``timestamp`` is absent.
    """

    def _result(self, event_times: dict, generated_at: datetime) -> list:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_thresholds(root)
            ledger = root / ".gzkit" / "ledger.jsonl"
            ledger.parent.mkdir(parents=True)
            event = {
                "event": "adr-evaluation",
                "id": "ADR-0.0.26",
                "dimensions": {"clarity": 1.0},
                "red_team_challenges_fired": [],
                **event_times,
            }
            ledger.write_text(json.dumps(event) + "\n", encoding="utf-8")
            _write_justify(
                root,
                "adr-0-0-26.md",
                _walkthrough(_draft_anchor("adr-0-0-26"), generated_at=generated_at),
            )
            return validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

    @covers("REQ-0.0.26-02-01")
    def test_reasoning_that_predates_the_evaluation_is_refused(self) -> None:
        before = datetime(2025, 12, 31, tzinfo=UTC)
        cases = [
            ({"timestamp": _EVALUATED_AT, "ts": _EVALUATED_AT}, before, "timestamp"),
            ({"ts": _EVALUATED_AT}, before, "ts when timestamp is absent"),
            ({}, _AFTER_EVALUATION, "an evaluation with no recorded time cannot be answered"),
        ]
        for times, generated_at, why in cases:
            with self.subTest(why=why):
                self.assertEqual(len(self._result(times, generated_at)), 1)

    @covers("REQ-0.0.26-02-03")
    def test_reasoning_at_or_after_the_evaluation_is_admitted(self) -> None:
        at = datetime(2026, 1, 1, tzinfo=UTC)
        cases = [
            ({"timestamp": _EVALUATED_AT}, at, "same instant"),
            ({"timestamp": _EVALUATED_AT}, _AFTER_EVALUATION, "after"),
            ({"ts": _EVALUATED_AT}, _AFTER_EVALUATION, "after ts when timestamp is absent"),
        ]
        for times, generated_at, why in cases:
            with self.subTest(why=why):
                self.assertEqual(self._result(times, generated_at), [])


class TestRefusalRecoveryOutputContract(unittest.TestCase):
    """The refusal is three-part recovery prose (`.gzkit/rules/guardrail-feedback-prose.md`).

    The next step it names must be satisfiable: before GHI #996 the recovery was
    `justify <artifact-id> --save`, which `gz justify` refuses for every ADR id.
    """

    def _finding_message(self, artifact_id: str, root: Path) -> str:
        result = validate_evaluation_justify_binding(artifact_id, project_root=root)
        self.assertEqual(len(result), 1, f"expected one refusal for {artifact_id}: {result}")
        return result[0].message

    def test_refused_candidates_are_named_with_their_reason(self) -> None:
        # output-contract: the finding names what was refused and why
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _triggered_project(root)
            _write_justify(root, "adr-0-0-26-empty.md", "")
            _write_justify(
                root, "adr-0-0-26-draft.md", _walkthrough(_draft_anchor("adr-0-0-26"), filled=False)
            )
            _write_justify(root, "adr-0-0-26-other.md", _walkthrough(_draft_anchor("adr-0-0-27")))

            message = self._finding_message("ADR-0.0.26", root)

            for name in ("adr-0-0-26-empty.md", "adr-0-0-26-draft.md", "adr-0-0-26-other.md"):
                self.assertIn(f"artifacts/justify/{name}", message)
            self.assertIn("not a parseable walkthrough", message)
            self.assertIn("unfilled", message)
            self.assertIn("adr-0-0-27", message)
            self.assertIn("ADR-0.0.26 Decision 2", message)
            self.assertIn("uv run gz justify validate", message)

    def test_the_named_producer_step_closes_the_loop(self) -> None:
        """Following the recovery command yields a walkthrough the gate admits."""
        cases = [
            ("ADR-0.35.0-canon-entry-corpus-landing", r"--draft-slug (\S+)", "draft"),
            ("OBPI-0.26.0-03-cluster-chore", r"uv run gz justify (OBPI-\S+) --save", "obpi"),
        ]
        for artifact_id, pattern, kind in cases:
            with self.subTest(artifact_id=artifact_id), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _triggered_project(root, artifact_id)
                message = self._finding_message(artifact_id, root)
                self.assertNotIn(f"gz justify {artifact_id} ", message)
                match = re.search(pattern, message)
                self.assertIsNotNone(match, f"no runnable producer step in: {message}")
                assert match is not None
                named = match.group(1)
                anchor = (
                    _draft_anchor(named)
                    if kind == "draft"
                    else AnchorRef(kind="obpi", identifier=named, body="brief")
                )
                _write_justify(root, "followed-recovery.md", _walkthrough(anchor))

                self.assertEqual(
                    validate_evaluation_justify_binding(artifact_id, project_root=root), []
                )


class TestLifecycleConsumesTheQualifier(unittest.TestCase):
    """The lifecycle transition gate (ADR-0.0.26 Decision 2) inherits the same qualifier."""

    @covers("REQ-0.0.26-02-01")
    def test_draft_to_proposed_refuses_present_but_false_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _triggered_project(root)
            _write_justify(root, "adr-0-0-26-20260102.md", "")

            with self.assertRaises(ValueError) as ctx:
                LifecycleStateMachine(project_root=root).transition(
                    "ADR-0.0.26", "ADR", "Draft", "Proposed"
                )
            self.assertIn("Lifecycle gate blocked", str(ctx.exception))

    @covers("REQ-0.0.26-02-03")
    def test_draft_to_proposed_admits_a_qualifying_walkthrough(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _triggered_project(root)
            _write_justify(root, "reasoning.md", _walkthrough(_draft_anchor("adr-0-0-26")))

            try:
                result = LifecycleStateMachine(project_root=root).transition(
                    "ADR-0.0.26", "ADR", "Draft", "Proposed"
                )
            except ValueError as exc:
                self.fail(f"a qualifying walkthrough was refused at the lifecycle gate: {exc}")
            self.assertEqual(result["to_state"], "Proposed")


if __name__ == "__main__":
    unittest.main()
