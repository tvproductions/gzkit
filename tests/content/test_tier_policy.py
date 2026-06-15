"""Invariant-tier policy tests — OBPI-0.0.37-23."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.content.composer import compose
from gzkit.content.models import Corpus, CorpusEntry
from gzkit.content.tier_policy import assert_invariant_verbatim, invariant_entries
from gzkit.traceability import covers

_PRIME_DIRECTIVE_TEXT = "YOU OWN THE WORK COMPLETELY. No deferral, no rationalized incompleteness."
_DO_IT_RIGHT_TEXT = "The most thorough and comprehensive fix is always preferred."
_NEVER_PYTEST_TEXT = "Testing: unittest over pytest. Enforced by forbid-pytest pre-commit hook."

_COMPOSER_INVARIANT_TEXT = "YOU OWN THE WORK COMPLETELY."
_COMPOSER_VENDOR_MANIFEST = {
    "content_type_routes": {"AgentContract": ["claude", "codex"]},
    "content_type_temperatures": {"AgentContract": {"codex": "lite", "claude": "heavy"}},
}


def _seed_composer_project(root: Path) -> None:
    """Write a minimal project (corpus + vendor manifest) so ``compose`` can run.

    The corpus JSONL is written directly rather than via
    ``corpus_store.append_entry`` so this OBPI-23 test does not import OBPI-19's
    store module. ``corpus_store`` is a consumed prerequisite of this OBPI, not
    an edited surface; importing it here would falsely trip the brief-reconcile
    neighborhood heuristic (it shares the ``src/gzkit/content/`` parent with the
    allowlisted ``tier_policy.py``). The store path layout
    (``.gzkit/corpus/<surface>.jsonl``) is the load_corpus contract; a layout
    change breaks ``compose`` loudly with FileNotFoundError, never silently.
    """
    (root / "data").mkdir(exist_ok=True)
    (root / "data" / "vendor-manifest.json").write_text(
        json.dumps(_COMPOSER_VENDOR_MANIFEST), encoding="utf-8"
    )
    corpus_dir = root / ".gzkit" / "corpus"
    corpus_dir.mkdir(parents=True, exist_ok=True)
    entry = CorpusEntry(
        id="e-invariant",
        surface="AGENTS.md",
        section="prime-directive",
        tier="invariant",
        classification="Mechanical",
        text=_COMPOSER_INVARIANT_TEXT,
        origin="test",
        ts="2026-06-14T00:00:00Z",
    )
    (corpus_dir / "AGENTS.md.jsonl").write_text(entry.model_dump_json() + "\n", encoding="utf-8")


def _entry(entry_id: str, text: str, *, tier: str = "compressible") -> CorpusEntry:
    return CorpusEntry(
        id=entry_id,
        surface="AGENTS.md",
        section="prime-directive",
        tier=tier,  # type: ignore
        classification="Mechanical",
        text=text,
        origin="test",
        ts="2026-06-14T00:00:00Z",
    )


class TestInvariantEntries(unittest.TestCase):
    @covers("REQ-0.0.37-23-01")
    def test_returns_only_invariant_entries(self) -> None:
        """Mixed corpus: invariant_entries() returns only the invariant-tier entry."""
        inv = _entry("inv-1", "must keep this", tier="invariant")
        comp = _entry("comp-1", "can drop this", tier="compressible")
        corpus = Corpus(entries=(inv, comp))
        result = invariant_entries(corpus)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "inv-1")

    @covers("REQ-0.0.37-23-01")
    def test_empty_corpus_returns_empty_list(self) -> None:
        """Empty corpus: invariant_entries() returns []."""
        corpus = Corpus()
        self.assertEqual(invariant_entries(corpus), [])

    @covers("REQ-0.0.37-23-01")
    def test_all_compressible_returns_empty_list(self) -> None:
        """All-compressible corpus: invariant_entries() returns []."""
        corpus = Corpus(
            entries=(
                _entry("c-1", "compressible text", tier="compressible"),
                _entry("c-2", "also compressible", tier="compressible"),
            )
        )
        self.assertEqual(invariant_entries(corpus), [])


class TestAssertInvariantVerbatim(unittest.TestCase):
    @covers("REQ-0.0.37-23-01")
    def test_passes_when_all_invariants_present(self) -> None:
        """rendered_text containing all invariant texts: no ValueError raised."""
        inv1 = _entry("inv-1", "alpha text", tier="invariant")
        inv2 = _entry("inv-2", "beta text", tier="invariant")
        corpus = Corpus(entries=(inv1, inv2))
        rendered = "alpha text and beta text and more content"
        assert_invariant_verbatim(corpus, rendered)  # must not raise

    @covers("REQ-0.0.37-23-01")
    def test_raises_when_invariant_absent(self) -> None:
        """rendered_text missing an invariant entry: ValueError is raised."""
        inv = _entry("inv-1", "must be present", tier="invariant")
        corpus = Corpus(entries=(inv,))
        rendered = "completely different content with no match"
        with self.assertRaises(ValueError) as ctx:
            assert_invariant_verbatim(corpus, rendered)
        self.assertIn("inv-1", str(ctx.exception))

    @covers("REQ-0.0.37-23-01")
    def test_raises_when_invariant_altered(self) -> None:
        """rendered_text with a slightly altered invariant: ValueError is raised."""
        inv = _entry("inv-1", "exact required text", tier="invariant")
        corpus = Corpus(entries=(inv,))
        rendered = "exact required TEXT"  # case-altered
        with self.assertRaises(ValueError):
            assert_invariant_verbatim(corpus, rendered)

    @covers("REQ-0.0.37-23-01")
    def test_passes_with_empty_corpus(self) -> None:
        """No invariant entries: assert_invariant_verbatim passes unconditionally."""
        corpus = Corpus()
        assert_invariant_verbatim(corpus, "any rendered text")  # must not raise


class TestInvariantSurvivesLeanestSetpoint(unittest.TestCase):
    """0-Kelvin floor: canonical invariants must survive verbatim at every setpoint."""

    @covers("REQ-0.0.37-23-02")
    def test_prime_directive_survives_lite(self) -> None:
        """PRIME DIRECTIVE invariant text survives in a simulated lite rendition."""
        corpus = Corpus(entries=(_entry("prime", _PRIME_DIRECTIVE_TEXT, tier="invariant"),))
        rendered = f"Some lite context. {_PRIME_DIRECTIVE_TEXT} End."
        assert_invariant_verbatim(corpus, rendered)

    @covers("REQ-0.0.37-23-02")
    def test_do_it_right_survives_lite(self) -> None:
        """DO IT RIGHT invariant text survives in a simulated lite rendition."""
        corpus = Corpus(entries=(_entry("do-it-right", _DO_IT_RIGHT_TEXT, tier="invariant"),))
        rendered = f"Preamble. {_DO_IT_RIGHT_TEXT} Postamble."
        assert_invariant_verbatim(corpus, rendered)

    @covers("REQ-0.0.37-23-02")
    def test_never_pytest_survives_lite(self) -> None:
        """NEVER PYTEST invariant text survives in a simulated lite rendition."""
        corpus = Corpus(entries=(_entry("never-pytest", _NEVER_PYTEST_TEXT, tier="invariant"),))
        rendered = f"Rules: {_NEVER_PYTEST_TEXT} That is all."
        assert_invariant_verbatim(corpus, rendered)

    @covers("REQ-0.0.37-23-02")
    def test_all_three_survive_lite(self) -> None:
        """All three canonical invariants survive verbatim (0-Kelvin floor holds)."""
        corpus = Corpus(
            entries=(
                _entry("prime", _PRIME_DIRECTIVE_TEXT, tier="invariant"),
                _entry("do-it-right", _DO_IT_RIGHT_TEXT, tier="invariant"),
                _entry("never-pytest", _NEVER_PYTEST_TEXT, tier="invariant"),
            )
        )
        rendered = f"{_PRIME_DIRECTIVE_TEXT} {_DO_IT_RIGHT_TEXT} {_NEVER_PYTEST_TEXT}"
        assert_invariant_verbatim(corpus, rendered)

    @covers("REQ-0.0.37-23-02")
    def test_floor_fails_when_lite_drops_invariant(self) -> None:
        """Floor catches when lite rendition omits one of the canonical invariants."""
        corpus = Corpus(
            entries=(
                _entry("prime", _PRIME_DIRECTIVE_TEXT, tier="invariant"),
                _entry("do-it-right", _DO_IT_RIGHT_TEXT, tier="invariant"),
                _entry("never-pytest", _NEVER_PYTEST_TEXT, tier="invariant"),
            )
        )
        # Omit _NEVER_PYTEST_TEXT from the rendered output
        rendered = f"{_PRIME_DIRECTIVE_TEXT} {_DO_IT_RIGHT_TEXT}"
        with self.assertRaises(ValueError):
            assert_invariant_verbatim(corpus, rendered)


class TestCentralizedEnforcement(unittest.TestCase):
    """Proves `tier_policy` is the single enforcement surface the composer's
    compression path calls — no duplicated inline check."""

    @covers("REQ-0.0.37-23-03")
    def test_candidate_dropping_invariant_is_rejected(self) -> None:
        """Candidate rendition omitting an invariant entry raises ValueError."""
        inv = _entry("inv-drop", "invariant content that must stay", tier="invariant")
        corpus = Corpus(entries=(inv,))
        candidate = "some compressed content without the invariant"
        with self.assertRaises(ValueError):
            assert_invariant_verbatim(corpus, candidate)

    @covers("REQ-0.0.37-23-03")
    def test_candidate_combining_invariants_is_rejected(self) -> None:
        """Paraphrase combining two invariant entries still raises ValueError."""
        inv1 = _entry("inv-a", "alpha invariant text", tier="invariant")
        inv2 = _entry("inv-b", "beta invariant text", tier="invariant")
        corpus = Corpus(entries=(inv1, inv2))
        # Paraphrase combines them but neither verbatim form is present
        candidate = "alpha-and-beta combined paraphrase invariant"
        with self.assertRaises(ValueError):
            assert_invariant_verbatim(corpus, candidate)

    @covers("REQ-0.0.37-23-03")
    def test_candidate_rewriting_invariant_is_rejected(self) -> None:
        """Slightly reworded invariant still raises ValueError (verbatim required)."""
        inv = _entry("inv-rw", "verbatim content must appear exactly as written", tier="invariant")
        corpus = Corpus(entries=(inv,))
        # "written" swapped to "described" — the invariant text is not a substring
        candidate = "verbatim content must appear exactly as described"
        with self.assertRaises(ValueError):
            assert_invariant_verbatim(corpus, candidate)

    @covers("REQ-0.0.37-23-03")
    def test_valid_candidate_with_extra_text_passes(self) -> None:
        """Candidate with invariant text PLUS extra content passes (extra text allowed)."""
        inv = _entry("inv-ok", "invariant anchor text", tier="invariant")
        corpus = Corpus(entries=(inv,))
        candidate = "INTRODUCTION invariant anchor text CONCLUSION and more"
        assert_invariant_verbatim(corpus, candidate)  # must not raise


class TestComposerRoutesThroughPolicy(unittest.TestCase):
    """REQ-03: `tier_policy` is the single enforcement surface the composer's
    compression path calls — proven by routing `compose()` through the shared
    policy, not a duplicated inline check. If the composer kept its own inline
    check, the patched-policy test below would see zero calls."""

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        _seed_composer_project(self._root)

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    @covers("REQ-0.0.37-23-03")
    def test_compose_invokes_shared_tier_policy(self) -> None:
        """compose() routes its invariant-floor check through the shared tier_policy."""
        candidate = f"{_COMPOSER_INVARIANT_TEXT}\ncompressed body"
        with patch("gzkit.content.composer.assert_invariant_verbatim") as mock_assert:
            compose(self._root, "AGENTS.md", "codex", candidate)
        mock_assert.assert_called_once()

    @covers("REQ-0.0.37-23-03")
    def test_compose_rejects_dropped_invariant_via_policy(self) -> None:
        """A dropped invariant is rejected by the shared policy through compose()."""
        candidate = "only compressible content, the invariant was dropped"
        with self.assertRaises(ValueError) as ctx:
            compose(self._root, "AGENTS.md", "codex", candidate)
        self.assertIn("Invariant-floor violation", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
