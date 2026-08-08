"""Foundation Sunset migration executor (ADR-0.34.0, OBPI-04).

The load-bearing claim is *partition by Layer-2 ledger truth, never by
frontmatter*. The ADR-0.0.37 investigation proved frontmatter can lie about
repudiated OBPIs, so a foundation wearing the most terminal-looking frontmatter
available (``status: Validated``) must still demote when the ledger shows zero
completed OBPIs. That negative control is the test that would catch a
frontmatter-reading regression; the happy path would not.

Each test builds its own isolated project root. None reads the real
repository's foundation set, manifest, or ledger.
"""

from __future__ import annotations

import inspect
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from gzkit.commands.ontology import compute_seams
from gzkit.config import GzkitConfig
from gzkit.events import parse_typed_event
from gzkit.foundation.sunset_migrate import (
    anchor_integrity,
    build_manifest_entries,
    check_blockers,
    compute_partition,
    graph_probe,
    interrupted_demotions,
    main,
    rename_integrity,
    rename_map,
    run_migration,
)
from gzkit.ledger import Ledger, adr_created_event
from gzkit.ledger_events import (
    artifact_renamed_event,
    audit_receipt_emitted_event,
    foundation_grandfathered_event,
    obpi_completion_repudiated_event,
    obpi_created_event,
    obpi_receipt_emitted_event,
    obpi_superseded_event,
)
from gzkit.models.foundation_grandfather import FoundationGrandfatherManifest
from gzkit.ontology.graph import OntologyGraph
from gzkit.ontology.model import (
    LinkType,
    ObjectType,
    OntologyEdge,
    OntologyNode,
    Ownership,
    Plane,
    Provenance,
)
from gzkit.traceability import covers
from gzkit.validate_pkg.ledger_check import validate_ledger
from tests.commands.common import CliRunner, _quick_init

_FOUNDATION_ADR = """---
id: {adr_id}
status: {status}
kind: foundation
semver: {semver}
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-01
---

# {adr_id}: {title}

## Intent

{body_marker} intent prose that must survive demotion verbatim.

## Decision

{body_marker} decision prose with a distinctive marker.
"""

_OBPI_BRIEF = """---
id: {obpi_id}
parent: {adr_id}
lane: heavy
status: Draft
---

# {obpi_id}: Sample
"""


def _seed_foundation(
    config: GzkitConfig,
    adr_id: str,
    semver: str,
    *,
    status: str = "Pending",
    title: str = "Sample Foundation",
    body_marker: str = "DISTINCTIVE",
    brief_count: int = 0,
) -> Path:
    """Write a ``kind: foundation`` ADR package with ``brief_count`` child briefs."""
    pkg = Path(config.paths.adrs) / "foundation" / adr_id
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / f"{adr_id}.md").write_text(
        _FOUNDATION_ADR.format(
            adr_id=adr_id, semver=semver, status=status, title=title, body_marker=body_marker
        ),
        encoding="utf-8",
    )
    if brief_count:
        (pkg / "obpis").mkdir(exist_ok=True)
        for idx in range(1, brief_count + 1):
            obpi_id = f"OBPI-{semver}-{idx:02d}-sample"
            (pkg / "obpis" / f"{obpi_id}.md").write_text(
                _OBPI_BRIEF.format(obpi_id=obpi_id, adr_id=adr_id), encoding="utf-8"
            )
    return pkg


def _child_obpi_ids(semver: str, count: int) -> list[str]:
    return [f"OBPI-{semver}-{idx:02d}-sample" for idx in range(1, count + 1)]


def _seed_ledger(
    ledger: Ledger, adr_id: str, semver: str, *, briefs: int = 0, completed: int = 0
) -> None:
    """Register the ADR and its OBPI children, completing the first ``completed``."""
    ledger.append(adr_created_event(adr_id, "", "heavy"))
    ids = _child_obpi_ids(semver, briefs)
    for obpi_id in ids:
        ledger.append(obpi_created_event(obpi_id, parent=adr_id))
    for obpi_id in ids[:completed]:
        ledger.append(
            obpi_receipt_emitted_event(
                obpi_id,
                receipt_event="attested_completed",
                attestor="g0",
                parent_adr=adr_id,
                obpi_completion="attested_completed",
            )
        )


class TestPartitionReadsLedgerNotFrontmatter(unittest.TestCase):
    """The partition is computed from Layer-2, so frontmatter cannot steer it."""

    def test_validated_frontmatter_with_zero_completions_still_demotes(self) -> None:
        """A foundation may CLAIM terminality in frontmatter; only the ledger proves it.

        This is the negative control for the whole migration. ``status: Validated``
        is the most terminal-looking frontmatter available. If the partition ever
        starts trusting it, this foundation silently stays grandfathered while
        holding no completed work -- exactly the frontmatter-lie failure class
        ADR-0.0.37 exposed.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.90-liar", "0.0.90", status="Validated", brief_count=3)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.90-liar", "0.0.90", briefs=3, completed=0)

            partition = compute_partition(Path.cwd(), ledger)

            self.assertEqual(
                [row.id for row in partition.demote],
                ["ADR-0.0.90-liar"],
                "a foundation with zero ledger-completed OBPIs must demote regardless "
                "of a Validated frontmatter claim",
            )
            self.assertEqual([row.id for row in partition.grandfather], [])

    def test_draft_frontmatter_with_one_completion_is_grandfathered(self) -> None:
        """The converse: real attested work is never discarded to tidy the partition."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.91-worker", "0.0.91", status="Draft", brief_count=3)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.91-worker", "0.0.91", briefs=3, completed=1)

            partition = compute_partition(Path.cwd(), ledger)

            self.assertEqual(
                [row.id for row in partition.grandfather],
                ["ADR-0.0.91-worker"],
                "one completed OBPI is enough to grandfather -- no foundation holding "
                "attested work may be pooled",
            )
            self.assertEqual([row.id for row in partition.demote], [])

    def test_partition_carries_h1_title_not_frontmatter(self) -> None:
        """ADR frontmatter has no title key; the H1 after the colon is the source."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.92-titled", "0.0.92", title="Distinct Title Here")
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.92-titled", "0.0.92")

            partition = compute_partition(Path.cwd(), ledger)

            rows = partition.demote + partition.grandfather
            self.assertEqual([row.title for row in rows], ["Distinct Title Here"])


@patch("gzkit.foundation.sunset_migrate._SUNSET_PREREQUISITES", ())
class TestDemotionPreservesBody(unittest.TestCase):
    """REQ-0.34.0-04-01 -- demotion is body-preserving."""

    @covers("REQ-0.34.0-04-01")
    def test_pool_file_retains_adr_body_verbatim_below_the_h1(self) -> None:
        """The pooled ADR keeps its Intent/Decision prose byte-for-byte.

        Demotion is a re-homing, not a rewrite: a foundation demoted to pool must
        remain re-promotable as a feature later, which requires its design content
        to survive intact. The taxonomy frontmatter changes, and so does the H1's
        id token — it is a second statement of the ``id:`` this migration
        rewrites, not design content (GHI #776).

        The assertion stays byte-for-byte over the whole body rather than
        excluding the heading, so it can still fail if demotion mangles the H1.
        Excluding the line would have bought the new behavior by making the test
        blind to it.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pkg = _seed_foundation(config, "ADR-0.0.93-body", "0.0.93", body_marker="KEEPME")
            source = (pkg / "ADR-0.0.93-body.md").read_text(encoding="utf-8")
            source_body = source.split("\n---\n", 1)[1]
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.93-body", "0.0.93")

            run_migration(
                project_root=Path.cwd(),
                receipt_dir=Path("artifacts/receipts"),
                dry_run=False,
                attestor="g0",
                attestation="test attestation",
            )

            pool_file = Path(config.paths.adrs) / "pool" / "ADR-pool.body.md"
            self.assertTrue(pool_file.is_file(), "demotion must produce the pool file")
            pooled = pool_file.read_text(encoding="utf-8")
            expected_body = source_body.replace("# ADR-0.0.93-body:", "# ADR-pool.body:", 1)
            self.assertNotEqual(
                expected_body, source_body, "the fixture must carry an H1 to rewrite"
            )
            self.assertEqual(
                pooled.split("\n---\n", 1)[1],
                expected_body,
                "the ADR body must survive demotion byte-for-byte below the H1, "
                "whose id token becomes the pool id",
            )

    @covers("REQ-0.34.0-04-01")
    def test_frontmatter_strips_taxonomy_keys_and_preserves_the_rest(self) -> None:
        """Exactly kind/semver/date leave; id/status are rewritten; others persist."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.94-fm", "0.0.94")
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.94-fm", "0.0.94")

            run_migration(
                project_root=Path.cwd(),
                receipt_dir=Path("artifacts/receipts"),
                dry_run=False,
                attestor="g0",
                attestation="test attestation",
            )

            pooled = (Path(config.paths.adrs) / "pool" / "ADR-pool.fm.md").read_text(
                encoding="utf-8"
            )
            head = pooled.split("\n---\n", 1)[0]
            self.assertNotIn("kind:", head)
            self.assertNotIn("semver:", head)
            self.assertNotIn("date:", head)
            self.assertIn("id: ADR-pool.fm", head)
            self.assertIn("status: Pool", head)
            self.assertIn("lane: heavy", head)
            self.assertIn("parent: PRD-GZKIT-1.0.0", head)


@patch("gzkit.foundation.sunset_migrate._SUNSET_PREREQUISITES", ())
class TestDemotionBlastRadius(unittest.TestCase):
    """The demote verb deletes the source package; pin that so it cannot surprise."""

    def test_source_package_is_removed_and_children_are_parked(self) -> None:
        """Demotion removes the package (briefs included) and parks each child OBPI.

        ``_apply_demote`` rmtree's the source directory, so the demoted
        foundation's OBPI briefs are destroyed. That is the verb's deliberate
        design -- lineage survives as one ``obpi_parked`` event per child, and
        parking is reversible on re-promotion. Asserting it here means the blast
        radius is a documented contract rather than a discovery in a diff.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pkg = _seed_foundation(config, "ADR-0.0.95-radius", "0.0.95", brief_count=4)
            self.assertEqual(len(list((pkg / "obpis").glob("OBPI-*.md"))), 4)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.95-radius", "0.0.95", briefs=4, completed=0)

            receipt = run_migration(
                project_root=Path.cwd(),
                receipt_dir=Path("artifacts/receipts"),
                dry_run=False,
                attestor="g0",
                attestation="test attestation",
            )

            self.assertFalse(pkg.exists(), "the source package directory is removed")
            events = [
                json.loads(line)
                for line in Path(config.paths.ledger).read_text(encoding="utf-8").splitlines()
                if line
            ]
            parked = {e["id"] for e in events if e.get("event") == "obpi_parked"}
            self.assertEqual(parked, set(_child_obpi_ids("0.0.95", 4)))
            self.assertEqual(
                receipt["deleted_brief_count"],
                4,
                "the receipt must account for every brief the demotion deleted",
            )

    def test_dry_run_deletes_nothing(self) -> None:
        """The preview path must be inert -- it is the review surface before --apply."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pkg = _seed_foundation(config, "ADR-0.0.96-inert", "0.0.96", brief_count=2)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.96-inert", "0.0.96", briefs=2, completed=0)
            before = Path(config.paths.ledger).read_text(encoding="utf-8")

            receipt = run_migration(
                project_root=Path.cwd(),
                receipt_dir=Path("artifacts/receipts"),
                dry_run=True,
            )

            self.assertTrue(pkg.exists(), "dry-run must not remove the source package")
            self.assertEqual(
                Path(config.paths.ledger).read_text(encoding="utf-8"),
                before,
                "dry-run must not append any ledger event",
            )
            self.assertTrue(receipt["dry_run"])
            self.assertFalse(
                Path("data/foundation_grandfather.json").exists(),
                "dry-run must not populate the manifest",
            )


class TestManifestIsIdentityOnly(unittest.TestCase):
    """Lifecycle must be read live from Layer-2, never baked into Layer-1."""

    def test_entries_carry_exactly_the_four_identity_keys(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.97-keys", "0.0.97", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.97-keys", "0.0.97", briefs=1, completed=1)

            entries = build_manifest_entries(compute_partition(Path.cwd(), ledger), "2026-07-29")

            self.assertEqual(len(entries), 1)
            self.assertEqual(set(entries[0]), {"id", "title", "semver", "frozen_at"})
            self.assertEqual(entries[0]["id"], "ADR-0.0.97-keys")
            self.assertEqual(entries[0]["frozen_at"], "2026-07-29")
            FoundationGrandfatherManifest.model_validate(entries[0])

    def test_a_lifecycle_field_is_rejected_by_the_model(self) -> None:
        """extra=forbid is the mechanism that keeps Layer-2 facts out of Layer-1."""
        with self.assertRaises(Exception) as ctx:
            FoundationGrandfatherManifest.model_validate(
                {
                    "id": "ADR-0.0.98-x",
                    "title": "X",
                    "semver": "0.0.98",
                    "frozen_at": "2026-07-29",
                    "lifecycle": "Validated",
                }
            )
        self.assertIn("lifecycle", str(ctx.exception))


@patch("gzkit.foundation.sunset_migrate._SUNSET_PREREQUISITES", ())
class TestGrandfatheredEventsAreEmittedPerEntry(unittest.TestCase):
    """REQ-0.34.0-04-02 support surface -- one witness per manifest entry."""

    def test_one_event_per_entry_with_the_slugged_id(self) -> None:
        """The terminal-partition gate matches manifest ids against event ids exactly.

        A bare-semver id here would leave every grandfathered foundation reading
        as limbo the instant OBPI-05 wires the gate.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            for idx, semver in ((1, "0.0.81"), (2, "0.0.82")):
                _seed_foundation(config, f"ADR-{semver}-kept{idx}", semver, brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            for idx, semver in ((1, "0.0.81"), (2, "0.0.82")):
                _seed_ledger(ledger, f"ADR-{semver}-kept{idx}", semver, briefs=1, completed=1)

            run_migration(
                project_root=Path.cwd(),
                receipt_dir=Path("artifacts/receipts"),
                dry_run=False,
                attestor="g0",
                attestation="test attestation",
            )

            events = [
                json.loads(line)
                for line in Path(config.paths.ledger).read_text(encoding="utf-8").splitlines()
                if line
            ]
            witnessed = [e for e in events if e.get("event") == "foundation_grandfathered"]
            self.assertEqual(
                {e["id"] for e in witnessed},
                {"ADR-0.0.81-kept1", "ADR-0.0.82-kept2"},
                "one witness per manifest entry, keyed by the full slugged id",
            )
            self.assertTrue(all(e.get("attestor") == "g0" for e in witnessed))
            manifest = json.loads(
                Path("data/foundation_grandfather.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                {entry["id"] for entry in manifest},
                {e["id"] for e in witnessed},
                "the manifest and the witness set must be a bijection",
            )

    def test_golden_fixture_is_written_byte_identical(self) -> None:
        """The tamper guard is a byte comparison, so the fixture moves with the data."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.83-gold", "0.0.83", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.83-gold", "0.0.83", briefs=1, completed=1)
            golden = Path("tests/governance/fixtures/foundation_grandfather_golden.json")
            golden.parent.mkdir(parents=True, exist_ok=True)
            golden.write_text("[]\n", encoding="utf-8")

            run_migration(
                project_root=Path.cwd(),
                receipt_dir=Path("artifacts/receipts"),
                dry_run=False,
                attestor="g0",
                attestation="test attestation",
            )

            self.assertEqual(
                golden.read_text(encoding="utf-8"),
                Path("data/foundation_grandfather.json").read_text(encoding="utf-8"),
                "manifest and golden fixture must be byte-identical or the guard fails",
            )


class TestEveryTerminalNegationCountsAsUnstarted(unittest.TestCase):
    """Adversarial finding #2 -- the negation set is TERMINAL_EVENTS, not a subset.

    ``obpi_superseded`` is in ``obpi_lifecycle.TERMINAL_EVENTS``, but the graph's
    supersession applier sets ``superseded=True`` WITHOUT clearing
    ``ledger_completed``. A tally that excludes only withdrawn/repudiated
    therefore counts a permanently-superseded completion as live work and
    grandfathers a foundation whose only completion was negated -- silently
    sparing a package that should have been pooled.
    """

    def test_completed_then_superseded_does_not_grandfather(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.70-superseded", "0.0.70", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.70-superseded", "0.0.70", briefs=1, completed=1)
            ledger.append(
                obpi_superseded_event(
                    "OBPI-0.0.70-01-sample",
                    parent="ADR-0.0.70-superseded",
                    superseded_by="OBPI-0.0.70-02-sample",
                    rationale="test supersession",
                    attestor="g0",
                )
            )

            partition = compute_partition(Path.cwd(), ledger)

            self.assertEqual(
                [row.id for row in partition.demote],
                ["ADR-0.0.70-superseded"],
                "a completion that was later SUPERSEDED is negated work -- the "
                "foundation holds no live completion and must demote",
            )

    def test_completed_then_repudiated_does_not_grandfather(self) -> None:
        """The sibling negation, pinned so the pair cannot regress independently."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.71-repudiated", "0.0.71", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.71-repudiated", "0.0.71", briefs=1, completed=1)
            ledger.append(
                obpi_completion_repudiated_event(
                    "OBPI-0.0.71-01-sample",
                    "ADR-0.0.71-repudiated",
                    "receipt-0001",
                    "model-induced-fabrication",
                    "g0",
                    "fabricated attestation",
                )
            )

            partition = compute_partition(Path.cwd(), ledger)

            self.assertEqual([row.id for row in partition.demote], ["ADR-0.0.71-repudiated"])


class TestReversibleDispositionsAreNotPermanent(unittest.TestCase):
    """Adversarial pass-2 finding #2 -- repudiation is REVERSIBLE (ADR-0.0.71).

    ``TERMINAL_EVENTS`` answers "did a terminal event ever occur?"; the partition
    needs "is this child terminal NOW?". Reading the ever-seen set pools a
    foundation whose only work was genuinely re-completed -- destroying real work
    to tidy the partition, which the parent ADR forbids outright.
    """

    def test_repudiated_then_genuinely_recompleted_is_grandfathered(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.68-recompleted", "0.0.68", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.68-recompleted", "0.0.68", briefs=1, completed=1)
            ledger.append(
                obpi_completion_repudiated_event(
                    "OBPI-0.0.68-01-sample",
                    "ADR-0.0.68-recompleted",
                    "receipt-0001",
                    "model-induced-fabrication",
                    "g0",
                    "fabricated attestation",
                )
            )
            # Genuine re-attestation CLEARS repudiated (governance-core.md
            # § Withdraw vs Repudiate: "Re-completable? Yes").
            ledger.append(
                obpi_receipt_emitted_event(
                    "OBPI-0.0.68-01-sample",
                    receipt_event="attested_completed",
                    attestor="g0",
                    parent_adr="ADR-0.0.68-recompleted",
                    obpi_completion="attested_completed",
                )
            )

            partition = compute_partition(Path.cwd(), ledger)

            self.assertEqual(
                [row.id for row in partition.grandfather],
                ["ADR-0.0.68-recompleted"],
                "a genuinely re-completed OBPI is live work -- reading the ever-seen "
                "terminal set would pool this foundation and delete it",
            )
            self.assertEqual([row.id for row in partition.demote], [])


@patch("gzkit.foundation.sunset_migrate._SUNSET_PREREQUISITES", ("ADR-0.0.37",))
class TestUnrelatedAuditReceiptsAreNotCloseout(unittest.TestCase):
    """Adversarial pass-2 finding #4 -- not every audit receipt is a closeout."""

    def test_a_meta_receipt_does_not_satisfy_a_prerequisite(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.37-prereq", "0.0.37", brief_count=2)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.37-prereq", "0.0.37", briefs=2, completed=2)
            ledger.append(
                audit_receipt_emitted_event(
                    "ADR-0.0.37-prereq", receipt_event="meta-receipt-bind", attestor="g0"
                )
            )

            blockers = check_blockers(Path.cwd(), ledger)

            self.assertTrue(
                any("closeout witness" in b for b in blockers),
                f"a non-`validated` receipt must not read as closeout; got {blockers}",
            )

    def test_a_validated_receipt_does_satisfy_a_prerequisite(self) -> None:
        """The converse, so the predicate is not merely refusing everything."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.37-prereq", "0.0.37", brief_count=2)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.37-prereq", "0.0.37", briefs=2, completed=2)
            ledger.append(
                audit_receipt_emitted_event(
                    "ADR-0.0.37-prereq", receipt_event="validated", attestor="g0"
                )
            )

            self.assertEqual(check_blockers(Path.cwd(), ledger), [])


class TestWitnessFactoryRefusesFabrication(unittest.TestCase):
    """Adversarial pass-2 finding #5 -- the factory itself must not be forgeable."""

    def test_factory_refuses_an_empty_attestor(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            foundation_grandfathered_event(
                adr_id="ADR-0.0.9-x", title="X", semver="0.0.9", frozen_at="2026-07-29", attestor=""
            )
        self.assertIn("attestor", str(ctx.exception).lower())

    def test_factory_refuses_a_whitespace_attestor(self) -> None:
        with self.assertRaises(ValueError):
            foundation_grandfathered_event(
                adr_id="ADR-0.0.9-x",
                title="X",
                semver="0.0.9",
                frozen_at="2026-07-29",
                attestor="   ",
            )


@patch("gzkit.foundation.sunset_migrate._SUNSET_PREREQUISITES", ())
class TestInterruptedDemotionIsDetected(unittest.TestCase):
    """Adversarial pass-2 finding #6 -- the GHI #520 stranding signature.

    ``_apply_demote`` writes the pool file, rmtree's the source, THEN appends the
    rename and parking events. A crash in that window leaves the old ADR node
    live in Layer-2 with unparked children pointing at a parent id that no longer
    resolves -- the exact 237-record stranding GHI #520 recorded. A bare retry
    cannot see it: the vanished package is absent from the partition, so the
    migration recomputes over the reduced tree and reports clean success.
    """

    def test_a_journaled_demotion_with_no_rename_event_blocks_the_retry(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            ledger = Ledger(Path(config.paths.ledger))
            # Simulate the crash window: journal names a demotion, the package is
            # gone, and no artifact_renamed event was ever appended.
            journal = Path("artifacts/receipts/foundation-sunset-journal.json")
            journal.parent.mkdir(parents=True, exist_ok=True)
            journal.write_text(
                json.dumps(
                    {"demotions": [{"source_id": "ADR-0.0.67-lost", "package": "ADR-0.0.67-lost"}]}
                ),
                encoding="utf-8",
            )

            stranded = interrupted_demotions(Path.cwd(), ledger)

            self.assertTrue(
                any("ADR-0.0.67-lost" in s for s in stranded),
                f"an interrupted demotion must be named, not silently recomputed; got {stranded}",
            )
            self.assertTrue(
                any("no `artifact_renamed` event" in s for s in stranded),
                "the blocker must name the stranding signature, not just the id",
            )

    def test_apply_refuses_while_a_stranded_demotion_is_outstanding(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.66-ok", "0.0.66", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.66-ok", "0.0.66", briefs=1, completed=1)
            journal = Path("artifacts/receipts/foundation-sunset-journal.json")
            journal.parent.mkdir(parents=True, exist_ok=True)
            journal.write_text(
                json.dumps(
                    {"demotions": [{"source_id": "ADR-0.0.67-lost", "package": "ADR-0.0.67-lost"}]}
                ),
                encoding="utf-8",
            )

            with self.assertRaises(RuntimeError) as ctx:
                run_migration(
                    project_root=Path.cwd(),
                    receipt_dir=Path("artifacts/receipts"),
                    dry_run=False,
                    attestor="g0",
                    attestation="attest completed",
                )
            self.assertIn("ADR-0.0.67-lost", str(ctx.exception))

    def test_a_completed_apply_discharges_the_journal(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.64-gone", "0.0.64", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.64-gone", "0.0.64", briefs=1, completed=0)

            run_migration(
                project_root=Path.cwd(),
                receipt_dir=Path("artifacts/receipts"),
                dry_run=False,
                attestor="g0",
                attestation="attest completed",
            )

            self.assertFalse(
                Path("artifacts/receipts/foundation-sunset-journal.json").exists(),
                "a fully applied migration must discharge its write-ahead journal",
            )


class TestIdentityIncoherenceFailsClosed(unittest.TestCase):
    """Adversarial finding #3 -- a silent skip in front of a destructive loop.

    Frontmatter ``id`` is the load-bearing ledger join. Skipping a package whose
    id is missing means it never appears in the partition at all: it is neither
    demoted nor grandfathered, so the closed-kind gate keeps flagging it while
    the migration reports success. Silence in front of an rmtree loop is the
    failure mode, not the missing key.
    """

    def test_package_without_a_readable_id_raises(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pkg = Path(config.paths.adrs) / "foundation" / "ADR-0.0.99-nameless"
            pkg.mkdir(parents=True, exist_ok=True)
            (pkg / "ADR-0.0.99-nameless.md").write_text(
                "---\nstatus: Draft\nkind: foundation\nsemver: 0.0.99\n---\n\n# No id key\n",
                encoding="utf-8",
            )
            ledger = Ledger(Path(config.paths.ledger))

            with self.assertRaises(RuntimeError) as ctx:
                compute_partition(Path.cwd(), ledger)

            self.assertIn("ADR-0.0.99-nameless", str(ctx.exception))

    def test_frontmatter_id_disagreeing_with_its_package_raises(self) -> None:
        """The data-loss path: a mismatched id resolves the ledger join elsewhere.

        With ledger completions recorded under the package's REAL id but
        frontmatter renamed, the tally reads zero and the package -- holding
        attested work -- is destructively pooled. Counting rows cannot catch this;
        only comparing identities can.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pkg = _seed_foundation(config, "ADR-0.0.63-real", "0.0.63", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.63-real", "0.0.63", briefs=1, completed=1)
            # Point frontmatter at an id the ledger knows nothing about.
            adr_file = pkg / "ADR-0.0.63-real.md"
            adr_file.write_text(
                adr_file.read_text(encoding="utf-8").replace(
                    "id: ADR-0.0.63-real", "id: ADR-0.0.99-wrong"
                ),
                encoding="utf-8",
            )

            with self.assertRaises(RuntimeError) as ctx:
                compute_partition(Path.cwd(), ledger)

            message = str(ctx.exception)
            self.assertIn("ADR-0.0.99-wrong", message)
            self.assertIn("package directory", message)
            self.assertTrue(pkg.exists(), "the package must survive a refused partition")

    def test_an_id_with_no_ledger_graph_node_raises(self) -> None:
        """Zero completions for want of ledger presence is not zero completions."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.62-unledgered", "0.0.62", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))  # deliberately no adr_created

            with self.assertRaises(RuntimeError) as ctx:
                compute_partition(Path.cwd(), ledger)

            self.assertIn("no Layer-2 graph node", str(ctx.exception))

    def test_partition_is_a_bijection_with_on_disk_packages(self) -> None:
        """Every package lands in exactly one side -- none silently vanishes."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.86-a", "0.0.86", brief_count=1)
            _seed_foundation(config, "ADR-0.0.87-b", "0.0.87", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.86-a", "0.0.86", briefs=1, completed=0)
            _seed_ledger(ledger, "ADR-0.0.87-b", "0.0.87", briefs=1, completed=1)

            partition = compute_partition(Path.cwd(), ledger)

            on_disk = {
                p.name for p in (Path(config.paths.adrs) / "foundation").iterdir() if p.is_dir()
            }
            accounted = {row.package.name for row in partition.demote + partition.grandfather}
            self.assertEqual(accounted, on_disk)
            self.assertEqual(partition.total, len(on_disk))


@patch("gzkit.foundation.sunset_migrate._SUNSET_PREREQUISITES", ())
class TestAttestationIsBoundNotAdvisory(unittest.TestCase):
    """Adversarial finding #5 -- the witness must bind at the library boundary.

    The taxonomy reader accepts any ``foundation_grandfathered`` event with a
    non-empty id and never inspects the attestor. If only the argparse wrapper
    enforces the witness, a direct ``run_migration`` call emits unwitnessed
    events that satisfy the SUPPORT gate -- the fabricated-witness surface this
    ADR exists to close.
    """

    def test_run_migration_apply_refuses_an_empty_attestor(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            with self.assertRaises(ValueError) as ctx:
                run_migration(
                    project_root=Path.cwd(),
                    receipt_dir=Path("artifacts/receipts"),
                    dry_run=False,
                    attestor="",
                    attestation="words",
                )
            self.assertIn("attestor", str(ctx.exception).lower())

    def test_run_migration_apply_refuses_empty_attestation_text(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            with self.assertRaises(ValueError):
                run_migration(
                    project_root=Path.cwd(),
                    receipt_dir=Path("artifacts/receipts"),
                    dry_run=False,
                    attestor="g0",
                    attestation="   ",
                )

    def test_emitted_witness_carries_a_non_empty_attestor(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.88-witness", "0.0.88", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.88-witness", "0.0.88", briefs=1, completed=1)

            run_migration(
                project_root=Path.cwd(),
                receipt_dir=Path("artifacts/receipts"),
                dry_run=False,
                attestor="g0",
                attestation="attest completed",
            )

            events = [
                json.loads(line)
                for line in Path(config.paths.ledger).read_text(encoding="utf-8").splitlines()
                if line
            ]
            witnesses = [e for e in events if e.get("event") == "foundation_grandfathered"]
            self.assertTrue(witnesses)
            for event in witnesses:
                self.assertTrue(
                    (event.get("attestor") or "").strip(),
                    "every terminality witness must name its human attestor",
                )


@patch("gzkit.foundation.sunset_migrate._SUNSET_PREREQUISITES", ())
class TestApplyIsPreflightedAndIdempotent(unittest.TestCase):
    """Adversarial finding #6 -- retry safety in front of an irreversible delete.

    Apply deletes packages one at a time and appends witnesses unconditionally.
    A crash partway leaves a half-migrated tree; re-running recomputes over the
    REDUCED tree and appends duplicate witnesses, violating REQ-02's
    exactly-one-per-entry requirement. Preflight and idempotence are what make
    a 136-file deletion safe to retry.
    """

    def test_rerunning_apply_does_not_duplicate_witnesses(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.89-once", "0.0.89", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.89-once", "0.0.89", briefs=1, completed=1)

            for _ in range(2):
                run_migration(
                    project_root=Path.cwd(),
                    receipt_dir=Path("artifacts/receipts"),
                    dry_run=False,
                    attestor="g0",
                    attestation="attest completed",
                )

            events = [
                json.loads(line)
                for line in Path(config.paths.ledger).read_text(encoding="utf-8").splitlines()
                if line
            ]
            witnesses = [
                e
                for e in events
                if e.get("event") == "foundation_grandfathered" and e.get("id") == "ADR-0.0.89-once"
            ]
            self.assertEqual(
                len(witnesses),
                1,
                "REQ-02 requires EXACTLY ONE witness per entry -- a retry must not append a second",
            )

    def test_a_promotion_round_trip_collision_keeps_the_intake_record(self) -> None:
        """pool -> foundation -> pool is a return leg, not a clash.

        The existing pool file's ``promoted_to:`` names this very ADR, so it is
        the historical intake record this foundation came from. keep-pool is the
        correct resolution: the record stays, its stale promotion marker is
        reversed, and the demotion proceeds.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pkg = _seed_foundation(config, "ADR-0.0.54-roundtrip", "0.0.54", brief_count=1)
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            (pool_dir / "ADR-pool.roundtrip.md").write_text(
                "---\nid: ADR-pool.roundtrip\nstatus: Superseded\n"
                "promoted_to: ADR-0.0.54-roundtrip\n---\n\n# Intake record\n",
                encoding="utf-8",
            )
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.54-roundtrip", "0.0.54", briefs=1, completed=0)

            run_migration(
                project_root=Path.cwd(),
                receipt_dir=Path("artifacts/receipts"),
                dry_run=False,
                attestor="g0",
                attestation="attest completed",
            )

            self.assertFalse(pkg.exists(), "the foundation package is still demoted")
            self.assertTrue((pool_dir / "ADR-pool.roundtrip.md").is_file())

    def test_an_unrelated_slug_clash_refuses_rather_than_discarding_a_body(self) -> None:
        """The dangerous branch: keep-pool here would destroy REQ-01's content.

        When the existing pool file was NOT promoted from this ADR, keeping it
        means this foundation's Intent/Decision is never written anywhere — a
        silent loss of exactly what REQ-0.34.0-04-01 requires be preserved.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pkg = _seed_foundation(config, "ADR-0.0.52-clash", "0.0.52", brief_count=1)
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            # Same derived slug, but promoted from a DIFFERENT ADR.
            (pool_dir / "ADR-pool.clash.md").write_text(
                "---\nid: ADR-pool.clash\nstatus: Superseded\n"
                "promoted_to: ADR-0.0.99-someone-else\n---\n\n# Different lineage\n",
                encoding="utf-8",
            )
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.52-clash", "0.0.52", briefs=1, completed=0)

            with self.assertRaises(RuntimeError) as ctx:
                run_migration(
                    project_root=Path.cwd(),
                    receipt_dir=Path("artifacts/receipts"),
                    dry_run=False,
                    attestor="g0",
                    attestation="attest completed",
                )

            self.assertIn("was NOT promoted from this ADR", str(ctx.exception))
            self.assertTrue(pkg.exists(), "the package must survive a refused collision")

    def test_preflight_rejects_a_pool_slug_collision_before_any_write(self) -> None:
        """All demotions are validated before the first rmtree, not during."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pkg_a = _seed_foundation(config, "ADR-0.0.78-dup", "0.0.78", brief_count=1)
            # Pre-place the pool file this demotion would target -> collision.
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            (pool_dir / "ADR-pool.dup.md").write_text(
                "---\nid: ADR-pool.dup\nstatus: Pool\n---\n\n# existing\n", encoding="utf-8"
            )
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.78-dup", "0.0.78", briefs=1, completed=0)

            with self.assertRaises(RuntimeError):
                run_migration(
                    project_root=Path.cwd(),
                    receipt_dir=Path("artifacts/receipts"),
                    dry_run=False,
                    attestor="g0",
                    attestation="attest completed",
                )

            self.assertTrue(
                pkg_a.exists(),
                "preflight must fail BEFORE any package is removed",
            )


@patch("gzkit.foundation.sunset_migrate._SUNSET_PREREQUISITES", ())
class TestRenameLeavesNoOrphanedLineage(unittest.TestCase):
    """REQ-0.34.0-04-03 -- the corpus subgraph survives the 23-node rename."""

    @staticmethod
    def _seeded_graph(adr_ids: list[str]) -> OntologyGraph:
        """A graph of foundation ADRs, each with an OBPI child and a covers anchor."""
        graph = OntologyGraph()
        for adr_id in adr_ids:
            graph.add_node(
                OntologyNode(
                    node_id=adr_id,
                    object_type=ObjectType.ADR,
                    ownership=Ownership.HARNESS,
                    plane=Plane.PROCESS,
                )
            )
            obpi_id = f"OBPI-{adr_id.removeprefix('ADR-')}-01-sample"
            graph.add_node(
                OntologyNode(
                    node_id=obpi_id,
                    object_type=ObjectType.OBPI,
                    ownership=Ownership.HARNESS,
                    plane=Plane.PROCESS,
                )
            )
            graph.add_edge(
                OntologyEdge(
                    source_id=adr_id,
                    target_id=obpi_id,
                    link_type=LinkType.CHILD,
                    provenance=Provenance.INTENT,
                )
            )
            graph.add_edge(
                OntologyEdge(
                    source_id=obpi_id,
                    target_id=adr_id,
                    link_type=LinkType.COVERS,
                    provenance=Provenance.OBSERVED,
                )
            )
        return graph

    @classmethod
    def _relabelled(
        cls, adr_ids: list[str], mapping: dict[str, str], *, relabel_edges: bool
    ) -> OntologyGraph:
        """Rebuild the graph with ADR nodes renamed; optionally leave edges stale."""
        graph = OntologyGraph()
        for adr_id in adr_ids:
            new_id = mapping.get(adr_id, adr_id)
            graph.add_node(
                OntologyNode(
                    node_id=new_id,
                    object_type=ObjectType.ADR,
                    ownership=Ownership.HARNESS,
                    plane=Plane.PROCESS,
                )
            )
            obpi_id = f"OBPI-{adr_id.removeprefix('ADR-')}-01-sample"
            graph.add_node(
                OntologyNode(
                    node_id=obpi_id,
                    object_type=ObjectType.OBPI,
                    ownership=Ownership.HARNESS,
                    plane=Plane.PROCESS,
                )
            )
            endpoint = new_id if relabel_edges else adr_id
            graph.add_edge(
                OntologyEdge(
                    source_id=endpoint,
                    target_id=obpi_id,
                    link_type=LinkType.CHILD,
                    provenance=Provenance.INTENT,
                )
            )
            graph.add_edge(
                OntologyEdge(
                    source_id=obpi_id,
                    target_id=endpoint,
                    link_type=LinkType.COVERS,
                    provenance=Provenance.OBSERVED,
                )
            )
        return graph

    @covers("REQ-0.34.0-04-03")
    def test_rename_introduces_no_dangling_endpoint(self) -> None:
        """Relabelling nodes and their edges together leaves the graph seam-free.

        A seam is an edge whose endpoint is not a materialized node, which is
        exactly what an orphaned `@covers`/`@surface` edge looks like after an ADR
        id changes underneath it.
        """
        adr_ids = [f"ADR-0.0.{n}-sample" for n in range(38, 61)]
        self.assertEqual(len(adr_ids), 23, "exercise the real 23-node rename width")
        mapping = {adr_id: f"ADR-pool.{adr_id.split('-', 2)[2]}" for adr_id in adr_ids}

        before = self._seeded_graph(adr_ids)
        after = self._relabelled(adr_ids, mapping, relabel_edges=True)

        self.assertEqual(compute_seams(before), [], "the pre-migration graph is seam-free")
        self.assertEqual(
            compute_seams(after),
            [],
            "the 23-node rename must not orphan any lineage or anchor edge",
        )

    @covers("REQ-0.34.0-04-03")
    def test_a_rename_that_strands_its_edges_is_detected(self) -> None:
        """Negative control: the seam check must actually bite.

        If nodes are renamed but their edges keep pointing at the old ids, every
        such edge is dangling. A seam predicate that returned [] here would make
        the assertion above worthless.
        """
        adr_ids = [f"ADR-0.0.{n}-sample" for n in range(38, 61)]
        mapping = {adr_id: f"ADR-pool.{adr_id.split('-', 2)[2]}" for adr_id in adr_ids}

        stranded = self._relabelled(adr_ids, mapping, relabel_edges=False)
        seams = compute_seams(stranded)

        self.assertEqual(
            len(seams),
            len(adr_ids) * 2,
            "each stranded node leaves both its CHILD and its COVERS edge dangling",
        )
        self.assertEqual(
            {seam.link_type for seam in seams},
            {"child", "covers"},
            "both the lineage edge and the anchor edge must surface as seams",
        )

    @covers("REQ-0.34.0-04-03")
    def test_real_migration_rebuilds_the_projection_without_new_seams(self) -> None:
        """Integration proof: drive the REAL migration, then re-project the graph.

        The fixture-relabelling tests above prove ``compute_seams`` works; they
        cannot fail if the migration renames the wrong nodes, because the test
        does the renaming. This one lets ``run_migration`` mutate a real ledger
        and tree, rebuilds the corpus projection from that mutated Layer-2, and
        asserts the outcome — so a migration that stopped emitting rename events
        or orphaned lineage WOULD turn it red.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.75-goes", "0.0.75", brief_count=2)
            _seed_foundation(config, "ADR-0.0.76-stays", "0.0.76", brief_count=2)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.75-goes", "0.0.75", briefs=2, completed=0)
            _seed_ledger(ledger, "ADR-0.0.76-stays", "0.0.76", briefs=2, completed=1)

            before = graph_probe(ledger)
            receipt = run_migration(
                project_root=Path.cwd(),
                receipt_dir=Path("artifacts/receipts"),
                dry_run=False,
                attestor="g0",
                attestation="attest completed",
            )
            after = graph_probe(Ledger(Path(config.paths.ledger)))

            self.assertLessEqual(
                after["seam_count"],
                before["seam_count"],
                "the migration must not introduce orphaned lineage or dangling edges",
            )
            self.assertEqual(receipt["graph_diff"]["seam_delta"], 0)
            self.assertNotIn(
                "ADR-0.0.75-goes",
                after["adr_node_ids"],
                "the demoted ADR's old id must no longer be a live node",
            )
            self.assertIn(
                "ADR-pool.goes",
                after["adr_node_ids"],
                "every removed node needs its successor -- the rename must be imaged",
            )
            self.assertIn("ADR-0.0.76-stays", after["adr_node_ids"])
            self.assertEqual(receipt["blockers"], [])

    def test_rename_map_covers_exactly_the_demote_set(self) -> None:
        """The receipt's rename map is the diff contract for the re-sense gate."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.84-goes", "0.0.84", brief_count=1)
            _seed_foundation(config, "ADR-0.0.85-stays", "0.0.85", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.84-goes", "0.0.84", briefs=1, completed=0)
            _seed_ledger(ledger, "ADR-0.0.85-stays", "0.0.85", briefs=1, completed=1)

            mapping = rename_map(compute_partition(Path.cwd(), ledger))

            self.assertEqual(mapping, {"ADR-0.0.84-goes": "ADR-pool.goes"})


class TestRenameIntegrityIsTheBindingReq03Proof(unittest.TestCase):
    """Pass-3 F1 -- seam analysis cannot see a dangling anchor, so this must.

    ``graph_probe`` documents that project_all's compose step discards an
    ``@covers`` edge whose source-unit node was never materialized, so an
    orphaned anchor never surfaces as a seam. Successor-completeness is the
    assertion that does not depend on anchor visibility.
    """

    def test_a_removed_node_with_no_successor_is_reported(self) -> None:
        problems = rename_integrity(
            {"ADR-0.0.42-storybook": "ADR-pool.storybook"},
            {"adr_node_ids": ["ADR-0.0.42-storybook"]},
            {"adr_node_ids": []},
        )
        self.assertTrue(any("no successor" in p for p in problems))
        self.assertTrue(any("GHI #520" in p for p in problems))

    def test_a_node_that_never_disappeared_is_reported(self) -> None:
        problems = rename_integrity(
            {"ADR-0.0.42-storybook": "ADR-pool.storybook"},
            {"adr_node_ids": ["ADR-0.0.42-storybook"]},
            {"adr_node_ids": ["ADR-0.0.42-storybook", "ADR-pool.storybook"]},
        )
        self.assertTrue(any("did not transact" in p for p in problems))

    def test_a_clean_rename_reports_nothing(self) -> None:
        self.assertEqual(
            rename_integrity(
                {"ADR-0.0.42-storybook": "ADR-pool.storybook"},
                {"adr_node_ids": ["ADR-0.0.42-storybook", "ADR-0.0.9-keep"]},
                {"adr_node_ids": ["ADR-pool.storybook", "ADR-0.0.9-keep"]},
            ),
            [],
        )

    def test_an_unexpected_disappearance_is_reported(self) -> None:
        """A node vanishing that was NOT a planned demotion is also stranding."""
        problems = rename_integrity(
            {},
            {"adr_node_ids": ["ADR-0.0.9-keep"]},
            {"adr_node_ids": []},
        )
        self.assertTrue(any("not an expected demotion" in p for p in problems))


class TestAnchorIntegrityIsCheckedDirectly(unittest.TestCase):
    """Pass-4 F1 -- REQ-03's ANCHOR conjunct, checked without seam analysis.

    ``graph_probe`` provably cannot see this failure: project_all discards an
    anchor edge whose source-unit node was never materialized, so an orphaned
    ``@covers`` yields ``covers_edges == []`` and ``seams == []`` while fidelity
    reports complete. Reading the anchor index answers the question directly.
    """

    def test_an_anchor_targeting_a_doomed_req_is_reported(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.77-doomed", "0.0.77", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.77-doomed", "0.0.77", briefs=1, completed=0)
            # Live source anchoring a REQ whose brief this migration deletes.
            src = Path("src/probe_pkg")
            src.mkdir(parents=True, exist_ok=True)
            # The anchor index detects the DECORATOR form, not a docstring
            # mention -- verified against build_source_anchor_index.
            (src / "probe.py").write_text(
                "from gzkit.traceability import covers\n\n\n"
                '@covers("REQ-0.0.77-01-01")\n'
                "def probe() -> None:\n"
                '    """Anchored at a REQ this migration deletes."""\n',
                encoding="utf-8",
            )

            partition = compute_partition(Path.cwd(), ledger)
            problems = anchor_integrity(Path.cwd(), partition)

            self.assertTrue(
                any("REQ-0.0.77-01-01" in p for p in problems),
                f"an anchor at a doomed REQ must be reported; got {problems}",
            )
            self.assertTrue(any("would dangle" in p for p in problems))

    def test_an_anchor_targeting_a_surviving_req_is_not_reported(self) -> None:
        """The converse, so the check is not simply flagging every anchor."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.79-keeps", "0.0.79", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.79-keeps", "0.0.79", briefs=1, completed=1)
            src = Path("src/probe_pkg")
            src.mkdir(parents=True, exist_ok=True)
            (src / "probe.py").write_text(
                "from gzkit.traceability import covers\n\n\n"
                '@covers("REQ-0.0.79-01-01")\n'
                "def probe() -> None:\n"
                '    """Anchored at a REQ that survives."""\n',
                encoding="utf-8",
            )

            partition = compute_partition(Path.cwd(), ledger)

            self.assertEqual(partition.demote, ())
            self.assertEqual(anchor_integrity(Path.cwd(), partition), [])

    def test_an_expected_demotion_missing_from_the_pre_image_is_not_waived(self) -> None:
        """Pass-4: an absent pre-image node was previously skipped silently."""
        problems = rename_integrity(
            {"ADR-0.0.42-storybook": "ADR-pool.storybook"},
            {"adr_node_ids": []},
            {"adr_node_ids": []},
        )
        self.assertTrue(
            any("absent from the pre-migration graph" in p for p in problems),
            f"an unprovable rename must be reported, not waived; got {problems}",
        )


class TestWitnesslessEventFailsTheProofSurfaces(unittest.TestCase):
    """Pass-3 F5 -- the typed model and schema must reject a witnessless event.

    The taxonomy reader admits any event of this type with a non-empty id and
    never inspects the attestor, so if the model and schema tolerated a blank
    one, a hand-built event would satisfy REQ-02's structural proof with no
    Gate-5 authority. Enforcing it here means such an event fails
    ``gz validate --ledger``, a bound ``gz check`` step.
    """

    def test_typed_model_rejects_a_missing_attestor(self) -> None:
        with self.assertRaises(Exception) as ctx:
            parse_typed_event(
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "foundation_grandfathered",
                    "id": "ADR-0.0.9-x",
                    "ts": "2026-07-29T00:00:00Z",
                    "title": "X",
                    "semver": "0.0.9",
                    "frozen_at": "2026-07-29",
                }
            )
        self.assertIn("attestor", str(ctx.exception))

    def test_typed_model_rejects_an_empty_attestor(self) -> None:
        with self.assertRaises(Exception) as ctx:
            parse_typed_event(
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "foundation_grandfathered",
                    "id": "ADR-0.0.9-x",
                    "ts": "2026-07-29T00:00:00Z",
                    "title": "X",
                    "semver": "0.0.9",
                    "frozen_at": "2026-07-29",
                    "attestor": "",
                }
            )
        self.assertIn("attestor", str(ctx.exception))

    def test_typed_model_rejects_a_whitespace_only_attestor(self) -> None:
        """``min_length=1`` counts CHARACTERS -- three spaces satisfy it.

        Measured bypass: ``attestor="   "`` passed both the model and the ledger
        schema while naming no witness. Stripped-nonempty is the real invariant.
        """
        with self.assertRaises(Exception) as ctx:
            parse_typed_event(
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "foundation_grandfathered",
                    "id": "ADR-0.0.9-x",
                    "ts": "2026-07-29T00:00:00Z",
                    "title": "X",
                    "semver": "0.0.9",
                    "frozen_at": "2026-07-29",
                    "attestor": "   ",
                }
            )
        self.assertIn("whitespace is not an attestation", str(ctx.exception))

    def test_the_ledger_validator_rejects_a_whitespace_attestor(self) -> None:
        """`min_length` measured RAW characters, so `"   "` satisfied every guard.

        Behavioral probe against the real validator, not an assertion about the
        schema's field value: a whitespace-only attestor previously produced zero
        ledger errors while naming no witness. The fix strips before measuring,
        which closes the same hole across all 54 min_length-guarded event fields.
        """
        base = {
            "schema": "gzkit.ledger.v1",
            "event": "foundation_grandfathered",
            "id": "ADR-0.0.9-x",
            "ts": "2026-07-30T00:00:00+00:00",
            "title": "X",
            "semver": "0.0.9",
            "frozen_at": "2026-07-29",
        }
        with TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "ledger.jsonl"
            for label, attestor, expected in (
                ("whitespace", "   ", 1),
                ("empty", "", 1),
                ("valid", "g0", 0),
            ):
                with self.subTest(attestor=label):
                    event = {**base, "attestor": attestor}
                    ledger_path.write_text(json.dumps(event) + "\n", encoding="utf-8")
                    self.assertEqual(len(validate_ledger(ledger_path)), expected)

    # A test asserting that schemas/ledger.json literally contains "attestor" in
    # `required` with min_length 1 was removed here: it read the file and echoed
    # its content, so it could not fail if ledger_check's BEHAVIOR regressed while
    # the schema text stayed put — the discriminator in `.gzkit/rules/tests.md`.
    # `test_the_ledger_validator_rejects_a_whitespace_attestor` above is the real
    # proof: it runs validate_ledger and asserts the error counts.


class TestPrerequisiteTerminalityComesFromCanonicalState(unittest.TestCase):
    """Pass-3 F4 -- an event's presence is not proof the ADR is validated."""

    def test_a_validated_receipt_over_a_nonvalidated_graph_does_not_satisfy(self) -> None:
        """The graph replay is the authority; the receipt discriminator is not.

        A ``validated`` receipt whose evidence says ``adr_completion=not_completed``
        previously produced zero blockers while the graph's ``validated`` flag was
        False.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.37-prereq", "0.0.37", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.37-prereq", "0.0.37", briefs=1, completed=1)

            graph = ledger.get_artifact_graph()
            node = graph.get(ledger.canonicalize_id("ADR-0.0.37-prereq")) or {}
            self.assertFalse(
                node.get("validated"),
                "fixture precondition: the ADR must not be graph-validated",
            )
            with patch("gzkit.foundation.sunset_migrate._SUNSET_PREREQUISITES", ("ADR-0.0.37",)):
                blockers = check_blockers(Path.cwd(), ledger)

            self.assertTrue(
                any("closeout witness" in b for b in blockers),
                f"a non-validated ADR must block regardless of receipt events; got {blockers}",
            )


@patch("gzkit.foundation.sunset_migrate._SUNSET_PREREQUISITES", ())
class TestConcurrentApplyFailsClosed(unittest.TestCase):
    """Pass-3 F6 -- an existing journal must not be silently overwritten."""

    def test_a_second_apply_cannot_claim_an_existing_journal(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.59-a", "0.0.59", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.59-a", "0.0.59", briefs=1, completed=1)
            # A journal naming a demotion whose package is still present is an
            # in-flight or interrupted apply -- either way, refuse.
            journal = Path("artifacts/receipts/foundation-sunset-journal.json")
            journal.parent.mkdir(parents=True, exist_ok=True)
            journal.write_text(
                json.dumps({"demotions": [{"source_id": "ADR-0.0.59-a", "children": []}]}),
                encoding="utf-8",
            )

            with self.assertRaises(RuntimeError) as ctx:
                run_migration(
                    project_root=Path.cwd(),
                    receipt_dir=Path("artifacts/receipts"),
                    dry_run=False,
                    attestor="g0",
                    attestation="attest completed",
                )
            self.assertIn("ADR-0.0.59-a", str(ctx.exception))

    def test_a_renamed_demotion_with_unparked_children_is_reported(self) -> None:
        """The later torn-write window: renamed, but children never parked."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            ledger = Ledger(Path(config.paths.ledger))
            ledger.append(
                artifact_renamed_event(
                    old_id="ADR-0.0.57-torn",
                    new_id="ADR-pool.torn",
                    reason="pool_demotion",
                )
            )
            journal = Path("artifacts/receipts/foundation-sunset-journal.json")
            journal.parent.mkdir(parents=True, exist_ok=True)
            journal.write_text(
                json.dumps(
                    {
                        "demotions": [
                            {
                                "source_id": "ADR-0.0.57-torn",
                                "children": ["OBPI-0.0.57-01-x", "OBPI-0.0.57-02-x"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            stranded = interrupted_demotions(Path.cwd(), ledger)

            self.assertTrue(
                any("never parked" in s for s in stranded),
                f"a rename without its parking events must be reported; got {stranded}",
            )


class TestShippedPrerequisiteRosterBites(unittest.TestCase):
    """Deliberately UNPATCHED -- proves the roster gzkit actually ships fail-closes.

    Every other apply-path class patches ``_SUNSET_PREREQUISITES`` to ``()``,
    because a fixture tree contains none of the five real prerequisites. That
    scoping is necessary but it also means nothing else in this module exercises
    the shipped tuple. This class is the one that does; patching it would leave
    the production gate untested.
    """

    def test_default_run_reports_absent_prerequisites_and_writes_nothing(self) -> None:
        """No flags means preview. Exit 3 here is correct, not a defect.

        A bare fixture carries none of the real Sunset prerequisites, so the
        default run reports absent-prerequisite blockers and exits non-zero -- a
        recorded blocker that still exited 0 would be a green-looking run over a
        red result. What the DEFAULT guarantees is that nothing was written.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            with redirect_stdout(io.StringIO()):
                exit_code = main([])
            self.assertEqual(exit_code, 3, "absent prerequisites must exit non-zero")
            self.assertFalse(
                Path("data/foundation_grandfather.json").exists(),
                "the default mode must be a preview that writes no manifest",
            )

    def test_run_migration_has_no_prerequisite_bypass_parameter(self) -> None:
        """The gate must not be disableable through the production signature.

        A ``prerequisites=()`` keyword would switch off a STOP-on-BLOCKERS
        requirement with no boundary distinguishing a fixture from the real
        repository -- so the parameter's ABSENCE is the contract.
        """
        signature = inspect.signature(run_migration)
        self.assertNotIn(
            "prerequisites",
            signature.parameters,
            "the prerequisite roster must not be overridable by a production caller",
        )


@patch("gzkit.foundation.sunset_migrate._SUNSET_PREREQUISITES", ())
class TestApplyRequiresAttestation(unittest.TestCase):
    """The Gate-5 witness is what legitimises the pre-ledger backfill."""

    def test_apply_without_attestor_fails_closed(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            exit_code = main(["--apply", "--attestation", "words"])
            self.assertEqual(exit_code, 2, "--apply without --attestor must fail closed")

    def test_apply_without_attestation_fails_closed(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            exit_code = main(["--apply", "--attestor", "g0"])
            self.assertEqual(exit_code, 2, "--apply without --attestation must fail closed")

    def test_dry_run_over_a_terminal_tree_exits_zero(self) -> None:
        """The converse, so exit 3 above is not simply "always non-zero"."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.61-fine", "0.0.61", brief_count=1)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.61-fine", "0.0.61", briefs=1, completed=1)

            receipt = run_migration(
                project_root=Path.cwd(),
                receipt_dir=Path("artifacts/receipts"),
                dry_run=True,
            )

            self.assertEqual(receipt["blockers"], [])
            self.assertTrue(receipt["dry_run"])


class TestBlockersHaltBeforeAnyWrite(unittest.TestCase):
    """Brief Requirement 1 -- a mid-limbo populate would false-red the gate."""

    def test_non_terminal_prerequisite_is_reported_as_a_blocker(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            # ADR-0.0.37 is a declared Sunset prerequisite; seed it with authored
            # but uncompleted work so it sits in Pending-with-attested-work limbo.
            _seed_foundation(config, "ADR-0.0.37-prereq", "0.0.37", brief_count=2)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.37-prereq", "0.0.37", briefs=2, completed=1)

            blockers = check_blockers(Path.cwd(), ledger)

            self.assertTrue(
                any("ADR-0.0.37" in blocker for blocker in blockers),
                f"a non-terminal prerequisite must be named as a blocker; got {blockers}",
            )

    def test_apply_raises_when_blockers_are_present(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_foundation(config, "ADR-0.0.37-prereq", "0.0.37", brief_count=2)
            ledger = Ledger(Path(config.paths.ledger))
            _seed_ledger(ledger, "ADR-0.0.37-prereq", "0.0.37", briefs=2, completed=1)

            # Deliberately uses the REAL default prerequisite tuple: this test
            # exists to prove the shipped fail-closed list bites, so narrowing it
            # here would test nothing.
            with self.assertRaises(RuntimeError):
                run_migration(
                    project_root=Path.cwd(),
                    receipt_dir=Path("artifacts/receipts"),
                    dry_run=False,
                    attestor="g0",
                    attestation="test attestation",
                )


if __name__ == "__main__":
    unittest.main()
