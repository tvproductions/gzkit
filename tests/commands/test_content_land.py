"""gz content land command tests -- OBPI-0.35.0-07 (preflight half).

REQ-derived: ``gz content land <surface>`` is the governed multi-consumer
promotion seam (ADR-0.35.0 Decision 6). These tests pin the preflight
contract: the positional surface is required (REQ-01), a new corpus delta
without attestation refuses and writes nothing (REQ-03), a removed block
without a valid retention map refuses the WHOLE landing and writes nothing
(REQ-10), and ``--dry-run`` writes nothing.

This module deliberately imports nothing from ``gzkit.content.landing``: the
fixture below is shared with ``tests/content/test_landing.py`` and builds the
isolated project only from surfaces that predate the landing module.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import unittest
from pathlib import Path
from unittest import mock

from gzkit.cli.main import main
from gzkit.config import AuthorshipConfig, GzkitConfig
from gzkit.content.corpus_store import append_entry, load_corpus
from gzkit.content.models import CorpusEntry
from gzkit.content.ownership import declaration_path, measure_section_spans, sections_digest
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    fingerprint_path,
    rendition_fingerprint,
    rendition_path,
)
from gzkit.content.retention import Condition, RemovedBlock, RetentionMap
from gzkit.governance.events import emit_section_ownership_genesis
from gzkit.traceability import covers
from tests.commands.common import CliRunner

LAND_SURFACE = "LandSurface.md"
LAND_OWNER = "LandType"
LAND_CONSUMERS = ("alpha", "beta", "gamma")

# The prior committed rendition, already in the exact byte form the generator
# emits for a corpus holding only `e-seed` (heading, blank line, body): a new
# entry therefore only ADDS a block and the retention gate stays vacuous.
LAND_PRIOR_TEXT = (
    "## Owned Section\n\nseed rule text.\n## Unowned Section\ncarried forward text verbatim\n"
)
# A prior carrying a block the corpus does not: regeneration REMOVES it.
LAND_PRIOR_WITH_DOOMED = (
    "## Owned Section\n\nseed rule text.\n\ndoomed rule text.\n"
    "## Unowned Section\ncarried forward text verbatim\n"
)
_DECL_SECTIONS = {"owned-section": "corpus-owned", "unowned-section": "unowned"}


def _entry(entry_id: str, text: str) -> CorpusEntry:
    return CorpusEntry(
        id=entry_id,
        surface=LAND_SURFACE,
        section="owned-section",
        tier="compressible",
        classification="Ambiguous",
        text=text,
        origin="test",
        ts="2026-09-27T00:00:00Z",
    )


def build_land_project(
    root: Path,
    *,
    prior_text: str = LAND_PRIOR_TEXT,
    new_delta: bool = True,
) -> None:
    """Build an isolated three-consumer project under *root*.

    Writes a vendor manifest routing ``LAND_SURFACE`` to three consumers, a
    corpus, a witnessed ownership declaration, and a prior committed rendition
    plus provenance sidecar per consumer frozen against the corpus AS SEEDED.
    With *new_delta* one entry is appended afterward, so every sidecar's corpus
    fingerprint is stale: the landing carries a NEW corpus delta.
    """
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / "data" / "vendor-manifest.json").write_text(
        json.dumps(
            {
                "content_type_routes": {LAND_OWNER: list(LAND_CONSUMERS)},
                "content_type_temperatures": {LAND_OWNER: dict.fromkeys(LAND_CONSUMERS, "lite")},
                "surface_content_types": {LAND_SURFACE: LAND_OWNER},
            }
        ),
        encoding="utf-8",
    )
    (root / ".gzkit").mkdir(exist_ok=True)
    append_entry(root, LAND_SURFACE, _entry("e-seed", "seed rule text."))

    spans = measure_section_spans(prior_text)
    floor = sum(span for sid, span in spans.items() if _DECL_SECTIONS.get(sid) == "unowned")
    digest = sections_digest(_DECL_SECTIONS)
    event_id = f"section-ownership-genesis-{LAND_SURFACE}-{digest[:12]}"
    emit_section_ownership_genesis(root, event_id, LAND_SURFACE, digest, floor)
    decl = declaration_path(root, LAND_SURFACE)
    decl.parent.mkdir(parents=True, exist_ok=True)
    decl.write_text(
        json.dumps(
            {
                "surface": LAND_SURFACE,
                "sections": _DECL_SECTIONS,
                "unowned_byte_floor": floor,
                "measured_at": "2026-09-27T00:00:00Z",
                "floor_event_id": event_id,
            }
        ),
        encoding="utf-8",
    )

    corpus = load_corpus(root, LAND_SURFACE)
    prior_bytes = prior_text.encode("utf-8")
    for consumer in LAND_CONSUMERS:
        path = rendition_path(root, LAND_SURFACE, consumer)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(prior_bytes)
        sidecar = RenditionProvenance(
            corpus_fingerprint=corpus_fingerprint(corpus),
            corpus_entry_count=len(corpus.entries),
            rendition_fingerprint=rendition_fingerprint(prior_bytes),
            committed_ts="2026-09-26T00:00:00+00:00",
            attestor="g0",
            attestation_text="baseline attested",
        )
        fingerprint_path(root, LAND_SURFACE, consumer).write_bytes(
            (sidecar.model_dump_json(indent=2) + "\n").encode("utf-8")
        )

    if new_delta:
        append_entry(root, LAND_SURFACE, _entry("e-new", "new rule text."))


def _configure_attestor(root: Path, handle: str) -> None:
    """Write a `.gzkit.json` recording *handle* as the configured attestor default."""
    GzkitConfig(authorship=AuthorshipConfig(attestor_handle=handle)).save(root / ".gzkit.json")


def write_dropped_map(root: Path, consumer: str, *, condition_id: str = "C1") -> Path:
    """Write a retention map DROPPING the doomed block under *condition_id*."""
    retention_map = RetentionMap(
        surface=LAND_SURFACE,
        consumer=consumer,
        extracted_by="reviewer-agent",
        mapped_by="author-agent",
        blocks=[
            RemovedBlock(
                removed="doomed rule text.",
                conditions=[
                    Condition(
                        id=condition_id,
                        quote="doomed rule text.",
                        disposition="dropped",
                        reason="superseded by the seed rule",
                    )
                ],
            )
        ],
    )
    path = root / f"{consumer}.map.json"
    path.write_text(retention_map.model_dump_json(), encoding="utf-8")
    return path


def snapshot_tree(root: Path) -> dict[str, str]:
    """Return ``{relative posix path: sha256}`` for every file under *root*."""
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _land_args(*extra: str, attestor: str = "g0", text: str = "corpus delta attested") -> list:
    return [
        "content",
        "land",
        LAND_SURFACE,
        "--attestor",
        attestor,
        "--attestation-text",
        text,
        *extra,
    ]


class TestLandSurfaceIsRequired(unittest.TestCase):
    """REQ-0.35.0-07-01: the positional surface is required, matching compose/commit."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-07-01")
    def test_land_without_surface_is_a_usage_error(self) -> None:
        with self._runner.isolated_filesystem():
            result = self._runner.invoke(main, ["content", "land"])
        # argparse's usage-error exit is 2; the gz CLI renders the error line
        # itself, naming the verb and the missing positional.
        self.assertEqual(result.exit_code, 2, msg=result.output)
        self.assertIn(
            "gz content land: error: the following arguments are required: surface",
            result.output,
        )


class TestLandAttestationFailClosed(unittest.TestCase):
    """REQ-0.35.0-07-03 (refusal half): an unattested corpus delta writes NOTHING.

    "Nothing" is witnessed as a byte-identical project tree: no journal, no
    rendition, no sidecar, and a byte-identical ledger.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _assert_refused_writing_nothing(self, args: list, *, project: dict | None = None) -> str:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root, **(project or {}))
            before = snapshot_tree(root)
            result = self._runner.invoke(main, args)
            after = snapshot_tree(root)
        self.assertEqual(result.exit_code, 1, msg=result.output)
        self.assertEqual(before, after, "a refused landing must write nothing at all")
        self.assertIn("--attestation-text", result.output)
        self.assertIn("Next", result.output)
        return result.output

    @covers("REQ-0.35.0-07-03")
    def test_new_delta_with_empty_attestor_refuses(self) -> None:
        self._assert_refused_writing_nothing(_land_args(attestor=""))

    @covers("REQ-0.35.0-07-03")
    def test_new_delta_with_empty_attestation_text_refuses(self) -> None:
        self._assert_refused_writing_nothing(_land_args(text=""))

    @covers("REQ-0.35.0-07-03")
    def test_new_delta_with_whitespace_only_attestor_or_text_refuses(self) -> None:
        self._assert_refused_writing_nothing(_land_args(attestor="   "))
        self._assert_refused_writing_nothing(_land_args(text=" \t "))

    @covers("REQ-0.35.0-07-03")
    def test_unchanged_corpus_with_forged_sidecar_is_not_reusable_evidence(self) -> None:
        """A sidecar whose rendition_fingerprint no longer matches its bytes is not proof."""
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root, new_delta=False)
            # Forge beta's sidecar: the current corpus fingerprint, but a rendition
            # fingerprint describing bytes that are not on disk -- the shape of a
            # good sidecar copied next to other bytes.
            sidecar_path = fingerprint_path(root, LAND_SURFACE, "beta")
            forged = json.loads(sidecar_path.read_text(encoding="utf-8"))
            forged["rendition_fingerprint"] = hashlib.sha256(b"other bytes").hexdigest()
            sidecar_path.write_bytes(json.dumps(forged).encode("utf-8"))
            before = snapshot_tree(root)
            result = self._runner.invoke(main, _land_args(attestor="", text=""))
            after = snapshot_tree(root)
        self.assertEqual(result.exit_code, 1, msg=result.output)
        self.assertEqual(before, after)
        self.assertIn("'beta': its rendition_fingerprint does not match", result.output)

    @covers("REQ-0.35.0-07-03")
    def test_unchanged_corpus_with_corrupt_sidecar_is_not_reusable_evidence(self) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root, new_delta=False)
            fingerprint_path(root, LAND_SURFACE, "gamma").write_bytes(b"{not json")
            before = snapshot_tree(root)
            result = self._runner.invoke(main, _land_args(attestor="", text=""))
            after = snapshot_tree(root)
        self.assertEqual(result.exit_code, 1, msg=result.output)
        self.assertEqual(before, after)
        self.assertIn("'gamma': its provenance sidecar is unreadable or malformed", result.output)


class TestLandRetentionGateRefusesWholeLanding(unittest.TestCase):
    """REQ-0.35.0-07-10 (refusal half): an unaccounted removed block refuses EVERY consumer."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _run(self, *extra: str, text: str = "corpus delta attested", maps: tuple = ()) -> tuple:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root, prior_text=LAND_PRIOR_WITH_DOOMED)
            map_args: list[str] = []
            for consumer in maps:
                map_args += ["--retention-map", write_dropped_map(root, consumer).as_posix()]
            before = snapshot_tree(root)
            result = self._runner.invoke(main, _land_args(*map_args, *extra, text=text))
            after = snapshot_tree(root)
        return result, before, after

    @covers("REQ-0.35.0-07-10")
    def test_removed_block_without_map_refuses_all_three_consumers(self) -> None:
        result, before, after = self._run()
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertEqual(before, after, "no consumer may be written when one is refused")
        self.assertIn("missing-retention-map", result.output)

    @covers("REQ-0.35.0-07-10")
    def test_dropped_id_absent_from_this_invocations_text_refuses(self) -> None:
        result, before, after = self._run(
            text="corpus delta attested", maps=("alpha", "beta", "gamma")
        )
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertEqual(before, after)
        self.assertIn("dropped-id-not-attested", result.output)


class TestLandDryRunWritesNothing(unittest.TestCase):
    """--dry-run prints the plan for every consumer and writes nothing, not even the ledger."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-07-03")
    def test_dry_run_plans_every_consumer_and_writes_nothing(self) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root)
            before = snapshot_tree(root)
            result = self._runner.invoke(main, _land_args("--dry-run"))
            after = snapshot_tree(root)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(before, after, "a dry run must write nothing")
        for consumer in LAND_CONSUMERS:
            self.assertIn(f".gzkit/renditions/{LAND_SURFACE}/{consumer}.md", result.output)
            self.assertIn(
                f".gzkit/renditions/{LAND_SURFACE}/{consumer}.lineage.json", result.output
            )


def landed_events(root: Path) -> list[dict]:
    """Return every ``rendition_landed`` row in *root*'s ledger, in order."""
    ledger = root / ".gzkit" / "ledger.jsonl"
    rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line]
    return [row for row in rows if row.get("event") == "rendition_landed"]


def committed_artifacts(snapshot: dict[str, str]) -> dict[str, str]:
    """Drop the surface lock sidecar: an OS lock file is not a committed artifact."""
    return {path: digest for path, digest in snapshot.items() if not path.endswith(".lock")}


def _surface_dir(root: Path) -> Path:
    return root / ".gzkit" / "renditions" / LAND_SURFACE


class TestLandPublishesTheWholeSet(unittest.TestCase):
    """REQ-04/05 and the REQ-03/10 success halves, end to end through the real CLI."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _sidecars(self, root: Path) -> list[RenditionProvenance]:
        return [
            RenditionProvenance.model_validate_json(
                fingerprint_path(root, LAND_SURFACE, consumer).read_text(encoding="utf-8")
            )
            for consumer in LAND_CONSUMERS
        ]

    @covers("REQ-0.35.0-07-04")
    def test_every_sidecar_shares_one_attestation_and_landing_id_with_one_event(self) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root)
            result = self._runner.invoke(main, _land_args())
            sidecars = self._sidecars(root)
            events = landed_events(root)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual({s.attestation_text for s in sidecars}, {"corpus delta attested"})
        landing_ids = {s.landing_id for s in sidecars}
        self.assertEqual(len(landing_ids), 1, f"one shared landing_id, got {landing_ids}")
        (landing_id,) = landing_ids
        self.assertIsNotNone(landing_id)
        self.assertEqual(
            [event["landing_id"] for event in events],
            [landing_id],
            "exactly one rendition_landed event for the corpus delta",
        )
        self.assertEqual(
            [consumer["consumer"] for consumer in events[0]["consumers"]], list(LAND_CONSUMERS)
        )
        self.assertIn(str(landing_id), result.output)
        self.assertIn("uv run gz agent sync control-surfaces", result.output)

    @covers("REQ-0.35.0-07-05")
    def test_completed_landing_leaves_no_journal_or_staging(self) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root)
            result = self._runner.invoke(main, _land_args())
            leftovers = sorted(
                path.name
                for path in _surface_dir(root).iterdir()
                if path.name.startswith(".landing") and not path.name.endswith(".lock")
            )
            events = landed_events(root)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(len(events), 1, "the landing must have completed")
        self.assertEqual(leftovers, [], "the journal and staging are cleared LAST, on success")

    @covers("REQ-0.35.0-07-03")
    def test_unchanged_corpus_lands_reusing_the_standing_attestation(self) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root, new_delta=False)
            result = self._runner.invoke(main, _land_args(attestor="", text=""))
            sidecars = self._sidecars(root)
            events = landed_events(root)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(
            {(s.attestor, s.attestation_text) for s in sidecars}, {("g0", "baseline attested")}
        )
        self.assertEqual(len({s.landing_id for s in sidecars} - {None}), 1)
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0]["attestation_reused"])
        self.assertIn("reused", result.output)

    @covers("REQ-0.35.0-07-10")
    def test_valid_maps_publish_each_consumers_retention_sidecar(self) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root, prior_text=LAND_PRIOR_WITH_DOOMED)
            map_args: list[str] = []
            expected: dict[str, bytes] = {}
            for consumer in LAND_CONSUMERS:
                map_path = write_dropped_map(root, consumer)
                map_args += ["--retention-map", map_path.as_posix()]
                reviewed = RetentionMap.model_validate_json(map_path.read_text(encoding="utf-8"))
                expected[consumer] = (reviewed.model_dump_json() + "\n").encode("utf-8")
            result = self._runner.invoke(main, _land_args(*map_args, text="C1 drop accepted"))
            sidecars = {
                consumer: _surface_dir(root) / f"{consumer}.retention.json"
                for consumer in LAND_CONSUMERS
            }
            published = {c: p.read_bytes() for c, p in sidecars.items() if p.exists()}
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(published, expected)

    @covers("REQ-0.35.0-07-10")
    def test_stale_retention_sidecar_is_removed_when_no_block_is_removed(self) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root)
            stale = _surface_dir(root) / "beta.retention.json"
            stale.write_bytes(b"{}\n")
            result = self._runner.invoke(main, _land_args())
            still_there = stale.exists()
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertFalse(still_there, "a stale retention sidecar never outlives the landing")


def _interrupt_after_alpha_cli(runner: CliRunner, root: Path) -> str:
    """Land through the CLI, crashing on beta's first replacement; return the landing id."""
    import gzkit.content.landing as landing_mod  # noqa: PLC0415 - fixture stays landing-free

    real_replace = landing_mod._replace_artifact

    def replace(root_: Path, staging: Path, artifact) -> None:  # noqa: ANN001
        if Path(artifact.path).name.startswith("beta."):
            raise OSError("injected: interrupted after the first consumer")
        real_replace(root_, staging, artifact)

    with mock.patch.object(landing_mod, "_replace_artifact", side_effect=replace):
        result = runner.invoke(main, _land_args())
    assert result.exit_code == 2, result.output
    journal = json.loads((_surface_dir(root) / ".landing.json").read_text(encoding="utf-8"))
    return journal["landing_id"]


def _status_verdicts(output: str) -> dict[str, str]:
    verdicts: dict[str, str] = {}
    for line in output.splitlines():
        name, _, verdict = line.strip().partition(": ")
        if name in LAND_CONSUMERS and verdict in ("new", "old", "indeterminate"):
            verdicts[name] = verdict
    return verdicts


class TestLandStatusRendering(unittest.TestCase):
    """REQ-0.35.0-07-06 through the CLI: `--status <landing_id>` is read-only.

    output-contract: the per-consumer `<consumer>: <verdict>` line is the
    operator-facing status contract, so it is parsed here.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-07-06")
    def test_status_classifies_mixed_state_and_writes_nothing(self) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root)
            landing_id = _interrupt_after_alpha_cli(self._runner, root)
            before = snapshot_tree(root)
            result = self._runner.invoke(
                main, ["content", "land", LAND_SURFACE, "--status", landing_id]
            )
            after = snapshot_tree(root)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(before, after, "status is read-only")
        self.assertEqual(
            _status_verdicts(result.output), {"alpha": "new", "beta": "old", "gamma": "old"}
        )
        self.assertIn("publishing", result.output)

    @covers("REQ-0.35.0-07-06")
    def test_status_of_an_unknown_landing_exits_1(self) -> None:
        with self._runner.isolated_filesystem():
            build_land_project(Path("."))
            result = self._runner.invoke(
                main,
                ["content", "land", LAND_SURFACE, "--status", "landing-20260101T000000Z-00000000"],
            )
        self.assertEqual(result.exit_code, 1, msg=result.output)
        self.assertIn("Next:", result.output)


class TestLandResume(unittest.TestCase):
    """REQ-0.35.0-07-07/08 through the CLI: re-running `land` resumes the journaled landing."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _sidecar_record(self, root: Path) -> set[tuple]:
        return {
            (s.landing_id, s.attestor, s.attestation_text)
            for s in (
                RenditionProvenance.model_validate_json(
                    fingerprint_path(root, LAND_SURFACE, c).read_text(encoding="utf-8")
                )
                for c in LAND_CONSUMERS
            )
        }

    @covers("REQ-0.35.0-07-07")
    def test_resume_without_attestation_completes_with_the_recorded_one(self) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root)
            landing_id = _interrupt_after_alpha_cli(self._runner, root)
            alpha = rendition_path(root, LAND_SURFACE, "alpha").read_bytes()
            result = self._runner.invoke(main, ["content", "land", LAND_SURFACE])
            record = self._sidecar_record(root)
            alpha_after = rendition_path(root, LAND_SURFACE, "alpha").read_bytes()
            events = landed_events(root)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(record, {(landing_id, "g0", "corpus delta attested")})
        self.assertEqual(alpha_after, alpha)
        self.assertEqual([e["landing_id"] for e in events], [landing_id])

    @covers("REQ-0.35.0-07-08")
    def test_resume_with_different_explicit_attestation_keeps_the_recorded_one(self) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root)
            landing_id = _interrupt_after_alpha_cli(self._runner, root)
            result = self._runner.invoke(main, _land_args(attestor="x", text="other words"))
            record = self._sidecar_record(root)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(record, {(landing_id, "g0", "corpus delta attested")})
        self.assertIn("ignored", result.output)

    @covers("REQ-0.35.0-07-08")
    def test_resume_with_no_flags_under_a_configured_attestor_prints_no_ignored_note(
        self,
    ) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root)
            _configure_attestor(root, "g0")
            _interrupt_after_alpha_cli(self._runner, root)
            result = self._runner.invoke(main, ["content", "land", LAND_SURFACE])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertNotIn("ignored", result.output)

    @covers("REQ-0.35.0-07-08")
    def test_resume_with_explicit_attestation_text_alone_prints_the_ignored_note(self) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root)
            _configure_attestor(root, "g0")
            _interrupt_after_alpha_cli(self._runner, root)
            result = self._runner.invoke(
                main, ["content", "land", LAND_SURFACE, "--attestation-text", "other words"]
            )
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("--attestation-text were ignored", result.output)
        self.assertNotIn("--attestor/--attestation-text", result.output)

    @covers("REQ-0.35.0-07-08")
    def test_resume_with_a_retention_map_names_it_as_dropped(self) -> None:
        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root)
            _interrupt_after_alpha_cli(self._runner, root)
            map_path = write_dropped_map(root, "alpha")
            result = self._runner.invoke(
                main, ["content", "land", LAND_SURFACE, "--retention-map", map_path.as_posix()]
            )
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn(map_path.as_posix(), result.output)
        self.assertIn("dropped", result.output)

    @covers("REQ-0.35.0-07-08")
    def test_no_force_style_override_is_offered(self) -> None:
        with self._runner.isolated_filesystem():
            result = self._runner.invoke(main, ["content", "land", LAND_SURFACE, "--force"])
        self.assertEqual(result.exit_code, 2, msg=result.output)
        self.assertIn("unrecognized arguments: --force", result.output)


class _HardKill(BaseException):
    """A process kill: nothing in the landing gets to clean up."""


class TestLandResumeAfterKillMidStaging(unittest.TestCase):
    """REQ-0.35.0-07-08 through the CLI: a kill mid-staging resumes with no attestation."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-07-08")
    def test_land_without_attestation_completes_a_landing_killed_while_staging(self) -> None:
        import gzkit.content.landing as landing_mod  # noqa: PLC0415 - fixture stays landing-free

        real_stage = landing_mod._stage_artifact
        staged: list[Path] = []

        def stage(path: Path, data: bytes) -> None:
            if staged:
                raise _HardKill
            real_stage(path, data)
            staged.append(path)

        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root)
            with (
                mock.patch.object(landing_mod, "_stage_artifact", side_effect=stage),
                contextlib.suppress(_HardKill),
            ):
                self._runner.invoke(main, _land_args())
            journal = json.loads((_surface_dir(root) / ".landing.json").read_text(encoding="utf-8"))
            result = self._runner.invoke(main, ["content", "land", LAND_SURFACE])
            sidecars = {
                (s.landing_id, s.attestor, s.attestation_text)
                for s in (
                    RenditionProvenance.model_validate_json(
                        fingerprint_path(root, LAND_SURFACE, c).read_text(encoding="utf-8")
                    )
                    for c in LAND_CONSUMERS
                )
            }
            events = landed_events(root)
        self.assertEqual(journal["phase"], "prepared")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(sidecars, {(journal["landing_id"], "g0", "corpus delta attested")})
        self.assertEqual([e["landing_id"] for e in events], [journal["landing_id"]])


class TestLandResumeRetentionAfterKill(unittest.TestCase):
    """REQ-0.35.0-07-08 through the CLI: a retention landing killed before staging resumes."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-07-08")
    def test_land_without_attestation_publishes_the_reviewed_retention_sidecars(self) -> None:
        import gzkit.content.landing as landing_mod  # noqa: PLC0415 - fixture stays landing-free

        with self._runner.isolated_filesystem():
            root = Path(".")
            build_land_project(root, prior_text=LAND_PRIOR_WITH_DOOMED)
            map_args: list[str] = []
            expected: dict[str, bytes] = {}
            for consumer in LAND_CONSUMERS:
                map_path = write_dropped_map(root, consumer)
                map_args += ["--retention-map", map_path.as_posix()]
                reviewed = RetentionMap.model_validate_json(map_path.read_text(encoding="utf-8"))
                expected[consumer] = (reviewed.model_dump_json() + "\n").encode("utf-8")
            with (
                mock.patch.object(landing_mod, "_stage_artifact", side_effect=_HardKill),
                contextlib.suppress(_HardKill),
            ):
                self._runner.invoke(main, _land_args(*map_args, text="C1 drop accepted"))
            result = self._runner.invoke(main, ["content", "land", LAND_SURFACE])
            published = {
                c: (_surface_dir(root) / f"{c}.retention.json").read_bytes()
                for c in LAND_CONSUMERS
                if (_surface_dir(root) / f"{c}.retention.json").exists()
            }
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(published, expected)
