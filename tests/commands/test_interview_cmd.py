"""Tests for ``gz interview adr`` ADR scaffolding (GHI #505).

GHI #505: the ``gz interview adr`` path wrote ADRs to a flat directory
(``<adrs>/<id>.md``) and emitted bare-id ``adr_created`` events, diverging
from the canonical ``<adrs>/{foundation,pre-release}/<id>/<id>.md``
slug-package layout that ``gz plan create`` produces. These tests pin the
canonical slug-package routing, canonical-form id validation, and
on-disk-derived ledger emission that close the bare-id ``adr_created`` class
(GHI #279 / #344 / #494 / #505).
"""

import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.ledger import Ledger
from tests.commands.common import CliRunner, _quick_init

# Every ADR interview question except ``id`` and ``semver`` (supplied
# per-test). All ADR questions are required, so a complete answer set keeps
# the interview off the "create anyway?" confirmation path.
_BASE_ADR_ANSWERS = {
    "title": "Use JWT for Authentication",
    "lane": "lite",
    "parent": "PRD-GZKIT-1.0.0",
    "intent": "Stateless auth that scales horizontally.",
    "decision": "Use JWT tokens with RS256 signing.",
    "positive_consequences": "1. Stateless auth scales horizontally",
    "negative_consequences": "1. Token size larger than session cookies",
    "checklist": "1. Set up JWT library and key management",
    "alternatives": "Session-based auth: rejected, requires sticky sessions.",
}


def _write_answers(path: str, *, doc_id: str, semver: str) -> None:
    """Write a complete ADR answers JSON for ``gz interview adr --from``."""
    answers = dict(_BASE_ADR_ANSWERS)
    answers["id"] = doc_id
    answers["semver"] = semver
    Path(path).write_text(json.dumps(answers), encoding="utf-8")


class TestInterviewAdrCanonicalScaffolding(unittest.TestCase):
    """GHI #505 — ``gz interview adr`` produces canonical slug-package ADRs."""

    def test_bare_adr_id_rejected_before_emission(self) -> None:
        """A bare ``ADR-X.Y.Z`` id fails fast with no file or ledger write.

        The bare-id class (GHI #279 / #344 / #494): a non-slug id emits an
        unslugged ``adr_created`` event that diverges from the canonical
        on-disk directory. The interview path must reject it at exit 1
        before any write — file untouched, ledger untouched.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger_path = Path(".gzkit/ledger.jsonl")
            events_before = [e.id for e in Ledger(ledger_path).read_all()]

            _write_answers("answers.json", doc_id="ADR-0.1.0", semver="0.1.0")
            result = runner.invoke(main, ["interview", "adr", "--from", "answers.json"])

            self.assertEqual(result.exit_code, 1, msg=result.output)
            unwrapped = result.output.replace("\n", " ")
            self.assertIn("ADR-0.1.0", unwrapped)
            self.assertIn("slug", unwrapped)

            adrs_root = Path("design/adr")
            self.assertFalse(
                adrs_root.exists() and any(adrs_root.rglob("*.md")),
                msg="no ADR file may be written on bare-id rejection",
            )
            events_after = [e.id for e in Ledger(ledger_path).read_all()]
            self.assertEqual(
                events_after,
                events_before,
                msg="ledger must be untouched on bare-id rejection",
            )

    def test_feature_adr_routes_to_pre_release_slug_package(self) -> None:
        """A feature-semver ADR lands in ``pre-release/<id>/<id>.md``.

        The canonical layout: ``<adrs>/pre-release/ADR-<semver>-<slug>/
        ADR-<semver>-<slug>.md`` — never the flat ``<adrs>/<id>.md``.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_answers("answers.json", doc_id="ADR-0.1.0-jwt-authentication", semver="0.1.0")
            result = runner.invoke(main, ["interview", "adr", "--from", "answers.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_id = "ADR-0.1.0-jwt-authentication"
            expected = Path(f"design/adr/pre-release/{adr_id}/{adr_id}.md")
            self.assertTrue(expected.is_file(), msg=f"expected slug-package at {expected}")
            self.assertFalse(
                Path(f"design/adr/{adr_id}.md").exists(),
                msg="flat-directory ADR file must not be written",
            )
            body = expected.read_text(encoding="utf-8")
            self.assertIn("kind: feature", body)

    def test_foundation_adr_routes_to_foundation_slug_package(self) -> None:
        """A ``0.0.x`` ADR lands in ``foundation/<id>/<id>.md`` as foundation kind.

        ``foundation`` <=> ``0.0.x`` is the ADR-0.0.17 taxonomy binding; the
        interview derives kind and routing from the semver embedded in the
        canonical id. Foundation ADRs scaffold the ``## Why foundation tier?``
        section that ``kind_invariance`` validation requires.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_answers("answers.json", doc_id="ADR-0.0.5-token-discipline", semver="0.0.5")
            result = runner.invoke(main, ["interview", "adr", "--from", "answers.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_id = "ADR-0.0.5-token-discipline"
            expected = Path(f"design/adr/foundation/{adr_id}/{adr_id}.md")
            self.assertTrue(expected.is_file(), msg=f"expected slug-package at {expected}")
            body = expected.read_text(encoding="utf-8")
            self.assertIn("kind: foundation", body)
            self.assertIn("## Why foundation tier?", body)

    def test_adr_created_event_id_derives_from_on_disk_directory(self) -> None:
        """The emitted ``adr_created`` id equals the on-disk slug-package dir.

        T2 (ledger event) must match T1 (on-disk directory) — the event id is
        derived from the canonical slug-package directory name, not echoed
        from the raw interview answer.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_answers("answers.json", doc_id="ADR-0.2.0-graph-engine", semver="0.2.0")
            result = runner.invoke(main, ["interview", "adr", "--from", "answers.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_dir = Path("design/adr/pre-release/ADR-0.2.0-graph-engine")
            self.assertTrue(adr_dir.is_dir(), msg=f"expected slug-package dir {adr_dir}")
            adr_events = [
                e
                for e in Ledger(Path(".gzkit/ledger.jsonl")).read_all()
                if e.event == "adr_created"
            ]
            self.assertEqual(len(adr_events), 1, msg=str([e.id for e in adr_events]))
            self.assertEqual(
                adr_events[0].id,
                adr_dir.name,
                msg="adr_created.id must equal the on-disk directory slug-form",
            )

    def test_rendered_frontmatter_substitutes_kind_placeholder(self) -> None:
        """The rendered ADR carries a real ``kind:`` value, not literal ``{kind}``.

        The flat-path interview never passed ``kind`` to the template, so the
        ADR frontmatter rendered the literal placeholder ``kind: {kind}`` —
        which fails the ``adr.json`` schema ``kind`` enum.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_answers("answers.json", doc_id="ADR-0.0.7-density-bands", semver="0.0.7")
            result = runner.invoke(main, ["interview", "adr", "--from", "answers.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_id = "ADR-0.0.7-density-bands"
            body = Path(f"design/adr/foundation/{adr_id}/{adr_id}.md").read_text(encoding="utf-8")
            self.assertNotIn("{kind}", body)
            self.assertIn("kind: foundation", body)


if __name__ == "__main__":
    unittest.main()
