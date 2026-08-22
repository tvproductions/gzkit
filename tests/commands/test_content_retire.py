"""gz content retire command tests — append-only corpus retirement (GHI #635).

The corpus store has no delete, so a superseded operator directive bound the
invariant floor forever and the only escape was hand-editing the append-only
JSONL. These tests pin the governed alternative: a retraction row that retires
an id without removing it, shrinking the floor rather than growing it.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.content.models import Corpus
from gzkit.content.rendition_store import (
    RenditionProvenance,
    save_fingerprint,
    save_rendition,
)
from gzkit.content.tier_policy import invariant_entries
from tests.commands.common import CliRunner

_SURFACE = """# Test Agent Contract

Purpose line.

## Behavior Rules

- Do the thing.

## Prime Directive

- Own it.
"""

_CORPUS_PATH = Path(".gzkit") / "corpus" / "AGENTS.md.jsonl"


def _seed_surface(name: str = "AGENTS.md") -> Path:
    path = Path(name)
    path.write_text(_SURFACE, encoding="utf-8")
    return path


def _load_corpus() -> Corpus:
    return Corpus.loads(_CORPUS_PATH.read_text(encoding="utf-8"))


def _ledger_events() -> list[dict]:
    ledger_path = Path(".gzkit") / "ledger.jsonl"
    if not ledger_path.exists():
        return []
    return [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _seed_committed_rendition(consumer: str, *, corpus_fingerprint: str) -> None:
    """Commit a rendition + provenance sidecar for AGENTS.md/<consumer> in the cwd."""
    root = Path()
    save_rendition(root, "AGENTS.md", consumer, _SURFACE.encode("utf-8"))
    save_fingerprint(
        root,
        "AGENTS.md",
        consumer,
        RenditionProvenance(
            corpus_fingerprint=corpus_fingerprint,
            corpus_entry_count=0,
            rendition_fingerprint=None,
            committed_ts="2026-08-22T00:00:00+00:00",
            attestor="g0",
            attestation_text="seeded for test",
        ),
    )


class TestContentRetireDriftWarning(unittest.TestCase):
    """Retirement must announce the rendition drift it causes (GHI #863).

    GHI #654 established that a corpus mutation has to say so, and gave
    `remember` a warning. `retire` never got it, and its help asserted the
    opposite -- "no recomposition is implied". Both verbs append to the corpus
    and both move its fingerprint, so both break every committed rendition's
    derivation proof. The measured cost of the gap was a blocked push and an
    operator told no recompose was due.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _remember(self, text: str, *, tier: str = "invariant") -> str:
        result = self._runner.invoke(
            main,
            [
                "content",
                "remember",
                "AGENTS.md",
                "--section",
                "Prime Directive",
                "--text",
                text,
                "--tier",
                tier,
            ],
        )
        self.assertEqual(result.exit_code, 0, msg=result.output)
        return _load_corpus().entries[-1].id

    def _retire(self, entry_id: str):
        return self._runner.invoke(
            main,
            ["content", "retire", "AGENTS.md", "--entry", entry_id, "--reason", "superseded"],
        )

    def test_warns_naming_every_drifted_consumer(self) -> None:
        """The operator learns which renditions this retirement just unprovable-ised."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("Some directive.")
            _seed_committed_rendition("root", corpus_fingerprint="stale-root")
            _seed_committed_rendition("codex", corpus_fingerprint="stale-codex")

            result = self._retire(entry_id)
            self.assertIn("root", result.output)
            self.assertIn("codex", result.output)
            self.assertIn("Rendition freshness", result.output)

    def test_warning_never_changes_the_exit_code(self) -> None:
        """The retirement succeeded and IS the intended effect; the warning is advisory."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("Some directive.")
            _seed_committed_rendition("root", corpus_fingerprint="stale-root")
            self.assertEqual(self._retire(entry_id).exit_code, 0)

    def test_does_not_claim_the_floor_gate_is_at_risk(self) -> None:
        """Retirement only ever SHRINKS the floor, so floor coherence cannot break.

        This is the true half of the help text GHI #863 corrects, and it is what
        distinguishes a retirement from an invariant-tier append: `remember`
        must warn about the floor gate, `retire` must not. Naming a gate that
        cannot fail would send the operator to recompose for the wrong reason.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("Some directive.", tier="invariant")
            _seed_committed_rendition("root", corpus_fingerprint="stale-root")

            result = self._retire(entry_id)
            self.assertNotIn("floor coherence", result.output.lower())

    def test_silent_when_no_rendition_is_committed(self) -> None:
        """Nothing to drift, nothing to say."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("Some directive.")
            result = self._retire(entry_id)
            self.assertEqual(result.exit_code, 0)
            self.assertNotIn("Rendition freshness", result.output)

    def test_help_states_both_halves_of_the_consequence(self) -> None:
        """The sentence an operator reads BEFORE retiring must be true as workflow.

        "no recomposition is implied" was accurate about the FLOOR and false
        about the PUSH, which is the whole of GHI #863. Both halves have to be
        present: state only the floor half and the operator is misled again;
        state only the freshness half and the floor claim GHI #635 established
        is lost.

        The single-occurrence assertion is not decoration. The first attempt at
        this fix replaced only the tail of a multi-line description string and
        produced "...stay valid and no shrinks the floor, so every...", which an
        absence-plus-keyword assertion passed happily. Pinning the count is what
        catches a spliced string.
        """
        output = self._runner.invoke(main, ["content", "retire", "--help"]).output
        self.assertNotIn("no recomposition is implied", output)
        self.assertNotIn("committed renditions stay valid", output)
        self.assertEqual(output.count("shrinks the floor"), 1, "spliced description")
        self.assertIn("rendition-freshness", output)
        self.assertIn("recompose", output.lower())


class TestContentRetire(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    def _remember(self, text: str, *, tier: str = "invariant") -> str:
        """Append one entry and return its id."""
        result = self._runner.invoke(
            main,
            [
                "content",
                "remember",
                "AGENTS.md",
                "--section",
                "Prime Directive",
                "--text",
                text,
                "--tier",
                tier,
            ],
        )
        self.assertEqual(result.exit_code, 0, msg=result.output)
        return _load_corpus().entries[-1].id

    def test_retired_entry_stops_binding_the_invariant_floor(self) -> None:
        """The behavior the GHI needs: a retired invariant no longer constrains renditions."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            old = self._remember("doctrine, verbatim: 'x'")
            self._remember('doctrine, verbatim: "x"')
            self.assertEqual(len(invariant_entries(_load_corpus())), 2)

            result = self._runner.invoke(
                main,
                ["content", "retire", "AGENTS.md", "--entry", old, "--reason", "superseded"],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)

            live = invariant_entries(_load_corpus())
            self.assertEqual(len(live), 1)
            self.assertNotIn(old, [e.id for e in live])

    def test_retirement_preserves_the_retired_row(self) -> None:
        """Append-only: the store grows by one row; the retired entry is still on disk."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            old = self._remember("superseded doctrine")
            before = len(_load_corpus().entries)

            self._runner.invoke(
                main,
                ["content", "retire", "AGENTS.md", "--entry", old, "--reason", "superseded"],
            )

            after = _load_corpus()
            self.assertEqual(len(after.entries), before + 1)
            self.assertIn(old, [e.id for e in after.entries])
            self.assertEqual(after.retired_ids(), frozenset({old}))

    def test_does_not_modify_the_rendered_surface(self) -> None:
        """Retirement touches the corpus only — never a rendered surface."""
        with self._runner.isolated_filesystem():
            surface = _seed_surface()
            old = self._remember("superseded doctrine")
            before = surface.read_bytes()

            self._runner.invoke(
                main,
                ["content", "retire", "AGENTS.md", "--entry", old, "--reason", "superseded"],
            )

            self.assertEqual(surface.read_bytes(), before)

    def test_emits_a_corpus_entry_retired_event(self) -> None:
        """Retirement is witnessed at Layer 2 distinctly from a plain append."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            old = self._remember("superseded doctrine")

            self._runner.invoke(
                main,
                ["content", "retire", "AGENTS.md", "--entry", old, "--reason", "quote-style drift"],
            )

            retired = [e for e in _ledger_events() if e.get("event") == "corpus_entry_retired"]
            self.assertEqual(len(retired), 1)
            self.assertEqual(retired[0]["retired_entry_id"], old)
            self.assertEqual(retired[0]["reason"], "quote-style drift")

    def test_unknown_entry_fails_closed(self) -> None:
        """An id no row carries writes nothing and exits 1."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            self._remember("some doctrine")
            before = _CORPUS_PATH.read_bytes()

            result = self._runner.invoke(
                main,
                [
                    "content",
                    "retire",
                    "AGENTS.md",
                    "--entry",
                    "corpus-nonexistent",
                    "--reason",
                    "x",
                ],
            )

            self.assertEqual(result.exit_code, 1)
            self.assertEqual(_CORPUS_PATH.read_bytes(), before)

    def test_double_retirement_fails_closed(self) -> None:
        """Retiring an already-retired entry refuses rather than appending a second retraction."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            old = self._remember("superseded doctrine")
            self._runner.invoke(
                main,
                ["content", "retire", "AGENTS.md", "--entry", old, "--reason", "first"],
            )
            before = _CORPUS_PATH.read_bytes()

            result = self._runner.invoke(
                main,
                ["content", "retire", "AGENTS.md", "--entry", old, "--reason", "second"],
            )

            self.assertEqual(result.exit_code, 1)
            self.assertEqual(_CORPUS_PATH.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
