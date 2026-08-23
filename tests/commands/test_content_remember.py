"""gz content remember command tests — OBPI-0.0.37-19 (BEHAVIOR REQ proofs).

REQ-derived from the brief's Acceptance Criteria, not from the implementation:
capture appends one addressed entry to the per-surface corpus store, emits a
corpus_entry_appended ledger event, NEVER edits a rendered surface, and fails
closed on an unknown surface or an unaddressable section.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.content.models import Corpus
from gzkit.content.rendition_store import (
    RenditionProvenance,
    save_fingerprint,
    save_rendition,
)
from gzkit.traceability import covers
from tests.commands.common import CliRunner

_SURFACE = """# Test Agent Contract

Purpose line.

## Behavior Rules

- Do the thing.

## Prime Directive

- Own it.
"""


def _seed_surface(name: str = "AGENTS.md") -> Path:
    """Write a minimal parseable AgentContract surface into the cwd; return its path."""
    path = Path(name)
    path.write_text(_SURFACE, encoding="utf-8")
    return path


def _ledger_events() -> list[dict]:
    """Return the parsed ledger events from the cwd project, or [] when none."""
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
            committed_ts="2026-07-22T00:00:00+00:00",
            attestor="g0",
            attestation_text="seeded for test",
        ),
    )


class TestContentRemember(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.0.37-19-01")
    def test_appends_one_entry_with_all_addressed_fields(self) -> None:
        """A known surface + resolvable section appends one fully-populated entry; exit 0."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            result = self._runner.invoke(
                main,
                [
                    "content",
                    "remember",
                    "AGENTS.md",
                    "--section",
                    "Behavior Rules",
                    "--text",
                    "Prefer stdlib JSONL for append-only stores.",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            corpus = Corpus.loads(
                (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(len(corpus.entries), 1)
            entry = corpus.entries[0]
            self.assertEqual(entry.surface, "AGENTS.md")
            self.assertEqual(entry.section, "behavior-rules")
            self.assertEqual(entry.tier, "compressible")
            self.assertEqual(entry.classification, "Ambiguous")
            self.assertTrue(entry.id)
            self.assertTrue(entry.ts)
            self.assertEqual(entry.text, "Prefer stdlib JSONL for append-only stores.")

    @covers("REQ-0.0.37-19-02")
    def test_does_not_modify_the_rendered_surface(self) -> None:
        """Capturing against AGENTS.md leaves it byte-unchanged — only the corpus store changes."""
        with self._runner.isolated_filesystem():
            surface = _seed_surface()
            before = surface.read_bytes()
            result = self._runner.invoke(
                main,
                [
                    "content",
                    "remember",
                    "AGENTS.md",
                    "--section",
                    "Prime Directive",
                    "--text",
                    "Own the work.",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(surface.read_bytes(), before)
            self.assertTrue((Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").exists())

    @covers("REQ-0.0.37-19-03")
    def test_emits_corpus_entry_appended_ledger_event(self) -> None:
        """A successful append emits corpus_entry_appended with surface/section/entry_id/tier."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            result = self._runner.invoke(
                main,
                [
                    "content",
                    "remember",
                    "AGENTS.md",
                    "--section",
                    "behavior-rules",
                    "--text",
                    "x",
                    "--tier",
                    "invariant",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            events = [e for e in _ledger_events() if e.get("event") == "corpus_entry_appended"]
            self.assertEqual(len(events), 1, msg=_ledger_events())
            event = events[0]
            self.assertEqual(event["surface"], "AGENTS.md")
            self.assertEqual(event["section"], "behavior-rules")
            self.assertEqual(event["tier"], "invariant")
            self.assertTrue(event["entry_id"])

    @covers("REQ-0.0.37-19-04")
    def test_fails_closed_on_unknown_surface(self) -> None:
        """An unknown surface (no file) aborts non-zero and writes no corpus entry."""
        with self._runner.isolated_filesystem():
            result = self._runner.invoke(
                main,
                ["content", "remember", "NOPE.md", "--section", "behavior-rules", "--text", "x"],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertFalse((Path(".gzkit") / "corpus" / "NOPE.md.jsonl").exists())

    @covers("REQ-0.0.37-19-04")
    def test_fails_closed_on_unaddressable_section(self) -> None:
        """A section that resolves to no Pillar aborts non-zero and writes no corpus entry."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            result = self._runner.invoke(
                main,
                ["content", "remember", "AGENTS.md", "--section", "no-such-section", "--text", "x"],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertFalse((Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").exists())


class TestContentRememberDriftWarning(unittest.TestCase):
    """Capture must announce the rendition drift it causes (GHI #654 gap 1).

    Behavior contract: appending to the corpus invalidates every committed rendition's
    derivation proof, so the next `gz check` fails on Rendition freshness. `remember`
    reported success and said nothing, making a silent red tree the normal outcome of
    capturing one line of canon. The warning is advisory — it never changes the exit
    code, because the append itself succeeded and IS the intended effect.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _remember(self, *extra: str) -> object:
        return self._runner.invoke(
            main,
            [
                "content",
                "remember",
                "AGENTS.md",
                "--section",
                "behavior-rules",
                "--text",
                "x",
                *extra,
            ],
        )

    @covers("REQ-0.35.0-08-03")
    def test_warns_naming_the_routed_consumer_not_the_retained_record(self) -> None:
        """A routed consumer is named; a retained off-route rendition is not.

        Amended REQ-0.35.0-08-03. The advisory's job is to say what recompose work
        is now due. An off-route rendition has none: the manifest declares it no
        setpoint, so `compose` cannot run for it, and doctrine forbids re-creating
        it as a consumer. Naming it prescribes an impossible and prohibited action.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_committed_rendition("root", corpus_fingerprint="0" * 64)
            _seed_committed_rendition("codex", corpus_fingerprint="0" * 64)
            result = self._remember()
            # output-contract: the warning IS the deliverable — GHI #654 gap 1 is that
            # remember produced no operator-visible signal at all.
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertNotIn("codex", result.output)
            self.assertIn("gz content compose", result.output)
            # Count and name are built from different expressions in production,
            # so assert both off the SAME rendered line: an implementation that
            # counts from the raw glob and names from the predicate would emit
            # "drifted 2 ... (root)" and pass a names-only check.
            match = re.search(
                r"drifted (\d+) committed rendition\(s\) of 'AGENTS\.md'\s*\n\s*\(([^)]*)\)",
                result.output,
            )
            self.assertIsNotNone(match, msg=result.output)
            assert match is not None
            self.assertEqual(int(match.group(1)), 1)
            self.assertEqual({name.strip() for name in match.group(2).split(",")}, {"root"})

    def test_invariant_tier_append_also_warns_about_the_floor(self) -> None:
        """An invariant-tier entry additionally breaks floor coherence; the warning says so."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_committed_rendition("root", corpus_fingerprint="0" * 64)
            result = self._remember("--tier", "invariant")
            # output-contract: floor coherence is a distinct gate from freshness; an
            # operator told only about freshness under-recovers.
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("floor", result.output.lower())

    def test_malformed_sidecar_never_costs_the_append_or_the_exit_code(self) -> None:
        """Drift detection is best-effort: a corrupt sidecar must not break capture.

        The append is durable before the advisory is computed, so a fault in the
        reporting path may cost the warning but never the operator's words.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_committed_rendition("root", corpus_fingerprint="0" * 64)
            # Corrupt the sidecar of the SEEDED, ON-ROUTE rendition. Pointing this at
            # an off-route or absent consumer would make the test vacuous: the
            # enumeration would never open the file, and the malformed-sidecar path
            # this test exists to exercise would not run.
            (Path(".gzkit") / "renditions" / "AGENTS.md" / "root.corpus.json").write_text(
                "{ not json at all", encoding="utf-8"
            )
            result = self._remember()
            self.assertEqual(result.exit_code, 0, msg=result.output)
            corpus = Corpus.loads(
                (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(len(corpus.entries), 1)

    def test_malformed_manifest_never_costs_the_exit_code(self) -> None:
        """A top-level non-object manifest must not turn capture into a failure.

        Enumeration asks the vendor manifest which consumers are routed, so a
        manifest fault is now reachable from the advisory — a channel that did
        not exist before the route filter. `[]` parses as valid JSON and then has
        no `.get`, and the seam's handler catches only `(OSError, ValueError)`,
        so an unguarded read raised AttributeError AFTER the corpus row was
        durable: the operator kept their words and lost their exit code, which
        the handler's own comment forbids in those terms.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_committed_rendition("root", corpus_fingerprint="0" * 64)
            manifest = Path("data") / "vendor-manifest.json"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text("[]", encoding="utf-8")
            result = self._remember()
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertNotIn("Unexpected error", result.output)
            corpus = Corpus.loads(
                (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(len(corpus.entries), 1)

    def test_silent_when_no_rendition_has_been_committed(self) -> None:
        """No committed rendition means the append drifted nothing — no false alarm."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            result = self._remember()
            # output-contract: a warning with no drifted rendition trains operators to
            # ignore the warning, which is the failure this fix exists to prevent.
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertNotIn("gz content compose", result.output)


class TestContentRememberRefusesLiveDuplicates(unittest.TestCase):
    """Capture refuses a text that is already live in the corpus (GHI #862).

    `gz content retire` already refuses a second retraction of the same id --
    "idempotent by refusal, not by silent re-append". Capture had no matching
    guard, so a re-import of already-captured canon doubled it silently: one
    2026-06-19 pass appended seven duplicates that every check read green,
    because byte-identical copies are both satisfied by one rendered occurrence.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _remember(self, text: str, section: str = "behavior-rules"):
        return self._runner.invoke(
            main,
            ["content", "remember", "AGENTS.md", "--section", section, "--text", text],
        )

    def test_refuses_a_second_append_of_live_text(self) -> None:
        """The second capture aborts and leaves the corpus at one entry."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            first = self._remember("Never create feature branches.")
            self.assertEqual(first.exit_code, 0)

            second = self._remember("Never create feature branches.")
            self.assertNotEqual(second.exit_code, 0)

            corpus = Corpus.loads(
                (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(len(corpus.entries), 1, "the refused append must not reach the store")

    def test_refusal_names_the_entry_already_holding_the_text(self) -> None:
        """A bare refusal makes the operator hunt; name the row that blocks it."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            self._remember("Work directly on main.")
            second = self._remember("Work directly on main.")
            corpus = Corpus.loads(
                (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_text(encoding="utf-8")
            )
            self.assertIn(corpus.entries[0].id, second.output)

    def test_refuses_across_sections(self) -> None:
        """Section is not part of the predicate.

        Six of the seven GHI #862 pairs sat in DIFFERENT sections -- a topical
        original plus a canon-section copy -- so a section-scoped check would
        have missed exactly the instances that motivated this guard.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            first = self._remember("Attestation is sacrosanct.", section="behavior-rules")
            self.assertEqual(first.exit_code, 0)
            # `prime-directive` must be a section the seeded surface actually
            # addresses -- an unaddressable one exits 1 on its own and would
            # make this test pass without the guard under exercise.
            second = self._remember("Attestation is sacrosanct.", section="prime-directive")
            self.assertNotEqual(second.exit_code, 0)

    def test_permits_re_capture_once_the_prior_copy_is_retired(self) -> None:
        """Retire-then-remember is the amendment path and must stay open.

        The operator ruling of 2026-08-22 permits toning down canon captured in
        frustration. Executing that means retiring the old wording and
        remembering the corrected one; a guard that counted retired rows would
        refuse the second half and make canon unamendable.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            self._remember("Original wording.")
            corpus = Corpus.loads(
                (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_text(encoding="utf-8")
            )
            entry_id = corpus.entries[0].id

            retired = self._runner.invoke(
                main,
                ["content", "retire", "AGENTS.md", "--entry", entry_id, "--reason", "toned down"],
            )
            self.assertEqual(retired.exit_code, 0)

            again = self._remember("Original wording.")
            self.assertEqual(again.exit_code, 0, "a retired copy must not block re-capture")


if __name__ == "__main__":
    unittest.main()


class TestRememberWitnessProvenance(unittest.TestCase):
    """`--witness` records WHO stands behind an entry, distinct from `--origin` (GHI #821).

    Measured 2026-08-18 before this landed: `CorpusEntry.witness` was set on 0 of
    65 live AGENTS.md entries — a model field no CLI path could reach — while
    `origin` carried the machine string `cli:content-remember` on 36 of them. The
    operator's identity, where recorded at all, had been smuggled into `origin` as
    free prose. The two fields answer different questions and must stay separable:
    `origin` is HOW the entry arrived, `witness` is WHO vouches for it.

    Capture must never be blocked (ADR-0.35.0 § Decision 7), so `--witness` is
    optional on every tier and its absence is never an error.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _remember(self, *extra: str) -> object:
        return self._runner.invoke(
            main,
            [
                "content",
                "remember",
                "AGENTS.md",
                "--section",
                "Behavior Rules",
                "--text",
                "Canon text.",
                *extra,
            ],
        )

    def _only_entry(self) -> object:
        corpus = Corpus.loads(
            (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_text(encoding="utf-8")
        )
        self.assertEqual(len(corpus.entries), 1)
        return corpus.entries[0]

    def test_witness_is_recorded_on_the_entry(self) -> None:
        """`--witness g0` reaches `CorpusEntry.witness` — the field stops being dead."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            self.assertEqual(self._remember("--witness", "g0").exit_code, 0)
            self.assertEqual(self._only_entry().witness, "g0")

    def test_witness_is_optional_and_capture_is_never_blocked(self) -> None:
        """No `--witness` → exit 0, entry written, witness None.

        Pins ADR-0.35.0 § Decision 7 against the obvious future tightening: making
        an invariant-tier append fail closed on a missing witness would trade the
        operator's words for a red tree, which the ADR forbids in those terms.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            self.assertEqual(self._remember("--tier", "invariant").exit_code, 0)
            self.assertIsNone(self._only_entry().witness)

    def test_witness_and_origin_are_independent_channels(self) -> None:
        """Supplying both keeps them distinct — witness never overwrites origin."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            self.assertEqual(self._remember("--witness", "g0", "--origin", "GHI #821").exit_code, 0)
            entry = self._only_entry()
            self.assertEqual(entry.witness, "g0")
            self.assertEqual(entry.origin, "GHI #821")
