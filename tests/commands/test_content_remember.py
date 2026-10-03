"""gz content remember command tests — OBPI-0.0.37-19 (BEHAVIOR REQ proofs).

REQ-derived from the brief's Acceptance Criteria, not from the implementation:
capture appends one addressed entry to the per-surface corpus store, emits a
corpus_entry_appended ledger event, NEVER edits a rendered surface, and fails
closed on an unknown surface or an unaddressable section.
"""

from __future__ import annotations

import contextlib
import errno
import io
import json
import re
import shlex
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

from gzkit.cli.main import main
from gzkit.content.models import Corpus
from gzkit.content.rendition_store import (
    RenditionProvenance,
    is_graded_rendition,
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


def _seed_committed_rendition(
    consumer: str, *, corpus_fingerprint: str, surface: str = "AGENTS.md"
) -> None:
    """Commit a rendition + provenance sidecar for <surface>/<consumer> in the cwd."""
    root = Path()
    save_rendition(root, surface, consumer, _SURFACE.encode("utf-8"))
    save_fingerprint(
        root,
        surface,
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


class _AdvisoryWriteFails(io.StringIO):
    """A stderr sink that raises OSError when the drift advisory is written; counts hits."""

    def __init__(self) -> None:
        super().__init__()
        self.hits = 0

    def write(self, text: str) -> int:
        if "Warning: this" in text:
            self.hits += 1
            raise OSError(errno.ENOSPC, "No space left on device (advisory sink)")
        return super().write(text)


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

    @covers("REQ-0.35.0-08-01")
    def test_append_survives_and_exit_stays_0_when_the_advisory_fires(self) -> None:
        """A drift-triggering append is never turned into a refusal.

        REQ-0.35.0-08-01: on the path where every committed rendition of the
        surface is left stale, the entry IS appended and the exit code is 0 --
        the advisory is additive, never a gate on the capture itself. Unlike
        `test_warns_naming_the_routed_consumer_not_the_retained_record`, which
        only asserts `exit_code == 0` and never reads the corpus back, this test
        proves the OTHER half of the REQ: the corpus on disk holds exactly the
        entry `remember` was asked to append.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_committed_rendition("root", corpus_fingerprint="0" * 64)
            result = self._remember()
            self.assertEqual(result.exit_code, 0, msg=result.output)
            # Premise guard: this is the advisory-fires path, not a silent one.
            self.assertIn("committed rendition(s)", result.output)
            corpus = Corpus.loads(
                (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(len(corpus.entries), 1)
            entry = corpus.entries[0]
            self.assertEqual(entry.surface, "AGENTS.md")
            self.assertEqual(entry.section, "behavior-rules")
            self.assertEqual(entry.text, "x")

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
            self.assertIn("gz content land AGENTS.md", result.output)
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

    @covers("REQ-0.35.0-08-04")
    def test_advisory_names_drift_cites_the_seam_and_gives_a_runnable_land(self) -> None:
        """The advisory carries all three parts of the guardrail-feedback bar.

        REQ-0.35.0-08-04: WHAT drifted (each rendition named), WHY (the
        ADR-0.0.37 corpus -> rendition seam, cited), and the GOVERNED NEXT STEP
        (`gz content land <surface>`), never the stale compose+commit recovery
        and never an auto-compose of the rendition.

        The next step is EXECUTED, not only matched: the printed invocation is
        extracted, its two placeholders filled, and run through the real CLI. The
        advisory fires exactly when a sidecar is frozen against another corpus
        fingerprint, the state in which `land` demands an attestor and text, so the
        printed command must carry those flags.

        Fixture limit, observed: in this minimal fixture `land` stops at candidate
        generation (no temperature in a vendor manifest; past that, the ownership
        declaration needs a ledger-witnessed genesis that only production modules
        this file does not import can write), which precedes the attestation check.
        So the printed command is extracted by shape (whatever verb and flags were
        printed), run through the real parser, and must reach the handler (exit 1,
        never the exit-2 usage error): a wrong verb or flag in the advisory fails
        there. Only then is it pinned to `content land` with both attestation flags.
        The attestation refusal itself is not reachable in this fixture.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_committed_rendition("root", corpus_fingerprint="0" * 64)
            result = self._remember()
            self.assertEqual(result.exit_code, 0, msg=result.output)
            # output-contract: the advisory prose IS the deliverable (GHI #654).
            self.assertRegex(result.output, r"\(root\)")
            self.assertRegex(result.output, r"corpus->rendition seam \(ADR-0\.0\.37")
            self.assertNotIn("gz content compose", result.output)
            self.assertNotIn("gz content commit", result.output)
            # The advisory never auto-landed: `remember` left the rendition untouched.
            sidecar_path = Path(".gzkit") / "renditions" / "AGENTS.md" / "root.corpus.json"
            sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
            self.assertEqual(sidecar["corpus_fingerprint"], "0" * 64)

            # Match the command by SHAPE, not by its tokens, so a wrong verb or flag in
            # the advisory reaches the real parser instead of failing the extraction.
            printed = re.search(
                r"(?m)^\s*(uv run gz content \S+ AGENTS\.md\s*\\\n"
                r"\s*--\S+ <handle> --\S+ \"<[^\"]*>\")\s*$",
                result.output,
            )
            self.assertIsNotNone(printed, msg=result.output)
            assert printed is not None
            command = printed.group(1).replace("\\\n", " ")
            command = command.replace("<handle>", "g0")
            command = re.sub(r'"<[^"]*>"', '"the operator words"', command)
            argv = shlex.split(command)
            self.assertEqual(argv[:3], ["uv", "run", "gz"], msg=command)
            landed = self._runner.invoke(main, argv[3:])
            # Exit 2 is the parser rejecting the verb or a flag; the handler's own
            # refusals exit 1. A wrong verb or flag fails here.
            self.assertEqual(landed.exit_code, 1, msg=landed.output)
            self.assertNotIn("unrecognized arguments", landed.output)
            self.assertNotIn("invalid choice", landed.output)
            self.assertIn("could not be generated", landed.output)
            # Only now, with the parser satisfied, pin that it is the governed command.
            self.assertEqual(argv[3:5], ["content", "land"], msg=command)
            self.assertIn("--attestor", argv)
            self.assertIn("--attestation-text", argv)

    @covers("REQ-0.35.0-08-01")
    def test_advisory_output_fault_never_costs_the_exit_code(self) -> None:
        """A stderr sink that raises while the advisory is written cannot cost the exit.

        Brief Requirement 1: on EVERY path the entry is appended and the exit stays 0.
        Emission is part of the path: the row is durable before the advisory is
        written, so an output fault may cost the warning, never the exit code.
        Paired fixtures share one sink; only the stale rendition differs.
        """

        def run(*, stale: bool) -> tuple[object, list]:
            with self._runner.isolated_filesystem():
                _seed_surface()
                if stale:
                    _seed_committed_rendition("root", corpus_fingerprint="0" * 64)
                stderr = _AdvisoryWriteFails()
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                    try:
                        code = main(
                            ["content", "remember", "AGENTS.md", "--section", "behavior-rules"]
                            + ["--text", "durable capture"]
                        )
                    except SystemExit as exc:
                        code = exc.code
                entries = Corpus.loads(
                    (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_text(encoding="utf-8")
                ).entries
                return (code or 0), list(entries)

        control_code, control_rows = run(stale=False)
        self.assertEqual(control_code, 0)
        self.assertEqual(len(control_rows), 1)
        code, rows = run(stale=True)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].text, "durable capture")
        self.assertEqual(code, 0, "an advisory output fault must not change the exit code")

    @covers("REQ-0.35.0-08-04")
    def test_printed_command_quotes_a_surface_name_containing_a_space(self) -> None:
        """The printed land command is runnable for a surface whose name has a space.

        An unquoted surface splits into two positionals and the parser exits 2
        (`unrecognized arguments`). The command is extracted by shape, the surface
        must arrive as ONE argv token equal to the real name, and the real parser
        must accept it (the handler's exit 1, never the parser's exit 2).
        """
        surface = "Land Surface.md"
        with self._runner.isolated_filesystem():
            _seed_surface(surface)
            _seed_committed_rendition("root", corpus_fingerprint="0" * 64, surface=surface)
            result = self._runner.invoke(
                main,
                ["content", "remember", surface, "--section", "behavior-rules", "--text", "x"],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("committed rendition(s)", result.output)
            printed = re.search(
                r"(?m)^\s*(uv run gz content \S+ (?:'[^']*'|\S+)\s*\\\n"
                r"\s*--\S+ <handle> --\S+ \"<[^\"]*>\")\s*$",
                result.output,
            )
            self.assertIsNotNone(printed, msg=result.output)
            assert printed is not None
            command = printed.group(1).replace("\\\n", " ").replace("<handle>", "g0")
            command = re.sub(r'"<[^"]*>"', '"the operator words"', command)
            argv = shlex.split(command)
            self.assertIn(surface, argv, msg=command)
            landed = self._runner.invoke(main, argv[3:])
            self.assertEqual(landed.exit_code, 1, msg=landed.output)
            self.assertNotIn("unrecognized arguments", landed.output)

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

    @covers("REQ-0.35.0-08-02")
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
            # Premise guard: the advisory is silent on this fault path, so prove the
            # enumeration grades the seeded rendition (and so opens the corrupt sidecar).
            self.assertTrue(
                is_graded_rendition(Path(".gzkit") / "renditions" / "AGENTS.md" / "root.md", Path())
            )
            result = self._remember()
            self.assertEqual(result.exit_code, 0, msg=result.output)
            corpus = Corpus.loads(
                (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(len(corpus.entries), 1)

    @covers("REQ-0.35.0-08-02")
    def test_drift_detection_raising_oserror_never_costs_the_append_or_the_exit_code(
        self,
    ) -> None:
        """The seam's OSError arm: an unreadable corpus/rendition store at advisory time.

        The sibling malformed-sidecar test exercises the ValueError arm. This one
        makes the sidecar unreadable (a directory in its place) so the production
        read raises OSError AFTER the row is durable; narrowing the handler to
        ValueError fails here.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_committed_rendition("root", corpus_fingerprint="0" * 64)
            # Real unreadable evidence: a DIRECTORY where the sidecar file should be
            # makes `read_text` raise an OSError subclass on every platform.
            sidecar = Path(".gzkit") / "renditions" / "AGENTS.md" / "root.corpus.json"
            sidecar.unlink()
            sidecar.mkdir()
            # Premise guard: the enumeration grades the seeded rendition, so it reads
            # the unreadable sidecar rather than skipping it.
            self.assertTrue(
                is_graded_rendition(Path(".gzkit") / "renditions" / "AGENTS.md" / "root.md", Path())
            )
            result = self._remember()
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertNotIn("Unexpected error", result.output)
            corpus = Corpus.loads(
                (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(len(corpus.entries), 1)
            self.assertEqual(corpus.entries[0].text, "x")

    @covers("REQ-0.35.0-08-06")
    def test_exit_code_and_row_are_identical_with_and_without_drift_under_an_output_fault(
        self,
    ) -> None:
        """REQ-0.35.0-08-06: "...BYTE-IDENTICAL and the exit code is identical".

        The exit-code clause is the half a quiet run cannot falsify: without an
        output fault, drift and no-drift both exit 0 whatever the code does. Under a
        stderr sink that raises when the advisory is written, a run that lets the
        fault escape exits 1 with drift and 0 without, so the paired form is what
        makes "identical" bite. Both runs share one frozen clock and the same sink
        class; only the stale rendition differs.
        """
        frozen = datetime(2026, 10, 3, 12, 0, 0, tzinfo=UTC)

        def run(*, stale: bool) -> tuple[object, bytes, int]:
            with self._runner.isolated_filesystem():
                _seed_surface()
                if stale:
                    _seed_committed_rendition("root", corpus_fingerprint="0" * 64)
                sink = _AdvisoryWriteFails()
                with (
                    mock.patch("gzkit.commands.content.remember.datetime") as clock,
                    contextlib.redirect_stdout(io.StringIO()),
                    contextlib.redirect_stderr(sink),
                ):
                    clock.now.return_value = frozen
                    try:
                        code = main(
                            ["content", "remember", "AGENTS.md", "--section", "behavior-rules"]
                            + ["--text", "x"]
                        )
                    except SystemExit as exc:
                        code = exc.code
                corpus = (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_bytes()
                return (code or 0), corpus, sink.hits

        drift_code, drift_bytes, drift_hits = run(stale=True)
        quiet_code, quiet_bytes, quiet_hits = run(stale=False)
        self.assertGreater(drift_hits, 0, "the drift run must attempt the advisory")
        self.assertEqual(quiet_hits, 0, "the no-drift run must not")
        self.assertEqual(drift_code, quiet_code, "exit code must be identical")
        self.assertEqual(drift_bytes, quiet_bytes)
        self.assertEqual(drift_code, 0)

    @covers("REQ-0.35.0-08-06")
    def test_corpus_row_is_byte_identical_with_and_without_drift(self) -> None:
        """The advisory never alters what is appended (paired fixtures, one clock).

        REQ-0.35.0-08-06: the same append, once where a committed rendition is
        left stale (advisory fires) and once where none exists (silent), writes
        byte-identical corpus rows and the same exit code. The clock in
        `remember.py` stamps both `ts` and the entry id, so it is frozen.
        """
        frozen = datetime(2026, 10, 3, 12, 0, 0, tzinfo=UTC)
        outcomes: list[tuple[int, bytes, str]] = []
        for with_drift in (True, False):
            with self._runner.isolated_filesystem():
                _seed_surface()
                if with_drift:
                    _seed_committed_rendition("root", corpus_fingerprint="0" * 64)
                with mock.patch("gzkit.commands.content.remember.datetime") as clock:
                    clock.now.return_value = frozen
                    result = self._remember()
                corpus_bytes = (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_bytes()
                outcomes.append((result.exit_code, corpus_bytes, result.output))
        (drift_exit, drift_bytes, drift_out), (quiet_exit, quiet_bytes, quiet_out) = outcomes
        # Guard the fixtures: the paired runs must actually differ in advisory.
        self.assertIn("committed rendition(s)", drift_out)
        self.assertNotIn("committed rendition(s)", quiet_out)
        self.assertEqual(drift_exit, quiet_exit)
        self.assertEqual(drift_exit, 0)
        self.assertEqual(drift_bytes, quiet_bytes)

    # No @covers here. `vendors.py::_read_manifest_key` (809f1370) added
    # `if not isinstance(data, dict): return {}`, so a `[]` manifest now
    # returns `{}` cleanly and `drifted_consumers()` completes without
    # raising — `_drift.py`'s `except (OSError, ValueError)` handler is
    # never entered. This test proves that defensive-parsing regression
    # guard in `vendors.py`, not REQ-0.35.0-08-02's raise-survival claim
    # (drift detection RAISING must still cost neither the append nor the
    # exit code). That claim is proven by
    # `test_malformed_sidecar_never_costs_the_append_or_the_exit_code`,
    # which genuinely raises via `RenditionProvenance.model_validate_json`.
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

    @covers("REQ-0.35.0-08-05")
    def test_silent_when_no_rendition_has_been_committed(self) -> None:
        """No committed rendition means the append drifted nothing — no false alarm.

        Asserts the absence of the advisory's structural markers, not one
        particular incantation. `warn_on_rendition_drift` (`_drift.py`) emits
        the "Warning:" banner and the "drifted ... committed rendition(s)"
        line unconditionally whenever it fires at all — those two are the
        real claim that "NO advisory is emitted" makes. A prior version of
        this test asserted only the absence of the literal substring
        "gz content compose", which a regression emitting any other non-empty
        advisory (or unrelated stderr noise) would pass silently. Asserting
        stderr is empty is inexpressible through this harness: `CliRunner`
        merges stdout/stderr into one buffer (`tests/commands/common.py`), so
        that clause of the REQ cannot be proven here (residual, tracked in
        the OBPI brief).
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            result = self._remember()
            # output-contract: a warning with no drifted rendition trains operators to
            # ignore the warning, which is the failure this fix exists to prevent.
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertNotIn("Warning:", result.output)
            self.assertNotIn("committed rendition(s)", result.output)
            self.assertNotIn("gz content land", result.output)


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


if __name__ == "__main__":
    unittest.main()
