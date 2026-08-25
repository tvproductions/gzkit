"""gz content retire command tests — append-only corpus retirement (GHI #635).

The corpus store has no delete, so a superseded operator directive bound the
invariant floor forever and the only escape was hand-editing the append-only
JSONL. These tests pin the governed alternative: a retraction row that retires
an id without removing it, shrinking the floor rather than growing it.
"""

from __future__ import annotations

import json
import re
import shlex
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.content.models import Corpus
from gzkit.content.models.corpus import effective_corpus
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    is_graded_rendition,
    save_fingerprint,
    save_rendition,
)
from gzkit.content.tier_policy import invariant_entries
from gzkit.traceability import covers
from gzkit.validate_pkg.ledger_check import validate_ledger
from tests.commands.common import CliRunner

_SURFACE = """# Test Agent Contract

Purpose line.

## Behavior Rules

- Do the thing.

## Prime Directive

- Own it.
"""

_CORPUS_PATH = Path(".gzkit") / "corpus" / "AGENTS.md.jsonl"

# The citation check must read the REAL repo: these tests run inside
# isolated_filesystem(), where a relative rule path resolves to an empty sandbox
# and every citation would 'not exist' for a reason unrelated to the citation.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _seed_surface(name: str = "AGENTS.md") -> Path:
    path = Path(name)
    path.write_text(_SURFACE, encoding="utf-8")
    return path


def _load_corpus() -> Corpus:
    return Corpus.loads(_CORPUS_PATH.read_text(encoding="utf-8"))


def _corpus_fingerprint() -> str:
    """Production fingerprint of the corpus on disk.

    Replaces raw ``Path.read_bytes()`` comparison in the fail-closed tests. This is
    the stronger assertion, not a workaround for the tautological-test audit: it is
    the same digest `gz validate --rendition-freshness` reads, so "the corpus did not
    move" is asserted in the units the rest of the system uses, and the filesystem
    read lives here rather than in a test body that is about behavior.
    """
    return corpus_fingerprint(_load_corpus())


def _corpus_store_exists() -> bool:
    """Whether the per-surface corpus store file exists."""
    return _CORPUS_PATH.exists()


def _section_present_in(filename: str, section: str) -> tuple[bool, bool]:
    """Return (file_exists, section_present) for a cited `<file> § <section>`."""
    path = Path(_PROJECT_ROOT) / filename
    if not path.exists():
        return (False, False)
    return (True, section in path.read_text(encoding="utf-8"))


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
            [
                "content",
                "retire",
                "AGENTS.md",
                "--entry",
                entry_id,
                "--reason",
                "superseded",
                "--attestor",
                "g0",
            ],
        )

    @covers("REQ-0.35.0-08-03")
    def test_warns_naming_the_routed_consumer_not_the_retained_record(self) -> None:
        """The operator learns which renditions this retirement just unprovable-ised.

        Amended REQ-0.35.0-08-03: only the routed consumer, because only it has
        recompose work due. Both verbs share one advisory, so the retire side
        must reach the same verdict as the remember side.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("Some directive.")
            _seed_committed_rendition("root", corpus_fingerprint="stale-root")
            _seed_committed_rendition("codex", corpus_fingerprint="stale-codex")

            result = self._retire(entry_id)
            self.assertIn("root", result.output)
            self.assertNotIn("codex", result.output)
            self.assertIn("Rendition freshness", result.output)

    @covers("REQ-0.35.0-08-08")
    def test_advisory_names_exactly_what_the_gates_grade(self) -> None:
        """REQ-0.35.0-08-08 — the advisory's count AND names equal the graded set.

        The advisory's entire content is a claim about which gates will now fail,
        so it must enumerate by the predicate those gates share. Both halves are
        parsed from the SAME rendered line, because the count and the names are
        built from different expressions in production: an implementation that
        counted from the raw glob and named from the predicate would emit
        "drifted 2 committed rendition(s) ... (root)" and satisfy a names-only
        assertion while reproducing the operator confusion this REQ exists to
        remove.

        `graded` is derived, never pinned to a literal. A hardcoded expectation
        would collapse the parity claim to "names == {root}", which a private
        copy of the predicate — a bare glob plus `stem != "codex"` — satisfies,
        and that copy is precisely what this REQ forbids. Non-triviality is
        asserted structurally instead: the directory must hold more renditions
        than survive grading, so an implementation excluding nothing fails.

        Scope note: the candidate arm of `is_graded_rendition` is subsumed here
        rather than witnessed. A candidate is `<consumer>.candidate.md`, so its
        stem is never itself a routed consumer and the route arm rejects it
        first. The arm is decisive only when the route set is empty. Tracked
        rather than asserted, because the predicate belongs to a terminal brief.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("Some directive.")
            _seed_committed_rendition("root", corpus_fingerprint="stale-root")
            _seed_committed_rendition("codex", corpus_fingerprint="stale-codex")
            # A sidecar, so the candidate is excluded by the PREDICATE rather than
            # by the `provenance is not None` skip further down — without it this
            # arm of the fixture proves nothing about grading.
            _seed_committed_rendition("root.candidate", corpus_fingerprint="stale-cand")

            result = self._retire(entry_id)

            rendition_dir = Path(".gzkit") / "renditions" / "AGENTS.md"
            on_disk = {path.stem for path in rendition_dir.glob("*.md")}
            graded = {
                path.stem
                for path in rendition_dir.glob("*.md")
                if is_graded_rendition(path, Path())
            }
            self.assertTrue(graded, msg="fixture must leave something to grade")
            self.assertLess(len(graded), len(on_disk), msg="fixture must exercise an exclusion")

            # Parse the advisory's own header so count and names come from one
            # source and cannot be satisfied independently.
            match = re.search(
                r"drifted (\d+) committed rendition\(s\) of 'AGENTS\.md'\s*\n\s*\(([^)]*)\)",
                result.output,
            )
            self.assertIsNotNone(match, msg=result.output)
            assert match is not None
            named = {name.strip() for name in match.group(2).split(",")}
            self.assertEqual(named, graded)
            self.assertEqual(int(match.group(1)), len(graded))

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
                [
                    "content",
                    "retire",
                    "AGENTS.md",
                    "--entry",
                    old,
                    "--reason",
                    "superseded",
                    "--attestor",
                    "g0",
                ],
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
                [
                    "content",
                    "retire",
                    "AGENTS.md",
                    "--entry",
                    old,
                    "--reason",
                    "superseded",
                    "--attestor",
                    "g0",
                ],
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
                [
                    "content",
                    "retire",
                    "AGENTS.md",
                    "--entry",
                    old,
                    "--reason",
                    "superseded",
                    "--attestor",
                    "g0",
                ],
            )

            self.assertEqual(surface.read_bytes(), before)

    def test_emits_a_corpus_entry_retired_event(self) -> None:
        """Retirement is witnessed at Layer 2 distinctly from a plain append."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            old = self._remember("superseded doctrine")

            self._runner.invoke(
                main,
                [
                    "content",
                    "retire",
                    "AGENTS.md",
                    "--entry",
                    old,
                    "--reason",
                    "quote-style drift",
                    "--attestor",
                    "g0",
                ],
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
            before = _corpus_fingerprint()

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
            self.assertEqual(_corpus_fingerprint(), before)

    def test_double_retirement_fails_closed(self) -> None:
        """Retiring an already-retired entry refuses rather than appending a second retraction.

        The fixture is `compressible` deliberately. Under the class default
        (`invariant`) the FIRST retirement now fails at the corpus-attestation gate,
        so nothing is ever retired and the second call refuses for that reason instead
        -- deleting the already-retired branch entirely would not change the outcome.
        The test kept passing while measuring nothing (OBPI-0.35.0-02 spec review;
        AGENTS.md Invariant 1a -- a change that alters a surface another test reads is
        repaired in the same commit).

        The premise assertion below is the durable half: it fails loudly if the first
        retirement ever stops succeeding, rather than letting this silently go vacuous
        again the next time a gate is added upstream.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            old = self._remember("superseded doctrine", tier="compressible")
            first = self._runner.invoke(
                main,
                ["content", "retire", "AGENTS.md", "--entry", old, "--reason", "first"],
            )
            self.assertEqual(first.exit_code, 0, msg=f"premise broken: {first.output}")
            self.assertIn(old, _load_corpus().retired_ids())
            before = _corpus_fingerprint()

            result = self._runner.invoke(
                main,
                ["content", "retire", "AGENTS.md", "--entry", old, "--reason", "second"],
            )

            self.assertEqual(result.exit_code, 1)
            self.assertEqual(_corpus_fingerprint(), before)


class TestContentRetireAttestation(unittest.TestCase):
    """Tier-discriminated corpus attestation on retirement (OBPI-0.35.0-02).

    An invariant-tier entry is the 0-Kelvin floor every rendition must carry
    verbatim; un-binding it without a named attestor leaves no human name on
    the decision. Compressible-tier retirement stays frictionless.
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

    def _retire(self, entry_id: str, *, args: list[str]):
        return self._runner.invoke(
            main,
            ["content", "retire", "AGENTS.md", "--entry", entry_id, *args],
        )

    @covers("REQ-0.35.0-02-01")
    def test_invariant_tier_retirement_without_reason_fails_closed(self) -> None:
        """Brief Requirement 2 gates on `--attestor` OR `--reason`, not attestor alone.

        The cell nobody tested: a named attestor with `--reason` omitted entirely.
        `--reason` defaults to "" at the parser, so the whitespace guard (which fires
        only on a non-empty all-space value) never sees it, and a gate written against
        the attestor half alone lets a 0-Kelvin-floor entry be un-bound.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("floor text", tier="invariant")
            before = _corpus_fingerprint()
            events_before = len(_ledger_events())
            result = self._retire(entry_id, args=["--attestor", "g0"])
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_corpus_fingerprint(), before)
            self.assertEqual(len(_ledger_events()), events_before)

    @covers("REQ-0.35.0-02-02")
    def test_compressible_tier_still_refuses_whitespace_only_attestor(self) -> None:
        """The whitespace refusal is deliberately broader than REQ-02's literal text.

        REQ-02 scopes the whitespace cases to the invariant-tier invocation; the
        implementation refuses on every tier. Fail-closed-broader is defensible, but an
        unpinned extension is indistinguishable from an accident, so it is covered here.
        Distinct from REQ-03: that concerns an OMITTED flag, this a supplied-but-empty one.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("routine text", tier="compressible")
            before = _corpus_fingerprint()
            result = self._retire(entry_id, args=["--attestor", "   ", "--reason", "why"])
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_corpus_fingerprint(), before)

    def _recovery_commands(self, output: str) -> list[str]:
        """Every `gz ...` command the recovery prose tells the operator to run."""
        return re.findall(r"`(gz [^`]+)`", output)

    def _assert_recovery_commands_run(self, output: str) -> None:
        """Every recommended command must actually parse and run (Invariant 6g).

        A substring assertion on our own stderr passes for ANY string, including one
        naming a verb that does not exist -- which is exactly how `gz content list
        <surface>` shipped. This invokes what the prose recommends and fails on an
        argparse rejection, so a fabricated incantation cannot pass again.
        """
        commands = self._recovery_commands(output)
        self.assertTrue(commands, msg=f"recovery prose named no runnable command: {output}")
        for cmd in commands:
            argv = shlex.split(cmd)[1:]
            # Placeholder operands (`<your name>`) are the operator's to fill. SUBSTITUTE
            # rather than strip: stripping leaves a required-value flag with no value, so
            # argparse errors on THAT before it ever reaches the rest of the command, and
            # a later flag's rename would slip past the checks below unseen. Substituting
            # exercises the whole parse. A dummy value may fail at RUNTIME (no such entry),
            # which is fine -- the assertions below test the command's shape, not its luck.
            probe = ["_probe_" if a.startswith("<") else a for a in argv]
            outcome = self._runner.invoke(main, probe)
            # The list is exhaustive over argparse's REJECTION vocabulary, not a
            # sample of it. An earlier version checked only the first two, and two
            # further broken retries shipped past it -- both refused with "the
            # following arguments are required", a phrase the helper never looked
            # for (Codex tier-1 refutation, 2026-08-25). Fixing the instance while
            # leaving the assertion list narrow is how the same defect returns
            # through a door left open on purpose.
            for rejection in (
                "unrecognized arguments",
                "invalid choice",
                "the following arguments are required",
                "expected one argument",
                "not allowed with argument",
            ):
                self.assertNotIn(
                    rejection,
                    outcome.output,
                    msg=(
                        f"recovery prose recommends a command argparse rejects "
                        f"({rejection!r}): {cmd}\n{outcome.output}"
                    ),
                )

    def _assert_citations_resolve(self, output: str) -> None:
        """Every `<file> § <section>` citation must resolve in the file it names.

        `.claude/rules/guardrail-feedback-prose.md` requires the rule be CITED, not
        paraphrased. A citation naming a section absent from the named file sends the
        operator somewhere the answer is not -- and no exit-code assertion can see it.
        """
        cites = re.findall(r"([\w./-]+\.md) § ([^;:\n(]+)", output)
        self.assertTrue(cites, msg=f"recovery prose cited no rule: {output}")
        for filename, section in cites:
            needle = section.strip().rstrip("—-").strip()
            exists, present = _section_present_in(filename, needle)
            self.assertTrue(exists, msg=f"cited file does not exist: {filename}")
            # assertIn would dump the entire cited file into the failure message;
            # assertTrue keeps the signal to the one fact that matters.
            self.assertTrue(
                present,
                msg=f"cited section {needle!r} not found in {filename}",
            )

    @covers("REQ-0.35.0-02-03")
    def test_every_retirement_emits_a_ledger_event_the_validator_accepts(self) -> None:
        """The retirement's ledger event must survive `gz validate --ledger`.

        REQ-03 was first read as "compressible retirement needs NEITHER flag", which made
        `--reason` optional -- and `reason` is load-bearing on two surfaces the REQ never
        mentions: it becomes the retraction row's text, and the corpus_entry_retired
        event's `reason`, which `ledger_check` guards with min_length=1 over
        `value.strip()`. An omitted reason therefore wrote an event the validator
        rejects, and no exit-code assertion could see it -- these tests run in an
        isolated filesystem and never invoke the validator.

        Operator ruling 2026-08-25: keep `--reason` required on every tier and relax only
        `--attestor`, honouring REQ-03's stated rationale ("the corpus attestation guards
        the 0-Kelvin floor, not routine retirement"), which is about the attestor.

        This runs the REAL validator over the REAL emitted event, so the coupling is
        held by a witness rather than by the memory of having checked it once.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("routine text", tier="compressible")
            result = self._retire(entry_id, args=["--reason", "superseded"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            emitted = [e for e in _ledger_events() if e["event"] == "corpus_entry_retired"]
            self.assertEqual(len(emitted), 1, msg=f"events: {emitted}")

            ledger_path = Path(".gzkit") / "ledger.jsonl"
            errors = validate_ledger(ledger_path)
            offending = [e for e in errors if "corpus_entry" in (e.artifact or "")]
            self.assertEqual(offending, [], msg=f"validator rejected the event: {offending}")

    @covers("REQ-0.35.0-02-06")
    def test_help_documents_the_attestation_gate_it_actually_enforces(self) -> None:
        """`--help` must describe the gate the code enforces, not an earlier one.

        The help text is the only place an operator learns the requirement BEFORE
        tripping it, and it drifted once already: while the gate checked `--attestor`
        alone it read "needs neither --attestor nor --reason", which stayed on the page
        after the gate changed. Nothing pinned it, so nothing would have caught the
        re-drift either (OBPI-0.35.0-02 spec re-review; AGENTS.md Invariant 1a).

        Asserted as behaviour rather than as a string match on one sentence: the help
        must name `--attestor` as the invariant-tier requirement, and must NOT still
        claim a tier exists that needs neither flag.
        """
        output = self._runner.invoke(main, ["content", "retire", "--help"]).output
        self.assertIn("--attestor", output)
        self.assertIn("invariant", output)
        self.assertNotIn("neither --attestor nor --reason", output)

    @covers("REQ-0.35.0-02-01")
    def test_an_invisible_attestor_is_not_a_named_human(self) -> None:
        """U+200B ZERO WIDTH SPACE must not pass as an attestor.

        `.strip()` does not remove it — U+200B is not in Unicode's `White_Space`
        property — so it survives every whitespace guard and satisfies truthiness.
        The tier-1 adversary retired an invariant-tier entry with it and the ledger
        recorded the invisible string as the human who authorized the change
        (`RETIRE_EXIT=0`, `LEDGER_ATTESTOR='\u200b'`, 2026-08-25). A gate whose whole
        guarantee is "a human name is on this decision" cannot accept a value with no
        visible glyph.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("floor doctrine", tier="invariant")
            before = _corpus_fingerprint()
            result = self._retire(entry_id, args=["--reason", "superseded", "--attestor", "\u200b"])
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_corpus_fingerprint(), before)
            self._assert_recovery_commands_run(result.output)

    @covers("REQ-0.35.0-02-01")
    def test_retiring_a_tombstone_that_revives_a_floor_entry_needs_an_attestor(self) -> None:
        """The gate must read what a retirement DOES, not what it is aimed at.

        Retiring a tombstone REVIVES whatever it retired (Algebra 6). A tombstone is
        always written `compressible`, so a gate keyed on `target.tier` waves it
        through — and invariant-tier canon re-enters the effective view with no
        attestor recorded anywhere. The tier-1 adversary reproduced exactly this:
        `SECOND_EXIT_NO_ATTESTOR=0`, `ORIGINAL_EFFECTIVE_AFTER_SECOND=True`
        (2026-08-25). The bypass INVERTS the guarantee — the floor moves precisely
        because the row aimed at was not floor-tier.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            floor_id = self._remember("floor doctrine", tier="invariant")
            first = self._retire(floor_id, args=["--reason", "superseded", "--attestor", "g0"])
            self.assertEqual(first.exit_code, 0, msg=f"premise broken: {first.output}")
            tombstone = _load_corpus().entries[-1]
            self.assertEqual(tombstone.tier, "compressible", "premise: tombstones are compressible")
            self.assertEqual(tombstone.retires, floor_id, "premise: it retires the floor entry")

            before = _corpus_fingerprint()
            second = self._retire(tombstone.id, args=["--reason", "undo"])
            self.assertNotEqual(
                second.exit_code,
                0,
                msg=f"reviving invariant canon needs an attestor: {second.output}",
            )
            self.assertEqual(_corpus_fingerprint(), before)
            self.assertIn(floor_id, second.output, "the refusal must name the entry at risk")

    @covers("REQ-0.35.0-02-01")
    def test_a_two_hop_tombstone_chain_still_needs_an_attestor(self) -> None:
        """`invariant -> tombstone -> tombstone`: retiring the SECOND one moves the floor.

        The first fix here walked ONE tombstone edge, and an independent review found
        the chain it misses: retiring the second tombstone drops the invariant back out
        of the effective corpus with no attestor required (2026-08-25). Two hops would
        then have missed three — any finite hop count is the wrong shape of answer.

        The gate now computes a before/after delta over the fold, so this test is not
        really about "two hops": it pins that the question asked is *does the floor
        move*, which is hop-count independent by construction.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            floor_id = self._remember("floor doctrine", tier="invariant")

            first = self._retire(floor_id, args=["--reason", "superseded", "--attestor", "g0"])
            self.assertEqual(first.exit_code, 0, msg=f"premise: {first.output}")
            tomb1 = _load_corpus().entries[-1].id

            # Retiring tomb1 REVIVES the invariant. That is floor movement too, so it
            # is attested -- supply one, keeping the chain building.
            second = self._retire(tomb1, args=["--reason", "undo", "--attestor", "g0"])
            self.assertEqual(second.exit_code, 0, msg=f"premise: {second.output}")
            tomb2 = _load_corpus().entries[-1].id
            self.assertIn(
                floor_id,
                {e.id for e in effective_corpus(_load_corpus()).entries},
                "premise: the invariant is live again after the second retirement",
            )

            # Now the two-hop case: retiring tomb2 re-arms tomb1, which re-retires the
            # invariant. Nothing in this invocation names a floor-tier row.
            before = _corpus_fingerprint()
            third = self._retire(tomb2, args=["--reason", "redo"])
            self.assertNotEqual(
                third.exit_code,
                0,
                msg=f"two-hop floor movement must still require an attestor: {third.output}",
            )
            self.assertEqual(_corpus_fingerprint(), before)
            self.assertIn(floor_id, third.output, "the refusal must name the entry at risk")

    @covers("REQ-0.35.0-02-02")
    def test_the_handler_enforces_reason_without_relying_on_argparse(self) -> None:
        """`required=True` does not mean non-empty — `--reason ""` satisfies argparse.

        The tier-1 adversary reached the handler with `reason=""` and retired a row,
        writing an event `gz validate --ledger` then rejected (`DIRECT_EXIT=0`,
        `LEDGER_ERRORS=["Field 'reason' must be at least 1 ..."]`). It called the
        handler directly, but the same hole is reachable straight through the CLI: the
        flag IS present, so argparse is satisfied, and only a handler-side check stops
        it. A contract enforced at the front door alone is not enforced.

        Driven through the CLI rather than by importing the handler on purpose: this
        test file also `@covers` OBPI-0.35.0-08's REQs, and a module-level import of
        `retire.py` pulls it into THAT brief's allowlist scan (measured: brief-reconcile
        drift on a brief this OBPI does not touch). The public surface proves the same
        thing without leaking scope across briefs.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("routine note", tier="compressible")
            before = _corpus_fingerprint()
            result = self._retire(entry_id, args=["--reason", "", "--attestor", "g0"])
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_corpus_fingerprint(), before)

    @covers("REQ-0.35.0-02-04")
    def test_a_legacy_format_row_is_normalized_not_preserved_byte_for_byte(self) -> None:
        """Pins the REAL boundary of REQ-04's "verbatim", including where it does NOT hold.

        The byte-identity test seeds its row through the CURRENT serializer, which makes
        byte-stability true by construction — an independent review called that circular,
        and it was right (2026-08-25). `corpus_store.append_entry` reloads and rewrites
        the ENTIRE store through `Corpus.dumps`, so a row persisted in an older shape
        (reordered keys, explicit nulls, spaces after separators) is rewritten on the
        next append.

        This test asserts what is ACTUALLY true rather than the claim that is not:
        the retired entry SURVIVES with every field intact, while its byte encoding is
        normalized. Preserving original bytes would mean appending without reserializing,
        which is `corpus_store.py` — a Denied Path for this OBPI, so the behavior is
        pinned and disclosed here rather than silently asserted away.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _CORPUS_PATH.parent.mkdir(parents=True, exist_ok=True)
            legacy = (
                '{"ts": "2026-01-01T00:00:00+00:00", "origin": "probe", '
                '"text": "floor text", "classification": "Mechanical", '
                '"tier": "invariant", "section": "prime-directive", '
                '"surface": "AGENTS.md", "id": "legacy-row", '
                '"retires": null, "supersedes": null}'
            )
            _CORPUS_PATH.write_text(legacy + "\n", encoding="utf-8")
            before_line = _CORPUS_PATH.read_text(encoding="utf-8").splitlines()[0]

            result = self._retire("legacy-row", args=["--reason", "superseded", "--attestor", "g0"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            after_line = next(
                line
                for line in _CORPUS_PATH.read_text(encoding="utf-8").splitlines()
                if '"legacy-row"' in line
            )
            # Disclosed, not asserted away: the bytes DO change for a legacy row.
            self.assertNotEqual(
                before_line, after_line, "premise: append_entry reserializes the store"
            )
            # What REQ-04 actually protects: the entry survives, whole.
            survivor = next(e for e in _load_corpus().entries if e.id == "legacy-row")
            self.assertEqual(survivor.text, "floor text")
            self.assertEqual(survivor.tier, "invariant")
            self.assertEqual(survivor.origin, "probe")
            self.assertEqual(survivor.ts, "2026-01-01T00:00:00+00:00")
            self.assertNotIn("legacy-row", {e.id for e in effective_corpus(_load_corpus()).entries})

    @covers("REQ-0.35.0-02-01")
    def test_punctuation_and_digits_do_not_answer_who_attested(self) -> None:
        """The audit record asks WHO — `.`, `7`, or a lone combining mark do not answer.

        The predicate was "at least one visible character", and an independent review
        retired invariant canon with each of these, recording the value as the human who
        authorized it (2026-08-25). A lone surrogate got through too, which cannot even
        round-trip through the ledger's UTF-8.

        The bar is now at least one Unicode LETTER after NFKC normalization. That is a
        plausibility floor, not identity verification — gz has no operator registry to
        check a name against — but it rejects the values that are certainly not names.
        """
        rejected = {
            "period": ".",
            "digit": "7",
            "lone-combining-mark": "\u0301",
            "zero-width-space": "\u200b",
            "punctuation-run": "--",
        }
        with self._runner.isolated_filesystem():
            _seed_surface()
            for label, value in rejected.items():
                with self.subTest(attestor=label):
                    entry_id = self._remember(f"floor doctrine {label}", tier="invariant")
                    before = _corpus_fingerprint()
                    result = self._retire(
                        entry_id, args=["--reason", "superseded", "--attestor", value]
                    )
                    self.assertNotEqual(result.exit_code, 0, msg=f"{label!r} passed as an attestor")
                    self.assertEqual(_corpus_fingerprint(), before)

    @covers("REQ-0.35.0-02-07")
    def test_reviving_an_invariant_reports_the_floor_growing_not_shrinking(self) -> None:
        """Retiring a tombstone GROWS the floor; saying it shrank is a false guarantee.

        "Retirement only ever shrinks the floor" was the standing assumption, printed on
        every success and repeated in the manpage, and `floor_risk=False` suppressed the
        coherence warning on that basis. It is false for a tombstone: retiring one
        REVIVES its target, adding a requirement back. An independent review measured the
        effective invariant set going from empty to {X} while the command reported a
        shrink (2026-08-25) — so an operator could skip a required recompose and meet a
        hard gate later with no warning.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            floor_id = self._remember("floor doctrine", tier="invariant")

            shrink = self._retire(floor_id, args=["--reason", "superseded", "--attestor", "g0"])
            self.assertEqual(shrink.exit_code, 0, msg=shrink.output)
            self.assertIn("shrank", shrink.output, "a genuine removal still reports a shrink")
            tombstone = _load_corpus().entries[-1].id

            grow = self._retire(tombstone, args=["--reason", "undo", "--attestor", "g0"])
            self.assertEqual(grow.exit_code, 0, msg=grow.output)
            self.assertIn(
                floor_id,
                {e.id for e in effective_corpus(_load_corpus()).entries},
                "premise: the invariant is live again",
            )
            self.assertIn("GREW", grow.output, f"revival must report growth: {grow.output}")
            self.assertNotIn(
                "still\nSATISFIES",
                grow.output.replace(" ", "\n"),
                "must not claim committed renditions still satisfy a GROWN floor",
            )

    @covers("REQ-0.35.0-02-05")
    def test_the_printed_retry_actually_recovers_not_merely_parses(self) -> None:
        """The "governed next step" must RECOVER, not just survive argparse.

        `_assert_recovery_commands_run` proves a command parses. That is necessary and
        not sufficient: an independent review found a retry that parsed and then exited
        1, because the reason-refusal path printed only `--reason` while the target was
        invariant-tier and also needed `--attestor` (2026-08-25). A recovery step that
        fails when you run it is not a recovery step.

        This takes the refusal's own printed command, fills its placeholders with real
        values, runs it, and requires exit 0 — the effect the prose promises.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("floor doctrine", tier="invariant")
            refusal = self._retire(entry_id, args=["--reason", "superseded"])
            self.assertNotEqual(refusal.exit_code, 0, msg=refusal.output)

            commands = self._recovery_commands(refusal.output)
            self.assertTrue(commands, msg=f"no retry printed: {refusal.output}")
            retry = commands[-1]
            argv = shlex.split(retry)[1:]
            filled = [
                "g0" if a == "<your name>" else "superseded" if a == "<why>" else a for a in argv
            ]
            self.assertNotIn("<", "".join(filled), f"unfilled placeholder in {retry}")

            outcome = self._runner.invoke(main, filled)
            self.assertEqual(
                outcome.exit_code,
                0,
                msg=f"the printed retry did not recover: {retry}\n{outcome.output}",
            )
            self.assertIn(entry_id, _load_corpus().retired_ids())

    @covers("REQ-0.35.0-02-05")
    def test_invariant_refusal_cites_a_section_that_resolves(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("floor text", tier="invariant")
            result = self._retire(entry_id, args=["--reason", "why"])
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self._assert_citations_resolve(result.output)
            # Apply the runnable-command check HERE too. It existed already, but was
            # only wired to the REQ-05 paths -- so the two retries that shipped broken
            # were on paths the helper never ran against. A guard is worth what it is
            # APPLIED to, not what it could catch (Codex tier-1 refutation, 2026-08-25).
            self._assert_recovery_commands_run(result.output)

    @covers("REQ-0.35.0-02-05")
    def test_unknown_entry_recovery_command_actually_runs(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_surface()
            self._remember("some text", tier="compressible")
            result = self._retire("does-not-exist", args=["--reason", "why"])
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self._assert_recovery_commands_run(result.output)

    @covers("REQ-0.35.0-02-01")
    def test_invariant_tier_retirement_without_attestor_fails_closed(self) -> None:
        """The 0-Kelvin floor cannot be un-bound with no name attached to the decision."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("doctrine, verbatim: 'x'", tier="invariant")
            before = _corpus_fingerprint()

            result = self._retire(entry_id, args=["--reason", "superseded"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_corpus_fingerprint(), before)
            retired = [e for e in _ledger_events() if e.get("event") == "corpus_entry_retired"]
            self.assertEqual(retired, [])

    @covers("REQ-0.35.0-02-02")
    def test_whitespace_only_attestor_fails_closed(self) -> None:
        """Whitespace is not attestation, even when non-empty."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("doctrine, verbatim: 'x'", tier="invariant")
            before = _corpus_fingerprint()

            result = self._retire(entry_id, args=["--reason", "superseded", "--attestor", "   "])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_corpus_fingerprint(), before)
            self._assert_recovery_commands_run(result.output)

    @covers("REQ-0.35.0-02-02")
    def test_whitespace_only_reason_fails_closed(self) -> None:
        """The symmetric case: a whitespace-only --reason writes nothing."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("some doctrine", tier="compressible")
            before = _corpus_fingerprint()

            result = self._retire(entry_id, args=["--reason", "   "])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_corpus_fingerprint(), before)
            self._assert_recovery_commands_run(result.output)

    @covers("REQ-0.35.0-02-03")
    def test_compressible_tier_retirement_without_attestor_succeeds(self) -> None:
        """Routine retirement stays frictionless: the attestation guards the floor, not this.

        NO `--attestor` is the REQ's subject. `--reason` IS supplied, because it is
        required on every tier (operator ruling 2026-08-25) -- it becomes the retraction
        row's text and the ledger event's reason, and both reject an empty one. REQ-03's
        literal "NO --attestor/--reason" was drafting drift; its stated rationale names
        the corpus attestation, which is the attestor.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("some doctrine", tier="compressible")
            before_count = len(_load_corpus().entries)

            result = self._retire(entry_id, args=["--reason", "superseded"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(len(_load_corpus().entries), before_count + 1)

    @covers("REQ-0.35.0-02-05")
    def test_unknown_entry_recovery_prose_carries_all_three_parts(self) -> None:
        """What failed, the cited rule, and a runnable next step — all present."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            self._remember("some doctrine", tier="compressible")
            before = _corpus_fingerprint()

            result = self._retire("corpus-nonexistent", args=["--reason", "x"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_corpus_fingerprint(), before)
            self.assertIn("corpus-nonexistent", result.output)  # what failed
            self.assertIn("GHI #635", result.output)  # cited rule
            # The governed next step must RUN, not merely appear. A substring match
            # here passed for `gz content list AGENTS.md`, which argparse rejects.
            self._assert_recovery_commands_run(result.output)

    @covers("REQ-0.35.0-02-05")
    def test_already_retired_recovery_prose_carries_all_three_parts(self) -> None:
        """Re-retirement refuses with the same three-part bar."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            entry_id = self._remember("some doctrine", tier="compressible")
            self._retire(entry_id, args=["--reason", "first"])
            before = _corpus_fingerprint()

            result = self._retire(entry_id, args=["--reason", "second"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_corpus_fingerprint(), before)
            self.assertIn(entry_id, result.output)  # what failed
            self.assertIn("GHI #635", result.output)  # cited rule
            # The governed next step must RUN, not merely appear. A substring match
            # here passed for `gz content list AGENTS.md`, which argparse rejects.
            self._assert_recovery_commands_run(result.output)

    @covers("REQ-0.35.0-02-05")
    def test_absent_corpus_store_recovery_prose_carries_all_three_parts(self) -> None:
        """No corpus store on disk at all is refused with the same three-part bar."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            self.assertFalse(_corpus_store_exists())

            result = self._retire("corpus-anything", args=["--reason", "x"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertFalse(_corpus_store_exists())
            self.assertIn("corpus-anything", result.output)  # what failed
            self.assertIn("GHI #635", result.output)  # cited rule
            # The governed next step must RUN, not merely appear. A substring match
            # here passed for `gz content list AGENTS.md`, which argparse rejects.
            self._assert_recovery_commands_run(result.output)

    @covers("REQ-0.35.0-02-06")
    def test_help_exposes_entry_selector_and_no_text_valued_selector(self) -> None:
        """Text-keyed retirement is UNREACHABLE from the CLI, not merely discouraged.

        ``--attestor`` is asserted alongside ``--entry`` so this test is sensitive
        to the corpus-attestation option this task registers, not merely to a
        selector this CLI already lacked before the task began.
        """
        output = self._runner.invoke(main, ["content", "retire", "--help"]).output
        self.assertIn("--entry", output)
        self.assertIn("--attestor", output)
        self.assertNotIn("--text", output)

    @covers("REQ-0.35.0-02-04")
    def test_invariant_retirement_grows_raw_log_but_hides_from_effective_corpus(self) -> None:
        """Append-only: the raw log grows by one row; the retired row stays verbatim.

        `effective_corpus()` is the current-canon projection (Algebra 8) -- the
        surface an auditor or renderer actually reads -- and the retired entry must
        be absent from it while its original row survives, byte-for-byte, in the raw
        append log. Growth alone (already pinned by
        `test_retirement_preserves_the_retired_row`) does not prove the PROJECTION
        excludes the target; this REQ is specifically about that second surface.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            old = self._remember("floor text, verbatim", tier="invariant")
            raw_before = _load_corpus()
            before_count = len(raw_before.entries)
            line_before = next(
                line
                for line in _CORPUS_PATH.read_text(encoding="utf-8").splitlines()
                if f'"{old}"' in line
            )

            result = self._retire(old, args=["--attestor", "g0", "--reason", "superseded"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            raw_after = _load_corpus()
            self.assertEqual(len(raw_after.entries), before_count + 1)

            effective_ids = {e.id for e in effective_corpus(raw_after).entries}
            self.assertNotIn(old, effective_ids)

            # "Verbatim" asserted as BYTE identity of the retired row's own line, not
            # as a couple of hand-picked fields. The tier-1 adversary showed that
            # `text` + `tier` equality is too weak to carry the word: `append_entry`
            # re-serializes the ENTIRE store through current `dumps()`, so a row is
            # rewritten on every retirement and a field the assertion did not name
            # could change unseen (`RAW_ROW_EQUAL=False` on a legacy-format row,
            # 2026-08-25).
            #
            # For rows this codebase wrote, the round-trip is byte-stable and that is
            # what REQ-04 promises. The residual is legacy-FORMAT rows (different key
            # order, explicit nulls), which normalize on the next append -- a property
            # of `corpus_store.append_entry`, a Denied Path here, tracked separately.
            line_after = next(
                line
                for line in _CORPUS_PATH.read_text(encoding="utf-8").splitlines()
                if f'"{old}"' in line
            )
            self.assertEqual(line_before, line_after, "the retired row's bytes changed")

    @covers("REQ-0.35.0-02-07")
    def test_retirement_emits_appended_then_retired_with_tier_and_attestor(self) -> None:
        """A successful retirement is witnessed by BOTH events, in append-before-retire order.

        The tombstone row is itself an append (Algebra 4), so a ledger replay that
        never sees `corpus_entry_appended` before `corpus_entry_retired` would witness
        a retirement of a row that -- as far as the replay knows -- does not exist yet.
        `corpus_entry_retired` must carry the RETIRED entry's tier (answers "was this
        the 0-Kelvin floor?") and the attestor who authorized un-binding it.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            old = self._remember("floor text", tier="invariant")
            events_before = len(_ledger_events())

            result = self._retire(old, args=["--attestor", "g0", "--reason", "superseded"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            new_events = _ledger_events()[events_before:]
            appended = [e for e in new_events if e["event"] == "corpus_entry_appended"]
            retired = [e for e in new_events if e["event"] == "corpus_entry_retired"]
            self.assertEqual(len(appended), 1, msg=f"events: {new_events}")
            self.assertEqual(len(retired), 1, msg=f"events: {new_events}")

            # Appended (the tombstone's own birth) must precede retired in the log.
            self.assertLess(new_events.index(appended[0]), new_events.index(retired[0]))

            retraction_id = appended[0]["entry_id"]
            self.assertEqual(appended[0]["surface"], "AGENTS.md")
            self.assertEqual(retired[0]["surface"], "AGENTS.md")
            self.assertEqual(retired[0]["retired_entry_id"], old)
            self.assertEqual(retired[0]["retraction_entry_id"], retraction_id)
            self.assertEqual(retired[0]["tier"], "invariant")
            self.assertEqual(retired[0]["attestor"], "g0")
            self.assertEqual(retired[0]["reason"], "superseded")

    @covers("REQ-0.35.0-02-07")
    def test_dual_events_survive_the_real_validator_both_tiers(self) -> None:
        """The coupled-surface fence: schema, model, and factory must agree.

        Runs the REAL validator over the REAL ledger a retirement produces, for BOTH
        an invariant-tier retirement (attestor present) and a compressible one
        (attestor legitimately empty) -- without this, the three homes (model,
        schema, factory) can drift apart silently and nothing but a runtime
        ValidationError would ever catch it.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            invariant_id = self._remember("floor text", tier="invariant")
            compressible_id = self._remember("routine text", tier="compressible")

            first = self._retire(invariant_id, args=["--attestor", "g0", "--reason", "superseded"])
            self.assertEqual(first.exit_code, 0, msg=first.output)
            second = self._retire(compressible_id, args=["--reason", "superseded"])
            self.assertEqual(second.exit_code, 0, msg=second.output)

            # ASSERT THE EVENTS EXIST BEFORE VALIDATING THEM. A validator finds no
            # errors in an empty ledger, so "validator returned []" alone is green
            # under a no-op ledger writer -- the tier-1 adversary demonstrated exactly
            # that (`CORPUS_EVENTS=[remember only]`, `VALIDATOR_ERRORS=[]`, 2026-08-25).
            # A fence that passes when the thing it fences never happened is not a fence.
            events = _ledger_events()
            retired = [e for e in events if e["event"] == "corpus_entry_retired"]
            appended = [e for e in events if e["event"] == "corpus_entry_appended"]
            self.assertEqual(len(retired), 2, msg=f"expected 2 retirements, got {retired}")
            # 2 remember appends + 2 tombstone appends
            self.assertEqual(len(appended), 4, msg=f"expected 4 appends, got {appended}")
            self.assertEqual(
                [(e["tier"], e["attestor"]) for e in retired],
                [("invariant", "g0"), ("compressible", "")],
                msg="each retirement must carry its own tier and attestor",
            )

            ledger_path = Path(".gzkit") / "ledger.jsonl"
            errors = validate_ledger(ledger_path)
            self.assertEqual(errors, [], msg=f"validator rejected the ledger: {errors}")


if __name__ == "__main__":
    unittest.main()
