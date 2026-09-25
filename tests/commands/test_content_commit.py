"""gz content commit command tests — OBPI-0.0.37-22 (REQ-0.0.37-22-07 BEHAVIOR).

REQ-derived: the governed candidate→committed promotion seam. ``gz content commit``
promotes the staged candidate to the durable committed rendition AND freezes the
corpus content-fingerprint in a provenance sidecar, under operator attestation
(corpus attestation: ``--attestor`` / ``--attestation-text`` fail-closed on empty --
 NOT Gate 5, which names OBPI/ADR completion only; GHI #822). It is the
missing REQ-22-01 substance — ``save_rendition`` previously had no governed caller.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.content.corpus_store import append_entry, load_corpus
from gzkit.content.models import CorpusEntry
from gzkit.content.rendition import candidate_path
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    fingerprint_path,
    load_fingerprint,
    rendition_fingerprint,
    rendition_path,
    save_fingerprint,
    save_rendition,
)
from gzkit.content.retention import RetentionMap, retention_path
from gzkit.traceability import covers
from tests.commands.common import CliRunner

_CANDIDATE_TEXT = "# AGENTS.md\n\nYOU OWN THE WORK COMPLETELY.\n\ncompressed body\n"


def _entry(entry_id: str, *, tier: str = "compressible", text: str = "body") -> CorpusEntry:
    return CorpusEntry(
        id=entry_id,
        surface="AGENTS.md",
        section="behavior-rules",
        tier=tier,
        classification="Mechanical",
        text=text,
        origin="test",
        ts="2026-06-19T00:00:00+00:00",
    )


def _seed_corpus_and_candidate() -> None:
    """Seed a corpus and a staged candidate in the current isolated filesystem."""
    Path(".gzkit").mkdir()
    Path(".gzkit", "corpus").mkdir()
    root = Path(".")
    append_entry(root, "AGENTS.md", _entry("e1", text="YOU OWN THE WORK COMPLETELY."))
    append_entry(root, "AGENTS.md", _entry("e2", text="compressible content"))
    cand = candidate_path(root, "AGENTS.md", "codex")
    cand.parent.mkdir(parents=True, exist_ok=True)
    cand.write_text(_CANDIDATE_TEXT, encoding="utf-8")


def _commit_args(
    attestor: str = "g0",
    text: str = "attest completed",
    *,
    consumer: str = "codex",
    retention_map: str | None = None,
) -> list[str]:
    args = [
        "content",
        "commit",
        "AGENTS.md",
        "--consumer",
        consumer,
        "--attestor",
        attestor,
        "--attestation-text",
        text,
    ]
    if retention_map is not None:
        args += ["--retention-map", retention_map]
    return args


def _seed_prior_rendition(prior_text: str, *, consumer: str = "codex") -> None:
    """Seed a corpus + a PRIOR COMMITTED rendition directly (OBPI-0.35.0-14 fixture).

    A prior committed rendition is created either by a first successful `gz
    content commit`, or -- as here -- by writing `rendition_path` directly plus
    a matching fingerprint sidecar, so tests can pin an exact prior text (e.g.
    the GHI #1090 replay fixture) without depending on compose's own rendering.
    """
    Path(".gzkit").mkdir(exist_ok=True)
    Path(".gzkit", "corpus").mkdir(exist_ok=True)
    root = Path(".")
    append_entry(root, "AGENTS.md", _entry("e1", text="seed"))
    corpus = load_corpus(root, "AGENTS.md")
    fingerprint = corpus_fingerprint(corpus)
    rendition_bytes = prior_text.encode("utf-8")
    save_rendition(root, "AGENTS.md", consumer, rendition_bytes)
    save_fingerprint(
        root,
        "AGENTS.md",
        consumer,
        RenditionProvenance(
            corpus_fingerprint=fingerprint,
            corpus_entry_count=len(corpus.entries),
            rendition_fingerprint=rendition_fingerprint(rendition_bytes),
            committed_ts="2026-09-17T00:00:00+00:00",
            attestor="g0",
            attestation_text="baseline seed",
        ),
    )


def _stage_candidate(text: str, *, consumer: str = "codex") -> None:
    cand = candidate_path(Path("."), "AGENTS.md", consumer)
    cand.parent.mkdir(parents=True, exist_ok=True)
    cand.write_text(text, encoding="utf-8")


def _ledger_line_count() -> int:
    """Count non-blank lines in .gzkit/ledger.jsonl, or 0 when it does not exist."""
    ledger = Path(".gzkit/ledger.jsonl")
    if not ledger.exists():
        return 0
    return len([line for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()])


class TestContentCommitCmd(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.0.37-22-07")
    @covers("REQ-0.35.0-14-05")
    def test_commit_promotes_candidate_and_writes_fingerprint(self) -> None:
        """Success: committed rendition holds candidate bytes; sidecar holds the corpus digest.

        REQ-0.35.0-14-05 vacuous case (a): NO prior committed rendition exists
        (this is the first commit for this consumer), so the retention gate is
        vacuous and the commit succeeds with no --retention-map.
        """
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            result = self._runner.invoke(main, _commit_args())
            self.assertEqual(result.exit_code, 0, msg=result.output)

            root = Path(".")
            committed = rendition_path(root, "AGENTS.md", "codex")
            self.assertTrue(committed.exists(), "committed rendition must be written")
            self.assertEqual(committed.read_text(encoding="utf-8"), _CANDIDATE_TEXT)

            sidecar = fingerprint_path(root, "AGENTS.md", "codex")
            self.assertTrue(sidecar.exists(), "provenance sidecar must be written")
            prov = load_fingerprint(root, "AGENTS.md", "codex")
            assert prov is not None
            expected_fp = corpus_fingerprint(load_corpus(root, "AGENTS.md"))
            self.assertEqual(prov.corpus_fingerprint, expected_fp)
            self.assertEqual(prov.attestor, "g0")
            # GHI #694: commit also freezes a digest of the bytes it wrote, so a
            # later out-of-seam edit to the rendition is detectable. The digest
            # must be the digest OF the committed bytes, not merely present.
            self.assertEqual(
                prov.rendition_fingerprint,
                rendition_fingerprint(committed.read_bytes()),
                "commit must freeze a digest of the committed rendition bytes",
            )

    @covers("REQ-0.0.37-22-07")
    def test_commit_is_byte_lossless_for_crlf_candidate(self) -> None:
        """A CRLF candidate commits to LF-normalized bytes (playback stays line-ending clean)."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            cand = candidate_path(Path("."), "AGENTS.md", "codex")
            cand.write_bytes(_CANDIDATE_TEXT.replace("\n", "\r\n").encode("utf-8"))
            result = self._runner.invoke(main, _commit_args())
            self.assertEqual(result.exit_code, 0, msg=result.output)
            committed = rendition_path(Path("."), "AGENTS.md", "codex").read_bytes()
            self.assertNotIn(b"\r", committed, "committed rendition must be LF-normalized")

    @covers("REQ-0.0.37-22-07")
    def test_commit_emits_rendition_committed_event(self) -> None:
        """A successful commit emits a rendition_committed event with attestor + fingerprint."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            self._runner.invoke(main, _commit_args())
            events = [
                json.loads(line)
                for line in Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            committed = [e for e in events if e.get("event") == "rendition_committed"]
            self.assertEqual(len(committed), 1, f"expected 1 rendition_committed, got {events}")
            self.assertEqual(committed[0]["attestor"], "g0")
            self.assertIn("corpus_fingerprint", committed[0])

    @covers("REQ-0.0.37-22-07")
    def test_commit_fails_closed_on_empty_attestor(self) -> None:
        """Empty --attestor → exit 1; no rendition, no sidecar (corpus attestation fail-closed)."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            result = self._runner.invoke(main, _commit_args(attestor=""))
            self.assertNotEqual(result.exit_code, 0)
            self.assertFalse(rendition_path(Path("."), "AGENTS.md", "codex").exists())
            self.assertFalse(fingerprint_path(Path("."), "AGENTS.md", "codex").exists())

    @covers("REQ-0.0.37-22-07")
    def test_commit_fails_closed_on_empty_attestation_text(self) -> None:
        """Empty --attestation-text → exit 1, nothing written."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            result = self._runner.invoke(main, _commit_args(text=""))
            self.assertNotEqual(result.exit_code, 0)
            self.assertFalse(rendition_path(Path("."), "AGENTS.md", "codex").exists())

    @covers("REQ-0.0.37-22-07")
    def test_commit_fails_closed_on_absent_candidate(self) -> None:
        """No staged candidate → exit 1, nothing written."""
        with self._runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            Path(".gzkit", "corpus").mkdir()
            append_entry(Path("."), "AGENTS.md", _entry("e1"))
            result = self._runner.invoke(main, _commit_args())
            self.assertNotEqual(result.exit_code, 0)
            self.assertFalse(rendition_path(Path("."), "AGENTS.md", "codex").exists())


class TestCommitAttestationGranularity(unittest.TestCase):
    """`commit` gates the CORPUS DELTA, never the re-render (GHI #821).

    Operator ruling 2026-08-17, verbatim: *"a rerender of unhanged canon doesn't
    require my attestation"* (spelling preserved). The discriminator is
    ``corpus_fingerprint()`` — already computed at every commit, previously read
    for freshness but never for this. These tests assert the RULING, not the
    branch: each one names which of the four dispositions it pins, so a future
    change to how the exemption is detected cannot quietly change WHAT is exempt.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _commit_unattested(self) -> object:
        return self._runner.invoke(main, ["content", "commit", "AGENTS.md", "--consumer", "codex"])

    def test_first_commit_still_requires_attestation(self) -> None:
        """No prior sidecar → canon is unproven, not unchanged → still fail-closed.

        The absence of a sidecar is NOT evidence that canon is unchanged; it is
        absence of evidence either way. Reading it as an exemption would make the
        very first commit of every consumer the one unattested one.
        """
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            result = self._commit_unattested()
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertFalse(fingerprint_path(Path("."), "AGENTS.md", "codex").exists())

    def test_recommit_of_unchanged_canon_needs_no_attestation(self) -> None:
        """Corpus fingerprint unmoved since the committed sidecar → exempt, exit 0."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            self.assertEqual(self._runner.invoke(main, _commit_args()).exit_code, 0)

            # Re-render the SAME canon: rewrite the candidate, commit with no attestation.
            candidate_path(Path("."), "AGENTS.md", "codex").write_text(
                _CANDIDATE_TEXT + "\ntrimmed tail\n", encoding="utf-8"
            )
            result = self._commit_unattested()
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_exempt_recommit_carries_the_standing_attestation_forward(self) -> None:
        """The exempt path inherits the prior attestor rather than blanking it.

        Canon did not move, so the operator's standing attestation still describes
        this corpus. Writing an empty attestor would record that nobody attested
        a corpus somebody did attest — losing provenance to express an exemption.
        """
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            self._runner.invoke(main, _commit_args(attestor="g0", text="attest completed"))
            candidate_path(Path("."), "AGENTS.md", "codex").write_text(
                _CANDIDATE_TEXT + "\ntrimmed tail\n", encoding="utf-8"
            )
            self.assertEqual(self._commit_unattested().exit_code, 0)

            prov = load_fingerprint(Path("."), "AGENTS.md", "codex")
            assert prov is not None
            self.assertEqual(prov.attestor, "g0")
            self.assertEqual(prov.attestation_text, "attest completed")

    def test_recommit_after_canon_moved_is_fail_closed_again(self) -> None:
        """A corpus delta re-arms the gate — this is the arm that must NOT relax.

        Distinguishes the ruling from "commit never needs attestation": appending
        one entry moves the fingerprint, and the standing attestation no longer
        describes the corpus being committed.
        """
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            self.assertEqual(self._runner.invoke(main, _commit_args()).exit_code, 0)

            append_entry(Path("."), "AGENTS.md", _entry("e3", text="new canon"))
            result = self._commit_unattested()
            self.assertNotEqual(result.exit_code, 0, msg=result.output)

    def test_explicit_attestation_still_honored_on_the_exempt_path(self) -> None:
        """Exempt means "not required", never "not accepted" — a supplied attestor wins."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            self._runner.invoke(main, _commit_args(attestor="first", text="first words"))
            candidate_path(Path("."), "AGENTS.md", "codex").write_text(
                _CANDIDATE_TEXT + "\nagain\n", encoding="utf-8"
            )
            result = self._runner.invoke(main, _commit_args(attestor="second", text="second words"))
            self.assertEqual(result.exit_code, 0, msg=result.output)

            prov = load_fingerprint(Path("."), "AGENTS.md", "codex")
            assert prov is not None
            self.assertEqual(prov.attestor, "second")


class TestCommitNamesThePlaybackWriter(unittest.TestCase):
    """`commit` writes the RENDITION only; it must say so and name the next writer.

    The pipeline is corpus -> compose -> commit -> playback, and the stages have
    different writers: this seam writes `.gzkit/renditions/<surface>/<consumer>.md`
    and never the played-back surface itself. A session that stops here has a
    rendered contract still showing the PRIOR canon while the ledger records a
    committed rendition — the half-applied state `gz validate --invariant-coherence`
    exists to catch, which only bites if someone runs it.

    Observed 2026-08-20: a canon repair reached this seam and reported three
    success lines with no next step. Asserting the SEMANTIC (a governed next step
    naming the playback writer) rather than the sentence, per DO IT RIGHT #6 and
    the three-part bar in `.claude/rules/guardrail-feedback-prose.md`.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def test_success_output_names_the_playback_writer(self) -> None:
        """A successful commit names the runnable command that writes the surface."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            result = self._runner.invoke(main, _commit_args())
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(
                "gz agent sync control-surfaces",
                result.output,
                "commit must name the playback writer; without it the rendered "
                "surface silently keeps the prior canon",
            )

    def test_success_output_states_the_rendition_only_scope(self) -> None:
        """The prose says what was written and which gate stays red until playback."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            output = self._runner.invoke(main, _commit_args()).output
            self.assertIn("rendition", output, "must state that only the rendition was written")
            self.assertIn(
                "--invariant-coherence",
                output,
                "must name the gate that stays red until playback runs, so the "
                "operator can tell a finished change from a half-applied one",
            )


# The GHI #1090 replay fixture. `_PRIOR_BLOCK_1090` is `git show
# c3582975f:AGENTS.md` line 234, verbatim -- captured via:
#   git show c3582975f:AGENTS.md | sed -n '234p'
# `_CANDIDATE_BULLET_1090` is the 2026-09-17 compressed bullet that replaced
# it (the same paragraph as it stands, post-compression, in root AGENTS.md's
# § OBPI Acceptance Protocol today).
_PRIOR_BLOCK_1090 = (
    "**REQ-coverage gate (ADR-0.0.25, ADR-0.0.59).** Every **BEHAVIOR** REQ "
    "must have a covering passing test before `gz obpi complete`; it cannot "
    "be waived — `--accept-uncovered` is refused on every lane, because "
    "BEHAVIOR's only proof channel is a `@covers` test (GHI #537). SUPPORT "
    "and STRUCTURAL-FENCE REQs are exempt by proof channel and never reach "
    "the waiver path. Failing-cover REQs cannot be waived."
)
_CANDIDATE_BULLET_1090 = (
    "REQ-coverage gate: every BEHAVIOR REQ needs a passing `@covers` test "
    "before `gz obpi complete`; this cannot be waived. SUPPORT and "
    "STRUCTURAL-FENCE REQs use their declared proof channels."
)


class TestContentCommitRetentionGate(unittest.TestCase):
    """The retention gate inside `gz content commit` (OBPI-0.35.0-14, ADR-0.35.0 Decision 10).

    A removed prior block must be accounted for in a `--retention-map`, or the
    commit exits 3 and writes NOTHING — the mechanical floor under the
    operator ruling that compression may never lose meaning (GHI #1090, #1091).
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-14-01")
    def test_missing_retention_map_when_block_removed_exits_3(self) -> None:
        """A removed block with no --retention-map exits 3 and writes nothing."""
        with self._runner.isolated_filesystem():
            prior = "# AGENTS.md\n\nBlock one stays.\n\nBlock two must not vanish silently.\n"
            _seed_prior_rendition(prior)
            _stage_candidate("# AGENTS.md\n\nBlock one stays.\n")

            result = self._runner.invoke(main, _commit_args())

            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertIn("Block two must not vanish silently.", result.output)

            root = Path(".")
            self.assertEqual(
                rendition_path(root, "AGENTS.md", "codex").read_text(encoding="utf-8"),
                prior,
                "the committed rendition must be unchanged, not overwritten",
            )
            self.assertFalse(
                retention_path(root, "AGENTS.md", "codex").exists(),
                "no retention sidecar is written on refusal",
            )
            self.assertFalse(
                Path(".gzkit/ledger.jsonl").exists(),
                "no rendition_committed ledger event is written on refusal",
            )

    @covers("REQ-0.35.0-14-01")
    def test_missing_retention_map_names_every_removed_block(self) -> None:
        """TWO removed blocks with no --retention-map: exits 3, names BOTH, writes nothing."""
        with self._runner.isolated_filesystem():
            prior = (
                "# AGENTS.md\n\n"
                "Block one must not vanish silently.\n\n"
                "Block two must not vanish silently either.\n"
            )
            _seed_prior_rendition(prior)
            root = Path(".")
            prior_provenance = fingerprint_path(root, "AGENTS.md", "codex").read_text(
                encoding="utf-8"
            )
            _stage_candidate("# AGENTS.md\n\nreplacement body only.\n")

            result = self._runner.invoke(main, _commit_args())

            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertIn("Block one must not vanish silently.", result.output)
            self.assertIn("Block two must not vanish silently either.", result.output)

            self.assertEqual(
                rendition_path(root, "AGENTS.md", "codex").read_text(encoding="utf-8"),
                prior,
                "the committed rendition must be unchanged, not overwritten",
            )
            self.assertFalse(
                retention_path(root, "AGENTS.md", "codex").exists(),
                "no retention sidecar is written on refusal",
            )
            self.assertEqual(
                fingerprint_path(root, "AGENTS.md", "codex").read_text(encoding="utf-8"),
                prior_provenance,
                "the provenance sidecar must be unchanged, not overwritten",
            )
            self.assertFalse(
                Path(".gzkit/ledger.jsonl").exists(),
                "no rendition_committed ledger event is written on refusal",
            )

    @covers("REQ-0.35.0-14-04")
    def test_dropped_condition_requires_id_in_attestation(self) -> None:
        """A DROPPED condition's id absent from --attestation-text exits 3; present, exits 0."""
        with self._runner.isolated_filesystem():
            prior = "# AGENTS.md\n\nDeprecated note: old policy text.\n"
            _seed_prior_rendition(prior)
            _stage_candidate("# AGENTS.md\n\nreplacement body.\n")

            retention_map = {
                "surface": "AGENTS.md",
                "consumer": "codex",
                "extracted_by": "reviewer-agent",
                "mapped_by": "author-agent",
                "blocks": [
                    {
                        "removed": "Deprecated note: old policy text.",
                        "conditions": [
                            {
                                "id": "C1",
                                "quote": "Deprecated note: old policy text.",
                                "disposition": "dropped",
                                "reason": "superseded by replacement body",
                            }
                        ],
                        "non_binding": [],
                    }
                ],
            }
            Path("map.json").write_text(json.dumps(retention_map), encoding="utf-8")

            root = Path(".")
            prior_provenance = fingerprint_path(root, "AGENTS.md", "codex").read_text(
                encoding="utf-8"
            )
            ledger_lines_before = _ledger_line_count()

            unattested = self._runner.invoke(
                main, _commit_args(text="attest without the drop id", retention_map="map.json")
            )
            self.assertEqual(unattested.exit_code, 3, msg=unattested.output)
            # (a) the removed block's first line is named.
            self.assertIn("Deprecated note: old policy text.", unattested.output)
            # (b) the specific violation kind is named, not merely "refused".
            self.assertIn("dropped-id-not-attested", unattested.output)
            # (c) three-part recovery prose is present.
            self.assertIn("Why forbidden", unattested.output)
            self.assertIn("Next: account for every condition", unattested.output)
            # (d) nothing was written on this validator-violation path.
            self.assertFalse(retention_path(root, "AGENTS.md", "codex").exists())
            self.assertEqual(
                rendition_path(root, "AGENTS.md", "codex").read_text(encoding="utf-8"),
                prior,
                "the committed rendition must be unchanged on refusal",
            )
            self.assertEqual(
                fingerprint_path(root, "AGENTS.md", "codex").read_text(encoding="utf-8"),
                prior_provenance,
                "the provenance sidecar must be unchanged on refusal",
            )
            self.assertEqual(
                _ledger_line_count(),
                ledger_lines_before,
                "no rendition_committed ledger event is written on refusal",
            )

            attested = self._runner.invoke(
                main,
                _commit_args(text="attest completed; C1 drop accepted", retention_map="map.json"),
            )
            self.assertEqual(attested.exit_code, 0, msg=attested.output)
            sidecar = retention_path(Path("."), "AGENTS.md", "codex")
            self.assertTrue(sidecar.exists())
            self.assertEqual(
                RetentionMap.model_validate_json(sidecar.read_text(encoding="utf-8")),
                RetentionMap.model_validate(retention_map),
                "the sidecar must hold the validated map",
            )

    @covers("REQ-0.35.0-14-05")
    def test_stale_retention_sidecar_removed_when_nothing_removed(self) -> None:
        """A stale sidecar from an earlier promotion is removed when this one removes nothing."""
        with self._runner.isolated_filesystem():
            prior = "# AGENTS.md\n\nDeprecated note: old policy text.\n"
            _seed_prior_rendition(prior)
            _stage_candidate("# AGENTS.md\n\nreplacement body.\n")
            retention_map = {
                "surface": "AGENTS.md",
                "consumer": "codex",
                "extracted_by": "reviewer-agent",
                "mapped_by": "author-agent",
                "blocks": [
                    {
                        "removed": "Deprecated note: old policy text.",
                        "conditions": [
                            {
                                "id": "C1",
                                "quote": "Deprecated note: old policy text.",
                                "disposition": "dropped",
                                "reason": "superseded by replacement body",
                            }
                        ],
                        "non_binding": [],
                    }
                ],
            }
            Path("map.json").write_text(json.dumps(retention_map), encoding="utf-8")
            first = self._runner.invoke(
                main, _commit_args(text="C1 drop accepted", retention_map="map.json")
            )
            self.assertEqual(first.exit_code, 0, msg=first.output)
            sidecar = retention_path(Path("."), "AGENTS.md", "codex")
            self.assertTrue(sidecar.exists())

            # Next promotion only ADDS a block (no removal) -- succeeds with no
            # map, and the stale sidecar from the prior promotion is removed.
            _stage_candidate("# AGENTS.md\n\nreplacement body.\n\nAn added block.\n")
            second = self._runner.invoke(main, _commit_args(text="add-only recommit"))
            self.assertEqual(second.exit_code, 0, msg=second.output)
            self.assertFalse(sidecar.exists(), "a stale retention sidecar must be removed")

    def test_malformed_retention_map_exits_1_and_writes_nothing(self) -> None:
        """Bad JSON or a schema error in --retention-map exits 1 and writes nothing."""
        with self._runner.isolated_filesystem():
            prior = "# AGENTS.md\n\nDeprecated note: old policy text.\n"
            _seed_prior_rendition(prior)
            _stage_candidate("# AGENTS.md\n\nreplacement body.\n")
            Path("map.json").write_text("{not valid json", encoding="utf-8")

            result = self._runner.invoke(main, _commit_args(retention_map="map.json"))

            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertFalse(retention_path(Path("."), "AGENTS.md", "codex").exists())
            self.assertEqual(
                rendition_path(Path("."), "AGENTS.md", "codex").read_text(encoding="utf-8"),
                prior,
                "the prior committed rendition must be unchanged",
            )

    def test_non_utf8_retention_map_exits_1_and_writes_nothing(self) -> None:
        """A --retention-map file holding invalid UTF-8 bytes exits 1, not a traceback."""
        with self._runner.isolated_filesystem():
            prior = "# AGENTS.md\n\nDeprecated note: old policy text.\n"
            _seed_prior_rendition(prior)
            _stage_candidate("# AGENTS.md\n\nreplacement body.\n")
            Path("map.json").write_bytes(b"\xff\xfe{")

            result = self._runner.invoke(main, _commit_args(retention_map="map.json"))

            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("malformed", result.output)
            self.assertFalse(retention_path(Path("."), "AGENTS.md", "codex").exists())
            self.assertEqual(
                rendition_path(Path("."), "AGENTS.md", "codex").read_text(encoding="utf-8"),
                prior,
                "the prior committed rendition must be unchanged",
            )

    @covers("REQ-0.35.0-14-04")
    def test_dropped_condition_with_empty_id_exits_1_and_writes_nothing(self) -> None:
        """An empty condition id is not a human-typable token (brief Requirement 6).

        Without a constraint, ``_id_in_attestation("", text)`` matches ANY
        text, so a DROPPED condition with id "" would be "attested" by
        whatever --attestation-text happens to be supplied. The id pattern
        makes "" unconstructable, so the map fails Pydantic validation and the
        commit is refused as malformed (exit 1), never silently accepted.
        """
        with self._runner.isolated_filesystem():
            prior = "# AGENTS.md\n\nDeprecated note: old policy text.\n"
            _seed_prior_rendition(prior)
            _stage_candidate("# AGENTS.md\n\nreplacement body.\n")
            retention_map = {
                "surface": "AGENTS.md",
                "consumer": "codex",
                "extracted_by": "reviewer-agent",
                "mapped_by": "author-agent",
                "blocks": [
                    {
                        "removed": "Deprecated note: old policy text.",
                        "conditions": [
                            {
                                "id": "",
                                "quote": "Deprecated note: old policy text.",
                                "disposition": "dropped",
                                "reason": "superseded by replacement body",
                            }
                        ],
                        "non_binding": [],
                    }
                ],
            }
            Path("map.json").write_text(json.dumps(retention_map), encoding="utf-8")

            result = self._runner.invoke(
                main,
                _commit_args(
                    text="unrelated attestation text that mentions nothing in particular",
                    retention_map="map.json",
                ),
            )

            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("malformed", result.output)
            self.assertFalse(retention_path(Path("."), "AGENTS.md", "codex").exists())
            self.assertEqual(
                rendition_path(Path("."), "AGENTS.md", "codex").read_text(encoding="utf-8"),
                prior,
                "the prior committed rendition must be unchanged",
            )

    def test_unreadable_prior_rendition_exits_2(self) -> None:
        """An existing-but-unreadable prior rendition exits 2, never treated as vacuous."""
        with self._runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            Path(".gzkit", "corpus").mkdir()
            append_entry(Path("."), "AGENTS.md", _entry("e1"))
            prior_rendition = rendition_path(Path("."), "AGENTS.md", "codex")
            prior_rendition.parent.mkdir(parents=True, exist_ok=True)
            # A directory where a file is expected: `exists()` is True but
            # `read_text` raises OSError.
            prior_rendition.mkdir()
            cand = candidate_path(Path("."), "AGENTS.md", "codex")
            cand.parent.mkdir(parents=True, exist_ok=True)
            cand.write_text(_CANDIDATE_TEXT, encoding="utf-8")

            result = self._runner.invoke(main, _commit_args())

            self.assertEqual(result.exit_code, 2, msg=result.output)

    def test_success_prints_kept_and_dropped_correspondence(self) -> None:
        """A successful commit with removed blocks prints each KEPT/DROPPED correspondence."""
        with self._runner.isolated_filesystem():
            prior = "# AGENTS.md\n\nKept block text here.\n\nDropped block text here.\n"
            _seed_prior_rendition(prior)
            _stage_candidate("# AGENTS.md\n\nKept block relocated here.\n")
            retention_map = {
                "surface": "AGENTS.md",
                "consumer": "codex",
                "extracted_by": "reviewer-agent",
                "mapped_by": "author-agent",
                "blocks": [
                    {
                        "removed": "Kept block text here.",
                        "conditions": [
                            {
                                "id": "C1",
                                "quote": "Kept block text here.",
                                "disposition": "kept",
                                "span": "Kept block relocated here.",
                            }
                        ],
                        "non_binding": [],
                    },
                    {
                        "removed": "Dropped block text here.",
                        "conditions": [
                            {
                                "id": "C2",
                                "quote": "Dropped block text here.",
                                "disposition": "dropped",
                                "reason": "no longer relevant",
                            }
                        ],
                        "non_binding": [],
                    },
                ],
            }
            Path("map.json").write_text(json.dumps(retention_map), encoding="utf-8")

            result = self._runner.invoke(
                main, _commit_args(text="C2 drop accepted", retention_map="map.json")
            )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(
                'C1: "Kept block text here." -> "Kept block relocated here."', result.output
            )
            self.assertIn("C2: DROPPED -- no longer relevant", result.output)

    def test_success_prints_non_binding_exemptions_with_their_reason(self) -> None:
        """A non_binding declaration that exempts a removed block is never invisible.

        Requirement 9: a KEPT/DROPPED condition is not the only way a removed
        block's meaning can be accounted for -- a ``non_binding`` declaration
        can exempt a whole block from coverage with only a reason attached.
        Change Log 2026-09-25: that exemption was never printed alongside the
        KEPT/DROPPED correspondence, so the loss it excuses stayed invisible
        to the operator. Every non_binding entry must appear in the success
        report, each with its quote and reason.
        """
        with self._runner.isolated_filesystem():
            prior = "# AGENTS.md\n\nKept block text here.\n\nSide note that binds nothing.\n"
            _seed_prior_rendition(prior)
            _stage_candidate("# AGENTS.md\n\nKept block relocated here.\n")
            retention_map = {
                "surface": "AGENTS.md",
                "consumer": "codex",
                "extracted_by": "reviewer-agent",
                "mapped_by": "author-agent",
                "blocks": [
                    {
                        "removed": "Kept block text here.",
                        "conditions": [
                            {
                                "id": "C1",
                                "quote": "Kept block text here.",
                                "disposition": "kept",
                                "span": "Kept block relocated here.",
                            }
                        ],
                        "non_binding": [],
                    },
                    {
                        "removed": "Side note that binds nothing.",
                        "conditions": [],
                        "non_binding": [
                            {
                                "quote": "Side note that binds nothing.",
                                "reason": "editorial aside, not a governed condition",
                            }
                        ],
                    },
                ],
            }
            Path("map.json").write_text(json.dumps(retention_map), encoding="utf-8")

            result = self._runner.invoke(
                main, _commit_args(text="no drops this commit", retention_map="map.json")
            )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(
                'C1: "Kept block text here." -> "Kept block relocated here."', result.output
            )
            self.assertIn(
                'NB: "Side note that binds nothing." -- NON-BINDING: '
                "editorial aside, not a governed condition",
                result.output,
            )

    @covers("REQ-0.35.0-14-04")
    def test_dropped_id_check_uses_this_invocations_attestation_not_standing(self) -> None:
        """A DROPPED id must appear in THIS invocation's attestation text.

        ADR-0.35.0 Decision 10: the operator rules on every drop in the words
        supplied WITH THIS COMMIT. A standing attestation carried forward from an
        earlier, unrelated commit (exempt because the CORPUS is unchanged, per
        GHI #821) must never satisfy the retention gate's id-attested check --
        only the raw ``attestation_text`` this invocation supplied may.
        """
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            baseline = self._runner.invoke(
                main,
                _commit_args(attestor="g0", text="baseline; mentions C1 for unrelated reasons"),
            )
            self.assertEqual(baseline.exit_code, 0, msg=baseline.output)

            # Corpus UNCHANGED -> the corpus attestation is exempt and the
            # standing text above carries forward for IT. The candidate removes
            # a block, and the retention gate's DROPPED-id check must NOT be
            # satisfied by that carried-forward text.
            _stage_candidate("# AGENTS.md\n\nreplacement body only.\n\ncompressed body\n")
            retention_map = {
                "surface": "AGENTS.md",
                "consumer": "codex",
                "extracted_by": "reviewer-agent",
                "mapped_by": "author-agent",
                "blocks": [
                    {
                        "removed": "YOU OWN THE WORK COMPLETELY.",
                        "conditions": [
                            {
                                "id": "C1",
                                "quote": "YOU OWN THE WORK COMPLETELY.",
                                "disposition": "dropped",
                                "reason": "test fixture",
                            }
                        ],
                        "non_binding": [],
                    }
                ],
            }
            Path("map.json").write_text(json.dumps(retention_map), encoding="utf-8")

            root = Path(".")
            prior_provenance = fingerprint_path(root, "AGENTS.md", "codex").read_text(
                encoding="utf-8"
            )
            ledger_lines_before = _ledger_line_count()

            result = self._runner.invoke(
                main,
                [
                    "content",
                    "commit",
                    "AGENTS.md",
                    "--consumer",
                    "codex",
                    "--retention-map",
                    "map.json",
                ],
            )

            self.assertEqual(result.exit_code, 3, msg=result.output)
            # (a) the removed block's first line is named.
            self.assertIn("YOU OWN THE WORK COMPLETELY.", result.output)
            # (b) the specific violation kind is named, not merely "refused".
            self.assertIn("dropped-id-not-attested", result.output)
            # (c) three-part recovery prose is present.
            self.assertIn("Why forbidden", result.output)
            self.assertIn("Next: account for every condition", result.output)
            # (d) nothing was written on this validator-violation path.
            self.assertFalse(retention_path(root, "AGENTS.md", "codex").exists())
            self.assertEqual(
                rendition_path(root, "AGENTS.md", "codex").read_text(encoding="utf-8"),
                _CANDIDATE_TEXT,
                "the committed rendition must be unchanged on refusal",
            )
            self.assertEqual(
                fingerprint_path(root, "AGENTS.md", "codex").read_text(encoding="utf-8"),
                prior_provenance,
                "the provenance sidecar must be unchanged on refusal",
            )
            self.assertEqual(
                _ledger_line_count(),
                ledger_lines_before,
                "no rendition_committed ledger event is written on refusal",
            )

    @covers("REQ-0.35.0-14-02")
    def test_multiple_violations_all_named_in_one_refusal(self) -> None:
        """Three distinct violation kinds in one map: exit 3, EACH is named, nothing written.

        REQ-0.35.0-14-02: the validator returns every violation, not only the
        first, so one refusal names every gap. Proven here at the CLI (not
        only against the pure validator) so a regression that swallows all
        but the first violation on the way to `result.output` is caught.
        """
        with self._runner.isolated_filesystem():
            prior = (
                "# AGENTS.md\n\n"
                "Sentence Alpha must persist here. Sentence Beta must persist "
                "elsewhere. Sentence Gamma must persist too.\n"
            )
            _seed_prior_rendition(prior)
            _stage_candidate("# AGENTS.md\n\nreplacement body only.\n")

            removed_block = (
                "Sentence Alpha must persist here. Sentence Beta must persist "
                "elsewhere. Sentence Gamma must persist too."
            )
            retention_map = {
                "surface": "AGENTS.md",
                "consumer": "codex",
                "extracted_by": "reviewer-agent",
                "mapped_by": "author-agent",
                "blocks": [
                    {
                        "removed": removed_block,
                        "conditions": [
                            {
                                # quote-not-in-block: not a substring of removed_block.
                                "id": "C1",
                                "quote": "ZZZZ not present anywhere in this block",
                                "disposition": "dropped",
                                "reason": "quote check fixture",
                            },
                            {
                                # kept-span-not-in-candidate: span absent from candidate.
                                "id": "C2",
                                "quote": "Sentence Beta must persist elsewhere.",
                                "disposition": "kept",
                                "span": "this span text is nowhere in the candidate",
                            },
                            {
                                # dropped-without-reason: empty reason.
                                "id": "C3",
                                "quote": "Sentence Gamma must persist too.",
                                "disposition": "dropped",
                                "reason": "",
                            },
                        ],
                        "non_binding": [],
                    }
                ],
            }
            Path("map.json").write_text(json.dumps(retention_map), encoding="utf-8")

            root = Path(".")
            prior_provenance = fingerprint_path(root, "AGENTS.md", "codex").read_text(
                encoding="utf-8"
            )
            ledger_lines_before = _ledger_line_count()

            result = self._runner.invoke(
                main, _commit_args(text="attest test run", retention_map="map.json")
            )

            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertIn("quote-not-in-block", result.output)
            self.assertIn("kept-span-not-in-candidate", result.output)
            self.assertIn("dropped-without-reason", result.output)
            self.assertIn(removed_block, result.output)
            self.assertIn("Why forbidden", result.output)
            self.assertIn("Next: account for every condition", result.output)

            self.assertFalse(
                retention_path(root, "AGENTS.md", "codex").exists(),
                "no retention sidecar is written on refusal",
            )
            self.assertEqual(
                rendition_path(root, "AGENTS.md", "codex").read_text(encoding="utf-8"),
                prior,
                "the committed rendition must be unchanged on refusal",
            )
            self.assertEqual(
                fingerprint_path(root, "AGENTS.md", "codex").read_text(encoding="utf-8"),
                prior_provenance,
                "the provenance sidecar must be unchanged on refusal",
            )
            self.assertEqual(
                _ledger_line_count(),
                ledger_lines_before,
                "no rendition_committed ledger event is written on refusal",
            )

    @covers("REQ-0.35.0-14-03")
    def test_independence_violations_named_at_cli(self) -> None:
        """extracted_by == mapped_by (case/whitespace-folded), or empty: exit 3, nothing written.

        REQ-0.35.0-14-03: proven at the CLI, not only against the pure
        validator, so a regression that drops the independence check between
        the validator and `result.output` is caught.
        """
        prior = "# AGENTS.md\n\nDeprecated note about legacy policy text.\n"

        def _map(extracted_by: str, mapped_by: str) -> dict:
            return {
                "surface": "AGENTS.md",
                "consumer": "codex",
                "extracted_by": extracted_by,
                "mapped_by": mapped_by,
                "blocks": [
                    {
                        "removed": "Deprecated note about legacy policy text.",
                        "conditions": [
                            {
                                "id": "C1",
                                "quote": "Deprecated note about legacy policy text.",
                                "disposition": "dropped",
                                "reason": "superseded by replacement body",
                            }
                        ],
                        "non_binding": [],
                    }
                ],
            }

        cases = [
            ("non-independent-mapping", " Reviewer-A ", "reviewer-a"),
            ("empty-extracted-by", "", "author-agent"),
        ]
        for expected_kind, extracted_by, mapped_by in cases:
            with self.subTest(expected_kind=expected_kind), self._runner.isolated_filesystem():
                _seed_prior_rendition(prior)
                _stage_candidate("# AGENTS.md\n\nreplacement body.\n")
                retention_map = _map(extracted_by, mapped_by)
                Path("map.json").write_text(json.dumps(retention_map), encoding="utf-8")

                root = Path(".")
                prior_provenance = fingerprint_path(root, "AGENTS.md", "codex").read_text(
                    encoding="utf-8"
                )
                ledger_lines_before = _ledger_line_count()

                result = self._runner.invoke(
                    main,
                    _commit_args(text="C1 drop accepted", retention_map="map.json"),
                )

                self.assertEqual(result.exit_code, 3, msg=result.output)
                self.assertIn(expected_kind, result.output)

                self.assertFalse(
                    retention_path(root, "AGENTS.md", "codex").exists(),
                    "no retention sidecar is written on refusal",
                )
                self.assertEqual(
                    rendition_path(root, "AGENTS.md", "codex").read_text(encoding="utf-8"),
                    prior,
                    "the committed rendition must be unchanged on refusal",
                )
                self.assertEqual(
                    fingerprint_path(root, "AGENTS.md", "codex").read_text(encoding="utf-8"),
                    prior_provenance,
                    "the provenance sidecar must be unchanged on refusal",
                )
                self.assertEqual(
                    _ledger_line_count(),
                    ledger_lines_before,
                    "no rendition_committed ledger event is written on refusal",
                )

    @covers("REQ-0.35.0-14-04")
    def test_all_kept_map_may_still_land_on_standing_attestation(self) -> None:
        """An all-KEPT map has no DROPPED id to attest, so it may land on the standing text."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            baseline = self._runner.invoke(main, _commit_args(attestor="g0", text="baseline"))
            self.assertEqual(baseline.exit_code, 0, msg=baseline.output)

            _stage_candidate(
                "# AGENTS.md\n\nOWN THE WORK COMPLETELY, relocated.\n\ncompressed body\n"
            )
            retention_map = {
                "surface": "AGENTS.md",
                "consumer": "codex",
                "extracted_by": "reviewer-agent",
                "mapped_by": "author-agent",
                "blocks": [
                    {
                        "removed": "YOU OWN THE WORK COMPLETELY.",
                        "conditions": [
                            {
                                "id": "C1",
                                "quote": "YOU OWN THE WORK COMPLETELY.",
                                "disposition": "kept",
                                "span": "OWN THE WORK COMPLETELY, relocated.",
                            }
                        ],
                        "non_binding": [],
                    }
                ],
            }
            Path("map.json").write_text(json.dumps(retention_map), encoding="utf-8")

            result = self._runner.invoke(
                main,
                [
                    "content",
                    "commit",
                    "AGENTS.md",
                    "--consumer",
                    "codex",
                    "--retention-map",
                    "map.json",
                ],
            )

            self.assertEqual(result.exit_code, 0, msg=result.output)


class TestContentCommitRetentionGateVacuousCases(unittest.TestCase):
    """REQ-0.35.0-14-05: when a promotion removes no prior block, the gate is
    vacuous -- exit 0, no --retention-map required. Case (a), first commit
    (no prior committed rendition), is exercised by
    ``TestContentCommitCmd.test_commit_promotes_candidate_and_writes_fingerprint``
    (bound to this REQ too, rather than duplicated here). Cases (b)-(d) below
    each seed a REAL prior committed rendition, so `removed_blocks` runs for
    real and must return empty.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-14-05")
    def test_byte_identical_rerender_succeeds_with_no_map(self) -> None:
        """Case (b): a byte-identical re-render removes nothing."""
        with self._runner.isolated_filesystem():
            prior = "# AGENTS.md\n\nBlock text stays exactly as it was.\n"
            _seed_prior_rendition(prior)
            _stage_candidate(prior)

            result = self._runner.invoke(main, _commit_args())

            self.assertEqual(result.exit_code, 0, msg=result.output)

    @covers("REQ-0.35.0-14-05")
    def test_reorder_only_candidate_succeeds_with_no_map(self) -> None:
        """Case (c): a candidate that only REORDERS the prior blocks removes nothing."""
        with self._runner.isolated_filesystem():
            prior = "# AGENTS.md\n\nBlock A text.\n\nBlock B text.\n"
            _seed_prior_rendition(prior)
            _stage_candidate("# AGENTS.md\n\nBlock B text.\n\nBlock A text.\n")

            result = self._runner.invoke(main, _commit_args())

            self.assertEqual(result.exit_code, 0, msg=result.output)

    @covers("REQ-0.35.0-14-05")
    def test_crlf_and_trailing_whitespace_only_candidate_succeeds_with_no_map(self) -> None:
        """Case (d): a candidate differing only by CRLF endings + trailing whitespace."""
        with self._runner.isolated_filesystem():
            prior = "# AGENTS.md\n\nBlock text with content.\n"
            _seed_prior_rendition(prior)
            _stage_candidate("# AGENTS.md  \r\n\r\nBlock text with content.   \r\n")

            result = self._runner.invoke(main, _commit_args())

            self.assertEqual(result.exit_code, 0, msg=result.output)


class TestContentCommitRetentionGateGHI1090Replay(unittest.TestCase):
    """The GHI #1090 replay through the CLI (REQ-0.35.0-14-06).

    `--accept-uncovered` is refused on every lane" has no KEPT span in the
    compressed candidate: a map marking it KEPT fails the span check.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _seed_and_stage(self) -> None:
        prior = "# AGENTS.md\n\n" + _PRIOR_BLOCK_1090 + "\n"
        _seed_prior_rendition(prior)
        _stage_candidate("# AGENTS.md\n\n" + _CANDIDATE_BULLET_1090 + "\n")

    @staticmethod
    def _all_kept_map() -> dict:
        return {
            "surface": "AGENTS.md",
            "consumer": "codex",
            "extracted_by": "reviewer-agent",
            "mapped_by": "author-agent",
            "blocks": [
                {
                    "removed": _PRIOR_BLOCK_1090,
                    "conditions": [
                        {
                            "id": "C1",
                            "quote": "`--accept-uncovered` is refused on every lane",
                            "disposition": "kept",
                            "span": "`--accept-uncovered` is refused on every lane",
                        }
                    ],
                    # Covers the rest of the block's sentences so the ONLY
                    # violation under test is C1's KEPT span.
                    "non_binding": [
                        {
                            "quote": _PRIOR_BLOCK_1090,
                            "reason": ("fixture stub -- only C1's disposition is under test here"),
                        }
                    ],
                }
            ],
        }

    @covers("REQ-0.35.0-14-06")
    def test_all_kept_map_refused_on_accept_uncovered_condition(self) -> None:
        """A map marking the accept-uncovered condition KEPT is refused: no such span exists."""
        with self._runner.isolated_filesystem():
            self._seed_and_stage()
            retention_map = self._all_kept_map()
            Path("map.json").write_text(json.dumps(retention_map), encoding="utf-8")

            result = self._runner.invoke(
                main, _commit_args(text="all kept", retention_map="map.json")
            )

            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertIn("kept-span-not-in-candidate", result.output)
            self.assertIn("Condition C1", result.output)

    @covers("REQ-0.35.0-14-06")
    def test_dropped_accept_uncovered_condition_with_attested_id_succeeds(self) -> None:
        """The same map with the condition DROPPED and its id attested succeeds."""
        with self._runner.isolated_filesystem():
            self._seed_and_stage()
            retention_map = self._all_kept_map()
            retention_map["blocks"][0]["conditions"][0] = {
                "id": "C1",
                "quote": "`--accept-uncovered` is refused on every lane",
                "disposition": "dropped",
                "reason": "2026-09-17 compression dropped this condition; disclosed here",
            }
            Path("map.json").write_text(json.dumps(retention_map), encoding="utf-8")

            result = self._runner.invoke(
                main,
                _commit_args(
                    text="C1 drop accepted for the accept-uncovered clause",
                    retention_map="map.json",
                ),
            )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertTrue(retention_path(Path("."), "AGENTS.md", "codex").exists())


if __name__ == "__main__":
    unittest.main()
