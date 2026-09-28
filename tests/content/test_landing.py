"""Landing preparation tests -- OBPI-0.35.0-07 (pure preflight layer).

REQ-derived: ``prepare_landing`` builds one plan for every routed consumer and
writes nothing; the journal models accept only the surface's own artifact
paths; the published byte forms equal the forms the loaders and gates read;
the provenance sidecar gains an optional ``landing_id`` without loosening
``extra="forbid"``.
"""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from unittest import mock

from pydantic import ValidationError

import gzkit.content.landing as landing_mod
from gzkit.content.corpus_store import append_entry
from gzkit.content.landing import (
    ArtifactKind,
    ArtifactTarget,
    ConsumerPlan,
    LandingJournal,
    LandingPlan,
    LandingRefusal,
    artifact_relpath,
    complete_landing,
    journal_path,
    lineage_bytes,
    load_journal,
    prepare_landing,
    provenance_bytes,
    publish_landing,
    sha256_hex,
)
from gzkit.content.lineage import (
    ConsumerLineage,
    SectionLineage,
    lineage_path,
    save_candidate_lineage,
)
from gzkit.content.models import CorpusEntry
from gzkit.content.rendition_store import (
    RenditionProvenance,
    fingerprint_path,
    load_fingerprint,
    rendition_path,
    save_fingerprint,
)
from gzkit.content.retention import RetentionMap, retention_path
from gzkit.traceability import covers
from tests.commands.test_content_land import (
    LAND_CONSUMERS,
    LAND_PRIOR_WITH_DOOMED,
    LAND_SURFACE,
    build_land_project,
    committed_artifacts,
    landed_events,
    snapshot_tree,
    write_dropped_map,
)

_SHA = "a" * 64
_LANDING_ID = "landing-20260927T120000Z-0123abcd"


def _journal(**overrides: object) -> dict:
    document: dict = {
        "landing_id": _LANDING_ID,
        "surface": LAND_SURFACE,
        "phase": "prepared",
        "new_corpus_fingerprint": _SHA,
        "corpus_entry_count": 2,
        "route_digest": _SHA,
        "ownership_digest": _SHA,
        "consumers": [
            {
                "consumer": "alpha",
                "old_corpus_fingerprint": None,
                "artifacts": [
                    {
                        "kind": "rendition",
                        "path": f".gzkit/renditions/{LAND_SURFACE}/alpha.md",
                        "old_sha256": None,
                        "new_sha256": _SHA,
                    }
                ],
            }
        ],
        "attestor": "g0",
        "attestation_text": "attested",
        "attestation_reused": False,
        "created_ts": "2026-09-27T12:00:00+00:00",
    }
    document.update(overrides)
    return document


def _with_path(path: str) -> dict:
    document = _journal()
    document["consumers"][0]["artifacts"][0]["path"] = path
    return document


_OLD_SIDECAR = {
    "corpus_fingerprint": _SHA,
    "corpus_entry_count": 1,
    "committed_ts": "2026-09-26T00:00:00+00:00",
    "attestor": "g0",
    "attestation_text": "baseline",
}


def _must_succeed(test: unittest.TestCase, call, *args):
    """Run a landing that must succeed; report a refusal as a failed assertion.

    A success-path test that lets ``LandingRefusal`` escape errors instead of
    failing, so a mutation that breaks the landing reads as an execution error
    rather than as the assertion the test exists to make.
    """
    try:
        return call(*args)
    except LandingRefusal as exc:
        test.fail(f"landing refused with exit {exc.exit_code}:\n{exc.message}")


class _TempRoot(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)


class TestProvenanceLandingId(unittest.TestCase):
    """REQ-0.35.0-07-04: sidecars carry an optional landing_id; nothing else loosens."""

    @covers("REQ-0.35.0-07-04")
    def test_new_sidecar_carries_landing_id(self) -> None:
        prov = RenditionProvenance.model_validate({**_OLD_SIDECAR, "landing_id": _LANDING_ID})
        self.assertEqual(prov.landing_id, _LANDING_ID)

    @covers("REQ-0.35.0-07-04")
    def test_old_sidecar_loads_and_unexpected_or_lineage_field_is_rejected(self) -> None:
        self.assertIsNone(RenditionProvenance.model_validate(_OLD_SIDECAR).landing_id)
        with self.assertRaises(ValidationError):
            RenditionProvenance.model_validate({**_OLD_SIDECAR, "lineage": {}})


class TestByteForms(_TempRoot):
    """The landing publishes exactly the bytes the loaders and gates read."""

    @covers("REQ-0.35.0-07-04")
    def test_lineage_bytes_equal_save_candidate_lineage(self) -> None:
        lineage = ConsumerLineage(
            surface=LAND_SURFACE,
            consumer="alpha",
            sections={"s": SectionLineage(owned=True, entry_ids=("e1",), byte_span=(0, 5))},
        )
        written = save_candidate_lineage(self.root, lineage).read_bytes()
        self.assertEqual(lineage_bytes(lineage), written)

    @covers("REQ-0.35.0-07-04")
    def test_provenance_bytes_equal_save_fingerprint_on_every_platform(self) -> None:
        prov = RenditionProvenance.model_validate(_OLD_SIDECAR)
        save_fingerprint(self.root, LAND_SURFACE, "alpha", prov)
        written = fingerprint_path(self.root, LAND_SURFACE, "alpha").read_bytes()
        self.assertEqual(provenance_bytes(prov), written)

    @covers("REQ-0.35.0-07-04")
    def test_artifact_relpaths_are_the_loaders_paths(self) -> None:
        expected: tuple[tuple[ArtifactKind, Path], ...] = (
            ("rendition", rendition_path(self.root, LAND_SURFACE, "alpha")),
            ("provenance", fingerprint_path(self.root, LAND_SURFACE, "alpha")),
            ("lineage", lineage_path(self.root, LAND_SURFACE, "alpha")),
            ("retention", retention_path(self.root, LAND_SURFACE, "alpha")),
        )
        for kind, path in expected:
            self.assertEqual(
                artifact_relpath(LAND_SURFACE, "alpha", kind),
                path.relative_to(self.root).as_posix(),
            )


class TestJournalPathSafety(unittest.TestCase):
    """REQ-0.35.0-07-05: the journal may name only the surface's own artifact files."""

    @covers("REQ-0.35.0-07-05")
    def test_valid_journal_round_trips(self) -> None:
        journal = LandingJournal.model_validate(_journal())
        self.assertEqual(journal, LandingJournal.model_validate_json(journal.model_dump_json()))

    @covers("REQ-0.35.0-07-05")
    def test_unsafe_or_foreign_paths_are_rejected(self) -> None:
        for path in (
            f".gzkit/renditions/{LAND_SURFACE}/../other/alpha.md",
            "/etc/alpha.md",
            "C:/alpha.md",
            f".gzkit\\renditions\\{LAND_SURFACE}\\alpha.md",
            ".gzkit/renditions/OtherSurface.md/alpha.md",
            f".gzkit/renditions/{LAND_SURFACE}/beta.md",
            f".gzkit/renditions/{LAND_SURFACE}/alpha.corpus.json",
        ):
            with self.subTest(path=path), self.assertRaises(ValidationError):
                LandingJournal.model_validate(_with_path(path))

    @covers("REQ-0.35.0-07-05")
    def test_malformed_landing_id_hash_and_duplicate_kind_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            LandingJournal.model_validate(_journal(landing_id="landing-x"))
        with self.assertRaises(ValidationError):
            ArtifactTarget(kind="rendition", path="a.md", old_sha256="zz", new_sha256=None)
        target = ArtifactTarget(kind="rendition", path="a.md", old_sha256=None, new_sha256=_SHA)
        with self.assertRaises(ValidationError):
            ConsumerPlan(consumer="alpha", old_corpus_fingerprint=None, artifacts=(target, target))


class TestPrepareLanding(_TempRoot):
    """prepare_landing plans every consumer under one landing_id and writes nothing."""

    def _prepare(self, **kwargs: object):
        arguments: dict = {"attestor": "g0", "attestation_text": "delta attested"}
        arguments.update(kwargs)
        return prepare_landing(self.root, LAND_SURFACE, **arguments)

    @covers("REQ-0.35.0-07-04")
    def test_every_sidecar_shares_one_landing_id_and_attestation(self) -> None:
        build_land_project(self.root)
        before = snapshot_tree(self.root)
        plan = self._prepare()
        self.assertEqual(before, snapshot_tree(self.root), "preparation must write nothing")
        journal = plan.journal
        self.assertEqual([c.consumer for c in journal.consumers], list(LAND_CONSUMERS))
        sidecars = [
            RenditionProvenance.model_validate_json(
                plan.payloads[artifact_relpath(LAND_SURFACE, consumer, "provenance")]
            )
            for consumer in LAND_CONSUMERS
        ]
        self.assertEqual({s.landing_id for s in sidecars}, {journal.landing_id})
        self.assertEqual({s.attestation_text for s in sidecars}, {"delta attested"})
        self.assertEqual({s.corpus_fingerprint for s in sidecars}, {journal.new_corpus_fingerprint})
        for consumer, sidecar in zip(LAND_CONSUMERS, sidecars, strict=True):
            rendition = plan.payloads[artifact_relpath(LAND_SURFACE, consumer, "rendition")]
            self.assertEqual(sidecar.rendition_fingerprint, sha256_hex(rendition))
        self.assertFalse(journal.attestation_reused)
        for consumer_plan in journal.consumers:
            self.assertNotIn(
                consumer_plan.old_corpus_fingerprint, (None, journal.new_corpus_fingerprint)
            )

    @covers("REQ-0.35.0-07-03")
    def test_unchanged_corpus_reuses_verified_evidence(self) -> None:
        build_land_project(self.root, new_delta=False)
        plan = self._prepare(attestor="", attestation_text="")
        self.assertTrue(plan.journal.attestation_reused)
        self.assertEqual(plan.journal.attestor, "g0")
        self.assertEqual(plan.journal.attestation_text, "baseline attested")

    @covers("REQ-0.35.0-07-03")
    def test_new_delta_without_attestation_refuses_with_exit_1(self) -> None:
        build_land_project(self.root)
        with self.assertRaises(LandingRefusal) as ctx:
            self._prepare(attestation_text="  ")
        self.assertEqual(ctx.exception.exit_code, 1)

    @covers("REQ-0.35.0-07-03")
    def test_disagreeing_committed_attestations_are_not_reusable(self) -> None:
        build_land_project(self.root, new_delta=False)
        path = fingerprint_path(self.root, LAND_SURFACE, "gamma")
        document = json.loads(path.read_text(encoding="utf-8"))
        document["attestation_text"] = "some other words"
        path.write_bytes(json.dumps(document).encode("utf-8"))
        with self.assertRaises(LandingRefusal) as ctx:
            self._prepare(attestor="", attestation_text="")
        self.assertEqual(ctx.exception.exit_code, 1)
        self.assertIn("disagreeing", ctx.exception.message)

    @covers("REQ-0.35.0-07-10")
    def test_valid_maps_plan_a_retention_sidecar_per_consumer(self) -> None:
        build_land_project(self.root, prior_text=LAND_PRIOR_WITH_DOOMED)
        maps = [write_dropped_map(self.root, c).as_posix() for c in LAND_CONSUMERS]
        plan = self._prepare(attestation_text="C1 drop accepted", retention_maps=maps)
        for consumer_plan in plan.journal.consumers:
            path = artifact_relpath(LAND_SURFACE, consumer_plan.consumer, "retention")
            self.assertIn("retention", {a.kind for a in consumer_plan.artifacts})
            self.assertEqual(json.loads(plan.payloads[path])["consumer"], consumer_plan.consumer)

    @covers("REQ-0.35.0-07-10")
    def test_stale_retention_sidecar_is_planned_for_removal(self) -> None:
        build_land_project(self.root)
        retention_path(self.root, LAND_SURFACE, "beta").write_bytes(b"{}\n")
        plan = self._prepare()
        beta = next(c for c in plan.journal.consumers if c.consumer == "beta")
        retention = next(a for a in beta.artifacts if a.kind == "retention")
        self.assertIsNone(retention.new_sha256)
        self.assertEqual(retention.old_sha256, sha256_hex(b"{}\n"))

    @covers("REQ-0.35.0-07-10")
    def test_map_bound_to_no_routed_consumer_is_a_retention_refusal_exit_3(self) -> None:
        """A map binding to no landed consumer leaves every removal unaccounted: exit 3."""
        build_land_project(self.root, prior_text=LAND_PRIOR_WITH_DOOMED)
        stray = write_dropped_map(self.root, "delta").as_posix()
        before = snapshot_tree(self.root)
        with self.assertRaises(LandingRefusal) as ctx:
            self._prepare(attestation_text="C1 drop accepted", retention_maps=[stray])
        self.assertEqual(ctx.exception.exit_code, 3)
        self.assertEqual(before, snapshot_tree(self.root))
        self.assertIn("Next:", ctx.exception.message)

    @covers("REQ-0.35.0-07-10")
    def test_two_maps_for_one_consumer_is_a_user_error_exit_1(self) -> None:
        build_land_project(self.root, prior_text=LAND_PRIOR_WITH_DOOMED)
        alpha = write_dropped_map(self.root, "alpha").as_posix()
        with self.assertRaises(LandingRefusal) as ctx:
            self._prepare(attestation_text="C1 drop accepted", retention_maps=[alpha, alpha])
        self.assertEqual(ctx.exception.exit_code, 1)

    @covers("REQ-0.35.0-07-10")
    def test_removed_block_without_map_refuses_with_exit_3(self) -> None:
        build_land_project(self.root, prior_text=LAND_PRIOR_WITH_DOOMED)
        before = snapshot_tree(self.root)
        with self.assertRaises(LandingRefusal) as ctx:
            self._prepare()
        self.assertEqual(ctx.exception.exit_code, 3)
        self.assertEqual(before, snapshot_tree(self.root))


def _consumer_of(path: str) -> str:
    return PurePosixPath(path).name.split(".", 1)[0]


class TestPublishLanding(_TempRoot):
    """Durable publication: journal first, per-file replace, one event, journal cleared LAST."""

    def _plan(self, **project: object) -> LandingPlan:
        build_land_project(self.root, **project)
        return prepare_landing(
            self.root, LAND_SURFACE, attestor="g0", attestation_text="delta attested"
        )

    def _refused(self, plan: LandingPlan) -> LandingRefusal:
        with self.assertRaises(LandingRefusal) as ctx:
            publish_landing(self.root, plan)
        return ctx.exception

    def _on_disk(self, relpath: str) -> str | None:
        path = self.root / relpath
        return sha256_hex(path.read_bytes()) if path.exists() else None

    def _journal_exists(self) -> bool:
        return journal_path(self.root, LAND_SURFACE).exists()

    @covers("REQ-0.35.0-07-04")
    def test_success_shares_landing_id_and_attestation_with_exactly_one_event(self) -> None:
        plan = self._plan()
        _must_succeed(self, publish_landing, self.root, plan)
        journal = plan.journal
        for consumer_plan in journal.consumers:
            sidecar = load_fingerprint(self.root, LAND_SURFACE, consumer_plan.consumer)
            assert sidecar is not None
            self.assertEqual(sidecar.landing_id, journal.landing_id)
            self.assertEqual(sidecar.attestation_text, "delta attested")
            for artifact in consumer_plan.artifacts:
                self.assertEqual(self._on_disk(artifact.path), artifact.new_sha256)
        events = landed_events(self.root)
        self.assertEqual([e["landing_id"] for e in events], [journal.landing_id])
        self.assertEqual(events[0]["id"], f"rendition-landed-{journal.landing_id}")
        manifest = {
            a["path"]: a["new_sha256"] for c in events[0]["consumers"] for a in c["artifacts"]
        }
        self.assertEqual(
            manifest,
            {a.path: a.new_sha256 for c in journal.consumers for a in c.artifacts},
            "the event carries the full target/hash manifest so status survives cleanup",
        )
        self.assertFalse(self._journal_exists())

    @covers("REQ-0.35.0-07-05")
    def test_journal_precedes_every_artifact_byte_and_survives_interruption(self) -> None:
        plan = self._plan()
        real_stage, real_replace = landing_mod._stage_artifact, landing_mod._replace_artifact
        journal_seen: list[bool] = []

        def stage(path: Path, data: bytes) -> None:
            journal_seen.append(self._journal_exists())
            real_stage(path, data)

        def replace(root: Path, staging: Path, artifact: ArtifactTarget) -> None:
            journal_seen.append(self._journal_exists())
            if _consumer_of(artifact.path) == "beta":
                raise OSError("injected: interrupted after the first consumer")
            real_replace(root, staging, artifact)

        with (
            mock.patch.object(landing_mod, "_stage_artifact", side_effect=stage),
            mock.patch.object(landing_mod, "_replace_artifact", side_effect=replace),
        ):
            refusal = self._refused(plan)
        self.assertEqual(refusal.exit_code, 2)
        self.assertTrue(journal_seen, "staging and replacement must have run")
        self.assertTrue(all(journal_seen), "the journal must exist before any artifact byte")
        journal = load_journal(self.root, LAND_SURFACE)
        assert journal is not None
        self.assertEqual(journal.landing_id, plan.journal.landing_id)
        self.assertEqual([c.consumer for c in journal.consumers], list(LAND_CONSUMERS))
        self.assertEqual(journal.new_corpus_fingerprint, plan.journal.new_corpus_fingerprint)
        self.assertEqual([c.published for c in journal.consumers], [True, False, False])
        self.assertEqual(landed_events(self.root), [])

    @covers("REQ-0.35.0-07-02")
    def test_staging_failure_on_second_consumer_modifies_nothing(self) -> None:
        plan = self._plan()
        before = committed_artifacts(snapshot_tree(self.root))
        real_stage = landing_mod._stage_artifact

        def stage(path: Path, data: bytes) -> None:
            if _consumer_of(path.name) == "beta":
                raise OSError("injected: disk full while staging beta")
            real_stage(path, data)

        with mock.patch.object(landing_mod, "_stage_artifact", side_effect=stage):
            refusal = self._refused(plan)
        self.assertEqual(refusal.exit_code, 2)
        self.assertEqual(committed_artifacts(snapshot_tree(self.root)), before)
        self.assertFalse(self._journal_exists())
        self.assertEqual(landed_events(self.root), [])
        self.assertIn("Next:", refusal.message)

    @covers("REQ-0.35.0-07-02")
    def test_replace_failure_after_first_file_keeps_journal_and_emits_nothing(self) -> None:
        plan = self._plan()
        real_replace = landing_mod._replace_artifact
        done: list[ArtifactTarget] = []

        def replace(root: Path, staging: Path, artifact: ArtifactTarget) -> None:
            if done:
                raise OSError("injected: replace failed between a rendition and its sidecars")
            real_replace(root, staging, artifact)
            done.append(artifact)

        with mock.patch.object(landing_mod, "_replace_artifact", side_effect=replace):
            refusal = self._refused(plan)
        landing_id = plan.journal.landing_id
        self.assertEqual(refusal.exit_code, 2)
        self.assertIn(f"gz content land {LAND_SURFACE} --status {landing_id}", refusal.message)
        self.assertIn("incomplete", refusal.message)
        journal = load_journal(self.root, LAND_SURFACE)
        assert journal is not None
        self.assertEqual(journal.phase, "publishing")
        self.assertFalse(journal.consumers[0].published)
        self.assertEqual(self._on_disk(done[0].path), done[0].new_sha256)
        self.assertEqual(landed_events(self.root), [])

    @covers("REQ-0.35.0-07-02")
    def test_journal_write_failure_before_any_byte_writes_nothing(self) -> None:
        plan = self._plan()
        before = committed_artifacts(snapshot_tree(self.root))
        with mock.patch.object(
            landing_mod, "_write_journal", side_effect=OSError("injected: journal write failed")
        ):
            refusal = self._refused(plan)
        self.assertEqual(refusal.exit_code, 2)
        self.assertEqual(committed_artifacts(snapshot_tree(self.root)), before)
        self.assertEqual(landed_events(self.root), [])

    @covers("REQ-0.35.0-07-05")
    def test_crash_after_last_file_before_event_leaves_verified_journal(self) -> None:
        plan = self._plan()
        with mock.patch.object(
            landing_mod, "emit_rendition_landed", side_effect=OSError("injected: crash")
        ):
            refusal = self._refused(plan)
        self.assertEqual(refusal.exit_code, 2)
        journal = load_journal(self.root, LAND_SURFACE)
        assert journal is not None
        self.assertEqual(journal.phase, "verified")
        self.assertEqual(landed_events(self.root), [])

    @covers("REQ-0.35.0-07-04")
    def test_crash_after_event_before_cleanup_never_duplicates_the_event(self) -> None:
        plan = self._plan()
        with mock.patch.object(
            landing_mod, "_clear_landing", side_effect=OSError("injected: crash before cleanup")
        ):
            refusal = self._refused(plan)
        self.assertEqual(refusal.exit_code, 2)
        self.assertEqual(len(landed_events(self.root)), 1)
        journal = load_journal(self.root, LAND_SURFACE)
        assert journal is not None
        complete_landing(self.root, journal)
        self.assertEqual(len(landed_events(self.root)), 1, "completion is idempotent by event id")
        self.assertFalse(self._journal_exists())

    @covers("REQ-0.35.0-07-02")
    def test_corrupt_artifact_with_valid_metadata_fails_verification(self) -> None:
        plan = self._plan()
        real_replace = landing_mod._replace_artifact
        last = plan.journal.consumers[-1].artifacts[-1].path
        alpha = self.root / artifact_relpath(LAND_SURFACE, "alpha", "rendition")

        def replace(root: Path, staging: Path, artifact: ArtifactTarget) -> None:
            real_replace(root, staging, artifact)
            if artifact.path == last:
                alpha.write_bytes(b"tampered bytes beside a good sidecar\n")

        with mock.patch.object(landing_mod, "_replace_artifact", side_effect=replace):
            refusal = self._refused(plan)
        self.assertEqual(refusal.exit_code, 2)
        self.assertIn("alpha.md", refusal.message)
        self.assertTrue(self._journal_exists())
        self.assertEqual(landed_events(self.root), [])

    @covers("REQ-0.35.0-07-02")
    def test_corpus_drift_after_preparation_refuses_writing_nothing(self) -> None:
        plan = self._plan()
        append_entry(
            self.root,
            LAND_SURFACE,
            CorpusEntry(
                id="e-late",
                surface=LAND_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="late rule text.",
                origin="test",
                ts="2026-09-27T00:00:00Z",
            ),
        )
        before = committed_artifacts(snapshot_tree(self.root))
        refusal = self._refused(plan)
        self.assertEqual(refusal.exit_code, 1)
        self.assertIn("corpus", refusal.message)
        self.assertEqual(committed_artifacts(snapshot_tree(self.root)), before)

    @covers("REQ-0.35.0-07-02")
    def test_retry_resumes_from_verified_hashes_not_from_the_published_flag(self) -> None:
        """REQ-02: retry never rewrites a file already at its new hash, flag or no flag."""
        plan = self._plan()
        real_replace = landing_mod._replace_artifact
        done: list[ArtifactTarget] = []

        def fail_after_first(root: Path, staging: Path, artifact: ArtifactTarget) -> None:
            if done:
                raise OSError("injected: replace failed after the first published file")
            real_replace(root, staging, artifact)
            done.append(artifact)

        with mock.patch.object(landing_mod, "_replace_artifact", side_effect=fail_after_first):
            refusal = self._refused(plan)
        self.assertEqual(refusal.exit_code, 2)
        first = done[0]
        first_path = self.root / first.path
        first_bytes = first_path.read_bytes()

        journal = load_journal(self.root, LAND_SURFACE)
        assert journal is not None
        self.assertFalse(
            journal.consumers[0].published, "the first file's consumer never completed"
        )

        replayed: list[str] = []

        def spy(root: Path, staging: Path, artifact: ArtifactTarget) -> None:
            replayed.append(artifact.path)
            real_replace(root, staging, artifact)

        with mock.patch.object(landing_mod, "_replace_artifact", side_effect=spy):
            _must_succeed(self, landing_mod.resume_landing, self.root, LAND_SURFACE)

        self.assertNotIn(first.path, replayed, "a hash-verified file must never be replayed")
        self.assertEqual(first_path.read_bytes(), first_bytes)
        for consumer_plan in plan.journal.consumers:
            for artifact in consumer_plan.artifacts:
                self.assertEqual(self._on_disk(artifact.path), artifact.new_sha256, artifact.path)
        self.assertEqual(len(landed_events(self.root)), 1)
        self.assertFalse(self._journal_exists())

    @covers("REQ-0.35.0-07-02")
    def test_staging_failure_with_a_failing_cleanup_still_raises_the_refusal(self) -> None:
        plan = self._plan()
        with (
            mock.patch.object(
                landing_mod, "_stage_artifact", side_effect=OSError("injected: disk full")
            ),
            mock.patch.object(
                landing_mod,
                "_clear_landing",
                side_effect=OSError("injected: cleanup failed too"),
            ),
        ):
            refusal = self._refused(plan)
        self.assertEqual(refusal.exit_code, 2)
        self.assertIn("injected: disk full", refusal.message)
        self.assertIn("injected: cleanup failed too", refusal.message)

    @covers("REQ-0.35.0-07-04")
    def test_manifest_round_trips_through_the_landed_event(self) -> None:
        """The manifest status rebuilds from the event agrees with the journal's own."""
        plan = self._plan()
        journal = _must_succeed(self, publish_landing, self.root, plan)
        event = landing_mod.landed_event(journal)
        serialized = event.model_dump(mode="json")
        manifest = landing_mod._manifest_from_event(journal.surface, journal.landing_id, serialized)

        def _shape(consumers: tuple) -> list:
            return [
                (
                    c.consumer,
                    [(a.path, a.kind, a.old_sha256, a.new_sha256) for a in c.artifacts],
                )
                for c in consumers
            ]

        self.assertEqual(_shape(manifest.consumers), _shape(journal.consumers))

    @covers("REQ-0.35.0-07-05")
    def test_active_journal_refuses_a_second_landing(self) -> None:
        plan = self._plan()
        path = journal_path(self.root, LAND_SURFACE)
        path.write_bytes(plan.journal.model_dump_json().encode("utf-8"))
        second = prepare_landing(
            self.root, LAND_SURFACE, attestor="g0", attestation_text="delta attested"
        )
        before = committed_artifacts(snapshot_tree(self.root))
        refusal = self._refused(second)
        self.assertEqual(refusal.exit_code, 1)
        self.assertIn(plan.journal.landing_id, refusal.message)
        self.assertEqual(committed_artifacts(snapshot_tree(self.root)), before)


def _interrupt_after_alpha(root: Path, plan: LandingPlan) -> None:
    """Publish *plan* and crash on beta's first replacement: alpha landed, beta/gamma old."""
    real_replace = landing_mod._replace_artifact

    def replace(root_: Path, staging: Path, artifact: ArtifactTarget) -> None:
        if _consumer_of(artifact.path) == "beta":
            raise OSError("injected: interrupted after the first consumer")
        real_replace(root_, staging, artifact)

    with (
        mock.patch.object(landing_mod, "_replace_artifact", side_effect=replace),
        contextlib.suppress(LandingRefusal),
    ):
        publish_landing(root, plan)


class TestLandingStatus(_TempRoot):
    """REQ-0.35.0-07-06: status classifies each consumer by hashes, never by mtime."""

    def _plan(self) -> LandingPlan:
        build_land_project(self.root)
        return prepare_landing(
            self.root, LAND_SURFACE, attestor="g0", attestation_text="delta attested"
        )

    def _verdicts(self, landing_id: str) -> dict[str, str]:
        status = landing_mod.landing_status(self.root, LAND_SURFACE, landing_id)
        return {c.consumer: c.verdict for c in status.consumers}

    @covers("REQ-0.35.0-07-06")
    def test_mixed_state_after_interruption_is_classified_exactly(self) -> None:
        plan = self._plan()
        _interrupt_after_alpha(self.root, plan)
        status = landing_mod.landing_status(self.root, LAND_SURFACE, plan.journal.landing_id)
        self.assertEqual(
            {c.consumer: c.verdict for c in status.consumers},
            {"alpha": "new", "beta": "old", "gamma": "old"},
        )
        self.assertEqual(status.phase, "publishing")
        self.assertEqual(status.source, "journal")

    @covers("REQ-0.35.0-07-06")
    def test_completed_landing_is_new_everywhere_from_the_ledger_event(self) -> None:
        plan = self._plan()
        _must_succeed(self, publish_landing, self.root, plan)
        self.assertFalse(journal_path(self.root, LAND_SURFACE).exists())
        status = landing_mod.landing_status(self.root, LAND_SURFACE, plan.journal.landing_id)
        self.assertEqual({c.verdict for c in status.consumers}, {"new"})
        self.assertEqual(status.phase, "complete")
        self.assertEqual(status.source, "ledger")

    @covers("REQ-0.35.0-07-06")
    def test_altered_rendition_beside_a_good_sidecar_is_indeterminate(self) -> None:
        plan = self._plan()
        _must_succeed(self, publish_landing, self.root, plan)
        alpha = self.root / artifact_relpath(LAND_SURFACE, "alpha", "rendition")
        alpha.write_bytes(b"altered bytes beside a good sidecar\n")
        status = landing_mod.landing_status(self.root, LAND_SURFACE, plan.journal.landing_id)
        verdicts = {c.consumer: c for c in status.consumers}
        self.assertEqual(verdicts["alpha"].verdict, "indeterminate")
        self.assertEqual(verdicts["beta"].verdict, "new")
        self.assertTrue(any("alpha.md" in finding for finding in verdicts["alpha"].findings))
        recovery = verdicts["alpha"].recovery or ""
        for part in ("Error:", "Why forbidden:", "Next:"):
            self.assertIn(part, recovery)

    @covers("REQ-0.35.0-07-06")
    def test_sidecar_claiming_another_landing_is_indeterminate(self) -> None:
        """A good-looking sidecar whose bytes are not this landing's is never `new`."""
        plan = self._plan()
        _interrupt_after_alpha(self.root, plan)
        # Copy alpha's freshly landed sidecar over beta's: beta's provenance now
        # matches NEITHER manifest entry, whatever the sidecar claims.
        beta = fingerprint_path(self.root, LAND_SURFACE, "beta")
        beta.write_bytes(fingerprint_path(self.root, LAND_SURFACE, "alpha").read_bytes())
        self.assertEqual(self._verdicts(plan.journal.landing_id)["beta"], "indeterminate")

    @covers("REQ-0.35.0-07-06")
    def test_identical_fingerprints_with_different_mtimes_classify_identically(self) -> None:
        plan = self._plan()
        _interrupt_after_alpha(self.root, plan)
        beta = rendition_path(self.root, LAND_SURFACE, "beta")
        gamma = rendition_path(self.root, LAND_SURFACE, "gamma")
        self.assertEqual(beta.read_bytes(), gamma.read_bytes())
        os.utime(beta, (1_000_000_000, 1_000_000_000))
        os.utime(gamma, (2_000_000_000, 2_000_000_000))
        verdicts = self._verdicts(plan.journal.landing_id)
        self.assertEqual(verdicts["beta"], verdicts["gamma"])
        self.assertEqual(verdicts["beta"], "old")

    @covers("REQ-0.35.0-07-06")
    def test_status_writes_nothing(self) -> None:
        plan = self._plan()
        _interrupt_after_alpha(self.root, plan)
        before = snapshot_tree(self.root)
        landing_mod.landing_status(self.root, LAND_SURFACE, plan.journal.landing_id)
        self.assertEqual(before, snapshot_tree(self.root))

    @covers("REQ-0.35.0-07-06")
    def test_unknown_landing_id_refuses_with_exit_1(self) -> None:
        self._plan()
        with self.assertRaises(LandingRefusal) as ctx:
            landing_mod.landing_status(self.root, LAND_SURFACE, _LANDING_ID)
        self.assertEqual(ctx.exception.exit_code, 1)
        self.assertIn("Next:", ctx.exception.message)


class TestResumeLanding(_TempRoot):
    """REQ-0.35.0-07-07/08: resume is non-destructive and reuses the recorded attestation."""

    def _interrupted(self) -> LandingPlan:
        build_land_project(self.root)
        plan = prepare_landing(
            self.root, LAND_SURFACE, attestor="g0", attestation_text="delta attested"
        )
        _interrupt_after_alpha(self.root, plan)
        return plan

    def _alpha_bytes(self) -> dict[str, bytes]:
        kinds: tuple[ArtifactKind, ...] = ("rendition", "provenance", "lineage")
        return {
            kind: (self.root / artifact_relpath(LAND_SURFACE, "alpha", kind)).read_bytes()
            for kind in kinds
        }

    def _refused(self) -> LandingRefusal:
        with self.assertRaises(LandingRefusal) as ctx:
            landing_mod.resume_landing(self.root, LAND_SURFACE)
        return ctx.exception

    @covers("REQ-0.35.0-07-07")
    def test_resume_leaves_the_landed_consumer_byte_unchanged(self) -> None:
        plan = self._interrupted()
        before = self._alpha_bytes()
        real_replace = landing_mod._replace_artifact
        replaced: list[str] = []

        def replace(root: Path, staging: Path, artifact: ArtifactTarget) -> None:
            replaced.append(artifact.path)
            real_replace(root, staging, artifact)

        with mock.patch.object(landing_mod, "_replace_artifact", side_effect=replace):
            _must_succeed(self, landing_mod.resume_landing, self.root, LAND_SURFACE)
        self.assertEqual(self._alpha_bytes(), before, "a landed consumer is never rewritten")
        self.assertEqual([p for p in replaced if _consumer_of(p) == "alpha"], [])
        self.assertTrue(replaced, "beta and gamma must have been published")
        for consumer_plan in plan.journal.consumers:
            for artifact in consumer_plan.artifacts:
                path = self.root / artifact.path
                current = sha256_hex(path.read_bytes()) if path.exists() else None
                self.assertEqual(current, artifact.new_sha256, artifact.path)
        self.assertEqual(
            [e["landing_id"] for e in landed_events(self.root)], [plan.journal.landing_id]
        )
        self.assertFalse(journal_path(self.root, LAND_SURFACE).exists())

    @covers("REQ-0.35.0-07-08")
    def test_resume_reuses_the_recorded_attestation_and_landing_id(self) -> None:
        plan = self._interrupted()
        resumed = _must_succeed(self, landing_mod.resume_landing, self.root, LAND_SURFACE)
        self.assertEqual(resumed.landing_id, plan.journal.landing_id)
        for consumer in LAND_CONSUMERS:
            sidecar = load_fingerprint(self.root, LAND_SURFACE, consumer)
            assert sidecar is not None
            self.assertEqual(
                (sidecar.landing_id, sidecar.attestor, sidecar.attestation_text),
                (plan.journal.landing_id, "g0", "delta attested"),
            )
        self.assertEqual(landed_events(self.root)[0]["attestation_text"], "delta attested")

    @covers("REQ-0.35.0-07-08")
    def test_resume_after_event_before_cleanup_records_no_second_event(self) -> None:
        build_land_project(self.root)
        plan = prepare_landing(
            self.root, LAND_SURFACE, attestor="g0", attestation_text="delta attested"
        )
        with (
            mock.patch.object(landing_mod, "_clear_landing", side_effect=OSError("crash")),
            contextlib.suppress(LandingRefusal),
        ):
            publish_landing(self.root, plan)
        _must_succeed(self, landing_mod.resume_landing, self.root, LAND_SURFACE)
        self.assertEqual(len(landed_events(self.root)), 1)
        self.assertFalse(journal_path(self.root, LAND_SURFACE).exists())

    @covers("REQ-0.35.0-07-08")
    def test_resume_after_crash_before_event_completes_from_verified(self) -> None:
        build_land_project(self.root)
        plan = prepare_landing(
            self.root, LAND_SURFACE, attestor="g0", attestation_text="delta attested"
        )
        with (
            mock.patch.object(landing_mod, "emit_rendition_landed", side_effect=OSError("crash")),
            contextlib.suppress(LandingRefusal),
        ):
            publish_landing(self.root, plan)
        _must_succeed(self, landing_mod.resume_landing, self.root, LAND_SURFACE)
        self.assertEqual(len(landed_events(self.root)), 1)
        self.assertFalse(journal_path(self.root, LAND_SURFACE).exists())

    def _assert_refused_writing_nothing(self) -> LandingRefusal:
        before = committed_artifacts(snapshot_tree(self.root))
        refusal = self._refused()
        self.assertEqual(refusal.exit_code, 1)
        self.assertEqual(committed_artifacts(snapshot_tree(self.root)), before)
        self.assertEqual(landed_events(self.root), [])
        for part in ("Error:", "Why forbidden:", "Next:"):
            self.assertIn(part, refusal.message)
        return refusal

    @covers("REQ-0.35.0-07-07")
    def test_corpus_drift_after_interruption_refuses(self) -> None:
        self._interrupted()
        append_entry(
            self.root,
            LAND_SURFACE,
            CorpusEntry(
                id="e-late",
                surface=LAND_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="late rule text.",
                origin="test",
                ts="2026-09-27T00:00:00Z",
            ),
        )
        refusal = self._assert_refused_writing_nothing()
        self.assertIn("corpus", refusal.message)

    @covers("REQ-0.35.0-07-07")
    def test_externally_edited_artifact_at_neither_hash_refuses(self) -> None:
        plan = self._interrupted()
        (self.root / artifact_relpath(LAND_SURFACE, "gamma", "rendition")).write_bytes(b"hand\n")
        refusal = self._assert_refused_writing_nothing()
        self.assertIn("gamma.md", refusal.message)
        self.assertIn(f"--status {plan.journal.landing_id}", refusal.message)

    @covers("REQ-0.35.0-07-07")
    def test_deleted_staged_file_refuses(self) -> None:
        plan = self._interrupted()
        staging = landing_mod.staging_path(self.root, LAND_SURFACE, plan.journal.landing_id)
        (staging / "beta.md").unlink()
        refusal = self._assert_refused_writing_nothing()
        self.assertIn("beta.md", refusal.message)

    @covers("REQ-0.35.0-07-07")
    def test_malformed_journal_refuses(self) -> None:
        self._interrupted()
        journal_path(self.root, LAND_SURFACE).write_bytes(b"{not a journal")
        self._assert_refused_writing_nothing()

    @covers("REQ-0.35.0-07-07")
    def test_journal_naming_another_surface_refuses(self) -> None:
        self._interrupted()
        path = journal_path(self.root, LAND_SURFACE)
        document = json.loads(path.read_text(encoding="utf-8"))
        document["surface"] = "Other.md"
        for consumer in document["consumers"]:
            for artifact in consumer["artifacts"]:
                artifact["path"] = artifact["path"].replace(LAND_SURFACE, "Other.md")
        path.write_bytes(json.dumps(document).encode("utf-8"))
        self._assert_refused_writing_nothing()


class _HardKill(BaseException):
    """A process kill: unlike OSError, nothing in the landing gets to clean up."""


class TestResumeAfterKillMidStaging(_TempRoot):
    """REQ-0.35.0-07-08: a landing killed while staging resumes without a new attestation."""

    def _killed_while_staging(self, *, after_files: int) -> LandingPlan:
        build_land_project(self.root)
        plan = prepare_landing(
            self.root, LAND_SURFACE, attestor="g0", attestation_text="delta attested"
        )
        real_stage = landing_mod._stage_artifact
        staged: list[Path] = []

        def stage(path: Path, data: bytes) -> None:
            if len(staged) == after_files:
                raise _HardKill
            real_stage(path, data)
            staged.append(path)

        with (
            mock.patch.object(landing_mod, "_stage_artifact", side_effect=stage),
            contextlib.suppress(_HardKill),
        ):
            publish_landing(self.root, plan)
        journal = load_journal(self.root, LAND_SURFACE)
        assert journal is not None
        self.assertEqual(journal.phase, "prepared")
        return plan

    def _assert_completed_with_recorded_attestation(self, plan: LandingPlan) -> None:
        for consumer in LAND_CONSUMERS:
            sidecar = load_fingerprint(self.root, LAND_SURFACE, consumer)
            assert sidecar is not None
            self.assertEqual(
                (sidecar.landing_id, sidecar.attestor, sidecar.attestation_text),
                (plan.journal.landing_id, "g0", "delta attested"),
            )
        for consumer_plan in plan.journal.consumers:
            for artifact in consumer_plan.artifacts:
                path = self.root / artifact.path
                current = sha256_hex(path.read_bytes()) if path.exists() else None
                self.assertEqual(current, artifact.new_sha256, artifact.path)
        self.assertEqual(
            [e["landing_id"] for e in landed_events(self.root)], [plan.journal.landing_id]
        )
        self.assertFalse(journal_path(self.root, LAND_SURFACE).exists())

    @covers("REQ-0.35.0-07-08")
    def test_kill_right_after_the_journal_resumes_without_attestation(self) -> None:
        plan = self._killed_while_staging(after_files=0)
        _must_succeed(self, landing_mod.resume_landing, self.root, LAND_SURFACE)
        self._assert_completed_with_recorded_attestation(plan)

    @covers("REQ-0.35.0-07-08")
    def test_kill_after_one_staged_file_resumes_without_attestation(self) -> None:
        plan = self._killed_while_staging(after_files=1)
        _must_succeed(self, landing_mod.resume_landing, self.root, LAND_SURFACE)
        self._assert_completed_with_recorded_attestation(plan)

    @covers("REQ-0.35.0-07-08")
    def test_regenerated_bytes_that_disagree_with_the_journal_refuse(self) -> None:
        self._killed_while_staging(after_files=1)
        real_generate = landing_mod._generate_and_verify

        def generate(root: Path, surface: str, consumer: str):  # noqa: ANN202
            generated = real_generate(root, surface, consumer)
            return generated.model_copy(
                update={"candidate_text": generated.candidate_text + "drifted\n"}
            )

        before = committed_artifacts(snapshot_tree(self.root))
        with (
            mock.patch.object(landing_mod, "_generate_and_verify", side_effect=generate),
            self.assertRaises(LandingRefusal) as ctx,
        ):
            landing_mod.resume_landing(self.root, LAND_SURFACE)
        refusal = ctx.exception
        self.assertEqual(refusal.exit_code, 1)
        self.assertEqual(committed_artifacts(snapshot_tree(self.root)), before)
        self.assertEqual(landed_events(self.root), [])
        for part in ("Error:", "Why forbidden:", "Next:"):
            self.assertIn(part, refusal.message)


_RETENTION_TEXT = '{"surface": "LandSurface.md", "consumer": "alpha"}\n'


def _journal_with_retention(new_sha256: str | None, payload: str | None) -> dict:
    document = _journal()
    consumer = document["consumers"][0]
    consumer["artifacts"].append(
        {
            "kind": "retention",
            "path": f".gzkit/renditions/{LAND_SURFACE}/alpha.retention.json",
            "old_sha256": None if new_sha256 is not None else _SHA,
            "new_sha256": new_sha256,
        }
    )
    consumer["retention_payload"] = payload
    return document


class TestJournalRetentionPayload(unittest.TestCase):
    """REQ-0.35.0-07-08: the journal records the reviewed retention sidecar, honestly."""

    @covers("REQ-0.35.0-07-08")
    def test_recorded_payload_hashing_to_new_sha256_is_accepted(self) -> None:
        digest = sha256_hex(_RETENTION_TEXT.encode("utf-8"))
        journal = LandingJournal.model_validate(_journal_with_retention(digest, _RETENTION_TEXT))
        self.assertEqual(journal.consumers[0].retention_payload, _RETENTION_TEXT)

    @covers("REQ-0.35.0-07-08")
    def test_payload_not_matching_new_sha256_or_on_a_removal_is_malformed(self) -> None:
        for new_sha256, payload in ((_SHA, _RETENTION_TEXT), (None, _RETENTION_TEXT)):
            with (
                self.subTest(new_sha256=new_sha256),
                self.assertRaises(ValidationError),
            ):
                LandingJournal.model_validate(_journal_with_retention(new_sha256, payload))


class TestResumeRetentionLandingAfterKill(_TempRoot):
    """REQ-0.35.0-07-08: a retention landing killed before staging resumes byte-for-byte."""

    @covers("REQ-0.35.0-07-08")
    def test_retention_sidecar_is_rebuilt_from_the_journal_on_resume(self) -> None:
        build_land_project(self.root, prior_text=LAND_PRIOR_WITH_DOOMED)
        maps = {c: write_dropped_map(self.root, c) for c in LAND_CONSUMERS}
        plan = prepare_landing(
            self.root,
            LAND_SURFACE,
            attestor="g0",
            attestation_text="C1 drop accepted",
            retention_maps=[path.as_posix() for path in maps.values()],
        )
        with (
            mock.patch.object(landing_mod, "_stage_artifact", side_effect=_HardKill),
            contextlib.suppress(_HardKill),
        ):
            publish_landing(self.root, plan)
        _must_succeed(self, landing_mod.resume_landing, self.root, LAND_SURFACE)
        for consumer, map_path in maps.items():
            reviewed = RetentionMap.model_validate_json(map_path.read_text(encoding="utf-8"))
            published = retention_path(self.root, LAND_SURFACE, consumer).read_bytes()
            self.assertEqual(published, (reviewed.model_dump_json() + "\n").encode("utf-8"))
        self.assertEqual(
            [e["landing_id"] for e in landed_events(self.root)], [plan.journal.landing_id]
        )
