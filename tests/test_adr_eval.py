"""Tests for the ADR/OBPI deterministic evaluation engine."""

import tempfile
import unittest
from pathlib import Path

from gzkit.adr_eval import (
    AdrEvalResult,
    DimensionScore,
    EvalVerdict,
    ObpiDimensionScores,
    RedTeamChallengeResult,
    _passes_to_score,
    compute_verdict,
    evaluate_adr,
    render_scorecard_markdown,
    resolve_adr_package,
    score_adr_deterministic,
    score_obpis_deterministic,
)


class TestPassesToScore(unittest.TestCase):
    def test_all_pass(self) -> None:
        self.assertEqual(_passes_to_score(4, 4), 4)

    def test_all_but_one(self) -> None:
        self.assertEqual(_passes_to_score(3, 4), 3)

    def test_more_than_half(self) -> None:
        self.assertEqual(_passes_to_score(3, 5), 2)

    def test_half_or_fewer(self) -> None:
        self.assertEqual(_passes_to_score(2, 5), 1)

    def test_zero_total(self) -> None:
        self.assertEqual(_passes_to_score(0, 0), 1)


class TestResolveAdrPackage(unittest.TestCase):
    def test_finds_adr_and_obpis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_dir = root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.1.0-test"
            obpi_dir = adr_dir / "obpis"
            obpi_dir.mkdir(parents=True)
            adr_file = adr_dir / "ADR-0.1.0-test.md"
            adr_file.write_text("# ADR-0.1.0\n", encoding="utf-8")
            (obpi_dir / "OBPI-0.1.0-01-foo.md").write_text("# OBPI\n", encoding="utf-8")
            (obpi_dir / "OBPI-0.1.0-02-bar.md").write_text("# OBPI\n", encoding="utf-8")

            path, content, obpis = resolve_adr_package(root, "ADR-0.1.0")
            self.assertEqual(path, adr_file)
            self.assertEqual(len(obpis), 2)

    def test_raises_on_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "design" / "adr").mkdir(parents=True)
            with self.assertRaises(FileNotFoundError):
                resolve_adr_package(root, "ADR-99.0.0")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_STRONG_ADR = """\
---
id: ADR-0.1.0-test
status: Proposed
lane: heavy
parent: PRD-TEST
---

# ADR-0.1.0-test: Test ADR

## Intent

Before this ADR, the system had no existing capability for widget processing.
The current state requires manual intervention for every widget. After this
change, widgets will be processed automatically with full observability.
This targets the core processing pipeline and is explicitly scoped to the
widget domain only.

## Decision

The decision is to implement a widget processor because the manual approach
does not scale. The rationale is that automated processing reduces errors by
90%.

1. Use event-driven architecture because it decouples producers from consumers
2. Store state in SQLite because it is portable and requires no server

## Alternatives Considered

- Manual processing: rejected because it does not scale beyond 100 widgets/day
- Redis queues: rejected because it adds operational complexity without benefit
  at our current volume

## Consequences

### Positive

- Automated processing reduces errors by 90%

### Negative

- Adds a new runtime dependency on SQLite

## Non-Goals

- Real-time streaming is explicitly out of scope for this ADR
- Multi-tenant isolation is not addressed here
- Cloud deployment patterns are excluded from this scope

## Checklist

- [ ] OBPI-0.1.0-01: Define widget processor command contract
- [ ] OBPI-0.1.0-02: Implement widget state persistence

## Decomposition Scorecard

- Final Target OBPI Count: 2
"""

_STRONG_OBPI = """\
---
id: OBPI-0.1.0-01-define-widget-processor
parent: ADR-0.1.0-test
lane: Heavy
status: Draft
---

# OBPI-0.1.0-01: Define widget processor command contract

## Objective

Define the CLI command contract for the widget processor including
subcommands, flags, exit codes, and output schemas that operators
will use to manage automated widget processing.

## Allowed Paths

- `src/gzkit/widget.py` - Widget processor implementation
- `tests/test_widget.py` - Widget processor tests
- `docs/user/commands/widget.md` - Command documentation

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Widget processor must accept --input and --output flags
2. REQUIREMENT: Exit code 0 on success, 1 on validation error
3. NEVER: Do not write to stdout in --json mode except valid JSON
4. ALWAYS: Include --help with usage examples

## Quality Gates

### Gate 2: TDD

- [ ] Tests pass: `uv run gz test`
- [ ] Widget-specific tests: `uv run -m unittest tests.test_widget -v`

## Acceptance Criteria

- [ ] REQ-0.1.0-01-01: Given valid input, when processor runs, then exit 0
- [ ] REQ-0.1.0-01-02: Given invalid input, when processor runs, then exit 1
- [ ] REQ-0.1.0-01-03: Given --json flag, when processor runs, then stdout is valid JSON

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.test_widget -v
```
"""

_SCAFFOLD_OBPI = """\
---
id: OBPI-0.1.0-01-scaffold
parent: ADR-0.1.0-test
lane: Heavy
status: Draft
---

# OBPI-0.1.0-01-scaffold

## Objective

Define widget processor command contract.

## Allowed Paths

- `src/module/` - Reason this is in scope
- `tests/test_module.py` - Reason

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: First constraint
1. REQUIREMENT: Second constraint
1. NEVER: What must not happen
1. ALWAYS: What must always be true

## Quality Gates

### Gate 2: TDD

- [ ] Tests pass: `uv run gz test`

## Acceptance Criteria

- [ ] REQ-0.1.0-01-01: Given/When/Then behavior criterion 1
- [ ] REQ-0.1.0-01-02: Given/When/Then behavior criterion 2

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
command --to --verify
```
"""


class TestAdrDimensionScoring(unittest.TestCase):
    """Test deterministic ADR dimension scoring with real and weak content."""

    def _score_strong(self) -> list[DimensionScore]:
        obpi_paths = [Path("OBPI-0.1.0-01.md"), Path("OBPI-0.1.0-02.md")]
        return score_adr_deterministic(_STRONG_ADR, 2, obpi_paths, [_STRONG_OBPI, _STRONG_OBPI])

    def test_strong_adr_scores_above_threshold(self) -> None:
        dims = self._score_strong()
        total = sum(d.weighted for d in dims)
        self.assertGreaterEqual(total, 2.5, f"Strong ADR should score >= 2.5, got {total:.2f}")

    def test_weak_adr_scores_low(self) -> None:
        weak = "---\nid: ADR-0.1.0\nstatus: Draft\n---\n\n# ADR\n\n## Intent\n\nDo stuff.\n"
        dims = score_adr_deterministic(weak, 0, [], [])
        total = sum(d.weighted for d in dims)
        self.assertLess(total, 2.5, f"Weak ADR should score < 2.5, got {total:.2f}")

    def test_all_eight_dimensions_scored(self) -> None:
        dims = self._score_strong()
        self.assertEqual(len(dims), 8)


class TestObpiDimensionScoring(unittest.TestCase):
    def test_strong_obpi_scores_well(self) -> None:
        path = Path("OBPI-0.1.0-01-define-widget-processor.md")
        scores = score_obpis_deterministic([path], [_STRONG_OBPI])
        self.assertEqual(len(scores), 1)
        self.assertGreaterEqual(scores[0].average, 2.5)

    def test_scaffold_obpi_scores_poorly(self) -> None:
        path = Path("OBPI-0.1.0-01-scaffold.md")
        scores = score_obpis_deterministic([path], [_SCAFFOLD_OBPI])
        self.assertEqual(len(scores), 1)
        self.assertLess(scores[0].average, 3.0)

    def test_five_dimensions_scored(self) -> None:
        path = Path("OBPI-0.1.0-01.md")
        scores = score_obpis_deterministic([path], [_STRONG_OBPI])
        obpi = scores[0]
        for dim in [obpi.independence, obpi.testability, obpi.value, obpi.size, obpi.clarity]:
            self.assertGreaterEqual(dim, 1)
            self.assertLessEqual(dim, 4)


class TestVerdictComputation(unittest.TestCase):
    def _make_obpi(self, avg: float = 3.5, min_dim: int = 3) -> ObpiDimensionScores:
        return ObpiDimensionScores(
            obpi_id="OBPI-test",
            independence=min_dim,
            testability=min_dim,
            value=min_dim,
            size=min_dim,
            clarity=min_dim,
            average=avg,
        )

    def test_go_verdict(self) -> None:
        verdict, items = compute_verdict(3.2, [self._make_obpi(3.5)])
        self.assertEqual(verdict, EvalVerdict.GO)
        self.assertEqual(items, [])

    def test_conditional_go_on_adr_threshold(self) -> None:
        verdict, _ = compute_verdict(2.7, [self._make_obpi(3.5)])
        self.assertEqual(verdict, EvalVerdict.CONDITIONAL_GO)

    def test_no_go_on_low_adr(self) -> None:
        verdict, _ = compute_verdict(2.0, [self._make_obpi(3.5)])
        self.assertEqual(verdict, EvalVerdict.NO_GO)

    def test_no_go_on_obpi_dimension_1(self) -> None:
        verdict, items = compute_verdict(3.5, [self._make_obpi(2.0, min_dim=1)])
        self.assertEqual(verdict, EvalVerdict.NO_GO)
        self.assertTrue(any("scored 1" in i for i in items))

    def test_conditional_on_obpi_average_below_3(self) -> None:
        verdict, _ = compute_verdict(3.5, [self._make_obpi(2.5, min_dim=2)])
        self.assertIn(verdict, {EvalVerdict.CONDITIONAL_GO, EvalVerdict.NO_GO})

    def test_boundary_exactly_3_0(self) -> None:
        verdict, _ = compute_verdict(3.0, [self._make_obpi(3.0)])
        self.assertEqual(verdict, EvalVerdict.GO)

    def test_boundary_2_99(self) -> None:
        verdict, _ = compute_verdict(2.99, [self._make_obpi(3.5)])
        self.assertEqual(verdict, EvalVerdict.CONDITIONAL_GO)

    def test_red_team_5_failures_no_go(self) -> None:
        rt = [
            RedTeamChallengeResult(
                challenge_number=i, challenge_name=f"C{i}", passed=i > 5, notes=""
            )
            for i in range(1, 11)
        ]
        verdict, _ = compute_verdict(3.5, [self._make_obpi(3.5)], rt)
        self.assertEqual(verdict, EvalVerdict.NO_GO)

    def test_red_team_2_failures_go(self) -> None:
        rt = [
            RedTeamChallengeResult(
                challenge_number=i, challenge_name=f"C{i}", passed=i > 2, notes=""
            )
            for i in range(1, 11)
        ]
        verdict, _ = compute_verdict(3.5, [self._make_obpi(3.5)], rt)
        self.assertEqual(verdict, EvalVerdict.GO)


class TestScorecardRendering(unittest.TestCase):
    def test_renders_markdown(self) -> None:
        result = AdrEvalResult(
            adr_id="ADR-0.1.0",
            adr_dimensions=[
                DimensionScore(
                    dimension="Problem Clarity",
                    weight=0.15,
                    score=3,
                    weighted=0.45,
                    findings=[],
                )
            ],
            adr_weighted_total=3.0,
            obpi_scores=[
                ObpiDimensionScores(
                    obpi_id="OBPI-0.1.0-01",
                    independence=3,
                    testability=3,
                    value=3,
                    size=3,
                    clarity=3,
                    average=3.0,
                )
            ],
            red_team_results=None,
            verdict=EvalVerdict.GO,
            action_items=[],
            timestamp="2026-03-21T00:00:00+00:00",
        )
        md = render_scorecard_markdown(result)
        self.assertIn("ADR EVALUATION SCORECARD", md)
        self.assertIn("ADR-0.1.0", md)
        self.assertIn("[x] GO", md)
        self.assertIn("3.00/4.0", md)


class TestEvaluateAdr(unittest.TestCase):
    def _make_project(self, adr_content: str, obpi_contents: list[str]) -> Path:
        import tempfile

        tmp = tempfile.mkdtemp()
        root = Path(tmp)
        adr_dir = root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.1.0-test"
        obpi_dir = adr_dir / "obpis"
        obpi_dir.mkdir(parents=True)
        (adr_dir / "ADR-0.1.0-test.md").write_text(adr_content, encoding="utf-8")
        for i, content in enumerate(obpi_contents, 1):
            (obpi_dir / f"OBPI-0.1.0-{i:02d}-item.md").write_text(content, encoding="utf-8")
        return root

    def test_strong_adr_returns_go_or_conditional(self) -> None:
        root = self._make_project(_STRONG_ADR, [_STRONG_OBPI, _STRONG_OBPI])
        result = evaluate_adr(root, "ADR-0.1.0")
        self.assertIn(result.verdict, {EvalVerdict.GO, EvalVerdict.CONDITIONAL_GO})
        self.assertGreaterEqual(result.adr_weighted_total, 2.5)

    def test_scaffold_adr_returns_no_go(self) -> None:
        root = self._make_project(_STRONG_ADR, [_SCAFFOLD_OBPI, _SCAFFOLD_OBPI])
        result = evaluate_adr(root, "ADR-0.1.0")
        self.assertEqual(result.verdict, EvalVerdict.NO_GO)


if __name__ == "__main__":
    unittest.main()
