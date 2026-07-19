"""Tests for the closed foundation-kind grandfather manifest (ADR-0.34.0, OBPI-01).

Covers REQ-0.34.0-01-03 (``FoundationGrandfatherManifest`` rejects a
``lifecycle`` field, any extra key, and any missing identity field via
``ValidationError``) and REQ-0.34.0-01-04 (the golden-file test fails when
``data/foundation_grandfather.json`` diverges from the pinned sunset roster).

@covers REQ-0.34.0-01-03
@covers REQ-0.34.0-01-04
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import ValidationError

from gzkit.models.foundation_grandfather import FoundationGrandfatherManifest
from gzkit.traceability import covers  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "data" / "foundation_grandfather.json"
GOLDEN_PATH = Path(__file__).resolve().parent / "fixtures" / "foundation_grandfather_golden.json"


def manifest_diverges(manifest_path: Path, golden_path: Path) -> bool:
    """Return True when the manifest is not byte-identical to its pinned fixture.

    The single read-and-compare path the tamper-guard tests all drive, so the
    negative controls exercise the real guard rather than re-asserting
    ``unittest``'s own behavior.
    """
    return manifest_path.read_text(encoding="utf-8") != golden_path.read_text(encoding="utf-8")


VALID_ENTRY = {
    "id": "ADR-0.0.1",
    "title": "Example Foundation",
    "semver": "0.0.1",
    "frozen_at": "2026-01-01",
}


class TestFoundationGrandfatherManifestValidation(unittest.TestCase):
    """REQ-0.34.0-01-03: identity-only entries; extra/lifecycle keys forbidden."""

    @covers("REQ-0.34.0-01-03")
    def test_valid_entry_constructs(self) -> None:
        entry = FoundationGrandfatherManifest(**VALID_ENTRY)
        self.assertEqual(entry.id, "ADR-0.0.1")

    @covers("REQ-0.34.0-01-03")
    def test_lifecycle_field_raises_validation_error(self) -> None:
        payload = {**VALID_ENTRY, "lifecycle": "active"}
        with self.assertRaises(ValidationError):
            FoundationGrandfatherManifest(**payload)

    @covers("REQ-0.34.0-01-03")
    def test_arbitrary_extra_key_raises_validation_error(self) -> None:
        payload = {**VALID_ENTRY, "unexpected_field": "x"}
        with self.assertRaises(ValidationError):
            FoundationGrandfatherManifest(**payload)

    @covers("REQ-0.34.0-01-03")
    def test_missing_required_field_raises_validation_error(self) -> None:
        for missing in ("id", "title", "semver", "frozen_at"):
            payload = {k: v for k, v in VALID_ENTRY.items() if k != missing}
            with self.subTest(missing=missing), self.assertRaises(ValidationError):
                FoundationGrandfatherManifest(**payload)

    @covers("REQ-0.34.0-01-03")
    def test_model_is_frozen(self) -> None:
        entry = FoundationGrandfatherManifest(**VALID_ENTRY)
        with self.assertRaises(ValidationError):
            entry.id = "ADR-0.0.2"  # type: ignore[misc]


class TestGoldenFileTamperGuard(unittest.TestCase):
    """REQ-0.34.0-01-04: golden-file test fails when the manifest diverges."""

    @covers("REQ-0.34.0-01-04")
    def test_manifest_matches_golden_fixture(self) -> None:
        """The committed manifest matches its pinned fixture."""
        self.assertFalse(
            manifest_diverges(MANIFEST_PATH, GOLDEN_PATH),
            "data/foundation_grandfather.json diverged from the pinned golden "
            "fixture; reopening the foundation kind must land as a deliberate, "
            "reviewable diff (both files must change together)",
        )

    @covers("REQ-0.34.0-01-04")
    def test_guard_detects_a_tampered_manifest(self) -> None:
        """The guard flags a real tampered manifest file on disk.

        Negative control for the assertion above. It drives the SAME
        ``manifest_diverges`` read-and-compare path the guard uses, against a
        real tampered file — so a guard that stopped detecting divergence
        (e.g. always returning False) fails HERE.

        The prior form of this test asserted that ``assertEqual`` raises on two
        unequal string literals. That exercised unittest itself, never the
        guard, and could not fail when the guard broke — the tautological shape
        AGENTS.md DO IT RIGHT Rule 6 forbids (flagged by the OBPI-0.34.0-01
        Step-4b adversary, Codex session 019f7ae0).
        """
        with TemporaryDirectory() as tmp:
            tampered = Path(tmp) / "foundation_grandfather.json"
            tampered.write_text(
                '[{"id": "ADR-0.0.99", "title": "Tampered", '
                '"semver": "0.0.99", "frozen_at": "2026-01-01"}]\n',
                encoding="utf-8",
            )
            self.assertTrue(
                manifest_diverges(tampered, GOLDEN_PATH),
                "the guard must flag a manifest that diverges from the fixture",
            )

    @covers("REQ-0.34.0-01-04")
    def test_guard_accepts_a_byte_identical_copy(self) -> None:
        """The guard does not flag a file that genuinely matches.

        Pins the other direction, so a guard hard-wired to report divergence
        (which would pass the tamper test above) fails here.
        """
        with TemporaryDirectory() as tmp:
            twin = Path(tmp) / "foundation_grandfather.json"
            twin.write_text(GOLDEN_PATH.read_text(encoding="utf-8"), encoding="utf-8")
            self.assertFalse(manifest_diverges(twin, GOLDEN_PATH))


if __name__ == "__main__":
    unittest.main()
