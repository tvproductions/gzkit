"""Tests for bullet retention validator (OBPI-0.0.33-01, OBPI-0.0.37-25).

Covers:
    REQ-0.0.33-01-01 — Mechanical/Promotable bullet present in surface → no errors
    REQ-0.0.33-01-02 — Mechanical/Promotable bullet absent from surface → exit-3 ValidationError
    REQ-0.0.33-01-03 — Judgment/Ambiguous bullets are NOT enforced
    REQ-0.0.33-01-04 — validate_bullet_retention resolves from trust_audits re-export
    REQ-0.0.33-01-05 — --bullet-retention flag registered in CLI
    REQ-0.0.37-25-01 — invariant-tier bullet absent/altered → exit-3 (verbatim contract preserved)
    REQ-0.0.37-25-02 — compressible-tier bullet reworded + valid advisor-QC witness → no error
    REQ-0.0.37-25-03 — compressible-tier bullet WITHOUT a valid witness → exit-3 (unwitnessed)

All tests use ``tempfile.TemporaryDirectory`` for sandbox isolation; never
write to the live repo root.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.content import advisor_qc
from gzkit.content.models.corpus import Corpus, CorpusEntry
from gzkit.governance.trust_audits.bullet_retention import validate_bullet_retention
from gzkit.ledger import Ledger
from gzkit.ledger_events import rendition_advisor_verdict_event
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Minimal synthetic scorecard tables
# ---------------------------------------------------------------------------

_SCORECARD_MECHANICAL = """\
| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | use uv run for commands | **Mechanical** | enforced by hook |
"""

_SCORECARD_PROMOTABLE = """\
| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | top-level imports only | **Promotable** | partially enforced |
"""

_SCORECARD_JUDGMENT = """\
| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | read agents before work | **Judgment** | pre-work discipline |
"""

_SCORECARD_AMBIGUOUS = """\
| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | some ambiguous rule | **Ambiguous** | unclear scope |
"""

_SCORECARD_MIXED = """\
| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | use uv run for commands | **Mechanical** | enforced by hook |
| 2 | read agents before work | **Judgment** | pre-work discipline |
| 3 | top-level imports only | **Promotable** | partially enforced |
"""


def _make_tree(
    tmp: str,
    scorecard_content: str,
    agents_content: str = "",
    claude_content: str = "",
    rule_content: str | None = None,
) -> Path:
    """Seed a minimal project root for bullet-retention tests.

    Creates:
      docs/governance/advisory-rules-audit.md  ← scorecard
      AGENTS.md                                 ← per-turn surface (optional body)
      CLAUDE.md                                 ← per-turn surface (optional body)
      .claude/rules/test-rule.md               ← per-turn rule (when rule_content given)
    """
    root = Path(tmp)
    scorecard_path = root / "docs" / "governance" / "advisory-rules-audit.md"
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    scorecard_path.write_text(scorecard_content, encoding="utf-8")

    (root / "AGENTS.md").write_text(agents_content, encoding="utf-8")
    (root / "CLAUDE.md").write_text(claude_content, encoding="utf-8")

    if rule_content is not None:
        rules_dir = root / ".claude" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        (rules_dir / "test-rule.md").write_text(rule_content, encoding="utf-8")

    return root


class TestBulletPresentReturnsNoErrors(unittest.TestCase):
    """Mechanical or Promotable bullet present verbatim in surface → no ValidationError."""

    @covers("REQ-0.0.33-01-01")
    def test_mechanical_bullet_in_agents_md_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                agents_content="use uv run for commands when executing Python",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                errors,
                [],
                "A Mechanical bullet present verbatim in AGENTS.md must produce no errors",
            )

    @covers("REQ-0.0.33-01-01")
    def test_promotable_bullet_in_claude_md_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_PROMOTABLE,
                claude_content="top-level imports only — standard library first",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(errors, [], "A Promotable bullet in CLAUDE.md must produce no errors")

    @covers("REQ-0.0.33-01-01")
    def test_bullet_in_rules_dir_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                rule_content="use uv run for commands in all shell invocations",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                errors,
                [],
                "A Mechanical bullet found under .claude/rules/** must produce no errors",
            )

    @covers("REQ-0.0.33-01-01")
    def test_bullet_with_different_surrounding_whitespace_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                agents_content="  -  use uv run for commands  (binding)  ",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                errors,
                [],
                "Whitespace and bullet-marker variation must not prevent a match",
            )


class TestBulletAbsentReturnsError(unittest.TestCase):
    """Mechanical or Promotable bullet absent from per-turn surface → exit-3 ValidationError."""

    @covers("REQ-0.0.33-01-02")
    def test_missing_mechanical_bullet_emits_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                agents_content="this surface does not contain the rule",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(len(errors), 1, "Exactly one error expected for one missing bullet")

    @covers("REQ-0.0.33-01-02")
    def test_missing_bullet_error_type_is_bullet_retention(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                agents_content="unrelated text",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(errors[0].type, "bullet_retention")

    @covers("REQ-0.0.33-01-02")
    def test_missing_bullet_error_names_the_bullet_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                agents_content="unrelated text",
            )
            errors = validate_bullet_retention(root)
            self.assertIn(
                "use uv run for commands",
                errors[0].message,
                "Error message must name the missing bullet text",
            )

    @covers("REQ-0.0.33-01-02")
    def test_missing_bullet_error_names_classification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                agents_content="unrelated text",
            )
            errors = validate_bullet_retention(root)
            self.assertIn(
                "Mechanical",
                errors[0].message,
                "Error message must name the source classification",
            )

    @covers("REQ-0.0.33-01-02")
    def test_missing_promotable_bullet_also_emits_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_PROMOTABLE,
                agents_content="unrelated content only",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, "bullet_retention")

    @covers("REQ-0.0.33-01-02")
    def test_empty_surface_corpus_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
            )
            errors = validate_bullet_retention(root)
            self.assertGreater(
                len(errors),
                0,
                "Empty surface corpus must not silently pass for enforced bullets",
            )


class TestJudgmentAndAmbiguousNotEnforced(unittest.TestCase):
    """Judgment/Ambiguous bullets are NOT enforced regardless of surface content."""

    @covers("REQ-0.0.33-01-03")
    def test_judgment_bullet_absent_from_surface_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_JUDGMENT,
                agents_content="this surface mentions nothing about the judgment rule",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                errors,
                [],
                "Judgment bullets must not be enforced even when absent from the surface",
            )

    @covers("REQ-0.0.33-01-03")
    def test_ambiguous_bullet_absent_from_surface_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_AMBIGUOUS,
                agents_content="surface does not contain ambiguous content",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                errors,
                [],
                "Ambiguous bullets must not be enforced",
            )

    @covers("REQ-0.0.33-01-03")
    def test_mixed_scorecard_only_enforces_mechanical_and_promotable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # Only Mechanical and Promotable bullets present; Judgment absent
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MIXED,
                agents_content=(
                    "use uv run for commands and top-level imports only"
                    " — both Mechanical/Promotable bullets satisfied here"
                ),
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                errors,
                [],
                "Mixed scorecard: only enforced bullets need to be in the surface",
            )

    @covers("REQ-0.0.33-01-03")
    def test_mixed_scorecard_still_errors_when_enforced_bullet_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MIXED,
                agents_content="read agents before work — only the judgment rule is here",
            )
            errors = validate_bullet_retention(root)
            self.assertGreater(
                len(errors),
                0,
                "Missing Mechanical/Promotable bullets must still emit errors",
            )
            for err in errors:
                self.assertEqual(err.type, "bullet_retention")


class TestPackageReExport(unittest.TestCase):
    """validate_bullet_retention resolves from the trust_audits package re-export."""

    @covers("REQ-0.0.33-01-04")
    def test_validate_bullet_retention_importable_from_trust_audits(self) -> None:
        from gzkit.governance.trust_audits import validate_bullet_retention as fn

        self.assertTrue(callable(fn))

    @covers("REQ-0.0.33-01-04")
    def test_function_signature_accepts_path(self) -> None:
        import inspect

        sig = inspect.signature(validate_bullet_retention)
        params = list(sig.parameters)
        self.assertEqual(
            params,
            ["project_root"],
            "Function must accept exactly project_root: Path",
        )

    @covers("REQ-0.0.33-01-04")
    def test_function_returns_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(tmp, scorecard_content="no table here\n")
            result = validate_bullet_retention(root)
            self.assertIsInstance(result, list)


class TestCLIFlagRegistered(unittest.TestCase):
    """--bullet-retention appears in gz validate --help output."""

    @covers("REQ-0.0.33-01-05")
    def test_bullet_retention_flag_in_help(self) -> None:
        import io
        from contextlib import redirect_stderr, redirect_stdout

        from gzkit.cli import main

        output = io.StringIO()
        try:
            with redirect_stdout(output), redirect_stderr(output):
                main(["validate", "--help"])
        except SystemExit:
            pass
        help_text = output.getvalue()
        self.assertIn(
            "--bullet-retention",
            help_text,
            "gz validate --bullet-retention must be registered in CLI",
        )


# ---------------------------------------------------------------------------
# Tier-scoped enforcement (OBPI-0.0.37-25) — fixtures
# ---------------------------------------------------------------------------

_TIER_BULLET = "use uv run for commands"
_TIER_SURFACE = "AGENTS.md"

_SCORECARD_TIER = """\
| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | use uv run for commands | **Mechanical** | enforced by hook |
"""


def _seed_corpus(root: Path, *, tier: str, text: str, surface: str = _TIER_SURFACE) -> None:
    """Write a one-entry per-surface corpus store carrying *tier* for *text*."""
    entry = CorpusEntry(
        id=f"corpus-tier-test-{tier}",
        surface=surface,
        section="execution-rules",
        tier=tier,
        classification="Mechanical",
        text=text,
        origin="tier-scoped-test",
        ts="2026-06-15T00:00:00+00:00",
    )
    store = root / ".gzkit" / "corpus" / f"{surface}.jsonl"
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(Corpus(entries=(entry,)).dumps() + "\n", encoding="utf-8")


def _seed_advisor_witness(
    root: Path,
    *,
    surface: str = _TIER_SURFACE,
    exit_status: int = 0,
    run_id: str | None = None,
) -> str:
    """Record a real advisor-QC receipt + verdict event for *surface*; return its receipt_id.

    Uses the production ``record_verdict`` engine so the fixture exercises the
    real receipt envelope the validator reads. ``exit_status`` is patched onto
    the written receipt to model a non-zero (invalid-witness) case. The returned
    receipt_id is the exact linkage the validator follows
    (``rendition_advisor_verdict.receipt_id`` → ``<receipt_id>.json``); the
    receipts root is env-pinned by the caller via ``GZKIT_ARB_RECEIPTS_ROOT``.
    """
    resolved_run_id = run_id if run_id is not None else f"arb-step-judge-{'a' * 32}"
    receipt_path = advisor_qc.record_verdict(
        root=root,
        surface=surface,
        consumer=None,
        explanation="All retained; two bullets combined without information loss.",
        score=0.95,
        run_id=resolved_run_id,
        timestamp="2026-06-15T00:00:00Z",
    )
    if exit_status != 0:
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        payload["exit_status"] = exit_status
        receipt_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    Ledger(root / ".gzkit" / "ledger.jsonl").append(
        rendition_advisor_verdict_event(
            surface=surface,
            consumer=None,
            receipt_id=receipt_path.stem,
            score=0.95,
        )
    )
    return receipt_path.stem


class TestInvariantTierVerbatimContract(unittest.TestCase):
    """REQ-0.0.37-25-01 — invariant-tier content keeps the Era-1 verbatim contract."""

    @covers("REQ-0.0.37-25-01")
    def test_invariant_tier_bullet_absent_fails_closed(self) -> None:
        """An invariant-tier bullet absent from the rendered surface fails closed."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_TIER,
                agents_content="this surface omits the invariant bullet text entirely",
            )
            _seed_corpus(root, tier="invariant", text=f"{_TIER_BULLET} when executing Python")
            errors = validate_bullet_retention(root)
            self.assertEqual(
                len(errors),
                1,
                "An invariant-tier bullet missing from the surface must fail closed (exit 3)",
            )
            self.assertEqual(errors[0].type, "bullet_retention")

    @covers("REQ-0.0.37-25-01")
    def test_invariant_tier_bullet_present_is_clean(self) -> None:
        """An invariant-tier bullet present verbatim in the surface produces no error."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_TIER,
                agents_content=f"{_TIER_BULLET} when executing Python",
            )
            _seed_corpus(root, tier="invariant", text=f"{_TIER_BULLET} when executing Python")
            errors = validate_bullet_retention(root)
            self.assertEqual(errors, [], "Invariant-tier bullet present verbatim must be clean")

    @covers("REQ-0.0.37-25-01")
    def test_unknown_tier_falls_back_to_invariant_verbatim(self) -> None:
        """A bullet that maps to no corpus entry uses the conservative invariant fallback."""
        with tempfile.TemporaryDirectory() as tmp:
            # No corpus store seeded → tier unknown → invariant verbatim contract.
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_TIER,
                agents_content="this surface does not contain the rule text",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                len(errors),
                1,
                "Unknown-tier bullet must fall back to the verbatim contract and fail closed",
            )


class TestCompressibleTierWitnessedRetention(unittest.TestCase):
    """REQ-0.0.37-25-02 — compressible-tier retention is satisfied by a valid advisor-QC witness."""

    @covers("REQ-0.0.37-25-02")
    def test_compressible_reworded_with_valid_witness_passes(self) -> None:
        """A reworded compressible bullet carrying a valid witness must NOT fail."""
        with tempfile.TemporaryDirectory() as tmp:
            receipts = Path(tmp) / "receipts"
            with mock.patch.dict(os.environ, {"GZKIT_ARB_RECEIPTS_ROOT": str(receipts)}):
                root = _make_tree(
                    tmp,
                    # Surface is reworded — it does NOT contain the bullet verbatim.
                    scorecard_content=_SCORECARD_TIER,
                    agents_content="invoke python through the uv runner for every command",
                )
                _seed_corpus(root, tier="compressible", text=f"{_TIER_BULLET} in all shells")
                _seed_advisor_witness(root)
                errors = validate_bullet_retention(root)
                self.assertEqual(
                    errors,
                    [],
                    "Compressible bullet with a valid advisor-QC witness must not fail "
                    "even when reworded (no verbatim requirement at the compressible tier)",
                )

    @covers("REQ-0.0.37-25-02")
    def test_compressible_with_witness_does_not_require_verbatim(self) -> None:
        """The witnessed compressible path is independent of verbatim surface presence."""
        with tempfile.TemporaryDirectory() as tmp:
            receipts = Path(tmp) / "receipts"
            with mock.patch.dict(os.environ, {"GZKIT_ARB_RECEIPTS_ROOT": str(receipts)}):
                root = _make_tree(
                    tmp,
                    scorecard_content=_SCORECARD_TIER,
                    agents_content="",  # empty surface — verbatim would fail, witness saves it
                )
                _seed_corpus(root, tier="compressible", text=f"{_TIER_BULLET} in all shells")
                _seed_advisor_witness(root)
                errors = validate_bullet_retention(root)
                self.assertEqual(
                    errors,
                    [],
                    "A valid witness satisfies compressible retention regardless of the "
                    "rendered surface's verbatim content",
                )


class TestCompressibleTierUnwitnessedFailsClosed(unittest.TestCase):
    """REQ-0.0.37-25-03 — compressible-tier without a valid witness fails closed."""

    @covers("REQ-0.0.37-25-03")
    def test_compressible_without_any_witness_fails_closed(self) -> None:
        """A compressible bullet with no advisor-QC verdict event fails closed (exit 3)."""
        with tempfile.TemporaryDirectory() as tmp:
            receipts = Path(tmp) / "receipts"
            with mock.patch.dict(os.environ, {"GZKIT_ARB_RECEIPTS_ROOT": str(receipts)}):
                root = _make_tree(
                    tmp,
                    scorecard_content=_SCORECARD_TIER,
                    agents_content="reworded surface text without the verbatim bullet",
                )
                _seed_corpus(root, tier="compressible", text=f"{_TIER_BULLET} in all shells")
                # No verdict event / receipt seeded → retention is unwitnessed.
                errors = validate_bullet_retention(root)
                self.assertEqual(
                    len(errors),
                    1,
                    "Compressible retention without a witness must fail closed — the "
                    "compressible tier is not an unconditional retention escape",
                )
                self.assertEqual(errors[0].type, "bullet_retention")

    @covers("REQ-0.0.37-25-03")
    def test_compressible_with_nonzero_exit_status_receipt_fails_closed(self) -> None:
        """A verdict whose receipt carries a non-zero exit_status is not a valid witness."""
        with tempfile.TemporaryDirectory() as tmp:
            receipts = Path(tmp) / "receipts"
            with mock.patch.dict(os.environ, {"GZKIT_ARB_RECEIPTS_ROOT": str(receipts)}):
                root = _make_tree(
                    tmp,
                    scorecard_content=_SCORECARD_TIER,
                    agents_content="reworded surface text without the verbatim bullet",
                )
                _seed_corpus(root, tier="compressible", text=f"{_TIER_BULLET} in all shells")
                _seed_advisor_witness(root, exit_status=1)
                errors = validate_bullet_retention(root)
                self.assertEqual(
                    len(errors),
                    1,
                    "A receipt with exit_status != 0 is not a valid retention witness",
                )

    @covers("REQ-0.0.37-25-03")
    def test_compressible_witness_for_other_surface_does_not_satisfy(self) -> None:
        """A verdict event for a different surface does not witness this surface's retention."""
        with tempfile.TemporaryDirectory() as tmp:
            receipts = Path(tmp) / "receipts"
            with mock.patch.dict(os.environ, {"GZKIT_ARB_RECEIPTS_ROOT": str(receipts)}):
                root = _make_tree(
                    tmp,
                    scorecard_content=_SCORECARD_TIER,
                    agents_content="reworded surface text without the verbatim bullet",
                )
                _seed_corpus(root, tier="compressible", text=f"{_TIER_BULLET} in all shells")
                # Witness recorded for a DIFFERENT surface than the corpus entry's.
                _seed_advisor_witness(root, surface="CLAUDE.md")
                errors = validate_bullet_retention(root)
                self.assertEqual(
                    len(errors),
                    1,
                    "A witness for another surface must not satisfy this surface's retention",
                )

    @covers("REQ-0.0.37-25-03")
    def test_latest_verdict_governs_clean_then_invalid_fails_closed(self) -> None:
        """When the LATEST verdict is invalid, an earlier valid one does not rescue retention."""
        with tempfile.TemporaryDirectory() as tmp:
            receipts = Path(tmp) / "receipts"
            with mock.patch.dict(os.environ, {"GZKIT_ARB_RECEIPTS_ROOT": str(receipts)}):
                root = _make_tree(
                    tmp,
                    scorecard_content=_SCORECARD_TIER,
                    agents_content="reworded surface text without the verbatim bullet",
                )
                _seed_corpus(root, tier="compressible", text=f"{_TIER_BULLET} in all shells")
                # Earlier verdict is valid; later (latest) verdict is invalid → latest governs.
                _seed_advisor_witness(root, run_id=f"arb-step-judge-{'a' * 32}")
                _seed_advisor_witness(root, exit_status=1, run_id=f"arb-step-judge-{'b' * 32}")
                errors = validate_bullet_retention(root)
                self.assertEqual(
                    len(errors),
                    1,
                    "The latest verdict event governs — a superseded valid receipt must not "
                    "rescue retention once a later invalid verdict lands",
                )

    @covers("REQ-0.0.37-25-02")
    def test_latest_verdict_governs_invalid_then_clean_passes(self) -> None:
        """When the LATEST verdict is valid, an earlier invalid one does not block retention."""
        with tempfile.TemporaryDirectory() as tmp:
            receipts = Path(tmp) / "receipts"
            with mock.patch.dict(os.environ, {"GZKIT_ARB_RECEIPTS_ROOT": str(receipts)}):
                root = _make_tree(
                    tmp,
                    scorecard_content=_SCORECARD_TIER,
                    agents_content="reworded surface text without the verbatim bullet",
                )
                _seed_corpus(root, tier="compressible", text=f"{_TIER_BULLET} in all shells")
                # Earlier verdict is invalid; later (latest) verdict is valid → latest governs.
                _seed_advisor_witness(root, exit_status=1, run_id=f"arb-step-judge-{'a' * 32}")
                _seed_advisor_witness(root, run_id=f"arb-step-judge-{'b' * 32}")
                errors = validate_bullet_retention(root)
                self.assertEqual(
                    errors,
                    [],
                    "The latest verdict event governs — a later valid receipt witnesses "
                    "retention even after an earlier invalid verdict",
                )


if __name__ == "__main__":
    unittest.main()
