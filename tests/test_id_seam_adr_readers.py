"""ADR readers follow the identity seam (drydock RO-2 tranche 4).

`docs/governance/harbor-ro2-identity-seam.md` § Tranches row 4. The ADR grammar
and the foundation test (``0.0.x``) are spelled once, in ``gzkit.core.models``;
no reader outside the seam carries its own copy.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from gzkit.core import models
from gzkit.governance.trust_audits.id_seam import scan_seam_sites

_ROOT = Path(__file__).resolve().parent.parent


class TestAdrSemverAndFoundation(unittest.TestCase):
    """The seam answers what every ``_is_foundation_adr`` copy answered."""

    def test_adr_semver_reads_the_semver_of_any_adr_form(self) -> None:
        self.assertEqual(models.adr_semver("ADR-0.18.0-slug"), "0.18.0")
        self.assertEqual(models.adr_semver("ADR-0.18.0"), "0.18.0")
        self.assertEqual(models.adr_semver("ADR-12.3.45-x-y"), "12.3.45")

    def test_adr_semver_is_none_for_ids_that_carry_none(self) -> None:
        self.assertIsNone(models.adr_semver("ADR-pool.some-slug"))
        self.assertIsNone(models.adr_semver("OBPI-0.18.0-01"))
        self.assertIsNone(models.adr_semver(""))

    def test_foundation_adr_is_the_zero_zero_series_only(self) -> None:
        for adr_id in ("ADR-0.0.1", "ADR-0.0.36-slug", "ADR-0.0.74-mx"):
            self.assertTrue(models.is_foundation_adr(adr_id), adr_id)
        for adr_id in ("ADR-0.1.0-x", "ADR-1.0.0", "ADR-pool.x", "ADR-0.10.0-x", "junk"):
            self.assertFalse(models.is_foundation_adr(adr_id), adr_id)


class TestAdrBodies(unittest.TestCase):
    """The loose ADR bodies readers embed keep the breadth each reader had."""

    def test_pool_prefix_opens_only_pool_ids(self) -> None:
        pattern = re.compile(rf"^{models.ADR_POOL_PREFIX_BODY}[a-z]")
        self.assertTrue(pattern.match("ADR-pool.slug"))
        self.assertFalse(pattern.match("ADR-0.1.0-slug"))

    def test_components_body_names_major_minor_patch(self) -> None:
        match = re.match(models.ADR_SEMVER_COMPONENTS_BODY, "ADR-3.14.15-x")
        assert match is not None
        self.assertEqual((match["major"], match["minor"], match["patch"]), ("3", "14", "15"))

    def test_adr_or_prd_prefix_excludes_obpi(self) -> None:
        pattern = re.compile(rf"^{models.ADR_PRD_PREFIX_BODY}")
        self.assertTrue(pattern.match("ADR-0.1.0"))
        self.assertTrue(pattern.match("PRD-x"))
        self.assertFalse(pattern.match("OBPI-0.1.0-01"))


class TestNoAdrRowOutsideTheSeam(unittest.TestCase):
    """The close condition of tranche 4: the scan finds no ADR site."""

    def test_scan_finds_no_adr_grammar_outside_the_seam(self) -> None:
        stray = [f"{s.file}:{s.line}" for s in scan_seam_sites(_ROOT) if s.kind == "ADR"]
        self.assertEqual(stray, [])


if __name__ == "__main__":
    unittest.main()
