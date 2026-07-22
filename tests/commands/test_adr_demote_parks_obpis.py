"""Demotion must transact over its child OBPIs (GHI #584).

The 2026-05-23 Day-0 pool demotion (GHI #520) renamed 28 ADRs and emitted
exactly one ``artifact_renamed`` event per ADR. Their OBPIs received no event
of any kind, leaving 237 ``obpi_created`` records pointing at parent ids that
no longer resolve — parentless live nodes in the Layer-3 state graph.

Operator disposition ruling (2026-07-21, verbatim): "we can't leave these
stranded - we need to find a way to park/archive them as they are related to
the original ADR and were relevant at the time of their authoring."

Park is therefore NOT withdraw. ``governance-core.md`` § Withdraw vs Repudiate
defines withdraw as permanent one-way retirement, re-completable: No. A parked
OBPI is the pooled ADR's decomposition and becomes live again if the ADR is
re-promoted, so parking must be reversible and must preserve re-promotability.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event
from gzkit.ledger_events import obpi_created_event, obpi_withdrawn_event
from tests.commands.common import CliRunner, _quick_init
from tests.commands.test_adr_demote import (
    _SAMPLE_FEATURE_ADR_ID,
    _SAMPLE_POOL_ID,
    _seed_feature_adr,
)


def _read_events(path: str = ".gzkit/ledger.jsonl") -> list[dict[str, object]]:
    """Return every ledger event as a dict."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line]


def _events_of(kind: str, path: str = ".gzkit/ledger.jsonl") -> list[dict[str, object]]:
    """Return ledger events matching one event type."""
    return [event for event in _read_events(path) if event.get("event") == kind]


class TestDemoteParksChildObpis(unittest.TestCase):
    """``gz adr demote`` transacts over child OBPIs rather than stranding them."""

    def test_apply_emits_one_park_event_per_live_child_obpi(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))
            for idx in (1, 2):
                ledger.append(
                    obpi_created_event(
                        f"OBPI-0.27.0-{idx:02d}-sample", parent=_SAMPLE_FEATURE_ADR_ID
                    )
                )

            result = runner.invoke(main, ["adr", "demote", _SAMPLE_FEATURE_ADR_ID, "--ghi", "584"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            parked = _events_of("obpi_parked")
            self.assertEqual(
                {str(event["id"]) for event in parked},
                {"OBPI-0.27.0-01-sample", "OBPI-0.27.0-02-sample"},
                "every live child OBPI must be parked in the same ceremony as the demotion",
            )

    def test_park_event_records_the_pool_id_the_parent_became(self) -> None:
        """A parked OBPI must point at a parent id that resolves post-demotion."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))
            ledger.append(
                obpi_created_event("OBPI-0.27.0-01-sample", parent=_SAMPLE_FEATURE_ADR_ID)
            )

            runner.invoke(main, ["adr", "demote", _SAMPLE_FEATURE_ADR_ID, "--ghi", "584"])

            parked = _events_of("obpi_parked")
            self.assertEqual(len(parked), 1, msg=str(parked))
            event = parked[0]
            self.assertEqual(
                event.get("parked_to"),
                _SAMPLE_POOL_ID,
                "the park event must name the pool id so the OBPI's lineage still resolves",
            )
            self.assertEqual(event.get("parent"), _SAMPLE_FEATURE_ADR_ID)
            self.assertEqual(
                event.get("reason"),
                "pool_demotion",
                "park cause must be attributable to the transition that caused it",
            )

    def test_already_terminal_obpis_are_not_parked(self) -> None:
        """Withdrawn OBPIs are already terminal — parking them would double-count."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))
            ledger.append(
                obpi_created_event("OBPI-0.27.0-01-sample", parent=_SAMPLE_FEATURE_ADR_ID)
            )
            ledger.append(
                obpi_created_event("OBPI-0.27.0-02-sample", parent=_SAMPLE_FEATURE_ADR_ID)
            )
            ledger.append(
                obpi_withdrawn_event(
                    "OBPI-0.27.0-02-sample",
                    parent=_SAMPLE_FEATURE_ADR_ID,
                    reason="superseded",
                    attestor="g0",
                )
            )

            runner.invoke(main, ["adr", "demote", _SAMPLE_FEATURE_ADR_ID, "--ghi", "584"])

            parked = _events_of("obpi_parked")
            self.assertEqual(
                [str(event["id"]) for event in parked],
                ["OBPI-0.27.0-01-sample"],
                "an OBPI carrying a terminal event must not also be parked",
            )

    def test_dry_run_reports_park_plan_without_writing_events(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))
            ledger.append(
                obpi_created_event("OBPI-0.27.0-01-sample", parent=_SAMPLE_FEATURE_ADR_ID)
            )
            before = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")

            result = runner.invoke(
                main, ["adr", "demote", _SAMPLE_FEATURE_ADR_ID, "--ghi", "584", "--dry-run"]
            )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(
                Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8"),
                before,
                "dry-run must not append park events",
            )
            self.assertIn("OBPI-0.27.0-01-sample", result.output)
            self.assertIn("Would park 1 child OBPI", result.output)

    def test_demotion_with_no_child_obpis_emits_no_park_events(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(main, ["adr", "demote", _SAMPLE_FEATURE_ADR_ID, "--ghi", "584"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_events_of("obpi_parked"), [])


class TestParkIsReversible(unittest.TestCase):
    """Park preserves re-promotability — the property that rules out withdraw."""

    def test_promoting_the_pool_adr_unparks_its_obpis(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))
            ledger.append(
                obpi_created_event("OBPI-0.27.0-01-sample", parent=_SAMPLE_FEATURE_ADR_ID)
            )
            runner.invoke(main, ["adr", "demote", _SAMPLE_FEATURE_ADR_ID, "--ghi", "584"])
            self.assertEqual(len(_events_of("obpi_parked")), 1)
            pool_file = Path(config.paths.adrs) / "pool" / f"{_SAMPLE_POOL_ID}.md"
            pool_file.write_text(
                pool_file.read_text(encoding="utf-8")
                + "\n## Target Scope\n\n- sample: a seeded actionable scope bullet.\n"
                + "\n## Feature Checklist\n\n- [ ] sample: a seeded checklist item.\n",
                encoding="utf-8",
            )

            # --force bypasses the post-apply eval-quality gate: this test asserts
            # park reversibility, not the seeded fixture's scorecard.
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    _SAMPLE_POOL_ID,
                    "--kind",
                    "feature",
                    "--semver",
                    "0.27.0",
                    "--force",
                ],
            )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            unparked = _events_of("obpi_unparked")
            self.assertEqual(
                [str(event["id"]) for event in unparked],
                ["OBPI-0.27.0-01-sample"],
                "re-promoting the parent must release its parked OBPIs",
            )


if __name__ == "__main__":
    unittest.main()


class TestOrphanCensusIdForms(unittest.TestCase):
    """The orphan census resolves both ADR id forms (GHI #584)."""

    def test_bare_semver_parent_resolves_to_slugged_adr_on_disk(self) -> None:
        """An OBPI naming `ADR-0.0.43` is not an orphan when `ADR-0.0.43-<slug>` exists.

        Older `obpi_created` records cite the bare-semver parent form while the
        ADR lives on disk under its slugged id. Reporting those as orphans is a
        false positive, and a gate that false-fires teaches operators to skip it.
        """
        from gzkit.obpi_lifecycle import orphaned_obpi_ids

        events = [
            {"event": "obpi_created", "id": "OBPI-0.0.43-01-x", "parent": "ADR-0.0.43"},
            {"event": "obpi_created", "id": "OBPI-9.9.9-01-y", "parent": "ADR-9.9.9"},
        ]
        live = {"ADR-0.0.43-ddd-domain-cascade", "ADR-0.0.43"}

        orphans = orphaned_obpi_ids(events, live)

        self.assertNotIn("OBPI-0.0.43-01-x", orphans)
        self.assertIn(
            "OBPI-9.9.9-01-y",
            orphans,
            "an OBPI whose parent is absent in BOTH id forms is still an orphan",
        )

    def test_live_adr_ids_registers_both_forms(self) -> None:
        from gzkit.governance.trust_audits.taxonomy import _live_adr_ids

        runner = CliRunner()
        with runner.isolated_filesystem():
            pkg = Path("docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade")
            pkg.mkdir(parents=True)
            (pkg / "ADR-0.0.43-ddd-domain-cascade.md").write_text(
                "---\nid: ADR-0.0.43-ddd-domain-cascade\nkind: foundation\n---\n\n# x\n",
                encoding="utf-8",
            )

            live = _live_adr_ids(Path("."))

            self.assertIn("ADR-0.0.43-ddd-domain-cascade", live)
            self.assertIn("ADR-0.0.43", live)
