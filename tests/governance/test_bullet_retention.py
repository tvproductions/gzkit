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

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

from gzkit.advisory import advisory_lines
from gzkit.content import advisor_qc
from gzkit.content.corpus_store import append_entry, corpus_path, load_corpus
from gzkit.content.models.corpus import Corpus, CorpusEntry
from gzkit.content.ownership import declaration_path, sections_digest
from gzkit.content.parse import section_id
from gzkit.content.rendition_store import corpus_fingerprint
from gzkit.governance.events import emit_section_ownership_genesis
from gzkit.governance.trust_audits.bullet_retention import (
    audited_population,
    validate_bullet_retention,
)
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


class TestLinkTargetIsLocationRelative(unittest.TestCase):
    """A quoted bullet keeps its words; its link target is relative to where it lives.

    The scorecard (under `docs/`) quotes a rule clause (under `.claude/rules/`).
    A relative link valid beside the rule is dead in the docs site, so the quote
    must be free to repoint the target without failing retention (GHI #803).
    The link TEXT stays under the verbatim contract.
    """

    _SCORECARD = (
        "| # | Rule | Score | Notes |\n|---|------|-------|-------|\n"
        "| 1 | data lives in [`t.json`](https://example.invalid/rules/t.json) "
        "| **Promotable** | note |\n"
    )

    def test_repointed_link_target_still_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=self._SCORECARD,
                rule_content="The data lives in [`t.json`](t.json), a sibling.",
            )
            self.assertEqual(validate_bullet_retention(root), [])

    def test_changed_link_text_still_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=self._SCORECARD,
                rule_content="The data lives in [`other.json`](t.json), a sibling.",
            )
            self.assertEqual(len(validate_bullet_retention(root)), 1)


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


# ---------------------------------------------------------------------------
# Classification reader and source-aware retention (OBPI-0.35.0-10) — fixtures
# ---------------------------------------------------------------------------

_OWNED_RULE = "owned rule alpha must hold"
_UNOWNED_RULE = "hand rule beta must hold"
_OWNED_HEADING = "## Owned Section\n\n"
_UNOWNED_CHUNK = f"## Unowned Section\n{_UNOWNED_RULE}\n"
_OWN_SECTIONS = {"owned-section": "corpus-owned", "unowned-section": "unowned"}
_SCORECARD_SECTION = "fixture-contract"
_OWNED_NOTE = "`source=AGENTS.md#owned-section entry=e-alpha`"


def _scorecard(*rows: tuple[str, str, str, str], heading: str = "Fixture Contract") -> str:
    """Render one scorecard section from ``(number, rule, score, notes)`` rows."""
    lines = [f"### {heading}", "", "| # | Rule | Score | Notes |", "|---|------|-------|-------|"]
    lines.extend(f"| {num} | {rule} | **{score}** | {notes} |" for num, rule, score, notes in rows)
    return "\n".join(lines) + "\n"


def _entry(entry_id: str, classification: str, **fields: str | None) -> CorpusEntry:
    """Build one corpus entry addressed to the fixture's owned section by default."""
    values: dict[str, str | None] = {
        "surface": "AGENTS.md",
        "section": "owned-section",
        "tier": "invariant",
        "text": _OWNED_RULE,
        "origin": "obpi-0.35.0-10-test",
        "ts": "2026-10-03T00:00:00+00:00",
    }
    values.update(fields)
    return CorpusEntry.model_validate({"id": entry_id, "classification": classification, **values})


class _OwnershipFixtureMixin:
    """Isolated root with an enrolled surface: one corpus-owned and one unowned section."""

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._root = Path(self._tempdir.name)

    def _enroll(
        self,
        *entries: CorpusEntry,
        owned_body: str = "",
        scorecard: str,
        rule_content: str | None = None,
    ) -> None:
        """Write the surface, its witnessed ownership declaration, corpus and scorecard."""
        _make_tree(
            str(self._root),
            scorecard_content=scorecard,
            agents_content=f"{_OWNED_HEADING}{owned_body}\n{_UNOWNED_CHUNK}",
            rule_content=rule_content,
        )
        floor = len(_UNOWNED_CHUNK.encode("utf-8"))
        digest = sections_digest(_OWN_SECTIONS)
        event_id = f"section-ownership-genesis-AGENTS.md-{digest[:12]}"
        emit_section_ownership_genesis(self._root, event_id, "AGENTS.md", digest, floor)
        path = declaration_path(self._root, "AGENTS.md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "surface": "AGENTS.md",
                    "sections": _OWN_SECTIONS,
                    "unowned_byte_floor": floor,
                    "measured_at": "2026-10-03T00:00:00Z",
                    "floor_event_id": event_id,
                }
            ),
            encoding="utf-8",
        )
        for entry in entries:
            append_entry(self._root, "AGENTS.md", entry)

    def _audit(self) -> tuple[list, list[str]]:
        """Run the audit and return ``(errors, advisory lines)`` with stderr captured."""
        captured = io.StringIO()
        with redirect_stderr(captured):
            errors = validate_bullet_retention(self._root)
        return errors, advisory_lines(captured.getvalue())

    def _bullet(self, number: str, section: str = _SCORECARD_SECTION):
        """Return the audited bullet with identity ``(section, number)``."""
        captured = io.StringIO()
        with redirect_stderr(captured):
            population = audited_population(self._root)
        matches = [b for b in population if (b.section_id, b.row_number) == (section, number)]
        self.assertEqual(
            len(matches), 1, f"identity ({section}, {number}) not audited exactly once"
        )
        return matches[0]


class TestOwnedBulletResolvesFromCorpus(_OwnershipFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-10-01 — a corpus-owned section's classification comes from its entry."""

    @covers("REQ-0.35.0-10-01")
    def test_corpus_enforced_class_binds_over_a_scorecard_judgment(self) -> None:
        """The corpus says Mechanical, the scorecard Judgment: the bullet is enforced."""
        self._enroll(
            _entry("e-alpha", "Mechanical"),
            scorecard=_scorecard(("1", _OWNED_RULE, "Judgment", _OWNED_NOTE)),
        )
        errors, _ = self._audit()
        self.assertEqual(len(errors), 1, "the corpus class must enforce retention")
        self.assertIn(_OWNED_RULE, errors[0].message)
        self.assertIn("e-alpha", errors[0].message)
        bullet = self._bullet("1")
        self.assertEqual(
            (bullet.authority, bullet.classification, bullet.entry_id),
            ("corpus", "Mechanical", "e-alpha"),
        )

    @covers("REQ-0.35.0-10-01")
    def test_corpus_judgment_binds_over_a_scorecard_enforced_class(self) -> None:
        """The corpus says Judgment, the scorecard Mechanical: the bullet is not enforced."""
        self._enroll(
            _entry("e-alpha", "Judgment"),
            scorecard=_scorecard(("1", _OWNED_RULE, "Mechanical", _OWNED_NOTE)),
        )
        errors, _ = self._audit()
        self.assertEqual(errors, [], "the scorecard class must not bind an owned bullet")
        self.assertEqual(self._bullet("1").classification, "Judgment")

    @covers("REQ-0.35.0-10-01")
    def test_broken_owned_mapping_fails_closed_without_scorecard_fallback(self) -> None:
        """A missing, wrong-section or retired entry id is a named failure, never a fallback."""
        elsewhere = _entry("e-elsewhere", "Mechanical", section="unowned-section")
        retired = _entry("e-retired", "Mechanical")
        tombstone = _entry("t-retired", "Mechanical", retires="e-retired", text="superseded")
        cases = {
            "`source=AGENTS.md#owned-section`": "cites no entry id",
            "`source=AGENTS.md#owned-section entry=e-unknown`": "e-unknown",
            "`source=AGENTS.md#owned-section entry=e-elsewhere`": "e-elsewhere",
            "`source=AGENTS.md#owned-section entry=e-retired`": "e-retired",
            "`source=AGENTS.md#no-such-section entry=e-alpha`": "no-such-section",
        }
        for note, named in cases.items():
            with self.subTest(note=note):
                self.setUp()
                self._enroll(
                    _entry("e-alpha", "Judgment"),
                    elsewhere,
                    retired,
                    tombstone,
                    owned_body=_OWNED_RULE,
                    scorecard=_scorecard(("1", _OWNED_RULE, "Judgment", note)),
                )
                errors, _ = self._audit()
                self.assertEqual(len(errors), 1, "a broken owned mapping must fail closed")
                self.assertIn(named, errors[0].message)
                self.assertIn(f"{_SCORECARD_SECTION} #1", errors[0].message)


_RULE_NOTE = "`source=.claude/rules/test-rule.md`"
_UNOWNED_NOTE = "`source=AGENTS.md#unowned-section`"
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _table_identities(scorecard_text: str) -> list[tuple[str | None, str]]:
    """Read ``(section id, row number)`` straight off a scorecard's tables (the oracle).

    Independent of the audit's row grammar: every line of a ``| # | Rule | Score |``
    table, or of a pipe block with no header row, counts, whatever its cells hold.
    """
    identities: list[tuple[str | None, str]] = []
    section: str | None = None
    lines = [line.strip() for line in scorecard_text.splitlines()]
    counting = in_block = False
    for index, line in enumerate(lines):
        if line.startswith("### "):
            section = section_id(line[4:])
        if not line.startswith("|"):
            in_block = False
            continue
        first, second = (line.split("|") + ["", ""])[1:3]
        ruled = set(line) <= set("|-: ")
        if not in_block:
            in_block = True
            following = lines[index + 1] if index + 1 < len(lines) else ""
            headed = following.startswith("|") and set(following) <= set("|-: ")
            counting = not headed or (first.strip(), second.strip().lower()) == ("#", "rule")
            if headed:
                continue
        if counting and not ruled:
            identities.append((section, first.strip()))
    return identities


class TestUnownedBulletResolvesFromScorecard(_OwnershipFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-10-02 — unowned rows keep scorecard authority; no identity is lost."""

    @covers("REQ-0.35.0-10-02")
    def test_unowned_section_row_binds_the_scorecard_class(self) -> None:
        """A row in an unowned section is enforced by its scorecard score."""
        self._enroll(
            _entry("e-alpha", "Judgment"),
            scorecard=_scorecard(
                ("1", _UNOWNED_RULE, "Mechanical", _UNOWNED_NOTE),
                ("2", "absent rule gamma", "Mechanical", _UNOWNED_NOTE),
                ("3", "absent rule delta", "Judgment", _UNOWNED_NOTE),
            ),
        )
        errors, advisories = self._audit()
        self.assertEqual(len(errors), 1)
        self.assertIn("absent rule gamma", errors[0].message)
        self.assertEqual(advisories, [])
        bullet = self._bullet("2")
        self.assertEqual((bullet.authority, bullet.entry_id), ("scorecard", None))

    @covers("REQ-0.35.0-10-02")
    def test_same_text_in_two_sections_keeps_both_identities_and_sources(self) -> None:
        """Identity is (section id, row number): equal text never merges two rows."""
        scorecard = _scorecard(("1", _OWNED_RULE, "Mechanical", _OWNED_NOTE)) + _scorecard(
            ("1", _OWNED_RULE, "Mechanical", _RULE_NOTE), heading="Rule File Contract"
        )
        self._enroll(
            _entry("e-alpha", "Mechanical"),
            owned_body=_OWNED_RULE,
            scorecard=scorecard,
            rule_content=_OWNED_RULE,
        )
        errors, _ = self._audit()
        self.assertEqual(errors, [])
        with redirect_stderr(io.StringIO()):
            population = audited_population(self._root)
        self.assertEqual(
            {(b.section_id, b.row_number): (b.source, b.authority) for b in population},
            {
                ("fixture-contract", "1"): ("AGENTS.md", "corpus"),
                ("rule-file-contract", "1"): (".claude/rules/test-rule.md", "scorecard"),
            },
        )

    @covers("REQ-0.35.0-10-02")
    def test_duplicate_or_unattributed_identity_fails_closed(self) -> None:
        """One identity standing in for another, or a row with no source, is refused."""
        cases = {
            "shares its identity": _scorecard(
                ("1", _UNOWNED_RULE, "Judgment", _UNOWNED_NOTE),
                ("1", "another rule", "Judgment", _UNOWNED_NOTE),
            ),
            "carries no `source=` attribution": _scorecard(
                ("1", _UNOWNED_RULE, "Judgment", "no attribution here"),
            ),
        }
        for named, scorecard in cases.items():
            with self.subTest(named=named):
                self.setUp()
                self._enroll(_entry("e-alpha", "Judgment"), scorecard=scorecard)
                errors, _ = self._audit()
                self.assertEqual(len(errors), 1)
                self.assertIn(named, errors[0].message)
                self.assertIn(f"{_SCORECARD_SECTION} #1", errors[0].message)

    @covers("REQ-0.35.0-10-02")
    def test_missing_row_number_fails_closed_naming_the_row(self) -> None:
        """A row whose number cell is blank has no identity and is refused by name."""
        scorecard = _scorecard(
            ("1", "a numbered rule", "Judgment", _UNOWNED_NOTE),
            (" ", _UNOWNED_RULE, "Judgment", _UNOWNED_NOTE),
        )
        self._enroll(_entry("e-alpha", "Judgment"), scorecard=scorecard)
        errors, _ = self._audit()
        self.assertEqual(len(errors), 1)
        self.assertIn("has no row number", errors[0].message)
        self.assertIn(_SCORECARD_SECTION, errors[0].message)
        self.assertIn(_UNOWNED_RULE, errors[0].message)

    @covers("REQ-0.35.0-10-02")
    def test_unreadable_rule_row_fails_closed_and_is_never_skipped(self) -> None:
        """A rule-table row the audit cannot read is refused by name, not dropped."""
        good = _scorecard(("1", "a numbered rule", "Judgment", _UNOWNED_NOTE))
        unreadable = {
            "an empty number cell": f"|| {_UNOWNED_RULE} | **Judgment** | {_UNOWNED_NOTE} |",
            "a score that is not bold": f"| 2 | {_UNOWNED_RULE} | Judgment | {_UNOWNED_NOTE} |",
            "an empty rule cell": f"| 2 || **Judgment** | {_UNOWNED_NOTE} |",
        }
        for named, line in unreadable.items():
            with self.subTest(named=named):
                self.setUp()
                self._enroll(_entry("e-alpha", "Judgment"), scorecard=f"{good}{line}\n")
                errors, _ = self._audit()
                self.assertEqual(len(errors), 1)
                self.assertIn("cannot read", errors[0].message)
                self.assertIn(_SCORECARD_SECTION, errors[0].message)
                self.assertIn("uv run gz validate --bullet-retention", errors[0].message)
                with redirect_stderr(io.StringIO()):
                    audited = [b.row_number for b in audited_population(self._root)]
                self.assertEqual(audited, ["1"])

    @covers("REQ-0.35.0-10-02")
    def test_escaped_pipe_row_is_audited_with_its_pipe_restored(self) -> None:
        """A rule whose text carries an escaped pipe keeps its identity and its text."""
        scorecard = _scorecard(
            ("1", "a numbered rule", "Judgment", _UNOWNED_NOTE),
            ("2", "use `str \\| None` for an optional", "Judgment", _UNOWNED_NOTE),
        )
        self._enroll(_entry("e-alpha", "Judgment"), scorecard=scorecard)
        errors, _ = self._audit()
        self.assertEqual(errors, [])
        self.assertEqual(self._bullet("2").rule, "use `str | None` for an optional")

    @covers("REQ-0.35.0-10-02")
    def test_score_cell_binds_its_leading_class_and_keeps_a_qualifier(self) -> None:
        """A score cell that qualifies its class is read by the class it leads with."""
        qualified = "Mechanical** (shape invariant); size targets remain **Judgment"
        scorecard = _scorecard(
            ("1", "a numbered rule", "Judgment", _UNOWNED_NOTE),
            ("2", "rule file rule kept", qualified, _RULE_NOTE),
        )
        self._enroll(
            _entry("e-alpha", "Judgment"), scorecard=scorecard, rule_content="rule file rule kept"
        )
        errors, _ = self._audit()
        self.assertEqual(errors, [])
        self.assertEqual(self._bullet("2").classification, "Mechanical")

    @covers("REQ-0.35.0-10-02")
    def test_table_of_another_shape_holds_no_rule_rows(self) -> None:
        """A table that is not a rule table is neither audited nor refused."""
        legend = "\n| Score | Meaning |\n|---|---|\n| **Mechanical** | enforced by a check |\n"
        scorecard = _scorecard(("1", "a numbered rule", "Judgment", _UNOWNED_NOTE)) + legend
        self._enroll(_entry("e-alpha", "Judgment"), scorecard=scorecard)
        errors, _ = self._audit()
        self.assertEqual(errors, [])
        with redirect_stderr(io.StringIO()):
            audited = [b.row_number for b in audited_population(self._root)]
        self.assertEqual(audited, ["1"])

    @covers("REQ-0.35.0-10-02")
    def test_rule_file_row_keeps_the_per_turn_surface_check(self) -> None:
        """A non-AgentContract row is retained against the per-turn surface, as before."""
        scorecard = _scorecard(
            ("1", "rule file rule kept", "Mechanical", _RULE_NOTE),
            ("2", "rule file rule lost", "Promotable", _RULE_NOTE),
        )
        self._enroll(
            _entry("e-alpha", "Judgment"), scorecard=scorecard, rule_content="rule file rule kept"
        )
        errors, _ = self._audit()
        self.assertEqual(len(errors), 1)
        self.assertIn("rule file rule lost", errors[0].message)
        self.assertIn("per-turn surface", errors[0].message)

    @covers("REQ-0.35.0-10-02")
    def test_rule_file_row_keeps_the_compressible_witness_path(self) -> None:
        """Tier-scoped retention is unchanged: a witnessed compressible bullet may be reworded."""
        receipts = self._root / "receipts"
        with mock.patch.dict(os.environ, {"GZKIT_ARB_RECEIPTS_ROOT": str(receipts)}):
            self._enroll(
                _entry("e-alpha", "Judgment"),
                _entry(
                    "e-compressible",
                    "Mechanical",
                    tier="compressible",
                    section="unowned-section",
                    text="reworded rule epsilon in all shells",
                ),
                scorecard=_scorecard(("1", "reworded rule epsilon", "Mechanical", _RULE_NOTE)),
                rule_content="the per-turn surface words it differently",
            )
            self.assertEqual(len(self._audit()[0]), 1, "unwitnessed compressible must fail")
            _seed_advisor_witness(self._root)
            self.assertEqual(self._audit()[0], [])

    @covers("REQ-0.35.0-10-02")
    def test_unenrolled_project_keeps_the_legacy_audit(self) -> None:
        """With no ownership declaration and no attribution the scorecard answers every row."""
        _make_tree(str(self._root), scorecard_content=_SCORECARD_MIXED, agents_content="")
        errors, advisories = self._audit()
        self.assertEqual(len(errors), 2, "both enforced rows are absent from the surface")
        self.assertEqual(advisories, [])
        with redirect_stderr(io.StringIO()):
            population = audited_population(self._root)
        self.assertEqual([b.authority for b in population], ["scorecard"] * 3)

    @covers("REQ-0.35.0-10-02")
    def test_live_scorecard_population_keeps_every_table_identity(self) -> None:
        """Every row identity in the committed scorecard is audited once, with a source."""
        scorecard = (_REPO_ROOT / "docs" / "governance" / "advisory-rules-audit.md").read_text(
            encoding="utf-8"
        )
        expected = _table_identities(scorecard)
        with redirect_stderr(io.StringIO()):
            population = audited_population(_REPO_ROOT)
        self.assertEqual(
            sorted((b.section_id or "", b.row_number) for b in population),
            sorted((section or "", number) for section, number in expected),
        )
        self.assertEqual([b for b in population if not b.source], [])


class TestOwnedDisagreementIsReported(_OwnershipFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-10-03 — the corpus value binds and the disagreement is surfaced."""

    def _verdict(self, corpus_class: str, scorecard_class: str) -> tuple[int, list[str]]:
        """Return ``(error count, advisories)`` for an owned bullet absent from the surface."""
        self.setUp()
        self._enroll(
            _entry("e-alpha", corpus_class),
            scorecard=_scorecard(("1", _OWNED_RULE, scorecard_class, _OWNED_NOTE)),
        )
        errors, advisories = self._audit()
        return len(errors), advisories

    @covers("REQ-0.35.0-10-03")
    def test_disagreement_names_the_row_the_entry_and_both_values(self) -> None:
        """The operator sees which row and entry disagree, and what each says."""
        error_count, advisories = self._verdict("Judgment", "Mechanical")
        self.assertEqual(error_count, 0, "the corpus Judgment binds")
        self.assertEqual(len(advisories), 1)
        for named in (f"{_SCORECARD_SECTION} #1", "e-alpha", "'Mechanical'", "'Judgment'"):
            self.assertIn(named, advisories[0])

    @covers("REQ-0.35.0-10-03")
    def test_scorecard_change_alone_never_changes_the_verdict(self) -> None:
        """Holding the corpus fixed, the scorecard cell decides only whether a report appears."""
        for scorecard_class, reported in (("Mechanical", 0), ("Judgment", 1), ("Promotable", 1)):
            with self.subTest(scorecard_class=scorecard_class):
                error_count, advisories = self._verdict("Mechanical", scorecard_class)
                self.assertEqual(error_count, 1, "the corpus Mechanical enforces retention")
                self.assertEqual(len(advisories), reported)

    @covers("REQ-0.35.0-10-03")
    def test_corpus_change_alone_changes_the_verdict(self) -> None:
        """Holding the scorecard fixed, the corpus classification decides the verdict."""
        self.assertEqual(self._verdict("Mechanical", "Mechanical")[0], 1)
        self.assertEqual(self._verdict("Judgment", "Mechanical")[0], 0)


class TestCaptureDefaultNeverBinds(_OwnershipFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-10-04 — an owned section holding an unreviewed default fails closed."""

    _CLEAN_SCORECARD = _scorecard(("1", _OWNED_RULE, "Judgment", _OWNED_NOTE))

    @covers("REQ-0.35.0-10-04")
    def test_every_live_ambiguous_entry_is_named_with_rule_and_next_step(self) -> None:
        """Unmapped entries count too: the fence reads the section, not the scorecard."""
        self._enroll(
            _entry("e-alpha", "Judgment"),
            _entry("e-unmapped", "Ambiguous", text="an entry no row cites"),
            _entry("e-second", "Ambiguous", text="another entry no row cites"),
            scorecard=self._CLEAN_SCORECARD,
        )
        errors, _ = self._audit()
        self.assertEqual(len(errors), 1)
        for named in (
            "e-unmapped",
            "e-second",
            "owned-section",
            "ADR-0.35.0 § Decision item 9",
            "gz content retire AGENTS.md",
            "gz content remember AGENTS.md",
            "gz validate --bullet-retention",
        ):
            self.assertIn(named, errors[0].message)

    @covers("REQ-0.35.0-10-04")
    def test_retired_or_unowned_ambiguous_entries_do_not_trip_the_fence(self) -> None:
        """The fence reads the effective view of corpus-owned sections only."""
        self._enroll(
            _entry("e-alpha", "Judgment"),
            _entry("e-old", "Ambiguous", text="a default later retired"),
            _entry("t-old", "Mechanical", retires="e-old", text="reviewed"),
            _entry("e-hand", "Ambiguous", section="unowned-section", text="unowned default"),
            scorecard=self._CLEAN_SCORECARD,
        )
        self.assertEqual(self._audit()[0], [])

    @covers("REQ-0.35.0-10-04")
    def test_capture_default_on_a_mapped_entry_is_refused_not_reported_as_binding(self) -> None:
        """A row citing an unreviewed entry fails closed; nothing claims the default binds."""
        self._enroll(
            _entry("e-alpha", "Ambiguous"),
            scorecard=_scorecard(("1", _OWNED_RULE, "Mechanical", _OWNED_NOTE)),
        )
        errors, advisories = self._audit()
        self.assertEqual(len(errors), 1)
        self.assertIn("e-alpha", errors[0].message)
        self.assertEqual(advisories, [])

    @covers("REQ-0.35.0-10-04")
    def test_invalid_ownership_never_converts_owned_rows_to_scorecard_rows(self) -> None:
        """A declaration that no longer loads fails closed; its rows resolve from nowhere."""
        self._enroll(_entry("e-alpha", "Judgment"), scorecard=self._CLEAN_SCORECARD)
        path = declaration_path(self._root, "AGENTS.md")
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["sections"]["owned-section"] = "unowned"
        path.write_text(json.dumps(raw), encoding="utf-8")
        errors, _ = self._audit()
        self.assertEqual(len(errors), 1)
        self.assertIn("ownership", errors[0].message)
        with redirect_stderr(io.StringIO()):
            self.assertEqual(audited_population(self._root), [])

    @covers("REQ-0.35.0-10-04")
    def test_missing_declaration_never_converts_owned_rows_to_scorecard_rows(self) -> None:
        """Deleting the declaration leaves an entry-citing row refused, not scorecard-bound."""
        self._enroll(_entry("e-alpha", "Judgment"), scorecard=self._CLEAN_SCORECARD)
        declaration_path(self._root, "AGENTS.md").unlink()
        errors, _ = self._audit()
        self.assertEqual(len(errors), 1)
        self.assertIn("no ownership declaration", errors[0].message)


class TestReconciliationIsAppendOnly(_OwnershipFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-10-05 — reconciling a classification appends; old rows never change."""

    @covers("REQ-0.35.0-10-05")
    def test_retire_then_capture_clears_the_fence_and_keeps_the_old_prefix(self) -> None:
        """Interrupted reconciliation stays refused; completed, the old rows are byte-identical."""
        self._enroll(
            _entry("e-alpha", "Ambiguous"),
            scorecard=_scorecard(("1", _OWNED_RULE, "Judgment", _OWNED_NOTE)),
        )
        store = corpus_path(self._root, "AGENTS.md")
        before_bytes = store.read_bytes()
        before = load_corpus(self._root, "AGENTS.md")
        self.assertEqual(len(self._audit()[0]), 1, "the capture default must not bind")

        append_entry(
            self._root, "AGENTS.md", _entry("t-alpha", "Mechanical", retires="e-alpha", text="r")
        )
        interrupted, _ = self._audit()
        self.assertEqual(len(interrupted), 1, "retire without capture is incomplete")
        self.assertIn("e-alpha", interrupted[0].message)

        append_entry(self._root, "AGENTS.md", _entry("e-alpha-reviewed", "Judgment"))
        refreshed = _OWNED_NOTE.replace("e-alpha", "e-alpha-reviewed")
        (self._root / "docs" / "governance" / "advisory-rules-audit.md").write_text(
            _scorecard(("1", _OWNED_RULE, "Judgment", refreshed)), encoding="utf-8"
        )
        self.assertEqual(self._audit()[0], [])

        after = load_corpus(self._root, "AGENTS.md")
        self.assertTrue(store.read_bytes().startswith(before_bytes.rstrip(b"\n")))
        self.assertEqual(after.entries[: len(before.entries)], before.entries)
        self.assertEqual(
            corpus_fingerprint(Corpus(entries=after.entries[: len(before.entries)])),
            corpus_fingerprint(before),
        )
        self.assertNotEqual(corpus_fingerprint(after), corpus_fingerprint(before))


class TestDeclaredSourceRetention(_OwnershipFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-10-08 / -09 — skill- and ADR-sourced rows are retained in their source."""

    _SOURCES = (
        ".gzkit/skills/demo/SKILL.md",
        "docs/design/adr/pre-release/ADR-9.9.9-demo/ADR-9.9.9-demo.md",
    )
    _RULE = "declared rule zeta must hold"

    def _enroll_sourced(self, source: str, *, source_text: str | None, surface: str) -> None:
        """Enroll with one Mechanical row attributed to *source* and the given texts."""
        self.setUp()
        self._enroll(
            _entry("e-alpha", "Judgment"),
            scorecard=_scorecard(("1", self._RULE, "Mechanical", f"`source={source}`")),
            rule_content=surface,
        )
        if source_text is not None:
            path = self._root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(source_text, encoding="utf-8")

    @covers("REQ-0.35.0-10-08")
    def test_row_is_retained_by_its_source_not_the_per_turn_surface(self) -> None:
        """Text in the source alone satisfies retention; no per-turn mirror is needed."""
        for source in self._SOURCES:
            with self.subTest(source=source):
                self._enroll_sourced(source, source_text=f"- {self._RULE}\n", surface="")
                self.assertEqual(self._audit()[0], [])

    @covers("REQ-0.35.0-10-08")
    def test_per_turn_mirror_does_not_satisfy_a_declared_source(self) -> None:
        """Text in the per-turn surface but not in the source is a retention violation."""
        for source in self._SOURCES:
            with self.subTest(source=source):
                self._enroll_sourced(source, source_text="other text\n", surface=self._RULE)
                errors, _ = self._audit()
                self.assertEqual(len(errors), 1)
                self.assertIn(source, errors[0].message)

    @covers("REQ-0.35.0-10-09")
    def test_missing_source_or_absent_text_fails_closed_with_recovery(self) -> None:
        """The finding names the row identity, the source path, the rule and the next step."""
        for source in self._SOURCES:
            for source_text in (None, "the source says something else\n"):
                with self.subTest(source=source, source_text=source_text):
                    self._enroll_sourced(source, source_text=source_text, surface=self._RULE)
                    errors, _ = self._audit()
                    self.assertEqual(len(errors), 1)
                    for named in (
                        f"{_SCORECARD_SECTION} #1",
                        source,
                        "ADR-0.0.33 Invariant 1",
                        "gz validate --bullet-retention",
                    ):
                        self.assertIn(named, errors[0].message)


if __name__ == "__main__":
    unittest.main()
