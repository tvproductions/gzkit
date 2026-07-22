"""Pinning tests for the two `--documents` scope guards landed under GHI #480.

`validate_document` carries two narrow skips that together suppress the bulk of
the pre-convention corpus drift GHI #480 measured:

* a kind-aware skip that exempts pool ADRs entirely (`is_pool_adr_path`), and
* a lifecycle-aware grandfather skip that exempts Completed/Validated ADRs from
  `required_headers`, decomposition, and missing-required-field checks
  (`is_adr_shape_grandfathered`).

Both shipped in OBPI-0.0.54-03 without tests. A scope guard is the one shape of
code where "passes" and "disabled" look identical from outside, so every skip
assertion below is paired with a **negative control**: an identically-shaped
artifact that differs only in the discriminating attribute (pool-ness, or
lifecycle status) and must still produce errors. Without the control, these
tests would keep passing if `validate_document` were reduced to `return []`.

The narrowness assertion is the third leg: grandfathering suppresses
*authoring-era shape* requirements only. Enum/pattern checks on fields that are
actually present remain mechanical invariants and must keep firing, otherwise
the guard has quietly become a blanket exemption for post-Accepted ADRs.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.validate_pkg.document import (
    is_adr_shape_grandfathered,
    is_pool_adr_path,
    validate_document,
)

# An ADR body missing every header the adr schema requires beyond Intent.
_SPARSE_BODY = "# {adr_id}: Sample\n\n## Intent\n\nSample intent.\n"


def _write_adr(
    directory: Path,
    adr_id: str,
    status: str,
    *,
    extra_frontmatter: str = "",
) -> Path:
    """Write a deliberately sparse ADR and return its path.

    The artifact omits `semver`, `kind`, and `date` and carries only an Intent
    header, so it trips both the missing-frontmatter-field and the
    missing-required-section families unless a scope guard exempts it.
    """
    path = directory / f"{adr_id}.md"
    path.write_text(
        "---\n"
        f"id: {adr_id}\n"
        f"status: {status}\n"
        "parent: PRD-GZKIT-1.0.0\n"
        "lane: heavy\n"
        f"{extra_frontmatter}"
        "---\n\n" + _SPARSE_BODY.format(adr_id=adr_id),
        encoding="utf-8",
    )
    return path


def _missing_section_errors(errors: list) -> list[str]:
    return [e.message for e in errors if e.message.startswith("Missing required section")]


def _missing_field_errors(errors: list) -> list[str]:
    return [e.message for e in errors if e.message.startswith("Missing required frontmatter field")]


class TestPoolAdrScopeGuard(unittest.TestCase):
    """Pool ADRs are exempt from the foundation/feature adr schema shape."""

    def test_pool_adr_is_detected_by_id_prefix(self) -> None:
        self.assertTrue(is_pool_adr_path(Path("ADR-pool.some-slug.md")))
        self.assertFalse(is_pool_adr_path(Path("ADR-0.9.9-some-slug.md")))

    def test_sparse_pool_adr_produces_no_errors(self) -> None:
        with TemporaryDirectory() as tmp:
            path = _write_adr(Path(tmp), "ADR-pool.sample-work", "Pool")
            self.assertEqual(validate_document(path, "adr"), [])

    def test_negative_control_same_shape_non_pool_adr_still_errors(self) -> None:
        """The guard, not vacuous validation, is what silences the pool case.

        Identical body and frontmatter shape; only the id prefix differs.
        """
        with TemporaryDirectory() as tmp:
            path = _write_adr(Path(tmp), "ADR-0.9.9-sample-work", "Draft")
            errors = validate_document(path, "adr")
            self.assertNotEqual(errors, [])
            self.assertTrue(_missing_section_errors(errors))


class TestLifecycleGrandfatherScopeGuard(unittest.TestCase):
    """Completed/Validated ADRs keep the shape they were attested with."""

    def test_grandfathered_statuses_are_exactly_completed_and_validated(self) -> None:
        for status in ("Completed", "Validated", "completed", "validated"):
            with self.subTest(status=status):
                self.assertTrue(is_adr_shape_grandfathered({"status": status}))
        for status in ("Draft", "Proposed", "Accepted", "Pool", "Deprecated", ""):
            with self.subTest(status=status):
                self.assertFalse(is_adr_shape_grandfathered({"status": status}))

    def test_validated_adr_is_exempt_from_shape_requirements(self) -> None:
        with TemporaryDirectory() as tmp:
            path = _write_adr(Path(tmp), "ADR-0.9.9-sample-work", "Validated")
            errors = validate_document(path, "adr")
            self.assertEqual(_missing_section_errors(errors), [])
            self.assertEqual(_missing_field_errors(errors), [])

    def test_negative_control_draft_adr_of_same_shape_still_errors(self) -> None:
        """Only the lifecycle status differs from the exempt case above."""
        with TemporaryDirectory() as tmp:
            path = _write_adr(Path(tmp), "ADR-0.9.9-sample-work", "Draft")
            errors = validate_document(path, "adr")
            self.assertTrue(_missing_section_errors(errors))
            self.assertTrue(_missing_field_errors(errors))

    def test_grandfathering_does_not_suppress_checks_on_present_fields(self) -> None:
        """Narrowness assertion: enum violations remain mechanical invariants.

        A Validated ADR that carries an out-of-enum `lane` must still fail. If
        this passes cleanly, grandfathering has widened from "authoring-era
        shape" into a blanket exemption for post-Accepted artifacts.
        """
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "ADR-0.9.9-sample-work.md"
            path.write_text(
                "---\n"
                "id: ADR-0.9.9-sample-work\n"
                "status: Validated\n"
                "parent: PRD-GZKIT-1.0.0\n"
                "lane: not-a-real-lane\n"
                "---\n\n" + _SPARSE_BODY.format(adr_id="ADR-0.9.9-sample-work"),
                encoding="utf-8",
            )
            errors = validate_document(path, "adr")
            self.assertNotEqual(errors, [], "enum check on a present field must still fire")


if __name__ == "__main__":
    unittest.main()
