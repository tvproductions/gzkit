"""Tests for resolve_fence_proof enforcement-asserting vs state-property fence paths.

REQ-0.0.74-18-01 (BEHAVIOR): an enforcement-asserting fence resolves "pass" ONLY
when its own @enforces claim (named as a backticked slug) is registered; the
result is claim-bound and import-order-independent.
REQ-0.0.74-18-02 (BEHAVIOR): a state-property fence resolution is unchanged —
parent-ADR ## Boundary Invariants anchor, no regression.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.traceability import covers


def _make_fake_adr(project_root: Path, semver: str, *, has_boundary_invariants: bool) -> None:
    """Create a minimal ADR package under project_root/docs/design/adr/foundation/."""
    adr_dir = project_root / "docs" / "design" / "adr" / "foundation" / f"ADR-{semver}-test"
    adr_dir.mkdir(parents=True)
    content = f"# ADR-{semver}-test\n"
    if has_boundary_invariants:
        # (OBPI-01) anchors the state-property fences these tests resolve
        # (REQ-0.0.74-01-03); heading presence alone is no longer proof (GHI #538).
        content += "\n## Boundary Invariants\n\n- Invariant 1 (OBPI-01)\n"
    (adr_dir / f"ADR-{semver}-test.md").write_text(content, encoding="utf-8")


class TestEnforcementAssertingFencePath(unittest.TestCase):
    """REQ-0.0.74-18-01: enforcement fence is claim-bound — pass only for its own live claim."""

    def setUp(self) -> None:
        from gzkit.enforcement import reset_enforcement_registry

        # Start clean so the resolver's own _ensure_production_claims_registered()
        # call is what populates the registry — this is the import-order guard
        # under test: a clean registry must not produce a spurious unproven-fence.
        reset_enforcement_registry()

    def tearDown(self) -> None:
        from gzkit.enforcement import reset_enforcement_registry

        reset_enforcement_registry()

    @covers("REQ-0.0.74-18-01")
    def test_named_registered_claim_resolves_pass_from_clean_registry(self) -> None:
        """A fence naming a real production claim resolves 'pass' even from an empty registry.

        The resolver triggers production-claim registration itself (via the
        canonical idempotent entrypoint), so the result does not depend on
        whether a registering module was imported first — the import-order
        weakness the registry-global check had is closed. ``req-kind-discipline``
        is a real qc enforcement claim covered by that entrypoint.
        """
        from gzkit.req_kind_fence import resolve_fence_proof

        with tempfile.TemporaryDirectory() as tmpdir:
            result = resolve_fence_proof(
                "REQ-0.0.74-16-04",
                Path(tmpdir),
                "the `req-kind-discipline` enforcement claim is live with a passing NC",
            )
        self.assertEqual(result, "pass")

    @covers("REQ-0.0.74-18-01")
    def test_named_unregistered_claim_resolves_unproven_fence(self) -> None:
        """A fence naming a claim that is NOT registered resolves 'unproven-fence'.

        This is the claim-binding teeth: a non-empty registry does NOT make every
        enforcement fence pass — only the fence whose own claim is live.
        """
        from gzkit.req_kind_fence import resolve_fence_proof

        with tempfile.TemporaryDirectory() as tmpdir:
            result = resolve_fence_proof(
                "REQ-0.0.74-13-03",
                Path(tmpdir),
                "`definitely-not-a-registered-claim` enforcement is live",
            )
        self.assertEqual(result, "unproven-fence")

    @covers("REQ-0.0.74-18-01")
    def test_meta_property_fence_naming_no_claim_resolves_unproven_fence(self) -> None:
        """A meta-property enforcement fence that names no single claim resolves unproven.

        REQ-16-06-style claims ("the registry has no _NEGATIVE_CONTROL_DEBT escape")
        are not per-claim bindable; they prove via the OBPI-19 floor at ADR closeout,
        not via this resolver.
        """
        from gzkit.req_kind_fence import resolve_fence_proof

        with tempfile.TemporaryDirectory() as tmpdir:
            result = resolve_fence_proof(
                "REQ-0.0.74-16-06",
                Path(tmpdir),
                "The enforcement-claim registry has no `_NEGATIVE_CONTROL_DEBT`-style escape",
            )
        self.assertEqual(result, "unproven-fence")

    @covers("REQ-0.0.74-18-01")
    def test_enforcement_asserting_keywords_detected(self) -> None:
        """Each enforcement keyword triggers the claim-bound path."""
        from gzkit.req_kind_fence import _is_enforcement_asserting

        enforcement_texts = [
            "the @enforces registry is live",
            "enforcement mechanism is present",
            "the runner fail-closes on absence",
            "bound to a live nc entry",
            "bound to a live negative control",
            "no _NEGATIVE_CONTROL_DEBT escape exists",
        ]
        for text in enforcement_texts:
            with self.subTest(text=text):
                self.assertTrue(_is_enforcement_asserting(text))


class TestStatePropertyFencePath(unittest.TestCase):
    """REQ-0.0.74-18-02: state-property fence resolution unchanged — no regression."""

    @covers("REQ-0.0.74-18-02")
    def test_state_property_with_anchor_resolves_pass(self) -> None:
        """State-property fence resolves 'pass' when parent ADR has Boundary Invariants."""
        from gzkit.req_kind_fence import resolve_fence_proof

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _make_fake_adr(project_root, "0.0.74", has_boundary_invariants=True)
            result = resolve_fence_proof(
                "REQ-0.0.74-01-03",
                project_root,
                "The marker is the single MX truth-source every surface consults",
            )
        self.assertEqual(result, "pass")

    @covers("REQ-0.0.74-18-02")
    def test_state_property_without_anchor_resolves_unproven_fence(self) -> None:
        """State-property fence resolves 'unproven-fence' when anchor is absent."""
        from gzkit.req_kind_fence import resolve_fence_proof

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _make_fake_adr(project_root, "0.0.74", has_boundary_invariants=False)
            result = resolve_fence_proof(
                "REQ-0.0.74-01-03",
                project_root,
                "The marker is the single MX truth-source every surface consults",
            )
        self.assertEqual(result, "unproven-fence")

    @covers("REQ-0.0.74-18-02")
    def test_empty_req_text_falls_through_to_anchor_path(self) -> None:
        """Empty req_text (backward-compat default) uses the anchor-only path.

        This pins the no-regression guarantee for the 2-arg closeout_proof.py
        consumer, which never passes req_text.
        """
        from gzkit.req_kind_fence import resolve_fence_proof

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _make_fake_adr(project_root, "0.0.74", has_boundary_invariants=True)
            result = resolve_fence_proof("REQ-0.0.74-01-03", project_root)
        self.assertEqual(result, "pass")

    @covers("REQ-0.0.74-18-02")
    def test_non_enforcement_keywords_do_not_trigger_claim_path(self) -> None:
        """State-property text (no enforcement keyword) does not trigger the claim-bound path."""
        from gzkit.req_kind_fence import _is_enforcement_asserting

        state_property_texts = [
            "Every fail-closed funnel consults the shared checkpoint",
            "the marker is the single truth-source",
            "no per-gate hand-set staging flag remains",
            "the one disposition handler routes the level",
        ]
        for text in state_property_texts:
            with self.subTest(text=text):
                self.assertFalse(_is_enforcement_asserting(text))


class TestMetaPropertyFenceClassification(unittest.TestCase):
    """is_meta_property_enforcement_fence separates a meta-property fence (no
    single bindable claim → defers to the OBPI-19 floor at closeout) from a
    single-claim fence (names a claim slug → OBPI-18 teeth) and a state-property
    fence (no enforcement vocabulary)."""

    def test_meta_property_texts_classify_as_meta(self) -> None:
        from gzkit.req_kind_fence import is_meta_property_enforcement_fence

        meta_texts = [
            "The enforcement-claim registry has no `_NEGATIVE_CONTROL_DEBT`-style "
            "escape; the runner fail-closes",
            "Every enforcement claim is registered through this single `@enforces` "
            "primitive into one registry",
            "the meta-validator enumerates `GATE5_INVARIANTS` membership and requires "
            "each member to carry an `@enforces` entry",
        ]
        for text in meta_texts:
            with self.subTest(text=text):
                self.assertTrue(is_meta_property_enforcement_fence(text))

    def test_single_claim_fence_is_not_meta(self) -> None:
        from gzkit.req_kind_fence import is_meta_property_enforcement_fence

        # Names a hyphenated claim-id-shaped slug → single-claim, keeps the teeth.
        self.assertFalse(
            is_meta_property_enforcement_fence("the `grader-gaming` enforcement is live")
        )
        self.assertFalse(
            is_meta_property_enforcement_fence(
                "`nonexistent-claim-xyz` fail-closes via a live negative control"
            )
        )

    def test_state_property_text_is_not_meta(self) -> None:
        from gzkit.req_kind_fence import is_meta_property_enforcement_fence

        # No enforcement keyword at all → not enforcement-asserting → not meta.
        self.assertFalse(
            is_meta_property_enforcement_fence("the marker is the single MX truth-source")
        )


if __name__ == "__main__":
    unittest.main()
