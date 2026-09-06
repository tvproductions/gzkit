"""Plan ownership and FAIL-receipt preservation in preflight (GHI #967).

Two coupled defects. Plan *discovery* matched any mention of an OBPI id
anywhere in a plan's body, while *orphan detection* matched only the full slug —
so one plan file was at once "the plan for OBPI-05" and "no plan exists for
OBPI-05", and the FAIL receipt that says no plan exists orphaned itself by
construction: the way a sibling plan mentions an unplanned OBPI IS the
short-form exclusion sentence.

Then `_apply_cleanup` unlinked that orphan raw, three lines under a docstring
refusing to do the same to an expired lock because it would be "a silent bypass
of that audit coupling". A FAIL verdict is audit content, not a plain artifact.

These tests pin the shared ownership rule (declared in filename or H1, never an
incidental body mention) and the four constraints the archive must satisfy:
complete contents, provenance, verify-before-remove, and fail closed with the
original retained when preservation fails.
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from gzkit.commands.preflight import _find_orphan_receipts, archive_plan_audit_receipt
from gzkit.pipeline_markers import plan_declares_obpi


def _plan(directory: Path, name: str, body: str) -> Path:
    path = directory / name
    path.write_text(body, encoding="utf-8")
    return path


class TestPlanOwnership(unittest.TestCase):
    def test_an_incidental_body_mention_is_not_ownership(self) -> None:
        # The exact shape that self-orphaned the receipt: the OBPI-04 plan
        # disclaims scope it does not carry, naming OBPI-05 in the disclaimer.
        # A plan that says it does NOT ship something does not own it.
        with TemporaryDirectory() as td:
            plan = _plan(
                Path(td),
                "section-ownership-and-ratchet-OBPI-0.35.0-04.md",
                "# Plan — OBPI-0.35.0-04-section-ownership-and-ratchet\n\n"
                "It does NOT ship materialization (OBPI-0.35.0-05).\n",
            )
            self.assertTrue(plan_declares_obpi(plan, "OBPI-0.35.0-04-section-ownership"))
            self.assertFalse(plan_declares_obpi(plan, "OBPI-0.35.0-05-corpus-candidate"))

    def test_a_plan_owns_the_obpi_in_its_h1_even_without_it_in_the_filename(self) -> None:
        # Measured 2026-09-06: 304 of 306 plans declare their OBPI in the H1,
        # while only 217 carry it in the filename — auto-named plans are the
        # majority of the gap, so filename-only ownership would orphan them.
        with TemporaryDirectory() as td:
            plan = _plan(
                Path(td),
                "adaptive-squishing-lovelace.md",
                "# OBPI-0.0.20-01-validator-and-allowlist — Validator Foundation\n",
            )
            self.assertTrue(plan_declares_obpi(plan, "OBPI-0.0.20-01-validator-and-allowlist"))

    def test_a_plan_owns_the_obpi_in_its_filename_even_when_the_h1_does_not(self) -> None:
        # The filename is the TOOL-GENERATED declaration; the H1 is authored
        # prose. Measured 2026-09-06: zero live plans declare in one and not the
        # other, because both are written together — so this arm is redundant
        # today and pinned anyway. Dropping it would make ownership depend
        # solely on a heading an agent typed.
        with TemporaryDirectory() as td:
            plan = _plan(
                Path(td),
                "corpus-candidate-generator-OBPI-0.35.0-05.md",
                "# Plan — corpus candidate generator\n\nNo identifier in the heading.\n",
            )
            self.assertTrue(plan_declares_obpi(plan, "OBPI-0.35.0-05-corpus-candidate"))

    def test_short_and_full_forms_agree(self) -> None:
        # The disagreement itself: discovery matched short form, orphan
        # detection matched the full slug. One directory, one rule.
        with TemporaryDirectory() as td:
            plan = _plan(Path(td), "x-OBPI-0.1.0-02.md", "# Plan — OBPI-0.1.0-02\n")
            self.assertTrue(plan_declares_obpi(plan, "OBPI-0.1.0-02"))
            self.assertTrue(plan_declares_obpi(plan, "OBPI-0.1.0-02-some-long-slug"))

    def test_a_plan_owning_no_obpi_owns_none(self) -> None:
        with TemporaryDirectory() as td:
            plan = _plan(Path(td), "stale.md", "# Stale plan — superseded\n")
            self.assertFalse(plan_declares_obpi(plan, "OBPI-0.1.0-02"))


class TestOrphanDetectionUsesOwnership(unittest.TestCase):
    def test_a_receipt_whose_plan_only_mentions_it_is_still_an_orphan(self) -> None:
        # Ownership is stricter than mention in BOTH directions: this receipt is
        # correctly an orphan, and the fix must not make it disappear by
        # loosening detection to match discovery's old any-mention rule.
        with TemporaryDirectory() as td:
            plans = Path(td)
            _plan(
                plans,
                "sibling-OBPI-0.35.0-04.md",
                "# Plan — OBPI-0.35.0-04\n\nExcludes OBPI-0.35.0-05.\n",
            )
            (plans / ".plan-audit-receipt-OBPI-0.35.0-05.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.35.0-05-corpus", "verdict": "FAIL"}),
                encoding="utf-8",
            )
            orphans = _find_orphan_receipts(plans)
        self.assertEqual([p.name for p, _ in orphans], [".plan-audit-receipt-OBPI-0.35.0-05.json"])

    def test_a_receipt_whose_plan_declares_it_is_not_an_orphan(self) -> None:
        with TemporaryDirectory() as td:
            plans = Path(td)
            _plan(plans, "owner-OBPI-0.35.0-04.md", "# Plan — OBPI-0.35.0-04\n")
            (plans / ".plan-audit-receipt-OBPI-0.35.0-04.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.35.0-04-section-ownership", "verdict": "PASS"}),
                encoding="utf-8",
            )
            self.assertEqual(_find_orphan_receipts(plans), [])


class TestReceiptArchive(unittest.TestCase):
    def _receipt(self, plans: Path) -> tuple[Path, str]:
        body = json.dumps({"obpi_id": "OBPI-0.35.0-05-corpus", "verdict": "FAIL", "gaps": 3})
        path = plans / ".plan-audit-receipt-OBPI-0.35.0-05.json"
        path.write_text(body, encoding="utf-8")
        return path, hashlib.sha256(body.encode()).hexdigest()

    def test_contents_are_preserved_byte_for_byte(self) -> None:
        # "Preserves the complete contents" — the archived copy must hash
        # identically. A receipt rewritten on the way out is not preserved.
        with TemporaryDirectory() as td:
            plans = Path(td)
            path, digest = self._receipt(plans)
            result = archive_plan_audit_receipt(path)
            self.assertTrue(result.archived, result.error)
            archived = Path(result.archive_path)
            self.assertEqual(hashlib.sha256(archived.read_bytes()).hexdigest(), digest)

    def test_provenance_records_origin_and_leaves_the_verdict_standing(self) -> None:
        # "Leaves the finding and FAIL verdict unresolved." Moving evidence is
        # not resolving its finding, and the record must say so rather than
        # reading as a disposition.
        with TemporaryDirectory() as td:
            plans = Path(td)
            path, digest = self._receipt(plans)
            result = archive_plan_audit_receipt(path)
            provenance = json.loads(Path(result.provenance_path).read_text(encoding="utf-8"))
        self.assertEqual(provenance["original_path"], str(path))
        self.assertEqual(provenance["sha256"], digest)
        self.assertEqual(provenance["verdict"], "FAIL")
        self.assertFalse(provenance["finding_resolved"])

    def test_the_operational_copy_is_removed_only_after_the_archive_verifies(self) -> None:
        with TemporaryDirectory() as td:
            plans = Path(td)
            path, _ = self._receipt(plans)
            result = archive_plan_audit_receipt(path)
            self.assertTrue(result.archived, result.error)
            self.assertFalse(path.exists())

    def test_preservation_failure_retains_the_original_and_fails_closed(self) -> None:
        # The constraint that makes the rest safe: if the archive cannot be
        # written or does not verify, the ONLY copy must survive. Losing a FAIL
        # verdict to a cleanup pass is the outcome this whole issue is about.
        with TemporaryDirectory() as td:
            plans = Path(td)
            path, _ = self._receipt(plans)
            blocker = plans / "archive"
            blocker.write_text("not a directory", encoding="utf-8")
            result = archive_plan_audit_receipt(path)
            self.assertFalse(result.archived)
            self.assertTrue(result.error)
            self.assertTrue(path.exists(), "the original must survive a failed archive")

    def test_a_corrupted_archive_is_caught_before_the_original_is_removed(self) -> None:
        # "Verifies the archive before removing the operational copy." Without a
        # corrupted-copy case the verification branch is unwitnessed — a mutant
        # replacing it with `if False:` passed the rest of this class. A truncated
        # or garbled copy must fail closed with the original still in place.
        with TemporaryDirectory() as td:
            plans = Path(td)
            path, _ = self._receipt(plans)

            def _corrupting_copy(src: str, dst: str) -> None:
                Path(dst).write_text("{}", encoding="utf-8")

            with mock.patch("gzkit.commands.preflight.shutil.copyfile", _corrupting_copy):
                result = archive_plan_audit_receipt(path)
            self.assertFalse(result.archived)
            self.assertIn("digest mismatch", result.error)
            self.assertTrue(path.exists(), "the original must survive a bad copy")
